"""The SDF Main Gun's beam (shots2 sheet sprites 58-63, all 1x1: 12 x 14 cells), modelled (2026-10-30, round 3 of the
energy shots' models; until then each segment was drawn as its sprite with volume, flat, from the 4x sheets, with the
automatic glow).

Who fires it: the SDF Main Gun, a special weapon (special 41, stype 9: a "flare" linked to the player): a press of the
fire button (a new press: varz.c JE_doSpecialShot) starts it, and for 8 + 2 x the front weapon's power ticks (power 11:
30) it fires weapon 778 every tick (shotrepeat 0): two segments at once (multi 2), 6 pixels left and right of the ship
(bx -6 and 6, by 10), each 14 pixels long and flying up 14 pixels a tick (sy 14, the cell's height) while following
the ship (sx 101), so that they join end to end into one beam 24 pixels wide reaching up the screen; their damage 251
(over 250: they pierce, so the beam is never cut). Its four positions take turns (max 4): one tick 558 (left) and 561
(right), the next 559 and 562; each segment shows weapani + 1 = 2 frames (558 559, 561 562, 559 560, 562 563), so at
any tick a whole column shows one look: the left column 58 or 60 one tick and 59 the next, the right one 61 or 63 and
62. Nothing else fires these sprites.

As the sprites draw it: each a half of a white beam, 12 pixels wide, white (0x0f) to its inner side (where it meets the
other half) and blue at its outer edge (0x94, then 0x9c), a crackle of light blue (0x9f, a stroke a pixel wide
wandering between the 3rd and 4th columns from the edge, paler 0x8c beside it, 0x8e dots further in) running down it
inside the blue edge. 58 and 60 are the same; 59 is 58 turned upside down (the crackle mirrored top to bottom); 61 is 58
turned half round (the right half: its edge on the right), 62 is 59 turned half round, 63 is 61: the beam's two crackles
flicker by turns, a tick each.

The models: a length of the beam 14 pixels long (y -7 to 7), so that the segments join into one beam: the half of a
wide rod, round on top and flat underneath (the game's camera only ever sees shots from above), its section a quarter
of a flattened ellipse rising from the outer edge (x -6, z 0) to the beam's middle line (x 6, its top: DEPTH times the
beam's half-width), closed by a wall at the middle line where the other half meets it. Its colours in stripes along it
(the mesh's own section points, no face cut): the dark blue rim (0x94) and the blue (0x9c) at the outer edge, pale
cyan under the crackle (0x8c) and beside it (0x8e), white (0x0f) over the middle, each glowing in its own colour
(0.26-0.34: the beam is wide and white, and the game's bloom burned it into one white mass at more). The crackle: a
filament of light blue light (0x9f, glowing 0.5) lying on the rod and standing out of it, zigzagging along it as the
sprite's light-blue stroke goes row by row (its swing a little wider than the pixels'), with short forks reaching in
where the sprite draws its paler pixels beside the stroke and small sparks where it draws its dots; its ends meet the
next segment's in the same place (the stroke's middle, 3 pixels in from the edge), so that the crackle runs on unbroken
up the beam. Both ends are rounded (a quarter dome a quarter of the beam's half-width long, inside the next segment
where they join: the beam's foot at the ship and its front; the right half is the left turned half round, so its ends
swap), each end an object of its own (the rounding would bend the length's normals: a shading line at every joint).
Two models, the two crackles (58's, and 59's: 58 upside down): 58, 60 and 59 as drawn, the right half's 61, 63 and 62
the same models turned half round (yaw=180). Both have the same height bounds (the crackle stays below the middle
line's top), so the game centres them alike and the beam is level. 404 triangles, 6 materials each.

Each line takes beam (models.cfg: in the tick a segment is fired a copy of it stays where it was fired, so that between
ticks the beam, moving on, still reaches the gun) and a weak blue glow on its outer edge (every segment carries one, 60
at a time at power 11: they add up).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the origin at the
sprite's centre (pixel 6, 7 of the cell: column c is x = c + 0.5 - 6, row r is y = 6.5 - r); the beam stands on z = 0
(the game centres shot models in height on the player's layer).

models.cfg (the shots section): the build prints the model and shot lines (SHOTS below).

Run: Blender -b --factory-startup -P tools/blender/models/shots/polish_shot_sdf.py -- [--only <name,...>]
     [--outdir <dir>] (default assets/models/shots) [--check <sheets dir>] (each model's top view against its sprites
     in <dir>/shots2.png, turned as their lines say) [--preview <prefix>] (top, three-quarter and game-camera views, and
     <prefix>beam_game.png: a beam of segments joined end to end, both halves, as the game draws it)
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ENEMIES = os.path.join(HERE, "..", "enemies")
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, ENEMIES)
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_launched_flames import grid, lit, check_frames, turn  # noqa: E402
from polish_shot_starburst import game_camera  # noqa: E402

OUTDIR = os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "shots")
HALF = 7.0  # half a segment's length (the cell's 14 rows)

# --- The sprites (palette indices; rows top to bottom): the left half's two crackles --------------------------------

SPRITES = {
    58: """
94 9c 0f 9f 8c 0f 0f 0f 0f 0f 0f 0f
94 9c 9f 0f 0f 0f 0f 0f 0f 0f 0f 0f
94 9c 9f 9f 8c 0f 0f 0f 0f 0f 0f 0f
94 9c 9f 1f 0f 8e 0f 0f 0f 0f 0f 0f
94 9c 9f 9f 0f 0f 0f 0f 0f 0f 0f 0f
94 9c 9f 0f 0f 0f 0f 0f 0f 0f 0f 0f
94 9c 0f 9f 8c 0f 0f 0f 0f 0f 0f 0f
94 8d 9f 9f 0f 0f 0f 0f 0f 0f 0f 0f
94 9c 0f 0f 0f 8e 0f 0f 0f 0f 0f 0f
94 9c 0f 9f 8c 0f 0f 0f 0f 0f 0f 0f
94 9c 9f 0f 0f 0f 0f 0f 0f 0f 0f 0f
94 9c 9f 9f 0f 0f 0f 0f 0f 0f 0f 0f
94 9c 0f 9f 8c 0f 0f 0f 0f 0f 0f 0f
94 9c 9f 0f 0f 8e 0f 0f 0f 0f 0f 0f
""",
}
SPRITES[59] = "\n".join(reversed(SPRITES[58].strip("\n").splitlines()))  # (59 is 58 upside down)

# --- The beam ---------------------------------------------------------------------------------------------------------
# The rod: the beam's half-width (two halves of 12), its height over that (flattened: a beam, not a pipe), the stripes
# across the half from its outer edge ((from x, palette index)), and the points round its section between the stripes'
# borders (at most GAP radians apart round the ellipse).
BEAM_HALF = 12.0
DEPTH = 0.36
STRIPES = ((-6.0, 0x94), (-5.15, 0x9c), (-4.25, 0x8c), (-2.2, 0x8e), (0.6, 0x0f))
GAP = math.radians(9.0)
# The bottom end's rounding: its length (times the beam's half-width) and its rings (fractions of the way to its tip).
CAP = 0.25
CAP_RINGS = (0.35, 0.65, 0.88)
# The crackle: the filament's half-width and how far its top stands out of the rod, its points across, how much wider
# its swing is than the sprite's (about its middle, CRACKLE_X), the ends' x; the forks' half-width and length (towards
# the paler pixels), the sparks' size and lift.
FILAMENT_HALF, FILAMENT_LIFT, FILAMENT_POINTS = 0.42, 0.32, 5
SWING, CRACKLE_X = 1.5, -3.0
FORK_HALF, FORK_LIFT = 0.24, 0.22
SPARK_SIZE, SPARK_LIFT = 0.42, 0.35
# Emission by palette index; roughness.
GLOW = {0x94: 0.26, 0x9c: 0.34, 0x8c: 0.3, 0x8e: 0.3, 0x0f: 0.32, 0x9f: 0.5}
ROUGHNESS, FILAMENT_ROUGHNESS = 0.35, 0.3
CRACKLE, PALE, DOT = 0x9f, (0x8c, 0x8d, 0x1f), 0x8e


def surface(x):
    """The rod's top at x (the half from the outer edge, x -6, to the beam's middle line, x 6)."""
    u = min(max((6.0 - x) / BEAM_HALF, 0.0), 1.0)
    return DEPTH * BEAM_HALF * math.sqrt(max(0.0, 1.0 - u * u))


def section_xs():
    """The section's points from the outer edge to the middle line: the stripes' borders and points between them no
    further apart than GAP round the ellipse."""
    borders = [x for x, _ in STRIPES] + [6.0]
    out = [borders[0]]
    for a, b in zip(borders, borders[1:]):
        ta, tb = math.acos(min((6.0 - a) / BEAM_HALF, 1.0)), math.acos(min((6.0 - b) / BEAM_HALF, 1.0))
        extra = int(abs(tb - ta) / GAP)
        out += [6.0 - BEAM_HALF * math.cos(ta + (tb - ta) * (i + 1) / (extra + 1)) for i in range(extra)]
        out.append(b)
    return out


def stripe_of(x):
    return max(i for i, (start, _) in enumerate(STRIPES) if x >= start - 1e-9)


def mesh(name, verts, faces, mats, materials):
    """A mesh of these faces (a face with a repeated corner loses it; one with fewer than 3 corners goes), each taking
    materials[mats[i]] (one slot per material)."""
    clean_faces, clean_mats = [], []
    for f, m in zip(faces, mats):
        pts = []
        for v in f:
            if v not in pts:
                pts.append(v)
        if len(pts) >= 3 and len({verts[v] for v in pts}) >= 3:
            clean_faces.append(tuple(pts))
            clean_mats.append(m)
    obj = k.mesh_object(name, verts, clean_faces)
    slots = []
    for m in materials:
        if m not in slots:
            slots.append(m)
            obj.data.materials.append(m)
    for poly, m in zip(obj.data.polygons, clean_mats):
        poly.material_index = slots.index(materials[m])
    return obj


def rod(name, materials):
    """The half rod: its top in stripes from end to end, both ends rounded (a quarter dome shrinking towards the middle
    line's foot, inside the next segment where they join: the right half is the left turned half round, so its ends
    swap), the wall at the middle line and the flat underside; each ring of the section is its top's points (outer
    edge to middle line) and the middle line's foot. Wound outwards as built: the tops up, the wall to +x, the
    underside down. Three objects (the length and its two ends), so that the ends' rounding doesn't bend the length's
    normals (a shading line at every joint)."""
    xs = section_xs()
    n = len(xs)
    wall, under = stripe_of(5.99), 0
    cap_len = CAP * BEAM_HALF

    def ring(verts, y, shrink):
        start = len(verts)
        for x in xs:
            verts.append((round(6.0 + (x - 6.0) * shrink, 6), round(y, 6), round(surface(x) * shrink, 6)))
        verts.append((6.0, round(y, 6), 0.0))  # (the middle line's foot)
        return start

    def strip(verts, rings, tips):
        """Faces between the rings (top to bottom) and fans to the tips (None: open)."""
        faces, mats = [], []
        for r in range(len(rings) - 1):
            a, b = rings[r], rings[r + 1]
            for j in range(n - 1):
                faces.append((a + j, b + j, b + j + 1, a + j + 1))
                mats.append(stripe_of((xs[j] + xs[j + 1]) / 2))
            faces.append((a + n - 1, b + n - 1, b + n, a + n))
            mats.append(wall)
            faces.append((a + n, b + n, b, a))
            mats.append(under)
        top_tip, bottom_tip = tips
        for tip, rg, above in ((top_tip, rings[0], True), (bottom_tip, rings[-1], False)):
            if tip is None:
                continue
            for j in range(n - 1):
                faces.append((tip, rg + j, rg + j + 1) if above else (rg + j, tip, rg + j + 1))
                mats.append(stripe_of((xs[j] + xs[j + 1]) / 2))
            faces += [(tip, rg + n - 1, rg + n), (tip, rg + n, rg)] if above else \
                [(rg + n - 1, tip, rg + n), (rg + n, tip, rg)]
            mats += [wall, under]
        return faces, mats
    parts = []
    verts = []
    rings = [ring(verts, HALF, 1.0), ring(verts, -HALF, 1.0)]
    faces, mats = strip(verts, rings, (None, None))
    parts.append(k.smooth(mesh(name, verts, faces, mats, materials), 30))
    for end, sign in (("top", 1.0), ("bottom", -1.0)):
        verts = []
        fs = list(CAP_RINGS) if sign < 0 else list(reversed(CAP_RINGS))
        rings = [ring(verts, sign * (HALF + f * cap_len), math.sqrt(max(0.0, 1.0 - f * f))) for f in fs]
        rings = [ring(verts, sign * HALF, 1.0)] + rings if sign < 0 else rings + [ring(verts, sign * HALF, 1.0)]
        tip = len(verts)
        verts.append((6.0, round(sign * (HALF + cap_len), 6), 0.0))
        faces, mats = strip(verts, rings, (tip, None) if sign > 0 else (None, tip))
        parts.append(k.smooth(mesh(f"{name}_{end}", verts, faces, mats, materials), 30))
    return parts


def crackle_path(rows):
    """The crackle's middle line down the segment: each row's light-blue stroke's middle (its swing about CRACKLE_X
    widened by SWING), rows without one left out, the ends at CRACKLE_X (so that they meet the next segment's)."""
    path = [(CRACKLE_X, HALF)]
    for r, row in enumerate(rows):
        cols = [c for c, v in enumerate(row) if v == CRACKLE]
        if cols:
            x = (min(cols) + max(cols) + 1) / 2 - 6.0
            path.append((CRACKLE_X + SWING * (x - CRACKLE_X), 6.5 - r))
    path.append((CRACKLE_X, -HALF))
    return path


def ribbon(points, half_widths, lift, sink=0.05, across=FILAMENT_POINTS):
    """A half-tube lying on the rod along points (x, y): at each a section across the line (half-width half_widths[i],
    its top lift[i] over the rod, its edges sunk a little into it). Returns (verts, faces), faces wound upwards."""
    verts, faces = [], []
    count = len(points)
    for i, (x, y) in enumerate(points):
        ax, ay = points[max(i - 1, 0)]
        bx, by = points[min(i + 1, count - 1)]
        dx, dy = bx - ax, by - ay
        length = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / length, dx / length
        for j in range(across):
            a = math.pi * j / (across - 1)
            off = half_widths[i] * math.cos(a)
            px, py = x + nx * off, y + ny * off
            z = surface(px) - sink + (lift[i] + sink) * math.sin(a)
            verts.append((px, py, z))
    for i in range(count - 1):
        for j in range(across - 1):
            a, b = i * across + j, (i + 1) * across + j
            faces.append((a, b, b + 1, a + 1))
    return verts, faces


def upwards(verts, faces):
    """Each face turned so that its normal points up (a strip lying on the rod)."""
    out = []
    for f in faces:
        p = [Vector(verts[v]) for v in f]
        normal = (p[1] - p[0]).cross(p[2] - p[0])
        out.append(tuple(reversed(f)) if normal.z < 0 else f)
    return out


def crackle(name, rows, materials):
    """The crackle on the rod: the filament along the stroke, a fork from it towards each paler pixel beside it, a spark
    at each dot; all light blue."""
    verts, faces = [], []

    def add(vs, fs):
        base = len(verts)
        verts.extend(vs)
        faces.extend(tuple(base + v for v in f) for f in fs)
    path = crackle_path(rows)
    # (the filament's ends a little thinner and lower, running into the next segment's)
    widths = [FILAMENT_HALF * (0.75 if i in (0, len(path) - 1) else 1.0) for i in range(len(path))]
    lifts = [FILAMENT_LIFT * (0.75 if i in (0, len(path) - 1) else 1.0) for i in range(len(path))]
    add(*ribbon(path, widths, lifts))

    def path_x(y):
        for (x0, y0), (x1, y1) in zip(path, path[1:]):
            if y1 <= y <= y0:
                f = (y0 - y) / (y0 - y1) if y0 != y1 else 0.0
                return x0 + (x1 - x0) * f
        return CRACKLE_X
    for r, row in enumerate(rows):
        y = 6.5 - r
        for c, v in enumerate(row):
            x = c + 0.5 - 6.0
            if v in PALE:
                # (a fork: from the stroke towards the pixel, tapering to a point, a little up the beam)
                start = (path_x(y), y)
                end = (x + (0.35 if x > start[0] else -0.35), y + 0.6)
                mid = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2 + 0.1)
                add(*ribbon([start, mid, end], [FORK_HALF, FORK_HALF * 0.7, 0.02], [FORK_LIFT, FORK_LIFT * 0.8, 0.0],
                            across=3))
            elif v == DOT:
                # (a spark: a little four-sided pyramid standing on the rod)
                base = surface(x) - 0.05
                pts = [(x + SPARK_SIZE, y, base), (x, y + SPARK_SIZE, base), (x - SPARK_SIZE, y, base),
                       (x, y - SPARK_SIZE, base), (x, y, surface(x) + SPARK_LIFT)]
                add(pts, [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)])
    faces = upwards(verts, faces)
    obj = mesh(name, verts, faces, [0] * len(faces), materials)
    return k.smooth(obj, 50)


def material(index, roughness=ROUGHNESS):
    return lit(f"sdf_{index:02x}", index, GLOW[index], roughness=roughness)


def build_model(name, sprite):
    rows = grid(SPRITES[sprite])
    parts = rod(name + "_rod", [material(i) for _, i in STRIPES])
    parts.append(crackle(name + "_crackle", rows, [material(CRACKLE, FILAMENT_ROUGHNESS)]))
    return triangulate(parts)


# name: (the sprite it is authored as, what it is)
MODELS = [
    ("shot_sdf", 58, "the beam's left half, its first crackle (58, 60; turned half round: 61, 63)"),
    ("shot_sdf_59", 59, "the beam's left half, its second crackle (59; turned half round: 62)"),
]

# The shot lines: (sprite, model, yaw, glow (size, strength, palette index, dx, dy), comment).
EDGE_GLOW = (14, 0.08, 0x9c)
SHOTS = [
    (58, "shot_sdf", 0, (*EDGE_GLOW, -3, 0), "the beam's left half (white, its blue edge to the left)"),
    (59, "shot_sdf_59", 0, (*EDGE_GLOW, -3, 0), "... its crackle the next tick"),
    (60, "shot_sdf", 0, (*EDGE_GLOW, -3, 0), "... (the same as 58)"),
    (61, "shot_sdf", 180, (*EDGE_GLOW, 3, 0), "the right half: the left turned half round"),
    (62, "shot_sdf_59", 180, (*EDGE_GLOW, 3, 0), "... its crackle the next tick"),
    (63, "shot_sdf", 180, (*EDGE_GLOW, 3, 0), "... (the same as 61)"),
]


def facing(parts):
    """(faces facing up, facing down, others) over all the parts."""
    up = down = side = 0
    for p in parts:
        for poly in p.data.polygons:
            z = poly.normal.z
            if z > 0.2:
                up += 1
            elif z < -0.2:
                down += 1
            else:
                side += 1
    return up, down, side


def cfg_lines(only=None):
    names = [m[0] for m in MODELS if only is None or m[0] in only]
    width = max(len(n) for n in names)
    lines = [f"model {n.ljust(width)} shots/{n}.glb" for n in names]
    rows = []
    for sprite, name, yaw, glow, comment in SHOTS:
        if name not in names:
            continue
        size, strength, colour, gx, gy = glow
        rows.append([f"shot shots2 {sprite} {name.ljust(width)}", f"yaw={yaw:g}" if yaw else "", "beam",
                     f"glow={size:g}:{strength:g}:{colour}:{gx:g}:{gy:g}", comment])
    widths = [max(len(r[i]) for r in rows) for i in range(4)]
    return lines + [" ".join([r[0]] + [r[i].ljust(widths[i]) for i in range(1, 4) if widths[i]]) + " # " + r[4]
                    for r in rows]


# --- Previews ---------------------------------------------------------------------------------------------------------

def game_view(prefix, objects):
    mk.preview(prefix, objects, size=(12, 14), scale=32, distance=0.42)
    scene = bpy.context.scene
    cam, sun = game_camera(scene, 16.0, (512, 512))
    scene.render.filepath = prefix + "_game.png"
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam)
    bpy.data.objects.remove(sun)


def beam_view(prefix):
    """Two beams of six segments joined end to end, as the game draws them on two ticks (the left halves 6 pixels left
    of the middle, the right halves turned half round 6 pixels right; each centred in height on its bounds): 58's
    crackle, and beside it 59's."""
    k.reset()
    scene = bpy.context.scene
    scene.view_settings.view_transform = "Standard"
    for bx, name in ((-16.0, "shot_sdf"), (16.0, "shot_sdf_59")):
        for n in range(6):
            for side, yaw in ((-6.0, 0.0), (6.0, 180.0)):
                parts = build_model(f"{name}_{n}_{int(side)}", 58 if name == "shot_sdf" else 59)
                zs = [(p.matrix_world @ v.co).z for p in parts for v in p.data.vertices]
                mk.transform(parts, Matrix.Translation((bx + side, (n - 2.5) * 2 * HALF, -(max(zs) + min(zs)) / 2))
                             @ turn(yaw))
    bpy.context.view_layer.update()
    cam, sun = game_camera(scene, 96.0, (900, 1000))
    scene.render.filepath = prefix + "beam_game.png"
    bpy.ops.render.render(write_still=True)


def build():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    outdir = options.get("outdir", OUTDIR)
    for name, sprite, what in MODELS:
        if only is not None and name not in only:
            continue
        k.reset()
        parts = build_model(name, sprite)
        bpy.context.view_layer.update()
        zs = [(p.matrix_world @ v.co).z for p in parts for v in p.data.vertices]
        print(f"== {name} (shots2 {sprite}): {what}; height bounds {min(zs):.3f}..{max(zs):.3f}; "
              f"faces up/down/sideways {facing(parts)}")
        if "check" in options:
            for s, model, yaw, _, _ in SHOTS:
                if model == name:
                    check_frames(parts, os.path.join(options["check"], "shots2.png"), [(s, turn(yaw), f"shots2 {s}")],
                                 move_to_frame=False)
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, parts, os.path.join(outdir, name + ".glb"))
        if "preview" in options:
            game_view(options["preview"] + name, parts)
    if "preview" in options and only is None:
        beam_view(options["preview"])
    print("models.cfg:")
    for line in cfg_lines(only):
        print("  " + line)


if __name__ == "__main__":
    build()
