"""EYESPY's robot, two armoured halves on the top layer (sheet 9: the left half 1 3 above 39, the right one 5 7 above
45, 2x2 each; 48 x 56 pictures without their lower right / lower left quarter); polished (2026-10-22, round 36), rebuilt
from machined solids (2026-10-23, round 38: round 36's was one heightfield a half painted from the sprites' pixels, its
arms shapeless blobs). It replaced wave2_e_parts.py's robot.

Where the level puts them (EYESPY t4500, event 7, the top layer; episode 4's enemies 351-356): the left half 351 (1) at
(64, -56), 352 (3) at (88, -56), 353 (39) at (64, -28), link 1; the right half 354 (5) at (240, -56), 355 (7) at (264,
-56), 356 (45) at (264, -28), link 2: far apart, each moving on its own. Armour 255; 353 and 356 (the arms) fire (tur
119, 120); one frame each, no damaged look, nothing launched. The right half is the left one's pixels mirrored a pixel
over, exactly (5 is 3 mirrored, 7 is 1, 45 is 39), so it is the left one's solids mirrored about x = 0.5; no other
sprite is their pixels mirrored, turned or in other ramps; no other enemy shows them; episode 6's EYESPY waves (DELI
RUIN, GLACIER) don't hold them. (The blue lens pods beside them on the sheet, 9 41 and 43, are polish_lens_pod.py's.)

As the sprites and their 4x upscales draw the left half (its picture's columns and rows; grey armour, ramp 0, lit from
the upper left): an arm hanging from a shoulder at the top right. The shoulder's axle (the roll) lies across the top
(columns 19-47 of rows 2-11), two bright bands round its outer end (columns 36-39 and 41-44); under it the shoulder
block (columns 25-46 of rows 11-28), its top lit, its front falling away, a dark pocket in its left part (columns 26-34
of rows 13-27) where the arm hinges; the upper arm a broad beam down to the left (columns 8-28 of rows 8-31) with a lit
band down it (columns 17-27); the elbow a rounded drum (columns 14-22 of rows 29-38); the forearm a fork hooked over
the gun's back end (columns 5-14 of rows 31-39: its legs either side of a dark gap); the gun's barrel down and out to a
blue lens (ramp 9, columns 3-10 of rows 46-50).

Built from machined solids (polish_sheet9_solids): the axle a turned part with two chrome bands and a domed end; the
block an armour plate with a flat top and its front chamfered down, the pocket a hole through it over a dark floor,
a chrome hinge pin across it; the upper arm a bevelled beam with a raised cover plate along the lit band and bolts;
the elbow a turned drum with a chrome cap; the fork a bent tube whose legs end on the gun's breech; the gun a turned
barrel with a chrome muzzle ring; the lens a turned glass dome glowing in its own blue. Materials by part
(palette indices of ramp 0 and the lens's ramp 9): the beam 0x06, the block and the cover plate 0x08, the joints
0x07, chrome 0x0b, the pocket's floor and the cuts 0x02, the barrel 0x05, the lens 0x9c (glowing 0.4). Heights: z 0
to 10.4 (the axle's bands; round 36's 10.9).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera (z 0: the top
layer's plane). Each half's origin is its picture's middle (column 24, row 28): column c's left edge is x = c - 24, row
r's top edge y = 28 - r; the pieces' origins (-12, 14), (12, 14), (-12, -14) on the left (1, 3, 39), (-12, 14),
(12, 14), (12, -14) on the right (5, 7, 45) (models.cfg origin).

models.cfg: the six model and sprite lines stay as they are (eyespy_l_shoulder ... origin; yaw=0).

Replaces round 36's version of this script (its heightfield, polish_sheet9_kit's Plate and Painter); wave2_e_parts.py's
robot is already gone.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each piece's outline as the
camera sees it against its sprite's pixels), --preview <prefix> (each half: top and 3/4 views; --pieces 1: each
piece), --only <name,...>.
"""
import os
import sys

from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_sheet9_solids as ss  # noqa: E402

LEFT, TOP = -24.0, 28.0
MIRROR = 0.5                       # the right half is the left one mirrored about x = MIRROR

# The axle: from, to (column, row), its axis's height; its profile (along it, radius); its chrome bands (from, to).
AXLE = ((21.2, 9.7), (46.9, 5.6), 5.7)
AXLE_PROFILE = [(0.0, 2.0), (0.8, 3.1), (2.4, 3.9), (5.0, 4.2), (14.0, 4.3), (22.6, 4.2), (23.9, 3.8), (24.9, 3.0),
                (25.5, 1.9), (25.75, 0.4)]
AXLE_BANDS = [(15.2, 17.2), (19.9, 21.9)]
BAND_R = 4.65
# The shoulder block: its outline, its top, where its front starts falling and how low it falls; the pocket; its pin.
BLOCK = [(25.8, 11.8), (44.6, 11.0), (45.0, 12.6), (44.6, 20.8), (40.4, 27.8), (31.6, 27.8), (26.4, 22.0),
         (25.6, 19.6)]
BLOCK_TOP, BLOCK_FRONT, BLOCK_LOW = 7.4, 20.0, 4.4   # its top; the row its front starts falling from, to this height
POCKET = [(27.0, 13.6), (33.4, 13.2), (34.0, 21.0), (28.4, 21.6)]
POCKET_FLOOR = 2.0
PIN = ((26.4, 17.4), (34.8, 17.2), 4.2, 1.8)          # from, to (column, row), height, radius
# The upper arm: the beam's outline and top; the cover plate over its lit band; bolts.
BEAM = [(20.6, 8.6), (27.4, 10.8), (26.4, 15.0), (25.6, 22.0), (24.6, 27.4), (21.4, 29.0), (15.0, 29.6), (12.8, 31.0),
        (8.2, 30.4), (7.9, 26.0), (8.6, 22.2), (11.8, 18.8), (15.0, 13.0)]
BEAM_TOP, BEAM_BEVEL = 6.0, 1.1
COVER = [(21.0, 10.6), (26.0, 11.8), (24.9, 16.0), (24.4, 26.4), (22.6, 28.2), (18.4, 28.0), (17.2, 25.4), (18.8, 20.8),
         (19.8, 14.8)]
COVER_T, COVER_BEVEL = 1.0, 0.6
BOLTS = [(22.8, 13.4), (21.6, 20.2), (20.6, 25.8), (11.0, 27.4), (13.8, 20.4)]
# The elbow drum: middle (column, row), radii, its top; the fork (a bent tube: column, row), its radius and height.
ELBOW = ((18.2, 33.9), (4.3, 5.1), 6.3)
FORK = [(12.6, 39.2), (13.2, 35.8), (12.6, 33.0), (10.4, 31.6), (7.8, 32.0), (6.2, 34.0), (5.9, 36.8), (6.8, 39.6)]
FORK_R, FORK_Z = 2.3, 4.0
# The gun: its barrel's back and muzzle (column, row), its axis's height; the trunnion pin through the fork's legs.
GUN = ((10.5, 37.8), (5.7, 48.8), 4.5)
CORNER = 1.2


def P(c, r):
    return (c + LEFT, TOP - r)


def P3(c, r, z):
    x, y = P(c, r)
    return Vector((x, y, z))


def materials():
    p = ss.pal
    return {
        "beam": p("espy_beam", 0x06, 0.3, 0.38), "plate": p("espy_plate", 0x08, 0.3, 0.34),
        "joint": p("espy_joint", 0x07, 0.4, 0.3), "chrome": p("espy_chrome", 0x0b, 0.55, 0.2),
        "dark": p("espy_dark", 0x02, 0.2, 0.6), "gun": p("espy_gun", 0x05, 0.45, 0.3),
        "lens": p("espy_lens", 0x9c, 0.0, 0.05, 0.4),
    }


def outline(points):
    return ss.round_corners([P(c, r) for c, r in points], CORNER)


def axle(m):
    (c0, r0), (c1, r1), z = AXLE
    a, b = P3(c0, r0, z), P3(c1, r1, z)
    out = [ss.lathe_between("espy_axle", AXLE_PROFILE, a, b, m["joint"], around=28, smooth=40.0)]
    for i, (t0, t1) in enumerate(AXLE_BANDS):
        prof = [(t0, 3.9), (t0 + 0.25, BAND_R), (t1 - 0.25, BAND_R), (t1, 3.9)]
        out.append(ss.lathe_between("espy_band%d" % i, prof, a, b, m["chrome"], around=28, smooth=40.0))
    return out


def block_top(x, y):
    yf = TOP - BLOCK_FRONT
    if y >= yf:
        return BLOCK_TOP
    yl = TOP - max(r for _, r in BLOCK)
    return BLOCK_TOP - (BLOCK_TOP - BLOCK_LOW) * min(1.0, (yf - y) / (yf - yl))


def block_normal(x, y):
    if y >= TOP - BLOCK_FRONT:
        return (0.0, 0.0, 1.0)
    slope = (BLOCK_TOP - BLOCK_LOW) / (max(r for _, r in BLOCK) - BLOCK_FRONT)   # dz/dy: it rises up the screen
    return tuple(Vector((0.0, -slope, 1.0)).normalized())


def block(m):
    """The shoulder block: an armour plate standing on the layer, its front chamfered down, the pocket a hole in it
    over a dark floor, the hinge pin across the pocket."""
    shape = outline(BLOCK)
    pocket = outline(POCKET)
    obj = ss.shell_plate("espy_block", shape, [pocket], lambda x, y: block_top(x, y) - 1.0, block_normal, 1.0, 0.9,
                         m["plate"], m["dark"], drop=20.0)
    floor = ss.shell_plate("espy_pocket_floor", ss.inset(pocket, -0.6), [], *ss.flat(POCKET_FLOOR - 1.0), 1.0, 0.4,
                           m["dark"], m["dark"], drop=20.0)
    (c0, r0), (c1, r1), z, rad = PIN
    prof = [(0.0, rad * 0.7), (0.3, rad), (abs(c1 - c0) - 0.3, rad), (abs(c1 - c0), rad * 0.7)]
    pin = ss.lathe_between("espy_pin", prof, P3(c0, r0, z), P3(c1, r1, z), m["chrome"], around=18, smooth=40.0)
    return [obj, floor, pin]


def upper_arm(m):
    beam = ss.shell_plate("espy_beam", outline(BEAM), [], *ss.flat(BEAM_TOP - 1.2), 1.2, BEAM_BEVEL, m["beam"],
                          m["dark"], drop=20.0)
    cover = ss.shell_plate("espy_cover", outline(COVER), [], *ss.flat(BEAM_TOP), COVER_T, COVER_BEVEL, m["plate"],
                           m["beam"])
    out = [beam, cover]
    for i, (c, r) in enumerate(BOLTS):
        x, y = P(c, r)
        on_cover = i < 3
        z = BEAM_TOP + (COVER_T if on_cover else 0.0)
        out.append(ss.dome_on("espy_bolt%d" % i, (x, y, z), (0.0, 0.0, 1.0), 0.65, 0.55, m["chrome"], segments=12,
                              steps=3, sink=0.4))
    return out


def elbow(m):
    (c, r), (rx, ry), top = ELBOW
    x, y = P(c, r)
    prof = [(rx, 0.02), (rx, top - 1.0), (rx - 0.25, top - 0.35), (rx - 0.7, top), (0.001, top)]
    drum = mk.lathe("espy_elbow", prof, (x, y), m["joint"], segments=40, squash=(1.0, ry / rx))
    k.recalc_normals(drum)
    k.smooth(drum, 40)
    cap = ss.turned_on("espy_elbow_cap", (x, y, top), (0.0, 0.0, 1.0),
                       [(1.7, -0.3), (1.7, 0.35), (1.45, 0.6), (0.9, 0.78), (0.001, 0.82)], m["chrome"], segments=20)
    return [drum, cap]


def fork(m):
    pts = ss.chaikin_open([tuple(P3(c, r, FORK_Z)) for c, r in FORK], 2)
    return [ss.tube_along("espy_fork", pts, [FORK_R] * len(pts), m["joint"], around=16, squash=1.0)]


def gun(m):
    (c0, r0), (c1, r1), z = GUN
    a, b = P3(c0, r0, z), P3(c1, r1, z)
    L = (b - a).length
    breech = [(-0.6, 3.0), (-0.3, 4.1), (0.2, 4.4), (2.2, 4.4), (2.6, 3.8), (2.8, 3.4)]
    barrel = [(2.0, 3.9), (2.4, 4.0), (L - 3.4, 3.9), (L - 3.2, 3.6), (L - 1.0, 3.6), (L - 0.8, 3.2)]
    ring = [(L - 3.3, 3.8), (L - 3.1, 4.3), (L - 1.3, 4.3), (L - 1.05, 3.8)]
    lens = [(L - 1.2, 3.3), (L - 0.6, 3.28), (L + 0.2, 2.9), (L + 0.9, 2.2), (L + 1.5, 1.2), (L + 1.75, 0.01)]
    return [ss.lathe_between("espy_breech", breech, a, b, m["joint"], around=26, smooth=40.0),
            ss.lathe_between("espy_barrel", barrel, a, b, m["gun"], around=26, smooth=40.0),
            ss.lathe_between("espy_muzzle", ring, a, b, m["chrome"], around=26, smooth=40.0),
            ss.lathe_between("espy_lens", lens, a, b, m["lens"], around=26, smooth=70.0)]


def left_half(m):
    parts = axle(m) + block(m) + upper_arm(m) + elbow(m) + fork(m) + gun(m)
    return parts


HALVES = {"l": [("eyespy_l_shoulder", 1, (-24.0, 0.0, 0.0, 28.0), (-12.0, 14.0)),
                ("eyespy_l_dome", 3, (0.0, 24.0, 0.0, 28.0), (12.0, 14.0)),
                ("eyespy_l_arm", 39, (-24.0, 0.0, -28.0, 0.0), (-12.0, -14.0))],
          "r": [("eyespy_r_dome", 5, (-24.0, 0.0, 0.0, 28.0), (-12.0, 14.0)),
                ("eyespy_r_shoulder", 7, (0.0, 24.0, 0.0, 28.0), (12.0, 14.0)),
                ("eyespy_r_arm", 45, (0.0, 24.0, -28.0, 0.0), (12.0, -14.0))]}


def build():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    sheet = os.path.join(options["check"], "enemy_9.png") if "check" in options else None
    for side, pieces in HALVES.items():
        if only is not None and not any(name in only for name, *_ in pieces):
            continue
        k.reset()
        m = materials()
        parts = left_half(m)
        if side == "r":
            mirrored = [ss.mirror_copy(o, MIRROR, o.name + "_r") for o in parts]
            ss.remove(parts)
            parts = mirrored
        if "preview" in options:
            ss.whole_preview(options["preview"] + "eyespy_" + side, parts, (52, 60))
        ss.export_pieces(parts, [(n, s, box, o, None) for n, s, box, o in pieces], m["dark"], options, sheet)


if __name__ == "__main__":
    build()
