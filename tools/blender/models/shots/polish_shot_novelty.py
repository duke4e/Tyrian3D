"""The sidekicks' and specials' odd shots (shots sheet sprites 28, 23, 24, 25 and 26; shots2 sheet sprites 155-162, 110,
111, 129 and 130; all 1x1: 12 x 14 cells), modelled (2026-10-30, round 4 of the shots' models: until then each was drawn
as its sprite with volume and the automatic glow, 13 pixels at 0.7 in the sprite's brightest colour). Objects, not
energy: built with polish_shot_ordnance.py's kit (half-bodies on the colours' borders, palette materials) and Batch AS's
shapes (shot_kit.py: puffed outlines, tubes, spheres).

Who fires them (weapons as the item data numbers them; sidekicks by their shop ids, specials by their item ids):
- 28: the Beno Protron System -B- sidekick (28, sold only in shop 4:17, on the right; unlimited), weapon 737: this disc
  a volley (with four of the Protron's blue pearls, 247, already modelled), flying up at 2 pixels a frame and homing on
  the nearest enemy (aim 7); in episodes 4 and 5 its sprite number carries 9000, so it also sheds blue sparkles.
- 23, 24, 25, 26: the Bubble Gum-Gun sidekick (31, shop 5:2; ammo 80), weapon 792: one gum ball every 2 frames, the
  eight positions of its record taking 23, 24, 25, 26, 23 ... in turn (orange, mauve, pink, blue), each flying its own
  way (a pixel or two a frame) and wobbling in a small ellipse as it goes (circlesize 88).
- shots2 155-162: the Flying Punch sidekick (32, sold in no shop; reached with TYR3D_SIDEKICKS=32), weapon 794: one fist
  a volley in five shots that the game moves together, accelerating up the screen and flying on through what they hit
  (damage 251): four 12 x 14 pieces 6 pixels out to either side and 7 up or down (155/156 above left, 157/158 above
  right, 159/160 below left, 161/162 below right; two frames each, a frame each) and a fifth piece in the middle 7 below
  (shots2 163/164, the People Pretzels' pretzel, as the data has it: it keeps its pretzel lines).
- shots2 110, 111, 129, 130: the Super Pretzel special (47; Super Arcade's Pretzel Pete fires it), weapon 1024: one big
  pretzel in four pieces moved together (110 above left, 111 above right, 129 below left, 130 below right, 6 out and 7
  up or down), flying up at 5 pixels a frame through what it hits (damage 251), one every 150 frames.

As the sprites draw them (palette indices):
- 28: a disc 12 pixels across: a rim of pale icy cyan (ramp 13, 0xd2-0xde: brightest at its lower right outside and at
  the top inside, dark at its left) round a green panel (ramp 12, 0xc0-0xc6) whose middle draws a crosshair: a pale
  upright bar (0xde, 0xdd, 0xd9) broken by a bright green row (0xc6).
- 23-26: one gum ball (11 pixels across, its middle at x = -0.5, y = -0.5) in four colours: orange (ramp 7, 0x79 with
  0x7a-0x7d towards its upper right, 0x74-0x77 round its lower left), mauve (ramp 5, 0x5b), pink (ramp 4, 0x4b), blue
  (ramp 3, 0x3b), a dark outline (shade 0 or 2) round each.
- the fist (the four pieces together, 24 x 28): a red glove (ramp 7, 0x72-0x79) flying up the screen, 12 pixels wide, a
  thumb rising at its upper left, its fingers bulging to the right, a dark wrist (rows 19-21) and below it a jet of fire
  (rows 22-27, 0x7a 0x7b at its hottest in the first frame, 0x79 0x7a in the second: the frames differ only there).
- the Super Pretzel (24 x 28): a pretzel of dough-brown rope (ramp 11, 0xb7 0xb8, salt 0xba-0xbd, shadows 0xb3-0xb5)
  3 pixels thick: two lobes on top (a heart's outline down to its point at the bottom), its ends twisted together in the
  middle above and fanning out down to the heart's lower sides.

The models (as the sprites draw them; built on z = 0; the disc, the fist and the pretzel leant towards the camera as
polish_shot_ordnance.LEAN says, so that the slanted camera sees them laid out as the sprites draw them; the gum balls
stand upright: leant, a plain ball read as a flat button):
- shot_benob (28): a disc: an icy glass ring, round on top (0xd8, a brighter crescent of 0xdb on its outer slope from
  its right round to its bottom, where the sprite brightens: the light through the glass; glowing 0.3-0.4), round a
  green lens (0xc3 round 0xc6, glowing 0.45-0.55) with a raised crosshair (an upright pale bar, 0xdd, a level one in the
  lens's green). 5 materials.
- shot_gum (23), shot_gum_mauve (24), shot_gum_pink (25), shot_gum_blue (26): a glossy gum ball flattened underneath,
  its shell in rings round the vertical: a top a shade lighter, the colour, a foot two or three shades darker (each
  glowing a little in its own colour: a ball reads black from the slanted camera otherwise); the sun gives the glint.
- the fist (shot_punch_b155, _b157, _b159, _b160, _b161, _b162): a red boxing glove built whole: a padded mitt (a puffed
  outline of the sprite's), a thumb along its upper left, the knuckles' creases, a dark cuff (a half-ring), and a jet of
  fire out of the cuff (half-cones, 0x78 round 0x7b in the first frame, 0x77 round 0x79 in the second); cut into the
  four sprites' pieces (polish_machine_kit.cut: the pieces keep the whole's shading across the cuts), each moved so that
  its sprite's centre is its origin; the top pieces serve both frames. Its lines' height= sets the glove a little above
  the player's layer, over the People Pretzels' pretzel the data puts under its wrist (the 2D game paints the fist over
  it).
- the Super Pretzel (shot_superpretzel_b110, _b111, _b129, _b130): one rope (a tube along the sprite's path, thicker
  round the belly, lifted where it crosses itself and where its ends lie on the belly) of baked dough (0xb9: a shade
  lighter than the sprite's 0xb7 0xb8, glossy and glowing a little, as 0xb8 read olive grey in the game) with a pale
  split along the belly (0xbc) and coarse salt (0xbe); cut into the four sprites' pieces as the fist.
The pieces' model lines take origin (drawn at their own origin, not each centred on its own bounds); the Super Pretzel's
shot lines height= half the whole's height down, so the whole is centred on the player's layer as the other shots are.
Glow (glow= replaces the automatic glow): the disc's lens green, the gum balls a small halo in their colour, the fist's
fire on the lower left piece (the others a faint one), the pretzel's pieces a faint warm one.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; a 1x1 sprite's
origin at its centre (pixel 6, 7 of the cell); the four-piece objects are built round the pieces' shared corner (column
c, row r of the 24 x 28 whole: x = c + 0.5 - 12, y = 13.5 - r), each piece moved onto its own sprite's centre.

Triangles: 960 (the disc, 5 materials), 288 (each gum ball, 3), the fist's pieces 358-958 (2-6 materials; 1 706 the
whole), the pretzel's 1 036-1 172 (2-3; 3 600 the whole).

models.cfg: --cfg <file> writes the block (MODELS, GROUPS and TITLE below: the model lines, the shot lines).

Run: Blender -b --factory-startup -P tools/blender/models/shots/polish_shot_novelty.py -- [--only <name,...>]
     [--outdir <dir>] (default assets/models/shots) [--check <sheets dir>] (each model's top view against its sprite(s)
     in <dir>/shots.png and shots2.png, from TYR3D_EXTRACT; the whole fist and pretzel against the four sprites)
     [--preview <prefix>] (top, three-quarter and game-camera views; the wholes too) [--cfg <file>]
"""
import math
import os
import random
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_shot_ordnance as po  # noqa: E402  (the kit: materials, half-bodies, the build loop)
from polish_shot_ordnance import k, mk, s, pal, finish, half_revolve, flame, triangulate, view  # noqa: E402
from polish_shot_ordnance import Model, lean  # noqa: E402
from polish_shot_ordnance import LEAN, upright_copies, remove_copies  # noqa: E402


# === The Beno Protron System -B-'s disc (28) ==========================================================================

BB_MAJOR, BB_MINOR, BB_SQUASH = 4.35, 1.65, 0.8  # the ring: its middle line's radius, its section's, its height
BB_SEGMENTS, BB_SIDES = 36, 8  # round it (10 degrees each: the crescent's ends lie on them), over its section
BB_CRESCENT = (-110.0, 10.0)  # where its outer slope brightens (degrees, counter-clockwise from +X): right to bottom
BB_LENS = (2.85, 1.55)  # the lens's radius and height


def ring(name, mats):
    """The icy ring, round on top and flat underneath: faces between its rounds (every 10 degrees) and its section's
    points (outside, over the top, inside); the outer half of the section takes the crescent where the sprite's rim
    brightens."""
    main, bright = mats
    verts, faces, face_mats = [], [], []
    for i in range(BB_SEGMENTS):
        phi = 2 * math.pi * i / BB_SEGMENTS
        for j in range(BB_SIDES + 1):
            th = math.pi * j / BB_SIDES
            r = BB_MAJOR + BB_MINOR * math.cos(th)
            verts.append((r * math.cos(phi), r * math.sin(phi), BB_MINOR * BB_SQUASH * math.sin(th)))
    n = BB_SIDES + 1
    lo, hi = (math.radians(a) for a in BB_CRESCENT)
    for i in range(BB_SEGMENTS):
        a, b = i * n, ((i + 1) % BB_SEGMENTS) * n
        phi = 2 * math.pi * (i + 0.5) / BB_SEGMENTS
        phi_s = phi - 2 * math.pi if phi > math.pi else phi
        for j in range(BB_SIDES):
            faces.append((a + j, b + j, b + j + 1, a + j + 1))
            outer = j < BB_SIDES // 2
            face_mats.append(bright if outer and lo <= phi_s <= hi else main)
        faces.append((a + n - 1, b + n - 1, b, a))  # the flat underside
        face_mats.append(main)
    return finish(name, verts, faces, face_mats, 70)


def dome_z(name, centre, radius, height, bands, segments=24, angle=70.0, rings_per_band=2):
    """A dome over (centre) round the vertical, flat underneath: bands [(from polar angle in degrees, material)], the
    first from the top (0) and the last ending at the rim (90); rings_per_band rings in each (the bands' borders are
    rings of the mesh)."""
    cx, cy = centre
    thetas = []
    for i, (t0, _) in enumerate(bands):
        t1 = bands[i + 1][0] if i + 1 < len(bands) else 90.0
        for kk in range(rings_per_band):
            thetas.append(t0 + (t1 - t0) * kk / rings_per_band)
    thetas.append(90.0)
    thetas = thetas[1:]  # the top is a point
    verts = [(cx, cy, height)]
    for t in thetas:
        th = math.radians(t)
        for j in range(segments):
            ph = 2 * math.pi * j / segments
            verts.append((cx + radius * math.sin(th) * math.cos(ph), cy + radius * math.sin(th) * math.sin(ph),
                          height * math.cos(th)))
    verts.append((cx, cy, 0.0))
    bottom = len(verts) - 1

    def band(t):
        m = bands[0][1]
        for t0, mat in bands:
            if t >= t0 - 1e-6:
                m = mat
        return m
    faces, mats = [], []
    for j in range(segments):
        faces.append((0, 1 + j, 1 + (j + 1) % segments))
        mats.append(band(thetas[0] / 2))
    for i in range(len(thetas) - 1):
        a, b = 1 + i * segments, 1 + (i + 1) * segments
        m = band((thetas[i] + thetas[i + 1]) / 2)
        for j in range(segments):
            jj = (j + 1) % segments
            faces.append((a + j, b + j, b + jj, a + jj))
            mats.append(m)
    last = 1 + (len(thetas) - 1) * segments
    for j in range(segments):
        faces.append((last + (j + 1) % segments, last + j, bottom))
        mats.append(bands[-1][1])
    return finish(name, verts, faces, mats, angle)


def surface_z(objects, x, y):
    """The height of the objects' top surface at (x, y) (a ray cast down), or None."""
    best = None
    for obj in objects:
        bvh = BVHTree.FromPolygons([v.co for v in obj.data.vertices], [p.vertices[:] for p in obj.data.polygons])
        hit = bvh.ray_cast(Vector((x, y, 50.0)), Vector((0.0, 0.0, -1.0)))
        if hit[0] is not None and (best is None or hit[0].z > best):
            best = hit[0].z
    return best


def ridge(name, host, points, radius, mat, lift=0.12, squash=0.6, segments=6):
    """A thin ridge laid on a host's top surface along points [(x, y)]: a tube following the surface, lift above it."""
    pts = []
    for x, y in points:
        z = surface_z(host, x, y)
        pts.append((x, y, (z if z is not None else 0.0) + lift))
    return s.tube(name, pts, radius, mat, segments, squash=squash)


def benob():
    ice, crescent = pal("bb_ice", 0xd8, 0.3, 0.25, 0.1), pal("bb_ice", 0xdb, 0.4, 0.25, 0.1)
    pale = pal("bb_bar", 0xdd, 0.5, 0.3)
    rim, lens = pal("bb_lens", 0xc3, 0.45, 0.3), pal("bb_lens", 0xc6, 0.55, 0.25)
    parts = [ring("bb_ring", (ice, crescent))]
    r, h = BB_LENS
    glass = dome_z("bb_lens", (0.0, 0.0), r, h, [(0.0, lens), (62.0, rim)], segments=24)
    parts.append(glass)
    # The crosshair on the lens: an upright pale bar (the sprite's columns 5-6) and a level green one (its row 6).
    parts.append(ridge("bb_bar_v", [glass], [(0.0, y) for y in (-2.3, -1.2, 0.0, 1.2, 2.3)], 0.38, pale))
    parts.append(ridge("bb_bar_h", [glass], [(x, 0.5) for x in (-2.3, -1.2, 0.0, 1.2, 2.3)], 0.3, lens, lift=0.08))
    return lean(parts)


# === The Bubble Gum-Gun's gum balls (23-26) ===========================================================================

GUM_CENTRE, GUM_RADIUS, GUM_HEIGHT = (-0.5, -0.5), 5.25, 4.85
# Each colour: (top, body, foot) palette indices, glows; the sprite's.
GUM = {"shot_gum": ((0x7a, 0x79, 0x76), (0.38, 0.33, 0.26)),
       "shot_gum_mauve": ((0x5c, 0x5b, 0x58), (0.38, 0.33, 0.26)),
       "shot_gum_pink": ((0x4c, 0x4b, 0x48), (0.38, 0.33, 0.26)),
       "shot_gum_blue": ((0x3c, 0x3b, 0x38), (0.38, 0.33, 0.26))}
GUM_BANDS = (0.0, 24.0, 72.0)  # where the top, the colour and the foot begin (degrees from the top)


def gum(name):
    (top, body, foot), (et, eb, ef) = GUM[name]
    mats = [pal("gum", top, et, 0.2), pal("gum", body, eb, 0.22), pal("gum", foot, ef, 0.3)]
    return [dome_z("gum_ball", GUM_CENTRE, GUM_RADIUS, GUM_HEIGHT, list(zip(GUM_BANDS, mats)), segments=24)]


# === The Flying Punch's fist (shots2 155-162) =========================================================================

# The pieces: (sprite, the box of the whole it shows (x0, x1, y0, y1), its sprite's centre in the whole).
PUNCH_PIECES = [(155, (-12.0, 0.0, 0.0, 14.0), (-6.0, 7.0)), (157, (0.0, 12.0, 0.0, 14.0), (6.0, 7.0)),
                (159, (-12.0, 0.0, -14.0, 0.0), (-6.0, -7.0)), (161, (0.0, 12.0, -14.0, 0.0), (6.0, -7.0))]
# The mitt's outline (the whole's coordinates), from the top of its knuckles clockwise round the fingers' bulge, down to
# the wrist and up its left side under the thumb.
MITT = [(-1.6, 6.75), (0.4, 7.05), (2.3, 6.45), (3.9, 5.2), (5.15, 3.55), (5.75, 1.6), (5.55, -0.6), (5.05, -2.8),
        (4.15, -4.6), (2.9, -5.9), (0.6, -6.5), (-2.2, -6.5), (-4.7, -6.0), (-5.75, -4.3), (-5.95, -1.6), (-5.8, 1.2),
        (-5.25, 3.4), (-4.2, 5.1), (-2.9, 6.2)]
MITT_HEIGHT = 5.4
THUMB = [(-4.75, 0.2, 2.9), (-4.9, 2.4, 3.55), (-4.65, 4.5, 3.85), (-4.15, 6.3, 3.7), (-3.65, 7.6, 3.1),
         (-3.45, 8.2, 2.5)]
CUFF = (-1.9, -8.0, -5.35, 4.2)  # its axis x, its bottom and top y, its radius
FIRE = (-1.9, -8.0, -13.9, 3.5)  # the jet: its axis x, its root and tip y, its root's radius
# The frames' fire: (outer index, glow), (core index, glow).
PUNCH_FIRE = {0: ((0x78, 0.5), (0x7b, 0.6)), 1: ((0x77, 0.45), (0x79, 0.55))}


def glove(frame):
    leather, light = pal("pu_leather", 0x76, 0.1, 0.42), pal("pu_leather", 0x78, 0.12, 0.38)
    crease, cuff_m = pal("pu_crease", 0x72, 0.0, 0.5), pal("pu_cuff", 0x74, 0.06, 0.45)
    (oi, oe), (ci, ce) = PUNCH_FIRE[frame]
    outer, core = pal("pu_fire", oi, oe, 0.5), pal("pu_fire", ci, ce, 0.45)
    mitt = s.puff("pu_mitt", s.smooth_outline(MITT, step=0.7), 0.0, MITT_HEIGHT, leather, side=0.18, steps=6,
                  power=2.3)
    parts = [mitt]
    # The thumb along the upper left, standing out of the mitt.
    parts.append(s.tube("pu_thumb", s.catmull(THUMB, 0.6), [1.3, 1.55, 1.6, 1.52, 1.35, 1.05], light, 10,
                        squash=0.8))
    # The knuckles' creases: where the fingers fold (the sprite's dark column 12 and row 12) and between the fingers.
    parts.append(crease_ridge("pu_crease", [mitt], [(0.9, 4.3), (0.75, 2.2), (0.55, 0.0), (0.4, -2.3), (0.6, -4.2)],
                              0.28, crease))
    for y0 in (3.1, 0.9, -1.3):
        parts.append(crease_ridge("pu_finger", [mitt],
                                  [(0.7, y0), (2.4, y0 + 0.15), (4.0, y0 - 0.05), (5.0, y0 - 0.35)], 0.22, crease))
    # The cuff: a dark half-ring round the wrist with a lighter band.
    x, y0, y1, r = CUFF
    parts.append(half_revolve("pu_cuff", [(y0, r * 0.92, crease), (y0 + 0.35, r, cuff_m), (y1 - 0.5, r, crease),
                                          (y1 - 0.15, r * 0.97, crease), (y1, r * 0.9, crease)], x=x, segments=12,
                              squash=0.95))
    x, root, tip, rr = FIRE
    parts += flame("pu_fire", x, root + 0.1, tip, rr, outer, core)
    return lean(parts)


def crease_ridge(name, host, points, radius, mat):
    return ridge(name, host, points, radius, mat, lift=0.0, squash=0.5)


# === The Super Pretzel (shots2 110, 111, 129, 130) ====================================================================

SP_PIECES = [(110, (-12.0, 0.0, 0.0, 14.0), (-6.0, 7.0)), (111, (0.0, 12.0, 0.0, 14.0), (6.0, 7.0)),
             (129, (-12.0, 0.0, -14.0, 0.0), (-6.0, -7.0)), (130, (0.0, 12.0, -14.0, 0.0), (6.0, -7.0))]
# The rope from its left end (lying on the belly's lower left) up through the twist into the right lobe, round the belly
# to the left lobe, down through the twist again to its right end: (x, y, z) of its middle line; z lifts the strand that
# crosses over the other and the ends where they lie on the belly.
SP_ROPE = [(-5.15, -4.33, 2.6), (-3.75, -3.32, 2.2), (-2.55, -1.75, 1.7), (-1.75, -0.09, 1.55), (-0.95, 1.67, 1.7),
           (-0.45, 3.42, 2.55), (0.55, 5.18, 2.4), (1.1, 6.74, 1.75), (1.9, 8.31, 1.5), (3.3, 9.38, 1.45),
           (5.3, 9.65, 1.45), (7.4, 9.19, 1.45), (9.05, 7.85, 1.45), (9.8, 5.73, 1.5), (9.85, 3.05, 1.5),
           (9.4, 0.47, 1.55), (8.7, -2.02, 1.6), (7.6, -4.15, 1.65), (6.2, -5.99, 1.7), (4.6, -7.75, 1.75),
           (2.8, -9.22, 1.8), (0.9, -10.19, 1.8), (-0.9, -10.19, 1.8), (-2.8, -9.22, 1.8), (-4.6, -7.75, 1.75),
           (-6.2, -5.99, 1.7), (-7.6, -4.15, 1.65), (-8.7, -2.02, 1.6), (-9.4, 0.47, 1.55), (-9.85, 3.05, 1.5),
           (-9.8, 5.73, 1.5), (-9.05, 7.85, 1.45), (-7.4, 9.19, 1.45), (-5.3, 9.65, 1.45), (-3.3, 9.38, 1.45),
           (-1.9, 8.31, 1.5), (-1.1, 6.74, 1.6), (-0.4, 4.9, 1.3), (0.55, 3.33, 1.25), (1.95, 1.67, 1.55),
           (2.75, -0.09, 1.55), (3.55, -1.75, 1.7), (4.75, -3.32, 2.2), (6.15, -4.33, 2.6)]
# Its thickness along it (radii at evenly spaced points from end to end): the ends thinner, the belly thickest.
SP_RADII = [0.95, 1.1, 1.25, 1.38, 1.42, 1.5, 1.62, 1.72, 1.78, 1.78, 1.72, 1.62, 1.5, 1.42, 1.38, 1.25, 1.1, 0.95]
SP_SPLIT = (17, 27)  # the rope's points between which the belly's pale split runs (its bottom arc)
SP_SALT = 22


def superpretzel():
    dough, split = pal("sp_dough", 0xb9, 0.12, 0.3), pal("sp_split", 0xbc, 0.15, 0.45)
    salt = pal("sp_salt", 0xbe, 0.15, 0.5)
    pts = s.catmull([Vector(p) for p in SP_ROPE], 0.75)
    n = len(pts)
    rope = s.tube("sp_rope", pts, SP_RADII, dough, 10, smooth_angle=60, squash=0.88)
    parts = [rope]
    # The pale split along the belly's top: a flat ridge on the rope's crown.
    a = s.catmull([Vector(p) for p in SP_ROPE[:SP_SPLIT[0] + 1]], 0.75)
    b = s.catmull([Vector(p) for p in SP_ROPE[:SP_SPLIT[1] + 1]], 0.75)
    i0, i1 = len(a) - 1, len(b) - 1
    crown = []
    for i in range(i0, i1 + 1):
        t = i / max(n - 1, 1) * (len(SP_RADII) - 1)
        j = min(int(t), len(SP_RADII) - 2)
        r = SP_RADII[j] + (SP_RADII[j + 1] - SP_RADII[j]) * (t - j)
        crown.append(pts[i] + Vector((0.0, 0.0, r * 0.88 - 0.12)))
    parts.append(s.tube("sp_split", crown, [0.12, 0.42, 0.5, 0.5, 0.42, 0.12], split, 6, squash=0.35))
    # Coarse salt on top: small tilted cubes on the rope's crown, spread along it.
    rng = random.Random(29)
    for kk in range(SP_SALT):
        i = int((kk + 0.5) / SP_SALT * (n - 6)) + 3
        t = i / max(n - 1, 1) * (len(SP_RADII) - 1)
        j = min(int(t), len(SP_RADII) - 2)
        r = SP_RADII[j] + (SP_RADII[j + 1] - SP_RADII[j]) * (t - j)
        side = rng.uniform(-0.55, 0.55)
        tangent = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized()
        across = tangent.cross(Vector((0, 0, 1))).normalized()
        p = pts[i] + across * side * r + Vector((0, 0, r * 0.88 * math.sqrt(max(0.0, 1 - side * side)) - 0.05))
        cube = k.box("sp_salt", (0, 0, 0), (0.55, 0.55, 0.45), salt)
        cube.data.transform(Matrix.Translation(p) @ Matrix.Rotation(rng.uniform(0, 3.14), 4, "Z") @
                            Matrix.Rotation(rng.uniform(-0.5, 0.5), 4, "X"))
        parts.append(cube)
    return lean(parts)


# === Cutting a whole into the sprites' pieces =========================================================================

def cut_pieces(whole, pieces, cap):
    """The whole cut into the sprites' pieces, each moved so that its sprite's centre is its origin: {sprite: [objects]}
    (polish_machine_kit.cut: each piece keeps the whole's shading across the cuts; the cuts closed in cap)."""
    out = {}
    for sprite, box, (cx, cy) in pieces:
        parts = []
        for obj in whole:
            piece = mk.cut(obj, box, cap)
            if piece is None:
                continue
            piece.data.transform(Matrix.Translation((-cx, -cy, 0.0)))
            piece.name = "%s_b%d" % (obj.name, sprite)
            parts.append(piece)
        out[sprite] = triangulate(parts)
    return out


def check_whole(label, whole, sheets, pieces):
    """The whole's top view (24 x 28) against the four sprites put together, and each piece's against its sprite."""
    m = [[False] * 24 for _ in range(28)]
    for sprite, box, (cx, cy) in pieces:
        mask = k.sprite_mask(os.path.join(sheets, "shots2.png"), sprite, large=False)
        c0, r0 = int(cx - 6 + 12), int(14 - (cy + 7))
        for r in range(14):
            for c in range(12):
                m[r0 + r][c0 + c] = m[r0 + r][c0 + c] or mask[r][c]
    upright = upright_copies(whole)
    mk.compare(label, mk.coverage(upright, 24, 28), m)
    remove_copies(upright)


def build_pieces(name_of, pieces, make, sheets, label, cap_of):
    """make() -> the whole's objects; returns {model name: objects} for the pieces (name_of(sprite))."""
    whole = triangulate(make())
    bpy.context.view_layer.update()
    low, high = mk.bounds(whole)
    print("%s whole: %d triangles, z %.2f..%.2f (centred on the layer by height=%.2f)" % (
        label, mk.triangles(whole), low.z, high.z, -(low.z + high.z) / 2))
    if sheets:
        check_whole(label + " whole", whole, sheets, pieces)
    if PREVIEW_WHOLE:
        bpy.context.scene.view_settings.view_transform = "Standard"
        view(PREVIEW_WHOLE + label + "_whole", whole, size=(24, 28))
    cut = cut_pieces(whole, pieces, cap_of(whole))
    for o in whole:
        bpy.data.objects.remove(o)
    out = {}
    for sprite, parts in cut.items():
        out[name_of(sprite)] = parts
        if sheets:
            upright = upright_copies(parts)
            mk.compare("%s (shots2 %d)" % (name_of(sprite), sprite), mk.coverage(upright, 12, 14),
                       k.sprite_mask(os.path.join(sheets, "shots2.png"), sprite, large=False))
            remove_copies(upright)
    return out


PREVIEW_WHOLE = None


def material_named(objects, prefix):
    for o in objects:
        for m in o.data.materials:
            if m is not None and m.name.startswith(prefix):
                return m
    return None


def punch_pieces(sheets):
    out = {}
    for frame in (0, 1):
        names = {155: "shot_punch_b155", 157: "shot_punch_b157", 159: "shot_punch_b%d" % (159 + frame),
                 161: "shot_punch_b%d" % (161 + frame)}
        got = build_pieces(lambda sp: names[sp], PUNCH_PIECES, lambda: glove(frame), sheets, "punch_f%d" % frame,
                           lambda whole: material_named(whole, "pu_leather_76"))
        for name, parts in got.items():
            if frame == 1 and name in ("shot_punch_b155", "shot_punch_b157"):
                for o in parts:  # (the top pieces are the same in both frames: the first frame's are kept)
                    bpy.data.objects.remove(o)
                continue
            out[name] = parts
    return out


def pretzel_pieces(sheets):
    return build_pieces(lambda sp: "shot_superpretzel_b%d" % sp, SP_PIECES, superpretzel, sheets, "superpretzel",
                        lambda whole: material_named(whole, "sp_dough"))


# === The block ========================================================================================================

PUNCH_H = "height=-1.2"
SP_H = "height=-2"
MODELS = [
    Model("shot_benob", [("shots", 28, "glow=10:0.35:198:0:0", "Beno Protron System -B- (sidekick 28, weapon 737)")],
          benob, "an icy glass ring round a green lens with a crosshair", ("shots", 28), leant=LEAN),
    Model("shot_gum", [("shots", 23, "glow=9:0.25:123:-0.5:0.5", "Bubble Gum-Gun (sidekick 31, weapon 792): orange")],
          lambda: gum("shot_gum"), "an orange gum ball", ("shots", 23)),
    Model("shot_gum_mauve", [("shots", 24, "glow=9:0.25:93:-0.5:0.5", "... mauve")],
          lambda: gum("shot_gum_mauve"), "a mauve gum ball", ("shots", 24)),
    Model("shot_gum_pink", [("shots", 25, "glow=9:0.25:77:-0.5:0.5", "... pink")],
          lambda: gum("shot_gum_pink"), "a pink gum ball", ("shots", 25)),
    Model("shot_gum_blue", [("shots", 26, "glow=9:0.25:61:-0.5:0.5", "... blue")],
          lambda: gum("shot_gum_blue"), "a blue gum ball", ("shots", 26)),
    Model("shot_punch_b155", [("shots2", 155, PUNCH_H + " glow=6:0.1:120:3:3",
                               "Flying Punch (sidekick 32, weapon 794): the fist above left"),
                              ("shots2", 156, PUNCH_H + " glow=6:0.1:120:3:3", "... (its second frame)")],
          None, "the fist above left (both frames)", origin=True),
    Model("shot_punch_b157", [("shots2", 157, PUNCH_H + " glow=6:0.1:120:-3:3", "... above right"),
                              ("shots2", 158, PUNCH_H + " glow=6:0.1:120:-3:3", "... (its second frame)")],
          None, "the fist above right (both frames)", origin=True),
    Model("shot_punch_b159", [("shots2", 159, PUNCH_H + " glow=10:0.4:122:4.1:3.5", "... below left, the fire")],
          None, "the fist below left, the cuff and the fire (first frame)", origin=True),
    Model("shot_punch_b160", [("shots2", 160, PUNCH_H + " glow=10:0.34:121:4.1:3.5", "... (its second frame)")],
          None, "the fist below left, the cuff and the fire (second frame)", origin=True),
    Model("shot_punch_b161", [("shots2", 161, PUNCH_H + " glow=6:0.1:120:-3:-3", "... below right")],
          None, "the fist below right (first frame)", origin=True),
    Model("shot_punch_b162", [("shots2", 162, PUNCH_H + " glow=6:0.1:120:-3:-3", "... (its second frame)")],
          None, "the fist below right (second frame)", origin=True),
    Model("shot_superpretzel_b110", [("shots2", 110, SP_H + " glow=8:0.1:187:3:3",
                                      "Super Pretzel (special 47, weapon 1024): above left")],
          None, "the Super Pretzel above left", origin=True),
    Model("shot_superpretzel_b111", [("shots2", 111, SP_H + " glow=8:0.1:187:-3:3", "... above right")],
          None, "the Super Pretzel above right", origin=True),
    Model("shot_superpretzel_b129", [("shots2", 129, SP_H + " glow=8:0.1:187:3:-3", "... below left")],
          None, "the Super Pretzel below left", origin=True),
    Model("shot_superpretzel_b130", [("shots2", 130, SP_H + " glow=8:0.1:187:-3:-3", "... below right")],
          None, "the Super Pretzel below right", origin=True),
]
GROUPS = [(["shot_punch_b155", "shot_punch_b157", "shot_punch_b159", "shot_punch_b160", "shot_punch_b161",
            "shot_punch_b162"], punch_pieces),
          (["shot_superpretzel_b110", "shot_superpretzel_b111", "shot_superpretzel_b129", "shot_superpretzel_b130"],
           pretzel_pieces)]

TITLE = [
    "The sidekicks' and specials' odd shots (tools/blender/models/shots/polish_shot_novelty.py): the Beno Protron",
    "System -B-'s disc, an icy glass ring round a green lens with a crosshair (28); the Bubble Gum-Gun's gum balls,",
    "glossy, in four colours (23 24 25 26); the Flying Punch's red boxing glove with a jet of fire out of its cuff,",
    "built whole and cut into the four sprites the game moves together (155/156 157/158 above, 159/160 161/162",
    "below: the fire's two frames); the Super Pretzel, a big salted pretzel built whole and cut into its four",
    "sprites (110 111 above, 129 130 below). The pieces are drawn at their own origin (origin), the pretzel's",
    "lowered half its height (height=-2) so that it is centred on the player's layer; the glove's less",
    "(height=-1.2), so that it sits over the fifth piece the data puts under its wrist (shots2 163/164, the People",
    "Pretzels' pretzel, which keeps its lines), as the 2D game paints the fist over it. Round ones lean towards the",
    "camera (the disc, the fist, the pretzel), so that the slanted camera sees them laid out as the sprites draw",
    "them.",
]


if __name__ == "__main__":
    options = k.args()
    PREVIEW_WHOLE = options.get("preview")
    po.run(MODELS, GROUPS, TITLE)
