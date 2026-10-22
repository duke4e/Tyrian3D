"""The skull chest of GAUNTLET and MACES (sheet A: eight 2x2 sprites, 153 155 157 159 above 191 193 195 197, laid out as
one 96 x 56 picture), polished (2026-10-22, round 36; it replaces wave3_q_mace.py, an inflated outline painted by hand
with block straps and a tube handle, 15 pixels tall).

Where it appears (episode 3; event 52: one-frame ground pieces, armour 255): GAUNTLET t404 at x 76 100 124 148, y -78
(the top row) and -50 (the bottom row), link 64, dragged along by the mace's chain (event 19 at t461 sets it moving with
the chain's rings, links 61-63); t5284-5286 again at x 126 ... 198 (link 84); MACES t466, t1272, t2306 and t2728 (link
74), the same four by two. No other enemy shows these sprites; none is another sprite's pixels mirrored, turned or in
other ramps; there are no frames and no damaged looks; no upscales exist (built from the originals).

As the sprites draw it (the picture's columns and rows; lit from the upper left): a wooden chest (ramp 1's browns;
columns 13-84 of rows 17-54) seen from above its lid: two end planks (columns 13-24 and 72-84), their boards parted by
dark seams across them (rows 26, 33, 41, 47); two steel straps over the lid (ramp 0's light greys; columns 25-34 and
62-71), wrapping its rear and front edges (rows 17 and 54-55); between them the lid's middle with a sunken panel
(columns 39-57 of rows 26-47: its upper wall in shadow, its lower one lit) and a skull carved in it (dark browns and
black, columns 41-55 of rows 29-46); a steel handle (an arch from the lid's rear edge up the screen to row 4, its
knuckles at columns 37-42 and 55-60 of rows 15-17), folded back behind the chest.

Built for the game's camera as polish_green_shell.py is (one heightfield in the picture's plane, sheared along the
camera's line of sight, y - z tan 20, on polish_gyges_wall.Plate's grid, 0.5 pixel apart, whose lines are the pieces'
edges, so each piece is the cells of its sprite's box): the chest a box LID high with its edges rounded over FALL, its
walls down to FOOT (4 under the layer: it stands on the ground, as the mace's anchor's do, without height=, so it keeps
the chain's height); the straps' pixels raised STRAP over it; the panel sunk PANEL_DEPTH, its walls bevelled; the skull
and the seams carved CARVE deep by the sprite's darkness; the handle a round bar along the sprite's arch at its axis
HANDLE_Z (where it stands out behind the chest a plate of its own with its underside: a solid bar), its knuckles knobs
on the lid's rear edge. Painted by the sprite's shades (polish_green_shell's Paint: each face the ink of the pixels
under it, wood or steel, in that ink's shade there, blurred, lifted and lighter where the game's sun lights it less),
the black lines dark, the sides wood (0x14) and steel (0x07). Heights: z -4 (its foot) to 10.7 (the handle's bar; its
knuckles 10.2, the lid 8.6, the straps 9.3). Deterministic (no random numbers; the faces' centres and normals rounded
before they pick their shades).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera. The whole's origin
is the picture's middle (its pixel edge 48, 28): column c's left edge is x = c - 48, row r's top edge y = 28 - r; a
piece whose sprite's top left pixel is (c0, r0) has its origin at (c0 + 12 - 48, 14 - r0) (models.cfg origin).

models.cfg: the model and sprite lines of skull_chest_t1 ... _b4 stay as they are (origin, yaw=0).

Replaces wave3_q_mace.py (all of it: the chest is all it builds; nothing imports it) and wave3_q_art.py's CHEST (read
only by it, through wave3_q_kit's art).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the outline as the camera sees
it against the sprites' pixels, the whole and each piece), --preview <prefix> (each piece's top and 3/4 views), --only
<name,...> (pieces to export).
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_gyges_wall as gw  # noqa: E402  (Plate, the shear to the camera, the faces' light)
from polish_green_shell import edt, limit_materials, seg_dist  # noqa: E402

W, H = 96, 56                     # the whole picture; its origin is its middle, the pixel edge (48, 28)
LEFT, TOP = -48.0, 28.0
S = 4                             # the fine grid of the fields: S cells a pixel


def px(c):
    """A pixel edge's column in the picture's plane."""
    return c - 48.0


def py(r):
    return 28.0 - r


def parse_picture(text, first_row=4):
    a = -np.ones((H, W), int)
    for i, line in enumerate(text.split()):
        for c in range(W):
            t = line[2 * c:2 * c + 2]
            if t != "..":
                a[first_row + i, c] = int(t, 16)
    return a


def up(m):
    return np.repeat(np.repeat(m, S, 0), S, 1)


class Field:
    """Values on the fine grid (S cells a pixel), sampled bilinearly between its cells' middles."""

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


def rounded(depth, height, fall):
    """A slab's top: height inside, rounded over `fall` at its edge (depth: how far inside)."""
    return height * np.sqrt(1.0 - (1.0 - np.clip(depth / fall, 0.0, 1.0)) ** 2)


def box_mask(c0, c1, r0, r1):
    m = np.zeros((H, W), bool)
    m[r0:r1, c0:c1] = True
    return m


# --- The chest's heights ------------------------------------------------------------------------------------------------

LID = 8.6                         # the lid's top (the chest's underside 4 under the layer: it stands on the ground)
FOOT = -4.0
FALL = 1.3                        # the lid's edges rounded over this
STRAPS = [(25, 35), (62, 72)]     # the steel straps' columns (their pixels rise STRAP over the lid)
STRAP = 0.7
PANEL = (39, 58, 26, 48)          # the sunken panel: columns, rows (its walls bevelled over BEVEL)
PANEL_DEPTH, BEVEL = 0.9, 0.8
CARVE = 0.55                      # the skull and the planks' seams carved this deep where the sprite draws them darkest
SEAMS = [(13, 25), (72, 85)]      # the end planks (their dark rows are the seams between their boards)
HANDLE = [(40.4, 16.4), (40.3, 13.0), (40.6, 10.2), (41.4, 8.5), (42.8, 7.0), (45.0, 5.9), (48.5, 5.5), (52.0, 6.0),
          (54.0, 7.3), (55.3, 8.8), (56.1, 10.5), (56.8, 13.0), (56.8, 16.4)]   # the handle's bar: its path (pixel
HANDLE_R, HANDLE_Z = 1.9, LID + 0.2                                             # edges), radius, its axis's height
HINGES = [(39.8, 16.3), (57.3, 16.3)]   # the knuckles it turns in, on the lid's rear edge


class Chest:
    """The chest's heightfield in the picture's plane, from the sprites' pixels."""

    def __init__(self, a):
        self.a = a
        ramp = np.where(a >= 0, a >> 4, -1)
        shade = np.where(a >= 0, a & 15, 0)
        rows = np.arange(H)[:, None] + np.zeros((1, W), int)
        cols = np.arange(W)[None, :] + np.zeros((H, 1), int)
        body = (a >= 0) & (rows >= 17)
        self.body = body
        fine = gw.blur(up(body.astype(float)), 0.5 * S) > 0.5
        e = edt(fine, 1.0 / S)
        z = rounded(e, LID, FALL)
        straps = np.zeros((H, W), bool)
        for c0, c1 in STRAPS:
            straps |= box_mask(c0, c1, 17, 56)
        straps &= body & (ramp == 0) & (a >= 2)
        sm = gw.blur(up(straps.astype(float)), 0.45 * S) > 0.5
        z = np.where(sm, z + rounded(edt(sm, 1.0 / S), STRAP, 0.5), z)
        c0, c1, r0, r1 = PANEL
        pm = up(box_mask(c0, c1, r0, r1))
        z = z - PANEL_DEPTH * np.clip(edt(pm, 1.0 / S) / BEVEL, 0.0, 1.0)
        # The carving: the skull's dark browns and black in the panel, the seams' dark rows across the end planks.
        dark = np.clip((6.0 - shade) / 6.0, 0.0, 1.0) * ((ramp == 1) | (a == 1))
        carve = box_mask(c0 + 1, c1 - 1, r0 + 2, r1 - 1) & (dark > 0)
        for s0, s1 in SEAMS:
            seam = box_mask(s0 + 1, s1 - 1, 19, 53) & (ramp == 1) & (shade <= 7)
            carve |= seam
        cf = gw.blur(up(np.where(carve, dark + 0.35, 0.0)), 0.45 * S)
        z = z - CARVE * np.clip(cf, 0.0, 1.0) * np.clip(e / 1.5, 0.0, 1.0)
        self.field = Field(np.where(fine, z, FOOT))
        self.inside = Field(fine.astype(float))
        self.handle_mask = (a >= 0) & (rows < 17)

    def cells(self, cx, cy):
        return self.inside(cx, cy) > 0.5

    def handle_cells(self, cx, cy):
        return (self.inside(cx, cy) <= 0.5) & (self.handle(cx, cy) > FOOT)

    def handle(self, Xa, Ya):
        pts = [(px(c), py(r)) for c, r in HANDLE]
        d = seg_dist(Xa, Ya, pts)
        z = HANDLE_Z + np.sqrt(np.clip(HANDLE_R ** 2 - d * d, 0.0, None))
        out = np.where(d < HANDLE_R, z, FOOT)
        for c, r in HINGES:
            u = ((Xa - px(c)) / 2.6) ** 2 + ((Ya - py(r)) / 1.6) ** 2
            out = np.maximum(out, np.where(u < 1.0, LID + 0.2 + 1.4 * np.sqrt(np.clip(1.0 - u, 0.0, None)), FOOT))
        return out

    def heights(self, Xa, Ya):
        Xa, Ya = np.asarray(Xa, float), np.asarray(Ya, float)
        return np.maximum(self.field(Xa, Ya), self.handle(Xa, Ya))

    def bar_top(self, Xa, Ya):
        """The bar's top where it stands out behind the chest (its rim at its axis' height, as its underside's)."""
        Xa, Ya = np.asarray(Xa, float), np.asarray(Ya, float)
        pts = [(px(c), py(r)) for c, r in HANDLE]
        d = seg_dist(Xa, Ya, pts)
        return HANDLE_Z + np.sqrt(np.clip(HANDLE_R ** 2 - d * d, 0.0, None))

    def under_handle(self, Xa, Ya):
        """The bar's underside where it stands out behind the chest (a solid bar, not a wall down to the ground)."""
        Xa, Ya = np.asarray(Xa, float), np.asarray(Ya, float)
        pts = [(px(c), py(r)) for c, r in HANDLE]
        d = seg_dist(Xa, Ya, pts)
        return HANDLE_Z - np.sqrt(np.clip(HANDLE_R ** 2 - d * d, 0.0, None))


# --- Painting (polish_green_shell's way) --------------------------------------------------------------------------------

INKS = {   # shades, (metallic, roughness), lift, contrast (about shade 7), comp
    "wood": ([0x12, 0x14, 0x16, 0x18, 0x1a, 0x1c, 0x1e], (0.0, 0.72), 0.6, 1.0, 1.6),
    "steel": ([0x05, 0x07, 0x09, 0x0b, 0x0d, 0x0f], (0.55, 0.3), 0.6, 1.0, 2.0),
}
DARK = 0x01
WALL = ("wood", 0x14)             # the chest's sides (seen only off the screen's middle)
LIT_MEAN = 0.72


def pal(prefix, index, metallic, roughness):
    return k.material("%s_%x" % (prefix, index), palette=index, metallic=metallic, roughness=roughness)


def mat_of(key):
    if key == "dark":
        return pal("chest_dark", 0x11, 0.0, 0.8)
    shades, (met, rough), _, _, _ = INKS[key[0]]
    return pal("chest_" + key[0], key[1], met, rough)


def ink_mask(name, a):
    ramp = np.where(a >= 0, a >> 4, -1)
    return (ramp == 1) if name == "wood" else (ramp == 0) & (a >= 2)


class Paint:
    def __init__(self, a):
        shade = np.where(a >= 0, a & 15, 0).astype(float)
        self.inks = []
        for name, (shades, _, lift, contrast, comp) in INKS.items():
            mask = ink_mask(name, a)
            soft = gw.blur(gw.fill(shade, mask), 0.5)
            self.inks.append((name, shades, gw.blur(mask.astype(float), 0.6), 7.0 + contrast * (soft - 7.0), lift,
                              comp))
        self.dark = gw.blur((a == DARK).astype(float), 0.55)

    def sample(self, field, Xa, Ya):
        fc = np.clip(np.asarray(Xa, float) - LEFT - 0.5, 0.0, W - 1.0)
        fr = np.clip(TOP - np.asarray(Ya, float) - 0.5, 0.0, H - 1.0)
        c0 = np.minimum(np.floor(fc).astype(int), W - 2)
        r0 = np.minimum(np.floor(fr).astype(int), H - 2)
        tc, tr = fc - c0, fr - r0
        return ((field[r0, c0] * (1 - tc) + field[r0, c0 + 1] * tc) * (1 - tr) +
                (field[r0 + 1, c0] * (1 - tc) + field[r0 + 1, c0 + 1] * tc) * tr)

    def keys(self, Xa, Ya, normals, on_handle):
        lit_by = gw.sun_on(normals)
        weights = np.stack([self.sample(ink[2], Xa, Ya) for ink in self.inks], 0)
        which = weights.argmax(0)
        dark = self.sample(self.dark, Xa, Ya)
        per = [gw.nearest(self.sample(soft, Xa, Ya) + lift + comp * (LIT_MEAN - lit_by), shades)
               for name, shades, _, soft, lift, comp in self.inks]
        out = []
        for i in range(len(Xa)):
            w = 1 if on_handle[i] else which[i]
            if dark[i] > 0.6 and weights[w, i] < 0.35:
                out.append("dark")
            else:
                out.append((self.inks[w][0], int(per[w][i])))
        return out


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


# --- The pieces ---------------------------------------------------------------------------------------------------------

LAYOUT = [("skull_chest_t1", 153, 0, 0), ("skull_chest_t2", 155, 24, 0), ("skull_chest_t3", 157, 48, 0),
          ("skull_chest_t4", 159, 72, 0), ("skull_chest_b1", 191, 0, 28), ("skull_chest_b2", 193, 24, 28),
          ("skull_chest_b3", 195, 48, 28), ("skull_chest_b4", 197, 72, 28)]


def box_of(c0, r0):
    return (px(c0), px(c0 + 24), py(r0 + 28), py(r0))


def check(chest, sheet):
    covered = gw.own_coverage(lambda Xa, Ya: chest.cells(Xa, Ya) | chest.handle_cells(Xa, Ya), W, H, LEFT, TOP)
    mask = [[False] * W for _ in range(H)]
    for _, sprite, c0, r0 in LAYOUT:
        for r, line in enumerate(k.sprite_mask(sheet, sprite)):
            for c, v in enumerate(line):
                if v:
                    mask[r0 + r][c0 + c] = True
    mk.compare("the skull chest (its 96 x 56 picture)", covered, mask)
    for name, sprite, c0, r0 in LAYOUT:
        sub_c = [row[c0:c0 + 24] for row in covered[r0:r0 + 28]]
        sub_m = [row[c0:c0 + 24] for row in mask[r0:r0 + 28]]
        both = sum(p and q for rp, rq in zip(sub_c, sub_m) for p, q in zip(rp, rq))
        either = sum(p or q for rp, rq in zip(sub_c, sub_m) for p, q in zip(rp, rq))
        print("silhouette overlap %s (a %d): %.3f" % (name, sprite, both / max(1, either)))


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    a = parse_picture(PICTURE)
    chest = Chest(a)
    if "check" in options and only is None:
        sheets = options["check"]
        check(chest, os.path.join(sheets, "enemy_A.png") if os.path.isdir(sheets) else sheets)
    # The chest: its walls down to the ground under it (no bottom: never seen); the handle's bar behind it a plate of
    # its own, with its underside.
    plate = gw.Plate((-48.0, 48.0, -28.0, 28.0), chest.heights, base=lambda Xa, Ya: np.full(np.shape(Xa), FOOT),
                     cells=chest.cells, bottom=False)
    bar = gw.Plate((-48.0, 48.0, -28.0, 28.0), chest.bar_top, base=chest.under_handle, cells=chest.handle_cells)
    paint = Paint(a)
    for name, sprite, c0, r0 in LAYOUT:
        if only is not None and name not in only:
            continue
        k.reset()
        box = box_of(c0, r0)
        parts = []
        for src, is_bar in ((plate, False), (bar, True)):
            obj, kinds, _ = src.mesh(name + ("_bar" if is_bar else ""), gw.piece_owner(box))
            if obj is None:
                continue
            centres, normals = gw.face_data(obj)
            centres, normals = np.round(centres, 4), np.round(normals, 4)
            on_handle = is_bar | (chest.handle(centres[:, 0], centres[:, 1]) >=
                                  chest.field(centres[:, 0], centres[:, 1]) - 0.05)
            top = paint.keys(centres[:, 0], centres[:, 1], normals, on_handle)
            keys = [top[i] if kinds[i] == 0 else ("steel", 0x07) if on_handle[i] else WALL for i in range(len(kinds))]
            assign(obj, keys)
            parts.append(obj)
        gw.finish_piece(name, parts, box, out, options)


# --- The sprites' pixels ----------------------------------------------------------------------------------------------
# Each pixel its palette index as two hex digits ('..' none), rows top to bottom (the picture's empty rows left out).

PICTURE = """
........................................................................................0101010101010101........................................................................................
....................................................................................010207090808080807050101....................................................................................
..................................................................................01070a0907050505050507080501..................................................................................
................................................................................01080d08030101010101010507080501................................................................................
..............................................................................01070c050101............010106080501..............................................................................
............................................................................01040c0801....................0105080401............................................................................
............................................................................01090801........................01070601............................................................................
..........................................................................0107090201........................0104070401..........................................................................
..........................................................................01080701............................01070501..........................................................................
..........................................................................01070701............................01080601..........................................................................
..........................................................................01040301............................01030101..........................................................................
........................................................................020b0e0a0501........................01090e0a0501........................................................................
........................................................................01070b050601........................01060b050601........................................................................
................................................0101010101010101010101..01060b060301........................01060b060301....0101010101010101010101..............................................
........................010110010101010101010101010b0908080808080808010102060707040101....................010105060603010101010b09080808080808080101010101010101010101010101....................
........................011a1b1a1a1a1a1a1a1a1a1a010f0c0c0c0c0c0b0b0901151717151312111001010101010101010101011a1a1a1a1a1a1a1a010f0c0c0c0c0c0b0b09011517191a1a1a1a1a1a1a1a1801....................
........................011b1f1f1d1d1d1d1d1d1d1d100f0809080808090a090115171a1814131211141516161616151515151a1c1b1d1d1d1c1b1b100f0809080808090a0901171a1b1e1e1d1d1d1d1d1a1701....................
........................011a1e1b1a1a1a1a1a1a1a1a010f090a080808080809011516181b16131312141414151515151515161a1b1b1b1b1919191a010f090a0808080808090115161819191a1a1a1a1a161501....................
........................011a1c1a1a1a1a1a1a1a1a1a010f0a0a08080808080a011517191a1c161514161717171717171717191a1c1c1d1c1a1a1a19010f0a0a08080808080a0114161819191919191919161401....................
........................01191b191a1a1a1a1a1a1a1a01090706060504050406011416191a1a1b1816171818181817171717181b1b1d1b19191a1a1a010907060605040504060115171a1b1b1b1b1a1816130101....................
........................01191c1a1919191919191919010e0d0d0d0a0a0b0b0f021416181a1b1b1e1b1b1b1c1d1d1e1e1e1e1d1c1d1b1a1a1b1b1b1a010e0d0d0d0a0a0b0b0f0214161a1c1c1c1c1d1f1e1a1710....................
........................01191b19191a1a1a1a1a1a1a010d0b0b0a090808080c101517191a1a19191919191919191919191919191a191b1b1b1a1919010d0b0b0a090808080c1016181a1b1b1b1b1b1b1b181701....................
........................01161717181818191a191919010d0b0b0a090808080d011416181812121212121212121212121212121314141312191a1a1a010d0b0b0a090808080d011416181a1a1a1a1a1a1a181501....................
........................011b1f1d1c1b1a1a1a1a1a1a010c0b0b0a090908080d01151719191318181818181818181819191a1a1a181818141c1a1a1a010c0b0b0a090908080d011517191a1919191a1a1a181401....................
........................011a1d1a191a1a1a1a1a1a1a010c0b0b0a0a0909090d0114161818121715161616161616171717161617171717131d1b1b1b010c0b0b0a0a0909090d01141517191a1a1a191919171301....................
........................01191c191a1919191919191a010c0b0b0b0a0909090d0115171615111818181710101001010101010116161616121c1a1a1a010c0b0b0b0a0909090d011317191a1a1a1a1a1a1a181401....................
........................01181c1a1a1a1a1a1919191a010c0b0b0b0a0a09090d011416181a141715150101111111111111111110151516131d1b1b1b010c0b0b0b0a0a09090d0112151719191919191919171301....................
........................01131818191a1a1a1a191a1a010c0b0b0b0b0a0a090d0115171919131816171012121313131313131313191716121c1a1a1a010c0b0b0b0b0a0a090d01121719191a191a1a191a171401....................
........................01171e1c1b1b1a1a1a191a19010c0b0b0b0b0b0a090d0115171919131816011113131312121212121212111616121c1a1a1a010c0b0b0b0b0b0a090d0112161819181817161614121001....................
........................011518161618191919191a19010c0a0b0b0b0b0a0a0d0111131818121614011111111112121212121212121814011a161513010c0a0b0b0b0b0a0a0d011216181a1b1c1b1c1d1d191410....................
........................101b1e1c1c1c1b1a1a1a1c1b010b0a0a0b0b0b0a0a0d1014181a1a151917111313131313131313131313131917131e1c1c1c010b0a0a0b0b0b0a0a0d1013181a1b1a1a1b1b1c1b181501....................
........................011b1c191a1a1b1b1b1b1a1a010b0a0a0b0b0b0a0a0d1015171919121715011818181811111219191919121816121c1a1a1a010b0a0a0b0b0b0a0a0d1014181a1b1b1b1b1b1b19181601....................
........................011a1c1a1a1a191a1a1a1a1a010b090a0a0b0b0b0a0d0115171919131815011715151501111016141616101715121c1a1a1a010b090a0a0b0b0b0a0d0110141617191919191918181601....................
........................011a1c1a1a19191919191a1a010b09090a0a0b0b0a0d0112121414011513011015160110191211161501011816111b19191a010b09090a0a0b0b0a0d011115191a1a1a191a1919171601....................
........................011a1c1a1918191919191a1a010b09090a0a0b0b0b0d0115181b1b151917171110010111170111100101181715111b181818010b09090a0a0b0b0b0d0111141619191819191a1a181601....................
........................01181c1a1a1a191919191919010b09090a0a0a0b0b0d0114171919131715151618111111101012121919181616121c1a1a1a010b09090a0a0a0b0b0d011416191a1a1a1a1a1918171501....................
........................01161b191a1a1a1a1a191919010b0809090a0a0b0b0e0115171919131816161616101212121111111715151516121c1a1a1a010b0809090a0a0b0b0e011517191a1a1a1a1a1917161401....................
........................011318171718191919191a1a010b080909090a0b0b0e01151719191319171717171813131313131a1917161616121c1a1a1a010b080909090a0b0b0e0116191b1d1c1b1b1b1b1b191601....................
........................101b1e1b1a19191919191a1a010b080809090a0a0b0d01151819191318161616160110191219121015151516151019161614010b080809090a0a0b0d011518191b1a1a1a181817141101....................
........................011a1c1b1b1b1b1b1b1b1b1b100b08080809090a0b0c0114161919131816161616101218101810121816161618141d1c1c1c100b08080809090a0b0c011416191b1b1b1b1b1c1d1a1601....................
........................011a1c1a1a1a1a1a1a1a191a010b08080808090a0a0c0115171818121715151515161110011001181715151515111a19191a010b08080808090a0a0c011517181a1a1a1a1a1a1a181601....................
........................01181c1a191919191919191a010b0808080809090a0d011517191914191717171717181313131a1917171717150116181a1a010b0808080809090a0d01151618191919191a191a171701....................
........................01161c1a1a1a1a1a1a1918190107040505040605070a0115171919121715151515151516181816151616161615111d1b1a190107040505040605070a011417191a1a1a1a1a1a1a171701....................
........................01131617171919191919191a010c0a0b0b0b0b0b0c0f0215181a1a141513131313131312121211111212121212121c1a1a1a010c0a0b0b0b0b0b0c0f0214171a1919191a191919161701....................
........................01191e1b1a1a1a1a1a1a1a1a010b080808080808090b0115171818191c1c1c1c1c1c1c1c1c1c1c1b1b1b1c1c1b1b1b191919010b080808080808090b011517181a1a1a1a1a1a1a161701....................
........................011a1c191919191919191a1a010c080808080808090b011516181a1a19181a1b1c1c1c1c1c1c1c1c1c1b1d1b1a1a1a1a1919010c080808080808090b0114151719191a19191919161701....................
........................011a1c1a1a1a191919191819010c090808080808080b0114151819181413151515151515151515151516171c1b1919191a1a010c090808080808080b011415181a1a1a1a1a1a1a171701....................
........................011a1c1a1a1a1a1a1a19191a010b0d0908080807070a011517191912011214141414141414141414141416191c1b1a1a1a1a010b0d0908080807070a0115171819191919191919161701....................
........................01191b191919191919191919010a0b0b07060808080a01151718160101101011121212121212121212121417191c1a1a1a1a010a0b0b07060808080a0113141618181818181818151701....................
........................0117171616161616161616150105040306050302040701151613100101010101010101010101010101011011141518171616010504030605030204070111121515151515151515121201....................
........................0101010101010101010101010108090909090a0b0d0c0201010101010101......................0101010101010101010108090909090a0b0d0c0201011001010101010101010101....................
................................................0101010101010101010201......................................................0101010101010101010201..............................................
"""


if __name__ == "__main__":
    build()
