"""The grey shield-shaped ship of the asteroid levels (sheet S sprite 93, 2x2: 24 x 28 pixels; ASTEROID?'s enemy 459
of episode 1, sky; MINEMAZE's enemy 590 of episode 1, sky and ground; GAUNTLET's of episode 3, AST ROCK's and
ASTEROIDS' of episode 5, sky; its animation 93 131 131 131 93, played when it fires: the hatch opens on a red eye
and shuts again), polished (2026-10-21; it replaces wave2_g.py's hatch_ship(), a hull inflated from the sprite's
outline with tubes laid on for its frame and ribs, which showed the hatch open all the time). models.cfg:
sprite s 93 hatch_ship yaw=0 (the hatch shut, as the ship is when it doesn't fire); model hatch_ship_131
enemies/hatch_ship_131.glb and frame s 131 hatch_ship_131 (the hatch open on the eye; no other enemy shows sheet S's
93 or 131). Only two sprites: no frame between shut and open to model.

S 131 is S 93's pixels but in the hatch (columns 10-13 of rows 9-12, the eye) and the shades round it (the hood's rim,
rows 8-13, the shoulder ridges, columns 7 and 16, and the keel's top, rows 16-17), one to two shades lighter: the
eye's light (and two pixels of the top rim, columns 10-11 of row 3, a shade darker). No other sprite is these pixels
mirrored or in other ramps.

As the sprites and their 4x upscales draw it (symmetric about the sprite's middle, x = 0): a shield of grey armour
(ramp 0) in a near-black outline, its top edge straight (row 2) with an ear at each corner (columns 3-4 and 19-20 of
row 1), its sides straight (columns 2 and 21) down to row 15 with a notch at row 14, then tapering on the diagonal
to the keel's width (columns 8-15 of rows 21-23) and to a point (row 27). Its upper half is a tray: a raised rim
along the top edge (row 3, lit) and down the sides (columns 3-4 and 19-20, the left lit, the right in shadow) round
a recessed panel (05); in the middle of the panel a hood (columns 9-14 of rows 7-13), its brow lit (row 8), round a
socket, the hatch (columns 10-13 of rows 9-11): dark when it is shut (93), a red eye glowing orange in its middle
when open (131); two prongs reach up the screen from the brow (columns 10 and 13 of rows 5-7). A red light burns on
each ear (columns 4-5 and 18-19 of rows 2-3). Below the panel two shoulder plates angle out to the notches (columns
3-7 of rows 12-18, a lit ridge down their inner edges at columns 7 and 16), and down the middle runs the keel
(columns 9-14 of rows 13-26, lit down its left), a blue glass canopy set into it (columns 10-13 of rows 19-24).

Built as a CAD modeller would (polish_machine_kit): the hull a prism of its plan (the outline's steps cut through
their middles), the tray's panel and the lower hull cut down into it with an exact boolean (the rim is what is
left), its edges bevelled, the lower hull beside the keel as dark (03) as the sprites draw it; the hood a bevelled
block, its top sloping down to its lower edge, the socket cut into it; the prongs and the shoulder plates (wedges
sloping out from their ridges) laid on and bevelled; the keel lofted down the screen (a rounded crest on a foot sunk
into the deck, its top end rounded off to the gap under the hood, lowering to the tip); the canopy a glass dome; the
lights red glass domes on the ears. The hatch shut: two dark lids meeting across the socket (93); open: the lids
drawn back into the hood and the eye, a red glass ball, its heat in bands of the sprite's shades
(polish_orb_red.band_split), glowing well under 1 (the game's bloom adds to it), its light baked into the hood's
and the keel's shades a shade lighter, as the sprite draws it. Both frames have the same shapes but the hatch, and
the same bounds. A flying ship: flat underneath (the camera never sees its belly), 4.8 pixels high, centred in
height by the game (on MINEMAZE's ground layer it hovers).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; origin at the
sprite's centre (pixel 12, 14): column c's left edge is x = c - 12, row r's top edge y = 14 - r.

Replaces wave2_g.py's hatch_ship() (its "S 93: the hatch ship" section's @model("hatch_ship", "S", 93) registration
and hatch_ship(), and the hatch_ship lines of its docstring; NOT rounded_rect(), which deli_tower_tl() uses too) and
wave2_g_art.py's S93 and S131 (nothing else reads them): remove them so that they don't overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each frame's silhouette
against enemy_S.png), --preview <prefix>, --only <name,...>.
"""
import math
import os
import sys

import bmesh
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402

# The hull's plan, its right half from the tip up (the left half is its mirror image): the outline's steps cut
# through their middles; the notch at row 14; the ear at the top corner (columns 19-20 of row 1).
HALF_PLAN = [(0.0, -13.95), (1.15, -13.75), (3.8, -10.3), (3.95, -7.35), (4.55, -6.95), (9.65, -1.85), (10.0, -1.3),
             (9.35, -0.5), (10.0, 0.3), (10.0, 11.45), (9.6, 12.35), (8.85, 12.95), (7.15, 12.95), (6.7, 12.05)]
# Heights: the rim's top; the panel and the lower hull; the bevels.
RIM_TOP, DECK = 3.4, 2.4
HULL_BEVEL, EDGE_BEVEL = 0.55, 0.22
# The tray's panel inside the rim (x half-width, its top edge, corner radius); the rim's sides end at FLARE[0], where
# the cut widens to take the whole lower hull (at FLARE[1] it reaches the hull's sides).
PANEL = (6.85, 10.55, 1.3)
FLARE = (0.45, -0.55)
LOWER_Y = -0.15                 # below this the deck is the lower hull's, darker
# The hood: plan (x0, x1, y0, y1, corner radius), top, bevel; the socket (x0, x1, y0, y1, radius) and its floor.
HOOD = (-3.1, 3.1, 0.1, 6.85, 1.5)
HOOD_TOP, HOOD_SLOPE, HOOD_BEVEL = 4.85, 0.14, 0.55     # its top falls by HOOD_SLOPE a pixel from the brow down
SOCKET = (-2.05, 2.05, 1.55, 5.35, 1.0)
SOCKET_FLOOR = 2.75
# The prongs (x of their middles; half-width; from y to y; top).
PRONGS = [-1.5, 1.5]
PRONG_HALF, PRONG_Y, PRONG_TOP = 0.62, (6.2, 9.35), 4.05
# The shoulder plates (the left one; mirrored): plan, the ridge's height and the outer tip's.
PLATE = [(-3.6, 2.85), (-9.4, -0.5), (-4.15, -4.0)]
PLATE_RIDGE, PLATE_TIP = 3.75, 2.75
# The keel (columns 9-14 of rows 15-26, a dark gap at row 14 between it and the hood): its half-width down the screen
# ((y, half-width), from its rounded top end to the tip), its top there and at the tip.
KEEL_WIDTH = [(-0.75, 0.9), (-0.95, 1.9), (-1.35, 2.6), (-2.1, 3.0), (-8.9, 3.05), (-10.2, 2.75), (-11.4, 2.1),
              (-12.4, 1.45), (-13.15, 0.8), (-13.4, 0.2)]
KEEL_TOP, KEEL_TIP_TOP = 3.85, 3.0
# The canopy: centre (x, y, z), radii (columns 10-13 of rows 19-24).
CANOPY = ((0.0, -7.75, 3.0), (1.95, 3.15, 1.35))
# The red lights on the ears: centre (x, y), radius, height.
LAMPS = [(-7.55, 11.55), (7.55, 11.55)]
LAMP_R, LAMP_H = 1.0, 0.75
# The eye (131): centre, radii; its heat: the hottest point (x, y) and the bands (lowest heat, index, glow).
EYE = ((0.0, 3.45, SOCKET_FLOOR + 0.35), (1.95, 1.8, 1.15))
EYE_HOT = (0.1, 3.6)
EYE_BANDS = [(-9.0, 0x73, None), (0.35, 0x75, 0.35), (0.62, 0x77, 0.45), (0.8, 0x79, 0.5), (0.92, 0x7a, 0.55)]
# (the outer band, None, is the lights' red glass)
# The lids (93): their top, the seam between them (y), its width.
LID_TOP, LID_SEAM, LID_GAP = 3.75, 3.45, 0.22

# The frames: model, sprite, hatch open, the hood's and the keel's shades.
FRAMES = [("hatch_ship", 93, False, 0x0a, 0x07), ("hatch_ship_131", 131, True, 0x0b, 0x08)]


def plan():
    """The hull's whole plan, counter-clockwise: the right half up from the tip, the left half (its mirror image)
    down to it."""
    return HALF_PLAN + [(-x, y) for x, y in reversed(HALF_PLAN[1:])]


def rrect(x0, x1, y0, y1, r, segments=40):
    ring = mk.rounded_rect_ring(((x0 + x1) / 2, (y0 + y1) / 2), (x1 - x0) / 2, (y1 - y0) / 2, r, 0.0, segments)
    return [(p.x, p.y) for p in ring]


def materials(frame):
    glow = k.level_palette()
    _, _, open_, hood, keel = frame

    def mat(name, index, metallic=0.55, roughness=0.34):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)

    def lit(name, index, strength, roughness=0.2, emission_index=None):
        return k.material(name, palette=index, metallic=0.0, roughness=roughness,
                          emission=glow[index if emission_index is None else emission_index],
                          emission_strength=strength)
    m = {
        "deck": mat("hatch_deck", 0x05),
        "rim": mat("hatch_rim", 0x08, roughness=0.3),
        "side": mat("hatch_side", 0x03, roughness=0.45),
        "seam": mat("hatch_seam", 0x02, roughness=0.5),
        "hood": mat(f"hatch_hood_{hood:x}", hood, roughness=0.28),
        "prong": mat("hatch_prong", 0x09, roughness=0.3),
        "plate": mat("hatch_plate", 0x06),
        "keel": mat(f"hatch_keel_{keel:x}", keel, roughness=0.3),
        "socket": mat("hatch_socket", 0x01, metallic=0.3, roughness=0.6),
        "lamp": lit("hatch_lamp", 0x73, 0.35, 0.2, 0x75),
        "canopy": lit("hatch_canopy", 0x94, 0.3, 0.08, 0x96),
    }
    if open_:
        for _, index, strength in EYE_BANDS:
            m[("eye", index)] = m["lamp"] if strength is None else lit(f"hatch_eye_{index:x}", index, strength)
    else:
        m["lid"] = mat("hatch_lid", 0x02, metallic=0.6, roughness=0.3)
    return m


# --- The hull -------------------------------------------------------------------------------------------------------

def hull(m):
    """The hull: a prism of its plan up to the rim's top; the panel and the lower hull cut down to the deck (the rim
    along the top edge and the sides is what is left); its edges bevelled; the tops painted rim or deck, the walls
    dark."""
    body = mk.prism("hull", plan(), 0.0, RIM_TOP, m["side"])
    mk.boolean(body, mk.prism("pocket", pocket_plan(), DECK, 20.0, m["deck"]), "DIFFERENCE")
    mk.cleanup(body)
    mk.bevel(body, HULL_BEVEL, 3, 30)
    # The deck split where the panel ends and the darker lower hull begins (one flat face after the boolean).
    bm = bmesh.new()
    bm.from_mesh(body.data)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5,
                           plane_co=(0.0, LOWER_Y, 0.0), plane_no=(0.0, 1.0, 0.0))
    bm.to_mesh(body.data)
    bm.free()
    mk.shade(body, 35)

    def pick(c, n):
        if n.z > 0.7:
            if c.z > DECK + 0.4:
                return m["rim"]
            return m["side"] if c.y < LOWER_Y else m["deck"]  # the lower hull as dark as the walls
        return m["side"]
    mk.paint(body, pick)
    return body


def pocket_plan(segments=8):
    """What is cut down to the deck, counter-clockwise: the panel inside the rim (its top corners rounded), widening
    below FLARE[0] to the whole lower hull."""
    hw, y1, r = PANEL
    fy0, fy1 = FLARE
    out = [(14.0, -20.0), (14.0, fy1), (hw, fy0)]
    for cx, a0 in ((hw - r, 0.0), (-hw + r, 90.0)):
        for i in range(segments + 1):
            a = math.radians(a0 + 90.0 * i / segments)
            out.append((cx + r * math.cos(a), y1 - r + r * math.sin(a)))
    return out + [(-hw, fy0), (-14.0, fy1), (-14.0, -20.0)]


def half_rrect(x0, x1, y0, y1, r, keep_below, cut, segments=10):
    """The part of a rounded rectangle below (keep_below) or above y = cut, counter-clockwise (cut between its
    straight sides)."""
    out = []
    if keep_below:
        corners = [(x0 + r, y0 + r, 180.0), (x1 - r, y0 + r, 270.0)]
        out.append((x0, cut))
    else:
        corners = [(x1 - r, y1 - r, 0.0), (x0 + r, y1 - r, 90.0)]
        out.append((x1, cut))
    for cx, cy, a0 in corners:
        for i in range(segments + 1):
            a = math.radians(a0 + 90.0 * i / segments)
            out.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    out.append((x1, cut) if keep_below else (x0, cut))
    return out


# --- The hood, the socket and what is in it -------------------------------------------------------------------------

def hood(m):
    x0, x1, y0, y1, r = HOOD
    body = mk.wedge("hood", rrect(x0, x1, y0, y1, r), DECK - 0.5, lambda x, y: HOOD_TOP - HOOD_SLOPE * (y1 - y),
                    m["hood"])
    mk.bevel(body, HOOD_BEVEL, 3, 30)
    sx0, sx1, sy0, sy1, sr = SOCKET
    mk.boolean(body, mk.prism("socket_cut", rrect(sx0, sx1, sy0, sy1, sr), SOCKET_FLOOR, 20.0, m["socket"]),
               "DIFFERENCE")
    mk.cleanup(body)
    mk.bevel(body, EDGE_BEVEL, 2, 40)
    mk.shade(body, 35)

    def pick(c, n):
        inside = mk.rounded_rect_distance(c.x - (sx0 + sx1) / 2, c.y - (sy0 + sy1) / 2, (sx1 - sx0) / 2,
                                          (sy1 - sy0) / 2, sr) < 0.12
        if inside and c.z < HOOD_TOP - 0.35:
            return m["socket"]
        return None
    mk.paint(body, pick)
    parts = [body]
    for i, x in enumerate(PRONGS):
        prong = mk.prism(f"prong{i}", rrect(x - PRONG_HALF, x + PRONG_HALF, PRONG_Y[0], PRONG_Y[1], PRONG_HALF * 0.95),
                         DECK - 0.3, PRONG_TOP, m["prong"])
        mk.bevel(prong, 0.42, 3, 30)
        mk.shade(prong, 40)
        parts.append(prong)
    return parts


def lids(m):
    """The hatch shut: two dark lids meeting across the socket (a seam between them), a little domed."""
    sx0, sx1, sy0, sy1, sr = SOCKET
    grow = 0.25  # the lids reach a little into the hood's walls round the socket
    out = []
    for i, (below, cut) in enumerate(((True, LID_SEAM - LID_GAP / 2), (False, LID_SEAM + LID_GAP / 2))):
        outline = half_rrect(sx0 - grow, sx1 + grow, sy0 - grow, sy1 + grow, sr + grow, below, cut)
        lid = mk.wedge(f"lid{i}", outline, SOCKET_FLOOR - 0.2,
                       lambda x, y: LID_TOP - 0.18 * abs(y - LID_SEAM) - 0.08 * x * x, m["lid"])
        mk.bevel(lid, 0.16, 2, 40)
        mk.shade(lid, 40)
        out.append(lid)
    return out


def eye(m):
    """The hatch open: a red glass ball in the socket, its heat in bands round its hot middle."""
    (cx, cy, cz), radii = EYE
    ball = mk.ball("eye", (cx, cy, cz), radii, m[("eye", EYE_BANDS[0][1])], 32, 16)
    hx, hy = EYE_HOT

    def heat(p):
        d = math.hypot((p.x - hx) / radii[0], (p.y - hy) / radii[1])
        up = max(0.0, (p.z - cz) / radii[2])
        return (1.0 - d) * 0.75 + up * 0.25
    band_split(ball, [heat(v.co) for v in ball.data.vertices], [(lo, m[("eye", index)]) for lo, index, _ in EYE_BANDS])
    k.smooth(ball, 80)
    return [ball]


# --- The shoulders, the keel, the canopy and the lights -------------------------------------------------------------

def plate_top(x, y, side):
    """The shoulder plate's top: RIDGE along its inner edge, falling to PLATE_TIP at the outer tip."""
    (ax, ay), (bx, by), _ = PLATE
    t = (abs(x) - abs(ax)) / (abs(bx) - abs(ax))
    return PLATE_RIDGE + (PLATE_TIP - PLATE_RIDGE) * max(0.0, min(1.0, t))


def shoulders(m):
    out = []
    for side in (-1, 1):
        outline = [(side * -x if side > 0 else x, y) for x, y in PLATE]
        if side > 0:
            outline = outline[::-1]
        plate = mk.wedge(f"plate{side}", outline, DECK - 0.5, lambda x, y, s=side: plate_top(x, y, s), m["plate"])
        mk.bevel(plate, 0.4, 3, 25)
        mk.shade(plate, 35)
        out.append(plate)
    return out


def keel_width(y):
    pts = KEEL_WIDTH
    if y >= pts[0][0]:
        return pts[0][1]
    for (ya, wa), (yb, wb) in zip(pts, pts[1:]):
        if yb <= y <= ya:
            return wa + (wb - wa) * (ya - y) / (ya - yb)
    return pts[-1][1]


def keel(m):
    """The keel: lofted down the screen, its cross-section a rounded crest on a flat foot sunk into the deck, its
    top lowering towards the tip; the canopy a glass dome set into it."""
    base = DECK - 0.5
    rings = []
    y = KEEL_WIDTH[0][0]
    while y > KEEL_WIDTH[-1][0] - 1e-6:
        top = KEEL_TOP + (KEEL_TIP_TOP - KEEL_TOP) * mk.smoothstep(-4.0, -13.4, y)
        end = mk.smoothstep(KEEL_WIDTH[0][0], KEEL_WIDTH[3][0], y)  # its top end rounded down to the gap
        rings.append(k.ring(y, keel_width(y), (top - base) * (0.55 + 0.45 * math.sqrt(end)), 24, z=base,
                            bottom=0.12, power=2.6))
        y -= 0.35
    body = k.loft("keel", rings, m["keel"])
    k.smooth(body, 50)
    (cx, cy, cz), radii = CANOPY
    canopy = mk.ball("canopy", (cx, cy, cz), radii, m["canopy"], 32, 16)
    return [body, canopy]


def lamps(m):
    out = []
    for i, (x, y) in enumerate(LAMPS):
        out.append(mk.dome(f"lamp{i}", (x, y), (LAMP_R, LAMP_R, LAMP_H), RIM_TOP - 0.25, m["lamp"], 24, 6))
    return out


# --- Build ----------------------------------------------------------------------------------------------------------

def build_frame(frame, options):
    name, sprite, open_, _, _ = frame
    k.reset()
    m = materials(frame)
    parts = [hull(m)] + hood(m) + shoulders(m) + keel(m) + lamps(m) + (eye(m) if open_ else lids(m))
    parts = triangulate(parts)
    bpy.context.view_layer.update()
    if "check" in options:
        sheet = os.path.join(options["check"], "enemy_S.png")
        mk.compare("%s (S %d)" % (name, sprite), mk.coverage(parts, 24, 28), k.sprite_mask(sheet, sprite))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mk.report(name, parts, os.path.join(mk.outdir(options), name + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + name, parts, distance=0.6)


def build():
    options = k.args()
    only = options["only"].split(",") if "only" in options else [f[0] for f in FRAMES]
    for frame in FRAMES:
        if frame[0] in only:
            build_frame(frame, options)


if __name__ == "__main__":
    build()
