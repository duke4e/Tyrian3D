"""FLEET's slotted grey block on two grey claws (sheet K sprite 283, 2x2: 24 x 28 pixels; enemy 707 of episode 3, sky
and top layers; THE CORE's enemy 1674 of episode 6, sky; not animated), polished (2026-10-19; it replaces
wave3_o_machines.py's k_clawblock(), pixel-art pillows with tubes laid on). models.cfg: model k_clawblock
enemies/k_clawblock.glb; sprite k 283 k_clawblock yaw=0 (unchanged).

As the sprite and its 4x upscale draw it: a grey block across the whole width (rows 4-13), its top lit along its back
edge (row 4), a window in its middle (columns 8-15 of rows 7-9: a dark slot, its floor lighter at the bottom) in a light
frame (row 10 and columns 7 and 16), a flange down either side (columns 2-4 and 19-21: lit inner edges, a groove across
at row 8 with a bright rivet under it); behind it (up the screen) a low hip roof (rows 0-3: its back facet grey,
columns 6-17 of row 3 narrowing to 10-13 of row 0, its side facets falling away dark), two small dark blue lamps on
them (columns 4 and 19 of row 3). Under the
block (down the screen) two claws (columns 0-10 and 13-23 of rows 14-27): grey, a groove down their outer parts
(columns 3 and 20) and one across (row 22); down their inner sides a dark channel with two glowing red tubes in it
(columns 7 and 9, 13 and 15; hottest at row 21); at their ends lit feet hooking inwards (rows 25-27).

Built as a CAD modeller would: the block a rounded prism, its top edges bevelled, the window cut into it with an exact
boolean and framed; the roof a prism cut by three sloping planes (a hip roof); the flanges bevelled bars with their
groove cut; each claw a prism of its plan (narrowing to a hooked tip at its inner foot), its channel cut deep into its
inner side, the tubes turned parts lying in it (cut along smooth contours into a hotter middle), the feet bevelled pads.
Symmetric about the sprite's middle (x = 0).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; origin at the
sprite's centre (pixel 12, 14): column c's left edge is x = c - 12, row r's top edge y = 14 - r. Its underside at
z = 0 (sky and top layer models are centred in height by the game).

Replaces wave3_o_machines.py's k_clawblock(): remove it with its @o.model("k_clawblock", [(283, True)]) registration,
claws() (only k_clawblock() uses it) and k_clawblock's lines in the docstring; slot_block() and wave3_o_art.py's K283
stay (k_turret and k_lampgun use them).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against
enemy_K.png), --preview <prefix>.
"""
import math
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_orb_red import band_split  # noqa: E402

# The block: x0, x1, y0, y1, corner radius, top, the bevel of its top edges.
BLOCK = (-11.75, 11.75, 0.15, 10.35, 0.9, 7.0, 0.55)
# The window: x0, x1, y0, y1, corner radius, depth; its frame: how far out round it, how proud.
WINDOW = (-4.0, 4.0, 4.05, 7.1, 0.7, 1.9)
FRAME = (0.85, 0.28)
# The roof: its plan (from the block's back edge up the screen to its back, counter-clockwise), its height at the
# block's back edge and at its back; its sides' height at their edges and how they rise inwards.
ROOF = [(-11.6, 10.0), (11.6, 10.0), (2.3, 13.75), (-2.3, 13.75)]
ROOF_Z = (7.25, 5.5)
ROOF_SIDE = (5.2, 0.9)
# The flanges (the right one; mirrored): x0, x1, y0, y1, how proud of the block; the groove across (y, width,
# depth); the rivet under it (x, y, radius).
FLANGE = (6.85, 10.15, 0.6, 10.0, 0.75)
GROOVE = (5.5, 0.55, 0.45)
RIVET = (7.55, 4.45, 0.55)
LAMPS = [(-7.5, 10.35), (7.5, 10.35)]   # the dark blue lamps by the roof (columns 4 and 19 of row 3)
# The right claw's plan (mirrored for the left): pixel edges, from the block down to its hooked inner tip.
CLAW = [(1.0, 0.4), (12.0, 0.4), (12.0, -12.6), (11.0, -14.0), (3.6, -14.0), (2.7, -13.1), (2.6, -11.8),
        (1.6, -10.9), (1.0, -10.0)]
CLAW_Z, CLAW_BEVEL = 5.0, 0.5
CHANNEL = (1.5, 6.15, -0.15, -10.85, 0.5, 1.4)    # the channel: x0, x1, y0, y1, corner radius, its floor
TUBES = [2.55, 4.6]                               # the red tubes' x (the right claw's); their radius, y
TUBE_R, TUBE_Y = 0.62, (-10.55, -0.45)
# The tubes' colours along y: (from y, palette index, glow): hottest at rows 20-21 (y -6..-8).
TUBE_BANDS = [(-99.0, 0x73, 1.0), (-8.9, 0x79, 1.8), (-6.7, 0x76, 1.4), (-4.0, 0x74, 1.2), (-1.6, 0x73, 1.0)]
OUTER_GROOVE = (8.5, 0.5, 0.35)                   # down the claw's outer part: x, width, depth
CROSS_GROOVE = (-8.5, 0.5, 0.35)                  # across it (row 22)
FOOT = [(3.1, -11.0), (11.6, -11.0), (11.6, -12.7), (10.8, -13.65), (3.85, -13.65), (3.2, -12.9)]
FOOT_Z = (CLAW_Z - 0.6, CLAW_Z + 0.35)            # the foot pad: its underside (in the claw) and top


def materials():
    glow = k.level_palette()

    def lit(name, index, strength, roughness=0.2):
        return k.material(name, palette=index, metallic=0.0, roughness=roughness, emission=glow[index],
                          emission_strength=strength)
    m = {
        "grey": k.material("kblock_grey", palette=0x09, metallic=0.55, roughness=0.32),
        "side": k.material("kblock_side", palette=0x07, metallic=0.55, roughness=0.36),
        "light": k.material("kblock_light", palette=0x0b, metallic=0.55, roughness=0.28),
        "bright": k.material("kblock_bright", palette=0x0d, metallic=0.55, roughness=0.25),
        "groove": k.material("kblock_groove", palette=0x05, metallic=0.5, roughness=0.4),
        "slot": k.material("kblock_slot", palette=0x03, metallic=0.45, roughness=0.45),
        "slot_floor": k.material("kblock_slot_floor", palette=0x06, metallic=0.5, roughness=0.4),
        "channel": lit("kblock_channel", 0x70, 0.35, 0.5),
        "lamp": k.material("kblock_lamp", palette=0x31, metallic=0.2, roughness=0.15),
    }
    for _, index, strength in TUBE_BANDS:
        m[("tube", index)] = lit(f"kblock_tube_{index:x}", index, strength)
    return m


def rect(x0, x1, y0, y1, r, segments=48):
    ring = mk.rounded_rect_ring(((x0 + x1) / 2, (y0 + y1) / 2), (x1 - x0) / 2, (y1 - y0) / 2, r, 0.0, segments)
    return [(p.x, p.y) for p in ring]


def plane_box(name, top, size=40.0):
    """Everything under the plane z = top(x, y), for intersecting with (polish_arch.py's)."""
    s = size
    return mk.wedge(name, [(-s, -s), (s, -s), (s, s), (-s, s)], 0.0, top, bottom=lambda x, y: top(x, y) - 200.0)


# --- The block ---------------------------------------------------------------------------------------------------

def block(m):
    """The block: a rounded prism, its top edges bevelled; the window cut into its top, its floor lighter towards the
    front; the frame round it."""
    x0, x1, y0, y1, r, top, bev = BLOCK
    body = mk.prism("block", rect(x0, x1, y0, y1, r, 64), 0.0, top, m["grey"])
    mk.bevel(body, bev, 3, 30)
    wx0, wx1, wy0, wy1, wr, depth = WINDOW
    cutter = mk.prism("window", rect(wx0, wx1, wy0, wy1, wr), top - depth, top + 2.0, m["slot"])
    mk.boolean(body, cutter, "DIFFERENCE")
    mk.cleanup(body)
    mk.shade(body, 35)

    def pick(c, n):
        if wx0 - 0.05 < c.x < wx1 + 0.05 and wy0 - 0.05 < c.y < wy1 + 0.05 and c.z < top - 0.05:
            if n.z > 0.8:  # the window's floor: lighter towards its front (the sprite's rows 8-9)
                return m["slot_floor"] if c.y < (wy0 + wy1) / 2 else m["slot"]
            return m["slot"]
        if n.z > 0.8:
            return None
        if n.z > 0.3 and n.y > 0.3:  # the bevel along the back edge, lit (row 4)
            return m["light"]
        if n.z < 0.3:
            return m["side"]
        return None
    mk.paint(body, pick)
    # The frame round the window: a ring a little proud of the top, its edges rounded.
    out, proud = FRAME
    outer = mk.prism("frame", rect(wx0 - out, wx1 + out, wy0 - out, wy1 + out, wr + out), top - 0.3, top + proud,
                     m["light"])
    inner = mk.prism("frame_hole", rect(wx0, wx1, wy0, wy1, wr), top - 1.0, top + 1.0, m["light"])
    mk.boolean(outer, inner, "DIFFERENCE")
    mk.cleanup(outer)
    mk.bevel(outer, 0.18, 2, 30)
    mk.shade(outer, 35)
    mk.paint(outer, lambda c, n: m["bright"] if n.z > 0.8 and c.y < wy0 else None)


def roof(m):
    """The hip roof behind the block: a prism of its plan cut by three planes, one falling to its back, one to each
    side; its edges bevelled."""
    z0, z1 = ROOF_Z
    body = mk.prism("roof", ROOF, 0.0, z0 + 1.0, m["grey"])
    y0, y1 = ROOF[0][1], ROOF[2][1]
    planes = [lambda x, y: z0 + (z1 - z0) * (y - y0) / (y1 - y0)]
    for (ax, ay), (bx, by) in ((ROOF[1], ROOF[2]), (ROOF[3], ROOF[0])):
        length = math.hypot(by - ay, bx - ax)
        nx, ny = (by - ay) / length, -(bx - ax) / length  # the side's outward normal (the plan is counter-clockwise)
        d = nx * ax + ny * ay
        planes.append(lambda x, y, nx=nx, ny=ny, d=d: ROOF_SIDE[0] + ROOF_SIDE[1] * (d - (nx * x + ny * y)))
    for i, top in enumerate(planes):
        mk.boolean(body, plane_box(f"roof_plane{i}", top), "INTERSECT")
    mk.cleanup(body)
    mk.bevel(body, 0.3, 2, 30)
    mk.shade(body, 35)
    mk.paint(body, lambda c, n: m["side"] if n.z < 0.3 else None)


def flanges(m):
    """The flanges down the block's sides: bevelled bars proud of its top, a groove across, a rivet under it; the
    dark blue lamps by the roof."""
    x0, x1, y0, y1, proud = FLANGE
    top = BLOCK[5]
    gy, gw, gd = GROOVE
    for sign in (1, -1):
        xa, xb = sorted((sign * x0, sign * x1))
        bar = mk.box(f"flange{sign}", xa, xb, y0, y1, top - 0.6, top + proud, m["grey"])
        mk.bevel(bar, 0.3, 2, 30)
        groove = mk.box(f"flange_groove{sign}", xa - 1.0, xb + 1.0, gy - gw / 2, gy + gw / 2, top + proud - gd,
                        top + 2.0, m["groove"])
        mk.boolean(bar, groove, "DIFFERENCE")
        mk.cleanup(bar)
        mk.shade(bar, 35)
        inner_x = xa if sign > 0 else xb

        def pick(c, n, inner_x=inner_x):
            if abs(c.y - gy) < gw / 2 + 0.02 and c.z < top + proud - 0.02:
                return m["groove"]
            if n.z < 0.8 and abs(c.x - inner_x) < 0.5:  # the inner edge, lit
                return m["light"]
            return None
        mk.paint(bar, pick)
        rx, ry, rr = RIVET
        rivet = mk.dome(f"rivet{sign}", (sign * rx, ry), (rr, rr, 0.35), top + proud - 0.05, m["bright"], 16, 4)
        k.smooth(rivet, 60)
    for i, (x, y) in enumerate(LAMPS):
        lamp = mk.dome(f"lamp{i}", (x, y), (0.6, 0.45, 0.35), top - 0.1, m["lamp"], 16, 4)
        k.smooth(lamp, 60)


# --- The claws -----------------------------------------------------------------------------------------------------

def claw(m, sign):
    """A claw: a prism of its plan, its edges bevelled; its channel cut deep along its inner side, the grooves down and
    across its outer part; the red tubes lying in the channel, glowing, hottest towards the foot; the foot pad."""
    plan = [(sign * x, y) for x, y in CLAW]
    if sign < 0:
        plan.reverse()
    body = mk.prism(f"claw{sign}", plan, 0.0, CLAW_Z, m["grey"])
    mk.bevel(body, CLAW_BEVEL, 3, 30)
    cx0, cx1, cy0, cy1, cr, floor = CHANNEL
    xa, xb = sorted((sign * cx0, sign * cx1))
    channel = mk.prism(f"channel{sign}", rect(xa, xb, cy1, cy0, cr), floor, CLAW_Z + 2.0, m["channel"])
    gx, gw, gd = OUTER_GROOVE
    down = mk.box(f"groove_down{sign}", sign * gx - gw / 2, sign * gx + gw / 2, -11.2, 1.0, CLAW_Z - gd, CLAW_Z + 2.0,
                  m["groove"])
    cy, cw, cd = CROSS_GROOVE
    xs = sorted((sign * cx1, sign * 12.5))
    across = mk.box(f"groove_across{sign}", xs[0], xs[1], cy - cw / 2, cy + cw / 2, CLAW_Z - cd, CLAW_Z + 2.0,
                    m["groove"])
    mk.boolean(body, [channel, down, across], "DIFFERENCE")
    mk.cleanup(body)
    mk.shade(body, 35)

    def pick(c, n):
        if xa - 0.02 < c.x < xb + 0.02 and cy1 - 0.02 < c.y < cy0 + 0.02 and c.z < CLAW_Z - 0.05:
            return m["channel"]
        if abs(c.x - sign * gx) < gw / 2 + 0.02 and c.z < CLAW_Z - 0.02 and c.z > CLAW_Z - gd - 0.05:
            return m["groove"]
        if abs(c.y - cy) < cw / 2 + 0.02 and c.z < CLAW_Z - 0.02 and c.z > CLAW_Z - cd - 0.05:
            return m["groove"]
        if n.z < 0.3:
            return m["side"]
        return None
    mk.paint(body, pick)
    # The tubes in the channel.
    y0, y1 = TUBE_Y
    for i, x in enumerate(TUBES):
        tube = mk.tube(f"tube{sign}{i}", [(sign * x, y, floor + TUBE_R * 0.95) for y in
                                          [y0 + (y1 - y0) * t / 24 for t in range(25)]], TUBE_R,
                       m[("tube", TUBE_BANDS[-1][1])], 16)
        band_split(tube, [v.co.y for v in tube.data.vertices],
                   [(start, m[("tube", index)]) for start, index, _ in TUBE_BANDS])
        k.smooth(tube, 60)
    # The foot pad, lit on top.
    pad = [(sign * x, y) for x, y in FOOT]
    if sign < 0:
        pad.reverse()
    foot = mk.prism(f"foot{sign}", pad, FOOT_Z[0], FOOT_Z[1], m["light"])
    mk.bevel(foot, 0.3, 2, 30)
    mk.shade(foot, 35)
    mk.paint(foot, lambda c, n: m["bright"] if n.z > 0.8 else m["side"] if n.z < 0.3 else None)


def build():
    options = k.args()
    out = mk.outdir(options)
    k.reset()
    m = materials()
    block(m)
    roof(m)
    flanges(m)
    for sign in (1, -1):
        claw(m, sign)
    parts = mk.meshes()
    for obj in parts:
        mk.apply(obj)
    bpy.context.view_layer.update()
    if "check" in options:
        sheet = os.path.join(options["check"], "enemy_K.png")
        mk.compare("k_clawblock (K 283)", mk.coverage(parts, 24, 28), k.sprite_mask(sheet, 283))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mk.report("k_clawblock", parts, os.path.join(out, "k_clawblock.glb"))
    if "preview" in options:
        mk.preview(options["preview"] + "k_clawblock", parts)


if __name__ == "__main__":
    build()
