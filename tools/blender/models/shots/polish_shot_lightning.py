"""The lightning bolts (shots sheet sprites 191-200, 210-213, 229-232, 248-251 and 267-270, all 1x1: 12 x 14 cells),
modelled (2026-10-30, round 3 of the energy shots' models; until then each was drawn as its sprite with volume, flat,
from the 4x sheets, with the automatic glow: separate blue blobs with white zig-zags, a column of them with gaps).

Who fires them (weapons as the item data numbers them):
  The Lightning Cannon (front port 8, first sold in episode 1's shop 15, weapons 232-242 for power levels 1-11), every
    6 game frames (shotrepeat 5; power 10 every 3, 11 every 2), straight up the screen at 22 pixels a frame:
      power 1-6: a column of 3-5 segments of the narrow bolt 191, one above the other 14 pixels apart (by -22, -8, 6,
        20, 34), so that they join into one bolt; a player's shot shows weapani + 1 frames (shots.c shotAniMax): every
        segment shows 191, 192, 193 by turns, all of a column the same frame at once (they are fired together);
      power 3-4: one or two more 191s flying down the screen (sy -12), drawn as they are;
      power 5-9: two diagonal bolts flying up and out at 45 degrees (sx -/+10, sy 10; del 101: two frames), 194 and
        195 by turns up and left, 196 and 197 up and right (power 6, 8, 9: two of each);
      power 7-11: the big column in place of the 191s: four pieces one above the other 14 pixels apart (210 at by -22,
        229, 248, 267 at by 20), each animating in four frames (del 103: 210 211 212 213; 229-232; 248-251; 267-270,
        the fourth frame the first again), all four the same frame at once; power 10 one column 8 pixels left, power 11
        two, 8 left and 8 right.
  The sidekick Companion Ship Quicksilver (port 16's weapon 233: a column of four 191s), the specials Lightning UP
    (weapon 721: eight segments, 192 and 191 by turns, each animating to the next sprite: 192 193, 191 192), UP+LEFT
    and UP+RIGHT (722, 723: eight diagonal segments in a line, 194 195 / 196 197 by turns, not animated), LEFT and RIGHT
    (724, 725: the sideways bolts, see below), Lightning Zone (750: two 191s) and Dragon Lightning (1025: one big
    column).
  Enemies (an enemy's shot shows weapani frames): in episodes 4 and 5 weapons 139 (eight segments falling 8 pixels a
    frame, 192 and 191 by turns, not animated), 140 and 141 (eight diagonal segments in a line, 196 197 / 194 195 by
    turns): SURFACE's turret (enemy 249, sheet ^), and once fire override events give them a frequency CORE, SIDE EXIT,
    UNDERDELI, ICE EXIT, LAVA EXIT, LAVA RUN, BRAINIAC (enemies 178, 181), DREAD-NOT and NOSE DRIP; weapon 149 (one 191
    falling slowly, animating through 191-198: BONUS, MISTAKES, FLEET, STARGATE) and 150 (three, through 191-196:
    FLEET, MINERS, STATION); weapon 242 (the Lightning Cannon's power 11: two big columns animating 210 211 ...: CORAL,
    EYESPY, LAVA RUN, MINERS); 123, 124, 151 and 152 the sideways bolts (LAVA EXIT, SURFACE, TIME WAR, STATION).
  The sideways bolts 198-200: the specials Lightning LEFT and RIGHT and the enemies' weapons 123, 124, 151, 152 fire
    eight segments in a row 12 pixels apart (bx 0, -/+12 ... -/+84), 198 and 199 by turns, flying sideways at 22 pixels
    a frame (the player's animate to the next sprite: 198 199, 199 200).

As the sprites draw them (ramp 9's blues, 0x90 near black to 0x9f sky blue, with ramp 8's and ramp 3's whites): each is
a jagged bolt 3-5 pixels across, its edges dark blue (0x92-0x94), blue (0x96-0x9b) and a light core a pixel or two wide
(0x9c-0x9f) that flashes white (0x8f, 0x8d) in places. 191 and 192 are one zig-zag down the cell (191 out to the right
and back, 192 out to the left), 193 a bolt that splits into two strands and joins again (an eye); stacked they make one
long bolt, the ends a pixel or two apart where they meet. 194 is a wide bolt from the cell's top left corner to its
bottom right, a bright knot in its upper half (0x8d, 0x8b) under a dim arch; 195 a thin, dim bolt the same way; 197 and
196 their mirror images. 198, 199 and 200 are thin bolts lying across the cell, waving up and down (198 bright, white at
its first wave). The big column (210 over 229 over 248 over 267, 12 pixels wide and 50 rows long) is a channel of blue
plasma, darker at its edges and tapering at both ends, with white-hot lightning (ramp 3's 0x3e, 0x3f) zig-zagging down
it in strands that split and join, different in each frame.

The models: every bolt is a tube of light along its sprite's path (traced by hand from the pixels, its corners kept
sharp), round on top and flat underneath (a half-body: the game's camera only sees shots from above), 2.9 pixels wide
where it is hottest and down to 0.84 of that where it is dim (195, 196 and the sideways bolts 2.3), its section in
longitudinal bands of ramp 9: dark blue at its edges (0x95), blue (0x9a), and along its top a raised core ridge in the
core's colour: light blue (0x9d), lighter (0x9f) and white (0x8f, ramp 8) where the sprite's core flashes white, by the
heat traced with the path (the mesh has a ring wherever the core's band changes, so no face is cut). Corners are mitred
(the tube turns sharply, as lightning does), the ends rounded. Every frame of a family is the same tube along another
path, so the frames read as one bolt flickering. Where segments join (a column of 191s, the diagonal and sideways
chains), each path ends on the same point of its cell's edge (191-193 the middle of the top and bottom edges, 194/195
and 196/197 the corners, 198-200 the middle of the side edges, half a pixel above the cell's centre): any two segments
meet exactly, whatever their frames (the sprites' ends lie up to 1.5 pixels apart). 306-666 triangles, 4-5 materials.
The big column: per frame, built whole and cut into its four pieces at the cells' edges (each piece moved onto its own
cell's centre; models.cfg's model lines take "origin" so that the pieces meet, their shot lines height=-1.6, half the
column's height, to centre it in height as the other shots are): a sheath of plasma lofted along the column's outline
row by row (each row's pixels from 0x91 up, smoothed), flattened (0.42 times its half-width high), in bands across it
(0x94 at its edges, 0x97, 0x9a along its middle), and the strands of lightning as the same tubes lying on it (closed
underneath, inside the sheath), their cores white (0x3f, 0x3e) and light blue (0x9e) where they dim, light blue (0x9d)
round them. 384-1264 triangles a piece, 5-7 materials. Each band glows in its own colour by its shade (CONVENTIONS 4:
0.31-0.62). Each shot line's glow= (in place of the automatic glow, 13 pixels at 0.7 in the sprite's brightest colour,
a white haze) is a light blue halo (0x9d), weak (0.3-0.42) because the segments' halos overlap along a column.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the origin at the
sprite's centre (pixel 6, 7 of the cell: column c is x = c + 0.5 - 6, row r is y = 6.5 - r, its top edge y = 7 - r);
the bolts stand on z = 0 (the game centres shot models in height on the player's layer; the column's pieces are drawn
at their origin and lowered by height=).

models.cfg: the build prints the model and shot lines (cfg_lines(): GLOW, COLUMN_GLOW, COLUMN_HEIGHT).

Run: Blender -b --factory-startup -P tools/blender/models/shots/polish_shot_lightning.py -- [--only <name,...>]
     [--outdir <dir>] (default assets/models/shots) [--check <sheets dir>] (each model's top view against its sprite in
     <dir>/shots.png, from TYR3D_EXTRACT) [--preview <prefix>] (top, three-quarter and game-camera views, and
     <prefix>chains_game.png / chains_top.png: the segments joined as the game fires them)
"""
import math
import os
import sys

import bpy
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
ENEMIES = os.path.join(HERE, "..", "enemies")
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, ENEMIES)
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_launched_flames import lit, check_frames, turn  # noqa: E402
from polish_shot_starburst import glow_of, game_camera  # noqa: E402

OUTDIR = os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "shots")


def P(col, row):
    """A point of the cell in model coordinates from the sprite's (column, row) (fractions allowed)."""
    return (col + 0.5 - 6.0, 6.5 - row)


# --- The tube ---------------------------------------------------------------------------------------------------------
# A tube along a path in the plane, round on top and flat underneath: its section a half-ellipse DEPTH times its
# half-width high, with a ridge along its top (the core: CORE_U of the half-width either side of the middle, standing
# CORE_LIFT pixels out of the tube); its bands along it: (from u, the band) out from the middle (u 0) to the edge (1),
# the first the core (its palette index by the path's heat), the rest fixed. The underside takes the edge's band.


def last_band(bands, value):
    """The palette index of the last of bands ((lowest value, index), ascending) whose lowest value is reached."""
    index = bands[0][1]
    for lowest, i in bands:
        if value >= lowest - 1e-9:
            index = i
    return index


class Section:
    def __init__(self, half, depth, core_u, core_lift, bands, core_bands, roughness=(0.4, 0.5), extra=()):
        self.half, self.depth, self.core_u, self.core_lift = half, depth, core_u, core_lift
        self.bands = bands  # ((from u, palette index), ...), the core first (its index None: by heat)
        self.core_bands = core_bands  # ((lowest heat, palette index), ...) coolest first
        self.roughness = roughness  # (the core's, the rest's)
        self.extra = extra  # more section points (u) between the bands' borders, for roundness

    def us(self):
        """The section's points out from the middle: 0, the core's edge, every band border, the edge."""
        points = sorted({0.0, 1.0, self.core_u} | {b[0] for b in self.bands[1:]} | set(self.extra))
        return points

    def z(self, u, w):
        """The section's height at u (0 the middle, 1 the edge) for a half-width w."""
        u = min(abs(u), 1.0)
        body = self.depth * w * math.sqrt(max(0.0, 1.0 - u * u))
        if u < self.core_u - 1e-9:
            body += self.core_lift * (w / self.half) * math.sqrt(max(0.0, 1.0 - (u / self.core_u) ** 2))
        return body

    def band_of_strip(self, u0, u1):
        """The band (index into bands) of the strip between u0 and u1 (0 <= u0 < u1 <= 1)."""
        mid = (u0 + u1) / 2
        return max(i for i, b in enumerate(self.bands) if mid >= b[0] - 1e-9)

    def core_index(self, heat):
        """The core's palette index at a heat: the last of core_bands (coolest first) whose lowest heat it reaches."""
        return last_band(self.core_bands, heat)


# The bolts' section: 2.9 pixels wide (where the bolt is hottest; down to 0.84 of it where it is dim), a half-ellipse
# 0.62 times as high as wide, a core ridge 0.4 of the half-width either side of the middle standing 0.36 pixels out of
# it; bands out from the core: blue (0x9a), dark blue at the edge (0x95); the core light blue (0x9d), lighter (0x9f)
# and white (0x8f) by the heat traced with the path (in the shades of ramp 9; 16 = white).
BOLT = Section(1.45, 0.62, 0.4, 0.36, ((0.0, None), (0.4, 0x9a), (0.74, 0x95)),
               ((-99.0, 0x9d), (10.5, 0x9f), (14.0, 0x8f)), extra=(0.88,))
THIN = Section(1.15, 0.62, 0.42, 0.3, ((0.0, None), (0.42, 0x9a), (0.76, 0x95)),
               ((-99.0, 0x9d), (10.5, 0x9f), (14.0, 0x8f)), extra=(0.88,))
# The column's strands: a white core (0x3f, 0x3e where it dims, light blue 0x9e where the sprite's strand is blue),
# light blue (0x9d) round it.
STRAND = Section(1.2, 0.6, 0.45, 0.3, ((0.0, None), (0.45, 0x9d)),
                 ((-99.0, 0x9e), (12.5, 0x3e), (15.5, 0x3f)), extra=(0.78,))
CAP = 0.62  # a rounded end reaches this many half-widths past its last point
CAP_RINGS = (0.5, 0.82)  # (sines of the cap's angles: its rings)
MITRE_MAX = 1.9
SNAP = 0.45  # (pixels: a core band's border nearer a corner than this moves onto the corner's ring)


def thickness(heat):
    """The bolt's width at a heat, against its full width: the hot flashes full, the dim stretches thinner (the pins'
    heat 11 the same in every frame, so that segments meet at one width)."""
    return 0.84 + 0.16 * min(max((heat - 6.0) / 9.0, 0.0), 1.0)


def material(index, roughness):
    """One material per palette index (glowing in its own colour by its shade); the white and light cores smoother."""
    return lit(f"lightning_{index:02x}", index, glow_of(index & 15), roughness=roughness)


def resample(points, heats, section, step=None):
    """The rings' places along a path: its points (corners), each core band's border where the heat crosses it on a
    straight run (not nearer a corner than SNAP), and (step) points every step pixels for tubes lying on a curved
    surface. Returns [(x, y, heat, corner)]."""
    out = [(points[0][0], points[0][1], heats[0], True)]
    borders = [lowest for lowest, _ in section.core_bands[1:]]
    for i in range(len(points) - 1):
        (x0, y0), (x1, y1) = points[i], points[i + 1]
        h0, h1 = heats[i], heats[i + 1]
        length = math.hypot(x1 - x0, y1 - y0)
        ts = []
        for b in borders:
            if (h0 - b) * (h1 - b) < 0:
                t = (b - h0) / (h1 - h0)
                if t * length >= SNAP and (1 - t) * length >= SNAP:
                    ts.append(t)
        if step is not None and length > step:
            n = int(length / step)
            ts += [j / (n + 1) for j in range(1, n + 1)]
        for t in sorted(ts):
            out.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, h0 + (h1 - h0) * t, False))
        out.append((x1, y1, h1, True))
    return out


def tube(name, points, heats, section, materials, width=1.0, base=None, underside=True, step=None):
    """A tube along the path (points [(x, y)], heats per point), its section `section` at `width` times its half-width,
    mitred at the corners, its ends rounded; lying on z = 0 or (base) on a surface base(x, y) -> z, sunk a little into
    it; closed underneath (underside) or open. materials: {palette index: material}. Returns the object."""
    w = section.half * width
    pts = resample(points, heats, section, step)
    widths = [w * thickness(heat) for _, _, heat, _ in pts]
    n = len(pts)
    # Each ring's direction (the corners' bisector), its normal (to the left of the way along), its mitre.
    dirs = []
    for i in range(n - 1):
        dx, dy = pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]
        length = math.hypot(dx, dy) or 1e-9
        dirs.append((dx / length, dy / length, length))
    rings = []
    for i, (x, y, heat, corner) in enumerate(pts):
        if i == 0:
            d, m = dirs[0][:2], 1.0
        elif i == n - 1:
            d, m = dirs[-1][:2], 1.0
        else:
            a, b = dirs[i - 1], dirs[i]
            bx, by = a[0] + b[0], a[1] + b[1]
            bl = math.hypot(bx, by)
            if bl < 1e-6:
                d, m = b[:2], 1.0
            else:
                d = (bx / bl, by / bl)
                cos_half = max(d[0] * b[0] + d[1] * b[1], 1e-3)
                m = min(1.0 / cos_half, MITRE_MAX)
                # (the inner side mustn't reach past the next ring: short runs pinch the corner instead)
                sin_half = math.sqrt(max(0.0, 1.0 - cos_half * cos_half))
                if sin_half > 1e-6:
                    m = max(1.0, min(m, 0.85 * min(a[2], b[2]) / (widths[i] * sin_half)))
        nx, ny = -d[1], d[0]
        rings.append((x, y, heat, nx * m, ny * m, d))
    us = section.us()
    order = [u for u in reversed(us[1:])] + [-u for u in us]  # (from the right edge over the top to the left edge)
    # (the right edge: u > 0 along -normal, so that the ring runs from the right side to the left)

    def lift(x, y):
        return max(base(x, y) - 0.12, 0.0) if base is not None else 0.0

    verts, faces, bands = [], [], []

    def add_ring(x, y, nx, ny, wr, scale_w, scale_h, dx=0.0, dy=0.0):
        first = len(verts)
        for u in order:
            px, py = x + dx - nx * u * wr * scale_w, y + dy - ny * u * wr * scale_w
            verts.append((px, py, lift(px, py) + section.z(u, wr) * scale_h))
        return first

    starts = [add_ring(x, y, nx, ny, widths[i], 1.0, 1.0) for i, (x, y, _, nx, ny, _) in enumerate(rings)]
    strip_band = []
    for j in range(len(order) - 1):
        u0, u1 = sorted((abs(order[j]), abs(order[j + 1])))
        strip_band.append(section.band_of_strip(u0, u1))

    def index_of(band, heat):
        return section.core_index(heat) if section.bands[band][1] is None else section.bands[band][1]
    count = len(order)
    for i in range(n - 1):
        heat = (rings[i][2] + rings[i + 1][2]) / 2
        a, b = starts[i], starts[i + 1]
        for j in range(count - 1):
            faces.append((a + j, b + j, b + j + 1, a + j + 1))
            bands.append(index_of(strip_band[j], heat))
        if underside:
            faces.append((a + count - 1, b + count - 1, b, a))
            bands.append(section.bands[-1][1])
    # The rounded ends: rings shrinking past each end (a quarter of an ellipsoid), then a point.
    for end in (0, n - 1):
        x, y, heat, nx, ny, d = rings[end]
        sign = -1.0 if end == 0 else 1.0
        nl = math.hypot(nx, ny)
        nx, ny = nx / nl, ny / nl
        previous = starts[end]
        for s in CAP_RINGS:
            c = math.sqrt(1.0 - s * s)
            reach = sign * CAP * widths[end] * s
            ring = add_ring(x, y, nx, ny, widths[end], c, c, d[0] * reach, d[1] * reach)
            for j in range(count - 1):
                if end == 0:
                    faces.append((ring + j, previous + j, previous + j + 1, ring + j + 1))
                else:
                    faces.append((previous + j, ring + j, ring + j + 1, previous + j + 1))
                bands.append(index_of(strip_band[j], heat))
            if underside:
                if end == 0:
                    faces.append((ring + count - 1, previous + count - 1, previous, ring))
                else:
                    faces.append((previous + count - 1, ring + count - 1, ring, previous + count - 1 - count + 1))
                bands.append(section.bands[-1][1])
            previous = ring
        tip = len(verts)
        reach = sign * CAP * widths[end]
        tx, ty = x + d[0] * reach, y + d[1] * reach
        verts.append((tx, ty, lift(tx, ty)))
        for j in range(count - 1):
            faces.append((previous + j + 1, previous + j, tip) if end == 0 else (previous + j, previous + j + 1, tip))
            bands.append(index_of(strip_band[j], heat))
        if underside:
            faces.append((previous, previous + count - 1, tip) if end == 0 else (previous + count - 1, previous, tip))
            bands.append(section.bands[-1][1])
    obj = k.mesh_object(name, verts, faces)
    slots = []
    for index in bands:
        if index not in slots:
            slots.append(index)
    for index in slots:
        obj.data.materials.append(materials[index])
    for poly, index in zip(obj.data.polygons, bands):
        poly.material_index = slots.index(index)
    if underside:
        k.recalc_normals(obj)
    else:
        orient_up(obj)
    return k.smooth(obj, 62)


def orient_up(obj):
    """An open mesh lying on a surface: every face turned to face up (the faces of a strip are built consistently; the
    caps' fans too, so one look at the majority decides)."""
    up = sum(1 for p in obj.data.polygons if p.normal.z > 0)
    if up < len(obj.data.polygons) / 2:
        obj.data.flip_normals()


# --- The bolts' paths (traced from the sprites: (column, row, heat), the heat in ramp 9's shades of the core pixel,
# 16 for white; the ends of segments that join others on the cell's edge) ---------------------------------------------

TOP_PIN, BOTTOM_PIN = (5.5, -0.5), (5.5, 13.5)  # (the middle of the top and bottom edges: x 0)
TL_PIN, BR_PIN = (-0.5, -0.5), (11.5, 13.5)  # (the top left and bottom right corners)
LEFT_PIN, RIGHT_PIN = (-0.5, 7.0), (11.5, 7.0)  # (the side edges' middles, half a pixel above the cell's centre)


def stroke(*points):
    return [(c, r, h) for c, r, h in points]


BOLTS = {
    # 191: from the top out to the right (its core lighting up), back to the left (white at rows 8-9), down.
    191: [stroke((*TOP_PIN, 11), (6.2, 0.6, 9), (8.2, 2.3, 11), (9.5, 4.0, 12), (9.1, 5.1, 15), (8.2, 6.1, 11),
                 (6.4, 7.1, 13), (5.3, 8.1, 16), (4.2, 9.2, 16), (5.0, 10.3, 12), (5.1, 11.6, 10), (*BOTTOM_PIN, 11))],
    # 192: out to the left and back (white at rows 4-5 and a light knee at row 8).
    192: [stroke((*TOP_PIN, 11), (6.6, 0.8, 9), (6.2, 2.4, 11), (6.8, 4.1, 16), (5.6, 5.2, 16), (4.3, 6.1, 12),
                 (2.6, 7.0, 11), (1.6, 8.2, 15), (1.9, 9.6, 12), (3.2, 11.0, 11), (4.4, 12.3, 9), (*BOTTOM_PIN, 11))],
    # 193: splits under the top into two strands (an eye) that join again near the bottom: the right strand bright
    # (with the stem and the tail: one tube), the left a thinner branch.
    193: [stroke((*TOP_PIN, 11), (5.1, 1.2, 10), (5.6, 2.3, 11), (6.3, 3.2, 12), (7.0, 4.2, 15), (7.0, 5.3, 16),
                 (7.0, 6.6, 14), (6.6, 8.0, 12), (6.1, 9.1, 15), (6.4, 10.1, 11), (6.9, 11.1, 15), (6.3, 12.2, 13),
                 (*BOTTOM_PIN, 11)),
          ("branch", 0.85, stroke((5.4, 2.4, 10), (4.2, 3.2, 8), (3.0, 4.1, 10), (2.8, 5.2, 11), (2.1, 6.2, 12),
                                  (2.1, 7.1, 15), (2.9, 8.1, 13), (3.4, 9.1, 10), (4.4, 10.1, 10), (6.0, 10.9, 11)))],
    # 194: the wide diagonal bolt: from the top left corner a bright run down to a white knot (rows 4-5), on down to the
    # bottom right; a dim arch over the knot.
    194: [stroke((*TL_PIN, 12), (0.2, 1.0, 14), (1.0, 2.1, 14), (1.8, 3.3, 12), (2.9, 4.6, 15), (4.2, 5.1, 16),
                 (5.5, 4.5, 15), (6.7, 5.0, 15), (7.3, 6.1, 12), (7.8, 7.2, 13), (8.5, 8.2, 15), (9.2, 9.2, 15),
                 (9.7, 10.3, 13), (10.3, 11.2, 14), (10.8, 12.2, 11), (*BR_PIN, 11)),
          ("branch", 0.8, stroke((3.4, 4.3, 9), (4.4, 3.1, 10), (6.0, 2.9, 10), (7.2, 3.5, 9), (7.4, 4.6, 11)))],
    # 195: the thin diagonal bolt (dim, a light flash at its first bend and one low down).
    195: [stroke((*TL_PIN, 9), (0.1, 1.0, 6), (0.3, 2.1, 9), (1.1, 3.0, 12), (2.4, 3.4, 9), (4.2, 3.9, 6),
                 (6.0, 4.1, 13), (7.0, 5.0, 12), (7.4, 6.1, 11), (8.1, 7.1, 7), (8.0, 8.2, 5), (7.2, 9.1, 8),
                 (7.2, 10.1, 12), (8.1, 11.0, 9), (9.6, 11.8, 5), (10.6, 12.5, 5), (*BR_PIN, 9))],
    # 198-200: the sideways bolts, left to right.
    198: [stroke((*LEFT_PIN, 11), (0.3, 7.4, 11), (1.1, 6.8, 12), (2.0, 6.0, 16), (3.1, 6.0, 15), (4.1, 7.0, 12),
                 (5.0, 8.1, 15), (6.0, 8.9, 15), (7.1, 8.8, 13), (8.2, 8.0, 13), (9.2, 7.7, 11), (10.2, 7.0, 11),
                 (11.0, 6.7, 9), (*RIGHT_PIN, 10))],
    199: [stroke((*LEFT_PIN, 10), (0.4, 6.9, 9), (1.1, 6.0, 11), (2.0, 5.1, 12), (3.1, 5.2, 7), (4.2, 5.7, 6),
                 (5.2, 6.8, 10), (6.1, 8.0, 12), (7.1, 8.6, 11), (8.1, 8.6, 8), (9.1, 8.1, 7), (10.1, 7.9, 9),
                 (11.0, 7.4, 6), (*RIGHT_PIN, 10))],
    200: [stroke((*LEFT_PIN, 10), (0.3, 6.0, 6), (1.1, 5.1, 9), (2.6, 4.6, 8), (4.0, 4.3, 11), (5.1, 5.1, 12),
                 (6.0, 6.1, 10), (6.7, 7.0, 6), (7.9, 7.6, 6), (9.0, 7.9, 12), (10.0, 6.9, 11), (11.0, 6.1, 8),
                 (*RIGHT_PIN, 10))],
}
MIRRORED = {196: 195, 197: 194}  # (196 and 197 are 195's and 194's mirror images)

# The big column, per frame (its pieces' first sprites 210, 229, 248, 267, + the frame), rows 0-49 of the four cells
# one above the other: its strands (the first the main bolt from its top to its bottom), traced from the white (0x3e,
# 0x3f: heat 15, 16) and light blue pixels (0x9c-0x9f: 12-15).
COLUMN = {
    0: [stroke((5.0, 0.3, 7), (4.8, 2.5, 10), (4.9, 4.8, 11), (4.6, 7.0, 10), (3.6, 8.6, 9), (2.7, 10.2, 10),
               (2.9, 12.3, 13), (3.1, 14.1, 15), (4.4, 15.6, 16), (3.7, 17.3, 16), (3.1, 19.2, 16), (3.0, 21.2, 16),
               (3.0, 23.3, 15), (3.0, 25.4, 15), (3.2, 27.2, 13), (3.0, 29.0, 15), (3.1, 30.4, 15), (3.6, 32.2, 13),
               (4.2, 34.0, 16), (5.3, 35.8, 16), (5.6, 37.6, 16), (6.0, 39.3, 15), (5.6, 41.0, 10), (5.6, 43.0, 9),
               (6.6, 45.0, 12), (6.5, 46.6, 9), (5.6, 48.6, 4)),
        ("branch", 0.85, stroke((4.4, 8.4, 9), (6.3, 9.4, 11), (7.1, 10.8, 12), (7.1, 12.4, 13), (6.3, 14.0, 15),
                                (5.0, 15.2, 16))),
        ("branch", 0.85, stroke((3.4, 21.3, 12), (5.0, 22.4, 8), (5.9, 23.8, 10), (6.1, 25.6, 11), (6.6, 27.4, 13),
                                (7.0, 28.6, 16), (7.0, 30.2, 15), (6.5, 31.4, 11), (5.8, 33.2, 10),
                                (5.2, 35.2, 15)))],
    1: [stroke((5.5, 0.4, 7), (5.4, 2.5, 9), (5.3, 4.2, 13), (5.3, 6.0, 14), (5.4, 7.6, 11), (5.1, 9.1, 11),
               (4.3, 10.3, 10), (3.4, 12.0, 10), (3.0, 14.0, 15), (3.0, 15.2, 13), (3.2, 16.2, 15), (3.8, 17.6, 15),
               (4.0, 19.0, 15), (4.6, 20.1, 12), (6.2, 20.8, 12), (7.6, 21.4, 13), (8.0, 22.6, 12), (8.0, 24.2, 13),
               (8.3, 25.6, 14), (8.0, 27.0, 11), (7.0, 28.5, 9), (5.6, 29.5, 12), (5.0, 30.3, 16), (4.4, 31.6, 16),
               (3.6, 33.0, 16), (3.0, 34.8, 16), (3.0, 36.8, 16), (3.0, 38.6, 16), (3.1, 40.2, 15), (3.6, 41.3, 14),
               (4.6, 42.2, 15), (4.8, 43.4, 12), (4.6, 45.0, 9), (4.2, 46.6, 6), (4.0, 48.0, 3)),
        ("branch", 0.8, stroke((5.2, 10.6, 10), (6.4, 12.2, 11), (7.0, 13.6, 13), (7.2, 15.0, 14), (7.7, 16.3, 12),
                               (7.4, 18.0, 9), (7.3, 19.8, 9), (7.4, 21.2, 12)))],
    2: [stroke((5.5, 0.4, 7), (5.5, 2.0, 10), (5.0, 3.1, 12), (5.0, 4.6, 15), (5.0, 7.0, 16), (5.2, 9.0, 16),
               (6.0, 10.2, 16), (6.4, 11.3, 16), (7.1, 12.3, 15), (7.6, 13.4, 14), (8.0, 14.6, 11), (8.1, 16.0, 11),
               (7.5, 17.2, 10), (6.4, 18.2, 11), (5.0, 19.1, 13), (3.4, 20.1, 15), (2.6, 21.1, 16), (2.0, 22.2, 15),
               (1.3, 23.6, 14), (1.0, 25.0, 14), (1.0, 26.6, 14), (2.3, 28.1, 9), (4.4, 28.4, 10), (6.1, 28.5, 13),
               (7.2, 29.5, 13), (8.0, 30.6, 11), (8.7, 31.8, 12), (9.0, 33.2, 14), (9.0, 34.6, 15), (9.0, 35.8, 16),
               (8.8, 37.0, 14), (7.6, 38.3, 14), (7.0, 39.4, 15), (7.0, 40.8, 13), (7.0, 42.3, 11), (6.9, 44.4, 8),
               (6.7, 46.5, 6), (6.5, 48.6, 4)),
        ("branch", 0.75, stroke((8.7, 0.6, 3), (9.4, 3.0, 4), (10.0, 6.4, 5), (10.6, 9.6, 6), (11.0, 12.2, 8),
                                (11.0, 14.6, 13), (11.0, 16.6, 13), (11.0, 18.4, 12), (10.4, 19.6, 11),
                                (9.0, 20.4, 9))),
        ("branch", 0.8, stroke((4.0, 30.6, 9), (4.4, 32.4, 13), (5.2, 33.6, 15), (5.6, 34.6, 15), (6.0, 35.8, 15),
                               (6.1, 37.2, 14), (6.4, 38.4, 15), (7.0, 39.4, 15))),
        ("branch", 0.75, stroke((1.0, 26.6, 12), (0.4, 28.4, 9), (0.1, 30.0, 12), (0.2, 31.5, 13), (0.6, 33.0, 10),
                                (1.0, 34.6, 9), (1.8, 36.0, 7)))],
}
COLUMN_PIECES = (210, 229, 248, 267)
COLUMN_ROWS = 50
# The sheath: its height over its half-width (flattened), its bands across ((from u, palette index): the middle's blue,
# a darker blue, the edges' dark blue), the points across it (u), its outline's smoothing (rows each way).
SHEATH_DEPTH = 0.42
SHEATH_BANDS = ((0.0, 0x9a), (0.5, 0x97), (0.82, 0x94))
SHEATH_US = (0.0, 0.3, 0.5, 0.66, 0.82, 1.0)
SHEATH_SMOOTH = 1


# --- The sprites' pixels (for the column's outline) -----------------------------------------------------------------

def sheet_indices(sheet_png, sprite):
    """The sprite's palette indices (rows of 12, None for transparent) from the extracted sheet's .idx."""
    sys.path.insert(0, os.path.join(HERE, "..", ".."))
    from sprite_profile import sprite_indices
    return sprite_indices(sheet_png, sprite, large=False)


COLUMN_OUTLINES = {  # (per frame: (first, last) column of each row's pixels from 0x91 up; rows 0-49), from the sheet
    0: ((4, 6), (4, 6), (3, 6), (3, 7), (3, 8), (3, 8), (3, 7), (3, 8), (3, 8), (2, 9), (2, 9), (1, 9), (1, 9), (1, 9),
        (1, 8), (1, 8), (2, 8), (1, 8), (1, 8), (1, 8), (1, 8), (1, 7), (1, 7), (1, 7), (1, 7), (1, 7), (1, 7), (0, 8),
        (0, 9), (1, 9), (0, 9), (0, 9), (0, 10), (0, 10), (0, 10), (0, 10), (0, 10), (0, 9), (0, 9), (1, 8), (1, 8),
        (1, 8), (2, 9), (3, 8), (4, 8), (3, 9), (4, 8), (4, 8), (4, 6), (4, 6)),
    1: ((5, 7), (4, 7), (3, 8), (2, 7), (2, 6), (3, 6), (2, 7), (3, 7), (2, 7), (1, 7), (2, 7), (2, 7), (1, 8), (1, 8),
        (1, 9), (1, 9), (1, 10), (2, 10), (2, 10), (3, 10), (3, 10), (3, 10), (3, 10), (4, 11), (4, 11), (3, 11),
        (3, 11), (3, 11), (4, 11), (2, 11), (2, 10), (1, 10), (2, 10), (2, 11), (2, 10), (2, 8), (1, 8), (1, 7), (1, 7),
        (1, 7), (2, 7), (1, 7), (1, 6), (1, 6), (1, 6), (2, 7), (3, 6), (3, 6), (3, 6), (3, 6)),
    2: ((5, 9), (4, 10), (4, 9), (4, 9), (4, 9), (4, 9), (4, 9), (4, 9), (4, 10), (4, 10), (4, 10), (4, 11), (4, 11),
        (4, 11), (5, 11), (6, 11), (6, 11), (5, 11), (3, 11), (1, 11), (0, 11), (0, 11), (0, 11), (0, 8), (0, 7),
        (0, 6), (0, 6), (0, 6), (0, 8), (0, 8), (0, 9), (0, 9), (0, 10), (0, 11), (0, 11), (0, 11), (1, 11), (2, 10),
        (3, 10), (5, 10), (6, 10), (6, 10), (6, 10), (6, 10), (6, 10), (6, 9), (6, 9), (6, 9), (6, 8), (6, 8)),
}


def outline_from_sheet(sheet_png, frame):
    """Each row's (first, last) column of pixels from 0x91 up over the column's 50 rows (used to write
    COLUMN_OUTLINES)."""
    rows = []
    for base in COLUMN_PIECES:
        rows += sheet_indices(sheet_png, base + frame)
    out = []
    for r in range(COLUMN_ROWS):
        cols = [c for c, i in enumerate(rows[r]) if i is not None and (i & 15) >= 1]
        out.append((cols[0], cols[-1]) if cols else out[-1])
    return out


# --- The column -------------------------------------------------------------------------------------------------------

def column_shape(frame):
    """The sheath's middle and half-width at y (the whole column's model coordinates: row r is y = 6.5 - r), from the
    rows' outline smoothed, closing to points past the first and last rows."""
    raw = COLUMN_OUTLINES[frame]
    lefts = [a - 0.5 + 0.5 for a, _ in raw]  # (pixel edges: the first column's left edge is c, the last's right c + 1)
    rights = [b + 1.0 - 0.5 + 0.5 for _, b in raw]
    smooth_l, smooth_r = [], []
    for r in range(COLUMN_ROWS):
        span = range(max(0, r - SHEATH_SMOOTH), min(COLUMN_ROWS, r + SHEATH_SMOOTH + 1))
        weights = [1.0 + SHEATH_SMOOTH - abs(r - s) for s in span]
        smooth_l.append(sum(lefts[s] * wt for s, wt in zip(span, weights)) / sum(weights))
        smooth_r.append(sum(rights[s] * wt for s, wt in zip(span, weights)) / sum(weights))
    # (in model x: column edge e is x = e - 6)
    mids = [((a + b) / 2 - 6.0) for a, b in zip(smooth_l, smooth_r)]
    halves = [max((b - a) / 2, 0.6) for a, b in zip(smooth_l, smooth_r)]
    return mids, halves


def sheath_at(mids, halves, y):
    """The sheath's (middle, half-width) at y, between the rows' middles (row r at y = 6.5 - r), tapering to points
    half a row past the ends."""
    r = 6.5 - y
    if r <= 0.0:
        f = max(0.0, 1.0 + r / 1.0)  # (to a point at row -1)
        return mids[0], halves[0] * math.sqrt(f)
    if r >= COLUMN_ROWS - 1:
        f = max(0.0, 1.0 - (r - (COLUMN_ROWS - 1)) / 1.2)
        return mids[-1], halves[-1] * math.sqrt(f)
    i = int(r)
    t = r - i
    return mids[i] + (mids[i + 1] - mids[i]) * t, halves[i] + (halves[i + 1] - halves[i]) * t


def sheath_top(mids, halves):
    def top(x, y):
        c, w = sheath_at(mids, halves, y)
        if w <= 1e-6:
            return 0.0
        u = (x - c) / w
        return SHEATH_DEPTH * w * math.sqrt(max(0.0, 1.0 - u * u))
    return top


def sheath(name, frame, materials):
    """The column's sheath: rings across it row by row (the outline's middle and half-width), a half-ellipse
    SHEATH_DEPTH times its half-width high, its bands across it on the section's points; closed underneath."""
    mids, halves = column_shape(frame)
    ys = [7.5] + [7.0 - i for i in range(COLUMN_ROWS + 2)]  # (the rows' edges, from the top's point to the bottom's)
    us = list(SHEATH_US)
    order = [u for u in reversed(us[1:])] + [-u for u in us]
    verts, faces, bands = [], [], []
    rings = []
    for y in ys:
        c, w = sheath_at(mids, halves, y)
        ring = len(verts)
        for u in order:
            verts.append((c + u * w, y, SHEATH_DEPTH * max(w, 0.0) * math.sqrt(max(0.0, 1.0 - u * u))))
        rings.append(ring)
    count = len(order)

    def band(u0, u1):
        return last_band(SHEATH_BANDS, (abs(u0) + abs(u1)) / 2)
    for i in range(len(rings) - 1):
        a, b = rings[i], rings[i + 1]
        for j in range(count - 1):
            faces.append((a + j, a + j + 1, b + j + 1, b + j))
            bands.append(band(order[j], order[j + 1]))
        faces.append((a + count - 1, a, b, b + count - 1))
        bands.append(SHEATH_BANDS[-1][1])
    obj = k.mesh_object(name, verts, faces)
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.dissolve_degenerate(bm, dist=1e-6, edges=bm.edges)
    bm.to_mesh(obj.data)
    bm.free()
    slots = []
    for index in bands:
        if index not in slots:
            slots.append(index)
    for index in slots:
        obj.data.materials.append(materials[index])
    # (dissolving may drop faces: their bands by their place, from the face's middle u)
    for poly in obj.data.polygons:
        cx, cy, cz = poly.center
        c, w = sheath_at(mids, halves, cy)
        if poly.normal.z < -0.5:
            index = SHEATH_BANDS[-1][1]
        else:
            index = last_band(SHEATH_BANDS, abs(cx - c) / max(w, 1e-6))
        poly.material_index = slots.index(index) if index in slots else 0
    k.recalc_normals(obj)
    return k.smooth(obj, 60), (mids, halves)


def column_parts(frame, prefix):
    """The column of a frame built whole: its sheath and its strands lying on it."""
    mats = {}
    for _, index in SHEATH_BANDS:
        mats[index] = material(index, 0.5)
    for _, index in STRAND.bands[1:]:
        mats[index] = material(index, 0.5)
    for _, index in STRAND.core_bands:
        mats[index] = material(index, 0.4)
    body, (mids, halves) = sheath(f"{prefix}_sheath", frame, mats)
    top = sheath_top(mids, halves)
    parts = [body]
    for n, entry in enumerate(COLUMN[frame]):
        width, points = (1.0, entry) if not isinstance(entry, tuple) else (entry[1], entry[2])
        xy = [P(c, r) for c, r, _ in points]
        heats = [h for _, _, h in points]
        # (closed underneath, inside the sheath: the cut into pieces turns an open strip's faces whichever way)
        parts.append(tube(f"{prefix}_strand{n}", xy, heats, STRAND, mats, width=width, base=top, underside=True,
                          step=0.9))
    return parts, mats


def column_piece(frame, piece, name):
    """One of the column's four pieces (piece 0 the top): the whole column cut at the cells' edges, moved onto its own
    cell's centre."""
    parts, mats = column_parts(frame, name)
    y0, y1 = -7.0 - 14.0 * piece, 7.0 - 14.0 * piece
    cut = []
    for p in parts:
        mk.apply(p)
        q = mk.cut(p, (-20.0, 20.0, y0, y1), mats[SHEATH_BANDS[0][1]])
        if q is not None:
            cut.append(q)
    for p in parts:
        mesh = p.data
        bpy.data.objects.remove(p)
        bpy.data.meshes.remove(mesh)
    mk.transform(cut, Matrix.Translation((0.0, 14.0 * piece, 0.0)))
    for i, q in enumerate(cut):
        q.name = f"{name}_{i}"
    return cut


# --- The models -------------------------------------------------------------------------------------------------------

def bolt_parts(sprite, name):
    mirrored = sprite in MIRRORED
    source = MIRRORED.get(sprite, sprite)
    section = THIN if source in (195, 198, 199, 200) else BOLT
    mats = {}
    for _, index in section.bands[1:]:
        mats[index] = material(index, section.roughness[1])
    for _, index in section.core_bands:
        mats[index] = material(index, section.roughness[0])
    parts = []
    for n, entry in enumerate(BOLTS[source]):
        width, points = (1.0, entry) if not isinstance(entry, tuple) else (entry[1], entry[2])
        cols = [(11.0 - c if mirrored else c) for c, _, _ in points]
        xy = [P(c, r) for c, (_, r, _) in zip(cols, points)]
        heats = [h for _, _, h in points]
        parts.append(tube(f"{name}_{n}", xy, heats, section, mats, width=width))
    return parts


# (name, sprites it shows, what it is, how: "bolt" or ("column", frame, piece))
MODELS = [
    ("shot_lightning", (191,), "the narrow bolt, out to the right and back", "bolt"),
    ("shot_lightning_192", (192,), "the narrow bolt, out to the left and back", "bolt"),
    ("shot_lightning_193", (193,), "the narrow bolt splitting into two strands and joining again", "bolt"),
    ("shot_lightning_194", (194,), "the wide diagonal bolt, up and left (its knot white)", "bolt"),
    ("shot_lightning_195", (195,), "the thin diagonal bolt, up and left", "bolt"),
    ("shot_lightning_196", (196,), "the thin diagonal bolt, up and right (195's mirror image)", "bolt"),
    ("shot_lightning_197", (197,), "the wide diagonal bolt, up and right (194's mirror image)", "bolt"),
    ("shot_lightning_side", (198,), "the sideways bolt (bright, white at its first wave)", "bolt"),
    ("shot_lightning_side_199", (199,), "the sideways bolt, dimmer", "bolt"),
    ("shot_lightning_side_200", (200,), "the sideways bolt, waving higher", "bolt"),
] + [
    (f"shot_lightning_{base + frame}", (base + frame,) + ((base + 3,) if frame == 0 else ()),
     f"the big column's {('top', 'second', 'third', 'bottom')[piece]} piece, frame {frame + 1}"
     + (" (and frame 4, the same)" if frame == 0 else ""), ("column", frame, piece))
    for frame in range(3) for piece, base in enumerate(COLUMN_PIECES)
]


def build_model(name, sprite, how):
    if how == "bolt":
        return triangulate(bolt_parts(sprite, name))
    _, frame, piece = how
    return triangulate(column_piece(frame, piece, name))


def zbounds(parts):
    zs = [(p.matrix_world @ v.co).z for p in parts for v in p.data.vertices]
    return min(zs), max(zs)


# --- Previews ---------------------------------------------------------------------------------------------------------

def game_view(prefix, objects):
    mk.preview(prefix, objects, size=(12, 14), scale=32, distance=0.42)
    scene = bpy.context.scene
    cam, sun = game_camera(scene, 16.0, (512, 512))
    scene.render.filepath = prefix + "_game.png"
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam)
    bpy.data.objects.remove(sun)


CHAINS = [  # (x, y of the first cell's centre, [(sprite, dx, dy)...] cells as the game places them, dy up)
    (-66.0, 20.0, [(191, 0, -14 * i) for i in range(4)]),
    (-52.0, 20.0, [(192, 0, -14 * i) for i in range(4)]),
    (-38.0, 20.0, [(193, 0, -14 * i) for i in range(4)]),
    (-24.0, 20.0, [(192 - (i % 2), 0, -14 * i) for i in range(4)]),
    (-8.0, 20.0, [(210 + f * 19, 0, -14 * f) for f in range(4)]),
    (6.0, 20.0, [(211 + f * 19, 0, -14 * f) for f in range(4)]),
    (20.0, 20.0, [(212 + f * 19, 0, -14 * f) for f in range(4)]),
    (40.0, 20.0, [(194 + (i % 2), -12 * i, 14 * i) for i in range(3)]),
    (44.0, -24.0, [(196 + (i % 2), 12 * i, 14 * i) for i in range(3)]),
    (56.0, 34.0, [(198 + (i % 2), 12 * i, 0) for i in range(3)]),
    (56.0, 18.0, [(199 + (i % 2), 12 * i, 0) for i in range(3)]),
]


def chains_view(prefix):
    """The segments joined as the game fires them: columns of 191s, 192s, 193s, 192/191 by turns, the big column's
    three frames, the diagonal and sideways chains (game camera and from straight above)."""
    k.reset()
    scene = bpy.context.scene
    scene.view_settings.view_transform = "Standard"
    by_sprite = {}
    for entry in MODELS:
        for s in entry[1]:
            by_sprite[s] = entry
    heights = {}
    for x, y, cells in CHAINS:
        for sprite, dx, dy in cells:
            name, _, _, how = by_sprite[sprite]
            parts = build_model(f"{name}_c{len(heights)}", sprite, how)
            low, high = zbounds(parts)
            # (bolts centred in height as the game does; the column's pieces at their origin, lowered as height= says)
            lift = -(low + high) / 2 if how == "bolt" else -COLUMN_HEIGHT
            mk.transform(parts, Matrix.Translation((x + dx, y + dy, lift)))
            heights[len(heights)] = lift
    bpy.context.view_layer.update()
    cam, sun = game_camera(scene, 150.0, (1500, 1200))
    scene.render.filepath = prefix + "chains_game.png"
    bpy.ops.render.render(write_still=True)
    cam.rotation_euler = (0.0, 0.0, 0.0)
    cam.location = (0.0, 0.0, 60.0)
    scene.render.filepath = prefix + "chains_top.png"
    bpy.ops.render.render(write_still=True)


# The column's pieces are drawn at their origin (model line "origin"): lowered by half the column's height (its
# strands' tops, ~3.3 pixels) so that it is centred in height on the player's layer as every other shot is.
COLUMN_HEIGHT = 1.6


GLOW = {  # sprite: glow= (size:strength:colour:dx:dy)
    191: "12:0.38:157:0:0", 192: "12:0.38:157:0:0", 193: "12:0.38:157:0:0",
    194: "13:0.42:157:0:0", 195: "11:0.32:157:0:0", 196: "11:0.32:157:0:0", 197: "13:0.42:157:0:0",
    198: "12:0.36:157:0:0", 199: "11:0.3:157:0:0", 200: "11:0.3:157:0:0",
}
COLUMN_GLOW = "18:0.3:157:0:0"


def cfg_lines():
    """The models.cfg block's model and shot lines."""
    models, shots = [], []
    for name, sprites, what, how in MODELS:
        origin = " origin" if how != "bolt" else ""
        models.append(f"model {name:<24} shots/{name}.glb{origin}")
        for s in sprites:
            options = f"height=-{COLUMN_HEIGHT:g} " if how != "bolt" else ""
            options += f"glow={GLOW.get(s, COLUMN_GLOW)}"
            shots.append((s, name, options, what))
    return models, shots


def build():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    outdir = options.get("outdir", OUTDIR)
    for name, sprites, what, how in MODELS:
        if only is not None and name not in only:
            continue
        k.reset()
        parts = build_model(name, sprites[0], how)
        bpy.context.view_layer.update()
        low, high = zbounds(parts)
        print(f"== {name} (shots {', '.join(str(s) for s in sprites)}): {what}; z {low:.2f}..{high:.2f}")
        if "check" in options:
            check_frames(parts, os.path.join(options["check"], "shots.png"),
                         [(s, turn(0), f"shots {s}") for s in sprites[:1]], move_to_frame=False)
        bpy.context.scene.view_settings.view_transform = "Standard"
        mk.report(name, parts, os.path.join(outdir, name + ".glb"))
        if "preview" in options:
            game_view(options["preview"] + name, parts)
    if "preview" in options and only is None:
        chains_view(options["preview"])
    models, shots = cfg_lines()
    print("CFG:")
    for line in models:
        print(line)
    for s, name, opts, what in sorted(shots):
        print(f"shot shots {s:<3} {name:<24} {opts}")


if __name__ == "__main__":
    build()
