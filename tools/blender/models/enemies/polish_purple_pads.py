"""TYRIAN's panel of purple pads (sheet 2 sprites 279, 281, 283 above 245, 169, 207 above 273, 275, 277, 2x2 each: one
72 x 84 picture; top layer; one frame each; TYRIAN and TYRIAN X, enemies 32-39 and 41 of episodes 1 and 3), polished
(2026-10-21; it replaces wave3_p_ground.py's pad_tile() and eye_block(), each sprite a ribbed heightfield on boulders of
its own). models.cfg: model purple_pad_tl / purple_pad_t / purple_pad_tr / purple_pad_l / eye_block / purple_pad_r /
purple_pad_bl / purple_pad_b / purple_pad_br ... origin (unchanged); the sprite lines get height=-6 (below).

How the levels lay it out (event 7, top enemies, all at the tile grid's x, one row of sprites every 9-10 events, 28
pixels): the full panel (279 281 283 above 245 169 207 above 273 275 277: TYRIAN 3088-3107), the corners alone (279 283
above 273 277: 2659-2668, 2995-3004), three wide without the middle row (279 281 283 above 273 275 277: 2771-2780,
3210-3219), five wide (279 281 281 281 283 above 273 275 275 275 277: 3294-3303) and a ring of corners round an empty
middle (279 283 / 279 . . 283 / 273 . . 277 / 273 277, 2892-2920). They lie on background 3's outcrops, exactly over
map tiles 156-158, 166, 150, 168, 176-178 (and 159, 160, 169, 170 inside the ring), which draw the same panel wrecked
(cracked pads, the eye broken): the sprites' grey cobbles and tan stones round the purple are those tiles' own pixels,
the map's ground, so the models leave them out (their silhouettes are checked against the purple and blue only).

None of the nine is another's pixels mirrored, turned or in other ramps (the left and right ones are nearly mirror
images, but the light from the upper left shades them differently: 273 / 277 match 70%). What the art is instead is
periodic: every pad sprite has its pad at the same place, and the floor between them repeats every 24 pixels across
and 28 down, so that the sprites meet in all those layouts (281's left columns are 283's, 279's right columns 281's,
279's bottom rows 245's, and so on).

As the sprites draw it (columns and rows of the 72 x 84 picture; purples of ramp 5): in each pad sprite a bevelled
octagonal pad (its columns 3-20 of rows 4-19, the corners cut 5 pixels, a flat top in shade 8, its upper and left
bevels lit (10-11), the right and lower ones darker, its front a dark row (19)); round each corner where four sprites
meet a junction: the floor (shade 9) running down between the pads from their middles (row 11 of the upper sprite, a
lit bevel at its top end) to the middles of the pads below (row 10 of the lower one), widening between the pad rows into
a band (rows 19-31 of the upper sprite and the top of the lower one) on which stand two raised blocks, A (shade 9, lit
on its left) under the upper left pad and B (shade 10, lit on its right) under the upper right one, and between them a
round boss (8 pixels across, centred on the corner, its rim lit at the upper left), and below the band a light block
between the lower pads (rows 33-38, a lit lower edge). In the middle sprite (169) a purple housing (its columns 2-21 of
rows 1-24): a frame round a dark blue glass eye (columns 6-18 of rows 6-15, a white glint at its upper left, a light
crescent inside its lower right), a tab in the frame's top (columns 11-13), and below the eye two blue glass capsules
slanting in like cheeks (columns 1-7 and 17-22 of rows 16-22) either side of a grille (columns 8-16 of rows 18-24): a
lit lip over four teeth in a dark slot.

Built as a machined panel (polish_machine_kit): the floor one plate (the union of the junctions' bands, the strips
between the pads and the fills under the pads' cut corners) with bevelled edges; the pads octagonal prisms with
chamfered tops; the blocks rounded prisms; the bosses turned studs; the housing an octagonal block with the eye's
socket and the grille's slot cut into it by exact booleans, a rounded bezel ring round the socket, a glass dome in it
(the crescent painted in a band as polish_balls.painted_ball paints, the glint thin turned dabs on the dome, a white
core in a light blue halo; the glass glowing a little, well under 1), the capsules lofted glass lozenges with a light
streak, the teeth and the lip rounded bars. Every junction is the same (built from one function at each of the four
corners), so a piece's edges are the same wherever it lies: built whole as the full panel and cut along the sprites'
edges (polish_arch.py's cut(): the pieces keep the whole's shading across the cuts), each piece moved so its sprite's
centre is its origin, they meet in every layout above (checked in the game camera's view, each layout assembled).
Every mesh is triangulated before the export (polish_k_pod.triangulate: the same split every run).

Where it stands: the top layer's enemies are drawn 6 pixels above background 3 (layer heights 38 and 32), whose
outcrops are a solid with its plane at its layer's height (polish_hood_turret.py); "height=-6" on the sprite lines sets
the panel on that plane (the plate reaches SKIRT below it).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from background 3's plane (z = 0);
the whole's origin is the middle of the picture (the middle of 169): column c's left edge is x = c - 36, row r's top
edge y = 42 - r. A junction's own coordinates (u, v) are from its corner: x = X + u, y = Y + v.

Replaces wave3_p_ground.py's panel: remove OCTAGON, purple_mats(), purple_floor(), octagon_pad(), pad_tile(), the loop
registering purple_pad_tl ... purple_pad_br, PX() (only eye_block() uses it), eye_block() with its @model("eye_block",
[169]) registration, and the purple_pad / eye_block lines of its docstring; and wave3_p_art.py's EYE, PAD_ML, PAD_MR,
PAD_TL, PAD_TM, PAD_TR, PAD_BL, PAD_BM and PAD_BR (only wave3_p_ground.py reads them), so that they don't overwrite
these models. The gold domes, the gold pyramid and the red works stay in wave3_p_ground.py (np, ramp(), shade(), art
and the kit's helpers with them).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the whole
and of each piece against enemy_2.png's purple and blue), --preview <prefix> (the whole's and each piece's top and 3/4
views), --only <model,...>, --whole <file.glb> (the uncut panel as well, for looking at).
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_arch import cut  # noqa: E402  (polish_machine_kit.cut without its material indices shifted twice)
from polish_balls import Ellipsoid, painted_ball  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402

# The pieces: (name, sprite, the box it covers in the whole's coordinates (x0, x1, y0, y1)).
PIECES = [("purple_pad_tl", 279, (-36.0, -12.0, 14.0, 42.0)), ("purple_pad_t", 281, (-12.0, 12.0, 14.0, 42.0)),
          ("purple_pad_tr", 283, (12.0, 36.0, 14.0, 42.0)), ("purple_pad_l", 245, (-36.0, -12.0, -14.0, 14.0)),
          ("eye_block", 169, (-12.0, 12.0, -14.0, 14.0)), ("purple_pad_r", 207, (12.0, 36.0, -14.0, 14.0)),
          ("purple_pad_bl", 273, (-36.0, -12.0, -42.0, -14.0)), ("purple_pad_b", 275, (-12.0, 12.0, -42.0, -14.0)),
          ("purple_pad_br", 277, (12.0, 36.0, -42.0, -14.0))]
LAYOUT = [[279, 281, 283], [245, 169, 207], [273, 275, 277]]
PAD_SPRITES = (279, 281, 283, 245, 207, 273, 275, 277)
JUNCTIONS = [(-12.0, 14.0), (12.0, 14.0), (-12.0, -14.0), (12.0, -14.0)]   # the corners where four sprites meet

SKIRT = -0.5                 # how far everything reaches below background 3's plane
FLOOR_TOP = 1.2              # the floor plate
PAD_TOP = 4.4                # the pads
BLOCK_TOP = 2.65             # blocks A and B
BOSS_TOP = 2.55              # the bosses
TONGUE_TOP = 2.0             # the light block between the lower pads
# The pad: its plan about its sprite's centre (pixel edges: columns 3-21, rows 4-20, the corners cut through the
# middles of the stair-stepped corner pixels), the chamfer round its top.
PAD = [(-3.5, 10.0), (3.5, 10.0), (9.0, 4.5), (9.0, -0.5), (3.5, -6.0), (-3.5, -6.0), (-9.0, -0.5), (-9.0, 4.5)]
PAD_CHAMFER = 0.85
# A junction (u, v from its corner): the band between the pad rows, the strip between the pad columns (from the upper
# pads' middles to the lower ones'), the fills under the pads' cut corners (hidden by them), the blocks A and B, the
# boss (its middle, radius) and the light block (tongue) between the lower pads.
BAND_V = (-4.0, 9.0)
STRIP_U, STRIP_V = 3.0, (-11.0, 17.0)
FILL_UP = [(-3.0, 17.0), (3.0, 17.0), (11.5, 8.5), (-11.0, 8.5)]
FILL_DOWN = [(-10.0, -4.0), (10.0, -4.0), (3.0, -11.0), (-3.0, -11.0)]
BLOCK_A = (-11.0, -4.3, -4.0, 8.0)
BLOCK_B = (5.0, 11.75, -4.0, 8.0)
BOSS_AT, BOSS_R = (0.0, 0.85), 4.05
TONGUE = [(-4.9, -4.8), (4.9, -4.8), (3.0, -6.7), (3.0, -10.85), (-3.0, -10.85), (-3.0, -6.7)]
# The panel's floor reaches from block A's left edge in the left column to column 12 of the right column (in the
# middle right sprite 207, where B's shadow is drawn beside it, to column 13: BAND_207).
BAND_X = (-23.0, 24.0)
BAND_207 = 25.0
# The housing (the middle sprite's own coordinates): its plan, its top; the eye's socket (middle, radii, depth); the
# tab in the frame's top; the eye's glass dome (radii, its middle's height); the grille's slot (x0, x1, y0, y1, depth),
# its lip and teeth; the capsules (ends, radius, height).
HOUSING = [(-7.4, 13.0), (7.6, 13.0), (10.5, 10.1), (10.5, 0.6), (11.4, -2.6), (6.2, -9.6), (5.6, -11.0), (-4.6, -11.0),
           (-5.2, -9.6), (-11.4, -2.6), (-10.5, 0.6), (-10.5, 10.1)]
HOUSING_TOP = 3.9
EYE_AT, EYE_R = (0.5, 3.0), (6.55, 5.45)
SOCKET_R, SOCKET_DEPTH = (7.25, 6.2), 1.2
BEZEL = (0.6, 0.62, 0.8)                        # the rounded ring round the socket: its offset out, its radius, squash
TAB = (-1.0, 2.0, 9.6, 13.0, 0.5)               # x0, x1, y0, y1, height over the housing
DOME_RZ, DOME_Z = 3.4, HOUSING_TOP - 1.3
GRILLE = (-4.05, 5.05, -10.7, -5.05, 1.5)
LIP = (-3.2, 4.25, -5.15, -3.85, 0.5)
TEETH_X, TEETH_Y, TEETH_HW = (-2.5, -0.5, 1.5, 3.5), (-10.35, -5.45), 0.5
CAPSULES = [((-9.25, -3.35), (-5.75, -7.95)), ((9.55, -3.85), (6.95, -7.6))]
CAPSULE_R, CAPSULE_Z = 1.5, HOUSING_TOP + 0.35
# The eye's light: the glint (its middle's offset from the eye's seen from above, its halo's and its white core's
# radii: columns 8-11 of rows 8-10, the core columns 9-10 of rows 8-9), the crescent painted inside the
# lower right of its rim (round the direction CRESCENT_AT seen from above, spread, how far out (a part of the eye's
# radii) and its width: rows 12-15, columns 13-17).
GLINT_AT, GLINT_SIZE, GLINT_CORE = (-2.4, 2.1), 1.65, 1.0
CRESCENT_AT, CRESCENT_SPREAD, CRESCENT_Q = -48.0, 42.0, (0.68, 0.13)


def materials():
    def purple(name, index, roughness=0.42):
        return k.material(name, palette=index, metallic=0.3, roughness=roughness)

    def glass(name, index, glow, roughness=0.06):
        return k.material(name, palette=index, metallic=0.2, roughness=roughness, emission=k.level_palette()[index],
                          emission_strength=glow)
    return {
        "seam": purple("pads_seam", 0x54, 0.6),
        "wall": purple("pads_wall", 0x55, 0.5),
        "dark": purple("pads_dark", 0x56, 0.46),
        "top": purple("pads_top", 0x58),
        "floor": purple("pads_floor", 0x59),
        "light": purple("pads_light", 0x5a, 0.4),
        "lit": purple("pads_lit", 0x5b, 0.36),
        "bright": purple("pads_bright", 0x5d, 0.34),
        "recess": purple("pads_recess", 0x52, 0.6),
        "socket": k.material("pads_socket", palette=0x66, metallic=0.4, roughness=0.3),
        "eye": glass("pads_eye", 0x34, 0.3),
        "capsule": glass("pads_capsule", 0x36, 0.25),
        "crescent": glass("pads_crescent", 0x3b, 0.42),
        "glint": glass("pads_glint", 0x3e, 0.55, 0.04),
    }


# --- Helpers --------------------------------------------------------------------------------------------------------

def ccw(pts):
    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(pts, pts[1:] + pts[:1]))
    return pts if area > 0 else pts[::-1]


def moved(points, dx, dy):
    return [(x + dx, y + dy) for x, y in points]


def rrect(x0, x1, y0, y1, r, steps=4):
    """A rectangle's plan with its corners rounded (radius r)."""
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90.0), (x1 - r, y1 - r, 0.0), (x0 + r, y1 - r, 90.0), (x0 + r, y0 + r, 180.0)):
        for i in range(steps + 1):
            a = math.radians(a0 + 90.0 * i / steps)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def sprite_centre(sprite):
    for j, row in enumerate(LAYOUT):
        if sprite in row:
            return (24.0 * row.index(sprite) - 24.0, 28.0 - 28.0 * j)
    raise KeyError(sprite)


def paint_by_normal(obj, m, top="top", lit="lit", mid="floor", dark="dark", front="wall", side="dark"):
    """Faces facing up keep top; the bevels lit where they face the upper left, darker to the lower right (as the
    sprites shade them); the walls dark, the front ones (down the screen, which the camera sees) darkest."""
    def pick(c, n):
        if n.z > 0.92:
            return m[top]
        if n.z > 0.3:
            if n.x < -0.25 or n.y > 0.25:
                return m[lit] if not (n.x > 0.2) else m[mid]
            if n.x > 0.25 and n.y < -0.1:
                return m[dark]
            return m[mid]
        if n.z < -0.5:
            return m["seam"]
        return m[front] if n.y < -0.35 else m[side]
    mk.paint(obj, pick)


def slab(name, outline, z0, z1, m, chamfer, segments=2, mat="top", **paint):
    """A prism of a plan, its top edges chamfered (and its corners, where they are sharper than 50 degrees), shaded
    flat on its flat faces, painted by normal."""
    obj = mk.prism(name, ccw(list(outline)), z0, z1, m[mat])
    mk.bevel(obj, chamfer, segments, 50)
    mk.shade(obj, 35)
    paint_by_normal(obj, m, top=mat, **paint)
    return obj


# --- The parts ------------------------------------------------------------------------------------------------------

def floor_plate(m):
    """The floor: the union of the junctions' bands, strips and fills, one plate with bevelled edges; its top end
    (row 11 of the upper sprites) and its lower end lit, as drawn."""
    parts = []
    for i, (X, Y) in enumerate(JUNCTIONS):
        parts.append(mk.prism(f"strip{i}", ccw([(X - STRIP_U, Y + STRIP_V[0]), (X + STRIP_U, Y + STRIP_V[0]),
                                               (X + STRIP_U, Y + STRIP_V[1]), (X - STRIP_U, Y + STRIP_V[1])]),
                              SKIRT, FLOOR_TOP))
        parts.append(mk.prism(f"fill_up{i}", ccw(moved(FILL_UP, X, Y)), SKIRT, FLOOR_TOP))
        parts.append(mk.prism(f"fill_down{i}", ccw(moved(FILL_DOWN, X, Y)), SKIRT, FLOOR_TOP))
    for i, Y in enumerate(sorted({Y for _, Y in JUNCTIONS})):
        parts.append(mk.box(f"band{i}", BAND_X[0], BAND_X[1], Y + BAND_V[0], Y + BAND_V[1], SKIRT, FLOOR_TOP))
        y0, y1 = max(Y + BAND_V[0], -14.0), min(Y + BAND_V[1], 14.0)      # its part in 207
        parts.append(mk.box(f"band207_{i}", BAND_X[1] - 0.5, BAND_207, y0, y1, SKIRT, FLOOR_TOP))
    plate = parts[0]
    plate.name = "floor"
    mk.boolean(plate, parts[1:], "UNION")
    mk.cleanup(plate)
    plate.data.materials.clear()
    plate.data.materials.append(m["floor"])
    mk.bevel(plate, 0.45, 2, 50)
    mk.shade(plate, 35)

    def pick(c, n):
        if n.z > 0.92:
            return m["floor"]
        if n.z > 0.3:
            if n.y > 0.25 or n.x < -0.25:
                return m["lit"]
            if n.y < -0.25:                  # the lower ends between the bottom pads: lit, as drawn
                return m["lit"]
            return m["top"]
        if n.z < -0.5:
            return m["seam"]
        return m["wall"] if n.y < -0.35 else m["dark"]
    mk.paint(plate, pick)
    return plate


def pads(m):
    for sprite in PAD_SPRITES:
        cx, cy = sprite_centre(sprite)
        slab(f"pad{sprite}", moved(PAD, cx, cy), SKIRT, PAD_TOP, m, PAD_CHAMFER, 3, mat="top", mid="floor")


def boss(name, centre, m):
    """A turned stud: a short cylinder, its top edge rounded, a shallow crown."""
    profile = [(BOSS_R, FLOOR_TOP - 0.3), (BOSS_R, BOSS_TOP - 0.55), (BOSS_R - 0.12, BOSS_TOP - 0.3),
               (BOSS_R - 0.45, BOSS_TOP - 0.08), (BOSS_R - 0.95, BOSS_TOP), (0.6, BOSS_TOP + 0.08),
               (0.02, BOSS_TOP + 0.09)]
    obj = mk.lathe(name, profile, centre, m["top"], 40)
    k.smooth(obj, 50)

    def pick(c, n):
        if n.z > 0.95:
            return m["top"]
        if n.z > 0.2:
            return m["lit"] if (n.x < -0.2 or n.y > 0.2) else m["dark"] if (n.x > 0.2 and n.y < -0.1) else m["floor"]
        return m["wall"] if n.y < -0.35 else m["dark"]
    mk.paint(obj, pick)
    return obj


def junction(i, X, Y, m):
    """Blocks A and B on the band, the boss on the corner, the light block between the lower pads."""
    a0, a1, av0, av1 = BLOCK_A
    slab(f"block_a{i}", rrect(X + a0, X + a1, Y + av0, Y + av1, 0.7), FLOOR_TOP - 0.3, BLOCK_TOP, m, 0.42, 2,
         mat="floor")
    b0, b1, bv0, bv1 = BLOCK_B
    slab(f"block_b{i}", rrect(X + b0, X + b1, Y + bv0, Y + bv1, 0.7), FLOOR_TOP - 0.3, BLOCK_TOP, m, 0.42, 2,
         mat="light")
    boss(f"boss{i}", (X + BOSS_AT[0], Y + BOSS_AT[1]), m)
    tongue = slab(f"tongue{i}", moved(TONGUE, X, Y), FLOOR_TOP - 0.3, TONGUE_TOP, m, 0.38, 2, mat="light")
    # Its lower end is drawn lit (row 38).
    mk.paint(tongue, lambda c, n: m["lit"] if (0.3 < n.z < 0.92 and n.y < -0.3) else None)


def housing(m):
    """The middle sprite's housing: an octagonal block, the eye's socket and the grille's slot cut into it, the tab in
    its top, the glass dome in the socket, the lip and the teeth in the slot, the capsules on its lower corners."""
    body = mk.prism("housing", ccw(list(HOUSING)), SKIRT, HOUSING_TOP, m["top"])
    ex, ey = EYE_AT
    sock = mk.lathe("socket_cut", [(1.0, HOUSING_TOP - SOCKET_DEPTH), (1.0, HOUSING_TOP + 2.0)], EYE_AT, None, 48,
                    squash=(1.0, SOCKET_R[1] / SOCKET_R[0]))
    for v in sock.data.vertices:          # (the lathe's radius 1 drawn out to the socket's radii)
        v.co.x = ex + (v.co.x - ex) * SOCKET_R[0]
        v.co.y = ey + (v.co.y - ey) * SOCKET_R[0]
    sock.data.materials.append(m["socket"])
    g0, g1, gy0, gy1, gd = GRILLE
    slot = mk.prism("slot_cut", ccw(rrect(g0, g1, gy0, gy1, 0.5)), HOUSING_TOP - gd, HOUSING_TOP + 2.0, m["recess"])
    mk.boolean(body, [sock, slot], "DIFFERENCE")
    mk.cleanup(body)
    mk.bevel(body, 0.5, 2, 50)
    mk.shade(body, 35)

    def pick(c, n):
        r = math.hypot((c.x - ex) / SOCKET_R[0], (c.y - ey) / SOCKET_R[1])
        if r < 1.04 and c.z < HOUSING_TOP - 0.1:
            return m["socket"]                    # the socket's wall and floor
        if g0 - 0.1 < c.x < g1 + 0.1 and gy0 - 0.1 < c.y < gy1 + 0.1 and c.z < HOUSING_TOP - 0.1:
            return m["recess"]                    # the slot
        if n.z > 0.92:
            return m["top"]
        if n.z > 0.3:
            if n.x < -0.25 or n.y > 0.25:
                return m["lit"]
            return m["dark"] if (n.x > 0.25 and n.y < -0.1) else m["floor"]
        if n.z < -0.5:
            return m["seam"]
        return m["wall"] if n.y < -0.35 else m["dark"]
    mk.paint(body, pick)
    # The tab in the frame's top.
    t0, t1, ty0, ty1, th = TAB
    slab("tab", rrect(t0, t1, ty0, ty1, 0.35), HOUSING_TOP - 0.6, HOUSING_TOP + th, m, 0.28, 2, mat="light")
    # The lip over the slot and the teeth in it.
    l0, l1, ly0, ly1, lh = LIP
    slab("lip", rrect(l0, l1, ly0, ly1, 0.5), HOUSING_TOP - 0.6, HOUSING_TOP + lh, m, 0.35, 2, mat="lit", lit="bright")
    for j, tx in enumerate(TEETH_X):
        slab(f"tooth{j}", rrect(tx - TEETH_HW, tx + TEETH_HW, TEETH_Y[0], TEETH_Y[1], 0.42), HOUSING_TOP - gd - 0.2,
             HOUSING_TOP - 0.15, m, 0.3, 2, mat="lit", lit="bright", mid="light", dark="light", front="light",
             side="light")
    # The bezel round the socket: a rounded ring, lit at its upper left.
    off, rad, squash = BEZEL
    ring = [(ex + (SOCKET_R[0] + off) * math.cos(2 * math.pi * i / 52),
             ey + (SOCKET_R[1] + off) * math.sin(2 * math.pi * i / 52), HOUSING_TOP + 0.05) for i in range(53)]
    bezel = mk.tube("bezel", ring, rad, m["top"], 10)
    for v in bezel.data.vertices:
        v.co.z = HOUSING_TOP + 0.05 + (v.co.z - HOUSING_TOP - 0.05) * squash
    k.recalc_normals(bezel)
    k.smooth(bezel, 60)
    mk.paint(bezel, lambda c, n: m["lit"] if (n.z > 0.3 and (n.x < -0.3 or n.y > 0.3)) else
             m["dark"] if (n.z > 0.3 and n.x > 0.3 and n.y < 0.0) else m["socket"] if n.z <= 0.3 and
             math.hypot((c.x - ex) / SOCKET_R[0], (c.y - ey) / SOCKET_R[1]) < 1.0 + off / SOCKET_R[0] else None)
    eye(m)
    for j, (a, b) in enumerate(CAPSULES):
        capsule(f"capsule{j}", a, b, m)


def eye(m):
    """The glass dome in the socket: dark blue, the glint at its upper left, the crescent inside its lower right."""
    ex, ey = EYE_AT
    shape = Ellipsoid((ex, ey, DOME_Z), (EYE_R[0], EYE_R[1], DOME_RZ))

    def crescent(p, n):
        u, w = (p.x - ex) / EYE_R[0], (p.y - ey) / EYE_R[1]
        off = (math.degrees(math.atan2(w, u)) - CRESCENT_AT + 180.0) % 360.0 - 180.0
        return math.exp(-(off / CRESCENT_SPREAD) ** 2 - ((math.hypot(u, w) - CRESCENT_Q[0]) / CRESCENT_Q[1]) ** 2)
    paint = [(crescent, (0.38,), ("eye", "crescent"))]
    dome = painted_ball("eye", shape, paint, m, subdivisions=4)
    # The glint: a white core in a light blue halo, thin turned dabs on the dome (smoother than bands of its faces).
    d = Vector((GLINT_AT[0] / EYE_R[0], GLINT_AT[1] / EYE_R[1], 0.0))
    d.z = math.sqrt(max(0.0, 1.0 - d.x * d.x - d.y * d.y))
    at, normal = shape.point(d.normalized())
    place = Matrix.Translation(at) @ Vector((0.0, 0.0, 1.0)).rotation_difference(normal).to_matrix().to_4x4()
    for name, radius, lift, mat in (("glint_halo", GLINT_SIZE, 0.07, "crescent"), ("glint", GLINT_CORE, 0.16, "glint")):
        dab = mk.lathe(name, [(radius, -0.25), (radius * 0.97, lift - 0.1), (radius * 0.7, lift - 0.03), (0.02, lift)],
                       (0.0, 0.0), m[mat], 28, squash=(1.0, 0.85))
        dab.data.transform(place)
        k.smooth(dab, 60)
    # Only its top half stands out of the socket: the rest is cut away.
    bm = bmesh.new()
    bm.from_mesh(dome.data)
    res = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5,
                                 plane_co=(0, 0, HOUSING_TOP - SOCKET_DEPTH + 0.05), plane_no=(0, 0, -1),
                                 clear_outer=True)
    edges = [e for e in res["geom_cut"] if isinstance(e, bmesh.types.BMEdge) and e.is_valid and e.is_boundary]
    if edges:
        bmesh.ops.holes_fill(bm, edges=edges, sides=0)
    bm.to_mesh(dome.data)
    bm.free()
    return dome


def capsule(name, a, b, m):
    """A glass lozenge lying on the housing from a to b (seen from above): a round bar with rounded ends, a light
    streak along its upper left."""
    a, b = Vector((a[0], a[1], CAPSULE_Z)), Vector((b[0], b[1], CAPSULE_Z))
    d = (b - a).normalized()
    pts, radii = [], []
    n_end, n_mid = 6, 6
    length = (b - a).length
    for i in range(n_end + 1):                       # the round end at a
        t = math.pi / 2 * (1 - i / n_end)
        pts.append(a - d * CAPSULE_R * math.sin(t) * 0.9)
        radii.append(max(0.02, CAPSULE_R * math.cos(t)))
    for i in range(1, n_mid):
        pts.append(a + d * length * i / n_mid)
        radii.append(CAPSULE_R)
    for i in range(n_end + 1):                       # the round end at b
        t = math.pi / 2 * i / n_end
        pts.append(b + d * CAPSULE_R * math.sin(t) * 0.9)
        radii.append(max(0.02, CAPSULE_R * math.cos(t)))
    obj = mk.tube(name, pts, CAPSULE_R, m["capsule"], 14, radii=radii)
    for v in obj.data.vertices:                      # flattened a little: a lozenge
        v.co.z = CAPSULE_Z + (v.co.z - CAPSULE_Z) * 0.75
    k.recalc_normals(obj)
    k.smooth(obj, 70)
    side = Vector((-d.y, d.x, 0.0))
    if side.x > 0:
        side = -side                                 # towards the upper left
    mk.paint(obj, lambda c, n: m["crescent"] if (n.z > 0.55 and n.dot(side) > 0.25) else None)
    return obj


# --- Build ----------------------------------------------------------------------------------------------------------

def build_whole(m):
    floor_plate(m)
    pads(m)
    for i, (X, Y) in enumerate(JUNCTIONS):
        junction(i, X, Y, m)
    housing(m)
    whole = mk.meshes()
    for obj in whole:
        mk.apply(obj)
    bpy.context.view_layer.update()
    return [o for o in whole if len(o.data.polygons) > 0]


def object_mask(sheet, sprite):
    """The sprite's own pixels: purple, blue and the eye's grey-blue (ramps 5, 3, 6) and what they enclose; the grey
    cobbles and tan stones round them are the map's."""
    from sprite_profile import sprite_indices
    idx = sprite_indices(sheet, sprite)
    keep = [[v is not None and (v >> 4) in (3, 5, 6) for v in row] for row in idx]
    h, w = len(keep), len(keep[0])
    outside = [[False] * w for _ in range(h)]
    todo = [(x, y) for x in range(w) for y in (0, h - 1)] + [(x, y) for y in range(h) for x in (0, w - 1)]
    while todo:
        x, y = todo.pop()
        if 0 <= x < w and 0 <= y < h and not keep[y][x] and not outside[y][x]:
            outside[y][x] = True
            todo += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    return [[keep[y][x] or not outside[y][x] for x in range(w)] for y in range(h)]


def whole_mask(sheet):
    mask = [[False] * 72 for _ in range(84)]
    for j, row in enumerate(LAYOUT):
        for i, sprite in enumerate(row):
            part = object_mask(sheet, sprite)
            for y in range(28):
                for x in range(24):
                    if part[y][x]:
                        mask[28 * j + y][24 * i + x] = True
    return mask


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    k.reset()
    m = materials()
    whole = build_whole(m)
    print("whole panel: %d triangles, %d objects" % (mk.triangles(whole), len(whole)))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    sheet = os.path.join(options["check"], "enemy_2.png") if "check" in options else None
    if sheet:
        sys.path.insert(0, os.path.join(HERE, "..", ".."))
        mk.compare("whole (2 279 281 283 / 245 169 207 / 273 275 277)", mk.coverage(whole, 72, 84), whole_mask(sheet))
    if "preview" in options:
        mk.preview(options["preview"] + "pads_whole", whole, size=(72, 84), scale=8, distance=2.2)
    if "whole" in options:  # the uncut panel, for looking at
        mk.export(whole, options["whole"])
    for name, sprite, box in PIECES:
        if only and name not in only:
            continue
        pieces = [p for p in (cut(src, box, m["seam"]) for src in whole) if p is not None]
        mk.transform(pieces, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
        triangulate(pieces)
        bpy.context.view_layer.update()
        for src in whole:
            src.hide_render = True
        if sheet:
            mk.compare("%s (2 %d)" % (name, sprite), mk.coverage(pieces, 24, 28), object_mask(sheet, sprite))
        mk.report(name, pieces, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, pieces)
        for obj in pieces:
            bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False


if __name__ == "__main__":
    build()
