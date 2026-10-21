"""The big dark glass orb of FLEET, STARGATE and MISTAKES (sheet E sprites 191, 193 above 229, 231, 2x2 each: one
48 x 56 picture; enemies 682-685 of episodes 2 and 3, one frame each), polished (2026-10-21; it replaces wave3_aa.py's
orb, an ellipsoid painted pixel by pixel from the sprite with lenses for eyes). models.cfg: model dark_orb_tl / _tr /
_bl / _br enemies/dark_orb_*.glb origin (unchanged); sprite e 191 dark_orb_tl yaw=0 height=-4 and the same for 193,
229, 231 (see below). No other enemy shows these sprites; none is another sprite's pixels mirrored, turned or in other
ramps (the small orbs E 195 and E 233 are other drawings).

The levels lay the four as a square (STARGATE's sky events at 700-990 and ground ones at 4510, MISTAKES' ground ones
at 4710, FLEET's top ones at 200 and 400): 682 (191) at (x, y), 683 (193) 24 pixels to its right, 684 (229) and 685
(231) 28 pixels below them; each group on one layer, moving together.

As the sprites and their 4x upscales draw it (columns and rows of the 48 x 56 picture): a glass ball (columns 7-40 of
rows 12-42, its middle at column 23.5, row 27: 34 x 31 pixels) of black glass over a red shell. The black covers its
upper left two thirds (CAP: from row 13 to row 33, columns 10-33 at its widest), the red showing round it in a rim
that is thin along the top and the left (one to three pixels) and broad on the right and at the bottom (nine or ten),
dark red (0x70, 0x71) on the right, red to orange (0x73-0x79) along the left and the top left, where a bright line
runs just inside the edge, and glowing hotter and hotter along the bottom towards the lower right, where it burns
white (0x7f at columns 31-33 of rows 39-40): the glow of a glass ball lit from the upper left. A seam of 0x40 (as
dark as the black) parts the black from the red. In the black, four lights: the big eye in the upper left (columns 13-23 of rows 17-26),
white-hot (0x7f) through yellow and orange into dark red; the small eye below the middle (columns 23-29 of rows
26-30), white-hot in its middle; an ember to the upper right of the big eye (columns 26-30 of rows 18-23, 0x78 at its
middle) and a dimmer one above, between them (columns 22-26 of rows 15-18, 0x75).

Built as a ball of glass: an ellipsoid (17 x 15.5 pixels as the sprite draws it, 13 high) of even triangles (an
icosphere, finer where the camera sees it and round the lights), standing on the ground (z = 0), painted in bands of
heat cut along smooth contours (polish_orb_red.band_split): the black cap raised a little over the red shell, the
lights soft lenses in it, each a radial profile of heat; the shell's heat by the angle round the ball and the distance
from its middle, as the sprite's rim, with faint patches. The painting is laid out as the sprite draws it seen from
VIEW_TILT degrees off straight down, from the bottom of the screen (the game's camera is 20 degrees off): the slanted
camera sees the ball's face, high on it, where the sprite draws it (seen from straight above it lies a little lower
on the ball, as polish_orb_eyes.py moves its face). The red glows in its own colours (lighter ones for the darkest
reds, so that the shell reads red, not black, from the slanted camera; emission 0.2-0.6: the game's bloom adds), the
black glass is glossy. The whole ball is then cut along the sprites' edges (x = 0, y = 0; polish_arch.py's cut(): the
pieces keep the whole's shading across the cuts; the cuts are closed with the shell's glowing red, which shows only
when a piece is shot away), each piece moved so that its sprite's centre is its origin.

Where it stands: models drawn at their origin stand at their layer's height, on the ground 4 pixels above the
terrain; height=-4 on the four sprite lines sets the ball on the ground (MISTAKES, STARGATE) and lowers it 4 pixels in
the sky and on top (STARGATE, FLEET), where it floats anyway.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground (z = 0); the whole's
origin is the middle of the picture (the corner where the four sprites meet): column c is x = c + 0.5 - 24, row r is
y = 27.5 - r. The pieces' centres: 191 (-12, 14), 193 (12, 14), 229 (-12, -14), 231 (12, -14).

Replaces wave3_aa.py's orb: remove its section ("# --- E 191 193 / 229 231: the big dark orb": ORB, ORB_CENTRE,
ORB_RADII, orb_whole() and the kit.pieced("dark_orb", ...) registration) and the dark_orb paragraph of its docstring;
and wave3_aa_art.py's ORB (only that section reads it).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the
whole and of each piece against enemy_E.png), --preview <prefix> (the whole's top and 3/4 views; --pieces 1 also each
piece's), --only <name,...> (pieces to export), --whole <file.glb> (the uncut ball as well, for looking at).
"""
import math
import os
import sys

import bmesh
import bpy
import mathutils.noise as noise
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_orb_red import band_split, smoothstep  # noqa: E402
from polish_arch import cut  # noqa: E402  (polish_machine_kit.cut without its material indices shifted twice)
from polish_k_pod import triangulate  # noqa: E402

PIECES = [("dark_orb_tl", 191, (-24.0, 0.0, 0.0, 28.0)), ("dark_orb_tr", 193, (0.0, 24.0, 0.0, 28.0)),
          ("dark_orb_bl", 229, (-24.0, 0.0, -28.0, 0.0)), ("dark_orb_br", 231, (0.0, 24.0, -28.0, 0.0))]
SPRITE_CELLS = {191: (0, 0), 193: (24, 0), 229: (0, 28), 231: (24, 28)}

# The ball: its middle (as the sprite draws it: columns 7-40, rows 12-42) and radii; it stands on the ground.
RX, RY, RZ = 17.0, 15.5, 13.0
CENTRE = Vector((0.0, 0.5, RZ))
# The painting is laid out as the sprite draws it seen from this many degrees off straight down (from the bottom of
# the screen; the game's camera: 20).
VIEW_TILT = 20.0

# The black cap: how far out from the ball's middle its edge lies (a fraction of the radius) at angles round it
# (degrees counter-clockwise from the right, as the sprite draws it); how wide its edge blends into the red (the
# sprite's seam of 0x40, as dark as the black) and how much the black stands over the red.
CAP = [(0, 0.46), (10, 0.53), (20, 0.6), (30, 0.74), (40, 0.84), (50, 0.905), (60, 0.925), (70, 0.93), (80, 0.935),
       (90, 0.93), (100, 0.895), (110, 0.87), (120, 0.87), (130, 0.865), (140, 0.85), (150, 0.84), (160, 0.84),
       (170, 0.835), (180, 0.82), (190, 0.79), (200, 0.725), (210, 0.66), (220, 0.575), (230, 0.535), (240, 0.485),
       (250, 0.445), (260, 0.405), (270, 0.36), (280, 0.355), (290, 0.37), (300, 0.39), (310, 0.39), (320, 0.42),
       (330, 0.44), (340, 0.445), (350, 0.46)]
SEAM = 0.035
CAP_RAISE = 0.32

# The red shell round it: at angles round the ball, where its heat starts to rise from the dark red at the cap's edge
# (a fraction of the radius), where it peaks, the peak and the heat at the edge (heat: the shade of ramp 7, 0 = 0x70,
# 15 = 0x7f).
RIM = [(0, 0.72, 0.95, 6.0, 6.0), (15, 0.8, 0.93, 1.6, 1.2), (30, 0.88, 0.95, 0.9, 0.8), (45, 0.9, 0.95, 0.4, 0.4),
       (60, 0.9, 0.95, 0.3, 0.3), (75, 0.9, 0.95, 0.5, 0.4), (90, 0.88, 0.95, 1.8, 1.2), (105, 0.87, 0.93, 3.8, 2.6),
       (120, 0.865, 0.925, 5.4, 3.4), (135, 0.85, 0.915, 8.2, 3.6), (150, 0.84, 0.905, 8.4, 3.0),
       (165, 0.82, 0.89, 6.4, 3.6), (180, 0.8, 0.9, 5.4, 3.2), (195, 0.76, 0.87, 5.0, 2.6), (210, 0.72, 0.86, 5.0, 4.4),
       (225, 0.67, 0.87, 5.0, 4.8), (240, 0.62, 0.83, 5.2, 4.4), (255, 0.6, 0.84, 6.0, 5.0), (270, 0.6, 0.88, 7.8, 6.6),
       (285, 0.63, 0.9, 10.6, 7.0), (300, 0.65, 0.92, 14.6, 10.0), (315, 0.66, 0.89, 13.2, 8.0),
       (330, 0.68, 0.89, 11.6, 6.5), (345, 0.71, 0.93, 8.6, 6.4)]
PATCHES = 0.45      # the shell's faint patches (heat)
BACK = 1.0          # the shell's heat on the side the camera doesn't see

# The lights in the black, as the sprite draws them: (x, y, horizontal stretch, heat by distance (pixels) from the
# middle, how much the lens bulges out of the glass and its radius).
LIGHTS = [
    # The big eye (columns 13-23 of rows 17-26): white-hot, yellow, orange, red, into the seam's dark.
    (-5.5, 6.0, 1.1, [(0.0, 15.0), (2.7, 15.0), (3.3, 13.0), (3.8, 10.0), (4.3, 6.5), (4.8, 3.4), (5.3, 1.2),
                      (5.8, -0.6), (6.3, -2.0)], 0.5, 6.0),
    # The small eye (columns 23-29 of rows 26-30): white-hot in its middle.
    (2.1, -0.4, 1.05, [(0.0, 15.0), (0.7, 14.6), (1.2, 12.0), (1.7, 8.6), (2.2, 5.2), (2.7, 2.2), (3.2, 0.2),
                       (3.6, -1.0), (4.0, -2.0)], 0.3, 3.8),
    # The ember to the upper right (columns 26-30 of rows 18-23, 0x78 in its middle).
    (4.5, 7.2, 1.05, [(0.0, 8.2), (0.5, 7.6), (1.1, 5.4), (1.7, 3.2), (2.2, 1.4), (2.7, 0.0), (3.1, -1.2),
                      (3.4, -2.0)], 0.26, 3.2),
    # The dim ember above (columns 22-26 of rows 15-18, 0x75).
    (0.7, 10.9, 1.05, [(0.0, 5.2), (0.6, 4.4), (1.1, 3.0), (1.6, 1.4), (2.1, 0.0), (2.5, -1.2), (2.9, -2.0)],
     0.2, 2.8),
]

# The bands of heat: (lowest heat, palette index, emission strength, the emission's palette index). Fifteen
# materials at most: the seam's 0x40 (all but black) is left out, and so is 0x76, so that the hot reds and yellows
# keep every shade (their steps show most).
BANDS = [
    (-9.0, 0x01, 0.0, None),
    (-1.0, 0x70, 0.22, 0x72),
    (0.5, 0x71, 0.22, 0x73),
    (1.5, 0x72, 0.28, 0x72),
    (2.5, 0x73, 0.3, 0x73),
    (3.5, 0x74, 0.32, 0x74),
    (4.5, 0x75, 0.35, 0x75),
    (6.0, 0x77, 0.4, 0x77),
    (7.5, 0x78, 0.42, 0x78),
    (8.5, 0x79, 0.45, 0x79),
    (9.5, 0x7a, 0.48, 0x7a),
    (10.6, 0x7b, 0.5, 0x7b),
    (12.0, 0x7d, 0.55, 0x7d),
    (13.6, 0x7e, 0.58, 0x7e),
    (14.6, 0x7f, 0.6, 0x7f),
]
CUT_BAND = 0x72     # the cuts are closed with the shell's glowing red


def periodic(points, angle):
    """Catmull-Rom through (angle, value) points round a circle (degrees)."""
    angle %= 360.0
    n = len(points)
    for i in range(n):
        a0, v0 = points[i]
        a1, v1 = points[(i + 1) % n]
        span = (a1 - a0) % 360.0
        if (angle - a0) % 360.0 <= span:
            t = ((angle - a0) % 360.0) / span
            vp, vn = points[i - 1][1], points[(i + 2) % n][1]
            return 0.5 * (2 * v0 + (-vp + v1) * t + (2 * vp - 5 * v0 + 4 * v1 - vn) * t * t +
                          (-vp + 3 * v0 - 3 * v1 + vn) * t ** 3)
    return points[0][1]


def rim_at(angle):
    """The shell's (start, peak's distance, peak, edge) at an angle round the ball."""
    return [periodic([(r[0], r[i]) for r in RIM], angle) for i in range(1, 5)]


def radial(profile, r):
    """Linear through (distance, value) points."""
    for (r0, v0), (r1, v1) in zip(profile, profile[1:]):
        if r <= r1:
            return v0 + (v1 - v0) * max(0.0, r - r0) / (r1 - r0)
    return profile[-1][1]


T = math.radians(VIEW_TILT)
TOWARDS_VIEW = Vector((0.0, -math.sin(T), math.cos(T)))
VIEW_H = math.hypot(RY * math.cos(T), RZ * math.sin(T))   # the ball's half-height seen from the view


def view(p):
    """Where the point p of the ball's surface shows in the view the painting is laid out in, in the sprite's
    coordinates (its disc: 17 x 15.5 round (0, 0.5)), the angle round the middle (degrees), the distance out (a
    fraction of the radius; on the side the view doesn't see, 2 less it) and whether the view sees it."""
    rel = p - CENTRE
    u = rel.x / RX
    v = (rel.y * math.cos(T) + rel.z * math.sin(T)) / VIEW_H
    normal = Vector((rel.x / RX ** 2, rel.y / RY ** 2, rel.z / RZ ** 2))
    seen = normal.dot(TOWARDS_VIEW) > 0.0
    rho = math.hypot(u, v)
    angle = math.degrees(math.atan2(v, u)) % 360.0
    sprite = Vector((CENTRE.x + u * 17.0, CENTRE.y + v * 15.5))
    return sprite, angle, (rho if seen else 2.0 - rho), seen


def direction(p):
    rel = p - CENTRE
    return Vector((rel.x / RX, rel.y / RY, rel.z / RZ)).normalized()


def outward(p):
    """The ellipsoid's normal at p."""
    rel = p - CENTRE
    return Vector((rel.x / RX ** 2, rel.y / RY ** 2, rel.z / RZ ** 2)).normalized()


def shell_heat(angle, rho, d):
    start, peak_at, peak, edge = rim_at(angle)
    if rho <= peak_at:
        heat = peak * smoothstep(start, peak_at, rho) ** 1.5
    elif rho <= 1.0:
        heat = peak + (edge - peak) * smoothstep(peak_at, 1.0, rho)
    else:   # the side the view doesn't see: the edge's heat fading to the shell's dark red
        heat = edge + (BACK - edge) * smoothstep(1.0, 1.12, rho)
    # Faint patches in the dark red (the hot glow stays smooth).
    patches = noise.noise(d * 2.3 + Vector((1.0, 5.0, 2.0))) + 0.5 * noise.noise(d * 5.1 + Vector((3.0, 1.0, 7.0)))
    return heat + PATCHES * patches * (1.0 - 0.8 * smoothstep(1.5, 5.0, heat))


def heat_and_lift(p):
    """The heat at the ball's surface point p (-2: the black glass, 0-15: ramp 7) and how far the surface there
    stands out of the ellipsoid."""
    d = direction(p)
    sprite, angle, rho, seen = view(p)
    heat = shell_heat(angle, rho, d)
    lift = 0.08 * noise.noise(d * 3.0 + Vector((4.0, 2.0, 7.0)))
    if not seen:
        return heat, lift
    inside = periodic(CAP, angle) - rho            # > 0 inside the cap
    # The black glass, raised over the red.
    black = smoothstep(-SEAM, SEAM, inside)
    heat = heat * (1.0 - black) + (-2.0) * black
    lift += CAP_RAISE * smoothstep(-0.02, 0.03, inside)
    # The lights, soft lenses in the black.
    if inside > -0.05:
        for x, y, stretch, profile, bulge, radius in LIGHTS:
            r = math.hypot((sprite.x - x) / stretch, sprite.y - y)
            if r < radius + 1.0:
                heat = max(heat, radial(profile, r))
                lift += bulge * max(0.0, 1.0 - (r / radius) ** 2) ** 2
    return heat, lift


def ball_mesh(name):
    """An ellipsoid of even triangles (an icosphere), finer where the camera sees it and finer still round the
    lights and the hot rim."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=4, radius=1.0)

    def point(v):
        d = v.co.normalized()
        return CENTRE + Vector((d.x * RX, d.y * RY, d.z * RZ))

    def seen(v):
        return outward(point(v)).dot(TOWARDS_VIEW) > -0.2

    def detailed(v):
        p = point(v)
        sprite, angle, rho, vis = view(p)
        if not vis:
            return False
        near_light = any(math.hypot(sprite.x - x, sprite.y - y) < r + 1.0 for x, y, _, _, _, r in LIGHTS)
        return near_light or (rho > 0.6 and (angle > 230 or angle < 10 or 100 < angle < 200))

    for keep in (seen, detailed):
        edges = [e for e in bm.edges if all(keep(v) for v in e.verts)]
        bmesh.ops.subdivide_edges(bm, edges=edges, cuts=1, use_grid_fill=True)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        for v in bm.verts:
            v.co.normalize()
    for v in bm.verts:
        v.co = point(v)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def materials():
    glow = k.level_palette()
    mats = {}
    for _, index, strength, emit in BANDS:
        black = index < 0x70
        mats[index] = k.material(f"darkorb_{index:02x}", palette=index, metallic=0.05 if black else 0.0,
                                 roughness=0.12 if black else 0.22 if strength < 0.45 else 0.3,
                                 emission=glow[emit] if emit is not None else None, emission_strength=strength)
    return mats


def build_whole():
    mats = materials()
    orb = ball_mesh("dark_orb")
    values = []
    for v in orb.data.vertices:
        p = v.co.copy()
        heat, lift = heat_and_lift(p)
        values.append(heat)
        v.co = p + outward(p) * lift
    band_split(orb, values, [(lowest, mats[index]) for lowest, index, _, _ in BANDS])
    k.smooth(orb, 70)
    return [orb], mats


def object_mask(sheet):
    mask = [[False] * 48 for _ in range(56)]
    for sprite, (c0, r0) in SPRITE_CELLS.items():
        for r, row in enumerate(k.sprite_mask(sheet, sprite)):
            for c, v in enumerate(row):
                mask[r0 + r][c0 + c] = v
    return mask


def build():
    k.reset()
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    whole, mats = build_whole()
    triangulate(whole)  # the cuts are the same every run (with and without --check)
    low, high = mk.bounds(whole)
    print("== whole orb: %d triangles, %d materials, x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (
        mk.triangles(whole), len(mk.materials_of(whole)), low.x, high.x, low.y, high.y, low.z, high.z))
    mask = None
    if "check" in options:
        sheets = options["check"]
        sheet = os.path.join(sheets, "enemy_E.png") if os.path.isdir(sheets) else sheets
        mask = object_mask(sheet)
        mk.compare("whole (E 191 193 above 229 231)", mk.coverage(whole, 48, 56), mask)
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    if "preview" in options:
        mk.preview(options["preview"] + "dark_orb_whole", whole, size=(48, 56), scale=10, distance=1.6)
    if "whole" in options:
        mk.export(whole, options["whole"])
    for name, sprite, box in PIECES:
        if only and name not in only:
            continue
        pieces = [p for p in (cut(src, box, mats[CUT_BAND]) for src in whole) if p is not None]
        mk.transform(pieces, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
        triangulate(pieces)
        bpy.context.view_layer.update()
        for src in whole:
            src.hide_render = True
        if mask is not None:
            c0, r0 = SPRITE_CELLS[sprite]
            mk.compare("%s (E %d)" % (name, sprite), mk.coverage(pieces, 24, 28),
                       [row[c0:c0 + 24] for row in mask[r0:r0 + 28]])
        mk.report(name, pieces, os.path.join(out, name + ".glb"))
        if "preview" in options and options.get("pieces") == "1":
            mk.preview(options["preview"] + name, pieces)
        for obj in pieces:
            bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False


if __name__ == "__main__":
    build()
