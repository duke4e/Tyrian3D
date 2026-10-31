"""IXMUCANE's boss (sheet R, written r in models.cfg), polished (2026-10-22, round 36): the machine heap (16 2x2
sprites), the boss's eye and lamps lit (enemies of their own over the machine, four frames each) and the heap of
boulders that covers it (12 2x2 sprites). It replaces wave3_af_heap.py (all of it: the heaps of convex boulders on a
mound, the machine as stepped slabs painted pixel by pixel, the eye and lamps halfway through their animation).

Where it appears: IXMUCANE (episode 3, t4300) lays it out from ground enemies: the machine heap 642-657 (event 6, link
142) at x 124 + 24 i, 84 - 28 j pixels above the bottom row, the sheet's layout (R 159 161 163 165 / 197 199 201 203 /
235 237 239 241 / 273 275 277 279: one 96 x 112 picture); the eye 658 (R 167, link 142) at x 134, 53 above (its
sprite's top left pixel at the picture's column 10, row 31) and the lamps 659 (R 169, link 42) at x 134, 25 above (row
59); the cover 630-641 (event 10, ground 2, link 141: drawn after the ground enemies, over the machine heap) at x 100 +
24 i (R 153 155 157 / 191 193 195 / 229 231 233 / 267 269 271: one 72 x 112 picture, 24 pixels left of the machine
heap, so its right two thirds lie over the machine's 48 left columns and hide the machine, the eye and the lamps).
The boss bar is link 142; the events then hold the heaps on the screen and slide them apart and together again
(event 20: the cover about 27 pixels left and back, then the machine heap with the eye and lamps right and back),
over and over. Every heap piece is armour 255 or 0 (never destroyed); the eye (armour 25, animate 1: 167 167 205 205
243 243 281 281 243 243 205 205, cooling from white-hot yellow to red and back) is the target; the lamps (armour 25,
animate 1: 169 ... 283) switch at armour 10 to their damaged sprite R 115, which is blank (default volume: nothing),
so the machine's own dull lamps show then. REEF (episode 6, t5700: compose.expand takes IXMUCANE's boss block by its
boss bar's link 142) brings the machine heap (1548-1563) and the eye (1564) the same way, without the cover and the
lamps: there the machine and its own dull lamps show all fight long. No other enemy, launched ones included, shows
any of these sprites (frame models are safe); R 155 is also dropped by enemies in SAVARA Y's arcade games, where it
shows that piece of the cover. None is another sprite's pixels mirrored, turned or in other ramps.

As the sprites and their 4x upscales draw them (the pictures' columns and rows; lit from the upper left):
- the machine heap: a grey machine on its left (ramp 0, columns 0-37 of rows 13-87; the sprite cuts it straight at
  column 0, where the cover lies over it): a vent block with four vertical fins (columns 5, 9, 13, 17 of rows 19-35,
  their lower ends lit 08-0d) and lower ribs between them; a silver ring (columns 9-33 of rows 37-57) round a big red
  eye (ramp 7 with deep red edges of ramp 4: columns 11-31 of rows 39-55); a lit rod right of the ring (columns
  32-35); under the ring a spine (columns 12-31 of rows 57-86) with three red lamps in silver sockets, the largest
  first (columns 16-27 of rows 60-66, 18-25 of 71-75, 19-24 of 80-82); dark rails off to the left (columns 0-12 of
  rows 66-86); boulders heaped over its top (rows 5-14) and all over the picture's right (columns 28-95): angular
  brown-grey stones (ramp 10, a2-ab) and golden tan ones (ramp 1), a few blue-grey (ramp 0), lit facets at their
  upper left, dark crevices (01, a0-a2) between them;
- the eye's frames (R 167 205 243 281): the lit orb, drawn 3 rows lower than the machine's eye (sprite rows 11-27 =
  the picture's rows 42-58), with the machine's greys round it; the lamps' frames (R 169 207 245 283): the machine's
  pixels round the three lamps (rows 0-8, 11-17, 20-27), each lamp lit in turn;
- the cover: a heap of the same boulders, about 22 of them, 6-25 pixels across (columns 2-64 of rows 0-102).

Built for the game's camera, as GYGES' maw and CORAL's citadel are: each heap is one heightfield in the picture's
plane (x, y as the sprites draw it, z up from the ground), on a grid STEP apart whose lines are the sprites' edges (so
each piece is the cells of its sprite's box: no mesh cutting; walls where cut, dark, inside the whole), its outline
the sprite's (smoothed a little), sheared along the camera's line of sight (y - z tan 20, polish_gyges_wall's
Plate and shear_to_camera), so the camera sees every point where the sprites draw it. Its heights:
- the boulders: the sprite's boulders found by a watershed of its shading (from the light peaks down to the dark
  crevices; a basin whose peak stands less than SEG_PROMINENCE shades over the saddle merges into its neighbour, grey
  stones apart, regions under MIN_REGION pixels joined to their neighbour): each a convex cap of large planar facets
  over the simplified hull of its region (5-9 edges): from each edge, tangent planes of a rounded profile at
  TIERS of the way in, each a little turned, steeper or flatter at random (seeded), the lowest plane at a point
  making the cap; its top cut flat under its apex, leaning towards the light; 1.6 + 0.3 sqrt(area) pixels high
  over the mound; the crevices where neighbouring caps meet are V-grooves;
- under them a dark mound rising from the heap's outline over 9-10 pixels to 4.5 (machine heap) or 6.5 (cover),
  only under the rock, so the boulders by the machine lean on it as the sprite heaps them over its side;
- the machine (heights over the ground): its housing 2.2 (rising from its outline over 0.9), the sprite's shading
  laid on as a little relief (EMBOSS), the vent's fins standing 1.5 (the lower ribs 0.6), the ring a rounded band
  rising to 4.7 round the dull red eye (a dome to 4.4), the rod 4.1, the spine 0.9 over the housing with its three
  sockets (rings 1.15 high) round the three dull red lamps (domes).
Painted by the sprite under each face: each boulder one colour, the mean shade of the sprite's pixels of its
commonest ramp under it, LIFT + BOULDER_LIFT lighter, its faces the heightfield's own normals, so the game's light
shades its facets (2026-10-31: a colour and a plane's normal a facet, given cell by cell, drew the facets' borders
as pixel staircases in flat posterised patches); the crevices where the sprite draws its near-black lines (smoothed) dark
0xa2; the machine's faces its own greys MACHINE_LIFT lighter (its sprite is mostly near-black), the ring, rod and
sockets silver, the dull eye and lamps red glass with a faint glow of their own; at most 15 materials a piece (the
rarest merged into their neighbours of the same ramp). Heights: the machine heap 0-13.8 pixels, the cover 0-14.3
(the cover stands higher than the machine wherever it lies over it, so it hides the machine, the eye and the lamps
as the sprites do; background 2 is far above here: IXMUCANE's rock walls are at the screen's sides).

The eye and the lamps (their own models, at their sprites' centres, sheared the same way): the eye a glowing lens
dome over the machine's eye (its rim at 3.4 in the ring, its top 6.2: it bulges out of the ring), the lamps three
lenses in the sockets (to 4.85); painted by their frames' heat, smoothed between the pixels (ramp 7 its shade, the
deep reds darker, golden glints warm): eight shades of ramp 7 glowing 0.21-0.57 the hotter the more, the rim 0x72.
The eye's frames draw the orb 3 rows lower than the machine's eye: the model lays it on the machine's eye, in its
ring (a sprite 3 pixels off its hitbox, as the old model did); models.cfg moves its glow onto it (dx -0.5, dy 2.3).
Frame models (each frame its own heat): ixm_boss_eye (167), _205, _243, _281; ixm_boss_lamps (169), _207, _245, _283.
The eye leaves a wreck of its current frame's model where it dies (tyrian2.c leave_wreck, as any ground enemy).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera. The machine
heap's whole has its origin at its picture's middle (48, 56): column c is x = c + 0.5 - 48, row r is y = 55.5 - r;
the cover's at its own middle (36, 56). A piece whose sprite's top left corner is the picture's (c0, r0) has its
origin at its sprite's centre (models.cfg origin); the eye's origin is the picture's corner (22, 45), the lamps' (22,
73). All on the ground: height=-4 sets them on the terrain (the same for every piece, the eye and the lamps).

models.cfg: the model lines of ixm_boss_*, ixm_cover_* stay; new model lines ixm_boss_eye_205/_243/_281,
ixm_boss_lamps_207/_245/_283 (origin) and their frame lines; the sprite lines of all of them get height=-4, the eye's
glow dx -0.5 dy 2.3.

Replaces wave3_af_heap.py (all of it: delete it) and, with polish_flying_stone.py (which replaces wave3_af.py),
wave3_af_kit.py and wave3_af_art.py (only those two read them: delete them).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each piece's silhouette
against enemy_R.png as the camera sees it, and from straight above), --only <model or group,...> (groups ixm_boss,
lit (the eye and the lamps), ixm_cover), --preview <prefix> (each model's top and 3/4 views).
"""
import heapq
import math
import os
import random
import sys

import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_gyges_wall as gw  # noqa: E402  (the picture-plane heightfield, its grid solids, the camera's shear)
from polish_gyges_wall import Pic, parse, blur, Plate, shear_to_camera, dilate, smoothstep  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402

TAN_T = gw.TAN_T
SUN = np.array(gw.SUN)
STEP = gw.STEP                    # the heightfield's grid (pixels); its lines are the sprites' edges

# Sheet R 159-165 / 197-203 / 235-241 / 273-279: the machine heap, 96 x 112 (rows top to bottom; each pixel its
# palette index in hex, '..' none; trailing transparent pixels left out).
BOSS_ART = """
..
..
..
..
......................................................................................010101010101010101
............................................................................0101010101a0a1a1a2a2a2a1a001
....01....................01010101..............................010101010101a2a3a4151515a4a3a2a2a2a1a0a201
....01010101........01010101a4a4a30101................01010101010115151616171817161616a4a3a3a2a2a1a0a1a4a0
....a00101010101..01a6a6a7a7a5a5a5a5a301..............01a3a4a3a3..a41716171716151515a4a4a3a3a1..01a1a1a5a101
....a1a0a0a2a1010101a6a9a7a6a5a5a5a5a4a10101......010101a4a4a4a4..a41516171615151515a3a1a1....a2a301a0a3a101
....a1a2a2a3a2a1a0a2a3a8a8a6a6a5a6a5a5a3a10101..0101a4a3a4a6a7a6..a4a4151716151515a3a1a415a3a1a1a2a201a0a101
....a2a4a2a5a1a2a1a1a2a4a6a8a7a6a6a6a5a4a0a20101a3a3a4a5a7a7a5a4a1a4a4a41618161515a3a11515a1a3a3a3a3a2a00101
..a1a1a4a6a6a5a4a1a1a2a3a4a5a6a7a8a6a5a3a0a2a4a6a7a7a8a7a5a4010101a2a4a4a416181515a301a2a1a2a3a3a3a3a3a2a00101
0101a0a0a0a2a2a3a2a0a1a3a4a4a4a5a5a5a4a3a0a1a2a5a5a5a5a3a30101a2a2a0a2a3a4a41518a5a2a0a1a2a3a3a3a3a3a3a3a101a201
0101010101a1a2a3a3a2a0a2a3a3a3a3a3a3a3a2a0a1a1a1a2a3a3a30101a3a2a2a2a001a1a3a3a6a4a1a3a3a4a3a3a3a3a3a3a3a2a0a3a301
0101010101a1a2a3a2a2a1a1a3a3a3a3a3a3a3a1a0a0a2a2a0a1a30101a3a3a3a2a2a1a10101a0a0a0a2a3a4a3a3a3a3a3a3a3a3a2a1a3a1a301
0101010101a1a2a2a2a2a0a0a1a2a3a3a3a3a3a1a0a2a2a3a2a1a201a1a3a4a4a3a3a2a2a001a1a1a1a1a1a4a3a3a3a3a3a3a3a3a1a1a3a2a4a401........0101010101
0101010101a0a1a2a2a1a0a0a2a2a2a2a2a2a2a0a0a2a2a3a3a1a101a2a3a4a4a4a4a3a3a0a1a2a2a3a4a2a1a3a3a3a3a3a3a3a1a1a1a1a2a4a5a401010101a1a2a2a1a0a1a0
0101010101a0a1a2a2a1a0a0a1a2a2a2a2a1a1a0a0a1a2a3a3a1a001a2a3a4a4a4a5a4a3a0a1a304040504a0a1a3a3a3a3a2a2a2a3a3a4a3a1a3a3a3a2a3a3a3a4a2a2a2a1a1a0
010101010101a0a1a1a1a0a0a1a0a0a0a2a0a0a0a0a0a1a2a2a1a001a2a3a4a5a5a4a3a3a0a4040505050403a0a2a2a2a2a3a4a4a3a4a5a5a3a1a2a2a2a4a415a2a2a2a2a2a2a001
01010101010101a0010101a0010101a0010101a0a0a0a1a2a1a0a001a2a3a4a4a3a3a3a2a1a4050505060403a3a3a3a3a4a4a5a5a3a4a5a5a5a1a2a4a41515a4a2a2a2a2a2a2a2a001
0101010101020101010201010102010101020101010101a0a0010101a2a3a3a3a3a3a3a2a40505050506040303a3a3a4a5a5a5a5a3a3a4a5a4a31515161615a3a2a2a2a2a2a2a2a2a001
0202020201020101010201010102010101020101010101a0a0010402a2a3a3a3a3a2a203050505050507040303a4a5a5a5a5a5a5a4a2a3a3a4161616171715a3a2a2a2a2a2a2a2a2a101
02020202010201010102010101020101010201020204010101010502a2a3a3a3a3a20405050505050607040404a5a5a5a5a5a4a4a4a3a61717171717171915a3a2a2a2a2a2a2a2a2a2a001010101
01010202010301010103010201030101010301020304040303040502a2a3a3a3a1a20505050505060608040404a5a5a5a4a4a6a6a6a5a61817191818181915a3a2a2a2a2a2a2a2a2a2a101a0a1a0a2a0
02020102010401010104010201040101010401020404040403040502a2a3a3a1a2a50505050506060608040404a5a3a4a5a6a6a6a6a6a51618191919191a15a3a2a2a2a2a2a2a2a2a2a001a1a2a4a4a2a1
02020102010401010204010302040201020401020506060403040503a2a3a2a1a505050506060606060a040404a3a3a4a7a7a6a6a6a6a6151617191a1a1a16a3a2a2a2a2a2a2a2a2a2a0a0a0a2a4a5a3a2a0
04030103020601020306010403060202030601010101010102030503a2a3a1a31505050606060707090a040403a4a4a6a7a9a7a6a6a6a6a615a417191a1c16a3a2a2a2a2a2a2a2a2a201a0a1a3a4a6a4a3a201
05030103010701030307010403070202030602040707060604010503a2a2a21505050606060607090908030303a4a4a6a6a8aaa8a7a6a6a6a6a3a317191c16a3a2a2a2a2a2a2a2a2a101a0a2a3a4a7a3a3a301
06040103010901050409010504090203040802040706060604030402a0a0a405050506060708090805030303a3a4a5a6a7a7a9aaa8a7a6a6a6a5a2a3171815a3a2a2a2a2a2a2a2a2a001a1a3a4a5a8a3a3a301
05040204030d0106050d0106050d0205050d01050a0c0d0c07020102a1a10505050606090808050404a3a3a3a3a4a5a6a7a7a8a9aaa9a7a6a6a6a4a2a31615a2..a0a0a0a0a1a2a1a0a1a2a4a5a5a9a3a3a301
04030203020a0205040a0105040a0305040a02040603040504010102a1a104060707070704040404a3a3a3a2a3a4a5a6a7a7a7a8a9aaa9a6a6a6a5a3a1a2a4..01a2a2a2a1a001a0a1a2a3a3a4a5a5a3a3a201
010102030208030504080204040803050408030406040b0704020204a2a30203040404040404a4a2a4a5a5a5a3a3a5a6a7a7a7a8a8a8aaa8a6a6a6a4a20101a0a2a2a2a2a2a1a1a1a1a3a3a3a3a3a3a3a2a101
03040403010803050408020504080305040803040603090604030607a2a4a4020203040403a2a2a2a5a6a5a6a4a2a3a5a6a7a7a7a8a8a8aaa9a6a6a5a4a101a3a2a2a2a2a2a2a0a1a2a3a3a3a3a3a3a2a20101
040404040208030504080206040803060408030506020a0503040706a2a4a3a202020202a2a3a5a7a8a8a6a6a4a4a2a3a5a6a7a7a8a8a8a8aaa9a6a5a5a4a0a2a3a2a2a2a2a001a2a2a2a3a3a3a3a2a0a101
04040404030a0305040a0206040a0306040a030606020804020607050303030201a3a4a4a4a7a9a9aaa9a8a7a6a3a101a5a6a6a7a7a8a8a8a8a9a9a7a5a5a3a0a2a2a2a2a001a1a1a2a2a2a3a2a0a0a0a001
......0403030205030302060304020503030206060306040406070505040201020304a5a5a5a5a4a4a3a3a3a3a3a101a4a5a6a7a7a8a8a8a8a8a8a8a7a5a4a1a0a1a1a001a0a1a1a1a2a2a1a1a2a2a1a101
..........04040506060607080a02040506050606040601030706020302040405050605a5a4a4a3a3a3a3a3a3a1a0a0a5a5a6a7a7a7a8a8a8a8a8a8a8a6a5a30101010101a0a0a1a1a1a0a1a4a4a3a10101
............040506060708080b0104060606060503010203040203050403050505050503a3a3a3a3a3a3a3a101a1a1a5a5a6a6a7a7a8a8a8a8a8a8a8a7a6a4a4a20101a0a0a001a0a0a1a3a4a4a3a2a101
..............0506070708080b010305a571717272724343030405060401030403030303a0a10101a1a1a2a1a3a2a0a4a5a6a5a5a5a6a7a8a8a8a8a7a6a4a4a4a1a101010101a0a2a2a4a4a4a4a2a1a1a101
..............05070708080c0701a57171747473737474727012040603020202050505010101a1a4a6a6a6a6a6a4a2a1a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a2a0a0a1a1a2a2a4a4a5a5a6a5a4a2a1a1a1a101
................0708080b050243717374747473757876747372707002050606050503030604a4a6a6a6a6a6a6a4a3a1a0a2a2a2a2a2a2a2a2a2a2a2a2a2a101a0a0a3a5a4a4a5a5a5a5a5a5a4a2a1a1a1a10101
..................0a0c0502447274767576757577797775737373720104060606060404070705a6a6a6a6a7a6a2a0a0a0a1a1a1a1a1a1a1a1a1a1a1a1a001a0a1a0a3a5a5a5a5a5a5a5a5a5a5a1a1a1a1a1a10101
..................0201024473747577797a7a7676777675747374757342050606060504070707a6a6a7a8a6a4a1a0a1a1a0a1a1a1a1a1a1a1a0a0a0a0a0a0a1a101a4a6a5a5a5a5a5a5a5a5a5a1a1a1a1a1a1a101
..................0302a571747477787e7f7d7775757677747374767572a40706060402070707a7a9a8a6a4a2a1a1a1a1a1a2a3a2a0a1a2a1a1a1a1a1a1a1a1a101a5a8a6a5a5a5a5a5a5a5a1a1a1a1a1a1a1a101
..................01014371747576797e7f7e7877787a79757374787474430806070201070706a9a8a5a3a3a0a2a2a2a3a3a4a4a4a201a1a2a2a2a2a2a2a2a2a2a0a4a5a8a7a5a5a5a5a5a5a1a1a1a1a1a1a1a101
..................02027071737575777a7b7a7576787a797573747974734208040a0301020907a9a4a3a3a0a1a3a4a4a4a4a5a5a5a5a4a1a1a3a3a3a3a3a3a2a0a0a3a4a5a7a8a6a5a5a5a1a1a1a1a1a1a1a1a1a101
....................047070717375767475767574757676737478797574710a010d030401010501a3a3a2a2a4a4a4a4a4a41515151515a5a2a101a1a1a1a101a0a2a3a4a4a5a7a9a8a5a4a1a1a1a1a1a1a1a1a1a10101
....................04707171717375757575747373747373777a797575420b020c030503010101a3a3a0a415161616151515161515151515a5a2a2a1a10101a2a3a3a4a4a5a5a5aaa5a1a1a1a1a1a1a1a1a1a1a10101
....................067171727171717273737373727374767a7c747475420a030a030605010101a2a0a2a3161616161616161516151615151515a5a5a4a1a0a3a3a3a4a4a5a5a5a5a5a1a1a1a1a1a1a1a1a1a1010101
....................0708707272727271717172727375787b7d77737573430b02080306060301a3a201a3a4161716161716161615161516151615151515a4a1a3a3a3a4a4a5a4a2a2a5a1a1a1a1a1a1a1a1a1a0010101
....................090a7071727272727373747578797a7a7573747472a30b01010206060401a101a1a4a4a4171817161716161616161516151615151515a4a2a3a3a4a4a2a1a1a1a4a1a1a1a1a0a0a0010101010101
..................02060c090471727373737475767676767374757372120a0801010206060201a0a1a4a5a4a4151817171617161716161616161516151515a5a2a3a3a3a2a1a1a1a1a3a1a0a0a0..5050a0010101a00101
..................0103070b09707172737374757575737475757242a20c090701010205050201a1a3a4a4a4a4151619171716171617161716161616161615a4a2a2a2a2a2a1a1a1a1a3a10101020202020101a1a2a1a101
................05030305080c0a07427172757676757473727242070d0b0702030403030301a3a4a6a5a4a4a4151517181817171717171617161616161515a5a101a1a1a1a1a1a1a1a001a002020303020101a2a2a20101
..............0604040203060a0a09070442727272727142a2a20a0c090503010304050101a1a5a6a5a4a4a415151516181817171717171717171818171515a3a001a0a1a1a1a1a1a101010203030303025001a20101
............030504050303030609090706010202020102060a0a0b080303030103040603a1a4a7a5a4a3a4a51515151517191817171717171718181615a4a3a101010101a0a0a1a1a101a002020303020250010101
..........04030504050504030304040605010108060201050707050303030401030405a2a0a3a3a2a3a41515151515151619191717171718191716a4a3a3a3a0a1a1a1a0a1a001a0a00101500202020250a001
..........04030504050506040404030303020201010101030402020303040402030404a2a0a1a1a0a2a4151515151515151619191717191916a4a3a3a3a3a3a1a2a2a2a2a1a101a0a101015001010150a001
..........0303050405050606050405090a0a0906040404040404030304040403020404a3a3a1a1a2a4a41515151515151515171917191815a4a3a3a3a3a3a2a1a2a2a2a2a3a1a0a0a0a001..505050a00101
..........05040504050506060503090c08017001707272727205050405040405020203a3a3a1a2a2a3a41515151515151515171c191816a4a3a3a3a3a3a3a1a1a2a3a3a4a4a3a3a0010101a0....a0a001
..........04030504050506040202060901700101017273737272060603020305040301a1a2a3a3a2a3a41515151515151515161c1916a4a3a3a3a3a3a3a2a1a2a3a4a4a4a4a4a4a3a1a101010101a00101
..........03020403040405010101017273767371727576747374720102010205040401a2a3a4a3a2a3a4a415151515151515151a1715a3a3a3a3a3a3a3a1a1a2a3a4a4a4a4a4a4a4a3a3a101a0a0a001
..........02010302030404010101017376777401017474727476720201010103040401a2a4a5a3a3a2a3a415151515a51515151aa4a3a3a3a3a3a3a3a2a1a1a2a3a4a4a4a4a4a4a4a4a4a3a2a101a00101
..........01010201020303050101017273757101010171727676720202010102030301a3a4a5a5a3a2a3a4a4151515151515151aa4a3a3a3a3a3a3a2a1a1a1a2a3a4a4a4a4a4a4a4a4a4a4a4a3a101a201
..........01010201020303070101010172717001010170757772060501010102030301a3a4a5a5a3a3a2a3a4a415151515151519a4a3a3a3a3a3a2a1a1a0a1a2a3a4a4a4a4a4a4a4a4a4a4a4a4a3a1a301
..........01010101020303040501010103010101017173737206080501010101030301a3a4a5a5a4a3a2a2a3a4a4151515151518a4a3a3a3a3a2a1a3a2a0a1a2a3a4a4a4a4a4a4a4a4a4a4a4a5a4a2a101
..........05050505050606060103010103020603030303030304040101010102030301a3a5a5a5a5a4a3a1a3a3a4a41515151518a4a3a3a2a2a1a4a6a4a2a1a2a3a4a4a4a4a4a4a4a4a4a4a4a5a5a2a2a201
........01010101010101010101030302050907070606060403010101010102030301a1a3a5a5a5a5a4a4a2a1a2a3a4a4a4151517a3a2a2a2a1a0a3a4a3a2a1a0a2a3a4a4a4a4a4a4a4a4a4a4a6a5a2a2a201
......01010101010102020202020303050b08737574727372050402010101030301a3a3a2a3a4a5a5a4a3a2a1a0a0a2a4a4a4a416a2a2a2a1a1a0a2a3a3a2a1a0a1a2a4a4a4a4a4a4a4a4a5a6a5a2a2a2a201
....0304040404040405060601010303020509070706060604030101010101020303a4a4a3a3a3a3a3a3a3a2a2a2a1a0a0a2a3a3a2a0a0a0a0a001a1a2a2a2a101a0a1a2a3a4a5a6a6a6a6a6a5a2a2a2a2a201
01010101010101010101020202020303050b08737573707171050301010105030301a4a4a4a4a3a3a2a2a2a1a3a4a4a3a2a1a1a1a2a0a0a1a1a1a001a0a1a1a0a0a0a1a0a1a2a2a2a2a2a2a2a2a2a2a2a2a201
01010101010101010102030306020303070a73767a757171717201010101050301a4a5a5a4a4a4a4a4a4a2a1a3a4a3a3a2a1a0a0a1a2020202020201a0a0a0a0a0a1a1a1a0a1a2a2a2a2a2a2a2a2a2a2a2a201
030303030303030303040506020203030506727474707001747301010101050201a41515151514a4a4a4a4a4a3a3a3a3a3a0a203030302020202020201a001a2a3a2a1a1a1a1a1a1a2a2a2a2a2a2a2a2a2a201
010101010101010101010202030303030405720101010172757301010101020101a5151515151515a5a4a4a4a4a3a3a2a2a00303030404020202020201a0..a3a3a3a2a1a1a1a2a1a1a1a2a2a2a2a2a2a20101
010101010101010101020303060103030304037001010172010604010101a4a4a5a5151515151515151515a4a4a4a4a4a3a1030303030403020202020101a01414a3a3a3a1a1a2a2a2a1a1a1a2a2a2a20101
010101010101010101020203020203030303040403030304050605010101a4a4a5a615151515151515151515a4a4a4a4a3a103030303040503020202a101a015141414a3a3a2a2a2a2a2a2a2a1a1a10101
010101010101010201010106020704040404057275767372720603010201a3a4a516151515151515151515151514a4a4a4a1a20303030405030202a1a101a01514141414a3a3a3a2a2a2a2a2a2a20101
010101010101010201010105010602030303040373737272040501010201a3a4151615151515151515151516161616a5a4a2a203030404050302a2a1a0a0a0a31614141414a3a3a3a3a2a2a2a2a201
010101010101010201010104030202020304060905040404040401010101a4a4a5a6151515151515161616161617171716a3a202030405040202a0a0a0a0a001151514141414a3a3a3a3a3a2a2a201
010202020201010201010104020101010203080474720171040301010101a3a4a5a615151515161616161616171717171614a3a10203040302a0a0a0a0a0a0a0a216151414141414a3a3a3a3a2a201
010101010101010101010104020501010201017173700101720301010101a3a4a5a616151616161616161717171717161514a4a3a1a0a1a1a0a0a0a0a0a0a0a0a01416151414141414a3a3a3a3a301
01010101010101......0103010401010101010101010101010201010201a3a4a5a617161616161617171717171615141414a4a4a3a101a0a0a0a0a0a0a1a1a0a0a21416141414141414a3a3a3a301
01010101010101......0103010201010101010101020302010101010201a3a4a5a6161717171717171717161514141414a4a4a4a3a201a0a0a0a0a1a1a1a2a2a0a0a2161614141414141414a3a301
01010101010101......0103010302030303030301010101030303030301a201a1a3a4141414141414141414141414a4a4a4a4a2a3a101a0a0a0a1a1a1a2a2a3a2a0a1a21616141414141414a4a401
01010101010101......0103010201010101010101....01010101010101a2a2a0a2a3a3a41414141414a3a3a3a3a3a3a3a3a3a20101010101a0a1a1a2a2a3a3a4a0a0a1a21615141414a3a3a30101
....................0102010101............................01a2a2a2a1a1a1a0a1a0a1a1a1a2a2a2a2a2a2a3a3a2a1a00101010101a1a1a2a3a3a4a5a1a0a0a0a3a3a3a3a3a3a30101
..........................................................01a2a2a2a2a0a1a2a3a2a1a0a1a1a2a2a2a2a3a2a101a1a1a001010101a0a1a3a3a4a4a3a0a1a2a2a1a0a0a0a3a301
..........................................................01a2a2a2a2a1a1a4a4a3a3a101a1a1a2a2a2a0a0a0a1a1a1a001010101a0a2a3a4a4a3a1a0a2a3a4a0a0a0010101
..........................................................01a2a2a2a2a1a1a4a4a4a3a2a101a0a2a2a0a0a1a1a1a1a1a10101010101a2a2a2a1a0a0a2a3a4a1a0a001
..........................................................a101a1a2a2a0a2a4a4a3a3a2a201a0a1a0a0a1a1a1a1a2a2a1010101010101a0a0a0a0a0a1a1a1a0010101
..........................................................0101a1a1a001a4a4a4a3a2a2a2a0a0a001a0a1a1a1a1a2a2a3a20101010101a0a0a0a0a0a0a0a0a001
..........................................................0101a0a001a2a4a4a4a3a2a2a2a2a00101a0a1a1a1a1a2a2a2a3a10101010101a0a0a0a0a0a00101
............................................................01a2a201a3a4a4a4a2a2a2a2a2a00101a0a1a1a1a2a2a2a2a2a4a101010101010101a0a00101
............................................................01a4a301a4a4a4a4a2a2a2a2a2a00101a0a1a1a1a2a2a2a3a3a4a6a101a0010101010101
............................................................01a3a201a4a4a4a4a2a2a2a2a2a10101a0a1a1a2a2a2a3a3a3a4a5a6a201a001010101
............................................................01a0a101a4a4a4a3a2a2a2a2a2a10101a0a1a1a2a2a3a3a3a4a4a4a5a6a1a1a00101
..............................................................010101a4a4a4a3a2a2a2a2a2a1a001a1a1a2a2a3a3a3a4a4a4a4a4a5a3a20101
................................................................0101a4a4a3a3a2a2a2a2a2010101a1a1a2a3a3a3a4a4a4a4a4a4a4a4a301
..................................................................01a4a4a3a3a2a2a2a2a201..0101a1a2a3a3a4a4a4a4a4a4a4a3a3a201
..................................................................01a4a4a3a2a2a2a2a20101....0101a1a1a4a4a4a4a3a2a2a2a2a2a101
..................................................................01a4a4a2a2a2a2a20101........0101a1a1a2a2a2a2a1a1a1a1a1a101
..................................................................01a4a2a2a201010101............0101a1a1a1a1a1a1a1a1a1a1a101
....................................................................01010101......................01a1a1a1a1a1a1a1a1a1a10101
..................................................................................................0101a1a1a101010101010101
....................................................................................................0101010101
..
..
..
..
..
..
"""

# Sheet R 153-157 / 191-195 / 229-233 / 267-271: the cover, 72 x 112.
COVER_ART = """
................................................................................0101a1a2a2a2a3a3a20101
................................................................................01a2a3a4a4a5a5a5a5a5a201
................................................................................01a3a4a4a5a5a5a5a5a5a5a201
................................................................................01a4a4a5a5a5a5a6a6a6a6a6a201
..............................................................................0101a5a5a5a5a5a6a6a6a6a6a6a6a101
............................................................................0101a3a6a5a5a5a6a6a6a6a6a6a6a7a3a20101
..................................................010101010101010101010101010101a4a7a5a5a6a6a6a6a6a6a6a6a7a3a5a301
................................................01a0a0a2a3a3a3a3a3a3a3a301010101a5a7a5a5a6a6a6a6a6a6a7a7a8a4a5a401
................................................01a1a2a4a4a4141414a4a40101a001a0a5a7a5a5a6a6a6a6a6a7a7a7a8a5a5a401
................................................01a0a4171414141414..01a4a2a2a0a0a5a8a5a6a6a6a6a6a7a7a7a7a8a5a5a401
................................................01a01416141414a3....a4a4a4a3a0a1a4a8a7a6a6a6a6a7a7a7a7a7a8a5a5a1a0
..............................................01a2a215161414....1514a5a5a4a4a2a1a2a8a7a6a6a6a7a7a7a7a7a7a8a5a20101
..............................................01a1a3151714....161616a6a4a4a4a3a1a2a7a8a6a6a7a7a7a7a7a7a7a8a40101
..............................................01a1a31416....a31516a6a5a5a4a4a4a2a2a6a9a6a7a7a7a7a7a7a7a8a6a0
............................................0101a2a314..a2a2a3a5a6a6a7a7a7a6a5a2a2a6a9a7a7a7a7a7a7a7a7a7a0
..................................010101010101a4a401..a0a2a2a3a5a6a6a6a7a8a7a6a4a3a4a9a7a7a7a7a7a7a7a8a2
................................01a0a2a2a10101010101a1a0a1a3a3a5a6a6a6a6a7a8a6a6a5a3a9a8a7a7a7a7a7a8a701
..............................01a0a2a2a3a3a3a3a4a4a4a3a1a2a3a4a6a6a6a6a6a7a7a8a6a6a3a7a9a8a7a7a7a8a8a401
..........................0101a0a2a3a4a4a4a4a4a4a4a5a5a3a1a3a5a6a6a6a6a6a7a7a8a8a6a4a5a9a8a8a8a8a8a9a401
......................0101a0a1a3a3a4a4a4a4a4a4a5a4a4a5a5a5a2a3a5a6a6a6a6a7a7a7a8a7a5a4a9a9a8a8a8a9a9a301
..................0101a0a2a2a2a3a4a4a4a4a4a4a5a5a3a4a4a6a6a5a2a3a5a6a6a7a7a7a7a8a6a5a4a6a9a9a9a9aaa8a301
..................01a1a2a2a2a2a2a3a4a4a4a4a5a5a5a3a4a4a5a6a6a6a2a1a5a7a7a7a7a8a8a6a4a4a4a9a9a9aaaba7a401
................01a0a1a2a2a3a3a3a2a3a4a4a5a5a5a5a3a4a4a4a5a6a6a6a3a2a5a7a8a8a8a6a5a4a4a2a8a9a9aaaba7a4a1
................01a0a1a2a3a3a4a4a3a2a3a4a4a5a5a5a3a4a4a4a4a5a6a6a6a3a0a3a5a5a5a5a5a4a4a2a6a9a9aaaba5a4a2
................01a0a1a2a2a4a5a5a4a3a3a3a4a3a3a3a3a4a4a4a4a4a6a7a8a5a0a1a3a4a5a4a4a4a3a0a4aaaaaaaba5a4a2
................01a0a1a2a1a4a5a5a5a5a4a3a3a4a4a4a4a4a4a4a4a5a6a7a8a6a3a001a1a1a1a1a2a2a1a3a9aaaaaba5a4a2
..................01a1a2a1a4a5a6a6a6a5a5a4a3a4a4a4a4a4a4a4a5a7a8a9a6a3a2a1a2a2a3a2a3a3a2a2a7abababa5a4a2
..................01a1a2a0a4a5a6a6a6a6a6a5a5a4a4a4a4a4a4a5a6a8a8a9a5a2a2a4a5a4a1a416a7a4a3a5a9ababa5a4a2
....................010101a4a4a5a6a6a7a7a7a7a7a6a5a5a7a8a8a8a8a9aaa4a3a3a3a4a2a216191716a4a4a7abaaa5a4a2
....................010101a3a3a4a5a6a6a7a7a8a8a8a8a8a8a8a8a8a9aaaaa3a3a3a3a3a2a4177b171716a4a5a8a7a5a5a3
................0101a1a1a101a2a3a4a5a5a6a6a7a8a8a9a9a8a8a8a8aaaba9a3a3a3a3a3a2a4161c19181717a5a5a5a5a5a3
............0101a3a4a4a3a10101a2a3a4a4a5a6a7a7a7a8aaaaa9a9aaaaaba7a3a3a3a3a3a21516161a1a181717a6a4a3a101
..........01a2a4a4a4141414a2a201a2a4a4a4a4a5a5a6a7a7a9abababababa5a3a3a3a3a2a21616161617191918a7a7a6a3a1
........01a4a414141414141414a301a0a3a4a5a4a4a4a5a6a7a7a8aaacadaaa3a3a3a3a3a2a2a41616161616171919a6a6a5a2
......01a315151515141414141414a201a3a3a5a5a5a5a4a4a4a6a7a7a9acaaa3a3a3a3a3a1a3a4151616161616161717a5a4a1
....01141515151515151514141414a30101a3a5a5a5a5a5a5a4a4a6a7a7a9a7a3a3a3a3a1a1a2a3151516161616161615a4a201
..01a3151515151515151514141414a3a101a3a4a5a5a5a5a5a5a4a3a4a5a7a6a3a3a2a1a2a3a3a2a415151616161616a4a4a5a3a2a3a2a3a101
01a3a4151515151515151514141414a3a301a2a4a5a5a5a5a5a5a5a4a3a2a2a2a1a1a1a3a3a3a3a2a2a4151516151515a4a5a6a6a5a5a5a5a4a10101
01a1a2a3141515151515141414a3a3a3a301a2a3a4a4a5a5a5a5a5a3a2a5a6a4a3a4a4a4a3a3a3a3a2a1a3a4a4151515a3a5a6a8a7a7a7a6a6a5a5a001
..01a1a2a2a2a2a2a2a2a2a0010101010101a2a2a3a4a4a4a5a5a4a2a3a608060505040404040404a4a3a2a1a1a4a4a4a3a5a6a9a8a7a7a6a6a6a6a6a101
....01a1a1a2a2a2a2a2a0a1a4a5a5a5a5a6a6a2a2a3a3a4a4a4a4a3a4060807060505040404040405a6a4a2a0a1a2a3a0a5a6a8a9a7a7a7a7a6a6a6a5a0
......01a0a1a2a2a201a2a5a5a5a5a5a5a5a5a6a5a3a3a3a3a3a3a3a4060908070605050404040506a5a3a3a2a1a1a201a5a5a7aaa8a8a7a7a7a6a6a6a301
........01a0a0a101a2a5a5a5a5a5a5a5a5a5a6a6a6a5a3a3a3a3a3a3060908070706050505050606a4a3a3a2a3a4a201a3a5a7a9aaa8a8a7a7a7a6a6a5a001
..........010101a4a5a5a5a5a5a5a5a5a5a5a6a6a6a6a6a5a3a3a3a40509090807070606060607a3a3a3a3a2a4a5a3a2a1a5a5a8aaa8a8a8a8a7a7a7a6a301
..........0101a5a5a5a5a5a5a5a5a5a5a6a6a6a6a6a6a6a6a6a5a5a404080a0808070707070806a4a3a3a3a1a4a5a5a4a1a4a5a6aaa9a8a8a8a8a7a7a7a601
........0101a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a503060a0908080808090504a4a4a3a3a1a4a6a6a6a1a2a5a6a9aaa8a8a8a8a8a8a7a6a1
........01a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a7a7a7a6a6a504070a090909090706a5a4a3a3a3a3a4a6a8a9a3a1a3a6a8aaa9a8a8a8a8a8a8a7a5
........01a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a6a7a7a7a7a7a8a7a6a504090a0a09060505a5a4a3a2a3a3a3a3a4a4a4a2a0a5a6aaa9a8a9a9a9a9a9a9a8a0
........01a4a5a6a7a7a7a7a7a7a7a7a7a7a7a7a7a7a7a7a7a7a8a9a7a6a6a504070807050505a5a4a1a1a3a2a1a3a4a4a4a4a2a2a6a9aaaaaaaaaaaaabaaa501
........01a4a4a4a4a5a6a6a7a7a7a7a7a7a7a7a7a7a7a7a8a8aba9a7a6a6a6a2030605050505a4a101a2a3a4a2a1a2a3a4a4a3a3a4a7aaaaaaaaabaaa7a4a3a1
........0101a4a4a4a4a4a5a6a6a7a7a7a7a7a7a7a8a8a8a9aaa9a6a6a5a5a5a3a1a3040404a3a101a1a4a4a4a4a2a1a2a3a3a3a3a4a4a9abaaa8a7a5a4a3a3a1
..........01a4a4a4a4a4a4a4a4a5a6a7a7a7a8a8a8a9a9a9a7a6a6a5a5a5a5a4a3a2a2a2a2a2a101a3a4a4a4a4a4a2a2a1a0a2a4a5a2a4a7a7a4a4a3a3a3a301
..........01a2a3a4a4a4a4a4a4a4a4a5a6a6a6a6a6a6a6a6a6a5a5a5a5a5a4a3a2a3a3a3a3a101a2a4a4a4a4a4a4a5a5a4a5a3a4a4a4a3a3a4a4a3a3a3a301
..........0101a2a2a4a4a4a4a4a4a4a4a4a4a4a5a5a5a5a5a5a5a5a5a5a4a3a214151615a3a1a3a4a4a4a4a4a5a5a5a5a6a6a6a5a5a5a5a2a2a2a3a3a3a301
............0101a2a2a4a4a4a4a4a4a4a4a4a4a4a4a4a4a5a5a5a5a5a4a3a2a315161714a2a3a4a4a4a4a5a6a6a6a6a6a6a6a6a6a6a5a5a5a1a2a3a3a301
............01a1a0a1a2a3a3a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a4a3a3a2a316171514a3a5a5a6a5a5a6a6a6a6a6a6a6a6a6a6a6a6a5a6a3a2a2a301
............01a0a0a0a0a1a1a3a3a4a4a4a4a4a4a4a4a4a4a4a4a4a3a3a3a2a3a31414a3a4a5a6a5a6a6a6a6a6a6a6a6a6a6a6a6a6a7a5a5a5a2a201
..........01030350a2a1a001a0a1a2a3a3a4a4a4a3a3a3a3a2a2a3a3a3a3a3a2a3a3a3a3a4a6a5a6a6a7a6a6a6a6a6a6a6a7a6a7a7a7a5a5a5a401
............04020202a2a2a2a0a1a0a2a3a2a2a3a3a3a3a3a2a5a4a4a4a4a4a4a3a2a2a3a6a5a7a6a7a6a7a6a7a6a7a6a7a6a7a7a7a8a5a5a4a401
............0603020203a3a3a3a3a3a3a2a2a314a4a3a3a3a2a5a5a5a5a5a5a5a5a5a3a5a6a7a7a7a7a7a6a7a6a7a6a7a6a7a6a7a7a8a5a5a4a401
............0606050404040403a3a3a21414141414a4a3a3a2a6a5a5a5a5a5a5a5a5a4a5a7a7a7a7a7a7a7a6a7a6a7a6a7a6a7a7a7a8a5a5a4a401
............040706050505040404a4a21515151514a4a4a3a2a6a6a6a6a6a6a6a6a6a5a7a8a8a7a8a7a7a7a7a7a7a7a7a7a7a7a7a7a8a5a5a4a401
............030407060505050404a3a1141616161514a4a3a2a6a6a6a6a6a6a6a6a6a5a5a8a8a8a7a8a7a8a7a7a7a7a7a7a7a7a7a7a8a3a3a4a401
..............0404070706050302a2a2a21616161515a4a4a3a6a7a7a6a6a6a6a6a6a6a5a7a8a8a8a7a8a7a8a7a8a7a8a7a8a7a7a7a8a3a3a4a401
..............01030304040250a1a1a1a21516161615a4a4a3a5a7a7a7a6a6a6a6a6a6a5a5a7a8a8a8a8a8a7a8a7a8a7a8a7a8a7a8a7a3a3a3a401
................010101010101a0a0a0a0a31616161615a4a3a3a8a7a7a7a6a6a6a6a6a6a5a5a7a8a8a8a8a8a8a8a8a8a8a8a8a8a7a3a2a2a3a301
................a0a0a0a2a2a2a2a1a0a0a2161616161615a4a3a6a8a7a7a7a6a6a6a6a6a6a5a3a7a8a8a8a8a8a8a8a8a8a8a8a6a3a2a2a2a2a301
............0101a2a2a3a3a3a3a2a2a001a1161616161616a4a2a1a7a8a7a7a7a7a6a6a6a6a6a3a3a7a7a8a9a9a9a9a9a9a7a5a2a2a2a2a2a2a201
..........01a3a3a3a3a3a3a3a3a3a2a1a0a1a31616161614a2a2a0a4a7a8a7a7a7a7a6a6a6a6a4a2a3a4a5a5a5a5a5a5a5a4a2a2a2a2a2a1a101
......0101a6a3a3a3a3a3a3a3a3a3a4a3a0a2a215161614a2a2a2a1a3a5a6a8a8a7a7a7a7a6a5a4a2a0a3a4a4a4a4a4a4a4a4a3a2a2a2a001a0
....01a2a3a8a5a4a4a3a3a4a4a4a4a4a2a0a001a1a2a2a2a2a2a2a1a2a3a4a4a4a4a4a4a4a4a4a4a3a2a1a3a3a4a4a4a4a4a4a3a2a2a001a1
....01a2a4a7a6a5a5a4a4a4a3a2a2a2a1010101a0a2a2a2a2a2a2a1a1a2a3a4a4a4a4a4a4a4a4a4a3a4a3a2a2a3a3a3a3a3a3a2a10101
....01a3a4a5a6a5a3a2a2a2a2a2a1a0a0a001a00101a1a2a2a2a1a1a1a0a2a3a4a4a4a4a4a4a4a3a4a5a5a3a2a4a5a5a5a5a5a4a3a0
......01a0a1a1a1a1a1a1a1a1a1a1a0a0a001a0a0a0a1a1a1a0500102025001a3a4a4a4a4a3a3a4a5a5a5a6a3a4a4a5a5a5a5a5a3a0
......01a0a0a1a1a1a1a1a1a1a1a1a0a0a001a0a0a102020303030303030250a1a0a1a2a1a4a5a5a5a5a5a6a3a4a4a4a4a4a4a4a4a0
........01a0a1a1a1a1a1a1a1a1a1a0a0a001a0020303030303030304040202a101a0a001a2a4a5a5a5a6a5a3a2a4a4a4a4a4a4a4a0
........01a0a0a1a1a1a1a1a1a1a1a0a001a002030404040404040404050302a101a1a2a1a1a2a3a4a5a4a4a4a1a3a4a4a4a4a4a4a0
..........01a0a0a1a1a1a1a1a0a0a0a001a203040404040404040405050303a201a2a2a2a2a1a1a2a3a4a4a4a3a0a3a4a4a4a4a401
............01a0a1a1a1a0a0a0a0a001a103040404040404040405060403a3a1a1a3a4a4a3a2a2a1a2a3a3a3a3a2a0a3a4a4a4a301
............01a0a0a0a0a0a0a0a0a0a00304040505050505050506050303a3a1a3a5a5a4a3a3a3a2a2a1a3a3a2a2a101a3a3a3a201
..............01a0a0a0a0a0a0a001020404050505050505050605040303a1a2a4a6a5a4a3a3a3a2a2a0a0a2a2a2a201a0a2a2a101
................01010101010101010204040505050505050605030303a1a2a3a5a6a5a4a3a3a2a2a2a201a1a2a2a0a1a0a0a00101
..................010101010101010104040505050506060503030302a3a3a4a5a6a5a3a3a2a2a2a2a2a2a0a0a1a0a2a2a1a00101
............................01a1a1030404050506060403030302a3a4a4a5a6a6a3a3a3a2a2a2a2a2a2a2a001a1a2a3a3a3a001
............................01a2a20104040405040303a3a3a2a3a3a4a4a5a7a5a3a3a3a2a2a2a2a2a2a2a1a0a2a3a314a4a301
............................01a4a30201020202a2a2a2a2a2a3a4a4a4a4a5a8a5a3a3a3a2a2a2a2a2a2a1a1a2a314151514a4a0
............................01a5a7a3015001a1a1a1a1a2a3a3a4a4a4a5a5a8a5a3a3a3a2a2a2a2a2a2a1a1a21415151514a4a0
............................01a3a6a4a3a2a2a1a1a0a1a3a3a3a4a4a5a5a7a9a5a3a3a2a2a2a2a2a2a1a1a1a21615151414a4a0
............................0101a2a2a2a2a1a1a1a0a1a3a3a3a4a5a7a7a9a8a5a3a3a2a2a2a2a2a2a1a1a1a217151414a4a4a0
..............................0101a2a2a1a1a001a0a2a3a4a5a6a6a6a5a5a4a3a3a2a2a2a2a2a2a2a1a1a1a217151414a4a401
................................01010101010101a2a4a5a5a5a4a3a4a4a3a3a1a1a1a2a2a2a2a2a2a0a1a1a217141414a4a301
............................................01a2a3a2a2a2a2a3a3a3a3a3a0a0a1a1a2a2a2a2a0a0a1a1a218141414a4a1a1
............................................01a1a2a2a2a2a2a3a3a3a3a3a0a0a1a1a1a1a2a2a0a0a1a1a2171514a4a3a101
............................................01a1a2a2a2a2a2a3a3a3a3a3a0a0a1a1a1a1a1a2a0a0a1a1a2151614a4a301
............................................01a1a2a2a2a2a2a3a3a3a3a3a0a0a1a1a1a1a1a10101a1a1a2a31615a4a201
............................................01a1a2a2a2a2a2a3a3a3a3a3a0a0a1a1a1a1a1a101a0a0a1a2a215a6a401
..............................................01a1a2a2a2a2a3a3a3a3a3a0a0a1a1a1a1a1010101..a0a2a2a3a5a201
................................................01a1a2a2a2a3a3a3a3a3a0a0a1a1a1a10101....01a0a1a2a2a2a301
................................................01a1a2a2a2a3a3a3a3a3a0a0a1a1a101..........0101a2a2a201
..................................................0101a1a2a3a3a3a3a3a0a0a1a101..............0101a2a201
......................................................0101a2a3a3a3a301a00101..................010101
..........................................................0101a1a2a201a001
..............................................................a001a101a0
................................................................010101
..
..
..
..
..
..
..
..
"""

# R 167: the eye, lit (24 x 28).
EYE_167 = """
..
..
..
..
..
..
..
..
..
..
0708080b0104060606060503010203040203050403050505
0708080b0103051749797a7a191643030405060401030403
08080c0701a5797a7c7c7b7b7c7b7a481615060302020205
080b050215797b7c7c7c7b7d7f7e7c7b7a79480205060605
0c0502167a7c7e7d7e7d7d7f7f7f7d7b7b7b7a1504060606
0102447a7c7d7f7f7f7f7e7e7f7e7d7c7b7c7d1a16050606
02a5497b7c7f7f7f7f7f7f7d7d7e7f7c7b7c7e7d1aa40706
0145797c7d7e7f7f7f7f7f7f7f7f7f7d7b7c7f7c7a160806
0247797b7d7d7f7f7f7f7d7e7f7f7f7d7b7c7f7c7a170804
047878797b7d7e7c7d7e7d7c7d7e7e7b7c7f7f7d7b190a01
04787979797b7d7d7d7d7c7b7b7c7b7b7f7f7f7d7b180b02
0649797a7979797a7b7b7b7b7a7b7c7e7f7f7c7c7b170a03
0719797a7a7a7a7979797a7a7b7d7f7f7f7f7b7d7a170b02
090a49797a7a7a7a7b7b7c7d7f7f7f7f7d7b7c7b1aa70b01
060c0918797a7b7b7b7c7d7e7e7e7e7b7c7d7b1a180a0801
03070ba949797a7b7b7c7d7d7d7b7c7d7d7a17180c090701
0305080c0aa817797a7d7e7e7d7c7b7a1917070d0b070203
0203060a0a0906a616197a7a7a491616170a0c0905030103
"""

# R 205: the eye, lit (24 x 28).
EYE_205 = """
..
..
..
..
..
..
..
..
..
..
0708080b0104060606060503010203040203050403050505
0708080b0103054648787878474644a40405060401030403
08080c07014547777a7a79797a79784745a5060302020205
080b05024548797a7a7a797b7e7c7a79784746a305060605
0c050245487a7c7b7c7b7b7d7f7d7b797979784404060606
010244497a7b7d7f7f7f7c7c7d7c7b7a797a7b4915050606
02a547797a7d7e7f7f7f7d7b7b7c7d7a797a7c7b48a40706
0143777a7b7c7f7f7f7f7e7d7e7f7f7b797a7e7a79150806
027677797b7b7d7f7f7f7b7c7e7f7f7b797a7f7a79460804
04757677797b7c7a7b7c7b7a7b7c7c797a7e7f7b7a480a01
0475777777797b7b7b7b7a79797a79797d7f7f7b7b170b02
06477778777777787979797978797a7c7f7f7a7a7b160a03
074876787878787777777878797b7e7f7f7d797b79170b02
09a948777878787879797a7b7e7f7f7f7b797a7a48170b01
060ca84777787979797a7b7c7c7c7c797a7b7948170a0801
03070ba948777879797a7b7b7b797a7b7b7846a70c090701
0305080c0aa74677787b7c7c7b7a79784847a80d0b070203
0203060a0a0906a54548494948474615a60a0c0905030103
"""

# R 243: the eye, lit (24 x 28).
EYE_243 = """
..
..
..
..
..
..
..
..
..
..
0708080b0104060606060503010203040203050403050505
0708080b010305a575757675754543030405060401030403
08080c0701a57575787877777878757444a4060302020205
080b050244757778787877797c7a78767574450205060605
0c05024575787a797a79797b7d7b79777777754304060606
0102457678797b7d7e7e7a7a7b7a79787778794745a50606
02447578787b7c7f7f7f7b79797a7b7877787a7976a40706
01447578797a7d7f7f7f7c7b7c7e7d7977787c7878430806
0273757779797b7e7f7e797a7c7e7d7977787d7877450804
0473747577797a78797a7978797a7a77787c7d7978470a01
047475757577797979797877777877777b7e7d7979460b02
0646757675757576777777777677787a7e7f787879460a03
07a77576767676757575767677797c7f7f7b777977460b02
090a477576767676777778797c7d7e7e7977787875a60b01
060ca846757677777778797a7a7a7a7778797775460a0801
03070ba8477576777778797979777879797645a60c090701
0305080ca9a7457576797a7a797877764646070d0b070203
0203060a0a0906a54446477575744545a60a0c0905030103
"""

# R 281: the eye, lit (24 x 28).
EYE_281 = """
..
..
..
..
..
..
..
..
..
..
0708080b0104060606060503010203040203050403050505
0708080b010305a573737474744343030405060401030403
08080c0701a5737376767575767574721204060302020205
080b050243737576767675777a7876757373720205060605
0c05024474767877787777797b7977757575734304060606
010244757677797b7c7c7878797877767576777444050606
02a5737676797a7f7f7f7977777879767576787774a50706
0143737677787b7f7f7f7a797a7c7b7775767a7676450806
027273757777797c7d7c77787a7c7b7775767b7675450804
04727273757778767778777677787875767a7b7776450a01
04437373737577777777767575767575797c7b7777450b02
064573747373737475757575747576787c7e767677450a03
07084474747474737373747475777a7d7f79757775450b02
090a467374747474757576777a7b7c7c7775767674a60b01
060c09a573747575757677787878787576777574a60a0801
03070b09464574757576777777757677777444a60c090701
0305080c0aa7447374777878777675747445070d0b070203
0203060a0a0907a443737474737344a2a20a0c0905030103
"""

# R 169: the lamps, lit (24 x 28).
LAMPS_169 = """
050606050405090a0a090604040404040403030404040302
05060605050a0c0874757474747474740505040504050502
05060605080c0a74787b7875757575747406070504040604
04050504080a74787f7f7f7a787876757674070701040504
04040402050775787e7f7d79787674767874090701010304
030303020404747577777674737374787874090701010203
030303020204047474747271727377797408090501010203
030303020101020372727272737373720608070101010103
060606010201010302060303030303030404010101010203
..
..
010101010303020509070706060604030101010101020303
020202020303050b087a7c7b797a49050402010101030301
060606020303070a1b7d7f7f7d7b7a4906040101010301a4
0202020203030506797c7f7f7d797b7a06040101010201a4
030303030303040549797b7b797b7d1a06040101010101a5
050606010303030415484949797a1a1806040101a4a4a5a5
0202020203030303040403030304050605010101a4a4a5a6
..
..
0303030303030304060905040404040401010101a4a4a5a6
0203030303030304090576767474050402010101a3a4a5a6
0106020704040404057477787574740603010201a3a4a5a6
0105010602030303040375757474040501010201a3a4a5a6
0104010502030303030303030303020101010201a3a4a5a6
0104010402030303020101010101010101010201a3a4a5a6
0104010402030303030201010101010101020301a1a4a5a6
010301040203030303030101030102020203030101a3a5a6
"""

# R 207: the lamps, lit (24 x 28).
LAMPS_207 = """
050606050405090a0a090604040404040403030404040302
05060605050a0c0876777676767676760505040504050502
05060605080c0a767a7d7a77777777767606070504040604
04050504080a767a7f7f7f7c7a7a78777876070701040504
040404020507777a7f7f7f7b7a7876787a76090701010304
0303030204047677797978767575767a7a76090701010203
0303030202040476767674737475797b7608090501010203
030303020101020376767676777777760608070101010103
060606010201010302060303030303030404010101010203
..
..
010101010303020509070706060604030101010101020303
020202020303050b08797b7a787978050402010101030301
060606020303070a797c7f7f7c7a787806040101010301a4
0202020203030506787b7f7f7c787a7906040101010201a4
030303030303040578787a7a787a7c7906040101010101a5
050606010303030403787777797b780606040101a4a4a5a5
0202020203030303040403030304050605010101a4a4a5a6
..
..
0303030303030304060905040404040401010101a4a4a5a6
0203030303030304090578787676050402010101a3a4a5a6
01060207040404040576797a7776760603010201a3a4a5a6
0105010602030303040377777676040501010201a3a4a5a6
0104010502030303030303030303020101010201a3a4a5a6
0104010402030303020101010101010101010201a3a4a5a6
0104010402030303030201010101010101020301a1a4a5a6
010301040203030303030101030102020203030101a3a5a6
"""

# R 245: the lamps, lit (24 x 28).
LAMPS_245 = """
050606050405090a0a090604040404040403030404040302
05060605050a0c08797a7979797979790505040504050502
05060605080c0a797d7f7d7a7a7a7a797906070504040604
04050504080a797d7f7f7f7f7d7d7b7a7b79070701040504
0404040205077a7d7f7f7f7e7d7b797b7d79090701010304
030303020404797a7c7c7b797878797d7d79090701010203
03030302020404797979774777787c7e7908090501010203
0303030201010203797979797a7a7a790608070101010103
060606010201010302060303030303030404010101010203
..
..
010101010303020509070706060604030101010101020303
020202020303050b08777978767776050402010101030301
060606020303070a777a7f7d7a78767606040101010301a4
020202020303050676797d7d7a76787706040101010201a4
03030303030304057676787876787a7706040101010101a5
0506060103030304037675757779760606040101a4a4a5a5
0202020203030303040403030304050605010101a4a4a5a6
..
..
0303030303030304060905040404040401010101a4a4a5a6
0203030303030304090579797777050402010101a3a4a5a6
010602070404040405777a7b7877770603010201a3a4a5a6
0105010602030303040378787777040501010201a3a4a5a6
0104010502030303030303030303020101010201a3a4a5a6
0104010402030303020101010101010101010201a3a4a5a6
0104010402030303030201010101010101020301a1a4a5a6
010301040203030303030101030102020203030101a3a5a6
"""

# R 283: the lamps, lit (24 x 28).
LAMPS_283 = """
050606050405090a0a090604040404040403030404040302
05060605050a0c087b7c7b7b7b7b7b7b0505040504050502
05060605080c0a7b7f7f7f7c7c7c7c7b7b06070504040604
04050504080a7b7f7f7f7f7f7f7f7d7c7d7b070701040504
0404040205077c7f7f7f7f7f7f7d7b7d7f7b090701010304
0303030204047b7c7e7e7d7b7a7a7b7f7f7b090701010203
030303020204047b7b7b797a797a7e7f7b08090501010203
03030302010102037a7a7a7a7b7b7b7a0608070101010103
060606010201010302060303030303030404010101010203
..
..
010101010303020509070706060604030101010101020303
020202020303050b08757776747574050402010101030301
060606020303070a75787e7b7876747406040101010301a4
020202020303050674777b7b7874767506040101010201a4
0303030303030405747476767476787506040101010101a5
0506060103030304037473737577740606040101a4a4a5a5
0202020203030303040403030304050605010101a4a4a5a6
..
..
0303030303030304060905040404040401010101a4a4a5a6
020303030303030409057c7c7a7a050402010101a3a4a5a6
0106020704040404057a7d7e7b7a7a0603010201a3a4a5a6
010501060203030304037b7b7a7a040501010201a3a4a5a6
0104010502030303030303030303020101010201a3a4a5a6
0104010402030303020101010101010101010201a3a4a5a6
0104010402030303030201010101010101020301a1a4a5a6
010301040203030303030101030102020203030101a3a5a6
"""


# --- Pictures -----------------------------------------------------------------------------------------------------

def picture(text, width, left, top):
    rows = parse(text)
    return Pic([row + [None] * (width - len(row)) for row in rows], left, top)


BOSS_W, BOSS_H = 96, 112
COVER_W, COVER_H = 72, 112
# The machine heap's whole has its origin at its picture's middle (48, 56), the cover's at its own (36, 56).
BOSS_LEFT, BOSS_TOP = -48.0, 56.0
COVER_LEFT, COVER_TOP = -36.0, 56.0
# The pieces: their sprites row by row (columns 0, 24, 48 (, 72); rows 0, 28, 56, 84 of the pictures).
BOSS_SPRITES = [[159, 161, 163, 165], [197, 199, 201, 203], [235, 237, 239, 241], [273, 275, 277, 279]]
COVER_SPRITES = [[153, 155, 157], [191, 193, 195], [229, 231, 233], [267, 269, 271]]
# The eye's and the lamps' sprites: their top left pixels in the machine heap's picture (the events' offsets).
EYE_AT, LAMPS_AT = (10, 31), (10, 59)
EYE_FRAMES = (167, 205, 243, 281)
LAMP_FRAMES = (169, 207, 245, 283)
EYE_SHIFT = 3                     # the eye's sprite draws the orb 3 rows lower than the machine's eye


def piece_boxes(sprites, left, top):
    """(sprite, box (x0, x1, y0, y1), centre) of each piece."""
    out = []
    for j, row in enumerate(sprites):
        for i, sprite in enumerate(row):
            x0, y1 = left + 24 * i, top - 28 * j
            out.append((sprite, (x0, x0 + 24.0, y1 - 28.0, y1), (x0 + 12.0, y1 - 14.0)))
    return out


def inside_poly(poly, X, Y):
    """Even-odd inside test of points against a polygon."""
    res = np.zeros(np.shape(X), bool)
    n = len(poly)
    for i in range(n):
        (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % n]
        cond = (y0 > Y) != (y1 > Y)
        with np.errstate(divide="ignore", invalid="ignore"):
            xc = x0 + (Y - y0) * (x1 - x0) / np.where(y1 - y0 == 0, 1e-12, y1 - y0)
        res ^= cond & (X < xc)
    return res


def chamfer(mask, step):
    """For each cell of a mask, its distance (in pixels, cells step apart) to the nearest cell outside it (two-pass
    3-4 chamfer, deterministic); 0 outside."""
    h, w = mask.shape
    big = 1e6
    d = np.where(mask, big, 0.0)
    a, b = step, step * math.sqrt(2)
    for r in range(h):
        row = d[r]
        prev = d[r - 1] if r > 0 else None
        for c in range(w):
            if row[c] == 0:
                continue
            best = row[c]
            if c > 0:
                best = min(best, row[c - 1] + a)
            else:
                best = min(best, a)
            if prev is not None:
                best = min(best, prev[c] + a)
                best = min(best, (prev[c - 1] if c > 0 else 0.0) + b)
                best = min(best, (prev[c + 1] if c < w - 1 else 0.0) + b)
            else:
                best = min(best, a)
            row[c] = best
    for r in range(h - 1, -1, -1):
        row = d[r]
        nxt = d[r + 1] if r < h - 1 else None
        for c in range(w - 1, -1, -1):
            if row[c] == 0:
                continue
            best = row[c]
            best = min(best, (row[c + 1] if c < w - 1 else 0.0) + a)
            if nxt is not None:
                best = min(best, nxt[c] + a)
                best = min(best, (nxt[c + 1] if c < w - 1 else 0.0) + b)
                best = min(best, (nxt[c - 1] if c > 0 else 0.0) + b)
            else:
                best = min(best, a)
            row[c] = best
    return d


# --- The boulders: a watershed of the sprite's shading ---------------------------------------------------------

SEG_SIGMA, SEG_PROMINENCE = 0.6, 1.6   # the shade's blur and how far a boulder's peak must stand over its saddle
MIN_REGION = 14                         # smaller regions join the neighbour they share the longest border with


def segment(pic, rock):
    """The boulders the sprite draws: a watershed of its blurred shade (from the light peaks down to the dark
    crevices), a basin merging into its neighbour where its peak stands less than SEG_PROMINENCE over their saddle;
    grey stones (ramp 0) apart from the brown ones. Returns a label per pixel (-1 none), labels 0..n-1."""
    a = pic.a
    h, w = a.shape
    shade = np.where(a >= 0, a & 15, 0).astype(float)
    grey = (a >= 0) & ((a >> 4) == 0) & (shade >= 3)
    cls = np.where(grey, 1, 0)
    num, den = blur(shade * rock, SEG_SIGMA), blur(rock.astype(float), SEG_SIGMA)
    sm = np.where(rock, num / np.maximum(den, 1e-6), -1.0)
    order = sorted((-round(float(sm[r, c]), 6), r, c) for r in range(h) for c in range(w) if rock[r, c])
    lab = -np.ones((h, w), int)
    parent, peak = [], []

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for negv, r, c in order:
        v = -negv
        nb = set()
        for r2, c2 in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1), (r + 1, c + 1), (r - 1, c - 1),
                       (r + 1, c - 1), (r - 1, c + 1)):
            if 0 <= r2 < h and 0 <= c2 < w and lab[r2, c2] >= 0 and cls[r2, c2] == cls[r, c]:
                nb.add(find(lab[r2, c2]))
        if not nb and shade[r, c] <= 2:
            for r2, c2 in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                if 0 <= r2 < h and 0 <= c2 < w and lab[r2, c2] >= 0:
                    nb.add(find(lab[r2, c2]))
        if not nb:
            parent.append(len(parent))
            peak.append(v)
            lab[r, c] = len(parent) - 1
            continue
        nb = sorted(nb, key=lambda i: (-peak[i], i))
        top = nb[0]
        for o in nb[1:]:
            if peak[o] - v < SEG_PROMINENCE:
                parent[o] = top
        lab[r, c] = top
    for r in range(h):
        for c in range(w):
            if lab[r, c] >= 0:
                lab[r, c] = find(lab[r, c])
    # Small regions join their neighbour with the longest shared border.
    while True:
        ids = sorted(set(lab[lab >= 0].tolist()))
        sizes = {i: int((lab == i).sum()) for i in ids}
        small = [i for i in ids if sizes[i] < MIN_REGION]
        if not small:
            break
        i = min(small, key=lambda j: (sizes[j], j))
        border = {}
        for r, c in zip(*np.nonzero(lab == i)):
            for r2, c2 in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                if 0 <= r2 < h and 0 <= c2 < w and lab[r2, c2] >= 0 and lab[r2, c2] != i:
                    border[lab[r2, c2]] = border.get(lab[r2, c2], 0) + 1
        if not border:
            lab[lab == i] = -1
            continue
        j = max(border, key=lambda q: (border[q], -q))
        lab[lab == i] = j
    ids = sorted(set(lab[lab >= 0].tolist()))
    remap = {old: new for new, old in enumerate(ids)}
    return np.vectorize(lambda v: remap.get(v, -1))(lab)


def convex_hull(points):
    pts = sorted(set(points))

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 1e-9:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 1e-9:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def simplify(poly, count):
    """Visvalingam: the polygon's vertices removed, the one spanning the smallest triangle first, down to count."""
    pts = list(poly)

    def area(i):
        a, b, c = pts[i - 1], pts[i], pts[(i + 1) % len(pts)]
        return abs((b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])) / 2
    while len(pts) > count:
        i = min(range(len(pts)), key=lambda j: (area(j), j))
        pts.pop(i)
    return pts


TIERS = (0.06, 0.32, 0.66)         # the fractions of the way in where each edge's facets touch the boulder's profile


class Boulder:
    """A boulder over a region of the sprite: a convex cap of planar facets, one rising from each edge of its
    footprint (its core pixels' simplified hull, the edge at the mound's height there) to its apex, cut by a flat
    top a little under the apex, leaning towards the light; its colours its pixels' ramp."""

    def __init__(self, index, pic, cells, mound_at, seed, heights):
        self.index = index
        base, per, cut, top_lean = heights
        rng = random.Random(seed)
        a = pic.a
        cs = [(r, c) for r, c in cells]
        core = [(r, c) for r, c in cs if (a[r, c] & 15) >= 3] or cs
        ramps = {}
        for r, c in core:
            ramps[a[r, c] >> 4] = ramps.get(a[r, c] >> 4, 0) + 1
        self.ramp = max(sorted(ramps), key=lambda q: ramps[q])
        corners = []
        for r, c in core:
            for du, dv in ((0, 0), (1, 0), (0, 1), (1, 1)):
                corners.append((pic.left + c + du, pic.top - r - dv))
        hull = convex_hull(corners)
        n = max(5, min(9, int(round(4 + math.sqrt(len(core)) / 4))))
        self.hull = simplify(hull, n) if len(hull) > n else hull
        xs = np.array([pic.left + c + 0.5 for r, c in cs])
        ys = np.array([pic.top - r - 0.5 for r, c in cs])
        # The apex: between the region's middle and its widest point (farthest from its outline).
        mid = (float(xs.mean()), float(ys.mean()))
        hx = np.array([p[0] for p in self.hull])
        hy = np.array([p[1] for p in self.hull])
        hmid = (float(hx.mean()), float(hy.mean()))
        jitter = (rng.uniform(-0.6, 0.6), rng.uniform(-0.6, 0.6))
        self.apex = (0.5 * mid[0] + 0.5 * hmid[0] + jitter[0], 0.5 * mid[1] + 0.5 * hmid[1] + jitter[1])
        size = math.sqrt(len(cs))
        h = (base + per * size) * rng.uniform(0.9, 1.1)
        self.size = size
        planes = []
        edge_z = []
        m = len(self.hull)
        for i in range(m):
            p0, p1 = self.hull[i], self.hull[(i + 1) % m]
            ex, ey = p1[0] - p0[0], p1[1] - p0[1]
            length = math.hypot(ex, ey)
            if length < 1e-6:
                continue
            nx, ny = -ey / length, ex / length            # inward for a counter-clockwise hull
            mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
            ze = mound_at(mx, my) + 0.35
            edge_z.append(ze)
            planes.append((nx, ny, p0, ze))
        apex_z = max(mound_at(*self.apex) + h, max(edge_z) + 1.2)
        self.top_z = apex_z
        self.planes = []
        # Each edge's facets: tangent planes of a rounded profile (a quarter ellipse from the edge up to the top)
        # at fractions TIERS of the way in, each a little turned and steeper or flatter at random: the min of all
        # the planes is a boulder of large flat facets, its top cut flat a little under its apex.
        for nx, ny, p0, ze in planes:
            d_apex = max(nx * (self.apex[0] - p0[0]) + ny * (self.apex[1] - p0[1]), 0.8)
            rise = apex_z - ze
            for t in TIERS:
                q = 1.0 - t
                height = ze + rise * math.sqrt(max(0.0, 1.0 - q * q))
                slope = rise * q / max(math.sqrt(max(1e-6, 1.0 - q * q)), 1e-3) / d_apex
                slope *= rng.uniform(0.85, 1.15)
                turn = rng.uniform(-0.18, 0.18)
                tx, ty = nx * math.cos(turn) - ny * math.sin(turn), nx * math.sin(turn) + ny * math.cos(turn)
                # z = height + slope * (n' . (p - p0) - t d_apex)
                self.planes.append((slope * tx, slope * ty,
                                    height - slope * (tx * p0[0] + ty * p0[1] + t * d_apex)))
        # The flat top, a little under the apex, leaning towards the light (up and to the left).
        tz = apex_z - cut * h
        lx, ly = -top_lean * rng.uniform(0.6, 1.4), top_lean * rng.uniform(0.6, 1.4)
        self.planes.append((-lx, -ly, tz + lx * self.apex[0] + ly * self.apex[1]))
        xs_h = [p[0] for p in self.hull]
        ys_h = [p[1] for p in self.hull]
        self.box = (min(xs_h) - 1.0, max(xs_h) + 1.0, min(ys_h) - 1.0, max(ys_h) + 1.0)

    def field(self, X, Y):
        """The cap's height at points and the facet that makes it (the lowest plane)."""
        z = np.full(np.shape(X), np.inf)
        which = np.zeros(np.shape(X), int)
        for i, (A, B, C) in enumerate(self.planes):
            zi = A * X + B * Y + C
            better = zi < z
            z = np.where(better, zi, z)
            which = np.where(better, i, which)
        return z, which


# --- The heap ------------------------------------------------------------------------------------------------------

class Heap:
    """A heap of boulders (and, for the machine heap, the machine) as one heightfield in the picture's plane on the
    grid STEP apart: Z (heights of the grid points), the owner of each cell (-1 the mound, boulder index, or a
    machine part: MACHINE + part) and of each boulder cell its facet."""

    def __init__(self, pic, rock, mound, edge, heights, seed, machine=None):
        self.pic = pic
        h, w = pic.a.shape
        self.box = (pic.left, pic.left + w, pic.top - h, pic.top)
        obj = pic.a >= 0
        self.obj_mask = obj
        # The outline: the pixels' mask, a little smoothed (its 0.5 contour).
        self.soft = blur(obj.astype(float), 0.55)
        nx, ny = int(round(w / STEP)), int(round(h / STEP))
        xs = pic.left + STEP * np.arange(nx + 1)
        ys = pic.top - h + STEP * np.arange(ny + 1)
        self.X, self.Y = np.meshgrid(xs, ys)
        cx, cy = self.X[:-1, :-1] + STEP / 2, self.Y[:-1, :-1] + STEP / 2
        self.cell_in = pic.sample(self.soft, cx, cy) > 0.5
        # The mound: rising from the outline (of the whole object) over `edge` pixels to `mound`.
        fine_in = pic.sample(self.soft, self.X, self.Y) > 0.5
        d = chamfer(fine_in, STEP)
        t = np.clip(d / edge, 0.0, 1.0)
        self.M = 0.25 + (mound - 0.25) * np.sqrt(t * (2.0 - t))

        def mound_at(x, y):
            i = int(round((x - pic.left) / STEP))
            j = int(round((y - (pic.top - h)) / STEP))
            i, j = max(0, min(nx, i)), max(0, min(ny, j))
            return float(self.M[j, i])
        labels = segment(pic, rock)
        self.labels = labels
        self.boulders = []
        for i in range(labels.max() + 1):
            cells = list(zip(*np.nonzero(labels == i)))
            self.boulders.append(Boulder(i, pic, cells, mound_at, seed * 101 + i, heights))
        Z = self.M.copy()
        owner = -np.ones(Z.shape, int)
        facet = np.zeros(Z.shape, int)
        for b in self.boulders:
            x0, x1, y0, y1 = b.box
            sel = (self.X >= x0) & (self.X <= x1) & (self.Y >= y0) & (self.Y <= y1)
            zb, which = b.field(self.X[sel], self.Y[sel])
            cur = Z[sel]
            up = zb > cur
            Z[sel] = np.where(up, zb, cur)
            o = owner[sel]
            o[up] = b.index
            owner[sel] = o
            f = facet[sel]
            f[up] = which[up]
            facet[sel] = f
        if machine is not None:
            Zm, part = machine(self.X, self.Y)
            up = Zm > Z
            Z = np.where(up, Zm, Z)
            owner = np.where(up, MACHINE + part, owner)
        self.Z, self.owner_pt, self.facet_pt = Z, owner, facet

    def top(self, X, Y):
        """Plate's top: the heights at its grid points (the plate's grid is this one's)."""
        i = np.round((X - self.box[0]) / STEP).astype(int)
        j = np.round((Y - self.box[2]) / STEP).astype(int)
        return self.Z[j, i]

    def cells(self, X, Y):
        i = np.floor((X - self.box[0]) / STEP).astype(int)
        j = np.floor((Y - self.box[2]) / STEP).astype(int)
        i = np.clip(i, 0, self.cell_in.shape[1] - 1)
        j = np.clip(j, 0, self.cell_in.shape[0] - 1)
        return self.cell_in[j, i]


MACHINE = 1000                    # owner codes of the machine's parts start here


# --- The machine ---------------------------------------------------------------------------------------------------
# Its parts in the machine heap's picture: (column, row) pixel corners (u, v); its heights over the ground.

MACHINE_POLY = [(0.0, 13.5), (25.5, 13.5), (27.5, 29.0), (30.5, 33.0), (30.5, 35.5), (38.0, 35.5), (38.0, 57.0),
                (31.5, 58.5), (31.5, 87.0), (0.0, 87.0)]
HOUSING, HOUSING_FALL = 2.2, 0.9          # the housing's top and how far in from its outline it rises to it
EMBOSS = (0.16, -0.45, 0.8)               # the sprite's shading as relief: per shade over 4.5, its limits
VENT = (18.0, 36.0)                       # the vent's fins run down these rows
FINS = [(5.5, 1.5), (9.5, 1.5), (13.5, 1.5), (17.5, 1.5), (7.5, 0.6), (11.5, 0.6), (15.5, 0.6)]
FIN_HALF = 0.62
EYE_C, EYE_R = (21.5, 47.3), (10.2, 8.4)  # the eye (its pixels: columns 11-31 of rows 39-55)
RING_R, RING_HALF, RING_H = (11.2, 9.4), 1.35, 2.5
EYE_BASE, EYE_H = 0.5, 1.7                # the dull eye: over the housing, its dome
ROD = (33.8, 1.6, 37.0, 57.0, 1.9)        # the rod right of the ring: column, half-width, rows, height
SPINE_POLY = [(12.5, 57.0), (30.5, 57.0), (31.0, 86.5), (12.0, 86.5)]
SPINE_H = 0.9
LAMPS = [((22.0, 63.5), (6.0, 3.5)), ((22.0, 73.5), (4.0, 2.5)), ((22.0, 81.5), (3.0, 1.6))]
SOCKET_GROW, SOCKET_HALF, SOCKET_H = 0.95, 0.75, 1.15
LAMP_BASE, LAMP_H = 0.35, 0.95            # the dull lamps: over the spine, their domes
# Part codes (owner MACHINE + code).
P_HOUSING, P_FIN, P_RING, P_EYE, P_ROD, P_SPINE, P_SOCKET, P_LAMP = range(8)


def machine_mask(pic):
    h, w = pic.a.shape
    cc, rr = np.meshgrid(np.arange(w) + 0.5, np.arange(h) + 0.5)
    ramp = pic.a >> 4
    return inside_poly(MACHINE_POLY, cc, rr) & (pic.a >= 0) & np.isin(ramp, (0, 7, 4))


def ellipse_rho(u, v, centre, radii):
    return np.sqrt(((u - centre[0]) / radii[0]) ** 2 + ((v - centre[1]) / radii[1]) ** 2)


def bead(rho, radii, half):
    """A rounded band along an ellipse (rho 1), half wide either side: 0-1."""
    reach = (rho - 1.0) * 0.5 * (radii[0] + radii[1])
    return np.sqrt(np.clip(1.0 - (reach / half) ** 2, 0.0, None))


def dome01(rho):
    return np.sqrt(np.clip(1.0 - rho ** 2, 0.0, None))


def machine_heights(pic, mask):
    """The machine as a function of the picture's points: (Z, part); -inf outside it."""
    soft = blur(mask.astype(float), 0.5)
    shade = np.where(pic.a >= 0, pic.a & 15, 0).astype(float)
    num, den = blur(shade * mask, 0.55), blur(mask.astype(float), 0.55)
    sm = np.where(den > 1e-3, num / np.maximum(den, 1e-6), 0.0)
    spine = None

    def heights(X, Y):
        u, v = X - pic.left, pic.top - Y
        inside = pic.sample(soft, X, Y) > 0.5
        d = chamfer(inside, STEP)
        t = np.clip(d / HOUSING_FALL, 0.0, 1.0)
        z = 0.2 + (HOUSING - 0.2) * np.sqrt(t * (2.0 - t))
        part = np.full(z.shape, P_HOUSING)
        k_, lo, hi = EMBOSS
        z = z + np.clip((pic.sample(sm, X, Y) - 4.5) * k_, lo, hi) * t
        # The vent's fins.
        vr = smoothstep(VENT[0], VENT[0] + 1.5, v) * (1.0 - smoothstep(VENT[1] - 1.8, VENT[1], v))
        for uf, hf in FINS:
            f = np.sqrt(np.clip(1.0 - ((u - uf) / FIN_HALF) ** 2, 0.0, None)) * vr * (u < 27.0)
            up = f * hf
            part = np.where((up > 0.3) & (hf > 1.0), P_FIN, part)
            z = z + up
        # The spine: a raised plate under the lamps.
        sp = inside_poly([(a_, b_) for a_, b_ in SPINE_POLY], u, v)
        z = np.where(sp, z + SPINE_H, z)
        part = np.where(sp, P_SPINE, part)
        # The ring and the dull eye in it.
        rho = ellipse_rho(u, v, EYE_C, RING_R)
        ring = bead(rho, RING_R, RING_HALF)
        rz = HOUSING + RING_H * ring
        part = np.where((ring > 0.05) & (rz > z), P_RING, part)
        z = np.maximum(z, np.where(ring > 0.0, rz, -np.inf))
        er = ellipse_rho(u, v, EYE_C, EYE_R)
        ez = HOUSING + EYE_BASE + EYE_H * dome01(er)
        inside_eye = er < 1.0
        part = np.where(inside_eye & (ez >= z - 1e-6), P_EYE, part)
        z = np.where(inside_eye, np.maximum(z, ez), z)
        # The rod right of the ring.
        rc, rw, r0, r1, rh = ROD
        rod = np.sqrt(np.clip(1.0 - ((u - rc) / rw) ** 2, 0.0, None)) * smoothstep(r0, r0 + 1.2, v) * \
            (1.0 - smoothstep(r1 - 1.2, r1, v))
        rz = HOUSING + rh * rod
        part = np.where((rod > 0.05) & (rz > z), P_ROD, part)
        z = np.maximum(z, np.where(rod > 0.0, rz, -np.inf))
        # The lamps' sockets and the dull lamps.
        top = HOUSING + SPINE_H
        for (c, rad) in LAMPS:
            grown = (rad[0] + SOCKET_GROW, rad[1] + SOCKET_GROW)
            rho = ellipse_rho(u, v, c, grown)
            s = bead(rho, grown, SOCKET_HALF)
            sz = top + SOCKET_H * s
            part = np.where((s > 0.05) & (sz > z), P_SOCKET, part)
            z = np.maximum(z, np.where(s > 0.0, sz, -np.inf))
            lr = ellipse_rho(u, v, c, rad)
            lz = top + LAMP_BASE + LAMP_H * dome01(lr)
            inside_l = lr < 1.0
            part = np.where(inside_l & (lz >= z - 1e-6), P_LAMP, part)
            z = np.where(inside_l, np.maximum(z, lz), z)
        z = np.where(inside, z, -np.inf)
        return z, part
    return heights


# --- Colours -------------------------------------------------------------------------------------------------------

LIFT = 0.8                        # painted this many shades lighter than drawn (the game reads darker)
MACHINE_LIFT = 1.7                # the machine's dark steel more (its sprite is mostly near-black)
COMP, LIT_MEAN = 0.8, 0.72        # and lighter where the game's sun lights a face less (gyges_wall's way)
BOULDER_LIFT = 0.6                # a boulder's one colour this much lighter again (its faces away from the sun read dark)
CREVICE = 0xa2                    # the dark between the boulders (the sprite's near-black lines and outline)
ROCK = (0.05, 0.78)               # finishes (metallic, roughness)
STEEL = (0.45, 0.36)
SILVER = (0.6, 0.24)
GLASS = (0.2, 0.22)
RAMP_SHADES = {0xa: (3, 4, 5, 6, 7, 8, 9, 10, 11), 0x1: (4, 5, 6, 7, 8, 9, 10, 11), 0x0: (2, 4, 6, 8, 10, 12, 13),
               0xb: (3, 4, 5, 6, 7), 0x7: (1, 3, 5, 7, 9, 11, 13), 0x4: (2, 3, 4, 5)}


def lit(normals):
    """How much the game's sun lights faces of these normals (0-1), after the shear."""
    n = np.array(normals, float)
    n = np.stack([n[..., 0], n[..., 1], n[..., 2] + TAN_T * n[..., 1]], -1)
    n /= np.linalg.norm(n, axis=-1)[..., None]
    return np.clip(n @ SUN, 0.0, 1.0)


def quantize(ramp, shade):
    shades = RAMP_SHADES.get(ramp, (3, 5, 7, 9, 11))
    return ramp * 16 + min(shades, key=lambda s: (abs(s - shade), s))


class Palette:
    """The materials of a model: (index, finish, glow) -> material, made on first use."""

    def __init__(self, prefix):
        self.prefix, self.mats = prefix, {}

    def get(self, key):
        if key not in self.mats:
            index, finish, glow = key
            metallic, roughness = finish
            extra = {}
            if glow > 0:
                extra = dict(emission=k.level_palette()[index], emission_strength=glow)
            name = "%s_%s%x" % (self.prefix, {ROCK: "r", STEEL: "s", SILVER: "m", GLASS: "g"}.get(finish, "x"), index)
            if glow > 0:
                name += "e"
            self.mats[key] = k.material(name, palette=index, metallic=metallic, roughness=roughness, **extra)
        return self.mats[key]


# --- The whole heaps -----------------------------------------------------------------------------------------------

def grid(left, top, w, h, offset=0.0):
    nx, ny = int(round(w / STEP)), int(round(h / STEP))
    count = (nx + 1, ny + 1) if offset == 0.0 else (nx, ny)
    xs = left + offset + STEP * np.arange(count[0])
    ys = top - h + offset + STEP * np.arange(count[1])
    return np.meshgrid(xs, ys)


class Whole:
    """A heap as one heightfield: Z on the grid's points; on its cells' middles the owner (-1 the mound, a boulder's
    index, or MACHINE + a machine part) and the boulder facet."""

    def __init__(self, pic, rock, mound, edge, heights, seed, machine=None):
        self.pic = pic
        h, w = pic.a.shape
        self.w, self.h = w, h
        self.rock_soft = blur(rock.astype(float), 0.55)
        # The sprite's near-black lines (the crevices between the boulders), smoothed.
        darkmask = np.vectorize(lambda v: dark(int(v)))(pic.a) & (pic.a >= 0)
        self.dark_soft = blur(darkmask.astype(float), 0.5)
        self.box = (pic.left, pic.left + w, pic.top - h, pic.top)
        self.soft = blur((pic.a >= 0).astype(float), 0.7)
        self.X, self.Y = grid(pic.left, pic.top, w, h)
        self.CX, self.CY = grid(pic.left, pic.top, w, h, STEP / 2)
        self.cell_in = pic.sample(self.soft, self.CX, self.CY) > 0.5
        self.labels = segment(pic, rock)
        nx, ny = self.X.shape[1] - 1, self.X.shape[0] - 1
        Mg = self.mound(self.X, self.Y, mound, edge)

        def mound_at(x, y):
            i = max(0, min(nx, int(round((x - pic.left) / STEP))))
            j = max(0, min(ny, int(round((y - (pic.top - h)) / STEP))))
            return float(Mg[j, i])
        self.boulders = [Boulder(i, pic, list(zip(*np.nonzero(self.labels == i))), mound_at, seed * 101 + i, heights)
                         for i in range(self.labels.max() + 1)]
        self.machine = machine
        self.Z, _, _ = self.fields(self.X, self.Y, Mg)
        Mc = self.mound(self.CX, self.CY, mound, edge)
        _, self.owner, self.facet = self.fields(self.CX, self.CY, Mc)

    def mound(self, X, Y, mound, edge):
        """The dark mound under the boulders: rising from the object's outline over `edge` to `mound`; only under
        the rock (not over the machine, which the boulders lean on)."""
        inside = self.pic.sample(self.soft, X, Y) > 0.5
        t = np.clip(chamfer(inside, STEP) / edge, 0.0, 1.0)
        m = 0.25 + (mound - 0.25) * np.sqrt(t * (2.0 - t))
        return np.where(self.pic.sample(self.rock_soft, X, Y) > 0.35, m, 0.0)

    def fields(self, X, Y, M):
        Z = M.copy()
        owner = -np.ones(Z.shape, int)
        facet = np.zeros(Z.shape, int)
        for b in self.boulders:
            x0, x1, y0, y1 = b.box
            sel = (X >= x0) & (X <= x1) & (Y >= y0) & (Y <= y1)
            zb, which = b.field(X[sel], Y[sel])
            cur = Z[sel]
            up = zb > cur
            Z[sel] = np.where(up, zb, cur)
            o = owner[sel]
            o[up] = b.index
            owner[sel] = o
            f = facet[sel]
            f[up] = which[up]
            facet[sel] = f
        if self.machine is not None:
            Zm, part = self.machine(X, Y)
            up = Zm > Z
            Z = np.where(up, Zm, Z)
            owner = np.where(up, MACHINE + part, owner)
        return Z, owner, facet

    def cell_of(self, x, y):
        i = int(math.floor((x - self.box[0]) / STEP))
        j = int(math.floor((y - self.box[2]) / STEP))
        return max(0, min(self.owner.shape[0] - 1, j)), max(0, min(self.owner.shape[1] - 1, i))

    def plate(self):
        def top(X, Y):
            i = np.round((X - self.box[0]) / STEP).astype(int)
            j = np.round((Y - self.box[2]) / STEP).astype(int)
            return self.Z[j, i]

        def cells(X, Y):
            i = np.clip(np.floor((X - self.box[0]) / STEP).astype(int), 0, self.cell_in.shape[1] - 1)
            j = np.clip(np.floor((Y - self.box[2]) / STEP).astype(int), 0, self.cell_in.shape[0] - 1)
            return self.cell_in[j, i]
        return Plate(self.box, top, cells=cells)


def pixel_at(pic, x, y):
    c = int(math.floor(x - pic.left))
    r = int(math.floor(pic.top - y))
    if 0 <= r < pic.h and 0 <= c < pic.w:
        return int(pic.a[r, c])
    return -1


def dark(index):
    return index < 0 or index in (0x01, 0x00) or ((index >> 4) in (0xa, 0x1, 0xb, 0x0) and (index & 15) <= 2)


def facet_colours(whole):
    """Each boulder facet's palette index: the mean shade of the sprite's pixels under its cells in their
    commonest ramp (the dark ones left out), lifted, lighter the less the game's sun lights its plane."""
    pic = whole.pic
    a = pic.a
    sums = {}
    for j in range(whole.owner.shape[0]):
        for i in range(whole.owner.shape[1]):
            o = whole.owner[j, i]
            if o < 0 or o >= MACHINE or not whole.cell_in[j, i]:
                continue
            v = pixel_at(pic, whole.CX[j, i], whole.CY[j, i])
            if dark(v) or (v >> 4) not in RAMP_SHADES or (v >> 4) in (7, 4):
                continue
            key = (o, int(whole.facet[j, i]))
            sums.setdefault(key, {}).setdefault(v >> 4, []).append(v & 15)
    # One colour a boulder (2026-10-31): a colour a facet, given cell by cell on the grid, drew its facets' borders as
    # pixel staircases in flat posterised patches (the QA pass); the game's light shades its facets instead.
    out = {}
    for b in whole.boulders:
        default = float(np.median([a[r, c] & 15 for r, c in zip(*np.nonzero(whole.labels == b.index))
                                   if not dark(int(a[r, c]))] or [5]))
        by_ramp = {}
        for f in range(len(b.planes)):
            for ramp, shades in sums.get((b.index, f), {}).items():
                by_ramp.setdefault(ramp, []).extend(shades)
        if sum(len(v) for v in by_ramp.values()) >= 3:
            ramp = max(sorted(by_ramp), key=lambda q: len(by_ramp[q]))
            mean = float(np.mean(by_ramp[ramp]))
        else:
            ramp, mean = b.ramp, default
        colour = quantize(ramp, mean + LIFT + BOULDER_LIFT)
        for f in range(len(b.planes)):
            out[(b.index, f)] = colour
    return out


def machine_colour(whole, part, x, y, normal):
    """A machine face's (index, finish, glow) from the sprite's pixel under it."""
    pic = whole.pic
    v = pixel_at(pic, x, y)
    light = float(lit([normal])[0])
    comp = COMP * (LIT_MEAN - light)
    ramp, shade = (v >> 4, v & 15) if v >= 0 else (0, 2)
    if part in (P_EYE, P_LAMP):
        if ramp not in (7, 4):
            ramp, shade = 7, 2
        return (quantize(ramp, shade + 0.5), GLASS, 0.15)
    if part in (P_RING, P_SOCKET, P_ROD):
        s = max(shade if ramp == 0 else 0, 7) + LIFT + comp
        return (quantize(0, s), SILVER, 0.0)
    if ramp == 0:
        return (quantize(0, max(shade, 2) + MACHINE_LIFT + comp), STEEL, 0.0)
    if ramp in (7, 4):
        return (quantize(ramp, shade), GLASS, 0.12)
    return (quantize(ramp if ramp in RAMP_SHADES else 0xa, shade + LIFT + comp), ROCK, 0.0)


def limit_materials(keys, counts, limit=15):
    """Merges the rarest keys into the nearest of the same finish and ramp until at most `limit` remain."""
    keys = dict(keys)
    while len(set(keys.values())) > limit:
        used = {}
        for face, key in keys.items():
            used[key] = used.get(key, 0) + 1
        rare = min(used, key=lambda q: (used[q], q))
        others = [q for q in used if q != rare]
        same = [q for q in others if q[1] == rare[1] and q[0] >> 4 == rare[0] >> 4] or \
            [q for q in others if q[1] == rare[1]] or others
        near = min(same, key=lambda q: (abs((q[0] & 15) - (rare[0] & 15)), q))
        keys = {face: (near if key == rare else key) for face, key in keys.items()}
    return keys


def paint_piece(whole, obj, kinds, facet_key, palette, dark_key):
    """Every face's material, and the boulders' facets their planes' normals (flat, crisp)."""
    mesh = obj.data
    keys = {}
    normals = [Vector(n.vector) for n in mesh.corner_normals]
    current = None
    for poly, kind in zip(mesh.polygons, kinds):
        if kind == 0:
            c = poly.center
            j, i = whole.cell_of(c.x, c.y)
            current = (j, i)
            o = int(whole.owner[j, i])
            if 0 <= o < MACHINE:
                f = int(whole.facet[j, i])
                if float(whole.pic.sample(whole.dark_soft, c.x, c.y)) > 0.5:
                    keys[poly.index] = dark_key
                else:
                    keys[poly.index] = (facet_key[(o, f)], ROCK, 0.0)
                # (The heightfield's own normals: its triangles' facets, not the planes' cell by cell.)
                n = Vector(poly.normal)
                for li in poly.loop_indices:
                    normals[li] = n
            elif o >= MACHINE:
                n = Vector(normals[poly.loop_indices[0]])
                keys[poly.index] = machine_colour(whole, o - MACHINE, c.x, c.y, tuple(n))
            else:
                keys[poly.index] = dark_key
        else:
            o = int(whole.owner[current]) if current is not None else -1
            keys[poly.index] = (0x02, STEEL, 0.0) if o >= MACHINE else dark_key
    keys = limit_materials(keys, None)
    order = sorted(set(keys.values()))
    for key in order:
        mesh.materials.append(palette.get(key))
    for poly in mesh.polygons:
        poly.material_index = order.index(keys[poly.index])
    mesh.normals_split_custom_set([tuple(n) for n in normals])
    mesh.update()


def heap_pieces(whole, sprites, name, palette, options):
    """The whole cut into its pieces on the grid (each the cells of its sprite's box), painted, sheared for the
    camera, moved to its sprite's centre and exported."""
    plate = whole.plate()
    facet_key = facet_colours(whole)
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    sheet = os.path.join(options["check"], "enemy_R.png") if "check" in options else None
    results = []
    for sprite, box, centre in piece_boxes(sprites, whole.box[0], whole.box[3]):
        model = "%s_%d" % (name, sprite)
        if only and model not in only and name not in only:
            continue
        x0, x1, y0, y1 = box
        e = 1e-6
        obj, kinds, _ = plate.mesh(model, lambda X, Y: (X > x0 + e) & (X < x1 - e) & (Y > y0 + e) & (Y < y1 - e))
        if obj is None:
            print("== %s: empty" % model)
            continue
        paint_piece(whole, obj, kinds, facet_key, palette, (CREVICE, ROCK, 0.0))
        shear_to_camera([obj])
        obj.data.transform(Matrix.Translation((-centre[0], -centre[1], 0.0)))
        parts = triangulate([obj])
        bpy.context.view_layer.update()
        if sheet:
            mask = k.sprite_mask(sheet, sprite)
            mk.compare("%s (R %d, as the camera sees it)" % (model, sprite), piece_coverage(whole, box), mask)
            mk.compare("%s (R %d, from straight above)" % (model, sprite), mk.coverage(parts, 24, 28), mask)
        mk.report(model, parts, os.path.join(out, model + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + model, parts)
        results.append(parts)
        for o in parts:
            bpy.data.objects.remove(o)
    return results


def piece_coverage(whole, box):
    """Which pixels of a piece's box the heightfield's cells cover (in the picture's plane: as the camera sees
    it), half of a pixel's cells or more."""
    x0, x1, y0, y1 = box
    rows = []
    for r in range(28):
        row = []
        for c in range(24):
            n = 0
            for dj in (0.25, 0.75):
                for di in (0.25, 0.75):
                    j, i = whole.cell_of(x0 + c + di, y1 - r - dj)
                    n += bool(whole.cell_in[j, i])
            row.append(n >= 2)
        rows.append(row)
    return rows


# --- The eye and the lamps, lit (enemies of their own over the machine's) -------------------------------------------

EYE_LENS = (3.4, 2.8)                 # the lit eye: its rim's height (in the ring) and its dome over it
LAMP_LENS = [(3.5, 1.35), (3.5, 1.1), (3.5, 0.9)]
HOT_SHADES = (2, 4, 6, 8, 10, 12, 14, 15)
RIM = 0x72                            # the lens's rim (where the sprite draws its golden or dark red bezel)


def hot_key(heat):
    """A lit lens face's (index, finish, glow) for a heat (a shade of ramp 7, 0-15; None: the rim): its own red,
    glowing the more the hotter."""
    if heat is None or heat < 1.0:
        return (RIM, GLASS, 0.22)
    s = min(HOT_SHADES, key=lambda q: (abs(q - heat), q))
    return (0x70 + s, GLASS, round(0.16 + 0.027 * s, 3))


def lens(name, pic, centre, radii, base, height, sample, palette, rings=10, segments=44):
    """A glowing lens over an ellipse of the picture (pixel corners (u, v) of the machine heap): a dome rising from
    its rim at `base` to `base + height`, a skirt under its rim, its faces painted by sample(u, v) -> palette index."""
    (uc, vc), (ru, rv) = centre, radii
    cx, cy = pic.left + uc, pic.top - vc
    verts, faces = [], []
    ring_rho = [1.0 - (i / rings) ** 1.6 for i in range(rings)]  # finer towards the rim
    profile = [(1.02, base - 0.7)] + [(rho, base + height * (1.0 - rho * rho) ** 0.55) for rho in ring_rho]
    for rho, z in profile:
        for s in range(segments):
            a = 2 * math.pi * s / segments
            verts.append((cx + ru * rho * math.cos(a), cy + rv * rho * math.sin(a), z))
    top = len(verts)
    verts.append((cx, cy, base + height))
    bottom = len(verts)
    verts.append((cx, cy, base - 0.7))
    n = len(profile)
    for i in range(n - 1):
        for s in range(segments):
            a0, a1 = i * segments + s, i * segments + (s + 1) % segments
            faces.append((a0, a1, a1 + segments, a0 + segments))
    last = (n - 1) * segments
    for s in range(segments):
        faces.append((last + s, last + (s + 1) % segments, top))
        faces.append(((s + 1) % segments, s, bottom))
    obj = k.mesh_object(name, verts, faces, None)
    keys = []
    for poly in obj.data.polygons:
        c = poly.center
        keys.append(hot_key(sample(c.x - pic.left, pic.top - c.y)) if c.z > base - 0.05 else (RIM, GLASS, 0.22))
    order = sorted(set(keys))
    for key in order:
        obj.data.materials.append(palette.get(key))
    for poly, key in zip(obj.data.polygons, keys):
        poly.material_index = order.index(key)
    k.recalc_normals(obj)
    return k.smooth(obj, 70)


def frame_sampler(text, at, shift=0):
    """The frame's heat under a point of the machine heap's picture (u, v), smoothed between its pixels: ramp 7 its
    shade, the deep reds (ramp 4) darker, the golden glints (ramp 1) warm, the bezel (ramp a) cool; its sprite's top
    left pixel at `at`, sampled `shift` rows lower (the eye's sprite draws its orb lower than the machine's eye)."""
    rows = parse(text)
    heat = np.zeros((28, 24))
    for r, row in enumerate(rows[:28]):
        for c, v in enumerate(row[:24]):
            if v is None:
                continue
            ramp, shade = v >> 4, v & 15
            heat[r, c] = {7: shade, 4: 0.6 * shade, 1: 6.0, 0xa: 1.5}.get(ramp, 0.0)
    heat = blur(heat, 0.6)

    def sample(u, v):
        fc = u - at[0] - 0.5
        fr = v - at[1] + shift - 0.5
        if not (-0.5 <= fc <= 23.5 and -0.5 <= fr <= 27.5):
            return None
        fc, fr = min(max(fc, 0.0), 22.999), min(max(fr, 0.0), 26.999)
        c0, r0 = int(fc), int(fr)
        tc, tr = fc - c0, fr - r0
        return float((heat[r0, c0] * (1 - tc) + heat[r0, c0 + 1] * tc) * (1 - tr) +
                     (heat[r0 + 1, c0] * (1 - tc) + heat[r0 + 1, c0 + 1] * tc) * tr)
    return sample


def frame_text(prefix, frame):
    return globals()["%s_%d" % (prefix, frame)]


def lit_models(pic, options):
    """The eye (four frames) and the lamps (four frames), each at its sprite's centre."""
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    eye_centre = (pic.left + EYE_AT[0] + 12, pic.top - EYE_AT[1] - 14)
    lamps_centre = (pic.left + LAMPS_AT[0] + 12, pic.top - LAMPS_AT[1] - 14)
    jobs = []
    for i, f in enumerate(EYE_FRAMES):
        jobs.append(("ixm_boss_eye" if i == 0 else "ixm_boss_eye_%d" % f, "EYE", f, eye_centre))
    for i, f in enumerate(LAMP_FRAMES):
        jobs.append(("ixm_boss_lamps" if i == 0 else "ixm_boss_lamps_%d" % f, "LAMPS", f, lamps_centre))
    for name, kind, f, centre in jobs:
        if only and name not in only and "lit" not in only:
            continue
        palette = Palette("ixml%d" % f)
        objs = []
        if kind == "EYE":
            sample = frame_sampler(frame_text(kind, f), EYE_AT, EYE_SHIFT)
            objs.append(lens(name, pic, EYE_C, EYE_R, EYE_LENS[0], EYE_LENS[1], sample, palette, rings=12, segments=56))
        else:
            sample = frame_sampler(frame_text(kind, f), LAMPS_AT)
            for i, ((c, rad), (base, height)) in enumerate(zip(LAMPS, LAMP_LENS)):
                objs.append(lens("%s_%d" % (name, i), pic, c, rad, base, height, sample, palette,
                                 rings=8, segments=36 - 6 * i))
        shear_to_camera(objs)
        for o in objs:
            o.data.transform(Matrix.Translation((-centre[0], -centre[1], 0.0)))
        parts = triangulate(objs)
        bpy.context.view_layer.update()
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts)
        for o in parts:
            bpy.data.objects.remove(o)


# --- Build ---------------------------------------------------------------------------------------------------------

BOSS_MOUND, BOSS_EDGE = 4.5, 9.0
COVER_MOUND, COVER_EDGE = 6.5, 10.0
HEIGHTS = (1.6, 0.30, 0.16, 0.08)     # a boulder's height: base + per * sqrt(area); its top cut; its top's lean


def build():
    options = k.args()
    k.reset()
    bpy.context.scene.view_settings.view_transform = "Standard"
    groups = options["only"].split(",") if "only" in options else ["ixm_boss", "lit", "ixm_cover"]
    want = lambda g: any(n == g or n.startswith(g + "_") or (g == "lit" and n.startswith("ixm_boss_e"))  # noqa: E731
                         or (g == "lit" and n.startswith("ixm_boss_l")) for n in groups)
    boss = picture(BOSS_ART, BOSS_W, BOSS_LEFT, BOSS_TOP)
    if want("ixm_boss") or want("lit"):
        mask = machine_mask(boss)
        rock = (boss.a >= 0) & ~mask
        if want("ixm_boss"):
            whole = Whole(boss, rock, BOSS_MOUND, BOSS_EDGE, HEIGHTS, 7, machine_heights(boss, mask))
            print("machine heap: %d boulders, z %.2f..%.2f" % (len(whole.boulders), whole.Z.min(), whole.Z.max()))
            heap_pieces(whole, BOSS_SPRITES, "ixm_boss", Palette("ixmb"), options)
        if want("lit"):
            lit_models(boss, options)
    if want("ixm_cover"):
        cover = picture(COVER_ART, COVER_W, COVER_LEFT, COVER_TOP)
        whole = Whole(cover, cover.a >= 0, COVER_MOUND, COVER_EDGE, HEIGHTS, 5)
        print("cover: %d boulders, z %.2f..%.2f" % (len(whole.boulders), whole.Z.min(), whole.Z.max()))
        heap_pieces(whole, COVER_SPRITES, "ixm_cover", Palette("ixmc"), options)


if __name__ == "__main__":
    build()
