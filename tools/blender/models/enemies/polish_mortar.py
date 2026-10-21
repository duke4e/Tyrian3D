"""The mortar of TORM, BOTANY A and BONUS (episode 2): sheet G sprites 165 and 167 above 203 and 205 (2x2 each: one
48 x 56 picture; enemies 768, 769, 770 and 771, ground layer), polished (2026-10-21; it replaces wave3_r.py's
mortar_whole() and mortar_piece(), a lathed barrel on a tube neck with rounded boxes, and wave3_ap_mortar.py's damaged
look, built from it). models.cfg: model mortar_breech / mortar_muzzle / mortar_mount / mortar_leaves and the frame and
damaged models below, enemies/mortar_*.glb origin; sprite g 165 mortar_breech yaw=0 height=-4 and so on.

The levels put the four as a square (TORM's events at 49, 1981, 2233, 2681, 4109, BOTANY A's at 945, 1281, 1729, 1841,
2485, BONUS's at 1141, 1253, 1729, 1813, 2597, 2653): 770 (203) at (x, y), 771 (205) 24 pixels to its right, 768 (165)
and 769 (167) 28 pixels above them, all four on one link. Episode 6 takes TORM's and BOTANY A's waves without their
ground enemies, so no mortar there.

The animations play together as the mortar fires: 768 165 241 281 281 281 241 241 241 165, 769 167 243 283 ..., 770
203 279 245 ..., 771 205 alone. 241 and 281 light the red lamp on the barrel's flank (165: 0x73-0x76; 241 orange, 0x77
-0x7a; 281 white-hot, 0x7d-0x7f); 243 and 283 blow a flame out of the muzzle up the screen to the right (243 a short
one, 283 one reaching the sprite's corner) and light the lamp on the barrel's top and the muzzle's red ring; 279 and
245 heat the red slot in the mount (to yellow and white at its top). No other enemy shows G 241, 243, 245, 279, 281 or
283: frame models (frame g 241 mortar_breech_241 and so on). The damaged looks, G 169 and 207 (768's and 769's dgr,
dlevel -1: what 768 and 769 turn into when the mortar is destroyed, while 770 and 771 leave the game's slumped wrecks
of their models), burn the barrel: the flank's lamp blown out in a torn black hole with embers (169, its lower right),
the top lamp's plating torn and burnt with embers round it and the muzzle's ring dark (207). No sprite of these is
another's pixels mirrored, turned or in other ramps (the field gun, J 89 127 129, is another drawing).

As the sprites and their 4x upscales draw it (columns and rows of the 48 x 56 picture): a thick grey barrel raised up
the screen and to the right at 45 degrees (its edges along columns + rows = 43 and 58, from row 34 up to its muzzle at
column 34 of row 13), lit along its upper left; a collar round its lower end (rows 28-31), a dark seam (rows 16-21)
before a narrower nose with a red ring round the muzzle (columns 33-36 of rows 14-16); a red lamp in a socket on its
upper left flank (columns 20-22 of row 23) and one on its top (columns 26-27 of rows 24-26). From under its lower end a
thick neck curves down to the left (rows 33-41) into a heavy upright block (columns 5-10 of rows 39-50) with a red slot
along it (columns 7-8 of rows 42-50), a thumb-like claw beside it down to the left (columns 1-8 of rows 36-46), a fist
of knuckles in front of it (columns 12-21 of rows 41-51) and a thin hooked claw from under the barrel down over the
fist to the right (columns 15-22 of rows 33-46): a mechanical hand holding the gun up. The leaves round it (ramps 2 and
12, the black of their shadows) are the map's: TORM's, BOTANY's and BONUS's leaves (the 3D ground and its plants show
them); the model leaves them out, so 205 holds only the barrel's lower right edge reaching into it.

Built for the game's slanted camera (20 degrees off straight down, from the bottom of the screen): the barrel is turned
along an axis raised ELEVATION degrees (its muzzle up to 22 pixels high), its section a rounded square, and lofted
through its profile (breech, collar, body, the seam's groove, the nose, the muzzle's face); its breech is cut off
under the collar by a plane leaning back under it (BREECH_CUT: seen from above or by the camera the barrel ends level
along row 34.5, as the sprite's does), and a palm under it closes the cut and holds the neck and the hook. The lamps are
glossy lenses in dark sockets on its surface, the muzzle's face a red ring round a dark bore, the flame a licking
teardrop along the axis, hottest at its root and in its middle. The neck, the thumb and the hook are swept along their
paths (polish_jaw_gun.py's swept bars, down into the ground), the palm, the block and the fist are bevelled prisms of
the sprite's outlines (polish_machine_kit), the slot cut into the block with an exact boolean, a glowing bar in it, the
knuckles turned. Every grey part is painted in bands of how squarely it faces the light (LIGHT: the upper left, where
the sprite and the game's sun light it), cut along smooth contours (polish_orb_red.band_split); the lamps, the slot,
the ring and the flame glow in bands of their own colours (0.16-0.6: the game's bloom adds). The damaged state presses
the plating in and paints it with soot and embers where 169 and 207 differ from 165 and 167 (DAMAGE, blurred into
fields), the lamps gone, the ring dark. The whole mortar is then cut along the sprites' edges (x = 0, y = 0;
polish_coral_manta.cut: the pieces keep the whole's shading across the cuts, their caps the parts' dark inside), the
barrel's parts leaned (LEAN: their points moved down the screen by a quarter of their height above the breech, after
the cut, so each lamp stays in its sprite's piece: the camera then sees the raised barrel about where the sprites draw
it; the hand, low, stays upright), each piece moved so its sprite's centre is its origin. One whole per state (cold,
charge, fire, damaged): the frame models are its pieces as that state shows them.

Where it stands: drawn at their origins (models.cfg origin), height=-4 on the sprite lines sets the hand on the leaves
(as the jaw guns, the lens pad and the window block of TORM stand); the swept parts reach SKIRT below z = 0 so no gap
shows on uneven ground.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground (z = 0); the whole's
origin is the corner where the four sprites meet: column c is x = c + 0.5 - 24, row r is y = 27.5 - r. The pieces'
centres: 165 (-12, 14), 167 (12, 14), 203 (-12, -14), 205 (12, -14).

Replaces wave3_r.py's mortar (all that is left in it: MORTAR_ORIGIN, mpx(), mpy(), frame_along(), mortar_whole(),
mortar_piece() and the four r.model("mortar_...") lines; with them the file has nothing left to build: delete it) and
wave3_ap_mortar.py (only the mortar's damaged look, kit.load("wave3_r"): delete it), and their pixels wave3_r_art.py's
MORTAR and MORTAR_FIRE and wave3_ap_art.py's MORTAR_DMG (nothing else reads them).

The silhouette checks are top views: leaned, the barrel's top view lies lower than the sprite's (the whole's overlap
0.81, unleaned 0.89; --lean 0 builds it unleaned).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the whole
and of each piece against the mortar's own pixels), --preview <prefix> (the whole's top and 3/4 views per state;
--pieces 1 also each piece's), --only <name,...> (models to export), --states <cold,charge,fire,damaged>, --whole
<prefix> (the uncut wholes as GLBs, for looking at), --lean <k> (LEAN; 0: the barrel unleaned, as seen from above).
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
from polish_orb_red import band_split, icosphere  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_coral_manta import cut  # noqa: E402  (caps keep their material when a later plane cuts them)
from polish_jaw_gun import swept, clip_below, SKIRT  # noqa: E402  (bars down into the ground, SKIRT 1.5)


def PX(c):
    """The middle of the picture's column c."""
    return c + 0.5 - 24.0


def PY(r):
    """The middle of the picture's row r."""
    return 27.5 - r


def XE(c):
    """The left edge of column c."""
    return c - 24.0


def YE(r):
    """The top edge of row r."""
    return 28.0 - r


# The pieces: (part, sprite of the cold mortar, box (x0, x1, y0, y1) in the whole).
BOXES = {"breech": (-24.0, 0.0, 0.0, 28.0), "muzzle": (0.0, 24.0, 0.0, 28.0), "mount": (-24.0, 0.0, -28.0, 0.0),
         "leaves": (0.0, 24.0, -28.0, 0.0)}
# The states and the models they make: part -> (model, sprite).
MODELS = [
    ("cold", {"breech": ("mortar_breech", 165), "muzzle": ("mortar_muzzle", 167), "mount": ("mortar_mount", 203),
              "leaves": ("mortar_leaves", 205)}),
    ("charge", {"breech": ("mortar_breech_241", 241), "muzzle": ("mortar_muzzle_243", 243),
                "mount": ("mortar_mount_279", 279)}),
    ("fire", {"breech": ("mortar_breech_281", 281), "muzzle": ("mortar_muzzle_283", 283),
              "mount": ("mortar_mount_245", 245)}),
    ("damaged", {"breech": ("mortar_breech_damaged", 169), "muzzle": ("mortar_muzzle_damaged", 207)}),
]
# The pictures the states' sprites make (for the silhouette checks): (top left, top right, bottom left, bottom right).
PICTURES = {"cold": (165, 167, 203, 205), "charge": (241, 243, 279, 205), "fire": (281, 283, 245, 205),
            "damaged": (169, 207, 203, 205)}

# --- The barrel ----------------------------------------------------------------------------------------------------
# Its axis in plan: through AXIS0, up the screen and to the right at 45 degrees (the sprite's edges: columns + rows =
# 43 and 58, so x - y = -0.5 in the middle); where its breech end lies along it (plan) and how high, its elevation.
AXIS0 = Vector((-0.5, 0.5))
T_BREECH, Z_BREECH = -11.6, 6.6
ELEVATION = 22.0
POWER = 2.5                         # its section: a rounded square (|u|^p + |v|^p = 1)
SEGMENTS = 40
# Its profile: (distance along the axis from the breech, radius): the breech's rounded end, the collar (rows 28-31),
# the body, the step into the seam's groove (rows 16-21), the nose, its rounded front edge and the muzzle's face.
R_BODY = 5.8
BARREL = [(0.0, 2.6), (0.25, 4.3), (0.7, 5.3), (1.3, 5.75), (1.55, 5.8), (1.75, 6.3), (3.05, 6.3), (3.25, 5.8),
          (8.0, 5.8), (13.0, 5.8), (18.0, 5.8), (23.6, 5.8), (23.85, 5.3), (24.3, 4.8), (24.7, 4.8), (24.95, 5.0),
          (28.9, 5.0), (29.55, 4.7), (30.0, 4.15), (30.2, 3.7)]
MUZZLE_S = 30.2                     # the muzzle's face
# The barrel and what is on it lean down the screen (towards the camera) with their height above the breech: y moves
# by -LEAN * (z - Z_BREECH), after the pieces are cut (so each lamp stays in its sprite's piece), so that the game's
# slanted camera sees the raised barrel about where the sprite draws it (tan 20 degrees, 0.36, would put it exactly
# there and turn its side faces edge-on; the hand, low, stays upright).
LEAN = 0.25
# The breech end, under the collar, is cut off by a plane leaning back under it (facing down the screen and down, so
# neither the camera nor a view from above sees the cut): the sprite's barrel ends along row 34.5, level, where the
# neck and the hook come out from under it. The plane: a point of it (y, z) and how far it leans from upright.
BREECH_CUT = (YE(34.6) + 3.05, 7.25, 29.8)
# The lamps: (plan point of the sprite's lamp (x, y), half-sizes (across, along), states' colours (rim, core) as
# (palette index, glow)).
LAMPS = {
    "flank": ((PX(21.0), PY(23.0)), (2.05, 1.05), {"cold": ((0x73, 0.22), (0x76, 0.3)), "charge": ((0x77, 0.34),
                                                                                                  (0x7a, 0.44)),
                                                   "fire": ((0x7a, 0.44), (0x7e, 0.58)),
                                                   "damaged": None}),
    "top": ((PX(26.6), PY(25.0)), (1.9, 1.0), {"cold": ((0x73, 0.22), (0x76, 0.3)), "charge": ((0x79, 0.4),
                                                                                                (0x7d, 0.52)),
                                                 "fire": ((0x7c, 0.5), (0x7f, 0.6)), "damaged": None}),
}
# The muzzle's ring (radius, tube) and bore (radius), by state: (ring colour, bore colour or None for dark).
RING_R, RING_TUBE, BORE_R = 2.95, 0.55, 2.3
MUZZLE = {"cold": ((0x74, 0.24), None), "charge": ((0x7b, 0.45), (0x79, 0.4)), "fire": ((0x7e, 0.56), (0x7d, 0.52)),
          "damaged": ((0x71, 0.0), None)}
# The flames (charge: 243, fire: 283): profile (distance out of the muzzle's face, radius) and how far it bends up;
# its heat in bands (lowest value, palette index, glow).
FLAMES = {
    "charge": [(0.0, 2.4), (0.9, 3.1), (2.4, 3.3), (4.4, 2.9), (6.3, 2.0), (7.8, 1.0), (8.8, 0.05)],
    "fire": [(0.0, 2.6), (1.2, 3.5), (3.5, 3.9), (7.0, 3.6), (10.6, 2.8), (14.0, 1.7), (16.5, 0.7), (17.4, 0.05)],
}
FLAME_LICK = 0.32                   # how much its surface licks in and out (a share of its radius)
FLAME_BANDS = [(-9.0, 0x74, 0.3), (0.35, 0x77, 0.38), (0.55, 0x7a, 0.45), (0.74, 0x7d, 0.52), (0.88, 0x7f, 0.6)]

# --- The hand ------------------------------------------------------------------------------------------------------
# The neck from under the breech down to the block (x, y, z of its top's middle line), its half-width and how far its
# top stands over that line; the thumb (half-widths along it); the hook (x, y, z, radius).
NECK = [(PX(15.6), PY(32.4), 5.2), (PX(12.4), PY(35.0), 5.7), (PX(9.6), PY(37.9), 5.9), (PX(8.2), PY(40.6), 5.6)]
NECK_HALF, NECK_TOP = 3.1, 1.7
THUMB = [(PX(7.4), PY(35.4), 4.6), (PX(4.9), PY(37.8), 4.1), (PX(2.9), PY(40.8), 3.2), (PX(1.8), PY(43.8), 1.8),
         (PX(1.6), PY(45.9), 0.6)]
THUMB_HALF, THUMB_TOP = (1.6, 1.7), 1.1
HOOK = [(PX(16.4), PY(32.6), 3.6, 1.45), (PX(15.8), PY(35.6), 4.9, 1.4), (PX(15.9), PY(38.8), 5.8, 1.35),
        (PX(17.6), PY(41.0), 5.8, 1.3), (PX(20.0), PY(42.9), 4.5, 1.1), (PX(21.4), PY(45.0), 2.2, 0.85),
        (PX(21.8), PY(46.5), -0.6, 0.55)]
# The block (plan x0, x1, y0, y1; its top's height at the back and the front; bevel), the slot along it (x0, x1, y0,
# y1, depth) and the glowing bar in it (inset, how far under the block's top), its heat along it by state (from its
# bottom, 0, to its top end, 1: (lowest value, palette index, glow)).
# The palm under the barrel's breech, where the neck and the hook come out from under it (hidden under the barrel from
# above; it closes the cut-off breech's underside): its plan (columns and rows), its top (inside the barrel), bevel.
PALM = ([(13.2, 34.6), (19.0, 34.6), (22.8, 31.6), (22.6, 28.6), (16.5, 27.8), (13.4, 30.0)], 7.2, 0.9)
# The block's plan (columns and rows of the picture), its top's height at the back and the front, its bevel.
BLOCK = ([(4.9, 39.4), (4.5, 42.0), (4.5, 46.2), (5.6, 48.8), (6.6, 51.0), (9.4, 51.0), (11.0, 48.6), (11.4, 44.0),
          (11.4, 40.6), (10.6, 39.4)], 6.7, 5.7, 1.1)
SLOT = (XE(6.9), XE(9.0), YE(50.6), YE(41.8), 1.15)
BAR_INSET, BAR_DOWN = 0.22, 0.3
# its heat: hottest a third of the way down from its top end (HOT_AT along it), the more of it the hotter the state
# (how far the heat spreads, then the bands of it).
HOT_AT = 0.76
SLOT_HEAT = {
    "cold": (0.24, [(-9.0, 0x71, 0.16), (0.2, 0x72, 0.2), (0.4, 0x73, 0.23), (0.6, 0x75, 0.27), (0.78, 0x77, 0.31),
                    (0.92, 0x7a, 0.36)]),
    "charge": (0.36, [(-9.0, 0x73, 0.24), (0.2, 0x75, 0.29), (0.4, 0x77, 0.34), (0.6, 0x79, 0.4), (0.78, 0x7b, 0.45),
                      (0.92, 0x7d, 0.5)]),
    "fire": (0.52, [(-9.0, 0x75, 0.32), (0.2, 0x77, 0.38), (0.4, 0x7a, 0.44), (0.6, 0x7c, 0.5), (0.78, 0x7e, 0.55),
                    (0.92, 0x7f, 0.6)]),
}
SLOT_HEAT["damaged"] = SLOT_HEAT["cold"]
# The fist (plan x0, x1, y0, y1, height, bevel) and its knuckles (y, x0, x1, radius, height of their middle).
# The fist's plan (columns and rows), its height and bevel.
FIST = ([(11.6, 41.2), (13.4, 40.2), (17.6, 40.4), (20.0, 41.6), (21.2, 43.8), (21.2, 46.4), (19.8, 49.4),
         (17.6, 51.6), (13.0, 51.8), (11.7, 50.0), (11.3, 46.0)], 4.3, 1.2)
# its knuckles: (from (x, y), to (x, y), radius, height of their middle), slanting down to the left as the sprite's
KNUCKLES = [((XE(19.8), YE(42.6)), (XE(12.6), YE(45.4)), 1.3, 3.95), ((XE(20.2), YE(45.6)), (XE(12.4), YE(48.6)), 1.3,
                                                                       3.95),
            ((XE(18.0), YE(48.9)), (XE(12.6), YE(50.6)), 1.15, 3.7)]

# The greys: bands of how squarely a face looks towards LIGHT (the sprite's light and the game's sun: the upper left),
# (lowest value, palette index); the dark parts.
LIGHT = Vector((-0.55, 0.45, 0.7)).normalized()
GREYS = [(-9.0, 0x04), (0.05, 0x06), (0.42, 0x08), (0.78, 0x0a), (0.94, 0x0c)]
CAP = 0x04                          # the cuts' caps: the parts' dark inside

# The damaged looks' pixels where they differ from the intact sprites (169 from 165, 207 from 167, in the picture's
# rows and columns: "column:intact>damaged"): the barrel's plating burnt and torn round its lamps, embers in it.
DAMAGE = """
14 33:74>71 34:75>71
15 34:72>01 35:76>01 36:74>01
16 33:09>07 34:07>04 36:73>01
17 27:09>08 33:05>01 34:06>01 35:04>02
18 26:07>06 27:08>05 28:09>07 31:07>05 32:07>04 34:05>01 35:02>01
19 26:08>05 27:09>05 28:07>03 29:05>03 30:04>02 31:05>02 32:06>04 33:07>04 35:04>02
20 25:08>07 26:09>07 27:07>03 28:05>02 29:04>01 30:05>01 31:05>01 32:05>06 34:07>05 35:05>03
21 22:06>05 23:06>05 25:09>08 26:07>04 27:05>04 28:04>70 29:05>71 30:05>73 31:05>03 32:05>08 33:05>04 34:06>04 35:08>05
22 21:03>02 22:02>70 23:04>01 24:09>08 25:07>06 26:05>03 27:04>71 28:05>71 29:05>74 30:05>01 31:05>09 32:05>06 33:06>03 34:07>04 35:05>02
23 20:73>01 21:76>71 22:74>73 23:07>02 24:07>06 26:02>72 27:05>01 28:05>73 29:05>72 31:05>02 32:06>04 33:08>07 34:09>08
24 21:07>06 22:08>04 23:07>01 24:05>02 25:01>73 26:73>72 27:02>72 28:05>01 29:05>02 30:05>06 31:06>03 32:07>06 34:01>70
25 20:08>07 21:09>07 22:07>02 23:05>71 24:02>73 25:03>71 26:76>01 27:74>70 28:02>70 29:05>03 30:06>07 31:07>04 32:08>07
26 19:08>07 20:0a>07 21:07>01 22:05>01 23:04>71 24:05>04 25:04>03 26:03>02 27:73>71 28:02>01 29:05>04 31:08>07
27 20:09>06 21:05>01 22:04>71 23:05>02 25:05>06
"""
# How the burns are painted (the soot's and the embers' blurred fields at a face's middle): (lowest ember, palette
# index, glow) and (lowest soot, palette index); how deep the plating is pressed in where it is burnt most.
EMBERS = [(0.42, 0x71, 0.16), (0.7, 0x73, 0.26)]
SOOT = [(0.2, 0x04), (0.36, 0x02), (0.6, 0x01)]
TORN = 1.2


class Mats:
    """The materials, made once each (by palette index and glow)."""

    def __init__(self):
        self.cache = {}

    def get(self, index, glow=0.0, metallic=0.45, roughness=0.36):
        key = (index, round(glow, 3))
        if key not in self.cache:
            pal = k.level_palette()
            name = "mortar_%02x" % index + ("_g%02d" % round(glow * 100) if glow > 0 else "")
            if glow > 0:
                self.cache[key] = k.material(name, palette=index, metallic=0.05, roughness=0.18,
                                             emission=pal[index], emission_strength=glow)
            else:
                self.cache[key] = k.material(name, palette=index, metallic=metallic, roughness=roughness)
        return self.cache[key]


# --- Helpers -------------------------------------------------------------------------------------------------------

def paint_greys(obj, m, light=LIGHT, bands=GREYS):
    """The grey part's faces in bands of how they face the light, cut along smooth contours."""
    obj.data.update()
    values = [v.normal.dot(light) for v in obj.data.vertices]
    band_split(obj, values, [(lowest, m.get(index)) for lowest, index in bands])
    return obj


def clip_plane(obj, co, normal):
    """Cuts an object off on the side of a plane its normal points to, closing the cut."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    result = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=co,
                                    plane_no=normal, clear_outer=True)
    edges = [e for e in result["geom_cut"] if isinstance(e, bmesh.types.BMEdge) and e.is_valid and e.is_boundary]
    if edges:
        bmesh.ops.holes_fill(bm, edges=edges, sides=0)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    return obj


def plan_outline(points, iterations=2):
    """A plan given by the picture's columns and rows (counter-clockwise or not), its corners rounded, in x, y."""
    pts = [(XE(c), YE(r)) for c, r in points]
    area = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
    if area < 0:
        pts.reverse()
    return mk.chaikin(pts, iterations)


def barrel_frame():
    """The barrel's axis: its breech end's middle B, its direction D, across it SIDE (level, to the lower right) and
    UP (across it, upwards)."""
    a = Vector((1.0, 1.0, 0.0)).normalized()
    c, s = math.cos(math.radians(ELEVATION)), math.sin(math.radians(ELEVATION))
    plan = AXIS0 + Vector((a.x, a.y)) * T_BREECH
    B = Vector((plan.x, plan.y, Z_BREECH))
    D = Vector((a.x * c, a.y * c, s))
    side = Vector((1.0, -1.0, 0.0)).normalized()
    up = side.cross(D).normalized()
    return B, D, side, up


def section(phi):
    """The barrel's section at angle phi (0: SIDE, 90: UP): its point (u, v) and outward normal (nu, nv)."""
    u, v = mk.superellipse_point(phi, POWER)
    nu = math.copysign(abs(u) ** (POWER - 1), u)
    nv = math.copysign(abs(v) ** (POWER - 1), v)
    n = math.hypot(nu, nv) or 1.0
    return u, v, nu / n, nv / n


def barrel_profile(step=0.75):
    """BARREL with points added along its long runs (so that the burns and the bands have points to follow)."""
    out = [BARREL[0]]
    for (s0, r0), (s1, r1) in zip(BARREL, BARREL[1:]):
        n = max(1, int(math.ceil((s1 - s0) / step)))
        for i in range(1, n + 1):
            out.append((s0 + (s1 - s0) * i / n, r0 + (r1 - r0) * i / n))
    return out


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
    obj = k.loft("barrel", rings, m.get(0x07), start_point=B, end_point=B + D * MUZZLE_S)
    k.recalc_normals(obj)
    y, z, lean = BREECH_CUT
    clip_plane(obj, (0.0, y, z), (0.0, -math.cos(math.radians(lean)), -math.sin(math.radians(lean))))
    burn = damage_fields() if state == "damaged" else None
    if burn:
        tear(obj, burn)
    paint_greys(obj, m)
    # The seam's groove dark, the muzzle's face dark.
    mk.paint(obj, lambda c, n: m.get(0x02) if 23.75 < (c - B).dot(D) < 24.85 else
             (m.get(0x02) if (c - B).dot(D) > MUZZLE_S - 0.05 and n.dot(D) > 0.9 else None))
    if burn:
        scorch(obj, burn, m)
    return k.smooth(obj, 40)


def damage_fields():
    """The damaged sprites' soot (how much darker than the intact sprite, a lamp blown out the darkest) and embers (red
    where the intact sprite was grey or a lamp), blurred a little, as samplers at plan points."""
    import numpy as np
    soot = np.zeros((56, 48))
    ember = np.zeros((56, 48))
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
        u, v = x + 24.0 - 0.5, 27.5 - y
        c0, r0 = int(math.floor(u)), int(math.floor(v))
        fu, fv = u - c0, v - r0

        def px(r, c):
            return a[min(max(r, 0), 55), min(max(c, 0), 47)]
        return ((1 - fu) * (1 - fv) * px(r0, c0) + fu * (1 - fv) * px(r0, c0 + 1) + (1 - fu) * fv * px(r0 + 1, c0) +
                fu * fv * px(r0 + 1, c0 + 1))
    return (lambda x, y: at(soot, x, y)), (lambda x, y: at(ember, x, y))


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
        for lowest, index, glow in reversed(EMBERS):
            if e >= lowest:
                return m.get(index, glow)
        d = soot(c.x, c.y)
        for lowest, index in reversed(SOOT):
            if d >= lowest:
                return m.get(index, metallic=0.25, roughness=0.7)
        return None
    mk.paint(obj, pick)


def surface_at(target, u_frac):
    """The barrel's surface point whose plan position is target (x, y), on the side of its section at u_frac (the
    section's u, -1 the upper left edge, 1 the lower right): (point, outward normal, along, across)."""
    B, D, side, up = barrel_frame()
    radius = R_BODY
    # the section's angle with that u, on its upper half
    lo, hi = 0.0, math.pi
    for _ in range(50):
        mid = (lo + hi) / 2
        if section(mid)[0] > u_frac:
            lo = mid
        else:
            hi = mid
    u, v, nu, nv = section((lo + hi) / 2)
    off = side * (u * radius) + up * (v * radius)
    a = Vector((1.0, 1.0, 0.0)).normalized()
    # along the axis so that the plan position's distance along a matches the target's
    t_target = Vector((target[0], target[1], 0.0)).dot(a) - Vector((AXIS0.x, AXIS0.y, 0.0)).dot(a)
    s = (t_target - T_BREECH - off.dot(a)) / Vector((D.x, D.y, 0.0)).dot(a)
    p = B + D * s + off
    n = (side * nu + up * nv).normalized()
    across = n.cross(D).normalized()
    return p, n, D, across


def oriented_ball(name, centre, radii, frame, mat, subdivisions=3):
    """An ellipsoid of even triangles with radii along the frame's axes (across, along, out)."""
    obj = icosphere(name, (0.0, 0.0, 0.0), radii, subdivisions)
    if mat is not None:
        obj.data.materials.append(mat)
    across, along, out = frame
    mat4 = Matrix((across.to_4d(), along.to_4d(), out.to_4d(), (0, 0, 0, 1))).transposed()
    mat4.translation = centre
    obj.data.transform(mat4)
    return obj


def lamp(name, spec, state, m):
    """A lamp on the barrel: a dark socket sunk into it, a lens in it (rim and core), glowing in the state's colours;
    blown out (the socket only, deeper) when damaged."""
    target, (half_across, half_along), by_state = spec
    colours = by_state[state]
    side = Vector((1.0, -1.0)).normalized()
    across_axis = Vector(target).dot(side) - AXIS0.dot(side)     # how far it lies to the lower right of the axis
    p, n, along, across = surface_at(target, max(-0.97, min(0.97, across_axis / R_BODY)))
    frame = (across, along, n)
    if colours is None:     # blown out: the torn, burnt plating (barrel's tear() and scorch()) is all that is left
        return []
    parts = [oriented_ball(f"{name}_socket", p - n * 0.22, (half_across + 0.45, half_along + 0.4, 0.55), frame,
                           m.get(0x01, metallic=0.2, roughness=0.55))]
    if colours is not None:
        (rim, rim_glow), (core, core_glow) = colours
        parts.append(oriented_ball(f"{name}_lens", p + n * 0.02, (half_across, half_along, 0.42), frame,
                                   m.get(rim, rim_glow)))
        parts.append(oriented_ball(f"{name}_core", p + n * 0.16, (half_across * 0.55, half_along * 0.55, 0.34),
                                   frame, m.get(core, core_glow)))
    for obj in parts:
        k.smooth(obj, 80)
    return parts


def muzzle_face(state, m):
    """The muzzle's face: a red ring round the bore, the bore dark (or glowing as it fires)."""
    B, D, side, up = barrel_frame()
    c = B + D * MUZZLE_S
    (ring_index, ring_glow), bore = MUZZLE[state]
    # The ring: a torus round the axis, half sunk into the face.
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
    ring = k.mesh_object("muzzle_ring", verts, faces, m.get(ring_index, ring_glow, 0.3, 0.3))
    k.recalc_normals(ring)
    k.smooth(ring, 80)
    bore_mat = m.get(0x01, metallic=0.2, roughness=0.6) if bore is None else m.get(*bore)
    prof = [(-0.6, BORE_R), (0.06, BORE_R), (0.08, 0.01)]
    bore_obj = turned_axis("muzzle_bore", prof, c, D, side, up, bore_mat, 32)
    return [ring, bore_obj]


def turned_axis(name, profile, origin, d, side, up, mat, segments=24):
    """A round part along d from origin: profile [(distance along d, radius)], closed at both ends."""
    rings = []
    for t, r in profile:
        rings.append([origin + d * t + (side * math.cos(2 * math.pi * j / segments) +
                                        up * math.sin(2 * math.pi * j / segments)) * r for j in range(segments)])
    obj = k.loft(name, rings, mat, start_point=origin + d * profile[0][0], end_point=origin + d * profile[-1][0])
    k.recalc_normals(obj)
    return k.smooth(obj, 60)


def flame(state, m):
    """The flame out of the muzzle: a teardrop along the barrel's axis, hottest at its root and in its middle as the
    camera sees it, red at its edges."""
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
    # licking: its surface pushed in and out along its length (smooth noise, the same every run)
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
    obj.data.update()
    values = []
    for v in obj.data.vertices:
        along = min(1.0, max(0.0, (v.co - c).dot(D) / length))
        facing = max(0.0, v.normal.dot(view))
        values.append(0.55 * (1.0 - along) ** 0.8 + 0.5 * facing ** 1.5)
    band_split(obj, values, [(lowest, m.get(index, glow)) for lowest, index, glow in FLAME_BANDS])
    k.recalc_normals(obj)
    return k.smooth(obj, 80)


# --- The hand ------------------------------------------------------------------------------------------------------

def neck(m):
    obj = swept("neck", [Vector(p) for p in NECK], NECK_HALF, NECK_TOP, m.get(0x07), power=3.0, segments=16)
    return k.smooth(paint_greys(obj, m), 50)


def thumb(m):
    dense = mk.chaikin([tuple(p) for p in THUMB], 2, closed=False)
    # half-widths along the path, tapering to the tip
    n = len(dense)
    halves = [THUMB_HALF[0] + (THUMB_HALF[1] - THUMB_HALF[0]) * math.sin(math.pi * 0.8 * i / (n - 1)) -
              0.9 * smoothstep(0.75, 1.0, i / (n - 1)) for i in range(n)]
    points = [Vector(p) for p in dense]
    rings = []
    segments, power = 16, 3.0
    for i, p in enumerate(points):
        t = (points[min(i + 1, n - 1)] - points[max(i - 1, 0)]).normalized()
        across = t.cross(Vector((0, 0, 1))).normalized()
        upv = across.cross(t).normalized()
        ring = []
        for j in range(segments):
            a = 2 * math.pi * j / segments
            cc, ss = math.cos(a), math.sin(a)
            ring.append(p + across * math.copysign(abs(cc) ** (2 / power), cc) * halves[i] +
                        upv * math.copysign(abs(ss) ** (2 / power), ss) * (THUMB_TOP if ss >= 0 else p.z + SKIRT + 0.5))
        rings.append(ring)
    obj = k.loft("thumb", rings, m.get(0x07))
    clip_below(obj, -SKIRT)
    k.recalc_normals(obj)
    return k.smooth(paint_greys(obj, m), 50)


def hook(m):
    obj = mk.smooth_tube("hook", HOOK, m.get(0x07), segments=12, iterations=2)
    clip_below(obj, -SKIRT)
    k.recalc_normals(obj)
    return k.smooth(paint_greys(obj, m), 60)


def rounded_rect(x0, x1, y0, y1, r, steps=6):
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for i in range(steps + 1):
            a = math.radians(a0 + 90 * i / steps)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def densify(outline, step):
    """An outline with points added along its long edges (so a value along it has points to follow)."""
    out = []
    for i, p in enumerate(outline):
        q = outline[(i + 1) % len(outline)]
        n = max(1, int(math.ceil(math.hypot(q[0] - p[0], q[1] - p[1]) / step)))
        out += [(p[0] + (q[0] - p[0]) * j / n, p[1] + (q[1] - p[1]) * j / n) for j in range(n)]
    return out


def block(state, m):
    """The upright block: a rounded prism with a sloping top, bevelled and painted; the slot cut along it (its walls
    dark) and the glowing bar in it."""
    outline, back, front, bev = BLOCK
    plan = plan_outline(outline)
    x0, x1 = min(p[0] for p in plan), max(p[0] for p in plan)
    y0, y1 = min(p[1] for p in plan), max(p[1] for p in plan)
    top = mk.plane((x0, y1, back), (x1, y1, back), (x0, y0, front))
    body = mk.wedge("block", plan, -SKIRT, top, m.get(0x07))
    mk.bevel(body, bev, 3, 35)
    paint_greys(body, m)
    sx0, sx1, sy0, sy1, depth = SLOT
    dark = m.get(0x01, metallic=0.2, roughness=0.6)
    cutter = mk.wedge("slot_cut", rounded_rect(sx0, sx1, sy0, sy1, 0.95), -1.0, lambda x, y: top(x, y) + 2.0, dark,
                      bottom=lambda x, y: top(x, y) - depth)
    mk.boolean(body, cutter, "DIFFERENCE")
    k.recalc_normals(body)
    k.smooth(body, 35)
    # the glowing bar in the slot, hottest at its top end
    bx0, bx1, by0, by1 = sx0 + BAR_INSET, sx1 - BAR_INSET, sy0 + BAR_INSET, sy1 - BAR_INSET
    bar = mk.wedge("slot_bar", densify(rounded_rect(bx0, bx1, by0, by1, 0.7), 0.35), -1.0,
                   lambda x, y: top(x, y) - BAR_DOWN, None, bottom=lambda x, y: top(x, y) - depth - 0.3)
    mk.bevel(bar, 0.3, 2, 35)
    bar.data.update()
    spread, bands = SLOT_HEAT[state]
    heat = [math.exp(-(((v.co.y - by0) / (by1 - by0) - HOT_AT) / spread) ** 2) for v in bar.data.vertices]
    band_split(bar, heat, [(lowest, m.get(index, glow)) for lowest, index, glow in bands])
    k.recalc_normals(bar)
    k.smooth(bar, 35)
    return [body, bar]


def palm(m):
    outline, top, bev = PALM
    body = mk.prism("palm", plan_outline(outline, 1), -SKIRT, top, m.get(0x07))
    mk.bevel(body, bev, 2, 35)
    paint_greys(body, m)
    return k.smooth(body, 35)


def fist(m):
    outline, height, bev = FIST
    body = mk.prism("fist", plan_outline(outline), -SKIRT, height, m.get(0x07))
    mk.bevel(body, bev, 2, 35)
    paint_greys(body, m)
    k.smooth(body, 35)
    parts = [body]
    for i, (a, b, r, z) in enumerate(KNUCKLES):
        start, end = Vector((a[0], a[1], z)), Vector((b[0], b[1], z))
        d = (end - start)
        length = d.length
        d.normalize()
        prof = [(0.0, 0.01), (0.12, r * 0.6), (0.4, r * 0.92), (0.8, r), (length - 0.8, r), (length - 0.4, r * 0.92),
                (length - 0.12, r * 0.6), (length, 0.01)]
        upv = Vector((0.0, 0.0, 1.0))
        side = upv.cross(d).normalized()
        obj = turned_axis(f"knuckle{i}", prof, start, d, side, upv, m.get(0x07), 18)
        parts.append(k.smooth(paint_greys(obj, m), 60))
    return parts


# --- The whole -----------------------------------------------------------------------------------------------------

def build_whole(state):
    k.reset()
    m = Mats()
    parts = [barrel(m, state)]
    for name, spec in LAMPS.items():
        parts += lamp(name, spec, state, m)
    parts += muzzle_face(state, m)
    if state in FLAMES:
        parts.append(flame(state, m))
    for obj in parts:
        obj["lean"] = True              # the barrel's parts (see LEAN)
    parts += [palm(m), neck(m), thumb(m), hook(m)]
    parts += block(state, m)
    parts += fist(m)
    for obj in parts:
        k.recalc_normals(obj)
    return parts, m


def lean(obj):
    """Leans a part of the barrel (see LEAN): its points moved down the screen with their height, its normals with
    them."""
    mesh = obj.data
    normals = [Vector(c.vector) for c in mesh.corner_normals]
    for v in mesh.vertices:
        v.co.y -= LEAN * (v.co.z - Z_BREECH)
    mesh.update()
    mesh.normals_split_custom_set([tuple(Vector((n.x, n.y, n.z + LEAN * n.y)).normalized()) for n in normals])
    return obj


def leaned_whole(whole):
    """The whole as it is exported: copies of the barrel's parts leaned, with the hand's parts."""
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
    """The mortar's own pixels in the 48 x 56 picture the four sprites make: the biggest group of greys and reds (ramps
    0 and 7) joined side by side, without the black specks of the leaves' shadows joined to it at its foot."""
    from sprite_profile import sprite_indices
    tl, tr, bl, br = sprites
    pic = [[None] * 48 for _ in range(56)]
    for sprite, (c0, r0) in ((tl, (0, 0)), (tr, (24, 0)), (bl, (0, 28)), (br, (24, 28))):
        idx = sprite_indices(sheet, sprite)
        for r in range(28):
            for c in range(24):
                pic[r0 + r][c0 + c] = idx[r][c]
    own = [[pic[r][c] is not None and pic[r][c] >> 4 in (0, 7) for c in range(48)] for r in range(56)]
    seen = [[False] * 48 for _ in range(56)]
    best = []
    for r0 in range(56):
        for c0 in range(48):
            if own[r0][c0] and not seen[r0][c0]:
                group, stack = [], [(r0, c0)]
                seen[r0][c0] = True
                while stack:
                    r, c = stack.pop()
                    group.append((r, c))
                    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        rr, cc = r + dr, c + dc
                        if 0 <= rr < 56 and 0 <= cc < 48 and own[rr][cc] and not seen[rr][cc]:
                            seen[rr][cc] = True
                            stack.append((rr, cc))
                if len(group) > len(best):
                    best = group
    mask = [[False] * 48 for _ in range(56)]
    for r, c in best:
        if r < 52 and (r, c) not in ((47, 3), (47, 23), (47, 24), (48, 23)):
            mask[r][c] = True
    return mask


def piece_mask(mask, part):
    x0, x1, y0, y1 = BOXES[part]
    c0, r0 = int(x0 + 24), int(28 - y1)
    return [row[c0:c0 + 24] for row in mask[r0:r0 + 28]]


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
        mk.compare("whole, %s" % state, mk.coverage(shown, 48, 56), mask)
    bpy.context.scene.view_settings.view_transform = "Standard"
    if "preview" in options:
        mk.preview(options["preview"] + "mortar_whole_" + state, shown, size=(48, 56), scale=8, distance=1.6)
    if "whole" in options:
        mk.export(shown, options["whole"] + state + ".glb")
    for obj in shown:
        if obj not in whole:
            bpy.data.objects.remove(obj)
    cap = m.get(CAP)
    for part, name, sprite in wanted:
        box = BOXES[part]
        parts = []
        for src in whole:
            p = cut(src, box, cap)
            if p is not None:
                parts.append(lean(p) if src.get("lean") else p)
        drop_unused(parts)
        mk.transform(parts, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
        bpy.context.view_layer.update()
        triangulate(parts)
        parts = [join(parts, name)]
        parts[0].data.name = name
        for src in whole:
            src.hide_render = True
        if sheet:
            mk.compare("%s (G %d, the mortar's own pixels)" % (name, sprite), mk.coverage(parts, 24, 28),
                       piece_mask(mask, part))
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options and options.get("pieces") == "1":
            mk.preview(options["preview"] + name, parts)
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
        sheet = os.path.join(sheets, "enemy_G.png") if os.path.isdir(sheets) else sheets
        sys.path.insert(0, os.path.join(HERE, "..", ".."))
    states = options["states"].split(",") if "states" in options else [s for s, _ in MODELS]
    global LEAN
    LEAN = float(options.get("lean", LEAN))
    for state, pieces in MODELS:
        if state in states:
            export_state(state, pieces, options, sheet, out)


if __name__ == "__main__":
    build()
