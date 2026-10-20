"""BOTANY B's lilac stone (sheet 0 sprite 153, 2x2: a 19 x 19 stone in the 24 x 28 cell; enemy 820 on the ground of
BOTANY B; its animation 153 155 155 157 157 157 155 155 155 153), polished (2026-10-20; it replaces wave3_ai.py's
botany_stone(), a cluster of purple balls round a glowing cross of boxes). models.cfg: sprite 0 153 botany_stone yaw=0
glow=10:0.3:117 (unchanged), frame 0 155 botany_stone_155, frame 0 157 botany_stone_157. No other enemy shows these
three sprites; they are no other sprites' pixels mirrored or in other ramps (only each other: the same stone, the core
lit).

As the sprite and its 4x upscales draw it (columns and rows of the cell; lilacs of ramp 5): four rounded lobes of
polished stone, one in each quarter (columns 7-11 and 13-17 of rows 8-12 and 14-18, five pixels square, rounded), lit
at their upper left; between them a cross of narrow crevices (column 12, row 13) and at the end of each of its arms,
at the points of the stone's diamond, a knob, a small rounded nub against the lobes' ends with a pale bead on its top
(columns 10-14 of rows 4-7 and 19-22, columns 3-6 and 18-21 of rows 10-15). In the crevices a core: dark in 153 (the
crevices' purple), its middle glowing red in 155 (columns 11-13 of rows 11-15, 72-76), the whole cross in 157
(columns 8-16 of row 13 and column 12 of rows 9-17, 73-7b, yellow-hot in the middle). (The upscales make the lobes
eggs on the diagonals; the sprite's rounded squares keep the cross straight and the stone compact.)

Built as such a stone on the ground. The lobes and knobs are one solid, a signed distance on a grid STEP pixels apart,
its surface extracted (polish_rock_arch.surface_nets), smoothed and reduced to about TARGET triangles: each lobe a dome
over a rounded square (a superellipsoid: widest LOBE_Z up, curving in under it, an ellipse LOBE_UP high above it),
the crevice between neighbours a pixel wide at their widest and opening up between their domes, rocked by smooth
noise; the knobs ellipsoids against the lobes' ends, joined to them by a small fillet; a dark floor under it all (the
crevices' bottoms). The solid is painted in the sprite's lilacs (a shade lighter: the slanted camera sees them darker)
in bands of how its faces face (tops lightest, a highlight towards the sun, undersides and crevice walls dark), cut
along smooth contours (polish_orb_red.band_split). A pale bead on each knob. In the crevices the core, a four-armed
star of ember whose arms' tops show in the crevices and whose middle fills the pit where the lobes' corners meet,
painted in bands of the sprite's reds by the distance from its middle, glowing in their own colour (emission 0.08-0.6:
the bloom and the cfg's glow add). One model per frame: the same stone, the core's materials changed; every frame
carries a speck at PIN_Z (a triangle a thousandth of a pixel across, invisible), so the game, which centres a model in
height on the ground enemies' layer (4) and lifts it to 0.3 when it would reach lower, puts the stone on the ground and
every frame alike.

Origin at the sprite's centre (pixel 12, 14): the stone's middle is pixel (12, 13), x 0.5, y 0.5; +Y up the screen, +Z
up from the ground (z = 0).

Replaces wave3_ai.py's botany_stone() (its @kit.model("botany_stone", ...) function, STONE and SC, the botany_stone
lines of its docstring; steel(), shade_by_slope() and botany_beetle() stay) and wave3_ai_art.py's STONE and STONE_157
(nothing else reads them).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against
enemy_0.png's 153), --preview <prefix>, --only <name,...>.
"""
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_rock_arch import decimate, finish_whole, mesh_object, noise3, smax, surface_nets  # noqa: E402

CENTRE = Vector((0.5, 0.5, 0.0))     # the stone's middle: the sprite's pixel (12, 13)
# The lobes: one in each quarter, its middle LOBE_C0 from the stone's middle along both axes and LOBE_Z up, its plan a
# rounded square (a superellipse of power LOBE_P, half-size LOBE_HALF: CREVICE = 2 (LOBE_C0 - LOBE_HALF) between
# neighbours at their widest), domed (an ellipse LOBE_UP high above its widest, curving in under it).
LOBE_C0, LOBE_HALF, LOBE_P = 3.3, 2.8, 2.35
LOBE_Z, LOBE_UP = 1.3, 3.6
NOISE = ((0.13, 1.8), (0.05, 0.8))  # amplitude, scale (pixels)
# The knobs on the axes: their middles' distance from the stone's, half-sizes (along the axis, across, height), their
# middles' height; the bead on each (its distance, height, radius).
KNOB_R, KNOB_SIZE, KNOB_Z = 7.15, (1.8, 2.6, 2.0), 1.0
BEAD = (7.15, 2.8, 0.8)
FLOOR_R, FLOOR_TOP = 6.3, 0.5
# The core: the star's arms in the grooves (their length from the middle, their half-width, their top), its middle in
# the pit where the lobes' inner ends meet (radius, top).
ARM_LEN, ARM_W, ARM_TOP = 6.0, 0.9, 2.6
CORE_R, CORE_TOP = 1.9, 3.0
PIN_Z = 7.6
STEP = 0.12                          # the grid the solid is sampled on
TARGET = 3000                        # the solid's triangles

# The frames: (model, sprite, the core's bands: (largest distance from the middle, palette index, emission)).
FRAMES = [
    ("botany_stone", 153, [(99.0, 0x55, 0.0)]),
    ("botany_stone_155", 155, [(1.05, 0x76, 0.5), (1.9, 0x74, 0.35), (2.7, 0x72, 0.18), (99.0, 0x55, 0.0)]),
    ("botany_stone_157", 157, [(0.95, 0x7b, 0.6), (1.85, 0x78, 0.5), (2.8, 0x75, 0.38), (3.8, 0x74, 0.28),
                               (4.8, 0x73, 0.18), (99.0, 0x72, 0.08)]),
]
SUN = Vector((-0.6, 0.6, 1.0)).normalized()   # towards the game's sun


def materials():
    def mat(name, index, roughness=0.32):
        return k.material(name, palette=index, metallic=0.05, roughness=roughness)
    return {
        "floor": mat("stone_floor", 0x53, 0.6),
        "under": mat("stone_under", 0x56, 0.45),
        "side": mat("stone_side", 0x59, 0.36),
        "top": mat("stone_top", 0x5b, 0.3),
        "crown": mat("stone_crown", 0x5c, 0.28),
        "shine": mat("stone_shine", 0x5e, 0.22),
        "bead": mat("stone_bead", 0x5f, 0.2),
    }


def core_materials(bands):
    glow = k.level_palette()
    out = []
    for limit, index, strength in bands:
        if strength > 0:
            m = k.material(f"stone_core_{index:x}", palette=index, metallic=0.0, roughness=0.3, emission=glow[index],
                           emission_strength=strength)
        else:
            m = k.material(f"stone_core_{index:x}", palette=index, metallic=0.05, roughness=0.5)
        out.append((limit, m))
    return out


# --- The solid ------------------------------------------------------------------------------------------------------

def smin(a, b, kk):
    return -smax(-a, -b, kk)


def solid():
    """The lobes, knobs and floor as a signed distance on the grid (negative inside); the grid's origin."""
    lo = Vector((CENTRE.x - 10.4, CENTRE.y - 10.4, -0.6))
    nx = ny = int(round(20.8 / STEP)) + 1
    nz = int(round(6.6 / STEP)) + 1
    xs = lo.x + STEP * np.arange(nx)
    ys = lo.y + STEP * np.arange(ny)
    zs = lo.z + STEP * np.arange(nz)
    gx, gy = np.meshgrid(xs - CENTRE.x, ys - CENTRE.y, indexing="ij")
    z = zs[None, None, :]
    f = np.full((nx, ny, nz), 1e3, np.float32)
    for sx, sy in ((1, 1), (-1, 1), (-1, -1), (1, -1)):
        qx, qy = sx * gx - LOBE_C0, sy * gy - LOBE_C0
        rho = ((np.abs(qx) / LOBE_HALF) ** LOBE_P + (np.abs(qy) / LOBE_HALF) ** LOBE_P) ** (1.0 / LOBE_P)
        dome = (np.sqrt(rho[:, :, None] ** 2 + ((z - LOBE_Z) / LOBE_UP) ** 2) - 1.0) * min(LOBE_HALF, LOBE_UP)
        f = np.minimum(f, dome.astype(np.float32))
    # The knobs: ellipsoids on the axes (an approximate distance, scaled by their smallest half-size).
    a, b, c = KNOB_SIZE
    for ux, uy in ((0, 1), (-1, 0), (0, -1), (1, 0)):
        along = gx * ux + gy * uy
        across = -gx * uy + gy * ux
        q = np.sqrt(((along - KNOB_R) / a) ** 2 + (across / b) ** 2)[:, :, None]
        e = (np.sqrt(q ** 2 + ((z - KNOB_Z) / c) ** 2) - 1.0) * min(a, b, c)
        f = smin(f, e.astype(np.float32), 0.4).astype(np.float32)
    # The floor under it all.
    floor_ = np.maximum(np.hypot(gx, gy)[:, :, None] - FLOOR_R, z - FLOOR_TOP)
    f = np.minimum(f, floor_.astype(np.float32))
    # Rocked by smooth noise near the surface, cut off flat at the ground.
    i, j, kz = np.nonzero(np.abs(f) < 1.2)
    px, py, pz = xs[i], ys[j], zs[kz]
    detail = np.zeros(len(i))
    for n, (amp, scale) in enumerate(NOISE):
        detail += amp * noise3(px / scale, py / scale, pz / scale, 153 + n)
    detail *= np.clip((pz - 0.2) / 0.8, 0.0, 1.0)
    f[i, j, kz] += detail.astype(np.float32)
    f = np.maximum(f, -np.broadcast_to(z, f.shape).astype(np.float32))
    return f, lo


def body(m):
    f, lo = solid()
    verts, quads = surface_nets(f, (lo.x, lo.y, lo.z), STEP)
    obj = mesh_object("stone", verts, quads)
    finish_whole(obj, smooth=2)
    decimate(obj, set(), TARGET)
    k.smooth(obj, 180)
    # The lilacs: bands of how the faces face, the floor and the crevices' bottoms dark.
    mesh = obj.data
    values = []
    for v in mesh.vertices:
        n = Vector(v.normal)
        r = math.hypot(v.co.x - CENTRE.x, v.co.y - CENTRE.y)
        if v.co.z < FLOOR_TOP + 0.25 and r < FLOOR_R + 0.3:
            values.append(-1.0)
            continue
        values.append(0.6 * n.z + 0.4 * max(0.0, n.dot(SUN)))
    band_split(obj, values, [(-9.0, m["floor"]), (-0.15, m["under"]), (0.25, m["side"]), (0.55, m["top"]),
                             (0.8, m["crown"]), (0.95, m["shine"])])
    k.smooth(obj, 180)
    return obj


def beads(m):
    r, z, rad = BEAD
    for i, (ux, uy) in enumerate(((0, 1), (-1, 0), (0, -1), (1, 0))):
        c = CENTRE + Vector((ux, uy, 0.0)) * r
        bead = mk.ball(f"bead{i}", (c.x, c.y, z), (rad, rad, rad * 0.85), m["bead"], 16, 8)
        mk.paint(bead, lambda cc, n: m["side"] if n.z < 0.0 else None)


def core():
    """The core in the crevices: a four-armed star of ember, its arms tapering out along the crevices, its middle a
    dome; faces fine enough to be painted in bands by the distance from the middle."""
    parts = [mk.dome("core", (CENTRE.x, CENTRE.y), (CORE_R, CORE_R, CORE_TOP), 0.0, None, 32, 8)]
    for i, angle in enumerate((0.0, 90.0, 180.0, 270.0)):
        phi = math.radians(angle)
        u = Vector((math.cos(phi), math.sin(phi), 0.0))
        v = Vector((-math.sin(phi), math.cos(phi), 0.0))
        rings = []
        steps = 14
        for j in range(steps + 1):
            t = j / steps
            dist = 0.4 + (ARM_LEN - 0.4) * t
            w = ARM_W * (1.0 - 0.4 * t)
            h = ARM_TOP * (1.0 - 0.35 * t)
            rings.append([CENTRE + u * dist + v * (w * math.cos(2 * math.pi * q / 12)) +
                          Vector((0, 0, max(0.0, h * math.sin(2 * math.pi * q / 12)))) for q in range(12)])
        arm = k.loft(f"arm{i}", rings, None)
        k.smooth(arm, 60)
        parts.append(arm)
    return parts


def paint_core(parts, bands):
    for obj in parts:
        obj.data.materials.clear()
        for _, mat in bands:
            obj.data.materials.append(mat)
        for poly in obj.data.polygons:
            d = math.hypot(poly.center.x - CENTRE.x, poly.center.y - CENTRE.y)
            poly.material_index = next(i for i, (limit, _) in enumerate(bands) if d < limit)
        obj.data.update()


def pin(m):
    x, y = CENTRE.x, CENTRE.y
    e = 0.001
    return k.mesh_object("pin", [(x, y, PIN_Z), (x + e, y, PIN_Z), (x, y + e, PIN_Z)], [(0, 1, 2)], m["floor"])


def main():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    k.reset()
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    m = materials()
    body(m)
    beads(m)
    core_parts = core()
    pin(m)
    for name, sprite, bands in FRAMES:
        if only and name not in only:
            continue
        paint_core(core_parts, core_materials(bands))
        objects = mk.meshes()
        if "check" in options:
            mk.compare("%s (0 %d)" % (name, sprite), mk.coverage(objects, 24, 28),
                       k.sprite_mask(os.path.join(options["check"], "enemy_0.png"), sprite))
        mk.report(name, objects, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, objects)


if __name__ == "__main__":
    main()
