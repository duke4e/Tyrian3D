"""SOH JIN's red sign "WARNING / MISSILE SHIPS!!" (sheet A: sprites 49 and 51, 2x2 each, side by side: one 48 x 28 picture;
enemies 788 and 789 of episode 2, armour 0, one frame each), polished (2026-10-22, round 36; it replaces wave3_q.py's
sign, strokes inflated from the pixels' outlines).

Where it appears: SOH JIN's events 15 (the sky) at t1, t1200 and t3501: 788 (A 49) at x 114 and 789 (A 51) at x 138, the
same y: the halves side by side, the sign drifting down the screen with the sky. No other enemy shows A 49 or 51; they
are no other sprite's pixels mirrored, turned or in other ramps. The 4x upscales garble the letters (their WARNING reads
WARNIC): built from the original pixels, so that the words stay readable.

As the sprites draw it (the picture's columns and rows): the word WARNING in a blocky pixel font (rows 6-11, columns
2-38), each upright stroke two pixels wide, darker red on its left (0x76) than on its right (0x78); a line under it (row
13, columns 4-34) fading darker to its ends (0x74-0x77); MISSILE (rows 16-20, columns 2-27) with a wedge after it
(columns 28-32 of rows 16-20, its slope lit, a tail along row 20 to column 37 fading to 0x72); SHIPS!! (rows 22-26,
columns 13-36) with a wedge before it (a line along row 22 from column 3, sloping down to column 12 at row 26).

Built as a sign of channel letters (polish_warning.py's family, FLEET's green WARNING sign): the strokes are one
heightfield in the picture's plane on polish_gyges_wall.Plate's grid made finer (STEP 1/3 pixel; its lines on the
sprites' edge, so each half is the cells of its sprite), sheared along the game camera's line of sight (y - z tan 20):
inside the sprite's pixels (their corners rounded off, pixels that touch only at a corner bridged by a bar between their
middles so the S's, the slants and the !! stay whole, the wedges' slopes straight where the pixels step), their faces
TOP_Z high, rounded over ROUND at their edges; walls down to the layer's plane. The faces glow in the sprite's own reds
pixel by pixel (0x74-0x78, emission 0.3-0.56: a lit sign; the wedges bright with darker slopes), their rounded rims and
sides dark red (0x72, 0.18). Heights: z 0 to 1.5 (the old sign 1.5). Deterministic (no random numbers; faces' centres
rounded before they pick their colours).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera. The whole's origin
is the edge between the two sprites at their middle (the pixel edge 24, 14): column c's left edge is x = c - 24, row r's
top edge y = 14 - r; the halves' origins are their sprites' middles (-12, 0) and (12, 0) (models.cfg origin).

models.cfg: the model and sprite lines of missile_sign_left and missile_sign_right stay as they are (origin, yaw=0).

Replaces wave3_q.py (all of it: the sign is all it builds; nothing imports it) and wave3_q_art.py's SIGN (read only by
it, through wave3_q_kit's art).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the outline as the camera sees
it against the sprites' pixels, the whole and each half), --preview <prefix> (each half's top and 3/4 views), --only
<name,...> (halves to export).
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_gyges_wall as gw  # noqa: E402  (Plate, the shear to the camera, the pieces' finish)
from polish_green_shell import edt  # noqa: E402

W, H = 48, 28                     # the whole picture (A 49 beside 51); its origin is its middle, the pixel edge (24, 14)
LEFT, TOP = -24.0, 14.0
STEP = 1.0 / 3.0                  # the strokes' heightfield grid (polish_gyges_wall.Plate's, made finer)
FINE = 8                          # the fields under it: this many cells a pixel
TOP_Z = 1.5                       # the letters' faces over the layer's plane
ROUND = 0.5                       # their edges rounded over this
SMOOTH = 0.22                     # the pixels' corners rounded off (their mask blurred this much before its outline)
WEDGES = [((28, 16), (28, 20.1), (32.2, 20.1)), ((4.9, 21.9), (12.2, 21.9), (12.2, 27.0))]   # the two arrow wedges:
#                                   their right-angled triangles (pixel-edge corners), straight where the pixels step
BRIDGE = 0.5                      # (half its width)
SIDE = 0x72                       # the letters' sides (seen off the screen's middle): dark red
EDGE = 0x76                       # the wedges' slopes (the sprite's darker staircase there)
GLOW = {0x72: 0.18, 0x74: 0.3, 0x75: 0.36, 0x76: 0.42, 0x77: 0.5, 0x78: 0.56}


def px(c):
    return c - 24.0


def py(r):
    return 14.0 - r


def parse_picture(text, first_row=6):
    a = -np.ones((H, W), int)
    for i, line in enumerate(text.split()):
        for c in range(W):
            t = line[2 * c:2 * c + 2]
            if t != "..":
                a[first_row + i, c] = int(t, 16)
    return a


def in_triangle(X, Y, tri):
    (x0, y0), (x1, y1), (x2, y2) = [(px(c), py(r)) for c, r in tri]

    def side(ax, ay, bx, by):
        return (bx - ax) * (Y - ay) - (by - ay) * (X - ax)
    s0, s1, s2 = side(x0, y0, x1, y1), side(x1, y1, x2, y2), side(x2, y2, x0, y0)
    return ((s0 >= 0) & (s1 >= 0) & (s2 >= 0)) | ((s0 <= 0) & (s1 <= 0) & (s2 <= 0))


class Fine:
    """Values on the fine grid (FINE cells a pixel), sampled bilinearly between its cells' middles."""

    def __init__(self, values):
        self.v = values

    def __call__(self, Xa, Ya):
        h, w = self.v.shape
        fc = np.clip((np.asarray(Xa, float) - LEFT) * FINE - 0.5, 0.0, w - 1.0)
        fr = np.clip((TOP - np.asarray(Ya, float)) * FINE - 0.5, 0.0, h - 1.0)
        c0 = np.minimum(np.floor(fc).astype(int), w - 2)
        r0 = np.minimum(np.floor(fr).astype(int), h - 2)
        tc, tr = fc - c0, fr - r0
        v = self.v
        return ((v[r0, c0] * (1 - tc) + v[r0, c0 + 1] * tc) * (1 - tr) +
                (v[r0 + 1, c0] * (1 - tc) + v[r0 + 1, c0 + 1] * tc) * tr)


class Sign:
    """The strokes in the picture's plane: inside the sprite's pixels (their corners rounded, the wedges' slopes
    straight), their faces TOP_Z high, rounded over ROUND at their edges."""

    def __init__(self, a):
        self.a = a
        xs = LEFT + (np.arange(W * FINE) + 0.5) / FINE
        ys = TOP - (np.arange(H * FINE) + 0.5) / FINE
        X, Y = np.meshgrid(xs, ys)
        pixels = np.repeat(np.repeat(a >= 0, FINE, 0), FINE, 1)
        # Pixels that touch only at a corner are bridged by a bar between their middles (the letters' curves and
        # slants stay whole once the corners are rounded).
        on = a >= 0
        for r in range(H - 1):
            for c in range(W - 1):
                for (r0, c0), (r1, c1), (o0, o1) in ((((r, c), (r + 1, c + 1), ((r, c + 1), (r + 1, c)))),
                                                    (((r, c + 1), (r + 1, c), ((r, c), (r + 1, c + 1))))):
                    if on[r0, c0] and on[r1, c1] and not on[o0] and not on[o1]:
                        ax, ay, bx, by = px(c0 + 0.5), py(r0 + 0.5), px(c1 + 0.5), py(r1 + 0.5)
                        t = np.clip(((X - ax) * (bx - ax) + (Y - ay) * (by - ay)) / 2.0, 0.0, 1.0)
                        pixels |= np.hypot(X - (ax + t * (bx - ax)), Y - (ay + t * (by - ay))) < BRIDGE
        mask = pixels.copy()
        for tri in WEDGES:
            cs = [c for c, _ in tri]
            rs = [r for _, r in tri]
            box = (X > px(min(cs))) & (X < px(max(cs))) & (Y < py(min(rs))) & (Y > py(max(rs)))
            mask = np.where(box, in_triangle(X, Y, tri) | (pixels & ~box), mask)
        soft = gw.blur(mask.astype(float), SMOOTH * FINE) > 0.5
        self.mask = Fine(soft.astype(float))
        d = edt(soft, 1.0 / FINE)
        self.height = Fine(np.where(soft, TOP_Z * np.sqrt(1.0 - (1.0 - np.clip(d / ROUND, 0.0, 1.0)) ** 2), 0.0))

    def cells(self, cx, cy):
        return self.mask(cx, cy) > 0.5

    def heights(self, Xa, Ya):
        return self.height(Xa, Ya)

    def index(self, Xa, Ya):
        """The palette index of the pixel under each point (the wedges' straight slopes take their neighbours')."""
        c = np.clip(np.floor(np.asarray(Xa) - LEFT).astype(int), 0, W - 1)
        r = np.clip(np.floor(TOP - np.asarray(Ya)).astype(int), 0, H - 1)
        out = self.a[r, c]
        for dc, dr in ((-1, 0), (0, 1), (1, 0), (0, -1), (-1, 1), (1, 1)):
            miss = out < 0
            if not miss.any():
                break
            out = np.where(miss, self.a[np.clip(r + dr, 0, H - 1), np.clip(c + dc, 0, W - 1)], out)
        out = np.where(out < 0, 0x78, out)
        # the wedges: bright, their slopes darker, the stepped shades the pixels give them left out
        for tri in WEDGES:
            (c0, r0), (c1, r1), (c2, r2) = tri
            inside = in_triangle(np.asarray(Xa), np.asarray(Ya), tri)
            ax, ay, bx, by = px(c0), py(r0), px(c2), py(r2)
            dist = np.abs((bx - ax) * (np.asarray(Ya) - ay) - (by - ay) * (np.asarray(Xa) - ax)) / np.hypot(bx - ax,
                                                                                                         by - ay)
            out = np.where(inside, np.where(dist < 0.8, EDGE, 0x78), out)
        return out


def mat_of(index):
    glow = GLOW.get(index, 0.0)
    extra = dict(emission=k.level_palette()[index], emission_strength=glow) if glow > 0 else {}
    return k.material("sign_red_%x" % index, palette=index, metallic=0.1, roughness=0.3, **extra)


def assign(obj, keys):
    order = sorted(set(keys))
    slot = {key: i for i, key in enumerate(order)}
    mesh = obj.data
    mesh.materials.clear()
    for key in order:
        mesh.materials.append(mat_of(key))
    mesh.polygons.foreach_set("material_index", [slot[key] for key in keys])
    mesh.update()


PIECES = [("missile_sign_left", 49, (-24.0, 0.0, -14.0, 14.0)), ("missile_sign_right", 51, (0.0, 24.0, -14.0, 14.0))]


def check(sign, sheet):
    covered = gw.own_coverage(lambda Xa, Ya: sign.cells(Xa, Ya), W, H, LEFT, TOP)
    mask = [[False] * W for _ in range(H)]
    for _, sprite, box in PIECES:
        c0 = 0 if box[0] < 0 else 24
        for r, line in enumerate(k.sprite_mask(sheet, sprite)):
            for c, v in enumerate(line):
                if v:
                    mask[r][c0 + c] = True
    mk.compare("the missile sign (its 48 x 28 picture)", covered, mask)
    for name, sprite, box in PIECES:
        c0 = 0 if box[0] < 0 else 24
        sub_c = [row[c0:c0 + 24] for row in covered]
        sub_m = [row[c0:c0 + 24] for row in mask]
        both = sum(p and q for rp, rq in zip(sub_c, sub_m) for p, q in zip(rp, rq))
        either = sum(p or q for rp, rq in zip(sub_c, sub_m) for p, q in zip(rp, rq))
        print("silhouette overlap %s (a %d): %.3f" % (name, sprite, both / max(1, either)))


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    sign = Sign(parse_picture(PICTURE))
    if "check" in options and only is None:
        sheets = options["check"]
        check(sign, os.path.join(sheets, "enemy_A.png") if os.path.isdir(sheets) else sheets)
    saved = gw.STEP
    gw.STEP = STEP               # Plate reads its grid's spacing from its module (while it is built and meshed)
    try:
        plate = gw.Plate((-24.0, 24.0, -14.0, 14.0), sign.heights, cells=sign.cells, bottom=False)
        for name, sprite, box in PIECES:
            if only is not None and name not in only:
                continue
            k.reset()
            obj, kinds, _ = plate.mesh(name, gw.piece_owner(box))
            centres, _ = gw.face_data(obj)
            centres = np.round(centres, 4)
            index = sign.index(centres[:, 0], centres[:, 1])
            keys = [int(index[i]) if kinds[i] == 0 and centres[i, 2] > 0.35 * TOP_Z else SIDE
                    for i in range(len(kinds))]
            assign(obj, keys)
            gw.finish_piece(name, [obj], box, out, options)
    finally:
        gw.STEP = saved


# --- The sprites' pixels ----------------------------------------------------------------------------------------------
# Each pixel its palette index as two hex digits ('..' none), rows top to bottom (the picture's empty rows left out).

PICTURE = """
....7678......78....7678....767878....7678..........76..7678..........7678......................
....7678......78..7678..78..7678..78..767878......7678..767878......7678..78....................
....7678......78..76787878..7678..78..7678..78....7678..7678..78....7678........................
....7678..78..78..7678..78..767878....7678....78..7678..7678....78..7678....78..................
....7678..78..78..7678..78..7678..78..7678....78..7678..7678....78..7678....78..................
......76787878....7678..78..7678..78..7678....78..7678..7678....78....767878....................
................................................................................................
........747677787878787878787878787878787878787878787878787878787878777674......................
................................................................................................
................................................................................................
......787878....78....7878....7878..78..78......787878..74......................................
....78..78..78..78..78......78......78..78......78......7874....................................
....78..78..78..78....78......78....78..78......7878....787874..................................
....78......78..78......78......78..78..78......78......78787874................................
....78......78..78..7878....7878....78..787878..787878..7878787878787878767472..................
................................................................................................
......74767778787878787878....7878..78..78..78..7878......7878..78..78..........................
..................75787878..78......78..78..78..78..78..78......78..78..........................
....................757878....78....787878..78..7878......78....78..78..........................
......................7578......78..78..78..78..78..........78..................................
........................75..7878....78..78..78..78......7878....78..78..........................
"""


if __name__ == "__main__":
    build()
