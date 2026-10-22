"""The big green shell of TORM, BOTANY A and BOTANY B (their boss), ?TUNNEL? and episode 6's GREY MOON and GLACIER (sheet
J: fifteen 2x2 sprites that the level events lay out as one 96 x 112 picture), its dome lighting up and its eye opening
as they fire; polished (2026-10-22, round 36). It replaces wave3_m_shell.py (a pillow carapace with procedural ribs, two
green glass balls, a cup eye, painted by hand) and wave3_at_j.py (its eye's frames, rebuilt with lids).

Where it appears: TORM t6600 (episode 2, link 64 and the boss bar): event 7 (top layer) 772 (J 193) at x 164, 773 (195)
at 188, y -56, 774 (241) at 164 and 775 (243) at 188, y -28; event 51 (the top layer's one-frame pieces, armour 250) 153
155 157 159 at x 140 164 188 212, y -84; 191 at 140 and 197 at 212, y -56; 229 at 140 and 235 at 212, y -28; 267 269 271
at 152 176 200, y 0: four rows of the sheet, the bottom one 12 pixels in. BOTANY A and B t4900 the same; ?TUNNEL? t200
the same 30 pixels to the left on the ground (events 10 and 52, armour 40). GREY MOON (t6300) and GLACIER (t5300) take
TORM's boss block, 1577-1580 (772-775's copies), but not its event 51 pieces (episode 6's boss blocks keep the boss's
spawns and link events only): there only the four middle pieces show. 772 and 773 fire gun 76 every 80 ticks and then
play their animation (animate 2): 193 161 199 237 275 165 203 203 165 275 237 199 161 193 (and 195 163 201 239 277 167
205 ...): the dome's glass lights up from a dull green through bright green to white-hot and back; 774 and 775 fire gun
116: 241 231 231 231 241 (and 243 233 ...): the eye opens on a green gem and the conduits beside it light up. No other
enemy, launched ones included, shows any of these sprites; none is another sprite's pixels mirrored, turned or in other
ramps (the shell is not even its own mirror image).

As the sprites and their 4x upscales draw it (the picture's columns and rows; lit from the upper left): a carapace of
green ribs (ramp 2) running down the screen, a broad cowl over its top (rows 2-20, columns 17-79) ribbed by its light
and parted by an L of seams, side pods at its shoulders (rows 12-35), the ribs below parting at the bottom into two
lobes (from row 82, columns 48-50 open); on it, all grey (ramp 0): a piston standing at each shoulder (columns 11-14 and
81-84 of rows 12-27, a lit collar at rows 16-18), an arm from each in to the middle (rows 19-21) with a bolt on it
(columns 27-32 and 62-66) and a joint by the dome (columns 35-41 and 55-60); the dome (columns 31-64 of rows 22-47), a
ball parted by a seam down its middle with a ladder of four rungs (column 48, rows 30-37) and a cleft at its top
(columns 44-51 of rows 18-27), its highlight at columns 39-46 of rows 30-34, brackets round its upper sides; a stack in
front of it (columns 46-51 of rows 39-46 between two lower shoulders); a hose curving from its lower right into the neck
(columns 56-64 of rows 42-51); the neck under it (rows 47-58) and the barrel down from it (columns 46-50 of rows 56-67)
to a dark housing (columns 37-59 of rows 66-83) with a ring round the black eye (columns 45-52 of rows 72-80); the
shoulder plates (columns 6-20 of rows 35-66 and 75-90 of rows 36-65), a lit ridge across each (row 44), their lower
outer corners chamfered and lit; and green lamps of ramp 12: the ends of two conduit ribs beside the housing (columns
32-35 of rows 52-55 and 84, columns 61-64 of rows 54-55 and 84-91), which the eye's frame lights along their length
(rows 56-83) and the dome's frames put out.

Built for the game's camera (polish_gyges_maw.py's way): the whole shell is one heightfield in the picture's plane (x, y
as the sprites draw it, z up), sheared along the camera's line of sight (y - z tan 20), so that the camera sees every
point where the sprites draw it; on polish_gyges_wall.Plate's grid, 0.5 pixel apart, whose lines are the pieces' edges,
so each piece is the cells of its sprite's box (no mesh cutting; walled where cut, dark). Its heights: the carapace's
edge rounded over FALL up to CREST, its rise to its middle (BULGE), rounded ribs between the sprite's dark lines (black
pixels with the shell all round them, the darkest greens and, in the cowl, greens darker than their neighbours; those
across the rows that run on down the columns, those down the columns that run on along the rows, each chain of them
straightened by a moving average and its gaps closed, so the ribs run straight where the sprite's lines wander); the
grey parts' slabs on it (the grey pixels, rounded, lifted by SLAB_LIFT); over them the pistons, arms, barrel, hose and
the plates' ridges as round bars, the bolts and joints as knobs, the dome (a superellipse ball, its cleft, seam and
rungs), the stack (three wedges falling towards the camera) and the eye (a ring round a pit, the gem in it). Painted by
the sprite's shades (polish_gyges_maw's way: each face the ink of the pixels under it, in that ink's shade there,
blurred, lifted and lighter where the game's sun lights it less: COMP), the carapace a shade or so darker down its
grooves; each look repaints the same heightfield with its own pixels: the dome frames' glass (glossy, glowing a little:
0.1-0.28), the sky's sheen on it (0x8a-0x8e) and its white-hot middle (0x7e-0x7f, 0.5-0.62), the lamps, the conduits and
the gem (ramp 12, 0.3-0.6). Heights: z 0 (the underside, the layer's plane) to 14.2 (the stack; the dome 14, the
carapace up to 7.2): on the top layer the player flies through the dome, as the 2D game draws the shell over the ship
(the old dome reached 22; CAMANIS' boss reaches 12.6, GYGES' maw 14). At most 15 materials a piece (the rarest shades
merged into their neighbours); deterministic (no random numbers; the faces' centres and normals rounded before they pick
their shades).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera. The whole's origin
is the picture's middle (its pixel edge 48, 56): column c's left edge is x = c - 48, row r's top edge y = 56 - r; a
piece whose sprite's top left pixel is (c0, r0) has its origin at (c0 + 12 - 48, 42 - r0) (models.cfg origin).

models.cfg: the model and sprite lines of green_shell_153 ... _271 stay (origin, yaw=0), the sprite lines get height=-4
(on ?TUNNEL?'s ground the shell rests on the terrain; on the top layer it sits 4 lower); new frame models
green_shell_161 199 237 275 165 203 (193's place) and 163 201 239 277 167 205 (195's), green_shell_231 and _233 (241's
and 243's), with frame lines j <sprite> green_shell_<sprite>; green_shell_eye_* and their frame lines (241 243 231 233)
go.

Replaces wave3_m_shell.py and wave3_at_j.py (all of both: the shell and its eye are all they build; wave3_at_j imports
wave3_m_shell, nothing else imports either), wave3_m_kit.py (only wave3_m_shell imports it) and wave3_m_art.py (its
BOSS, the only pixels left in it, read only by wave3_m_kit), and wave3_at_kit.py (only wave3_at_j imports it).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the outline as the camera sees
it against the sprites' pixels, the whole and each piece), --preview <prefix> (each piece's top and 3/4 views), --only
<name,...> (models to export).
"""
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_gyges_wall as gw  # noqa: E402  (Plate, the shear to the camera, the faces' light)
from polish_k_pod import triangulate  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402

W, H = 96, 112                    # the whole picture; its origin is its middle, the pixel edge (48, 56)
LEFT, TOP = -48.0, 56.0
S = 4                             # the fine grid of the carapace's fields: S cells a pixel


def px(c):
    """A pixel edge's column in the picture's plane."""
    return c - 48.0


def py(r):
    return 56.0 - r


# --- Pictures -------------------------------------------------------------------------------------------------------

def parse_picture(text, first_row=2):
    a = -np.ones((H, W), int)
    for i, line in enumerate(text.split()):
        for c in range(W):
            t = line[2 * c:2 * c + 2]
            if t != "..":
                a[first_row + i, c] = int(t, 16)
    return a


def patched(base, text):
    a = base.copy()
    for item in text.split():
        r, c, hexes = item.split(":")
        r, c = int(r), int(c)
        for i in range(len(hexes) // 2):
            t = hexes[2 * i:2 * i + 2]
            a[r, c + i] = -1 if t == ".." else int(t, 16)
    return a


def picture(look):
    base = parse_picture(PICTURE)
    return base if look == "idle" else patched(base, PATCHES[look])


# --- Numbers ----------------------------------------------------------------------------------------------------------

def blur(a, sigma):
    return gw.blur(a, sigma)


def blur1d(a, sigma, axis):
    r = int(math.ceil(3 * sigma))
    w = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2)
    w /= w.sum()
    if axis == 0:
        p = np.pad(a.astype(float), ((r, r), (0, 0)), mode="edge")
        n = a.shape[0]
        return sum(w[i] * p[i:i + n, :] for i in range(2 * r + 1))
    p = np.pad(a.astype(float), ((0, 0), (r, r)), mode="edge")
    n = a.shape[1]
    return sum(w[i] * p[:, i:i + n] for i in range(2 * r + 1))


def smoothstep(e0, e1, x):
    t = np.clip((np.asarray(x, float) - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def edt(mask, step):
    """Each cell's distance to the nearest cell outside the mask (exact; Felzenszwalb and Huttenlocher's two passes)."""
    inf = 1e12
    f = np.where(mask, inf, 0.0)

    def rows(g):
        n = g.shape[1]
        out = np.empty_like(g)
        for i in range(g.shape[0]):
            row = g[i]
            v = np.zeros(n, int)
            z = np.zeros(n + 1)
            j = 0
            z[0], z[1] = -inf, inf
            for q in range(1, n):
                s = ((row[q] + q * q) - (row[v[j]] + v[j] * v[j])) / (2 * q - 2 * v[j])
                while s <= z[j]:
                    j -= 1
                    s = ((row[q] + q * q) - (row[v[j]] + v[j] * v[j])) / (2 * q - 2 * v[j])
                j += 1
                v[j] = q
                z[j] = s
                z[j + 1] = inf
            j = 0
            for q in range(n):
                while z[j + 1] < q:
                    j += 1
                out[i, q] = (q - v[j]) ** 2 + row[v[j]]
        return out
    return np.sqrt(rows(rows(f).T).T) * step


def up(m):
    return np.repeat(np.repeat(m, S, 0), S, 1)


def fine_xy():
    xs = LEFT + (np.arange(W * S) + 0.5) / S
    ys = TOP - (np.arange(H * S) + 0.5) / S
    return np.meshgrid(xs, ys)


class Field:
    """Values on the fine grid, sampled bilinearly between its cells' middles."""

    def __init__(self, values):
        self.v = values

    def __call__(self, Xa, Ya):
        h, w = self.v.shape
        fc = np.clip((np.asarray(Xa, float) - LEFT) * S - 0.5, 0.0, w - 1.0)
        fr = np.clip((TOP - np.asarray(Ya, float)) * S - 0.5, 0.0, h - 1.0)
        c0 = np.minimum(np.floor(fc).astype(int), w - 2)
        r0 = np.minimum(np.floor(fr).astype(int), h - 2)
        tc, tr = fc - c0, fr - r0
        v = self.v
        return ((v[r0, c0] * (1 - tc) + v[r0, c0 + 1] * tc) * (1 - tr) +
                (v[r0 + 1, c0] * (1 - tc) + v[r0 + 1, c0 + 1] * tc) * tr)


def components(mask):
    """4-connected components of a mask (labels 1.., 0 none), numbered in scan order."""
    lab = np.zeros(mask.shape, int)
    n = 0
    h, w = mask.shape
    for r in range(h):
        for c in range(w):
            if mask[r, c] and not lab[r, c]:
                n += 1
                stack = [(r, c)]
                lab[r, c] = n
                while stack:
                    y, x = stack.pop()
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        yy, xx = y + dy, x + dx
                        if 0 <= yy < h and 0 <= xx < w and mask[yy, xx] and not lab[yy, xx]:
                            lab[yy, xx] = n
                            stack.append((yy, xx))
    return lab, n


def run_length(mask, axis):
    """Each cell's run of True cells along an axis (0 where False)."""
    m = mask if axis == 0 else mask.T
    h, w = m.shape
    down = np.zeros((h, w), int)
    upr = np.zeros((h, w), int)
    for r in range(h):
        down[r] = np.where(m[r], (down[r - 1] if r else 0) + 1, 0)
    for r in range(h - 1, -1, -1):
        upr[r] = np.where(m[r], (upr[r + 1] if r < h - 1 else 0) + 1, 0)
    out = np.where(m, down + upr - 1, 0)
    return out if axis == 0 else out.T


def close_gaps(mask, gap):
    """The mask with its gaps down the columns up to `gap` pixels long filled."""
    out = mask.copy()
    h = mask.shape[0]
    for g in range(1, gap + 1):
        for r in range(1, h - g):
            fill = mask[r - 1] & mask[min(h - 1, r + g)]
            for t in range(g):
                out[r + t] |= fill
    return out


def chain_distance(mask, Xf, Yf, flip=False):
    """How far each fine cell lies across from the nearest of the mask's chains of pixels down its columns (8-connected
    from row to row), each chain's course a moving average of its pixels' columns row by row (less half a pixel: the
    dark line's own width). flip: the mask is a transposed picture (its rows the picture's columns, Xf and Yf the
    picture's -y and -x)."""
    h, w = mask.shape
    lab = np.zeros(mask.shape, int)
    n = 0
    for r in range(h):
        for c in range(w):
            if mask[r, c] and not lab[r, c]:
                n += 1
                stack = [(r, c)]
                lab[r, c] = n
                while stack:
                    y, x = stack.pop()
                    for dy in (-1, 1):
                        for dx in (-1, 0, 1):
                            yy, xx = y + dy, x + dx
                            if 0 <= yy < h and 0 <= xx < w and mask[yy, xx] and not lab[yy, xx]:
                                lab[yy, xx] = n
                                stack.append((yy, xx))
    # the fine grid's rows (as picture rows) and columns
    fr = (np.arange(Xf.shape[0]) + 0.5) / S - 0.5
    fx = Xf[0]
    out = np.full(Xf.shape, 1e9)
    for i in range(1, n + 1):
        rr, cc = np.nonzero(lab == i)
        if len(rr) < RUN:
            continue
        rows = np.arange(rr.min(), rr.max() + 1)
        course = np.array([cc[rr == r].mean() if (rr == r).any() else np.nan for r in rows])
        ok = ~np.isnan(course)
        course = np.interp(rows, rows[ok], course[ok])
        k = STRAIGHTEN // 2
        pad = np.concatenate([np.full(k, course[0]), course, np.full(k, course[-1])])
        course = np.convolve(pad, np.ones(2 * k + 1) / (2 * k + 1), mode="valid")
        sel = (fr >= rows[0] - 0.5) & (fr <= rows[-1] + 0.5)
        xc = np.interp(fr[sel], rows, course) + 0.5 + (LEFT if not flip else -TOP)
        d = np.abs(fx[None, :] - xc[:, None]) - 0.5
        out[sel] = np.minimum(out[sel], np.clip(d, 0.0, None))
    return out


def seg_dist(Xa, Ya, pts):
    d = np.full(np.shape(Xa), 1e9)
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        dx, dy = x1 - x0, y1 - y0
        t = np.clip(((Xa - x0) * dx + (Ya - y0) * dy) / max(1e-9, dx * dx + dy * dy), 0.0, 1.0)
        d = np.minimum(d, np.hypot(Xa - (x0 + t * dx), Ya - (y0 + t * dy)))
    return d


def inside_tri(Xa, Ya, tri):
    (x0, y0), (x1, y1), (x2, y2) = tri

    def side(ax, ay, bx, by):
        return (bx - ax) * (Ya - ay) - (by - ay) * (Xa - ax)
    s0, s1, s2 = side(x0, y0, x1, y1), side(x1, y1, x2, y2), side(x2, y2, x0, y0)
    return ((s0 >= 0) & (s1 >= 0) & (s2 >= 0)) | ((s0 <= 0) & (s1 <= 0) & (s2 <= 0))


def tube(Xa, Ya, pts_px, r, z_axis):
    """A round bar along a path of pixel-edge points (column, row): its top over the plane (-1 off it)."""
    pts = [(px(c), py(rw)) for c, rw in pts_px]
    d = seg_dist(Xa, Ya, pts)
    z = np.asarray(z_axis, float) + np.sqrt(np.clip(r * r - d * d, 0.0, None))
    return np.where(d < r, z, -1.0)


def knob(Xa, Ya, c, rw, rx, ry, z0, top, power=0.5):
    """A dome over an ellipse (its middle a pixel edge (column, row), its radii) from z0 at its rim up to top."""
    u = ((Xa - px(c)) / rx) ** 2 + ((Ya - py(rw)) / ry) ** 2
    return np.where(u < 1.0, z0 + (top - z0) * np.clip(1.0 - u, 0.0, 1.0) ** power, -1.0)


# --- The shell's heights ------------------------------------------------------------------------------------------------

CREST, FALL = 3.0, 3.8                  # the carapace's edge rounded over FALL up to CREST
BULGE = (4.2, 50.0, 6.0, 62.0, 0.7)     # and its rise to its middle: height, half-width, middle (y), half-height, power
RUN = 3                                 # grooves count where they run on this far (pixels)
STRAIGHTEN = 7                          # their courses smoothed over this many pixels
GAP = 3                                 # and gaps in them up to this long closed
RIB = (1.3, 2.0, 1.0, 2.5)              # its ribs: height, width of their rounded shoulders, smoothing along them, cap
GREY_FALL = 1.0                          # the grey parts' slabs rounded over this
SLAB_LIFT = [((10, 45), 2.8), ((84, 45), 2.8), ((48, 50), 2.0), ((40, 70), 1.7), ((55, 70), 1.7),
             ((12, 20), 1.0), ((70, 20), 1.0), ((40, 30), 1.2)]   # each grey slab's lift, by a pixel in it
SLAB_DEFAULT = 1.0
DOME = ((47.8, 34.8), (16.9, 12.7), 2.4, 14.0)   # middle (column, row), radii, plan's power, top
NOTCH = ((47.6, 27.6), (43.4, 17.5), (51.8, 17.5))   # the cleft at its top: its lowest point, its top corners
NOTCH_ROUND = 2.2
SEAM = (48.0, (26.5, 39.0), 0.55)       # the seam down its middle: column, rows, depth
RUNGS = [30.5, 32.5, 34.5, 36.6]        # the ladder's rungs on it
STACK = [((46.0, 52.0, 39.0, 46.6), (14.3, 12.7)), ((42.0, 46.2, 40.6, 46.6), (13.4, 12.3)),
         ((51.8, 56.0, 40.6, 46.6), (13.4, 12.3))]   # columns, rows; height at its top edge and at its foot
EYE = ((48.6, 76.3), 4.7, 1.15, 3.55, (2.9, 2.7, 1.4))   # middle, the ring's radius and tube, the pit, the gem
EYE_Z = 1.9                       # the ring's axis over the carapace's smooth surface (the pit 1.8 under it)


class Shell:
    """The shell's heightfield in the picture's plane (from the idle picture: the frames only repaint it)."""

    def __init__(self, a):
        self.a = a
        ramp = np.where(a >= 0, a >> 4, -1)
        shade = np.where(a >= 0, a & 15, 0)
        full = a >= 0
        Xf, Yf = fine_xy()
        inside = blur(up(full.astype(float)), 0.55 * S) > 0.5
        self.inside_fine = inside
        e = edt(inside, 1.0 / S)
        hgt, hw, yo, hh, pw = BULGE
        base = CREST * np.sqrt(1.0 - (1.0 - np.clip(e / FALL, 0.0, 1.0)) ** 2)
        base += hgt * np.clip(1.0 - (Xf / hw) ** 2 - ((Yf - yo) / hh) ** 2, 0.0, None) ** pw
        base = np.where(inside, base, 0.0)
        # The ribs: rounded between the sprite's dark lines (black pixels with the shell all round them, the darkest
        # greens, the outside), their distances along each row and column smoothed along the other.
        pad = np.pad(full, 1)
        allround = np.ones_like(full)
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                allround &= pad[1 + dr:1 + dr + H, 1 + dc:1 + dc + W]
        groove = ((a == 1) & allround) | ((ramp == 2) & (shade <= 1)) | ~full
        # and where a green is two shades darker than its left neighbour and one than its right one (the cowl's ribs
        # are drawn by their light alone)
        sl = np.pad(shade, ((0, 0), (1, 1)), mode="edge")
        groove |= (ramp == 2) & (shade <= sl[:, :-2] - 2) & (shade <= sl[:, 2:] - 1) & (shade <= 6)
        # Grooves across a row count only where they run on down the column (RUN pixels: a rib's edge), those
        # along a column only where they run on along the row (a seam), the outside always.
        # Each chain of them is straightened (its course along the column, or the row, a moving average over STRAIGHTEN
        # pixels: the sprite's dark lines wander by a pixel, the ribs between them shouldn't).
        rh, rw, sm, cap = RIB
        vert = close_gaps(groove & (run_length(groove, 0) >= RUN), GAP) & full
        horiz = close_gaps((groove & (run_length(groove, 1) >= RUN)).T, GAP).T & full
        dx = blur1d(np.minimum(chain_distance(vert, Xf, Yf), cap), sm * S, 0)
        dy = blur1d(np.minimum(chain_distance(horiz.T, -Yf.T, -Xf.T, flip=True).T, cap), sm * S, 1)
        out = up(~full)
        j = np.arange(out.shape[1])
        last = np.maximum.accumulate(np.where(out, j[None, :], -10 ** 6), axis=1)
        nxt = np.minimum.accumulate(np.where(out, j[None, :], 10 ** 6)[:, ::-1], axis=1)[:, ::-1]
        dx = np.minimum(dx, blur1d(np.minimum(np.minimum(j[None, :] - last, nxt - j[None, :]) / S, cap), sm * S, 0))
        d = np.minimum(dx, dy)
        rib = rh * np.sqrt(1.0 - (1.0 - np.clip(d / rw, 0.0, 1.0)) ** 2)
        carapace = np.where(inside, base + (rib - rh) * np.clip(e / 1.5, 0.0, 1.0), 0.0)
        self.rib = Field(np.where(inside, rib / rh, 1.0))
        # The grey parts' slabs: the grey pixels (their black outlines are the carapace's grooves), rounded.
        grey = (ramp == 0) & (a >= 2)
        lab, n = components(grey)
        lift = np.full(n + 1, SLAB_DEFAULT)
        for (c, r), v in SLAB_LIFT:
            if lab[r, c]:
                lift[lab[r, c]] = v
        gm = blur(up(grey.astype(float)), 0.5 * S) > 0.5
        eg = edt(gm, 1.0 / S)
        liftf = blur(up(lift[lab].astype(float)), 1.0 * S)
        slab = np.where(gm, base + liftf * np.sqrt(1.0 - (1.0 - np.clip(eg / GREY_FALL, 0.0, 1.0)) ** 2), -1.0)
        self.field = Field(np.maximum(carapace, slab))
        self.base = Field(base)
        self.inside = Field(inside.astype(float))

    def dome_pixels(self):
        """The pixels whose middles lie on the dome."""
        c, r = np.meshgrid(np.arange(W), np.arange(H))
        Xp, Yp = px(c + 0.5), py(r + 0.5)
        return self.dome(Xp, Yp, self.base(Xp, Yp)) > 0

    def cells(self, cx, cy):
        return self.inside(cx, cy) > 0.5

    def heights(self, Xa, Ya):
        Xa, Ya = np.asarray(Xa, float), np.asarray(Ya, float)
        z = self.field(Xa, Ya)
        b = self.base(Xa, Ya)
        parts = [
            tube(Xa, Ya, [(13.0, 13.8), (13.0, 27.0)], 2.0, b + 1.9),          # the pistons and their collars
            tube(Xa, Ya, [(13.0, 16.0), (13.0, 17.8)], 2.45, b + 1.9),
            tube(Xa, Ya, [(83.0, 15.6), (83.0, 28.0)], 2.0, b + 1.9),
            tube(Xa, Ya, [(83.0, 17.0), (83.0, 18.8)], 2.45, b + 1.9),
            tube(Xa, Ya, [(15.0, 20.0), (36.5, 20.0)], 1.3, b + 1.5),          # the arms
            tube(Xa, Ya, [(59.5, 20.2), (81.0, 20.2)], 1.3, b + 1.5),
            knob(Xa, Ya, 29.8, 18.0, 2.9, 2.4, b + 1.5, b + 4.4),              # the bolts on them
            knob(Xa, Ya, 64.6, 18.6, 2.9, 2.4, b + 1.5, b + 4.4),
            knob(Xa, Ya, 38.3, 20.3, 2.7, 2.1, b + 1.5, b + 3.6),              # their joints by the dome
            knob(Xa, Ya, 57.6, 20.6, 2.7, 2.1, b + 1.5, b + 3.6),
            tube(Xa, Ya, [(48.5, 56.0), (48.5, 67.5)], 2.5, b + 0.6),          # the barrel
            tube(Xa, Ya, [(63.6, 42.0), (63.6, 45.0), (62.2, 48.2), (59.4, 50.6), (56.4, 51.6)], 1.25, b + 1.3),
            tube(Xa, Ya, [(8.6, 44.5), (17.2, 44.5)], 0.65, z - 0.25),          # the plates' ridges
            tube(Xa, Ya, [(80.6, 44.5), (87.4, 44.5)], 0.65, z - 0.25),
        ]
        for p in parts:
            z = np.maximum(z, p)
        z = np.maximum(z, self.dome(Xa, Ya, b))
        z = np.maximum(z, self.stack(Xa, Ya))
        return self.eye(Xa, Ya, z, b)

    def dome(self, Xa, Ya, b):
        (c0, r0), (rx, ry), p, top = DOME
        q = ((np.abs(Xa - px(c0)) / rx) ** p + (np.abs(Ya - py(r0)) / ry) ** p) ** (1.0 / p)
        rim = b + 1.0
        z = rim + (top - rim) * np.sqrt(np.clip(1.0 - q * q, 0.0, None))
        (ac, ar), (lc, lr), (rc, rr) = NOTCH
        tri = [(px(lc), py(lr)), (px(ac), py(ar)), (px(rc), py(rr))]
        within = inside_tri(Xa, Ya, tri)
        z = rim + (z - rim) * np.sqrt(np.clip(seg_dist(Xa, Ya, tri) / NOTCH_ROUND, 0.0, 1.0))
        sx, (s0, s1), sd = SEAM
        along = smoothstep(py(s0) + 1.0, py(s0) - 1.0, Ya) * smoothstep(py(s1) - 1.0, py(s1) + 1.0, Ya)
        z = z - sd * np.exp(-((Xa - px(sx)) / 0.8) ** 2) * along
        for rw in RUNGS:
            z = z + 0.45 * np.clip(1.0 - (((Xa - px(48.5)) / 0.9) ** 2 + ((Ya - py(rw)) / 0.6) ** 2), 0.0, None)
        return np.where((q < 1.0) & ~within, z, -1.0)

    def stack(self, Xa, Ya):
        out = np.full(np.shape(Xa), -1.0)
        for (c0, c1, r0, r1), (ztop, zlow) in STACK:
            x0, x1, y1, y0 = px(c0), px(c1), py(r0), py(r1)
            inside = (Xa > x0) & (Xa < x1) & (Ya < y1) & (Ya > y0)
            t = np.clip((y1 - Ya) / (y1 - y0), 0.0, 1.0)
            edge = np.minimum(np.minimum(Xa - x0, x1 - Xa), np.minimum(y1 - Ya, Ya - y0))
            z = ztop + (zlow - ztop) * t - 0.5 * (1.0 - np.sqrt(np.clip(edge / 0.5, 0.0, 1.0)))
            out = np.where(inside, np.maximum(out, z), out)
        return out

    def eye(self, Xa, Ya, z, b):
        (c0, r0), R, r, pit_r, (gx, gy, gh) = EYE
        x0, y0 = px(c0), py(r0)
        d = np.hypot(Xa - x0, Ya - y0)
        axis = float(self.base(np.array([x0]), np.array([y0]))[0]) + EYE_Z
        ring = axis + np.sqrt(np.clip(r * r - (d - R) ** 2, 0.0, None))
        z = np.where(np.abs(d - R) < r, np.maximum(z, ring), z)
        pit = axis - 1.8
        gem = pit + gh * np.sqrt(np.clip(1.0 - ((Xa - x0) / gx) ** 2 - ((Ya - y0) / gy) ** 2, 0.0, None))
        return np.where(d < pit_r, np.maximum(pit, gem), z)


# --- Painting -----------------------------------------------------------------------------------------------------------
# Each face takes the ink of the pixels under it (their blurred masks: the most), in that ink's shade there (the
# sprite's, filled out from the ink's pixels and blurred), LIFT lighter and lighter still where the game's sun lights
# the face less (COMP: so that its light and the sprite's drawn light don't add up), the nearest of the ink's shades.

INKS = {   # shades, (metallic, roughness), glow strengths by shade, lift, contrast (about shade 7), comp
    "shell": ([0x22, 0x24, 0x26, 0x28, 0x2a, 0x2c], (0.25, 0.42), {}, 1.0, 0.9, 1.2),
    "metal": ([0x03, 0x05, 0x07, 0x09, 0x0b, 0x0d], (0.4, 0.3), {}, 1.0, 1.0, 2.0),
    "glow": ([0xc3, 0xc6, 0xc9, 0xcc, 0xce], (0.0, 0.25), {0xc3: 0.3, 0xc6: 0.38, 0xc9: 0.46, 0xcc: 0.54, 0xce: 0.6},
             0.5, 1.0, 1.0),
    # the dome's glass when it lights: its dull green, the sky's sheen on it, its white-hot middle
    "glass": ([0x27, 0x29, 0x2b, 0x2d], (0.2, 0.12), {0x27: 0.1, 0x29: 0.14, 0x2b: 0.2, 0x2d: 0.28}, 0.6, 1.0, 1.0),
    "sheen": ([0x8a, 0x8c, 0x8e], (0.1, 0.1), {0x8a: 0.2, 0x8c: 0.28, 0x8e: 0.36}, 0.5, 1.0, 1.0),
    "hot": ([0x7e, 0x7f], (0.0, 0.2), {0x7e: 0.5, 0x7f: 0.62}, 0.0, 1.0, 0.0),
}
HOT = (0x1f, 0x2f, 0x7e, 0x7f)


def ink_mask(name, a, dome):
    """The pixels of a picture an ink paints (dome: the dome's pixels, where the frames draw its glass lit)."""
    ramp = np.where(a >= 0, a >> 4, -1)
    hot = np.isin(a, HOT) & dome
    if name == "shell":
        return (ramp == 2) & (a >= 2) & ~dome
    if name == "metal":
        return (ramp == 0) & (a >= 2)
    if name == "glow":
        return ramp == 12
    if name == "glass":
        return (ramp == 2) & dome & ~hot
    if name == "sheen":
        return ramp == 8
    return hot
DARK = 0x01
GROOVE_SHADE = 2.5                # the carapace this many shades darker down in its grooves
LIT_MEAN = 0.72


def pal(prefix, index, metallic, roughness, glow=0.0):
    extra = dict(emission=k.level_palette()[index], emission_strength=glow) if glow > 0 else {}
    return k.material("%s_%x" % (prefix, index), palette=index, metallic=metallic, roughness=roughness, **extra)


def mat_of(key):
    if key == "dark":
        return pal("shell_dark", DARK, 0.2, 0.5)
    shades, (met, rough), glows, _, _, _ = INKS[key[0]]
    return pal("shell_" + key[0], key[1], met, rough, glows.get(key[1], 0.0))


class Paint:
    """How a look (its picture) paints the shell."""

    def __init__(self, a, shell):
        self.a, self.shell = a, shell
        shade = np.where(a >= 0, a & 15, 0).astype(float)
        ramp = np.where(a >= 0, a >> 4, -1)
        self.inks = []
        dome = shell.dome_pixels()
        for name, (shades, _, _, lift, contrast, comp) in INKS.items():
            mask = ink_mask(name, a, dome)
            if not mask.any():
                continue
            soft = blur(gw.fill(shade, mask), 0.5)
            self.inks.append((name, shades, blur(mask.astype(float), 0.6), 7.0 + contrast * (soft - 7.0), lift, comp))
        self.dark = blur((a == DARK).astype(float), 0.55)

    def sample(self, field, Xa, Ya):
        fc = np.clip(np.asarray(Xa, float) - LEFT - 0.5, 0.0, W - 1.0)
        fr = np.clip(TOP - np.asarray(Ya, float) - 0.5, 0.0, H - 1.0)
        c0 = np.minimum(np.floor(fc).astype(int), W - 2)
        r0 = np.minimum(np.floor(fr).astype(int), H - 2)
        tc, tr = fc - c0, fr - r0
        return ((field[r0, c0] * (1 - tc) + field[r0, c0 + 1] * tc) * (1 - tr) +
                (field[r0 + 1, c0] * (1 - tc) + field[r0 + 1, c0 + 1] * tc) * tr)

    def keys(self, Xa, Ya, normals):
        lit_by = gw.sun_on(normals)
        weights = np.stack([self.sample(ink[2], Xa, Ya) for ink in self.inks], 0)
        which = weights.argmax(0)
        dark = self.sample(self.dark, Xa, Ya)
        groove = GROOVE_SHADE * (self.shell.rib(Xa, Ya) - 1.0)
        per = [gw.nearest(self.sample(soft, Xa, Ya) + lift + comp * (LIT_MEAN - lit_by) +
                          (groove if name == "shell" else 0.0), shades)
               for name, shades, _, soft, lift, comp in self.inks]
        out = []
        for i in range(len(Xa)):
            w = which[i]
            if dark[i] > 0.6 and weights[w, i] < 0.35:
                out.append("dark")
            else:
                out.append((self.inks[w][0], int(per[w][i])))
        return out


def limit_materials(keys, limit=15):
    """Merges keys into the nearest shade of their ink until at most `limit` are left (the rarest shade of the ink with
    the most shades first; polish_gyges_maw's)."""
    keys = list(keys)
    while True:
        used = {}
        for key in keys:
            used[key] = used.get(key, 0) + 1
        if len(used) <= limit:
            return keys
        per_ink = {}
        for key in used:
            if isinstance(key, tuple):
                per_ink.setdefault(key[0], []).append(key)
        ink = max(per_ink, key=lambda name: (len(per_ink[name]), name))
        rarest = min(per_ink[ink], key=lambda key: (used[key], str(key)))
        same = [o for o in per_ink[ink] if o != rarest]
        to = min(same, key=lambda o: (abs((o[1] & 15) - (rarest[1] & 15)), -used[o]))
        keys = [to if key == rarest else key for key in keys]


def assign(obj, keys):
    keys = limit_materials(keys)
    order = sorted(set(keys), key=lambda key: str(key))
    slot = {key: i for i, key in enumerate(order)}
    mesh = obj.data
    mesh.materials.clear()
    for key in order:
        mesh.materials.append(mat_of(key))
    mesh.polygons.foreach_set("material_index", [slot[key] for key in keys])
    mesh.update()


# --- The pieces -----------------------------------------------------------------------------------------------------------

LAYOUT = [(153, 0, 0), (155, 24, 0), (157, 48, 0), (159, 72, 0), (191, 0, 28), (193, 24, 28), (195, 48, 28),
          (197, 72, 28), (229, 0, 56), (241, 24, 56), (243, 48, 56), (235, 72, 56), (267, 12, 84), (269, 36, 84),
          (271, 60, 84)]
FRAMES = {161: 193, 199: 193, 237: 193, 275: 193, 165: 193, 203: 193,       # the dome lit (772: 193's frames)
          163: 195, 201: 195, 239: 195, 277: 195, 167: 195, 205: 195,       # (773: 195's)
          231: 241, 233: 243}                                               # the eye open (774, 775)
LOOK_OF = {161: "dome161", 163: "dome161", 199: "dome199", 201: "dome199", 237: "dome237", 239: "dome237",
           275: "dome275", 277: "dome275", 165: "dome165", 167: "dome165", 203: "dome203", 205: "dome203",
           231: "eye231", 233: "eye231"}


def box_of(sprite):
    c0, r0 = {s: (c, r) for s, c, r in LAYOUT}[sprite]
    return (px(c0), px(c0 + 24), py(r0 + 28), py(r0))


def models():
    """(model name, the sprite whose place it takes, its look)."""
    out = [("green_shell_%d" % s, s, "idle") for s, _, _ in LAYOUT]
    out += [("green_shell_%d" % f, s, LOOK_OF[f]) for f, s in FRAMES.items()]
    return out


def check(shell, sheet):
    """The shell's outline as the camera sees it (the sheared heightfield puts each point where the sprites draw it: its
    cells) against the sprites' pixels, the whole and each piece."""
    covered = gw.own_coverage(lambda Xa, Ya: shell.cells(Xa, Ya), W, H, LEFT, TOP)
    mask = [[False] * W for _ in range(H)]
    for sprite, c0, r0 in LAYOUT:
        for r, line in enumerate(k.sprite_mask(sheet, sprite)):
            for c, v in enumerate(line):
                if v:
                    mask[r0 + r][c0 + c] = True
    mk.compare("the green shell (its 96 x 112 picture)", covered, mask)
    for sprite, c0, r0 in LAYOUT:
        sub_c = [row[c0:c0 + 24] for row in covered[r0:r0 + 28]]
        sub_m = [row[c0:c0 + 24] for row in mask[r0:r0 + 28]]
        both = sum(p and q for rp, rq in zip(sub_c, sub_m) for p, q in zip(rp, rq))
        either = sum(p or q for rp, rq in zip(sub_c, sub_m) for p, q in zip(rp, rq))
        print("silhouette overlap green_shell_%d (j %d): %.3f" % (sprite, sprite, both / max(1, either)))


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    sheet = None
    if "check" in options:
        sheets = options["check"]
        sheet = os.path.join(sheets, "enemy_J.png") if os.path.isdir(sheets) else sheets
    shell = Shell(picture("idle"))
    if sheet and only is None:
        check(shell, sheet)
    plate = gw.Plate((-48.0, 48.0, -56.0, 56.0), shell.heights, cells=shell.cells)
    paints = {}
    for model, sprite, look in models():
        if only is not None and model not in only:
            continue
        if look not in paints:
            paints[look] = Paint(picture(look), shell)
        k.reset()
        box = box_of(sprite)
        obj, kinds, _ = plate.mesh(model, gw.piece_owner(box))
        centres, normals = gw.face_data(obj)
        centres, normals = np.round(centres, 4), np.round(normals, 4)     # (Blender's float noise left out)
        top = paints[look].keys(centres[:, 0], centres[:, 1], normals)
        keys = [top[i] if kinds[i] == 0 else "dark" for i in range(len(kinds))]
        assign(obj, keys)
        gw.finish_piece(model, [obj], box, out, options)


# --- The sprites' pixels ------------------------------------------------------------------------------------------------
# Each pixel its palette index as two hex digits ('..' none). PICTURE: the 96 x 112 picture the events lay out, its rows
# 2-102 (the rest are empty); PATCHES: the runs of pixels ('row:column:hex') where the frames differ from it (the dome
# lit: j 161 beside 163 in 193's and 195's places, ...; the eye open: j 231 beside 233 in 241's and 243's).

PICTURE = """
........................................................................01010101010101010101010101010101010101010101012101......................................................................
..............................................................0101010101242027262626242726262626252525252521252424242126240101010101............................................................
........................................................0101012422272626262127262626232826262626262626252521272525252126242424212222010122......................................................
..................................................0101012426262623292727272228272727242b27272626262626262522292525252229252424212424242125010101................................................
..............................................010124242228272727242b292829242a292828252e272727272726262626222b272626222b2625252126242422282423220101............................................
............................................0124252626222b2a2828252e2b2b2b272c2b2a29252f282727272727272626222c292827222d282725222926262228242424242301..........................................
........................................01012228272727232c2b2a29262f2c2c2e2b2f2d2b2a262f292928282828282827222c2a2827222c2a2925222b292822282624242424230101......................................
......................................0123242429292928232d2c2b2a272f2c2e2f2c2f2e2c2a262f2a2a2a292929292929262b292727232a292925222b2a282229272524242424232201....................................
....................................01232526242b2a2a29232c2a2a2a272e2c2e2f2c2f2e2c2a262f2c2b2b2b2a2a2a2a2a262b262626232a272625222a2828222d28272525242424232101..................................
..................................0124252626242c2a2828242a2a292a272e2c2d2e2b2f2d2c2a2529282727272726262626252a262626232826252522292726232e2a28272525242424232201................................
..................010102........012425252626252a282727242a29292a272d2c2d2d2a2e2d2c2a272d2b2b2a2a2a2a2a2b2c272a262626232826252522282525232c2a2828272625242424232201........200101................
................0125260301010101242525262626242a2727282429292929272c2c2c2d2a2e2d2c2a262b29292828282827272a2528272626232826262522272525232b2828282727252424242323220101010121242301..............
..............01272427040506060123252526262623282727282428292929282c2b2c2c292d2c2c2a262a29292828282827272a2428272626232826262522272525242a262626262625242424242322010102032324232301............
............2026292428060809090123252626262523272727282528292828282c2b2b2c292d2c2b2a26292929282929292828292427272726232826262522252525242925242525252625242424232201020504262425242301..........
..........2026292a2428050b0c0a012324262626242227272728242627280705212a2a2b282b2b2b2a2629292928292424242325242627272623282626240121222524292524242424252524242423230206070729242526232301........
..........20272a2b2428040c0e0c012324252626232126262727232506090f0d0b01292a292b2b2b2a26292929282923242423252426272424232222220106080701222825242424242424242424232301090e0b2a242726242301........
........012627292c242805070a08012324242301012020202001010206090b0a08060101012020012a262929292829232426262724242201010101010106090e0807012101010101202223232424232302090c0a2a24282624242301......
........012528292d2428040508060123240101030406050404040404040508080503020a08080806012629292928292324272728242001080a0908070106090a0907050404040404040403022123232302080a092b242a2624242301......
......01252528292c2428040507060123010405070a090806060606060606060504030209070606050501292929282923242727282201090c09070706010506070706060606060606050504040303232323060707272123210121222201....
......012221232423012404050606010104040506042b2d2d2c2b2a2a29040403040403010104030303012123252525212427272822010705060501010102030405080705050505050604040403030303230506062d28282a2726252301....
......012526292a2c24280405060603030305062a2e2f2d2c2b2a28270101010101010203030102030401232627292b23242727282301070403010203030101010123242a2b2a2a2a2927230203030304050606062a26262a2726252301....
......01252628292a242803050606030304292c2e2e2f2c2c2c2c292701010102030303040404020404050120212326222427272701030204010103040503030202032a2a28272727282827252302030405060606252322222222222201....
......0124212323210122020506060404282c2c2c2c2e292a26252a2920010203040404040404050a0908060124272b22242727040b080704010204050606050404042a292a2b29282727262625242304050606062b2928272a28262301....
......012526292b2625262005060604292a2a2a2b2b2e272a27242428210102030405050505050c0908080806012024202427040d09070705010304060606060606052a282c262425252326252424242303050606282523262b28262301....
......012526292925252323220606262a2a2929292a2d272b27262424010103040506060606060a080708080601252a222327030907070705010304060606060606062a2c29232527282225252423232423030327272022222223222101....
....0123222226222322222b2622262b28282727292a2d272c2726262401010304050606060606070606060606060603040403050605040503010304060606060606062b28232527292a2224252423232324232627282121282a2c28262601..
..012525272b2c29262320262522232927262627292a2d272d2826262601010304050606060605050506070808080806090807080807060504020203060606060606062b232426292a2b22232524232323252522252a252326292c2825252501
..012525272a2d29262824202022232a27262627292a2d272e2727262601010304050606060505070808080808080805060506070808080807050201030606060606062a2326282a2b2b222325242323232527222223222526292b2824242501
..01252527292b29262728232328232a27262627292a2c272e2727262601010304050606040608080b0d0d0d0b0908070c0806070808080808070604010305060606062a23272a2a2b2b222325242323232426242524252726282b2824242401
..01252527292b29262527282928232a27262627292a2c282f27262627010103040506040608080a0e0f0f0f0e0c0907080505070808080808080707040103050606062a24282a2b2b2c222123242323232426222627272526272a2824242401
..01252527292929262525262726232a27262627292a27252d2b2b2928010103040404050708080b0f0f0f0f0e0d09070c0806070808080808080807060401030506062923282a2b2c2d22200120232323242622242424242526272624242301
..01252526282727262525252524232927262627272425252423232221010103040304070808080a0e0f0f0f0d0b0907070505070808080808080807060503010305062823282a2c2d2e22232201202323242622242424242525262524242301
..0125252526272626252525242423262626262723292c26262423232201010302040708080808090a0d0c0c0b0a09070a0805070808080808080807070604030103052723242323232222242420012123242523242424242525252424232301
..01252525252825250101010101010101262622272e2b2a292828252501010302050708080808080909090909090707070706050808080808080807070605030103022525262727262322242523010101200101010101012424242323232301
..01012525252a25010202030303030302010125292b2b2a29282827260102010306070808080808080808080808070b090808040708080808080807070605030301012123212427292826262524010101010101010101010125242323230101
....012525252a01020304040404040404030220292a2b2a29272322220102010406070808080808080808080808070a0808080407080808080808070706050304010120200101012529272625010101020203030303030201252423232301..
....012525252b01030404050606060606050403222a2b2a292222222201030104060708080808080808080808070707070707050608080808080807070605030401010101202101212a272620010102030405060606060505282424242301..
....012525252c0103040506060707070707060603232c2a232323232301010104060707080808080808080808070d0b0b0b0b0b0607080808080707060605030401010120202221012c2721010102030405060707070706052a2424242301..
....012525252b0103040506070707070707080805232c2a212224242424010103060607070808080808080808070b08080808080505070808070707060505030401012120212201212c2721010203040506070707070706052a2424242301..
....01252525270103040506070707070707080a07222b2a222225252524010103050607070708080808050606050b08080808080404060607070706060504030401012222222321222c2720010203050607070707070706042a2424242301..
....01252424240103040506070707070707080a07212b2a242325252525010103050606070707080808050b0a060d080808080804060a0305070606050402030501012222232421222c270101020405070707070707070603262425252301..
....01242323230101010304050505060607080a07202a29242325252525010103050506060707070707040907030b07070707070203060204060605040301040601012223242421222c270101020405070707070707070603232223242301..
....0101012223010508090a0c0c0c0d0606080a07012829232425252525010103040505060606070707040807030a07070707070103060203060504030201050701202223242421222b270101020406070b0b0b0b0b0b0906222223010101..
........0123250105070808080808080b05060907012729242326252525010103040405050606060606020606030706060606060103050103050403020103070701012323242501212b2701010204060b090807060606060504212201......
....0101012525010506080808080808090a050607012629242229262525010102030404050505060606010101010101010101010101020102040302010205090401012323242501202b27010102040b090807060707070706052423010101..
....012527282501050608080808080809090b050601262923232a2626250101200203040404050505040101010101010101010101010101020202010104080a0121012324252520212a27010102090908070607070708070605282b262401..
....0125292e2501040608080808080809090a0c0501262923232b262626010101020303040404040301010203030303030303030303020101020102040a0d040121012425252621222a27010207070807060707070808070605282a242401..
....0125292d2501040608080808080809090a0b0901262923232b272626010124010203030304040101020303030404050606060606050301040406090d05012221012525262621222a270105050707060607070808080706052726242401..
....012529262501040608080808080809090a0b0901272923232b272726010128220102020303030101020303040405060606050505040301060708070401212221012727262621222a270104050606060707080808080706052624242401..
....012427242501040608080808080809090a0a0801272923222b2727270121282321010102020201020407080909050606050b0808060301030302010122222221012a27272621222a270103050606060707080808080706052524242401..
....012424242401040608080808080809090a0a0801272823222b2727270121c6c3c022012201010102040607090c0505050b0a0707070501010101222222222320212a27272721222a270103050506060707080808080706042324242401..
......0123232301040708080808080809090a090801272722222b2727270121c9c4c2c10122222101030507080c06070409090b0907070501202001222423232321212a27272721212a2701020505060607070808080807060122222301....
........010101030506080808080707070707070701282721222b2727270122c9c4c3c201222321010406070a070405040607080b0707060121220121c1c0c0c121212a27272722212a27010204050607060708080808070604010101......
..............01050607080807060e0b0b0b0b0b012a2721222b2727270121c9c4c3c3202223230126272a0805040401050608090906020121220120c2c0c1c221212a27272720222a27010307090a0b0c0708080807060401............
................0105060707060d0909090a0a0b012a2721222b27272701212a272626212223242629292b24050303010404050529262220212320202724262621212a27272701222927010307080909090c070807060501..............
..................010607060c090909090a0b0c20282701212b27272701212b27272721222324262a292a26250401070103012528292620222421202826272722212a2727270121292620030407080909090a08070401................
..................0104050c090909090a0b0b0c20272601212a27272701212c27272721222324262a292826260109060901012527292820222421202a26272621212a272726012229260104030608090909090a060301................
....................010c0a0909090a0b0b0c2b20262601212a27272701202d27272721222324262a272626250c0603070b012527272921222421212b27272622212a27262622222926012604030608090909090a01..................
....................01090909090a0b0b0c2d2801272601212a27272701212d27272721222324262b29282726090403070a012326252622232421222b27272621212a26262622232926012726040406080909090901..................
....................010909090a0b0c0c0c292501282601232927272701222d27272720222324262401010122090403070a010101012123242421222b27272621222926262622232925012726200404060809090901..................
....................0109090a0b0c0c2d09262501272601222927272701222d27272720222324262725242401090403070a012223252826252421222b27272620212926262622232825012726012503050608090901..................
....................01090a0b0c0d2b2906262501272601222827272701222e27272720222324262727262601090303070b012224252827252423232b27272621222926262621212825222726012525040404060701..................
....................010b0b0a0a0a2a2605262501272601222827272701222f27272720222324262727272601090304070b012224262727252424252b27262522232926262522212825212726012523030203030501..................
....................010101082a06282504262501282601212826272701222e27272720222324262727272701090404070b012224262727252424252b26262522232926252522222825212726202424012423010101..................
........................01262505282503262501282601212826262720222d272727212223242627272727010704030608012324262727252424252a2626252223292525252222282521272601242401232401......................
........................20232404282520262501272601212826262721222c272727212102030405050605030103010501020405050404252323242a2626252223282525252322282522282420242420232501......................
........................01232422282420262501272601212826262621222b272727210102020304040403030204020501020304040404040302242a2626252122282525252322282523272420242321242501......................
........................01232422272401272520272501212826262620232b272727210101010203030302010205030501010102030303030202242a2625242122282525252222282522272420242221252501......................
........................01232421272401272520262501202826262620232b27272722010101020303020103050504040302010102030303020224292525242122282525252222282422272420232221272501......................
........................01232420272401272520262520212826262621232a27272723010101020302010207050505040303010101020303020223292525242122282525252222272422272420232322282501......................
..........................012420272401262520262521202826262622232a262727230101010203010508050301010101020301010102030202232925252421222825252522212724222623202324222720........................
..........................012420252401252520262520212726262622232a262626220101010202010a06020101010101010202010101030202242925252421222825252521212724222623202425222501........................
..........................0123212424012624012625212127252626212229262626220101010101010804010101010101010102010101020202242826252421222825252421202722222523202426222301........................
............................012124240126240126252122262525262121282626262201010101020109030101010101010101020101010102022428262524212128252424210127222225212025272201..........................
............................012124240125240125252221252525252021282626262201010102030107030101010101010101020101010102012427272524012127242424200127222125222026282201..........................
............................012124240125240124242120252525252020272626262222010102030105040101010101010102030101010202232427262524012027242423010127222024232127272201..........................
..............................01242401252401242401202525252521202725252521210101020301030403010101010102030301010103022324272525230120272323240120272201252421282801............................
..............................01242401262401242401012525252522202725252521210101020302020304030101010203030201010203022323272524240120272323240120272301272621282501............................
................................0124012624012524010124242525222127252525212101010203030202030403030303030201010303020223232724232401012623222401202825012727212501..............................
................................0124012624012524010124242424212227252525212101010203030302010101010101010101030302020123222624222401012623222420202726012927212401..............................
..................................010125242025240101242424242121262324242001010101020303030101......010203030302010101222226242224010126232224202028280129262101................................
..................................010124242026240101242424242121262424242001010101010101010101......010101010101010101222226242225010127232224202029280127242201................................
....................................0124242027250101242424242220c2c1c1c12001230120202221222301......0121212121212101242222c3c021c301012623222520202a2a01252201..................................
......................................01240126250120242424242101252424242001220101202223242401......0122222222222201242222c32221c401012624232620202c2b202401....................................
........................................010126250120242524242001252424242001230121212324252501......0124232323222301242222c32221c401012825252820202b282101......................................
..........................................0125250120242525242001252424240120242201222124252401......0124242424230124242222c2c021c40101282726292020282501........................................
............................................01240120242627242001252424250120242322012222242401......0124242424012423242222c22222c401012928282a20202422..........................................
..............................................010120242627240120242524260120242422012222242401......0124242424012422242222c222c0c401202a292a2b202001............................................
................................................0120242627250120242524260120242424012222242401......0124242424012422242122c3c0c3c501012b2a2a2a2001..............................................
..................................................01242728260101252624260120242424012222242401......0124242424012421242022c4c1c3c501202c2a292601................................................
....................................................012427270101282524260120242424012222242401......01242424240124222520222926282901212b282420..................................................
......................................................0124260101282524260120242424012222242401......01242424240125232620222b28292a0122272401....................................................
........................................................012501012925242601202424240122222401..........012424240126242701202d2a2a2901222501......................................................
..........................................................0101012a26242601202524240122222401..........012424240129242901012c2a2a28012101........................................................
............................................................01202a272726012027252401222201..............012424012a282a01202d2a29272001..........................................................
..............................................................0128262826012028272501222301..............012424012c2b2c01202b29282601............................................................
................................................................212527260120292827012201..................0124012c2b2b012026262620..............................................................
..................................................................0125260121292a270101......................01012a26280120242420................................................................
....................................................................20250121282a2501..........................0127262501202401..................................................................
......................................................................20012127262401..........................01242524202001....................................................................
........................................................................010120010101..........................010101010101......................................................................
"""

PATCHES = {
    "dome161": """
28:29:..
28:41:67292a2a2a2a
28:51:2a2a2967
29:29:..
29:38:66292a2a2a2a2a2a2a
29:51:292a2a2a0706
29:59:..
30:29:..
30:37:05072a2b8a8a8a2b2a2a
30:51:2a2a2a2a2a2a2905
30:60:..
31:24:1f
31:29:..
31:36:05072a2b8c8d8d8d8c2c2a
31:51:2a0a2a2a2a2a2a2906
31:61:..
32:29:..
32:35:66062a2a888d8e7f7f8c8b2b
32:51:a90a2a2a2a2a2a2a2905
32:62:..
33:29:..
33:35:06072a2a2b8c8d7f8e1e882a
33:51:2a0a0a0a2a2a2a2a296766
33:63:..
34:29:..
34:34:06072a2a2a2b6c8b890d0c2b2a
34:51:2a0a0a0a0a2a2a2a292967
34:64:..
35:29:..
35:34:06072a2a2a0a0b2b0b0b2b2a
35:52:2a0a0a0a2a2a2a29292866
35:64:..
36:29:..
36:31:..
36:34:062a2a2a2a0a0a2a0a0a2a2a
36:52:2a2a0a2a0a2a2a292928
36:65:....
37:29:..
37:31:..
37:34:292a2a2a2a2a2a2a0a0a2a2a
37:52:2a2a2a2a0a0a2a292928
37:65:....
37:69:......
38:29:..
38:31:..
38:34:06072a2a2a2a2a2a2a2a2a
38:53:2a0a0a0a2a2a292928
38:65:..
38:67:....
38:71:..
39:29:......
39:34:29292a2a2a2a2a2a2a2a2a
39:53:2a2a2a2a2a2a292928
39:65:......
40:30:....
40:33:076729292a2a2a2a2a2a2a2a
40:53:28292a2a2a29292928
40:65:....
40:71:..
41:30:....
41:33:06672929292a2a2a2a
41:56:292a29292928
41:65:....
42:30:....
42:33:0667282929292a2a2a
42:57:292929282723
42:65:....
43:30:....
43:34:0667282929292929
43:56:26292928272521
43:65:....
44:30:....
44:35:07672829292929
44:56:25292827252402
44:65:..
45:30:....
45:36:076767286728
45:52:..
45:57:2827252403
45:65:....
45:71:..
46:30:....
46:37:0706070707
46:43:......................
46:55:..232625240303
46:65:....
46:71:..
47:30:....
47:42:..
47:54:....
47:57:030302
47:64:..
47:66:..
48:30:......
48:41:....
48:55:..
48:58:..
48:64:..
48:66:..
49:30:....
49:33:..
49:40:..
49:56:..
49:63:..
49:66:..
50:30:....
50:34:..
50:40:..
50:56:..
50:62:..
50:66:..
51:30:..
51:35:....
51:40:..
51:56:..
51:66:..
52:30:..
52:32:292623
52:36:..
52:38:......
52:56:........
53:30:..
53:32:2a272524..
53:40:..
53:56:..
53:59:..
54:30:..
54:32:2a272625..
54:40:..
54:56:..
54:59:..
54:61:24232324
55:30:..
55:32:2a272626
55:40:..
55:56:..
55:59:..
55:61:25232425
""",
    "dome199": """
28:29:..
28:41:272929292929
28:51:29292928
29:29:..
29:38:2628292a2a2a2a2a2a
29:51:292a29292927
29:59:..
30:29:..
30:37:26292a2b2b88882b2a2a
30:51:2a2a2a2a29292827
30:60:..
31:24:1f
31:29:..
31:36:04292a2a8a8b8b8b8b2b2b
31:51:2b0c2b2a2a2a292827
31:61:..
32:29:..
32:35:2528292a2b8b8cafaf8b8a2b
32:51:1c2c2b2b2a2a2a292827
32:62:..
33:29:..
33:35:27292a2a878b8baf8c2e892b
33:51:2b0c2c0c2b2a2a2a292825
33:63:..
34:29:..
34:34:2728292a2a876d8a896e0d2b2a
34:51:2a0c0c2c2c2a2a2a292928
34:64:..
35:29:..
35:34:27292a2a2b0c0c870c0c872a
35:52:2b2c0c2c2a2a2a29292826
35:64:..
36:29:..
36:31:..
36:34:28292a2b2b0c2c2b2c0c2b2a
36:52:2a2b2c2b2c2b2a29292827
36:65:....
37:29:..
37:31:..
37:34:28292a2a2b2b2a2b2c2c2b2a
37:52:2a2b2b2b0c2c2a29292827
37:65:....
37:69:......
38:29:..
38:31:..
38:34:28292a2a2a2b2a2b2b2b2a
38:53:2b2c0c2c2b2a29292827
38:65:..
38:67:....
38:71:..
39:29:......
39:33:0729292a2a2a2a2a2a2a2a2a
39:53:2a2b2b2a2a2a29292827
39:65:......
40:30:....
40:33:072829292a2a2a2a2a2a2a2a
40:53:29292a2a2a2929292827
40:65:....
40:71:..
41:30:....
41:33:06282929292a2a2a2a
41:56:292a2929292826
41:65:....
42:30:....
42:33:0627282929292a2929
42:56:27292929282724
42:65:....
43:30:....
43:33:060728282929292929
43:56:262929282726c066
43:65:....
44:30:....
44:35:6a282829292929
44:56:25292827272504
44:65:..
45:30:....
45:36:6a2828282828
45:52:..
45:56:25282726250504
45:65:....
45:71:..
46:30:....
46:36:066a07080807
46:43:......................
46:55:..242626250504
46:65:....
46:71:..
47:30:....
47:42:..
47:54:....
47:57:04660402
47:64:..
47:66:..
48:30:......
48:41:....
48:55:..
48:58:..
48:64:..
48:66:..
49:30:....
49:33:..
49:40:..
49:56:..
49:63:..
49:66:..
50:30:....
50:34:..
50:40:..
50:56:..
50:62:..
50:66:..
51:30:..
51:35:....
51:40:..
51:56:..
51:66:..
52:30:..
52:32:292623
52:36:..
52:38:......
52:56:........
53:30:..
53:32:2a272524..
53:40:..
53:56:..
53:59:..
54:30:..
54:32:2a272625..
54:40:..
54:56:..
54:59:..
54:61:24232324
55:30:..
55:32:2a272626
55:40:..
55:56:..
55:59:..
55:61:25232425
""",
    "dome237": """
28:29:..
28:41:27c5c5c6c6c6
28:51:c5c5c527
29:29:..
29:38:2628c5c7c7c8c8c7c7
29:51:c7c7c6c5c526
29:59:..
30:29:..
30:37:25c5c7cacbcbcccbcac8
30:51:cacbcac8c5c52826
30:60:..
31:24:1f
31:29:..
31:36:2528c7c9cececfcfcfcbcb
31:51:cd5ecdcbc8c7c52826
31:61:..
32:29:..
32:35:2527c6c8cccfcf7e7ecfcfcc
32:51:2d2dcdcdcbc9c7c52826
32:62:..
33:29:..
33:35:26c5c9c8cdcfcf7ecf7ecfcb
33:51:cd5e2d5ecdcbc8c7c52725
33:63:..
34:29:..
34:34:2627c6c8ccce0ecfce5f0eccca
34:51:cc5e5e2d2dccc9c7c7c527
34:64:..
35:29:..
35:34:26c5c8cbcd5e6ece6e6ececa
35:52:cd2d5e2dcbcac9c7c6c426
35:64:..
36:29:..
36:31:..
36:34:27c5c8cdcd5e2dcd2d5ecdcb
36:52:cbcd2dcd2dcdcac8c7c4c3
36:65:....
37:29:..
37:31:..
37:34:28c5c8cbcdcdcacd2d2dcdc7
37:52:c9cdcdcd5e2dcbc8c7c4c3
37:65:....
37:69:......
38:29:..
38:31:..
38:34:27c5c7cacccdcacdcdcdca
38:53:cd2d5e2dcdcbc8c7c5c3
38:65:..
38:67:....
38:71:..
39:29:......
39:33:07c5c5c8cacacacbc9c9caca
39:53:cbcdcdcccbc9c7c6c5c3
39:65:......
40:30:....
40:33:0727c6c8c9cbc9c9cac8c8c8
40:53:c6c8c9c9cac8c7c6c5c3
40:65:....
40:71:..
41:30:....
41:33:0727c5c6c8c9c9c8ca
41:56:c6c9c7c6c6c526
41:65:....
42:30:....
42:33:0727c4c6c6c7c8c6c6
42:56:c3c7c6c6c5c5c1
42:65:....
43:30:....
43:33:060827c4c6c6c5c5c5
43:56:c3c6c6c6c5c4c105
43:65:....
44:30:....
44:35:0a27c5c6c6c5c6
44:56:c2c6c6c5c4c306
44:65:..
45:30:....
45:36:0a2727c527c5
45:52:..
45:56:25c5c5c4c30866
45:65:....
45:71:..
46:30:....
46:36:060a08080807
46:43:......................
46:55:..c1c3c3c30805
46:65:....
46:71:..
47:30:....
47:42:..
47:54:....
47:57:04060603
47:64:..
47:66:..
48:30:......
48:41:....
48:55:..
48:58:..
48:64:..
48:66:..
49:30:....
49:33:..
49:40:..
49:56:..
49:63:..
49:66:..
50:30:....
50:34:..
50:40:..
50:56:..
50:62:..
50:66:..
51:30:..
51:35:....
51:40:..
51:56:..
51:66:..
52:30:..
52:32:292623
52:36:..
52:38:......
52:56:........
53:30:..
53:32:2a272524..
53:40:..
53:56:..
53:59:..
54:30:..
54:32:2a272625..
54:40:..
54:56:..
54:59:..
54:61:24232324
55:30:..
55:32:2a272626
55:40:..
55:56:..
55:59:..
55:61:25232425
""",
    "dome275": """
28:29:..
28:41:c3c5c6c7c7c7
28:51:c6c6c5c4
29:29:..
29:38:c2c4c6c8c8c9c9c8c8
29:51:c8c8c7c6c5c2
29:59:..
30:29:..
30:37:c1c5c8c9c9cacbcacac9
30:51:cbcccbc9c6c6c4c2
30:60:..
31:24:1f
31:29:..
31:36:c0c4c8c9cccccdcececacc
31:51:cf1fcfccc9c8c6c4c2
31:61:..
32:29:..
32:35:c1c3c7c9cccecf7e7ecfcfcd
32:51:7e7ecfcfcccac8c6c4c2
32:62:..
33:29:..
33:35:c2c5cac9cecece7ecf7ecfcc
33:51:cf1f7e1fcfccc9c8c6c4c1
33:63:..
34:29:..
34:34:c1c3c7c9cdcf1fcfce1f1fcdcb
34:51:ce1f1f7e7ecdcac8c8c6c4
34:64:..
35:29:..
35:34:c1c5c9cccf1f1fcf1f1fcfcb
35:52:cf7e1f7ecccbcac8c7c5c2
35:64:..
36:29:..
36:31:..
36:34:c3c6c9cecf1f7ecf7e1fcfcc
36:52:ccce7ecf7ececbc9c8c5c4
36:65:....
37:29:..
37:31:..
37:34:c4c6c9cccfcfcbce7e7ecec8
37:52:cacecfce1f7eccc9c8c5c4
37:65:....
37:69:......
38:29:..
38:31:..
38:34:c3c5c8cbcdcecbcececfcb
38:53:cf7e1f7ecfccc9c8c6c4
38:65:..
38:67:....
38:71:..
39:29:......
39:33:07c5c6c9cbcbcbcccacacbcb
39:53:cccfcecdcccac8c8c6c4
39:65:......
40:30:....
40:33:08c4c7c9cacccacacbc9c9c9
40:53:c8c9cacacbc9c8c7c6c4
40:65:....
40:71:..
41:30:....
41:33:07c4c6c7c9cacac9cb
41:56:c7cac8c8c7c6c3
41:65:....
42:30:....
42:33:07c3c5c7c7c8c9c7c7
42:56:c4c8c8c8c6c6c2
42:65:....
43:30:....
43:33:0609c4c5c7c7c6c5c6
43:56:c4c8c8c7c6c5c305
43:65:....
44:30:....
44:35:0bc4c6c7c7c5c7
44:56:c3c7c7c6c6c408
44:65:..
45:30:....
45:36:0bc4c4c6c4c6
45:52:..
45:56:c2c6c6c5c40a05
45:65:....
45:71:..
46:30:....
46:36:060b09090908
46:43:......................
46:55:..c2c4c4c40a06
46:65:....
46:71:..
47:30:....
47:42:..
47:54:....
47:57:05070804
47:64:..
47:66:..
48:30:......
48:41:....
48:55:..
48:58:..
48:64:..
48:66:..
49:30:....
49:33:..
49:40:..
49:56:..
49:63:..
49:66:..
50:30:....
50:34:..
50:40:..
50:56:..
50:62:..
50:66:..
51:30:..
51:35:....
51:40:..
51:56:..
51:66:..
52:30:..
52:32:292623
52:36:..
52:38:......
52:56:........
53:30:..
53:32:2a272524..
53:40:..
53:56:..
53:59:..
54:30:..
54:32:2a272625..
54:40:..
54:56:..
54:59:..
54:61:24232324
55:30:..
55:32:2a272626
55:40:..
55:56:..
55:59:..
55:61:25232425
""",
    "dome165": """
28:29:..
28:41:c4c7c9cacaca
28:51:c9c9c8c6
29:29:..
29:38:c1c3c6cbcbcccccbcb
29:51:cbcbcac9c7c4
29:59:..
30:29:..
30:37:c2c5cbcccccdcecdcdcc
30:51:cecfceccc9c8c5c2
30:60:..
31:24:1f
31:29:..
31:36:c0c4cbcccfcf7e2f2fcdcf
31:51:2f1f2fcfcccbc9c5c2
31:61:..
32:29:..
32:35:c1c4cacccf2f2f2f2f2f2f7e
32:51:2f2f2f2fcfcdcbc9c6c2
32:62:..
33:29:..
33:35:c3c8cdcc2f2f2f2f2f2f2fcf
33:51:2f1f2f1f2fcfcccbc9c4c2
33:63:..
34:29:..
34:34:c1c6cacc7e2f1f2f2f1f1f7ece
34:51:2f1f1f2f2f7ecdcbcbc7c4
34:64:..
35:29:..
35:34:c2c8cccf1f1f1f2f1f1f7ece
35:52:2f2f1f2f2fcfcdcbcac5c2
35:64:..
36:29:..
36:31:..
36:34:c4c9cccf1f1f2f2f2f1fcfcf
36:52:cf2f2f2f2f2fcecccbc6c3
36:65:....
37:29:..
37:31:..
37:34:c5c9cccf1f2f2f2f2f2f7ecb
37:52:cd2f2f2f1f2fcfcccbc8c5
37:65:....
37:69:......
38:29:..
38:31:..
38:34:c5c8cbcecf2f2f2f2f2fce
38:53:2f2f1f2f2fcfcccbc9c5
38:65:..
38:67:....
38:71:..
39:29:......
39:33:07c6c9cccecececfcecdcece
39:53:cf2f2f7ecfcdcbcbc9c6
39:65:......
40:30:....
40:33:08c5cacccdcfcdcdcecccccc
40:53:cbcccdcdcecccbcac9c7
40:65:....
40:71:..
41:30:....
41:33:07c5c9cacccdcdccce
41:56:cacdcbcbcac9c6
41:65:....
42:30:....
42:33:07c4c7cacacbcccaca
42:56:c7cbcbcbc9c9c5
42:65:....
43:30:....
43:33:0609c5c7cacac9c8c9
43:56:c7cbcbcac9c7c505
43:65:....
44:30:....
44:35:0bc5c8cacac8ca
44:56:c6cacac9c8c508
44:65:..
45:30:....
45:36:0bc5c5c7c7c9
45:52:..
45:56:c5c9c9c7c50a05
45:65:....
45:71:..
46:30:....
46:36:060b09090908
46:43:......................
46:55:..c4c6c5c60a06
46:65:....
46:71:..
47:30:....
47:42:..
47:54:....
47:57:05070804
47:64:..
47:66:..
48:30:......
48:41:....
48:55:..
48:58:..
48:64:..
48:66:..
49:30:....
49:33:..
49:40:..
49:56:..
49:63:..
49:66:..
50:30:....
50:34:..
50:40:..
50:56:..
50:62:..
50:66:..
51:30:..
51:35:....
51:40:..
51:56:..
51:66:..
52:30:..
52:32:292623
52:36:..
52:38:......
52:56:........
53:30:..
53:32:2a272524..
53:40:..
53:56:..
53:59:..
54:30:..
54:32:2a272625..
54:40:..
54:56:..
54:59:..
54:61:24232324
55:30:..
55:32:2a272626
55:40:..
55:56:..
55:59:..
55:61:25232425
""",
    "dome203": """
28:29:..
28:41:c8cacccdcdcd
28:51:cccac7c4
29:29:..
29:38:c4c6cccececfcfcece
29:51:cececdccc9c5
29:59:..
30:29:..
30:37:c4cacecfcf7e2f7e7ecf
30:51:2f2f2fcfcccbc7c3
30:60:..
31:24:1f
31:29:..
31:36:c0cacecf2f2f2f2f2f7e2f
31:51:2f1f2f2fcfceccc9c4
31:61:..
32:29:..
32:35:c3c8cdcf2f2f2f2f2f2f2f2f
32:51:2f2f2f2f2f7ececccac5
32:62:..
33:29:..
33:35:c6cbcecf2f2f2f2f2f2f2f2f
33:51:2f1f2f1f2f2fcfceccc9c4
33:63:..
34:29:..
34:34:c3c8cdcf2f2f1f2f2f1f1f2f2f
34:51:2f1f1f2f2f2f7ecececcc8
34:64:..
35:29:..
35:34:c4cbcf7e2f1f1f2f1f1f2f2f
35:52:2f2f1f2f2f2f7ececdcbc4
35:64:..
36:29:..
36:31:..
36:34:c7cccf2f2f1f2f2f2f1f2f2f
36:52:2f2f2f2f2f2f2fcfcecbc7
36:65:....
37:29:..
37:31:..
37:34:c9cccf2f2f2f2f2f2f2f2fce
37:52:7e2f2f2f1f2f2fcfcecbc9
37:65:....
37:69:......
38:29:..
38:31:..
38:34:c8cbce2f2f2f2f2f2f2f2f
38:53:2f2f1f2f2f2fcfceccc9
38:65:..
38:67:....
38:71:..
39:29:......
39:33:07c9cccf2f2f2f2f7e7e2f2f
39:53:2f2f2f2f2f7ecececcc9
39:65:......
40:30:....
40:33:08c8cccf7e2f7e7e2fcfcfcf
40:53:cecf7e7e2fcfcecdccc9
40:65:....
40:71:..
41:30:....
41:33:07c7cbcccf7e7ecf2f
41:56:cd7ecececdccc8
41:65:....
42:30:....
42:33:07c6c8cccccecfcdcd
42:56:cacecececcccc6
42:65:....
43:30:....
43:33:0609c7c8cccccccbcc
43:56:cacececdcbc9c605
43:65:....
44:30:....
44:35:0bc7c9cbcdcbcd
44:56:c9cdcdcccbc808
44:65:..
45:30:....
45:36:0bc7c8cbc9cb
45:52:..
45:56:c8cbcbcac70a05
45:65:....
45:71:..
46:30:....
46:36:060b09090908
46:43:......................
46:55:..c6c7c6c60a06
46:65:....
46:71:..
47:30:....
47:42:..
47:54:....
47:57:05070804
47:64:..
47:66:..
48:30:......
48:41:....
48:55:..
48:58:..
48:64:..
48:66:..
49:30:....
49:33:..
49:40:..
49:56:..
49:63:..
49:66:..
50:30:....
50:34:..
50:40:..
50:56:..
50:62:..
50:66:..
51:30:..
51:35:....
51:40:..
51:56:..
51:66:..
52:30:..
52:32:292623
52:36:..
52:38:......
52:56:........
53:30:..
53:32:2a272524..
53:40:..
53:56:..
53:59:..
54:30:..
54:32:2a272625..
54:40:..
54:56:..
54:59:..
54:61:24232324
55:30:..
55:32:2a272626
55:40:..
55:56:..
55:59:..
55:61:25232425
""",
    "eye231": """
56:32:c9c4c3c3
56:61:c4c1c3c3
57:32:ccc4c4c4
57:61:c5c3c4c4
58:32:ccc4c4c4
58:61:c9c3c4c3
59:32:ccc4c4c4
59:61:ccc4c4c3
60:32:ccc4c4c4
60:61:ccc4c4c3
61:32:ccc4c4c4
61:61:ccc4c4c3
62:32:ccc4c4c4
62:61:ccc4c4c3
63:32:ccc4c4c4
63:61:ccc4c4c3
64:32:ccc4c4c4
64:61:ccc4c3c2
65:32:ccc4c4c4
65:61:ccc3c3c2
66:32:ccc4c4c4
66:46:0805040709
66:61:c9c3c3c2
67:32:ccc4c4c4
67:38:0406090e0d0c0a060306030803050809090807
67:61:c9c3c3c2
68:32:ccc4c4c4
68:37:030406080b070606060507050803050607070605050403
68:61:c9c3c3c2
69:32:ccc4c4c4
69:37:0304050608060605040508060804030305060604040403
69:61:c9c3c2c1
70:32:ccc4c4c4
70:37:02030405080605040d0908070808080304060604040303
70:61:c6c2c2c1
71:32:c9c4c4c4
71:37:02030405080504050a08
71:49:05080804
71:55:0504040303
71:61:c6c2c2c1
72:32:c9c3c4c4
72:37:020203050704080c0906c5c4c505070605
72:55:0304040303
72:61:c6c2c2c1
73:32:c9c3c3c3
73:37:0202030505040e0a05c6cacdc7c4050405
73:55:0204040303
73:61:c6c2c2c1
74:32:c6c3c3c3
74:37:0202030404030c07c5c9cfcfcbc5c50305
74:55:0202030303
74:61:c5c3c2c1
75:32:c5c3c3c3
75:37:0202030407030c06c4c8cacdc8c4c70305
75:55:0202020303
75:61:c5c3c2c1
76:32:c5c3c3c3
76:39:030b08030a06c4c5c7c5c4c7ca0405
76:55:020403
76:59:03
76:61:c4c4c2c1
77:32:c4c3c3c3
77:39:07080703060705c3c3c4c7cd040505
77:55:02040601
77:61:c4c3c2c1
78:32:c4c2c2c2
78:39:0506060306080805c6c7c804060604
78:55:02040601
78:61:c4c2c2c0
79:32:c4c2c2c2
79:39:0406060504070808040304060806030304050601
79:61:c4c2c1c1
80:32:c4c2c2c2
80:39:040606060504040808080908
80:52:01030406060501
80:61:c4c1c0c1
81:32:c4c2c2c2
81:39:020506060605
81:51:03030406060504
81:61:c3c1
81:64:c1
82:32:c3c0c1c1
82:40:020506060604
82:51:050606060503
82:61:c3c1
82:64:c1
83:32:c3c1c1c1
83:61:c3c1
83:64:c2
""",
}


if __name__ == "__main__":
    build()
