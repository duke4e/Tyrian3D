"""The big green shell of TORM, BOTANY A and BOTANY B (their boss), ?TUNNEL? and episode 6's GREY MOON and GLACIER (sheet
J: fifteen 2x2 sprites that the level events lay out as one 96 x 112 picture), its dome lighting up and its eye opening
as they fire; rebuilt (2026-10-23, round 38, the quality redo) as solids: round 36's model of it (one heightfield of
the whole picture on polish_gyges_wall.Plate's grid, painted by the sprites' shades) read as a blotchy embossed
sprite, worse than the old model before it. Round 36's model replaced wave3_m_shell.py and wave3_at_j.py.

Where it appears (as round 36 found it): TORM t6600 (episode 2, link 64 and the boss bar): event 7 (top layer) 772
(J 193) at x 164, 773 (195) at 188, y -56, 774 (241) at 164 and 775 (243) at 188, y -28; event 51 (the top layer's
one-frame pieces, armour 250) 153 155 157 159 at x 140 164 188 212, y -84; 191 at 140 and 197 at 212, y -56; 229 at
140 and 235 at 212, y -28; 267 269 271 at 152 176 200, y 0: four rows of the sheet, the bottom one 12 pixels in.
BOTANY A and B t4900 the same; ?TUNNEL? t200 the same 30 pixels to the left on the ground (events 10 and 52, armour
40). GREY MOON (t6300) and GLACIER (t5300) take TORM's boss block, 1577-1580 (772-775's copies), but not its event 51
pieces (episode 6's boss blocks keep the boss's spawns and link events only): there only the four middle pieces show
(their outer cut faces dark green, as before). 772 and 773 fire gun 76 every 80 ticks and then play their animation
(animate 2): 193 161 199 237 275 165 203 203 165 275 237 199 161 193 (and 195 163 201 239 277 167 205 ...): the
dome's glass lights up from a dull green through bright green to white-hot and back, and the lamps at the conduits'
tops (rows 52-55) go out; 774 and 775 fire gun 116: 241 231 231 231 241 (and 243 233 ...): the eye opens on a green
gem and the conduits beside it light up along their length (rows 56-83). No other enemy, launched ones included,
shows any of these sprites; none is another sprite's pixels mirrored, turned or in other ramps. The outline is its
own mirror image about the middle of column 48 (x 0.5): the shell is built symmetric about it, its parts placed
where each side's sprite draws them (the right conduit at columns 60-66, the left at 30-36; the hose only right).

As the sprites and their 4x upscales draw it (the picture's columns and rows; lit from the upper left): a carapace of
green ribs (ramp 2) running down the screen, a broad cowl over its top (rows 2-20) parted by an L of seams, side pods
at its shoulders (rows 12-35), the ribs parting at the bottom into two lobes (from row 82, columns 47-50 open); on it,
grey (ramp 0): a gun barrel standing at each shoulder (columns 11-15 and 81-85 of rows 12-28, a lit collar at rows
16-18), an arm from each in to the middle (rows 18-21) with a bolt on it (columns 31-35 and 63-67) and a claw at its
end gripping the dome's housing at its upper corners (columns 36-43 and 54-61 of rows 19-28); the dome (columns 29-68
of rows 21-49): a dark housing round two glass lobes (columns 34-63 of rows 28-46, which the frames light), a spine
between them with a ladder of four rungs (column 48, rows 30-37), a stack at its foot (columns 43-55 of rows 39-47);
a hose curving from its lower right into the neck (columns 56-64 of rows 41-52); the neck under it (two wedges, rows
47-56), the barrel down from it (columns 46-51 of rows 55-71) into the ring of the eye in its dark housing (columns
37-60 of rows 66-84); the shoulder plates (columns 6-21 of rows 36-66 and their mirror image: an upper tile, a lit
ridge across at row 44, the middle tile, the lower one with its outer corner cut away); green lamps of ramp 12 at the
tops of the two conduit ribs beside the housing (rows 52-55) and at their feet (rows 84-91).

Built as such a creature's armour (polish_fleet_walker.py's and polish_pincer_boss.py's way: solids in the picture's
plane, x and y as the sprites draw them and z up, cut along the sprites' edges and sheared along the game camera's
line of sight by polish_fleet_walker.export_pieces): the shell a dark solid over the sprites' outline (its pixels'
outline smoothed, polish_fleet_walker.mask_loops), domed (its height Z_RIM at the rim rising RISE over FALL pixels,
a crown across, bulges for the cowl, the side pods, the flanks beside the dome and the lobes: BULGES), its rim and the
grooves between the ribs showing; the ribs real solids on it, one per band between the grooves (RIBS_LEFT,
RIBS_RIGHT, the middle one only over the top), each over its band's plan within the outline (INSET), its top the
shell's height and its shoulders rounded (RIB_H, RIB_R), its ends rounded where they meet the rim; they are left out
where a grey part covers a whole band (occluders()), split where the cowl's seam crosses them and where the conduits'
lamps sit (lenses swelling over the ribs). The grey parts are separate solids standing over the ribs (levels(): each
at the highest rib top under it and a little more): the gun barrels and the barrel lathed along y (muzzle ring,
collar, body), the arms tubes with ellipsoid bolts and collars, the claws bevelled blocks sloping down onto the
housing with a knuckle, the dome's housing a frame (a solid over its outline, rounded), the glass two overlapping
ellipsoids (the spine over their crease), the spine, rungs, stack and posts bevelled blocks, the hose a smooth tube,
the neck two bevelled wedges, the eye's housing a rounded frame round the socket, the ring a torus, the closed eye a
glossy black dome, the open eye a faceted gem; the plates three bevelled blocks sloping down to the outside and a
ridge. Materials by part, each one palette index of the sprite's ramps (no shades painted from the sprite's pixels):
the ribs 0x28 (glossy), the shell under them 0x22, the steel 0x09 with its bright collars, bolts and rungs 0x0c, the
dome's housing 0x05, the eye's 0x05, the hose 0x08, the glass 0x0a (glossy), the pupil 0x02, the lamps 0xc5 (glowing
0.38). The frames change only what they light: the glass in bands of heat round each lobe's hot point (161 and 199
dull greens 0x28-0x2b glowing 0.1-0.18, 237 and 275 bright greens 0xc5-0xcd 0.3-0.5, 165 and 203 white-hot middles
0x2e-0x2f 0.55-0.62) with the top lamps out (rib green); 231/233 the gem (0xc5-0xcd, 0.42-0.6) and the conduits
(0xc7, 0.42). Heights: z 0 (the underside, the layer's plane) to 13.45 (the spine's rungs; the glass 13.3, the stack
13.15, the bolts and the barrel 12.3, the carapace's ribs up to 10.4); on the top layer the player flies through the
dome, as the 2D game draws the shell over the ship (round 36's dome reached 14). Deterministic: no random numbers, no booleans; every mesh triangulated before the export.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera. The whole's origin
is the picture's middle (its pixel edge 48, 56): column c's left edge is x = c - 48, row r's top edge y = 56 - r; a
piece whose sprite's top left pixel is (c0, r0) has its origin at (c0 + 12 - 48, 42 - r0) (models.cfg origin).

models.cfg: unchanged (the model, sprite and frame lines of green_shell_153 ... _271 and the 14 frame models, origin,
yaw=0, height=-4: on ?TUNNEL?'s ground the shell rests on the terrain, on the top layer it sits 4 lower).

Kept here for other scripts: edt, seg_dist and limit_materials (round 36's, unchanged), which polish_skull_chest.py,
polish_hot_dog.py, polish_nose_drip_face.py, polish_missile_sign.py and polish_brain.py import; polish_station.py
imports limit_materials (its capsule).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each piece's outline as the
camera sees it against its sprite), --preview <prefix> --pieces 1 (each piece's top and 3/4 views), --only <name,...>
(models to export), --whole <prefix> (the uncut wholes, unsheared, as <prefix><look>.glb, for looking at).
"""
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_fleet_walker as fw  # noqa: E402  (export_pieces, mask_loops, InsideDistance, area, paint_faces, LIGHT)
from polish_ring_machine import relief  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402

LEFT, TOP = -48.0, 56.0           # the picture's top left corner: column c's left edge is x = c - 48, row r's top y = 56 - r
AXIS_C = 48.5                     # the outline's mirror line (a column edge: the middle of column 48)


def X(c):
    return c - 48.0


def Y(r):
    return 56.0 - r


def P(c, r):
    return (X(c), Y(r))


def MC(c):
    """A column edge mirrored about the shell's middle."""
    return 2 * AXIS_C - c


def smooth01(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)


def rounded(t):
    """0 at 0 rising as a quarter circle to 1 at 1."""
    t = np.clip(t, 0.0, 1.0)
    return np.sqrt(np.clip(1.0 - (1.0 - t) ** 2, 0.0, 1.0))


def fnum(v):
    return float(np.asarray(v).reshape(-1)[0])


# --- Shared with other scripts ------------------------------------------------------------------------------------------
# Round 36's helpers, kept as they were: polish_skull_chest.py, polish_hot_dog.py, polish_nose_drip_face.py,
# polish_missile_sign.py and polish_brain.py import them from here (the shell itself no longer uses them).

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


def seg_dist(Xa, Ya, pts):
    d = np.full(np.shape(Xa), 1e9)
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        dx, dy = x1 - x0, y1 - y0
        t = np.clip(((Xa - x0) * dx + (Ya - y0) * dy) / max(1e-9, dx * dx + dy * dy), 0.0, 1.0)
        d = np.minimum(d, np.hypot(Xa - (x0 + t * dx), Ya - (y0 + t * dy)))
    return d


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


# --- Materials ------------------------------------------------------------------------------------------------------
# key: (palette index, metallic, roughness, emission strength in its own colour)
BASE_MATS = {
    "rib": (0x28, 0.3, 0.3, 0.0),          # the carapace's ribs: glossy green chitin
    "hull": (0x22, 0.2, 0.5, 0.0),         # the shell under them, seen in the grooves and along the rim
    "cap_green": (0x23, 0.1, 0.6, 0.0),    # cut faces of green parts
    "steel": (0x09, 0.3, 0.32, 0.0),       # guns, arms, plates, neck, barrel
    "bright": (0x0c, 0.3, 0.26, 0.0),      # collars, bolts, rungs, ridges
    "frame": (0x05, 0.35, 0.36, 0.0),      # the dome's housing
    "socket": (0x05, 0.35, 0.38, 0.0),     # the eye's housing
    "hose": (0x08, 0.3, 0.36, 0.0),
    "black": (0x01, 0.3, 0.35, 0.0),       # bores, the eye's socket floor
    "pupil": (0x02, 0.35, 0.12, 0.0),      # the closed eye: glossy black
    "cap_grey": (0x03, 0.2, 0.6, 0.0),     # cut faces of grey parts
    "lamp": (0xc5, 0.0, 0.2, 0.38),        # the conduits' lamps
    "glass": (0x0a, 0.5, 0.22, 0.0),       # the dome's glass, dark (193, 195)
}
# The dome's glass as the frames light it: bands of heat (lowest heat, palette index, glow), hottest in each lobe's
# upper middle (161 and 199 a dull green, 237 and 275 bright green, 165 and 203 white-hot in the middle).
GLASS_LOOKS = {
    "idle": [(-9.0, 0x0a, 0.0)],
    "dome161": [(-9.0, 0x28, 0.1), (0.55, 0x29, 0.13)],
    "dome199": [(-9.0, 0x29, 0.12), (0.5, 0x2a, 0.16)],
    "dome237": [(-9.0, 0xc5, 0.3), (0.45, 0xc8, 0.38)],
    "dome275": [(-9.0, 0xc7, 0.34), (0.35, 0xca, 0.42), (0.7, 0xcd, 0.5)],
    "dome165": [(-9.0, 0xc9, 0.38), (0.3, 0xcc, 0.46), (0.62, 0x2e, 0.55)],
    "dome203": [(-9.0, 0xcb, 0.42), (0.22, 0x2e, 0.55), (0.52, 0x2f, 0.62)],
}
CONDUIT_LIT = (0xc7, 0.0, 0.25, 0.42)  # the conduits as the eye's frame lights them
GEM = [(-9.0, 0xc5, 0.42), (0.55, 0xc9, 0.5), (0.85, 0xcd, 0.6)]   # the eye's gem (231, 233): bands by height


def materials(look):
    pal = k.level_palette()

    def mat(key, index, metallic, roughness, glow):
        extra = dict(emission=pal[index], emission_strength=glow) if glow > 0 else {}
        return k.material("gshell_%s" % key, palette=index, metallic=metallic, roughness=roughness, **extra)
    m = {key: mat(key, *spec) for key, spec in BASE_MATS.items()}
    m["glass_bands"] = [(lo, mat("glass%x" % index, index, 0.5 if index < 0x10 else 0.1, 0.22 if index < 0x10 else 0.1,
                             glow))
                        for lo, index, glow in GLASS_LOOKS.get(look, GLASS_LOOKS["idle"])]
    m["conduit"] = mat("conduit_lit", *CONDUIT_LIT) if look == "eye231" else m["rib"]
    m["lamp_top"] = m["rib"] if look.startswith("dome") else m["lamp"]
    m["gem_bands"] = [(lo, mat("gem%x" % index, index, 0.1, 0.12, glow)) for lo, index, glow in GEM]
    return m


# --- The carapace -----------------------------------------------------------------------------------------------------
# The picture's pixels (the sprites placed as the levels place them: row: column runs), the shell's outline.
OUTLINE = """
2:36-61 3:31-66 4:28-69 5:25-72 6:23-74 7:22-75 8:20-77 9:19-78 10:18-79 11:17-80 12:9-12,16-81,85-88 13:8-89
14:7-90 15:6-91 16:5-92 17:5-92 18:4-93 19:4-93 20:3-94 21:3-94 22:3-94 23:3-94 24:3-94 25:3-94 26:3-94 27:2-95
28:1-96 29:1-96 30:1-96 31:1-96 32:1-96 33:1-96 34:1-96 35:1-96 36:1-96 37:2-95 38:2-95 39:2-95 40:2-95 41:2-95
42:2-95 43:2-95 44:2-95 45:4-93 46:2-95 47:2-95 48:2-95 49:2-95 50:2-95 51:2-95 52:2-95 53:3-94 54:4-93 55:7-90
56:8-89 57:9-88 58:9-88 59:10-87 60:10-87 61:10-87 62:10-87 63:10-87 64:10-87 65:10-87 66:12-85 67:12-85 68:12-85
69:12-85 70:12-85 71:12-85 72:13-84 73:13-84 74:13-84 75:14-83 76:14-83 77:14-83 78:15-82 79:15-82 80:16-81 81:16-81
82:17-47,50-80 83:17-47,50-80 84:18-47,50-79 85:19-47,50-78 86:20-47,50-77 87:21-47,50-76 88:22-47,50-75
89:23-47,50-74 90:24-47,50-73 91:25-47,50-72 92:26-47,50-71 93:27-47,50-70 94:28-46,51-69 95:29-46,51-68
96:30-45,52-67 97:31-45,52-66 98:32-44,53-65 99:33-43,54-64 100:34-42,55-63 101:35-42,55-62 102:36-42,55-61
"""


def outline_mask():
    m = np.zeros((112, 96), bool)
    for item in OUTLINE.split():
        r, runs = item.split(":")
        for run in runs.split(","):
            c0, c1 = (int(v) for v in run.split("-"))
            m[int(r), c0:c1] = True
    return m


# The shell's height over its outline (z 0 its underside): its rim Z_RIM high, rising over FALL pixels by RISE, a
# crown across, and bulges: the cowl over the top, the side pods that carry the guns, the flanks beside the dome.
Z_RIM, RISE, FALL, CROWN = 1.4, 5.0, 12.0, 1.4
BULGES = [  # column, row, half-width, half-height (pixels), height, mirrored too
    (48.5, 9.5, 27.0, 11.5, 2.1, False),      # the cowl
    (8.5, 27.0, 8.0, 16.0, 1.6, True),        # the side pods
    (23.0, 28.5, 7.5, 9.0, 1.1, True),        # the flanks beside the dome
    (33.0, 92.0, 11.0, 11.0, 0.6, True),      # the lobes
]
INSET = 0.75                      # the ribs this far inside the shell's outline (its rim shows dark round them)
RIB_H, RIB_R = 1.1, 2.6           # the ribs' height over the shell, their rounded shoulders
GAP = 0.75                        # the grooves between them
RIB_END = 1.8                     # their ends rounded with this radius where they meet the rim
# The ribs' edges (column edges): the left half's, the middle rib's (only over the top: below it the dome, the neck,
# the barrel and the eye's housing cover it, and the lobes part there), the right half's. The cuts between the pieces
# (columns 12, 24, 36, 60, 72, 84) run along grooves; the conduits are the ribs 30-36 and 60-66.
RIBS_LEFT = [0.0, 6.0, 12.0, 18.0, 24.0, 30.0, 36.0, 41.5, 47.0]
RIB_MIDDLE = (47.0, 50.0, 31.0)   # columns, its lowest row
RIBS_RIGHT = [50.0, 55.0, 60.0, 66.0, 72.0, 78.0, 84.0, 90.0, 97.0]
SEAMED = [(41.5, 47.0), (47.0, 50.0), (50.0, 55.0)]   # the ribs the cowl's seam crosses (the sprite's L of seams)
SEAM_ROW, SEAM = 10.6, 0.8
CONDUITS = [  # band (columns), the lamp at its top (rows), the conduit (rows), the lamp at its foot (rows)
    ((30.0, 36.0), (51.8, 55.8), (56.2, 84.0), (84.4, 86.0)),
    ((60.0, 66.0), (53.6, 55.8), (56.2, 84.0), (84.4, 91.8)),
]


class Hull:
    """The shell's outline (the pixels' outline, smoothed), the distance inside it and its height."""

    def __init__(self):
        loops = fw.mask_loops(outline_mask(), LEFT, TOP, chaikin=2, sigma=1.6)
        self.loop = max(loops, key=lambda p: abs(fw.area(p)))
        self.dist = fw.InsideDistance([self.loop], step=0.25, sigma=1.0)

    def d(self, x, y):
        D = self.dist
        u = (np.asarray(x, float) - D.x0) / D.step
        v = (np.asarray(y, float) - D.y0) / D.step
        i = np.clip(np.floor(u).astype(int), 0, D.nx - 2)
        j = np.clip(np.floor(v).astype(int), 0, D.ny - 2)
        fu, fv = np.clip(u - i, 0.0, 1.0), np.clip(v - j, 0.0, 1.0)
        f = D.f
        return (f[j, i] * (1 - fu) + f[j, i + 1] * fu) * (1 - fv) + (f[j + 1, i] * (1 - fu) + f[j + 1, i + 1] * fu) * fv

    def z(self, x, y):
        x, y = np.asarray(x, float), np.asarray(y, float)
        z = Z_RIM + RISE * rounded(self.d(x, y) / FALL)
        z = z + CROWN * np.clip(1.0 - ((x - (AXIS_C - 48.0)) / 47.0) ** 2, 0.0, None)
        for c, r, hw, hh, h, both in BULGES:
            for cc in ((c, MC(c)) if both else (c,)):
                u = ((x - X(cc)) / hw) ** 2 + ((y - Y(r)) / hh) ** 2
                z = z + h * np.clip(1.0 - u, 0.0, None) ** 2
        return z

    def interval(self, x, inset):
        """The rows (as y) the outline, inset, spans at x: (low, high), or None."""
        ys = np.arange(-60.0, 60.0, 0.05)
        inside = self.d(np.full_like(ys, x), ys) >= inset
        if not inside.any():
            return None
        idx = np.nonzero(inside)[0]
        # the longest run
        runs, start = [], idx[0]
        for a, b in zip(idx, idx[1:]):
            if b != a + 1:
                runs.append((start, a))
                start = b
        runs.append((start, idx[-1]))
        a, b = max(runs, key=lambda r: r[1] - r[0])
        return ys[a], ys[b]


def rib_footprint(hull, x0, x1, y_lo, y_hi, round_cuts=False):
    """A rib's plan: the band x0..x1 within the inset outline and y_lo..y_hi, its ends rounded where they meet the
    rim (where they are cut by y_lo, y_hi they stay square, hidden under the parts there, unless round_cuts: a seam
    across the ribs)."""
    n = max(6, int(round((x1 - x0) / 0.2)) + 1)
    top, bottom = [], []
    for i in range(n):
        x = x0 + (x1 - x0) * i / (n - 1)
        span = hull.interval(x, INSET)
        if span is None:
            continue
        lo, hi = span
        a, b = max(lo, y_lo), min(hi, y_hi)
        side = min(x - x0, x1 - x)
        pull = RIB_END - math.sqrt(max(0.0, RIB_END ** 2 - max(0.0, RIB_END - side) ** 2))
        if hi < y_hi or round_cuts:
            b -= pull
        if lo > y_lo or round_cuts:
            a += pull
        if b - a < 0.25:
            continue
        top.append((x, b))
        bottom.append((x, a))
    if len(top) < 3:
        return None
    return top + bottom[::-1]


def rib_bands():
    """(name, x0, x1, y_lo, y_hi, key, round_cuts) of the ribs: the bands between the grooves, split where the
    conduits' lamps and the conduits are, and by the cowl's seam."""
    bands = []
    edges = [(RIBS_LEFT[i], RIBS_LEFT[i + 1]) for i in range(len(RIBS_LEFT) - 1)]
    edges += [(RIBS_RIGHT[i], RIBS_RIGHT[i + 1]) for i in range(len(RIBS_RIGHT) - 1)]
    c0, c1, low = RIB_MIDDLE
    edges.append((c0, c1))
    for c0, c1 in edges:
        x0, x1 = X(c0) + GAP / 2, X(c1) - GAP / 2
        top = 99.0
        bottom = -99.0 if (c0, c1) != RIB_MIDDLE[:2] else Y(RIB_MIDDLE[2])
        conduit = [cd for cd in CONDUITS if cd[0] == (c0, c1)]
        if conduit:
            _, lamp, body, foot = conduit[0]
            bands.append(("rib_%d_a" % int(c0), x0, x1, Y(lamp[0]) + 0.4, top, "rib", False))
            bands.append(("lamp_%d" % int(c0), x0, x1, Y(lamp[1]), Y(lamp[0]), "lamp_top", False))
            bands.append(("conduit_%d" % int(c0), x0, x1, Y(body[1]), Y(body[0]), "conduit", False))
            bands.append(("foot_%d" % int(c0), x0, x1, Y(foot[1]), Y(foot[0]), "lamp", False))
            bands.append(("rib_%d_b" % int(c0), x0, x1, bottom, Y(foot[1]) - 0.4, "rib", False))
        elif (c0, c1) in SEAMED:
            ys = Y(SEAM_ROW)
            bands.append(("rib_%d_c" % int(c0), x0, x1, ys + SEAM / 2, top, "rib", True))
            bands.append(("rib_%d" % int(c0), x0, x1, bottom, ys - SEAM / 2, "rib", True))
        else:
            bands.append(("rib_%d" % int(c0), x0, x1, bottom, top, "rib", False))
    return bands


def covered_rows(occluders, x0, x1, ys):
    """Which of the rows ys the occluding parts' plans (inset by a pixel) cover across the whole band x0..x1."""
    from polish_ring_machine import Region
    xs = np.linspace(x0 + 0.2, x1 - 0.2, max(3, int((x1 - x0) / 0.5) + 1))
    pts = np.array([(x, y) for y in ys for x in xs])
    cov = np.zeros(len(pts), bool)
    for poly in occluders:
        region = Region([poly])
        inside = region.inside(pts)
        if not inside.any():
            continue
        far = np.zeros(len(pts), bool)
        sel = np.nonzero(inside)[0]
        far[sel] = region.distance(pts[sel]) > 1.0
        cov |= far
    return cov.reshape(len(ys), len(xs)).all(1)


def carapace(m, hull, occluders):
    """The shell (dark, its rim and the grooves) and the ribs on it: each a solid over its plan, its top the shell's
    height and its shoulders rounded, left out where the grey parts cover a whole band."""
    def shell_height(x, y, d):
        return fnum(hull.z(x, y))
    shell = relief("hull", [hull.loop], shell_height, {"top": m["hull"], "side": m["hull"]}, bottom=0.0,
                   spacing=1.0, band=2.0, smooth_angle=70.0)
    parts = [shell]

    def rib_height(x, y, d):
        return fnum(hull.z(x, y)) - 0.06 + RIB_H * fnum(rounded(d / RIB_R))

    def lens_height(x, y, d):
        # the lamps: lenses swelling a little over the ribs' height
        return fnum(hull.z(x, y)) - 0.06 + (RIB_H + 0.35) * fnum(rounded(d / 1.6))
    ys = np.arange(-50.0, 56.0, 0.25)
    for name, x0, x1, y_lo, y_hi, key, round_cuts in rib_bands():
        cov = covered_rows(occluders, x0, x1, ys)
        # the band's runs of rows not covered, reaching a pixel under the covering parts
        segments, start = [], None
        for i, y in enumerate(ys):
            if not cov[i] and start is None:
                start = y
            if cov[i] and start is not None:
                segments.append((start, y))
                start = None
        if start is not None:
            segments.append((start, ys[-1] + 1.0))
        for j, (a, b) in enumerate(segments):
            lo = max(y_lo, a - 1.0 if a > ys[0] else -99.0)
            hi = min(y_hi, b + 1.0 if b < ys[-1] else 99.0)
            if hi - lo < 0.6:
                continue
            poly = rib_footprint(hull, x0, x1, lo, hi, round_cuts)
            if poly is None:
                continue
            mat = m[key]
            lens = key in ("lamp", "lamp_top")
            rib = relief("%s_%d" % (name, j), [poly], lens_height if lens else rib_height, {"top": mat, "side": mat},
                         bottom=0.4, spacing=0.4 if lens else 0.6, band=1.3, smooth_angle=65.0)
            parts.append(rib)
    return parts


# --- Hard parts ---------------------------------------------------------------------------------------------------------

def lathe_y(name, profile, cx, cz, mat, segments=24):
    """A round part along y (down the screen): profile [(row, radius), ...] in increasing row, its ends closed."""
    rings = []
    for r, rad in profile:
        y = Y(r)
        rings.append([Vector((cx + rad * math.cos(2 * math.pi * j / segments), y,
                              cz + rad * math.sin(2 * math.pi * j / segments))) for j in range(segments)])
    obj = k.loft(name, rings, mat, start_point=(cx, Y(profile[0][0]), cz), end_point=(cx, Y(profile[-1][0]), cz))
    return k.smooth(obj, 50)


def block(name, outline_cr, z0, top, mat, bevel=0.45, segments=2):
    """A bevelled block over an outline of (column, row) points from z0 up to top (a height or a function of x, y)."""
    pts = [P(c, r) for c, r in outline_cr]
    if callable(top):
        obj = mk.wedge(name, pts, z0, top, mat)
    else:
        obj = mk.prism(name, pts, z0, top, mat)
    mk.bevel(obj, bevel, segments, 30.0)
    mk.shade(obj, 35.0)
    return obj


def mirror_cr(pts):
    return [(MC(c), r) for c, r in reversed(pts)]


def guns(m, hull):
    """The gun pods' barrels standing at the shoulders (columns 11-15 and 81-85 of rows 12-28) on the side pods: a
    muzzle ring, the barrel, a lit collar (rows 16-18), the body, its foot under the arm."""
    parts = []
    for c in (13.0, 83.0):
        x = X(c)
        cz = fnum(hull.z(x, Y(21.0))) + RIB_H + 0.6
        profile = [(12.5, 0.6), (12.6, 1.9), (12.9, 2.25), (14.3, 2.25), (14.5, 1.85), (15.9, 1.85), (16.1, 2.5),
                   (18.4, 2.5), (18.6, 2.0), (26.6, 2.0), (27.4, 1.6), (27.7, 0.6)]
        parts.append(lathe_y("gun_%d" % int(c), profile, x, cz, m["steel"], 24))
        mk.paint(parts[-1], lambda co, n: m["bright"] if 16.1 <= 56.0 - co.y <= 18.4 or 56.0 - co.y < 14.4 else None)
        bore = lathe_y("gun_bore_%d" % int(c), [(12.45, 0.01), (12.45, 1.1), (12.7, 1.1), (12.71, 0.01)], x, cz,
                       m["black"], 16)
        parts.append(bore)
    return parts




def arms(m, hull, lv):
    """The arms from the guns in to the dome (rows 18-21), a bolt on each (columns 31-35 and 63-67), and the claws at
    their inner ends gripping the dome's housing at its upper corners (columns 37-43 and 54-60 of rows 20-28)."""
    parts = []
    ARM_Z, CLAW_TOP = lv["arm"], lv["arm"] + 1.2
    for side in (-1, 1):
        def C(c):
            return c if side < 0 else MC(c)
        a = (X(C(14.6)), Y(20.0), ARM_Z - 0.5)
        b = (X(C(37.4)), Y(20.4), ARM_Z)
        arm = mk.tube("arm_%d" % side, [a, b], 1.45, m["steel"], 18)
        k.smooth(arm, 50)
        parts.append(arm)
        bolt = k.ellipsoid("bolt_%d" % side, (X(C(33.0)), Y(18.4), ARM_Z + 0.9), (2.1, 1.8, 1.4), m["bright"], 20, 10)
        k.smooth(bolt, 70)
        parts.append(bolt)
        collar = mk.tube("arm_collar_%d" % side, [(X(C(26.0)), Y(20.2), ARM_Z - 0.2), (X(C(27.4)), Y(20.2), ARM_Z - 0.2)],
                         1.75, m["bright"], 18)
        k.smooth(collar, 50)
        parts.append(collar)
        claw = [(36.2, 19.0), (40.6, 19.2), (42.8, 21.2), (43.2, 25.4), (42.0, 27.6), (40.6, 27.6), (40.4, 24.6),
                (38.6, 22.6), (36.2, 22.2)]
        if side > 0:
            claw = mirror_cr(claw)

        def top(x, y, s=side, ct=CLAW_TOP):
            # sloping down the screen to the housing's rim
            t = min(1.0, max(0.0, (Y(19.0) - y) / 8.6))
            return ct - 1.1 * t
        parts.append(block("claw_%d" % side, claw, 5.0, top, m["steel"], 0.45))
        knuckle = k.ellipsoid("knuckle_%d" % side, (X(C(39.0)), Y(20.6), CLAW_TOP - 0.1), (1.7, 1.4, 1.1),
                              m["bright"], 18, 8)
        k.smooth(knuckle, 70)
        parts.append(knuckle)
    return parts


# The dome: its housing (a frame with a raised rim round the glass, its ears under the claws), two glass lobes, the
# spine between them with its ladder, the stack at its foot, the hose round its lower right.
HOUSING_LEFT = [(48.5, 27.4), (44.0, 27.2), (41.8, 26.4), (38.0, 23.2), (36.4, 21.6), (34.0, 21.0), (30.8, 21.4),
                (29.2, 23.4), (29.0, 30.0), (29.6, 37.6), (31.4, 43.0), (35.0, 46.6), (41.2, 48.6), (48.5, 49.2)]
LOBE = ((43.2, 37.3), (9.4, 9.15, 5.0), -1.4)    # the left lobe: middle (column, row), radii, its middle's height (over
#                                                  the housing's top)
LOBE_HOT = (-3.4, 2.4)                           # the lobes' hottest point, from their middle (x, y)
SPINE = (46.8, 50.2, 27.6, 40.6, 3.3)            # columns, rows, top (over the housing's)
RUNGS = [30.4, 32.4, 34.4, 36.4]
STACK = (45.4, 51.6, 38.6, 46.8, 3.1)            # the stack's middle block: columns, rows, top (over the housing's)
POSTS = (42.4, 45.2, 41.0, 46.6, 1.7)            # its side posts (the left one; the right mirrored)
HOSE = [(63.8, 41.4, -0.3), (64.0, 44.6, -0.6), (62.8, 48.0, -0.9), (60.0, 50.6, -1.1), (56.6, 51.9, -1.2)]   # (z
#                                                  over the housing's top)


def housing_outline():
    left = HOUSING_LEFT
    full = left[:-1] + [(MC(c), r) for c, r in reversed(left[1:])]
    pts = mk.chaikin([P(c, r) for c, r in full], 2, closed=True)
    return pts


def dome(m, hull, look, lv):
    parts = []
    outline = housing_outline()
    Z_HOUSING = lv["housing"]

    def h_height(x, y, d):
        zb = fnum(hull.z(x, y)) + RIB_H + 0.3
        return zb + (Z_HOUSING - zb) * fnum(rounded(d / 1.6))
    housing = relief("housing", [outline], h_height, {"top": m["frame"], "side": m["frame"]}, bottom=0.6,
                     spacing=0.55, band=2.2, smooth_angle=50.0)
    parts.append(housing)
    (c, r), radii, cz = LOBE
    cz += Z_HOUSING
    for side, cc in ((-1, c), (1, MC(c))):
        lobe = k.ellipsoid("glass_%d" % side, (X(cc), Y(r), cz), radii, m["glass_bands"][0][1], 36, 20)
        hx, hy = X(cc) + (LOBE_HOT[0] if side < 0 else -LOBE_HOT[0]), Y(r) + LOBE_HOT[1]

        def heat(p, hx=hx, hy=hy):
            u = math.hypot((p.x - hx) / (1.25 * radii[0]), (p.y - hy) / (1.25 * radii[1]))
            return 1.0 - u
        if len(m["glass_bands"]) > 1:
            band_split(lobe, [heat(v.co) for v in lobe.data.vertices], m["glass_bands"])
        k.smooth(lobe, 80)
        parts.append(lobe)
    c0, c1, r0, r1, top = SPINE
    top += Z_HOUSING
    spine = block("spine", [(c0, r1), (c1, r1), (c1, r0), (c0, r0)], 7.6, top, m["steel"], 0.5, 3)
    parts.append(spine)
    for i, rr in enumerate(RUNGS):
        rung = block("rung_%d" % i, [(c0 + 0.3, rr + 0.45), (c1 - 0.3, rr + 0.45), (c1 - 0.3, rr - 0.45),
                                     (c0 + 0.3, rr - 0.45)], top - 0.5, top + 0.45, m["bright"], 0.25, 2)
        parts.append(rung)
    c0, c1, r0, r1, top = STACK
    top += Z_HOUSING
    parts.append(block("stack", [(c0, r1), (c1, r1), (c1, r0), (c0, r0)], 8.0, top, m["steel"], 0.55, 3))
    lip = block("stack_lip", [(c0 - 0.3, r0 + 1.6), (c1 + 0.3, r0 + 1.6), (c1 + 0.3, r0), (c0 - 0.3, r0)],
                top - 0.6, top + 0.35, m["bright"], 0.3, 2)
    parts.append(lip)
    c0, c1, r0, r1, top = POSTS
    top += Z_HOUSING
    for side, (a, b) in ((-1, (c0, c1)), (1, (MC(c1), MC(c0)))):
        parts.append(block("post_%d" % side, [(a, r1), (b, r1), (b, r0), (a, r0)], 8.0, top, m["steel"], 0.45, 2))
    hose = mk.smooth_tube("hose", [(X(c), Y(r), Z_HOUSING + z, 1.25) for c, r, z in HOSE], m["hose"], 16, 2)
    k.smooth(hose, 50)
    parts.append(hose)
    return parts


# The neck under the dome (two wedges like a bow tie, columns 40-57 of rows 47-56), the barrel down from it (columns
# 46-51 of rows 55-71) into the eye's ring, the eye's housing (columns 37-60 of rows 66-84) with the ring round the eye.
NECK_LEFT = [(40.4, 47.4), (48.2, 47.4), (48.2, 55.8), (44.0, 55.8), (40.4, 51.8)]
NECK_Z = (0.0, 1.6)               # its outer and inner top (over its level)
BARREL = (48.5, 0.0)              # its axis: column, height (over its level)
EYE_BOX = (36.6, 60.2, 66.4, 83.8, 3.2)          # the eye's housing: columns, rows, corner radius
EYE = ((48.8, 75.8), 5.3, 1.15)                  # the ring: middle, radius, tube
SOCKET_DEPTH = 1.9                # the socket's floor under the eye's housing's top


def neck(m, hull, lv):
    parts = []
    for side in (-1, 1):
        pts = NECK_LEFT if side < 0 else mirror_cr(NECK_LEFT)
        zo, zi = (lv["neck"] + z for z in NECK_Z)
        x_out, x_in = X(40.4 if side < 0 else MC(40.4)), X(48.2 if side < 0 else MC(48.2))

        def top(x, y, xo=x_out, xi=x_in):
            t = (x - xo) / (xi - xo)
            return zo + (zi - zo) * min(1.0, max(0.0, t)) - 0.35 * min(1.0, max(0.0, (Y(47.4) - y) / 8.4))
        parts.append(block("neck_%d" % side, pts, 5.5, top, m["steel"], 0.45, 2))
    c, cz = BARREL
    cz += lv["barrel"]
    profile = [(54.8, 0.6), (55.0, 2.45), (56.8, 2.45), (57.0, 2.05), (63.4, 2.05), (63.6, 2.4), (65.2, 2.4),
               (65.4, 1.95), (70.8, 1.95), (71.2, 1.0)]
    barrel = lathe_y("barrel", profile, X(c), cz, m["steel"], 24)
    mk.paint(barrel, lambda co, n: m["bright"] if (55.0 <= 56.0 - co.y <= 56.8) or (63.6 <= 56.0 - co.y <= 65.2)
             else None)
    parts.append(barrel)
    return parts


def rounded_rect(c0, c1, r0, r1, rad, n=6):
    pts = []
    corners = [((c1 - rad, r1 - rad), 0), ((c1 - rad, r0 + rad), 1), ((c0 + rad, r0 + rad), 2), ((c0 + rad, r1 - rad), 3)]
    for (cc, rr), q in corners:
        for i in range(n + 1):
            a = math.radians(-90 + 90 * q + 90 * i / n)
            # rows grow down the screen: a corner's arc in (column, row)
            pts.append((cc + rad * math.cos(a), rr - rad * math.sin(a)))
    return pts


def eye(m, hull, look, lv):
    parts = []
    Z_EYE_BOX = lv["eyebox"]
    SOCKET_Z = Z_EYE_BOX - SOCKET_DEPTH
    c0, c1, r0, r1, rad = EYE_BOX
    outer = [P(c, r) for c, r in rounded_rect(c0, c1, r0, r1, rad)]
    (ec, er), R, tube_r = EYE
    hole = [(X(ec) + (R - 0.2) * math.cos(2 * math.pi * i / 40), Y(er) + (R - 0.2) * math.sin(2 * math.pi * i / 40))
            for i in range(40)]

    def b_height(x, y, d):
        zb = fnum(hull.z(x, y)) + RIB_H + 0.3
        return zb + (Z_EYE_BOX - zb) * fnum(rounded(d / 1.3))
    key = "socket"
    box = relief("eyebox", [outer, hole], b_height, {"top": m[key], "side": m[key]}, bottom=0.6, spacing=0.45,
                 band=2.4, smooth_angle=45.0)
    parts.append(box)
    floor = mk.lathe("socket_floor", [(0.01, SOCKET_Z - 0.6), (R, SOCKET_Z - 0.6), (R, SOCKET_Z), (0.01, SOCKET_Z)],
                     (X(ec), Y(er)), m["black"], 40)
    parts.append(floor)
    ring = []
    for i in range(48):
        a = 2 * math.pi * i / 48
        ring.append((X(ec) + R * math.cos(a), Y(er) + R * math.sin(a), Z_EYE_BOX - 0.1))
    hoop = mk.tube("eye_ring", ring + ring[:1], tube_r, m["steel"], 14, cap=False)
    k.smooth(hoop, 60)
    parts.append(hoop)
    if look == "eye231":
        gem = mk.lathe("gem", [(0.01, SOCKET_Z), (3.7, SOCKET_Z + 0.2), (4.0, SOCKET_Z + 1.0), (2.5, SOCKET_Z + 2.6),
                               (0.01, SOCKET_Z + 2.9)], (X(ec) - 0.3, Y(er) + 0.2), m["gem_bands"][0][1], 8)
        zs = [v.co.z for v in gem.data.vertices]
        band_split(gem, [(z - SOCKET_Z) / 2.9 for z in zs], m["gem_bands"])
        k.smooth(gem, 20)
        parts.append(gem)
    else:
        pupil = mk.dome("pupil", (X(ec), Y(er)), (R - 0.5, R - 0.5, 1.4), SOCKET_Z, m["pupil"], 40, 8)
        parts.append(pupil)
    return parts


# The shoulder plates (columns 6-21 of rows 36-66, and their mirror images): an upper tile with its outer top corner
# rounded, a lit ridge across under it (row 44), the middle tile, the lower tile with its outer corner cut away; their
# tops sloping down to the outside (they wrap round the shell's shoulders).
PLATE_A = [(6.4, 39.4), (7.0, 37.6), (8.6, 36.5), (19.8, 36.4), (21.2, 37.8), (21.2, 44.3), (6.4, 44.3)]
PLATE_B = [(6.4, 45.0), (21.2, 45.0), (21.2, 55.4), (20.0, 56.4), (8.4, 56.4), (6.4, 54.4)]
PLATE_C = [(9.8, 57.0), (21.0, 57.0), (20.6, 65.6), (19.4, 66.0), (13.4, 66.0), (10.0, 61.2)]
PLATE_Z = (0.5, 1.4)              # their outer and inner tops over the ribs under their outer and inner edges


def plates(m, hull, lv):
    """The shoulder plates: bevelled blocks, their tops sloping down to the outside, the ridge between the upper two."""
    parts = []
    for side in (-1, 1):
        def C(c):
            return c if side < 0 else MC(c)
        xo, xi = X(C(6.4)), X(C(21.2))
        zo, zi = lv["plate_out"] + PLATE_Z[0], lv["plate_in"] + PLATE_Z[1]

        def slope(x, y, xo=xo, xi=xi, drop=0.0, along=None, zo=zo, zi=zi):
            t = min(1.0, max(0.0, (x - xo) / (xi - xo)))
            z = zo + (zi - zo) * t
            if along is not None:
                z -= along * min(1.0, max(0.0, (Y(57.0) - y) / 9.0)) * (1.0 - 0.5 * t)
            return z - drop
        for name, pts, drop, along in (("plate_a", PLATE_A, 0.0, None), ("plate_b", PLATE_B, 0.3, None),
                                       ("plate_c", PLATE_C, 0.25, 1.6)):
            pp = pts if side < 0 else mirror_cr(pts)
            parts.append(block("%s_%d" % (name, side), pp, 4.0,
                               lambda x, y, d=drop, a=along: slope(x, y, drop=d, along=a), m["steel"], 0.6, 3))
        ridge = mk.tube("ridge_%d" % side, [(X(C(7.2)), Y(44.65), zo + 0.05), (X(C(20.8)), Y(44.65), zi - 0.05)],
                        0.58, m["bright"], 12)
        k.smooth(ridge, 50)
        parts.append(ridge)
    return parts


def occluders():
    """The plans of the big parts that hide the carapace under them (no ribs are built there)."""
    out = [housing_outline()]
    c0, c1, r0, r1, rad = EYE_BOX
    out.append([P(c, r) for c, r in rounded_rect(c0, c1, r0, r1, rad)])
    for pts in (PLATE_A, PLATE_B, PLATE_C, NECK_LEFT):
        out.append([P(c, r) for c, r in pts])
        out.append([P(c, r) for c, r in mirror_cr(pts)])
    return out


def levels(hull):
    """The parts' heights over the ribs where they stand (the highest rib top under them, and a little more)."""
    def top_at(c, r):
        return fnum(hull.z(X(c), Y(r))) + RIB_H
    lv = {
        "arm": max(top_at(c, 20.2) for c in (16, 22, 28, 34)) + 1.2,
        "housing": max(top_at(c, r) for c in (34, 40, 48.5, 57, 63) for r in (24, 30, 37, 44)) + 0.8,
        "neck": max(top_at(c, r) for c in (41, 45, 48.5) for r in (48, 52, 55)) + 0.7,
        "barrel": max(top_at(48.5, r) for r in (56, 60, 64, 68)) + 0.9,
        "eyebox": max(top_at(c, r) for c in (38, 44, 48.5, 53, 59) for r in (67, 72, 77, 83)) + 1.2,
        "plate_out": max(top_at(c, r) for c in (6.4, 8.0, 10.0) for r in (37, 45, 55, 61)),
        "plate_in": max(top_at(c, r) for c in (18.0, 21.2) for r in (37, 45, 55, 65)),
    }
    return lv


def whole(look):
    m = materials(look)
    hull = Hull()
    parts = carapace(m, hull, occluders())
    lv = levels(hull)
    parts += guns(m, hull) + arms(m, hull, lv) + dome(m, hull, look, lv) + neck(m, hull, lv) + eye(m, hull, look, lv)
    parts += plates(m, hull, lv)
    for obj in parts:
        mk.apply(obj)
    return parts, m


# --- Pieces -------------------------------------------------------------------------------------------------------------
# The fifteen sprites as the levels lay them out (sprite, its top left pixel in the picture); the bottom row 12 in.
LAYOUT = [(153, 0, 0), (155, 24, 0), (157, 48, 0), (159, 72, 0), (191, 0, 28), (193, 24, 28), (195, 48, 28),
          (197, 72, 28), (229, 0, 56), (241, 24, 56), (243, 48, 56), (235, 72, 56), (267, 12, 84), (269, 36, 84),
          (271, 60, 84)]
DOME_FRAMES = [(161, 163, "dome161"), (199, 201, "dome199"), (237, 239, "dome237"), (275, 277, "dome275"),
               (165, 167, "dome165"), (203, 205, "dome203")]      # (193's frame, 195's frame, look)
EYE_FRAMES = [(231, 233, "eye231")]                               # (241's, 243's)


def piece(name, sprite, c0, r0):
    x0, x1, y0, y1 = X(c0), X(c0 + 24), Y(r0 + 28), Y(r0)
    if c0 == 0 or (r0 == 84 and c0 == 12):
        x0 -= 10.0
    if c0 + 24 >= 96 or (r0 == 84 and c0 == 60):
        x1 += 10.0
    if r0 == 0:
        y1 += 10.0
    if r0 == 84:
        y0 -= 10.0
    return (name, sprite, (x0, x1, y0, y1), (X(c0 + 12), Y(r0 + 14)))


def pieces(look):
    place = {s: (c, r) for s, c, r in LAYOUT}
    if look == "idle":
        return [piece("green_shell_%d" % s, s, c, r) for s, c, r in LAYOUT]
    for f193, f195, lk in DOME_FRAMES:
        if lk == look:
            return [piece("green_shell_%d" % f193, f193, *place[193]), piece("green_shell_%d" % f195, f195, *place[195])]
    for f241, f243, lk in EYE_FRAMES:
        if lk == look:
            return [piece("green_shell_%d" % f241, f241, *place[241]), piece("green_shell_%d" % f243, f243, *place[243])]
    return []


LOOKS = ["idle"] + [lk for _, _, lk in DOME_FRAMES] + [lk for _, _, lk in EYE_FRAMES]


def cap_key(m):
    def cap_of(src):
        n = src.name
        if n.startswith(("hull", "rib", "lamp", "conduit", "foot")):
            return m["cap_green"]
        return m["cap_grey"]
    return cap_of


def build():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    sheet = None
    if "check" in options:
        sheets = options["check"]
        sheet = os.path.join(sheets, "enemy_J.png") if os.path.isdir(sheets) else sheets
    results = {}
    for look in LOOKS:
        todo = pieces(look)
        if only is not None and not any(p[0] in only for p in todo):
            continue
        k.reset()
        parts, m = whole(look)
        triangulate(parts)
        bpy.context.view_layer.update()
        bpy.context.scene.view_settings.view_transform = "Standard"
        low, high = mk.bounds(parts)
        print("== whole %s: %d triangles, x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (
            look, mk.triangles(parts), low.x, high.x, low.y, high.y, low.z, high.z))
        if "whole" in options:
            mk.export(parts, options["whole"] + look + ".glb")
        results.update(fw.export_pieces(parts, todo, cap_key(m), options, sheet, "J", only))
    if sheet:
        for name, score in results.items():
            if score is not None:
                print("overlap %-22s %.3f" % (name, score))


if __name__ == "__main__":
    build()
