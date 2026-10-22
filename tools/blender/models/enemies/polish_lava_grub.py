"""The lava grub of STARGATE and ASTEROIDS (sheet E; eight 2x2 sprites each, as the levels put them together: one
96 x 56 picture), the one with its head to the left (E 77 79 81 83 above 115 117 119 121: lava_grub_l_t1 .. _t4 above
_b1 .. _b4) and its mirror image with its head to the right (E 85 87 89 91 above 123 125 127 129: lava_grub_r_*),
polished (2026-10-22, round 30; it replaces wave3_aa_grub.py, a relief inflated from the sprites' outline and painted
pixel by pixel). Each is built whole and cut into its eight pieces (models.cfg origin).

How the levels place and move them (tools/content/tyrevents.py): STARGATE (episode 3) sends the right grub (enemies
670-677, event 10: the second ground list) at t 420, 520, 1520 and 1620 with x -24, 0, 24, 48 (links 2 and 4) and the
left grub (662-669, event 6: the ground) at t 470, 570, 1570 and 1670 with x 200 .. 272 (links 3 and 5); ASTEROIDS
(episode 5) the right one (1130-1137) at t 1720 (link 12) and the left one (1122-1129) at t 1870 (link 13). Each time
the top row at (x + 24 i, y - 28) above the bottom row at (x + 24 i, y): the sheet's own layout. 10 to 90 ticks
later event 20 sets the link's excc to +-20: every piece speeds up sideways together (one step a 20 ticks), the right
grub to the right and the left one to the left, head first, out of the screen; one rigid body, no piece moves on its
own. All 32 enemies have armour 30, one frame (ani 1), no damaged look (dgr 0), no guns; each grub is one link, so
shooting any piece down destroys all eight together (tyrian2.c): no piece is ever shot away alone (when the grub
scrolls off the screen's bottom the lower row goes first). No episode 6 level takes these waves (its invaders game uses
other enemies) and no other enemy, launched ones included, shows these sprites. The right grub is the left one's pixels
mirrored, a pixel right of the exact mirror image (its column c is the left one's 96 - c: 2725 of their 2870 pixels
alike; the rest a few shades of its second and fourth seams a little cooler, its eyes' shading, eight outline pixels):
it is the left model mirrored about x 0.5.

As the sprites and their 4x upscales draw it (columns and rows of the left grub's picture): a big segmented grub drawn
seen from in front and above, its head to the left, its back along the top. The head (columns 8-30, rows 10-37): a
dark red dome with two white-hot oval eyes stacked at its upper right (23, 14 and 23, 21), a seam of lava round its
left side, another from the lower eye round the corner of a wide dark mouth (rows 24-30) along the jaw, a third along
the chin; a column of four pale knobs (ramp 4) at the neck (columns 29-36). Five shields over the back (S1-S5 from
column 37 to 81, highest at the front: S1's lobe reaches row 3) and the tail's (81-93): each shield's front seam a line
of lava (bright from its lobe's rim down to row 22-25) that bends back along the shield's lower edge (its waist) and,
on S3-S5 and the tail, rises in a bar at its rear (the tail's white-hot, columns 82-84, rows 17-28); the rear edges
dark; the lobes' rims lit; on each shield a pale horn lying back along the spine (rows 12-21). Below the waists the
flanks: plates in dark reds sweeping down and forward to the belly, black seams between them. Under the head a long
sickle claw on the ground (from its tip at 9, 39 round to its joint at 27, 49), a shorter one under the middle (45-59,
rows 46-49), pale knobs at their joints and lava glowing in them (a hot claw tip at 34, 48); at the tail a pale bulb
(85-92, rows 18-26) and a pale hook curling down from it round the tail's end to 83, 34.

Built for the game's camera (VIEW_TILT: 20 degrees off straight down, from the bottom of the screen): everything is
modelled in the picture's plane (x, y as the sprite draws them, z up) and then sheared along the camera's line of
sight (y - z tan 20, the normals with it: shear_to_camera), so that the camera sees every point where the sprite draws
it, however high it stands, while from straight above the outline stays the sprite's (its rim is on the ground).
- The body (head, neck, shields, flanks and tail in one closed solid, polish_torm_beetle.Solid's shape over a mesh of
  its own: MeshSolid). Its height: the plates' back highest along SPINE (rows 12-23, a little under the sprite's top
  edge: the sprite's top rows are the far side of the back, seen beyond it) and falling steeply to the outline above
  it and in a long curve to the belly below, rounded off at the neck; the head a dome highest between the eyes, the
  mouth sunk into it, the jaw a lip under it, shallow sockets for the eyes; head and body met in a smooth crease
  (NECK_BLEND); grooves along every seam (the shields' front seams, waists and rear bars, the flanks' seams, the head's
  seams), the shields and the flanks' plates bulging between them (crowns), a raised rear edge on each shield before
  the next one's seam. Its mesh is a constrained Delaunay triangulation (body_mesh) of its outline (the sprites'
  pixels but the claws and their joints, blurred: BODY_FIELD), of lines along every glowing seam at the distances
  where its bands of heat change (STRIP_OFFSETS), along the dark seams and the neck's crease, of rings round the
  glowing spots, and of a coarse grid between (GRID): fine across the seams, where the heat changes fast, coarse on the
  plates.
- Painted in bands of ramp 7 (cut along smooth contours: polish_coral_manta.split_contour) by a heat: the plates' tone
  (the sprite's shades blurred broadly, lighter on the bulges and lips, darker in the grooves, dark in the flanks'
  seams and in the gap behind each shield's rear edge) and the lava: each seam's line glowing as hot as the sprite's
  hottest pixels along it (sprite_peaks), white-hot at its core and out through yellow, orange and red to the plates
  round it (the shields' front seams on the shield behind them only), the eyes' halos and the tail's white-hot spot.
  Every red glows a little in its own colour (0.12 for the darkest to 0.62 for white: the game's slanted camera would
  otherwise show the dark reds brown), with a sheen in its own red (metallic 0.45).
- The parts, in the picture's plane on the body: the eyes (lenses white-hot to their yellow rims, facing straight up so
  that the camera sees them round), the four collar knobs, the five horns (fat curved teeth out of the shields' backs,
  lying back over the next seam), the tail's bulb and hook (ramp 4, by the light they get: 0x44-0x4c, glowing a
  little), the two sickle claws (lens-shaped tubes on the ground, lit along their upper edges as hot as the sprite
  draws them), dark pads under their joints with their pale knobs and the front one's glowing tip.
Cut into the pieces in the picture's plane along the sprites' edges (x -24, 0, 24; y 0), before the shear: each piece
holds what its sprite draws, and its cut faces lie along the camera's line of sight, so that they stay unseen when a
neighbour is gone (the top row's lower faces would face the camera only higher up the screen than the middle, and the
top row is only ever seen alone at the screen's bottom, its lower row scrolled off). The cuts are
polish_coral_manta.cut's (caps of the inside: lava, 0x75, glowing), each piece moved so that its sprite's middle is its
origin, every mesh triangulated (polish_k_pod.triangulate: the same output with and without --check) and joined.
Deterministic: no random numbers, no booleans.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground (z = 0). The whole's
origin is the picture's middle (column 48, row 28): column c is x = c + 0.5 - 48, row r is y = 27.5 - r. The pieces'
origins (their sprites' middles): t1 .. t4 (-36, 14), (-12, 14), (12, 14), (36, 14); b1 .. b4 the same at y -14.

models.cfg: the 16 model lines (lava_grub_l_t1 .. lava_grub_r_b4, enemies/<name>.glb origin) stay; the 16 sprite lines
(sprite e 77 lava_grub_l_t1 yaw=0 ... sprite e 129 lava_grub_r_b4 yaw=0) get height=-4, which lays the grub on the
ground (drawn at its origin a ground piece otherwise stands 4 pixels over it); no frame lines (one frame each).

Replaces wave3_aa_grub.py (all of it: delete it; nothing imports it, wave3_aa.py's and wave3_aa_rocks.py's docstrings
and models.cfg's batch AA comment only name it) and wave3_aa_art.py's GRUB and GRUB_B (its last two sections; only
wave3_aa_grub.py reads them). wave3_aa_kit.py stays as it is (wave3_aa.py, wave3_aa_rocks.py, wave3_ad_kit.py,
wave3_ae_kit.py, wave3_af_kit.py, wave3_ag_kit.py, wave3_ah_kit.py and wave3_ai_gryphon.py import it; the grub only
added "grub_body" to its PROTECT list at run time).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each whole's silhouette as
the camera sees it and from straight above, and each piece's, against enemy_E.png), --preview <prefix> (each whole's
top and 3/4 views; --pieces 1 also each piece's), --only <name,...> (pieces to export), --whole <prefix> (the uncut
wholes as <prefix>l.glb and <prefix>r.glb, for looking at).
"""
import math
import os
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_coral_manta import cut, split_contour  # noqa: E402
from polish_torm_beetle import Solid, curve, densify, smax, sstep  # noqa: E402
from polish_orb_red import band_split  # noqa: E402

VIEW_TILT = 20.0                  # the game's camera: this far off straight down, from the bottom of the screen
TAN_T = math.tan(math.radians(VIEW_TILT))
GRID = 1.0                        # the body's coarse grid (pixels), between the lines along its seams

# --- The sprites' pixels ---------------------------------------------------------------------------------------------
# The left grub as the levels put its eight sprites together (E 77 79 81 83 above 115 117 119 121: the 96 x 56 picture,
# its rows 3-51; the rest is empty), one character a pixel: 0-9 a-f ramp 7's shades (0x70-0x7f), G-V ramp 4's
# (0x40-0x4f: the knobs, horns, bulb and hook, and the darkest outline 0x40), w x the dark browns 0xa1 0xa2 round the
# knobs, z 0xaf (in the upper eye); '.' none.
FIRST_ROW = 3
PIXELS = [
    "..........................................0GG...................................................",
    ".......................................0025750..................................................",
    ".....................................0G2689e900.....0GG0........................................",
    "....................................G46663666000.0025750........................................",
    "....................................0a8442238000G2689ea0........................................",
    ".............................00G....0d335036900356535ac0...000G00...............................",
    "............................GxM1G..G0c3250436004543335a000G125960...............................",
    "....................GGGGGG.GJMOM0GwwG9314021200422222360GG2433350...............................",
    "................GGG001243101GKLxwKLKG4112001100311000110132321250...............................",
    "..............00111005afc9531wxKMPSMG210GGGwMPSV3000002GG30GGG33000000000.......................",
    ".............00320GG7ffffe8310IMOQPL000GwJLMOPPRKG01LOSSVKGGG0100G1358860.......................",
    "............025300G5bfffzf9530wKKLK20000GGwKLMMNx0GwMMORTMG0Gww0G01464470000G00.................",
    "...........007500047cfffff8420Gxx21G0320G00120JL1021JKMMPKGGxMOPRR13123600G055G0GGGGG...........",
    "..........G373000259adeca9622G0GHLKJG63130111G063240336GKxGGxOOOORJ0G0120G68750264232G..........",
    ".........03a500G543322120000000HKQRMJ84140222GGa32403360w301wxLLMNwGGxLM10324300678782G0........",
    ".........099002530GGGG11G0100GxKOSPMKb6240423GGd32304360G5231xJ4Gw01IPUTO11GK203679cfKww0.......",
    "........02a213420G15adffdb9411KMNOMKxc5250434GGc422515600525035800G1GxORK0GxMM0368bffKJJKGG.....",
    "........0891320037acffffffc71GwKLKxx0d5250534G0d643362700634414a0021135O001MRTH27acefJKMOOK0....",
    "........0b2320039978dffffda7000GwJ00Gf5240255G0ba543473GG6435629005113681003OP0G78578wxMRRMKG...",
    "........0a300G6966668effd8730Gwwxx000f7234234G076a85589GG57557860051237910G25LxG4369awKRUURL00..",
    "........04100772332347998740wLPTQKG0Gfc64353300534899a90035998cc00643379122479303689c0KRUUSM10..",
    "........02008821100001122210KMPSOJwG0cda534570042345afaG021479cc0076447b22246a204789dGGJMOMKwG..",
    "........0G37511100GGGGGG0GGGxLLLJwGG189c955890031133597GG21135ba00368acd12244a1G577ac000GxJJxG..",
    "........G1441110G0000000000GwxwwwG0G1569b99a90G31123365G020114a7002237ad12345b10566ab0000GwM2G..",
    "........04622110G00000000000GG0G0G0G042486afa0021111264G020114a40G222248G2457c10466c800000wPx0..",
    "........G4a76110G000000000G001222G00031G245970G2111126300201149300212247G359ab1G255910000GPPG...",
    "........02998421GG0G000G1110135541G0031013365G02111135201201157201102247G111470014750000GOSL0...",
    "........0059c852110G012333225743300G121111264G1211114510110116700100224500012400146G000wLUR0....",
    ".........045cb8612456764547a96221G00121111263021111254001001275G010G22420011240027200GxKVR1.....",
    ".........00278976678742428a521011GG01211113521211113520010013620010G234000112400461GwJMTQ0......",
    "..........00135767840155a831000100G01211114512111115400G1002430001002430001124GG51JKKNPJ41......",
    "..........G1400G01001589610G0G01G0G0211112541211113400001003300010G114000G1131G04xxxxx0070......",
    "..........0400000G025993G00000GGG0G12111135221111153G0G1101320GG1G0141000G113G0G2GGG0G2640......",
    ".........G30G135688785000G0000GGG002111115421111143G00G1003200001G13200000031G00111123200.......",
    "........000000000000000..G0000GGG01211113401111143G0001012200001002100000020000000000000........",
    ".........................GG000GGG121111153G111132000G10120000001G21G0000120G0G0G................",
    ".........00...............GG0GGG021111143G111221G00011110G000000G00000G01000G1G.................",
    ".........03G...............GGGG021111143G11221000001110000xGGGG00G00000GG00G20G.................",
    "..........05G..............GGG0211111320222100000GGG0G000Jw0GG000000000000020G..................",
    "...........G60..............GG2111122100G0G000001......0JxGwLxGG130000000231G...................",
    "...........G350..............11112210G001321G0010......G0GwKMJxw351130G231G0....................",
    "............G240.............0222101200042300G20.........GxJLKwG03067232G0......................",
    ".............01410...............010111xx1G0G31.........G2GxJwwGG0G32100........................",
    "..............013200.............G6GG0xOMw022G........0G874xwwGGGG0000..........................",
    "...............0134300000000GGGG008wGGJMMJ120...0GGG1148ba2100..................................",
    "................G0245788aa0xJJJwG3bKJJKKK1G..G124667778862GG....................................",
    "..................G0234459GMQOLJx5a5wwGG00......GG000G00G0......................................",
    "....................GG02360JKJxx1340G00.........................................................",
    ".......................0000G0GGGGGG0............................................................",
]
W, H = 96, 56
R7 = "0123456789abcdef"


def grid_of(rows):
    """The picture as arrays: ramp 7's shade (nan where another ramp or none; 0xaf counts as white-hot) and the mask."""
    s7 = np.full((H, W), np.nan)
    mask = np.zeros((H, W), bool)
    for j, row in enumerate(rows):
        r = FIRST_ROW + j
        for c, ch in enumerate(row):
            if ch == ".":
                continue
            mask[r, c] = True
            if ch in R7:
                s7[r, c] = R7.index(ch)
            elif ch == "z":
                s7[r, c] = 15.0
    return s7, mask


S7, MASK = grid_of(PIXELS)


def gauss(m, sigma):
    """A Gaussian blur of a 2d array (sigma pixels)."""
    if sigma <= 0:
        return m
    rad = int(math.ceil(3 * sigma))
    t = np.arange(-rad, rad + 1)
    ker = np.exp(-t * t / (2 * sigma * sigma))
    ker /= ker.sum()
    m = np.apply_along_axis(lambda v: np.convolve(v, ker, mode="same"), 0, m)
    return np.apply_along_axis(lambda v: np.convolve(v, ker, mode="same"), 1, m)


def X(c):
    """A picture column (pixel edges: column c's middle is c + 0.5) as x."""
    return c - 48.0


def Y(r):
    """A picture row (pixel edges) as y."""
    return 28.0 - r


class Grid:
    """A field over the picture's pixels, sampled bilinearly at (x, y) (pixel middles at their values)."""

    def __init__(self, m):
        self.m = np.asarray(m, float)

    def __call__(self, x, y):
        x = np.atleast_1d(np.asarray(x, float))
        y = np.atleast_1d(np.asarray(y, float))
        fc = x + 48.0 - 0.5
        fr = 28.0 - y - 0.5
        h, w = self.m.shape
        c0 = np.clip(np.floor(fc).astype(int), 0, w - 2)
        r0 = np.clip(np.floor(fr).astype(int), 0, h - 2)
        tc = np.clip(fc - c0, 0.0, 1.0)
        tr = np.clip(fr - r0, 0.0, 1.0)
        m = self.m
        return (m[r0, c0] * (1 - tc) * (1 - tr) + m[r0, c0 + 1] * tc * (1 - tr) + m[r0 + 1, c0] * (1 - tc) * tr +
                m[r0 + 1, c0 + 1] * tc * tr)


def normalized_blur(values, weight, sigma):
    """The values blurred where weight is 1 (a weighted Gaussian: holes filled from round them)."""
    v = np.where(weight, np.nan_to_num(values), 0.0)
    wgt = weight.astype(float)
    a, b = gauss(v, sigma), gauss(wgt, sigma)
    return np.where(b > 1e-6, a / np.maximum(b, 1e-6), 0.0)


# --- Regions ---------------------------------------------------------------------------------------------------------

def body_mask():
    """The body's pixels (head, neck, shields, flanks, tail): all but the claws (under the head, rows 38 on, and under
    the middle, rows 46 on) and their joints (rows 46 on under the front, 42 on under the middle)."""
    rr, cc = np.mgrid[0:H, 0:W]
    claw_f = MASK & (((rr >= 38) & (cc <= 25)) | ((rr >= 47) & (cc <= 26)))
    foot_f = MASK & (rr >= 46) & (cc >= 26) & (cc <= 44)
    claw_m = MASK & (rr >= 46) & (cc >= 45) & (cc <= 62)
    foot_m = MASK & (rr >= 42) & (cc >= 54) & (cc <= 64)
    return MASK & ~claw_f & ~foot_f & ~claw_m & ~foot_m


BODY_MASK = body_mask()


# --- Curves ----------------------------------------------------------------------------------------------------------

def catmull(ctrl, step=0.2):
    """Catmull-Rom through control points (picture column, row), points about step pixels apart."""
    pts = [np.array(p, float) for p in ctrl]
    out = []
    for i in range(len(pts) - 1):
        p0, p1, p2 = pts[max(i - 1, 0)], pts[i], pts[i + 1]
        p3 = pts[min(i + 2, len(pts) - 1)]
        n = max(1, int(math.ceil(np.linalg.norm(p2 - p1) / step)))
        for j in range(n):
            t = j / n
            out.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t +
                              (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(pts[-1])
    return np.array(out)


class Path:
    """A smooth line through picture points: distances to it and where along it (pixels) the nearest point lies."""

    def __init__(self, ctrl):
        self.p = catmull(ctrl)
        self.a, self.b = self.p[:-1], self.p[1:]
        self.d = self.b - self.a
        self.l2 = np.maximum((self.d ** 2).sum(axis=1), 1e-12)
        self.cum = np.concatenate([[0.0], np.cumsum(np.sqrt(self.l2))])

    def query(self, c, r, reach=4.0):
        """Distances (reach and more for points farther than reach from the path's box) and positions along it."""
        c = np.atleast_1d(np.asarray(c, float))
        r = np.atleast_1d(np.asarray(r, float))
        dist = np.full(len(c), reach + 1.0)
        along = np.zeros(len(c))
        lo, hi = self.p.min(axis=0) - reach, self.p.max(axis=0) + reach
        near = np.nonzero((c >= lo[0]) & (c <= hi[0]) & (r >= lo[1]) & (r <= hi[1]))[0]
        for s in range(0, len(near), 4096):
            idx = near[s:s + 4096]
            pc, pr = c[idx, None], r[idx, None]
            t = np.clip(((pc - self.a[:, 0]) * self.d[:, 0] + (pr - self.a[:, 1]) * self.d[:, 1]) / self.l2, 0.0, 1.0)
            dc = pc - (self.a[:, 0] + t * self.d[:, 0])
            dr = pr - (self.a[:, 1] + t * self.d[:, 1])
            d2 = dc * dc + dr * dr
            i = np.argmin(d2, axis=1)
            rows = np.arange(len(i))
            dist[idx] = np.sqrt(d2[rows, i])
            along[idx] = self.cum[i] + t[rows, i] * np.sqrt(self.l2[i])
        return dist, along


def sprite_peaks(path, radius=1.05, sigma=1.3, spread=0.6):
    """The sprite's hottest shade of ramp 7 near each point of a path (pixel middles within radius), the hottest within
    spread pixels along it taken, smoothed along it: how hot a glowing line is where the sprite draws it (the
    sprite's lines step from pixel to pixel; the line glows evenly along them)."""
    hot = np.where(np.isnan(S7), -1.0, S7)
    out = []
    for c, r in path.p:
        best = -1.0
        for rr in range(int(r - radius - 1), int(r + radius + 1) + 1):
            for cc in range(int(c - radius - 1), int(c + radius + 1) + 1):
                if 0 <= rr < H and 0 <= cc < W and (cc + 0.5 - c) ** 2 + (rr + 0.5 - r) ** 2 <= radius * radius:
                    best = max(best, hot[rr, cc])
        out.append(best)
    out = np.array(out)
    step = np.diff(path.cum).mean() if len(path.cum) > 1 else 1.0
    n = int(round(spread / max(step, 1e-6)))
    out = np.array([out[max(0, i - n):i + n + 1].max() for i in range(len(out))])
    return gauss1(out, sigma / max(step, 1e-6))


def gauss1(v, sigma):
    """A Gaussian blur along a 1d array (sigma samples), its ends held."""
    if sigma <= 0:
        return v
    rad = int(math.ceil(3 * sigma))
    t = np.arange(-rad, rad + 1)
    ker = np.exp(-t * t / (2 * sigma * sigma))
    ker /= ker.sum()
    padded = np.concatenate([np.full(rad, v[0]), v, np.full(rad, v[-1])])
    return np.convolve(padded, ker, mode="valid")


# --- The body's shape (in the picture's plane: x, y as the sprite draws them, z up) -----------------------------------
# The plates' back: its top and bottom envelopes (picture column, row), the spine where it is highest and the height
# there; the body rounds off at the neck (NECK: from this column it is whole, NECK_R the rounding's length).
def envelopes():
    """The plates' top and bottom edges per column (the body's outline, smoothed along the columns): (column, row)."""
    top, bottom = [], []
    for c in range(8, 94):
        rows = np.nonzero(BODY_MASK[:, c])[0]
        top.append(rows[0])
        bottom.append(rows[-1] + 1.0)
    top, bottom = gauss1(np.array(top, float), 0.8), gauss1(np.array(bottom, float), 0.8)
    cols = [c + 0.5 for c in range(8, 94)]
    return list(zip(cols, top)), list(zip(cols, bottom))


TOP_ENV, BOT_ENV = envelopes()
SPINE = [(30, 12.0), (36, 12.0), (44, 13.0), (54, 14.6), (63, 16.6), (70, 18.6), (77, 20.6), (84, 22.0),
         (90, 23.0), (93.5, 23.5)]
SPINE_Z = [(30, 10.6), (36, 11.6), (44, 12.0), (54, 11.5), (63, 10.6), (70, 9.6), (77, 8.6), (84, 7.4),
           (90, 6.0), (93.5, 4.5)]
NECK, NECK_R = 37.0, 8.5
NECK_BLEND = 2.6                  # how broadly the head's dome and the body's meet in the crease at the neck
# The crease (picture column, row): the mesh is fine along it.
NECK_LINE = [(30.6, 9.5), (31.4, 14.0), (31.6, 20.0), (31.2, 26.0), (30.6, 32.0), (30.0, 38.0), (29.6, 43.0)]

# The shields over each segment's back: their front seams (picture row, column: from the back down to the waist),
# their waists (column, row: from the front seam back to the lower seam); the seams of the segments' flanks
# below (row, column: from the waist down and forward to the belly). Grooves run along all of them; lava glows in
# the shields' seams and waists as hot as the sprite draws it there.
SHIELD_FRONT = [
    [(5.6, 37.6), (10.5, 37.5), (16.5, 37.6), (20.5, 37.6), (22.5, 37.8)],
    [(6.8, 47.4), (12.0, 47.5), (17.5, 47.5), (20.8, 47.6)],
    [(8.6, 57.4), (14.0, 57.5), (19.0, 57.5), (22.0, 57.6)],
    [(11.6, 66.3), (16.0, 66.4), (20.5, 66.5), (24.4, 66.6)],
    [(14.0, 73.6), (18.0, 73.7), (22.0, 73.9), (25.6, 74.2)],
    [(15.4, 80.8), (19.0, 80.9), (23.0, 81.0), (26.5, 81.2)],
]
WAIST = [
    [(37.8, 22.5), (38.4, 23.9), (39.4, 24.9), (40.6, 25.8), (42.0, 26.6), (43.5, 27.2), (44.6, 27.4)],
    [(47.6, 20.8), (48.5, 21.7), (49.7, 22.5), (51.3, 23.4), (52.8, 24.2), (54.0, 25.2), (54.8, 26.4)],
    [(57.6, 22.0), (58.6, 23.0), (59.8, 23.6), (61.2, 23.9), (62.4, 24.3), (63.2, 25.4), (63.8, 26.8)],
    [(66.6, 24.4), (67.6, 25.3), (68.8, 25.6), (70.0, 25.8), (71.0, 26.5), (71.8, 27.8)],
    [(74.2, 25.6), (75.0, 27.4), (76.2, 28.3), (77.4, 28.6), (78.4, 28.9), (79.0, 29.6)],
    [(81.2, 26.5), (81.8, 28.0), (82.8, 29.0), (83.6, 30.0)],
]
# The bars of lava rising at the rear of the waists of the middle shields (picture column, row from the top down).
REAR_BARS = [
    [(63.3, 19.2), (63.2, 21.4), (63.0, 23.6), (62.9, 25.2)],
    [(71.3, 20.8), (71.3, 23.0), (71.2, 25.0), (71.1, 26.6)],
    [(77.6, 22.6), (77.6, 24.8), (77.6, 26.8), (78.2, 28.4)],
    [(83.9, 17.2), (84.0, 19.2), (84.1, 21.6), (84.0, 24.0), (83.8, 26.4), (83.4, 28.4)],
]
# The lobes' rims along the top of the first three shields.
RIMS = [
    [(38.2, 9.5), (38.4, 7.2), (39.4, 5.7), (41.0, 5.0), (42.8, 4.8), (44.4, 5.3), (45.2, 6.4)],
    [(48.4, 8.0), (49.4, 7.4), (50.8, 7.1), (52.4, 7.2), (53.6, 7.9), (54.4, 9.0), (54.6, 10.6)],
    [(59.4, 10.4), (60.6, 9.6), (62.2, 9.5), (63.6, 10.1), (64.6, 11.0)],
]
FLANK_SEAMS = [
    [(27.4, 44.6), (31.0, 42.8), (35.0, 41.2), (39.0, 39.2), (42.2, 37.2), (45.0, 35.6)],
    [(26.4, 54.8), (30.5, 52.6), (34.0, 50.6), (37.0, 48.6), (40.0, 47.0), (43.0, 45.6)],
    [(26.8, 63.8), (31.0, 61.2), (33.4, 59.6), (36.2, 57.6), (39.0, 56.0), (42.0, 54.6)],
    [(27.8, 71.8), (32.0, 69.6), (34.4, 67.6), (37.2, 65.6), (40.0, 63.6)],
    [(29.6, 79.0), (33.8, 76.6), (36.8, 74.6), (39.0, 73.0)],
    [(30.0, 83.6), (33.0, 82.0), (36.0, 80.2)],
]
# The head's glowing seams: round its left side under the upper eye, from the lower eye round the mouth's corner
# along the jaw, and along the chin up to the mouth's right end (picture column, row).
HEAD_SEAMS = [
    [(14.5, 14.6), (13.6, 15.5), (12.3, 16.5), (11.0, 17.6), (10.3, 18.6), (9.9, 19.6), (9.7, 20.6), (9.6, 21.6),
     (9.7, 22.6), (10.0, 23.6)],
    [(20.5, 21.6), (17.0, 21.9), (15.0, 22.6), (13.6, 23.6), (12.3, 24.8), (11.0, 26.2), (10.4, 27.6), (10.8, 28.9),
     (11.8, 30.0), (13.0, 31.0), (14.6, 32.0), (17.0, 32.5), (19.8, 32.5)],
    [(14.0, 36.5), (17.0, 36.6), (20.0, 36.2), (22.0, 35.2), (23.6, 34.2), (25.6, 33.0), (27.4, 31.8), (28.6, 30.8)],
]


def colrow(rc):
    """(row, column) points as (column, row)."""
    return [(c, r) for r, c in rc]


FRONT_PATHS = [Path(colrow(s)) for s in SHIELD_FRONT]
WAIST_PATHS = [Path(w) for w in WAIST]
BAR_PATHS = [Path(b) for b in REAR_BARS]
RIM_PATHS = [Path(r) for r in RIMS]
FLANK_PATHS = [Path(colrow(s)) for s in FLANK_SEAMS]
HEAD_PATHS = [Path(h) for h in HEAD_SEAMS]
GLOW_PATHS = FRONT_PATHS + WAIST_PATHS + BAR_PATHS + RIM_PATHS + HEAD_PATHS
GLOW_PEAKS = [sprite_peaks(p, sigma=2.4 if p in HEAD_PATHS else 1.3) for p in GLOW_PATHS]
# How wide each seam glows (a share of GLOW_EDGE): the head's broad bands of fire, the shields' seams.
GLOW_WIDTH = [1.0] * len(FRONT_PATHS + WAIST_PATHS + BAR_PATHS) + [1.1] * len(RIM_PATHS) + [1.4] * len(HEAD_PATHS)

# The grooves: (paths, depth, half-width).
GROOVES = [(FRONT_PATHS, 0.7, 1.55), (WAIST_PATHS, 0.65, 1.45), (BAR_PATHS, 0.4, 1.2), (FLANK_PATHS, 0.5, 1.4),
           (HEAD_PATHS, 0.55, 1.35)]
LIP = 0.4                         # the raised rear edge of each shield, before the next one's seam


def sstep_v(e0, e1, x):
    """sstep with array edges."""
    t = np.clip((np.asarray(x, float) - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def groove(d, w):
    """A groove's depth (a share) at distance d from its line, w its half-width."""
    return np.maximum(0.0, 1.0 - (d / w) ** 2) ** 1.5


def body_top(x, y):
    """The plates' back: highest along SPINE, falling steeply to the top envelope and in a long curve to the bottom
    one, rounded off at the neck."""
    c = x + 48.0
    r = 28.0 - y
    rt, rb, rs, zs = curve(TOP_ENV, c), curve(BOT_ENV, c), curve(SPINE, c), curve(SPINE_Z, c)
    north = np.clip((rs - r) / np.maximum(rs - rt + 0.8, 1.0), 0.0, 1.0)
    south = np.clip((r - rs) / np.maximum(rb - rs + 0.6, 1.0), 0.0, 1.0)
    prof = np.where(r < rs, np.sqrt(np.maximum(0.0, 1.0 - north ** 2.2)),
                    np.maximum(0.0, 1.0 - south ** 2.0) ** 0.62)
    neck = np.sqrt(np.maximum(0.0, 1.0 - (np.maximum(0.0, NECK - c) / NECK_R) ** 2))
    return zs * prof * neck, prof


SHIELD_CROWN, FLANK_CROWN = 0.55, 0.7    # how much the shields and the flanks' plates bulge between their seams
TAIL_END = 93.5                   # the column past the last shield
BLEND = 0.9                       # (pixels) how far a shield's bulge blends into the next one's or the flank's


def crowns(c, r):
    """The plates' bulge: across each shield (between its seam and the next) above its waist, and across each plate of
    the flanks (between their seams) below the waists; 0 at the seams, 1 midway. Everything blends smoothly (over
    BLEND pixels) where a shield gives way to the next or to the flank below its waist, and the flanks' bulge fades out
    towards the neck."""
    z_shield = np.zeros_like(c)
    below = np.zeros_like(c)
    kc = [curve(sf, r) for sf in SHIELD_FRONT] + [np.full_like(c, TAIL_END)]
    for i in range(len(SHIELD_FRONT)):
        a, b = kc[i], kc[i + 1]
        u = np.clip((c - a) / np.maximum(b - a, 1.0), 0.0, 1.0)
        inside = (c >= a) & (c < b)
        z_shield = np.where(inside, SHIELD_CROWN * np.sin(np.pi * u) ** 0.8, z_shield)
        share = sstep_v(a - BLEND, a + BLEND, c) - (sstep_v(b - BLEND, b + BLEND, c) if i + 1 < len(SHIELD_FRONT)
                                                     else 0.0)
        below += share * sstep(-BLEND, BLEND, r - curve(WAIST[i], c))
    # in front of the first shield (the neck) the flank begins under its waist's start
    below += (1.0 - sstep_v(kc[0] - BLEND, kc[0] + BLEND, c)) * sstep(-BLEND, BLEND, r - WAIST[0][0][1])
    z_flank = np.zeros_like(c)
    lc = [np.full_like(c, 30.0)] + [curve(fs, r) for fs in FLANK_SEAMS] + [np.full_like(c, TAIL_END + 1.0)]
    for j in range(len(lc) - 1):
        a, b = lc[j], lc[j + 1]
        v = np.clip((c - a) / np.maximum(b - a, 1.0), 0.0, 1.0)
        z_flank = np.where((c >= a) & (c < b), FLANK_CROWN * np.sin(np.pi * v) ** 0.7, z_flank)
    z_flank *= sstep_v(kc[0] - 5.0, kc[0] - 1.0, c)
    return z_shield * (1.0 - below) + z_flank * below


def relief(x, y, prof):
    """The grooves along the seams, the plates' bulges and the shields' raised rear edges, stronger on the back than
    down the flank."""
    c = x + 48.0
    r = 28.0 - y
    z = crowns(c, r)
    for paths, depth, width in GROOVES:
        for p in paths:
            d, _ = p.query(c, r)
            z -= depth * groove(d, width)
    for i, p in enumerate(FRONT_PATHS[1:]):
        d, _ = p.query(c, r)
        behind = c < curve(SHIELD_FRONT[i + 1], r)
        z += np.where(behind, LIP * np.exp(-((d - 1.7) / 1.15) ** 2), 0.0)
    return z * (0.35 + 0.65 * prof)


# The eyes (picture column, row of their middles; radii across and up the screen).
EYES = [((23.2, 14.3), (3.4, 2.3)), ((23.0, 21.0), (3.8, 2.25))]
EYE_LENS, EYE_SINK = 0.92, 0.12   # the lens's share of the eye (the rest its halo on the head); how deep it is set


def head_top(x, y):
    """The head: a dome highest between the eyes, its face falling to the jaw, the mouth sunk into it, the jaw a lip
    under it, the eyes in shallow sockets."""
    c = x + 48.0
    r = 28.0 - y
    u = np.where(c < 20.5, (c - 20.5) / 13.2, (c - 20.5) / 10.8)
    w = np.where(r < 17.5, (r - 17.5) / 8.6, (r - 17.5) / 20.6)
    q = np.maximum(0.0, 1.0 - u * u - w * w)
    z = 10.4 * q ** 0.55
    mouth = np.exp(-(((c - 19.6) / 7.2) ** 2 + ((r - 27.4) / 2.5) ** 2) ** 1.6)
    jaw = np.exp(-((r - 31.6) / 1.4) ** 2) * sstep(10.0, 13.0, c) * (1.0 - sstep(25.0, 29.0, c))
    z = z - 2.6 * mouth + 0.6 * jaw
    for (ec, er), (rx, ry) in EYES:
        z -= 0.7 * np.exp(-(((c - ec) / (rx * 1.15)) ** 2 + ((r - er) / (ry * 1.15)) ** 2) ** 2)
    return z


def main_top(x, y, d=None):
    """The head and the plates joined in a smooth crease at the neck, the seams grooved."""
    body, prof = body_top(x, y)
    return smax(head_top(x, y), body, NECK_BLEND) + relief(x, y, prof)


# --- Painting --------------------------------------------------------------------------------------------------------
# The plates' tone: the light the sprite puts over the body (its shades blurred broadly), lighter on the plates'
# bulges and lips and darker in their grooves (the relief), dark in the flanks' seams and in the gap behind each
# shield's raised rear edge (where the sprite draws its darkest reds and 0x40).
BIG = Grid(normalized_blur(S7, ~np.isnan(S7), 1.7))
TONE_A, TONE_B, TONE_RELIEF, TONE_MAX = 0.0, 0.78, 1.6, 5.6
DARK_SEAM, DARK_GAP = 2.6, 2.4
# A glowing seam: its peak heat out to GLOW_CORE from its line, nothing past GLOW_EDGE (the shields' front seams
# glow on the shield behind them only: in front of them, GLOW_FRONT); its light on the plates round it (SPILL: a
# share of its heat, the falloff's radius).
GLOW_CORE, GLOW_EDGE, GLOW_FRONT = 0.45, 1.5, 0.7
GLOW_LIFT = 0.4                   # the seams a little hotter than the sprite's pixels along them (they are thin)
SPILL = (0.34, 1.1)
# Glowing spots (picture column, row, radius, heat): under the eyes' lenses their halo, the tail's white-hot seam,
# the hot joints of the claws.
SPOTS = [(23.2, 14.3, 4.6, 9.4), (23.0, 21.0, 4.9, 9.4), (83.4, 19.2, 2.0, 15.0), (67.8, 44.2, 1.0, 7.0)]


def heat_at(x, y):
    """The heat painted on the body at picture-plane points (ramp 7's shade: 0 the darkest red, 15 white)."""
    c = x + 48.0
    r = 28.0 - y
    _, prof = body_top(x, y)
    tone = TONE_A + TONE_B * BIG(x, y) + TONE_RELIEF * relief(x, y, prof)
    for p in FLANK_PATHS:
        d, _ = p.query(c, r)
        tone -= DARK_SEAM * (1.0 - sstep(0.15, 0.95, d))
    for i, p in enumerate(FRONT_PATHS[1:]):
        d, _ = p.query(c, r)
        before = c < curve(SHIELD_FRONT[i + 1], r)
        tone -= np.where(before, DARK_GAP * np.exp(-((d - 1.0) / 0.45) ** 2), 0.0)
    heat = np.clip(tone, -1.0, TONE_MAX)
    kc = [curve(sf, r) for sf in SHIELD_FRONT]
    for n, (p, peaks, width) in enumerate(zip(GLOW_PATHS, GLOW_PEAKS, GLOW_WIDTH)):
        d, along = p.query(c, r)
        peak = np.interp(along, p.cum, peaks) + GLOW_LIFT
        edge = np.full_like(d, GLOW_EDGE * width)
        if n < len(FRONT_PATHS):
            edge = np.where(c < kc[n], GLOW_FRONT, GLOW_EDGE)
        heat = np.maximum(heat, peak * (1.0 - sstep_v(GLOW_CORE * width, edge, d)))
        heat = np.maximum(heat, SPILL[0] * peak * np.exp(-(d / SPILL[1]) ** 2))
    for sc, sr, rad, peak in SPOTS:
        d = np.hypot(c - sc, r - sr)
        heat = np.maximum(heat, peak * (1.0 - sstep(0.15 * rad, rad, d)))
    return heat


# The bands of heat: (lowest heat (ramp 7's shade), palette index, emission strength in its own colour).
BANDS = [
    (-99.0, 0x70, 0.12),
    (1.3, 0x72, 0.2),
    (2.7, 0x73, 0.27),
    (3.7, 0x74, 0.32),
    (4.8, 0x75, 0.37),
    (6.0, 0x77, 0.43),
    (8.0, 0x7a, 0.5),
    (10.4, 0x7d, 0.56),
    (12.6, 0x7f, 0.62),
]
# The pale knobs and horns (ramp 4), by the light they get (light_value: base where they face up).
KNOB_BANDS = [(-99.0, 0x44), (4.6, 0x46), (5.6, 0x49), (6.3, 0x4c)]
KNOB_GLOW = {0x44: 0.04, 0x46: 0.05, 0x49: 0.07, 0x4c: 0.09}
KNOB_TONE = 6.2                   # their light value where they face up (0x49; towards the sun 0x4c)
# The claws (ramp 7), by light.
CLAW_BANDS = [(-99.0, 0x70), (3.6, 0x72), (4.8, 0x73), (5.8, 0x74), (6.7, 0x75)]
CUT = 0x75                        # the inside, where the pieces were cut: hot lava
METALLIC, ROUGHNESS = 0.45, 0.45   # the crust: its sheen in its own red (a grey sheen browns the dark reds)
LIGHT = Vector((-0.6, 0.6, 1.0)).normalized()   # towards the game's sun
FLAT = LIGHT.z


def materials():
    """Ramp 7's bands (glowing in their own colours, a sheen in their own red) and ramp 4's for the knobs."""
    pal = k.level_palette()
    m = {}
    for _, index, glow in BANDS:
        m[index] = k.material(f"grub_{index:02x}", palette=index, metallic=METALLIC, roughness=ROUGHNESS,
                              emission=pal[index], emission_strength=glow)
    for index, glow in KNOB_GLOW.items():
        m[index] = k.material(f"grub_knob_{index:02x}", palette=index, metallic=0.02, roughness=0.3,
                              emission=pal[index], emission_strength=glow)
    m["cut"] = m[CUT]
    return m


def heat_field(x, y, z, n):
    """heat_at as a Solid's field."""
    return heat_at(x, y)


# The body's mesh: a constrained Delaunay triangulation of its outline, of lines along every glowing seam at the
# distances its bands of heat change (STRIP_OFFSETS: close across the seams, where the heat changes fast, so that the
# bands' borders follow them smoothly), of lines along the dark seams of the flanks and of rings round the glowing
# spots, and of a coarse grid in between (GRID).
STRIP_OFFSETS = (0.0, 0.34, 0.72, 1.1, 1.55)
STRIP_STEP = 0.6                 # the points along the strips' lines
FLANK_OFFSETS = (0.0, 0.6, 1.2)
RING_SHARES = (0.18, 0.36, 0.55, 0.72, 0.88, 1.05)
OUTLINE_STEP = 0.5
FLAT_MERGE = 3.0                  # (degrees) the body's faces merged where they meet flatter than this
RIM_R = 1.1                       # the body's top rounds down to the ground over this far in from its outline
BBOX = (-41.5, 46.5, -20.5, 25.5)
BODY_FIELD = Grid(gauss(BODY_MASK.astype(float), 0.8) - 0.5)


def resample(points, step, closed):
    """Points along a polyline (picture-plane x, y) about step apart, its ends kept."""
    pts = np.array(points, float)
    if closed:
        pts = np.vstack([pts, pts[:1]])
    seg = np.sqrt(((pts[1:] - pts[:-1]) ** 2).sum(axis=1))
    cum = np.concatenate([[0.0], np.cumsum(seg)])
    n = max(2, int(round(cum[-1] / step)) + 1)
    t = np.linspace(0.0, cum[-1], n)
    out = np.stack([np.interp(t, cum, pts[:, 0]), np.interp(t, cum, pts[:, 1])], axis=1)
    return out[:-1] if closed else out


def outline_loops():
    """The body's outline (BODY_FIELD = 0) as closed loops, counter-clockwise, points OUTLINE_STEP apart: the rim of a
    fine Solid, chained."""
    solid = Solid(BODY_FIELD, BBOX, spacing=0.36)
    rim = [e for e in solid.bm.edges if len(e.link_faces) == 1]
    adj = {}
    for e in rim:
        a, b = e.verts
        adj.setdefault(a, []).append(b)
        adj.setdefault(b, []).append(a)
    loops, seen = [], set()
    for start in sorted(adj, key=lambda v: (round(v.co.x, 6), round(v.co.y, 6))):
        if start in seen:
            continue
        loop, prev, cur = [start], None, start
        seen.add(start)
        while True:
            nxt = [v for v in adj[cur] if v is not prev and v not in seen]
            if not nxt:
                break
            prev, cur = cur, nxt[0]
            seen.add(cur)
            loop.append(cur)
        pts = [(v.co.x, v.co.y) for v in loop]
        area = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
                   for i in range(len(pts))) / 2
        if abs(area) < 1.0:
            continue
        if area < 0:
            pts = pts[::-1]
        loops.append(resample(pts, OUTLINE_STEP, True))
    solid.bm.free()
    return loops


def offset_lines(path, offsets, step):
    """Lines along a path (picture column, row) at the given distances either side, points step apart, as
    picture-plane x, y."""
    dense = resample(path.p, step, False)
    tan = np.gradient(dense, axis=0)
    tan /= np.maximum(np.linalg.norm(tan, axis=1)[:, None], 1e-9)
    nrm = np.stack([-tan[:, 1], tan[:, 0]], axis=1)
    lines = []
    for d in offsets:
        for sign in ((1.0,) if d == 0 else (1.0, -1.0)):
            pts = dense + nrm * d * sign
            lines.append(np.stack([pts[:, 0] - 48.0, 28.0 - pts[:, 1]], axis=1))
    return lines


class MeshSolid(Solid):
    """A Solid over a given triangulation of its region (Solid's shape, field and finish work on it as on the grid)."""

    def __init__(self, f, bm):
        self.f = f
        self.bm = bm
        rim_edges = [e for e in bm.edges if len(e.link_faces) == 1]
        self.rim = {v for e in rim_edges for v in e.verts}
        self.seg_a = np.array([[e.verts[0].co.x, e.verts[0].co.y] for e in rim_edges])
        self.seg_b = np.array([[e.verts[1].co.x, e.verts[1].co.y] for e in rim_edges])
        self.tops = set(bm.faces)
        self.vals = {"f": {v: 0.0 for v in bm.verts}}


def body_mesh():
    """The triangulation of the body's region (a bmesh in the picture's plane)."""
    from mathutils.geometry import delaunay_2d_cdt
    from mathutils.kdtree import KDTree
    loops = outline_loops()
    seg_a = np.vstack(loops)
    seg_b = np.vstack([np.roll(lp, -1, axis=0) for lp in loops])

    def to_outline(xy):
        d = np.full(len(xy), 1e9)
        ab = seg_b - seg_a
        l2 = np.maximum((ab ** 2).sum(axis=1), 1e-12)
        for s in range(0, len(xy), 1024):
            p = xy[s:s + 1024, None, :]
            t = np.clip(((p - seg_a) * ab).sum(axis=2) / l2, 0.0, 1.0)
            q = seg_a + t[..., None] * ab
            d[s:s + 1024] = np.sqrt(((p - q) ** 2).sum(axis=2)).min(axis=1)
        return d

    pts, edges, faces = [], [], []

    def add_line(line, closed=False):
        base = len(pts)
        pts.extend((float(p[0]), float(p[1])) for p in line)
        n = len(line)
        for k_ in range(n - 1 + (1 if closed else 0)):
            edges.append((base + k_, base + (k_ + 1) % n))
        return list(range(base, base + n))

    for lp in loops:
        faces.append(add_line(lp, closed=True))

    def add_inside(line):
        inside = (BODY_FIELD(line[:, 0], line[:, 1]) > 0.0) & (to_outline(line) > 0.32)
        run = []
        for p, ok in zip(line, inside):
            if ok:
                run.append(p)
            else:
                if len(run) >= 2:
                    add_line(np.array(run))
                run = []
        if len(run) >= 2:
            add_line(np.array(run))

    for p in GLOW_PATHS:
        for line in offset_lines(p, STRIP_OFFSETS, STRIP_STEP):
            add_inside(line)
    for p in FLANK_PATHS + [Path(NECK_LINE)]:
        for line in offset_lines(p, FLANK_OFFSETS, 0.7):
            add_inside(line)
    for sc, sr, rad, _ in SPOTS:
        for share in RING_SHARES:
            n = max(10, int(2 * math.pi * rad * share / STRIP_STEP))
            ring = np.array([(X(sc) + rad * share * math.cos(2 * math.pi * k_ / n),
                              Y(sr) + rad * share * math.sin(2 * math.pi * k_ / n)) for k_ in range(n)])
            inside = (BODY_FIELD(ring[:, 0], ring[:, 1]) > 0.0) & (to_outline(ring) > 0.32)
            if inside.all():
                add_line(ring, closed=True)
            else:
                add_inside(ring)
    # the coarse grid between, kept clear of the lines
    tree = KDTree(len(pts))
    for i, p in enumerate(pts):
        tree.insert((p[0], p[1], 0.0), i)
    tree.balance()
    x0, x1, y0, y1 = BBOX
    dy = GRID * math.sqrt(3) / 2
    grid = []
    for j in range(int((y1 - y0) / dy) + 1):
        for i in range(int((x1 - x0) / GRID) + 1):
            grid.append((x0 + i * GRID + (GRID / 2 if j % 2 else 0.0), y0 + j * dy))
    grid = np.array(grid)
    keep = (BODY_FIELD(grid[:, 0], grid[:, 1]) > 0.0) & (to_outline(grid) > 0.45 * GRID)
    for p in grid[keep]:
        if tree.find((p[0], p[1], 0.0))[2] > 0.45 * GRID:
            pts.append((float(p[0]), float(p[1])))
    out = delaunay_2d_cdt([Vector(p) for p in pts], edges, faces, 1, 1e-5)
    bm = bmesh.new()
    verts = [bm.verts.new((v.x, v.y, 0.0)) for v in out[0]]
    for f in out[2]:
        if len(f) >= 3:
            bm.faces.new([verts[i] for i in f])
    bm.normal_update()
    for face in bm.faces:
        if face.normal.z < 0:
            face.normal_flip()
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    return bm


def paint(solid, bands, under_key):
    """The top's faces cut along the bands' borders (smooth contours: along the seams the strips' lines are close
    across them), each taking its band; the underside under_key (Solid.paint without zones)."""
    bm = solid.bm
    faces = {fc for fc in bm.faces if fc in solid.tops}
    for lowest, _ in bands[1:]:
        faces = split_contour(bm, solid.vals, "heat", lowest, faces)
    solid.keys = {}
    for fc in bm.faces:
        if fc not in faces:
            solid.keys[fc] = under_key
            continue
        value = sum(solid.vals["heat"][v] for v in fc.verts) / len(fc.verts)
        key = bands[0][1]
        for lowest, mat in bands:
            if value >= lowest:
                key = mat
        solid.keys[fc] = key


def main_body(m):
    """The body: shaped over its mesh (its underside flat on the ground, its rim rounded over RIM_R), painted, its flat
    parts merged."""
    solid = MeshSolid(BODY_FIELD, body_mesh())
    solid.shape(main_top, lambda x, y, d: np.zeros_like(x), lambda x, y: np.zeros_like(x), radius=RIM_R)
    solid.field("heat", heat_field)
    paint(solid, [(lo, idx) for lo, idx, _ in BANDS], 0x70)
    return merge_flat(solid.finish("grub_body", m), FLAT_MERGE)


def merge_flat(obj, angle):
    """Merges the faces of a smooth mesh that meet flatter than angle (each material's apart) and splits them into
    triangles again; every vertex left keeps its normal."""
    mesh = obj.data
    normal = {}
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            normal[mesh.loops[li].vertex_index] = Vector(mesh.corner_normals[li].vector)
    by_pos = {tuple(round(c, 5) for c in v.co): normal[v.index] for v in mesh.vertices if v.index in normal}
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(angle), use_dissolve_boundaries=False, verts=bm.verts[:],
                             edges=bm.edges[:], delimit={"MATERIAL"})
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="BEAUTY", ngon_method="BEAUTY")
    bm.to_mesh(mesh)
    bm.free()
    for p in mesh.polygons:
        p.use_smooth = True
    mesh.normals_split_custom_set_from_vertices(
        [tuple(by_pos.get(tuple(round(c, 5) for c in v.co), Vector((0.0, 0.0, 1.0)))) for v in mesh.vertices])
    return obj


def surf(c, r):
    """The body's height at a picture point (its rim's rounding left out)."""
    return float(main_top(np.array([X(c)]), np.array([Y(r)]))[0])


def light_values(obj, base, a=3.0, b=2.0):
    """light_value of each vertex as the game will light it (its normal sheared to the camera's frame first)."""
    out = []
    for v in obj.data.vertices:
        n = Vector((v.normal.x, v.normal.y, v.normal.z + TAN_T * v.normal.y)).normalized()
        out.append(base + a * (n.dot(LIGHT) - FLAT) + b * (n.z - 1.0))
    return out


def paint_bands(obj, m, values, bands):
    """A part's faces in the bands of a value per vertex (polish_orb_red.band_split), smooth shaded."""
    band_split(obj, values, [(lo, m[key]) for lo, key in bands])
    k.smooth(obj, 80)
    return obj


def ellipsoid(name, centre, radii, mat, segments=14, rings=8):
    """tyrkit's ellipsoid (lofted from explicit rings: the same mesh every run)."""
    return k.ellipsoid(name, centre, radii, mat, segments=segments, rings_count=rings)


def horn_tube(name, stations, mat, segments=10):
    """A tube through its stations only (x, y, z, half-width, half-height, power: sections lying flat), closed to
    points at its ends: horns and hooks need no more rings than that."""
    pts = [Vector(st[:3]) for st in stations]
    rings = []
    for i, st in enumerate(stations):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        side = t.cross(Vector((0.0, 0.0, 1.0)))
        side = side.normalized() if side.length > 1e-6 else Vector((1.0, 0.0, 0.0))
        up = side.cross(t).normalized()
        ring = []
        for j in range(segments):
            a = 2 * math.pi * j / segments
            c, s_ = math.cos(a), math.sin(a)
            pw = st[5]
            ring.append(pts[i] + side * math.copysign(abs(c) ** (2 / pw), c) * max(st[3], 0.03) +
                        up * math.copysign(abs(s_) ** (2 / pw), s_) * max(st[4], 0.03))
        rings.append(ring)
    first = pts[0] - (pts[1] - pts[0]).normalized() * 0.15
    last = pts[-1] + (pts[-1] - pts[-2]).normalized() * 0.12
    return k.loft(name, rings[1:-1], mat, start_point=first, end_point=last)


# The pale knobs: the collar between the head and the first shield, the joints of the claws on the ground (picture
# column, row; radii across, up the screen, height; how far the knob stands out of what it sits on: a share of its
# height).
COLLAR = [(30.4, 10.4, 1.7, 1.4, 1.3), (32.8, 13.3, 2.7, 1.95, 1.8), (33.3, 18.6, 3.0, 2.5, 2.1),
          (31.0, 24.0, 3.0, 2.0, 1.9)]
FEET = [(29.4, 49.2, 1.9, 1.5, 1.4), (38.6, 47.4, 2.6, 1.3, 1.3), (60.4, 43.6, 1.7, 1.6, 1.3),
        (56.8, 41.6, 1.0, 0.9, 0.8)]
# The horns lying back along the shields' backs (picture column, row of their base and their tip; half-width and
# half-height at the base).
HORNS = [((41.4, 13.8), (49.6, 12.3), 1.55, 1.3), ((51.4, 14.0), (58.2, 12.9), 1.5, 1.25),
         ((60.2, 16.4), (66.8, 15.6), 1.45, 1.2), ((67.8, 18.7), (72.8, 18.3), 1.3, 1.1),
         ((74.2, 19.8), (78.8, 20.5), 1.25, 1.05)]
# The tail's tip: a pale bulb (column, row, radii) and the hook curling down from it round the tail's end (column,
# row, height over the tail's surface, half-width, half-height).
BULB = (88.8, 22.4, 3.6, 3.4, 2.7)
HOOK = [(91.6, 25.4, 0.2, 1.2, 0.95), (91.3, 27.4, 0.3, 1.25, 0.95), (90.3, 29.5, 0.35, 1.15, 0.85),
        (88.7, 31.2, 0.35, 1.0, 0.75), (86.7, 32.4, 0.3, 0.8, 0.6), (84.8, 33.2, 0.25, 0.5, 0.4),
        (83.2, 33.6, 0.2, 0.15, 0.12)]
HORN_RISE, HORN_BEND = 1.5, 0.35   # how much a horn rises to its tip and bends up the screen
# The sickle claws on the ground, from their tips (forwards, under the head and under the middle) to their joints
# (column, row, height, half-width, half-height).
CLAW_FRONT = [(8.6, 39.4, 0.5, 0.25, 0.15), (10.0, 41.0, 0.6, 0.6, 0.35), (11.5, 42.6, 0.7, 0.8, 0.5),
              (13.2, 44.2, 0.8, 1.0, 0.6), (15.2, 45.7, 0.9, 1.2, 0.7), (17.6, 47.0, 1.0, 1.4, 0.8),
              (20.6, 48.1, 1.1, 1.55, 0.9), (23.8, 48.8, 1.2, 1.65, 1.0), (26.6, 49.2, 1.3, 1.6, 1.0)]
CLAW_MID = [(45.4, 48.4, 0.45, 0.25, 0.15), (47.6, 48.5, 0.55, 0.6, 0.35), (50.4, 48.3, 0.7, 0.9, 0.5),
            (53.2, 47.9, 0.85, 1.15, 0.65), (56.0, 47.4, 1.0, 1.3, 0.75), (58.6, 46.6, 1.1, 1.3, 0.8)]
# The claws' joints under the body: low dark pads on the ground (column, row, radii) under the knobs, the lava in
# them glowing where the sprite draws it (SPOTS).
PADS = [(34.5, 47.6, 7.6, 2.5, 0.9), (60.6, 44.2, 3.9, 2.7, 0.9)]
PAD_TONE = 1.4
# The front claw's hot tip between its knobs, pointing up the screen (column, row, height, half-width, half-height;
# its heat at each station).
EMBER = [(34.8, 50.2, 0.5, 0.95, 0.7, 10.5), (34.6, 49.0, 0.9, 0.85, 0.65, 12.5), (34.3, 47.8, 1.25, 0.6, 0.5, 12.5),
         (34.0, 46.6, 1.5, 0.15, 0.15, 9.0)]


def knobs(m):
    """The pale parts (ramp 4, by the light they get): the collar's knobs, the claws' joints, the tail's bulb, the
    horns and the tail's hook."""
    parts = []
    for i, (c, r, rx, ry, rz) in enumerate(COLLAR):
        z0 = surf(c, r)
        parts.append(ellipsoid(f"collar{i}", (X(c), Y(r), z0 - 0.25 * rz), (rx, ry, rz), m[0x49]))
    for i, (c, r, rx, ry, rz) in enumerate(FEET):
        parts.append(ellipsoid(f"foot{i}", (X(c), Y(r), 0.45 * rz), (rx, ry, rz), m[0x49]))
    c, r, rx, ry, rz = BULB
    parts.append(ellipsoid("bulb", (X(c), Y(r), max(surf(c, r), 2.0) - 0.4 * rz), (rx, ry, rz), m[0x49], 20, 10))
    for i, ((c0, r0), (c1, r1), hw, hh) in enumerate(HORNS):
        # out of the shield's back (its base sunk into it) back over the next seam, rising a little to its tip
        z0 = surf(c0, r0) - 0.3
        stations = []
        for j in range(9):
            t = j / 8
            c, r = c0 + (c1 - c0) * t, r0 + (r1 - r0) * t
            # a fat curved tooth: thickest a third of the way out, its tip rounded off to a point
            body = math.sin(math.pi * (0.1 + 0.9 * t)) ** 0.55 * (1.0 - 0.45 * t)
            stations.append((X(c), Y(r) + HORN_BEND * t * t, z0 + HORN_RISE * t ** 1.3, hw * max(body, 0.08),
                             hh * max(body, 0.08) * (1.0 - 0.2 * t), 2.3))
        parts.append(horn_tube(f"horn{i}", stations, m[0x49]))
    hook = []
    for c, r, z, hw, hh in HOOK:
        hook.append((X(c), Y(r), max(surf(c, r), 0.4) + z, hw, hh, 2.0))
    parts.append(horn_tube("hook", [tuple(d) for d in densify(hook, 0.9)], m[0x49]))
    for obj in parts:
        paint_bands(obj, m, light_values(obj, KNOB_TONE), KNOB_BANDS)
    return parts


def claws(m):
    """The two sickle claws on the ground."""
    parts = []
    for name, path in (("claw_front", CLAW_FRONT), ("claw_mid", CLAW_MID)):
        stations = densify([(X(c), Y(r), z, hw, hh, 1.6) for c, r, z, hw, hh in path], 1.0)
        obj = horn_tube(name, [tuple(d) for d in stations], m[0x72])
        # lit by the sun, and along their upper edges as hot as the sprite draws them there
        line = Path([(c, r) for c, r, *_ in path])
        peaks = sprite_peaks(line, radius=1.4)
        tone = light_values(obj, 5.2)
        values = []
        for v, t0 in zip(obj.data.vertices, tone):
            d, along = line.query([v.co.x + 48.0], [28.0 - v.co.y])
            # its upper edge, towards the body (up the screen and up)
            edge = smoothstep(0.35, 0.85, 0.75 * v.normal.y + 0.65 * v.normal.z)
            hot = float(np.interp(along[0], line.cum, peaks)) * edge
            values.append(max(t0, hot))
        paint_bands(obj, m, values, CLAW_BANDS + [(lo, idx) for lo, idx, _ in BANDS if lo >= 8.0])
        parts.append(obj)
    return parts


def pads(m):
    """The dark pads under the claws' joints, and the front claw's glowing tip."""
    parts = []
    for i, (c, r, rx, ry, rz) in enumerate(PADS):
        obj = ellipsoid(f"pad{i}", (X(c), Y(r), 0.0), (rx, ry, rz), m[0x70], 20, 8)
        tone = light_values(obj, PAD_TONE)
        values = []
        for v, t0 in zip(obj.data.vertices, tone):
            pc, pr = v.co.x + 48.0, 28.0 - v.co.y
            hot = max([peak * (1.0 - smoothstep(0.15 * rad, rad, math.hypot(pc - sc, pr - sr)))
                       for sc, sr, rad, peak in SPOTS])
            values.append(max(t0, hot))
        paint_bands(obj, m, values, [(lo, idx) for lo, idx, _ in BANDS])
        parts.append(obj)
    stations = [(X(c), Y(r), z, hw, hh, 2.0) for c, r, z, hw, hh, _ in EMBER]
    ember = horn_tube("ember", stations, m[0x7d], segments=8)
    heats = [e[5] for e in EMBER]
    rows = [e[1] for e in EMBER]
    values = [float(np.interp(-(28.0 - v.co.y), [-r for r in rows], heats)) for v in ember.data.vertices]
    paint_bands(ember, m, values, [(lo, idx) for lo, idx, _ in BANDS])
    parts.append(ember)
    return parts


def eyes(m):
    """The eyes: glowing lenses on the head, white-hot, their rims yellow, facing straight up in the picture's plane
    (so that the camera sees them round) and standing over the head all round (their middles at the head's highest
    point under them)."""
    parts = []
    for i, ((c, r), (rx, ry)) in enumerate(EYES):
        a, b = rx * EYE_LENS, ry * EYE_LENS
        rim = [surf(c + a * math.cos(t) * 0.9, r - b * math.sin(t) * 0.9) for t in np.linspace(0, 2 * math.pi, 17)]
        z0 = max(rim + [surf(c, r)]) - EYE_SINK
        obj = ellipsoid(f"eye{i}", (X(c), Y(r), z0), (a, b, 0.8), m[0x7f], 18, 9)
        values = [15.2 - 7.0 * smoothstep(0.5, 1.0, math.hypot((v.co.x - X(c)) / a, (v.co.y - Y(r)) / b))
                  for v in obj.data.vertices]
        paint_bands(obj, m, values, [(lo, idx) for lo, idx, _ in BANDS])
        parts.append(obj)
    return parts


def smoothstep(e0, e1, x):
    """smoothstep of a number."""
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


# --- To the game's camera, the pieces --------------------------------------------------------------------------------

def shear_to_camera(objects):
    """Moves every point of the picture's plane along the game camera's line of sight to its height (y - z tan T), so
    that the camera sees each where the sprite draws it; the normals follow (the shear's inverse transpose)."""
    for obj in objects:
        mesh = obj.data
        normals = [Vector(cn.vector) for cn in mesh.corner_normals]
        for v in mesh.vertices:
            v.co.y -= v.co.z * TAN_T
        out = [Vector((n.x, n.y, n.z + TAN_T * n.y)).normalized() for n in normals]
        mesh.normals_split_custom_set([tuple(n) for n in out])
        mesh.update()


# name, sprite, box (x0, x1, y0, y1) in the picture's plane: the left grub's and the right one's (its mirror image).
PIECES_L = [("lava_grub_l_t1", 77, (-48.0, -24.0, 0.0, 28.0)), ("lava_grub_l_t2", 79, (-24.0, 0.0, 0.0, 28.0)),
            ("lava_grub_l_t3", 81, (0.0, 24.0, 0.0, 28.0)), ("lava_grub_l_t4", 83, (24.0, 48.0, 0.0, 28.0)),
            ("lava_grub_l_b1", 115, (-48.0, -24.0, -28.0, 0.0)), ("lava_grub_l_b2", 117, (-24.0, 0.0, -28.0, 0.0)),
            ("lava_grub_l_b3", 119, (0.0, 24.0, -28.0, 0.0)), ("lava_grub_l_b4", 121, (24.0, 48.0, -28.0, 0.0))]
PIECES_R = [(name.replace("_l_", "_r_"), sprite + 8, box) for name, sprite, box in PIECES_L]
MIRROR_X = 0.5                    # the right grub is the left one mirrored about x 0.5 (the sheet draws it a pixel
#                                   right of the exact mirror image: its column c is the left one's column 96 - c)


def mirror(objects, axis):
    """Mirrors objects about x = axis (their faces turned back the right way round, their normals mirrored)."""
    for obj in objects:
        mesh = obj.data
        corner = {}
        for poly in mesh.polygons:
            for li in poly.loop_indices:
                n = mesh.corner_normals[li].vector
                corner[(poly.index, mesh.loops[li].vertex_index)] = (-n.x, n.y, n.z)
        for v in mesh.vertices:
            v.co.x = 2 * axis - v.co.x
        mesh.flip_normals()
        normals = [None] * len(mesh.loops)
        for poly in mesh.polygons:
            for li in poly.loop_indices:
                normals[li] = corner[(poly.index, mesh.loops[li].vertex_index)]
        mesh.normals_split_custom_set(normals)
        mesh.update()


def whole_mask(sheet, sprites):
    """The eight sprites placed as the levels place them: 96 x 56."""
    mask = [[False] * W for _ in range(H)]
    for i, sprite in enumerate(sprites):
        c0, r0 = (i % 4) * 24, (i // 4) * 28
        for r, row in enumerate(k.sprite_mask(sheet, sprite)):
            for c, v in enumerate(row):
                if v:
                    mask[r0 + r][c0 + c] = True
    return mask


def build_whole():
    """The left grub whole, in the picture's plane: its parts and materials."""
    k.reset()
    m = materials()
    parts = [main_body(m)] + eyes(m) + knobs(m) + claws(m) + pads(m)
    return parts, m


def export_grub(side, options, sheet, out):
    """One grub (l, or r: the left one mirrored): the whole checked (as the camera sees it: in the picture's plane;
    from straight above: sheared), its pieces cut, sheared, moved to their sprites' middles, checked and exported."""
    pieces = PIECES_L if side == "l" else PIECES_R
    only = options["only"].split(",") if "only" in options else None
    wanted = [p for p in pieces if not only or p[0] in only]
    if not wanted and "whole" not in options and "preview" not in options:
        return
    whole, m = build_whole()
    if side == "r":
        mirror(whole, MIRROR_X)
    triangulate(whole)
    low, high = mk.bounds(whole)
    print("== whole %s: %d triangles, x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (
        side, mk.triangles(whole), low.x, high.x, low.y, high.y, low.z, high.z))
    sprites = [p[1] for p in pieces]
    if sheet:
        mask = whole_mask(sheet, sprites)
        mk.compare("whole %s, as the camera sees it" % side, mk.coverage(whole, W, H), mask)
    if "whole" in options or "preview" in options:
        seen = [o.copy() for o in whole]
        for o in seen:
            o.data = o.data.copy()
            bpy.context.scene.collection.objects.link(o)
        shear_to_camera(seen)
        if sheet:
            mk.compare("whole %s, from straight above" % side, mk.coverage(seen, W, H), mask)
        if "whole" in options:
            mk.export(seen, options["whole"] + side + ".glb")
        if "preview" in options:
            bpy.context.scene.view_settings.view_transform = "Standard"
            mk.preview(options["preview"] + "grub_" + side, seen, size=(W, H), scale=8, distance=2.4)
        for o in seen:
            bpy.data.objects.remove(o)
    for name, sprite, box in wanted:
        parts = [p for p in (cut(src, box, m["cut"]) for src in whole) if p is not None]
        drop_unused(parts)
        shear_to_camera(parts)
        mk.transform(parts, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
        bpy.context.view_layer.update()
        triangulate(parts)
        parts = [join(parts, name)]
        parts[0].data.name = name
        for src in whole:
            src.hide_render = True
        if sheet:
            mk.compare("%s (E %d)" % (name, sprite), mk.coverage(parts, 24, 28), k.sprite_mask(sheet, sprite))
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
        sheet = os.path.join(sheets, "enemy_E.png") if os.path.isdir(sheets) else sheets
    for side in ("l", "r"):
        export_grub(side, options, sheet, out)


if __name__ == "__main__":
    build()
