"""The HOT DOG pick-up of SAWBLADES (the coins sheet's sprite 92, 2x2: 24 x 28; it arms the ship with the hot dog weapons),
polished (2026-10-22, round 36; it replaces wave3_ai_items.py's hot_dog(), a lathed dish with tube buns and letters
inflated from the pixels' outlines). models.cfg: model hot_dog items/hot_dog.glb and sprite coins 92 hot_dog yaw=0 stay
as they are (no spin: the words stay readable; the game centres it in height on its layer). No other sprite is its
pixels mirrored, turned or in other ramps; one frame.

As the sprite draws it (columns and rows of the 24 x 28 sprite): the word HOT across its top (columns 2-16 of rows 0-6)
and DOG across its bottom (columns 8-23 of rows 21-27) in a blocky pixel font, each stroke a pixel wide in fire shades
(0x76 at the strokes' ends, 0x78, 0x7a across their middle row: lit from inside) outlined in dark red (0x70); between
them a blue oval plate (ramp 3, rows 6-21, all 24 columns; lit at its upper left, 0x3b-0x3d) and on it a hot dog lying
from its top right (column 16, row 6) down to its bottom left (column 6, row 19): a bun (ramp 1's tans, wider on its
right side) round a red sausage (0x73-0x79) with a yellow streak along it (0x7a-0x7c). The 4x upscale smears the words
(its HOT and DOG half legible): built from the original pixels.

Built for the game's camera as polish_green_shell.py is: one heightfield in the picture's plane on
polish_gyges_wall.Plate's grid (STEP 0.5, its lines on the pixels' edges, so the strokes stay square), sheared along the
camera's line of sight (y - z tan 20): the plate a shallow dish over the ellipse of its pixels' moments (ELLIPSE; their
overlap with it 0.94), its floor PLATE[0] high with a rounded rim rising PLATE[1] over it; the bun a flattened tube
along the sprite's diagonal (DOG_AXIS), shifted to its right as the sprite draws more bun there; the sausage a round bar
on it; the words a dark backing under their outline pixels with their bright strokes raised on it (LETTERS), standing
over the plate's edge where they meet it. Painted by the sprite's shades (polish_green_shell's Paint: each face the ink
of the pixels under it, plate, bun, sausage or word, in that ink's shade there, blurred, lifted and lighter where the
game's sun lights it less; the words' pixels exactly as drawn, so that they read), the words glowing in their own reds
(0x70 0.12, 0x76 0.42, 0x78 0.5), the sausage's yellow streak a little (0x7a, 0.15). Heights: z 0 (its underside) to 4.7
(the sausage; the words 1.6, the plate's rim 1.8). Deterministic (no random numbers; the faces' centres and normals
rounded before they pick their shades).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the origin is the
sprite's centre (its pixel edge 12, 14): column c's left edge is x = c - 12, row r's top edge y = 14 - r.

Replaces wave3_ai_items.py (all of it: the hot dog is all it builds; nothing imports it) and enemies/wave3_ai_art.py's
HOTDOG (read only by it, through wave3_ai_kit's frame()).

Options after "--": --outdir <dir> (default assets/models/items), --check <sheets dir> (the outline as the camera sees
it against coins.png's sprite 92), --preview <prefix> (top and 3/4 views).
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "enemies"))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_item_kit as kit  # noqa: E402
import polish_gyges_wall as gw  # noqa: E402  (Plate, the shear to the camera, the faces' light)
from polish_green_shell import edt, seg_dist, limit_materials  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402

W, H = 24, 28                     # the sprite; its origin its middle, the pixel edge (12, 14)
LEFT, TOP = -12.0, 14.0
S = 4                             # the fine grid of the fields: S cells a pixel
STEP = 0.5                        # the heightfield's grid (polish_gyges_wall.Plate's, made finer: the letters' strokes
#                                   are a pixel wide)
PLATE = (1.0, 0.8, 1.4, 0.55)     # the plate: its floor, its rim's rise over it, the rim's distance in from its edge
#                                   and its width
ELLIPSE = ((0.15, 0.26), (12.55, 8.2), 8.9)   # its outline: the ellipse of its pixels' moments (middle, semi-axes,
#                                   the long one's angle in degrees; its pixels' overlap with it 0.94)
DOG_AXIS = [(15.9, 6.2), (6.4, 19.0)]   # the hot dog: its axis (pixel edges, the top right end to the bottom left)
BUN = (0.7, 3.7, 1.3, 2.6)        # the bun: its axis's shift to the right, half-width, axis height, how high it rises
SAUSAGE = (1.35, 3.4)             # the sausage on it: its radius and its axis's height
LETTERS = (0.9, 0.7, 0.45)        # HOT and DOG: their dark backing's height, the strokes' rise over it, their rounding
GLOW = {0x70: 0.12, 0x72: 0.2, 0x74: 0.3, 0x76: 0.42, 0x78: 0.5, 0x7a: 0.58, 0x7c: 0.62}


def px(c):
    return c - 12.0


def py(r):
    return 14.0 - r


def parse_picture(text):
    a = -np.ones((H, W), int)
    for i, line in enumerate(text.split()):
        for c in range(W):
            t = line[2 * c:2 * c + 2]
            if t != "..":
                a[i, c] = int(t, 16)
    return a


def up(m):
    return np.repeat(np.repeat(m, S, 0), S, 1)


class Field:
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
    return height * np.sqrt(1.0 - (1.0 - np.clip(depth / fall, 0.0, 1.0)) ** 2)


class HotDog:
    """The pick-up in the picture's plane: the plate a shallow dish over its pixels (blue, and the hot dog's), the hot
    dog a bun along the sprite's diagonal with the sausage on it, the words a dark backing under their outline pixels
    with their bright strokes raised on it."""

    def __init__(self, a):
        self.a = a
        xs = LEFT + (np.arange(W * S) + 0.5) / S
        ys = TOP - (np.arange(H * S) + 0.5) / S
        X, Y = np.meshgrid(xs, ys)
        ramp = np.where(a >= 0, a >> 4, -1)
        rows = np.arange(H)[:, None] + np.zeros((1, W), int)
        words = (ramp == 7) & ((rows <= 5) | (rows >= 21) | ((rows == 6) & (np.arange(W)[None, :] < 6)))
        self.words = words
        (ex, ey), (ea, eb), ang = ELLIPSE
        t = np.radians(ang)
        u = (X - ex) * np.cos(t) + (Y - ey) * np.sin(t)
        v = -(X - ex) * np.sin(t) + (Y - ey) * np.cos(t)
        q = np.sqrt((u / ea) ** 2 + (v / eb) ** 2)
        dm = q < 1.0
        e = np.clip(1.0 - q, 0.0, None) * eb       # (about) how far in from the ellipse's edge
        floor, rise, at, width = PLATE
        plate = rounded(e, floor, 0.8) + rise * np.exp(-((e - at) / width) ** 2) * np.clip(e / 0.6, 0.0, 1.0)
        # The hot dog: the bun (a flattened tube beside the axis, shifted right as the sprite draws more bun there) and
        # the sausage in it.
        (x0, y0), (x1, y1) = [(px(c), py(r)) for c, r in DOG_AXIS]
        d = np.array([x1 - x0, y1 - y0])
        d = d / np.linalg.norm(d)
        right = np.array([-d[1], d[0]])             # to the right of the dog looking along it (down the screen)
        shift, hw, bz, brise = BUN
        bun_pts = [(x0 + right[0] * shift, y0 + right[1] * shift), (x1 + right[0] * shift, y1 + right[1] * shift)]
        db = seg_dist(X, Y, bun_pts)
        bun = np.where(db < hw, bz + brise * np.sqrt(np.clip(1.0 - (db / hw) ** 2, 0.0, None)), -1.0)
        sr, sz = SAUSAGE
        ds = seg_dist(X, Y, [(x0, y0), (x1, y1)])
        sausage = np.where(ds < sr, sz + np.sqrt(np.clip(sr * sr - ds * ds, 0.0, None)), -1.0)
        top = np.maximum(np.where(dm, plate, -1.0), np.maximum(bun, sausage))
        # The words.
        wm = gw.blur(up(words.astype(float)), 0.35 * S) > 0.5
        bright = words & (a > 0x70)
        bm = gw.blur(up(bright.astype(float)), 0.3 * S) > 0.5
        back, srise, rnd = LETTERS
        word_top = rounded(edt(wm, 1.0 / S), back, 0.35) + np.where(bm, rounded(edt(bm, 1.0 / S), srise, rnd), 0.0)
        top = np.where(wm, np.maximum(top, word_top), top)
        cells = (dm | wm | (bun > 0) | (sausage > 0)) & (top > 0.0)
        self.cells_f = Field(cells.astype(float))
        self.top_f = Field(np.where(cells, top, 0.0))
        self.sausage_f = Field((sausage > 0).astype(float))

    def cells(self, cx, cy):
        return self.cells_f(cx, cy) > 0.5

    def heights(self, Xa, Ya):
        return self.top_f(Xa, Ya)


# --- Painting -----------------------------------------------------------------------------------------------------------

INKS = {   # shades, (metallic, roughness), lift, contrast (about shade 7), comp
    "plate": ([0x33, 0x35, 0x37, 0x39, 0x3b, 0x3d], (0.35, 0.25), 0.8, 1.0, 1.6),
    "bun": ([0x16, 0x18, 0x1a, 0x1c, 0x1e], (0.0, 0.6), 0.6, 1.0, 1.4),
    "sausage": ([0x72, 0x74, 0x76, 0x78, 0x7a, 0x7c], (0.1, 0.32), 0.3, 1.0, 1.0),
    "word": ([0x70, 0x72, 0x74, 0x76, 0x78, 0x7a, 0x7c], (0.1, 0.3), 0.0, 1.0, 0.0),
}
LIT_MEAN = 0.72


def mat_of(key):
    shades, (met, rough), _, _, _ = INKS[key[0]]
    glow = GLOW.get(key[1], 0.0) if key[0] == "word" else (0.15 if key[1] >= 0x7a else 0.0)
    extra = dict(emission=k.level_palette()[key[1]], emission_strength=glow) if glow > 0 else {}
    return k.material("hot_dog_%s_%x" % (key[0], key[1]), palette=key[1], metallic=met, roughness=rough, **extra)


class Paint:
    def __init__(self, a, dog):
        shade = np.where(a >= 0, a & 15, 0).astype(float)
        ramp = np.where(a >= 0, a >> 4, -1)
        masks = {"plate": ramp == 3, "bun": ramp == 1, "sausage": (ramp == 7) & ~dog.words, "word": dog.words}
        self.inks = []
        for name, (shades, _, lift, contrast, comp) in INKS.items():
            mask = masks[name]
            # the words keep their pixels' own shades (outline dark, strokes bright: their legibility), unblurred
            soft = gw.fill(shade, mask) if name == "word" else gw.blur(gw.fill(shade, mask), 0.45)
            self.inks.append((name, shades, gw.blur(mask.astype(float), 0.5 if name != "word" else 0.3),
                              7.0 + contrast * (soft - 7.0), lift, comp))

    def sample(self, field, Xa, Ya, nearest=False):
        if nearest:
            c = np.clip(np.floor(np.asarray(Xa) - LEFT).astype(int), 0, W - 1)
            r = np.clip(np.floor(TOP - np.asarray(Ya)).astype(int), 0, H - 1)
            return field[r, c]
        fc = np.clip(np.asarray(Xa, float) - LEFT - 0.5, 0.0, W - 1.0)
        fr = np.clip(TOP - np.asarray(Ya, float) - 0.5, 0.0, H - 1.0)
        c0 = np.minimum(np.floor(fc).astype(int), W - 2)
        r0 = np.minimum(np.floor(fr).astype(int), H - 2)
        tc, tr = fc - c0, fr - r0
        return ((field[r0, c0] * (1 - tc) + field[r0, c0 + 1] * tc) * (1 - tr) +
                (field[r0 + 1, c0] * (1 - tc) + field[r0 + 1, c0 + 1] * tc) * tr)

    def keys(self, Xa, Ya, normals, on_sausage):
        lit_by = gw.sun_on(normals)
        weights = np.stack([self.sample(ink[2], Xa, Ya) for ink in self.inks], 0)
        which = weights.argmax(0)
        names = [ink[0] for ink in self.inks]
        per = [gw.nearest(self.sample(soft, Xa, Ya, nearest=(name == "word")) + lift + comp * (LIT_MEAN - lit_by),
                          shades) for name, shades, _, soft, lift, comp in self.inks]
        out = []
        for i, w in enumerate(which):
            if on_sausage[i] and names[w] != "word":
                w = names.index("sausage")
            out.append((names[w], int(per[w][i])))
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


def build():
    opts = kit.options()
    out = kit.outdir(opts)
    a = parse_picture(PICTURE)
    dog = HotDog(a)
    saved = gw.STEP
    gw.STEP = STEP               # Plate reads its grid's spacing from its module (while it is built and meshed)
    try:
        k.reset()
        plate = gw.Plate((-12.0, 12.0, -14.0, 14.0), dog.heights, cells=dog.cells, bottom=True)
        obj, kinds, _ = plate.mesh("hot_dog", lambda cx, cy: np.ones(np.shape(cx), bool))
    finally:
        gw.STEP = saved
    centres, normals = gw.face_data(obj)
    centres, normals = np.round(centres, 4), np.round(normals, 4)
    on_sausage = dog.sausage_f(centres[:, 0], centres[:, 1]) > 0.5
    top = Paint(a, dog).keys(centres[:, 0], centres[:, 1], normals, on_sausage)
    keys = [top[i] if kinds[i] == 0 else ("plate", 0x33) for i in range(len(kinds))]
    assign(obj, keys)
    if "check" in opts:
        covered = gw.own_coverage(lambda Xa, Ya: dog.cells(Xa, Ya), W, H, LEFT, TOP)
        kit.compare("hot_dog (coins 92), as the camera sees it", covered, kit.sprite_mask(opts["check"], 92, True))
    gw.shear_to_camera([obj])
    triangulate([obj])
    import bpy
    bpy.context.scene.view_settings.view_transform = "Standard"
    kit.report("hot_dog", [obj], os.path.join(out, "hot_dog.glb"))
    if "preview" in opts:
        kit.preview(opts["preview"] + "hot_dog", [obj], (24, 28), scale=16, distance=1.0)


# --- The sprites' pixels ----------------------------------------------------------------------------------------------
# Each pixel its palette index as two hex digits ('..' none), rows top to bottom (the picture's empty rows left out).

PICTURE = """
......70....70....7070....707070................
....707670707670707676707076767670..............
....7078707078707870707870707870................
....707a7a7a7a707a70707a70707a70................
....7078707078707870707870707870................
....70767070767070767670..70761010..............
......70....3233343537363534737572353533........
..........333536373736171a187976743637363533....
........353738393736171a1879761b1b163637383634..
......37393a393736171a187a761a1b1c1b363738393736
....373b3b3b3937361a187c79181a1c1d1b363737393a38
..373b3d3b393736171a187a76181a1c1d1b3637383a3b38
37393d3b393736171a187b76181a1c1d1b163637393b3c38
373c3d3b3937361a187a7775181c1b1d1b363737393b3d39
393d3b39373617187a7875181c1b1d1b163637393b3d3c37
383c3b3937361a187b75181a1c1b1d1b363737393b3d3937
383b3a393736187a75181a1c1b1d1b163637393b3d3b37..
3839393937367678181a1c1b1d1b163637393b3b3b37....
3637373737367476181c1b1c1b16363737393a3937......
..34353637373635341b1b1b1636373739383735........
......33333535363534343435363737363533..........
..................707070363735343332....7070....
................70767676707070767670..70767670..
................707870707870787070787078707070..
................707a70707a707a70707a707a707a7a70
................70787070787078707078707870707870
................7076767670..70767670..70767670..
..................707070......7070......7070....
"""


if __name__ == "__main__":
    build()
