"""The mace of GAUNTLET and MACES (sheet A sprites 77, 79 and 81 above 115, 117 and 119, 2x2 each: one 72 x 56
picture; ground layer; one frame each), polished (2026-10-21; it replaces wave3_q_mace.py's mace_whole(), a ball painted
pixel by pixel in the sprite's greys with plain cones and tori). models.cfg: model mace_tl / mace_tc / mace_tr / mace_bl
/ mace_bc / mace_br ... origin (unchanged); sprite a 77 mace_tl yaw=0, sprite a 79 mace_tc yaw=0, sprite a 81 mace_tr
yaw=0, sprite a 115 mace_bl yaw=0, sprite a 117 mace_bc yaw=0, sprite a 119 mace_br yaw=0 (unchanged: no height=-4, so
that the eyelet stays at the height of the chain's rings, CHAIN_Z, as the anchor's ball does). No other enemy shows
these sprites; none of the six is another's pixels mirrored, turned or in other ramps (the picture is nearly
symmetric, but its light from the upper left makes the halves differ). No 4x upscale of these sprites exists: modelled
from the original pixels.

How the levels place it (custom enemies of event 52, the ground enemies' second slots; GAUNTLET's second chain at 1196,
MACES' at 106, 160, 272 and 468): the six sprites as the sheet arranges them, 77, 79 and 81 at x, x + 24 and x + 48, 28
pixels above 115, 117 and 119, all of one link number with the chain's three rings and its anchor beside it (the
largest ring's middle 24 pixels from the mace's); events 19, 20 and 27 then send them circling round (exc / eyc 0 / 8,
accelerating by one every 3 frames, reversing at 8), the rings on smaller circles, so that the chain swings round
its anchor with the mace at its end. The mace never turns (yaw=0): seen from above whichever way the chain points.

As the sprite draws it (the 72 x 56 picture's columns and rows; greys of ramp 0, bronze of ramp 10): a steel ball
(columns 20-52 of rows 12-44, its middle at pixel 36, 28) lit from the upper left, a white glare there (columns 28-31 of
rows 20-23) fading through light greys, its lower right dark; four long spikes along the screen's axes (to row 1, row
55, column 9 and column 63: 27.5 pixels from the middle), round cones lit along their axes, 9 pixels across with their
outline at their feet (row 11), 7 for the next four rows, then narrowing in steps to the point (a full, bullet-like
taper), each in a bronze collar at the ball's edge (rows 12-14, columns 20-22, column 51, rows 43-44); four short spikes
between them (their tips at columns 20 and 52 of rows 12 and 44, 22.6 pixels out on the diagonals), steel cones rising
from behind the ball's edge; on top in the middle a bronze eyelet (columns 32-41 of rows 24-33), a ring thicker on its
lower right, round a steel bolt lit at its upper left (columns 34-38 of rows 26-30).

Built as a forged and turned piece: the ball an ellipsoid a little flattened (its top at the chain's height) painted in
bands as polish_balls.painted_ball paints its balls (the dark rim where it turns away, the glare at its upper left in
soft rings; a little emission in its own grey, since balls the slanted camera sees read near black); the spikes turned
cones (a short foot, then a full (ogive) taper to a sharp point, as the sprite's steps draw it), their collars turned
bronze bands with a lip, sunk into the ball; the short spikes radial cones rising ELEVATION degrees; the eyelet a turned
bronze grommet on the ball's top, its middle at CHAIN_Z where the chain's rings lie, and in it a domed steel bolt. Steel
as the chain's (glossy, metallic, ramp 0's greys), bronze as the collar's sprite pixels (ramp 10). Built whole and cut
along the sprites' edges (polish_arch.py's cut(): the pieces keep the whole's shading across the cuts), each piece moved
so its sprite's centre is its origin; every mesh triangulated before the export (polish_k_pod.triangulate: the same
split every run).

The heights: the levels' ground enemies stand 4 pixels above the terrain, the chain's rings and the anchor's ball at
CHAIN_Z (14) above that. The ball's middle is BALL_Z over the base, its top just under CHAIN_Z, the long spikes and
their collars round its middle (their undersides above the terrain); the eyelet's grommet stands from the ball's top to
15.1, its middle at CHAIN_Z, the bolt's head to 16.4. (The ball's lower half reaches under the terrain; the game's
camera, 20 degrees from straight down, never sees below z = -2.3 of it.)

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the base (z = 0); the whole's
origin is the middle of the picture (the edge between 79 and 117): column c's left edge is x = c - 36, row r's top
edge y = 28 - r.

Replaces wave3_q_mace.py's mace: remove MACE_ORIGIN, BALL, BALL_R, BALL_RZ, mace_whole() with its @q.whole("mace",
(72, 56)) registration, MACE_PIECES with its loop and place_pieces("mace", mace_whole, MACE_PIECES), steel() (only
mace_whole() calls it), "from mathutils import Vector" (only the mace uses it) and the mace lines of its docstring
("--whole mace|chest" becomes "--whole chest"); and wave3_q_art.py's MACE (only mace_whole() reads it). wood(),
shade_paint(), place_pieces() and math stay: the skull chest uses them.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the whole
and of each piece against enemy_A.png), --preview <prefix> (the whole's and each piece's top and 3/4 views),
--only <model,...>, --whole <file.glb> (the uncut mace as well, for looking at).
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_arch import cut  # noqa: E402  (polish_machine_kit.cut without its material indices shifted twice)
from polish_balls import Ellipsoid, painted_ball  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402

# The pieces: (name, sprite, the box it covers in the whole's coordinates (x0, x1, y0, y1)).
PIECES = [("mace_tl", 77, (-36.0, -12.0, 0.0, 28.0)), ("mace_tc", 79, (-12.0, 12.0, 0.0, 28.0)),
          ("mace_tr", 81, (12.0, 36.0, 0.0, 28.0)), ("mace_bl", 115, (-36.0, -12.0, -28.0, 0.0)),
          ("mace_bc", 117, (-12.0, 12.0, -28.0, 0.0)), ("mace_br", 119, (12.0, 36.0, -28.0, 0.0))]
SPRITE_AT = {77: (0, 0), 79: (24, 0), 81: (48, 0), 115: (0, 28), 117: (24, 28), 119: (48, 28)}  # in the picture

CHAIN_Z = 14.0                       # the chain's height (polish_chain_ring.py, polish_mace_anchor.py)
BALL_AT = (0.5, -0.5)                # the ball's middle seen from above (pixel 36, 28's centre)
BALL_Z = 0.85                        # its middle's height (the long spikes' undersides above the terrain)
BALL_R = 16.95                       # its radius across (to the sprite's outline)
BALL_RZ = CHAIN_Z - 0.8 - BALL_Z     # its half height: its top just under the chain's height
# The glare: its middle's offset from the ball's seen from above (beside where the game's sun puts its own
# highlight for its camera, which shows the two where the sprite draws its glare, columns 28-31 of rows 20-23, clear of
# the eyelet), and its size; the dark rim (the normal's z).
GLARE_AT, GLARE_SIZE = (-6.5, 3.8), 3.4
RIM = 0.2
# The long spikes: directions seen from above, their tips' distance from the middle (the lower one a little short of
# the picture's edge), the turned profile from inside the ball out: (radius, distance from the middle).
LONG = [((0.0, 1.0), 27.5), ((0.0, -1.0), 27.35), ((-1.0, 0.0), 27.5), ((1.0, 0.0), 27.5)]
SPIKE = [(4.2, 13.0), (4.25, 17.0), (4.05, 17.55), (3.75, 17.85), (3.62, 18.3)] + [
    (3.62 * (1.0 - t ** 1.7) + 0.04, 18.3 + 9.0 * t) for t in (0.12, 0.25, 0.38, 0.5, 0.62, 0.72, 0.81, 0.89, 0.95)]
SPIKE_SEGMENTS = 24
# The collars round their feet: a band and a lip at its outer end ((radius, distance)).
COLLAR = [(4.5, 13.4), (4.85, 13.7), (4.98, 14.4), (4.98, 16.45), (4.88, 16.95), (5.15, 17.1), (5.2, 17.55),
          (4.95, 17.8), (4.3, 17.88)]
# The short spikes: rising ELEVATION degrees on the diagonals, their tips TIP_PLAN out seen from above; the radius at
# the ball's surface.
ELEVATION, TIP_PLAN, SHORT_BASE = 20.0, 22.9, 3.1
# The eyelet: a bronze grommet on the ball's top (its middle seen from above, its turned profile (radius, z) from its
# foot, sunk into the ball, out and up, over its top and down into its hole), the steel bolt's domed head in it.
EYELET_AT = (0.7, -0.75)
GROMMET = [(r, CHAIN_Z + dz) for r, dz in ((5.05, -3.0), (5.35, -1.6), (5.5, -0.6), (5.42, 0.45), (5.1, 0.95),
                                           (4.6, 1.12), (3.2, 1.12), (2.75, 0.95), (2.5, 0.55), (2.42, 0.1))]
BOLT = [(r, CHAIN_Z + dz) for r, dz in ((2.4, -0.3), (2.42, 0.6), (2.3, 1.15), (2.02, 1.62), (1.6, 1.98), (1.08, 2.22),
                                        (0.5, 2.34), (0.02, 2.36))]


def materials():
    def steel(name, index, metallic=0.75, roughness=0.26, glow=None):
        if glow:
            return k.material(name, palette=index, metallic=metallic, roughness=roughness,
                              emission=k.level_palette()[index], emission_strength=glow)
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)

    def bronze(name, index, roughness=0.3):
        return k.material(name, palette=index, metallic=0.7, roughness=roughness)
    return {
        "ball": steel("mace_ball", 0x0a, 0.55, 0.24, glow=0.12),     # (balls the slanted camera sees read near black)
        "ball_rim": steel("mace_ball_rim", 0x05, 0.5, 0.4),
        "glare": steel("mace_glare", 0x0b, 0.4, 0.18),
        "glare_mid": steel("mace_glare_mid", 0x0d, 0.25, 0.14),
        "glare_core": steel("mace_glare_core", 0x0f, 0.1, 0.1),
        "spike": steel("mace_spike", 0x0a, 0.75, 0.24, glow=0.06),   # (the chain's steel)
        "spike_under": steel("mace_spike_under", 0x06, 0.7, 0.34),
        "bronze": bronze("mace_bronze", 0xaa),
        "bronze_lit": bronze("mace_bronze_lit", 0xad, 0.26),
        "bronze_dark": bronze("mace_bronze_dark", 0xa6, 0.36),
        "bolt": steel("mace_bolt", 0x0b, 0.7, 0.22, glow=0.06),
        "seam": steel("mace_seam", 0x03, 0.4, 0.5),
    }


# --- Helpers --------------------------------------------------------------------------------------------------------

def ball_centre():
    return Vector((BALL_AT[0], BALL_AT[1], BALL_Z))


def along(direction, origin):
    """The matrix turning +Z onto direction and moving the origin to origin."""
    d = Vector(direction).normalized()
    turn = Vector((0.0, 0.0, 1.0)).rotation_difference(d).to_matrix().to_4x4()
    return Matrix.Translation(Vector(origin)) @ turn


def turned(name, profile, direction, origin, mat, segments=SPIKE_SEGMENTS, angle=50.0):
    """A turned part: profile (radius, distance) along direction from origin, its ends closed to the axis."""
    obj = mk.lathe(name, [(r, z) for r, z in profile], (0.0, 0.0), mat, segments)
    obj.data.transform(along(direction, origin))
    obj.data.update()
    k.recalc_normals(obj)
    return k.smooth(obj, angle)


def ball_surface(direction):
    """Where the ray from the ball's middle in direction meets its surface: the distance."""
    d = Vector(direction).normalized()
    return 1.0 / math.sqrt((d.x / BALL_R) ** 2 + (d.y / BALL_R) ** 2 + (d.z / BALL_RZ) ** 2)


# --- The parts ------------------------------------------------------------------------------------------------------

def ball(m):
    """The ball: an ellipsoid painted with the dark rim where it turns away and the glare at its upper left."""
    c = ball_centre()
    shape = Ellipsoid(c, (BALL_R, BALL_R, BALL_RZ))
    gx, gy = c.x + GLARE_AT[0], c.y + GLARE_AT[1]

    def rim(p, n):
        return n.z

    def glare(p, n):
        if n.z <= 0.25:
            return 0.0
        return math.exp(-(((p.x - gx) / GLARE_SIZE) ** 2 + ((p.y - gy) / GLARE_SIZE) ** 2))
    paint = [(rim, (RIM,), ("ball_rim", "ball")),
             (glare, (0.2, 0.45, 0.74), (None, "glare", "glare_mid", "glare_core"))]
    return painted_ball("ball", shape, paint, m, subdivisions=5)


def long_spikes(m):
    """The four long spikes along the screen's axes, each in a bronze collar at the ball's edge."""
    c = ball_centre()
    for i, ((dx, dy), reach) in enumerate(LONG):
        direction = (dx, dy, 0.0)
        # The taper drawn out (or in) so that the point lands at reach.
        profile = [(r, z if z < 17.0 else 17.0 + (z - 17.0) * (reach - 17.0) / 10.5) for r, z in SPIKE]
        spike = turned(f"spike{i}", profile + [(0.03, reach)], direction, c, m["spike"])
        mk.paint(spike, lambda cc, n: m["spike_under"] if n.z < -0.55 else None)
        collar = turned(f"collar{i}", COLLAR, direction, c, m["bronze"], segments=32, angle=40.0)

        def collar_pick(cc, n, d=Vector(direction)):
            along_axis = n.dot(d)
            if along_axis > 0.45:            # the lip's face towards the tip
                return m["bronze_lit"]
            if n.z < -0.45:
                return m["bronze_dark"]
            if n.z > 0.55:
                return m["bronze_lit"]
            return None
        mk.paint(collar, collar_pick)


def short_spikes(m):
    """The four short spikes on the diagonals, rising ELEVATION degrees: radial cones from inside the ball, their tips
    TIP_PLAN out seen from above."""
    c = ball_centre()
    e = math.radians(ELEVATION)
    for i in range(4):
        a = math.radians(45 + 90 * i)
        d = Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e)))
        base = ball_surface(d)
        tip = TIP_PLAN / math.cos(e)
        slope = SHORT_BASE / (tip - base)
        profile = [(SHORT_BASE + slope * 2.0, base - 2.0), (SHORT_BASE, base),
                   (SHORT_BASE * 0.62, base + 0.38 * (tip - base)), (SHORT_BASE * 0.3, base + 0.7 * (tip - base)),
                   (0.03, tip)]
        spike = turned(f"short{i}", profile, d, c, m["spike"], segments=18)
        mk.paint(spike, lambda cc, n: m["spike_under"] if n.z < -0.55 else None)


def eyelet(m):
    """The bronze grommet on the ball's top, its middle at CHAIN_Z, and the domed steel bolt in it."""
    grommet = mk.lathe("grommet", GROMMET, EYELET_AT, m["bronze"], 40)
    k.smooth(grommet, 40)

    def pick(c, n):
        if n.z > 0.85:
            return m["bronze"]
        if n.z < -0.3:
            return m["bronze_dark"]
        r = math.hypot(c.x - EYELET_AT[0], c.y - EYELET_AT[1])
        if r < 3.3:                          # the hole's wall
            return m["bronze_dark"] if n.x > 0 or n.y < 0 else m["bronze_lit"]
        return m["bronze_lit"] if (n.x < -0.2 or n.y > 0.2) and n.z > 0.15 else None
    mk.paint(grommet, pick)
    bolt = mk.lathe("bolt", BOLT, EYELET_AT, m["bolt"], 32)
    k.smooth(bolt, 60)
    mk.paint(bolt, lambda c, n: m["spike_under"] if n.z < 0.35 and (n.x > 0.2 or n.y < -0.2) else None)


# --- Build ----------------------------------------------------------------------------------------------------------

def build_whole(m):
    ball(m)
    long_spikes(m)
    short_spikes(m)
    eyelet(m)
    whole = mk.meshes()
    for obj in whole:
        mk.apply(obj)
    bpy.context.view_layer.update()
    return whole


def whole_mask(sheet):
    mask = [[False] * 72 for _ in range(56)]
    for sprite, (c0, r0) in SPRITE_AT.items():
        part = k.sprite_mask(sheet, sprite)
        for y in range(28):
            for x in range(24):
                if part[y][x]:
                    mask[r0 + y][c0 + x] = True
    return mask


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    k.reset()
    m = materials()
    whole = build_whole(m)
    print("whole mace: %d triangles, %d objects" % (mk.triangles(whole), len(whole)))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    sheet = os.path.join(options["check"], "enemy_A.png") if "check" in options else None
    if sheet:
        mk.compare("whole (A 77 79 81 above 115 117 119)", mk.coverage(whole, 72, 56), whole_mask(sheet))
    if "preview" in options:
        mk.preview(options["preview"] + "mace_whole", whole, size=(72, 56), scale=8, distance=2.0)
    if "whole" in options:  # the uncut mace, for looking at
        mk.export(whole, options["whole"])
    for name, sprite, box in PIECES:
        if only and name not in only:
            continue
        pieces = [p for p in (cut(src, box, m["seam"]) for src in whole) if p is not None]
        mk.transform(pieces, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
        triangulate(pieces)
        bpy.context.view_layer.update()
        for src in whole:
            src.hide_render = True
        if sheet:
            mk.compare("%s (A %d)" % (name, sprite), mk.coverage(pieces, 24, 28), k.sprite_mask(sheet, sprite))
        mk.report(name, pieces, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, pieces)
        for obj in pieces:
            bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False


if __name__ == "__main__":
    build()
