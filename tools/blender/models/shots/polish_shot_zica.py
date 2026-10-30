"""The Zica Laser's beam (shots sheet sprites 97, 116, 135 and the wider 101, 120, 139, all 1x1: 12 x 14 cells),
modelled (2026-10-30, round 3 of the energy shots' models; until then each piece was drawn as its sprite with volume
and the automatic glow: a column of blue capsules in a white haze). Built with polish_shot_sidekick.py's Tube and
polish_shot_fireball.py's dome_core.

Who fires it: the Zica Laser (front port 5, shop 3:8, 1100; weapons 199-209), the Zica SuperCharger (sidekick 12: its
charge levels fire weapons 199-203), the Astral Zone special (13: weapon 672, volleys of both widths dropped at random
places) and the MegaLaser special (18: weapon 754, 116 one a frame at 14 a frame, following the ship: the Laser's way),
and CAMANIS's enemies 221 and 222 (weapon 34: 101, 120 and 139 fired together, falling at 14, 13 and 12 pixels a frame,
the head leading). The Zica Laser fires a volley every 6-9 frames: all its pieces at once, the head (97) 14 pixels
above the gun, the beam (116) at the gun, the tail (135) 14 below, so that they join end to end; they fly up
accelerating (a pixel a frame more each frame) and following the ship sideways (sx 120), the beam's pieces at speeds a
pixel apart, so the beam stretches as it flies (overlapping pieces drawing the same rod):
  power 1: 97 116 135 (8 a frame)          power 7: three short beams: 97 116 135 either side (14 a frame, 3 out
  power 2: 97 116 116 135 (9, 9, 8, 8)              a frame), 97 + 135 in the middle 4 ahead
  power 3: 97 + three 116 + 135 (9 .. 7)  power 8: the same, the middle one wide (101 + 139)
  power 4: 97 + four 116 + 135 (9 .. 6)   power 9: narrow 97 + 135 left, wide 101 + 139 right, wide 101 120 120 139
  power 5: 97 + six 116 + 135 (9 .. 4)              in the middle
  power 6: two beams (97 116 116 135)      power 10: 101 + six 120 + 139 (9 .. 4)
           spreading 1 a frame             power 11: two wide beams (101 120 120 139) 16 apart
Since the pieces of a volley are fired together and fly as one beam, the lines don't take beam (it would keep a copy
of every piece where it was fired for the frame it is fired in, and the volley's tail would jump at the next tick);
the MegaLaser's 116, fired one a frame, would want it (see the block's comment).

As the sprites draw them (ramp 9, the blue 0x90-0x9f, and ramp 8's pale blue-white 0x8a-0x8f):
- 116 the beam, 9 pixels wide (columns 2-10, its middle column 6: x 0.5), every row 91 95 99 9c 9f 9c 99 95 91 (a
  light blue middle); 120 the wide beam, 12 (the whole cell, x 0), 91 95 99 9c 9f 8c 8c 9f 9c 99 95 91 (its middle two
  columns pale blue-white).
- 97 the head: the beam swelling into a bulb 11 wide (columns 1-11, rows 4-12), round at its top (rows 0-3), white
  (0x8f) over its upper middle (rows 2-8) in rings of pale blue (0x8d, 0x8a) and light blue, the white running on down
  its middle column into the beam's 9f; 101 the wide head: the wide beam's own width, round at its top (row 0), white
  over rows 2-7 (8 columns), pale down its middle into the wide beam's 8c.
- 135 the tail: the beam narrowing from 9 to 3 pixels (7 at rows 3-7, 5 at 8-11, 3 at 12-13) and darkening a shade
  every row or so (its middle 9f .. 94); 139 the wide one, 12 to 6 (10, 8), its middle 8c .. 92.

The models: the beam is a rod (polish_shot_sidekick.Tube), round on top and flat underneath (its section a flattened
half-ellipse, DEPTH), its bands of ramp 9 along it (each border on a section point of the mesh, the faces between them
one band each: no face is cut), a core line standing out of its top down the middle (light blue; the wide beam's pale
blue-white), the same section at both ends of every piece so that the pieces join: the head's and the tail's ends at the
joints are the beam's. Each piece runs from its cell's top edge to its bottom edge (y 7 to -7), its bottom end rounded
inside the piece below where they join (open at its top: it faces away from the camera). The head swells into its bulb
and rounds off at its top, a ball of white plasma standing out of it (polish_shot_fireball.dome_core: white in its
middle, pale blue, light blue round it); the core line runs from the joint up into the ball (ringed every pixel, so that
it stays on the bulb's top), and at every joint it is cut off flat and left open, so that the overlapping pieces of a
volley show one unbroken line (a rounded or capped end lies almost on the next piece's line). The tail narrows to a
rounded point, darkening along it, its bands lying in long V's down it (polish_shot_sidekick.stream: the mesh's lines
follow the bands' borders, rings across it every 1.2 pixels; rings on borders that cross it at such a slant folded
faces), its core line fading out. Every material a palette index's (the rod's and the core line's alike), glowing in its
own colour by its shade at EMISSION of the shots' table (the beams' glows overlap). height= on the head's lines (its
ball stands higher than the beam: the game centres a model on its height bounds), printed by the build.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the origin at the
cell's centre (pixel 6, 7: column c is x = c + 0.5 - 6, row r is y = 6.5 - r, its top edge y = 7 - r); built on z = 0.

models.cfg: see the block's comment.

Run: Blender -b --factory-startup -P tools/blender/models/shots/polish_shot_zica.py -- [--only <name,...>]
     [--outdir <dir>] (default assets/models/shots) [--check <sheets dir>] (each piece's top view against its sprite
     in <dir>/shots.png) [--preview <prefix>] (top, three-quarter and game-camera views, and <prefix>beams_game.png:
     volleys of both widths, their pieces joined and overlapping as the game flies them)
"""
import math
import os
import sys

import bpy
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from polish_shot_sidekick import (kit, k, mk, triangulate, view, Path, Tube, band_material, top_of,  # noqa: E402
                                  facing, stream)
from polish_shot_starburst import game_camera  # noqa: E402

OUTDIR = kit.OUTDIR
HALF = 7.0  # half a piece's length (the cell's 14 rows)
DEPTH = 0.6  # the rod's height over its half-width
CAP = 0.36  # the rounded bottom end's length (times the half-width)
EMISSION = 0.85
CORE_HALF, CORE_LIFT = 0.7, 0.3

# The widths: the middle's x, the half-width; the heat across (u: 0 the middle, 1 the edge; one scale from ramp 9's
# shades up through ramp 8's pale blue-white: polish_shot_sidekick.shade_of), the rod's bands and its core line's.
WIDTHS = {
    "narrow": dict(x=0.5, half=4.5,
                   across=((0.0, 15.6), (0.222, 12.6), (0.444, 9.4), (0.667, 5.4), (0.889, 1.6), (1.0, 0.8)),
                   bands=[(-99.0, 0x92), (3.2, 0x95), (7.2, 0x98), (10.8, 0x9b), (13.8, 0x9d)],
                   core=[(-99.0, 0x9d), (14.6, 0x9f)], core_heat=15.6),
    "wide": dict(x=0.0, half=6.0,
                 across=((0.0, 19.6), (0.083, 19.2), (0.25, 15.4), (0.417, 12.4), (0.583, 9.3), (0.75, 5.4),
                         (0.917, 1.6), (1.0, 0.8)),
                 bands=[(-99.0, 0x92), (3.2, 0x95), (7.2, 0x98), (10.8, 0x9b), (13.8, 0x9d), (16.6, 0x8b)],
                 core=[(-99.0, 0x9d), (14.0, 0x9f), (17.0, 0x8b), (19.0, 0x8d)], core_heat=19.6),
}
# The heads: half-width by y (the bulb), the ball (its middle, half-axes, lift, bands from its middle out).
HEADS = {
    "narrow": dict(width=((7.0, 0.0), (6.92, 1.5), (6.7, 2.45), (6.2, 3.25), (5.4, 4.1), (4.4, 4.8), (3.2, 5.25),
                          (2.0, 5.5), (-3.5, 5.5), (-4.8, 5.35), (-5.9, 4.95), (-7.0, 4.5)),
                   ball=((0.5, 1.9), 3.25, 4.5, 0.55),
                   ball_bands=((0.0, 0x8f), (0.4, 0x8d), (0.62, 0x8b), (0.8, 0x9f))),
    "wide": dict(width=((7.0, 0.0), (6.95, 2.2), (6.8, 3.8), (6.4, 5.0), (5.8, 5.7), (5.0, 6.0), (-7.0, 6.0)),
                 ball=((0.0, 2.3), 4.6, 4.4, 0.6), ball_bands=((0.0, 0x8f), (0.45, 0x8d), (0.66, 0x8b), (0.84, 0x9f))),
}
# The tails: half-width by y; the heat on the middle line by y (each row's middle column) and how much less at the edge.
TAILS = {
    "narrow": dict(width=((7.0, 4.5), (5.5, 4.4), (3.0, 3.8), (0.0, 3.1), (-3.0, 2.45), (-5.5, 1.8), (-7.0, 1.35),
                          (-7.35, 0.85), (-7.6, 0.0)),
                   along=((7.0, 15.6), (6.5, 15.0), (4.5, 14.0), (2.5, 13.0), (0.5, 11.0), (-1.5, 9.0), (-3.5, 7.0),
                          (-5.5, 5.0), (-7.0, 3.6), (-7.6, 3.0)),
                   drop=((7.0, 15.0), (-7.6, 13.0))),
    "wide": dict(width=((7.0, 6.0), (5.0, 5.85), (2.0, 5.15), (-1.0, 4.4), (-4.0, 3.65), (-6.0, 3.1), (-7.0, 2.75),
                        (-7.4, 1.8), (-7.65, 0.0)),
                 along=((7.0, 19.6), (6.5, 17.5), (5.5, 14.4), (3.5, 13.0), (1.5, 12.0), (-0.5, 10.0), (-2.5, 8.0),
                        (-4.5, 5.6), (-6.5, 3.4), (-7.65, 2.2)),
                 drop=((7.0, 19.0), (-7.65, 10.0))),
}
# name: (sprite, width, piece)
MODELS = [
    ("shot_zica", 116, "narrow", "beam"),
    ("shot_zica_97", 97, "narrow", "head"),
    ("shot_zica_135", 135, "narrow", "tail"),
    ("shot_zica_120", 120, "wide", "beam"),
    ("shot_zica_101", 101, "wide", "head"),
    ("shot_zica_139", 139, "wide", "tail"),
]
FAMILY_BASE = {"narrow": "shot_zica", "wide": "shot_zica_120"}


def materials_for(bands, prefix="zica"):
    return [band_material(prefix, i, factor=EMISSION) for _, i in bands]


def straight(x, top, bottom):
    """A straight path down the screen from y top to y bottom."""
    return Path([(x, top), (x, bottom)], smooth=0)


def by_y(points, top, bottom):
    """A curve given by y ([(y, value)] from the top down) as a function of t (0 at y top, 1 at y bottom)."""
    f = kit.curve(sorted(points))

    def at(t):
        return f(top - t * (top - bottom))
    return at


def bottom_cap(half):
    """The rounded bottom end: (its length, its rings' t fractions along it)."""
    return CAP * half, (0.4, 0.75, 0.94)


def rod_heat(spec):
    across = kit.curve(spec["across"])

    def heat(t, u):
        return across(min(abs(u), 1.0))
    return heat


def core_line(name, spec, host, top, bottom, along=None, rounded_top=False, open_top=False, open_bottom=False,
              ring_gap=7.0):
    """The core line along the rod's top (its middle), from y top to y bottom, its bottom end rounded off; along(t):
    its heat along it (default the rod's middle's). open_top, open_bottom: that end cut off flat and left open, at a
    joint (where the pieces of a volley overlap, an end rounded or capped inside another piece's core line lies almost
    on it: the two fight for the depth in dashes down the line). ring_gap: the longest stretch between its rings (it
    stands on its host at its rings only: over a bulb, close rings, or it sinks into it between them)."""
    cap = 0.55
    end = bottom if open_bottom else bottom - cap
    path = straight(spec["x"], top, end)
    length = top - end

    def width(t):
        y = top - t * length
        if y < bottom:
            return CORE_HALF * math.sqrt(max(0.0, 1.0 - ((bottom - y) / cap) ** 2))
        if rounded_top and y > top - cap:
            return CORE_HALF * math.sqrt(max(0.0, 1.0 - ((y - (top - cap)) / cap) ** 2))
        return CORE_HALF

    def heat(t, u):
        h = along(t) if along is not None else spec["core_heat"]
        return h - 0.8 * u * u

    def floor(x, y):
        return host.top(x, y) - 0.05
    tube = Tube(path, width, heat, spec["core"], depth=CORE_LIFT / CORE_HALF + 0.0, floor=floor, gap=1.5,
                angle_gap=math.radians(45.0), caps=(not open_top, not open_bottom))
    if along is None:
        n = int(length / ring_gap) + 1
        tube.fixed = sorted([i / n * (top - bottom) / length for i in range(n + 1)] + ([] if open_bottom else [
            ((top - bottom) + cap * f) / length for f in (0.45, 0.8, 1.0)]) + ([] if not rounded_top else [
            cap * f / length for f in (0.2, 0.55, 1.0)]))
    return tube.build(name, materials_for(spec["core"]))


def beam(name, spec):
    half = spec["half"]
    cap, cap_rings = bottom_cap(half)
    path = straight(spec["x"], HALF, -HALF - cap)
    length = 2 * HALF + cap

    def width(t):
        y = HALF - t * length
        return half if y >= -HALF else half * math.sqrt(max(0.0, 1.0 - ((-HALF - y) / cap) ** 2))
    rod = Tube(path, width, rod_heat(spec), spec["bands"], depth=DEPTH, angle_gap=math.radians(20.0),
               caps=(True, True), fixed=[0.0, 2 * HALF / length] + [(2 * HALF + cap * f) / length for f in cap_rings]
               + [1.0])
    body = rod.build(name + "_rod", materials_for(spec["bands"]))
    parts = [k.smooth(body, 60)]
    parts.append(k.smooth(core_line(name + "_core", spec, rod, HALF, -HALF, open_top=True, open_bottom=True), 60))
    return parts


def head(name, spec, head_spec):
    half = spec["half"]
    cap, cap_rings = bottom_cap(half)
    path = straight(spec["x"], HALF, -HALF - cap)
    length = 2 * HALF + cap
    bulb = kit.curve(sorted(head_spec["width"]))

    def width(t):
        y = HALF - t * length
        return bulb(y) if y >= -HALF else half * math.sqrt(max(0.0, 1.0 - ((-HALF - y) / cap) ** 2))
    # (rings: close at the round top, every pixel or so down the bulb, the joint, the bottom cap)
    ys = [7.0, 6.97, 6.85, 6.6, 6.2, 5.6, 4.8, 3.8, 2.6, 1.0, -1.0, -3.0, -4.6, -5.9, -7.0]
    fixed = [(HALF - y) / length for y in ys] + [(2 * HALF + cap * f) / length for f in cap_rings] + [1.0]
    rod = Tube(path, width, rod_heat(spec), spec["bands"], depth=DEPTH, angle_gap=math.radians(20.0),
               caps=(True, True), fixed=fixed)
    body = rod.build(name + "_rod", materials_for(spec["bands"]))
    parts = [k.smooth(body, 60)]
    (bx, by), rx, ry, lift = head_spec["ball"]
    ball_bands = [(f, i, 0.0) for f, i in head_spec["ball_bands"]]
    mats = [band_material("zica", i, factor=EMISSION) for _, i in head_spec["ball_bands"]]
    parts.append(kit.dome_core(name + "_ball", (bx, by), rx, ry, lift, rod.top, ball_bands, mats, segments=20,
                               tongues=(5, 0.025, 1.0)))
    # (the core line from the joint up into the ball, its top end hidden under the ball)
    parts.append(k.smooth(core_line(name + "_core", spec, rod, by - ry * 0.55, -HALF, rounded_top=True,
                                    open_bottom=True, ring_gap=1.0), 60))
    return parts


def tail(name, spec, tail_spec):
    widths = sorted(tail_spec["width"])
    bottom = widths[0][0]
    path = straight(spec["x"], HALF, bottom)
    w = by_y(tail_spec["width"], HALF, bottom)
    along = by_y(tail_spec["along"], HALF, bottom)
    drop = by_y(tail_spec["drop"], HALF, bottom)

    def heat(t, u):
        return along(t) - drop(t) * min(abs(u), 1.0)
    rod = Tube(path, w, heat, spec["bands"], depth=DEPTH, angle_gap=math.radians(24.0))
    # (rings every 1.2 pixels, closer at the rounded tip; the bands' borders, long V's down the tail, on the section
    # lines that follow them: polish_shot_sidekick.stream)
    length = HALF - bottom
    ys = [HALF - i * 1.2 for i in range(int((HALF + 6.6) / 1.2) + 1)] + [-6.9, -7.2, -7.4, -7.52, bottom]
    ts = sorted({round((HALF - y) / length, 6) for y in ys if y >= bottom})
    body = stream(rod, name + "_rod", materials_for(spec["bands"]), ts, caps=(True, False))
    parts = [k.smooth(body, 60)]
    # (the core line fading down the tail: the middle line's heat, a shade hotter, ending where it has faded)
    end = 0.0
    for i in range(101):
        t = i / 100
        if along(t) + 0.6 < spec["core"][1][0]:
            break
        end = t
    end_y = HALF - end * (HALF - bottom)

    def core_along(t):
        y = HALF - t * (HALF - end_y + 0.55)
        tt = (HALF - y) / (HALF - bottom)
        return along(min(max(tt, 0.0), 1.0)) + 0.6
    parts.append(k.smooth(core_line(name + "_core", spec, rod, HALF, end_y, along=core_along, open_top=True), 60))
    return parts


def build_model(name, sprite, width, piece):
    spec = WIDTHS[width]
    if piece == "beam":
        return triangulate(beam(name, spec))
    if piece == "head":
        return triangulate(head(name, spec, HEADS[width]))
    return triangulate(tail(name, spec, TAILS[width]))


# --- Previews: volleys as the game flies them -------------------------------------------------------------------------

VOLLEYS = [  # (x, [(sprite, y of its cell's centre)]): power 1's volley, power 5's stretched, power 11's two wide beams
    (-26.0, [(97, 14.0), (116, 0.0), (135, -14.0)]),
    (-8.0, [(97, 30.0), (116, 16.0), (116, 12.0), (116, 8.0), (116, 4.0), (116, 0.0), (116, -4.0), (135, -18.0)]),
    (10.0, [(101, 14.0), (120, 0.0), (120, -3.0), (139, -17.0)]),
    (26.0, [(101, 14.0), (120, 0.0), (120, -3.0), (139, -17.0)]),
]


def volleys_view(prefix, heights):
    k.reset()
    scene = bpy.context.scene
    scene.view_settings.view_transform = "Standard"
    by_sprite = {s: (n, w, p) for n, s, w, p in MODELS}
    for x, pieces in VOLLEYS:
        for sprite, y in pieces:
            name, width, piece = by_sprite[sprite]
            parts = build_model(name, sprite, width, piece)
            lift = heights.get(name, 0.0) - top_of(parts) / 2
            mk.transform(parts, Matrix.Translation((x, y, lift)))
    bpy.context.view_layer.update()
    cam, sun = game_camera(scene, 90.0, (900, 1100))
    scene.render.filepath = prefix + "beams_game.png"
    bpy.ops.render.render(write_still=True)


def build():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    outdir = options.get("outdir", OUTDIR)
    tops = {}
    for name, sprite, width, piece in MODELS:
        k.reset()
        tops[name] = top_of(build_model(name, sprite, width, piece))
    heights = {name: round((tops[name] - tops[FAMILY_BASE[width]]) / 2, 2) for name, _, width, _ in MODELS}
    for name, sprite, width, piece in MODELS:
        if only is not None and name not in only:
            continue
        k.reset()
        parts = build_model(name, sprite, width, piece)
        bpy.context.view_layer.update()
        print(f"== {name} (shots {sprite}): the {width} beam's {piece}; top {tops[name]:.3f}, "
              f"height={heights[name]:g}; "
              f"faces up/down/sideways {facing(parts)}")
        if "check" in options:
            kit.check_lines(name, parts, os.path.join(options["check"], "shots.png"), [(sprite, 0, 0, 0)],
                            (WIDTHS[width]["x"], 2.0 if piece == "head" else 0.0))
        bpy.context.scene.view_settings.view_transform = "Standard"
        mk.report(name, parts, os.path.join(outdir, name + ".glb"))
        if "preview" in options:
            view(options["preview"] + name, parts)
    if "preview" in options and only is None:
        volleys_view(options["preview"], heights)


if __name__ == "__main__":
    build()
