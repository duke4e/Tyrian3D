"""The heavy grey field gun of TORM, BOTANY A and BONUS (episode 2): sheet J sprites 89 above 127, 129 to 127's right
(2x2 each; enemies 764, 765, 766, ground layer) and 119 to 89's left (enemy 763: the muzzle flash's own sprite),
polished (2026-10-21, round 26; it replaces wave3_m_ground.py's gun_whole() and gun_piece(), a lathed barrel on a tube
neck between two pillow blocks, and wave3_ap_torm.py's damaged barrel, built from it). models.cfg: model
field_gun_barrel / field_gun_breech / field_gun_mount / field_gun_flash and the frame and damaged models below,
enemies/field_gun_*.glb origin; sprite j 89 field_gun_barrel yaw=0 height=-4 and so on.

The levels put the four in a row and a column (TORM's events at 2345 and 2401, BOTANY A's at 105, 1029, 1085, 4193,
4445 and 4529, BONUS's at 1897, 2065, 2597, 2653, 3017 and 3045): 765 (127) at (x, y), 766 (129) 24 pixels to its
right, 764 (89) 28 pixels above 765 and 763 (119) 24 pixels to 89's left, all four on one link. Episode 6 does not
use them (ROOST, which takes TORM's ground enemies, draws none of sheet J's).

The animations play together as the gun fires: all four have launch frequency 70 and animate 2 (each launch runs
their nine frames once): 764 89 93 55 55 55 93 93 93 89, 763 119 91 17 17 17 91 91 91 119, 766 129 279 281 281 281
279 279 279 129; 765 shows 127 alone. 763 has no armour (it cannot be hit) and launches the gun's shell, enemy 762
(J 19, moving up the screen and to the left), every 70 ticks from its own place: so 119 draws nothing (it is empty),
91 and 17 the flame out of the muzzle beyond 89's left edge (91 a short one, 17 one reaching up the screen to the
left to row 2 of the picture), and 89's frames light it at the muzzle and light the barrel's lamps (93 orange, 55
white-hot), 129's frames heat the red slot in the mount (279, 281: from its top down). No other enemy, launched ones
included, shows J 17, 55, 91, 93, 279 or 281: frame models (frame j 93 field_gun_barrel_93 and so on).
The flash of 763 is drawn by the barrel's frame models 93 and 55, whole (the flame reaches across 119 from the
muzzle in 89), and 119 gets field_gun_flash, a blank model (one hidden speck): when the gun is destroyed, the game
leaves the slumped wreck of each linked enemy's model at its current frame (tyrian2.c leave_wreck), so a flame cut
into 119's own frame models would be left lying on the ground whenever the gun died while firing; without a model,
119 would show its flame as a flat sprite on the leaves (models.cfg's default, volume). The damaged look, J 273
(764's dgr, dlevel -1: what the barrel turns into when the gun is destroyed, while 765 and 766 leave the game's
slumped wrecks and 763 its blank one), burns the barrel: its plating torn and burnt along its top round the lamps,
embers in it, its lamps out, its muzzle's red tip dark. No sprite of these is another's pixels mirrored, turned or in
other ramps (the mortar of the same levels, G 165 167 203 205, is another drawing; twins.py over every sheet).

As the sprites and their 4x upscales draw it (columns and rows of the 72 x 56 picture the four make): a thick grey
barrel raised up the screen to the left at 45 degrees (its edges along columns - rows = 2.5 and 19.5, from its breech,
cut off level along row 34.5, up to its muzzle at column 25 of row 14), its section a rounded square lit along its top
(a dark seam along its middle, columns - rows = 12), a collar near its breech (rows 28-34), a dark ring before a short
nose (row 16), its muzzle's face dark with a red ring round the bore (columns 25-28 of rows 14-16); a red lamp on its
top at the seam's end (columns 34-35 of rows 24-26) and one on its upper right flank (columns 39-41 of row 23). Under
its breech, side by side: a thick neck curving down and back to the left (rows 33-41) into a rounded foot block
(columns 38-49 of rows 39-51), an upright block from under the breech down to the ground at the front (columns 48-56
of rows 33-51) with a red slot down its top (columns 53-54 of rows 42-50), and an arm curving from the breech's right
end down to the ground at the far right (columns 52-60 of rows 35-46), forked at its foot. The leaves round it (ramps
2 and 12, the black of their shadows) are the map's: TORM's, BOTANY's and BONUS's leaves (the 3D ground and its
plants show them); the model leaves them out.

Built for the game's slanted camera (20 degrees off straight down, from the bottom of the screen): the barrel is
turned along an axis raised ELEVATION degrees (its muzzle's top 22 pixels high), its section a rounded square (POWER 3,
squarer than the mortar's), lofted through its profile (the breech's rounded end, the collar and its groove, the body,
the ring's groove, the nose, the muzzle's face); its breech is cut off by a plane holding the line where its top meets
row 34.5 and leaning back under it (breech_plane(): seen from above or by the camera the barrel ends level along row
34.5, as the sprite's does; the cut faces down the screen and down, so neither sees it). The lamps are glossy lenses
in dark sockets on its surface, the seam a dark strip along its top, the muzzle's face a red ring round a dark bore,
the flame a licking teardrop along the axis, hottest at its root and in its middle (polish_mortar.py's, longer: the
sprite's flame is). The neck is swept along its path (polish_jaw_gun.swept, down into the ground), the arm and its
fork's second prong are round bars down into the ground (polish_machine_kit.smooth_tube), the foot and the upright
block bevelled prisms of the sprite's outlines, their tops sloping down to the front, the slot cut into the block with
an exact boolean, a glowing bar in it heating from its top down (polish_mortar.block's). The base's greys are painted
in bands of how squarely they face the light (polish_mortar.LIGHT and GREYS: the upper left, the game's sun), the
barrel's for a light from above (LIGHT_BARREL) a shade lighter (0x06-0x0c: the sprite's barrel is lit along its top,
and palette greys read darker in the game, on big smooth surfaces the more), all less metallic than the mortar's
(FINISHES), cut along smooth contours (polish_orb_red.band_split); the lamps, the slot, the ring and the flame glow in
bands of their own colours, one strength per shade (GLOW, 0.16-0.6: the game's bloom adds). The damaged state cuts the
burnt faces finer, presses the plating in and paints it with soot and embers where 273 differs from 89 (DAMAGE,
blurred into fields), the lamps and the seam gone, the ring dark. The whole gun is then cut along the sprites' edges
(x = 12, y = 0; polish_coral_manta.cut: the pieces keep the whole's shading across the cuts, their caps the parts'
dark inside), the barrel's parts leaned (LEAN 0.25, as the mortar's: their points moved down the screen by LEAN times
their height above LEAN_Z, the barrel's underside at its cut end, after the cut, so each lamp stays in its sprite's
piece: the camera then sees the raised barrel about where the sprites draw it, shifted up the screen as much as the
base (about 2-3 pixels at this height); the base, low, stays upright), each piece moved so its sprite's centre is its
origin. The barrel's piece takes all of the whole above y = 0, 119's box too (the flame). One whole per state (cold,
charge, fire, damaged): the frame models are its pieces as that state shows them. As polish_mortar.py's mortar, the
gun's family: its red lamps, ring, flame and slot, its base's greys and their light, the materials' kinds.

Where it stands: drawn at their origins (models.cfg origin), height=-4 on the sprite lines sets the base on the leaves
(as the mortar, the lens pad, the eye orb and the window block of TORM stand); the swept parts reach SKIRT below
z = 0 so no gap shows on uneven ground.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground (z = 0); the whole's
origin is the middle of 89's and 127's column at the row between them: column c is x = c + 0.5 - 36, row r is
y = 27.5 - r. The pieces' centres: 119 (-24, 14), 89 (0, 14), 127 (0, -14), 129 (24, -14).

Replaces wave3_m_ground.py (all that is left in it: greys(), wedge(), rect(), inside(), GUN_ORIGIN, gun_whole() with
@whole("gun", (72, 56)), gun_piece() and the three model("field_gun_...") lines, w.run(); with them the file has
nothing left to build: delete it) and wave3_ap_torm.py (only the gun's damaged barrel, kit.load("wave3_m_ground"):
delete it), and their pixels wave3_m_art.py's CANNON (read only by wave3_ap_torm.py; J93 and J281 there are read by
nothing) and wave3_ap_art.py's CANNON_DMG (read only by wave3_ap_torm.py).

The silhouette checks are top views: leaned, the barrel's top view lies lower than the sprite's (the whole's overlap 0.77
cold, unleaned 0.89; --lean 0 builds it unleaned); the game camera's view of the cold whole overlaps the sprites'
pixels 0.74 (unleaned 0.61; 0.80 at the full tan 20).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the whole
and of each piece against the gun's own pixels), --preview <prefix> (the whole's top and 3/4 views per state; --pieces
1 also each piece's), --only <name,...> (models to export), --states <cold,charge,fire,damaged>, --whole <prefix> (the
uncut wholes as GLBs, for looking at), --lean <k> (LEAN; 0: the barrel unleaned, as seen from above).
"""
import math
import os
import sys

import bmesh
import bpy
import mathutils.noise as noise
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k, smoothstep  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_coral_manta import cut  # noqa: E402  (caps keep their material when a later plane cuts them)
from polish_jaw_gun import swept, clip_below, SKIRT  # noqa: E402  (bars down into the ground, SKIRT 1.5)
from polish_mortar import (LIGHT, GREYS, CAP, FLAME_LICK, FLAME_BANDS, EMBERS, SOOT, TORN,  # noqa: E402
                           clip_plane, turned_axis, oriented_ball, densify, rounded_rect)


def PX(c):
    """The middle of the picture's column c."""
    return c + 0.5 - 36.0


def PY(r):
    """The middle of the picture's row r."""
    return 27.5 - r


def XE(c):
    """The left edge of column c."""
    return c - 36.0


def YE(r):
    """The top edge of row r."""
    return 28.0 - r


# The pieces: part -> (box (x0, x1, y0, y1) in the whole, its sprite's centre). The barrel's piece takes all of the
# whole above y = 0: 89's box and 119's (the flame).
BOXES = {"barrel": ((-80.0, 12.0, 0.0, 80.0), (0.0, 14.0)), "breech": ((-80.0, 12.0, -80.0, 0.0), (0.0, -14.0)),
         "mount": ((12.0, 80.0, -80.0, 0.0), (24.0, -14.0))}
# The states and the models they make: part -> (model, sprite).
MODELS = [
    ("cold", {"barrel": ("field_gun_barrel", 89), "breech": ("field_gun_breech", 127),
              "mount": ("field_gun_mount", 129)}),
    ("charge", {"barrel": ("field_gun_barrel_93", 93), "mount": ("field_gun_mount_279", 279)}),
    ("fire", {"barrel": ("field_gun_barrel_55", 55), "mount": ("field_gun_mount_281", 281)}),
    ("damaged", {"barrel": ("field_gun_barrel_damaged", 273)}),
]
FLASH = ("field_gun_flash", 119)
# The pictures the states' sprites make (for the silhouette checks): (119's place, 89's, 127's, 129's).
PICTURES = {"cold": (119, 89, 127, 129), "charge": (91, 93, 127, 279), "fire": (17, 55, 127, 281),
            "damaged": (119, 273, 127, 129)}
PLACES = ((0, 0), (24, 0), (24, 28), (48, 28))

# --- The barrel ----------------------------------------------------------------------------------------------------
# Its axis in plan: up the screen and to the left at 45 degrees (ALONG), W0 across it (ACROSS, to the upper right:
# x + y = W0 * sqrt 2); where its breech end lies along it (plan) and how high, its elevation.
ALONG = Vector((-1.0, 1.0, 0.0)).normalized()
ACROSS = Vector((1.0, 1.0, 0.0)).normalized()
W0 = 2.2
T_BREECH, Z_BREECH = -13.5, 6.1
ELEVATION = 22.0
POWER = 3.0                         # its section: a rounded square (|u|^p + |v|^p = 1), squarer than the mortar's
SEGMENTS = 48
# Its profile: (distance along the axis from the breech, radius): the breech's rounded end (cut away), the collar and
# its groove (rows 31-34), the body, the ring's groove (row 16), the nose, its rounded front edge and the muzzle's face.
R_BODY = 5.85
MUZZLE_S = 30.64                    # the muzzle's face
BARREL = [(0.0, 2.8), (0.3, 4.4), (0.75, 5.35), (1.3, 5.85), (2.84, 5.85), (3.09, 6.2), (7.24, 6.2), (7.49, 5.85),
          (7.74, 5.5), (8.34, 5.5), (8.59, 5.85), (14.0, 5.85), (20.0, 5.85), (25.44, 5.85), (25.69, 5.3), (26.19, 5.0),
          (26.59, 5.0), (26.84, 5.25), (29.54, 5.25), (30.09, 4.95), (30.49, 4.45), (30.64, 4.0)]
RING_GROOVE = (25.54, 26.84)        # the ring's groove before the nose (along the axis), painted dark
SEAM = (17.74, 25.34, 0.32)         # the seam along the top: from, to (along the axis), half-width (a dark strip)
# The barrel and what is on it lean down the screen (towards the camera) with their height above LEAN_Z (the barrel's
# underside where it is cut off): y moves by -LEAN * (z - LEAN_Z), after the pieces are cut (so each lamp stays in its
# sprite's piece), so that the game's slanted camera sees the raised barrel about where the sprite draws it (tan 20
# degrees, 0.36, would put it exactly there and turn its sides edge-on; the base, low, stays upright).
LEAN = 0.25
LEAN_Z = 3.0
# The breech is cut off by a plane leaning back under the barrel (facing down the screen and down, so neither the
# camera nor a view from above sees the cut): the sprite's barrel ends along row 34.5, level, where the neck and the
# arm come out from under it. The plane holds the line where the barrel's top meets y = YE(35) and leans back from it
# BREECH_LEAN degrees from upright (more than the camera's 20).
BREECH_Y, BREECH_LEAN = YE(35.0), 25.0
# The lamps: (plan point of the sprite's lamp (x, y), half-sizes (across, along), states' colours (rim, core) as
# (palette index, glow)).
# (palette index of the rim, of the core; they glow as GLOW says).
LAMPS = {
    "top": ((PX(34.9), PY(25.1)), (1.55, 1.25), {"cold": (0x73, 0x76), "charge": (0x77, 0x7b), "fire": (0x7b, 0x7f),
                                                 "damaged": None}),
    "flank": ((PX(40.0), PY(23.0)), (1.3, 1.6), {"cold": (0x73, 0x76), "charge": (0x77, 0x79), "fire": (0x79, 0x7d),
                                                 "damaged": None}),
}
# The muzzle's ring (radius, tube) and bore (radius), by state: (ring colour, glowing or not; bore colour, or None for
# dark).
RING_R, RING_TUBE, BORE_R = 2.35, 0.45, 1.8
MUZZLE = {"cold": ((0x74, True), None), "charge": ((0x7b, True), 0x79), "fire": ((0x7f, True), 0x7d),
          "damaged": ((0x71, False), None)}
# How strongly each red shade glows (one strength per palette index, so that the lamps, the ring, the flame, the slot
# and the embers share their materials): 0.16-0.6, the game's bloom adds.
GLOW = {0x71: 0.16, 0x72: 0.2, 0x73: 0.23, 0x74: 0.26, 0x75: 0.29, 0x76: 0.32, 0x77: 0.36, 0x78: 0.39, 0x79: 0.42,
        0x7a: 0.45, 0x7b: 0.47, 0x7c: 0.5, 0x7d: 0.53, 0x7e: 0.56, 0x7f: 0.6}
# The flames (charge: 93 with 91 beyond it, fire: 55 with 17): profile (distance out of the muzzle's face, radius).
FLAMES = {
    "charge": [(0.0, 2.5), (0.9, 3.2), (2.4, 3.4), (4.2, 3.0), (5.8, 2.1), (7.0, 1.0), (7.8, 0.05)],
    "fire": [(0.0, 2.7), (1.2, 3.6), (3.6, 4.0), (7.4, 3.7), (11.4, 2.9), (15.0, 1.8), (17.8, 0.75), (18.8, 0.05)],
}

# --- The base ------------------------------------------------------------------------------------------------------
# The neck from inside the breech down and back to the foot (x, y, z of its top's middle line), its half-width and how
# far its top stands over that line.
NECK = [(PX(46.4), PY(31.6), 6.6), (PX(46.6), PY(34.6), 7.0), (PX(45.8), PY(37.4), 6.7), (PX(44.4), PY(39.8), 5.8),
        (PX(43.2), PY(41.4), 4.6)]
NECK_HALF, NECK_TOP, NECK_POWER = 3.3, 1.6, 2.4
# The arm from the breech's right down to the ground (x, y, z, radius), forked at its foot: its two prongs.
ARM = [(PX(51.6), PY(32.8), 6.6, 1.9), (PX(54.4), PY(35.6), 6.2, 1.8), (PX(56.1), PY(37.7), 5.5, 1.7),
       (PX(57.3), PY(39.6), 4.5, 1.5), (PX(57.5), PY(41.6), 3.3, 1.2), (PX(57.2), PY(43.7), 1.7, 1.0),
       (PX(57.0), PY(45.6), -0.6, 0.9)]
PRONG = [(PX(57.8), PY(39.6), 4.4, 1.1), (PX(59.1), PY(41.5), 3.2, 1.0), (PX(59.7), PY(43.6), 1.6, 0.9),
         (PX(59.7), PY(45.6), -0.6, 0.8)]
# The upright block from under the breech's right down to the ground at the front (its plan, columns and rows of the
# picture; its top's height at the back and the front; bevel), the slot down its top (x0, x1, y0, y1, depth) and the
# glowing bar in it (inset, how far under the block's top), its heat along it by state (from the slot's bottom end, 0,
# to its top end, 1: how far it spreads, then (lowest value, palette index, glow)).
BLOCK = ([(48.4, 33.6), (48.0, 37.0), (49.6, 40.2), (49.9, 42.4), (49.9, 47.8), (50.6, 50.4), (52.4, 51.2),
          (54.6, 51.0), (56.0, 49.6), (56.2, 44.0), (55.8, 39.6), (53.8, 35.6), (51.4, 33.4)], 8.0, 5.4, 1.0)
SLOT = (XE(52.9), XE(55.05), YE(50.7), YE(41.8), 1.15)
BAR_INSET, BAR_DOWN = 0.22, 0.3
HOT_AT = 0.82                       # hottest near its top end (the sprites heat it from there down)
SLOT_HEAT = {
    "cold": (0.3, [(-9.0, 0x71), (0.2, 0x72), (0.4, 0x73), (0.6, 0x74), (0.78, 0x75), (0.92, 0x7a)]),
    "charge": (0.42, [(-9.0, 0x72), (0.2, 0x74), (0.4, 0x76), (0.6, 0x78), (0.78, 0x7a), (0.92, 0x7f)]),
    "fire": (0.62, [(-9.0, 0x72), (0.2, 0x75), (0.4, 0x78), (0.6, 0x7a), (0.78, 0x7d), (0.92, 0x7f)]),
}
SLOT_HEAT["damaged"] = SLOT_HEAT["cold"]
# The foot block's plan (columns and rows), its height at the back and the front, its bevel.
FOOT = ([(40.2, 40.4), (42.2, 39.4), (45.4, 39.4), (47.8, 40.3), (49.8, 42.0), (50.0, 48.4), (48.8, 50.6),
         (46.4, 51.6), (43.6, 51.6), (41.2, 50.0), (39.2, 47.4), (39.0, 43.0)], 5.0, 4.3, 0.65)
# The greys: the barrel's painted for a light from above (a little from the upper left, as the sprite's lit ridge along
# its upper left edge), a shade lighter than polish_mortar.GREYS and less metallic (palette greys read darker in the
# game, on big smooth surfaces the more); the base's as the mortar's hand (polish_mortar.LIGHT and GREYS).
LIGHT_BARREL = Vector((-0.2, 0.1, 1.0)).normalized()
GREYS_BARREL = [(-9.0, 0x06), (0.3, 0x08), (0.68, 0x0a), (0.88, 0x0c)]
# The finishes (metallic, roughness): the greys', the dark parts' (sockets, bore, slot), the soot's.
FINISHES = {"grey": (0.3, 0.38), "dark": (0.2, 0.6), "soot": (0.25, 0.7)}

# The damaged look's pixels where they differ from the intact sprites (273 from 89, in the picture's rows and columns:
# "column:intact>damaged"): the barrel's plating burnt and torn along its top round its lamps, embers in it, the
# muzzle's red tip dark.
DAMAGE = """
14 27:75>71 28:74>71
15 25:74>01 26:76>01 27:72>01
16 25:73>01 27:07>04 28:09>07
17 26:04>02 27:06>01 28:05>01 34:09>08
18 26:02>01 27:05>01 29:07>04 30:07>05 33:09>07 34:08>05 35:07>06
19 26:04>02 28:07>04 29:06>04 30:05>02 31:04>02 32:05>03 33:07>03 34:09>05 35:08>05
20 26:05>03 27:07>05 29:05>06 30:05>01 31:05>01 32:04>01 33:05>02 34:07>03 35:09>07 36:08>07
21 26:08>05 27:06>04 28:05>04 29:05>08 30:05>03 31:05>73 32:05>71 33:04>70 34:05>04 35:07>04 36:09>08 38:06>05 39:06>05
22 26:05>02 27:07>04 28:06>03 29:05>06 30:05>09 31:05>01 32:05>74 33:05>71 34:04>71 35:05>03 36:07>06 37:09>08 38:04>01 39:02>70 40:03>02
23 27:09>08 28:08>07 29:06>04 30:05>02 32:05>72 33:05>73 34:05>01 35:02>72 37:07>06 38:07>02 39:74>73 40:76>71 41:73>01
24 27:01>70 29:07>06 30:06>03 31:05>06 32:05>02 33:05>01 34:02>72 35:73>72 36:01>73 37:05>02 38:07>01 39:08>04 40:07>06
25 29:08>07 30:07>04 31:06>07 32:05>03 33:02>70 34:74>70 35:76>01 36:03>71 37:02>73 38:05>71 39:07>02 40:09>07 41:08>07
26 30:08>07 32:05>04 33:02>01 34:73>71 35:03>02 36:04>03 37:05>04 38:04>71 39:05>01 40:07>01 41:0a>07 42:08>07
27 36:05>06 38:05>02 39:04>71 40:05>01 41:09>06
"""


class Mats:
    """The materials, made once each: greys, dark parts and soot by palette index and finish (FINISHES), glowing reds
    by palette index (GLOW)."""

    def __init__(self):
        self.cache = {}

    def _make(self, kind, index):
        key = (kind, index)
        if key not in self.cache:
            if kind == "glow":
                pal = k.level_palette()
                self.cache[key] = k.material("fgun_%02x_glow" % index, palette=index, metallic=0.05, roughness=0.18,
                                             emission=pal[index], emission_strength=GLOW[index])
            else:
                metallic, roughness = FINISHES[kind]
                name = "fgun_%02x" % index + ("" if kind == "grey" else "_" + kind)
                self.cache[key] = k.material(name, palette=index, metallic=metallic, roughness=roughness)
        return self.cache[key]

    def grey(self, index):
        return self._make("grey", index)

    def dark(self, index):
        return self._make("dark", index)

    def soot(self, index):
        return self._make("soot", index)

    def glow(self, index):
        return self._make("glow", index)

    def get(self, index, glow=0.0, **_):
        """polish_mortar.Mats' call: a glowing red if glow is given, a grey else."""
        return self.glow(index) if glow > 0 else self.grey(index)


# --- Helpers -------------------------------------------------------------------------------------------------------

def paint_bands(obj, m, light, bands):
    """A grey part's faces in bands of how they face the light, cut along smooth contours (polish_mortar.paint_greys,
    with its own light and bands)."""
    obj.data.update()
    values = [v.normal.dot(light) for v in obj.data.vertices]
    band_split(obj, values, [(lowest, m.grey(index)) for lowest, index in bands])
    return obj


def plan_outline(points, iterations=2):
    """A plan given by the picture's columns and rows (counter-clockwise or not), its corners rounded, in x, y."""
    pts = [(XE(c), YE(r)) for c, r in points]
    area = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
    if area < 0:
        pts.reverse()
    return mk.chaikin(pts, iterations)


def barrel_frame():
    """The barrel's axis: its breech end's middle B, its direction D, across it SIDE (level, to the upper right) and UP
    (across it, upwards)."""
    c, s = math.cos(math.radians(ELEVATION)), math.sin(math.radians(ELEVATION))
    plan = ACROSS * W0 + ALONG * T_BREECH
    B = Vector((plan.x, plan.y, Z_BREECH))
    D = Vector((ALONG.x * c, ALONG.y * c, s))
    side = ACROSS.copy()
    up = side.cross(D).normalized()
    return B, D, side, up


def top_at(t):
    """The height of the barrel's top over its axis at plan distance t along it."""
    B, D, side, up = barrel_frame()
    s = (t - T_BREECH) / math.cos(math.radians(ELEVATION))
    return (B + D * s + up * R_BODY).z


def breech_plane():
    """The breech's cut: a point of it and its normal (facing down the screen and down)."""
    B, D, side, up = barrel_frame()
    # where the barrel's top crosses y = BREECH_Y at its left and its right side (plan points of the top's middle line
    # shifted across by the section's half-width)
    ends = []
    for u in (-0.85, 0.85):
        # the top's middle line, moved across: plan x + y = (W0 + u * R) * sqrt 2; on y = BREECH_Y
        w = W0 + u * R_BODY
        x = w * math.sqrt(2.0) - BREECH_Y
        t = (BREECH_Y - x) / math.sqrt(2.0)
        ends.append(Vector((x, BREECH_Y, top_at(t))))
    edge = (ends[1] - ends[0]).normalized()
    lean = math.radians(BREECH_LEAN)
    back = Vector((0.0, math.sin(lean), -math.cos(lean)))     # from the top edge down and back under the barrel
    normal = edge.cross(back).normalized()
    if normal.y > 0:
        normal = -normal
    return (ends[0] + ends[1]) / 2, normal


def barrel_profile(step=0.75):
    """BARREL with points added along its long runs (so that the burns and the bands have points to follow)."""
    out = [BARREL[0]]
    for (s0, r0), (s1, r1) in zip(BARREL, BARREL[1:]):
        n = max(1, int(math.ceil((s1 - s0) / step)))
        for i in range(1, n + 1):
            out.append((s0 + (s1 - s0) * i / n, r0 + (r1 - r0) * i / n))
    return out


def section(phi):
    """The barrel's section at angle phi (0: SIDE, 90: UP): its point (u, v) and outward normal (nu, nv)
    (polish_mortar.section, with this barrel's POWER)."""
    u, v = mk.superellipse_point(phi, POWER)
    nu = math.copysign(abs(u) ** (POWER - 1), u)
    nv = math.copysign(abs(v) ** (POWER - 1), v)
    n = math.hypot(nu, nv) or 1.0
    return u, v, nu / n, nv / n


def seam(m):
    """The seam along the barrel's top: a dark strip laid on it, from just in front of the top lamp to the ring's
    groove."""
    B, D, side, up = barrel_frame()
    s0, s1, half = SEAM
    verts, faces = [], []
    steps = 12
    for i in range(steps + 1):
        sv = s0 + (s1 - s0) * i / steps
        c = B + D * sv + up * (R_BODY + 0.03)           # (the seam runs along the body, R_BODY round)
        taper = min(1.0, (sv - s0) / 0.6, (s1 - sv) / 0.6)
        w = half * (0.4 + 0.6 * max(0.0, taper))
        verts += [c - side * w, c + side * w]
    for i in range(steps):
        faces.append((2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2))
    obj = k.mesh_object("seam", verts, faces, m.grey(0x02))
    k.recalc_normals(obj)
    if obj.data.polygons[0].normal.dot(up) < 0:
        obj.data.flip_normals()
    return k.smooth(obj, 30)


def barrel(m, state):
    B, D, side, up = barrel_frame()
    rings = []
    for s, r in barrel_profile():
        c = B + D * s
        ring = []
        for j in range(SEGMENTS):
            u, v, _, _ = section(2 * math.pi * j / SEGMENTS)
            ring.append(c + side * (u * r) + up * (v * r))
        rings.append(ring)
    obj = k.loft("barrel", rings, m.grey(0x07), start_point=B, end_point=B + D * MUZZLE_S)
    k.recalc_normals(obj)
    co, normal = breech_plane()
    clip_plane(obj, co, normal)
    burn = damage_fields() if state == "damaged" else None
    if burn:
        refine_burns(obj, burn)
        tear(obj, burn)
    paint_bands(obj, m, LIGHT_BARREL, GREYS_BARREL)

    # The seam and the ring's groove dark, the muzzle's face and the nose's rounded front edge dark.
    def dark(c, n):
        along = (c - B).dot(D)
        if RING_GROOVE[0] < along < RING_GROOVE[1] or along > MUZZLE_S - 0.6:
            return m.grey(0x02)
        return None
    mk.paint(obj, dark)
    if burn:
        scorch(obj, burn, m)
    return k.smooth(obj, 40)


def damage_fields():
    """The damaged sprite's soot (how much darker than the intact sprite, a lamp blown out the darkest) and embers (red
    where the intact sprite was grey or a lamp), blurred a little, as samplers at plan points (polish_mortar.py's, in
    this picture)."""
    import numpy as np
    soot = np.zeros((56, 72))
    ember = np.zeros((56, 72))
    for line in DAMAGE.strip().splitlines():
        row, *cells = line.split()
        r = int(row)
        for cell in cells:
            c, change = cell.split(":")
            a, b = (int(v, 16) for v in change.split(">"))
            c = int(c)
            if b >> 4 == 7:
                ember[r, c] = (b & 15) / 4.0 + 0.25
                soot[r, c] = 0.8
            elif a >> 4 == 7:
                soot[r, c] = 1.0
            else:
                soot[r, c] = max(0.0, min(1.0, ((a & 15) - (b & 15)) / 4.0))

    def blur(a, sigma=0.6):
        rad = 2
        kernel = np.exp(-0.5 * (np.arange(-rad, rad + 1) / sigma) ** 2)
        kernel /= kernel.sum()
        for axis in (0, 1):
            p = np.pad(a, [(rad, rad) if ax == axis else (0, 0) for ax in (0, 1)], mode="edge")
            a = sum(w * np.take(p, range(i, i + a.shape[axis]), axis=axis) for i, w in enumerate(kernel))
        return a
    soot, ember = blur(soot), blur(ember, 0.5)

    def at(a, x, y):
        u, v = x + 36.0 - 0.5, 27.5 - y
        c0, r0 = int(math.floor(u)), int(math.floor(v))
        fu, fv = u - c0, v - r0

        def px(r, c):
            return a[min(max(r, 0), 55), min(max(c, 0), 71)]
        return float((1 - fu) * (1 - fv) * px(r0, c0) + fu * (1 - fv) * px(r0, c0 + 1) + (1 - fu) * fv * px(r0 + 1, c0) +
                     fu * fv * px(r0 + 1, c0 + 1))
    return (lambda x, y: at(soot, x, y)), (lambda x, y: at(ember, x, y))


def refine_burns(obj, burn):
    """The faces the burns reach (on the barrel's upper side) cut in four, so that the soot, the embers and the torn
    plating follow the damaged sprite's pixels more finely than the barrel's rings."""
    soot, ember = burn
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.normal_update()
    edges = set()
    for f in bm.faces:
        c = f.calc_center_median()
        if f.normal.z > 0.0 and (soot(c.x, c.y) > 0.05 or ember(c.x, c.y) > 0.05):
            edges |= set(f.edges)
    if edges:
        bmesh.ops.subdivide_edges(bm, edges=sorted(edges, key=lambda e: e.index), cuts=1, use_grid_fill=True)
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    return obj


def tear(obj, burn):
    """The plating pressed in where it is burnt the most, raggedly (on the barrel's upper side, which the sprite
    shows)."""
    soot, _ = burn
    obj.data.update()
    for v in obj.data.vertices:
        if v.normal.z < 0.1:
            continue
        d = soot(v.co.x, v.co.y)
        if d > 0.5:
            rag = 0.65 + 0.35 * noise.noise(Vector((v.co.x * 0.9, v.co.y * 0.9, v.co.z * 0.9)))
            v.co -= v.normal * TORN * smoothstep(0.5, 1.0, d) * rag
    obj.data.update()


def scorch(obj, burn, m):
    """The burns painted on the barrel's upper side: soot darkening it, embers glowing in the torn plating."""
    soot, ember = burn

    def pick(c, n):
        if n.z < 0.05:
            return None
        e = ember(c.x, c.y)
        for lowest, index, _ in reversed(EMBERS):
            if e >= lowest:
                return m.glow(index)
        d = soot(c.x, c.y)
        for lowest, index in reversed(SOOT):
            if d >= lowest:
                return m.soot(index)
        return None
    mk.paint(obj, pick)


def surface_at(target, u_frac):
    """The barrel's surface point whose plan position is target (x, y), on the side of its section at u_frac (the
    section's u, -1 the lower left edge, 1 the upper right): (point, outward normal, along, across)."""
    B, D, side, up = barrel_frame()
    lo, hi = 0.0, math.pi
    for _ in range(50):
        mid = (lo + hi) / 2
        if section(mid)[0] > u_frac:
            lo = mid
        else:
            hi = mid
    u, v, nu, nv = section((lo + hi) / 2)
    off = side * (u * R_BODY) + up * (v * R_BODY)
    t_target = Vector((target[0], target[1], 0.0)).dot(ALONG)
    s = (t_target - T_BREECH - off.dot(ALONG)) / Vector((D.x, D.y, 0.0)).dot(ALONG)
    p = B + D * s + off
    n = (side * nu + up * nv).normalized()
    across = n.cross(D).normalized()
    return p, n, D, across


def lamp(name, spec, state, m):
    """A lamp on the barrel: a dark socket sunk into it, a lens in it (rim and core), glowing in the state's colours;
    blown out when damaged (the torn, burnt plating of tear() and scorch() is all that is left)."""
    target, (half_across, half_along), by_state = spec
    colours = by_state[state]
    if colours is None:
        return []
    across_axis = Vector((target[0], target[1], 0.0)).dot(ACROSS) - W0     # how far to the upper right of the axis
    p, n, along, across = surface_at(target, max(-0.97, min(0.97, across_axis / R_BODY)))
    frame = (across, along, n)
    parts = [oriented_ball(f"{name}_socket", p - n * 0.22, (half_across + 0.45, half_along + 0.4, 0.55), frame,
                           m.dark(0x01))]
    rim, core = colours
    parts.append(oriented_ball(f"{name}_lens", p + n * 0.02, (half_across, half_along, 0.42), frame, m.glow(rim)))
    parts.append(oriented_ball(f"{name}_core", p + n * 0.16, (half_across * 0.55, half_along * 0.55, 0.34), frame,
                               m.glow(core)))
    for obj in parts:
        k.smooth(obj, 80)
    return parts


def muzzle_face(state, m):
    """The muzzle's face: a red ring round the bore, the bore dark (or glowing as it fires)."""
    B, D, side, up = barrel_frame()
    c = B + D * MUZZLE_S
    (ring_index, ring_glows), bore = MUZZLE[state]
    verts, faces = [], []
    n_round, n_tube = 40, 10
    for i in range(n_round):
        a = 2 * math.pi * i / n_round
        radial = side * math.cos(a) + up * math.sin(a)
        for j in range(n_tube):
            b = 2 * math.pi * j / n_tube
            verts.append(c + radial * (RING_R + RING_TUBE * math.cos(b)) + D * (RING_TUBE * 0.75 * math.sin(b) - 0.12))
    for i in range(n_round):
        for j in range(n_tube):
            a0, a1 = i * n_tube + j, i * n_tube + (j + 1) % n_tube
            b0, b1 = ((i + 1) % n_round) * n_tube + j, ((i + 1) % n_round) * n_tube + (j + 1) % n_tube
            faces.append((a0, a1, b1, b0))
    ring = k.mesh_object("muzzle_ring", verts, faces, m.glow(ring_index) if ring_glows else m.soot(ring_index))
    k.recalc_normals(ring)
    k.smooth(ring, 80)
    bore_mat = m.dark(0x01) if bore is None else m.glow(bore)
    prof = [(-0.6, BORE_R), (0.06, BORE_R), (0.08, 0.01)]
    bore_obj = turned_axis("muzzle_bore", prof, c, D, side, up, bore_mat, 32)
    return [ring, bore_obj]


def flame(state, m):
    """The flame out of the muzzle: a teardrop along the barrel's axis, hottest at its root and in its middle as the
    camera sees it, red at its edges (polish_mortar.flame, along this barrel)."""
    B, D, side, up = barrel_frame()
    c = B + D * (MUZZLE_S + 0.05)
    profile = FLAMES[state]
    dense = []
    for (t0, r0), (t1, r1) in zip(profile, profile[1:]):
        n = max(1, int(math.ceil((t1 - t0) / 0.6)))
        dense += [(t0 + (t1 - t0) * i / n, r0 + (r1 - r0) * i / n) for i in range(n)]
    dense.append(profile[-1])
    obj = turned_axis("flame", dense, c, D, side, up, None, 32)
    length = profile[-1][0]
    obj.data.update()
    for v in obj.data.vertices:
        along = (v.co - c).dot(D)
        radial = v.co - (c + D * along)
        if radial.length < 1e-4 or along <= 0.05:
            continue
        lick = noise.noise(Vector((v.co.x * 0.45, v.co.y * 0.45, v.co.z * 0.45)) + Vector((3.1, 1.7, 0.4)))
        v.co += radial.normalized() * (FLAME_LICK * smoothstep(0.0, 0.25 * length, along) * lick * radial.length)
    obj.data.update()
    view = Vector((0.0, -math.sin(math.radians(20.0)), math.cos(math.radians(20.0))))
    values = []
    for v in obj.data.vertices:
        along = min(1.0, max(0.0, (v.co - c).dot(D) / length))
        facing = max(0.0, v.normal.dot(view))
        values.append(0.55 * (1.0 - along) ** 0.8 + 0.5 * facing ** 1.5)
    band_split(obj, values, [(lowest, m.glow(index)) for lowest, index, _ in FLAME_BANDS])
    k.recalc_normals(obj)
    return k.smooth(obj, 80)


# --- The base ------------------------------------------------------------------------------------------------------

def greys(obj, m):
    return paint_bands(obj, m, LIGHT, GREYS)


def neck(m):
    obj = swept("neck", [Vector(p) for p in NECK], NECK_HALF, NECK_TOP, m.grey(0x07), power=NECK_POWER, segments=20)
    return k.smooth(greys(obj, m), 50)


def arm(m):
    parts = []
    for name, path in (("arm", ARM), ("prong", PRONG)):
        obj = mk.smooth_tube(name, path, m.grey(0x07), segments=12, iterations=2)
        clip_below(obj, -SKIRT)
        k.recalc_normals(obj)
        parts.append(k.smooth(greys(obj, m), 60))
    return parts


def block(state, m):
    """The upright block: a rounded prism with a top sloping down to the front, bevelled and painted; the slot cut down
    it (its walls dark) and the glowing bar in it (polish_mortar.block's)."""
    outline, back, front, bev = BLOCK
    plan = plan_outline(outline)
    x0, x1 = min(p[0] for p in plan), max(p[0] for p in plan)
    y0, y1 = min(p[1] for p in plan), max(p[1] for p in plan)
    top = mk.plane((x0, y1, back), (x1, y1, back), (x0, y0, front))
    body = mk.wedge("block", plan, -SKIRT, top, m.grey(0x07))
    mk.bevel(body, bev, 3, 35)
    greys(body, m)
    sx0, sx1, sy0, sy1, depth = SLOT
    dark = m.dark(0x01)
    cutter = mk.wedge("slot_cut", rounded_rect(sx0, sx1, sy0, sy1, 0.95), -1.0, lambda x, y: top(x, y) + 2.0, dark,
                      bottom=lambda x, y: top(x, y) - depth)
    mk.boolean(body, cutter, "DIFFERENCE")
    k.recalc_normals(body)
    k.smooth(body, 35)
    bx0, bx1, by0, by1 = sx0 + BAR_INSET, sx1 - BAR_INSET, sy0 + BAR_INSET, sy1 - BAR_INSET
    bar = mk.wedge("slot_bar", densify(rounded_rect(bx0, bx1, by0, by1, 0.7), 0.35), -1.0,
                   lambda x, y: top(x, y) - BAR_DOWN, None, bottom=lambda x, y: top(x, y) - depth - 0.3)
    mk.bevel(bar, 0.3, 2, 35)
    bar.data.update()
    spread, bands = SLOT_HEAT[state]
    heat = [math.exp(-(((v.co.y - by0) / (by1 - by0) - HOT_AT) / spread) ** 2) for v in bar.data.vertices]
    band_split(bar, heat, [(lowest, m.glow(index)) for lowest, index in bands])
    k.recalc_normals(bar)
    k.smooth(bar, 35)
    return [body, bar]


def foot(m):
    outline, back, front, bev = FOOT
    plan = plan_outline(outline, 1)
    x0, x1 = min(p[0] for p in plan), max(p[0] for p in plan)
    y0, y1 = min(p[1] for p in plan), max(p[1] for p in plan)
    top = mk.plane((x0, y1, back), (x1, y1, back), (x0, y0, front))
    body = mk.wedge("foot", plan, -SKIRT, top, m.grey(0x07))
    mk.bevel(body, bev, 3, 35)
    greys(body, m)
    return k.smooth(body, 35)


# --- The whole -----------------------------------------------------------------------------------------------------

def build_whole(state):
    k.reset()
    m = Mats()
    parts = [barrel(m, state)]
    if state != "damaged":
        parts.append(seam(m))
    for name, spec in LAMPS.items():
        parts += lamp(name, spec, state, m)
    parts += muzzle_face(state, m)
    if state in FLAMES:
        parts.append(flame(state, m))
    for obj in parts:
        obj["lean"] = True              # the barrel's parts (see LEAN)
    parts += [neck(m), foot(m)] + arm(m) + block(state, m)
    for obj in parts:
        k.recalc_normals(obj)
    return parts, m


def lean(obj):
    """Leans a part of the barrel (see LEAN): its points moved down the screen with their height, its normals with
    them."""
    mesh = obj.data
    normals = [Vector(c.vector) for c in mesh.corner_normals]
    for v in mesh.vertices:
        v.co.y -= LEAN * (v.co.z - LEAN_Z)
    mesh.update()
    mesh.normals_split_custom_set([tuple(Vector((n.x, n.y, n.z + LEAN * n.y)).normalized()) for n in normals])
    return obj


def leaned_whole(whole):
    """The whole as it is exported: copies of the barrel's parts leaned, with the base's parts."""
    out = []
    for src in whole:
        if src.get("lean"):
            obj = src.copy()
            obj.data = src.data.copy()
            bpy.context.scene.collection.objects.link(obj)
            out.append(lean(obj))
        else:
            out.append(src)
    return out


def own_mask(sheet, sprites):
    """The gun's own pixels in the 72 x 56 picture the four sprites make: its greys and reds (ramps 0 and 7) joined side
    by side, the biggest group of them and the flame's (the leaves' black specks of shadow round it left out)."""
    from sprite_profile import sprite_indices
    pic = [[None] * 72 for _ in range(56)]
    for sprite, (c0, r0) in zip(sprites, PLACES):
        idx = sprite_indices(sheet, sprite)
        for r in range(28):
            for c in range(24):
                pic[r0 + r][c0 + c] = idx[r][c]
    own = [[pic[r][c] is not None and pic[r][c] >> 4 in (0, 7) for c in range(72)] for r in range(56)]
    seen = [[False] * 72 for _ in range(56)]
    groups = []
    for r0 in range(56):
        for c0 in range(72):
            if own[r0][c0] and not seen[r0][c0]:
                group, stack = [], [(r0, c0)]
                seen[r0][c0] = True
                while stack:
                    r, c = stack.pop()
                    group.append((r, c))
                    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        rr, cc = r + dr, c + dc
                        if 0 <= rr < 56 and 0 <= cc < 72 and own[rr][cc] and not seen[rr][cc]:
                            seen[rr][cc] = True
                            stack.append((rr, cc))
                groups.append(group)
    groups.sort(key=len, reverse=True)
    mask = [[False] * 72 for _ in range(56)]
    for r, c in groups[0] if groups else []:
        mask[r][c] = True
    return mask


def piece_mask(mask, part):
    """The part of the picture's mask in the piece's sprite (the barrel's: 119's and 89's, side by side)."""
    if part == "barrel":
        return [row[0:48] for row in mask[0:28]]
    c0, r0 = {"breech": (24, 28), "mount": (48, 28)}[part]
    return [row[c0:c0 + 24] for row in mask[r0:r0 + 28]]


def flash_blank(out, options):
    """119's model: nothing to see, one speck hidden under the ground (a model needs a triangle)."""
    k.reset()
    m = Mats()
    obj = k.mesh_object("field_gun_flash", [(0.0, 0.0, -2.0), (0.02, 0.0, -2.0), (0.0, 0.02, -2.0)], [(0, 1, 2)],
                        m.dark(0x01))
    triangulate([obj])
    mk.report(FLASH[0], [obj], os.path.join(out, FLASH[0] + ".glb"))


def export_state(state, pieces, options, sheet, out):
    only = options["only"].split(",") if "only" in options else None
    wanted = [(part, name, sprite) for part, (name, sprite) in pieces.items() if not only or name in only]
    if not wanted and "whole" not in options and "preview" not in options:
        return
    whole, m = build_whole(state)
    triangulate(whole)
    low, high = mk.bounds(whole)
    print("== whole, %s: %d triangles, x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (
        state, mk.triangles(whole), low.x, high.x, low.y, high.y, low.z, high.z))
    mask = own_mask(sheet, PICTURES[state]) if sheet else None
    shown = leaned_whole(whole)
    if sheet:
        mk.compare("whole, %s" % state, mk.coverage(shown, 72, 56), mask)
    bpy.context.scene.view_settings.view_transform = "Standard"
    if "preview" in options:
        mk.preview(options["preview"] + "field_gun_whole_" + state, shown, size=(72, 56), scale=8, distance=2.0)
    if "whole" in options:
        mk.export(shown, options["whole"] + state + ".glb")
    for obj in shown:
        if obj not in whole:
            bpy.data.objects.remove(obj)
    cap = m.grey(CAP)
    for part, name, sprite in wanted:
        box, centre = BOXES[part]
        parts = []
        for src in whole:
            p = cut(src, box, cap)
            if p is not None:
                parts.append(lean(p) if src.get("lean") else p)
        drop_unused(parts)
        mk.transform(parts, Matrix.Translation((-centre[0], -centre[1], 0)))
        bpy.context.view_layer.update()
        triangulate(parts)
        parts = [join(parts, name)]
        parts[0].data.name = name
        for src in whole:
            src.hide_render = True
        if sheet:
            w = 48 if part == "barrel" else 24
            mk.compare("%s (J %d, the gun's own pixels)" % (name, sprite),
                       mk.coverage(parts, w, 28, centre=(-12.0, 0.0) if part == "barrel" else (0.0, 0.0)),
                       piece_mask(mask, part))
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options and options.get("pieces") == "1":
            mk.preview(options["preview"] + name, parts, size=(48, 28) if part == "barrel" else (24, 28),
                       centre=(-12.0, 0.0) if part == "barrel" else (0.0, 0.0))
        for obj in parts:
            bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False


def build():
    options = k.args()
    out = mk.outdir(options)
    sheet = None
    if "check" in options:
        sheets = options["check"]
        sheet = os.path.join(sheets, "enemy_J.png") if os.path.isdir(sheets) else sheets
        sys.path.insert(0, os.path.join(HERE, "..", ".."))
    states = options["states"].split(",") if "states" in options else [s for s, _ in MODELS]
    global LEAN
    LEAN = float(options.get("lean", LEAN))
    for state, pieces in MODELS:
        if state in states:
            export_state(state, pieces, options, sheet, out)
    only = options["only"].split(",") if "only" in options else None
    if not only or FLASH[0] in only:
        flash_blank(out, options)


if __name__ == "__main__":
    build()
