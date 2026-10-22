"""ASTEROID?'s small block with a lid over a well (sheet P sprite 279 and its frames 281 245 283 237 239, 2x2: 24 x 28
pixels; enemy 198, armour 40), the same block standing open (P 53, enemy 457, armour 20) and the burnt block both leave
(P 87), polished (2026-10-22, round 37; it replaces wave3_w.py's small_block(), block_door() and block_slot(): a slab with
a hole and a plate always a little open, and wave3_ao_works.py's block_wreck(), the same slab pixelated and sunk).
models.cfg: model block_door / block_slot enemies/*.glb origin (unchanged), model block_wreck (unchanged), new model
block_door_281 / _245 / _283 / _237 / _239 enemies/*.glb origin and frame p 281 block_door_281 ... frame p 239
block_door_239; the sprite lines of P 279, 53 and 87 get height=-4.

Where the level puts them (ASTEROID?'s events, tools/content/tyrevents.py; the enemy data, tools/content/tyrdata.py): 198
five times (t160 at x 90, 114, 186, 210 and t1056 at 138, event 6, the ground), 457 twice (t384 at x 138, t552 at 186),
always on the plain asteroid floor (tile 372, terrain flat 0): the sprites' lower half (rows 14-27), their left columns
and the shadow at their right (columns 19-23) are the map's floor and the game's shadow, left out: the block is the rest
(columns 4-18, rows 0-13). 198 is still in the data (animate 0), but the events animate it: t200-220 event 24 (ani 10,
start 2, once) plays 279 281 281 281 245 245 245 283 283 283, the lid lifting off its well and staying open (283), then
event 24 (ani 19, start 12, when firing) and event 31 (launchfreq 40) make it play 283 237 237 239 239 237 237 283 each
time it launches: the seeker mine (enemy 199, P 171: polish_seeker_mine.py) rising in the well, its cross glowing red
(237) and orange (239); t1096 the same for the block of t1056 (launchfreq 1, then 10). No other enemy shows P 279 281 245
283 237 239 53 or 87; so the frames are frame models. 457 never animates; it launches the slot rocket (enemy 458, P 19:
polish_launched_last.py) every 20 ticks onto ground 2. Shot, both turn into P 87 (dgr, dlevel -1: it stays). Not in
episode 6. No sprite of these is another's pixels mirrored or recoloured.

As the sprites and their 4x upscales draw it (ramp 0's greys; the sprite's columns and rows): a squat block of rounded
concrete (columns 4-18, rows 0-13), its corners rounded, its edges rounded and lit along its left and back (0x0a-0x0e),
darker at its right (0x04), its front a row (13); in its top a square lid (columns 8-15, rows 3-11, 0x09, its left and
far edges lit 0x0e-0x0b) in a well whose rim is dark (columns 7 and 16, rows 2 and 12); a lug on each side (columns 4-6
and 16-18, rows 6-9, lit 0x0c-0x0d). The frames lift the lid on its far edge: 281 (its near edge at row 9 over a dark
slit), 245 (row 7), 283 (row 5: a lit band over the open well); 237 and 239 the open well with the mine's glowing cross
in it (rows 6-9). P 53: the well open (rows 7-11, near black), the lid standing up over its far half and tilted back
(rows 0-5, its face 0x09, its edges lit), dark arms at its sides. P 87: the lid gone, the block's top a burnt crater
(columns 5-18, rows 1-12, 0x01-0x03) with rubble in it, its rim broken.

Built for the game's camera where the world has it (one sprite: no pieces to cut): a block of BLOCK_H lofted from rounded
rectangles (polish_block_house.rrect) up its walls (from SKIRT under the ground), over its rounded edge (EDGE) to its top,
in round the well's rim and down the well's walls to its floor, so that the camera (20 degrees from straight down, from
the bottom of the screen) sees its top where the sprite draws rows 0-11, its rounded edge as row 12 and its front as row
13; the lugs bevelled blocks on its side rims; the lid a chamfered plate in the well, hinged on two knuckles at its far
edge and swung up LIDS degrees in the frames (23, 38.5, 52: where the camera sees its near edge at rows 9, 7 and 5); in
237 and 239 polish_seeker_mine's mine (its frames 190 and 247, a little smaller: MINE) rising in the well. The block
house's paint (polish_block_house: its roof, lit, shade, wall and well greys), the lid a shade lighter. P 53: the same
block, the well open, its lid (SLOT_LID) lifted on two brackets at the block's back edge and swung up 30 degrees over the
well (SLOT_HINGE), so that the camera sees its lit top where the sprite draws it (rows 0-5) and the dark well before it.
P 87: the block with a ragged crater (CRATER: its rim jagged and sunk) instead of the well, charred inside, chunks of the
lid and the rim in it.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground (z 0); the origin is
the sprite's middle (column c's left edge x = c - 12; a point of the world at height z is seen at y + z tan 20, row
r's top edge at 14 - r). height=-4 sets the blocks on the terrain (they reach SKIRT below it).

Replaces wave3_w.py (all of it: the small blocks were all it still built) and wave3_ao_works.py's section "P 87: the
small block's wreck" (DOOR, DOOR_DMG, block_wreck()); with polish_tan_launcher.py's wreck that was all wave3_ao_works.py
built: it goes, with wave3_ao_kit.py and wave3_ao_art.py (nothing else imports them), and wave3_w_kit.py and
wave3_w_art.py go with wave3_w.py and wave3_w_launcher.py (nothing else imports them).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each model's outline as the
camera sees it against its sprite's own pixels: columns 4-18 of rows 0-13), --preview <prefix>, --only <model,...>.
"""
import math
import os
import sys

import bpy
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_asteroid_kit as ak  # noqa: E402
from polish_block_house import rrect  # noqa: E402
import polish_seeker_mine as mine  # noqa: E402

TAN_T = ak.TAN_T
X0, X1 = -8.0, 7.0               # the block's sides (columns 4-18)
Y0, Y1 = 0.0, 12.5               # its front and back (the camera sees its back edge at row 0's top)
RADII = (2.6, 2.4, 1.4, 1.4)     # its corners' radii: front left, front right, back right, back left
BLOCK_H = 4.0                    # its top
EDGE = 0.75                      # its rounded top edge: width and drop
SKIRT = -4.0
WELL = (-4.3, 4.3, 0.95, 9.75)   # the well's opening (x0, x1, y0, y1): the lid's place, columns 8-15 of rows 3-11
WELL_R = 0.45                    # its corners' radius
WELL_FLOOR = 0.4                 # its floor
LID = (-4.0, 4.0, 1.15, 9.45)    # the lid closed (x0, x1, y0, y1)
LID_T = 0.75                     # its thickness (its top 0.2 over the block's)
HINGE = (9.5, BLOCK_H + 0.05)    # its hinge (y, z)
LIDS = {279: 0.0, 281: 23.0, 245: 38.5, 283: 52.0, 237: 52.0, 239: 52.0}
MINE = {237: 209, 239: 266}      # the mine in the well: its frame
MINE_AT = ((0.0, 5.6, 0.45), 0.86)   # where it rises in the well (its middle) and its scale
LUGS = [(-7.55, -5.0), (4.75, 6.6)]  # the lugs: x0, x1 (rows 6-9)
LUG_Y = (2.6, 6.3)
SLOT_LID = (-4.0, 4.0, 8.3, 0.75)    # P 53's lid: x0, x1, its length, its thickness
SLOT_HINGE = (12.3, BLOCK_H + 0.65, 30.0)    # its hinge on the block's back edge (y, z) and how far it is swung up
CRATER = (-6.2, 6.0, 0.55, 11.2)     # P 87's crater (x0, x1, y0, y1)


def materials():
    def m(name, index, metallic=0.3, roughness=0.55, glow=0.0):
        return ak.pal("block_" + name, index, metallic, roughness, glow)
    return {"top": m("top", 0x0a), "lit": m("lit", 0x0c), "shade": m("shade", 0x07), "wall": m("wall", 0x06),
            "front": m("front", 0x07), "well": m("well", 0x02, 0.2, 0.7), "floor": m("floor", 0x01, 0.1, 0.8),
            "lid": m("lid", 0x0a, 0.35, 0.45), "lid_lit": m("lid_lit", 0x0d, 0.35, 0.4),
            "lid_dark": m("lid_dark", 0x06, 0.3, 0.55), "hinge": m("hinge", 0x05, 0.45, 0.4),
            "soot": m("soot", 0x03, 0.1, 0.8), "char": m("char", 0x01, 0.05, 0.9), "rubble": m("rubble", 0x05, 0.1, 0.8)}


# --- The block ---------------------------------------------------------------------------------------------------------

def block(m, hole=WELL, floor=WELL_FLOOR, rim=None, name="block", hole_r=WELL_R):
    """The block: lofted from rounded rectangles up its walls, over its rounded top edge, in to the hole's rim and down
    the hole's walls to its floor (rim(x, y): how far the hole's rim sinks, for the crater)."""
    steps = 6
    hx0, hx1, hy0, hy1 = hole
    rings = [rrect(X0, X1, Y0, Y1, RADII, SKIRT, steps), rrect(X0, X1, Y0, Y1, RADII, BLOCK_H - EDGE, steps)]
    for a in (30, 60, 90):
        t = math.radians(a)
        inset = EDGE * (1 - math.cos(t))
        rings.append(rrect(X0 + inset, X1 - inset, Y0 + inset, Y1 - inset, [max(r - inset, 0.05) for r in RADII],
                           BLOCK_H - EDGE + EDGE * math.sin(t), steps))
    inner = [rrect(hx0 - 0.25, hx1 + 0.25, hy0 - 0.25, hy1 + 0.25, [hole_r + 0.25] * 4, BLOCK_H, steps),
             rrect(hx0, hx1, hy0, hy1, [hole_r] * 4, BLOCK_H - 0.25, steps),
             rrect(hx0, hx1, hy0, hy1, [hole_r] * 4, floor, steps)]
    if rim is not None:
        for ring in inner[:2]:
            for p in ring:
                p.z -= rim(p.x, p.y)
    rings += inner
    obj = k.loft(name, rings, m["wall"], start_point=((X0 + X1) / 2, (Y0 + Y1) / 2, SKIRT),
                 end_point=((hx0 + hx1) / 2, (hy0 + hy1) / 2, floor))

    def pick(c, n):
        inside = hx0 - 0.3 <= c.x <= hx1 + 0.3 and hy0 - 0.3 <= c.y <= hy1 + 0.3
        if inside and c.z < BLOCK_H - 0.2:
            return m["floor"] if n.z > 0.6 else m["well"]
        if inside:
            return m["well"] if n.z < 0.9 else m["top"]
        if n.z > 0.95:
            return m["top"]
        if n.z > 0.25:
            return m["lit"] if (n.x < -0.25 or n.y > 0.25) else m["shade"]
        if n.y < -0.6:
            return m["front"]
        return m["wall"]
    mk.paint(obj, pick)
    mk.shade(obj, 35)
    return obj


def lugs(m):
    out = []
    for i, (x0, x1) in enumerate(LUGS):
        lug = mk.box("lug%d" % i, x0, x1, LUG_Y[0], LUG_Y[1], BLOCK_H - 0.3, BLOCK_H + 0.55, m["top"])
        mk.bevel(lug, 0.3, 2, 35)
        mk.shade(lug, 35)
        mk.paint(lug, lambda c, n: m["lit"] if n.z > 0.95 or ((n.x < -0.3 or n.y > 0.3) and n.z > 0.2) else
                 m["shade"] if n.z > 0.2 else None)
        out.append(lug)
    return out


def plate(name, x0, x1, y0, y1, z0, z1, m):
    """A chamfered plate, its top lit along its left and far edges as the sprites draw the lid."""
    obj = mk.box(name, x0, x1, y0, y1, z0, z1, m["lid"])
    mk.bevel(obj, 0.22, 1, 35)
    mk.shade(obj, 35)
    mk.paint(obj, lambda c, n: m["lid"] if n.z > 0.95 else m["lid_lit"] if (n.x < -0.25 or n.y > 0.25) and n.z > 0.2
             else m["lid_dark"])
    return obj


def lid(m, angle):
    """The lid in the well, hinged at its far edge and swung up angle degrees, its knuckles on the hinge."""
    x0, x1, y0, y1 = LID
    parts = [plate("lid", x0, x1, y0, y1, BLOCK_H - LID_T + 0.2, BLOCK_H + 0.2, m)]
    hy, hz = HINGE
    for i, x in enumerate((-2.7, 2.7)):
        knuckle = ak.beam("knuckle%d" % i, (x - 0.8, hy, hz), (x + 0.8, hy, hz), ak.disc_profile(0.42, 10),
                          (0, 0, 1), m["hinge"])
        k.smooth(knuckle, 50)
        parts.append(knuckle)
    rot = (Matrix.Translation((0.0, hy, hz)) @ Matrix.Rotation(-math.radians(angle), 4, "X") @
           Matrix.Translation((0.0, -hy, -hz)))
    parts[0].data.transform(rot)
    return parts


def mine_in_well(sprite, m):
    """polish_seeker_mine's mine (the frame of the block's frame), a little smaller, rising in the well; its steel in
    the block's greys (the well hides most of it: a piece keeps to 15 materials), its lamp its own."""
    frame = next(f for f in mine.FRAMES if f[0] == MINE[sprite])
    parts = mine.build_mine(frame, prefix="well_mine")
    swap = {"mine_steel_d": m["lid_dark"], "mine_steel": m["shade"], "mine_steel_l": m["top"], "mine_bezel": m["well"],
            "mine_stud": m["hinge"], "mine_warm": m["lit"]}
    for obj in parts:
        for i, mat in enumerate(obj.data.materials):
            key = next((kk for kk in sorted(swap, key=len, reverse=True) if mat.name.startswith(kk)), None)
            if key is not None:
                obj.data.materials[i] = swap[key]
    (cx, cy, cz), s = MINE_AT
    (mx, my, mz), _ = mine.BALL
    mk.transform(parts, Matrix.Translation((cx, cy, cz)) @ Matrix.Scale(s, 4) @ Matrix.Translation((-mx, -my, -mz)))
    return parts


# --- P 53: the block standing open ---------------------------------------------------------------------------------------

def slot_lid(m):
    """P 53's lid: lifted on two brackets at the block's back edge and swung up SLOT_HINGE degrees over the open well,
    its top lit to the sun as the sprite draws it (rows 0-5), the well before it."""
    x0, x1, length, t = SLOT_LID
    hy, hz, angle = SLOT_HINGE
    lid_obj = plate("slot_lid", x0, x1, hy - length, hy, hz - t / 2, hz + t / 2, m)
    rot = (Matrix.Translation((0.0, hy, hz)) @ Matrix.Rotation(-math.radians(angle), 4, "X") @
           Matrix.Translation((0.0, -hy, -hz)))
    lid_obj.data.transform(rot)
    parts = [lid_obj]
    for i, x in enumerate((x0 + 0.9, x1 - 0.9)):
        bracket = mk.box("bracket%d" % i, x - 0.5, x + 0.5, hy - 0.8, hy + 0.15, BLOCK_H - 0.4, hz + 0.25,
                         m["hinge"])
        mk.bevel(bracket, 0.2, 1, 35)
        mk.shade(bracket, 35)
        parts.append(bracket)
    axle = ak.beam("axle", (x0 + 0.3, hy - 0.3, hz), (x1 - 0.3, hy - 0.3, hz), ak.disc_profile(0.35, 10), (0, 0, 1),
                   m["hinge"])
    k.smooth(axle, 50)
    parts.append(axle)
    return parts


# --- P 87: the burnt block -----------------------------------------------------------------------------------------------

def ragged(x, y):
    """How far the crater's rim is broken down (jagged, the same every run)."""
    return 0.9 + 0.55 * math.sin(2.3 * x + 1.1 * y) + 0.4 * math.sin(1.3 * x - 2.7 * y + 0.7)


def wreck(m):
    obj = block(m, CRATER, 0.3, ragged, "wreck", 3.2)
    x0, x1, y0, y1 = CRATER

    def pick(c, n):
        inside = x0 - 0.6 <= c.x <= x1 + 0.6 and y0 - 0.6 <= c.y <= y1 + 0.6
        if inside and c.z < BLOCK_H + 0.1:
            return m["char"] if c.z < BLOCK_H - 1.2 else m["soot"]
        if n.z > 0.3 and (x0 - 1.6 <= c.x <= x1 + 1.6 and y0 - 1.2 <= c.y <= y1 + 1.4):
            return m["soot"] if (math.sin(3.1 * c.x) + math.sin(2.3 * c.y)) > -0.6 else None
        return None
    mk.paint(obj, pick)
    parts = [obj]
    chunks = [((-3.2, 3.6), (1.6, 1.2, 0.7), 20.0), ((2.4, 6.8), (1.3, 1.1, 0.8), -35.0),
              ((0.2, 9.0), (1.7, 0.9, 0.6), 10.0), ((-4.4, 8.2), (1.0, 0.9, 0.7), 50.0),
              ((3.6, 2.4), (1.1, 0.8, 0.6), -15.0)]
    for i, ((x, y), (sx, sy, sz), turn) in enumerate(chunks):
        chunk = mk.box("chunk%d" % i, -sx, sx, -sy, sy, -sz, sz, m["rubble"])
        chunk.data.transform(Matrix.Translation((x, y, 0.3 + sz * 0.6)) @ Matrix.Rotation(math.radians(turn), 4, "Z") @
                             Matrix.Rotation(math.radians(18.0 + 7 * i), 4, "X"))
        mk.bevel(chunk, 0.2, 1, 35)
        mk.shade(chunk, 35)
        mk.paint(chunk, lambda c, n: m["soot"] if n.z < 0.5 else None)
        parts.append(chunk)
    return parts


# --- Build -------------------------------------------------------------------------------------------------------------

def own_mask(sheets, sprite):
    """The block's own pixels: its sprite's pixels in columns 4-18 of rows 0-13 (the floor round it and its shadow are
    the map's and the game's)."""
    pix = k.sprite_mask(os.path.join(sheets, "enemy_P.png"), sprite)
    return [[pix[r][c] and 4 <= c <= 18 and r <= 13 for c in range(24)] for r in range(28)]


def models():
    out = [("block_door" if s == 279 else "block_door_%d" % s, s) for s in (279, 281, 245, 283, 237, 239)]
    return out + [("block_slot", 53), ("block_wreck", 87)]


def build_model(sprite, m):
    if sprite == 87:
        return wreck(m) + lugs(m)
    parts = [block(m)] + lugs(m)
    if sprite == 53:
        return parts + slot_lid(m)
    parts += lid(m, LIDS[sprite])
    if sprite in MINE:
        parts += mine_in_well(sprite, m)
    return parts


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    for name, sprite in models():
        if only and name not in only:
            continue
        k.reset()
        bpy.context.scene.view_settings.view_transform = "Standard"
        m = materials()
        parts = build_model(sprite, m)
        mask = own_mask(options["check"], sprite) if "check" in options else None
        ak.finish(name, parts, (0.0, 0.0), out, options, mask, world=True,
                  label="%s (P %d) as the camera sees it, the block's own pixels" % (name, sprite))


if __name__ == "__main__":
    build()
