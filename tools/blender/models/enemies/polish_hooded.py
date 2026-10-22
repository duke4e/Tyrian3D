"""CORE's hooded figure (sheet 3 sprites 237 above 275, 2x2 each: one 24 x 56 picture) and its wreck (239 above 277),
polished (2026-10-22, round 36; it replaces wave3_n.py's hooded_whole(), a pillow inflated from the outline with the
head raised on it, and wave3_ap_core.py's hooded_damaged(), the same with its head swapped for shards).

Where it appears: CORE (episode 4) puts six on the ground at its start (t48-524: enemies 251 above 252 at the same x,
event 6: 237 28 pixels above 275, links 20-25); armour 20 each, value 25, one frame; shot down, each piece shows its
damaged sprite (dgr 239, 277) and stays (dlevel -1: a wreck). No other enemy shows these sprites, and none is another
sprite's pixels mirrored, turned or in other ramps.

As the sprites and their 4x upscales draw it (the picture's columns and rows; lit from the upper left): a figure in a
red hooded cloak seen from the front and above: the hood's red rim (70-75) round a smooth grey stone head (07-0c,
columns 7-20 of rows 6-17, lit at its upper left, a white glint at column 11 of row 17), a grey stone body under it
(columns 10-20 of rows 18-27, 03-07, darker to the right); the cloak hanging from the shoulders (row 28, grey stone
hands or shoulders at its top: columns 6-12 of rows 28-31) down to its ragged hem (rows 50-55), its folds red (70-77)
down both sides, its front open and black (01: columns 8-20 of rows 37-53). The wreck: the head and the hood gone, two
jagged shards of grey stone left at the neck (columns 5-22 of rows 20-27), the shoulders broken (rows 28-37), the cloak
as it was.

Built for the game's camera as the round 35 bosses are: one heightfield in the picture's plane on a grid STEP apart
whose lines are the sprites' edges (each piece the cells of its sprite's box), sheared along the camera's line of sight
(polish_gyges_wall's Plate and shear_to_camera), so the camera sees every point where the sprites draw it. Its
heights: the cloak a rounded mass over the outline (rising over FALL to RISE, its shoulders higher, its hem lower), its
folds the red's fine shading as relief, its open front sunk into a dark hollow; the hood a raised rim round the head;
the head a smooth stone dome (to 9.3 pixels) with the sprite's shading laid on; the body under it and the shoulders
stone standing a little out. The wreck: the same cloak from the damaged sprite, the shards steep jagged spikes (flat
facets) where it draws them grey. Painted by the sprite under each face (its ramp, its shade smoothed between the
pixels): the cloak's reds LIFT lighter and a faint glow of their own on the lighter ones (CORE is dark), the stone's
greys lifted, both lighter the less the game's sun lights a face (COMP), the hollow dark.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the whole's origin
is the picture's middle (12, 28) (the corner between the two sprites): column c is x = c + 0.5 - 12, row r is y =
27.5 - r; the top piece's origin is its sprite's centre (0, 14), the bottom's (0, -14) (models.cfg origin). On the
ground: height=-4 sets them on the terrain (all four lines).

models.cfg: the model lines stay; the sprite lines of hooded_top, hooded_bottom, hooded_top_damaged and
hooded_bottom_damaged get height=-4.

Replaces wave3_n.py (all it still builds is the hooded figure: delete it), wave3_ap_core.py (all of it: delete it),
wave3_n_art.py's HOOD and wave3_ap_art.py's HOOD_DMG (only those two read them).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each piece's silhouette
against enemy_3.png as the camera sees it, and from straight above), --only <model,...>, --preview <prefix> (each
piece's top and 3/4 views).
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
import polish_gyges_wall as gw  # noqa: E402
from polish_gyges_wall import Pic, parse, blur, Plate, shear_to_camera, smoothstep  # noqa: E402
from polish_ixm_boss import chamfer, grid, lit, limit_materials  # noqa: E402  (its build() runs only as a script)
from polish_k_pod import triangulate  # noqa: E402

STEP = gw.STEP
W, H = 24, 56
LEFT, TOP = -12.0, 28.0

# Sheet 3 237 above 275: the hooded figure, 24 x 56 (rows top to bottom; each pixel its palette index in hex,
# '..' none).
HOODED = """
..
..
..
..
..
..
........................72727001707070
......................700708080707070701
....................0107080908070707050470
....................7208090807070706060471
..................710808080707070608070472
................70080808070707060706080373
..............7008080807070705060607070271
..............0107080908070706070509050301
..............010609090908070605070a020201
................0108090a080706070707020101
................0106070a090808080704010101
................010407070a0c09060502010101
................70720707070704050502010201
................70727407070607030101010201
................01737307070602010102030201
................01737273060502020403040301
..............0172757373060503030403040501
..............0174757473060503030403040701
............01737575740406050203040304070201
............70747575750606050203040205070402
..........017375750775750505020304037206050170
..........017474070606740506010304037206070401
........01737575070505720505010104037204070470
........01747575070607730706050201017172077301
......70727406090b0a7574080606050401017275740101
....70727404050709077374070705050471017175757101
....70727405040607057374040606050372017172757301
..0101727303040504727474040303037173017071747471
..7071737473040503727473040302717171017071727473
..0172737473730471747473030202717171017070727374
..0172737273737072747372020202717170017071717274
..0173737272717173747302020271717101017070717375
..0172727270017373737201017070707001017070717276
..0171727101727373727101707070700101017070717274
..0101717070747774737170017001010101017070707274
..0101017173767273727001700101010101017070717372
..7271727373737071710101010101010170700170717201
..7372737272707101710101010101010101700170700101
....71727273710171010101010101017001010101010101
....72710173747172010101010101010170700101010101
....73737176737201010101017001017070010101010101
......737370737301010101010101010101010170017001
......717373717272717070010101010170707070700170
....71737374710170727001010101010101010101017072
....73757574710170700101010170717070707070707273
........7271737101010170707272727101010101717172
..........7172747271707071737271010170707070
..............727171717171717101
..
..
"""

# Sheet 3 239 above 277: its wreck (the damaged sprites), 24 x 56, the same way.
HOODED_DAMAGED = """
..
..
..
..
..
..
..
..
..
..
..
..
..
..
..
..
..
..
..
..
..............................0101
..............................010401
................010101........01050801
..............0104020401....010306060801
..............0106020301....01040606070701
............010507020303010103030206070b0601
............010606020303010308060104070a0501
..........010506070301030205050602020306070401
........01730506080401030502020505050104070470
........01747576080301040506040105040172077301
......7070710609..0302040505070701010172757401
....70727401010609050403050709080371017175757101
....70727405010304040503040707050472017172757301
..0101727303040503720305040403047273017071747471
..7071737473040503017173030304727471017071727473
..0172737472720401737473030405757371017070727374
..0172737273710101747373020505757170017071717274
..0173737272010171747302020571717101017070717375
..0172727270017301717201010101017001017070717276
..0171727101727372010101700101010101017070717274
..0101717070747774727170017001010101017070707274
..0101017173767273727001700101010101017070717372
..7271727373737071710101010101010170700170717201
..7372737272707101710101010101010101700170700101
....71727273710171010101010101017001010101010101
....72710173747172010101010101010170700101010101
....73737176737201010101017001017070010101010101
......737370737301010101010101010101010170017001
......717373717272717070010101010170707070700170
....71737374710170727001010101010101010101017072
....73757574710170700101010170717070707070707273
........7271737101010170707272727101010101717172
..........7172747271707071737271010170707070
..............727171717171717101
..
..
"""

PIECES = {"intact": [("hooded_top", 237, (-12.0, 12.0, 0.0, 28.0), (0.0, 14.0)),
                     ("hooded_bottom", 275, (-12.0, 12.0, -28.0, 0.0), (0.0, -14.0))],
          "damaged": [("hooded_top_damaged", 239, (-12.0, 12.0, 0.0, 28.0), (0.0, 14.0)),
                      ("hooded_bottom_damaged", 277, (-12.0, 12.0, -28.0, 0.0), (0.0, -14.0))]}

# Heights: the cloak (rising over FALL from its outline to RISE), its shoulders' lift, its hem's drop, its folds; the
# hollow of its open front; the hood's rim; the head (its base, its dome, how far in it rises); the stone parts.
FLOOR, RISE, FALL = 0.4, 3.6, 2.2
SHOULDERS, HEM = 1.2, 1.1
FOLD = 0.4
SINK = 2.6
HOOD_RISE = 1.6
HEAD_BASE, HEAD_H, HEAD_FALL = 5.0, 4.3, 3.2
STONE = 0.8
SHARD_SLOPE, SHARD_MAX = 2.4, 6.4
# Colours: the reds and greys this many shades lighter than drawn, lighter the less the sun lights a face.
LIFT_RED, LIFT_GREY = 2.4, 1.8
COMP, LIT_MEAN = 1.0, 0.72
CLOTH, STONE_FINISH, HOLLOW = (0.0, 0.68), (0.12, 0.45), (0.0, 0.9)
RED_SHADES = (3, 4, 5, 6, 7, 8, 9, 11)
GREY_SHADES = (2, 4, 6, 7, 8, 9, 10, 11, 12)


class Figure:
    def __init__(self, text, damaged):
        rows = parse(text)
        self.pic = pic = Pic([row + [None] * (W - len(row)) for row in rows], LEFT, TOP)
        self.damaged = damaged
        a = pic.a
        has = a >= 0
        ramp = np.where(has, a >> 4, -1)
        shade = np.where(has, a & 15, 0).astype(float)
        self.red = has & (ramp == 7)
        self.dark = has & (ramp == 0) & (shade <= 2)     # the near-black (01): the open front, the outline
        self.grey = has & (ramp == 0) & (shade >= 3)
        rr = np.arange(H)[:, None] * np.ones((1, W))
        self.head = self.grey & (rr >= 5) & (rr <= 18) if not damaged else np.zeros_like(has)
        self.shards = self.grey & (rr <= 27) if damaged else np.zeros_like(has)
        self.stone = self.grey & ~self.head & ~self.shards
        self.soft = blur(has.astype(float), 0.6)

        def norm_blur(values, mask, sigma):
            return blur(values * mask, sigma) / np.maximum(blur(mask.astype(float), sigma), 1e-6)
        self.red_fine = norm_blur(shade, self.red, 0.6)
        self.red_broad = norm_blur(shade, self.red, 2.0)
        self.grey_fine = norm_blur(shade, self.grey, 0.6)
        self.grey_broad = norm_blur(shade, self.grey, 2.0)
        self.dark_soft = blur(self.dark.astype(float), 0.8)
        self.red_soft = blur(self.red.astype(float), 0.7)
        self.head_soft = blur(self.head.astype(float), 0.5)
        self.stone_soft = blur(self.stone.astype(float), 0.6)
        self.shard_soft = blur(self.shards.astype(float), 0.45)
        # The hood: the red round the head (rows 5-21).
        self.hood = self.red & (rr >= 4) & (rr <= 21) if not damaged else np.zeros_like(has)
        self.hood_soft = blur(self.hood.astype(float), 1.0)
        self.X, self.Y = grid(LEFT, TOP, W, H)
        self.Z, self.part = self.heights(self.X, self.Y)
        CX, CY = grid(LEFT, TOP, W, H, STEP / 2)
        self.CX, self.CY = CX, CY
        self.cell_in = pic.sample(self.soft, CX, CY) > 0.5
        _, self.cell_part = self.heights(CX, CY)
        self.box = (LEFT, LEFT + W, TOP - H, TOP)

    def heights(self, X, Y):
        pic = self.pic
        v = TOP - Y
        inside = pic.sample(self.soft, X, Y) > 0.5
        t = np.clip(chamfer(inside, STEP) / FALL, 0.0, 1.0)
        edge = np.sqrt(t * (2.0 - t))
        prof = 1.0 + SHOULDERS / RISE * np.exp(-((v - 31.0) / 4.0) ** 2) - HEM / RISE * smoothstep(44.0, 56.0, v)
        z = FLOOR + RISE * edge * prof
        z = z + edge * FOLD * (pic.sample(self.red_fine, X, Y) - pic.sample(self.red_broad, X, Y)) * \
            pic.sample(self.red_soft, X, Y)
        z = z - SINK * edge * smoothstep(0.25, 0.85, pic.sample(self.dark_soft, X, Y))
        z = z + HOOD_RISE * edge * pic.sample(self.hood_soft, X, Y)
        z = z + STONE * edge * smoothstep(0.3, 0.7, pic.sample(self.stone_soft, X, Y))
        part = np.zeros(z.shape, int)               # 0 the cloak, 1 the head, 2 the stone, 3 the shards
        part[pic.sample(self.stone_soft, X, Y) > 0.5] = 2
        if not self.damaged:
            hin = pic.sample(self.head_soft, X, Y) > 0.5
            th = np.clip(chamfer(hin, STEP) / HEAD_FALL, 0.0, 1.0)
            hz = HEAD_BASE + HEAD_H * np.sqrt(th * (2.0 - th)) + 0.22 * (pic.sample(self.grey_fine, X, Y) -
                                                                      pic.sample(self.grey_broad, X, Y))
            up = hin & (hz > z)
            z = np.where(up, hz, z)
            part[up] = 1
        else:
            sin = pic.sample(self.shard_soft, X, Y) > 0.5
            ds = chamfer(sin, STEP)
            sz = 1.0 + np.minimum(SHARD_SLOPE * ds, SHARD_MAX) * (0.7 + 0.05 * pic.sample(self.grey_fine, X, Y))
            up = sin & (sz > z)
            z = np.where(up, sz, z)
            part[up] = 3
        return np.maximum(z, 0.2), part

    def plate(self):
        def top(X, Y):
            i = np.round((X - self.box[0]) / STEP).astype(int)
            j = np.round((Y - self.box[2]) / STEP).astype(int)
            return self.Z[j, i]

        def cells(X, Y):
            i = np.clip(np.floor((X - self.box[0]) / STEP).astype(int), 0, self.cell_in.shape[1] - 1)
            j = np.clip(np.floor((Y - self.box[2]) / STEP).astype(int), 0, self.cell_in.shape[0] - 1)
            return self.cell_in[j, i]
        return Plate(self.box, top, cells=cells)

    def colour(self, x, y, normal, part):
        pic = self.pic
        v = int(pic.pixel(np.array([x]), np.array([y]))[0])
        X, Y = np.array([x]), np.array([y])
        comp = COMP * (LIT_MEAN - float(lit([normal])[0]))
        if part in (1, 2, 3) or (v >= 0 and v >> 4 == 0 and (v & 15) >= 3):
            s = float(pic.sample(self.grey_fine, X, Y)[0]) + LIFT_GREY + comp
            return (min(GREY_SHADES, key=lambda q: (abs(q - s), q)), STONE_FINISH, 0.0)
        if v < 0 or (v >> 4 == 0 and (v & 15) <= 2) or float(pic.sample(self.dark_soft, X, Y)[0]) > 0.6:
            return (0x02, HOLLOW, 0.0)
        s = float(pic.sample(self.red_fine, X, Y)[0]) + LIFT_RED + comp
        q = min(RED_SHADES, key=lambda r: (abs(r - s), r))
        return (0x70 + q, CLOTH, 0.1 if q >= 6 else 0.0)


def material(key):
    index, finish, glow = key
    name = "hooded_%s%02x%s" % ({CLOTH: "c", STONE_FINISH: "s", HOLLOW: "h"}[finish], index, "e" if glow else "")
    extra = dict(emission=k.level_palette()[index], emission_strength=glow) if glow else {}
    return k.material(name, palette=index, metallic=finish[0], roughness=finish[1], **extra)


def paint(fig, obj, kinds):
    mesh = obj.data
    normals = [Vector(n.vector) for n in mesh.corner_normals]
    keys = []
    current = 0
    for poly, kind in zip(mesh.polygons, kinds):
        c = poly.center
        if kind == 0:
            i = min(max(int(math.floor((c.x - fig.box[0]) / STEP)), 0), fig.cell_part.shape[1] - 1)
            j = min(max(int(math.floor((c.y - fig.box[2]) / STEP)), 0), fig.cell_part.shape[0] - 1)
            current = int(fig.cell_part[j, i])
            n = tuple(normals[poly.loop_indices[0]])
            if current == 3:  # the shards: flat facets
                n = tuple(poly.normal)
                for li in poly.loop_indices:
                    normals[li] = Vector(n)
            keys.append(fig.colour(c.x, c.y, n, current))
        else:
            keys.append((0x01, HOLLOW, 0.0) if current != 3 else (0x03, STONE_FINISH, 0.0))
    keys = limit_materials(dict(enumerate(keys)), None)
    order = sorted(set(keys.values()))
    for key in order:
        mesh.materials.append(material(key))
    for poly in mesh.polygons:
        poly.material_index = order.index(keys[poly.index])
    mesh.normals_split_custom_set([tuple(n) for n in normals])
    mesh.update()


def coverage(fig, box):
    x0, x1, y0, y1 = box
    out = []
    for r in range(28):
        row = []
        for c in range(24):
            n = 0
            for dj in (0.25, 0.75):
                for di in (0.25, 0.75):
                    i = int(math.floor((x0 + c + di - fig.box[0]) / STEP))
                    j = int(math.floor((y1 - r - dj - fig.box[2]) / STEP))
                    n += bool(fig.cell_in[j, i])
            row.append(n >= 2)
        out.append(row)
    return out


def build():
    options = k.args()
    k.reset()
    bpy.context.scene.view_settings.view_transform = "Standard"
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    sheet = os.path.join(options["check"], "enemy_3.png") if "check" in options else None
    for kind, text in (("intact", HOODED), ("damaged", HOODED_DAMAGED)):
        fig = Figure(text, kind == "damaged")
        print("%s: z %.2f..%.2f" % (kind, fig.Z.min(), fig.Z.max()))
        plate = fig.plate()
        for name, sprite, box, centre in PIECES[kind]:
            if only and name not in only:
                continue
            x0, x1, y0, y1 = box
            e = 1e-6
            obj, kinds, _ = plate.mesh(name, lambda X, Y: (X > x0 + e) & (X < x1 - e) & (Y > y0 + e) & (Y < y1 - e))
            paint(fig, obj, kinds)
            shear_to_camera([obj])
            obj.data.transform(Matrix.Translation((-centre[0], -centre[1], 0.0)))
            parts = triangulate([obj])
            bpy.context.view_layer.update()
            if sheet:
                mask = k.sprite_mask(sheet, sprite)
                mk.compare("%s (3 %d, as the camera sees it)" % (name, sprite), coverage(fig, box), mask)
                mk.compare("%s (3 %d, from straight above)" % (name, sprite), mk.coverage(parts, 24, 28), mask)
            mk.report(name, parts, os.path.join(out, name + ".glb"))
            if "preview" in options:
                mk.preview(options["preview"] + name, parts)
            for o in parts:
                bpy.data.objects.remove(o)


if __name__ == "__main__":
    build()
