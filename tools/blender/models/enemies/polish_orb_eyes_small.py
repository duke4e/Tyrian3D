"""The small dark red orb with an eye that the black orb with two glowing eyes (E 195, orb_eyes) launches in ASTEROIDS,
BONUS, BUBBLES, FLEET, MISTAKES and STARGATE (sheet E sprite 235, 2x2: a 16 x 15 orb in the 24 x 28 cell; enemy 479 of
episodes 1, 3 and 5, still and homing in on the player (accel 94, 94), and 687 of episodes 2 and 3, rising 2 pixels a
tick and homing across, which E 195's enemy 686 launches every 2 ticks: a stream of them; armour 1; launched on the
launcher's layer: sky, ground 2 or top), polished (2026-10-21; it had no model: the game drew a pixelated stand-in).
models.cfg: model orb_eyes_small enemies/orb_eyes_small.glb; sprite e 235 orb_eyes_small yaw=0 (no glow: the streams
overlap them). One frame, not animated; no other enemy shows it, and it is no other sprite's pixels mirrored, turned
or in other ramps.

As the sprite draws it (the 4x upscales have no picture of it): the big dark glass orb of the same levels (E 191 193
above 229 231, polish_dark_orb.py) made small and in the palette's ramp 4, a dark brick red: black glass (the sprite
leaves it transparent: the space behind shows) over a red shell that shows round it as a rim, a pixel of dark red
(shade 3) along the top and the left, broad along the bottom (shades 1-7) and dark red on the right (shades 0-1),
where a bright crescent lies inside the rim at the lower right (rows 16-20, columns 14-18, shade 13: the glow of a
glass ball lit from the upper left); in the black, as in the big orb, a big eye at the upper left (columns 7-10 of
rows 10-13, white-pink in its middle, 0x4f, through pink into dark red), a small light below the middle (column 12 of
rows 14-15, shade 13) and a dim ember to the upper right of the eye (column 13 of row 11, shade 8).

Built as polish_dark_orb.py builds the big orb (its periodic() and radial() imported): an ellipsoid (8 x 7.5 pixels
as the sprite draws it, 7 high) of even triangles (an icosphere, finer where the camera sees it and round the
lights), standing on the ground (z = 0), painted in bands of shade cut along smooth contours (polish_orb_red's
band_split): the black glass cap raised a little over the red shell, its edge by the angle round the ball (CAP); the
shell's shade by the angle and the distance out (RIM, the crescent), with faint patches; the lights soft lenses in
the black, each a radial profile of shade. The painting is laid out as the sprite draws it seen from VIEW_TILT
degrees off straight down, from the bottom of the screen (the game's camera is 20 degrees off), so that the face
sits where the sprite draws it in the game's view. The reds glow in their own colours (the darkest in lighter ones,
so that the shell reads red, not black, from the slanted camera; 0.2-0.6: the game's bloom adds), the black glass is
glossy.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground; origin at the
sprite's centre (pixel 12, 14: column c is x = c + 0.5 - 12, row r is y = 13.5 - r). The game centres the model in
height (and on the ground lifts it so that it rests on it).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against
enemy_E.png), --preview <prefix>.
"""
import math
import os
import sys

import bmesh
import bpy
import mathutils.noise as noise
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_orb_red import band_split, smoothstep  # noqa: E402
from polish_dark_orb import periodic, radial  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402

NAME = "orb_eyes_small"
SPRITE = 235

# The ball: its middle (as the sprite draws it: columns 4-19, rows 7-21) and radii; it stands on the ground.
RX, RY, RZ = 8.0, 7.5, 7.0
CENTRE = Vector((0.0, -0.5, RZ))
VIEW_TILT = 20.0
T = math.radians(VIEW_TILT)
TOWARDS_VIEW = Vector((0.0, -math.sin(T), math.cos(T)))
VIEW_H = math.hypot(RY * math.cos(T), RZ * math.sin(T))

# The black glass cap: how far out from the ball's middle its edge lies (a fraction of the radius) at angles round
# it (degrees counter-clockwise from the right, as the sprite draws it), how wide its edge blends into the red and how
# much the black stands over the red.
CAP = [(0, 0.52), (30, 0.6), (60, 0.8), (90, 0.88), (120, 0.88), (150, 0.88), (180, 0.87), (210, 0.76),
       (235, 0.6), (260, 0.47), (285, 0.47), (310, 0.55), (335, 0.52)]
SEAM, CAP_RAISE = 0.04, 0.22

# The red shell round it: its shade (ramp 4) where it meets the cap, near the rim (at RIM_AT of the radius) and at the
# outline, by the angle round the ball; the crescent inside the rim at the lower right (its angle, spread (degrees),
# distance out, half-width and peak over the shell); faint patches; the shade on the side the camera doesn't see.
RIM = [(0, 0.2, 1.2, 2.2), (30, 0.2, 1.2, 2.2), (60, 0.5, 1.5, 2.4), (90, 2.2, 2.8, 2.6), (120, 2.6, 3.0, 2.8),
       (150, 2.8, 3.0, 3.0), (180, 2.6, 3.0, 3.0), (210, 1.0, 3.8, 3.6), (240, 0.6, 4.8, 4.6), (270, 0.4, 6.2, 5.6),
       (300, 0.8, 7.0, 5.8), (330, 0.6, 3.4, 3.0)]
RIM_AT = 0.9
CRESCENT_AT, CRESCENT_SPREAD, CRESCENT_RHO, CRESCENT_W, CRESCENT_PEAK = -44.0, 26.0, 0.865, 0.07, 9.0
PATCHES = 0.35
BACK = 1.5

# The lights in the black, as the sprite draws them (pixels from the sprite's centre): (x, y, vertical stretch, shade by
# distance (pixels) from the middle, how much the lens bulges out of the glass and its radius).
LIGHTS = [
    # The big eye (columns 7-10 of rows 10-13): white-pink, pink, red, into the black.
    (-2.5, 1.6, 1.0, [(0.0, 15.0), (0.6, 15.0), (0.95, 13.8), (1.3, 12.0), (1.7, 9.6), (2.1, 7.0), (2.5, 3.6),
                      (2.9, 0.4), (3.3, -2.0)], 0.28, 2.9),
    # The small light below the middle (column 12 of rows 14-15).
    (0.5, -1.25, 1.35, [(0.0, 13.5), (0.4, 12.6), (0.75, 9.4), (1.05, 5.6), (1.35, 2.0), (1.7, -2.0)], 0.16, 1.7),
    # The dim ember up to the right of the eye (column 13 of row 11).
    (1.5, 2.5, 1.0, [(0.0, 8.6), (0.45, 7.6), (0.85, 4.4), (1.2, 1.2), (1.6, -2.0)], 0.12, 1.6),
]

# The bands of shade: (lowest shade, palette index, emission strength, the emission's palette index). Fifteen
# materials at most: 0x41 and 0x46 are left out.
BANDS = [
    (-9.0, 0x01, 0.0, None),
    (-1.0, 0x40, 0.2, 0x42),
    (1.0, 0x42, 0.22, 0x43),
    (2.5, 0x43, 0.25, 0x44),
    (3.5, 0x44, 0.28, 0x44),
    (4.5, 0x45, 0.3, 0x45),
    (6.0, 0x47, 0.34, 0x47),
    (7.5, 0x48, 0.38, 0x48),
    (8.5, 0x49, 0.4, 0x49),
    (9.5, 0x4a, 0.43, 0x4a),
    (10.5, 0x4b, 0.46, 0x4b),
    (11.5, 0x4c, 0.5, 0x4c),
    (12.5, 0x4d, 0.54, 0x4d),
    (13.5, 0x4e, 0.57, 0x4e),
    (14.5, 0x4f, 0.6, 0x4f),
]


def view(p):
    """Where the point p of the ball's surface shows in the view the painting is laid out in: in the sprite's pixels
    (from the sprite's centre), the angle round the ball's middle (degrees), the distance out (a fraction of the
    radius; on the side the view doesn't see, 2 less it) and whether the view sees it."""
    rel = p - CENTRE
    u = rel.x / RX
    v = (rel.y * math.cos(T) + rel.z * math.sin(T)) / VIEW_H
    normal = Vector((rel.x / RX ** 2, rel.y / RY ** 2, rel.z / RZ ** 2))
    seen = normal.dot(TOWARDS_VIEW) > 0.0
    rho = math.hypot(u, v)
    angle = math.degrees(math.atan2(v, u)) % 360.0
    sprite = Vector((CENTRE.x + u * RX, CENTRE.y + v * 7.5))
    return sprite, angle, (rho if seen else 2.0 - rho), seen


def direction(p):
    rel = p - CENTRE
    return Vector((rel.x / RX, rel.y / RY, rel.z / RZ)).normalized()


def outward(p):
    rel = p - CENTRE
    return Vector((rel.x / RX ** 2, rel.y / RY ** 2, rel.z / RZ ** 2)).normalized()


def angle_off(a, b):
    return (a - b + 180.0) % 360.0 - 180.0


def shell_shade(angle, rho, d):
    at_cap, near_rim, outline = [periodic([(r[0], r[i]) for r in RIM], angle) for i in (1, 2, 3)]
    cap = periodic(CAP, angle)
    if rho <= RIM_AT:
        s = at_cap + (near_rim - at_cap) * smoothstep(cap, RIM_AT, rho)
    elif rho <= 1.0:
        s = near_rim + (outline - near_rim) * smoothstep(RIM_AT, 1.0, rho)
    else:   # the side the view doesn't see: the outline's shade fading to the shell's dark red
        s = outline + (BACK - outline) * smoothstep(1.0, 1.15, rho)
    s += CRESCENT_PEAK * (math.exp(-(angle_off(angle, CRESCENT_AT) / CRESCENT_SPREAD) ** 2) *
                          math.exp(-((rho - CRESCENT_RHO) / CRESCENT_W) ** 2))
    patches = noise.noise(d * 2.3 + Vector((1.0, 5.0, 2.0))) + 0.5 * noise.noise(d * 5.1 + Vector((3.0, 1.0, 7.0)))
    return s + PATCHES * patches * (1.0 - 0.8 * smoothstep(2.0, 6.0, s))


def shade_and_lift(p):
    """The shade at the ball's surface point p (-2: the black glass, 0-15: ramp 4) and how far the surface there
    stands out of the ellipsoid."""
    d = direction(p)
    sprite, angle, rho, seen = view(p)
    s = shell_shade(angle, rho, d)
    lift = 0.06 * noise.noise(d * 3.0 + Vector((4.0, 2.0, 7.0)))
    if not seen:
        return s, lift
    inside = periodic(CAP, angle) - rho            # > 0 inside the cap
    black = smoothstep(-SEAM, SEAM, inside)
    s = s * (1.0 - black) + (-2.0) * black
    lift += CAP_RAISE * smoothstep(-0.02, 0.03, inside)
    if inside > -0.05:
        for x, y, stretch, profile, bulge, radius in LIGHTS:
            r = math.hypot(sprite.x - x, (sprite.y - y) / stretch)
            if r < radius + 1.0:
                s = max(s, radial(profile, r))
                lift += bulge * max(0.0, 1.0 - (r / radius) ** 2) ** 2
    return s, lift


def ball_mesh(name):
    """An ellipsoid of even triangles (an icosphere), finer where the camera sees it and finer still round the
    lights and the crescent."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=3, radius=1.0)

    def point(v):
        d = v.co.normalized()
        return CENTRE + Vector((d.x * RX, d.y * RY, d.z * RZ))

    def seen(v):
        return outward(point(v)).dot(TOWARDS_VIEW) > -0.2

    def detailed(v):
        sprite, angle, rho, vis = view(point(v))
        if not vis:
            return False
        near_light = any(math.hypot(sprite.x - x, sprite.y - y) < r + 0.8 for x, y, _, _, _, r in LIGHTS)
        return near_light or (rho > 0.7 and 250 < angle < 360)

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
    pal = k.level_palette()
    mats = {}
    for _, index, strength, emit in BANDS:
        black = index < 0x40
        mats[index] = k.material(f"orbsmall_{index:02x}", palette=index, metallic=0.05 if black else 0.0,
                                 roughness=0.12 if black else 0.22 if strength < 0.45 else 0.3,
                                 emission=pal[emit] if emit is not None else None, emission_strength=strength)
    return mats


def filled(mask):
    """The mask with its holes filled: the sprite leaves the black glass transparent, inside the orb's outline (the
    pixels the transparent ones round the cell's border don't reach)."""
    h, w = len(mask), len(mask[0])
    outside = [[False] * w for _ in range(h)]
    todo = [(y, x) for y in range(h) for x in range(w) if (y in (0, h - 1) or x in (0, w - 1)) and not mask[y][x]]
    while todo:
        y, x = todo.pop()
        if outside[y][x] or mask[y][x]:
            continue
        outside[y][x] = True
        todo += [(y + dy, x + dx) for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1))
                 if 0 <= y + dy < h and 0 <= x + dx < w]
    return [[not outside[y][x] for x in range(w)] for y in range(h)]


def build():
    options = k.args()
    out = mk.outdir(options)
    k.reset()
    mats = materials()
    orb = ball_mesh(NAME)
    values = []
    for v in orb.data.vertices:
        p = v.co.copy()
        s, lift = shade_and_lift(p)
        values.append(s)
        v.co = p + outward(p) * lift
    band_split(orb, values, [(lowest, mats[index]) for lowest, index, _, _ in BANDS])
    k.smooth(orb, 70)
    objects = triangulate([orb])  # the same split every run (with and without --check)
    bpy.context.view_layer.update()
    if "check" in options:
        sheets = options["check"]
        sheet = os.path.join(sheets, "enemy_E.png") if os.path.isdir(sheets) else sheets
        mk.compare("%s (E %d, its transparent black glass filled)" % (NAME, SPRITE), mk.coverage(objects, 24, 28),
                   filled(k.sprite_mask(sheet, SPRITE)))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mk.report(NAME, objects, os.path.join(out, NAME + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + NAME, objects, scale=20, distance=0.55)


if __name__ == "__main__":
    build()
