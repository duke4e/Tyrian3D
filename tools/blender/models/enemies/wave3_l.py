"""Wave 3, batch L of the enemy models: the remaining enemies of sheet 5 (episode 4), authored as their sprites
look (models.cfg: yaw=0 unless noted; the stinger, 5 207: polish_flesh_stinger.py):

- purple_beacon (5 3): HARVEST's purple machine with horned lobes and two glowing green slots.
- eye_hatch (5 164): BRAINIAC's floor hatch with a red eye glowing between two lids (the purple octagon and
  the dark corners the sprite draws round it are the map's floor, not modelled).
- stone_fist, stone_fist_r (5 81, 5 83): BRAINIAC's faceted grey stones at the screen's edges (mirror images).
- hanging_pod (5 170): BRAINIAC's grey pod with a red eye hanging from a steel bracket.
- arrow_left, arrow_right (5 247, 5 266): DREAD-NOT's and EYESPY's glowing green arrows (mirror images).

The objects drawn from several sprites are in wave3_l_parts.py; the pixel art in wave3_l_art.py. (EYESPY's ears,
5 245 and 5 284: polish_ears.py; APPROACH's tan fighter, 5 49: polish_tan_fighter.py.)

usage: blender -b --factory-startup -P wave3_l.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1]
       blender -b --factory-startup -P wave3_l.py -- --whole <prefix> [--only object] [--check 1]
--preview renders <prefix><name>_top.png and _3q.png for each model; --check prints each model's
silhouette overlap with its sprite; --whole renders the objects the game draws in pieces, whole.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_l_art as art  # noqa: E402
import wave3_l_kit as w  # noqa: E402
import wave3_l_parts as parts  # noqa: E402
from wave3_l_kit import k, sh, pal, model  # noqa: E402


# --- 5 3: HARVEST's purple machine -----------------------------------------------------------------

@model("purple_beacon", 3)
def purple_beacon():
    """HARVEST's purple machine, as drawn: two horned lobes at the top curving down into a neck, a brow
    with two dark eye pits, ribbed shoulders sweeping down to both sides, and below them a block with
    two glowing green slots (the frames run a green bar down them; the model keeps the slots lit).
    Each part is inflated from its region of the sprite's pixels."""
    rows = [list(r) for r in art.BEACON.strip("\n").split("\n")]
    for c in (9, 14):
        rows[13][c] = "4"  # the eye pits are modelled
    a = w.Art("\n".join("".join(r) for r in rows), (12, 14))
    hull = pal("beacon_hull", 0x58, metallic=0.4, roughness=0.35)
    light = pal("beacon_light", 0x5b, metallic=0.4, roughness=0.3)
    dark = pal("beacon_dark", 0x54, metallic=0.3, roughness=0.5)
    green = pal("beacon_green", 0xc9, metallic=0.1, roughness=0.2, glow=1.6)
    mid = pal("beacon_mid", 0x56, metallic=0.4, roughness=0.38)

    def region(name, keep, mat, aspect, max_h, z_fn=None):
        polys = a.polys(rows=a.select(keep), smooth=2, epsilon=0.4)
        obj = w.rounded(name, polys, mat, aspect=aspect, max_height=max_h, spacing=0.55, z_fn=z_fn)
        return w.simplify_flat(obj)
    # The shoulders, sloping down outwards, with folds along them.
    shoulders = region("shoulders", lambda c, r, ch: (c <= 6 or c >= 17) and r >= 10, mid, 0.8, 4.2,
                       z_fn=lambda x, y, z: z * (1.0 - 0.45 * w.smoothstep(6.0, 12.0, abs(x))) + 0.6)
    for side in (-1, 1):
        for i, x in enumerate((side * 9.5, side * 6.8)):
            path = [(x, y) for y in (3.6, 1.0, -2.0, -5.0, -7.2 + 0.6 * i)]
            pts = w.catmull([(px, py, sh.surface_z(shoulders, px, py, 2.0) - 0.15) for px, py in path], 0.6)
            w.tube(f"fold{side}{i}", pts, 0.55, light, 8)
    # The lower block with its glowing slots and a ridge down the middle.
    block = region("block", lambda c, r, ch: 6 <= c <= 17 and r >= 15, hull, 0.9, 5.0)
    w.paint(block, lambda c, n: 1 if abs(c.x) < 2.6 and n.z > 0.3 else 0, [hull, dark])
    w.tube("ridge", [(0.0, -3.4, 4.6), (0.0, -7.0, 4.4), (0.0, -10.4, 3.4)], 0.6, light, 8)
    for side in (-1, 1):
        x = side * 4.0
        slot = w.plate(f"slot{side}", [w.rounded_rect(x, -6.6, 1.1, 3.9)], green, 0.5, radius=0.4, base=-0.3,
                       spacing=0.3)
        w.on_surface(slot, block, sink=0.0)
    # The brow across the middle, with two dark eye pits.
    brow = region("brow", lambda c, r, ch: 4 <= c <= 19 and 10 <= r <= 15, hull, 0.9, 5.6)
    for side in (-1, 1):
        x, y = side * 2.5, 0.5
        w.sphere(f"eye{side}", (x, y, sh.surface_z(brow, x, y, 4.0) - 0.5), (1.1, 0.9, 0.8), dark, 12, 6)
    # The neck and the head, two horned lobes curving into it.
    head = region("head", lambda c, r, ch: r <= 11 and 5 <= c <= 18, mid, 1.0, 6.4)
    for side in (-1, 1):
        path = [(side * 2.6, 13.4), (side * 3.4, 11.2), (side * 2.9, 8.4), (side * 1.6, 5.6), (side * 0.9, 3.4)]
        pts = w.catmull([(x, y, sh.surface_z(head, x, y, 4.0) - 0.4) for x, y in path], 0.5)
        radii = [1.6 - 0.7 * i / (len(pts) - 1) for i in range(len(pts))]
        w.tube(f"horn{side}", pts, 1.0, light, 10, radii=radii)
    for obj in w.meshes():
        w.lift(obj, -2.5)


# --- 5 164: BRAINIAC's hatch with a red eye ----------------------------------------------------------

@model("eye_hatch", 164)
def eye_hatch():
    """A hatch in BRAINIAC's floor: a dark housing sunk round a dark socket in which a red eye glows between
    two lids (the frames open and close it; the model keeps it half open), a dark hood over the eye and a
    block under it. The purple octagon the sprite draws it in (its arms reaching to the square's edges) and
    the dark corners are the floor's own pattern, which the map draws under it: not modelled (batch AV)."""
    frame = pal("hatch_frame", 0x56, metallic=0.35, roughness=0.4)
    light = pal("hatch_light", 0x59, metallic=0.35, roughness=0.35)
    dark = pal("hatch_dark", 0x51, metallic=0.3, roughness=0.5)
    housing = pal("hatch_housing", 0x53, metallic=0.35, roughness=0.45)
    red = pal("hatch_eye", 0x77, metallic=0.0, roughness=0.15, glow=1.6)
    hot = pal("hatch_eye_hot", 0x7b, metallic=0.0, roughness=0.1, glow=2.2)
    ex, ey = 0.5, 1.2  # the eye's centre

    def frame_z(x, y, z):
        q = math.hypot((x - ex) / 6.4, (y - ey) / 7.4)
        return z - 2.0 * w.smoothstep(1.15, 0.75, q) * min(1.0, z / 2.0)
    # The housing: the sprite's dark machine (columns 4-19, rows 3-21), its middle sunk round the socket.
    outline = [(-3.6, 10.6), (3.8, 10.6), (6.6, 7.8), (7.7, 3.4), (7.7, -3.6), (6.2, -7.7), (-5.2, -7.7),
               (-7.6, -3.6), (-7.6, 3.4), (-6.6, 7.8)]
    body = w.plate("frame", [sh._chaikin(outline, 2)], housing, 3.0, radius=1.2, base=0.0, spacing=0.5,
                   z_fn=frame_z)
    w.simplify_flat(body)
    # A purple ring round its top edge.
    rim = sh.inset(sh._chaikin(outline[::-1], 2), 0.9)
    w.tube("rim", [(x, y, sh.surface_z(body, x, y, 2.6) - 0.1) for x, y in rim + rim[:1]], 0.4, frame, 6)
    # The hood over the eye and the block under it (the sprite's dark plates above and below the socket).
    w.rounded_box("hood", (-0.2, 7.8, 2.0), (5.0, 5.6, 4.0), dark, bevel=0.9)
    w.rounded_box("hood_edge", (-0.2, 5.2, 3.7), (4.4, 0.8, 0.8), light, bevel=0.3)
    w.rounded_box("block", (0.6, -5.2, 1.6), (8.2, 4.4, 3.2), dark, bevel=0.8)
    # The socket: a dark bowl round the eye, its rim a ring.
    w.sphere("socket", (ex, ey, 1.4), (5.6, 4.4, 1.2), dark, 24, 8)
    rim = [(ex + 5.9 * math.cos(t), ey + 4.8 * math.sin(t)) for t in [2 * math.pi * i / 32 for i in range(33)]]
    w.tube("socket_rim", [(x, y, 2.0) for x, y in rim], 0.55, dark, 6)
    # The eye and its lids, leaving a slit across the middle.
    w.sphere("eye", (ex, ey, 1.6), (4.6, 3.3, 1.7), red, 24, 10)
    w.sphere("eye_hot", (ex - 0.2, ey + 0.1, 2.6), (2.6, 0.9, 0.9), hot, 16, 6)
    for side in (-1, 1):
        w.sphere(f"lid{side}", (ex, ey + side * 2.3, 1.9), (5.0, 2.2, 1.9), frame, 24, 10)
    for obj in w.meshes():
        k.recalc_normals(obj)


# --- 5 81, 5 83: BRAINIAC's stone fists -----------------------------------------------------------

def stone_fist(mirror):
    """A chunk of grey stone on the ground, cut in facets (sprite 81; 83 is its mirror image): a lumpy
    body over the sprite's outline, its relief from the sprite's shading, collapsed into a few
    hundred flat facets and coloured facet by facet in three greys."""
    a = w.Art(art.FIST, (12, 14))
    shade = w.shade_field(a, blur=1, skip="o")
    bands = [(-9.0, pal("fist_dark", 0x05, metallic=0.2, roughness=0.7)),
             (5.2, pal("fist_mid", 0x08, metallic=0.2, roughness=0.65)),
             (8.6, pal("fist_light", 0x0b, metallic=0.2, roughness=0.6))]
    polys = a.polys(smooth=1, epsilon=0.4)
    body = w.rounded("stone", polys, bands[1][1], aspect=0.85, max_height=7.5, spacing=0.4,
                     z_fn=lambda x, y, z: z + 0.45 * (shade(x, y) - 7.0) * w.smoothstep(0.5, 2.0, z))
    w.decimate(body, 360)
    k.smooth(body, 12)
    w.paint_bands(body, lambda c, n: shade(c.x, c.y) + 2.0 * (n.z - 0.6) + 1.2 * (n.x * -0.5 + n.y * 0.5), bands)
    if mirror:
        w.mirror_objects(w.meshes())


model("stone_fist", 81)(lambda: stone_fist(False))
model("stone_fist_r", 83)(lambda: stone_fist(True))


# --- 5 170: the hanging pod (5 168, BRAINIAC's red link: polish_red_link.py) ------------------------

@model("hanging_pod", 170)
def hanging_pod():
    """A grey pod hanging from a steel bracket (a bar across the top and posts down both sides): a
    domed head over a darker face with a red eye glowing in a socket."""
    metal = pal("hpod_metal", 0x68, metallic=0.65, roughness=0.3)
    light = pal("hpod_metal_light", 0x6b, metallic=0.65, roughness=0.25)
    grey = pal("hpod_grey", 0x08, metallic=0.55, roughness=0.3)
    dark = pal("hpod_dark", 0x03, metallic=0.4, roughness=0.45)
    red = pal("hpod_eye", 0x77, metallic=0.0, roughness=0.15, glow=1.6)
    hot = pal("hpod_eye_hot", 0x7b, metallic=0.0, roughness=0.1, glow=2.2)
    # The bracket.
    w.rounded_box("bar", (0.0, 11.6, 5.2), (24.0, 4.2, 2.6), metal, bevel=0.6)
    w.rounded_box("bar_light", (0.0, 12.6, 6.6), (22.0, 1.0, 0.4), light, bevel=0.15)
    for side in (-1, 1):
        w.rounded_box(f"post{side}", (side * 10.4, 4.6, 3.4), (3.2, 15.0, 3.0), metal, bevel=0.6)
        w.rounded_box(f"hook{side}", (side * 8.6, -2.0, 2.6), (3.2, 2.6, 2.4), metal, bevel=0.5)
    # The pod and its neck.
    w.lathe_axis("neck", [(0.0, 1.6), (3.0, 1.6)], light, (0.5, 7.0, 5.4), (0, 1, 0), 14)
    secs = []
    for y, hw in ((9.6, 0.5), (9.4, 3.2), (8.6, 6.0), (7.2, 7.6), (4.0, 8.2), (-4.0, 8.3), (-8.0, 8.1), (-9.6, 7.2),
                  (-10.6, 5.8), (-11.4, 3.6), (-11.8, 0.5)):
        secs.append((y, 0.5, 3.0, hw, min(4.8, hw * 0.75 + 0.8), 2.6))
    pod = w.loft_y("pod", secs[::-1], grey, segments=32, power=2.6)
    w.paint(pod, lambda c, n: 1 if c.y < -2.6 else 0, [grey, dark])
    # The eye in its socket (rows 18-22).
    w.sphere("socket", (0.5, -6.4, 6.4), (4.2, 3.6, 1.6), dark, 24, 10)
    w.sphere("eye", (0.5, -6.4, 7.0), (3.0, 2.6, 1.6), red, 24, 10)
    w.sphere("eye_hot", (0.2, -6.0, 8.0), (1.2, 1.0, 0.6), hot, 12, 6)


# --- 5 247, 5 266: the green arrows -----------------------------------------------------------------

def green_arrow(mirror):
    """A glowing green arrow pointing left (sprite 247; 266 points right): a bevelled head and shaft (rows
    3-9) with a bright line along the middle (the frames pulse it; the model keeps it lit)."""
    green = pal("arrow_green", 0xc5, metallic=0.1, roughness=0.3, glow=0.6)
    bright = pal("arrow_bright", 0xcc, metallic=0.0, roughness=0.2, glow=1.5)
    # Pixel corners of the left arrow in its 12 x 14 cell: the head (columns 0-4) and the shaft (to column 12).
    outline = [(0.0, 7.0), (3.4, 3.2), (5.0, 3.2), (5.0, 5.0), (12.0, 5.0), (12.0, 8.0), (5.0, 8.0), (5.0, 9.8),
               (3.4, 9.8)]
    poly = [(c - 6.0, 7.0 - r) for c, r in outline]
    w.bevelled_slab("arrow", poly, -0.8, 0.8, green, bevel=0.45, z_fn=lambda x, y, z: z * (1.0 + 0.6 *
                    w.smoothstep(-2.0, -5.5, x)))
    w.tube("line", [(-4.8, 0.5, 0.95), (5.6, 0.5, 0.75)], 0.42, bright, 8)
    if mirror:
        w.mirror_objects(w.meshes())


model("arrow_left", 247, large=False)(lambda: green_arrow(False))
model("arrow_right", 266, large=False)(lambda: green_arrow(True))


# --- The objects drawn in pieces (wave3_l_parts.py) ---------------------------------------------

for _name, _sprite, _builder in parts.PIECES:
    model(_name, _sprite)(_builder)

w.main()
