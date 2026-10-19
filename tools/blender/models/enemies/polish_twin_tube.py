"""The small tan twin tube that comes in swarms in IXMUCANE and SAWBLADES (sheet 8 sprite 19, 1x1: 12 x 14 pixels;
sky layer; its animation 19 38 57 76 95 114 133 152 132 151), polished (2026-10-19; it replaces wave3_y.py's
twin_tube()). models.cfg: sprite 8 19 twin_tube yaw=0 roll=frames:20 (unchanged).

Its frames roll it about its length, half a turn in ten frames: in 19 the two tubes lie side by side
(columns 1-2 and 9-10) with the flat middle tube between them; they close up (38, 57, 76, 95) until they lie
one above the other (114, one tube seen), then open again the other way (133, 152, 132, 151), their shading
mirrored. While they close, the left tube is the one in front (its three columns all show, the right one
hides behind it): the left tube rises towards the camera. The game rolls the model by (frame - 1) x 18
degrees about its nose axis (tyrian2.c, render_gpu.c: a turn about the screen's y axis that lifts the
model's left side towards the camera), which is that roll: so the model is built as frame 19 shows it, the
tubes' axes along y in the plane z = 0, symmetric about x = 0 and z = 0 (the game centres sky objects in
height, so the roll's axis runs midway between the tubes), and roll=frames:20 stays. A half turn brings it
back to itself, so the ten frames loop.

As the 4x upscale and the frames draw it:
- two tan tubes (x -4.05 and 4.05, radius 1.55, rows 0-13), their tops glowing red (row 1: 0x74-0x7b, as the
  frames flicker), a light collar under the glow (row 2) and another at row 8 with a groove below it (row
  9); their lower ends narrow into forks (rows 11-12): one prong shows in 19, where the fork's slot lies
  flat, two in 114, where it stands up;
- between them a flat middle tube (columns 3-8 in 19, two in 38: it is seen edge-on from 76 on), joined to
  the tubes from row 2 to row 7, its lower end (rows 8-10) free of them, a dark notch up its middle
  between two short legs (row 10).

Origin at the sprite's centre (pixel 6, 7); +Y up the sprite, +Z towards the camera.

Replaces wave3_y.py's twin_tube() (with its @y.model decorator) and TWIN, and wave3_y_art.py's TWIN and
TWIN_EDGE (TWIN_EDGE is used nowhere): remove them so that they don't overwrite this model.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir or enemy_8.png> (the
silhouette rolled to each of the ten frames against its sprite), --preview <prefix>.
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402

FRAMES = [19, 38, 57, 76, 95, 114, 133, 152, 132, 151]   # the animation; the game rolls 18 degrees a frame
ROLL_STEP = 18.0

TUBE_X, TUBE_R = 4.05, 1.55
TOP, BOTTOM = 6.65, -6.6          # the tubes' ends (2/3 into rows 0 and 13)
GLOW_Y = 5.05                     # the glowing top below this... (row 1)
COLLARS = [(4.05, 5.0), (-2.05, -1.0)]  # (from y, to y): rows 2 and 8
GROOVE_Y = -2.45                  # row 9
FORK_Y = -4.35                    # the fork's slot from here down (rows 11-12)
FORK_GAP = 0.36                   # half the slot's width
# The middle tube: half-width, half-thickness; from its top down to where it leaves the tubes, then its
# lower end and its legs.
MID_HALF, MID_THICK = 2.75, 0.95
MID_TOP, MID_JOIN, MID_BOTTOM = 5.6, -1.2, -4.6
LEG_HALF, NOTCH_HALF, NOTCH_TOP = 1.95, 0.72, -2.6


def lathe(name, profile, mat, x, segments=24, flatten=1.0):
    """A body of revolution about the line (x, *, 0) along y: profile [(y, radius)] in increasing y."""
    rings = [k.ring(y, r, r * flatten, segments, z=0.0, x=x) for y, r in profile if r > 0]
    first, last = profile[0], profile[-1]
    obj = k.loft(name, rings, mat, start_point=(x, first[0], 0.0), end_point=(x, last[0], 0.0))
    return obj


def tube(side, m):
    """One tube: its body with the collars and the groove, its glowing top, its forked lower end."""
    x = side * TUBE_X
    r = TUBE_R
    out = []
    # The body from the fork's root to under the glow; the collars and the groove are part of its profile.
    (c0a, c0b), (c1a, c1b) = COLLARS
    prof = [(FORK_Y - 0.02, r * 0.86), (FORK_Y + 0.4, r * 0.95), (FORK_Y + 0.9, r), (GROOVE_Y - 0.3, r),
            (GROOVE_Y - 0.12, r * 0.88), (GROOVE_Y + 0.12, r * 0.88), (GROOVE_Y + 0.25, r), (c1a - 0.05, r),
            (c1a + 0.05, r + 0.16), (c1a + 0.15, r + 0.2), (c1b - 0.15, r + 0.2), (c1b - 0.05, r + 0.16),
            (c1b + 0.05, r), (c0a - 0.05, r), (c0a + 0.05, r + 0.15), (c0a + 0.15, r + 0.2), (c0b - 0.12, r + 0.2),
            (c0b - 0.02, r + 0.12), (GLOW_Y, r * 0.97)]
    rings = [k.ring(y, rr, rr, 28, z=0.0, x=x) for y, rr in prof]
    body = k.loft(f"tube{side}", rings, None, cap_start=True, cap_end=False, start_point=(x, FORK_Y - 0.02, 0.0))
    for name in ("tan", "collar", "tan_dark"):
        body.data.materials.append(m[name])
    n = 28
    for poly in body.data.polygons:
        i = poly.index // n
        if i < len(prof) - 1:
            y0, y1 = prof[i][0], prof[i + 1][0]
            yc = 0.5 * (y0 + y1)
            if c1a <= yc <= c1b or c0a <= yc <= c0b:
                poly.material_index = 1
            elif GROOVE_Y - 0.12 <= yc <= GROOVE_Y + 0.12:
                poly.material_index = 2
    out.append(k.smooth(body, 40))
    # The glowing top: a short red section closed by a dome, a hot core showing through its end.
    glow = [(GLOW_Y - 0.1, r * 0.97), (GLOW_Y + 0.25, r * 0.98), (TOP - 0.55, r * 0.92), (TOP - 0.3, r * 0.75),
            (TOP - 0.12, r * 0.5), (TOP, 0.0)]
    rings = [k.ring(y, rr, rr, 28, z=0.0, x=x) for y, rr in glow if rr > 0]
    cap = k.loft(f"glow{side}", rings, m["glow"], start_point=(x, GLOW_Y - 0.1, 0.0), end_point=(x, TOP, 0.0))
    out.append(k.smooth(cap, 50))
    core = k.ellipsoid(f"glow_core{side}", (x, TOP - 0.5, 0.0), (r * 0.62, 0.62, r * 0.62), m["glow_hot"], 16, 8)
    out.append(k.smooth(core, 60))
    # The fork: two prongs (above and below the slot, which lies in the plane of the tubes), narrowing to
    # the tube's lower end.
    for zs in (-1, 1):
        rings = []
        ys = [FORK_Y + 0.15, FORK_Y - 0.3, FORK_Y - 0.8, FORK_Y - 1.3, FORK_Y - 1.7, BOTTOM + 0.25]
        for y in ys:
            t = max(0.0, (FORK_Y - y) / (FORK_Y - BOTTOM))
            rr = r * (0.86 - 0.42 * t ** 1.3)
            ring = []
            for a in range(16):  # a half disc above (or below) the slot, rounded at its corners
                ang = math.pi * a / 15
                c, s = math.cos(ang), math.sin(ang)
                ring.append(Vector((x + rr * c, y, zs * (FORK_GAP + (rr - FORK_GAP) * max(s, 0.0) ** 0.9))))
            rings.append(ring[::zs])
        prong = k.loft(f"prong{side}{zs}", rings, m["tan_dark"], end_point=(x, BOTTOM, zs * (FORK_GAP + 0.25 * r)))
        out.append(k.smooth(prong, 50))
    # The slot's floor, dark, at the fork's root.
    out.append(k.box(f"slot{side}", (x, FORK_Y - 0.05, 0.0), (r * 1.6, 0.25, 2 * FORK_GAP), m["notch"]))
    return out


def middle(m):
    """The flat middle tube: joined to the tubes from its top to MID_JOIN, below that free of them, a dark
    notch up its middle between two short legs."""
    out = []
    ys = [MID_TOP - 0.02, MID_TOP - 0.15, MID_TOP - 0.4, MID_TOP - 0.8] + \
         [MID_TOP - 0.8 + (MID_JOIN + 0.6 - MID_TOP + 0.8) * i / 6 for i in range(1, 7)] + [MID_JOIN + 0.3, MID_JOIN]
    rings = []
    for y in ys:
        f = min(1.0, (MID_TOP - y) / 0.8)
        f = math.sqrt(max(0.0, 1 - (1 - f) ** 2))
        hw = MID_HALF if y > MID_JOIN + 0.6 else LEG_HALF + (MID_HALF - LEG_HALF) * (y - MID_JOIN) / 0.6
        rings.append(k.ring(y, hw, MID_THICK * max(f, 0.3), 32, z=0.0, power=2.6))
    upper = k.loft("middle", rings[::-1], m["middle"], start_point=(0, MID_JOIN, 0.0), end_point=(0, MID_TOP, 0.0))
    out.append(k.smooth(upper, 45))
    # A light ridge along its middle, on top and underneath (the sprite's bright column; underneath too, so
    # that half a turn brings the model back to itself).
    for zs in (-1, 1):
        ys = [MID_JOIN + 0.2 + (MID_TOP - 0.55 - MID_JOIN - 0.2) * i / 10 for i in range(11)]
        rings = []
        for y in ys:
            f = min(1.0, (y - MID_JOIN - 0.2) / 0.5, (MID_TOP - 0.55 - y) / 0.5)
            f = math.sqrt(max(0.0, 1 - (1 - max(f, 0.0)) ** 2))
            rings.append(k.ring(y, 0.55 * max(f, 0.2), 1.0, 12, z=zs * (MID_THICK - 0.2), top=0.42 * max(f, 0.3) if zs > 0 else 0.3,
                                bottom=0.42 * max(f, 0.3) if zs < 0 else 0.3, power=2.2))
        ridge = k.loft(f"ridge{zs}", rings, m["collar"])
        out.append(k.smooth(ridge, 50))
    # The lower end: two legs, either side of the notch, flattened like the middle tube.
    for side in (-1, 1):
        x0, x1 = side * NOTCH_HALF, side * LEG_HALF
        xc, hw = 0.5 * (x0 + x1), 0.5 * abs(x1 - x0)
        ys = [MID_JOIN + 0.35, MID_JOIN - 0.4, NOTCH_TOP, NOTCH_TOP - 0.7, MID_BOTTOM + 0.6, MID_BOTTOM + 0.25,
              MID_BOTTOM + 0.05]
        rings = []
        for y in ys:
            f = min(1.0, (y - MID_BOTTOM) / 0.6)
            f = math.sqrt(max(0.0, 1 - (1 - f) ** 2))
            rings.append(k.ring(y, hw * max(f, 0.35), MID_THICK * 0.92 * max(f, 0.35), 20, z=0.0, x=xc, power=2.6))
        leg = k.loft(f"leg{side}", rings[::-1], m["tan_dark"], start_point=(xc, MID_BOTTOM, 0.0),
                     end_point=(xc, MID_JOIN + 0.35, 0.0))
        out.append(k.smooth(leg, 50))
    # The dark notch: a block between the legs, under the middle tube's lower end.
    out.append(k.box("notch", (0.0, 0.5 * (NOTCH_TOP + MID_JOIN) - 0.1, 0.0),
                     (2 * NOTCH_HALF + 0.1, MID_JOIN - NOTCH_TOP + 0.4, 2 * MID_THICK * 0.8), m["notch"]))
    return out


def materials():
    pal = k.level_palette()
    return {
        "tan": k.material("twin_tan", palette=0x1a, metallic=0.3, roughness=0.38),
        "collar": k.material("twin_collar", palette=0x1c, metallic=0.3, roughness=0.32),
        "tan_dark": k.material("twin_tan_dark", palette=0x17, metallic=0.3, roughness=0.42),
        "middle": k.material("twin_middle", palette=0x19, metallic=0.3, roughness=0.36),
        "notch": k.material("twin_notch", palette=0x12, metallic=0.2, roughness=0.6),
        "glow": k.material("twin_glow", palette=0x77, roughness=0.5, emission=pal[0x77], emission_strength=1.1),
        "glow_hot": k.material("twin_glow_hot", palette=0x7a, roughness=0.5, emission=pal[0x7a], emission_strength=1.6),
    }


def triangles():
    depsgraph = bpy.context.evaluated_depsgraph_get()
    total = 0
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            evaluated = obj.evaluated_get(depsgraph)
            mesh = evaluated.to_mesh()
            mesh.calc_loop_triangles()
            total += len(mesh.loop_triangles)
            evaluated.to_mesh_clear()
    return total


def bounds():
    vs = [obj.matrix_world @ v.co for obj in bpy.context.scene.objects if obj.type == "MESH" for v in obj.data.vertices]
    return [min(v[i] for v in vs) for i in range(3)], [max(v[i] for v in vs) for i in range(3)]


def roll_all(degrees):
    """Turns every mesh as the game rolls the model: about the model's nose axis (+Y here), lifting its
    left side (-X) towards the camera (+Z) for positive angles."""
    rot = Matrix.Rotation(math.radians(degrees), 4, "Y")
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            obj.data.transform(rot)


def build():
    options = k.args()
    k.reset()
    m = materials()
    for side in (-1, 1):
        tube(side, m)
    middle(m)
    used = {mat.name for o in bpy.context.scene.objects if o.type == "MESH" for mat in o.data.materials}
    low, high = bounds()
    print("== twin_tube (8 19): %d triangles, %d materials, x %.2f to %.2f, y %.2f to %.2f, z %.2f to %.2f: %s" % (
        triangles(), len(used), low[0], high[0], low[1], high[1], low[2], high[2], ", ".join(sorted(used))))
    if "check" in options:
        sheet = options["check"]
        sheet = os.path.join(sheet, "enemy_8.png") if os.path.isdir(sheet) else sheet
        for i, sprite in enumerate(FRAMES):
            print("-- frame %d (8 %d), rolled %d degrees:" % (i, sprite, ROLL_STEP * i))
            roll_all(ROLL_STEP * i)
            k.check_silhouette(sheet, sprite, large=False)
            roll_all(-ROLL_STEP * i)
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    path = os.path.join(outdir, "twin_tube.glb")
    k.export(path)
    print("%s: %.1f KB" % (path, os.path.getsize(path) / 1024))
    if "preview" in options:
        k.preview(options["preview"] + "twin_tube", size=(12, 14), scale=24)


if __name__ == "__main__":
    build()
