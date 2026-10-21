"""DELI's gun on a mast over a ball (sheet C sprites 245 above 283, 2x2 each: one 24 x 56 picture; enemies 145 and
146, ground layer, DELI and New Deli; VAULT and DELI RUIN put the ball, 146, on its own), polished (2026-10-21; it
replaces wave3_x_tower.py's mast_whole() and mast_piece(), a sphere painted by the sprite under a capsule gun, a slab
grip and a flat fin, on a carpet of the map's floor tiles). models.cfg: model ball_mast_gun / ball_mast_ball ... origin;
sprite c 245 ball_mast_gun yaw=0 height=-4, sprite c 283 ball_mast_ball yaw=0 height=-4 (height=-4: the ball stands
on the floor; without it the pieces float 4 pixels over it). The levels put 245 at the same x 28 pixels above 283 (DELI
and New Deli: event 6, the gun's d5 -28, linked by d4), and the game lifts the two pieces of one object together, so
they meet. Its damaged look (C 229 above 267) is polish_ball_mast_dmg.py's, built from this script's parts.

No sprite of any sheet is 245 or 283 mirrored, turned or in other ramps. 283's ramp-6 pixels round the ball are DELI's
floor tiles (and the ball's shadow on them): they are the map's, left out (the silhouettes are checked against the
ball's and the mast's own pixels).

As the sprites draw it (columns and rows of the 24 x 56 picture, 283's row r its row 28 + r): a grey gun pointing left
(the long top barrel, rows 3-7, its muzzle at column 0, a pale blue strip along its face, columns 7-12 of row 5; a
shorter barrel under it, rows 7-9 from column 4; a short stub under that, columns 6-8 of rows 10-14), its pale blue grip
hanging in front (columns 9-11 of rows 8-14), the dark receiver behind it (columns 12-16 of rows 6-14) and a blue fin
from the receiver's back (columns 14-21 of rows 8-15, lit pale at its upper left) narrowing to a blade down to row 27;
under the gun a grey U-shaped yoke (columns 9-15 of rows 15-23, open at its top, see-through inside); from the yoke two
blue rods (columns 10-11 and 13, a dark gap between) down into a slot in the ball (rows 28-34); the ball (columns 3-20
of rows 29-47): a grey cap round the rods, a band of pale blue panels (rows 32-34), grey panels down to a seam (rows
35-39), blue panels below it, a band down its middle (the slot, a pale blue window, then dark grey), dark seams between.

The sprites draw it from the side: a tall object, its gun high over the ball. As the other tall objects of the levels
(DELI's tower beside it leans 74 degrees), the mast is built upright and leaned back up the screen, 70 degrees from
upright about the ball's middle (the game's camera, 20 degrees from straight down, then sees it from the side, face on,
as the sprites draw it), laid out so that seen from straight above it covers the sprites' pixels: the ball sunk 3
pixels into the floor, the rods rising from the slot in its front, the gun on the yoke, its barrel 26 pixels over the
floor. The ball's bands run round an axis of their own, leaned 65 degrees (the camera sees them nearly edge on, as
the sprite's straight bands: the cap a segment at the top, the bands on the sprite's rows, BANDS). Built whole, then
cut along the sprites' edge (y = 0; polish_arch.cut keeps the whole's shading across the cut) into the two pieces,
each moved to its sprite's centre. The ball's piece holds the rods' foot (as 283 draws it), so the ball on its own
(VAULT, DELI RUIN) shows the stub of its mast; the fin ends above the cut, so a damaged gun (whose fin is gone) meets
an intact ball.

The ball: a sphere meshed in rings round its bands' axis (the seams' edges and floors on rings), cut along the middle
band's seams (polish_sphere_nozzle's split_along), the seams pressed in as grooves, the slot deeper; painted by band,
with a little emission (a ball seen by the slanted camera shows mostly its side away from the sun). The gun: the
barrels and the stub turned about x (the bore cut into the muzzle, two grooves round the top barrel), the strip, the
grip, the receiver and the block under the lower barrel rounded blocks, the fin lofted from smooth sections across it
(its paint's edges cut along smooth lines), the yoke and the rods round bars, a dark web between the rods; painted as
the sprites shade them.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the floor (z = 0); the whole's
origin is the middle of the sprites' common edge: column c of the picture is x = c + 0.5 - 12, row r is y = 27.5 - r.
The parts are built upright (x, d, h): h along the axis from the ball's middle, d back (the front, which the camera
sees, towards -d), then leaned (UPRIGHT_TO_WORLD; the ball by BALL_TO_WORLD).

Replaces wave3_x_tower.py's gun on the mast: remove its section (MAST_ORIGIN, BALL, BALL_R, category_map(), mast_whole()
with its x.whole("mast", (24, 56)) registration, mast_piece() and the ball_mast_gun / ball_mast_ball model loop), the
bullet of its docstring, "; C 245 above 283" in its first lines and "|mast" in its usage line; and wave3_x_art.py's
MAST. wave3_ao_deli.py reads both (its mast_damaged_whole(), M_INT): they go together with it, which
polish_ball_mast_dmg.py replaces. The tower stays.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the whole's and each piece's
silhouette against enemy_C.png, the floor left out), --preview <prefix>, --only <name,...>, --whole <file.glb>.
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
from polish_machine_kit import k  # noqa: E402
from polish_arch import cut  # noqa: E402  (polish_machine_kit.cut without its material indices shifted twice)
from polish_k_pod import triangulate  # noqa: E402

# The pieces: (name, sprite, the box it covers in the whole's coordinates (x0, x1, y0, y1)).
PIECES = [("ball_mast_gun", 245, (-12.0, 12.0, 0.0, 28.0)), ("ball_mast_ball", 283, (-12.0, 12.0, -28.0, 0.0))]

# The lean: the mast's axis turned back up the screen this far from upright, about the ball's middle; the ball's bands'
# axis turned back less (the game's camera, CAMERA degrees from straight down, sees the ball's cap over its pale band
# as the sprite draws it, and the mast from the side).
CAMERA = 20.0
BETA = math.radians(70.0)
BALL_TILT = 65.0
SB, CB = math.sin(BETA), math.cos(BETA)
BALL_C = Vector((0.0, -10.5, 6.0))
BALL_R = 9.25
FLOOR_CUT = -1.0                 # nothing below this (the floor hides it)
UPRIGHT_TO_WORLD = Matrix.Translation(BALL_C) @ Matrix.Rotation(-BETA, 4, "X")
BALL_TO_WORLD = Matrix.Translation(BALL_C) @ Matrix.Rotation(-math.radians(BALL_TILT), 4, "X")


def band_angle(y):
    """The angle from the ball's axis (top) of the ring the game's camera sees at the picture's y on the ball's
    middle."""
    return BALL_TILT + CAMERA - math.degrees(math.asin(max(-1.0, min(1.0, (y - BALL_C.y) / BALL_R))))


# The ball's bands: the cap's edge, the pale band's lower edge, the seam above the blue (rows 31.5, 34.5, 40 of the
# picture: y -4, -7, -12.5); the middle band (x centre, half-width); the seams' half-width and depth. The slot the
# rods stand in: the middle band on the front from SLOT_TOP down to the pale band's lower edge, SLOT_D deep; the rods
# enter it at SLOT_AT (all angles from the axis's top).
BANDS = tuple(band_angle(y) for y in (-4.0, -7.0, -12.5))
MID_X, MID_W = 0.5, 2.25
SEAM_W, SEAM_D = 0.24, 0.3
SLOT_TOP, SLOT_D = 28.0, 0.95
SLOT_AT = 51.0


def _slot_depth():
    """The mast's plane (its depth d in the mast's upright frame) through the point where the rods enter the slot."""
    a, t = math.radians(SLOT_AT), math.radians(BALL_TILT)
    y, z = BALL_R * math.sin(t - a), BALL_R * math.cos(t - a)
    return y * CB - z * SB


D0 = _slot_depth()               # the mast's and the gun's middle plane: this far in front of the ball's middle
# The rods: x, radius; their top in the yoke (as y on the picture); the web between them (x0, x1, how far behind).
RODS = [(-0.85, 0.8), (1.45, 0.7)]
ROD_TOP_Y = 4.9
WEB = (-0.2, 0.9, 0.35)
# The yoke: its path (x, y on the picture, radius), in the middle plane.
YOKE = [(-2.0, 13.0, 1.05), (-2.2, 11.4, 1.2), (-2.0, 9.4, 1.3), (-1.3, 7.3, 1.5), (0.55, 5.6, 1.75),
        (2.35, 6.1, 1.55), (3.4, 7.5, 1.3), (3.75, 9.2, 1.05), (3.6, 10.1, 0.75)]
PIN = (-1.6, 12.9, 1.05, 1.5)    # the pivot under the gun: x, y, radius, half-length (along d)
# The gun: the top barrel (y of its axis, radius, from x to x), the strip on its face (from x to x, half-height,
# how far out), the lower barrel and the stub (y, radius, from, to, depth about D0), the block joining them (x0, x1,
# y0, y1), the grip and the receiver (x0, x1, y0, y1, d0, d1 about D0), the grooves round the top barrel.
BARREL = (22.5, 2.15, -11.75, 2.7)
BORE = (0.66, 0.55)              # the bore's radius and depth
STRIP = (-5.2, 1.25, 0.6, 0.3)
BARREL2 = (19.35, 1.65, -8.6, 0.6, 0.3)
STUB = (14.6, 1.7, -6.4, -2.4, 0.1)
STUB_BLOCK = (-5.5, -2.6, 15.6, 18.4)
GRIP = (-3.1, 0.1, 12.7, 20.4, -2.7, 0.8)
RECEIVER = (-0.3, 5.6, 12.7, 22.3, -1.6, 2.2)
GROOVES = (-9.7, 0.9)
# The fin: its sections from its blade's tip up to its rounded top (y on the picture, left x, right x, half-thickness),
# interpolated smoothly; its depth about D0.
FIN = [(0.4, 8.2, 10.0, 0.22), (2.5, 7.75, 10.55, 0.35), (5.0, 7.2, 10.65, 0.45), (7.5, 6.2, 10.7, 0.56),
       (9.5, 5.0, 10.65, 0.66), (11.5, 3.3, 10.65, 0.78), (13.5, 2.3, 10.65, 0.85), (15.5, 2.3, 10.65, 0.85),
       (17.0, 3.6, 10.65, 0.8), (18.5, 5.4, 10.6, 0.72), (19.7, 6.0, 10.4, 0.62), (20.4, 6.9, 9.9, 0.45),
       (20.75, 7.9, 9.0, 0.2)]
FIN_LIT_Y = 12.6                 # above this the fin is lit pale
FIN_D = -1.75


def materials():
    pal = k.level_palette()

    def mat(name, index, metallic=0.5, roughness=0.35, glow=0.0):
        if glow > 0:
            return k.material(name, palette=index, metallic=metallic, roughness=roughness, emission=pal[index],
                              emission_strength=glow)
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)
    return {
        "seam": mat("mast_seam", 0x01, 0.3, 0.6),
        "shadow": mat("mast_shadow", 0x03, 0.5, 0.4),
        "grey_dark": mat("mast_grey_dark", 0x05, 0.55, 0.35),
        "grey": mat("mast_grey", 0x07, 0.6, 0.3),
        "steel": mat("mast_steel", 0x08, 0.6, 0.28),
        "steel_lit": mat("mast_steel_lit", 0x0a, 0.6, 0.26),
        "glint": mat("mast_glint", 0x0c, 0.6, 0.22),
        "pale_dark": mat("mast_pale_dark", 0x83, 0.45, 0.3),
        "pale": mat("mast_pale", 0x85, 0.45, 0.28),
        "pale_lit": mat("mast_pale_lit", 0x86, 0.45, 0.26),
        "sky": mat("mast_sky", 0x9e, 0.35, 0.25),
        "blue_dark": mat("mast_blue_dark", 0x36, 0.5, 0.32),
        "blue": mat("mast_blue", 0x38, 0.5, 0.3),
        "blue_lit": mat("mast_blue_lit", 0x3a, 0.5, 0.28),
        # The ball's panels, with a little light of their own.
        "ball_cap": mat("mast_ball_cap", 0x0a, 0.55, 0.3, 0.14),
        "ball_pale": mat("mast_ball_pale", 0x85, 0.45, 0.28, 0.16),
        "ball_grey": mat("mast_ball_grey", 0x08, 0.55, 0.3, 0.14),
        "ball_blue": mat("mast_ball_blue", 0x39, 0.5, 0.3, 0.18),
        "ball_dark": mat("mast_ball_dark", 0x04, 0.5, 0.35, 0.1),
        "ball_window": mat("mast_ball_window", 0x86, 0.45, 0.26, 0.18),
    }


# --- The frame ------------------------------------------------------------------------------------------------

def h_at(y, d=D0):
    """The height along the axis whose point at depth d lies over the picture's y once leaned."""
    return (y - BALL_C.y - d * CB) / SB


def lean(objects, matrix=UPRIGHT_TO_WORLD):
    for obj in objects:
        obj.data.transform(matrix)
        obj.data.update()


def floor_cut(objects, z=FLOOR_CUT):
    """Everything below z taken away (the ball's sunk part), the cut left open (under the floor)."""
    for obj in objects:
        if min((obj.matrix_world @ v.co).z for v in obj.data.vertices) >= z:
            continue
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=(0, 0, z),
                               plane_no=(0, 0, -1), clear_outer=True)
        bm.to_mesh(obj.data)
        bm.free()
        obj.data.update()


def ring_xd(h, cx, cd, hw, hd, segments, power=2.0):
    """A section across the axis at height h: a superellipse round (cx, cd), half-width hw along x, half-depth hd."""
    pts = []
    for j in range(segments):
        a = 2 * math.pi * j / segments
        u, v = mk.superellipse_point(a, power)
        pts.append(Vector((cx + u * hw, cd + v * hd, h)))
    return pts


def lathe_x(name, profile, cd, ch, mat, segments=24, squash=1.0):
    """A part turned about an axis along x through (d, h) = (cd, ch): profile [(x, radius)], increasing x."""
    rings = []
    for x, r in profile:
        rings.append([Vector((x, cd + r * math.cos(2 * math.pi * j / segments) * squash,
                              ch + r * math.sin(2 * math.pi * j / segments))) for j in range(segments)])
    return k.loft(name, rings, mat, start_point=(profile[0][0], cd, ch), end_point=(profile[-1][0], cd, ch))


def rounded_block(name, x0, x1, d0, d1, h0, h1, mat, bevel, segments=3):
    obj = mk.box(name, x0, x1, d0, d1, h0, h1, mat)
    mk.bevel(obj, bevel, segments, 30)
    mk.shade(obj, 35)
    return obj


# --- The ball -------------------------------------------------------------------------------------------------

def polar(co):
    """A point's angle from the ball's axis's top (degrees), in the ball's frame."""
    return math.degrees(math.acos(max(-1.0, min(1.0, co.z / max(co.length, 1e-6)))))


def ball_angles():
    """The rings' angles from the axis's top (degrees): about every 6 degrees, and on each seam's edges and floor and
    the slot's top."""
    half = math.degrees(SEAM_W / BALL_R)
    fixed = [SLOT_TOP, SLOT_TOP + 0.8]
    for b in BANDS:
        fixed += [b - half, b - half / 2, b + half / 2, b + half]
    out, a = [0.0], 0.0
    while a < 180.0 - 1e-6:
        nxt = min([f for f in fixed if f > a + 0.05] + [a + 6.0, 180.0])
        out.append(nxt)
        a = nxt
    return out


def seam_offset(alpha, x):
    """How far inside the nearest seam a point is (0 on its middle, 1 on its edge; None outside every seam)."""
    half = math.degrees(SEAM_W / BALL_R)
    best = None
    for b in BANDS:
        f = abs(alpha - b) / half
        if f <= 1.0 + 1e-4:
            best = f if best is None else min(best, f)
    for side in (-1, 1):
        f = abs(x - (MID_X + side * MID_W)) / SEAM_W
        if f <= 1.0 + 1e-4:
            best = f if best is None else min(best, f)
    return best


def in_slot(alpha, x, d, eps=1e-3):
    """The slot the rods stand in: the middle band on the front, from SLOT_TOP down to the pale band's lower seam."""
    half = math.degrees(SEAM_W / BALL_R)
    return (d < 0.0 and SLOT_TOP + 0.8 - eps <= alpha <= BANDS[1] - half / 2 + eps and
            abs(x - MID_X) <= MID_W - SEAM_W / 2 + eps)


def ball_depth(co):
    """How far a vertex of the ball is pressed in: the slot's floor, the seams' floors (their edges stay)."""
    a = polar(co)
    if in_slot(a, co.x, co.y):
        return SLOT_D
    f = seam_offset(a, co.x)
    return SEAM_D if f is not None and f <= 0.5 + 1e-3 else 0.0


def ball(m):
    """The ball (built about its own axis, leaned by BALL_TO_WORLD): rings round its axis (the seams' edges and floors
    on rings), cut along the middle band's seams' edges and floors, the seams' floors and the slot pressed in; each
    panel painted by its band."""
    segments = 40
    angles = ball_angles()
    bm = bmesh.new()
    rings = []
    for a in angles[1:-1]:
        ar = math.radians(a)
        rings.append([bm.verts.new((BALL_R * math.sin(ar) * math.sin(2 * math.pi * j / segments),
                                    -BALL_R * math.sin(ar) * math.cos(2 * math.pi * j / segments),
                                    BALL_R * math.cos(ar))) for j in range(segments)])
    top, bottom = bm.verts.new((0, 0, BALL_R)), bm.verts.new((0, 0, -BALL_R))
    for j in range(segments):
        jn = (j + 1) % segments
        bm.faces.new((top, rings[0][j], rings[0][jn]))
        for i in range(len(rings) - 1):
            bm.faces.new((rings[i][j], rings[i + 1][j], rings[i + 1][jn], rings[i][jn]))
        bm.faces.new((rings[-1][jn], rings[-1][j], bottom))
    # The middle band's seams: cut along their edges and floors (lines of equal x).
    for side in (-1, 1):
        for e in (-SEAM_W, -SEAM_W / 2, SEAM_W / 2, SEAM_W):
            mk.split_along(bm, {v: v.co.x for v in bm.verts}, MID_X + side * MID_W + e)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    for v in bm.verts:
        v.co = v.co.normalized() * (BALL_R - ball_depth(v.co))
    mesh = bpy.data.meshes.new("ball")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("ball", mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(m["ball_grey"])
    k.recalc_normals(obj)
    k.smooth(obj, 35)

    def pick(c, n):
        co = Vector(c)
        a = polar(co)
        if in_slot(a, co.x, co.y, eps=-1e-3) and co.length < BALL_R - 0.5 * SLOT_D:
            return m["seam"]
        f = seam_offset(a, co.x)
        if f is not None and f < 0.85 and co.length < BALL_R - 0.05:
            return m["seam"]
        band = sum(1 for b in BANDS if a > b)
        if abs(co.x - MID_X) < MID_W:
            if band <= 1:
                return m["ball_dark"]
            return m["ball_window"] if band == 2 else m["ball_dark"]
        return (m["ball_cap"], m["ball_pale"], m["ball_grey"], m["ball_blue"])[band]
    mk.paint(obj, pick)
    return obj


def rods(m):
    """The two rods from the slot up into the yoke's foot, parallel to the mast's axis, a dark web between them."""
    out = []
    top = h_at(ROD_TOP_Y)
    for i, (x, r) in enumerate(RODS):
        foot = math.sqrt(max(0.0, (BALL_R - SLOT_D - 0.5) ** 2 - D0 ** 2 - x * x))
        rings = [ring_xd(h, x, D0, r, r, 16) for h in (foot, foot + 1.0, top - 1.0, top)]
        rod = k.loft(f"rod{i}", rings, m["blue"])
        k.smooth(rod, 50)
        mk.paint(rod, lambda c, n, first=(i == 0): m["pale_dark"] if n.x < -0.55 and first else
                 m["blue_lit"] if n.x < -0.2 else m["blue_dark"] if n.x > 0.5 else None)
        out.append(rod)
    x0, x1, back = WEB
    foot = math.sqrt(max(0.0, (BALL_R - SLOT_D - 0.5) ** 2 - D0 ** 2))
    web = mk.box("web", x0, x1, D0 - 0.25 + back, D0 + 0.25 + back, foot, top - 0.3, m["shadow"])
    k.smooth(web, 30)
    return out


# --- The mast's head: the yoke and the gun ----------------------------------------------------------------------

def yoke(m):
    """The U-shaped yoke under the gun: a round bar, thick at its foot, open at its top; the pivot under the gun."""
    pts = [(x, D0, h_at(y), r) for x, y, r in YOKE]
    bar = mk.smooth_tube("yoke", pts, m["grey"], 16)
    k.smooth(bar, 55)
    mk.paint(bar, lambda c, n: m["steel_lit"] if n.y < -0.6 and n.z > 0.2 else m["grey_dark"] if n.z < -0.55 else None)
    px, py_, pr, plen = PIN
    h = h_at(py_)
    rings = [[Vector((px + pr * math.cos(2 * math.pi * j / 16), d, h + pr * math.sin(2 * math.pi * j / 16)))
              for j in range(16)] for d in (D0 - plen, D0 - plen + 0.2, D0 + plen)]
    pin = k.loft("pin", rings, m["shadow"])
    k.smooth(pin, 50)
    return bar


def barrels(m):
    """The top barrel (a rounded muzzle with the bore cut in, two grooves round it), the strip along its face, the
    lower barrel and the stub."""
    y, r, x0, x1 = BARREL
    bore_r, bore_d = BORE
    prof = [(x0 + bore_d, 0.01), (x0 + bore_d, bore_r), (x0, bore_r + 0.05), (x0 + 0.05, r * 0.62),
            (x0 + 0.2, r * 0.83), (x0 + 0.5, r * 0.95), (x0 + 0.95, r)]
    for g in GROOVES:
        prof += [(g - 0.3, r), (g - 0.12, r - 0.22), (g + 0.12, r - 0.22), (g + 0.3, r)]
    prof += [(x1 - 0.45, r), (x1 - 0.15, r * 0.9), (x1, r * 0.7)]
    h = h_at(y)
    top = lathe_x("barrel", prof, D0, h, m["steel"], 28)
    k.smooth(top, 40)

    def pick(c, n):
        if c.x < x0 + bore_d + 0.05 and math.hypot(c.y - D0, c.z - h) < bore_r + 0.08:
            return m["seam"]
        if any(abs(c.x - g) < 0.14 for g in GROOVES):
            return m["shadow"]
        if c.x < x0 + 0.35:
            return m["glint"]
        if n.z > 0.75 or (n.z > 0.35 and n.y < -0.3):
            return m["steel_lit"]
        if n.z < -0.45:
            return m["grey_dark"]
        return None
    mk.paint(top, pick)
    # The strip along its face.
    sx0, sx1, half, out = STRIP
    strip = rounded_block("strip", sx0, sx1, D0 - r - out, D0 - r + 0.6, h - half, h + half, m["pale_lit"], 0.22, 2)
    mk.paint(strip, lambda c, n: m["sky"] if n.z > 0.6 else m["pale"] if n.z < -0.5 else None)
    # The lower barrel and the stub.
    y2, r2, a2, b2, dd2 = BARREL2
    h2 = h_at(y2, D0 + dd2)
    prof2 = [(a2, 0.01), (a2 + 0.04, r2 * 0.55), (a2 + 0.2, r2 * 0.85), (a2 + 0.5, r2), (b2, r2)]
    low = lathe_x("barrel2", prof2, D0 + dd2, h2, m["steel"], 22)
    k.smooth(low, 40)
    mk.paint(low, lambda c, n: m["glint"] if c.x < a2 + 0.3 else m["steel_lit"] if n.z > 0.6 else
             m["grey_dark"] if n.z < -0.4 else None)
    ys, rs, a3, b3, dd3 = STUB
    h3 = h_at(ys, D0 + dd3)
    prof3 = [(a3, 0.01), (a3 + 0.05, rs * 0.6), (a3 + 0.25, rs * 0.88), (a3 + 0.6, rs), (b3, rs)]
    stub = lathe_x("stub", prof3, D0 + dd3, h3, m["grey"], 22)
    k.smooth(stub, 40)
    mk.paint(stub, lambda c, n: m["glint"] if c.x < a3 + 0.35 and n.x < -0.5 else m["steel"] if n.z > 0.5 else
             m["grey_dark"] if n.z < -0.4 else None)
    bx0, bx1, by0, by1 = STUB_BLOCK
    join = rounded_block("stub_block", bx0, bx1, D0 - 1.25, D0 + 1.25, h_at(by0), h_at(by1), m["grey_dark"], 0.45)
    mk.paint(join, lambda c, n: m["grey"] if n.y < -0.6 else None)
    return top


def grip(m):
    """The pale blue grip hanging in front of the lower barrel, its left edge lit, its foot dark blue."""
    x0, x1, y0, y1, d0, d1 = GRIP
    dm = D0 + (d0 + d1) / 2
    obj = rounded_block("grip", x0, x1, D0 + d0, D0 + d1, h_at(y0, dm), h_at(y1, dm), m["pale"], 0.55)
    mk.paint(obj, lambda c, n: m["sky"] if n.x < -0.5 and n.y < -0.2 else m["pale_lit"] if n.y < -0.6 else
             m["blue"] if n.z < -0.5 else m["pale_dark"] if n.x > 0.5 else None)
    return obj


def receiver(m):
    """The dark receiver behind the grip, its top's back corner bevelled off, its front left edge lit."""
    x0, x1, y0, y1, d0, d1 = RECEIVER
    dm = D0 + (d0 + d1) / 2
    h0, h1 = h_at(y0, dm), h_at(y1, dm)
    obj = mk.prism("receiver", [(x0, h0), (x1, h0), (x1, h1 - 2.0), (x1 - 2.0, h1), (x0, h1)], D0 + d0, D0 + d1,
                   m["shadow"], axis="y")
    mk.bevel(obj, 0.5, 3, 30)
    mk.shade(obj, 35)
    mk.paint(obj, lambda c, n: m["steel"] if n.x < -0.5 or (n.y < -0.5 and c.x < x0 + 1.0) else
             m["grey_dark"] if n.z > 0.5 else None)
    return obj


def fin_sections(step=0.45):
    """The fin's sections, interpolated smoothly from its tip up to its top: (y, left x, right x, half-thickness)."""
    return k.profile(FIN, step)


def fin(m):
    """The blue fin from the receiver's back: lofted from sections across it (from its blade's tip up to its rounded
    top), lens-shaped, in front of the receiver; lit pale over its upper part, a pale line down its blade beside the
    dark right edge."""
    rings = []
    d_mid = D0 + FIN_D
    sections = fin_sections()
    for y, xl, xr, t in sections:
        rings.append(ring_xd(h_at(y, d_mid), (xl + xr) / 2, d_mid, (xr - xl) / 2, t, 28, power=2.6))
    tip, top = sections[0], sections[-1]
    obj = k.loft("fin", rings, m["blue"], start_point=((tip[1] + tip[2]) / 2, d_mid, h_at(tip[0] - 0.3, d_mid)),
                 end_point=((top[1] + top[2]) / 2, d_mid, h_at(top[0] + 0.15, d_mid)))
    # The paint's edges cut along smooth lines (the lit part's lower edge, the shadow of the receiver, the pale line
    # down the blade and the dark right edge), then each face painted by where it lies.
    h_lit = h_at(FIN_LIT_Y, d_mid)
    h_shadow = h_at(17.8, d_mid)
    def lit_edge(co):
        return co.z - (h_lit + 0.25 * (co.x - 6.0))
    split_by(obj, [(lit_edge, 0.0), (lambda co: co.x, 4.6), (lambda co: co.z - h_shadow, 0.0),
                   (lambda co: co.x, 8.85), (lambda co: co.x, 9.75), (lambda co: co.x, 10.05)])
    k.smooth(obj, 60)

    def pick(c, n):
        co = Vector(c)
        if n.y > 0.35 or co.x > 10.05:
            return m["blue_dark"]
        if lit_edge(co) > 0.0:
            if co.x < 4.6 and co.z < h_shadow:
                return m["blue"]                       # where it meets the receiver: in its shadow
            return m["pale_lit"]
        if 8.85 < co.x < 9.75 and n.y < -0.5:
            return m["pale_dark"]
        if n.x < -0.35:
            return m["blue_lit"]
        return None
    mk.paint(obj, pick)
    return obj


def split_by(obj, fields):
    """Cuts an object's faces along the contours where each field (a function of a point) crosses its threshold
    (polish_sphere_nozzle's split_along), so that paint edges follow smooth lines."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    for fn, threshold in fields:
        mk.split_along(bm, {v: fn(v.co) for v in bm.verts}, threshold)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    return obj


# --- The whole -----------------------------------------------------------------------------------------------------

def build_mast(m):
    """The mast and its head, upright: the rods, the yoke, the gun."""
    rods(m)
    yoke(m)
    barrels(m)
    grip(m)
    receiver(m)
    fin(m)


def build_whole(m):
    """Every part upright, then leaned (the ball about its own tilt), the ball's sunk part cut away; returns the
    meshes."""
    sphere = ball(m)
    mk.apply(sphere)
    lean([sphere], BALL_TO_WORLD)
    build_mast(m)
    whole = mk.meshes()
    mast = [o for o in whole if o is not sphere]
    for obj in mast:
        mk.apply(obj)
    lean(mast)
    floor_cut(whole)
    bpy.context.view_layer.update()
    return [o for o in whole if len(o.data.polygons) > 0]


# --- Checks -------------------------------------------------------------------------------------------------------

def sprite_indices(sheet, sprite):
    """A 2x2 sprite's palette indices (rows of ints, None where transparent), from the sheet's .idx beside its .png."""
    mask = k.sprite_mask(sheet, sprite)
    raw = open(sheet[:-4] + ".idx", "rb").read()
    x0, y0 = (sprite - 1) % 19 * 12, (sprite - 1) // 19 * 14
    return [[raw[(y0 + r) * 228 + x0 + c] if mask[r][c] else None for c in range(24)] for r in range(28)]


def ball_own(sheet, sprite):
    """The ball sprite's own pixels: its disc (columns 3-20 of rows 1-19) and the mast's foot (columns 10-13 of rows
    0-4); the floor tiles round them are the map's."""
    idx = sprite_indices(sheet, sprite)
    return [[idx[r][c] is not None and ((((c - 11.5) / 9.0) ** 2 + ((r - 10.0) / 9.5) ** 2 <= 1.0) or
                                        (10 <= c <= 13 and r <= 4)) for c in range(24)] for r in range(28)]


def masks(sheet, top=245, bottom=283):
    gun, ball_ = k.sprite_mask(sheet, top), ball_own(sheet, bottom)
    return gun, ball_, gun + ball_


def check(whole, sheet, top=245, bottom=283, label="whole (C 245 above 283)"):
    gun, ball_, both = masks(sheet, top, bottom)
    mk.compare(label, mk.coverage(whole, 24, 56), both)
    return {top: gun, bottom: ball_}


def drop_unused(objects):
    """Takes the material slots no face uses off the objects (the faces' indices moved to match), so that the
    reports count only what the models show."""
    for obj in objects:
        mesh = obj.data
        used = sorted({p.material_index for p in mesh.polygons})
        if len(used) == len(mesh.materials):
            continue
        keep = [mesh.materials[i] for i in used]
        remap = {old: new for new, old in enumerate(used)}
        indices = [remap[p.material_index] for p in mesh.polygons]
        mesh.materials.clear()
        for mat in keep:
            mesh.materials.append(mat)
        mesh.polygons.foreach_set("material_index", indices)
        mesh.update()


def pieces_of(whole, box, cap):
    pieces = [p for p in (cut(src, box, cap) for src in whole) if p is not None]
    drop_unused(pieces)
    mk.transform(pieces, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
    bpy.context.view_layer.update()
    return pieces


def export_pieces(whole, m, options, pieces_table, sprite_masks, cap_key="seam"):
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    for name, sprite, box in pieces_table:
        if only and name not in only:
            continue
        pieces = pieces_of(whole, box, m[cap_key])
        triangulate(pieces)
        for src in whole:
            src.hide_render = True
        if sprite_masks:
            mk.compare("%s (C %d)" % (name, sprite), mk.coverage(pieces, 24, 28), sprite_masks[sprite])
        mk.report(name, pieces, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, pieces)
        for obj in pieces:
            bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False


def build():
    options = k.args()
    k.reset()
    m = materials()
    whole = build_whole(m)
    print("whole mast: %d triangles, %d objects" % (mk.triangles(whole), len(whole)))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    sprite_masks = None
    if "check" in options:
        sprite_masks = check(whole, os.path.join(options["check"], "enemy_C.png"))
    if "preview" in options:
        mk.preview(options["preview"] + "ball_mast_whole", whole, size=(24, 56), scale=10, distance=1.6)
    if "whole" in options:
        mk.export(whole, options["whole"])
    export_pieces(whole, m, options, PIECES, sprite_masks)


if __name__ == "__main__":
    build()
