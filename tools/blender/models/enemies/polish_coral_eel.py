"""CORAL's electric eel (sheet ', written x27 in models.cfg; enemies 1218 and 1219 of episode 5, ground enemies):
a brown eel lying in a crackling cushion of translucent pale blue light, head down the screen with two glowing
blue eyes. Polished (2026-10-21; it replaces wave3_ae_coral.py's eel). The levels always put its two 2x2 sprites
together as one 24 x 56 picture (CORAL's ground events at 200-3820, type 10, 26 pairs): 1218 (' 3) at (x, y - 28)
above 1219 (' 41) at (x, y); each is an enemy of its own (the two move together; one can be shot away first). Their
animation (3 3 3 3 5 5 5 5 and 41 41 41 41 43 43 43 43) makes the eel wriggle: 5 above 43 draws its body's S-curve
the other way round (each row's pixels moved so that its spine lies mirrored about the sprites' middle column, the
light on them unchanged), in a light crackling differently round it, with other sparks: frame models coral_eel_5
and coral_eel_43 (no other enemy, launched ones included, shows any of these four sprites; none of them is another
sprite's pixels mirrored, turned or in other ramps, in any sheet).

As the sprites and their 4x upscales draw it (columns and rows of the 24 x 56 picture, the first frame): the eel's
spine wanders down the picture in a gentle S (its middle at column 13 of rows 1-3, 15 of rows 9-13, 13 of rows 21-28,
15 of rows 35-40, 14 at the head: 1 to 3 pixels right of the sprites' middle), a body 6 pixels wide of ramp 1's
browns (0x16 at its edges, 0x18-0x19, 0x1a-0x1b along its back, lighter flecks 0x1c-0x1e), its tail at the top
narrowing over rows 1-5 to a blunt end; the head at the bottom (rows 48-55), 8 pixels wide, with two slanted blue
eyes (ramp 3, 0x3a-0x3e: columns 11-12 and 15-16 of rows 49-52, drawing closer towards the snout) either side of a
light ridge, narrowing to the snout at row 55; round the body (not the head) the light: 3-4 pixels a side, teal next
to the body (0x86), paler outwards (0x88, 0x8a) to a jagged pale rim (0x8d, 0x8f), its outline as ragged as sparks;
and a few white sparks (0x7f) a pixel or two outside it.

Built as such a creature in its light: the body lofted along the spine (cross-sections a little flattened, a low
crest along the back), its belly on the floor, the tail's end rounded, the head broader and flatter, narrowing to the
snout; painted in bands of ramp 1 cut along smooth contours (polish_orb_red.band_split) by how much each part faces
up (dark flanks 0x14-0x16, the back 0x19-0x1a), mottled with lighter flecks (0x1c); the eyes glowing lenses sunk into
the head (pale blue 0x3e over 0x3c, emission 0.62 and 0.5), each in a dark socket (0x14). The light a cushion it lies
in: a heightfield over the sprite's light (its outline the sprite's own ragged one, a little smoothed, crackling with
a little noise), rising from the floor at its rim to the eel's flanks, see-through (alpha 0.6-0.74) and glowing in
its own colours (0.44-0.62, brightest at the rim), banded as the sprite's own shades lie (blurred: teal 0x86 by the
body, 0x88, 0x8a, pale 0x8d at the rim); the sparks small glowing beads (0x8f, 0.6). The second frame is the first
one's body mirrored (x -> -x) in the second frame's light and sparks.

The game draws see-through materials blended, without depth writes or culling, after everything opaque, in the
order of their materials and then of their triangles: the cushion is one sheet (no underside; the floor is under it),
the parts of it under the eel's body are left out (the body hides them), and its faces are sorted from the camera's
far side to its near side (the model doesn't turn), so that where the slanted camera sees through two layers of it
the far one is drawn first.

The whole is built and cut along the sprites' edge (y = 0: polish_arch.cut for the solid parts, the body's cut
closed in its brown, which shows only when a piece is shot away; the light's sheet is cut open), each piece moved so
that its sprite's centre is its origin, every mesh triangulated (polish_k_pod.triangulate: the same output with and
without --check) and its parts joined into one mesh.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the floor (z = 0). The whole's
origin is the middle of the picture's width on the edge between the two sprites: column c is x = c + 0.5 - 12, row r
is y = 27.5 - r. The pieces' centres: 3 and 5 (0, 14), 41 and 43 (0, -14). models.cfg (model lines unchanged): model
coral_eel_t / coral_eel_b enemies/coral_eel_*.glb origin; sprite x27 3 coral_eel_t yaw=0 height=-4 glow=20:0.25:138
and sprite x27 41 coral_eel_b yaw=0 height=-4 glow=20:0.25:138 (height=-4 lays it on the sea floor: drawn at their
origin, ground pieces otherwise float 4 pixels over the terrain); new: model coral_eel_5 / coral_eel_43
enemies/coral_eel_*.glb origin, frame x27 5 coral_eel_5, frame x27 43 coral_eel_43.

Replaces wave3_ae_coral.py's eel (its section "' 3 / 41: the electric eel": EEL, EEL_Z, eel_centre(), eel_whole(),
the kit.PROTECT line naming eel_aura and eel_body, the kit.pieced("coral_eel", ...) registration, its docstring
paragraph; halves() stays, the worm and the egg use it) and wave3_ae_art.py's EEL and EEL_B (read only by that
section; EEL_B by nothing): remove them so that they don't overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of each
frame's whole and of each piece against enemy_x27.png, the light made opaque for them), --preview <prefix> (each
frame's whole: top and 3/4 views; --pieces 1 also each piece's), --only <model,...>, --whole <prefix> (the uncut
wholes as <prefix>A.glb, <prefix>B.glb, for looking at), --stats 1 (the wholes' largest parts).
"""
import math
import os
import sys

import bmesh
import bpy
import mathutils.noise as noise
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_arch import cut  # noqa: E402
from polish_deli_boss import join  # noqa: E402
from polish_orb_red import band_split, smoothstep  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402

BOX_T, BOX_B = (-12.0, 12.0, 0.0, 28.0), (-12.0, 12.0, -28.0, 0.0)
FRAMES = [("A", (3, 41), [("coral_eel_t", 3, BOX_T), ("coral_eel_b", 41, BOX_B)]),
          ("B", (5, 43), [("coral_eel_5", 5, BOX_T), ("coral_eel_43", 43, BOX_B)])]

# The two frames' pictures (24 x 56, 3 above 41 and 5 above 43): the light's pixels by their shade of ramp 8
# (6 0x86, 8 0x88, a 0x8a, d 0x8d, f 0x8f), '#' the eel's body, 'E' its eyes, '*' a spark (0x7f), '.' none.
PICTURES = {
    "A": [
        "..........da88ad........", "........da86##66ad......", ".......daa8####8afd.....", "......*.d86####66ad.....",
        "........da66####68ad....", "........da66####8ad.....", "........a86######6ad....", ".......dda8######68ad...",
        "........a88######66ad...", "........da66######68ad..", "........da86######88a.*.", "........da86######8aa...",
        "........da86######6add..", "........d866######68fd..", ".......daa8######66ad...", ".......dda8######68ad...",
        "......*.da8######8aad...", "........d88######8add...", ".......da86######68d....", ".......da86######68a....",
        "......dda66######68ad...", ".......a86#######6ad....", ".......a86######68ad....", "......da88######88a.....",
        "......daa6######8ad.....", ".......d86######8add....", "......daa6######8aad....", "......da88######68ad....",
        ".....*.d86######66ad....", ".......da66######68a....", ".......da88######68ad...", "........da6######68ad...",
        "........a86######68ad...", ".......da86######68a....", ".......da86######8ad....", "........da66######aad...",
        "........da86######8add..", ".......*fda8######6ad...", "........daa8######68ad..", "........da86######88ad..",
        "........a866######68d...", ".......da86######66ad...", ".......da88######68a....", "........aa8######8ad.*..",
        "........da8######8ad....", ".......dd86######88a....", ".......da86######68ad...", "........da8######8ad....",
        ".........d########d.....", "..........#E####E#......", "..........#EE##EE#......", "..........#EE##EE#......",
        "...........#E##E#.......", "...........######.......", "............####........", ".............##.........",
    ],
    "B": [
        "........da88ad..........", "......da86##66ad........", ".....da86####68ad*......", ".....da66####68ad*......",
        "....da86####66ad........", "....daa8####668ad.......", "..*.d86######68ad.......", "...da86######8aad.......",
        "...da66######68a........", "...a86######66ad........", "..da88######8aad........", "...da8######8ad.........",
        "..dda8######68ad*.......", "..da86######66ad........", "...da66######68d........", "...da86######68ad.......",
        "...da88######8ad........", "....da8######6ad........", "..*dda8######68a........", "...da88######68ad.*.....",
        "...da86######66ad.......", "....da66######68d.......", "....da86######68ad......", "....da86######88ad......",
        "...*fda8######8aa.......", "..*.daa8######8ad.......", "....da86######6ad.......", "....da86######68ad......",
        "....da66######68a.......", "...da86######66ad.......", "...da86######68ad.......", "...daa8######68d.*......",
        "....d88######68a........", "...da86######68ad.......", "...da66######68ad.......", "..da86######66ad........",
        "..da86######68ad........", "...da8######8ad.........", "...da8######6aa.*.......", "..da86######68ad........",
        "..da86######66ad........", "...da66######68a........", "...da86######8aad.......", "...da88######8ad........",
        "...daa8######8add.......", "...dd86######88ad.......", "...da86######68ad.......", "..*.da8######8ad........",
        ".....d########d.*.......", "......#E####E#..........", "......#EE##EE#..........", "......#EE##EE#..........",
        ".......#E##E#...........", ".......######...........", "........####............", ".........##.............",
    ],
}
LIGHT_ROWS = 49                      # the light reaches down to row 48 (the head's rows have none)

VIEW_TILT = 20.0
T = math.radians(VIEW_TILT)
TOWARDS_VIEW = Vector((0.0, -math.sin(T), math.cos(T)))

# --- The eel (the first frame; the second is its mirror image) -----------------------------------------------------
# Its spine: (y, x) from the snout's point up to the tail's end, a Catmull-Rom curve through them.
SPINE = [(-28.0, 2.0), (-22.5, 2.0), (-16.5, 2.1), (-10.0, 3.0), (-4.0, 2.0), (3.0, 1.0), (10.5, 2.0), (16.5, 3.0),
         (21.5, 2.0), (25.5, 1.1), (27.1, 1.0)]
# Along it (y): the half-width, the height of its back over the floor, the axis' height.
WIDTH = [(-28.0, 0.25), (-27.5, 1.0), (-26.5, 2.0), (-25.5, 2.85), (-24.5, 3.35), (-23.0, 3.9), (-21.5, 4.0),
         (-20.5, 3.75), (-19.5, 3.15), (-18.5, 3.0), (20.5, 3.0), (21.5, 2.7), (22.5, 2.25), (24.5, 2.0), (25.5, 1.85),
         (26.4, 1.3), (26.9, 0.6), (27.1, 0.2)]
BACK = [(-28.0, 1.2), (-27.0, 2.3), (-25.0, 3.6), (-22.0, 4.15), (-19.5, 4.45), (-17.0, 4.7), (20.0, 4.7),
        (24.0, 4.0), (26.5, 3.2), (27.1, 2.4)]
AXIS = [(-28.0, 1.1), (-25.0, 1.9), (-21.0, 2.25), (-17.0, 2.45), (20.0, 2.45), (26.0, 2.1), (27.1, 1.8)]
BELLY = 0.2                          # the belly's lowest point over the floor
CREST = 0.25                         # the crest along the back
SECTION = 16
STEP = 0.55                          # cross-sections this far apart along y
# Its shades (ramp 1, 0-15): by how much a part faces up (its sides SIDE, its back BACK_SHADE, its belly UNDER),
# mottled by MOTTLE (smooth noise MOTTLE_SCALE pixels across).
SIDE, BACK_SHADE, UNDER, MOTTLE, MOTTLE_SCALE = 3.6, 9.9, 3.0, 0.8, 1.5
FACING = 1.3                         # how sharply the shade rises towards the back
BODY_BANDS = [(-99.0, 0x14), (4.3, 0x16), (6.3, 0x18), (7.8, 0x19), (8.9, 0x1a), (10.1, 0x1c)]
BODY_FINISH = dict(metallic=0.1, roughness=0.3)
CUT_INDEX = 0x16
# The eyes: middle (x, y), half sizes along and across, lean (degrees, the top outwards), the light colours.
EYES = [((0.0, -23.0), (2.0, 0.92), 18.0), ((4.0, -23.0), (2.0, 0.92), -18.0)]
EYE_SINK, EYE_HEIGHT = 0.15, 0.55
SOCKET = (0.45, 0.1, 0.25)           # the dark socket round each eye: how much larger, its top over the head, its
                                     # half-height
EYE_MATS = [(0x3e, 0.62), (0x3c, 0.5)]

# --- The light -------------------------------------------------------------------------------------------------------
GRID = 0.5                           # the cushion's grid (pixels)
OUTLINE_BLUR, HEIGHT_BLUR, SHADE_BLUR = 0.7, 1.3, 0.75     # gaussian blurs (pixels) of the sprite's light
CRACKLE, CRACKLE_SCALE = 0.07, 1.6   # noise on its outline (in the blurred light's units), pixels across
EDGE_Z, INNER_Z = 0.08, 2.35         # the cushion's height at its rim and against the eel
RIM_SHADE = 13.0                     # the shade at its very rim (the last fraction of a pixel inside its outline)
HIDDEN = 0.55                        # the cushion is left out this far inside the body's outline
# (lowest shade, palette index, alpha, emission strength in its own colour)
LIGHT_BANDS = [(-99.0, 0x86, 0.6, 0.44), (6.6, 0x88, 0.62, 0.48), (8.4, 0x8a, 0.66, 0.54), (10.8, 0x8d, 0.74, 0.62)]
SPARK = (0x8f, 0.38, 0.6)            # the sparks: palette index, radius, emission


def X(c):
    return c + 0.5 - 12.0


def Y(r):
    return 27.5 - r


def curve(table, y):
    """Catmull-Rom through a table [(y, value)] (y ascending), clamped at its ends."""
    if y <= table[0][0]:
        return table[0][1]
    if y >= table[-1][0]:
        return table[-1][1]
    for i in range(len(table) - 1):
        y0, y1 = table[i][0], table[i + 1][0]
        if y <= y1:
            t = (y - y0) / (y1 - y0)
            p0 = table[max(i - 1, 0)][1]
            p1, p2 = table[i][1], table[i + 1][1]
            p3 = table[min(i + 2, len(table) - 1)][1]
            return 0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t +
                          (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)
    return table[-1][1]


def linear(table, y):
    if y <= table[0][0]:
        return table[0][1]
    for (y0, a), (y1, b) in zip(table, table[1:]):
        if y <= y1:
            return a + (b - a) * (y - y0) / (y1 - y0)
    return table[-1][1]


# --- Materials -------------------------------------------------------------------------------------------------------

def materials():
    pal = k.level_palette()
    m = {}
    for _, index in BODY_BANDS:
        m[index] = k.material(f"eel_{index:02x}", palette=index, **BODY_FINISH)
    for index, glow in EYE_MATS:
        m[index] = k.material(f"eel_eye_{index:02x}", palette=index, metallic=0.0, roughness=0.15,
                              emission=pal[index], emission_strength=glow)
    for _, index, alpha, glow in LIGHT_BANDS:
        m[index] = k.material(f"eel_light_{index:02x}", palette=index, metallic=0.0, roughness=0.25, alpha=alpha,
                              emission=pal[index], emission_strength=glow)
    index, _, glow = SPARK
    m["spark"] = k.material(f"eel_spark_{index:02x}", palette=index, metallic=0.0, roughness=0.3,
                            emission=pal[index], emission_strength=glow)
    return m


# --- The eel ---------------------------------------------------------------------------------------------------------

def spine_x(y):
    return curve(SPINE, y)


def body(m):
    """The eel lofted along its spine, painted in bands by how much it faces up; returns the object."""
    y0, y1 = SPINE[0][0], SPINE[-1][0]
    count = int(round((y1 - y0) / STEP))
    ys = [y0 + (y1 - y0) * i / count for i in range(1, count)]
    rings, ups = [], []
    for y in ys:
        cx = spine_x(y)
        slope = (spine_x(y + 0.05) - spine_x(y - 0.05)) / 0.1
        across = Vector((1.0, -slope, 0.0)).normalized()      # perpendicular to the spine in plan
        w, back, axis = curve(WIDTH, y), linear(BACK, y), linear(AXIS, y)
        top, bottom = back - axis, axis - BELLY
        ring, up = [], []
        for j in range(SECTION):
            a = 2 * math.pi * j / SECTION
            c, s = math.cos(a), math.sin(a)
            px = math.copysign(abs(c) ** (2 / 2.3), c) * w
            pz = math.copysign(abs(s) ** (2 / 2.3), s) * (top if s >= 0 else bottom)
            if s > 0:
                pz += CREST * s ** 8
            ring.append(Vector((cx, y, axis)) + across * px + Vector((0.0, 0.0, pz)))
            up.append(s)
        rings.append(ring)
        ups.append(up)
    snout = Vector((spine_x(y0), y0, linear(AXIS, y0)))
    tail = Vector((spine_x(y1), y1, linear(AXIS, y1)))
    obj = k.loft("eel_body", rings, m[0x18], start_point=snout, end_point=tail)
    values = []
    for v in obj.data.vertices:
        i = v.index
        if i < len(rings) * SECTION:
            s = ups[i // SECTION][i % SECTION]
        else:
            s = 0.2
        shade = SIDE + (BACK_SHADE - SIDE) * max(0.0, s) ** FACING if s >= 0 else SIDE + (UNDER - SIDE) * (-s)
        shade += MOTTLE * noise.noise(v.co * (1.0 / MOTTLE_SCALE) + Vector((2.3, 5.1, 0.7)))
        values.append(shade)
    band_split(obj, values, [(lowest, m[index]) for lowest, index in BODY_BANDS])
    close_holes(obj)
    return k.smooth(obj, 70)


def close_holes(obj):
    """Fills any hole the band cuts left in a closed body (a degenerate face dropped), in its neighbours' material."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    edges = [e for e in bm.edges if e.is_boundary]
    if edges:
        made = bmesh.ops.holes_fill(bm, edges=edges, sides=0)["faces"]
        for fc in made:
            near = [lp.link_loop_radial_next.face for lp in fc.loops if lp.link_loop_radial_next.face is not fc]
            if near:
                fc.material_index = near[0].material_index
        bmesh.ops.triangulate(bm, faces=made)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()


def head_top(x, y):
    """The top of the eel's body at (x, y) (approximately: its cross-section's upper half there)."""
    w, back, axis = curve(WIDTH, y), linear(BACK, y), linear(AXIS, y)
    u = min(1.0, abs(x - spine_x(y)) / max(w, 1e-3))
    return axis + (back - axis) * (1.0 - u ** 2.3) ** (1.0 / 2.3)


def eyes(m):
    """The eyes: lens-shaped ellipsoids sunk into the head, their upper parts the lighter blue, each in a dark socket
    (a flat ellipsoid a little larger, just above the head's surface)."""
    out = []
    grow, lift, depth = SOCKET
    for i, ((ex, ey), (ha, hc), lean) in enumerate(EYES):
        z = head_top(ex, ey) - EYE_SINK
        place = Matrix.Translation((ex, ey, z)) @ Matrix.Rotation(math.radians(lean), 4, "Z")
        eye = mk.ball(f"eel_eye{i}", (0.0, 0.0, 0.0), (hc, ha, EYE_HEIGHT), m[EYE_MATS[0][0]], 16, 10)
        mk.paint(eye, lambda c, n: m[EYE_MATS[1][0]] if c.y < -0.15 * ha or n.z < -0.2 else None)
        eye.data.transform(place)
        socket = mk.ball(f"eel_socket{i}", (0.0, 0.0, 0.0), (hc + grow, ha + grow, depth), m[0x14], 16, 8)
        socket.data.transform(Matrix.Translation((ex, ey, head_top(ex, ey) + lift - depth)) @
                              Matrix.Rotation(math.radians(lean), 4, "Z"))
        out += [eye, socket]
    return out


# --- The light -------------------------------------------------------------------------------------------------------

def blur(a, sigma, scale):
    """A gaussian blur (sigma in pixels) of an array sampled scale times a pixel."""
    s = sigma * scale
    r = int(math.ceil(3 * s))
    xs = np.arange(-r, r + 1)
    kern = np.exp(-0.5 * (xs / s) ** 2)
    kern /= kern.sum()
    out = np.apply_along_axis(lambda v: np.convolve(np.pad(v, r, mode="edge"), kern, mode="valid"), 0, a)
    return np.apply_along_axis(lambda v: np.convolve(np.pad(v, r, mode="edge"), kern, mode="valid"), 1, out)


class LightFields:
    """The sprite's light as smooth fields over the picture: inside (its outline at 0.5), height and shade."""
    SCALE = 4

    def __init__(self, picture):
        h, w = 56, 24
        s = self.SCALE
        light = np.zeros((h, w))
        cover = np.zeros((h, w))
        shade = np.zeros((h, w))
        for r, row in enumerate(picture[:LIGHT_ROWS]):
            for c, ch in enumerate(row):
                if ch in "68adf":
                    light[r, c] = 1.0
                    cover[r, c] = 1.0
                    shade[r, c] = int(ch, 16)
                elif ch in "#E":
                    cover[r, c] = 1.0
        up = lambda a: np.kron(a, np.ones((s, s)))  # noqa: E731
        pad = 4 * s
        cov = np.pad(up(cover), pad)
        self.inside = blur(cov, OUTLINE_BLUR, s)
        self.height = blur(cov, HEIGHT_BLUR, s)
        lit = np.pad(up(light), pad)
        weight = blur(lit, SHADE_BLUR, s)
        self.shade = blur(np.pad(up(shade * light), pad), SHADE_BLUR, s) / np.maximum(weight, 1e-6)
        self.shade[weight < 1e-4] = 6.0
        self.pad = pad

    def sample(self, field, x, y):
        """Bilinear at (x, y) (the whole's coordinates)."""
        s = self.SCALE
        fx = (x + 12.0) * s + self.pad - 0.5
        fy = (27.5 + 0.5 - y) * s + self.pad - 0.5
        h, w = field.shape
        x0, y0 = int(math.floor(fx)), int(math.floor(fy))
        tx, ty = fx - x0, fy - y0
        x0, y0 = max(0, min(w - 2, x0)), max(0, min(h - 2, y0))
        a, b = field[y0, x0], field[y0, x0 + 1]
        c, d = field[y0 + 1, x0], field[y0 + 1, x0 + 1]
        return (a * (1 - tx) + b * tx) * (1 - ty) + (c * (1 - tx) + d * tx) * ty


def body_inside(x, y, spine):
    """How far inside the body's outline (x, y) is (pixels; negative outside)."""
    if y < SPINE[0][0] or y > SPINE[-1][0]:
        return -9.0
    return curve(WIDTH, y) - abs(x - spine(y))


def light(m, picture, mirrored):
    """The cushion: a sheet over the sprite's light, cut along its outline, its parts under the body left out, banded
    by the sprite's shades (each piece's faces are sorted far to near after the cut: sort_far_first)."""
    f = LightFields(picture)
    spine = (lambda y: -spine_x(y)) if mirrored else spine_x
    seed = Vector((7.7, 1.9, 4.4)) if mirrored else Vector((0.3, 5.2, 8.6))
    bm = bmesh.new()
    nx, ny = int(24 / GRID), int(50 / GRID)
    verts = {}
    for j in range(ny + 1):
        for i in range(nx + 1):
            verts[i, j] = bm.verts.new((-12.0 + i * GRID, 28.0 - j * GRID, 0.0))
    for j in range(ny):
        for i in range(nx):
            bm.faces.new((verts[i, j + 1], verts[i + 1, j + 1], verts[i + 1, j], verts[i, j]))
    inside = {v: f.sample(f.inside, v.co.x, v.co.y) + CRACKLE * noise.noise(Vector((v.co.x, v.co.y, 0.0)) *
                                                                            (1.0 / CRACKLE_SCALE) + seed)
              for v in bm.verts}
    mk.split_along(bm, inside, 0.5)
    for v in bm.verts:
        if v not in inside:
            inside[v] = 0.5
    gone = [fc for fc in bm.faces if sum(inside[v] for v in fc.verts) / len(fc.verts) < 0.5 or
            body_inside(fc.calc_center_median().x, fc.calc_center_median().y, spine) > HIDDEN]
    bmesh.ops.delete(bm, geom=gone, context="FACES")
    loose = [v for v in bm.verts if not v.link_faces]
    bmesh.ops.delete(bm, geom=loose, context="VERTS")
    for v in bm.verts:
        hgt = f.sample(f.height, v.co.x, v.co.y)
        rise = smoothstep(0.5, 0.97, hgt)
        # Against the eel it rises to its flanks.
        near = smoothstep(-2.6, -0.2, body_inside(v.co.x, v.co.y, spine))
        v.co.z = EDGE_Z + (INNER_Z - EDGE_Z) * max(rise, near * 0.9)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    mesh = bpy.data.meshes.new("eel_light")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("eel_light", mesh)
    bpy.context.scene.collection.objects.link(obj)
    values = []
    for v in mesh.vertices:
        s = f.sample(f.shade, v.co.x, v.co.y)
        rim = 1.0 - smoothstep(0.5, 0.64, f.sample(f.inside, v.co.x, v.co.y))
        values.append(s + (RIM_SHADE - s) * rim)
    band_split(obj, values, [(lowest, m[index]) for lowest, index, _, _ in LIGHT_BANDS])
    k.smooth(obj, 80)
    return obj


def sparks(m, picture):
    out = []
    index, radius, _ = SPARK
    for r, row in enumerate(picture):
        for c, ch in enumerate(row):
            if ch == "*":
                z = 1.3 + 0.5 * noise.noise(Vector((c * 0.7, r * 0.7, 3.3)))
                bead = mk.ball(f"eel_spark_{r}_{c}", (X(c), Y(r), z), (radius, radius, radius), m["spark"], 8, 5)
                out.append(bead)
    return out


def sort_far_first(obj):
    """The faces of the see-through materials last and from the camera's far side to its near side (their order is
    the game's drawing order); the others keep theirs."""
    blended = {i for i, mat in enumerate(obj.data.materials) if mat.surface_render_method == "BLENDED"}
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.faces.ensure_lookup_table()
    count = len(bm.faces)
    order = {fc: (count + 1000.0 + fc.calc_center_median().dot(TOWARDS_VIEW) if fc.material_index in blended
                  else float(fc.index)) for fc in bm.faces}
    bm.faces.sort(key=lambda fc: order[fc])
    bm.faces.index_update()
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


def mirror(objects):
    flip = Matrix.Scale(-1, 4, (1, 0, 0))
    for obj in objects:
        obj.data.transform(flip)
        obj.data.flip_normals()
        obj.data.update()


def build_whole(m, frame):
    """The eel (mirrored for the second frame) in its frame's light, with its sparks: (solid parts, the light)."""
    picture = PICTURES[frame]
    eel = [body(m)] + eyes(m)
    for obj in eel:
        mk.apply(obj)
    if frame == "B":
        mirror(eel)
    glow = light(m, picture, frame == "B")
    solid = eel + sparks(m, picture)
    for obj in solid + [glow]:
        mk.apply(obj)
    bpy.context.view_layer.update()
    return solid, glow


# --- Cutting, checks and export ---------------------------------------------------------------------------------------

def cut_open(source, box):
    """The part of an open sheet inside box (x0, x1, y0, y1), its cuts left open; None if nothing is inside."""
    x0, x1, y0, y1 = box
    obj = source.copy()
    obj.data = source.data.copy()
    bpy.context.scene.collection.objects.link(obj)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    planes = (((x0, 0, 0), (-1, 0, 0)), ((x1, 0, 0), (1, 0, 0)), ((0, y0, 0), (0, -1, 0)), ((0, y1, 0), (0, 1, 0)))
    for co, no in planes:
        if not bm.faces:
            break
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6, plane_co=co, plane_no=no,
                               clear_outer=True)
    empty = not bm.faces
    bm.to_mesh(obj.data)
    bm.free()
    if empty:
        bpy.data.objects.remove(obj)
        return None
    return obj


def opaque_coverage(objects, w, h):
    """The top view's coverage with the see-through materials made opaque for it (polish_plasma_ball.py's)."""
    saved = []
    for mat in {mt for obj in objects for mt in obj.data.materials}:
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        saved.append((mat, bsdf.inputs["Alpha"].default_value, mat.surface_render_method))
        bsdf.inputs["Alpha"].default_value = 1.0
        mat.surface_render_method = "DITHERED"
    covered = mk.coverage(objects, w, h)
    for mat, alpha, method in saved:
        mat.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = alpha
        mat.surface_render_method = method
    return covered


def whole_mask(sheet, sprites):
    mask = [[False] * 24 for _ in range(56)]
    for sprite, r0 in zip(sprites, (0, 28)):
        for r, row in enumerate(k.sprite_mask(sheet, sprite)):
            for c, v in enumerate(row):
                mask[r0 + r][c] = v
    return mask


def export_frame(frame, sprites, pieces, options, sheet, out):
    only = options["only"].split(",") if "only" in options else None
    wanted = [p for p in pieces if not only or p[0] in only]
    if not wanted and "whole" not in options and "preview" not in options:
        return
    k.reset()
    m = materials()
    solid, glow = build_whole(m, frame)
    whole = solid + [glow]
    triangulate(whole)  # the cuts are the same every run (with and without --check)
    low, high = mk.bounds(whole)
    print("== whole, frame %s: %d triangles, %d materials, x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (
        frame, mk.triangles(whole), len(mk.materials_of(whole)), low.x, high.x, low.y, high.y, low.z, high.z))
    if "stats" in options:
        for obj in sorted(whole, key=lambda o: -mk.triangles([o]))[:6]:
            print("    %-22s %6d" % (obj.name, mk.triangles([obj])))
    mask = None
    if sheet:
        mask = whole_mask(sheet, sprites)
        mk.compare("whole, frame %s (x27 %d above %d)" % ((frame,) + sprites), opaque_coverage(whole, 24, 56), mask)
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    if "preview" in options:
        mk.preview(options["preview"] + "coral_eel_whole%s" % frame, whole, size=(24, 56), scale=12, distance=1.5)
    if "whole" in options:
        mk.export(whole, options["whole"] + "%s.glb" % frame)
    for name, sprite, box in wanted:
        parts = [cut(src, box, m[CUT_INDEX]) for src in solid] + [cut_open(glow, box)]
        parts = [p for p in parts if p is not None]
        mk.transform(parts, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
        bpy.context.view_layer.update()
        triangulate(parts)
        parts = [join(parts, name)]
        sort_far_first(parts[0])
        for src in whole:
            src.hide_render = True
        if mask is not None:
            r0 = int(28 - box[3])
            mk.compare("%s (x27 %d)" % (name, sprite), opaque_coverage(parts, 24, 28), mask[r0:r0 + 28])
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options and options.get("pieces") == "1":
            mk.preview(options["preview"] + name, parts)
        for obj in parts:
            bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False


def build():
    options = k.args()
    out = mk.outdir(options)
    sheet = None
    if "check" in options:
        sheets = options["check"]
        sheet = os.path.join(sheets, "enemy_x27.png") if os.path.isdir(sheets) else sheets
    for frame, sprites, pieces in FRAMES:
        export_frame(frame, sprites, pieces, options, sheet, out)


if __name__ == "__main__":
    build()
