"""MINERS's grey lander (sheet L sprite 229, 2x2: 24 x 28 pixels; enemy 1173 of episode 5, the sky, armour 60, worth 100;
and enemy 728 of episode 4, SQUADRON's ground layer, armour 40, worth 250), polished (2026-10-22, round 35; it replaces
wave3_z_small.py's red_mouth_lander(), a heightfield shell painted on its pixel grid with slats, a jet and legs laid
on). models.cfg: model red_mouth_lander enemies/red_mouth_lander.glb (unchanged), sprite l 229 red_mouth_lander yaw=0
(unchanged: drawn centred in height; on SQUADRON's ground the game rests it on its feet).

Where the levels put it (the level events, tools/content/tyrevents.py): MINERS sends it twice down the screen from a
random place (t850 and t3050, sky, vy +2), where it launches (fire overrides on its link: launchfreq 5); SQUADRON stands
one on its ground. Not animated; no other enemy, launched ones included, shows L 229; it is no other sprite's pixels
mirrored, turned or in other ramps; no episode 6 level places it.

As the sprite and its 4x upscale draw it (columns and rows of the 24 x 28 sprite; ramp 0's greys 0x01-0x0f): an
armoured grey pod, its back narrow (columns 7-17 of row 1) under a raised hatch (rows 1-3, a dark seam under it at row
4), widening to its full width by row 9, its broad front face sloping down to its lower edge at row 16: lit flanks
(0x09-0x0e) with dark seams down them (columns 9 and 15), in the middle a visor of three bright slats (columns 10, 12
and 14 of rows 8-12, 0x0c-0x0e) over a red mouth (columns 9-15 of rows 13-15, 0x71-0x77); under it the dark belly
(columns 5-18 of rows 16-25) with a jet glowing red to yellow down its middle (columns 10-14 of rows 18-23, 0x71-0x7c),
and two legs down the screen to its feet at the bottom corners (columns 0-4 and 19-23 of rows 15-27).

Built as such a craft, for the game's camera: designed in the picture's plane (x, y as the sprite draws them, z up,
the camera looking straight down) and then sheared along the game camera's line of sight (y - z tan 20:
polish_rock_column.py's way), so that the camera sees every part where the sprite draws it. The pod is a signed
distance field on a grid H pixels apart (polish_rock_arch.py's surface nets): its plan the sprite's outline (PLAN), its
top cut by planes (the front sloping from BACK_Z to FRONT_Z, the flanks and the back's chamfers falling to SIDE_Z), its
underside flat; the hatch a raised block on its back, the visor a plate with three slats on its front, the mouth a slot
in it. Its colours are the sprite's own greys under each face (the broad shading kept in part, the fine kept: its seams
and lit edges), the red pixels glowing (0x74, 0x77: emission 0.35, 0.45). Under it the belly a rounded box (0x03), the
jet a cone pointing down the screen glowing in bands (0x77 0.4, 0x7a 0.5, 0x7c 0.6), the legs round struts from the
pod's lower corners down to round feet (0x06-0x0d, painted by the light: polish_asteroid_rig.paint_light).

Coordinates as in tyrkit: 1 unit = 1 game pixel; +X right, +Y up the screen, +Z up; the origin is the sprite's
centre (pixel corner 12, 14): the pixel corner (c, r) is (c - 12, 14 - r). The game centres it in height.

Replaces wave3_z_small.py (all of it: the lander was all it still built) and the pixels only it reads (wave3_z_art.py's
MECH).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (its silhouette as the
camera sees it against L 229's pixels), --preview <prefix>.
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
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_rock_arch import surface_nets, finish_whole, mesh_object, smax, fill_outside, face_data, decimate  # noqa: E402
from polish_rock_arch import polygon_sdf  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_rock_column import shear_to_camera, view_coverage, TILT  # noqa: E402
from polish_asteroid_rig import paint_light  # noqa: E402

LIGHT = Vector((-0.55, 0.45, 0.7)).normalized()

# The sprite (L 229), a character per pixel: a hex digit its grey's shade (ramp 0), R O Y its reds, orange and yellows
# (ramp 7: shades under 6, 6-8, 9 and up); '.' none.
ART = """
........................
.......11111111111......
......179a877779561.....
......178da99abc461.....
.....111355554321111....
....1b9db6bbbbb48b791...
...1abbfd6cdddd6ad9a71..
..1abcaec6bcccc49c8b771.
.19bce9db7a424b48b7c7771
18acea8ba7c7c7c36a6d9777
899dba7ba6e6e6e2696ba674
199caa7ba6b6b5b2586aa563
199caa7a83736361586aa563
199caa7a612RRR21476aa562
178baa775RRRRRRR365aa553
.5777abda51ROR139eaa6442
.1111a987ecccca9779a6111
.17416744766666643663761
11774332266RRR6623435961
17cbb533222RRR3311149ba4
15a8cb7a166ROR66165ba8b3
15a59112332RYR23211296a3
17a571167aROYOR9761174b5
17a571.16611R11751.16396
179111..162444261..11176
1781.....1111111.....166
1181.................161
.181.................161
"""

PLAN = [(-5.0, 13.0), (6.0, 13.0), (12.0, 5.5), (12.0, -2.6), (-12.0, -2.6), (-12.0, 5.5)]
BACK_Z, FRONT_Z, SIDE_Z, BOTTOM_Z = 10.4, 4.6, 6.6, 2.6
FRONT_Y = (-2.6, 9.6)                   # the front slope: from its lower edge (row 16.6) to its top (row 4.4)
H = 0.25
X0, NX = -13.0, 105
Y0, NY = -4.0, 76
Z0, NZ = 1.0, 48
XS = X0 + H * np.arange(NX)
YS = Y0 + H * np.arange(NY)
ZS = Z0 + H * np.arange(NZ)
MID, KEEP, DETAIL, LIFT = 9.0, 0.6, 1.0, 1.5
SHADES = [0x04, 0x06, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e]
TARGET = 7000


def mat(name, index, metallic=0.25, roughness=0.35, glow=None):
    if glow is not None:
        return k.material(name, palette=index, metallic=0.0, roughness=0.4, emission=k.level_palette()[index],
                          emission_strength=glow)
    return k.material(name, palette=index, metallic=metallic, roughness=roughness)


def materials():
    m = {i: mat("lander_grey", i) for i in SHADES}
    m.update({"grey": m[0x0a], "grey_lit": m[0x0d], "grey_dark": m[0x06], "seam": m[0x04], "slat": m[0x0e],
              "red": mat("lander_red", 0x74, glow=0.35), "red_hot": mat("lander_red_hot", 0x77, glow=0.45),
              "jet": mat("lander_jet", 0x77, glow=0.4), "jet_hot": mat("lander_jet_hot", 0x7a, glow=0.5),
              "jet_core": mat("lander_jet_core", 0x7c, glow=0.6)})
    return m


def art():
    shade = np.full((28, 24), np.nan)
    red = np.zeros((28, 24), bool)
    for r, line in enumerate(ART.strip("\n").split("\n")):
        for c, ch in enumerate(line):
            if ch == ".":
                continue
            if ch in "ROY":
                shade[r, c], red[r, c] = 3.0, True
            else:
                shade[r, c] = int(ch, 16)
    return shade, red


def sample(a, x, y):
    rows, cols = a.shape
    u, v = x + 12.0 - 0.5, 13.5 - y
    c0, r0 = np.floor(u).astype(int), np.floor(v).astype(int)
    fu, fv = u - c0, v - r0

    def at(r, c):
        ok = (r >= 0) & (r < rows) & (c >= 0) & (c < cols)
        return np.where(ok, a[np.clip(r, 0, rows - 1), np.clip(c, 0, cols - 1)], 0.0)
    return ((1 - fu) * (1 - fv) * at(r0, c0) + fu * (1 - fv) * at(r0, c0 + 1) + (1 - fu) * fv * at(r0 + 1, c0) +
            fu * fv * at(r0 + 1, c0 + 1))


def blur(a, sigma):
    s = sigma / H
    r = int(math.ceil(3 * s))
    kernel = np.exp(-0.5 * (np.arange(-r, r + 1) / s) ** 2)
    kernel /= kernel.sum()
    out = a
    for axis in (0, 1):
        pad = [(0, 0), (0, 0)]
        pad[axis] = (r, r)
        p = np.pad(out, pad, mode="edge")
        acc = np.zeros_like(out)
        for i, w in enumerate(kernel):
            acc += w * (p[i:i + out.shape[0], :] if axis == 0 else p[:, i:i + out.shape[1]])
        out = acc
    return out


def sample_grid(a, x, y):
    u = np.clip((x - X0) / H, 0.0, NX - 1.001)
    v = np.clip((y - Y0) / H, 0.0, NY - 1.001)
    i, j = np.floor(u).astype(int), np.floor(v).astype(int)
    fu, fv = u - i, v - j
    return (a[i, j] * (1 - fu) * (1 - fv) + a[i + 1, j] * fu * (1 - fv) + a[i, j + 1] * (1 - fu) * fv +
            a[i + 1, j + 1] * fu * fv)


def pod():
    """The pod's solid: the plan, its top cut by the planes, its underside flat; returned as a mesh in the picture's
    plane."""
    gx, gy = np.meshgrid(XS, YS, indexing="ij")
    plan = polygon_sdf(gx.ravel(), gy.ravel(), PLAN).reshape(gx.shape)
    front = FRONT_Z + (BACK_Z - FRONT_Z) * np.clip((gy - FRONT_Y[0]) / (FRONT_Y[1] - FRONT_Y[0]), 0.0, 1.0)
    inside = np.maximum(-plan, 0.0)
    flank = SIDE_Z + 1.25 * inside
    top = np.minimum(np.minimum(front, flank), BACK_Z)
    # the hatch on its back (columns 7-17 of rows 1-4) a step higher
    hatch = (np.abs(gx - 0.5) < 5.2) & (gy > 9.6) & (gy < 13.0)
    top = np.where(hatch, np.minimum(top + 1.0, BACK_Z + 1.0), top)
    top = blur(top, 0.35)
    gz = ZS[None, None, :]
    d = smax(plan[:, :, None], gz - top[:, :, None], 0.6)
    d = smax(d, BOTTOM_Z - gz, 0.6).astype(np.float32)
    # the mouth: a slot in the front (columns 10-14 of rows 13-15), 1.2 deep
    mouth = (np.abs(gx - 0.5) < 3.2) & (gy > -2.0) & (gy < 1.0)
    d = np.where(mouth[:, :, None] & (gz > top[:, :, None] - 1.2), np.maximum(d, 0.15), d)
    for axis in range(3):
        p = np.pad(d, [(1, 1) if ax == axis else (0, 0) for ax in range(3)], mode="edge")
        d = 0.25 * np.take(p, range(0, d.shape[axis]), axis=axis) + 0.5 * d + \
            0.25 * np.take(p, range(2, d.shape[axis] + 2), axis=axis)
    verts, quads = surface_nets(d, (X0, Y0, Z0), H)
    obj = finish_whole(mesh_object("pod", verts, quads))
    return obj


def paint_pod(obj, m):
    shade, red = art()
    gx, gy = np.meshgrid(XS, YS, indexing="ij")
    s_px = sample(fill_outside(shade), gx, gy)
    fine, broad = blur(s_px, 0.5), blur(s_px, 4.0)
    local = blur(s_px, 0.6)
    paint = MID + (broad - MID) * KEEP + DETAIL * (local - broad)
    redf = blur(sample(red.astype(np.float64), gx, gy), 0.35)
    centres, normals = face_data(obj)
    x, y = centres[:, 0], centres[:, 1]
    s = sample_grid(paint, x, y)
    s = np.where(normals[:, 2] < -0.3, np.minimum(s, 4.0), s)
    s = s + LIFT
    keys = [min(SHADES, key=lambda v: abs(v - float(q))) for q in s]
    rr = sample_grid(redf, x, y)
    names = ["red_hot" if v > 0.7 else "red" if v > 0.4 else None for v in rr]
    mesh = obj.data
    used = []
    for kk, nm in zip(keys, names):
        key = nm or kk
        if key not in used:
            used.append(key)
    used.sort(key=lambda v: (isinstance(v, str), str(v) if isinstance(v, str) else "%03d" % v))
    mesh.materials.clear()
    for u in used:
        mesh.materials.append(m[u])
    slot = {u: i for i, u in enumerate(used)}
    mesh.polygons.foreach_set("material_index", [slot[nm or kk] for kk, nm in zip(keys, names)])
    mesh.update()


def visor(m):
    parts = []
    for c in (10.5, 12.5, 14.5):
        x = c - 12.0
        y0, y1 = 14.0 - 12.6, 14.0 - 8.0
        # on the front slope: the slat's foot follows the slope
        z0 = FRONT_Z + (BACK_Z - FRONT_Z) * (y0 - FRONT_Y[0]) / (FRONT_Y[1] - FRONT_Y[0])
        z1 = FRONT_Z + (BACK_Z - FRONT_Z) * (y1 - FRONT_Y[0]) / (FRONT_Y[1] - FRONT_Y[0])
        a, b = Vector((x, y0, z0 + 0.35)), Vector((x, y1, z1 + 0.35))
        slat = mk.tube(f"slat{c:.0f}", [a, b], 0.42, m["slat"], 8)
        parts.append(slat)
    return parts


def belly(m):
    body = mk.box("belly", -6.6, 7.0, 14.0 - 25.4, 14.0 - 15.8, 0.9, BOTTOM_Z + 0.5, m["seam"])
    mk.bevel(body, 0.9, 3, 35)
    mk.shade(body, 35)
    paint_light(body, m, "seam", "grey_dark", "seam", lit_at=0.6)
    a = Vector((0.5, 14.0 - 17.4, 2.6))
    b = Vector((0.5, 14.0 - 23.6, 2.2))
    jet = mk.tube("jet", [a, a.lerp(b, 0.4), b], 2.4, m["jet"], 20, radii=[2.5, 2.1, 0.4])

    def pick(c, n):
        t = (c - a).dot((b - a).normalized()) / (b - a).length
        return m["jet_core"] if t > 0.55 else m["jet_hot"] if t > 0.25 else m["jet"]
    mk.paint(jet, pick)
    ring = mk.tube("jet_ring", [a + Vector((0.0, 0.5, 0.0)), a - Vector((0.0, 0.4, 0.0))], 2.9, m["grey_dark"], 20)
    return [body, jet, ring]


def legs(m):
    parts = []
    for side, (hip_c, knee_c, foot_c) in ((-1, (2.8, 1.6, 2.0)), (1, (21.2, 22.4, 22.0))):
        hip = Vector((hip_c - 12.0, 14.0 - 15.4, BOTTOM_Z + 1.4))
        knee = Vector((knee_c - 12.0, 14.0 - 19.6, 4.4))
        foot = Vector((foot_c - 12.0, 14.0 - 26.0, 0.9))
        thigh = mk.tube(f"thigh{side}", [hip, hip.lerp(knee, 0.5) + Vector((0.0, 0.0, 0.5)), knee], 1.6, m["grey"], 14)
        shin = mk.tube(f"shin{side}", [knee, knee.lerp(foot, 0.5), foot], 1.35, m["grey"], 14)
        joint = mk.ball(f"knee{side}", tuple(knee), (1.9, 1.9, 1.6), m["grey_lit"], 14, 7)
        pad = mk.ball(f"foot{side}", tuple(foot + Vector((0.0, -0.6, -0.1))), (2.0, 1.9, 0.9), m["seam"], 14, 7)
        for p in (thigh, shin):
            k.smooth(p, 50)
            paint_light(p, m, "grey", "grey_lit", "grey_dark", lit_at=0.55)
        parts += [thigh, shin, joint, pad]
    return parts


def build():
    options = k.args()
    out = mk.outdir(options)
    sheets = options.get("check")
    k.reset()
    bpy.context.scene.view_settings.view_transform = "Standard"
    m = materials()
    shell = pod()
    decimate(shell, set(), TARGET)
    paint_pod(shell, m)
    parts = [shell] + visor(m) + belly(m) + legs(m)
    for o in parts:
        mk.apply(o)
        shear_to_camera(o)
    bpy.context.view_layer.update()
    if sheets:
        mk.compare("red_mouth_lander (L 229) as the camera sees it, its sprite's pixels",
                   view_coverage(parts, 24, 28, (0.0, 0.0)), k.sprite_mask(os.path.join(sheets, "enemy_L.png"), 229))
    drop_unused(parts)
    triangulate(parts)
    obj = join(parts, "red_mouth_lander")
    obj.data.name = "red_mouth_lander"
    bpy.context.view_layer.update()
    mk.report("red_mouth_lander", [obj], os.path.join(out, "red_mouth_lander.glb"))
    if "preview" in options:
        mk.preview(options["preview"] + "red_mouth_lander", [obj])


if __name__ == "__main__":
    build()
