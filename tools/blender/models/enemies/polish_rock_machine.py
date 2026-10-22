"""SURFACE's rock machine: a grey machine set in an outcrop of tan rock, its tower, two arched grips, a body, two thin
arms and two big claws (sheet ^, x5e in models.cfg: 77 79 81 above 115 117 119, 2x2 each, one 72 x 56 picture), the
sparks between its claws when it fires (117's frames 7 and 9) and its wreck (1 3 5 above 39 41 43); polished
(2026-10-22, round 37). It replaces wave3_i.py's sand_whole() and wave3_ap_surface.py's sand_damaged() (pixel regions
raised in bands; the wreck those regions cut back, dented and repainted).

Where the level puts it: SURFACE's event 7 (the top layer), four times (t2008 x 138, t2764 x 90, t4276 x 114, t6040 x
138): enemies 245 (77), 246 (79), 247 (81) at x, x + 24, x + 48 and y -84, 248 (115), 249 (117), 250 (119) under them
at y -56, all on link 199; t2869 and t6041 give link 199 the boss bar (t6041 also armour 254: the last one is SURFACE's
boss, with the two spiked hands, polish_spike_hand.py). Only 249 (117) has armour (20) and fires (tur 139-141): its
animation 117 7 7 9 9 7 7 9 9 117 (animate 2: once each time it fires) shows the sparks; the other five, armour 0, one
frame each. All six have dlevel -1 and their dgr: when 249 is shot down every piece of the link stays where it is,
switched to its wreck (77 -> 1, 79 -> 3, 81 -> 5, 115 -> 39, 117 -> 41, 119 -> 43; tyrian2.c's edlevel -1). SURFACE's
backgrounds 2 and 3 are empty and background 3 scrolls with background 1 (events 2: bg1 = bg3 throughout; event 65 sets
its x like background 1's), so the machine rides on the ground as if fixed in it: the map under it is plain sand (once
a metal track), the rock is the machine's own. No other level (episode 6 included) uses these enemies (INVADERS'
events naming 245 and 247 are fire overrides of links), and no other enemy, launched ones included, shows these
sprites, 7 and 9 or the wrecks; no other sprite is their pixels mirrored, turned or in other ramps.

As the sprites and their 4x upscales draw it (columns and rows of the 72 x 56 picture; grey ramp 0, tan ramp 1, lit
from the upper left; the machine symmetric about column 33's middle, the rock not): an outcrop of rock across the
whole width (rows 3-41), its top lit (shades b-e), its south face in shade (5-7) with dark cracks; set in it the
machine: the tower (columns 29-37 of rows 3-17), a lying round post, its lit left edge and a bright rim (row 7) under
its rounded end; the body (columns 22-45 of rows 15-36), a block with a seam down its middle (column 33); either side
an arched grip (columns 8-21 of rows 2-21 on the left), a bar rising out of the rock beside the body, up its long leg
and over in an arch whose short end goes back into the rock; a thin arm from each side of the body down to a little
splayed foot on the rock's south face (columns 4-10 of rows 33-37 on the left); two big claws from the body's lower
corners down and in over the sand to their points (columns 17-27 of rows 33-53 on the left, the points at columns 24
and 42 of row 53). 7 and 9: 117 with a crackling arc of light blue (ramp 3, 0x39-0x3e) between the claws' points
(rows 15-25 of 117). The wreck (1-43): the tower broken off to a jagged stump (rows 5-14), the body caved in and
cracked (dark holes), the claws snapped (the left one's stub to row 45, the right one's to row 38), the right grip's
leg broken through (rows 15-18); the rock, the arms and the left grip as before.

Built for the game's camera with polish_sheet9_kit: one heightfield of the whole picture in its plane on the sprites'
grid (the rock a slab rounding over at its outline, higher where the sprite lights it (its broad shading), its cracks
creased; the machine's parts over it: the tower a lying round post, the body a rounded block, the grips and the arms
lying bars that ride over the rock, the claws lying tubes falling from the body to the sand; the machine's pixels
decide where its parts stand, the rock's where only the rock does, so the wreck's broken grip and snapped claws follow
its own pixels); painted by the pixels under it (polish_sheet9_kit.Painter) and sheared along the camera's line of
sight; the wreck the same shapes on the wreck's pixels, the tower cut to a jagged stump, the body dented, its dark
cracks sunk deep. The arcs: a band of light floating between the claws' points, a heightfield of its own over its
pixels' outline with a lens-shaped section (its top and bottom meeting at its outline), sagging a little towards its
middle and wandering in height, painted by its pixels in their own blues, glowing (0.3-0.55); 117's model with it is
each frame's model (they share 117's origin). Heights: the rock 2.0-6.8, the body 9.0, the tower 11.7 (the wreck's
broken top 6.0 rising to the right, a shard to 8.5), the claws' points 2.3; the arcs 1.4-3.3.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground (z 0). The whole's
origin is the middle of the picture: column c is x = c + 0.5 - 36, row r is y = 27.5 - r; the pieces' origins (their
sprites' middles) (-24, 14) 77, (0, 14) 79, (24, 14) 81, (-24, -14) 115, (0, -14) 117, (24, -14) 119; the wreck's the
same (1 3 5 39 41 43); the frame models 7 and 9 117's.

models.cfg: model lines stay (rock_machine_tl ... _br, rock_machine_tl_damaged ... origin), new: model rock_machine_bc_7
and rock_machine_bc_9 enemies/rock_machine_bc_7.glb (_9) origin, frame x5e 7 rock_machine_bc_7, frame x5e 9
rock_machine_bc_9; every sprite line (77 79 81 115 117 119 and 1 3 5 39 41 43) gets layer=ground height=-4 (the game
puts the machine on the top layer, 38 pixels up; it belongs on the sand, as SURFACE's rock arch).

Replaces wave3_i.py's machine (SAND, sand_whole(), its w.WHOLES["sand"] entry and the loop registering rock_machine_tl
... _br, the rock_machine paragraph of its docstring, "sand," in its --whole usage line) and wave3_ap_surface.py
whole (its only model), wave3_i_art.py's SAND and wave3_ap_art.py's SAND_DMG.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each piece's outline as the
camera sees it against its sprite's pixels), --preview <prefix>, --only <name,...>.
"""
import math
import os
import sys

import bpy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_sheet9_kit as nk  # noqa: E402
from polish_sheet9_kit import Pic, parse, blur, smoothstep, smax, Region, Zone, Painter, round_rise  # noqa: E402

MIRROR_U = 33.5                   # the machine's mirror line (column 33's middle): u' = 2 MIRROR_U - u
ROCK = (2.0, 4.8, 2.6, (3.0, 11.0), 1.5)   # base height, more where lit, rounding, the lit shades' range, its blur
ROCK_DETAIL = (0.16, 0.45)        # the rock's fine shading as relief: per shade, its limit
ROCK_END = 4.5                    # the rock, cut off by the picture's sides, falls to the sand over this
ROCK_CRACK = 0.9                  # its dark cracks (a shade 3+ darker than round them) creased this deep
TOWER = [(33.5, 4.0, 4.6, 11.5), (33.5, 16.4, 4.7, 11.5)]   # a lying post (column, row, half width, height)
BODY = ((33.5, 25.6), (11.7, 10.7), 4.0, 9.0, 2.6)          # middle, half sizes, superellipse power, height, rounding
GRIP = [(23.0, 20.6), (19.6, 20.0), (16.2, 19.2), (13.4, 17.9), (11.5, 16.0), (10.3, 13.0), (9.9, 9.6), (10.0, 6.6),
        (10.7, 4.4), (12.5, 3.0), (14.7, 2.7), (16.9, 3.3), (18.5, 4.7), (19.3, 6.5)]  # the left grip's bar
GRIP_W = (2.0, 2.2, 6.2)          # its half width, how far it stands over the rock, its arch's least height
ARM = [(19.5, 24.4), (16.5, 25.4), (13.6, 27.0), (11.6, 28.8), (10.5, 30.8), (9.8, 32.8), (8.4, 34.6), (6.6, 35.8),
       (5.0, 36.6)]               # the left arm
ARM_W = (1.8, 2.4, 1.7)           # its half width, its foot's, how far it stands over the rock
CLAW = [(28.0, 30.0, 5.6, 9.0), (24.0, 35.5, 5.1, 7.4), (21.0, 40.0, 4.5, 6.0), (20.4, 44.0, 4.1, 4.9),
        (21.0, 48.0, 3.3, 3.9), (22.4, 50.8, 2.5, 3.0), (24.2, 53.3, 1.7, 2.3)]  # the left claw (column, row, hw, h)
CREASE = 0.8
DETAIL = (0.08, 0.2)
STUMP = (6.0, 0.35, (37.2, 6.0), (0.9, 1.6), 2.2)  # the wreck's tower: its broken top's height, rising this much a
                                  # column to the right, a shard standing at (column, row), its size, how high
DENT = 0.9                        # the wreck's body this much lower
HOLE = 2.6                        # and its dark cracks sunk this deep
GREY = list(range(0x01, 0x10))
TAN = list(range(0x10, 0x1f))
BLUE = [0x39, 0x3a, 0x3b, 0x3c, 0x3d, 0x3e]
BLUE_GLOW = {0x39: 0.3, 0x3a: 0.34, 0x3b: 0.38, 0x3c: 0.44, 0x3d: 0.5, 0x3e: 0.55}
BOLT_H = (0.7, 2.6, 0.5, 0.35)    # the arc: half its thickness, its middle's height, its sag, its wander
BOLT_MID = -2.5                   # the arc's middle (x): half way between the claws' points
FINISH = {"grey": (0.3, 0.36), "tan": (0.0, 0.8), "blue": (0.1, 0.3), "dark": (0.1, 0.6)}
PIECES = [("tl", 77, 1, (0, 0)), ("tc", 79, 3, (24, 0)), ("tr", 81, 5, (48, 0)), ("bl", 115, 39, (0, 28)),
          ("bc", 117, 41, (24, 28)), ("br", 119, 43, (48, 28))]

# The machine's pixels (palette indices), as the level puts its six sprites together.
ART = """
    ................................................................................................................................................
    ................................................................................................................................................
    ....................04040506050404..................................................................04040506050404..............................
    10101001010101....040406070606050404........................03010101020101........................040405060607060404....................10010110
    1b1a1a18171716160404060b09080706040404....................040707070606070503....................040404060708090b060404..........1010101013191b1c
    1c1c1c1c1c1b1d1c04040a080404040404040404..................040b08080808080804..................0404040404040404080a040401110110100117181a1c1c1c1c
    1c1c1c1c1a181b1a02040a05040404040404041110................020c090909090909050101010111111110121104040404040404050a04021617131418191b1c1c1c1c1c1c
    1c1c1c1c1c19191902040d051b1b1b1918171713131211100110101110030f0c0c0d0d0c0b05101213151819191b1a1919181717171a1c050d04021717171a1a1a1a1b1c1c1c1c1c
    1c1c1c1c1c1b191703040c051b1b1b1b1b1b1a1a181716151517171614040c0a0a0a0a0a0a051113161a1b1c1c1c1c1c1c1c1c1d1d1e1e050c04031717191a1a1a1a1a1b1c1c1c1c
    1b1b1b1b1b1b171703050b081b1b1b1b1b1b1b1b1b1b1a191a1a1a1814050a0909090909090412141a1b1b1a1c1c1c1c1d1d1e1e1e1d1c080b050317171b1b1a1a1a1a1a1a1b1b1b
    1b1b1b1b1b1b1918020409061b1b1b1b1b1b1b1b1b1b1b1b1b1a1b1a16070c0808080808080311171a1c1c1b1e1e1e1e1e1e1e1c1b1a1b0609040218191b1b1b1b1a1a1a1a1a1a1b
    1a1b1b1b1b1b1b17020308051b1b1b1b1b1b1b1b1b1b1b1c1d1b1b1b17070b0808080808080414181b1c1c1b1d1d1d1d1d1b1b1a1a1a1b0508030214171717171718181818191919
    19191919191a1a17030307051b1b1b1b1b1b1b1b1b1b1b1b1e1b1b1b17060a08080808080805161c1b1b1b181a1a1a1a1a1a1a1a1b1c1c05070303141818181919191a1a1a1a1a1a
    1a1a1a1a19181a19020306041b1b1b1b1b1b1b1b1b1b1a1b1e1b1a1915060908080808080805111c1b1b1b16181a1b1b1c1c1c1d1d1d1c040603021719191a1a1a1a1a1a1a1a1a1a
    1a1a1a1a18181a19020305041a1a191a1b1b1b1b1b1a1a1a1f1c1a1812050808080808080805141c1b1a1b1316171a1c1c1d1d1d1d1d1b0405030217191a1a1a1a1a1a1a1a1a1a1a
    1a1a191a1b1c1c1d13030404191819191818191919191a1a0e0b0a0903050808080808080705050d09090a131314181b1c1d1d1d1e1c1a04040310191a1a191a1a1a1a1a1a1a1a1a
    1b1a1a1c1b1c1c1c190304040318191919191818160404050e0a0a0905060708080808070706060c08090801030117191b1d1d1c1e1a03040403171919191a1a1a1a1a1a1a1a1a1a
    1b1c1c1c1c1c1b1b1a1404040303191a1a191918040505050e090909070606070808070706070b090808080304040116191d1d1c1a0303040413191a1b1b1b1b1b1a1a1a1a1a1a1a
    1c1c1b1a1a1a1a1a1a17150404040318191a1904050606060d0808080807060606060606080b08080808080504030303161b1c1b030404041819191b1b1b1b1b1b1b1b1a1a1b1b1c
    1b1a1a1a1a1a1a19171615150404040301030405050606060d08080808080909090a0a0a0a0808080808080504030303010301030404041818191b1b1b1b1b1b1b1b1b1b1c1c1c1c
    1a1a191818171616161616151603040404040405060607070b09080808080808080808080808080808080705040303030304040404031818191b1b1b1b1b1b1b1b1b1c1c1c1c1c1b
    1616161616161616161616171717170304040206060708090b0a08080808080808080808080808080808070504030303030304031717191a1b1b1b1b1b1b1b1b1b1b1b1a18171617
    171717171717171717171717181717171614030303040404090b0a080808080808080808080808080807050502020202021016171818181a1b1a1a19191818181818181716161617
    171717171717171717171717171717151410020607080906060a0b0b0a09080808070808080808080705050403050404031213151717161617161515141414151516161616171717
    171717171717171717171717161613010211040607080909060609090a0a0b0b0c060d0b0a0908070505030306040404041202011216151615141515161615121415171717171717
    17171717171717171717171715020404040402050708080909050808080707070a040a07070707050503030704040404040404040402131414141517171717151215171817171717
    17171717171717171717171501040404041504020707080808030508070707070a030a06060605050303060404040404041404040404011315151616161717171514161817171717
    171717171717171717161401040404031213100105070707070606070707070709030a07060605050303040404040402101212030404040113151616161616171614141418171717
    171717171717171717150204040410121113131303050707060707070707070709040a06060606060403030404040411101110111204040402141616161616161616151416181717
    171717171616151514010304041312141616161603030404050707070707070708040906060607070704030304040311121314131112040403011516161616161615161514151717
    171716151514121412030404111014151616161605050305080808080808070708010706070707080808060302030210131313131410110404031416161616161515151515131616
    151515161313131302040403111415151516161603040507080909080606060707010707070707080808080701020314131210111213110304040214151515151515151515121515
    1515131314131513020404021315151515151515020307080a0907050505060607010607070707080809090806020316161513121313110204040213151515151515151313121515
    11101111131515120404041315151515151515140307080a090505050505041514101415050607080809090a09040316161616151413121004040412151515151414121111111414
    121110111303030304040414151515141414121205090b0906050505050511101110121110030707080909090b070313141516161615131004040403030311131312010101101113
    0101121303040404040403141515131312111211080c0906050505050511101011....111111020608090909090b0601121211111111131003040404040403121210011011111011
    10101211010304040404011114121313131212130b0a08050505050511121011..............03060809090a0a0b0101..............01040404040301..0101100111121214
    11101211010303040402011211111013121314090b0a070505050512........................020708090a0a0b0801..............01020404030301....01111111121314
    14141413110201010101....131212111013080c0b0a0605050513............................0107090a0a0b0b0501..............0101010102........010101131515
    15151414111010..............14120101080a0b0b06050413..............................0107090a0a0b0a0501..................................1001131415
    1413121212....................13100108090c0b070610..................................0108090b0b080501....................................10100114
    10..............................140108080909060301..................................0108080a07060701..........................................10
    ..................................01070808090601......................................01080906060601............................................
    ..................................01060808090601......................................01080906070501............................................
    ..................................01040808090601......................................01080906060401............................................
    ....................................010808080501......................................010809060601..............................................
    ....................................010608080501......................................010809050501..............................................
    ......................................0108080601......................................0108090501................................................
    ......................................0105080601......................................0108080401................................................
    ........................................01060501......................................01080601..................................................
    ..........................................010501......................................010801....................................................
    ............................................010201..................................010801......................................................
    ..............................................0101..................................0101........................................................
    ................................................01..................................01..........................................................
    ................................................................................................................................................
    ................................................................................................................................................
"""
# Its wreck (1 3 5 above 39 41 43).
DMG_ART = """
    ................................................................................................................................................
    ................................................................................................................................................
    ....................04040506050404..................................................................04040506050404..............................
    10101001010101....040406070606050404..............................................................040405060607060404....................10010110
    1b1a1a18171716160404060b09080706040404..........................................................040404060708090b060404..........1010101013191b1c
    1c1c1c1c1c1b1d1c04040a080404040404040404................................0804..................0404040404040404080a040401110110100117181a1c1c1c1c
    1c1c1c1c1a181b1a02040a05040404040404041110............................0909050101010111111110121104040404040404050a04021617131418191b1c1c1c1c1c1c
    1c1c1c1c1c19191902040d051b1b1b1918171713131211100110101110030f0c0c0d0d0c0b05101213151819191b1a1919181717171a1c050d04021717171a1a1a1a1b1c1c1c1c1c
    1c1c1c1c1c1b191703040c051b1b1b1b1b1b1a1a181716151517171614040c0a0a0a0a0a0a051113161a1b1c1c1c1c1c1c1c1c1d1d1e1e050c04031717191a1a1a1a1a1b1c1c1c1c
    1b1b1b1b1b1b171703050b081b1b1b1b1b1b1b1b1b1b1a191a1a1a1814050a0909090808090412141a1b1b1a1c1c1c1c1d1d1e1e1e1d1c080b050317171b1b1a1a1a1a1a1a1b1b1b
    1b1b1b1b1b1b1918020409061b1b1b1b1b1b1b1b1b1b1b1b1b1a1b1a16070c0808060505070311171a1c1c1b1e1e1e1e1e1e1e1c1b1a1b0609040218191b1b1b1b1a1a1a1a1a1a1b
    1a1b1b1b1b1b1b17020307051b1b1b1b1b1b1b1b1b1b1b1c1d1b1b1b1706090807050404070414181b1c1c1b1d1d1d1d1d1b1b1a1a1a1b0508030214171717171718181818191919
    19191919191a1a17030205041b1b1b1b1b1b1b1b1b1b1b1b1e1b1b1b16020506060504060705161c1b1b1b181a1a1a1a1a1a1a1a1b1c1c05070303141818181919191a1a1a1a1a1a
    1a1a1a1a19181a19020204031b1b1b1b1b1b1b1b1b1b1a1b1e1b1a1914010103040306090805111c1b1b1b16181a1b1b1c1c1c1d1d1d1c040603021619191a1a1a1a1a1a1a1a1a1a
    1a1a1a1a18181a19020304041a1a191a1b1b1b1b1b1a1a1a1f1c1a181101010101040b080805141b1b1a1b1316171a1c1c1d1d1d1d1d1b0405030215191a1a1a1a1a1a1a1a1a1a1a
    1a1a191a1b1c1c1d13030404191819191818191919191a1a0e0b0a0903040301010a07080705050b09080a131314181b1c1d1b1b1b1b1b18010211181a1a191a1a1a1a1a1a1a1a1a
    1b1a1a1c1b1c1c1c190304040318191919191818160404050e0a0a0905060705030707050505040c07070701030117191b1d1d1b1b1b1b1b1716141718191a1a1a1a1a1a1a1a1a1a
    1b1c1c1c1c1c1b1b1a1404040303191a1a191918040505050e090909070606070104020305070a090607070304040116191d1d1c1a1a1a1a1a1a1717191b1b1b1b1a1a1a1a1a1a1a
    1c1c1b1a1a1a1a1a1a17150404040318191a1904050606060d0808080807050501020104070b07050608080504030303161b19151617181a1a1a1a1a1a1b1b1b1b1b1b1a1a1b1b1c
    1b1a1a1a1a1a1a19171615150404040301030405050606060d08080808090a0a0a0a0a09080504060809080504030303010302080502191b1b1a1a1b1b1b1b1b1b1b1b1b1c1c1c1c
    1a1a191818171616161616151603040404040405060607070b0908080809090a0a0a0c060403050a0908070504030303030405050403181b1b191b1b1b1b1b1b1b1b1c1c1c1c1c1b
    1616161616161616161616171717170304040206060708090b0a0808080809090a0b040205060b080808070504030303030304031717191a1b1a1b1b1b1b1b1b1b1b1b1a18171617
    171717171717171717171717181717171614030303040404090b0a08080808090a050202060808080807050502020202021016171818181a1b1a1a19191818181818181716161617
    171717171717171717171717171717151410020607080906060a0b0b0a09080704010202060808080705050403050404031213151717161617161515141414151516161616171717
    171717171717171717171717161613010211040607080909050609090a0a090707020905080908070505030305030404041202011216151615141515161615121415171717171717
    171717171717171717171717150204040404020506070808060408080806040206020601030607050503030501010304040404040402131414141517171717151215171817171717
    171717171717171717171715010404040415040104040605040105080606060509020701010505050302040101010304041404040404011315151616161717171514161817171717
    171717171717171717161401040404031213100101030302020506050405060709020702030404040101010101020402101212030404040113151616161616171614141418171717
    171717171717171717150204040410121113131201010301010606040405070708010501010303030101010102040411101110111204040402141616161616161616151416181717
    171717171616151514010304041312141616161501010101010505050507070708030706080808020101010104040311121314131112040403011516161616161615161514151717
    171716151514121412030404111014151616161603020101010506060808060608010707080805010102040302030210131313131410110404031416161616161515151515131616
    151515161313131302040403111415151516161603030301020608080504030507010707070501010108080701020314131210111213110304040214151515151515151515121515
    151513131413151302040402131515151515151502030604040706050104040607010606050301010107090806020316161513121313110204040213151515151515151313121515
    111011111315151204040413151515151515151403070808040205020304021514101313040301030303070a09040316161616151413121004040412151515151414121111111414
    121110111303030304040414151515141414121205090b0601010604050311101110121110040405050407070b070313141516161615131004040403030311131312010101101113
    0101121303040404040403141515131312111211080c0803010208040410101011....11121002050706050606080401121211111111131003040404040403121210011011111011
    10101211010304040404011114121313131212130b0804040309050410121011..............03060605050101020101..............01040404040301..0101100111121214
    11101211010303040402011211111013121314090b07050506050512........................0206030101......................01020404030301....01111111121314
    14141413110201010101....131212111013080c09050605050513............................0101............................0101010102........010101131515
    15151414111010..............14120101080a080504040413..............................01..................................................1001131415
    1413121212....................13100108090705020210......................................................................................10100114
    10..............................1401070401....................................................................................................10
    ..................................010403........................................................................................................
    ..................................0101..........................................................................................................
    ..................................0101..........................................................................................................
    ....................................01..........................................................................................................
    ................................................................................................................................................
    ................................................................................................................................................
    ................................................................................................................................................
    ................................................................................................................................................
    ................................................................................................................................................
    ................................................................................................................................................
    ................................................................................................................................................
    ................................................................................................................................................
    ................................................................................................................................................
    ................................................................................................................................................
"""
# The arcs: the blue pixels of 7 and 9 (117's box, 24 x 28; the rest of the sprites is 117's).
ARC_ART = {7: """
    ................................................
    ................................................
    ................................................
    ................................................
    ................................................
    ................................................
    ................................................
    ................................................
    ................................................
    ................................................
    ................................................
    ................................................
    ................................................
    ................................................
    ................................................
    ................................................
    ................................................
    39....39393a3a3a................................
    39393a3a3b3c3c3b3b..........39393b3a3b..........
    3a3c3d3d3d3c3c3c3c3d3d3a393a3a3c3c3d3a3a........
    3c3e3e3e3c3c3b3d3e3e3e3b3a3c3d3e3e3c3b39........
    3a3c3d3b3a..3b3c3d3d3d3b3b3c3c3c..3a3939........
    393a3b3a......3a3a3a3b3c3c3c3a3a....39..........
    ..39............3939..3b3b3a3939................
    ......................3a393939..................
    ........................39......................
    ................................................
    ................................................
""", 9: """
    ................................................
    ................................................
    ................................................
    ................................................
    ................................................
    ................................................
    ................................................
    ................................................
    ................................................
    ................................................
    ................................................
    ................................................
    ................................................
    ................................................
    ................................................
    39..............................................
    3939..............393a3a3a......................
    3b3939..........3a3b3b3b3b3a..3a39..............
    3c3d3a3a393a3b3c3c3b393b3b3c3c3c3a..............
    3e3d3d3c3c3c3a393b3c3e3e3e3d3e3c3b..393a........
    3a3b3c3d3d3c3c3a3a3b3d3e3d3e3d3e3d3e3e3b........
    393a3b3e3d3b3a3b3a3b3b3b3a3b3b393c3e3d3b........
    ..393b3c3c3a393939393a3a39393939393b3b..........
    ....39....3939................39..3939..........
    ......393939....................................
    ................................................
    ................................................
    ................................................
"""}


def lying(u, v, points, power=0.5):
    """polish_gyges_wall.tube in the picture's columns and rows (v down the picture)."""
    return nk.tube(u, -v, [(c, -r, hw, hh) for c, r, hw, hh in points], power)


def path_tube(u, v, path, hw, power=0.5):
    """A lying bar of one half width along a path of (column, row): its section's height (0-1) at each point, and
    where along the path (0-1) the nearest point lies."""
    best = np.full(u.shape, 1e9)
    along = np.zeros(u.shape)
    total = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(path, path[1:]))
    s = 0.0
    for (pu, pv), (qu, qv) in zip(path, path[1:]):
        du, dv = qu - pu, qv - pv
        ln = math.hypot(du, dv)
        t = np.clip(((u - pu) * du + (v - pv) * dv) / max(1e-9, ln * ln), 0.0, 1.0)
        d = np.hypot(u - (pu + t * du), v - (pv + t * dv))
        closer = d < best
        best = np.where(closer, d, best)
        along = np.where(closer, (s + t * ln) / total, along)
        s += ln
    return np.clip(1.0 - (best / hw) ** 2, 0.0, None) ** power, along


class Machine:
    def __init__(self, art, wreck=False):
        self.pic = Pic(parse(art), -36.0, 28.0)
        self.wreck = wreck
        a = self.pic.a
        own = a >= 0
        self.region = Region(self.pic, own, sigma=0.5)
        shade = np.where(own, a & 15, 0).astype(float)
        grey = own & (a >> 4 == 0)
        tan = own & (a >> 4 == 1)
        self.grey = blur(grey.astype(float), 0.7)
        h, w = a.shape
        p = np.pad(own, 1)
        surrounded = np.ones_like(own)
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            surrounded &= p[1 + dr:1 + dr + h, 1 + dc:1 + dc + w]
        dark = grey & (shade <= (2 if wreck else 1))
        self.crease = blur((dark & surrounded).astype(float), 0.45)
        tan_shade = nk.fill(shade, tan)
        round_ = blur(tan_shade, 1.0)
        self.crack = blur((tan & surrounded & (tan_shade <= round_ - 3.0)).astype(float), 0.45)
        self.lit = blur(tan_shade, ROCK[4])
        # The rock goes on under the machine near its own pixels, not under the claws out over the sand.
        self.near = np.clip(blur(nk.dilate(tan, 4).astype(float), 1.2) * 1.6, 0.0, 1.0)
        self.soft = blur(nk.fill(shade, own), 0.6)
        self.broad = blur(nk.fill(shade, own), 2.0)
        self.rsoft = blur(tan_shade, 0.6)
        self.rbroad = blur(tan_shade, 2.0)

    def rock(self, X, Y, d):
        pic = self.pic
        base, more, rnd, (s0, s1), _ = ROCK
        z = (base + more * smoothstep(s0, s1, pic.sample(self.lit, X, Y))) * round_rise(d, rnd)
        z = z * pic.sample(self.near, X, Y)
        z = z * round_rise(np.minimum(X + 36.0, 36.0 - X), ROCK_END)
        fine = pic.sample(self.rsoft, X, Y) - pic.sample(self.rbroad, X, Y)
        z = z + np.clip(ROCK_DETAIL[0] * fine, -ROCK_DETAIL[1], ROCK_DETAIL[1]) * smoothstep(0.8, 2.0, z)
        return z - ROCK_CRACK * pic.sample(self.crack, X, Y) * np.clip(z / 3.0, 0.0, 1.0)

    def half(self, u, v, rock):
        """The machine's left half over the rock (its right half mirrored)."""
        sec, along = path_tube(u, v, GRIP, GRIP_W[0])
        arch = GRIP_W[2] * np.sin(np.pi * np.clip((along - 0.45) / 0.55, 0.0, 1.0)) ** 0.5
        grip = np.where(sec > 0, np.maximum(rock + GRIP_W[1] * (0.45 + 0.55 * sec), arch * (0.55 + 0.45 * sec)), 0.0)
        sec, along = path_tube(u, v, ARM, ARM_W[0])
        foot, _ = path_tube(u, v, ARM[-3:], ARM_W[1])
        sec = np.maximum(sec, foot)
        arm = np.where(sec > 0, rock + ARM_W[2] * (0.4 + 0.6 * sec), 0.0)
        claw = lying(u, v, CLAW, power=0.4)
        return np.maximum(np.maximum(grip, arm), claw)

    def heights(self, X, Y):
        X, Y = np.asarray(X, float), np.asarray(Y, float)
        u, v = X + 36.0, 28.0 - Y
        d = self.region.depth(X, Y)
        rock = self.rock(X, Y, d)
        machine = np.maximum(self.half(u, v, rock), self.half(2 * MIRROR_U - u, v, rock))
        (bu, bv), (bx, by), power, bh, brnd = BODY
        q = np.abs((u - bu) / bx) ** power + np.abs((v - bv) / by) ** power
        body = bh * round_rise((1.0 - q) * min(bx, by) / power * 2.0, brnd) * (q < 1.0)
        tower = lying(u, v, TOWER, power=0.5)
        if self.wreck:
            body = np.maximum(body - DENT, 0.0)
            top, rise, (su, sv), (sx, sy), sh = STUMP
            teeth = top + rise * (u - MIRROR_U) + sh * np.exp(-((u - su) / sx) ** 2 - ((v - sv) / sy) ** 2)
            tower = np.minimum(tower, teeth)
        machine = smax(machine, smax(body, tower, 0.9), 0.6)
        g = self.pic.sample(self.grey, X, Y)
        z = rock + g * np.maximum(machine - rock, 0.0)
        pic = self.pic
        deep = HOLE if self.wreck else CREASE
        z = z - deep * pic.sample(self.crease, X, Y) * np.clip(z / 4.0, 0.0, 1.0) * g
        fine = pic.sample(self.soft, X, Y) - pic.sample(self.broad, X, Y)
        z = z + np.clip(DETAIL[0] * fine, -DETAIL[1], DETAIL[1]) * smoothstep(1.0, 3.0, z) * g
        z = z * round_rise(d, 0.8)
        return np.where(d > 0, np.maximum(z, 0.0), 0.0)


def arc_plate(frame):
    """The arc of frame 7 or 9: a band of light floating between the claws' points, one heightfield over its pixels
    (their smooth outline) with a lens-shaped section (its top and bottom BOLT_H[0] apart in its middle, meeting at its
    outline), wandering a little in height and sagging towards its middle; painted by its pixels."""
    pic = Pic(parse(ARC_ART[frame]), -12.0, 0.0)             # 117's box: x -12..12, y -28..0
    region = Region(pic, pic.a >= 0, sigma=0.45)
    half, mid, sag, wan = BOLT_H

    def centre(X, Y):
        t = np.clip(1.0 - ((X - BOLT_MID) / 10.0) ** 2, 0.0, 1.0)
        return mid - sag * t + wan * (0.6 * np.sin(0.9 * X + 0.4 * Y + 0.7) + 0.4 * np.sin(1.7 * X - 0.8 * Y + 2.1))

    def top(X, Y):
        d = region.depth(X, Y)
        return np.where(d > 0, centre(X, Y) + half * round_rise(d, 0.9), centre(X, Y))

    def base(X, Y):
        d = region.depth(X, Y)
        return np.where(d > 0, centre(X, Y) - half * round_rise(d, 0.9), centre(X, Y))
    return pic, nk.gw.Plate((-12.0, 12.0, -28.0, 0.0), top, base=base, cells=region.inside)


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    looks = [("rock_machine", ART, False, None), ("rock_machine_bc_7", ART, False, 7),
             ("rock_machine_bc_9", ART, False, 9), ("rock_machine_damaged", DMG_ART, True, None)]
    for look, art, wreck, frame in looks:
        names = []
        for key, sprite, dsprite, at in PIECES:
            if frame is not None and key != "bc":
                continue
            name = look if frame is not None else ("rock_machine_%s_damaged" % key if wreck else "rock_machine_%s" % key)
            names.append((name, key, sprite, dsprite, at))
        if only is not None and not any(n[0] in only for n in names):
            continue
        k.reset()
        machine = Machine(art, wreck)
        pic = machine.pic
        a = pic.a
        own = a >= 0
        zones = [Zone("grey", own & (a >> 4 == 0), GREY, FINISH["grey"]),
                 Zone("tan", own & (a >> 4 == 1), TAN, FINISH["tan"], sigma=0.7),
                 Zone("blue", own, BLUE, FINISH["blue"], glow=BLUE_GLOW, lift=0.0, comp=0.0, pick=False),
                 Zone("dark", own, [0x01, 0x02, 0x10, 0x11], FINISH["dark"], lift=0.0, comp=0.0, pick=False)]
        painter = Painter(pic, zones, "rockm")
        plate = nk.gw.Plate((-36.0, 36.0, -28.0, 28.0), machine.heights, cells=machine.region.inside)
        solids = []
        bolt = arc_plate(frame) if frame is not None else None

        def keys(obj, kinds, wall_z):
            centres, normals = nk.face_data(obj)
            near = painter.zone_at(centres[:, 0], centres[:, 1])
            out_ = painter.keys(obj, zones=["dark" if kinds[i] != 0 else near[i] for i in range(len(kinds))])
            return [("dark", 0x01) if kinds[i] != 0 else key for i, key in enumerate(out_)]
        for name, key, sprite, dsprite, (c0, r0) in names:
            if only is not None and name not in only:
                continue
            box = nk.sprite_box(pic, c0, r0)
            parts = nk.piece_parts(plate, keys, solids, box, nk.box_owner(box), name, painter, ("dark", 0x01))
            if bolt is not None:
                bpic, bplate = bolt
                obj, kinds, _ = bplate.mesh(name + "_arc", nk.box_owner(box))
                centres, _ = nk.face_data(obj)
                shade = bpic.sample(blur(nk.fill(bpic.shade(), bpic.a >= 0), 0.6), centres[:, 0], centres[:, 1])
                picks = nk.gw.nearest(shade + 0.4, BLUE)
                nk.assign(obj, [("blue", int(v)) for v in picks], painter)
                parts.append(obj)
            for p in parts:
                p.hide_render = False
            mask = None
            if "check" in options:
                mask = nk.sprite_mask(pic, c0, r0)
                if frame is not None:      # the frame's own pixels: 117's with the arc's over them
                    arc_rows = parse(ARC_ART[frame])
                    mask = [[mask[r][c] or arc_rows[r][c] is not None for c in range(24)] for r in range(28)]
            piece = nk.finish(name, parts, box, out, options, painter, mask=mask,
                              origin=(pic.left + c0 + 12, pic.top - r0 - 14))
            bpy.data.objects.remove(piece)


if __name__ == "__main__":
    build()
