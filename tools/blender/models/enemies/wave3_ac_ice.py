"""Batch AC of wave 3 (sheet 7: CAMANIS and ICESECRET; the globe on its legs: polish_ice_globe.py), the ground objects
the game draws in pieces, modelled
as their sprites look (models.cfg: yaw=0), each built whole and cut into its sprites' pieces, drawn at their
own origins (origin) so they meet. The level events place the pieces as the sheet arranges them (event 12
lays four 2x2 sprites as a square: the enemy, the next one beside it, the two after them above; the red dome
is placed as two events, the dome 28 rows above its arm). All stand on the ground layer. The sprites draw the
ice plateau round them and their shadows on it: the models leave both out (the 3D ground shows the ice, the
game casts the shadows). The kit is wave3_ac_kit.py, the pixels wave3_ac_art.py.

- ice_bunker_tl, _tr, _bl, _br (7 1, 3 above 39, 41; events 82, 83 above 80, 81): the grey and blue bunker,
  44 x 52: a flat grey deck with blue-grey corner panels, blocks and studs along its sides and a dark hatch with
  the gun's blue housing lying in it; on the deck's front edge a block with rounded shoulders and sloping sides,
  a glass skylight with three ribs between two blue lamps on its high back, and at its lower front two blue
  windows and a big glowing lens between two rails. Its frames would raise the gun from the hatch, but the
  enemy never fires, so the levels show it closed, as the model does.
- ice_drill_dome, ice_drill_arm (7 169 above 207; events 85, 86): CAMANIS' red hood with its arm, 24 x 56: a
  red dome with an orange lamp on its back, open at its front between clawed cheeks over a grey piston; out of
  its red collar the arm runs down the screen, a flange, a red knuckle and the grey head with its point. 169's
  frames would light the lamp (the enemy never fires: it stays dim); 207's frames (205, 203) pull the arm in
  when it launches, the model keeps it out.

usage: Blender -b --factory-startup -P wave3_ac_ice.py -- [--only names] [--preview <prefix>] [--check 1]
       [--whole <prefix>]
"""
import math
import os
import sys


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ac_kit as a  # noqa: E402
from wave3_ac_kit import pal, sphere  # noqa: E402


def quarters(prefix, fr, keep=None):
    """The four 2x2 pieces of a 48 x 56 object whose origin is its centre: (name, box, centre, mask); the
    masks keep the frame's object pixels (keep(index, column, row), default: all but the ice)."""
    out = []
    for suffix, (c0, r0) in (("tl", (0, 0)), ("tr", (24, 0)), ("bl", (0, 28)), ("br", (24, 28))):
        cx, cy = c0 - 24 + 12.0, 28 - r0 - 14.0
        box = (c0, c0 + 24, r0, r0 + 28)
        mask = (lambda b=box: a.object_mask(fr, b, keep)) if keep else (lambda b=box: a.object_mask(fr, b))
        out.append((f"{prefix}_{suffix}", (cx - 12.0, cx + 12.0, cy - 14.0, cy + 14.0), (cx, cy), mask))
    return out


# --- 7 1 3 / 39 41: the bunker ----------------------------------------------------------------------

BUNKER = a.frame("BUNKER", 48, (24, 28))


def bunker_keep(v, c, r):
    """The bunker's own pixels: the ice round it (and its shadow) left out, the blue of its hatch kept."""
    inside = (r <= 37 and c <= 43) or (38 <= r <= 51 and 4 <= c <= 39)
    return inside or not a.is_ice(v)


def build_bunker():
    B = BUNKER
    m = {f"g{v:x}": pal(f"bunker_grey{v:x}", v, metallic=0.45, roughness=0.42) for v in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)}
    m.update({
        "teal": pal("bunker_teal", 0x80, metallic=0.4, roughness=0.4),
        "panel": pal("bunker_panel", 0x82, metallic=0.4, roughness=0.35),
        "panel_light": pal("bunker_panel_light", 0x84, metallic=0.4, roughness=0.3),
        "panel_dark": pal("bunker_panel_dark", 0x81, metallic=0.4, roughness=0.4),
        "hatch": pal("bunker_hatch", 0x37, metallic=0.4, roughness=0.35),
        "hatch_dark": pal("bunker_hatch_dark", 0x35, metallic=0.35, roughness=0.4),
        "glass": pal("bunker_glass", 0x9e, metallic=0.1, roughness=0.08, glow=0.7),
        "glass_low": pal("bunker_glass_low", 0x83, metallic=0.2, roughness=0.1, glow=0.25),
        "lamp": pal("bunker_lamp", 0x9b, metallic=0.0, roughness=0.2, glow=2.2),
        "window": pal("bunker_window", 0x9a, metallic=0.1, roughness=0.15, glow=0.9),
        "slit": pal("bunker_slit", 0x83, metallic=0.2, roughness=0.2, glow=0.4),
        "lens": pal("bunker_lens", 0x9a, metallic=0.0, roughness=0.12, glow=1.6),
        "lens_hot": pal("bunker_lens_hot", 0x9e, metallic=0.0, roughness=0.1, glow=2.4),
        "lens_white": pal("bunker_lens_white", 0x8e, metallic=0.0, roughness=0.1, glow=2.8),
    })

    def shade(obj, top, edge, side, under=None):
        a.paint_faces(obj, lambda c, nrm: top if nrm.z > 0.9 else edge if nrm.z > 0.3 else
                      (under or m["g1"]) if nrm.z < -0.5 else side)

    # The back deck: a flat grey roof on the plateau, its edge lit.
    deck = a.slab("deck", B.rect(0, 43, 0, 37, 0.15), 0.0, 5.0, m["g4"], bevel=0.7, segments=2)
    shade(deck, m["g4"], m["g7"], m["g3"])
    # Its corner panels, blue-grey, and the studs and blocks along its sides.
    for c0, c1 in ((3, 7), (36, 40)):
        frame_ = a.slab(f"panel_frame{c0}", B.rect(c0, c1, 3, 7, 0.05), 4.6, 5.35, m["panel_light"], bevel=0.25,
                        segments=1)
        shade(frame_, m["panel_light"], m["panel"], m["panel_dark"])
        a.slab(f"panel{c0}", B.rect(c0 + 1, c1, 4, 6, 0.1), 4.9, 5.5, m["panel_dark"], bevel=0.2, segments=1)
    for cx, flip in ((5.0, 1), (38.5, -1)):
        for r0 in (8, 14):
            blk = a.rounded_box(f"block{cx}_{r0}", (B.X(cx), B.Y(r0 + 2.0), 5.4), (5.0, 4.6, 1.4), m["g7"],
                                bevel=0.4, segments=1)
            shade(blk, m["g7"], m["g8"], m["g5"])
            a.rounded_box(f"stud{cx}_{r0}", (B.X(cx + 1.5 * flip), B.Y(r0 + 1.6), 6.3), (2.0, 2.0, 0.8),
                          m["panel"], bevel=0.3, segments=1)
    # The rails either side of the hatch.
    for cx in (11.0, 31.5):
        rail = a.rounded_box(f"rail{cx}", (B.X(cx), B.Y(12.5), 5.6), (4.0, 12.0, 1.6), m["g6"], bevel=0.5,
                             segments=1)
        shade(rail, m["g7"], m["g8"], m["g5"])
    # The hatch: a dark well in the deck, the gun's blue housing lying in it (it never comes up).
    a.slab("well", B.rect(14, 30, 6, 18, 0.1), 4.95, 5.15, m["g1"], bevel=0.05, segments=1)
    for c0, c1 in ((15, 18), (26, 29)):
        ledge = a.slab(f"ledge{c0}", B.rect(c0, c1, 7, 18, 0.1), 5.0, 5.45, m["g4"], bevel=0.15, segments=1)
        shade(ledge, m["g4"], m["g3"], m["g2"])
    housing = a.slab("housing", B.rect(19, 26, 12, 18, 0.1), 5.0, 6.2, m["hatch"], bevel=0.4, segments=2)
    shade(housing, m["hatch"], m["panel"], m["hatch_dark"])
    barrel = a.slab("barrel", B.rect(20, 24, 7, 11, 0.15), 5.0, 5.8, m["hatch_dark"], bevel=0.35, segments=2)
    shade(barrel, m["hatch_dark"], m["hatch"], m["hatch_dark"])

    # The bunker: one block on the deck's front edge, its shoulders rounded and its sides sloping, high at the
    # back (a glass skylight on its flat top) and stepping down at its front, where two blue windows and the big
    # lens look out between two rails.
    ax = -1.75
    keys = [(B.top(19) + 0.6, 9.5, 5.5), (B.top(19), 12.5, 10.2), (B.top(20), 14.5, 11.8), (B.top(22), 16.4, 12.4),
            (B.bottom(33) + 0.6, 16.8, 12.4), (B.bottom(33), 16.9, 11.9), (B.bottom(34), 17.0, 9.0),
            (B.bottom(35), 17.0, 8.7), (B.bottom(50) + 0.4, 17.2, 8.6), (B.bottom(50) - 0.3, 17.0, 7.0),
            (B.bottom(51), 16.0, 2.0)]
    secs = []
    for (y0, hw0, t0), (y1, hw1, t1) in zip(keys, keys[1:]):
        steps = max(1, int(abs(y1 - y0) / 1.2))
        for i in range(steps):
            f = i / steps
            secs.append((y0 + (y1 - y0) * f, ax, 0.0, hw0 + (hw1 - hw0) * f, t0 + (t1 - t0) * f, 0.01))
    secs.append((keys[-1][0], ax, 0.0, keys[-1][1], keys[-1][2], 0.01))
    body = a.loft_y("body", secs[::-1], m["g7"], segments=40, power=3.4, smooth_angle=40)

    def body_paint(c, nrm):
        if nrm.z < -0.5:
            return m["g1"]
        if c.y < B.top(37) and abs(c.x - ax) > 14.6:
            return m["panel"] if nrm.z > 0.3 else m["panel_dark"]
        if nrm.z > 0.86:
            return m["g9"]
        if nrm.z > 0.4:
            return m["ga"] if c.x < ax else m["g7"]
        return m["teal"] if abs(nrm.x) > 0.6 else m["g5"]
    a.paint_faces(body, body_paint)
    # Raised plates on its top either side of the skylight.
    for c0, c1 in ((12, 15), (29, 32)):
        plate = a.slab(f"head_plate{c0}", B.rect(c0, c1, 21, 30, 0.1), 12.1, 12.8, m["g9"], bevel=0.25, segments=1)
        shade(plate, m["g9"], m["ga"], m["g6"])
    # The skylight: a glass vault along the top (bright at its back, teal at its front) with three ribs.
    vault_x0, vault_x1 = B.left(17), B.right(27)
    vx, vr = (vault_x0 + vault_x1) / 2, (vault_x1 - vault_x0) / 2
    length = B.top(19) - B.bottom(30)
    vault = a.lathe_axis("skylight", [(0.0, 0.01), (0.3, vr * 0.9), (0.9, vr), (length - 0.9, vr),
                                      (length - 0.3, vr * 0.9), (length, 0.01)],
                         m["glass"], (vx, B.top(19) - 0.2, 11.6), (0, -1, 0), segments=24, squash=0.5)
    a.paint_faces(vault, lambda c, nrm: m["glass"] if c.y > B.bottom(23) else m["glass_low"])
    for i in range(3):
        x = B.right(19 + 3 * i) - 0.5
        dz = 11.6 + 0.5 * vr * math.sqrt(max(0.0, 1 - ((x - vx) / vr) ** 2))
        a.tube(f"vault_rib{i}", [(x, B.top(19) - 0.8, dz), (x, B.bottom(30) + 0.5, dz)], 0.3, m["panel_dark"], 6)
    # The blue lamps either side of it.
    for c in (14.5, 29.5):
        sphere(f"lamp{c}", (B.X(c), B.Y(24.5), 12.7), (1.1, 1.1, 0.8), m["lamp"], 12, 6)

    # The front: a dark recess between two rails, the windows and the lens in it.
    a.slab("recess", B.rect(14, 29, 36, 49, 0.0), 8.2, 8.75, m["g2"], bevel=0.2, segments=1)
    for c0, c1 in ((11, 13), (30, 32)):
        rail = a.slab(f"front_rail{c0}", B.rect(c0, c1, 34, 48, 0.1), 8.0, 9.6, m["g9"], bevel=0.45, segments=2)
        a.paint_faces(rail, lambda c, nrm: m["g9"] if nrm.z > 0.9 else m["teal"] if nrm.z < 0.4 else m["ga"])
    for c0, c1 in ((15, 19), (24, 28)):
        a.slab(f"window{c0}", B.rect(c0, c1, 38, 40, 0.1), 8.4, 9.1, m["window"], bevel=0.15, segments=1)
        a.slab(f"slit{c0}", B.rect(c0, c1, 37, 37, 0.15), 8.4, 9.0, m["slit"], bevel=0.1, segments=1)
    divider = a.slab("divider", B.rect(20, 23, 37, 40, 0.1), 8.4, 9.3, m["g7"], bevel=0.25, segments=1)
    shade(divider, m["g7"], m["g8"], m["g5"])
    lx, ly = (B.left(16) + B.right(29)) / 2, (B.top(41) + B.bottom(48)) / 2
    sphere("lens", (lx, ly, 8.6), (6.6, 3.7, 1.9), m["lens"], 28, 10)
    sphere("lens_hot", (lx - 0.8, ly - 0.2, 9.6), (3.6, 1.8, 0.9), m["lens_hot"], 20, 8)
    sphere("lens_white", (lx - 1.6, ly + 0.3, 10.2), (1.4, 0.7, 0.45), m["lens_white"], 12, 6)


a.pieced("ice_bunker", build_bunker, (48, 56), quarters("ice_bunker", BUNKER, bunker_keep))


# --- 7 169 / 207: the red dome with its arm ---------------------------------------------------------

DRILL = a.frame("DRILL", 24, (12, 28))
DX = -1.0      # the object's axis (between the sprite's columns 10 and 11)
ARM_Z = 4.8    # the arm's axis above the ground


def build_drill():
    red = pal("drill_red", 0x76, metallic=0.35, roughness=0.3)
    red_dark = pal("drill_red_dark", 0x72, metallic=0.3, roughness=0.4)
    cavity = pal("drill_cavity", 0x70, metallic=0.1, roughness=0.7)
    lamp = pal("drill_lamp", 0x77, metallic=0.0, roughness=0.25, glow=1.2)
    grey = pal("drill_grey", 0x09, metallic=0.65, roughness=0.25)
    grey_light = pal("drill_grey_light", 0x0c, metallic=0.65, roughness=0.2)
    grey_dark = pal("drill_grey_dark", 0x05, metallic=0.55, roughness=0.35)

    def red_paint(obj):
        a.paint_faces(obj, lambda c, nrm: red if nrm.z > -0.2 else red_dark)

    def grey_paint(obj):
        a.paint_faces(obj, lambda c, nrm: grey if nrm.z > -0.25 else grey_dark)

    # The dome: a red hood over the arm's piston, open at its front between two cheeks.
    dome = sphere("dome", (DX, 16.6, 0.0), (10.3, 11.4, 10.4), red, 36, 18)
    a.carve(dome, (DX, 3.0, 0.0), (8.6, 20.0, 15.6))
    a.carve(dome, (DX, 16.6, -6.0), (30.0, 30.0, 12.0))
    red_paint(dome)
    # The fingers of the hood's cheeks, curling down over the piston's sides, tapering to blunt points.
    for side in (-1, 1):
        for v, y0, y1 in ((8.0, 13.0, 6.4), (5.6, 12.0, 6.0)):
            x = DX + side * v
            u = ((x - DX) / 10.3) ** 2 + ((y0 - 16.6) / 11.4) ** 2
            z0 = 10.4 * math.sqrt(max(0.0, 1 - u)) - 1.0
            path = a.catmull([(x, y0, z0), (x + side * 0.4, y0 - 3.0, z0 * 0.8), (x + side * 0.5, y1 + 0.8, 2.6),
                              (x + side * 0.3, y1, 1.0)], 0.6)
            radii = [1.35 - 0.8 * i / (len(path) - 1) for i in range(len(path))]
            red_paint(a.tube(f"finger{side}_{v}", path, radii, red, 10))
    # The cavity behind the opening, and the seam along the top.
    a.rounded_box("cavity", (DX, 9.6, 3.8), (8.4, 6.0, 7.6), cavity, bevel=0.4, segments=1)
    seam = []
    for i in range(7):
        yy = 22.5 - 1.5 * i
        seam.append((DX, yy, 10.4 * math.sqrt(max(0.0, 1 - ((yy - 16.6) / 11.4) ** 2)) - 0.1))
    a.tube("seam", seam, 0.4, red_dark, 6)
    # The lamp on its back: an orange panel (its frames light it up; this frame has it dim).
    sphere("lamp", (DX + 0.2, 24.2, 7.3), (4.1, 2.6, 1.3), lamp, 20, 8)

    # The arm, along the axis down the screen: the piston in the dome, the red collar, a rod, the flange, the
    # red knuckle, the grey head with its point.
    piston = a.lathe_axis("piston", [(0.0, 0.01), (0.2, 3.4), (8.6, 3.6), (9.2, 3.0), (9.4, 0.01)], grey,
                          (DX, 14.4, ARM_Z), (0, -1, 0), segments=24)
    grey_paint(piston)
    collar = a.lathe_axis("collar", [(0.0, 0.01), (0.2, 4.6), (1.4, 5.2), (3.6, 4.9), (5.0, 4.2), (5.4, 3.6),
                                     (5.6, 0.01)], red, (DX, 6.2, ARM_Z), (0, -1, 0), segments=24)
    red_paint(collar)
    rod = a.lathe_axis("rod", [(0.0, 0.01), (0.1, 2.0), (2.0, 2.0), (2.1, 0.01)], grey_dark, (DX, 0.9, ARM_Z),
                       (0, -1, 0), segments=16)
    flange = a.lathe_axis("flange", [(0.0, 0.01), (0.2, 3.6), (0.9, 4.6), (3.0, 4.6), (3.8, 3.4), (4.0, 0.01)],
                          grey, (DX, -0.5, ARM_Z), (0, -1, 0), segments=24)
    grey_paint(flange)
    a.lathe_axis("rod2", [(0.0, 0.01), (0.1, 1.6), (3.4, 1.6), (3.5, 0.01)], grey_dark, (DX, -4.2, ARM_Z), (0, -1, 0),
                 segments=14)
    knuckle = sphere("knuckle", (DX, -8.6, ARM_Z), (2.8, 2.0, 2.6), red, 18, 10)
    red_paint(knuckle)
    head = sphere("head", (DX, -15.7, ARM_Z), (6.9, 6.0, 4.8), grey, 32, 16)
    grey_paint(head)
    # The dark band round the head's middle.
    a.lathe_axis("head_band", [(0.0, 6.5), (0.2, 7.05), (0.9, 7.05), (1.1, 6.5)], grey_dark, (DX, -15.0, ARM_Z),
                 (0, -1, 0), segments=28, squash=0.72)
    tip = a.cone("tip", (DX, -19.6, ARM_Z), (0, -1, 0), 5.0, 4.0, grey_light, segments=16)
    a.paint_faces(tip, lambda c, nrm: grey_light if nrm.z > -0.25 else grey_dark)
    a.rounded_box("bracket", (DX + 6.2, -16.0, ARM_Z), (1.6, 7.0, 3.0), grey_dark, bevel=0.5, segments=1)


a.pieced("ice_drill", build_drill, (24, 56),
         [("ice_drill_dome", (-12.0, 12.0, 0.0, 28.0), (0.0, 14.0), lambda: a.object_mask(DRILL, (0, 24, 0, 28))),
          ("ice_drill_arm", (-12.0, 12.0, -28.0, 0.0), (0.0, -14.0), lambda: a.object_mask(DRILL, (0, 24, 28, 56)))])


if __name__ == "__main__":
    a.run()
