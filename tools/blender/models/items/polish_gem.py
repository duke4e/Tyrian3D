"""Gem (the coins sheet's sprites 14, 32 and 51: the red, green and blue gems of 250, 100 and 500 credits; 1x1,
12 x 14 pixels; about 1170 of them in the levels, the item seen most after the purple ball), polished (2026-10-20;
it replaces gem.py's lumpy octagonal stone). models.cfg: sprite coins 14/32/51 gem yaw=frames:64 color=sprite
glow=15:0.3, and the sparkle's frames as frame models (below).

The three gems are one picture in three ramps, shade for shade: 14 in ramp 7 (red-orange), 32 in ramp 2 (green),
51 in ramp 3 (blue). Each sparkles in five frames (14 15 16 17 18 17 16 15, two game frames each; 32-36 and 51-55
likewise), every pixel of the next frame one shade lighter than the last: 18 is 14 four shades lighter. No other
enemy shows these sprites.

As the sprite and its 4x upscales draw it: a cut stone seen from above, its outline a square on its corner (11 x 11
pixels: columns 1-11, rows 2-12, its corners blunt, three pixels wide), a bright cross from its middle to its
four corners (the ridges of a pyramid seen from above), a bright point in the middle, a lighter line a pixel
inside its upper edges, its upper left lighter than its lower right, a dark rim.

Built as a square cut (a princess cut turned on its corner) from planes, every facet flat (polish_item_kit.
convex): the girdle (short walls round the outline, its blunt corners too); above it the crown: a steep band
round the outline (the lighter line inside the edges), the bezel facets, each side's ground as two halves meeting
in a shallow ridge (so a turning gem flashes twice a side), the ridges where two sides' bezels meet over the
corners ground into narrow facets running from the table down to the outline's corners (the cross), a ring of
eight shallow star facets round the table (tilted about 15 degrees, so as the gem turns each catches the game's
sun towards its camera in turn: the glints) and the table (the bright middle); below it the pavilion, eight
facets to a point. The facets are painted in shades as the sprite's (the table and cross brightest, the bezels
darker, the girdle dark), lighter towards the middle (the crown is cut along two diamond-shaped rings for it),
glossy and a little metallic so that their highlights take the gem's colour; the game's light does the rest.

The materials are palette shades of ramp 0 without emission (polish_item_kit): color=sprite gives them the
frame's ramp. Models of the sparkle's frames are the same gem lighter, more gently than the sprites (the model
starts a shade lighter than 14 already): gem_15 a shade, gem_16 two (for 16 and 17), gem_18 three (models.cfg
frame coins 15 gem_15, 16 gem_16, 17 gem_16, 18 gem_18, and likewise 33-36 and 52-55); all span the same
bounds.

The gem is centred on the origin (the sprite's centre, pixel (6, 7)), half a pixel left of and above its drawn
middle, so that it turns in place (yaw=frames: a quarter turn per sparkle; it looks the same every quarter
turn). Its girdle's middle is at z = 0, its table at z = TABLE_Z, its point at z = -PAVILION_Z.

Options after "--": --outdir <dir> (default assets/models/items), --check <sheets dir> (the silhouette against
coins.png), --preview <prefix>, --only <name,...>, --ramp <0-15> (built in that ramp, written as _r<ramp>).
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_item_kit as kit  # noqa: E402
from polish_item_kit import k  # noqa: E402

# Where the sprite draws the gem's middle (for the silhouette check).
SPRITE_CENTRE = (0.5, -0.5)
# The frames: (model, sprite, shades lighter than the first).
FRAMES = [("gem", 14, 0), ("gem_15", 15, 1), ("gem_16", 16, 2), ("gem_18", 18, 3)]

# The outline: the diagonal edges EDGE from the middle (|x| + |y| <= 6.5: the stairs' pixels half covered), the
# blunt corners CORNER (columns 1 and 11, rows 2 and 12); the girdle from -GIRDLE_Z to GIRDLE_Z.
EDGE = 6.5 / math.sqrt(2)
CORNER = 5.5
GIRDLE_Z = 0.2
# The crown: the steep band round the edges (BAND_SLOPE, BAND_W wide seen from above), the bezels (BEZEL_SLOPE,
# each side's two halves turned BEZEL_TURN degrees either way), the ridges over the corners ground into facets
# ARM_W wide (the cross), the star facets (STAR_SLOPE, between the cross and the bezels' middles, through the point
# STAR_AT from the axis at the table's height) and the table at TABLE_Z.
BAND_SLOPE, BAND_W = 1.6, 0.75
BEZEL_SLOPE, BEZEL_TURN = 0.62, 13.0
ARM_W = 0.55
STAR_SLOPE, STAR_AT = 0.27, 0.6
TABLE_Z = 3.2
# The pavilion: eight facets (each side's two halves turned PAVILION_TURN either way) falling to the point at
# -PAVILION_Z.
PAVILION_SLOPE, PAVILION_TURN = 1.0, 15.0
PAVILION_Z = 4.4

# The shades of the first frame (the sprite's 14, about a shade lighter: the game's light darkens what faces away
# from its sun) and the finish of each part. The crown is lighter towards its middle, as the sprite (the light
# gathering in the stone): its facets are cut along rings (diamonds, |x| + |y| = RINGS) and the parts in
# RING_SHADES take a shade for each ring from the middle out.
SHADES = {"table": 13, "star": 11, "band": 8, "girdle": 3, "pavilion": 6}
RINGS = (2.7, 4.3)
RING_SHADES = {"arm": (12, 10, 7), "bezel_a": (9, 8, 7), "bezel_b": (7, 6, 5)}
GLOSS = dict(metallic=0.25, roughness=0.1)
FINISH = {"table": dict(metallic=0.25, roughness=0.06), "girdle": dict(metallic=0.1, roughness=0.45),
          "pavilion": dict(metallic=0.2, roughness=0.18)}


def design():
    """The gem's half-spaces and what each is (its key)."""
    planes, keys = [], []

    def add(plane, key):
        planes.append(plane)
        keys.append(key)

    halves = []  # each side's bezel halves: (towards the next corner counter-clockwise, towards the last)
    for i in range(4):
        edge = 45.0 + 90.0 * i
        corner = 90.0 * i
        add(kit.wall(edge, EDGE), "girdle")
        add(kit.wall(corner, CORNER), "girdle")
        # The crown.
        a = math.radians(edge)
        foot = (EDGE * math.cos(a), EDGE * math.sin(a), GIRDLE_Z)
        add(kit.facet(edge, BAND_SLOPE, foot), "band")
        inner = EDGE - BAND_W
        top = (inner * math.cos(a), inner * math.sin(a), GIRDLE_Z + BAND_SLOPE * BAND_W)
        halves.append((kit.facet(edge + BEZEL_TURN, BEZEL_SLOPE, top), kit.facet(edge - BEZEL_TURN, BEZEL_SLOPE, top)))
        add(halves[-1][0], "bezel_a")
        add(halves[-1][1], "bezel_b")
        for star in (corner + 22.5, corner - 22.5):
            s = math.radians(star)
            add(kit.facet(star, STAR_SLOPE, (STAR_AT * math.cos(s), STAR_AT * math.sin(s), TABLE_Z)), "star")
        # The pavilion.
        low = (EDGE * math.cos(a), EDGE * math.sin(a), -GIRDLE_Z)
        add(kit.facet(edge + PAVILION_TURN, PAVILION_SLOPE, low, below=True), "pavilion")
        add(kit.facet(edge - PAVILION_TURN, PAVILION_SLOPE, low, below=True), "pavilion")
    # The cross: the ridge where two sides' bezels meet over each corner, ground into a narrow facet.
    for i in range(4):
        add(kit.chamfer(halves[i][0], halves[(i + 1) % 4][1], ARM_W), "arm")
    add(kit.flat(TABLE_Z), "table")
    add(kit.flat(-PAVILION_Z, below=True), "pavilion")
    return planes, keys


def materials(name, lift, ramp):
    """The parts' materials: {key: material}, and {key: [material per ring]} for the ringed parts. Parts of the
    same finish and shade share a material."""
    made = {}

    def mat(key, value):
        finish = key if key in FINISH else "gloss"
        s = max(0, min(15, value + lift))
        if (finish, s) not in made:
            made[finish, s] = kit.shade(f"{name}_{finish}_{s}", s, ramp, **FINISH.get(key, GLOSS))
        return made[finish, s]
    flat = {key: mat(key, v) for key, v in SHADES.items()}
    ringed = {key: [mat(key, v) for v in values] for key, values in RING_SHADES.items()}
    return flat, ringed


def build_gem(name, lift, ramp, planes, keys):
    flat, ringed = materials(name, lift, ramp)
    gem = kit.solid(name, planes, keys, dict(flat, **{key: mats[-1] for key, mats in ringed.items()}))
    kit.bands(gem, lambda p: abs(p.x) + abs(p.y) if p.z > 0 else 99.0, RINGS,
              lambda key, band: ringed[key][band] if key in ringed else None)
    kit.drop_parts(gem)
    return gem


def build():
    opts = kit.options()
    ramp, _ = kit.ramp_of(opts)
    planes, keys = design()
    for name, sprite, lift in FRAMES:
        if not kit.wanted(opts, name):
            continue
        k.reset()
        gem = build_gem(name, lift, ramp, planes, keys)
        kit.finish(opts, name, [gem], sprite, large=False, distance=0.3, shift=SPRITE_CENTRE)


if __name__ == "__main__":
    build()
