"""TYRIAN's steel darts (shots sheet sprites 145, 146 and 147, 1x1: 12 x 14 cells), modelled (2026-10-29, round 2 of the
shots' models: until then they were drawn as their sprites with volume and the automatic glow, 13 pixels at 0.7 in the
sprite's near-white 0x5f, which made a grey-violet steel dart a glowing ball).

Who fires them: enemy weapons 2 (146, straight down the screen at 4 pixels a frame), 3 (147) and 4 (145) of episodes 1
and 3, the three turrets of enemy 15 (TYRIAN's grey gun towers, also TYRIAN X) and enemy 194 (ASTEROID2, ASTEROID?),
once fire override events give them a frequency (TYRIAN fires them from clock 2992 on), and weapon 8 (145, faster:
SAVARA, SAVARA V, SAVARA Y). An enemy's first turret fires as the weapon's data says, its second and third with the
velocity turned a quarter (tyrian2.c): so 146 flies down, 147 down and right, 145 down and left, each pointing the way
it flies. None is animated (weapani 0).

As the sprites draw them: a spindle of steel in ramp 5 (grey-violet, 0x54 at its edges to a near-white 0x5f highlight)
inside a one-pixel outline of 0x31 (a blue-black): 146 is 5 pixels wide and 11 long (column 5, rows 2-12), its widest
rows 5-10, a thin one-pixel spike of outline at its top (rows 2-3) and a short point at its bottom (rows 11-12); its
middle column brightens down the dart (0x57 at row 5 to 0x5f at row 9, the highlight two pixels behind the point, 0x59
and 0x55 in the point). 145 and 147 are the same dart drawn at 45 degrees, its point down and left (145: rows 3-11, the
highlight at column 2, row 9) or down and right (147).

The model: a steel dart pointing down the screen as 146 draws it (yaw 0), its axis on the sprite's column 5 (x = -0.5):
a faceted spindle, flat underneath (the camera never sees an underside), its section half an octagon (a narrow ridge on
top, two slopes, two wide rims down to z = 0) lofted along it from the sprite's outline (widest 2.1 pixels behind the
point, as the sprite's rows 8-9, tapering to a sharp point in front and a long thin tail behind), the facets kept sharp,
smooth along the dart. Its colours are ramp 5's (palette materials: they follow the level's palette and fades), steel
with a bright ridge, as the sprite is a dark outline round a bright middle: the ridge in bands like the sprite's middle
column (0x58 at the tail, 0x5b, 0x5d, the polished 0x5f behind the point, the point itself 0x5b), the slopes 0x57 and
0x56, the rims dark (0x53: the sprite's outline, as the camera sees the dart's edges). Three small swept fins at the
tail (one up, two out to the sides, 0x56) make its thin spike. Steel, metallic 0.15, roughness 0.45 (glossier steel
mirrored the bright sky and read as a pale lilac seed against TYRIAN's grey stone), its ridge glowing faintly in its
own colours (0.2-0.45, brightest on the polished part): an enemy's bullet must read at 1x, and the first version, dark
steel without a glow (rims 0x51, slopes 0x54 and 0x53), was a thin dark needle over TYRIAN's grey stone where the
sprite had been a bright violet lens (2026-10-30). 240 triangles, 7 materials. Its line's glow= keeps it from the
automatic glow (which made the dart a glowing ball): 9 pixels at 0.35 in 0x5e on the polished part. 145 and 147 take it turned (yaw 45, 315) and
moved (at=) onto their pixels (TILTS: measured by laying 146's pixels, turned, on theirs).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the origin at the
sprite's centre (pixel 6, 7 of the cell); the dart stands on z = 0 (the game centres shot models in height).

models.cfg (the shots section; --cfg writes them):
    model shot_dart shots/shot_dart.glb
    shot shots 146 shot_dart                       glow=9:0.35:94:-0.5:3.5
    shot shots 145 shot_dart yaw=45 at=-0.85:0.55  glow=9:0.35:94:-3.68:2.67
    shot shots 147 shot_dart yaw=315 at=1.55:-0.15 glow=9:0.35:94:3.67:2.68

Run: Blender -b --factory-startup -P tools/blender/models/shots/polish_shot_dart.py -- [--outdir <dir>] (default
     assets/models/shots) [--check <sheets dir>] (the model against 146 as built, and turned and moved onto 145 and 147,
     in <dir>/shots.png from TYR3D_EXTRACT) [--preview <prefix>] [--cfg <file>]
"""
import math
import os
import sys

import bpy
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_shot_pulse as pp  # noqa: E402  (its kit: tyrkit, the machine kit, the checks and the game view)
from polish_shot_pulse import k, mk  # noqa: E402

OUTDIR = pp.OUTDIR
NAME = "shot_dart"
AXIS_X = -0.5  # the sprite's column 5

# The dart's outline along it: (y, half-width), from the point (y -6, the bottom edge of row 12) to the tail's tip (y 5,
# the top edge of row 2). The height over z = 0 is HEIGHT times the half-width.
PROFILE = [(-6.0, 0.0), (-5.6, 0.44), (-5.0, 0.98), (-4.3, 1.48), (-3.5, 1.85), (-2.6, 2.07), (-1.6, 2.1),
           (-0.4, 2.02), (0.8, 1.84), (1.8, 1.52), (2.6, 1.06), (3.3, 0.58), (4.1, 0.3), (4.7, 0.15), (5.0, 0.0)]
HEIGHT = 0.78
# The section, from the right rim over the top to the left: (x, z) as fractions of the half-width and the height.
SECTION = [(1.0, 0.0), (0.62, 0.66), (0.24, 1.0), (-0.24, 1.0), (-0.62, 0.66), (-1.0, 0.0)]
FACETS = ["rim", "slope", "top", "slope", "rim"]  # between the section's points
# The top facet's bands along the dart (from y, palette index), the point first; the slopes' (from y, index).
TOP_BANDS = [(-99.0, 0x5b), (-5.2, 0x5f), (-1.8, 0x5d), (0.6, 0x5b), (2.4, 0x58)]
SLOPE_BANDS = [(-99.0, 0x57), (-0.6, 0x56)]
RIM = 0x53
FIN = 0x56
METALLIC, ROUGHNESS = 0.15, 0.45
# The ridge's faint glow in its own colour (palette index: emission strength); the rest is unlit steel.
EMIT = {0x5f: 0.45, 0x5d: 0.3, 0x5b: 0.2}
# The fins: (where along y their root starts and ends, how far they reach, their thickness).
FIN_ROOT = (2.6, 4.7)
FIN_REACH = 0.7
FIN_THICKNESS = 0.14

# The sprites: (sprite, yaw, at dx, at dy (game pixels, dy down the screen)); 146 is the model as built, 145 and 147 it
# turned and moved onto their pixels (the offsets measured by fit_offset; --check measures them again and prints both).
TILTS = [(146, 0.0, 0.0, 0.0), (145, 45.0, -0.85, 0.55), (147, 315.0, 1.55, -0.15)]
# The glow: size, strength, palette index, where on the model (x, y: the polished part behind the point).
GLOW = (9, 0.35, 0x5e, (AXIS_X, -3.5))


def material(index, metallic=METALLIC, roughness=ROUGHNESS):
    strength = EMIT.get(index, 0.0)
    return k.material(f"dart_{index:02x}", palette=index, metallic=metallic, roughness=roughness,
                      emission=k.level_palette()[index] if strength > 0 else None, emission_strength=strength)


def half_width(y):
    for (y0, w0), (y1, w1) in zip(PROFILE, PROFILE[1:]):
        if y0 <= y <= y1:
            t = (y - y0) / (y1 - y0)
            return w0 + (w1 - w0) * t
    return 0.0


def band(bands, y):
    index = bands[0][1]
    for start, i in bands:
        if y >= start:
            index = i
    return index


def body(mats):
    """The spindle: rings at the profile's points and at the bands' borders, each ring the half-octagon section; the
    faces between two rings take their facet's material at their middle's y; fans to the point and the tail's tip."""
    ys = sorted({y for y, _ in PROFILE[1:-1]} | {b for b, _ in TOP_BANDS[1:]} | {b for b, _ in SLOPE_BANDS[1:]})
    rings = []
    for y in ys:
        w = half_width(y)
        h = w * HEIGHT
        rings.append([(AXIS_X + w * sx, y, h * sz) for sx, sz in SECTION])
    verts = [p for ring in rings for p in ring]
    nose = len(verts)
    verts.append((AXIS_X, PROFILE[0][0], 0.0))
    tail = len(verts)
    verts.append((AXIS_X, PROFILE[-1][0], 0.0))
    n = len(SECTION)
    faces, face_mats = [], []

    def facet_mat(j, y):
        kind = FACETS[j]
        if kind == "top":
            return mats[band(TOP_BANDS, y)]
        if kind == "slope":
            return mats[band(SLOPE_BANDS, y)]
        return mats[RIM]
    for i in range(len(rings) - 1):
        a, b = i * n, (i + 1) * n
        ym = (ys[i] + ys[i + 1]) / 2
        for j in range(n - 1):
            faces.append((a + j, b + j, b + j + 1, a + j + 1))
            face_mats.append(facet_mat(j, ym))
        faces.append((a + n - 1, b + n - 1, b, a))  # the flat underside
        face_mats.append(mats[RIM])
    first, last = 0, (len(rings) - 1) * n
    for j in range(n - 1):
        faces.append((nose, first + j, first + j + 1))
        face_mats.append(facet_mat(j, PROFILE[0][0]))
        faces.append((tail, last + j + 1, last + j))
        face_mats.append(mats[FIN] if FACETS[j] != "rim" else mats[RIM])
    faces.append((nose, first + n - 1, first))
    face_mats.append(mats[RIM])
    faces.append((tail, last, last + n - 1))
    face_mats.append(mats[RIM])
    return finish("dart_body", verts, faces, face_mats, 25)


def finish(name, verts, faces, face_mats, angle):
    obj = k.mesh_object(name, verts, faces)
    used = []
    for m in face_mats:
        if m not in used:
            used.append(m)
    for m in used:
        obj.data.materials.append(m)
    for poly, m in zip(obj.data.polygons, face_mats):
        poly.material_index = used.index(m)
    k.recalc_normals(obj)
    return k.smooth(obj, angle)


def fin(name, mat, direction):
    """A swept fin from the tail's surface: its root along the dart (FIN_ROOT), reaching out FIN_REACH at its back end
    (a triangle swept back: the leading edge slopes from the root's front to the tip), FIN_THICKNESS thick; direction:
    the unit (x, z) it reaches out to, from the dart's ridge (up) or rims (sideways)."""
    y0, y1 = FIN_ROOT
    dx, dz = direction
    t = FIN_THICKNESS / 2
    # the side the thickness goes to: across the fin's plane
    ox, oz = -dz, dx

    def root(y):
        w = half_width(y)
        if dz > 0.5:  # the top fin stands on the top facet
            return AXIS_X, w * HEIGHT
        return AXIS_X + dx * w * 0.92, w * HEIGHT * 0.3
    tip_y = y1 - 0.15
    rx0, rz0 = root(y0)
    rx1, rz1 = root(y1 - 0.05)
    rxt, rzt = root(tip_y)
    reach = FIN_REACH
    pts = [(rx0, y0, rz0), (rx1, y1 - 0.05, rz1), (rxt + dx * reach, tip_y + 0.25, rzt + dz * reach)]
    verts = []
    for s in (1, -1):
        for x, y, z in pts:
            verts.append((x + s * ox * t, y, z + s * oz * t))
    faces = [(0, 1, 2), (5, 4, 3), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)]
    return finish(name, verts, faces, [mat] * len(faces), 30)


def build_model():
    indices = sorted({i for _, i in TOP_BANDS} | {i for _, i in SLOPE_BANDS} | {RIM, FIN})
    mats = {i: material(i) for i in indices}
    parts = [body(mats)]
    parts.append(fin("dart_fin_top", mats[FIN], (0.0, 1.0)))
    for side in (1, -1):
        a = math.radians(14)
        parts.append(fin(f"dart_fin_{'r' if side > 0 else 'l'}", mats[FIN], (side * math.cos(a), math.sin(a))))
    return pp.triangulate(parts)


# --- Where the turned dart lands on the tilted sprites ----------------------------------------------------------------

def sprite_points(sheet, sprite):
    """The sprite's pixel centres (model coordinates) and brightness (the shade in ramp 5, the outline 1)."""
    from sprite_profile import sprite_indices
    rows = sprite_indices(sheet, sprite, large=False)
    pts = []
    for r, row in enumerate(rows):
        for c, v in enumerate(row):
            if v:
                pts.append((c + 0.5 - 6.0, 6.5 - r, (v & 15) if v >> 4 == 5 else 1.0))
    return pts


def fit_offset(ref, target, yaw, reach=4.0, step=0.05):
    """The shift (model coordinates) that lays the reference's pixels turned by yaw onto the target's: both blurred
    (0.6 pixels), scored by coverage and brightness together."""
    import numpy as np
    sigma = 0.6
    t = math.radians(yaw)
    c, s = math.cos(t), math.sin(t)
    r = np.array(ref)
    tx = np.array([p[0] for p in target])
    ty = np.array([p[1] for p in target])
    tb = np.array([p[2] for p in target]) / 15.0
    rx = r[:, 0] * c + r[:, 1] * s
    ry = -r[:, 0] * s + r[:, 1] * c
    rb = r[:, 2] / 15.0
    best = None
    shifts = np.arange(-reach, reach + 1e-9, step)
    for dx in shifts:
        X = rx[:, None] + dx
        for dy in shifts:
            Y = ry[:, None] + dy
            g = np.exp(-((X - tx[None, :]) ** 2 + (Y - ty[None, :]) ** 2) / (2 * sigma * sigma))
            score = g.sum() + (g * rb[:, None] * tb[None, :]).sum()
            if best is None or score > best[0]:
                best = (score, dx, dy)
    return best[1], best[2]


def measure(sheets):
    """The offsets measured again against the sprites (printed beside TILTS's)."""
    ref = sprite_points(os.path.join(sheets, "shots.png"), 146)
    for sprite, yaw, dx, dy in TILTS:
        if sprite != 146:
            mx, my = fit_offset(ref, sprite_points(os.path.join(sheets, "shots.png"), sprite), yaw)
            print("  shots %d yaw %s: measured at=%s:%s (TILTS: %s:%s)" % (sprite, fmt(yaw), fmt(round(mx * 20) / 20),
                  fmt(-round(my * 20) / 20), fmt(dx), fmt(dy)))


def turned(x, y, yaw):
    t = math.radians(yaw)
    return x * math.cos(t) + y * math.sin(t), -x * math.sin(t) + y * math.cos(t)


def fmt(v):
    s = ("%.2f" % v).rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def cfg_lines(lines_tilts):
    size, strength, colour, (hx, hy) = GLOW
    out = ["model %s shots/%s.glb" % (NAME, NAME)]
    what = {146: "a steel dart, down (enemy weapon 2)", 145: "down and left (weapons 4, 8)",
            147: "down and right (weapon 3)"}
    rows = []
    for sprite, yaw, dx, dy in lines_tilts:
        gx, gy = turned(hx, hy, yaw)
        turn = "" if yaw == 0 else " yaw=%s at=%s:%s" % (fmt(yaw), fmt(dx), fmt(dy))
        head = "shot shots %d %s" % (sprite, NAME) + turn
        rows.append((head, "glow=%d:%s:%d:%s:%s" % (size, fmt(strength), colour, fmt(gx + dx), fmt(-gy + dy)),
                     what[sprite]))
    w0 = max(len(r[0]) for r in rows)
    w1 = max(len(r[1]) for r in rows)
    for head, glow, comment in rows:
        out.append("%s %s  # %s" % (head.ljust(w0), glow.ljust(w1), comment))
    return out


def build():
    options = k.args()
    outdir = options.get("outdir", OUTDIR)
    k.reset()
    parts = build_model()
    bpy.context.view_layer.update()
    print(f"== {NAME}: a steel dart, down the screen as 146 draws it")
    lines_tilts = TILTS
    if "check" in options:
        measure(options["check"])
        frames = [(sprite, Matrix.Translation((dx, -dy, 0.0)) @ pp.turn(yaw), f"shots {sprite} (yaw {fmt(yaw)} at "
                   f"{fmt(dx)}:{fmt(dy)})") for sprite, yaw, dx, dy in lines_tilts]
        pp.check_frames(parts, os.path.join(options["check"], "shots.png"), frames, move_to_frame=False)
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mk.report(NAME, parts, os.path.join(outdir, NAME + ".glb"))
    if "preview" in options:
        pp.game_view(options["preview"] + NAME, parts)
    if "cfg" in options:
        with open(options["cfg"], "w") as f:
            f.write("\n".join(cfg_lines(lines_tilts)) + "\n")
        print("wrote", options["cfg"])


if __name__ == "__main__":
    build()
