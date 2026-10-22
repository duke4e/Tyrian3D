"""The waterfall of TORM, BONUS and ROOST, polished (2026-10-22, round 34; it replaces wave3_ad_fall.py's still relief
and the HD volume the waterfall was left to since, which flowed with the frames). One 72 x 56 picture that the game
puts together from six 2x2 sprites of sheet H, each an enemy of its own (armour 0: scenery, never shot away), and
animates: four frames, each held three ticks (ani 12: 165 165 165 234 234 234 240 240 240 117 117 117).

PLACEMENT (the level events, tools/content/tyrevents.py; episode 6's roost.json)

- The pieces: enemies 739 740 741 (the top row: H 165 167 169, frames 234/240/117, 236/242/129, 238/244/153) above
  742 743 744 (the bottom row: H 203 205 207, frames 272/278/157, 274/280/267, 276/282/269); episode 6's ROOST has
  them as 1598-1600 above 1595-1597, the same sprites. Event 6 (the ground) puts the bottom row at (x + 24 i, y) and,
  28 pixels of scrolling later, the top row above it. The levels make the waterfall wider by repeating the middle
  column (740 above 743), and in two places leave it out: TORM t441/469, 749/777, 6377/6405, 6657/6685, 6825/6853 and
  7385/7413 (x 186) three columns; t945/973 five (the middle three times), t2737/2765 four, t4137/4165 six, t4501/4529
  four; t7385/7413 also the left and right pieces side by side at x 90 and 114 (no middle). BONUS (episode 2's second
  BONUS, level file 12, scrolling 3 a tick) six waterfalls of three columns (x -30, 186 at t49/77; -30 at t721/749;
  66 at t3857/3885, 3969/3997, 4053/4081). ROOST seven columns at t300/328, three at t2372/2400, 4696/4724 and
  5648/5676, five at t3296/3324, four at t4836/4864 (x -6) and at t3324/3352 the left piece and one middle at x 234,
  258 (its right piece beyond the map's edge). So every piece meets every other across its sides: the middle its own
  copy, the left piece the middle or the right piece, the right piece the middle or the left piece.
- The map paints a waterfall of its own there (the river's tiles over the rock cliff that crosses it); the object
  covers it and the cliff's rock on both sides. The terrain under it (assets/terrain: TORM's river class at -14, the
  ground levelled under standing enemies) is the river's level under the middle 48 pixels and rises to the banks
  towards its sides: up to 4-11 pixels over the lift at its outer columns (TORM, ROOST); BONUS's waterfalls stand on a
  lumpier ground (its cliff class at +14: the sides up to 15 pixels over the lift, the river in front 5-7 under it).
- The animation runs from each enemy's creation, a step a tick while it is on the screen's width: the pieces of a row
  are created in the same tick and stay in step; the top row is created 28 pixels of scrolling after the bottom row
  (TORM and ROOST: 28 ticks, so the top row shows mostly the frame before the bottom row's; BONUS: 9 ticks, the
  frame after), so the rows' frames differ (the original sprites don't match across the rows either).
- No other enemy, launched ones included, shows these sprites (catalog.json), so their frames can be frame models.

WHAT THE SPRITES SHOW (columns and rows of the picture; the 4x upscales)

Grey rock pillars at the sides (columns 0-11 and 60-71, ramp 0): rounded boulder caps at the top corners, pillars
below them with dark clefts between; a dark crevice (columns 56-59) between the water and the right-hand rocks. The
curtain of water (columns 12-56, rows 0-36, ramp 3): light at its lip along the top, then strands of light streaks on
darker water down to the pool, the lower half broken by dark gaps (the rock behind showing through the thinning
water). The pool (rows 36-55, columns 4-63): white foam where the curtain plunges (rows 37-48), the water beyond it
flowing on, between dark rock edges that close in at the front; leaves at the pool's corners (ramps 2 and 12). The four
frames are the same picture but for the water: light dashes on about ten strands (columns 15, 22, 24-27, 36-37, 40,
47-48, 55) brighten and darken in other rows from frame to frame, and the foam's speckles change place; the rocks and
leaves are the same (a dozen grey pixels at the curtain's edges change).

THE MODEL

Built for the game's camera (20 degrees off straight down, from the bottom of the screen) in the picture's plane (x, y
as the sprite draws them, z up) and sheared along the camera's line of sight (y - z tan 20, the normals with it), so
that the camera sees every point where the sprite draws it however high it stands, and the pieces' edges lie along its
line of sight; from straight above the outline is the sprite's rectangle.
- One height field over the picture, a grid of GRID_X across (the strands are thin) by GRID_Y down (they are long):
  the curtain a slope from its lip at the back (LIP high, rounding over) down to the pool (POOL) at FOOT, its strands
  raised (STRANDS per shade lighter than round them), a ridge of white water where it plunges (PLUNGE); the crevice
  sunk under it (CREVICE); the rock a slope ROCK_BACK..ROCK_MID..ROCK_FRONT, lumpy by the sprite's shading (ROCK_LUMPS:
  light raised, dark sunk: the boulder caps, the pillars and the clefts between them); the leaves' banks; the kinds
  blended softly (SOFT); no rise towards the back steeper than SLOPE (no folds towards the camera). Skirts down to
  SKIRT along the picture's outer edges (upright in the picture's plane: the camera sees along them; the back one in
  the water's blue, the river behind running up to the lip).
- Painted along smooth contours (Painter: polish_orb_red.band_split's way, every field carried to the cuts): where the
  water meets the rock, the rock the crevice and the banks, then each kind's bands. The water in WATER bands of ramp 3
  (lifted WATER_LIFT: the curtain faces away from the sun and the game reads palette colours darker; the light ones
  glowing 0.02-0.34): the curtain's shades the sprite's blurred far down the fall and sharpened across (STREAK: long
  thin strands, dark gaps between them low down), the pool's roundly (POOL_SHADE), white water under the foam
  (FOAM_LIGHT); the rock in ROCK bands of ramp 0 (its shades spread by ROCK_CONTRAST, darker on its steep sides); the
  crevice the darkest grey; the banks dark green. Water glossy (roughness 0.35, no metal), rock and leaves matt.
- The flow (the four frames: the same geometry but for the water): light pulses running down every strand (PERIOD,
  PULSE_LIGHT: each strand its own period and phase, periodic across, a quarter period further down each frame, so
  the frames loop), raised a little where they pass (PULSE_RELIEF, not within SEAM_CALM of the rows' seam); the pool's
  ripples flowing away (RIPPLES, a quarter of their spacing a frame); foam (FOAM_ROWS: froths of one to three low
  bubbles born at the curtain's foot, drifting FOAM_DRIFT down a frame, growing and then shrinking over four frames in
  four staggered sets, densest at the foot) and the white water churning along the foot (SPLASH: heaps swelling and
  bobbing).
- Leaves at the pool's corners (LEAF_SPACING, LEAF_LENGTH: rosettes of five pointed creased blades curling up, on the
  banks where the sprite draws leaves; ramp 12's green and ramp 2's dark green).

TILING: everything in the middle column (x -12..12) is periodic (its fields made from its 24 columns wrapped round, the
pulses' and ripples' phases periodic across, its foam a periodic set whose froths reaching over a seam are cut there and
continue on the other side), and the side columns take the middle's field within SEAM_SAME of their inner sides and
blend into their own over SEAM_BLEND beyond, their own foam clear of the seams, so that every pair of pieces meets
seamlessly side by side in every frame (left|middle, middle|middle, middle|right, left|right). The rows' seam is the
same in every frame (heights and normals: no moving relief there; the foam all below it); only the pulses' colours run
across it, as the sprites' do. --check prints the seams' worst differences (0).

Each piece is its own part of the field (grid lines on the sprites' edges: nothing to cut), its foam cut along its
edges (polish_machine_kit.cut, caps in the foam's colour), sheared, moved so that its sprite's centre is its origin,
every mesh triangulated and joined. Deterministic (seeded noise; the same GLBs with and without --check).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground. The whole's
origin is the picture's centre (pixel corner 36, 28): column c is x = c + 0.5 - 36, row r is y = 27.5 - r. Pieces'
origins: tl (-24, 14), tm (0, 14), tr (24, 14), bl (-24, -14), bm (0, -14), br (24, -14).

models.cfg: model lines torm_fall_<tl,tm,tr,bl,bm,br> (as before) and their frame models torm_fall_<piece>_<sprite>
(origin); sprite h 165 torm_fall_tl yaw=0 height=-4 (and 167, 169, 203, 205, 207: set on the terrain, the river's
level under its middle); frame lines for 234 236 238 272 274 276, 240 242 244 278 280 282 and 117 129 153 157 267 269.
Replaces wave3_ad_fall.py (all of it) and wave3_ad_art.py's FALL, FALL_2, FALL_3 and FALL_4 (only it read FALL; the
other three nothing).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <any value> (the pieces' coverage as the
camera sees them against their sprites' rectangles, and the seams' heights compared), --preview <prefix> (each frame's
whole, and with --pieces 1 each piece), --whole <prefix> (each frame's uncut whole as <prefix>torm_fall_<frame>.glb),
--only <model,...>, --frames 0,1,2,3.
"""
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_deli_boss import join  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_stone_face import view_coverage  # noqa: E402

TILT = math.tan(math.radians(20.0))
W, H = 72, 56

# The picture's kinds of surface: w the water (curtain and pool, with the dark gaps in it), r rock, c the crevice, g
# and G the leaves (ramps 2 and 12). Read off the four frames (which agree on them): ramp 3 in any frame, closed across
# and filled, is water.
KINDS = """
rrrrrrrrrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwcrrrrrrrrrrrrr
rrrrrrrrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwrrrrrrrrrrrrr
rrrrrrrrrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwrrrrrrrrrrrrr
rrrrrrrrrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwrrrrrrrrrrrrr
rrrrrrrrrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwccrrrrrrrrrrrr
rrrrrrrrrrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwccccrrrrrrrrrrr
rrrrrrrrrrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwcccccrrrrrrrrrrr
rrrrrrrrrrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwcccccrrrrrrrrrrr
rrrrrrrrrrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwcccccrrrrrrrrrrr
rrrrrrrrrrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwcccccrrrrrrrrrrr
rrrrrrrrrrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwcccrrrrrrrrrrrr
rrrrrrrrrrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwccrcrrrrrrrrrrr
rrrrrrrrrrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwcccccrrrrrrrrrrr
rrrrrrrrrrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwccrrrrrrrrrrrrr
rrrrrrrrrrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwccrrrrrrrrrrrr
rrrrrrrrrrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwcccrrrrrrrrrrr
rrrrrrrrrrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwcccrrrrrrrrrrr
rrrrrrrrrrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwcccrrrrrrrrrrr
rrrrrrrrrrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwccccrrrrrrrrrrr
rrrrrrrrrrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwccccrrrrrrrrrrr
rrrrrrrrrrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwccrrrrrrrrrrrrr
rrrrrrrrrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwccccrrrrrrrrrrr
rrrrrrrrrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwccccrrrrrrrrrrr
rrrrrrrrrrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwccccrrrrrrrrrrr
rrrrrrrrrrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwccccrrrrrrrrrrr
rrrrrrrrrrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwccccrrrrrrrrrrr
rrrrrrrrrrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwccccrrrrrrrrrrr
rrrrrrrrrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwccccrrrrrrrrrrr
rrrrrrrrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwcccccrrrrrrrrrrr
rrrrrrrrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwccccrrrrrrrrrrr
rrrrrrrrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwccccrrrrrrrrrrr
rrrrrrrrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwccccrrrrrrrrrrr
rrrrrrrrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwccrrrrrrrrrrr
rrrrrrrrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwGrrrrrrrrrrr
rrrrrrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwrgrrrrrrrrr
rrrrrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwgrrrrGrrrr
rrGrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwrrrrGrrrr
rrgGrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwrrrrgrrrr
rrGgwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwrrrgrrrr
rrggwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwrrggrrrr
rrgggwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwrrggrrrr
ggrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwrrrrgrrgg
ggggwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwrrrrggggg
Ggggwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwrrrggggg
GgggwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwrrrggggG
gGggrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwrrrgggGg
ggggrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwrrrggggg
gggGrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwrrrgggggg
gggggrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwrrrggggggg
gggggrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwrrrrrgggGggG
ggggggrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwrrrrrgggggggg
GggggGgrrrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwrrrgGgGGggGG
gggggGggrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwrrrrrrgggGGGggG
GGgGgggggrrrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwrrrrrggggGGGgGG
GGGGGggggrrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwrrrrrrggGgGGGgGG
GGGGGggggrrrwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwrrrrrggggggGGGGG
"""

# The four frames' mean shade of each pixel in its ramp (hex digit; the water's dark gaps are their greys' shades).
SHADES = """
443444455564584559857a84879b89dc9ac9558da67687ca7aa59a545323335443323333
55546555555359458a877a67a878a6adba7d777cc77868c77b857b654334537564344444
5554666666663756aa999a66b778a68ebb6db679d96769c78d768c633113529663454444
5664776666673756ac999966b867a76ebc69d679c9568ac58e867e634113419a82766656
6673977777763756ac8b9867c867899dab74b969d8547bc35c968e643112311323966666
78836a8777751666dd7ba778da668c9e9a95b969e96568d57ca66b633112111324b87777
883245b999621555db3b8667cb546b6e78649747e63337c65a74374321111113246c9777
8322333443421368c74d5556bb637c5d85438736b74335a459754634111111242445b887
4322435444421357a74d44457a615b1a6414591486232384486243241111113213455444
4322437545431155993b468569623a2a64136a1377342374296251361111253113455444
4322436865432558792957847953481a64226a2259242446296251561111431113455444
32224357766213598a4845856863551834134b3259342547388341981123221113355444
222243565321154a7a6747955862612634045a432a25336736a341881111121123355443
222322565331123a678746845981613833047a642856434844b342862113321113355532
323322565311134997463182477472486002681216b7313834b421783111411113395555
23331456531114597845328367755056813178042595414934a622684111211213379654
23353456531212385845527268854146815277052596414a348522782111211312355544
35562256431215383745626166863146817289052587416a546625683111221212354544
556311564233153a3846624145863146a19288152487516a644536472112221212345444
663111564273236a4826624044873134637277152468417a634527442121231112246563
43211156423533792526623144783152616396142336317a634448750113342112246853
432111464221237604166232246931625143870423253178624447451111122112235633
442111464221236616556222344931825002a60422253178715446641111122112225523
442111464111132826956322333931923111a70421253168604446841111122154425523
442111464111131937956421412821633120a61421353157503353832111132136625523
442111454111131a58967411312831421220a71412362157313352a41111142114425423
442111453111121967867510202730821221951421341057212352921111141113425413
442111453111330968757522312630801321a41411233157213452a01111141112425313
442111352113411929448522411321801421831401334149113462911111131333224313
442121352114400807259612502021901420931321455149112462521111121434324314
431121351112210804259613412031731420911221477149212462821111121364424313
42123135111110062534941251213064142183111147917c210552431111111146624313
41134335111100181554830551146454132085111116918a602552612041111134524313
41244435111111250466a513400663641411841021175179312631301111031124424313
411554452012013512458204112473851311840021263169414634421153222123424324
421475554420030411106113301142642730842711351197012a31481467423123404324
430557637554297430115425331140703533a024216a132511153089438b844123404324
4330531047634680024144040010155132219327718503231142116c5379854123324324
4313420115750852172635a30454324252018100316439b4055c35783826544422213323
4332421016782328666c8bb5132671317441634211464aa6438688823111333321324323
4301301214743476a766b98b214b6323b7315965612215ba44a98c758421010222313323
211321112113311367b987776556692237214767d746968ac43998748821010133412203
2302111023115779c58bac6169a9a54a6a8c79737746acbb647c74269311111241301000
0200211346386379865a76b444accaa88a6886a4844d85a4675b84486531212431200000
003011046552356964354363b5999ac579c86b6896688538457998667463224433401000
00102112355443554244675a6466a74559466ab8c8967664657436874444345444502103
00001211347645664634a557a64c744578565878455579a8587323522134556443502144
023031231624318a5455466677546344b984686665755765456655533345655543303223
2223221223532138324423344546775476a476688b955776336667765567553440022111
444002443458522475444354535556759685774767744664475667a44556245340120101
220004344313342467754565645547668873563668554565446568887662575200001001
131112234333364345676446577568756765644645544464446445778521363400113301
312131423344435345568557555479655656776654665373345544657221423102011320
10312110034433356455865775566a755577677655567564444544655423233133103301
210124201334323455556766875669865567666865667775444454544454234402205311
202313224333234444546665677669964467655688756875555454545554422222225023
"""

# Pieces: (name, the sprite in each frame, box (x0, x1, y0, y1) in the picture's plane).
PIECES = [("tl", (165, 234, 240, 117), (-36.0, -12.0, 0.0, 28.0)),
          ("tm", (167, 236, 242, 129), (-12.0, 12.0, 0.0, 28.0)),
          ("tr", (169, 238, 244, 153), (12.0, 36.0, 0.0, 28.0)),
          ("bl", (203, 272, 278, 157), (-36.0, -12.0, -28.0, 0.0)),
          ("bm", (205, 274, 280, 267), (-12.0, 12.0, -28.0, 0.0)),
          ("br", (207, 276, 282, 269), (12.0, 36.0, -28.0, 0.0))]


def model_name(piece, frame):
    """torm_fall_<piece> for the first frame, torm_fall_<piece>_<sprite> for the others."""
    name, sprites, _ = piece
    return "torm_fall_" + name + ("" if frame == 0 else "_%d" % sprites[frame])


# --- The shape -----------------------------------------------------------------------------------------------------
GRID_X = 0.6                # the height field's spacing across (the strands are thin) and down (they are long);
GRID_Y = 1.4                # the sprites' edges are grid lines
POOL = 0.8                  # the pool's water over the ground (the river's level)
LIP = 15.0                  # the curtain's lip at the back
FOOT = -9.0                 # where the curtain meets the pool (y: row 36.5)
ROCK_BACK = 17.0            # the rock's slope: at the back, at the curtain's foot, at the front
ROCK_MID = 9.0
ROCK_FRONT = 7.5
ROCK_LUMPS = 0.8            # the rock's relief per shade of the sprite (light raised, dark sunk)
BANK = 0.8                  # the leaves' banks over the rock's slope
CREVICE = 2.5               # how far the crevice sinks under the curtain
STRANDS = 0.11              # the curtain's corrugation per shade the strands are lighter than round them
STREAK = (0.3, 2.6, 1.6, -0.2, 2.0)   # the curtain's shades: blurred across, down; the wide blur; offset; how
#                                       much the strands stand out of the wide blur (sharpened across)
POOL_SHADE = (5.6, 0.55)    # the pool's shades: round its mean, the sprite's contrast kept
SLOPE = 2.0                 # the steepest rise towards the back (dz / dy; the camera's line of sight is 2.75)
PLUNGE = (0.5, 1.3)         # the white water's ridge along the curtain's foot: height, half-width
PLUNGE_LIGHT = 1.5          # and how many shades lighter it is
FOAM_LIGHT = (3.0, 4.5)     # the pool lighter (churned white) under the foam: shades, and how far down it reaches
SKIRT = -1.5                # the outer edges' skirts reach down to here
SOFT = 0.8                  # how softly the kinds blend (pixels)
SEAM_SAME = 1.0             # the side columns are the middle's periodic field this close to the seams,
SEAM_BLEND = 3.0            # and blend into their own over this far beyond
SEAM_CALM = (1.6, 3.6)      # the moving relief is nil this close to the rows' seam (y 0; the grid rows next to it too)

# The flow: pulses of light down the strands. Period (pixels) PERIOD[0] + PERIOD[1] * tanh(noise), phase noise; their
# light (shades) and relief (pixels) at the pulses' peaks; a quarter period further down each frame.
PERIOD = (11.0, 4.0)
PULSE_LIGHT = 3.4
PULSE_RELIEF = 0.35
RIPPLES = (0.9, 4.6, 0.35)  # the pool's ripples: light (shades), spacing (pixels), how much they curve

# Water bands: (palette index, lowest shade, emission strength); shades lifted by WATER_LIFT (the curtain faces away
# from the sun, and the game reads palette colours darker than the sprite's).
WATER = [(0x31, -99.0, 0.0), (0x33, 2.5, 0.0), (0x35, 4.0, 0.0), (0x38, 6.0, 0.02), (0x3b, 8.5, 0.08),
         (0x3d, 10.2, 0.2), (0x3e, 11.8, 0.34)]
WATER_LIFT = 1.8
WATER_FINISH = dict(metallic=0.0, roughness=0.35)
SKIRT_WATER = 0x38          # the water's skirts (the back's: the river behind running up to the lip)
ROCK = [(0x02, -99.0), (0x04, 3.4), (0x06, 5.0), (0x08, 6.7), (0x0a, 8.4)]   # (palette index, lowest shade)
ROCK_LIFT = 1.8
ROCK_CONTRAST = 1.35         # the sprite's rock shades spread this much round shade 4 (dark clefts, light caps)
ROCK_STEEP = 1.2            # steep rock this many shades darker
ROCK_FINISH = dict(metallic=0.0, roughness=0.75)
CREVICE_INDEX = 0x02        # the crevice: the darkest rock
LEAF = [0x23, 0xc4]         # the dark leaves (and the banks under them), the leaves
LEAF_FINISH = dict(metallic=0.0, roughness=0.55)


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def gauss(a, sx, sy, wrap_x=False):
    """A separable gaussian blur (sigmas in pixels across and down; edges clamped, or wrapped round across)."""
    out = a.astype(float)
    for axis, sigma in ((1, sx), (0, sy)):
        if sigma <= 0:
            continue
        r = int(math.ceil(3 * sigma))
        kern = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2)
        kern /= kern.sum()
        pad = [(0, 0), (0, 0)]
        pad[axis] = (r, r)
        p = np.pad(out, pad, mode="wrap" if (axis == 1 and wrap_x) else "edge")
        acc = np.zeros_like(out)
        for i, kv in enumerate(kern):
            sl = [slice(None), slice(None)]
            sl[axis] = slice(i, i + out.shape[axis])
            acc += kv * p[tuple(sl)]
        out = acc
    return out


def bilinear(a, u, v, wrap_x=False):
    """a at pixel coordinates (u across, v down; pixel centres at whole numbers)."""
    h, w = a.shape
    if wrap_x:
        u0 = np.floor(u).astype(int)
        fu = u - u0
        ua, ub = u0 % w, (u0 + 1) % w
    else:
        u = np.clip(u, 0, w - 1)
        u0 = np.minimum(np.floor(u).astype(int), w - 2)
        fu = u - u0
        ua, ub = u0, u0 + 1
    v = np.clip(v, 0, h - 1)
    v0 = np.minimum(np.floor(v).astype(int), h - 2)
    fv = v - v0
    return (1 - fv) * ((1 - fu) * a[v0, ua] + fu * a[v0, ub]) + fv * ((1 - fu) * a[v0 + 1, ua] + fu * a[v0 + 1, ub])


class Field:
    """A smooth field over the picture made from a pixel array: the middle column's from its 24 columns wrapped round
    (periodic: it tiles), the side columns' from the whole picture, blended into the middle's (continued round) over
    SEAM_BLEND pixels next to the seams, so that any two pieces meet."""

    def __init__(self, a, sx, sy):
        self.full = gauss(a, sx, sy)
        self.mid = gauss(a[:, 24:48], sx, sy, wrap_x=True)

    def __call__(self, x, y):
        v = 28.0 - y - 0.5
        full = bilinear(self.full, x + 36.0 - 0.5, v)
        mid = bilinear(self.mid, np.mod(x + 12.0, 24.0) - 0.5, v, wrap_x=True)
        w = 1.0 - smoothstep(12.0 + SEAM_SAME, 12.0 + SEAM_SAME + SEAM_BLEND, np.abs(x))
        return full * (1 - w) + mid * w


def periodic_noise(x, seed, terms=8):
    """A smooth function of x, periodic every 24 pixels (the middle column), the same everywhere."""
    rng = np.random.RandomState(seed)
    acc = np.zeros_like(x)
    for n in range(1, terms + 1):
        amp, phase = rng.uniform(0.2, 1.0), rng.uniform(0.0, 2 * math.pi)
        acc += amp / n ** 0.5 * np.sin(2 * math.pi * n * x / 24.0 + phase)
    return acc


def art():
    kinds = [list(r) for r in KINDS.strip().split("\n")]
    shades = np.array([[int(ch, 16) for ch in r] for r in SHADES.strip().split("\n")], float)
    return kinds, shades


def curtain_z(y):
    """The curtain's height: its lip at the back rounding over, steepest in its upper middle, easing into the pool."""
    t = np.clip((y - FOOT) / (28.0 - FOOT), 0.0, 1.0)
    s = t * t * (3 - 2 * t)
    return POOL + (LIP - POOL) * (0.3 * t + 0.7 * s)


def rock_base(y):
    return np.interp(y, [-28.0, FOOT, 28.0], [ROCK_FRONT, ROCK_MID, ROCK_BACK])


class Base:
    """The fields every frame shares, on the grid (rows of y from the front, columns of x from the left)."""

    def __init__(self):
        kinds, shades = art()
        self.xs = np.round(np.arange(-36.0, 36.0 + 1e-6, GRID_X), 6)
        self.ys = np.round(np.arange(-28.0, 28.0 + 1e-6, GRID_Y), 6)
        X, Y = np.meshgrid(self.xs, self.ys)
        self.X, self.Y = X, Y
        masks = {}
        for kind in "wrcgG":
            masks[kind] = np.array([[1.0 if ch == kind else 0.0 for ch in row] for row in kinds])
        masks["g"] = masks["g"] + masks["G"]
        soft = {kind: np.clip(Field(masks[kind], SOFT, SOFT)(X, Y), 0.0, None) for kind in "wrcg"}
        total = sum(soft.values()) + 1e-9
        self.soft = {kind: soft[kind] / total for kind in soft}
        self.bright = np.clip(Field(masks["G"], SOFT, SOFT)(X, Y), 0, 1)
        # The water's shades: blurred along the fall on the curtain (streaks), roundly on the pool.
        water_px = np.array([[ch == "w" for ch in row] for row in kinds])
        filled = np.where(water_px, shades, 2.0)
        along = Field(filled, STREAK[0], STREAK[1])(X, Y)
        wide = Field(filled, STREAK[2], STREAK[1])(X, Y)
        round_ = Field(filled, 1.0, 1.0)(X, Y)
        broad = Field(filled, 2.0, 2.0)(X, Y)
        on_curtain = smoothstep(FOOT - 2.5, FOOT + 1.5, Y)
        self.on_curtain = on_curtain
        self.highpass = (along - wide) * on_curtain
        self.strand = np.clip(self.highpass / 2.5, 0.0, 1.0)
        curtain_shade = wide + STREAK[3] + STREAK[4] * (along - wide)
        pool_shade = POOL_SHADE[0] + POOL_SHADE[1] * (0.7 * round_ + 0.3 * broad - POOL_SHADE[0])
        self.water_shade = curtain_shade * on_curtain + pool_shade * (1 - on_curtain)
        rock_px = Field(shades, 0.7, 0.9)(X, Y)
        self.rock_shade = Field(shades, 0.5, 0.5)(X, Y)
        # The heights of each kind, blended.
        plunge = np.exp(-((Y - FOOT) / PLUNGE[1]) ** 2)  # the white water where the curtain plunges
        churn = np.clip(1.0 - (FOOT - Y) / FOAM_LIGHT[1], 0.0, 1.0) * (Y < FOOT)  # white water under the foam
        self.water_shade = self.water_shade + PLUNGE_LIGHT * plunge + FOAM_LIGHT[0] * churn ** 1.5
        zw = np.where(Y > FOOT, curtain_z(Y), POOL) + STRANDS * self.highpass + PLUNGE[0] * plunge
        zr = rock_base(Y) + ROCK_LUMPS * (rock_px - 4.0)
        zc = curtain_z(Y) - CREVICE
        zg = rock_base(Y) + BANK
        s = self.soft
        z = s["w"] * zw + s["r"] * zr + s["c"] * zc + s["g"] * zg
        for j in range(1, z.shape[0]):  # no rise towards the back steeper than SLOPE (no folds towards the camera)
            z[j] = np.minimum(z[j], z[j - 1] + SLOPE * GRID_Y)
        self.z = z
        # The pulses' periods and phases, periodic in x.
        self.period = PERIOD[0] + PERIOD[1] * np.tanh(periodic_noise(X, 3))
        self.phase = 0.6 * periodic_noise(X, 7)
        light = on_curtain * (0.55 + 0.45 * smoothstep(-6.0, 12.0, Y)) * (1 - 0.5 * smoothstep(25.0, 28.0, Y))
        self.pulse_light = light
        self.pulse_relief = light * smoothstep(SEAM_CALM[0], SEAM_CALM[1], np.abs(Y))
        # The pool's ripples flowing away down the screen (curved by a periodic warp across).
        self.ripple_weight = (1 - on_curtain) * smoothstep(FOOT - 3.0, FOOT - 9.0, Y)
        self.ripple_warp = periodic_noise(X, 13, terms=4)

    def frame(self, f):
        """The heights and the water's shades of frame f (0-3): the pulses a quarter period further down each frame, and
        the pool's ripples a quarter of their spacing."""
        u = (self.Y + f * self.period / 4.0) / self.period + self.phase
        bump = (0.5 - 0.5 * np.cos(2 * math.pi * u)) ** 3
        z = self.z + PULSE_RELIEF * self.strand * self.pulse_relief * bump * self.soft["w"]
        shade = self.water_shade + PULSE_LIGHT * self.strand * self.pulse_light * (bump - 0.25)
        v = (self.Y + f * RIPPLES[1] / 4.0) / RIPPLES[1] + RIPPLES[2] * self.ripple_warp
        shade = shade + RIPPLES[0] * self.ripple_weight * np.sin(2 * math.pi * v)
        return z, shade


# --- Materials -----------------------------------------------------------------------------------------------------

def materials():
    pal = k.level_palette()
    m = {}
    for index, _, glow in WATER:
        if glow > 0:
            m[index] = k.material("fall_water", palette=index, emission=pal[index], emission_strength=glow,
                                  **WATER_FINISH)
        else:
            m[index] = k.material("fall_water", palette=index, **WATER_FINISH)
    for index, _ in ROCK:
        m[index] = k.material("fall_rock", palette=index, **ROCK_FINISH)
    for index in LEAF:
        m[index] = k.material("fall_leaf", palette=index, **LEAF_FINISH)
    return m


ORDER = [w[0] for w in WATER] + [r[0] for r in ROCK] + LEAF   # the materials' slots, in this order




# --- The surface ---------------------------------------------------------------------------------------------------

def picture_normals(z):
    """The height field's normals in the picture's plane (central differences over the whole picture, so that pieces
    agree along their seams)."""
    gy, gx = np.gradient(z, GRID_Y, GRID_X)
    n = np.stack([-gx, -gy, np.ones_like(z)], -1)
    return n / np.linalg.norm(n, axis=-1, keepdims=True)


def shear_arrays(points, normals):
    """To the game's camera: each point moved along its line of sight to its height (y - z tan 20), the normals with
    it (the shear's inverse transpose)."""
    p = points.copy()
    p[..., 1] -= p[..., 2] * TILT
    n = normals.copy()
    n[..., 2] += TILT * n[..., 1]
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    return p, n


def shear_object(obj):
    """shear_arrays for a mesh object (its corner normals kept as custom normals)."""
    mesh = obj.data
    normals = [Vector(c.vector) for c in mesh.corner_normals]
    for v in mesh.vertices:
        v.co.y -= v.co.z * TILT
    out = [Vector((n.x, n.y, n.z + TILT * n.y)).normalized() for n in normals]
    mesh.normals_split_custom_set([tuple(n) for n in out])
    mesh.update()


def build_mesh(name, verts, tris, mat_slots, loop_normals, mats):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([tuple(v) for v in verts.tolist()], [], [tuple(t) for t in tris.tolist()])
    for mat in mats:
        mesh.materials.append(mat)
    mesh.polygons.foreach_set("material_index", np.asarray(mat_slots, np.int32))
    mesh.polygons.foreach_set("use_smooth", np.ones(len(tris), bool))
    mesh.update()
    mesh.normals_split_custom_set([tuple(n) for n in loop_normals.tolist()])
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


class Painter:
    """Cuts a piece's triangles along smooth contours of its fields (polish_orb_red.band_split's way, with every field
    carried to the new vertices): first where the water meets the rest, then where the rock meets the crevice and
    the leaves' banks, then each kind's bands of shade; every edge cut once, so neighbours (and neighbouring pieces,
    whose seam vertices are the same) share the cuts."""

    FIELDS = ("fw", "fr", "fc", "sw", "sr")

    def __init__(self, points, normals, fields):
        self.co = [tuple(p) for p in points.tolist()]
        self.no = [tuple(n) for n in normals.tolist()]
        self.val = {name: list(fields[name].tolist()) for name in self.FIELDS}
        self.cuts = {}
        self.polys, self.mats = [], []

    def _cut(self, a, b, name, t):
        key = (min(a, b), max(a, b), name, t)
        if key not in self.cuts:
            va, vb = self.val[name][a], self.val[name][b]
            f = (t - va) / (vb - va)
            pa, pb = self.co[a], self.co[b]
            na, nb = self.no[a], self.no[b]
            self.co.append(tuple(pa[i] + (pb[i] - pa[i]) * f for i in range(3)))
            n = [na[i] + (nb[i] - na[i]) * f for i in range(3)]
            length = math.sqrt(sum(c * c for c in n)) or 1.0
            self.no.append(tuple(c / length for c in n))
            for fn in self.FIELDS:
                self.val[fn].append(t if fn == name else self.val[fn][a] + (self.val[fn][b] - self.val[fn][a]) * f)
            self.cuts[key] = len(self.co) - 1
        return self.cuts[key]

    def _clip(self, poly, name, t, above):
        vals = self.val[name]
        out = []
        for i in range(len(poly)):
            a, b = poly[i], poly[(i + 1) % len(poly)]
            ina, inb = (vals[a] >= t) == above, (vals[b] >= t) == above
            if ina:
                out.append(a)
            if ina != inb:
                out.append(self._cut(a, b, name, t))
        return out

    def split(self, poly, name, t):
        """The polygon's parts at or above t and below it (either may be empty)."""
        vals = [self.val[name][i] for i in poly]
        if min(vals) >= t:
            return poly, []
        if max(vals) < t:
            return [], poly
        return self._clip(poly, name, t, True), self._clip(poly, name, t, False)

    def bands(self, poly, name, bands):
        """Paints the polygon in bands [(palette index, lowest value)] of a field (ascending)."""
        rest = poly
        for b in range(len(bands) - 1, 0, -1):
            if len(rest) < 3:
                return
            upper, rest = self.split(rest, name, bands[b][1])
            if len(upper) >= 3:
                self.polys.append(upper)
                self.mats.append(bands[b][0])
        if len(rest) >= 3:
            self.polys.append(rest)
            self.mats.append(bands[0][0])

    def paint(self, tri):
        water, other = self.split(list(tri), "fw", 0.0)
        if len(water) >= 3:
            self.bands(water, "sw", [(w[0], w[1]) for w in WATER])
        if len(other) >= 3:
            rock, other = self.split(other, "fr", 0.0)
            if len(rock) >= 3:
                self.bands(rock, "sr", ROCK)
            if len(other) >= 3:
                crevice, bank = self.split(other, "fc", 0.0)
                for part, index in ((crevice, CREVICE_INDEX), (bank, LEAF[0])):
                    if len(part) >= 3:
                        self.polys.append(part)
                        self.mats.append(index)

    def triangles(self):
        """The painted polygons as triangles (fans: the polygons are convex), with their materials."""
        tris, mats = [], []
        for poly, index in zip(self.polys, self.mats):
            for i in range(1, len(poly) - 1):
                tris.append((poly[0], poly[i], poly[i + 1]))
                mats.append(index)
        return tris, mats


def surface(base, z, shade, box, m, name, outer):
    """A piece's part of the height field (its box's grid, in the picture's plane), painted along smooth contours,
    with skirts down its outer edges (outer: which of left, right, front, back), sheared to the camera."""
    i0, i1 = (int(round((v + 36.0) / GRID_X)) for v in box[:2])
    j0, j1 = (int(round((v + 28.0) / GRID_Y)) for v in box[2:])
    sub = (slice(j0, j1 + 1), slice(i0, i1 + 1))
    X, Y, Z = base.X[sub], base.Y[sub], z[sub]
    N = picture_normals(z)[sub]
    ny, nx = Z.shape
    s = {kind: base.soft[kind][sub] for kind in "wrcg"}
    steep = np.clip((0.9 - N[..., 2]) / 0.45, 0.0, 1.0)
    fields = {"fw": s["w"] - np.maximum(np.maximum(s["r"], s["c"]), s["g"]),
              "fr": s["r"] - np.maximum(s["c"], s["g"]),
              "fc": s["c"] - s["g"],
              "sw": shade[sub] + WATER_LIFT,
              "sr": 4.0 + ROCK_CONTRAST * (base.rock_shade[sub] - 4.0) + ROCK_LIFT - ROCK_STEEP * steep}
    fields = {key: value.ravel() for key, value in fields.items()}
    painter = Painter(np.stack([X, Y, Z], -1).reshape(-1, 3), N.reshape(-1, 3), fields)
    index = np.arange(ny * nx).reshape(ny, nx)
    for j in range(ny - 1):
        for i in range(nx - 1):
            a, b, c, d = (int(v) for v in (index[j, i], index[j, i + 1], index[j + 1, i + 1], index[j + 1, i]))
            if abs(Z[j, i] - Z[j + 1, i + 1]) <= abs(Z[j, i + 1] - Z[j + 1, i]):
                painter.paint((a, b, c))
                painter.paint((a, c, d))
            else:
                painter.paint((a, b, d))
                painter.paint((b, c, d))
    tris, mats = painter.triangles()
    verts, normals = list(painter.co), list(painter.no)
    # Skirts down the outer edges: their own vertices (flat, facing out), coloured by the kind along the edge.
    kind_at = np.stack([s["w"], s["r"], s["c"], s["g"]]).reshape(4, -1).argmax(0)
    edges = {"left": (index[:, 0], (-1.0, 0.0, 0.0), True), "right": (index[:, -1], (1.0, 0.0, 0.0), False),
             "front": (index[0, :], (0.0, -1.0, 0.0), False), "back": (index[-1, :], (0.0, 1.0, 0.0), True)}
    for side in outer:
        line, out_n, reverse = edges[side]
        line = [int(v) for v in (line[::-1] if reverse else line)]
        first = len(verts)
        for v in line:
            top = painter.co[v]
            verts += [top, (top[0], top[1], SKIRT)]
            normals += [out_n, out_n]
        for q in range(len(line) - 1):
            t0, b0, t1, b1 = first + 2 * q, first + 2 * q + 1, first + 2 * q + 2, first + 2 * q + 3
            kind = int(np.bincount([kind_at[line[q]], kind_at[line[q + 1]]], minlength=4).argmax())
            index_ = {0: SKIRT_WATER, 1: ROCK[0][0], 2: CREVICE_INDEX, 3: LEAF[0]}[kind]
            tris += [(t0, b0, b1), (t0, b1, t1)]
            mats += [index_, index_]
    verts, normals = shear_arrays(np.array(verts, float), np.array(normals, float))
    tris = np.array(tris, int)
    used = [i for i in ORDER if i in set(mats)]
    slot = {i: n for n, i in enumerate(used)}
    return build_mesh(name, verts, tris, [slot[i] for i in mats], normals[tris.ravel()], [m[i] for i in used])


# --- Foam ----------------------------------------------------------------------------------------------------------
# Where the foam is born (y) and how much of it across 24 pixels: densest at the curtain's foot, thinning out down the
# pool; each set of it drifts FOAM_DRIFT down a frame (and a little sideways), growing and then shrinking.
FOAM_ROWS = [(-9.7, 8), (-11.0, 8), (-12.4, 7), (-13.9, 6), (-15.6, 5), (-17.5, 4)]
FOAM_DRIFT = 1.2
FOAM_SIZE = [0.6, 1.0, 0.9, 0.55]                # by age (frames since it was born)
FOAM_SHADE = [0x3d, 0x3d, 0x3b, 0x3b]
FOAM_R = (0.4, 0.8)                              # a froth's bubbles: 1-3 of them, this big
FOAM_FLAT = 0.45                                 # the bubbles' height over their radius
SPLASH_Y = -9.0                                  # the white water churning along the curtain's foot
SPLASH_STEP = 1.25                               # a heap every this far across, bobbing and swelling
SPLASH_R = (0.5, 1.15)
SPLASH_SIZE = [0.8, 1.0, 0.85, 0.7]
SPLASH_BOB = [0.0, 0.22, 0.1, -0.05]
SPLASH_SHADE = [0x3e, 0x3d, 0x3d, 0x3b]


def froth(rng, x, y, splash):
    """One froth (its bubbles: (dx, dy, radius)), its phase and sideways drift."""
    if splash:
        return [(0.0, 0.0, rng.uniform(*SPLASH_R))], int(rng.randint(4)), 0.0
    count = int(rng.randint(1, 4))
    bubbles = [(rng.uniform(-0.6, 0.6) if c else 0.0, rng.uniform(-0.45, 0.45) if c else 0.0, rng.uniform(*FOAM_R))
               for c in range(count)]
    return bubbles, int(rng.randint(4)), rng.uniform(-0.3, 0.3)


def foam_specs():
    """Every froth: (x, y, bubbles, phase, sideways drift, splash?). The middle column's are a periodic set (each also
    24 pixels left and right of itself), the side columns' their own, clear of the seams."""
    out = []
    rng = np.random.RandomState(11)
    rows = [(y, n, False) for y, n in FOAM_ROWS] + [(SPLASH_Y, int(round(24.0 / SPLASH_STEP)), True)]
    for row, (y0, count, splash) in enumerate(rows):
        for n in range(count):
            x = -12.0 + (n + 0.5) * 24.0 / count + rng.uniform(-0.35, 0.35) * 24.0 / count + (0.5 if row % 2 else 0.0)
            x = (x + 12.0) % 24.0 - 12.0
            bubbles, phase, drift = froth(rng, x, y0, splash)
            y = y0 + (rng.uniform(-0.6, 0.5) if splash else rng.uniform(-0.55, 0.55))
            for shift in (0.0, -24.0, 24.0):
                out.append((x + shift, y, bubbles, phase, drift, splash))
    for lo, hi in ((-32.0, -14.8), (14.8, 26.0)):
        for y0, count, splash in rows:
            n_side = max(1, int(round(count * (hi - lo) / 24.0)))
            for n in range(n_side):
                x = lo + (n + 0.5) * (hi - lo) / n_side + rng.uniform(-0.3, 0.3) * (hi - lo) / n_side
                bubbles, phase, drift = froth(rng, x, y0, splash)
                y = y0 + (rng.uniform(-0.6, 0.5) if splash else rng.uniform(-0.55, 0.55))
                out.append((x, y, bubbles, phase, drift, splash))
    return out


def dome(name, centre, radii, mat, segments=6):
    """A bubble of foam: the upper half of an ellipsoid on explicit rings (the same every run), closed underneath, its
    rim a little under the water."""
    cx, cy, cz = centre
    rx, ry, rz = radii
    rings = []
    for e in (-12.0, 42.0):
        a = math.radians(e)
        rings.append([(cx + rx * math.cos(a) * math.cos(2 * math.pi * s / segments),
                       cy + ry * math.cos(a) * math.sin(2 * math.pi * s / segments), cz + rz * math.sin(a))
                      for s in range(segments)])
    verts = [p for ring in rings for p in ring] + [(cx, cy, cz + rz)]
    faces = []
    for r in range(len(rings) - 1):
        for s in range(segments):
            a, b = r * segments + s, r * segments + (s + 1) % segments
            faces.append((a, b, b + segments, a + segments))
    top = len(verts) - 1
    last = (len(rings) - 1) * segments
    faces += [(last + s, last + (s + 1) % segments, top) for s in range(segments)]
    faces.append(tuple(reversed(range(segments))))
    obj = k.mesh_object(name, verts, faces, mat)
    k.smooth(obj, 80.0)
    return obj


_WATER_MASK = None


def in_water(x, y):
    global _WATER_MASK
    if _WATER_MASK is None:
        _WATER_MASK = Field(np.array([[1.0 if ch == "w" else 0.0 for ch in row] for row in art()[0]]), 0.6, 0.6)
    return float(_WATER_MASK(np.array([x]), np.array([y]))[0])


def foam(base, frame, m, box):
    """The frame's foam that reaches into box, cut to it (in the picture's plane), as objects."""
    objs = []
    x0, x1, y0, y1 = box
    for n, (x, y, bubbles, phase, drift, splash) in enumerate(foam_specs()):
        age = (frame + phase) % 4
        if splash:
            size, mat, pz, flat = SPLASH_SIZE[age], m[SPLASH_SHADE[age]], POOL + 0.25 + SPLASH_BOB[age], 0.6
            cx, cy = x, y
        else:
            size, mat, pz, flat = FOAM_SIZE[age], m[FOAM_SHADE[age]], POOL + 0.05, FOAM_FLAT
            cx, cy = x + drift * age, y - FOAM_DRIFT * age
        if in_water(cx, cy) < 0.8:
            continue
        for b, (dx, dy, r) in enumerate(bubbles):
            rr = r * size
            px, py = cx + dx, cy + dy
            if px + rr <= x0 or px - rr >= x1 or py + rr <= y0 or py - rr >= y1:
                continue
            obj = dome("foam%d_%d" % (n, b), (px, py, pz), (rr, rr * 0.85, rr * flat), mat,
                       7 if splash else 6 if rr > 0.6 else 5)
            inside = x0 < px - rr and px + rr < x1 and y0 < py - rr and py + rr < y1
            if inside:
                objs.append(obj)
                continue
            part = mk.cut(obj, (x0, x1, y0, y1), mat)
            bpy.data.objects.remove(obj)
            if part is not None:
                objs.append(part)
    return objs


# --- Leaves --------------------------------------------------------------------------------------------------------
LEAF_SPACING = 2.7          # the rosettes' spacing on the banks
LEAF_LENGTH = (2.2, 3.4)
LEAF_WIDTH = (0.9, 1.4)
LEAF_LIFT = (0.4, 0.9)      # how far the tips curl up


def grid_sample(base, a, x, y):
    """A grid array at a point (bilinear)."""
    fx, fy = (x + 36.0) / GRID_X, (y + 28.0) / GRID_Y
    i, j = min(int(fx), a.shape[1] - 2), min(int(fy), a.shape[0] - 2)
    u, v = fx - i, fy - j
    return float((1 - v) * ((1 - u) * a[j, i] + u * a[j, i + 1]) + v * ((1 - u) * a[j + 1, i] + u * a[j + 1, i + 1]))


def blade(name, root, angle, length, width, lift, mat):
    """A pointed leaf lying on the bank from its root, its tip curling up, a crease along its middle."""
    d = Vector((math.cos(angle), math.sin(angle), 0.0))
    side = Vector((-d.y, d.x, 0.0))
    verts, faces = [], []
    ts = (0.0, 0.25, 0.55, 0.82, 1.0)
    for t in ts:
        p = Vector(root) + d * (length * t) + Vector((0.0, 0.0, lift * t * t))
        w = 0.5 * width * math.sin(math.pi * min(1.0, t * 1.05)) ** 0.8
        verts += [tuple(p + side * w), tuple(p + Vector((0.0, 0.0, 0.16 * w))), tuple(p - side * w)]
    for s in range(len(ts) - 1):
        l0, m0, r0, l1, m1, r1 = 3 * s, 3 * s + 1, 3 * s + 2, 3 * s + 3, 3 * s + 4, 3 * s + 5
        faces += [(m0, m1, l1, l0), (r0, r1, m1, m0)]
    obj = k.mesh_object(name, verts, faces, mat)
    k.smooth(obj, 70.0)
    return obj


def leaves(base, m, box):
    """Rosettes of leaves on the banks at the pool's corners (where the sprite draws leaves), inside box."""
    x0, x1, y0, y1 = box
    rng = np.random.RandomState(5 if x0 < 0 else 6)
    objs = []
    n = 0
    y = y0 + 0.9
    while y < y1 - 0.9:
        x = x0 + 0.9 + (0.5 * LEAF_SPACING if int((y - y0) / LEAF_SPACING) % 2 else 0.0)
        while x < x1 - 0.9:
            px, py = x + rng.uniform(-0.6, 0.6), y + rng.uniform(-0.6, 0.6)
            px, py = min(max(px, x0 + 0.6), x1 - 0.6), min(max(py, y0 + 0.6), y1 - 0.6)
            if grid_sample(base, base.soft["g"], px, py) > 0.55:
                bright = grid_sample(base, base.bright, px, py)
                a0 = rng.uniform(0, 2 * math.pi)
                for b in range(5):
                    angle = a0 + 2 * math.pi * b / 5 + rng.uniform(-0.3, 0.3)
                    length = rng.uniform(*LEAF_LENGTH)
                    tip = (px + length * math.cos(angle), py + length * math.sin(angle))
                    if not (x0 + 0.3 < tip[0] < x1 - 0.3 and y0 + 0.3 < tip[1] < y1 - 0.3):
                        length *= 0.55
                        tip = (px + length * math.cos(angle), py + length * math.sin(angle))
                        if not (x0 + 0.3 < tip[0] < x1 - 0.3 and y0 + 0.3 < tip[1] < y1 - 0.3):
                            continue
                    shade = rng.uniform(0, 1) + 0.6 * bright
                    mat = m[LEAF[1]] if shade > 0.45 else m[LEAF[0]]
                    z = grid_sample(base, base.z, px, py) + 0.15
                    objs.append(blade("leaf%d" % n, (px, py, z), angle, length, rng.uniform(*LEAF_WIDTH),
                                      rng.uniform(*LEAF_LIFT), mat))
                    n += 1
            x += LEAF_SPACING
        y += LEAF_SPACING * 0.87
    return objs


# --- The pieces ----------------------------------------------------------------------------------------------------
STATS = False
OUTER = {"tl": ("left", "back"), "tm": ("back",), "tr": ("right", "back"), "bl": ("left", "front"),
         "bm": ("front",), "br": ("right", "front")}


def piece_parts(base, z, shade, frame, m, piece, name):
    """A piece of one frame, in the game's axes (sheared), at its sprite's centre."""
    pname, _, box = piece
    parts = [surface(base, z, shade, box, m, name + "_surface", OUTER[pname])]
    if box[2] < 0:
        extra = foam(base, frame, m, box)
        if pname != "bm":
            extra += leaves(base, m, box)
        for obj in extra:
            shear_object(obj)
        parts += extra
    centre = Vector(((box[0] + box[1]) / 2, (box[2] + box[3]) / 2, 0.0))
    mk.transform(parts, Matrix.Translation(-centre))
    bpy.context.view_layer.update()
    triangulate(parts)
    if STATS:
        foam_tris = sum(mk.triangles([o]) for o in parts if o.name.startswith("foam"))
        leaf_tris = sum(mk.triangles([o]) for o in parts if o.name.startswith("leaf"))
        print("   %s: surface %d, foam %d, leaves %d triangles" % (name, mk.triangles(parts[:1]), foam_tris, leaf_tris))
    obj = join(parts, name)
    obj.data.name = name
    return obj


def whole_parts(base, z, shade, frame, m, name):
    """The whole picture of one frame (uncut, sheared), for checks and previews."""
    box = (-36.0, 36.0, -28.0, 28.0)
    parts = [surface(base, z, shade, box, m, name + "_surface", ("left", "right", "front", "back"))]
    extra = (foam(base, frame, m, box) + leaves(base, m, (-36.0, -12.0, -28.0, 0.0)) +
             leaves(base, m, (12.0, 36.0, -28.0, 0.0)))
    for obj in extra:
        shear_object(obj)
    parts += extra
    triangulate(parts)
    obj = join(parts, name)
    return obj


def seam_report(base):
    """The seams' heights and normals in every frame (they must not depend on the frame or the neighbour)."""
    i_l, i_r = int(round(24.0 / GRID_X)), int(round(48.0 / GRID_X))  # x -12 and 12
    j_s = int(round(28.0 / GRID_Y))                                  # y 0
    worst_cols, worst_rows, worst_n = 0.0, 0.0, 0.0
    rows = []
    for f in range(4):
        z, _ = base.frame(f)
        n = picture_normals(z)
        worst_cols = max(worst_cols, float(np.abs(z[:, i_l] - z[:, i_r]).max()))
        worst_n = max(worst_n, float(np.abs(n[:, i_l] - n[:, i_r]).max()))
        rows.append((z[j_s].copy(), n[j_s].copy()))
    for a in range(4):
        for b in range(4):
            worst_rows = max(worst_rows, float(np.abs(rows[a][0] - rows[b][0]).max()))
            worst_n = max(worst_n, float(np.abs(rows[a][1] - rows[b][1]).max()))
    print("seams: x -12 against x 12 (any frame) %.6f px; y 0 between frames %.6f px; normals %.6f" % (
        worst_cols, worst_rows, worst_n))


def build():
    global STATS
    options = k.args()
    STATS = "stats" in options
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    frames = [int(f) for f in options.get("frames", "0,1,2,3").split(",")]
    k.reset()
    bpy.context.scene.view_settings.view_transform = "Standard"
    base = Base()
    m = materials()
    if "check" in options:
        seam_report(base)
    for f in frames:
        z, shade = base.frame(f)
        if "whole" in options or "preview" in options:
            whole = whole_parts(base, z, shade, f, m, "torm_fall_%d" % f)
            print("== whole frame %d: %d triangles" % (f, mk.triangles([whole])))
            if "check" in options:
                mk.compare("whole, frame %d, as the camera sees it" % f, view_coverage([whole], W, H),
                           [[True] * W for _ in range(H)])
            if "whole" in options:
                mk.export([whole], options["whole"] + "torm_fall_%d.glb" % f)
            if "preview" in options:
                mk.preview(options["preview"] + "whole_%d" % f, [whole], size=(W, H), scale=8, distance=2.2)
            bpy.data.objects.remove(whole)
        for piece in PIECES:
            name = model_name(piece, f)
            if only and name not in only:
                continue
            obj = piece_parts(base, z, shade, f, m, piece, name)
            if "check" in options:
                mk.compare("%s (H %d) as the camera sees it" % (name, piece[1][f]), view_coverage([obj], 24, 28),
                           [[True] * 24 for _ in range(28)])
            mk.report(name, [obj], os.path.join(out, name + ".glb"))
            if "preview" in options and options.get("pieces") == "1":
                mk.preview(options["preview"] + name, [obj])
            data = obj.data
            bpy.data.objects.remove(obj)
            if data.users == 0:
                bpy.data.meshes.remove(data)


if __name__ == "__main__":
    build()
