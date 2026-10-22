"""The drilling rig on the block house of the asteroid levels, and its crane's wreck (sheet P sprites 9 and 11 above 1
and 3 above 39 and 41, 2x2 each: one 48 x 84 picture; the wreck P 47 and 49 in the top pair's place; ground layer;
ASTEROID1 and AST ROCK), polished (2026-10-22, round 33; it replaces wave3_w_works.py's rig_whole(), an upright tripod
on wave3_w_kit.py's old house whose head stood over the house's top pieces, the crane's sprites' place empty, and
wave3_ao_works.py's rig_wreck(), which changed from run to run).

PLACEMENT (the level events, tools/content/tyrevents.py; the enemy data, tools/content/tyrdata.py)

Six enemies, armour 40 each: 332 (P 9, worth 75), 333 (P 11), 334 (P 39), 335 (P 41), 336 (P 1) and 337 (P 3) in
episodes 1-3, 1024-1029 (the same sprites and data) in episode 5. Event 12 ("4-part enemy") puts 334 (39) at (x, y),
335 (41) at x + 24, 336 (1) 28 pixels up the screen and 337 (3) both, and with it event 6 puts 332 (9) and 333 (11) at x
and x + 24, 56 pixels up the screen (d5 -56): the picture whole, as the sheet's rows lay it out. ASTEROID1 t3548, 3604,
3688, 4220, 5116; AST ROCK t2204, 2288 (event 10, ground2, for the crane with d5 -57, event 12 with d5 -1: the same
layout). Each time the six share one link: shot, they go together, 332 and 333 turning to their wrecks (dgr 47 and 49,
dlevel -1: they stay, showing them), the other four dying (the game leaves its slumped wrecks of their models,
tyrian2.c leave_wreck); the maps paint the rig's ruin under the house (ASTEROID1's tiles 429 430 above 439 440: the
stays, the collar and the anchors broken, red embers) and plain floor under the crane. Episode 4's enemies of those
numbers are other things; no episode 6 level places the rig (GREY MOON and VAULT take only ASTEROID2's boss block, link
45). 336 and 337 animate (20 frames each, together): 1 1 5 5 81 81 77 77 43 43 43 43 43 43 77 77 81 81 5 5 and 3 3 7 7
83 83 79 79 45 ...: the drill string going down into the bore and up again; no other enemy (launched ones included)
shows P 1, 3, 5, 7, 43, 45, 77, 79, 81 or 83: frame models. No sprite of these is another's pixels mirrored, turned or
in other ramps.

THE RIG

As the sprites and their 4x upscales draw it (columns and rows of the 48 x 84 picture): the block house of these levels
(P 153 155 above 191 193 in its first frame, the hatches closed: its rows 0-52 are rows 28-80 here; the rig's sprites
draw its slabs, its conduit, its ribbed front; the stays' shadows painted on its roof are left out, the game casts its
own) and on it a derrick drawn leaning up the screen as the sprites draw tall things: at the top (rows 1-6, columns
10-31) a brown plank lying across, its top lit at its left end, its front a darker band, its right end bevelled; under
its middle a brown stem (columns 20-23 of rows 5-11) in front of a dark hub (columns 17-30 of rows 6-13); from the hub
four dark stays (black pipes lit along their left) down to four gold anchor cups on the roof, two at its sides (columns
5-12 and 36-43 of rows 43-50) and two in front (columns 10-19 and 29-38 of rows 56-63); gold clamps on the stays about
half way down (rows 31-38), each showing a gold ear towards the middle; the drill string (columns 22-25) from the hub
straight down into a bore hole in a gold collar (columns 17-30 of rows 41-52, its front a thick lit band, the hole
black); a bent pipe from the plank's left end down the left (columns 10-13) and in along rows 20-23 to the inner left
stay. The frames move the drill string's bit: above the collar in 1 and 3 (its tip at row 40.5), entering the hole in 5
and 7, deeper in 81 83, 77 79 and 43 45 (rows 45, 47, 48.5, 50). The wreck (P 47 49): the plank scorched dark in its
middle (columns 15-27), the stem too, the bent pipe snapped (rows 13-16 gone), the two right stays broken off under the
hub (from row 17; the outer one's stub from row 23 on).

Built as such a rig on polish_block_house.py's house (body(), slabs() with the hatches flush, wells(), ribs(); its vent
left off, under the right stay and its clamp; its conduit (slab j) from under the front left anchor to the front), for
the game's camera (20 degrees from straight down, from the bottom of the screen: a point at height z shows S(z) = (z -
10) tan 20 pixels further up the screen than one on the roof, whose own height the house's layout holds, as
polish_bronze_pump.py and polish_cargo_pod.py build on it): every part is laid out where the sprites draw it, at a
height chosen for it, and moved down the screen by S of that height (at()), so that the camera sees it where the sprite
draws it. The derrick therefore leans back up the screen (its stays from the anchors on the roof, z 12.4, to the hub, z
34; the drill string from the hub to the collar, about 56 degrees off upright; the plank's top 43 pixels over the floor,
under the player's 44), as the bronze pump's shaft and dome do (50 degrees): stood upright, as wave3_w_works.py had it,
the head stood over the house's top pieces and the crane's sprites showed nothing. Its parts: the plank a bevelled beam
(0x17, its lit left end 0x1b, its front and its lower right end 0x15) on a brown stem (the gold's 0x18 / 0x1b / 0x15)
hanging from its front into the hub (a dark collar, 0x15, at its top), the hub a rounded box of dark steel (0x03, lit
0x07) with its back right corner cut off; the stays and the drill string round steel pipes (0x03, lit 0x07); the bent
pipe lighter steel (the house's 0x05, lit 0x07); the clamps gold collars round the stays, each with a short arm (0x15)
to a gold plate lying level beside its stay, towards the middle (the sprites' gold ears); the anchors and the collar
turned (lathes), gold (0x18, lit 0x1b, shaded 0x15, as the pump's), the anchors' sockets and the collar's bore dark
(0x02), the bore 3.4 pixels deep to its floor on the slabs; the drill string's end a gold sleeve (0x15) over a steel
bit tapering to a point (0x07). Painted by how the faces meet the game's light (from the upper left and above). The
house's vent is left off (the right stay and its clamp pass over slab b); the house keeps polish_block_house's
materials (0x0a roof, 0x0c, 0x07, 0x05, 0x06, 0x04, 0x02, 0x08, 0x03).

The crane's wreck: the intact rig again, damaged in the crane's part as P 47 and 49 draw it: the plank's middle and the
stem scorched (0x13, the middle burnt 0x11, along smooth contours of a noise field: the faces finely divided first),
the hub a little; the bent pipe cut away where the camera sees it between rows 13.6 and 17 (its ends torn by noise and
closed burnt), the inner right stay cut away below row 21, the outer right one between rows 20 and 22.6; cut the same
way (only its two crane pieces are exported: when the rig is shot the house's four pieces die, leaving the game's
slumped wrecks of their models over the map's ruin of the rig).

The whole is cut along the planes the camera sees as the sprites' edges (polish_stone_face.view_cut: x = 0 upright; y +
S(z) = 0 and 28, leaning back up the screen; the cuts capped in each part's inside colour, the pieces keeping the uncut
shading), so that each piece holds what the camera sees in its sprite (the crane's pieces the plank, the hub, the bent
pipe and the stays' upper parts, standing over the house's back; the house's top pieces the drill string's lower part,
which their frames move), each piece moved so that its sprite's centre is its origin, every mesh triangulated
(polish_k_pod.triangulate) and its parts joined (polish_deli_boss.join). One whole per frame: the frame models are its
top pieces as that frame shows them (asteroid_rig_tl_5 / _tr_7 ... _tl_43 / _tr_45; the same bounds).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the floor (z 0, the roof at 10).
The whole's origin is the corner where the four house sprites meet (pixel corner 24, 56 of the picture: the block
house's own origin): E(c, r) is the picture's pixel corner (c, r), (c - 24, 56 - r). The pieces' centres: 9 (-12, 42),
11 (12, 42), 1 (-12, 14), 3 (12, 14), 39 (-12, -14), 41 (12, -14); the wreck's as 9's and 11's. Drawn at their origins
(origin) on the ground layer: height=-4 on every line (as the block house's, the pump's and the pod's) sets the house on
the terrain (its walls reach 4 pixels below it).

models.cfg: the model lines stay (asteroid_rig_crane_l / _r / _tl / _tr / _bl / _br, asteroid_rig_wreck_crane_l / _r,
origin); new model lines asteroid_rig_tl_5, _tl_81, _tl_77, _tl_43, asteroid_rig_tr_7, _tr_83, _tr_79, _tr_45 (origin)
and frame lines frame p 5 asteroid_rig_tl_5 ... frame p 45 asteroid_rig_tr_45; the sprite lines of P 9, 11, 1, 3, 39,
41, 47 and 49 get height=-4. Replaces wave3_w_works.py's rig (its section "P 9 11 / 1 3 / 39 41: the drilling rig": RIG,
RIG_ROOF, RIG_HEAD_Z, RIG_RISE, RIG_PLANK_RISE, RIG_DRAWN, side_offset(), torus(), rig_whole() and its
drawn_pieced("asteroid_rig", ...) registration), the last thing wave3_w_works.py builds (delete it: bronze_mats(),
paint_lit(), Drawn and drawn_pieced() served only the works), and wave3_ao_works.py's rig wreck (its section "P 47 49:
the drilling rig's crane, wrecked": RIG, RIG_DMG, rig_wreck() and its works.drawn_pieced("asteroid_rig_wreck", ...)
registration, the asteroid_rig_wreck bullet of its docstring and its works = kit.quiet_import("wave3_w_works") and wkit
lines); the pixels only those read: wave3_w_art.py's RIG, wave3_ao_art.py's RIG_DMG.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each piece's silhouette as the
game's camera sees it, relative to the roof, against its sprite's pixels, the floor they paint round the house left
out), --preview <prefix> (each piece's top and 3/4 views), --whole <prefix> (the uncut rig, frame 1, and its wreck as
<prefix>asteroid_rig.glb and <prefix>asteroid_rig_wreck.glb), --only <model,...>, --stats 1.
"""
import math
import os
import sys

import bmesh
import bpy
import mathutils.noise as noise
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
import polish_block_house as bh  # noqa: E402
from polish_cargo_pod import view_coverage  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_coral_manta import split_contour  # noqa: E402
from polish_stone_face import view_cut  # noqa: E402

H = bh.H                                      # the house's roof
SLAB_TOP = bh.H + bh.PANEL_H                  # the slabs' tops
TILT = math.tan(math.radians(20.0))           # the camera shows a point this much further up the screen per pixel up
LIGHT = Vector((-0.55, 0.45, 0.7)).normalized()   # towards the game's sun (polish_bronze_pump's)

# The pieces: name, sprite, the part of the picture it shows as the camera sees it at the roof's height (x0, x1, y0,
# y1; None: no neighbour that side), its sprite's centre.
PIECES = [("asteroid_rig_crane_l", 9, (None, 0.0, 28.0, None), (-12.0, 42.0)),
          ("asteroid_rig_crane_r", 11, (0.0, None, 28.0, None), (12.0, 42.0)),
          ("asteroid_rig_tl", 1, (None, 0.0, 0.0, 28.0), (-12.0, 14.0)),
          ("asteroid_rig_tr", 3, (0.0, None, 0.0, 28.0), (12.0, 14.0)),
          ("asteroid_rig_bl", 39, (None, 0.0, None, 0.0), (-12.0, -14.0)),
          ("asteroid_rig_br", 41, (0.0, None, None, 0.0), (12.0, -14.0))]
WRECK_PIECES = [("asteroid_rig_wreck_crane_l", 47, (None, 0.0, 28.0, None), (-12.0, 42.0)),
                ("asteroid_rig_wreck_crane_r", 49, (0.0, None, 28.0, None), (12.0, 42.0))]
# The frames of the top pieces (P 1 and 3 and their frames): the sprites, the row where the bit's tip is drawn.
FRAMES = [(1, 3, 40.5), (5, 7, 45.0), (81, 83, 47.0), (77, 79, 48.5), (43, 45, 50.0)]


def E(c, r):
    """A pixel corner (column c, row r) of the 48 x 84 picture in the whole's coordinates."""
    return (c - 24.0, 56.0 - r)


def S(z):
    """How much further up the screen the camera shows a point at height z than one on the roof."""
    return TILT * (z - H)


def at(c, r, z):
    """The point at height z that the camera shows where the sprites draw (c, r)."""
    x, y = E(c, r)
    return Vector((x, y - S(z), z))


def drawn(c0, r0, z0, c1, r1, z1, r):
    """The point drawn at row r on the line drawn from (c0, r0) at height z0 to (c1, r1) at z1 (its height in
    proportion)."""
    t = (r - r0) / (r1 - r0)
    return at(c0 + (c1 - c0) * t, r, z0 + (z1 - z0) * t)


# --- The rig's layout (picture columns and rows as drawn, heights) ------------------------------------------------
PLANK = dict(x0=-13.5, x1=7.5, back_row=1.0, front_row=4.6, top=43.0, bottom=37.6, bevel_x=3.5, bevel_y=2.4)
PLANK_END = dict(x0=1.6, x1=7.6, y0=38.3, y1=40.6, top=37.8, bottom=35.4)   # under its right end (rows 5-7 as drawn)
FLANGE = dict(x0=-8.0, x1=0.5, y0=38.3, y1=39.9, top=37.8, bottom=36.0)     # the stem's dark collar (rows 6-7)
HUB = dict(x0=-7.0, x1=7.0, back_row=7.0, front_row=10.8, top=36.4, bottom=30.4, notch=(4.2, 2.2))
STEM = dict(x=-2.0, top=(6.0, 40.0), bottom=(11.6, 35.4), width=4.0, depth=3.0)
STAY_TOP = (9.5, 34.0)                                     # where the stays and the drill string start in the hub
STAY_R = 1.7
# The anchors (drawn foot centre column and row, plan radii) and the stays (their top's column, their anchor).
ANCHORS = {"l": (8.4, 46.6, 3.5, 3.3), "r": (39.4, 46.5, 3.6, 3.0), "bl": (14.8, 59.8, 4.3, 3.3),
           "br": (33.6, 59.8, 4.3, 3.2)}
ANCHOR_TOP, SOCKET_Z = 13.1, 12.4
STAYS = [("l", 19.7, "l"), ("ml", 20.3, "bl"), ("mr", 26.0, "br"), ("r", 27.75, "r")]
# The clamps on the stays: the row where they are drawn, the side their ear points to (+1 right).
CLAMPS = {"l": (36.0, 1), "ml": (33.2, 1), "mr": (33.0, -1), "r": (35.3, -1)}
# The drill string: its column, the collar's top (where its axis meets it), the bore's floor.
DRILL_C, DRILL_R = 24.0, 1.85
COLLAR = dict(c=24.5, r=46.5, top=14.0, sq=0.9)            # drawn centre of its top, height, plan squash (y / x)
COLLAR_PROFILE = [(3.9, SLAB_TOP + 0.04), (3.9, 13.45), (4.15, 13.85), (4.7, 14.05), (5.3, 13.95), (5.7, 13.6),
                  (6.3, 12.4), (6.85, 11.15), (7.15, 10.3), (7.15, 9.8)]
SLEEVE_ROWS, BIT_ROWS = 2.6, 4.2                            # the sleeve's and the bit's length, as drawn
BIT_R = 2.75
# The bent pipe (as drawn: column, row, height), from under the plank's left end down to the inner left stay.
BENT_R = 1.75


def materials():
    def mat(name, index, metallic=0.3, roughness=0.5):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)
    m = bh.materials(0x0a)
    m["hatch"] = m["roof"]          # frame 1: the hatches as the slabs (one material less)
    m.update({
        "gold": mat("rig_gold", 0x18, 0.45, 0.3),
        "gold_lit": mat("rig_gold_lit", 0x1b, 0.45, 0.28),
        "gold_dark": mat("rig_gold_dark", 0x15, 0.4, 0.34),
        "plank": mat("rig_plank", 0x17, 0.25, 0.42),
        "steel": mat("rig_steel", 0x03, 0.55, 0.32),
        "steel_lit": mat("rig_steel_lit", 0x07, 0.5, 0.3),
        "burnt": mat("rig_burnt", 0x11, 0.15, 0.7),
        "scorched": mat("rig_scorched", 0x13, 0.2, 0.6),
    })
    return m


# --- Helpers -----------------------------------------------------------------------------------------------------

def paint_light(obj, m, top, lit, dark, under=None, lit_at=0.62, dark_at=0.2):
    """Faces by how they meet the light: turned to it `lit`, away from it `dark`, between them `top`."""
    def pick(c, n):
        if under is not None and n.z < -0.55:
            return m[under]
        d = n.dot(LIGHT)
        return m[lit] if d > lit_at else m[dark] if d < dark_at else m[top]
    mk.paint(obj, pick)
    return obj


def pipe(name, a, b, radius, m, top="steel", lit="steel_lit", segments=14, lit_at=0.45):
    """A straight round pipe from a to b, a ring every pixel or so (so that the wreck can break it anywhere)."""
    n = max(2, int((b - a).length / 1.2))
    obj = mk.tube(name, [a.lerp(b, i / n) for i in range(n + 1)], radius, m[top], segments)
    k.smooth(obj, 60)
    mk.paint(obj, lambda c, n: m[lit] if n.dot(LIGHT) > lit_at else None)
    return obj


def collar_on(name, p, d, r_in, r_out, length, m):
    """A short collar round a pipe through p along d."""
    d = d.normalized()
    pts = [p - d * (length / 2 + 0.3), p - d * (length / 2), p + d * (length / 2), p + d * (length / 2 + 0.3)]
    obj = mk.tube(name, pts, r_out, m["gold"], 18, radii=[r_in, r_out, r_out, r_in])
    k.smooth(obj, 50)
    return paint_light(obj, m, "gold", "gold_lit", "gold_dark")


def lathe_at(name, profile, centre, squash, m, segments=36):
    obj = mk.lathe(name, profile, centre, m["gold"], segments, squash=(1.0, squash))
    k.smooth(obj, 50)
    return obj


# --- The house ---------------------------------------------------------------------------------------------------

def conduit(m):
    """Slab j's conduit in clamps (polish_block_house.conduit), from under the front left anchor to the front."""
    c0, c1 = bh.CONDUIT[0], bh.CONDUIT[1]
    x = (bh.P(c0, 0)[0] + bh.P(c1 + 1, 0)[0]) / 2
    y_top = E(0, 60.5)[1]
    y_end = bh.Y_FRONT + bh.EDGE + 0.4
    pts, ups = [], []
    for i in range(7):
        y = y_top + (y_end - y_top) * i / 6
        pts.append(Vector((x, y, H - 0.05)))
        ups.append(Vector((0, 0, 1)))
    pipe_ = mk.bar("conduit", pts, ups, 1.05, 0.85, 0.2, m["conduit"], 14, 2.2)
    k.smooth(pipe_, 50)
    for i in range(2):
        y = y_top - 2.4 - i * 0.5 * (y_top - y_end - 3.6)
        clamp = mk.box(f"clamp{i}", x - 1.35, x + 1.35, y - 0.32, y + 0.32, H - 0.05, H + 0.95, m["shade"])
        mk.bevel(clamp, 0.22, 2, 35)
        mk.shade(clamp, 35)
    return pipe_


def house(m):
    """polish_block_house's house in its first frame (the hatches flush), without its vent, its conduit shortened."""
    bh.body(m)
    hatches = bh.slabs(m, 0.0)
    bh.wells(m, hatches)
    conduit(m)
    bh.ribs(m)
    return [o for o in mk.meshes()]


# --- The derrick -------------------------------------------------------------------------------------------------

def plank(m):
    """The plank lying across the top, its right end bevelled, a block under it; the stem hanging from its front."""
    p = PLANK
    y_back = E(0, p["back_row"])[1] - S(p["top"])
    y_front = E(0, p["front_row"])[1] - S(p["top"])
    outline = [(p["x0"], y_front), (p["x1"], y_front), (p["x1"], y_back - p["bevel_y"]),
               (p["x1"] - p["bevel_x"], y_back), (p["x0"], y_back)]
    obj = mk.prism("plank", outline, p["bottom"], p["top"], m["plank"])
    mk.bevel(obj, 0.55, 2, 35)
    mk.shade(obj, 35)

    def pick(c, n):
        if n.z > 0.9:
            return m["gold_lit"] if c.x < p["x0"] + 2.2 else m["plank"]
        if n.z < -0.5:
            return m["gold_dark"]
        if n.x < -0.6 or (n.z > 0.3 and n.dot(LIGHT) > 0.6):
            return m["gold_lit"]
        return m["gold_dark"]
    mk.paint(obj, pick)
    e = PLANK_END
    end = mk.box("plank_end", e["x0"], e["x1"], e["y0"], e["y1"], e["bottom"], e["top"], m["gold_dark"])
    mk.bevel(end, 0.4, 2, 35)
    mk.shade(end, 35)
    paint_light(end, m, "gold_dark", "gold", "gold_dark")
    f = FLANGE
    flange = mk.box("stem_flange", f["x0"], f["x1"], f["y0"], f["y1"], f["bottom"], f["top"], m["gold_dark"])
    mk.bevel(flange, 0.35, 2, 35)
    mk.shade(flange, 35)
    paint_light(flange, m, "gold_dark", "gold", "gold_dark", lit_at=0.8)
    # The stem: a square bar from the plank's front down into the hub.
    s = STEM
    a = at(s["x"] + 24.0, s["top"][0], s["top"][1])
    b = at(s["x"] + 24.0, s["bottom"][0], s["bottom"][1])
    d = (b - a).normalized()
    side = Vector((1.0, 0.0, 0.0))
    up = d.cross(side).normalized()
    if up.z < 0:
        up = -up
    corners = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    rings = []
    for q in (a - d * 0.8, b + d * 0.6):
        rings.append([q + side * (u * s["width"] / 2) + up * (v * s["depth"] / 2) for u, v in corners])
    stem = k.loft("stem", rings, m["gold"])
    mk.bevel(stem, 0.4, 2, 35)
    mk.shade(stem, 35)
    paint_light(stem, m, "gold", "gold_lit", "gold_dark")
    return [obj, end, flange, stem]


def hub(m):
    h = HUB
    y_back = E(0, h["back_row"])[1] - S(h["top"])
    y_front = E(0, h["front_row"])[1] - S(h["top"])
    nx, ny = h["notch"]         # its back right corner cut off (the sprites draw nothing at columns 28-31 of rows 8-9)
    outline = [(h["x0"], y_front), (h["x1"], y_front), (h["x1"], y_back - ny), (nx, y_back), (h["x0"], y_back)]
    obj = mk.prism("hub", outline, h["bottom"], h["top"], m["steel"])
    mk.bevel(obj, 1.1, 3, 35)
    mk.shade(obj, 35)
    paint_light(obj, m, "steel", "steel_lit", "steel", lit_at=0.75)
    return obj


def anchors(m):
    out = []
    for name, (c, r, rx, ry) in ANCHORS.items():
        x, y = E(c, r)
        y -= S(11.6)
        scale = rx / 3.6
        prof = [(0.01 * scale, 9.9), (3.6 * scale, 9.9), (3.6 * scale, 10.85), (3.35 * scale, 11.55),
                (2.8 * scale, 12.55), (2.3 * scale, ANCHOR_TOP), (1.85 * scale, ANCHOR_TOP + 0.05),
                (1.55 * scale, ANCHOR_TOP - 0.25), (1.5 * scale, SOCKET_Z), (0.01 * scale, SOCKET_Z)]
        cup = lathe_at(f"anchor_{name}", prof, (x, y), ry / rx, m)

        def pick(cc, n, x=x, y=y, scale=scale):
            if math.hypot(cc.x - x, (cc.y - y) * rx / ry) < 1.6 * scale and cc.z < ANCHOR_TOP - 0.1:
                return m["well"]
            d = n.dot(LIGHT)
            return m["gold_lit"] if d > 0.72 else m["gold_dark"] if d < 0.3 else m["gold"]
        mk.paint(cup, pick)
        out.append(cup)
    return out


def socket(name):
    c, r, _, _ = ANCHORS[name]
    x, y = E(c, r)
    return Vector((x, y - S(11.6), SOCKET_Z))


def stays(m, skip=None):
    """The four stays from the hub to the anchors, the clamps on them; returns their lines (top, bottom)."""
    out, lines = [], {}
    for name, c_top, anchor in STAYS:
        a = at(c_top, STAY_TOP[0], STAY_TOP[1])
        b = socket(anchor) + Vector((0.0, 0.0, -0.4))
        lines[name] = (a, b)
        out.append(pipe(f"stay_{name}", a, b, STAY_R, m))
        # The clamp: a collar round it where its drawn line crosses the clamp's row, an arm and a knob to the middle.
        row, side = CLAMPS[name]
        ca, cr = c_top, STAY_TOP[0]
        anc = ANCHORS[anchor]
        q = drawn(ca, cr, STAY_TOP[1], anc[0], anc[1] - 0.4, SOCKET_Z - 0.4, row)
        d = b - a
        out.append(collar_on(f"clamp_{name}", q, d, STAY_R + 0.25, STAY_R + 0.62, 1.5, m))
        # its ear: a gold plate lying level beside the stay, towards the middle
        ear = q + Vector((side * 2.6, 0.0, -0.2))
        arm = mk.tube(f"clamp_{name}_arm", [q, q.lerp(ear, 0.5), ear], 0.7, m["gold_dark"], 10)
        k.smooth(arm, 50)
        out.append(arm)
        plate = mk.ball(f"clamp_{name}_ear", tuple(ear), (1.75, 2.15, 0.75), m["gold"], 20, 10)
        paint_light(plate, m, "gold", "gold_lit", "gold_dark", lit_at=0.7, dark_at=0.35)
        out.append(plate)
    return out, lines


def drill_axis():
    """The drill string's axis: from its top in the hub to where it meets the collar's top (as drawn: column DRILL_C,
    rows STAY_TOP[0] and COLLAR's), and the drawn row of any point on it."""
    a = at(DRILL_C, STAY_TOP[0], STAY_TOP[1])
    b = at(DRILL_C, COLLAR["r"], COLLAR["top"])

    def point(row):
        return a + (b - a) * ((row - STAY_TOP[0]) / (COLLAR["r"] - STAY_TOP[0]))
    return a, b, point


def drill(m, tip_row):
    """The drill string from the hub down its axis, a gold sleeve and a steel bit at its end, the tip drawn at
    tip_row."""
    a, b, point = drill_axis()
    sleeve_top = point(tip_row - SLEEVE_ROWS - BIT_ROWS)
    sleeve_end = point(tip_row - BIT_ROWS)
    tip = point(tip_row)
    d = (tip - a).normalized()
    parts = [pipe("drill", a, sleeve_top + d * 0.4, DRILL_R, m)]
    sleeve = mk.tube("drill_sleeve", [sleeve_top, sleeve_top + d * 0.35, sleeve_end - d * 0.35, sleeve_end], BIT_R,
                     m["gold_dark"], 18, radii=[DRILL_R + 0.3, BIT_R, BIT_R, BIT_R - 0.15])
    k.smooth(sleeve, 50)
    paint_light(sleeve, m, "gold_dark", "gold", "gold_dark", lit_at=0.55)
    parts.append(sleeve)
    n = 7
    pts = [sleeve_end.lerp(tip, i / (n - 1)) for i in range(n)]
    radii = [BIT_R - 0.15, BIT_R - 0.35, BIT_R * 0.82, BIT_R * 0.66, BIT_R * 0.46, BIT_R * 0.24, 0.05]
    bit = mk.tube("drill_bit", pts, BIT_R, m["steel_lit"], 18, radii=radii)
    k.smooth(bit, 60)
    mk.paint(bit, lambda c, nn: m["steel"] if nn.dot(LIGHT) < 0.25 else None)
    parts.append(bit)
    return parts


def wellhead(m):
    """The gold collar round the bore, its bore and floor dark."""
    c = COLLAR
    x, y = E(c["c"], c["r"])
    y -= S(c["top"])
    obj = lathe_at("collar", [(0.01, COLLAR_PROFILE[0][1])] + COLLAR_PROFILE + [(0.01, COLLAR_PROFILE[-1][1])],
                   (x, y), c["sq"], m, 48)

    def pick(cc, n):
        rr = math.hypot(cc.x - x, (cc.y - y) / c["sq"])
        if rr < 4.0 and cc.z < 13.6:
            return m["well"]
        d = n.dot(LIGHT)
        return m["gold_lit"] if d > 0.74 else m["gold_dark"] if d < 0.32 else m["gold"]
    mk.paint(obj, pick)
    return obj


def bent_pipe(m, lines):
    """The bent pipe from under the plank's left end down the left and in to the inner left stay."""
    a, b = lines["ml"]
    # where it meets the stay: the stay's point drawn at row 22.3
    c_top, anchor = 20.3, ANCHORS["bl"]
    join_pt = drawn(c_top, STAY_TOP[0], STAY_TOP[1], anchor[0], anchor[1] - 0.4, SOCKET_Z - 0.4, 22.3)
    z0, z1 = 39.8, join_pt.z

    def z_of(row):
        return z0 + (z1 - z0) * (row - 4.5) / (22.3 - 4.5)
    path = [at(12.0, 4.8, z0), at(12.0, 8.0, z_of(8.0)), at(12.0, 13.0, z_of(13.0)), at(12.05, 17.5, z_of(17.5)),
            at(12.5, 20.2, z_of(20.2)), at(13.8, 21.7, z_of(21.7)), at(15.6, 22.3, z_of(22.3) + 0.15),
            at(17.4, 22.35, z_of(22.3) + 0.05), join_pt]
    dense = mk.chaikin([tuple(p) for p in path], 2, closed=False)
    obj = mk.tube("bent_pipe", dense, BENT_R, m["groove"], 14)
    k.smooth(obj, 60)
    mk.paint(obj, lambda c, n: m["shade"] if n.dot(LIGHT) > 0.45 else None)
    return obj


# --- Build -------------------------------------------------------------------------------------------------------

def build_whole(m, tip_row):
    parts = house(m)
    parts += plank(m)
    parts.append(hub(m))
    parts += anchors(m)
    s, lines = stays(m)
    parts += s
    parts.append(bent_pipe(m, lines))
    parts.append(wellhead(m))
    parts += drill(m, tip_row)
    for obj in parts:
        mk.apply(obj)
    bpy.context.view_layer.update()
    return parts


CAPS = {"house": "seam", "slab": "seam", "hatch": "seam", "rib": "seam", "bolt": "seam", "hinge": "seam",
        "conduit": "seam", "clamp": "gold_dark", "anchor": "gold_dark", "collar": "gold_dark", "plank": "gold_dark",
        "stem": "gold_dark", "drill_sleeve": "gold_dark"}


def cap_of(obj, m):
    for prefix in sorted(CAPS, key=len, reverse=True):
        if obj.name.startswith(prefix):
            return m[CAPS[prefix]]
    return m["steel"]


def rig_mask(sheets, sprites):
    """The sprites' pixels placed as the levels place them (9 11 / 1 3 / 39 41), the floor the house's sprites paint
    round it (left of column 4, right of column 42, below row 80) left out."""
    mask = [[False] * 48 for _ in range(84)]
    for i, sprite in enumerate(sprites):
        part = k.sprite_mask(os.path.join(sheets, "enemy_P.png"), sprite)
        ox, oy = (i % 2) * 24, (i // 2) * 28
        for y in range(28):
            for x in range(24):
                mask[oy + y][ox + x] = part[y][x] and (oy + y < 28 or (4 <= ox + x <= 42 and oy + y <= 80))
    return mask


def piece_mask(sheets, sprite, centre):
    part = k.sprite_mask(os.path.join(sheets, "enemy_P.png"), sprite)
    c0, r0 = int(centre[0] - 12 + 24), int(56 - centre[1] - 14)
    return [[part[y][x] and (r0 + y < 28 or (4 <= c0 + x <= 42 and r0 + y <= 80)) for x in range(24)]
            for y in range(28)]


def export(parts, name, options):
    out = mk.outdir(options)
    drop_unused(parts)
    triangulate(parts)
    if "stats" in options:
        for obj in sorted(parts, key=lambda o: -mk.triangles([o]))[:10]:
            print("    %-22s %6d" % (obj.name, mk.triangles([obj])))
    parts = [join(parts, name)]
    parts[0].data.name = name
    bpy.context.scene.view_settings.view_transform = "Standard"
    mk.report(name, parts, os.path.join(out, name + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + name, parts)
    for obj in parts:
        data = obj.data
        bpy.data.objects.remove(obj)
        if data.users == 0:
            bpy.data.meshes.remove(data)


def pieces(whole, specs, m, options, sheets, suffix=None):
    only = options["only"].split(",") if "only" in options else None
    for name, sprite, box, centre in specs:
        model = name if suffix is None else "%s_%d" % (name, suffix[name])
        if only and model not in only:
            continue
        parts = [p for p in (view_cut(src, box, cap_of(src, m), H) for src in whole) if p is not None]
        mk.transform(parts, Matrix.Translation((-centre[0], -centre[1], 0.0)))
        bpy.context.view_layer.update()
        for src in whole:
            src.hide_render = True
        if sheets:
            s = sprite if suffix is None else suffix[name]
            mk.compare("%s (P %d) as the camera sees it" % (model, s), view_coverage(parts, 24, 28, (-12.0, 14.0)),
                       piece_mask(sheets, s, centre))
        export(parts, model, options)
        for src in whole:
            src.hide_render = False


def build():
    options = k.args()
    only = options["only"].split(",") if "only" in options else None
    sheets = options.get("check")
    for i, (s_tl, s_tr, tip) in enumerate(FRAMES):
        if i == 0:
            specs, suffix = PIECES, None
        else:
            specs = PIECES[2:4]
            suffix = {"asteroid_rig_tl": s_tl, "asteroid_rig_tr": s_tr}
        names = [n if suffix is None else "%s_%d" % (n, suffix[n]) for n, _, _, _ in specs]
        if only and not any(n in only for n in names):
            continue
        k.reset()
        m = materials()
        whole = build_whole(m, tip)
        triangulate(whole)
        if i == 0:
            print("whole rig: %d triangles, %d objects" % (mk.triangles(whole), len(whole)))
            if sheets:
                mk.compare("whole rig as the camera sees it (P 9 11 / 1 3 / 39 41, the floor left out)",
                           view_coverage(whole, 48, 84, E(0, 0)), rig_mask(sheets, [9, 11, 1, 3, 39, 41]))
            if "whole" in options:
                mk.export(whole, options["whole"] + "asteroid_rig.glb")
        pieces(whole, specs, m, options, sheets, suffix)
    if only and not any(name in only for name, _, _, _ in WRECK_PIECES):
        return
    k.reset()
    m = materials()
    whole = wreck(build_whole(m, FRAMES[0][2]), m)
    triangulate(whole)
    print("whole wreck: %d triangles" % mk.triangles(whole))
    if "whole" in options:
        mk.export(whole, options["whole"] + "asteroid_rig_wreck.glb")
    pieces(whole, WRECK_PIECES, m, options, sheets)


# --- The crane's wreck (P 47 49) ---------------------------------------------------------------------------------

def break_pipe(obj, rows, m, seed):
    """Takes away the part of a pipe the camera sees between the rows (r0, r1) (the planes y + S(z) = 56 - r, torn by
    noise along them) and closes its torn ends in burnt colour."""
    r0, r1 = rows
    y_hi, y_lo = 56.0 - r0, 56.0 - r1
    bm = bmesh.new()
    bm.from_mesh(obj.data)

    def inside(co):
        jag = 0.55 * noise.noise(Vector((co.x * 1.9, co.y * 1.3 + co.z * 0.7, seed)))
        yv = co.y + S(co.z)
        return y_lo + jag < yv < y_hi + jag
    doomed = [f for f in bm.faces if inside(f.calc_center_median())]
    bmesh.ops.delete(bm, geom=doomed, context="FACES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    edges = sorted((e for e in bm.edges if len(e.link_faces) == 1),
                   key=lambda e: tuple(sorted((tuple(e.verts[0].co), tuple(e.verts[1].co)))))
    filled = bmesh.ops.holes_fill(bm, edges=edges, sides=0)["faces"]
    slot = mk.slot_of(obj, m["burnt"])
    for f in filled:
        f.material_index = slot
        f.smooth = False
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def scorch(obj, m, field, levels=((0.42, "scorched"), (0.78, "burnt")), levels_n=2):
    """Paints an object's faces where a field over its points rises over the levels (cut along its smooth contours,
    the faces first divided finely so the contours follow the field): scorched and burnt."""
    mod = obj.modifiers.new("fine", "SUBSURF")
    mod.subdivision_type = "SIMPLE"
    mod.levels = mod.render_levels = levels_n
    mk.apply(obj)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    vals = {"f": {v: field(v.co) for v in bm.verts}}
    for t, _ in levels:
        split_contour(bm, vals, "f", t)
    slots = [(t, mk.slot_of(obj, m[name])) for t, name in levels]
    for f in bm.faces:
        v = sum(vals["f"][q] for q in f.verts) / len(f.verts)
        for t, slot in slots:
            if v > t + 1e-6:
                f.material_index = slot
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def wreck(parts, m):
    """The crane's part damaged as P 47 and 49 draw it: the plank's middle and the stem scorched, the bent pipe
    snapped, the inner right stay broken off under the hub, the outer one broken through."""
    by_name = {o.name: o for o in parts}

    def burn(co):
        # strongest over the plank's middle (columns 15-27: x -9 .. 3), torn by noise
        centre = math.exp(-((co.x + 3.0) / 6.2) ** 2)
        return 1.45 * centre + 0.42 * noise.noise(Vector((co.x * 0.42, co.y * 0.42 + 7.0, co.z * 0.42)))
    for name in ("plank", "plank_end", "stem_flange", "stem"):
        scorch(by_name[name], m, burn)
    scorch(by_name["hub"], m, lambda co: 0.6 * burn(co), levels_n=1)
    break_pipe(by_name["bent_pipe"], (13.6, 17.0), m, 1.0)
    break_pipe(by_name["stay_mr"], (21.0, 70.0), m, 2.0)
    break_pipe(by_name["stay_r"], (20.0, 22.6), m, 3.0)
    for obj in parts:
        mk.apply(obj)
    return parts


if __name__ == "__main__":
    build()
