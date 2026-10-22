"""CAMANIS' boss, the flying fortress of sheet b (B in the catalogue): 23 2x2 sprites that the level events lay out as
one 120 x 140 picture, rows spawned 14 ticks apart at vy 2 (28 pixels): 2 4 6 8 at x + 12 ... x + 84 over 39 41 43 45
47 at x ... x + 96, 77-85, 115-123, 154 156 158 160 at x + 12 ... x + 84 (enemies 201-223 of episode 3; the barrels are
224 and 225 in the ground appearance). Polished 2026-10-22; it replaces wave3_ak_boss.py (reliefs inflated from the
pixels and painted pixel by pixel, 28 pixels tall) and wave1_d.py's mast_left / mast_right (b 39 and 47 modelled on
their own before batch AK cut them from the whole boss, unused since). models.cfg: model camanis_boss_<sprite>
enemies/camanis_boss_<sprite>.glb origin for the 23 pieces (unchanged), sprite b <sprite> camanis_boss_<sprite> yaw=0;
the frame and damaged models below.

Where it appears (CAMANIS only; episode 6 does not use it): t 1400, 2500 and 3700 in the sky (link 19, armor 255, at x
128, 28, 128), 5500 on the top layer (x 28) and 5700 in the sky (x 128, link 1), 5900 on the ground for the fight (x
78; its top row on ground2, all link 1, armor 255 until t 6000, then 254 and the boss bar). Every piece of one
appearance shares one link: the game kills them all when one dies and switches them all to their damaged looks when
one is hit down to dlevel 30 (tyrian2.c: the switch spreads to linked enemies with dlevel > 0), so no piece is ever shot
away on its own, and the damaged look is always the whole boss's. Ground pieces leave wrecks (leave_wreck), each piece
its own.

As the sprites and their 4x upscales draw it (the picture's columns and rows; symmetric about the middle of column 59
in coverage, 99.9 %, lit from the upper left): the hull, a wide grey bowl (columns 4-114 of rows 64-137), its deck flat
with a purple wing sloping down each flank (columns 4-17 of rows 70-118, three ribs across it at rows 84-88), ribbed
rails along the crease (columns 18-27 of rows 70-112), the gun port's housing on the deck beside each tank's bend
(columns 24-33 of rows 84-96, its hatch columns 25-31 of rows 89-94), a curved scoop sunk under it (columns 26-41 of
rows 96-107), an arc round the deck's front and panel lines, the front chamfered down to the rim (rows 129-137); the
two barrels lying in dark slots (columns 49-53 of rows 109-121) with their red lamps in sockets at the muzzles (rows
122-127) either side of a raised chin (columns 56-63 of rows 108-121). On the hull the two dark blue tanks (columns
33-52 and 66-85), glossy, running down the screen from under the engine hoods into the heart they turn into (rows
72-103): two bulging lobes over the turns (rows 72-82), a dip between them where the gap between the tanks closes
(row 74), a dark basin inside the rim, the machinery in it (a vent, a grid plate and a block, columns 51-67 of rows
82-103). On each tank a clamp of four grey plates (rows 28-44), a ribbed panel on its upper left (rows 57-71), a rail on
its inner side (column 54 of rows 43-59), a grey collar where it goes in under its hood (rows 15-19), a dark seam where
it meets the heart (row 71). The hoods (columns 21-55 of rows 0-34, mirrored): dark grey wedges, a flat top with three
red vents across its back and a grille (columns 33-48 of rows 1-13), a long chamfer down its outer side, a steep inner
flank, the front sloping down the screen into the purple skirt the tank comes out of (rows 13-33). Beside each tank a
glowing blue lamp (columns 24-31 of rows 47-69) on a purple mount. On the hull's back corners two antenna masts each
side (columns 12-18 of rows 29-81 and 1-9 of rows 45-81): a foot (the inner one a wide block), a neck, a body with a
valve on its outer side, a collar and a beaded tip.

Built as a CAD modeller would (polish_machine_kit): the hull a prism of its outline whose top and underside are cut on
a pixel grid and moved to their surfaces (the flat deck, the wing's plane, the front chamfer following the bowl, a belly
curving down to 3.4 under it), flat stretches dissolved again, its scoop, panel lines, slots and arc cut by exact
booleans; the tanks lofted superellipses (half-width 10.6, half-height 6.2, axis 4.4 over the base); the heart a
heightfield over its outline (the tanks' profile in from its rim, the basin 3 lower inside, the lobes 0.7 higher); the
hoods prisms of their plan cut by the planes of their top, front, chamfer and flank, bevelled, their vents and grille
cut in, slats in the vents; plates and ribs curved over the tanks; the masts turned about axes leaning back up the
screen (7.5 and 11.7 degrees, their tips 10 and 8.8 over the base: the sprite draws them standing up, the game's camera
then sees them where it does); the lamps half-sunk ellipsoids with a light glint at their upper left; the machinery,
the housings, the chin bevelled boxes. Faces are painted by how they face the sun (smooth bands along the light for the
tanks, the heart and the lamps). The left half's parts are built and the right's built the same way and mirrored about
x = -0.5 (each side its own: the ports and lamps differ between the frames, the damage between the sides); the hull,
the tanks, the heart, the machinery and the chin are built whole. Each look is built whole and cut along the sprites'
edges (polish_coral_manta.cut: the pieces keep the whole's shading across the cuts, their caps dark), each piece moved
so that its sprite's centre is its origin, its parts joined into one mesh and triangulated (the same output with and
without --check, run after run).

Heights: z from -3.4 (the belly) to 12.6 (the hoods' tops; tanks 10.6, heart 11.3, masts 11.6), over the layer it is
drawn on: in the sky (22 + the terrain's headroom) its hoods reach 2.6 over background 3's plane (CAMANIS' background 3
only has small grey flecks) and stay 9.4 under the player's; on the top layer the player flies through its upper parts,
as the 2D game draws the boss over the ship; on the ground (the fight) its pieces stand at their origin 4 over the
terrain (no height= needed: the belly 0.6 over the ground), the game lifting the 23 pieces onto one height, the
terrain's under their middle (render_gpu.c compute_object_lifts).

The guns' frames (animate 2: they play when the guns fire; no other enemy, launched ones included, shows these
sprites), frame models of their pieces: the left port (117; enemy 216: 117 195 233 271 197 235 273 and back) slides its
hatch towards the tank, into the housing (195: 2 pixels, 233: 4, 271: 6 with a dim red fire in the pit), then the fire
grows (197 red, 235 orange, 273 white-hot: camanis_boss_195 ... _273); the right port (121; enemy 218: 121 121 121 199
237 275 201 and back) shows only the fire growing in the dark (the sprites draw the right side in shadow and no hatch
sliding): its frames are the hatch open, the fire 199 dim, 237 red, 275 orange, 201 white-hot; the barrels (156, 158;
enemies 221, 222, 224, 225: 156 191 229 267 229 191 156) only heat their lamps: 191 and 229 are the same pixels
(camanis_boss_191 for both; camanis_boss_193 for the right's 193 and 231), 267 (269) hottest.

Its damaged look (dgr, all pieces at once): seven damaged sprites are their intact sprites' pixels unchanged (12 is 2
drawn a pixel higher; 49 = 39, 51 = 41, 53 = 43, 55 = 45, 208 = 47, 91 = 81): their sprite lines take the intact
models. The other sixteen (14 16 18, 87 89 93 246, 125 127 129 131 284, 164 166 168 170: camanis_boss_<dgr>) are the
pieces of the damaged whole, which the damaged sprites draw differently pixel by pixel (DAMAGE, below): the hull's
plating smashed in over its left (columns 13-42 of rows 69-135) and its lower right (columns 50-100 of rows 98-136),
torn and burnt, debris in the craters, embers in cracks down its right (columns 82-96 of rows 70-100) and across its
lower half; the left hood's inner flank cracked with embers (columns 47-55 of rows 8-21); the right hood burnt over its
top (columns 66-87 of rows 5-14), embers in it, its outer chamfer torn away (columns 86-91 of rows 5-16); the right
outer mast's casing blown off its core (rows 58-70), the wing's purple plating torn up between the right masts' feet;
the right tank's ribbed panel smashed; the left port and the chin shot away, the right barrel broken off, the left
rails along the crease broken. How: the map blurred into how smashed each point is, faded out towards the pieces that
keep their intact look (SEAM_FADE, so that a damaged piece meets an intact neighbour exactly); the hull's top pressed in
by it (DENT, with noise), faces charred by it (mottled black, 0x02, 0x04, 0x06); small parts shot away where it is
high; the hood's chamfer cut away by an exact boolean over the gone pixels (each run of rows its own cutter); seeded
debris chunks and ember chips (0x76 at 0.4) laid on the surface.

Materials (palette indices; at most 15 a piece): greys 0x01 0x02 0x04 0x06 0x08 0x09 0x0b; purples 0x54 0x57 0x5a; the
tanks 0x32 0x34 0x36 0x39 (emission 0.04-0.12, so the glossy blue does not read black from the game's camera) and their
glint 0x3d (0.25); the lamps 0x97 (0.32) and their glint 0x8b (0.4); the vents 0x72 (0.2); the barrels' lamps 0x76
(0.4), 0x78 (0.5), 0x7b (0.6); the ports' fire 0x72 (0.3), 0x75 (0.4), 0x78 (0.45), 0x7a (0.5) round cores 0x7c (0.55),
0x7e (0.6); the embers 0x76 (0.4).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera (z = 0 the base, on
its layer); the whole's origin is the middle of the picture (60, 70): column c's left edge is x = c - 60, row r's top
edge y = 70 - r; a piece whose sprite's top left corner is (c0, r0) has its origin at (c0 - 48, 56 - r0).

Replaces wave3_ak_boss.py (all of it: the boss is all it builds; nothing imports it) and wave3_ak_art.py (BOSS,
BOSS_DMG, BOSS_LIT: read only through wave3_ak_kit.frame() for wave3_ak_boss.py): delete both, and take frame() and
the import of wave3_ak_art out of wave3_ak_kit.py, which stays (wave3_an_kit.py and wave3_ap_kit.py use its patched,
dent, debris and pipe); and wave1_d.py's masts (its section "# --- The masts of CAMANIS": mast() and the two model()
registrations, and the docstring's mast line; models.cfg's model mast_left / mast_right lines and their GLBs).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the wholes
and of each piece against enemy_B.png), --preview <prefix> (the wholes' top and 3/4 views; --pieces 1 also each
piece's), --only <model,...> (models to export; "none": none), --whole <file.glb> (the uncut intact and damaged boss as
well, for looking at: <file>.glb and <file>_damaged.glb), --stats 1 (each piece's largest parts).
"""
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector, noise

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_coral_manta import cut  # noqa: E402  (savara's cut, the caps' material set as they are made)
from polish_k_pod import triangulate  # noqa: E402
from polish_orb_red import band_split  # noqa: E402

AX = -0.5                      # the mirror axis: the middle of the picture's column 59
LIGHT = Vector((-0.6, 0.6, 1.0)).normalized()   # towards the sun (from the upper left and above)

# The pieces: sprite, the picture's column and row of its top left corner (the 120 x 140 picture the events lay out).
CELLS = {2: (12, 0), 4: (36, 0), 6: (60, 0), 8: (84, 0),
         39: (0, 28), 41: (24, 28), 43: (48, 28), 45: (72, 28), 47: (96, 28),
         77: (0, 56), 79: (24, 56), 81: (48, 56), 83: (72, 56), 85: (96, 56),
         115: (0, 84), 117: (24, 84), 119: (48, 84), 121: (72, 84), 123: (96, 84),
         154: (12, 112), 156: (36, 112), 158: (60, 112), 160: (84, 112)}
# Each piece's damaged look (dgr); the ones whose sprite is the intact one's pixels unchanged reuse its model.
DAMAGED = {2: 12, 4: 14, 6: 16, 8: 18, 39: 49, 41: 51, 43: 53, 45: 55, 47: 208,
           77: 87, 79: 89, 81: 91, 83: 93, 85: 246, 115: 125, 117: 127, 119: 129, 121: 131, 123: 284,
           154: 164, 156: 166, 158: 168, 160: 170}
SAME_WHEN_DAMAGED = (2, 39, 41, 43, 45, 47, 81)


def XE(c):
    """The left edge of the picture's column c (fractions allowed)."""
    return c - 60.0


def YE(r):
    """The top edge of the picture's row r."""
    return 70.0 - r


def MX(x):
    """The mirror image of x about the axis."""
    return 2 * AX - x


def box_of(sprite):
    c, r = CELLS[sprite]
    return (XE(c), XE(c + 24), YE(r + 28), YE(r))


def smoothstep(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


# --- The measures (pixel edges of the picture; the left half, mirrored) -----------------------------------------------

Z_DECK, Z_RIM, Z_RIM_LOW, Z_BELLY = 4.4, 0.9, -0.7, -3.4
# The hull's outline, its left half: from the middle of its back (under the tanks' bend) round the back edge (under
# the masts), down the flank and round the bowl to the middle of its front.
HULL_LEFT = [(59.5, 73.6), (54.4, 73.6), (53.0, 64.4), (32.0, 64.4), (31.0, 66.0), (28.0, 67.2), (23.0, 69.6),
             (20.0, 71.1), (18.0, 72.5), (16.0, 74.0), (13.0, 76.0), (10.0, 78.0), (7.0, 79.6), (5.0, 81.0),
             (4.0, 81.8), (4.0, 87.0), (4.6, 92.0), (5.6, 95.8), (6.8, 98.8), (8.0, 101.4), (9.2, 104.0),
             (10.4, 106.6), (11.6, 109.0), (13.0, 111.4), (14.8, 114.0), (16.6, 116.6), (18.6, 119.0),
             (21.0, 121.6), (24.0, 124.6), (27.0, 127.4), (30.0, 129.6), (33.0, 131.4), (36.0, 133.2),
             (39.0, 134.8), (42.0, 136.2), (46.0, 137.4), (52.0, 138.0), (59.5, 138.0)]
WING_EDGE = 18.0                # the crease between the purple wing and the deck (column edge)
FRONT = (80.0, 55.5, 57.8, 2.3)  # the bowl's outline: centre row, half-width, half-height, power
FRONT_DECK = 0.86               # the deck's front edge, in the bowl's measure (the front chamfer outside it)

# The tanks: the left one's axis (x), half-width, half-height, the height of its axis, its superellipse power; its
# straight run from inside the hood down to the bend; the bend a half ellipse round the axis (its half-height).
TANK_X, TANK_W, TANK_H, TANK_Z, TANK_P = -17.0, 10.6, 6.2, 4.4, 2.4
TANK_TOP_Y = YE(14.0)
TANK_JOINT_Y = YE(71.6)         # the seam where the straight runs meet the heart
# The heart the tanks turn into (its left half's outline from the dip between the lobes, round the outer side and the
# bottom to the middle), the basin inside its rim (from how far in, to how far in, how deep), its lobes (column, row,
# reach across, reach along, lift).
HEART_LEFT = [(59.5, 74.2), (57.6, 73.4), (55.6, 72.4), (53.4, 71.6), (32.6, 71.6), (32.6, 84.0), (33.2, 87.0),
              (34.2, 90.0), (35.6, 93.0), (37.4, 96.0), (40.0, 98.6), (43.2, 100.6), (47.0, 102.2), (52.0, 103.2),
              (59.5, 103.6)]
HEART_BASIN = (8.0, 12.0, 3.0)
HEART_LOBE = (46.0, 76.0, 8.0, 3.6, 0.7)
TANK_BANDS = [(-9.0, "t2"), (0.3, "t5"), (0.6, "t8"), (0.84, "tb"), (0.96, "glint")]

# On the tank: the clamp's plates (columns, rows), the ribbed panel (columns, rows) and its ribs (rows), the rail.
CLAMP_COLS = [(34.8, 40.3), (41.0, 47.6)]
CLAMP_ROWS = [(28.2, 35.9), (37.4, 44.4)]
RIBS = (35.6, 41.6, 56.6, 71.4)
RIB_ROWS = [58.5, 60.5, 62.5, 64.5, 66.5]

# The hood's vents (columns), their rows, the grille's slots (rows; columns) and the slot down it.
VENTS = [(35.0, 38.0), (39.0, 42.0), (43.0, 46.0)]
VENT_ROWS = (0.8, 5.6)
GRILLE_ROWS = [(6.8, 7.7), (8.8, 9.7)]
GRILLE_COLS = (34.8, 47.4)
GRILLE_DOWN = (40.8, 41.6, 6.6, 10.6)

# The masts: their axes' columns, profiles [(row, radius)] from the foot to the tip, the heights of their axes at
# the foot and the tip (leaning back up the screen), their valves (row, radius, offset to the left).
MAST_A_COL, MAST_A_Z = 15.5, (3.2, 10.0)
MAST_A = [(80.6, 2.5), (64.0, 2.5), (55.2, 2.5), (54.4, 3.0), (53.0, 3.5),
          (42.6, 3.5), (42.0, 2.6), (41.6, 1.4), (39.0, 1.4), (38.6, 2.5), (36.4, 2.5), (36.0, 1.2), (33.2, 1.2),
          (32.6, 1.55), (31.8, 1.15), (30.4, 1.45), (29.6, 1.0), (28.8, 0.3)]
MAST_A_VALVE = (47.8, 1.5, 5.0)
MAST_A_FOOT = (9.8, 18.4, 64.2, 81.0, 2.2)   # its foot's block: columns, rows, how high it stands over its axis
MAST_B_COL, MAST_B_Z = 6.5, (1.2, 8.8)
MAST_B = [(81.4, 2.4), (70.6, 2.4), (70.0, 3.0), (68.8, 3.5), (58.6, 3.5), (58.0, 2.6), (57.6, 1.4), (55.0, 1.4),
          (54.6, 2.5), (52.4, 2.5), (52.0, 1.2), (49.2, 1.2), (48.6, 1.55), (47.8, 1.15), (46.4, 1.45), (45.6, 1.0),
          (44.8, 0.3)]
MAST_B_VALVE = (62.6, 1.5, 4.0)
MAST_B_TORN = (58.4, 70.6)       # the right one's casing, gone in its damaged look (rows)
# The purple plating torn up between the right masts' feet in the damaged look (columns and rows in the left half's
# frame, height, tilt).
SHARDS = [(5.0, 11.4, 63.6, 70.2, 4.2, 0.55), (5.0, 11.2, 74.6, 83.6, 3.0, 0.3)]

# The lamp (the middle column, row and height of its ellipsoid, its radii), its purple mount (columns, rows).
LAMP = (31.6, 58.1, 3.2, 8.6, 11.5, 6.0)
LAMP_MOUNT = [(28.8, 66.4), (32.4, 66.4), (32.4, 81.6), (28.8, 81.6)]

# The hull's fittings: the rails along the wing's crease (column, rows), the ribs across the wing (rows), the gun
# port's housing (columns, rows, height over the deck) and the pit its hatch closes (columns, rows, floor), the scoop
# (middle column and row, half-axes, turn, depth), the panel lines (columns, rows), the barrels' slots.
CREASE_RAILS = [(19.6, 72.0, 112.0), (22.6, 71.0, 84.0), (25.6, 70.0, 82.0)]
WING_RIBS = [84.0, 86.0, 88.0]
PORT_HOUSING = (23.6, 33.6, 83.6, 96.4, 1.0)
PORT_PIT = (24.8, 32.4, 88.4, 95.4)
PORT_FLOOR = Z_DECK - 0.8
SCOOP = (34.0, 102.0, 7.5, 3.0, -0.52, 0.8)
GROOVES = [(40.9, 41.6, 119.6, 129.4), (41.6, 48.2, 121.9, 122.6), (57.9, 58.5, 128.6, 134.8),
           (36.6, 37.2, 108.0, 117.2)]
ARC = (0.775, 18.6, 48.2, 0.38)  # the arc's measure in the bowl, its columns, its half-width
SLOT = (48.2, 55.8, 108.6, 121.6, 1.4)
# The barrel (its axis' column, rows, height), its lamp's socket (row of its middle, radius), the chin between the
# barrels (columns, rows, height over the deck).
BARREL_COL, BARREL_ROWS, BARREL_Z = 51.5, (111.8, 121.6), Z_DECK - 0.05
LAMP_ROW, SOCKET_R = 125.0, 2.4
CHIN = (55.6, 63.4, 108.6, 121.4, 1.5)
BARREL_BROKEN = 114.6            # where the right barrel breaks off in the damaged look (row)
# The machinery in the U: the vent, the grid plate and the block under them (columns, rows, top, bevel).
BLOCKS = [(54.8, 64.2, 81.6, 85.4, 11.4, 0.4), (52.8, 66.2, 85.6, 90.2, 11.8, 0.4),
          (50.8, 68.2, 90.6, 103.6, 12.2, 0.6)]
BLOCK_SLOTS = [(0, 55.6, 63.4, 82.8, 83.4), (0, 55.6, 63.4, 84.0, 84.6), (1, 53.4, 65.6, 88.0, 88.6),
               (1, 56.8, 57.4, 85.8, 90.0), (1, 61.6, 62.2, 85.8, 90.0), (2, 51.4, 67.6, 95.0, 95.6),
               (2, 58.2, 60.8, 91.2, 95.0)]

# The hood (the left one; mirrored): its plan, its flat top, the planes of its front (sloping down the screen from row
# 13), its left chamfer (falling to the left from column 34) and its right flank (from column 48.5).
HOOD_PLAN = [(33.0, 0.6), (48.0, 0.6), (54.9, 7.6), (54.9, 21.6), (37.4, 21.6), (37.6, 30.4), (32.0, 34.6),
             (24.0, 31.8), (21.2, 27.6), (21.2, 25.4)]
Z_HOOD = 12.6
HOOD_FRONT = (13.2, Z_HOOD, 33.0, 6.2)        # row, height; row, height
HOOD_LEFT = (34.0, Z_HOOD, 21.0, 5.4)         # column, height; column, height
HOOD_RIGHT = (48.6, Z_HOOD, 55.0, 7.4)
HOOD_BOTTOM = 3.0


def materials():
    pal = k.level_palette()

    def mat(name, index, metallic, roughness, glow=None):
        if glow:
            return k.material("cboss_" + name, palette=index, metallic=metallic, roughness=roughness,
                              emission=pal[index], emission_strength=glow)
        return k.material("cboss_" + name, palette=index, metallic=metallic, roughness=roughness)
    return {
        "black": mat("black", 0x01, 0.2, 0.5),
        "dark": mat("dark", 0x02, 0.25, 0.55),
        "g4": mat("g4", 0x04, 0.3, 0.5),
        "g6": mat("g6", 0x06, 0.3, 0.48),
        "g8": mat("g8", 0x08, 0.3, 0.45),
        "g9": mat("g9", 0x09, 0.3, 0.42),
        "gb": mat("gb", 0x0b, 0.3, 0.38),
        "p4": mat("p4", 0x54, 0.25, 0.45),
        "p7": mat("p7", 0x57, 0.25, 0.42),
        "pa": mat("pa", 0x5a, 0.25, 0.4),
        "t2": mat("t2", 0x32, 0.4, 0.28, 0.04),
        "t5": mat("t5", 0x34, 0.4, 0.24, 0.06),
        "t8": mat("t8", 0x36, 0.4, 0.2, 0.08),
        "tb": mat("tb", 0x39, 0.4, 0.18, 0.12),
        "glint": mat("glint", 0x3d, 0.25, 0.12, 0.25),
        "lamp": mat("lamp", 0x97, 0.05, 0.15, 0.32),
        "lamp_hot": mat("lamp_hot", 0x8b, 0.05, 0.1, 0.4),
        "vent": mat("vent", 0x72, 0.1, 0.4, 0.2),
        "red": mat("red", 0x76, 0.05, 0.2, 0.4),
        "red_hot": mat("red_hot", 0x78, 0.05, 0.2, 0.5),
        "red_hotter": mat("red_hotter", 0x7b, 0.05, 0.2, 0.6),
        "glow1": mat("glow1", 0x72, 0.05, 0.3, 0.3),
        "glow2": mat("glow2", 0x75, 0.05, 0.25, 0.4),
        "glow3": mat("glow3", 0x78, 0.05, 0.2, 0.45),
        "glow4": mat("glow4", 0x7a, 0.05, 0.2, 0.5),
        "core3": mat("core3", 0x7c, 0.0, 0.2, 0.55),
        "core4": mat("core4", 0x7e, 0.0, 0.2, 0.6),
        "ember": mat("ember", 0x76, 0.05, 0.3, 0.4),
    }


# --- Helpers ------------------------------------------------------------------------------------------------------

def ccw(pts):
    area = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
    return pts if area > 0 else pts[::-1]


def plan(points):
    """A plan in pixel edges (c, r)."""
    return ccw([(XE(c), YE(r)) for c, r in points])


def whole_plan(left):
    """A plan symmetric about the axis from its left half (pixel edges, from the axis at one end to the axis at the
    other)."""
    pts = [(XE(c), YE(r)) for c, r in left]
    right = [(MX(x), y) for x, y in reversed(pts[1:-1])]
    return ccw(pts + right)


def plane_box(name, top, size=90.0):
    """Everything under z = top(x, y) (a thick slab along it), for intersecting with."""
    s = size
    return mk.wedge(name, [(-s, -s), (s, -s), (s, s), (-s, s)], 0.0, top, bottom=lambda x, y: top(x, y) - 400.0)


def linear(a0, z0, a1, z1):
    return lambda a: z0 + (z1 - z0) * (a - a0) / (a1 - a0)


def grid_prism(name, outline, top, bottom, mat, step=1.0):
    """A prism of a plan whose top and bottom faces are cut along a grid (step apart) and moved to top(x, y) and
    bottom(x, y): a solid with curved top and underside, its flat stretches dissolved into few faces again."""
    obj = mk.prism(name, outline, 0.0, 1.0, mat)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    xs = [p[0] for p in outline]
    ys = [p[1] for p in outline]
    x = math.floor(min(xs)) + step
    while x < max(xs):
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=(x, 0, 0),
                               plane_no=(1, 0, 0))
        x += step
    y = math.floor(min(ys)) + step
    while y < max(ys):
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=(0, y, 0),
                               plane_no=(0, 1, 0))
        y += step
    for v in bm.verts:
        v.co.z = top(v.co.x, v.co.y) if v.co.z > 0.5 else bottom(v.co.x, v.co.y)
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="BEAUTY", ngon_method="BEAUTY")
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(0.3), use_dissolve_boundaries=False, verts=bm.verts,
                             edges=bm.edges, delimit={"MATERIAL"})
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def mirror_about_axis(objects, suffix="_r"):
    """Copies of objects mirrored about x = AX, keeping their shading (corner normals) and materials."""
    flip = Matrix.Translation((AX, 0, 0)) @ Matrix.Scale(-1, 4, (1, 0, 0)) @ Matrix.Translation((-AX, 0, 0))
    out = []
    for obj in objects:
        mk.apply(obj)
        copy = obj.copy()
        copy.data = obj.data.copy()
        copy.name = obj.name + suffix
        bpy.context.scene.collection.objects.link(copy)
        mesh = copy.data
        corner = {}
        for poly in mesh.polygons:
            for li in poly.loop_indices:
                n = mesh.corner_normals[li].vector
                corner[(poly.index, mesh.loops[li].vertex_index)] = (-n.x, n.y, n.z)
        mesh.transform(flip)
        mesh.flip_normals()
        normals = [None] * len(mesh.loops)
        for poly in mesh.polygons:
            for li in poly.loop_indices:
                normals[li] = corner[(poly.index, mesh.loops[li].vertex_index)]
        mesh.normals_split_custom_set(normals)
        out.append(copy)
    return out


def mirrored(objects):
    """objects moved to their mirror images about the axis (mirror_about_axis, the originals removed)."""
    out = mirror_about_axis(objects)
    for obj in objects:
        data = obj.data
        bpy.data.objects.remove(obj)
        if data.users == 0:
            bpy.data.meshes.remove(data)
    return out


def paint_light(obj, m, bands, under=None, keep=()):
    """Faces by how much they face the sun (n . LIGHT), along smooth borders (band_split): bands [(lowest, name)];
    faces turned down (n.z < -0.3) under."""
    mesh = obj.data
    mesh.update()
    names = {m[n].name for n in keep}
    values = [0.0] * len(mesh.vertices)
    count = [0] * len(mesh.vertices)
    for poly in mesh.polygons:
        for vi in poly.vertices:
            values[vi] += poly.normal.dot(LIGHT)
            count[vi] += 1
    values = [v / max(c, 1) for v, c in zip(values, count)]
    band_split(obj, values, [(lo, m[name]) for lo, name in bands])
    if under:
        mk.paint(obj, lambda c, n: m[under] if n.z < -0.3 else None)
    return obj


def bevelled_box(name, x0, x1, y0, y1, z0, z1, mat, bevel, segments=2, angle=35.0):
    obj = mk.box(name, min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), z0, z1, mat)
    if bevel > 0:
        mk.bevel(obj, bevel, segments, angle)
    return obj


def paint_faces(obj, m, top, side, lit=None, under="dark", top_min=0.9, lit_min=0.5, keep=()):
    """Faces by how they face: up (n.z > top_min) top, down under, turned to the sun (n . LIGHT > lit_min) lit, the
    others side; faces of the materials named in keep are kept."""
    names = {m[n].name for n in keep}
    mats = obj.data.materials

    def pick(c, n):
        if n.z > top_min:
            return m[top]
        if n.z < -0.3:
            return m[under]
        if lit and n.dot(LIGHT) > lit_min:
            return m[lit]
        return m[side]
    slots = {}
    for poly in obj.data.polygons:
        cur = mats[poly.material_index]
        if cur is not None and cur.name in names:
            continue
        mat = pick(poly.center, poly.normal)
        if mat.name not in slots:
            slots[mat.name] = mk.slot_of(obj, mat)
        poly.material_index = slots[mat.name]
    return obj


# --- The damage ------------------------------------------------------------------------------------------------------
# How the damaged sprites draw the picture differently, pixel by pixel (the top row's read a row lower): (row, first
# column, the run's pixels) with 'x' smashed (much darker), 's' scorched (darker), 'l' lighter (debris, torn edges),
# 'e' embers (red where it was not), '-' gone, '+' new; '.' as it was.
DAMAGE = [
    (5, 68, 'xs'), (5, 87, '-'), (6, 67, 'xxxs'), (6, 86, 's-'), (7, 66, 'xxxxxx'), (7, 83, 'xss---'),
    (8, 50, 'ssss'), (8, 65, 'sxxxxxxxx.xxe.xxxxxss---'), (9, 48, 'seeess'), (9, 66, 'sxxxxx...e.e...l.xss----'),
    (10, 46, 'sxseee.s'), (10, 67, 'sxxxxxxsexe.xxxxxss----'), (11, 45, 'sxxseee.s'),
    (11, 69, 'sxxxxseeesxxxxsss-----'), (12, 45, 'sxxseee.s'), (12, 70, 'ssxxseeesxxxxxss-----'),
    (13, 45, 'sssseeels'), (13, 72, 's.sess.ssss...s-----'), (14, 45, 'ssxseesle'), (14, 87, '-----'),
    (15, 46, 'sss..l.e'), (15, 88, '-----'), (16, 50, 'l.ee'), (16, 89, 'sss'), (17, 51, 'see'), (17, 89, 'lll'),
    (18, 51, 'ses'), (18, 91, 'll'), (19, 51, 'see'), (19, 92, 'l'), (20, 51, 'see'), (20, 93, 'l'), (21, 52, 'se'),
    (21, 93, 'l'), (22, 93, 'l'), (23, 96, '-'), (24, 96, 's-'), (56, 108, '+++.s.+'), (57, 108, '+++l..+'),
    (58, 79, 'sss'), (58, 108, '+l.ll..-'), (59, 78, 'ss'), (59, 108, '+.xxsxs-'), (60, 78, 'xxxxs'),
    (60, 108, '+.xxssx-'), (61, 78, 'ss'), (61, 108, '+.xxl.s---'), (62, 78, 'xxxxs'), (62, 108, '+.xxssx---'),
    (63, 78, 'ss'), (63, 108, '+.xxssx---'), (64, 78, 'xxxxs'), (64, 108, 'llxxssx---'), (65, 78, 'ss'),
    (65, 104, 'ssssll.xxsx---'), (66, 78, 'xxxxs'), (66, 103, 'xxxsxll.x.sx---'), (67, 78, 'xxsss'),
    (67, 102, 'xxxxsxll.s.xx-'), (68, 78, 'xxsss'), (68, 101, 'sxxxxsxll.llsx-'), (69, 23, 's'), (69, 78, 'sssss'),
    (69, 101, 'xxxxxsxll.l..x-'), (70, 22, 'sssxs'), (70, 80, 'sss'), (70, 89, 'e..x.s.e....xxxsxsx.s'),
    (71, 22, 'sxsxxs'), (71, 89, 'e..x.sx.....xxxsxsx'), (72, 17, 's..sxxxxxxx'),
    (72, 86, 'eeeeeeeeeeess..xxxsxsx.s'), (73, 18, 'sxxxxxxxxx'), (73, 88, 'ee..s.sx.ex....xsxsx.x.s'),
    (74, 17, 'xxxxxxxxxxx'), (74, 88, 'eee...sxeex.xx...xsx.x.x'), (75, 18, 'xxxxxxxxxx'),
    (75, 89, 'e.....xesx.xx.s...x.x.xs'), (76, 18, 'xxxxxxxxxx'), (76, 89, 'eee...xees.xx'), (76, 109, 'x.xx'),
    (77, 18, 'xxxxxxxxxx'), (77, 86, 'eeeeee...xeex.xx'), (77, 111, 'xx'), (78, 18, 'xxxxxxxxxs'),
    (78, 88, 'eee....xesx.xx'), (78, 112, 'xs'), (79, 18, 'sxxxxxxxxx'), (79, 89, 'ee....sesx.sx'),
    (80, 19, 'xxxxxxxxxx'), (80, 89, 'ee....sesx.sx'), (81, 19, 'xxxxxxxxxxx.s'), (81, 89, 'e..s..ses..ss'),
    (82, 19, 'xxxxxxxxxxxxx'), (82, 89, 'e.....sesl'), (83, 19, 'sxxxxxxxxxxxx'), (83, 88, 'eeeeeeesesll'),
    (84, 19, 'sxxxxxxxxxxxx'), (84, 89, 'e....ss.ssl'), (85, 19, 'xxxxxxxxxxxxx'), (85, 91, 'sssxx.ss.ll'),
    (86, 19, 'xxxxxxxxxxxx'), (86, 94, 'ss.ss.sl'), (87, 19, 'xxxx.xxxxxx.x'), (87, 95, 's.ss.ss'),
    (88, 19, 'sxxxlsxxxx.xxx'), (88, 95, 's.ss.ss'), (89, 20, 'xxxllxxxxxxxx'), (89, 95, 's.ss..s'),
    (90, 21, 'xxlxxxxxxxxxs'), (90, 97, 'ss.l'), (91, 21, 'sxsxxxxxxxxxx'), (91, 88, 'e...ss...ss.l'),
    (92, 22, 'slxxxxxxxxxxx'), (92, 88, 'e...ss...ss.s'), (93, 22, 'llxxxxxxxxxxx'), (93, 88, 'e..sss.s.ss.s'),
    (94, 23, 'lsxxxxxxxxxxx'), (94, 84, 'eee.e..sss.s.ss.ss'), (95, 22, 'sl..s.sxxxxxxxs'), (95, 84, 'e.eee'),
    (95, 95, 's.ss.s'), (96, 21, 'sxll..llxxxxxxxxs'), (96, 83, 'ee.eee.ss.....ss'), (97, 21, 'sx....ll..s.xxxxxs'),
    (97, 82, 'ee..ee.sss'), (98, 21, 'sxs'), (98, 33, 'xxxxxxs'), (98, 82, 'ee..e.ls'),
    (99, 21, 'sxs..ssssssxxxxxxxs'), (99, 82, 'ee...sl'), (100, 18, 'ss..s..sxxxxxxxxxxxxxxxxs'),
    (100, 81, 'seee.ssl'), (101, 17, 'xxxxs...xxxxxxxxxxxxxxxexxxs'), (101, 73, 'ssss..s.sesesssl'),
    (102, 17, 'xxxxxs..xxxxxxxxxxxxxxxexxxxxs'), (102, 72, 'ssxsssss.xsesss.l'),
    (103, 17, 'xxxxxxs.sxxxxxxxxxeexeeeeeeeexexse'), (103, 67, 'ssssxxxxssxxsexeess..l'),
    (104, 17, 'xxxxxxxxsxxxxxxxxxxxxxeexxxxxxxxss'), (104, 61, 'ssxxxxxxxxssxxxxxxeexxss.ssl'),
    (105, 17, 'xxxxxxxxxxsxxxxxxxxxxxeexxxxxxxss'), (105, 60, 'ssxxxxxxxxs..sxxxxxxsxxs.ssll..l'),
    (106, 17, 'xxxxxxxxxxxsxxxxxxxxxxxxsssss'), (106, 59, 'ssssss.xsxxsssxxxxxxxsssess.sl.l'),
    (107, 17, 'xxxxxxxxxxxxxxxxxxxxxll.xs'), (107, 59, 'sxxss.xxssxxxxxxxxxs.sxeessssl.l'),
    (108, 17, 'ssxxxxxxxxxxxxxxxxxx.sx.xxs'), (108, 59, 'sxxxssxxxsxxxxxxxs..s.eesssssl'),
    (109, 17, 's.xxxxxxxxxxxxxxxxxsxxxsxxxs'), (109, 59, 'sxxxxx.sslssssxxx..sxseeseesslsssss'),
    (110, 19, 'xxxxxxxxxxxxxxxxsxxxxxxxxs'), (110, 59, 'xxxxxx...lssssxxs.ssxxxexseesl.ssssss'),
    (111, 19, 'xxxxxxxxxxxxxxxxxxxxxxxxxs'), (111, 58, 'sxxxxxs.ll.sssxxxx.sxxxxexeeexllsss..s'),
    (112, 20, 'xxxxxxxxxxxxxxxxxxxssxxxs'), (112, 57, 'sxxxxxxs.llsssxxxxssxxxxxexeexxll.ss..s'),
    (113, 20, 'x.xxxxxxxxxxxxxsxxxssxxxs'), (113, 57, 'sxxxxxxs.lsxxsxxxxxsxxxxeexexxsl..ss....+'),
    (114, 20, 's.xxxxxxxxxxxsssxxxxxxxxs'), (114, 57, 'sxxs.ss..lxxxsxxx..sxxxxeexxxll...ss'),
    (115, 22, 'sxxxxxxxxxxslsxxxxxxxxs'), (115, 57, 'sxxx.....lxxxsxx.xxxxxxxxexxxl...ss'),
    (116, 23, 'sxxxxxxxxxss.sxxxxxxxx'), (116, 57, 'sxxxxs...sxxxsxlssxxxxxxxxxxx.l.ssss'),
    (117, 24, 'sxxxxxxxxxs.sxxxxxxxs'), (117, 57, 'sxxxxxxs.sxxllsl.sxxxxxxxexxxsllssxs'),
    (118, 25, 'ssxxxxxxs.sssxxxxxxs'), (118, 57, 'sxxxxxxx.sxxssxl.xxxxxxxeexxsxs...xss'),
    (119, 27, 'll..s...sxssxxxxs'), (119, 58, 'xxxxxxx.ssxxsxssxxeeexeexxs.sss.sx.s'), (120, 27, 'lll.....sxssxxxl'),
    (120, 56, 'ssxxxxxxxsssxxsxxxeeeeeeexxxxxxxxsxsss'), (121, 27, 'l'), (121, 36, 'ss.xxxss'),
    (121, 55, 'sxsxxxxxxss.ssxsxxxxeeeeex...sxxxxxx'), (122, 27, 'l'), (122, 39, 'xxxxx'),
    (122, 55, 'sxsssssss.....sssxxxxee..xxx..xxxxs'), (123, 27, 'l'), (123, 38, 'sxxxx'), (123, 55, 'sxsssssxs'),
    (123, 70, 'ssxxxxexsxxxxxssxxx'), (124, 37, 'sxxxxxs'), (124, 54, 'sxxxxs.sxss.....sssxxxs.xxxxxxxxxxs'),
    (125, 37, 'sxxxxsxxx'), (125, 53, 'ssxxxx..sxxxss...x.sxxxsxxxxxxxxxxs'), (126, 37, 'xxxxxxsxxx'),
    (126, 53, 'xxxxxxll.sssss...ssxxxxxxxxxxxxxsx'), (127, 36, 'xxxxxxxsxxxx.sxxxxxxxxsl....s.sxxxxxxxssxxxxxxxxxsx'),
    (128, 35, 'sxxxxxxxxxxxxxxsxxxxxsxs'), (128, 66, 'ssxxxxs..xxxxxxxxxxxs'),
    (129, 34, 'sxxxxxxxxxxxxxxxl.sssssxxl'), (129, 67, 'sxxxs..sxxxxsxxxxxss'),
    (130, 33, 'sxxxxxxxsxxxxxxxxl.....sxxl'), (130, 66, 'ssxxs.sxxxxxxsxxxxxs'),
    (131, 35, 'ssxsxxsxxxxxxxxx.l....sxx.l..ssxxxs.sxslxxxxsxxxs'),
    (132, 36, 'ssssxs.sssxxxxss.l...ssxx.s.sxxss.sxxxlxxxxsxss'),
    (133, 38, 'sxxs....xxxxxx.ll...sxxsx.sss..sxxxslsxxxsx'), (134, 39, 'sss....sxxxxxs.l...sssss.....ssxxsllxxxs'),
    (135, 47, 'sssssss.....sssl..sssssss.ssss'), (136, 48, 'sssssssl'), (136, 64, 'ssssssss'),
]
DENT = 2.3                       # how deep the smashed plating is pressed in
SEAM_FADE = (0.3, 1.8)           # the damage fades out towards the pieces that keep their intact look


def damage_cells():
    cells = {}
    for r, c0, run in DAMAGE:
        for i, ch in enumerate(run):
            if ch != ".":
                cells[(c0 + i, r)] = ch
    return cells


def blurred(values, sigma):
    """A 120 x 140 grid of values (a dict by pixel), blurred (a Gaussian of sigma pixels)."""
    radius = int(math.ceil(2.5 * sigma))
    kern = [math.exp(-(i * i) / (2 * sigma * sigma)) for i in range(-radius, radius + 1)]
    total = sum(kern)
    kern = [v / total for v in kern]
    grid = [[values.get((c, r), 0.0) for c in range(120)] for r in range(140)]
    rows = [[sum(kern[i + radius] * grid[r][min(119, max(0, c + i))] for i in range(-radius, radius + 1))
             for c in range(120)] for r in range(140)]
    return [[sum(kern[i + radius] * rows[min(139, max(0, r + i))][c] for i in range(-radius, radius + 1))
             for c in range(120)] for r in range(140)]


class Damage:
    """The damaged look's fields over the picture: how smashed each point is (0-1, smooth), fading out towards the
    pieces whose damaged sprite is their intact one; mirror: read on the other side of the axis (for the right half's
    parts, built on the left and mirrored)."""

    def __init__(self, mirror=False):
        self.mirror = mirror
        self.cells = damage_cells()
        weight = {"x": 1.0, "-": 1.0, "e": 0.85, "l": 0.6, "+": 0.5, "s": 0.45}
        self.field = blurred({cr: weight[ch] for cr, ch in self.cells.items()}, 1.1)
        self.keep = [box_of(sp) for sp in SAME_WHEN_DAMAGED]

    def fade(self, x, y):
        best = 1e9
        for x0, x1, y0, y1 in self.keep:
            dx = max(x0 - x, 0.0, x - x1)
            dy = max(y0 - y, 0.0, y - y1)
            best = min(best, math.hypot(dx, dy))
        return smoothstep(SEAM_FADE[0], SEAM_FADE[1], best)

    def S(self, x, y):
        if self.mirror:
            x = MX(x)
        c, r = x + 60.0 - 0.5, 70.0 - y - 0.5
        c0, r0 = int(math.floor(c)), int(math.floor(r))
        fc, fr = c - c0, r - r0
        v = 0.0
        for dc, dr, w in ((0, 0, (1 - fc) * (1 - fr)), (1, 0, fc * (1 - fr)), (0, 1, (1 - fc) * fr), (1, 1, fc * fr)):
            cc, rr = min(119, max(0, c0 + dc)), min(139, max(0, r0 + dr))
            v += w * self.field[rr][cc]
        return v * self.fade(x, y)

    def cell(self, x, y):
        if self.mirror:
            x = MX(x)
        return self.cells.get((int(math.floor(x + 60.0)), int(math.floor(70.0 - y))))

    def dent(self, x, y):
        """How far the plating at (x, y) is pressed in."""
        n = noise.noise(Vector((x / 2.3, y / 2.3, 0.7)))
        return DENT * self.S(x, y) * (0.72 + 0.28 * n)


def char(objects, m, dmg, keep=()):
    """Faces of smashed parts charred (black where smashed most, dark, scorched grey), as the damaged sprites paint
    them; faces of the materials named in keep (glass, fire) left alone."""
    names = {m[n].name for n in keep}
    for obj in objects:
        mats = obj.data.materials
        mw = obj.matrix_world
        slots = {}
        for poly in obj.data.polygons:
            cur = mats[poly.material_index]
            if cur is not None and cur.name in names:
                continue
            c = mw @ poly.center
            v = dmg.S(c.x, c.y)
            if v < 0.22 or poly.normal.z < -0.2:
                continue
            v += 0.25 * noise.noise(Vector((c.x / 1.7, c.y / 1.7, 2.3)))     # mottled, as burnt plating is
            mat = m["black"] if v > 0.98 else m["dark"] if v > 0.72 else m["g4"] if v > 0.48 else m["g6"]
            if mat.name not in slots:
                slots[mat.name] = mk.slot_of(obj, mat)
            poly.material_index = slots[mat.name]
    return objects


def smashed(dmg, x, y, limit=0.62):
    """Whether a small part at (x, y) is shot away."""
    return dmg is not None and dmg.S(x, y) > limit


def debris(m, dmg, surface):
    """Chunks of torn plating lying in the craters (where the sprites draw it smashed or with lighter bits), each a
    small bent plate turned its own way (seeded: the same every run)."""
    rnd = random.Random(11)
    parts = []
    placed = []
    for (c, r), ch in sorted(dmg.cells.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        if r < 64 or ch not in "xl":
            continue
        if rnd.random() > (0.24 if ch == "l" else 0.07):
            continue
        x, y = XE(c) + rnd.uniform(0.2, 0.8), YE(r) - rnd.uniform(0.2, 0.8)
        if dmg.fade(x, y) < 0.99 or any(math.hypot(x - a, y - b) < 3.0 for a, b in placed):
            continue
        z = surface(x, y)
        if z is None:
            continue
        placed.append((x, y))
        size = rnd.uniform(1.4, 3.4)
        chunk = bevelled_box(f"debris{len(parts)}", -size / 2, size / 2, -size * rnd.uniform(0.2, 0.45),
                             size * rnd.uniform(0.2, 0.45), -0.3, rnd.uniform(0.3, 0.8), m["g8"], 0.12, 1)
        turn = (Matrix.Translation((x, y, z)) @ Matrix.Rotation(rnd.uniform(0, 6.28), 4, "Z") @
                Matrix.Rotation(rnd.uniform(-0.5, 0.5), 4, "X") @ Matrix.Rotation(rnd.uniform(-0.5, 0.5), 4, "Y"))
        chunk.data.transform(turn)
        chunk.data.update()
        paint_faces(chunk, m, "g9" if ch == "l" else "g8", "g6", lit="gb", top_min=0.8, lit_min=0.6)
        parts.append(chunk)
    return parts


def embers(m, dmg, surface):
    """The embers glowing in the cracks: a small glowing chip on the surface at each pixel the sprites draw red."""
    verts, faces = [], []
    for (c, r), ch in sorted(dmg.cells.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        if ch != "e":
            continue
        x0, x1, y0, y1 = XE(c) + 0.08, XE(c) + 0.92, YE(r) - 0.92, YE(r) - 0.08
        zs = [surface(x, y) for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
        if any(z is None for z in zs):
            continue
        z = max(zs) + 0.06
        i = len(verts)
        verts += [(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)]
        faces.append((i, i + 1, i + 2, i + 3))
    if not faces:
        return []
    return [k.mesh_object("embers", verts, faces, m["ember"])]


# --- The hull -------------------------------------------------------------------------------------------------------

def bowl_measure(x, y):
    """How far out (x, y) lies in the bowl's outline (1 on it), below its centre row; 0 above it."""
    row0, a, b, p = FRONT
    d = abs(x - AX) / a
    dy = max(0.0, YE(row0) - y) / b
    return (d ** p + dy ** p) ** (1.0 / p)


def hull_top(x, y):
    """The hull's top: the flat deck, the purple wing sloping from the crease down to the rim at the flanks, the front
    chamfer round the bowl."""
    d = abs(x - AX)
    z = Z_DECK
    crease = abs(XE(WING_EDGE) - AX)
    if d > crease:
        z = min(z, Z_DECK - (d - crease) * (Z_DECK - Z_RIM) / (abs(XE(4.0) - AX) - crease))
    rho = bowl_measure(x, y)
    if rho > FRONT_DECK:
        z = min(z, Z_DECK - (rho - FRONT_DECK) / (1.0 - FRONT_DECK) * (Z_DECK - Z_RIM))
    return max(Z_RIM, z)


def outline_distance(outline):
    """distance(x, y) to the polygon's edges."""
    segs = [(outline[i], outline[(i + 1) % len(outline)]) for i in range(len(outline))]

    def dist(x, y):
        best = 1e9
        for (ax, ay), (bx, by) in segs:
            vx, vy = bx - ax, by - ay
            t = max(0.0, min(1.0, ((x - ax) * vx + (y - ay) * vy) / (vx * vx + vy * vy + 1e-12)))
            best = min(best, math.hypot(x - ax - t * vx, y - ay - t * vy))
        return best
    return dist


def hull_surface(dmg):
    """The hull's top as built: intact, or with the smashed plating pressed in."""
    if dmg is None:
        return hull_top
    return lambda x, y: max(Z_RIM_LOW + 0.5, hull_top(x, y) - dmg.dent(x, y))


def hull(m, dmg=None):
    outline = whole_plan(HULL_LEFT)
    dist = outline_distance(outline)

    def belly(x, y):
        return Z_RIM_LOW - (Z_RIM_LOW - Z_BELLY) * smoothstep(0.0, 16.0, dist(x, y))
    body = grid_prism("hull", outline, hull_surface(dmg), belly, m["g8"], step=1.0)
    crease = XE(WING_EDGE)

    def pick(c, n):
        if n.z < -0.3:
            return m["dark"]
        if n.z < 0.35:
            return m["g4"]           # the rim's band
        d = abs(c.x - AX)
        if d > abs(crease - AX) + 0.05 and n.z < 0.995 and bowl_measure(c.x, c.y) < 0.93:
            return m["p7"]           # the purple wing
        if n.z < 0.995:
            return m["g6"]           # the front chamfer
        return m["g8"]
    mk.paint(body, pick)
    mk.cleanup(body, dissolve=0.3)
    mk.shade(body, 30.0)
    return body


# --- The tanks ------------------------------------------------------------------------------------------------------

def tank_ring(p, t, sw=1.0, sh=1.0, inflate=0.0, segments=36):
    across = Vector((t.y, -t.x, 0.0)).normalized()     # to the right of the path
    up = Vector((0, 0, 1))
    ring = []
    for j in range(segments):
        a = 2 * math.pi * j / segments
        c, s = math.cos(a), math.sin(a)
        u = math.copysign(abs(c) ** (2 / TANK_P), c) * (TANK_W * sw + inflate)
        v = math.copysign(abs(s) ** (2 / TANK_P), s) * (TANK_H * sh + inflate)
        ring.append(p + across * u + up * v)
    return ring


def straight_tank(name, x, m):
    """A tank's straight run, from inside its hood down to the seam at the heart (a closed loft)."""
    rings = []
    ys = []
    y = TANK_TOP_Y
    while y > TANK_JOINT_Y + 1.0:
        ys.append(y)
        y -= 2.0
    ys.append(TANK_JOINT_Y)
    for y in ys:
        rings.append(tank_ring(Vector((x, y, TANK_Z)), Vector((0, -1, 0))))
    obj = k.loft(name, rings, m["t5"])
    k.smooth(obj, 50)
    return obj


def heart_outline():
    """The heart's plan (both halves) and which of its edges are open (the seams, where the tanks run on)."""
    pts = [(XE(c), YE(r)) for c, r in HEART_LEFT]
    right = [(MX(x), y) for x, y in reversed(pts[1:-1])]
    outline = pts + right
    open_edges = set()
    for i in range(len(outline)):
        a, b = outline[i], outline[(i + 1) % len(outline)]
        if abs(a[1] - TANK_JOINT_Y) < 1e-6 and abs(b[1] - TANK_JOINT_Y) < 1e-6:
            open_edges.add(i)
    return outline, open_edges


def heart_z(dist, x, y):
    """The heart's top: its rim rounded as the tanks are (their superellipse, from its outline in), the basin inside
    the rim lower, the two lobes over the turns a little higher."""
    d = dist(x, y)
    u = max(0.0, 1.0 - d / TANK_W)
    z = TANK_Z + TANK_H * (1.0 - u ** TANK_P) ** (1.0 / TANK_P)
    r0, r1, depth = HEART_BASIN
    z -= depth * smoothstep(r0, r1, d)
    c, r, rx, ry, lift = HEART_LOBE
    for cx in (XE(c), MX(XE(c))):
        z += lift * math.exp(-((x - cx) / rx) ** 2 - ((y - YE(r)) / ry) ** 2)
    return z


def heart(m):
    outline, open_edges = heart_outline()
    segs = [(outline[i], outline[(i + 1) % len(outline)]) for i in range(len(outline)) if i not in open_edges]

    def dist(x, y):
        best = 1e9
        for (ax, ay), (bx, by) in segs:
            vx, vy = bx - ax, by - ay
            t = max(0.0, min(1.0, ((x - ax) * vx + (y - ay) * vy) / (vx * vx + vy * vy + 1e-12)))
            best = min(best, math.hypot(x - ax - t * vx, y - ay - t * vy))
        return best
    obj = grid_prism("heart", ccw(outline), lambda x, y: heart_z(dist, x, y), lambda x, y: TANK_Z - 2.0, m["t5"],
                     step=0.9)
    k.smooth(obj, 60)
    return obj


def tanks(m):
    parts = [straight_tank("tank", TANK_X, m), straight_tank("tank_r", MX(TANK_X), m), heart(m)]
    for o in parts:
        paint_light(o, m, TANK_BANDS, under="t2")
    # The basin's floor darker (the heart's faces lower than its rim, inside it).
    r0, r1, depth = HEART_BASIN
    mk.paint(parts[2], lambda c, n: m["t2"] if c.z < TANK_Z + TANK_H - 0.6 * depth and n.z > 0.5 and
             c.y < TANK_JOINT_Y - 4.0 else None)
    # The seams where the tanks meet the heart: dark bands round them.
    for i, x in enumerate((TANK_X, MX(TANK_X))):
        band = k.loft(f"tank_seam{i}", [tank_ring(Vector((x, y, TANK_Z)), Vector((0, -1, 0)), inflate=0.22)
                                       for y in (TANK_JOINT_Y + 0.7, TANK_JOINT_Y - 0.5)], m["t2"])
        parts.append(k.smooth(band, 50))
    return parts


# --- The hoods ------------------------------------------------------------------------------------------------------

def hood_front(x, y):
    r0, z0, r1, z1 = HOOD_FRONT
    return linear(YE(r0), z0, YE(r1), z1)(y)


def hood_left(x, y):
    c0, z0, c1, z1 = HOOD_LEFT
    return linear(XE(c0), z0, XE(c1), z1)(x)


def hood_right(x, y):
    c0, z0, c1, z1 = HOOD_RIGHT
    return linear(XE(c0), z0, XE(c1), z1)(x)


def hood_z(x, y):
    """The (left) hood's unbevelled top over (x, y)."""
    return min(Z_HOOD, hood_front(x, y), hood_left(x, y), hood_right(x, y))


def torn_away(dmg, rows):
    """Cutters over the pixels the damaged sprites draw gone (in the side's own frame), rows r0..r1: for each run of
    rows, per row from outside the part to the last gone pixel, the inner edge ragged as the pixels are."""
    spans = []
    for r in range(rows[0], rows[1] + 1):
        cols = [c for c in range(120) if dmg.cell(XE(c) + 0.5, YE(r) - 0.5) == "-"]
        if cols:
            spans.append((r, min(cols), max(cols) + 1))
    runs = []
    for span in spans:
        if runs and span[0] == runs[-1][-1][0] + 1:
            runs[-1].append(span)
        else:
            runs.append([span])
    polys = []
    for run in runs:
        left = [(XE(c0) - 6.0, YE(r)) for r, c0, c1 in run] + [(XE(run[-1][1]) - 6.0, YE(run[-1][0] + 1))]
        right = []
        for r, c0, c1 in run:
            right += [(XE(c1), YE(r)), (XE(c1), YE(r + 1))]
        out = []
        for q in left + right[::-1]:      # no repeated points, none on a straight line between its neighbours
            if not out or abs(out[-1][0] - q[0]) > 1e-6 or abs(out[-1][1] - q[1]) > 1e-6:
                out.append(q)
        if abs(out[0][0] - out[-1][0]) < 1e-6 and abs(out[0][1] - out[-1][1]) < 1e-6:
            out.pop()
        clean = []
        for i, q in enumerate(out):
            a, b = out[i - 1], out[(i + 1) % len(out)]
            if abs((q[0] - a[0]) * (b[1] - a[1]) - (q[1] - a[1]) * (b[0] - a[0])) > 1e-6:
                clean.append(q)
        if len(clean) >= 3:
            polys.append(ccw(clean))
    return polys


def hood(m, dmg=None):
    body = mk.prism("hood", plan(HOOD_PLAN), HOOD_BOTTOM, 30.0, m["g8"])
    for i, top in enumerate((lambda x, y: Z_HOOD, hood_front, hood_left, hood_right)):
        mk.boolean(body, plane_box(f"hood_plane{i}", top), "INTERSECT")
    mk.cleanup(body)
    mk.bevel(body, 0.4, 2, 25.0)
    fy = Vector((0.0, -(HOOD_FRONT[1] - HOOD_FRONT[3]) / (YE(HOOD_FRONT[0]) - YE(HOOD_FRONT[2])), 1.0)).normalized()

    def pick(c, n):
        if n.z < -0.3:
            return m["dark"]
        if n.z > 0.97:
            return m["g8"]
        if n.dot(fy) > 0.97 and c.x < XE(42.0):
            return m["p7"]           # the purple skirt
        if n.dot(fy) > 0.97:
            return m["g6"]
        if n.x < -0.2:
            return m["g4"]           # the left chamfer
        if n.y < -0.5:
            return m["p4"]           # the skirt's foot
        return m["dark"]             # the right flank
    mk.paint(body, pick)
    # The three red vents across its back (rows 1-5) and the grille under them (two slots across, one down).
    cutters = []
    for i, (c0, c1) in enumerate(VENTS):
        cutters.append(mk.box(f"hood_vent{i}", XE(c0), XE(c1), YE(VENT_ROWS[1]), YE(VENT_ROWS[0]) + 2.0,
                              Z_HOOD - 1.0, Z_HOOD + 3.0, m["vent"]))
    for i, (r0, r1) in enumerate(GRILLE_ROWS):
        cutters.append(mk.box(f"hood_grille{i}", XE(GRILLE_COLS[0]), XE(GRILLE_COLS[1]), YE(r1), YE(r0),
                              Z_HOOD - 0.6, Z_HOOD + 3.0, m["black"]))
    c0, c1, r0, r1 = GRILLE_DOWN
    cutters.append(mk.box("hood_grille_down", XE(c0), XE(c1), YE(r1), YE(r0), Z_HOOD - 0.6, Z_HOOD + 3.0, m["black"]))
    for i, torn in enumerate(torn_away(dmg, (0, 30)) if dmg is not None else []):
        cutters.append(mk.prism(f"hood_torn{i}", torn, HOOD_BOTTOM - 2.0, Z_HOOD + 3.0, m["black"]))
    for c in cutters:
        mk.boolean(body, c, "DIFFERENCE")
    mk.cleanup(body, dissolve=0.0)
    mk.shade(body, 30.0)
    parts = [body]
    # The slats in the vents (their floors glow dull red), lit along their tops.
    for i, (c0, c1) in enumerate(VENTS):
        for j in range(2):
            cx = XE(c0) + (j + 1) * (XE(c1) - XE(c0)) / 3
            slat = bevelled_box(f"hood_slat{i}_{j}", cx - 0.22, cx + 0.22, YE(VENT_ROWS[1]) + 0.2, YE(VENT_ROWS[0]),
                                Z_HOOD - 1.0, Z_HOOD - 0.25, m["g6"], 0.08, 1)
            parts.append(slat)
    # The collar where the tank goes in under the hood.
    collar = k.loft("tank_collar", [tank_ring(Vector((TANK_X, y, TANK_Z)), Vector((0, -1, 0)), inflate=0.45)
                                    for y in (YE(15.4), YE(17.2), YE(18.2), YE(19.0))], m["g8"])
    k.smooth(collar, 40)
    paint_faces(collar, m, "gb", "g6", lit="g8", top_min=0.8, lit_min=0.6)
    parts.append(collar)
    return parts


# --- The tanks' fittings ------------------------------------------------------------------------------------------

def tank_surface_z(x, inflate=0.0):
    """The left tank's top over x (its straight run), inflate out from its surface."""
    u = min(1.0, abs(x - TANK_X) / (TANK_W + inflate))
    return TANK_Z + (TANK_H + inflate) * (1.0 - u ** TANK_P) ** (1.0 / TANK_P)


def sleeve(name, x0, x1, y0, y1, lift, mat, step=1.0):
    """A plate curved over the left tank's straight run between columns x0..x1 and y0..y1, lift above its surface (a
    shell 0.45 thick)."""
    rings = []
    y = y0
    ys = []
    while y < y1 - 1e-6:
        ys.append(y)
        y += step
    ys.append(y1)
    for y in ys:
        top, bottom = [], []
        n = max(4, int((x1 - x0) / 0.8))
        for i in range(n + 1):
            x = x0 + (x1 - x0) * i / n
            top.append(Vector((x, y, tank_surface_z(x, lift + 0.45))))
            bottom.append(Vector((x, y, tank_surface_z(x, lift) - 0.3)))
        rings.append(top + bottom[::-1])
    obj = k.loft(name, rings, mat)
    return obj


def tank_fittings(m, dmg=None):
    parts = []
    # The clamp round the tank (rows 28-44): a band, four plates on it (its grid).
    band = sleeve("clamp_band", XE(32.6), XE(49.6), YE(44.8), YE(27.8), 0.1, m["g4"])
    paint_faces(band, m, "g6", "g4", lit="g6", top_min=0.9, lit_min=0.7)
    k.smooth(band, 35)
    parts.append(band)
    for i, (c0, c1) in enumerate(CLAMP_COLS):
        for j, (r0, r1) in enumerate(CLAMP_ROWS):
            plate = sleeve(f"clamp_plate{i}{j}", XE(c0), XE(c1), YE(r1), YE(r0), 0.55, m["g8"])
            paint_faces(plate, m, "g8", "g6", lit="gb", top_min=0.95, lit_min=0.75)
            k.smooth(plate, 35)
            parts.append(plate)
    # The ribbed panel on the tank's upper left (rows 57-71) and its ribs.
    panel = sleeve("rib_panel", XE(RIBS[0]), XE(RIBS[1]), YE(RIBS[3]), YE(RIBS[2]), 0.1, m["g4"])
    paint_faces(panel, m, "g4", "dark", top_min=0.9)
    parts.append(k.smooth(panel, 35))
    for i, r in enumerate(RIB_ROWS):
        if smashed(dmg, (XE(RIBS[0]) + XE(RIBS[1])) / 2, YE(r), 0.5):
            continue
        rib = sleeve(f"rib{i}", XE(RIBS[0]) + 0.3, XE(RIBS[1]) - 0.3, YE(r + 0.5), YE(r - 0.5), 0.5, m["g8"], step=0.25)
        paint_faces(rib, m, "g9", "g6", lit="gb", top_min=0.95, lit_min=0.7)
        parts.append(k.smooth(rib, 35))
    # The rail along the tank's inner side (column 54, rows 43-59) on two brackets.
    x = XE(54.5)
    rail = mk.tube("tank_rail", [(x, YE(42.8), TANK_Z + 1.6), (x, YE(59.2), TANK_Z + 1.6)], 0.85, m["g6"], 10)
    paint_faces(rail, m, "g9", "g6", lit="gb", top_min=0.8, lit_min=0.6)
    parts.append(k.smooth(rail, 50))
    for i, r in enumerate((43.6, 58.4)):
        bracket = bevelled_box(f"rail_bracket{i}", XE(52.4), x + 0.5, YE(r) - 0.5, YE(r) + 0.5, TANK_Z,
                               TANK_Z + 1.9, m["g4"], 0.15, 1)
        parts.append(paint_faces(bracket, m, "g6", "g4", top_min=0.9))
    return parts


# --- The masts ------------------------------------------------------------------------------------------------------

def lathe_axis(name, profile, base, direction, mat, segments=16):
    """A turned part along an axis from base in direction: profile [(t, radius)] along it."""
    d = Vector(direction).normalized()
    ref = Vector((1, 0, 0)) if abs(d.x) < 0.9 else Vector((0, 1, 0))
    a = d.cross(ref).normalized()
    b = d.cross(a).normalized()
    rings = []
    for t, r in profile:
        c = Vector(base) + d * t
        rings.append([c + (a * math.cos(2 * math.pi * j / segments) + b * math.sin(2 * math.pi * j / segments)) *
                      max(r, 0.01) for j in range(segments)])
    return k.loft(name, rings, mat, start_point=Vector(base) + d * profile[0][0],
                  end_point=Vector(base) + d * profile[-1][0])


def mast_frame(col, foot_row, tip_row, foot_z, tip_z):
    """A mast's axis: from its foot (row, height) to its tip; returns (base, direction, scale) where t along the axis
    reaches row r at t = (foot_row - r) * scale."""
    base = Vector((XE(col), YE(foot_row), foot_z))
    tip = Vector((XE(col), YE(tip_row), tip_z))
    d = (tip - base)
    return base, d.normalized(), d.length / (foot_row - tip_row)


def mast_parts(name, col, rows, foot_row, tip_row, foot_z, tip_z, valve, m):
    """A turned mast from its profile [(row, radius)] (foot to tip), a valve on its outer side (row, radius), its
    beads dark."""
    base, d, s = mast_frame(col, foot_row, tip_row, foot_z, tip_z)
    profile = []
    for (ra, rada), (rb, radb) in zip(rows, rows[1:]):
        steps = max(1, int(round(abs(ra - rb) * 2)))
        for i in range(steps):
            f = i / steps
            profile.append(((foot_row - (ra + (rb - ra) * f)) * s, rada + (radb - rada) * f))
    profile.append(((foot_row - rows[-1][0]) * s, rows[-1][1]))
    body = lathe_axis(name, profile, base, d, m["g6"], 16)
    k.smooth(body, 45)
    paint_faces(body, m, "g6", "g4", lit="g9", top_min=0.85, lit_min=0.55)
    parts = [body]
    if valve is None:
        return parts
    vr, vrad, off = valve
    t = (foot_row - vr) * s
    centre = base + d * t + Vector((-off, 0, 0))
    v = mk.ball(name + "_valve", tuple(centre), (vrad, vrad * 1.35, vrad), m["g6"], 16, 8)
    paint_faces(v, m, "g6", "g4", lit="g9", top_min=0.85, lit_min=0.55)
    stem = mk.tube(name + "_valve_stem", [tuple(base + d * t), tuple(centre)], 0.7, m["g4"], 8)
    parts += [v, stem]
    return parts


def mast_foot(m):
    """Mast A's foot: a block on the wing (wider than the mast, as the sprite draws it), its top sloping up with the
    mast, its edges rounded."""
    c0, c1, r0, r1, over = MAST_A_FOOT
    base, d, s = mast_frame(MAST_A_COL, 80.6, 28.6, MAST_A_Z[0], MAST_A_Z[1])
    top = lambda x, y: base.z + over + (y - base.y) * d.z / d.y  # noqa: E731
    foot = mk.wedge("mast_a_foot", plan([(c0, r0), (c1, r0), (c1, r1), (c0, r1)]), Z_RIM - 1.0, top, m["g6"])
    mk.bevel(foot, 0.5, 2, 30.0)
    paint_faces(foot, m, "g6", "g4", lit="g9", top_min=0.9, lit_min=0.55)
    return mk.shade(foot, 35.0)


def masts(m, dmg=None):
    parts = []
    parts += mast_parts("mast_a", MAST_A_COL, MAST_A, 80.6, 28.6, MAST_A_Z[0], MAST_A_Z[1], MAST_A_VALVE, m)
    parts.append(mast_foot(m))
    rows, valve = MAST_B, MAST_B_VALVE
    if dmg is not None and dmg.mirror:
        # The outer mast's casing blown off its core where the damaged sprite draws it gone (rows 58-70), a torn
        # stump of it left at its foot.
        r0, r1 = MAST_B_TORN
        rows = [(r, rad if not (r1 > r > r0) else min(rad, 1.0)) for r, rad in rows]
        rows = sorted(rows + [(r1 - 0.01, 2.7), (r1 - 0.6, 1.0), (r0 + 0.01, 1.0)], key=lambda p: -p[0])
        valve = None
        # Shards of the wing's purple plating torn up between the masts' feet, as the damaged sprite draws them.
        for i, (c0, c1, r0, r1, z0, tilt) in enumerate(SHARDS):
            shard = bevelled_box(f"mast_shard{i}", XE(c0), XE(c1), YE(r1), YE(r0), -0.35, 0.35, m["p7"], 0.15, 1)
            cx, cy = (XE(c0) + XE(c1)) / 2, (YE(r0) + YE(r1)) / 2
            shard.data.transform(Matrix.Translation((cx, cy, z0)) @ Matrix.Rotation(tilt, 4, "X") @
                                 Matrix.Rotation(0.35, 4, "Y") @ Matrix.Translation((-cx, -cy, 0)))
            paint_faces(shard, m, "p7", "p4", lit="pa", top_min=0.85, lit_min=0.6)
            parts.append(shard)
    parts += mast_parts("mast_b", MAST_B_COL, rows, 81.4, 44.6, MAST_B_Z[0], MAST_B_Z[1], valve, m)
    return parts


# --- The lamps -------------------------------------------------------------------------------------------------------

def lamp(m):
    """The blue lamp against the left tank's outer side: half an ellipsoid of glowing glass, its glint at its upper
    left."""
    cx, cy, cz, rx, ry, rz = LAMP
    obj = mk.ball("lamp", (XE(cx), YE(cy), cz), (rx, ry, rz), m["lamp"], 28, 12)
    values = []
    for v in obj.data.vertices:
        dx, dy = (v.co.x - XE(cx)) / rx, (v.co.y - YE(cy)) / ry
        g = math.hypot((dx + 0.42) / 0.4, (dy - 0.18) / 0.45)
        values.append(1.0 - g)
    band_split(obj, values, [(-99.0, m["lamp"]), (0.0, m["lamp_hot"])])
    mk.paint(obj, lambda c, n: m["dark"] if n.z < -0.5 else None)
    k.smooth(obj, 70)
    # Its purple mount along the tank's side, under it and on down to the deck.
    mount = mk.wedge("lamp_mount", plan(LAMP_MOUNT), 0.0, lambda x, y: 5.6 + 0.35 * (x - XE(28.0)), m["p7"])
    mk.bevel(mount, 0.3, 2, 30.0)
    paint_faces(mount, m, "pa", "p4", lit="pa", top_min=0.9, lit_min=0.6)
    return [obj, mk.shade(mount, 35.0)]


# --- The hull's fittings -------------------------------------------------------------------------------------------

def port_shot(dmg):
    c0, c1, r0, r1, h = PORT_HOUSING
    return smashed(dmg, (XE(c0) + XE(c1)) / 2 - 1.5, (YE(r0) + YE(r1)) / 2, 0.55)


def hull_fittings(m, dmg=None):
    """The ribbed rails along the wing's crease, the ribs across the wing, the gun port's housing (left; mirrored).
    Damaged: the rails broken where smashed, the housing gone where the port is smashed."""
    parts = []
    for i, (c, r0, r1) in enumerate(CREASE_RAILS):
        x0 = XE(c)
        lengths = [(r0, r1)]
        if dmg is not None:     # in lengths of 2 pixels, those smashed gone
            lengths = [(r, min(r + 2.0, r1)) for r in [r0 + 2.0 * j for j in range(int(math.ceil((r1 - r0) / 2.0)))]]
            lengths = [(a, b) for a, b in lengths if not smashed(dmg, x0 + 0.5, YE((a + b) / 2), 0.45)]
        for j, (a, b) in enumerate(lengths):
            rail = bevelled_box(f"crease_rail{i}_{j}", x0, x0 + 1.0, YE(b), YE(a), Z_DECK - 0.4, Z_DECK + 0.55,
                                m["g9"], 0.25, 2)
            parts.append(paint_faces(rail, m, "gb", "g6", lit="gb", top_min=0.9, lit_min=0.5))
    for i, r in enumerate(WING_RIBS):
        pts = []
        for j in range(13):
            x = XE(5.2) + (XE(WING_EDGE) - XE(5.2)) * j / 12
            pts.append((x, YE(r + 0.5), hull_top(x, YE(r + 0.5)) + 0.05))
        rib = mk.tube(f"wing_rib{i}", pts, 0.42, m["pa"], 8)
        parts.append(paint_faces(k.smooth(rib, 50), m, "pa", "p7", lit="pa", top_min=0.8, lit_min=0.6))
    # The gun port's housing (columns 24-33, rows 84-96): a raised block, a pit for the hatch in its top.
    if port_shot(dmg):
        return parts
    c0, c1, r0, r1, h = PORT_HOUSING
    housing = bevelled_box("port_housing", XE(c0), XE(c1), YE(r1), YE(r0), Z_DECK - 1.0, Z_DECK + h, m["g9"], 0.35)
    c0, c1, r0, r1 = PORT_PIT
    pit = mk.box("port_pit", XE(c0), XE(c1), YE(r1), YE(r0), PORT_FLOOR, Z_DECK + 3.0, m["black"])
    mk.boolean(housing, pit, "DIFFERENCE")
    mk.cleanup(housing, dissolve=0.0)
    paint_faces(housing, m, "g9", "g6", lit="gb", top_min=0.9, lit_min=0.6, keep=("black",))
    parts.append(mk.shade(housing, 35.0))
    return parts


# The gun port's looks: the hatch's slide (towards the tank, into the housing) and the fire in the pit (layers of
# material, radius); the frames of the left port (117: 117 195 233 271 197 235 273 and back) and of the right one
# (121: 121 199 237 275 201 and back: the sprites draw no hatch sliding there, only the fire growing in the dark).
PORT_STATES = {"shut": (0.0, []), "slide2": (2.0, []), "slide4": (4.0, []), "dim": (6.0, [("glow1", 1.1)]),
               "red": (7.6, [("glow2", 1.7)]), "orange": (7.6, [("glow3", 2.3), ("core3", 1.25)]),
               "white": (7.6, [("glow4", 2.9), ("core4", 1.8)])}
LEFT_PORT_FRAMES = {195: "slide2", 233: "slide4", 271: "dim", 197: "red", 235: "orange", 273: "white"}
RIGHT_PORT_FRAMES = {199: "dim", 237: "red", 275: "orange", 201: "white"}
# The barrels' lamps: 156 (158) red, 191 and 229 (193, 231) hotter, 267 (269) hottest.
LAMP_FRAMES = {191: ("lamp_l", "red_hot", 156), 267: ("lamp_l", "red_hotter", 156),
               193: ("lamp_r", "red_hot", 158), 269: ("lamp_r", "red_hotter", 158)}


def port_parts(m, state, dmg=None):
    """The left port's hatch and the fire in its pit, as `state` draws them (none where it is smashed)."""
    if port_shot(dmg):
        return []
    slide, fire = PORT_STATES[state]
    parts = [port_hatch(m, slide)]
    c0, c1, r0, r1 = PORT_PIT
    cx, cy = XE((c0 + c1) / 2), YE((r0 + r1) / 2)
    for i, (name, r) in enumerate(fire):
        ball = mk.ball(f"port_fire{i}", (cx, cy, PORT_FLOOR + 0.1 * i), (r, r * 1.1, r * 0.75), m[name], 24, 10)
        parts.append(k.smooth(ball, 80))
    return parts


def port_hatch(m, slide):
    """The port's hatch slid `slide` towards the tank (into the housing)."""
    c0, c1, r0, r1 = PORT_PIT
    h = PORT_HOUSING[4]
    hatch = bevelled_box("port_hatch", XE(c0) + 0.1 + slide, XE(c1) - 0.1 + slide, YE(r1) + 0.1, YE(r0) - 0.1,
                         Z_DECK + h - 0.75, Z_DECK + h - 0.2, m["g9"], 0.18, 2)
    paint_faces(hatch, m, "gb", "g6", lit="gb", top_min=0.9, lit_min=0.6)
    return hatch


def hull_cuts(m, body, top=hull_top):
    """The scoop, the panel lines, the barrels' slots cut into the hull (both halves); top: the hull's surface the
    panel lines follow."""
    cutters = []
    cx, cy, ax, ay, ang, depth = SCOOP
    for side in (1, -1):
        pts = []
        for j in range(28):
            a = 2 * math.pi * j / 28
            u, v = ax * math.cos(a), ay * math.sin(a)
            x = u * math.cos(ang) - v * math.sin(ang)
            y = u * math.sin(ang) + v * math.cos(ang)
            px = XE(cx) + x
            pts.append((px if side > 0 else MX(px), YE(cy) + y))
        cutters.append(mk.prism(f"scoop{side}", ccw(pts), Z_DECK - depth, Z_DECK + 3.0, m["g6"]))
    for i, (c0, c1, r0, r1) in enumerate(GROOVES):
        for side in (1, -1):
            x0, x1 = (XE(c0), XE(c1)) if side > 0 else (MX(XE(c1)), MX(XE(c0)))
            cutters.append(mk.box(f"groove{i}{side}", x0, x1, YE(r1), YE(r0), -1.0, 9.0, m["g4"]))
    c0, c1, r0, r1, depth = SLOT
    for side in (1, -1):
        x0, x1 = (XE(c0), XE(c1)) if side > 0 else (MX(XE(c1)), MX(XE(c0)))
        cutters.append(mk.box(f"slot{side}", x0, x1, YE(r1), YE(r0), Z_DECK - depth, Z_DECK + 3.0, m["black"]))
    # The arc round the deck's front, following the bowl (from the wing's crease to the barrel's slot).
    rho, c0, c1, half = ARC
    row0, a, b, p = FRONT
    pts = []
    for i in range(41):
        x = XE(c0) + (XE(c1) - XE(c0)) * i / 40
        u = abs(x - AX) / a
        dy = b * max(0.0, rho ** p - u ** p) ** (1.0 / p)
        pts.append(Vector((x, YE(row0) - dy)))
    strip = []
    for i, q in enumerate(pts):
        t = (pts[min(i + 1, 40)] - pts[max(i - 1, 0)]).normalized()
        nrm = Vector((-t.y, t.x))
        strip.append((q + nrm * half, q - nrm * half))
    for side in (1, -1):
        outline = [s[0] for s in strip] + [s[1] for s in reversed(strip)]
        outline = [(o.x if side > 0 else MX(o.x), o.y) for o in outline]
        arc = mk.prism(f"groove_arc{side}", ccw(outline), -1.0, 9.0, m["g4"])
        arc.name = f"groove_arc{side}"
        cutters.append(arc)
    for c in cutters:
        groove_depth = 0.45
        if c.name.startswith("groove"):
            # a shallow groove: only as deep as groove_depth under the surface over it
            for v in c.data.vertices:
                if v.co.z < 0:
                    v.co.z = top(v.co.x, v.co.y) - groove_depth
            c.data.update()
        mk.boolean(body, c, "DIFFERENCE")
    mk.cleanup(body, dissolve=0.0)
    return body


# --- The machinery in the U, the guns ---------------------------------------------------------------------------------

def machinery(m):
    parts = []
    for i, (c0, c1, r0, r1, z1, bev) in enumerate(BLOCKS):
        block = bevelled_box(f"block{i}", XE(c0), XE(c1), YE(r1), YE(r0), TANK_Z, z1, m["g8"], bev)
        paint_faces(block, m, "g8", "g4", lit="g9", top_min=0.9, lit_min=0.55)
        parts.append(mk.shade(block, 35.0))
    # The vent's louvres, the grid plate's slots, the seam across the block: dark grooves across their tops.
    for i, (b, c0, c1, r0, r1) in enumerate(BLOCK_SLOTS):
        z = BLOCKS[b][4]
        slot = mk.box(f"block_slot{i}", XE(c0), XE(c1), YE(r1), YE(r0), z - 0.45, z + 2.0, m["black"])
        mk.boolean(parts[b], slot, "DIFFERENCE")
    for obj in parts:
        mk.cleanup(obj, dissolve=0.0)
        mk.shade(obj, 35.0)
    return parts


def guns(m, dmg=None):
    """The barrel lying in its slot (the left one) and the socket at its muzzle for its lamp (lamp_lens)."""
    left = []
    bx = XE(BARREL_COL)
    y0, y1 = YE(BARREL_ROWS[1]), YE(BARREL_ROWS[0])
    if smashed(dmg, bx, (y0 + y1) / 2, 0.45):
        y0 = YE(BARREL_BROKEN)       # broken off, a stub left at its back
    z = BARREL_Z
    barrel = lathe_axis("barrel", [(0.0, 0.01), (0.15, 1.35), (y1 - y0 - 0.6, 1.35), (y1 - y0 - 0.3, 1.0),
                                   (y1 - y0, 0.01)], (bx, y0, z), (0, 1, 0), m["g8"], 14)
    k.smooth(barrel, 50)
    paint_faces(barrel, m, "gb", "g6", lit="gb", top_min=0.8, lit_min=0.5)
    left.append(barrel)
    sx, sy, sr = XE(BARREL_COL), YE(LAMP_ROW), SOCKET_R
    socket = mk.lathe("socket", [(sr + 0.4, Z_DECK - 1.0), (sr + 0.4, Z_DECK + 0.6), (sr + 0.1, Z_DECK + 1.0),
                                 (sr - 0.4, Z_DECK + 1.0), (sr - 0.5, Z_DECK + 0.6), (0.01, Z_DECK + 0.4)],
                      (sx, sy), m["g8"], 24, squash=(1.0, 1.3))
    k.smooth(socket, 40)
    paint_faces(socket, m, "gb", "g6", lit="gb", top_min=0.8, lit_min=0.5)
    left.append(socket)
    return left


def chin(m, dmg=None):
    """The raised chin between the barrels (built whole; smashed away in the damaged look)."""
    c0, c1, r0, r1, h = CHIN
    if smashed(dmg, (XE(c0) + XE(c1)) / 2, (YE(r0) + YE(r1)) / 2, 0.55):
        return []
    obj = bevelled_box("chin", XE(c0), XE(c1), YE(r1), YE(r0), Z_DECK - 0.5, Z_DECK + h, m["g9"], 0.6, 3)
    paint_faces(obj, m, "g9", "g6", lit="gb", top_min=0.9, lit_min=0.55)
    return [mk.shade(obj, 35.0)]


def lamp_lens(m, mat):
    """The (left) barrel's red lamp: a lens in its socket."""
    sx, sy, sr = XE(BARREL_COL), YE(LAMP_ROW), SOCKET_R
    return mk.dome("lamp_lens", (sx, sy), (sr - 0.45, (sr - 0.45) * 1.3, 0.9), Z_DECK + 0.45, m[mat], 20, 6)


# --- The whole -------------------------------------------------------------------------------------------------------

INTACT = {"port_l": "shut", "port_r": "shut", "lamp_l": "red", "lamp_r": "red", "damaged": False}
GLOWING = ("lamp", "lamp_hot", "glow1", "glow2", "glow3", "glow4", "core3", "core4", "red", "red_hot", "red_hotter",
           "vent")


def build_side(m, port, lamp_mat, dmg):
    """The parts of the boss's left half (the right half is built so and mirrored): the hood, the tank's fittings,
    the masts, the lamp, the hull's fittings, the gun port, the barrel and its lamp; dmg: their damaged look (read on
    the right half for the right one's)."""
    parts = hood(m, dmg) + tank_fittings(m, dmg) + masts(m, dmg) + lamp(m) + hull_fittings(m, dmg)
    parts += guns(m, dmg) + [lamp_lens(m, lamp_mat)] + port_parts(m, port, dmg)
    if dmg is not None:
        char(parts, m, dmg, keep=GLOWING)
    return parts


def inside(poly, x, y):
    hit = False
    for i in range(len(poly)):
        (ax, ay), (bx, by) = poly[i], poly[(i + 1) % len(poly)]
        if (ay > y) != (by > y) and x < ax + (y - ay) * (bx - ax) / (by - ay):
            hit = not hit
    return hit


def damage_surface(dmg):
    """surface(x, y): the height of the damaged boss's plating at (x, y) for the embers and the debris (the hull
    pressed in, the hoods), or None where they do not go (on the tanks and the heart, off the boss, torn away)."""
    hull_plan = whole_plan(HULL_LEFT)
    heart_plan = heart_outline()[0]
    hood_l = plan(HOOD_PLAN)
    hood_r = [(MX(x), y) for x, y in hood_l]
    top = hull_surface(dmg)

    def surface(x, y):
        for tx in (TANK_X, MX(TANK_X)):
            if abs(x - tx) < TANK_W + 0.4 and TANK_JOINT_Y - 0.5 < y < TANK_TOP_Y:
                return None
        if inside(heart_plan, x, y):
            return None
        if inside(hood_l, x, y):
            return hood_z(x, y)
        if inside(hood_r, x, y):
            return None if dmg.cell(x, y) == "-" else hood_z(MX(x), y)
        if inside(hull_plan, x, y):
            return top(x, y)
        return None
    return surface


def build_whole(state=None):
    """The whole boss as `state` draws it (INTACT's keys: the ports' looks, the barrels' lamps, the damaged look)."""
    state = dict(INTACT, **(state or {}))
    m = materials()
    dmg = Damage() if state["damaged"] else None
    body = hull(m, dmg)
    hull_cuts(m, body, hull_surface(dmg))
    if dmg is not None:
        char([body], m, dmg)
    mk.shade(body, 30.0)
    parts = [body] + tanks(m)
    centre = machinery(m) + chin(m, dmg)
    if dmg is not None:
        char(centre, m, dmg)
    parts += centre
    parts += build_side(m, state["port_l"], state["lamp_l"], dmg)
    parts += mirrored(build_side(m, state["port_r"], state["lamp_r"], Damage(mirror=True) if dmg else None))
    if dmg is not None:
        surface = damage_surface(dmg)
        parts += debris(m, dmg, surface) + embers(m, dmg, surface)
    whole = [o for o in mk.meshes() if len(o.data.polygons) > 0]
    for obj in whole:
        mk.apply(obj)
    triangulate(whole)
    bpy.context.view_layer.update()
    return whole, m


# --- Checks, previews, export -----------------------------------------------------------------------------------------

def whole_mask(sheet, mapping=None):
    """The picture's pixels (the sprites placed as the events place them): 120 x 140."""
    mapping = mapping or {}
    mask = [[False] * 120 for _ in range(140)]
    for s, (c0, r0) in CELLS.items():
        for r, row in enumerate(piece_mask(sheet, mapping.get(s, s), s)):
            for c, v in enumerate(row):
                if v:
                    mask[r0 + r][c0 + c] = True
    return mask


def jobs():
    """What to build: (state, [(model, sprite of its look, piece's sprite)]) for the intact boss, the ports' and the
    lamps' frames and the damaged look."""
    out = [(INTACT, [(f"camanis_boss_{s}", s, s) for s in CELLS])]
    for s, st in LEFT_PORT_FRAMES.items():
        out.append(({"port_l": st}, [(f"camanis_boss_{s}", s, 117)]))
    for s, st in RIGHT_PORT_FRAMES.items():
        out.append(({"port_r": st}, [(f"camanis_boss_{s}", s, 121)]))
    for s, (key, mat, piece) in LAMP_FRAMES.items():
        out.append(({key: mat}, [(f"camanis_boss_{s}", s, piece)]))
    out.append(({"damaged": True}, [(f"camanis_boss_{DAMAGED[s]}", DAMAGED[s], s) for s in CELLS
                                    if s not in SAME_WHEN_DAMAGED]))
    return out


def piece_mask(sheet, sprite, piece):
    """The sprite's pixels in its piece's box (the top row's damaged sprites are drawn a pixel higher: read a row
    lower)."""
    mask = k.sprite_mask(sheet, sprite)
    if sprite in (12, 14, 16, 18):
        mask = [[False] * 24] + mask[:-1]
    return mask


def export_piece(whole, m, name, sprite, piece, options, sheet):
    box = box_of(piece)
    parts = [p for p in (cut(src, box, m["dark"]) for src in whole) if p is not None]
    drop_unused(parts)
    mk.transform(parts, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
    bpy.context.view_layer.update()
    triangulate(parts)
    if options.get("stats") == "1":
        for obj in sorted(parts, key=lambda o: -mk.triangles([o]))[:10]:
            print("    %-22s %6d" % (obj.name, mk.triangles([obj])))
    parts = [join(parts, name)]
    parts[0].data.name = name
    for src in whole:
        src.hide_render = True
    if sheet:
        mk.compare("%s (b %d)" % (name, sprite), mk.coverage(parts, 24, 28), piece_mask(sheet, sprite, piece))
    mk.report(name, parts, os.path.join(mk.outdir(options), name + ".glb"))
    if "preview" in options and options.get("pieces") == "1":
        mk.preview(options["preview"] + name, parts)
    for obj in parts:
        data = obj.data
        bpy.data.objects.remove(obj)
        if data.users == 0:
            bpy.data.meshes.remove(data)
    for src in whole:
        src.hide_render = False


def build():
    options = k.args()
    only = options["only"].split(",") if "only" in options else None
    sheet = None
    if "check" in options:
        sheets = options["check"]
        sheet = os.path.join(sheets, "enemy_B.png") if os.path.isdir(sheets) else sheets
    for state, pieces in jobs():
        if only is not None:
            pieces = [p for p in pieces if p[0] in only]
            wanted = (state is INTACT or state.get("damaged")) and ("whole" in options or "preview" in options)
            if not pieces and not wanted:
                continue
        k.reset()
        whole, m = build_whole(state)
        low, high = mk.bounds(whole)
        label = "damaged" if state.get("damaged") else ", ".join("%s %s" % kv for kv in state.items()
                                                                   if kv[1] != INTACT[kv[0]]) or "intact"
        print("== whole boss (%s): %d triangles, %d objects, %d materials, x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (
            label, mk.triangles(whole), len(whole), len(mk.materials_of(whole)), low.x, high.x, low.y, high.y, low.z,
            high.z))
        bpy.context.scene.view_settings.view_transform = "Standard"
        if state is INTACT or state.get("damaged"):
            suffix = "_damaged" if state.get("damaged") else ""
            if sheet:
                mapping = DAMAGED if state.get("damaged") else None
                mk.compare("whole%s" % suffix, mk.coverage(whole, 120, 140), whole_mask(sheet, mapping))
            if "preview" in options:
                mk.preview(options["preview"] + "camanis_boss_whole" + suffix, whole, size=(120, 140), scale=6,
                           distance=3.5)
            if "whole" in options:
                path = options["whole"]
                mk.export(whole, path.replace(".glb", suffix + ".glb"))
        for name, sprite, piece in pieces:
            export_piece(whole, m, name, sprite, piece, options, sheet)


if __name__ == "__main__":
    build()
