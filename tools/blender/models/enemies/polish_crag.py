"""The huge asteroid of ASTEROID1 and ASTEROIDS, polished (2026-10-21, round 26; it replaces wave3_j_rocks.py's crag,
smooth boulders packed on a low base). Sheet D, 72 x 84 pixels, which the game puts together from ten sprites (models
crag_<sprite>, drawn at their own origin): six 2x2 (13, 49, 51, 53, 89, 91) and four 1x1 (15, 31, 34, 88), at the
picture's columns and rows as the sheet lays them out (its columns 10-15, rows 0-5).

PLACEMENT (the level events, tools/content/tyrevents.py; the enemy data, tools/content/tyrdata.py)

Each sprite is an enemy of its own (armour 50, one frame, not animated, no damaged look (dgr 0), no launches), the ten
sharing one link number, so that shooting one away destroys them all (a piece never shows alone in the levels):
- ASTEROID1 (episode 1, enemies 444-453 = D 31, 13, 15, 34, 49, 51, 53, 88, 89, 91): eight times, by event 6 (ground)
  at clock 10 (still on the ground), 300, 1200, 1250, 1720, 2240 and 2420 (drifting down a pixel a tick faster than the
  ground, vy+1), and once by event 7 (top layer) at clock 1270 (vy+1; layer 3 stands still in ASTEROID1, so it drifts
  down a pixel a tick). The events give each part x = d2, y = -28 + d5: 49 at (x, -56), 13 at (x + 24, -84), 15 at
  (x + 42, -91), 31 at (x + 6, -77), 34 at (x + 42, -77), 51 (x + 24, -56), 53 (x + 48, -56), 88 (x + 6, -35), 89
  (x + 24, -28), 91 (x + 48, -28); with the 2x2 sprites drawn from (x - 6, y - 7) and the 1x1 ones from (x, y) (no
  event 26 in these levels) every sprite lands where the sheet has it: the picture whole.
- ASTEROIDS (episode 5, enemies 1111-1120, the same sprites and data): six times on the ground (event 6 at 110, 410,
  710, 1210, 2210, 2410; no vy: lying on the ground, scrolling with it).
- No episode 6 level places it (none takes a wave or a boss of ASTEROID1 or ASTEROIDS, and GREY MOON's ground objects,
  copied from ASTEROID1, ASTEROID2 and AST ROCK by waves.Source.ground_objects, are only their still enemies standing
  on the tile grid, which no crag piece does), but the side-scrolling levels line the window's edges with single
  pieces (src/layer3d.c decor_sets: crag_13, 31, 49 and 88 with the lumpy asteroid for MIGRATION's asteroids; 15, 34,
  51, 53, 89 and 91 for GRAVITRON's crags), each piece alone, turned at random, 1.3-2.3 times its size: there their
  cut faces show.
- No other enemy shows any of these sprites (catalog.json; none is launched) and none is another sprite's pixels
  mirrored, turned or in other ramps (it is the only 72 x 84 rock; the big asteroids D 1/3/39/41 and 7/9/45/47 are
  other pictures): no frame models, no twins.

How high it is drawn (src/layer3d.c's layer heights, render_gpu.c): a ground piece drawn at its own origin stands on
the ground enemies' layer, 4 pixels over the ground (plus the terrain's lift under the pieces' middle: 0 here);
ASTEROID1's terrain is flat with holes (tools/terrain/levels.json: no heights, void "hole") and the crag mostly
crosses black space there, floating over the void; ASTEROIDS has no terrain (tools/terrain/levels.json) and its ground
is black space (map index 71) but for a few small rocks of tiles, under the first crag's corner. On the top layer
(ASTEROID1 at 1270) the base is at 38 + 36 (the terrain's headroom, ASTEROID1 having a terrain) = 74, only 6 pixels
under the player's plane (80); this rock stands 12.4 high (drawn 1.02 times larger there), so its upper half rises
through the player's plane: where the ship meets it (contact hurts: explosion type 28, and the ten die together when
one is shot) the rock passes over the ship and hides it (the big asteroids do the same on that layer, 12.8 high). The
rock is kept as high as its family rather than flattened for that one passage (6 pixels would make a pancake of it on
the ground); height=-4 on its sprite lines would lower the base to 70 there (the rock then rising 2.6 pixels over the
player's plane), at the cost of the ground crags hovering at the terrain's height instead of 4 pixels over it (they
drift over ASTEROID1's void, so that would show only where one crosses a platform, its flat bottom sliding along it).
The camera: every layer's plane is scaled about the point under the camera (354 pixels over the player's plane) so
that it shows its sprites' size, the ground crag drawn 1.21 times larger and further off (1.11 in ASTEROIDS, without
the headroom); seen from 20 degrees off vertical the rock's top shows about a third of its height up the screen, and
at the screen's sides a little of its flank.

THE ROCK

As the sprite and its 4x upscales draw it (columns and rows of the picture): a heap of rounded boulders of grey stone
(ramp 0, 0x01-0x0f, a near-black outline 0x20), lit from the upper left, parted by dark crevices, the bottom third in
shadow; carved, as the big asteroids are, with rings and curls: a top lump (columns 27-42 of rows 4-18) with a lit lip
over a hollow that holds a pale knob (31-40, 18-24), a knob at its upper left with a curl; under them the great
ringed boulder (24-37, 23-38) with a spiral (an ammonite) in its ring, and beside it a boulder ringed round a flat face
(37-45, 23-36); down the right a dark slab (41-56, 5-25) and three boulders, the right one ringed round a shallow bowl
(48-62, 43-57); down the left two lit lumps, the second with a curl, the broad textured boulder (2-23, 37-47) and one
under it; in the middle a boulder with a lit streak along its lower edge (21-35, 39-62) and one with a C-shaped ring
(35-47, 41-58); at the bottom a lit knob (47-54, 56-63), the lower right boulder with a curl over its top (50-71,
62-79), and dark lumps along the bottom edge.

Built with the big asteroids' machinery (polish_asteroids.py, as polish_asteroid_lumpy.py, polish_sky_rocks.py and
polish_pebbles.py are) and their palette: 25 blocks over a network of crevices (JUNCTIONS, EDGES: each crevice between
two blocks, from junction to junction, its course rounded and wandering a little), each block a convex block over its
part of the picture (polish_asteroids.Block: its footprint's walls rising steeply from the ground, roof planes, a few
chips; polish_sky_rocks.RockBlock's chips; here a Boulder: its cap of large facets fitted to its footprint and rounder
than the big asteroids' (its ellipsoid's centre far down), so that each boulder is domed and its corners fall away),
four slabs faceted by roof planes instead (the dark slab at the top right and the one beside it, a dark face down the
right, the dark slab at the bottom); under them a dark floor (0x04, 4.6 high: each block's footprint again) that shows
where the domes' corners fall away; joined. The crevices are cut in as V-shaped grooves of dark stone (0x04), full
depth up to their junctions (three meet there: no taper) and running on through the rim where they reach it; hairlines
finer (0x06); the rings laid on as closed welts (loop_ridge), the spiral and the curls as polish_asteroids' welts
(0x0b-0x0c), the bowls cut into the ringed faces; the faces the camera sees retriangulated evenly and weathered by
smooth noise (this script's refine() and roughen(): polish_asteroids' own, but faces whose triangulation would not
keep their outline are left as they are, the grooves and the floor are not retriangulated, and the zero-thickness fins
the booleans' pinched faces triangulate into are removed: the rock is closed). Greys are the sprite's own indices: the
lit boulders 0x09-0x0b, the darker 0x07-0x08, the shadowed bottom 0x05-0x06; matte stone (roughness 0.6). Flat
underneath (the camera never sees the belly); 12.4 high at the great ring and the top lump, 9-11 at the rim, 8.8-9.6
at the bottom.

The whole is cut along the sprites' edges (x = 24 and 48, y = 14, 28, 56 of the picture) into the ten pieces, each
holding its sprite's box and, where no other piece lies beyond its edge, all the rock there (crag_31 the rim pixels
of cell 30, crag_88 those of cell 107: the sheet draws a few outline pixels in those cells, which the game never
draws), each moved so that its sprite's centre is its origin. The cuts are capped with the rock's inside (0x05, flat:
seen through a piece that is fading in, past a neighbour at the screen's sides, and on the side view's single pieces)
by this script's cut() (polish_coral_manta.cut's: the caps given their material as soon as they are made, the faces'
own winding kept, the uncut rock's shading); every mesh triangulated (polish_k_pod.triangulate).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera. The whole's origin
is the picture's centre (column 36, row 42: crag_51's centre); P() turns a pixel corner of the picture (column, row)
into polish_asteroids' 48 x 56 picture, whose px() puts its corner 24, 28 at the origin.

models.cfg: the model and sprite lines stay as they are (model crag_<n> enemies/crag_<n>.glb origin; sprite d <n>
crag_<n> yaw=0). Replaces wave3_j_rocks.py's crag (its "Boulder clusters on the ground" section, cluster() and
clamp_to_outline(), which nothing else uses; its "D 13, 15, 31, 34, 49, 51, 53, 88, 89, 91: the huge asteroid"
section: CRAG_BOULDERS, CRAG_PIECES, crag_whole(), crag_piece() and the loop registering the ten models; the crag_*
paragraph of its docstring and "crag|" in its usage; Matrix in its imports) and wave3_j_art.py's HUGE (with its
comment line), which nothing else reads. wave3_j_rocks.py's stone face and sky rocks stay (wave3_ap_face.py loads it
for stone_face_whole() and its art.FACE, wave3_ao_works.py imports it for stone_face_whole()).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the whole
and of each piece against enemy_D.png), --preview <prefix> (each piece's top and 3/4 views), --whole <prefix> (the
whole rock's), --only <model,...>.
"""
import math
import os
import random
import sys

import bmesh
import bpy
import mathutils.noise as noise
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_asteroids as pa  # noqa: E402
from polish_sky_rocks import RockBlock  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402

PREFIX = "crag"
W, H = 72, 84
# How far a block reaches across a crevice it borders (the big asteroids' 0.7, the lumpy asteroid's 0.55).
REACH = 0.6
# The walls (inset, height): at the rim steep from the ground, curving in towards the top; at a border between
# blocks, steeper (the big asteroids' profiles, a little taller).
OUTER = [(0.0, 0.0), (0.5, 3.4), (1.5, 6.8), (3.0, 9.0), (4.8, 10.2)]
INNER = [(0.0, 0.0), (0.15, 4.2), (0.5, 9.4), (1.1, 12.0), (2.0, 13.4)]
ROUGHNESS, METALLIC = 0.6, 0.02
CRACK, HAIRLINE, INSIDE = 0x04, 0x06, 0x05
JOINT_REACH = 0.45   # how far a crevice runs on past a junction inside the rock (its groove full depth up to it)
FLOOR = 4.6          # the floor under the boulders (what shows between their rounded corners), its grey
FLOOR_SHADE = 0x04
WANDER = (0.65, 0.16)  # how far a crevice's course wanders from its polyline (pixels) and how fast (cycles per pixel)
SPACING = 1.2        # how far apart the weathered faces' points are (the big asteroids' 0.9: this rock is larger)


def P(c, r):
    """A pixel corner of the 72 x 84 picture in polish_asteroids' picture (whose px() puts its corner 24, 28 at the
    origin): the picture's centre (36, 42) at the origin."""
    return (c - 12.0, r - 14.0)


# --- The outline and the crevice network -----------------------------------------------------------------------------

# The outline (the ten sprites' pixels and the rim pixels of cells 30 and 107, the near-black edge included), its
# steps cut through their middles: down the left side, along the bottom, up the right side, over the top.
OUTLINE = [
    (2, 39.5), (2, 42.5), (4, 44.5), (4, 45.5), (7, 48.5), (7, 49.5), (12, 54.5), (12, 55.5), (14, 56.5),
    (14, 60.5), (13, 61.5), (13, 66.5), (14, 67.5), (14, 68.5), (15.5, 70), (16.5, 70), (18.5, 72), (19.5, 72),
    (20.5, 73), (23.5, 73), (26.5, 71), (27, 71.5), (27, 74.5), (28.5, 76), (33.5, 76), (35.5, 74), (36.5, 74),
    (37.5, 75), (38.5, 75), (41.5, 77), (47.5, 77), (48, 76.5), (48, 75.5), (48.5, 75), (49.5, 75), (52.5, 77),
    (55.5, 77), (56.5, 78), (59.5, 78), (60.5, 79), (67.5, 79), (69, 77.5), (69, 76.5), (70, 75.5), (70, 73.5),
    (71, 72.5), (71, 67.5), (70, 66.5), (70, 63.5), (69, 62.5), (69, 58.5), (68, 57.5), (68, 48.5), (67, 47.5),
    (67, 39.5), (62.5, 35), (61.5, 35), (58, 31.5), (58, 29.5), (57, 28.5), (57, 25.5), (56, 24.5), (56, 21.5),
    (55, 20.5), (55, 18.5), (54, 17.5), (54, 16.5), (53, 15.5), (53, 14.5), (52, 13.5), (52, 12.5), (51, 11.5),
    (51, 10.5), (50, 9.5), (50, 8.5), (49.5, 8), (48.5, 8), (46.5, 6), (43.5, 6), (42.5, 5), (40.5, 5), (39.5, 4),
    (32.5, 4), (28, 8.5), (28, 9.5), (25, 12.5), (25, 13.5), (24, 14.5), (24, 15.5), (23.5, 16), (22.5, 16),
    (20, 18.5), (20, 19.5), (15.5, 24), (14.5, 24), (13.5, 25), (12.5, 25), (11.5, 26), (10.5, 26), (9.5, 28),
    (7.5, 28), (7, 28.5), (7, 29.5), (6, 30.5), (6, 31.5), (4, 34.5), (4, 36.5),
]

# Where crevices meet (pixel corners of the picture); those on the outline are where a crevice reaches the rim.
JUNCTIONS = {
    # the top lump, the hollow under it, the slab at its right
    "JA": (23.9, 15.6), "JB": (42.2, 5.0), "JT1": (49.0, 8.0), "JC": (41.0, 18.0), "JD": (27.6, 18.2),
    "JE": (29.0, 23.4), "JF": (36.6, 23.2), "JG": (40.6, 23.8), "JH": (45.0, 25.2), "JT2": (48.6, 25.4),
    "JR1": (56.5, 25.0),
    # the right
    "JK2": (44.8, 35.6), "JG2": (52.2, 35.0), "JR2": (60.2, 33.7), "JK3": (44.0, 42.4), "JK4": (47.4, 43.6),
    "JG3": (52.6, 43.4), "JR3": (67.0, 43.0),
    # the left
    "JU1": (16.6, 22.9), "JU2": (24.0, 25.8), "JL1": (13.2, 25.0), "JL2": (13.8, 37.2), "JL3": (23.4, 38.0),
    "JL4": (4.0, 36.6), "JE1": (21.0, 47.4), "JE2": (6.6, 48.1), "JH1": (20.6, 53.8), "JH2": (12.0, 55.0),
    # the middle and the bottom
    "JJ1": (36.0, 41.2), "JJ2": (33.4, 57.2), "JB1": (35.6, 57.6), "JI0": (30.4, 61.6), "JK5": (47.6, 56.8),
    "JP2": (46.8, 58.8), "JP1": (54.6, 57.8), "JQ2": (53.6, 62.6), "JP3": (50.6, 63.0), "JR4": (68.5, 58.0),
    "JR5": (69.0, 62.0), "JB2": (35.0, 68.4), "JB3": (29.8, 68.4), "JB4": (48.0, 66.8), "JB5": (36.0, 74.0),
    "JI1": (26.6, 70.9), "JM1": (49.0, 75.0),
}

# The crevices, each between two blocks: from a junction over pixel corners to a junction; width and depth. CREASES
# are only borders (where the blocks' tops meet, no groove): the dark slab at the top right is one slab in two facets.
CREASES = {"tr12"}
W1, W2, W3 = (1.1, 2.6), (0.95, 2.3), (0.8, 2.0)
EDGES = {
    "top_r": ("JB", [(41.7, 9.0), (41.3, 13.5)], "JC", W1), "top_b": ("JC", [(37.0, 18.6), (32.0, 18.8)], "JD", W1),
    "top_l": ("JD", [(25.6, 17.0)], "JA", W2), "hk_l": ("JD", [(28.0, 20.6)], "JE", W2),
    "hk_r": ("JC", [(40.6, 20.8)], "JG", W2), "ring_t": ("JE", [(32.0, 23.6)], "JF", W2),
    "rk_t": ("JF", [(38.6, 23.4)], "JG", W3), "tr1_rk": ("JG", [(42.8, 24.6)], "JH", W2),
    "tr1_g1": ("JH", [], "JT2", W2), "tr12": ("JT1", [(48.8, 12.0), (48.6, 19.0)], "JT2", W2),
    "tr2_g1": ("JT2", [(52.5, 25.4)], "JR1", W2), "rk_g1": ("JH", [(44.9, 30.0)], "JK2", W1),
    "rk_g2a": ("JK2", [(44.2, 38.6)], "JK3", W2), "ring_rk": ("JF", [(36.4, 27.0), (36.8, 33.0)], "JJ1", W2),
    "ul_ring": ("JE", [(26.0, 24.2)], "JU2", W2), "ul_l2": ("JU1", [(20.2, 24.8)], "JU2", W2),
    "ring_l2": ("JU2", [(23.2, 31.0)], "JL3", W1), "l12": ("JL1", [(13.6, 31.0)], "JL2", W2),
    "l1_e": ("JL4", [(9.0, 37.0)], "JL2", W1), "l2_e": ("JL2", [(19.0, 37.8)], "JL3", W1),
    "e_j": ("JL3", [(22.8, 42.5)], "JE1", W1), "e_h": ("JE2", [(12.0, 47.6), (17.0, 47.6)], "JE1", W2),
    "h_j": ("JE1", [(20.4, 50.5)], "JH1", W2), "h_i": ("JH2", [(16.5, 54.8)], "JH1", W2),
    "ring_j": ("JL3", [(28.0, 40.0), (33.0, 40.8)], "JJ1", W1), "rk_k": ("JJ1", [(40.0, 41.6)], "JK3", W1),
    "g1_g2a": ("JK2", [(48.5, 35.2)], "JG2", W2), "g1_g2b": ("JG2", [(56.5, 34.6)], "JR2", W2),
    "g2ab": ("JG2", [(52.4, 39.0)], "JG3", W3), "k_g2a": ("JK3", [], "JK4", W2), "g2a_r3": ("JK4", [], "JG3", W2),
    "g2b_r3": ("JG3", [(58.0, 43.2)], "JR3", W2), "j_k": ("JJ1", [(35.6, 47.0), (35.0, 53.0)], "JJ2", W1),
    "k_r3": ("JK4", [(47.4, 48.0), (47.8, 53.0)], "JK5", W1), "r3_p": ("JK5", [(51.0, 57.4)], "JP1", W2),
    "r3_q": ("JP1", [(62.0, 57.8)], "JR4", W2),
    "j_i": ("JH1", [(22.4, 57.5), (23.6, 61.4), (27.0, 62.6)], "JI0", W2), "j_b1": ("JI0", [(32.0, 59.4)], "JJ2", W2),
    "k_b1": ("JJ2", [], "JB1", W2), "k_b2": ("JB1", [(40.0, 57.8), (44.0, 58.4)], "JP2", W2),
    "k_p": ("JK5", [], "JP2", W3), "p_b2": ("JP2", [(47.0, 61.4)], "JP3", W3),
    "p_q": ("JP1", [(54.2, 60.2)], "JQ2", W3), "p_m": ("JQ2", [], "JP3", W3),
    "q_m": ("JQ2", [(60.0, 62.4)], "JR5", W2), "b2_m": ("JP3", [(50.0, 64.8)], "JB4", W2),
    "b4_m": ("JB4", [(49.2, 70.6)], "JM1", W2), "i_b1": ("JI0", [(30.4, 64.5)], "JB3", W2),
    "i_b3": ("JB3", [(28.2, 69.6)], "JI1", W2), "b1_b2": ("JB1", [(35.4, 63.0)], "JB2", W3),
    "b1_b3": ("JB3", [(32.4, 68.8)], "JB2", W3), "b3_b4": ("JB2", [(35.6, 71.4)], "JB5", W2),
    "b2_b4": ("JB2", [(41.0, 67.6)], "JB4", W2),
}

# The blocks: name, its rim (from one outline junction to another, along OUTLINE's order) or None, the crevices round
# it, its roof planes (column, row, height, nx, ny: through that point, leaning as (nx, ny, 1); the first one's point
# inside the block), its grey, its dome or None, how many random chips, a seed. A dome is a cap of large facets over the
# block's footprint (Boulder): (its top's height, its roundness: the cap's ellipsoid that many times as high as the
# top, its points[, the share of the footprint a knob in a hollow takes]).
OWN = 40.0  # the height of a domed block's first roof (only its point counts: the dome shapes the top)
BLOCKS = [
    ("top", ("JB", "JA"), ["top_r", "top_b", "top_l"],
     [(34.5, 11.0, OWN, 0.0, 0.0), (31.0, 9.5, 13.0, -0.42, 0.28), (38.8, 10.0, 12.8, 0.48, 0.12),
      (34.5, 16.6, 11.6, 0.0, -0.55), (34.0, 5.6, 11.8, -0.05, 0.65)], 0x0a, (13.8, 2.3, 28), 3, 3),
    ("hk", None, ["top_b", "hk_l", "ring_t", "rk_t", "hk_r"], [(34.4, 20.8, OWN, 0.0, 0.0)], 0x0b,
     (10.8, 2.0, 22, 0.62), 1, 5),
    ("ul", ("JA", "JU1"), ["top_l", "hk_l", "ul_ring", "ul_l2"], [(23.8, 20.4, OWN, 0.0, 0.0)], 0x0a,
     (12.4, 2.3, 24), 3, 7),
    ("tr1", ("JT1", "JB"), ["top_r", "hk_r", "tr1_rk", "tr1_g1", "tr12"],
     [(45.0, 15.0, 12.2, 0.1, 0.05), (42.4, 18.0, 11.8, -0.6, 0.05), (46.8, 9.0, 11.2, 0.15, 0.5),
      (46.5, 22.5, 11.2, 0.15, -0.4)], 0x08, None, 3, 11),
    ("tr2", ("JR1", "JT1"), ["tr12", "tr2_g1"],
     [(51.5, 17.0, 10.9, 0.45, 0.05), (50.5, 11.5, 10.2, 0.3, 0.45), (52.0, 23.0, 10.4, 0.35, -0.3)], 0x08, None,
     3, 13),
    ("g1", ("JR2", "JR1"), ["tr1_g1", "tr2_g1", "rk_g1", "g1_g2a", "g1_g2b"], [(50.5, 30.0, OWN, 0.0, 0.0)], 0x08,
     (12.0, 2.3, 24), 3, 17),
    ("ring", None, ["ring_t", "ring_rk", "ring_j", "ring_l2", "ul_ring"], [(30.4, 30.6, OWN, 0.0, 0.0)], 0x0a,
     (14.2, 2.3, 32), 2, 19),
    ("rk", None, ["rk_t", "tr1_rk", "rk_g1", "rk_g2a", "rk_k", "ring_rk"], [(40.6, 30.0, OWN, 0.0, 0.0)], 0x0a,
     (13.4, 2.3, 28), 2, 23),
    ("l1", ("JL1", "JL4"), ["l12", "l1_e"], [(9.2, 31.6, OWN, 0.0, 0.0), (6.4, 30.4, 10.4, -0.55, 0.35)], 0x0a,
     (11.4, 2.3, 24), 3, 29),
    ("l2", ("JU1", "JL1"), ["ul_l2", "ring_l2", "l2_e", "l12"], [(18.4, 31.0, OWN, 0.0, 0.0)], 0x09,
     (12.8, 2.3, 26), 3, 31),
    ("e", ("JL4", "JE2"), ["l1_e", "l2_e", "e_j", "e_h"], [(12.6, 42.0, OWN, 0.0, 0.0), (6.0, 41.0, 10.8, -0.55, 0.15)],
     0x0a, (12.6, 2.3, 30), 4, 37),
    ("h", ("JE2", "JH2"), ["e_h", "h_j", "h_i"], [(15.2, 51.0, OWN, 0.0, 0.0)], 0x08, (11.2, 2.3, 24), 3, 41),
    ("g2a", None, ["g1_g2a", "g2ab", "g2a_r3", "k_g2a", "rk_g2a"],
     [(48.3, 39.0, 11.2, 0.0, 0.05), (48.0, 42.6, 10.4, 0.0, -0.5), (45.6, 38.0, 10.6, -0.5, 0.1)], 0x07, None, 2, 43),
    ("g2b", ("JR3", "JR2"), ["g1_g2b", "g2ab", "g2b_r3"], [(56.5, 39.0, OWN, 0.0, 0.0), (62.5, 39.5, 9.8, 0.6, 0.05)],
     0x08, (11.6, 2.3, 24), 3, 47),
    ("r3", ("JR4", "JR3"), ["g2a_r3", "g2b_r3", "k_r3", "r3_p", "r3_q"],
     [(55.6, 50.0, OWN, 0.0, 0.0), (64.0, 50.0, 10.4, 0.6, 0.0)], 0x09, (13.4, 2.3, 30), 3, 53),
    ("j", None, ["ring_j", "j_k", "j_b1", "j_i", "h_j", "e_j"], [(28.6, 49.0, OWN, 0.0, 0.0)], 0x0a,
     (13.8, 2.3, 32), 3, 59),
    ("k", None, ["rk_k", "j_k", "k_b1", "k_b2", "k_p", "k_r3", "k_g2a"], [(41.4, 50.0, OWN, 0.0, 0.0)], 0x09,
     (13.4, 2.3, 30), 3, 61),
    ("i", ("JH2", "JI1"), ["h_i", "j_i", "i_b1", "i_b3"], [(21.0, 62.0, OWN, 0.0, 0.0)], 0x0a, (12.4, 2.3, 30), 3, 67),
    ("b1", None, ["j_b1", "k_b1", "b1_b2", "b1_b3", "i_b1"], [(33.0, 63.4, OWN, 0.0, 0.0)], 0x06,
     (9.6, 2.3, 20), 1, 71),
    ("b2", None, ["k_b2", "p_b2", "b2_m", "b2_b4", "b1_b2"],
     [(41.4, 62.6, 10.0, 0.05, 0.0), (40.0, 60.0, 9.6, -0.3, 0.45), (42.0, 66.6, 8.8, 0.0, -0.55)], 0x06, None, 3, 73),
    ("p", None, ["k_p", "r3_p", "p_q", "p_m", "p_b2"], [(50.4, 59.8, OWN, 0.0, 0.0)], 0x0a, (11.6, 2.3, 22), 1, 79),
    ("q", ("JR5", "JR4"), ["r3_q", "p_q", "q_m"], [(61.0, 60.0, OWN, 0.0, 0.0), (66.5, 60.0, 9.0, 0.6, 0.0)], 0x08,
     (10.2, 2.3, 20), 3, 83),
    ("m", ("JM1", "JR5"), ["q_m", "p_m", "b2_m", "b4_m"], [(59.0, 70.0, OWN, 0.0, 0.0), (67.0, 70.0, 9.8, 0.6, 0.0)],
     0x08, (12.0, 2.3, 32), 4, 89),
    ("b3", ("JI1", "JB5"), ["i_b3", "b1_b3", "b3_b4"], [(31.4, 72.0, OWN, 0.0, 0.0)], 0x05, (8.8, 2.3, 20), 2, 97),
    ("b4", ("JB5", "JM1"), ["b3_b4", "b2_b4", "b4_m"], [(42.4, 72.0, OWN, 0.0, 0.0)], 0x06, (9.4, 2.3, 24), 3, 101),
]


def ring(c, r, rx, ry, start, sweep, steps=24):
    """Pixel corners round an ellipse centred on (c, r), from the angle start (degrees, counter-clockwise on the
    screen, 0 to the right, 90 up) over sweep degrees."""
    return [(c + rx * math.cos(math.radians(start + sweep * i / steps)),
             r - ry * math.sin(math.radians(start + sweep * i / steps))) for i in range(steps + 1)]


def loop_ridge(name, surface, corners, half_width, height, mat, step=0.6, seed=0):
    """polish_asteroids.ridge round a closed loop of pixel corners (polish_asteroids' picture): a low welt lying on
    the surface all round it, its top rounded, its width wandering a little, no ends (a little coarser than ridge's:
    this rock has many)."""
    pts = mk.chaikin([tuple(pa.px(c, r)) for c, r in corners], 3, closed=True)
    path = pa.resample(pts + pts[:1], step)[:-1]
    shift = Vector((seed * 3.7, seed * 1.3, seed * 5.1))
    across = [-1.0, -0.72, -0.38, 0.0, 0.38, 0.72, 1.0]
    count = len(path)
    verts, faces = [], []
    for i, p in enumerate(path):
        t = (path[(i + 1) % count] - path[i - 1]).normalized()
        hit, normal = surface.hit(p.x, p.y)
        side = Vector((t.x, t.y, 0.0)).cross(normal).normalized()
        wob = 1.0 + 0.18 * noise.noise(p.to_3d() * 0.9 + shift)
        w = half_width * wob
        for u in across:
            verts.append(hit + side * (w * u) + normal * (height * (1 - abs(u) ** 3.0) ** 0.45 - 0.25))
        verts.append(hit + side * (w * 0.7) - normal * 0.9)
        verts.append(hit - side * (w * 0.7) - normal * 0.9)
    n = len(across) + 2
    for i in range(count):
        j = (i + 1) % count
        for a in range(n):
            b = (a + 1) % n
            faces.append((i * n + a, i * n + b, j * n + b, j * n + a))
    return pa.outward(k.mesh_object(name, verts, faces, mat))


def spiral(c, r, outer, inner, turns, start, steps=40):
    """polish_asteroids.spiral: pixel corners along a spiral round (c, r) from radius outer to inner."""
    pts = []
    for i in range(steps + 1):
        t = i / steps
        a = math.radians(start) + 2 * math.pi * turns * t
        rad = outer + (inner - outer) * t
        pts.append((c + rad * math.cos(a), r - rad * math.sin(a)))
    return pts


# The rings (closed loops), the spiral and the curls (pixel corners, half width, height, grey).
LOOPS = [
    (ring(30.2, 30.8, 5.8, 6.0, 0, 360, 28)[:-1], 1.05, 0.75, 0x0c),    # the great ring
    (ring(40.7, 29.8, 3.3, 4.7, 0, 360, 20)[:-1], 0.85, 0.6, 0x0c),     # the ring round the flat face beside it
    (ring(55.5, 49.8, 4.9, 5.2, 0, 360, 28)[:-1], 1.0, 0.7, 0x0c),      # the right boulder's ring
]
RIDGES = [
    (spiral(30.4, 30.8, 3.6, 0.9, 1.25, 100), 0.5, 0.45, 0x0b),     # the ammonite in the great ring
    (ring(41.6, 50.0, 4.4, 5.6, 75, 215), 0.9, 0.6, 0x0b),            # the C on the middle boulder
    ([(15.4, 29.4), (16.0, 32.2), (17.8, 34.8), (20.4, 36.4), (22.4, 36.6)], 0.9, 0.6, 0x0b),   # the left curl
    ([(22.8, 17.6), (25.0, 18.6), (26.6, 20.4), (27.0, 22.4)], 0.8, 0.55, 0x0b),                 # the upper left curl
    ([(29.4, 17.0), (32.5, 16.6), (36.0, 16.6), (39.0, 17.0)], 0.75, 0.5, 0x0b),                 # the top lump's lip
    ([(29.6, 52.4), (27.6, 55.4), (25.6, 58.4), (24.2, 60.6)], 0.75, 0.55, 0x0c),                # the streak
    ([(51.8, 67.8), (52.6, 65.6), (54.8, 64.6), (57.4, 64.6), (59.2, 65.6)], 0.9, 0.6, 0x0b),    # the lower right curl
]
# The bowls in the rings (column, row, radius, depth, grey).
BOWLS = [(40.7, 29.8, 2.0, 0.6, 0x08), (55.5, 49.8, 2.8, 0.7, 0x08), (30.6, 30.6, 1.0, 0.45, 0x08)]
# Hairline cracks inside blocks (pixel corners, width, depth).
HAIRLINES = [
    ([(9.6, 39.4), (12.0, 41.6), (13.0, 44.4)], 0.45, 0.6), ([(15.0, 39.0), (17.4, 41.4)], 0.4, 0.5),
    ([(60.0, 65.0), (61.6, 67.4), (61.0, 70.4)], 0.45, 0.6), ([(63.0, 66.0), (64.4, 68.6)], 0.4, 0.5),
    ([(45.0, 8.6), (46.4, 12.0), (46.0, 16.0)], 0.45, 0.6), ([(52.0, 27.0), (53.6, 30.4)], 0.4, 0.5),
    ([(38.0, 60.4), (43.4, 63.6)], 0.45, 0.6), ([(39.0, 70.6), (45.0, 72.0)], 0.4, 0.5),
]

# The pieces: model, sprite, 2x2, its box (left, top in the picture), the part of the whole it holds (columns c0-c1,
# rows r0-r1; None: on beyond the picture's edge, where no other piece lies).
PIECES = [
    ("crag_13", 13, True, (24, 0), (24, 48, None, 28)),
    ("crag_15", 15, False, (48, 0), (48, None, None, 14)),
    ("crag_31", 31, False, (12, 14), (None, 24, None, 28)),
    ("crag_34", 34, False, (48, 14), (48, None, 14, 28)),
    ("crag_49", 49, True, (0, 28), (None, 24, 28, 56)),
    ("crag_51", 51, True, (24, 28), (24, 48, 28, 56)),
    ("crag_53", 53, True, (48, 28), (48, None, 28, 56)),
    ("crag_88", 88, False, (12, 56), (None, 24, 56, None)),
    ("crag_89", 89, True, (24, 56), (24, 48, 56, None)),
    ("crag_91", 91, True, (48, 56), (48, None, 56, None)),
]


def on_outline(p, tolerance=0.3):
    """Whether a pixel corner lies on the outline (within tolerance)."""
    best = 1e9
    for a, b in zip(OUTLINE, OUTLINE[1:] + OUTLINE[:1]):
        ax, ay, bx, by = a[0], a[1], b[0], b[1]
        dx, dy = bx - ax, by - ay
        t = max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / max(dx * dx + dy * dy, 1e-12)))
        best = min(best, math.hypot(ax + dx * t - p[0], ay + dy * t - p[1]))
    return best < tolerance


def nearest_index(p):
    """The index of the outline's point nearest to p."""
    return min(range(len(OUTLINE)), key=lambda i: (OUTLINE[i][0] - p[0]) ** 2 + (OUTLINE[i][1] - p[1]) ** 2)


def rim(a, b):
    """The outline's points from junction a to junction b (along OUTLINE's order), the junctions included."""
    pa_, pb_ = JUNCTIONS[a], JUNCTIONS[b]
    i, j = nearest_index(pa_), nearest_index(pb_)
    points = [pa_]
    n = len(OUTLINE)
    step = i  # from a's nearest outline point (left out where it is a itself) to b's
    while True:
        q = OUTLINE[step]
        if (q[0] - pa_[0]) ** 2 + (q[1] - pa_[1]) ** 2 > 0.05:
            points.append(q)
        if step == j:
            break
        step = (step + 1) % n
    points.append(pb_)
    return points


def wander(points, seed):
    """A polyline's inner points moved sideways by smooth noise (WANDER), its ends kept: a crevice's course."""
    amount, rate = WANDER
    shift = Vector((seed * 0.37 % 17.0, seed * 0.91 % 13.0, 3.0))
    lengths = [0.0]
    for p, q in zip(points, points[1:]):
        lengths.append(lengths[-1] + math.hypot(q[0] - p[0], q[1] - p[1]))
    total = lengths[-1]
    out = [tuple(points[0])]
    for i in range(1, len(points) - 1):
        p, q, r = Vector(points[i - 1]), Vector(points[i]), Vector(points[i + 1])
        t = (r - p).normalized()
        side = Vector((-t.y, t.x))
        fade = min(1.0, lengths[i] / 2.5, (total - lengths[i]) / 2.5)
        d = amount * fade * noise.noise(Vector((lengths[i] * rate, 0.0, 0.0)) + shift)
        out.append(tuple(q + side * d))
    out.append(tuple(points[-1]))
    return out


def crevice(name):
    """An EDGES entry as polish_asteroids.Crack (pixel corners of polish_asteroids' picture): an end on the outline
    runs on through the rim ("out"), an end inside the rock runs on a little past its junction, full depth to it."""
    a, via, b, (width, depth) = EDGES[name]
    points = wander(mk.chaikin([JUNCTIONS[a]] + list(via) + [JUNCTIONS[b]], 2, closed=False), sum(map(ord, name)))
    ends = []
    for end, (i, j) in zip((a, b), ((0, 1), (-1, -2))):
        if on_outline(JUNCTIONS[end]):
            ends.append("out")
        else:
            ends.append("joint")
            p, q = Vector(points[i]), Vector(points[j])
            extended = tuple(p + (p - q).normalized() * JOINT_REACH)
            if i == 0:
                points.insert(0, extended)
            else:
                points.append(extended)
    return pa.Crack([P(c, r) for c, r in points], width, depth, tuple(ends), cut=name not in CREASES)


class Boulder(RockBlock):
    """polish_sky_rocks.RockBlock (polish_asteroids.Block whose chips are cut against its tops only, its cap widened to
    cover its footprint) whose cap is fitted to its footprint: centred on it, its radii the footprint's half extents
    (widened by RockBlock to reach its farthest corner at 0.9), dome = (top, roundness, points): the cap's top at
    that height, the ellipsoid roundness times as high (its centre that much lower): a rounded boulder, its corners
    falling below the floor; dome = (top, roundness, points, shrink): the radii that share of the half extents, not
    widened: a knob in a hollow, the floor round it."""

    def __init__(self, *args, dome=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.dome = dome

    def planes(self, cracks, outer, inner):
        if self.dome is None:
            return super().planes(cracks, outer, inner)
        poly = self.footprint(cracks)
        xs, ys = [p[0] for p in poly], [p[1] for p in poly]
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        top, roundness, count = self.dome[:3]
        shrink = self.dome[3] if len(self.dome) > 3 else None
        rz = roundness * top
        f = shrink or 1.0
        self.cap = (cx + 24.0, 28.0 - cy, f * (max(xs) - min(xs)) / 2, f * (max(ys) - min(ys)) / 2, rz, top - rz, count)
        if shrink:  # a knob in a hollow: the cap not widened, the floor round it
            return pa.Block.planes(self, cracks, outer, inner)
        return super().planes(cracks, outer, inner)


def spec():
    """The rock's parts in polish_asteroids' terms (its picture's pixel corners): the crevices, the blocks, the
    hairlines, the bowls, the welts and the rings."""
    cracks = {name: crevice(name) for name in EDGES}
    blocks = []
    for name, rim_ends, edges, roofs, shade, dome, chips, seed in BLOCKS:
        points = rim(*rim_ends) if rim_ends else []
        blocks.append(Boulder(name, [P(c, r) for c, r in points], list(edges),
                              [(*P(c, r), z, nx, ny) for c, r, z, nx, ny in roofs], shade, random_chips=chips,
                              seed=seed, dome=dome))
    return {
        "cracks": cracks, "blocks": blocks,
        "hairlines": [pa.Crack([P(c, r) for c, r in pts], width, depth) for pts, width, depth in HAIRLINES],
        "bowls": [(*P(c, r), radius, depth, shade) for c, r, radius, depth, shade in BOWLS],
        "ridges": [([P(c, r) for c, r in pts], half, height, shade) for pts, half, height, shade in RIDGES],
        "loops": [([P(c, r) for c, r in pts], half, height, shade) for pts, half, height, shade in LOOPS],
    }


def refine(bm, spacing, seen):
    """polish_asteroids.refine (the large flat faces the camera sees retriangulated evenly: points on a jittered grid
    inside each, joined to its outline by a constrained Delaunay triangulation), leaving a face as it is where the
    triangulation would not keep its outline (a point added on it, outline points merged or dropped, a triangle that
    exists already): those left a few open edges in the crag's rock."""
    from mathutils.geometry import delaunay_2d_cdt
    rng = random.Random(5)
    bm.normal_update()
    pa.split_edges(bm, [e for e in bm.edges if e.calc_length() > spacing * 1.2 and
                        any(seen(f) for f in e.link_faces) and max(v.co.z for v in e.verts) > 0.02], spacing)
    for face in [f for f in bm.faces if seen(f) and f.calc_area() > spacing * spacing * 1.5]:
        n = face.normal.copy()
        u = (Vector((1, 0, 0)) if abs(n.x) < 0.9 else Vector((0, 1, 0))).cross(n).normalized()
        w = n.cross(u)
        origin = face.verts[0].co.copy()
        ring_verts = list(face.verts)
        flat = [Vector(((v.co - origin).dot(u), (v.co - origin).dot(w))) for v in ring_verts]
        xs, ys = [p.x for p in flat], [p.y for p in flat]
        inner = []
        y = min(ys) + spacing * 0.5
        row = 0
        while y < max(ys):
            x = min(xs) + spacing * (0.5 + 0.5 * (row % 2))
            while x < max(xs):
                q = Vector((x + rng.uniform(-0.2, 0.2) * spacing, y + rng.uniform(-0.2, 0.2) * spacing))
                if pa.inside(q, flat) and pa.edge_distance(q, flat) > 0.45 * spacing:
                    inner.append(q)
                x += spacing
            y += spacing * 0.866
            row += 1
        if not inner:
            continue
        coords = flat + inner
        out_coords, _, out_faces, orig_verts, _, _ = delaunay_2d_cdt(coords, [], [list(range(len(flat)))], 1, 1e-6)
        if any(len(source) != 1 for source in orig_verts) or len(out_coords) != len(coords):
            continue  # the outline would not be kept
        tris = [tuple(orig_verts[i][0] for i in tri) for tri in out_faces]
        boundary = {}
        for tri in tris:
            for a, b in zip(tri, tri[1:] + tri[:1]):
                key = (min(a, b), max(a, b))
                boundary[key] = boundary.get(key, 0) + 1
        outline = {(min(i, (i + 1) % len(flat)), max(i, (i + 1) % len(flat))) for i in range(len(flat))}
        if {e for e, c in boundary.items() if c == 1} != outline:
            continue
        verts = ring_verts + [bm.verts.new(origin + u * q.x + w * q.y) for q in inner]
        if any(bm.faces.get([verts[i] for i in tri]) is not None for tri in tris):
            for v in verts[len(ring_verts):]:
                bm.verts.remove(v)
            continue
        material, smooth = face.material_index, face.smooth
        bm.faces.remove(face)
        for tri in tris:
            f = bm.faces.new([verts[i] for i in tri])
            f.material_index = material
            f.smooth = smooth
            f.normal_update()
            if f.normal.dot(n) < 0:
                f.normal_flip()
    bm.normal_update()


def remove_fins(bm):
    """Removes what triangulating the booleans' pinched faces leaves: pairs of triangles over the same three points
    back to back (zero-thickness fins: both go) or facing the same way (one goes), whatever is left loose and specks
    of zero area hanging by an edge; then fills a hole left over, so that the rock stays closed."""
    faces = {}
    for f in bm.faces:
        faces.setdefault(frozenset(f.verts), []).append(f)
    doomed = []
    for group in faces.values():
        if len(group) < 2:
            continue
        group[0].normal_update()
        group[1].normal_update()
        if len(group) == 2 and group[0].normal.dot(group[1].normal) > 0:
            doomed.append(group[1])
        else:
            doomed += group
    if doomed:
        bmesh.ops.delete(bm, geom=doomed, context="FACES_ONLY")
        loose = [e for e in bm.edges if not e.link_faces]
        if loose:
            bmesh.ops.delete(bm, geom=loose, context="EDGES")
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_edges], context="VERTS")
    for _ in range(4):  # specks: zero-area triangles left hanging by an edge
        specks = [f for f in bm.faces if f.calc_area() < 1e-8 and any(len(e.link_faces) == 1 for e in f.edges)]
        if not specks:
            break
        bmesh.ops.delete(bm, geom=specks, context="FACES_ONLY")
        bmesh.ops.delete(bm, geom=[e for e in bm.edges if not e.link_faces], context="EDGES")
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_edges], context="VERTS")
    holes = [e for e in bm.edges if len(e.link_faces) == 1]
    if holes:
        filled = bmesh.ops.holes_fill(bm, edges=holes, sides=0)
        bmesh.ops.triangulate(bm, faces=filled["faces"])


def roughen(obj, spacing=0.9, amount=0.2, seed=0):
    """polish_asteroids.roughen with this script's refine(): the faces the camera sees retriangulated evenly (not the
    dark grooves and the floor: they stay as cut, which saves a third of the triangles), every point moved along its
    normal by smooth noise, the ground kept flat."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(0.5), verts=bm.verts, edges=bm.edges, delimit={"MATERIAL"})
    bm.normal_update()
    plain = {i for i, m in enumerate(obj.data.materials) if m.name.endswith("@%d" % CRACK)}  # grooves, floor: as cut
    refine(bm, spacing, lambda f: f.normal.dot(pa.CAMERA) > 0.1 and f.material_index not in plain)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3])
    remove_fins(bm)
    bm.normal_update()
    shift = Vector((seed * 2.1 + 11.0, seed * 4.7 + 3.0, seed * 0.9 + 7.0))
    moves = []
    for v in bm.verts:
        if v.co.z < 0.02:
            moves.append(Vector())
            continue
        q = v.co * 0.7 + shift
        d = amount * (0.65 * noise.noise(q) + 0.35 * noise.noise(q * 2.6))
        moves.append(v.normal * d * min(1.0, v.co.z / 1.5))
    for v, m in zip(bm.verts, moves):
        v.co += m
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def hull_solid(name, planes, mat):
    """polish_asteroids.solid (the convex polyhedron of the half-spaces, standing on z = 0), remade as the convex hull
    of its corners: closed whatever the plane cuts left (a small block's cut through a corner can leave an open
    edge)."""
    obj = pa.solid(name, planes, mat)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    points = [v.co.copy() for v in bm.verts]
    bm.free()
    bm = bmesh.new()
    for p in points:
        bm.verts.new(p)
    result = bmesh.ops.convex_hull(bm, input=bm.verts[:])
    inside = {g for g in result["geom_interior"] + result["geom_unused"] if isinstance(g, bmesh.types.BMVert)}
    if inside:
        bmesh.ops.delete(bm, geom=list(inside), context="VERTS")
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(0.2), verts=bm.verts, edges=bm.edges)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def floor_planes(block, cracks):
    """A block's footprint and walls (polish_asteroids.Block.planes without its roofs, cap and chips) under a flat
    top at FLOOR: the floor that shows between the boulders' rounded corners."""
    poly = block.footprint(cracks)
    planes = []
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        profile = INNER if a[2] == "crack" and b[2] == "crack" else OUTER
        planes += pa.edge_planes(Vector(a[:2]), Vector(b[:2]), profile)
    return planes + [(Vector((0.0, 0.0, 1.0)), FLOOR)]


def build_rock():
    """The whole rock (one object, triangulated) and its grey materials: polish_asteroids.build_rock (the blocks
    joined, the crevices and hairlines cut in, the bowls cut out, the welts joined on, weathered), with this script's
    roughen()."""
    pa.REACH = REACH
    s = spec()
    grey = pa.greys(PREFIX)
    blocks = [hull_solid(b.name, b.planes(s["cracks"], OUTER, INNER), grey(b.shade)) for b in s["blocks"]]
    floors = [hull_solid(b.name + "_floor", floor_planes(b, s["cracks"]), grey(FLOOR_SHADE)) for b in s["blocks"]]
    rock = blocks[0]
    pa.boolean(rock, blocks[1:] + floors, "UNION")
    pa.tidy(rock)
    rock.name = PREFIX
    surface = pa.Surface(rock)
    lines = [(crack, CRACK) for _, crack in sorted(s["cracks"].items()) if crack.cut]
    lines += [(crack, HAIRLINE) for crack in s["hairlines"]]
    pa.boolean(rock, [pa.crack_cutter("crack%d" % i, surface, crack, grey(shade), seed=i)
                      for i, (crack, shade) in enumerate(lines)], "DIFFERENCE")
    surface = pa.Surface(rock)
    pa.boolean(rock, [pa.bowl_cutter("bowl%d" % i, surface, c, r, radius, depth, grey(shade))
                      for i, (c, r, radius, depth, shade) in enumerate(s["bowls"])], "DIFFERENCE")
    surface = pa.Surface(rock)
    welts = [pa.ridge("ridge%d" % i, surface, corners, half, height, grey(shade), step=0.6, seed=i)
             for i, (corners, half, height, shade) in enumerate(s["ridges"])]
    welts += [loop_ridge("loop%d" % i, surface, corners, half, height, grey(shade), seed=i + 20)
              for i, (corners, half, height, shade) in enumerate(s["loops"])]
    pa.boolean(rock, welts, "UNION")
    pa.tidy(rock)
    roughen(rock, spacing=SPACING, seed=len(PREFIX))
    k.smooth(rock, 34)  # the facets' edges sharp, the weathered faces and welts smooth
    for mat in rock.data.materials:
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Roughness"].default_value = ROUGHNESS
        bsdf.inputs["Metallic"].default_value = METALLIC
    triangulate([rock])
    bpy.context.view_layer.update()
    return rock, grey


# --- Cutting ---------------------------------------------------------------------------------------------------------

def cut(source, box_xy, cap_mat):
    """polish_coral_manta.cut: the part of the rock inside a box (x0, x1, y0, y1), its cuts capped with cap_mat facing
    out of their cut (the caps given their material as soon as they are made, so that a cap a later plane cuts in two
    keeps it), the faces' own winding kept, the uncut rock's shading; the caps flat. None if nothing is inside."""
    x0, x1, y0, y1 = box_xy
    corners = [source.matrix_world @ Vector(c) for c in source.bound_box]
    if (max(c.x for c in corners) <= x0 or min(c.x for c in corners) >= x1 or
            max(c.y for c in corners) <= y0 or min(c.y for c in corners) >= y1):
        return None
    obj = source.copy()
    obj.data = source.data.copy()
    bpy.context.scene.collection.objects.link(obj)
    cap_index = mk.slot_of(obj, cap_mat)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    planes = (((x0, 0, 0), (-1, 0, 0)), ((x1, 0, 0), (1, 0, 0)), ((0, y0, 0), (0, -1, 0)), ((0, y1, 0), (0, 1, 0)))
    for co, no in planes:
        if not bm.faces:
            break
        result = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6, plane_co=co,
                                        plane_no=no, clear_outer=True)
        edges = [e for e in result["geom_cut"] if isinstance(e, bmesh.types.BMEdge) and e.is_valid]
        open_edges = [e for e in edges if len(e.link_faces) == 1]
        if open_edges:
            filled = bmesh.ops.holes_fill(bm, edges=open_edges, sides=0)
            if filled["faces"]:
                for f in bmesh.ops.triangulate(bm, faces=filled["faces"])["faces"]:
                    f.normal_update()
                    if f.normal.dot(Vector(no)) < 0:
                        f.normal_flip()
                    f.material_index = cap_index
                    f.smooth = False
    if not bm.faces:
        bm.free()
        bpy.data.objects.remove(obj)
        return None
    bm.normal_update()
    bm.faces.index_update()
    cap_ids = {f.index for f in bm.faces if f.material_index == cap_index and not f.smooth}
    bm.to_mesh(obj.data)
    bm.free()
    shading = mk.NormalSource(source)
    mesh = obj.data
    normals = []
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            n = None
            if poly.index not in cap_ids:
                n = shading.normal(mesh.vertices[mesh.loops[li].vertex_index].co, poly.center)
            normals.append(tuple(n if n is not None else poly.normal))
    mesh.normals_split_custom_set(normals)
    return obj


def piece_box(region):
    """A piece's part of the whole in the whole's coordinates (x0, x1, y0, y1)."""
    c0, c1, r0, r1 = region
    far = 1000.0
    return (-far if c0 is None else c0 - 36.0, far if c1 is None else c1 - 36.0,
            -far if r1 is None else 42.0 - r1, far if r0 is None else 42.0 - r0)


def piece_centre(large, left, top):
    """A piece's sprite's centre in the whole's coordinates (its origin)."""
    w, h = (24, 28) if large else (12, 14)
    return Vector((left + w / 2 - 36.0, 42.0 - (top + h / 2), 0.0))


# --- Checks ----------------------------------------------------------------------------------------------------------

def whole_mask(sheet):
    """The ten sprites' silhouettes placed as the levels place them: 72 x 84."""
    mask = [[False] * W for _ in range(H)]
    for _, sprite, large, (left, top), _ in PIECES:
        part = k.sprite_mask(sheet, sprite, large)
        for y, row in enumerate(part):
            for x, v in enumerate(row):
                if v:
                    mask[top + y][left + x] = True
    return mask


def open_edge_count(obj):
    """How many edges of a mesh border one face only (holes) and how many more than two (slivers)."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    holes = sum(1 for e in bm.edges if len(e.link_faces) < 2)
    slivers = sum(1 for e in bm.edges if len(e.link_faces) > 2)
    bm.free()
    return holes, slivers


def build():
    options = k.args()
    only = options["only"].split(",") if "only" in options else None
    k.reset()
    rock, grey = build_rock()
    print("%s whole: %d triangles, %d materials, open edges %d, edges of more than two faces %d" % (
        PREFIX, mk.triangles([rock]), len(rock.data.materials), *open_edge_count(rock)))
    sheets = options.get("check")
    sheet = os.path.join(sheets, "enemy_D.png") if sheets else None
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    if sheet:
        mk.compare(PREFIX + " whole", mk.coverage([rock], W, H), whole_mask(sheet))
    if "whole" in options:
        mk.preview(options["whole"] + PREFIX, [rock], size=(W, H), scale=8, distance=1.5)
    out = mk.outdir(options)
    cap = grey(INSIDE)
    for name, sprite, large, (left, top), region in PIECES:
        if only and name not in only:
            continue
        piece = cut(rock, piece_box(region), cap)
        pieces = triangulate([piece])
        mk.transform(pieces, Matrix.Translation(-piece_centre(large, left, top)))
        w, h = (24, 28) if large else (12, 14)
        if sheet:
            mk.compare("%s (D %d)" % (name, sprite), mk.coverage(pieces, w, h), k.sprite_mask(sheet, sprite, large))
        print("%s: open edges %d, edges of more than two faces %d" % (name, *open_edge_count(piece)))
        mk.report(name, pieces, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, pieces, size=(w, h), scale=16 if large else 24,
                       distance=0.8 if large else 0.5)
        for obj in pieces:
            bpy.data.objects.remove(obj)


if __name__ == "__main__":
    build()
