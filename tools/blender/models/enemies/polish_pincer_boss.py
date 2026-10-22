"""FLEET's and STATION's pincer boss (sheet K: the left arm 161 163 199 237 238, the right arm 165 167 205 242 243, the
machine between them 153 above 191; twelve 2x2 sprites the level events put together), the machine's core heating
(frames 155 157 159) and its lamp flashing (193); polished (2026-10-22, round 36). It replaces wave1_d.py's pincer
(the arms: outlines inflated into tubes, pixels in wave1_d_art.py's CLAW, kit wave1_d_shapes.py) and
wave3_o_machines.py's pincer_core (the machine: pixel-art pillows; its helmet(), core_unit(), crossbar()).

Where it appears (tools/content/tyrevents.py 3 FLEET t 0, 5 STATION t 2500): sky enemies, all coming down at 2 pixels a
tick, in the level's layout (sprite top left corners): the left arm (link 57: 722-726, STATION 1044-1048) 161 at
(x, y - 84), 163 at (x + 24, y - 84), 199 at (x, y - 56), 237 at (x, y - 28), 238 at (x + 12, y - 28); the right arm
(link 58: 727-731, STATION 1049-1053) 165 at (x + 24, y - 84) (STATION: x + 34), 167 at (x + 48, y - 84), 205 at
(x + 48, y - 56), 242 at (x + 36, y - 28), 243 at (x + 48, y - 28); the machine (link 59: 732, 733) 153 at
(x + 24, y - 84), 191 at (x + 24, y - 56) (FLEET x = 100, STATION 120); a column of six crimson orbs (734, K 195,
polish_orb_crimson.py) follows over the machine. So 163, 165 and 153 lie on one another (the machine drawn last: its
sleeves over the arms' gun tubes), 237 and 238 overlap by half (as do 242 243): the sheet draws the arms 24 pixels
further apart, the levels close them round the machine. Then the arms open (event 19: link 57 x speed -1, link 58 +1
for 10 ticks) and close again over and over while the machine fires (event 31), the whole swaying from side to side
(event 20). The arms' pieces have armour 255 (never destroyed), the machine's 50 (dgr 0: no damaged look); 732 and 733
animate when they fire (animate 2: 153 155 155 157 157 159 159 157 157 155 155 153; 191 191 191 191 193 193 193 193
191 ...): frame models (no other enemy, launched ones included, shows K 155 157 159 193; K 195 is the orbs').
The right arm is the left one's pixels mirrored about the middle of the machine's column 12 (IoU 0.99), the machine
its own mirror image (but for its shading): built symmetric about x = 0.5.

As the sprites and their 4x upscales draw it (the closed layout's picture, 72 x 84, columns and rows): the machine is
FLEET's grey helmet (K 276's top half, polish_k_pod.py: its crown, grille, rails and seams; here with a solid cap
where the pod has a handle) over the red core between its two sleeves with its two grey arms and its glowing neck
reaching down to a crossbar (K 281's core unit upside down, polish_k_turret.py), a red lamp in the crossbar's middle,
two long legs from its ends down the screen (columns 25-27 and 45-47 of rows 30-46). Each arm a heavy grey beam bent
like a C round the machine: its shoulder at the top (columns 9-19 of rows 15-27) with a thick gun tube reaching in to
the machine's sleeve (rows 14-21) and a thin pipe over it, hooked up from the shoulder (rows 8-14), the beam down the
side (columns 1-12) with a red light strip on its inner edge (columns 9-11 of rows 42-51), bending down to the
jaw at the bottom (columns 8-25 of rows 60-82): a glowing red plate on its inner face (columns 15-23 of rows 64-73),
and a red ribbed coil pointing across to the other jaw's (columns 26-34 of rows 73-79).

Built as such a machine: the beam a constrained Delaunay top over its outline (polish_ring_machine.relief; the
outline through the midpoints of the sprite's boundary edges, rounded), its edge rounded over R_EDGE, its top crowned,
the shoulder raised to hold the tube, recesses where the lights are; the light strip and the plate glowing lenses in
their recesses, banded by heat (polish_orb_red.band_split); the tube lathed (a root segment with a collar, a groove,
the muzzle segment, a dark bore), the thin pipe a tube along its hook, the coil lathed (a collar, five ribs). The
machine: polish_k_pod.helmet() (its handle replaced by a solid cap), polish_k_turret's core, arms and neck mirrored
up the screen, sleeves of its kind with a bore for the arms' tubes (radius TUBE_R < BORE_R: the tubes slide in and
out as the arms move); the crossbar a bevelled prism with rounded knuckles at its ends, the lamp's housing a ring over
its outline round a dark niche, the lamp a lens banded by heat, the legs tapering tubes with knee rings and round
feet. Heights: z 0 the sky
plane; the beams' tops 6.2, the shoulders' 8.6, the tubes' axis 5.2 (the sleeves' too), the core's top 10.3 (as
the turret's).

The pieces are cut in the picture's plane along the sprites' edges (237 | 238 at x -12, 242 | 243 at x 12: each
piece holds what lies in its own part of the overlap), each moved so that its sprite's middle is its origin, then
sheared along the game camera's line of sight (polish_fleet_walker.export_pieces).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up. The whole's origin is the closed
picture's middle (its pixel edge 36, 42): column c's left edge is x = c - 36, row r's top edge y = 42 - r; a piece
whose sprite's top left pixel is (c0, r0) has its origin at (c0 - 24, 28 - r0). The machine's columns are the
sprite frame's of polish_k_pod/polish_k_turret (x = c - 12 of its own columns); its rows: K 153's y + 28.

Replaces wave1_d.py (the pincer was all it still built: delete it) and wave1_d_art.py (its CLAW; MAST is read by
nothing since the CAMANIS masts moved to polish_camanis_boss.py: delete it), and wave3_o_machines.py's pincer_core
(with polish_k_lampgun.py taking its k_lampgun: delete wave3_o_machines.py; see polish_k_lampgun.py for wave3_o*).
wave1_d_shapes.py stays (many kits import it).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes as the
camera sees them against enemy_K.png), --preview <prefix> --pieces 1 (each piece's top and 3/4 views), --only
<model,...> (or the groups arms, machine).
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
import polish_k_pod as kp  # noqa: E402
import polish_k_turret as kt  # noqa: E402
from polish_k_pod import triangulate, mirror_y  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_ring_machine import relief, round_edge  # noqa: E402
from polish_gyges_wall import parse  # noqa: E402
import polish_fleet_walker as fw  # noqa: E402  (export_pieces, shear_to_camera, paint_faces, rect_sd, poly_sd)

AXIS = 0.5                        # the mirror line (the middle of the machine's column 12)
LEFT, TOP = -36.0, 42.0           # the picture's top left corner in the plane

# --- Materials ------------------------------------------------------------------------------------------------------


def heat_glow(index):
    """The emission strength of a red (ramp 7) shade: the hotter, the stronger, well under 1."""
    return min(0.64, 0.12 + 0.034 * (index - 0x70))


def materials():
    glow = k.level_palette()

    def mat(name, index, metallic=0.55, roughness=0.32):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)
    m = {
        # the k family's steel (polish_k_pod, polish_k_turret use these keys)
        "plate": mat("kpin_plate", 0x0a), "grey": mat("kpin_grey", 0x09), "side": mat("kpin_side", 0x07, 0.55, 0.36),
        "light": mat("kpin_light", 0x0b, 0.55, 0.28), "bright": mat("kpin_bright", 0x0d, 0.55, 0.25),
        "groove": mat("kpin_groove", 0x05, 0.5, 0.42), "belt": mat("kpin_belt", 0x03, 0.45, 0.5),
        "slot": mat("kpin_slot", 0x03, 0.45, 0.45), "dark": mat("kpin_dark", 0x02, 0.4, 0.5),
        "shade": mat("kpin_shade", 0x06, 0.55, 0.36), "mid": mat("kpin_mid", 0x08, 0.55, 0.34),
        "hi": mat("kpin_hi", 0x0c, 0.55, 0.26),
    }
    for index in range(0x70, 0x80):
        m[("core", index)] = k.material(f"kpin_red_{index:x}", palette=index, metallic=0.1, roughness=0.2,
                                        emission=glow[index], emission_strength=heat_glow(index))
    return m


# --- The left arm ---------------------------------------------------------------------------------------------------
# Its pixels (the picture's columns 0-35 of rows 8-82: K 161 163 199 237 238), the sprite's palette indices.
ARM_ROW0 = 8
ARM = """
................................0101010101010101010101010101010101010101
............................01010809070707070707070707070707070707070501
..........................01070b0701010101010101010101010101010101010101
........................01070d0601
......................01070a0601
......................01080601
......................0104030101....010101010101010101010101010101010101
....................010809090808010107050b090909090909090909090909090701
..................01080a0a0807040507090607060606060709090909090909090701
..................01090e09070706050809090a0a0a0a0b0406060606040302030401
..................01080c09090706060909090909090909050b0a0909090909090701
................0101090b090807070809090a05040404040105040404040404040301
............01010909090b0808080808090b0604040404030104040404040404040301
..010101010109090909090b09090908090b060501010101010101010101010101010101
..010e0b06090909090a0b0c0a0909090b070501
..010b0905090a0b0b0c0a0a0909090b060501
..010b07060b0b0c0b08080808080b060501
..010a060b0d0b0907060c060b07060501
..0109060c0b09070d05090409060501
..0109060c0a070705010101010101
..0109060d0a070c0801
..0109070c0906060601
..0109070b09070d0a01
..0109070b09070a0a0901
..0109070b0908070c090901
..0109070b090907080b0a0901
..0109070b09090907060c0a0901
..0109080b09090909060a0c0901
..0109090b0909090907090c0901
..0109090a0909090907090d0a01
..0109090a0909090907080807
..0109090a080909090602040401
..0109090a0709090802040501
..0109090a0609090203030401
..0109090a0609080304037101
..0109090a0609080203027201
..010809090609080173017301
..010709090609090174017401
..010709090509090175707401
..010709090409090175707401
..010609090409090175727501
..010508090409090175737901
..010408090405050177727501
..0102070904090b0174017401
..0101060903050401730101
....010408040a0b090101
....010307060e0e0c01
......0106060d0b0d0b01
......0103020c0a0b0c01
........01020b0a0a0b0a01
........01030a0a0a0a0c01
..........0101030404040401
..........0101040403030701
............0103060605070701
............0102050605050701
..............0103060605060701
..............010104060505080171010101
................010205060506077476777501
................01020206050507747676787501
..................01010406050607747578797501
..................01020206050507747475787a7401
....................01010406050507747575777c7201
....................0101020605050774747474797301
......................0103070a0d0d0b73737376730101010101
......................0103060a09090a73737376730171757801
........................0104080a09090b01737673017174760178..78..78..78
........................0105060a09090a01010101010101767175717571757175
..........................0106080a090a0a0a0d080a0e01777277727772777276
............................0106080a0909090c04080b017b737a737a73797379
..............................0105090a09090c05090a01737073707370737073
................................0107090a090b04040601737073707370737073
..................................0106090a0d0c0c0e0173..73..73..73..73
....................................01060708080807017301
......................................010404050607010101
........................................010101010101
"""


def arm_art():
    rows = parse(ARM)
    width = max(len(r) for r in rows)
    a = np.full((ARM_ROW0 + len(rows), 36), -1, int)
    for i, row in enumerate(rows):
        for c, v in enumerate(row[:36]):
            a[ARM_ROW0 + i, c] = -1 if v is None else v
    return a


def arm_masks():
    """The arm's parts as pixel masks of the picture (84 rows, 36 columns): the beam (with its shoulder, the jaw and
    the lights' pixels), the light strip and the jaw's plate (its red pixels)."""
    a = arm_art()
    h, w = a.shape
    rr, cc = np.mgrid[0:h, 0:w]
    px = a >= 0
    pipe = px & (((rr <= 10) & (cc >= 16)) | ((rr <= 14) & (cc <= 16) & (rr >= 8) & ~((rr == 14) & (cc <= 10))))
    tube = px & (rr >= 14) & (rr <= 21) & (cc >= 17)
    coil = px & (((rr >= 72) & (rr <= 80) & (cc >= 26)) | ((rr >= 72) & (rr <= 73) & (cc >= 24)))
    beam = px & ~pipe & ~tube & ~coil
    red = (a >> 4) == 7
    strip = beam & red & (rr >= 40) & (rr <= 53)
    plate = beam & red & (rr >= 62) & (rr <= 75)
    return beam, strip, plate


# The beam's heights: its edge rounded (from Z_EDGE at the outline up EDGE_UP over R_EDGE), then a low roof rising
# ROOF_SLOPE per pixel inwards to a rounded crest along its middle (the inside distance blurred), at most Z_CAP; the
# shoulder (y over SHOULDER_Y) raised SHOULDER_UP more to hold the tube; the lights' recesses' floor.
Z_EDGE, EDGE_UP, R_EDGE, ROOF_SLOPE, Z_CAP = 2.2, 1.6, 1.1, 0.5, 7.0
Z_TOP = 6.2
SHOULDER_UP, SHOULDER_Y = 1.6, (13.4, 17.4)
Z_BOTTOM = -1.2
Z_RECESS = 3.3
# The thick tube: its axis (y, z), its profile along x from the shoulder: (x, radius) (x of the left arm's).
TUBE_Y, TUBE_Z = 24.0, 5.2
TUBE_R = 3.95
TUBE = [(-21.0, 3.4), (-20.2, 3.8), (-18.6, 3.8), (-18.4, 4.1), (-16.4, 4.1), (-16.2, 3.8), (-11.4, 3.8),
        (-11.2, 3.35), (-10.6, 3.35), (-10.4, 3.95), (-0.6, 3.95), (-0.3, 3.55), (-0.25, 2.5)]
TUBE_GROOVE = (-11.3, -10.5)      # the dark groove between its segments (column 25)
BORE_DEPTH = 1.2
# The thin pipe: its path (x, y, z) from inside the shoulder up its hook and in under the helmet; its radius.
PIPE = [(-22.6, 26.2, 6.4), (-22.5, 27.6, 6.0), (-22.4, 28.6, 5.0), (-22.1, 29.6, 3.6), (-21.5, 30.6, 2.3),
        (-20.4, 31.6, 1.4), (-19.0, 32.3, 1.0), (-17.4, 32.5, 0.9), (-9.0, 32.5, 0.9), (-0.6, 32.5, 0.9)]
PIPE_R = 1.5
# The coil at the jaw's tip: its axis (y, z), the collar and the ribs along x.
COIL_Y, COIL_Z = -34.5, 3.6
COIL_CORE = 2.7
COIL_COLLAR = (-11.6, -9.9, 3.7)
COIL_RIBS = [-9.5, -7.5, -5.5, -3.5, -1.5]
COIL_RIB = (0.45, 3.5)            # half-width, radius
COIL_END = -0.9


def beam(m, masks):
    """The beam: a relief over its outline, its edge rounded, its top crowned, the shoulder raised, the lights'
    recesses sunk; painted by how its faces meet the sun."""
    body, strip, plate = masks
    loops = fw.mask_loops(body, LEFT, TOP, chaikin=1)
    loops = [p for p in loops if abs(fw.area(p)) > 4.0]
    lights = [p for p in fw.mask_loops(strip, LEFT, TOP, 1, sigma=0.5) + fw.mask_loops(plate, LEFT, TOP, 1, sigma=0.5)
              if abs(fw.area(p)) > 1.0]
    inside = fw.InsideDistance(loops)

    def light_d(x, y):
        return min(fw.poly_sd(x, y, p) for p in lights)

    def height(x, y, d):
        roof = ROOF_SLOPE * max(0.0, inside(x, y) - R_EDGE)
        z = min(Z_CAP, Z_EDGE + EDGE_UP * round_edge(d, R_EDGE) + roof)
        s = fw.smoothstep(SHOULDER_Y[0], SHOULDER_Y[1], y)
        z += SHOULDER_UP * s * round_edge(d, R_EDGE * 1.5)
        ld = light_d(x, y)
        if ld < 0.35:
            z = min(z, Z_RECESS + (z - Z_RECESS) * max(0.0, ld / 0.35))
        return z
    borders = [(lambda x, y, d: -light_d(x, y), -0.35), (lambda x, y, d: -light_d(x, y), 0.0)]

    def paint(x, y, d):
        return "recess" if light_d(x, y) < 0.0 else "top"
    mats = {"top": m["grey"], "side": m["groove"], "recess": m[("core", 0x71)]}
    obj = relief("arm_beam", loops, height, mats, paint=paint, side="side", bottom=Z_BOTTOM, spacing=0.45,
                 borders=borders, smooth_angle=40.0, band=3.0)

    def pick(c, n):
        if light_d(c.x, c.y) < 0.02:
            return m[("core", 0x71)]
        if n.z < 0.2:
            return m["groove"]
        lit = n.dot(fw.LIGHT)
        return (m["hi"] if lit > 0.93 else m["light"] if lit > 0.8 else m["plate"] if lit > 0.62 else
                m["mid"] if lit > 0.42 else m["shade"])
    fw.paint_faces(obj, pick)
    return obj, lights


def lenses(m, lights):
    """The light strip and the jaw's plate: glowing lenses filling their recesses, hottest along their middles."""
    parts = []
    for i, poly in enumerate(lights):
        region_d = lambda x, y, p=poly: -fw.poly_sd(x, y, p)
        xs = [p[0] for p in poly]
        ys = [p[1] for p in poly]
        half = 0.5 * min(max(xs) - min(xs), max(ys) - min(ys))

        def height(x, y, d, half=half):
            return Z_RECESS + 0.2 + (Z_TOP - 0.5 - Z_RECESS) * round_edge(d, max(0.6, half * 0.9))
        mats = {"top": m[("core", 0x75)], "side": m[("core", 0x71)]}
        obj = relief(f"arm_light{i}", [poly], height, mats, side="side", bottom=Z_RECESS - 0.4, spacing=0.3,
                     smooth_angle=70.0)
        values = []
        for v in obj.data.vertices:
            t = min(1.0, max(0.0, region_d(v.co.x, v.co.y) / max(0.5, half)))
            values.append(t)
        band_split(obj, values, [(-9.0, m[("core", 0x72)]), (0.25, m[("core", 0x75)]), (0.55, m[("core", 0x78)]),
                                 (0.8, m[("core", 0x7b)])])
        k.smooth(obj, 70)
        parts.append(obj)
    return parts


def lathe_x(name, profile, axis_y, axis_z, mat, segments=24):
    """A round part along x: profile [(x, radius), ...] in increasing x, its ends closed to the axis."""
    rings = []
    for x, r in profile:
        rings.append([Vector((x, axis_y + r * math.cos(2 * math.pi * j / segments),
                              axis_z + r * math.sin(2 * math.pi * j / segments))) for j in range(segments)])
    return k.loft(name, rings, mat, start_point=(profile[0][0], axis_y, axis_z),
                  end_point=(profile[-1][0], axis_y, axis_z))


def tube(m):
    """The thick gun tube from the shoulder to its muzzle: lathed along x, its groove dark, a dark bore."""
    obj = lathe_x("arm_tube", TUBE, TUBE_Y, TUBE_Z, m["grey"], 28)
    k.smooth(obj, 40)

    def pick(c, n):
        if TUBE_GROOVE[0] < c.x < TUBE_GROOVE[1]:
            return m["groove"]
        if c.x > TUBE[-2][0] + 0.05:
            return m["dark"]                                   # the muzzle's face, the bore
        if -18.5 < c.x < -16.3:
            return m["light"]                                  # the collar
        return None
    fw.paint_faces(obj, pick)
    bore = lathe_x("arm_bore", [(TUBE[-1][0] - BORE_DEPTH, 2.35), (TUBE[-1][0] + 0.02, 2.35)], TUBE_Y, TUBE_Z,
                   m["slot"], 20)
    return [obj, bore]


def pipe(m):
    """The thin pipe hooked up from the shoulder and in under the helmet's side."""
    pts = mk.chaikin(PIPE, 2, closed=False)
    obj = mk.tube("arm_pipe", pts, PIPE_R, m["grey"], 14)
    k.smooth(obj, 50)
    return [obj]


def coil(m):
    """The coil at the jaw's tip: a dark core, a collar against the jaw, five glowing ribs."""
    x0 = COIL_COLLAR[0] - 0.6
    core = lathe_x("arm_coil_core", [(x0, COIL_CORE), (COIL_END - 0.3, COIL_CORE), (COIL_END, COIL_CORE - 0.6),
                                     (COIL_END + 0.01, 0.01)], COIL_Y, COIL_Z, m[("core", 0x71)], 20)
    k.smooth(core, 50)
    parts = [core]
    a, b, r = COIL_COLLAR
    collar = lathe_x("arm_coil_collar", [(a, r - 0.6), (a + 0.3, r), (b - 0.3, r), (b, r - 0.5)], COIL_Y, COIL_Z,
                     m[("core", 0x74)], 24)
    k.smooth(collar, 50)
    parts.append(collar)
    hw, rr = COIL_RIB
    for i, cx in enumerate(COIL_RIBS):
        rib = lathe_x(f"arm_coil_rib{i}", [(cx - hw, COIL_CORE), (cx - hw * 0.6, rr), (cx + hw * 0.6, rr),
                                          (cx + hw, COIL_CORE)], COIL_Y, COIL_Z, m[("core", 0x77)], 24)
        band_split(rib, [(v.co.z - COIL_Z) / rr for v in rib.data.vertices],
                   [(-9.0, m[("core", 0x73)]), (0.15, m[("core", 0x77)]), (0.7, m[("core", 0x7a)])])
        k.smooth(rib, 50)
        parts.append(rib)
    return parts


def left_arm(m):
    masks = arm_masks()
    body, lights = beam(m, masks)
    parts = [body] + lenses(m, lights) + tube(m) + pipe(m) + coil(m)
    for obj in parts:
        mk.apply(obj)
    return parts


def mirrored(objects, suffix):
    """Copies of objects mirrored about x = AXIS (faces turned back out, custom normals mirrored)."""
    out = []
    flip = Matrix.Translation((2 * AXIS, 0, 0)) @ Matrix.Scale(-1, 4, (1, 0, 0))
    for obj in objects:
        c = obj.copy()
        c.data = obj.data.copy()
        c.name = obj.name.replace("arm_", "rarm_") + suffix
        bpy.context.scene.collection.objects.link(c)
        mesh = c.data
        corner = {}
        for poly in mesh.polygons:
            for li in poly.loop_indices:
                n = mesh.corner_normals[li].vector
                corner[(poly.index, mesh.loops[li].vertex_index)] = (-n.x, n.y, n.z)
        mesh.transform(flip)
        mesh.flip_normals()
        normals = [None] * len(mesh.loops)
        for poly in mesh.polygons:
            for li in poly.loop_indices:
                normals[li] = corner[(poly.index, mesh.loops[li].vertex_index)]
        mesh.normals_split_custom_set(normals)
        mesh.update()
        out.append(c)
    return out


# --- The machine ----------------------------------------------------------------------------------------------------
# polish_k_pod's helmet (K 276's top half, here K 153's rows 0-12): moved up by 28 (K 153's y + 28 in the whole); its
# handle (posts and bar) replaced by a solid cap over the same span (K 153's rows 0-2).
UP = 28.0
CAP = (-5.9, 6.9, 10.0, 13.9, 1.1, 2.9)          # x0, x1, y0, y1, corner radius, top (K 153's frame)
# The sleeves (K 153's rows 14-22): polish_k_turret's profile, with a bore at the outer end for the arms' tubes.
BORE_R = 4.08
BORE_IN = 2.6                                     # how deep the bore goes
# The crossbar (the whole's rows 28-38; x as the machine's columns, x = c - 12): the bar its arms and neck end on (its
# plan, its heights), the knuckles at its ends, the lamp's housing under its middle (its plan and the niche's), the
# legs (their axis' x, from y, to y, radii at the top and the foot, the knee ring's y).
BAR = [(-7.4, 11.2), (8.4, 11.2), (8.4, 13.2), (7.0, 14.2), (-6.0, 14.2), (-7.4, 13.2)]
BAR_Z = (-0.6, 3.7)
KNUCKLE = (-11.6, -5.7, 4.7, 12.9, 4.5, 1.7)        # x0, x1, y0, y1, top, bevel
HOUSING = [(-6.6, 11.6), (7.6, 11.6), (5.0, 3.2), (-4.0, 3.2)]
NICHE = [(-2.3, 11.8), (3.3, 11.8), (2.7, 5.0), (-1.7, 5.0)]
HOUSING_Z, NICHE_Z = 3.1, 0.3
LEG = (-9.5, 8.0, -4.6, 1.55, 1.15, -2.4)
LIP = (-11.9, 11.9, 27.2, 29.1, 3.1)              # the helmet's lower lip over the sleeves (K 153's row 13)
LAMP = (0.5, 8.1, 1.75, 3.0, 1.6)                  # the 191 lamp: x, y, radii (x, y, z): in the niche
LAMP_LIT = (0.5, 7.8, 2.45, 3.45, 2.0)             # the 193 lamp, swollen


def helmet(m):
    parts = kp.helmet(m, "helm")
    keep = []
    for obj in parts:
        if "_post" in obj.name or "_bar" in obj.name or obj.name.endswith("_cap"):
            mesh = obj.data
            bpy.data.objects.remove(obj)
            bpy.data.meshes.remove(mesh)
            continue
        keep.append(obj)
    x0, x1, y0, y1, r, top = CAP
    cap = mk.prism("helm_cap", kp.rect(x0, x1, y0, y1, r), kp.BOTTOM + 2.0, top, m["plate"])
    mk.bevel(cap, 0.35, 2, 30)
    mk.shade(cap, 35)
    mk.paint(cap, lambda c, n: m["light"] if n.z > 0.8 else m["side"] if n.z < 0.3 else None)
    seam = mk.box("helm_cap_seam", x0 + 0.6, x1 - 0.6, 12.0, 12.45, top - 0.25, top + 0.06, m["groove"])
    keep += [cap, seam]
    mk.transform(keep, Matrix.Translation((0.0, UP, 0.0)))
    # The lower lip under the helmet's edge, between it and the sleeves' tops.
    lx0, lx1, ly0, ly1, ltop = LIP
    lip = mk.prism("helm_lip", kp.rect(lx0, lx1, ly0, ly1, 0.5), kp.BOTTOM + 1.0, ltop, m["side"])
    mk.bevel(lip, 0.3, 2, 30)
    mk.shade(lip, 35)
    mk.paint(lip, lambda c, n: m["light"] if (n.z < 0.8 and n.y > 0.3) else None)
    keep.append(lip)
    return keep


def core_bands(shift):
    return [(lo, min(0x7f, index + shift)) for lo, index, _ in kt.CORE_BANDS]


def core(m, shift=0):
    """polish_k_turret's core in its bands of heat, every band `shift` shades hotter (the frames), its dark hoop."""
    centre, radii, power = kt.CORE
    ball = kt.superellipsoid("mcore", centre, radii, power)
    band_split(ball, [kt.core_heat(v.co) for v in ball.data.vertices],
               [(lowest, m[("core", index)]) for lowest, index in core_bands(shift)])
    k.smooth(ball, 80)
    out, r = kt.HOOP
    ring = []
    for j in range(64):
        a = 2 * math.pi * j / 64
        ux, uy = mk.superellipse_point(a, power)
        ring.append((centre.x + (radii[0] + out) * ux, centre.y + (radii[1] + out) * uy, centre.z))
    hoop = mk.tube("mhoop", ring + ring[:1], r, m["groove"], 12, cap=False)
    k.smooth(hoop, 60)
    return [ball, hoop]


def sleeve(m, side):
    """polish_k_turret's sleeve with a bore in its outer end (the arms' tubes slide into it): lathed along x from the
    core's side to the sprite's edge, painted as the turret's; the bore dark."""
    inner = kt.SLEEVE_INNER[0] if side < 0 else kt.SLEEVE_INNER[1]
    edge = kt.EDGES[0] if side < 0 else kt.EDGES[1]
    length = abs(edge - inner)
    y, z = kt.SLEEVE_AXIS
    outer = list(kt.INNER_COLLAR) + [(length - d, r) for d, r in kt.OUTER_END[:-1]]
    # The bore: from the end face's rim in to BORE_IN deep, its bottom closed.
    profile = outer + [(length, BORE_R + 0.3), (length, BORE_R), (length - BORE_IN, BORE_R),
                       (length - BORE_IN - 0.01, 0.01)]
    rings = []
    for d, r in profile:
        x = inner + side * d
        rings.append([Vector((x, y + r * math.cos(2 * math.pi * j / 32), z + r * math.sin(2 * math.pi * j / 32)))
                      for j in range(32)])
    obj = k.loft(f"msleeve{side}", rings, m["grey"], start_point=(inner, y, z), cap_end=False)
    k.recalc_normals(obj)
    k.smooth(obj, 40)

    def pick(c, n):
        d = abs(c.x - inner)
        r = math.hypot(c.y - y, c.z - z)
        if d > length - BORE_IN - 0.05 and r < BORE_R + 0.05:
            return m["dark"]                                       # the bore
        if d < kt.INNER_COLLAR[-1][0] - 0.1:
            return m["light"]
        if length - kt.OUTER_END[0][0] + 0.05 < d < length - kt.OUTER_END[3][0] - 0.05:
            return m["groove"]
        if d > length - kt.OUTER_END[3][0] - 0.05:
            return m["side"] if d > length - 0.2 else m["light"]
        return None
    mk.paint(obj, pick)
    return obj


def neck(m, shift=0):
    """polish_k_turret's neck, its heat `shift` shades hotter."""
    y0, y1, r = kt.COLLAR
    collar = mk.tube("mneck_collar", [(kt.MID, yy, kt.NECK_Z) for yy in (y0, y0 + 0.2, y1 - 0.2, y1)], 1.0,
                     m["groove"], 24, radii=[r - 0.25, r, r, r - 0.3])
    k.smooth(collar, 50)
    obj = mk.tube("mneck", [(kt.MID, yy, kt.NECK_Z) for yy, _ in kt.NECK], 1.0, m[("core", 0x73)], 24,
                  radii=[rr for _, rr in kt.NECK])

    def heat(p):
        along = kt.NECK_HEAT[0][1]
        for (ya, ha), (yb, hb) in zip(kt.NECK_HEAT, kt.NECK_HEAT[1:]):
            if ya <= p.y <= yb:
                along = ha + (hb - ha) * (p.y - ya) / (yb - ya)
        if p.y > kt.NECK_HEAT[-1][0]:
            along = kt.NECK_HEAT[-1][1]
        up = (p.z - kt.NECK_Z) / max(1e-6, math.hypot(p.x - kt.MID, p.z - kt.NECK_Z))
        return along + kt.NECK_TOP * mk.smoothstep(0.2, 0.95, up) * mk.smoothstep(10.0, 12.0, p.y)
    band_split(obj, [heat(v.co) for v in obj.data.vertices],
               [(lowest, m[("core", min(0x7f, index + shift))]) for lowest, index in kt.NECK_BANDS])
    k.smooth(obj, 50)
    return [collar, obj]


def core_unit(m, shift=0):
    """The core, its sleeves, its arms (polish_k_turret's, without the yoke: here they reach the crossbar) and the
    neck, in K 281's frame; then mirrored up the screen and moved to K 153's place (y -> UP - y)."""
    before = set(mk.meshes())
    kt.arms(m)
    made = [o for o in mk.meshes() if o not in before]
    arms = []
    for o in made:
        if o.name.startswith("yoke"):
            mesh = o.data
            bpy.data.objects.remove(o)
            bpy.data.meshes.remove(mesh)
        else:
            arms.append(o)
    parts = core(m, shift) + [sleeve(m, -1), sleeve(m, 1)] + arms + neck(m, shift)
    for obj in parts:
        mk.apply(obj)
    mirror_y(parts)
    mk.transform(parts, Matrix.Translation((0.0, UP, 0.0)))
    return parts


def crossbar(m, lit=False, prefix="mbar", foot_y=None, knee=True):
    """The crossbar under the core (K 191, the whole's rows 28-38): a bevelled bar, lit along its back edge; rounded
    knuckles at its ends, the legs from them down the screen (tapering tubes, a ring at the knee, rounded feet); the
    lamp's housing under its middle, a dark niche in it and the lamp hanging in the niche, a glowing lens banded by heat
    (lit: the 193 frame, swollen and white-hot)."""
    parts = []
    z0, z1 = BAR_Z

    def lit_back(c, n):
        return m["light"] if (n.z < 0.8 and n.y > 0.3) else m["side"] if n.z < 0.3 else None
    bar = mk.prism(f"{prefix}", BAR, z0, z1, m["grey"])
    mk.bevel(bar, 0.45, 2, 30)
    mk.shade(bar, 35)
    mk.paint(bar, lit_back)
    parts.append(bar)
    bx0, bx1, by0, by1, btop, bbev = KNUCKLE
    lx, ly0, ly1, r0, r1, knee_y = LEG
    if foot_y is not None:
        ly1 = foot_y
    for side in (-1, 1):
        def X(x):
            return x if side < 0 else 2 * AXIS - x
        xs = sorted((X(bx0), X(bx1)))
        knuckle = mk.prism(f"{prefix}_knuckle{side}", kp.rect(xs[0], xs[1], by0, by1, 2.2), z0, btop, m["grey"])
        mk.bevel(knuckle, bbev, 4, 30)
        mk.shade(knuckle, 50)
        mk.paint(knuckle, lambda c, n: m["hi"] if n.dot(fw.LIGHT) > 0.9 else m["light"] if n.z > 0.85 else
                 m["side"] if n.z < 0.3 else None)
        parts.append(knuckle)
        # the leg: a tapering tube down the screen, its foot rounded
        steps = 12
        pts = [(X(lx), ly0 + (ly1 + r1 - ly0) * t / steps, 1.6 - 0.35 * t / steps) for t in range(steps + 1)]
        radii = [r0 + (r1 - r0) * t / steps for t in range(steps + 1)]
        leg = mk.tube(f"{prefix}_leg{side}", pts, 1.0, m["grey"], 16, radii=radii)
        k.smooth(leg, 50)
        parts.append(leg)
        foot = k.ellipsoid(f"{prefix}_foot{side}", (X(lx), ly1 + r1, pts[-1][2]), (r1, r1, r1), m["grey"], 16, 8)
        k.smooth(foot, 60)
        parts.append(foot)
        if knee:
            ring = mk.tube(f"{prefix}_knee{side}", [(X(lx), knee_y + 0.45, 1.33), (X(lx), knee_y - 0.45, 1.31)], 1.0,
                           m["light"], 16, radii=[r1 + 0.32, r1 + 0.3])
            k.smooth(ring, 50)
            parts.append(ring)
    # the lamp's housing: a ring over the outline round the niche, dark inside, the niche's floor
    def h_height(x, y, d):
        return HOUSING_Z - 0.6 * (1.0 - round_edge(d, 0.7))
    housing = relief(f"{prefix}_housing", [HOUSING, list(reversed(NICHE))], h_height, {"top": m["grey"],
                                                                                         "side": m["dark"]},
                     side="side", bottom=z0, spacing=0.35, smooth_angle=40.0)
    mk.paint(housing, lambda c, n: m["dark"] if fw.poly_sd(c.x, c.y, NICHE) < 0.25 else
             (m["light"] if n.dot(fw.LIGHT) > 0.85 else None))
    parts.append(housing)
    nx = [p[0] for p in NICHE]
    ny = [p[1] for p in NICHE]
    parts.append(mk.prism(f"{prefix}_niche", NICHE, z0, NICHE_Z, m["slot"]))
    lx_, ly_, rx, ry, rz = LAMP_LIT if lit else LAMP
    lens = k.ellipsoid(f"{prefix}_lamp", (lx_, ly_, NICHE_Z + 0.4), (rx, ry, rz), m[("core", 0x74)], 32, 16)
    hot = 0.25 if lit else 0.0

    def heat(p):
        # the sprite's lamp: hottest low in its middle (row 35 of 191, 34 of 193)
        u, v = (p.x - lx_) / rx, (p.y - (ly_ - ry * 0.25)) / ry
        return 1.0 - math.hypot(u, v) + hot
    bands = [(-9.0, 0x71), (0.2, 0x74), (0.45, 0x77), (0.65, 0x7a), (0.85, 0x7d)]
    if lit:
        bands = [(-9.0, 0x72), (0.2, 0x76), (0.45, 0x7a), (0.65, 0x7d), (0.85, 0x7f)]
    band_split(lens, [heat(v.co) for v in lens.data.vertices], [(lo, m[("core", idx)]) for lo, idx in bands])
    k.smooth(lens, 80)
    parts.append(lens)
    for obj in parts:
        mk.apply(obj)
    return parts


def machine(m, shift=0, lit=False):
    return helmet(m) + core_unit(m, shift) + crossbar(m, lit)


# --- Pieces ---------------------------------------------------------------------------------------------------------

def piece(name, sprite, c0, r0, x0=None, x1=None):
    """(name, sprite, box, origin, columns) of a piece whose sprite's top left pixel is (c0, r0) of the picture; its
    box the sprite's (or x0..x1 where pieces overlap: then only the sprite's columns in it are checked); the picture's
    edge pieces' boxes reach out past it."""
    bx0 = LEFT + c0 if x0 is None else x0
    bx1 = LEFT + c0 + 24 if x1 is None else x1
    by1, by0 = TOP - r0, TOP - r0 - 28
    origin = (LEFT + c0 + 12, TOP - r0 - 14)
    if c0 == 0:
        bx0 -= 10.0
    if c0 + 24 >= 72:
        bx1 += 10.0
    if r0 == 0:
        by1 += 10.0
    if r0 + 28 >= 84:
        by0 -= 10.0
    cols = (int(round(max(bx0, LEFT + c0) - (LEFT + c0))), int(round(min(bx1, LEFT + c0 + 24) - (LEFT + c0))))
    return (name, sprite, (bx0, bx1, by0, by1), origin, cols)


LEFT_PIECES = [piece("pincer_l_hook", 161, 0, 0), piece("pincer_l_tubes", 163, 24, 0),
               piece("pincer_l_side", 199, 0, 28), piece("pincer_l_jaw", 237, 0, 56, x1=-12.0),
               piece("pincer_l_coil", 238, 12, 56, x0=-12.0)]
RIGHT_PIECES = [piece("pincer_r_tubes", 165, 24, 0), piece("pincer_r_hook", 167, 48, 0),
                piece("pincer_r_side", 205, 48, 28), piece("pincer_r_coil", 242, 36, 56, x1=12.0),
                piece("pincer_r_jaw", 243, 48, 56, x0=12.0)]
MACHINE_TOP = [piece("pincer_core_top", 153, 24, 0)]
MACHINE_LEGS = [piece("pincer_core_legs", 191, 24, 28)]
HEAT_FRAMES = [(155, 2), (157, 6), (159, 8)]
GROUPS = {"arms": [p[0] for p in LEFT_PIECES + RIGHT_PIECES],
          "machine": ["pincer_core_top", "pincer_core_legs"] + ["pincer_core_top_%d" % f for f, _ in HEAT_FRAMES] +
          ["pincer_core_legs_193"]}


def cap_key(m):
    def cap_of(src):
        if src.name.startswith(("arm_light", "rarm_light", "arm_coil", "rarm_coil", "mcore", "mneck", "mbar_lamp")):
            return m[("core", 0x72)]
        return m["dark"]
    return cap_of


def build_arms(options, sheet, only):
    k.reset()
    m = materials()
    left = left_arm(m)
    right = mirrored(left, "")
    for obj in left + right:
        triangulate([obj])
    bpy.context.view_layer.update()
    bpy.context.scene.view_settings.view_transform = "Standard"
    whole = left + right
    low, high = mk.bounds(whole)
    print("== arms: %d triangles, x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (
        mk.triangles(whole), low.x, high.x, low.y, high.y, low.z, high.z))
    results = {}
    results.update(fw.export_pieces(left, LEFT_PIECES, cap_key(m), options, sheet, "K", only))
    results.update(fw.export_pieces(right, RIGHT_PIECES, cap_key(m), options, sheet, "K", only))
    return results, whole


def build_machine(options, sheet, only):
    results = {}
    variants = [("", 0, False, MACHINE_TOP + MACHINE_LEGS)]
    variants += [("_%d" % f, s, False, [(MACHINE_TOP[0][0] + "_%d" % f, f) + MACHINE_TOP[0][2:]])
                 for f, s in HEAT_FRAMES]
    variants += [("_193", 0, True, [(MACHINE_LEGS[0][0] + "_193", 193) + MACHINE_LEGS[0][2:]])]
    for suffix, shift, lit, pieces in variants:
        if only and not any(p[0] in only for p in pieces):
            continue
        k.reset()
        m = materials()
        whole = machine(m, shift, lit)
        triangulate(whole)
        bpy.context.view_layer.update()
        bpy.context.scene.view_settings.view_transform = "Standard"
        low, high = mk.bounds(whole)
        print("== machine%s: %d triangles, x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (
            suffix, mk.triangles(whole), low.x, high.x, low.y, high.y, low.z, high.z))
        results.update(fw.export_pieces(whole, pieces, cap_key(m), options, sheet, "K", only))
    return results


def build():
    options = k.args()
    only = None
    if "only" in options:
        only = set()
        for name in options["only"].split(","):
            only |= set(GROUPS.get(name, [name]))
    sheet = None
    if "check" in options:
        sheets = options["check"]
        sheet = os.path.join(sheets, "enemy_K.png") if os.path.isdir(sheets) else sheets
    results = {}
    if not only or any(n in only for n in GROUPS["arms"]):
        r, whole = build_arms(options, sheet, only)
        results.update(r)
    results.update(build_machine(options, sheet, only))
    if sheet:
        for name, score in results.items():
            if score is not None:
                print("overlap %-26s %.3f" % (name, score))


if __name__ == "__main__":
    build()
