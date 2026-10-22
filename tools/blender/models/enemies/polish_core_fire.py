"""CORE's great fire (sheet 3: fourteen 2x2 sprites, 3 22 23 39 44 60 61 77 82 96 98 99 101 117 118, that the level
puts together into one 84 x 98 blaze), polished (2026-10-22, round 36; it replaces wave3_n_fire.py, an outline inflated
into a molten pillow painted in bands of the fire's shades that glowed up to 2.2: one white blob).

Where it appears: CORE's boss (episode 4, t5350; THE CORE in episode 6 brings the same wave, enemies 1672-1685, copies
of 366-379): fourteen top enemies (event 7, link 199, armour 250, then 255 and 254 by events 25), placed at x 140,
164, 176, 200 as the sheet lays the sprites out: 39 77 96 at the picture's column 0 (rows 14, 42, 56), 22 60 98 117
at column 24 (rows 0, 28, 56, 70), 23 61 99 118 at column 36 (the same rows), 44 82 101 at column 60 (rows 14, 42, 56):
windows into one picture, overlapping (columns 36-47 of the two middle columns, rows 56-69 of the side columns and
70-83 of the middle ones show the same pixels twice). The boss bar is link 199; the events move it about the screen
(event 20) and make it fire. One frame each, not animated; no other enemy shows these sprites, and none is another
sprite's pixels mirrored, turned or in other ramps.

As the sprites and their 4x upscales draw it (the picture's columns and rows; all in the fire ramp, 7, 70-7f): a
blaze of flames licking up the screen, its middle (columns 24-60) the tallest, three long tongues reaching to row 0
(columns 32-36, 45-52), the sides' flames shorter (columns 4-12 and 72-80 from row 20), white-hot yellow cores (7b-7f)
streaking up the middle of each tongue, orange round them, dark red at its edges and in the gaps between the tongues;
at its feet two dark loops, see-through (columns 15-23 and 61-70 of rows 63-82), and a ragged base (rows 80-97).

Built for the game's camera as the round 35 bosses are: one heightfield of the whole blaze in the picture's plane on a
grid STEP (1 pixel) apart whose lines are the sprites' edges and the overlaps' middles, sheared along the camera's line
of sight (polish_gyges_wall's Plate and shear_to_camera); each piece the cells of the part of the picture it keeps
(PIECES: the overlaps split in their middles, at column 42 and rows 63 and 77, as wave3_n_fire.py split them), so drawn
together the blaze is there once. Its heights: a floor rising from the outline over FALL, the fire's broad heat (the
shades blurred) as its body (hotter, thicker: up to 8.8 pixels in the middle), the shades' fine streaks laid on as
relief (the tongues' bright cores ridges, the gaps between them furrows), the loops open. Painted in bands of the fire
ramp's own palette indices by the heat under each point (smooth contours: polish_orb_red.band_split), the top TOP_HEAT
shades hotter than drawn, each band glowing in its own colour, more the hotter: polish_fire_wall.py's bands (FLEET's
and LAVA RUN's fire: one family), its dark red ones glowing a little more (0.2 for 0x72 up to 0.65 for the white-hot
0x7f: a molten mass, not flames over the ground), matte; its normals the heightfield's. The fire is a top enemy (38 +
the terrain's headroom): its base on that layer, its top far under the player's plane.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera. The whole has its
origin at the picture's middle (42, 49): column c is x = c + 0.5 - 42, row r is y = 48.5 - r; a piece whose sprite's
top left corner is the picture's (c0, r0) has its origin at its sprite's centre (c0 + 12 - 42, 49 - r0 - 14)
(models.cfg origin).

models.cfg: the model and sprite lines of core_fire_* stay as they are (origin; yaw=0).

Replaces wave3_n_fire.py (all of it: delete it) and wave3_n_art.py's FIRE (only wave3_n_fire.py reads it).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each piece's silhouette as the
camera sees it against the part of its sprite it keeps), --only <model,...>, --preview <prefix> (each piece's top and
3/4 views).
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
from polish_gyges_wall import Pic, parse, blur, Plate, shear_to_camera  # noqa: E402
from polish_ixm_boss import chamfer  # noqa: E402  (its build() runs only as a script)
from polish_orb_red import band_split  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402

STEP = 1.0                        # the fire's grid (pixels): coarser than the bosses' (its bands' contours are smooth)
W, H = 84, 98
LEFT, TOP = -42.0, 49.0

# Sheet 3 22 23 39 44 60 61 77 82 96 98 99 101 117 118: CORE's fire, the 84 x 98 picture the fourteen sprites are
# windows into (the sheet's pixels x 0-83, y 14-111, inside the sprites' boxes): each pixel its palette index in hex,
# '..' none (trailing ones left out).
FIRE_ART = """
....................................................................72..............................73
..................................................................727572..........................737473
..................................................................727672..........................737573
..................................................................727672..........................737573
..................................................................727672..........................737573
..................................................................727672..........................737573
................................................................71737672..........................73757472
..............................................................7172747772..........................73757472
..............................................................7173757772..........................73757472
..............................................................717476777471........................73757572
..............................................................717476777471........................7375757372
..............................................................717476777471........................7375767472
..............................................................717576777471........................7375777672
..............................................................717676777471........................7375787673
............................................................71757776777571........................737578787571
............................................................71767976777571........................737578797571
..........................................................7172767976777571........................737578797572
........................................................717271777976777571........................73757879767370
......................................................71727471787976777571........................7374787976737271
............70........................................71747572797876777571........................737478797774727170........................................70
............7070....................................7073777474797876787571........................737378797775737170......................................7071
............707270..................................71747573757a77757876727170..............71....72737879787573727070..................................707271
............707370................................7172747274787a7775797672737170..........727572..72737879787574727070..................................717271
............707370................................7172737376787a7776797672747271..........727674..7272787978757473717170................................717371
............707470................................707273767779797776797773747371....72..70747674717372787978757473717271................................717371
............707571................................7072747879797976777a7773747472..72747271757675707472777978757473727371................................717371
............707671................................717276797a7a7877787a77747474727172747271757775737573777978757473727371................................717371
............707871..............................717372787b7b797876787b77757574737172757271757775737573767878757473727471..............................71737371
............707871..............................727472787d7b7977767a7b7776757574717375727275787574767475777875757373747371............................71747371
............707972..............................727571787d7c7977777c79777675757471737673727579757477757477787575747374747271..........................71747371
............70797371..........................71747574787d7c79777c7a79777675757471747673727679767578757477787475747374747371..........................71757371
............71797572..........................71757574787d7c79787d797977767675747274767473777a777579767476787475757374757372..........................71757371
............717a777470......................7172787775787d7c79797b797877767775747274767473787a78757976747577747575747475737372......................7174757371
............717a797672......................7174787875787d7c79787b7978777677757573747674737a7c79767977757577747575747476747371......................7174757371
............707a79767471....................7176787975787d7b79777b797877767775767374767473777977767977767576737576757476747371....................717474757371
............707b7976747270..................7177787974787a7978777b797776767775777474767573767776767977767576737576757476747371..................70737475757371
............717b7976757370..................717578797578797978777b797776767775777474767574737575767978777576737576767476747271..................70737475757371
............717b7977767470..................717278797577787877767b797676767875777574767675747374767a78777676737476777576747271..................70737475757370
..........70737c7a7877747070..................7178797876777877777a797676767976787574767776757573777a797876767474767776767471..................707074757675737270
..........70747c7a7877747270..7170......70..7072787a7878757776797a797576777976787574767878777674787a797876767574767876767370......70........71727174757675737270
........7072757c7a787775737071767270..7074707075787a79787875767a7a7974767779767876747578797a7775787a797876767574767877767370..707072......717474737576767573727270
........7073787c7a787776737172787471727377717277787a79787876797a7a7973767779767976747577797a7976787a7978757676747578777775707074707371..70747575737576767473727270
........70757a7e7a78797a757274797571737679757777787a797879787a7a7a7974777879767a77747477787c7c77787a79787576777675787877757071757173727074767675737677767473727270
........70757b7e7b77797b77737579767274777a777877787a797879787a7a7a7976777979757a78747576797c7e79797a79777476787875787978757172757274737375767675757776767473727270
........70757a7c7a767a7b78737679777475787a787877797a797879787a7a7a797678797976797b777576787b7f7a7a7a78777277797974777978767273757375737375767675767776767472727170
........0174787a78757b7d7774767a777476787a7878787a7a79797a787a7a7a787679797777777b7a7677787a7f7b7a7978767376787772777a79767274757375737376767576777776767472727070
........7072767776727b7d7874777a777476787a78787a7a7a78797a787b7a7977767978777777787b7b7a7a7a7e7b797978777574747371777a79767375767376737376757678777676757372727070
........7072727274757c7f7875787b787576787a78797b7a79787a7b787b79787777797877797677797c7e7c7a7b7b797878777676757371777b79777375767377747376747879777676757372717070
......707172737372777c7f7976797b787676787b787a7c7a78787a7b787b78767677797877797777777a7d7f7b7a7a7a7878777676747271777a7977747676737776747874797a777675747272707070
......707273747373797b7d7877797b777676787b787b7c7a77787b7b797b777576787a777879777776787a7d7c79787a7878777675747171767878777376767377767478737c7a777675747271707270
......7073747575747a797a78777a7c777777797b787b7c7977797b7c797b767576787a77787a77757576797a797675797978777675737170747677747577767377777478737d79777675747170717270
......7074757576767b797877787a7c7877787a7b797b7c7977797b7c797c757576787b77787a777575757777767472777878777674737171737474757578767377787579737d78777575727071727170
......7074757676777c797877797c7c7878797b7b797b7c79767a7b7c7a7d767576787b77787a777575767876757573747879767573727172747676757579767377787579737c78767574707171727170
......7074757677797c797876797e7c79797a7c7b797b7c77757a7c7e7b7c777376787b77777b787675767a7776767474767876757372707274777675757976737778757a737c777675747071727170
......7074767677797d7a7876797d7a797a7c7c7b797a7b76747b7e7f7b7c787375787d77787b7a7676787b7877767473757776747271707375787675767976747779757c747b7775747370717270
......70727677777a7e7a7876777979797b7d7c7b78797874737b7c7f7b7c797475787f7a7a7d7a7777797b7978777574737775747271707476797674767a7674787a767a73797675747370707170
......70717677797a7f7b7878767778797b7c7b7a7877757574797b7c7a7b7a7675797f7d7d7d7b79777a7c7a797676747377757372717074777a7673777b7674787a767972797675737373737170
........017777797b7f7c7879767578797a7b7a79777677767574777a7a7c7b7876797f7d7c7b7a79777a7e7a787676747376747272717174787c7773787c7773797b78777277767473747575737070
........0177787a7c7e7b7779767478797a7a7a7977777b7a77757278797d7d7b777a7d7d7a787a7975787a76767576757375737272717174787c7873797d77727a7d78767178757473757676737170
......717278797b7c7e7a777976727678787a7b7a787a7a76767674777a7f7f7c787a7e7d7976777873747573747477757375737272717274797e7975797f7a72797b7875737875737475777473717070
......7074787a7c7d7c78777a76707477787a7b7a77777574757674777b7f7f7a787a7f7c7875757873727273747577757375737272727274797c79777b7e797376777570767975737576767472707070
......0175797b7c7d7978787b7701727577797a787573727375757377797c7a77777a7e7c7675737973727374747779767474737272727374767a76777b7c79707374717377787574757676737170717170
......7075797b7c7e7a78787c7771017375767876747070747875727777777777787b7e7b777473797372747476797a787474737272727373747776767a7975717271727476767675757576737071737170
......7074787a7c7d7a78787b7874017072737473017072747874727779777777797d7f7c787473797573747576797a79757473737272747374787876767471747472717374767776757477737172747170
......017376797a7c7a78777b7876717071707170707373777a747377797776767a7f7f7d7a75727a7573747677797b797674747372727472757a78757271707373707173737478777474787371737570
......01017476777978797779797673707070......7072777b757378797874777a7f7f7f7c76747a76737577787a7b7a777374737372757274787773727170707070717274747876747478747173767170
......717172747577787977787875740171..........70787b77747a7b7975777a7d7f7c7a77747b78737577797a7b7a787374747372757372747372727170......727376777876737578747173777270
......707372727577787b78787776747370..........70787b77747b7c797677787c7f7b7972767a78747578797b7b7a7973757473737674727171727170........7274777879757376787671747a7570
......727374747375797c79767776757370..........70797d78747c7d7a747776797d7a7374777a79767577797b7d7b7a73757573737676747271707070........727376757674737679777174777470
......707375757472777a78767577757370..........707b7e77757c7f797477757475727475787c7a777577797b7e7b7a737576737377777472717070..........72737573747373767b767074747270
......707375757472777a78767577757370..........707b7e77757c7f797477757475727475787c7a777577797b7e7b777375777473777774727170............727375737273727677757073727071
........7074757471767877757373747170..........707a7e77737a7e7873787574757576767b7e7c777376787a7c79737576777473777974727070............7273757372727172747070717071
..........70727572747575727178787570..........70797c7873787b7975787674767877797d7e7d79717577777673747577787573787a7672717070..........73747573727271717070717070
............707070727373717779777570..........70767b7873757678767877737779787a7c7e7d7a727676737374757678787573777b767472717070........737575727272727272717070
................7070707071767779787470........7075787874747577767878737679787a7c7e7e7b737777747475767778787472767b767473717170......7274787472717171707071
........................707276777a777570......70767778747677787578787374757676797c7e79727776747576787878777470757a757473707070....7375787573727070
..........................707376777a787570....70787779757778797478787472737474767778727477767375777878787672707479747476727070707376797573727170
............................707375767b7a76707071767a79757878797378787774727272727371747478767274787878777370707376757a747376737476797673727271
..............................707375757b7d7b7a77727b78757678797478797979767574747474777778757072747676747070717275777d717a767678797573727271
................................7073747675767474727978757677797578797a7a7a7877757576777877747070707071717071727375777b717c7c7a777573727270
..................................707274737373727477767476777a7576797a7a7a7a797677787878757370707070727373737473757778707775767573737271
....................................7070727171737775737476777a767478797a7a7a7a79797978767471727270727476767675757574777372737473737170
........................................707070707170707376787b7775737578797a7a7979787574727374747274767777767675757374767270707070
................................................7070727375787b787775747375767676767473727374757473757778787776757471707270
..................................................7071737578797876767675737272737473737374757575737577787877757473717070
..................................................70707273757776767778787776747475757273747575747374767777757474737070
....................................................7070707274757778787877767474757572727374747272737476767574737070
..........................................................70727476787878777574757574707173737372727373747473727070
............................................................7071727475767574747572707070707272727272737373717070
..............................................................70707071737374737070....7070707071717171717070
..................................................................707070707071..............70707070707070
..
..
..
..
..
..
..
"""

# The pieces: sprite, its top left corner in the picture (column, row), the part of the picture it keeps (columns
# c0..c1, rows r0..r1: the overlaps split in their middles).
PIECES = [(39, (0, 14), (0, 24, 14, 42)), (77, (0, 42), (0, 24, 42, 63)), (96, (0, 56), (0, 24, 63, 84)),
          (22, (24, 0), (24, 42, 0, 28)), (23, (36, 0), (42, 60, 0, 28)),
          (60, (24, 28), (24, 42, 28, 56)), (61, (36, 28), (42, 60, 28, 56)),
          (98, (24, 56), (24, 42, 56, 77)), (99, (36, 56), (42, 60, 56, 77)),
          (117, (24, 70), (24, 42, 77, 98)), (118, (36, 70), (42, 60, 77, 98)),
          (44, (60, 14), (60, 84, 14, 42)), (82, (60, 42), (60, 84, 42, 63)), (101, (60, 56), (60, 84, 63, 84))]

# Heights: the floor at the outline and its rise over FALL; the body: per shade of the broad heat; the fine streaks.
FLOOR, RISE, FALL = 0.5, 1.6, 1.6
BODY = 0.5                        # per shade of the heat blurred over BROAD pixels
BROAD, FINE = 2.2, 0.55
STREAK = 0.38                     # per shade of the fine heat over the broad
TOP_HEAT = 1.8                    # the top this many shades hotter than drawn (the camera sees mostly the top)


# The heat bands: (lowest heat, palette index, emission strength in the palette colour): polish_fire_wall.py's bands
# (heat as the sprites' shades of the fire ramp, 7), the low ones glowing a little more (this is a molten mass, its
# dark red body glowing, not flames over the ground), all well under 1: the game's bloom brightens them further.
BANDS = [(-99.0, 0x72, 0.2), (3.5, 0x74, 0.24), (5.0, 0x75, 0.27), (6.0, 0x76, 0.3), (7.0, 0x77, 0.33),
         (8.0, 0x78, 0.36), (9.0, 0x79, 0.4), (10.0, 0x7a, 0.43), (11.0, 0x7b, 0.47), (12.0, 0x7c, 0.5),
         (13.0, 0x7d, 0.55), (14.0, 0x7e, 0.6), (14.8, 0x7f, 0.65)]


def materials():
    """The bands' materials: (lowest heat, material). Fire has no gloss to speak of."""
    pal = k.level_palette()
    return [(lowest, k.material("core_fire_%02x" % index, palette=index, metallic=0.0, roughness=0.85,
                                emission=pal[index], emission_strength=glow))
            for lowest, index, glow in BANDS]


def grid(left, top, w, h, offset=0.0):
    nx, ny = int(round(w / STEP)), int(round(h / STEP))
    count = (nx + 1, ny + 1) if offset == 0.0 else (nx, ny)
    xs = left + offset + STEP * np.arange(count[0])
    ys = top - h + offset + STEP * np.arange(count[1])
    return np.meshgrid(xs, ys)


class Fire:
    def __init__(self):
        rows = parse(FIRE_ART)
        self.pic = Pic([row + [None] * (W - len(row)) for row in rows], LEFT, TOP)
        a = self.pic.a
        mask = (a >= 0).astype(float)
        shade = np.where(a >= 0, a & 15, 0).astype(float)
        self.soft = blur(mask, 0.6)
        den_b, den_f = np.maximum(blur(mask, BROAD), 1e-6), np.maximum(blur(mask, FINE), 1e-6)
        self.broad = blur(shade, BROAD) / den_b
        self.fine = blur(shade, FINE) / den_f
        self.X, self.Y = grid(LEFT, TOP, W, H)
        inside = self.pic.sample(self.soft, self.X, self.Y) > 0.5
        t = np.clip(chamfer(inside, STEP) / FALL, 0.0, 1.0)
        edge = np.sqrt(t * (2.0 - t))
        b = self.pic.sample(self.broad, self.X, self.Y)
        f = self.pic.sample(self.fine, self.X, self.Y)
        self.Z = FLOOR + RISE * edge + edge * (BODY * b + STREAK * (f - b))
        self.Z = np.maximum(self.Z, 0.3)
        gy, gx = np.gradient(self.Z, STEP)
        n = np.stack([-gx, -gy, np.ones_like(gx)], -1)
        self.N = n / np.linalg.norm(n, axis=-1)[..., None]
        CX, CY = grid(LEFT, TOP, W, H, STEP / 2)
        self.cell_in = self.pic.sample(self.soft, CX, CY) > 0.5
        self.box = (LEFT, LEFT + W, TOP - H, TOP)

    def plate(self):
        gw.STEP = STEP  # Plate reads polish_gyges_wall's STEP: the fire's grid

        def top(X, Y):
            i = np.round((X - self.box[0]) / STEP).astype(int)
            j = np.round((Y - self.box[2]) / STEP).astype(int)
            return self.Z[j, i]

        def cells(X, Y):
            i = np.clip(np.floor((X - self.box[0]) / STEP).astype(int), 0, self.cell_in.shape[1] - 1)
            j = np.clip(np.floor((Y - self.box[2]) / STEP).astype(int), 0, self.cell_in.shape[0] - 1)
            return self.cell_in[j, i]
        return Plate(self.box, top, cells=cells)

    def heat(self, x, y, z, top):
        h = float(self.pic.sample(self.fine, np.array([x]), np.array([y]))[0])
        return h + (TOP_HEAT if top else -1.0)

    def normal(self, x, y):
        """The heightfield's normal at a point (bilinear between the grid's)."""
        fi = min(max((x - self.box[0]) / STEP, 0.0), self.Z.shape[1] - 1.001)
        fj = min(max((y - self.box[2]) / STEP, 0.0), self.Z.shape[0] - 1.001)
        i, j = int(fi), int(fj)
        ti, tj = fi - i, fj - j
        n = (self.N[j, i] * (1 - ti) + self.N[j, i + 1] * ti) * (1 - tj) + \
            (self.N[j + 1, i] * (1 - ti) + self.N[j + 1, i + 1] * ti) * tj
        return Vector(tuple(n)).normalized()


def finish(fire, obj):
    """The banded piece's normals: the heightfield's on its top, flat on its walls."""
    mesh = obj.data
    normals = []
    for poly in mesh.polygons:
        flat = abs(poly.normal.z) < 0.35
        for li in poly.loop_indices:
            v = mesh.vertices[mesh.loops[li].vertex_index].co
            normals.append(tuple(poly.normal) if flat or v.z < 0.05 else tuple(fire.normal(v.x, v.y)))
    mesh.polygons.foreach_set("use_smooth", [True] * len(mesh.polygons))
    mesh.normals_split_custom_set(normals)
    mesh.update()


def keep_coverage(fire, keep):
    """Which pixels of the kept part the cells cover (in the picture's plane: as the camera sees it)."""
    c0, c1, r0, r1 = keep
    out = []
    for r in range(r0, r1):
        row = []
        for c in range(c0, c1):
            n = 0
            for dj in (0.25, 0.75):
                for di in (0.25, 0.75):
                    i = int(math.floor((c + di) / STEP))
                    j = int(math.floor((H - r - dj) / STEP))
                    n += bool(fire.cell_in[min(j, fire.cell_in.shape[0] - 1), min(i, fire.cell_in.shape[1] - 1)])
            row.append(n >= 2)
        out.append(row)
    return out


def keep_mask(sheet, sprite, at, keep):
    """The sprite's own pixels in the part of the picture its piece keeps."""
    m = k.sprite_mask(sheet, sprite)
    c0, c1, r0, r1 = keep
    return [[m[r - at[1]][c - at[0]] for c in range(c0, c1)] for r in range(r0, r1)]


def build():
    options = k.args()
    k.reset()
    bpy.context.scene.view_settings.view_transform = "Standard"
    fire = Fire()
    print("fire: z %.2f..%.2f" % (fire.Z.min(), fire.Z.max()))
    plate = fire.plate()
    bands = materials()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    sheet = os.path.join(options["check"], "enemy_3.png") if "check" in options else None
    for sprite, at, keep in PIECES:
        name = "core_fire_%d" % sprite
        if only and name not in only:
            continue
        c0, c1, r0, r1 = keep
        x0, x1, y0, y1 = LEFT + c0, LEFT + c1, TOP - r1, TOP - r0
        e = 1e-6
        obj, kinds, _ = plate.mesh(name, lambda X, Y: (X > x0 + e) & (X < x1 - e) & (Y > y0 + e) & (Y < y1 - e))
        mesh = obj.data
        values = [fire.heat(v.co.x, v.co.y, v.co.z, v.co.z > 0.05) for v in mesh.vertices]
        band_split(obj, values, bands)
        finish(fire, obj)
        shear_to_camera([obj])
        cx, cy = LEFT + at[0] + 12.0, TOP - at[1] - 14.0
        obj.data.transform(Matrix.Translation((-cx, -cy, 0.0)))
        parts = triangulate([obj])
        bpy.context.view_layer.update()
        if sheet:
            mk.compare("%s (3 %d, its part, as the camera sees it)" % (name, sprite), keep_coverage(fire, keep),
                       keep_mask(sheet, sprite, at, keep))
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts)
        for o in parts:
            bpy.data.objects.remove(o)


if __name__ == "__main__":
    build()
