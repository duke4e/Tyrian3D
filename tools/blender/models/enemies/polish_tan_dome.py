"""MINERS's tan creature in its pit of dark red rock (sheet L sprites 161 163 above 199 201, 2x2 each: one 48 x 56
picture; enemies 1151-1154 of episode 5, ground layer, armour 20 each; the upper two worth 25 and 0, the lower 0 and 25),
the nub on its head swelling into a fire ball (161 165 165 203 203 and 163 167 167 205 205 as it fires: frame models),
and what its top left piece leaves when it dies (L 238), polished (2026-10-22, round 35; it replaces wave3_z_rock.py's
creature, a heightfield over the sprites' outline with the arms baked in and the fire ball laid on, wave3_at_misc.py's
fire-ball frames and wave3_ap_miners.py's damaged look, the whole creature with its left half blown off). models.cfg:
model tan_dome_tl / _tr / _bl / _br, tan_dome_165 / _167 / _203 / _205 and tan_dome_tl_damaged ... origin
(unchanged); the sprite lines of L 161, 163, 199, 201 and 238 get height=-4.

Where the level puts it (the level events, tools/content/tyrevents.py; the enemy data, tools/content/tyrdata.py):
MINERS puts it six times (t608 at column 10, t692 at 11, t1084 at 3, t1252 at 1, t4024 at 1, t4108 at 9), each time
1151 (161) and 1152 (163) 28 pixels up the screen from 1153 (199) and 1154 (201), side by side, one link, on the ground
layer: the sheet's picture whole. Always on the map's row above tiles of its own, in a patch of the dark red hex rock (a
pit there: the terrain lies 24 pixels under the sand), the tiles under its lower half painting its broken shell and its
arms (the creature dead). The upper pieces fire (tur 7, animate 2): each shot plays their frames once, the nub on its
head swelling into a red ball of fire (165 / 167: 7 pixels across, rows 15-18) and a bigger one, white-hot in its
middle (203 / 205: 8 across, rows 12-18); no other enemy, launched ones included, shows L 161-167, 199-205 or 238, so
they are frame models. Shot, the four go together (one link): the top left one turns to L 238 (dgr, dlevel -1: it
stays), which draws only a few crumbs of shell at its bottom edge (rows 26-27: the rim of the broken shell the map's
tile under it paints), the other three die (the game leaves its slumped wrecks of their models). No sprite of these is
another's pixels mirrored, turned or in other ramps; no episode 6 level places the creature.

As the sprites and their 4x upscales draw it (columns and rows of the 48 x 56 picture; ramp 10's tans 0xa2-0xae): a
smooth grey-tan body like a seal's, its head up the screen, a small red nub at its tip (rows 17-19, 0x74-0x77, in a dark
collar 0x10), widening into its shoulders (rows 24-28) and a fat torso (columns 15-33, rows 28-47), lit high on its left
and down its middle, a dark crease on its right (columns 27-28 of rows 35-40); two thick arms from its shoulders, out to
its elbows (columns 7 and 41, row 29) and down to its paws on the rock (columns 3-9 and 39-45 of rows 43-47), dark
underneath and at the paws. The dark red rock round it, the gaps between its arms and its body and its shadow (ramps 7,
15 and 4; the dark browns under its body below row 47) are the map's: left out.

Built as such a creature, for the game's camera: designed in the picture's plane (x, y as the picture draws them, z up,
the camera looking straight down) and then sheared along the game camera's line of sight (y - z tan 20:
polish_lava_grub.py's and polish_rock_column.py's way), so that the camera sees every point where the picture draws it.
In the picture's plane its body is a body of revolution about an axis leaning back LEAN (68) degrees from its foot ring
(drawn at row 44 at its sides) to its tip (row 18): PROFILE gives its radius along the axis (the torso 9.6, the head
narrowing to the nub), so the camera sees its bottom edge as the arc the sprites draw (r cos LEAN deeper at its front)
and its head where they draw it; under its foot ring its sides go straight down to the ground (unseen by the camera).
The arms are round tubes (ARM: points and radii) from inside its shoulders out to the elbows, held up, and down to the
paws, flattened balls on the ground. The nub is a red ball in a dark collar at the tip, glowing a little (0x75, 0.3); in
the frames a ball of fire swells over it, in bands by how squarely its faces look at the camera (165/167: 0x75 glowing
0.35 at its rim, 0x77 0.42, a core 0x79 0.5; 203/205: 0x76 0.4, 0x78 0.48, 0x7b 0.56, a white-hot core 0x7e 0.65), the
nub inside it glowing in the fire's outer red. It is a signed distance field on a grid H pixels apart
(polish_rock_arch.py's surface nets), the parts joined smoothly; its colours are the picture's own shades under each
face (the faces' points taken back into the picture's plane): the broad shading kept in part round MID (KEEP: the
game's sun shades it), the fine kept; the undersides dark. After the shear the creature stands about 15 pixels high,
its head leaning back up the screen over its torso, its arms propping it up.

The whole is cut along the planes the camera sees as the sprites' edges (x = 0; y + tan 20 z = 0, leaning back up the
screen: polish_stone_face.view_cut's planes), so that each piece holds what the camera sees in its sprite, the cuts
capped in the body's inside colour (CAP), each piece's triangles reduced to TARGET with its cut's vertices kept and its
normals those of the dense whole (polish_rock_column's pieces), moved so that its sprite's centre is its origin,
triangulated. The frames are the whole again with the fire ball, only its upper pieces exported. L 238 is a few curved
shards of the shell (SHARDS) lying on the rock at its bottom edge where the sprite draws them.

Coordinates: 1 unit = 1 game pixel; +X right, +Y up the screen, +Z up from the ground (z = 0); the whole's origin is
the picture's middle (the corner where the four sprites meet): column c is x = c + 0.5 - 24, row r is y = 27.5 - r. The
pieces' centres: 161 (-12, 14), 163 (12, 14), 199 (-12, -14), 201 (12, -14). Drawn at their origins (origin) on the
ground layer: height=-4 sets the creature on the terrain (the floor of its pit: the game lifts pieces side by side
moving alike to the terrain under their middle).

Replaces wave3_z_rock.py (all of it: the creature was all it still built), wave3_at_misc.py (all of it: the creature's
fire-ball frames were all it built) and wave3_ap_miners.py (all of it: the damaged look), and the pixels only they
read: wave3_z_art.py's DOME (and DOME_FIRE, read by nothing), wave3_ap_art.py's TAN_DOME_DMG.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each piece's silhouette as the
camera sees it against its sprite's own pixels, the rock and the shadow they paint left out), --preview <prefix>,
--whole <prefix> (the uncut creature and its fire-ball frames: views and GLBs), --only <name,...>.
"""
import math
import os
import sys
import time

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_rock_arch import (surface_nets, finish_whole, mesh_object, noise3, smax, fill_outside, face_data,  # noqa: E402
                              assign, decimate, shade_like)
from polish_k_pod import triangulate  # noqa: E402
from polish_rock_column import drop_islands, shear_to_camera, cut_piece, TILT  # noqa: E402
from polish_stone_face import view_cut  # noqa: E402

LIGHT = Vector((-0.55, 0.45, 0.7)).normalized()

# The creature's picture (rows 16-47 of the 48 x 56, 161 163 above 199 201), a character per pixel: a hex digit its
# shade (ramps 10, 11, 1 and 0: the tans, browns and darks), N the nub's red (ramp 7, rows 17-19); '.' none, or the map's
# rock, the gaps and the shadow (ramps 7, 15 and 4; the dark browns under the body from row 48): left out.
ART = """
................................................
.......................000......................
......................0NNN0.....................
.....................0800090....................
....................089abaa90...................
...................07679ba9990..................
..................077778bcba990.................
.................0677789dedb9990................
...............310567899efec999046..............
............32210656789adedb999a04567...........
.........53321110466799adcbaaaa702224655........
........432211662445899abbcaa865355222245.......
.......4211667631356899aaaaa98753556551224......
.......31667876313567888888888653566655512......
.......6688887631356789aa98888752456666656......
.....668888765412356789aa9888875413456677896....
.....78877655224345678acca8888765422345679b9....
....877765422..4446678bddc88887767..22459bdb6...
....66655221...4445679bccb99878777...12269b96...
....665524.....4545679bccb98588877...13425986...
....465525.1...4545678abba95788887...12525676...
....4655243..1.45466789aa984888887....3425676...
....46542.10..14556778899965888887......25676...
....35542200...4556778899957888887......24676...
....3554200....4556778899978888877......24576...
....355410.....4556678899988888777......14576...
....344301.....4556678899988888775......03455...
....333301.....3455678888888888775......02335...
....03220.......33456788887777765........002....
...000000.......12334577776665431.......00.0....
....0000........211233555553221.12......000.....
....000.........11111.23332.2..1.1.......1100...
"""
ART_TOP = 16

# The pieces: model, sprite, its box in the picture's plane (x0, x1, y0, y1; None: open), its sprite's centre.
PIECES = [("tan_dome_tl", 161, (None, 0.0, 0.0, None), (-12.0, 14.0)),
          ("tan_dome_tr", 163, (0.0, None, 0.0, None), (12.0, 14.0)),
          ("tan_dome_bl", 199, (None, 0.0, None, 0.0), (-12.0, -14.0)),
          ("tan_dome_br", 201, (0.0, None, None, 0.0), (12.0, -14.0))]
# The frames (the upper pieces' sprites): the fire ball (its centre's column, row, radii x / y / z, its layers'
# (palette index, emission, share of the radii)).
FRAMES = [(165, 167, (24.0, 16.9), (3.5, 2.7, 3.0), [(0x75, 0.35, 0.0), (0x77, 0.42, 0.45), (0x79, 0.5, 0.8)]),
          (203, 205, (24.0, 15.2), (4.1, 3.8, 3.8), [(0x76, 0.4, 0.0), (0x78, 0.48, 0.35), (0x7b, 0.56, 0.62),
                                                      (0x7e, 0.65, 0.84)])]
DAMAGED = ("tan_dome_tl_damaged", 238, (-12.0, 14.0))

# --- The creature (in the picture's plane) ----------------------------------------------------------------------------
LEAN = math.radians(68.0)
SA, CA = math.sin(LEAN), math.cos(LEAN)
X_AXIS, Y_FOOT = 0.5, -17.0              # its axis meets the foot ring here (its sides drawn at row 44)
# Its radius along the axis (pixels from the foot ring), from the sprites' half widths (the head's tip at row 18).
PROFILE = [(0.0, 8.6), (2.5, 9.3), (7.0, 9.6), (12.5, 9.55), (16.0, 9.25), (18.5, 8.8), (20.5, 8.2), (22.5, 7.3),
           (24.3, 6.1), (25.8, 4.7), (27.0, 3.1), (27.9, 1.4), (28.3, 0.0)]
DEPTH = 0.92                             # its cross-section's depth (front to back) as a share of its width
NUB = (27.9, 1.45, 0x75, 0.3)            # the nub: along the axis, its radius, its colour and glow
COLLAR = (27.2, 2.3, 0.8)               # its dark collar: along the axis, its radius, its thickness
# The arms (the left one; the right one mirrored about the axis): points (x, y in the picture's plane, z) and radii.
ARM = [(-6.5, 0.6, 7.0, 2.3), (-10.5, 0.2, 7.6, 2.5), (-14.8, -2.0, 7.2, 2.7), (-16.9, -5.6, 5.6, 2.8),
       (-17.4, -10.0, 3.6, 2.7), (-17.5, -13.8, 2.2, 2.6)]
PAW = ((-17.7, -16.6, 1.3), (3.2, 3.0, 1.7))
SKIRT = 1.5
NOISE = ((0.07, 3.0), (0.03, 1.2))
RELIEF = 0.06

# The grid (the picture's plane).
H = 0.3
X0, NX = -24.6, 165
Y0, NY = -23.0, 175
Z0, NZ = -2.4, 68
XS = X0 + H * np.arange(NX)
YS = Y0 + H * np.arange(NY)
ZS = Z0 + H * np.arange(NZ)

MID, KEEP, DETAIL, DITHER = 9.6, 0.8, 0.5, 0.3
LIFT = 1.4                               # (the game's light reads a shade or two darker than the flat sprite)
CAP = 0xa5
COLLAR_DARK = 0xa1
TARGET = 4200


def smoothstep(e0, e1, x):
    t = np.clip((np.asarray(x, dtype=np.float64) - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


# --- The picture ------------------------------------------------------------------------------------------------------

def art():
    """The picture's shades (56 x 48, nan: none) and the nub's pixels."""
    shade = np.full((56, 48), np.nan)
    nub = np.zeros((56, 48), bool)
    for i, line in enumerate(ART.strip("\n").split("\n")):
        r = ART_TOP + i
        for c, ch in enumerate(line):
            if ch == ".":
                continue
            if ch == "N":
                shade[r, c], nub[r, c] = 7.0, True
            else:
                shade[r, c] = int(ch, 16)
    return shade, nub


def sample(a, x, y, pad=0.0):
    """Bilinear sample of a pixel array a[row, column] of the picture (values at the pixels' centres)."""
    rows, cols = a.shape
    u, v = x + 24.0 - 0.5, 27.5 - y
    c0, r0 = np.floor(u).astype(int), np.floor(v).astype(int)
    fu, fv = u - c0, v - r0

    def at(r, c):
        ok = (r >= 0) & (r < rows) & (c >= 0) & (c < cols)
        return np.where(ok, a[np.clip(r, 0, rows - 1), np.clip(c, 0, cols - 1)], pad)
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


def paint_fields():
    shade, nub = art()
    filled = fill_outside(shade)
    gx, gy = np.meshgrid(XS, YS, indexing="ij")
    s_px = sample(filled, gx, gy)
    fine, mid, broad = blur(s_px, 0.5), blur(s_px, 1.6), blur(s_px, 4.0)
    local = blur(s_px, 0.6)
    paint = MID + (broad - MID) * KEEP + DETAIL * (local - broad)
    paint = paint + LIFT * smoothstep(4.0, 7.0, blur(s_px, 1.2))
    return {"paint": paint, "relief": fine - mid, "own": ~np.isnan(shade)}


# --- The solid --------------------------------------------------------------------------------------------------------

def profile_radius(t):
    ts = np.array([p[0] for p in PROFILE])
    rs = np.array([p[1] for p in PROFILE])
    return np.interp(t, ts, rs, left=rs[0], right=0.0)


def axis_point(t):
    return Vector((X_AXIS, Y_FOOT + t * SA, t * CA))


def capsule(gx, gy, gz, a, b, ra, rb):
    """The distance to a round bar from a (radius ra) to b (rb)."""
    ab = b - a
    px, py, pz = gx - a.x, gy - a.y, gz - a.z
    h = np.clip((px * ab.x + py * ab.y + pz * ab.z) / ab.length_squared, 0.0, 1.0)
    dx, dy, dz = px - h * ab.x, py - h * ab.y, pz - h * ab.z
    return np.sqrt(dx * dx + dy * dy + dz * dz) - (ra + (rb - ra) * h)


def arms(gx, gy, gz):
    d = None
    for side in (-1.0, 1.0):
        pts = [Vector((X_AXIS + side * (x - X_AXIS), y, z)) for x, y, z, _ in ARM]
        rad = [r for *_, r in ARM]
        for i in range(len(pts) - 1):
            seg = capsule(gx, gy, gz, pts[i], pts[i + 1], rad[i], rad[i + 1])
            d = seg if d is None else -smax(-d, -seg, 0.8)
        (px, py, pz), (rx, ry, rz) = PAW
        cx = X_AXIS + side * (px - X_AXIS)
        paw = (np.sqrt(((gx - cx) / rx) ** 2 + ((gy - py) / ry) ** 2 + ((gz - pz) / rz) ** 2) - 1.0) * rz
        d = -smax(-d, -paw, 1.2)
    return d


def body_sdf(gx, gy, gz):
    dy, dz = gy - Y_FOOT, gz
    t = dy * SA + dz * CA
    v = -dy * CA + dz * SA
    u = gx - X_AXIS
    r = profile_radius(np.maximum(t, 0.0))
    body = np.sqrt(u * u + (v / DEPTH) ** 2) - r
    body = np.maximum(body, -t)
    # Under the foot ring: straight down to the ground.
    z_ring = -dy * SA / CA
    v_ring = -dy * CA + z_ring * SA
    foot = np.maximum(np.sqrt(u * u + (v_ring / DEPTH) ** 2) - PROFILE[0][1], gz - z_ring)
    return np.minimum(body, foot)


def solid(fl):
    t0 = time.time()
    gx = XS[:, None, None]
    gy = YS[None, :, None]
    gz = ZS[None, None, :].astype(np.float64)
    body = body_sdf(gx, gy, gz)
    d = -smax(-body, -arms(gx, gy, gz), 1.6)
    d = d.astype(np.float32)
    d -= (RELIEF * fl["relief"][:, :, None]).astype(np.float32)
    i, j, kz = np.nonzero(np.abs(d) < 2.0)
    x, y, zz = XS[i], YS[j], ZS[kz]
    detail = np.zeros(len(i))
    for n, (amp, scale) in enumerate(NOISE):
        detail += amp * noise3(x / scale, y / scale, zz / scale, 61 + n)
    d[i, j, kz] += detail.astype(np.float32)
    d = np.maximum(d, np.float32(-SKIRT) - ZS[None, None, :].astype(np.float32))
    for axis in range(3):
        p = np.pad(d, [(1, 1) if ax == axis else (0, 0) for ax in range(3)], mode="edge")
        d = 0.25 * np.take(p, range(0, d.shape[axis]), axis=axis) + 0.5 * d + \
            0.25 * np.take(p, range(2, d.shape[axis] + 2), axis=axis)
    print("solid: %.1f s" % (time.time() - t0))
    return d.astype(np.float32)


# --- Colours ----------------------------------------------------------------------------------------------------------

def materials():
    m = {i: k.material("tan_dome_skin", palette=i, metallic=0.05, roughness=0.5) for i in range(0xa1, 0xae)}
    return m


def glow_material(index, strength):
    return k.material("tan_dome_glow_%d" % int(strength * 100), palette=index, metallic=0.0, roughness=0.4,
                      emission=k.level_palette()[index], emission_strength=strength)


def shades(centres, normals, fl):
    x, y, z = centres[:, 0], centres[:, 1], centres[:, 2]
    py = y + TILT * z
    s = sample_grid(fl["paint"], x, py)
    s = s + DITHER * noise3(x / 1.0, py / 1.0, z / 1.0, 67)
    s = np.where(normals[:, 2] < -0.3, np.minimum(s, 3.5), s)
    return 0xa0 + np.clip(np.round(s), 1, 13).astype(int)


# --- The nub, the fire, the shards -------------------------------------------------------------------------------------

def sheared(p):
    return Vector((p.x, p.y - TILT * p.z, p.z))


def nub_parts(m):
    """The nub (a red ball glowing a little) and its dark collar, at the head's tip (already sheared)."""
    t, radius, index, strength = NUB
    c = axis_point(t)
    nub = mk.ball("nub", tuple(sheared(c)), (radius, radius, radius * 0.9), glow_material(index, strength), 20, 10)
    tc, rc, th = COLLAR
    a = axis_point(tc - th / 2)
    b = axis_point(tc + th / 2)
    collar = mk.tube("collar", [sheared(a), sheared(b)], rc, m[COLLAR_DARK], 20, radii=[rc, rc * 0.85])
    k.smooth(collar, 50)
    return [nub, collar]


def fire_parts(spec):
    """A ball of fire over the nub, its centre where the frame draws it (in the picture's plane), a pixel over the nub:
    painted in bands by how squarely its faces look at the camera (the rim the darkest red, the middle white-hot), each
    band glowing (its layers: palette index, emission, from what share of facing on)."""
    _, _, (col, row), (rx, ry, rz), layers = spec
    t, radius, _, _ = NUB
    z = axis_point(t).z + 1.0
    centre = sheared(Vector((col + 0.5 - 24.0, 27.5 - row, z)))
    mats = [glow_material(index, strength) for index, strength, _ in layers]
    ball = mk.ball("fire", tuple(centre), (rx, ry, rz), mats[0], 32, 16)
    view = Vector((0.0, -math.sin(math.radians(20.0)), math.cos(math.radians(20.0))))

    def pick(c, n):
        facing = n.dot(view)
        choice = mats[0]
        for mat, (_, _, share) in zip(mats, layers):
            if facing >= share:
                choice = mat
        return choice
    mk.paint(ball, pick)
    return [ball]


# The shards L 238 draws (its rows 26-27): (column, row, length across, height), lying on the rock.
SHARDS = [(14.0, 27.0, 3.2, 1.2), (20.5, 26.6, 4.0, 1.5)]


def shards(m):
    out = []
    for i, (c, r, length, h) in enumerate(SHARDS):
        x, y = c + 0.5 - 24.0, 27.5 - r
        pts = []
        for j in range(7):
            a = math.pi * j / 6
            pts.append((x + 0.5 * length * math.cos(a), y - 0.2 + 0.9 * math.sin(a) * (0.6 + 0.4 * (j % 2))))
        shard = mk.prism("shard%d" % i, pts[::-1] if False else pts, 0.0, h, m[0xa5])
        for v in shard.data.vertices:
            if v.co.z > 0.5:
                v.co.z = h * (0.6 + 0.4 * math.sin(3.1 * v.co.x + 1.7 * v.co.y + i))
        shard.data.update()
        mk.paint(shard, lambda cc, n: m[0xa2] if n.z < 0.6 else m[0xa4])
        out.append(shard)
    return out


# --- Build ------------------------------------------------------------------------------------------------------------

def view_coverage(objects, w, h, centre):
    copies = []
    for obj in objects:
        c = obj.copy()
        c.data = obj.data.copy()
        bpy.context.scene.collection.objects.link(c)
        shear_to_camera(c, +1.0)
        copies.append(c)
    covered = mk.coverage(copies, w, h, centre=centre)
    for c in copies:
        data = c.data
        bpy.data.objects.remove(c)
        bpy.data.meshes.remove(data)
    return covered


def whole_body(fl, m):
    d = solid(fl)
    verts, quads = surface_nets(d, (X0, Y0, Z0), H)
    quads = drop_islands(verts, quads)
    whole = finish_whole(mesh_object("tan_dome", verts, quads))
    bm = bmesh.new()
    bm.from_mesh(whole.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    bm.to_mesh(whole.data)
    bm.free()
    shear_to_camera(whole)
    whole.data.update()
    centres, normals = face_data(whole)
    assign(whole, shades(centres, normals, fl), m)
    return whole


def cut_part(src, box, name, m):
    """A part cut by a piece's box (the body: decimated with its cut kept, shaded as the whole; small parts as they
    are), its caps in CAP."""
    obj, rim = cut_piece(src, box, name, m[CAP])
    if obj is None:
        return None
    return obj, rim


def export(parts, name, options, out, mask=None, centre=None):
    if mask is not None:
        mk.compare("%s as the camera sees it, its sprite's own pixels" % name,
                   view_coverage(parts, 24, 28, centre), mask)
    mk.transform(parts, Matrix.Translation((-centre[0], -centre[1], 0.0)))
    from polish_deli_boss import join, drop_unused
    drop_unused(parts)
    triangulate(parts)
    obj = join(parts, name)
    obj.data.name = name
    bpy.context.view_layer.update()
    mk.report(name, [obj], os.path.join(out, name + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + name, [obj], size=(24, 40), scale=12, centre=(0.0, -6.0))
    bpy.data.objects.remove(obj)


def pieces_of(whole, extras, specs, m, options, out, fl, check, sheets=None):
    source = mk.NormalSource(whole)
    for name, sprite, box, centre in specs:
        parts = []
        obj, rim = cut_piece(whole, box, name, m[CAP])
        if obj is not None:
            whole.hide_render = True
            decimate(obj, rim, TARGET)
            shade_like(obj, source)
            centres, normals = face_data(obj)
            idx = shades(centres, normals, fl)
            flags = np.empty(len(obj.data.polygons), np.int64)
            obj.data.polygons.foreach_get("material_index", flags)
            idx[flags == 1] = CAP
            assign(obj, idx, m)
            parts.append(obj)
        for e in extras:
            piece = view_cut(e, box, e.data.materials[0])
            if piece is not None:
                piece.name = e.name + "_" + name
                parts.append(piece)
        for o in [whole] + extras:
            o.hide_render = True
        mask = None
        if check:
            c0, r0 = int(centre[0] - 12 + 24), int(28 - centre[1] - 14)
            mask = fl["own"][r0:r0 + 28, c0:c0 + 24].tolist()
            if sheets and centre[1] > 0:               # (an upper piece: its sprite has no rock; its frames' fire)
                mask = k.sprite_mask(os.path.join(sheets, "enemy_L.png"), sprite)
        export(parts, name, options, out, mask, centre)
        for o in [whole] + extras:
            o.hide_render = False


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    check = "check" in options
    sheets = options.get("check")
    k.reset()
    bpy.context.scene.view_settings.view_transform = "Standard"
    m = materials()
    fl = paint_fields()
    whole = whole_body(fl, m)
    print("whole: %d triangles" % len(whole.data.polygons))
    nub = nub_parts(m)
    if check or "whole" in options:
        if check:
            mk.compare("whole creature as the camera sees it (the rock left out)",
                       view_coverage([whole] + nub, 48, 56, (0.0, 0.0)), fl["own"].tolist())
        if "whole" in options:
            view = [o.copy() for o in [whole] + nub]
            for o, src in zip(view, [whole] + nub):
                o.data = src.data.copy()
                bpy.context.scene.collection.objects.link(o)
            triangulate(view)
            mk.export(view, options["whole"] + "tan_dome.glb")
            mk.preview(options["whole"] + "tan_dome", view, size=(48, 56), scale=10, distance=1.2)
            for o in view:
                bpy.data.objects.remove(o)
    specs = [(name, sprite, box, centre) for name, sprite, box, centre in PIECES if not only or name in only]
    pieces_of(whole, nub, specs, m, options, out, fl, check, sheets)
    for spec in FRAMES:
        tl, tr = spec[0], spec[1]
        names = {"tan_dome_tl": "tan_dome_%d" % tl, "tan_dome_tr": "tan_dome_%d" % tr}
        fspecs = [(names[name], {"tan_dome_tl": tl, "tan_dome_tr": tr}[name], box, centre)
                  for name, sprite, box, centre in PIECES[:2] if not only or names[name] in only]
        if not fspecs and "whole" not in options:
            continue
        fire = fire_parts(spec)
        # The fire ball engulfs the nub: in these frames the nub glows in the fire's outer red (a material fewer).
        fnub = [o.copy() for o in nub]
        for o, src in zip(fnub, nub):
            o.data = src.data.copy()
            bpy.context.scene.collection.objects.link(o)
        fnub[0].data.materials[0] = fire[0].data.materials[0]
        if "whole" in options:
            view = [o.copy() for o in [whole] + fnub + fire]
            for o, src in zip(view, [whole] + fnub + fire):
                o.data = src.data.copy()
                bpy.context.scene.collection.objects.link(o)
            triangulate(view)
            mk.export(view, options["whole"] + "tan_dome_%d.glb" % tl)
            for o in view:
                bpy.data.objects.remove(o)
        pieces_of(whole, fnub + fire, fspecs, m, options, out, fl, check, sheets)
        for o in fnub + fire:
            bpy.data.objects.remove(o)
    name, sprite, centre = DAMAGED
    if not only or name in only:
        for o in [whole] + nub:
            o.hide_render = True
        parts = shards(m)
        mask = None
        if check:
            shade = np.full((28, 24), False)
            for c, r, length, h in SHARDS:
                pass
            mask = None
        export(parts, name, options, out, None, centre)


if __name__ == "__main__":
    build()
