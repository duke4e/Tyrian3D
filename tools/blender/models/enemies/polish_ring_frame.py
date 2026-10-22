"""The grey frame with a blue orb of ICE EXIT, BRAINIAC, ICESECRET and DREAD-NOT (and GRAVITRON in episode 6): sheet 3
sprite 271, 2x2 (a 23 x 25 device in the 24 x 28 cell); enemies 416 of episode 4 and 1664 of episode 6, armour 255 (it
cannot be shot down), one frame, not animated. Polished (2026-10-22, round 36; it replaces wave1_d.py's ring_frame(), an
outline inflated into a pillow with an orb, a canister and inlays laid on it). models.cfg: sprite 3 271 ring_frame yaw=0
(the line as it is).

Where it appears: ICE EXIT (t3700) and BRAINIAC (t5300) bring it up from the bottom of the screen at the boss (sky
enemy, event 18, vy -1, link 183) and stop it there; GRAVITRON twice (t2902, t3353) the same way; DREAD-NOT puts it on
the ground (t300, event 6, vy 2). Without "origin" the game centres it in height on its layer (sky or ground). It is
not another sprite's pixels mirrored, turned or in other ramps; it is the blue sibling of the ring machine of the lava
levels (3 195, polish_ring_machine.py: a frame round a see-through hole with a dome over a hub), whose relief() builds
its parts, so that the two match.

As the sprite and its 4x upscale draw it (columns and rows of the sprite; symmetric about the middle of column 12 in
shape, its right half darker, in the shadow of the light from the upper left): a heavy grey frame (ramp 0: 06 lit
down its left, 04 on its right, 0a and the blue-grey 6a along its inner edge) round a hole (columns 7-17 of rows
7-16), see-through below the orb; a glossy blue orb (ramp 3, 31-3e, its highlight at column 11 of row 10) hanging in
the hole's top half (columns 8-16 of rows 7-14), the ring's band over it (row 6); on top of the ring a short neck
(columns 7-17 of rows 1-6, waisted at row 4) with two blue strips down it (columns 11 and 13); at its upper corners
two dark posts rising like horns (columns 1-4 and 20-23 of rows 3-8), a blue strip down each (columns 3 and 21);
under the hole a crossbar lit along its top (0a-0d, rows 17-19); below it a blue canister lying down the screen
(columns 9-15 of rows 19-25), lit along its top (3d 3e, row 21), grey feet either side of it (columns 5-8 and 16-19 of
rows 22-25) and two small blue lamps at the lower corners (columns 4-6 and 18-20 of rows 20-22).

Built as the ring machine is: the frame a relief() over its outline with the hole open (its outer edge rounded, its
top at 2, its underside at -2.2), a light ring standing on it round the hole (to 3, its inner half the blue-grey 6a,
the rest 0a; across the bottom it is the crossbar's lit top, which stands to 2.7 under it), the neck and the posts
reliefs standing higher (3.4, 4.2) with the blue strips laid in them (lit a little: they read as lit panels), the orb
a ball lofted from explicit rings hanging in the hole (its glare painted at the upper left, a little light of its own:
round things read near black from the game's slanted camera), the canister lathed along y with two grey bands round
it and its lit top painted, the feet low reliefs, the lamps small domes that glow. Heights from the orb's underside
(z -3.1) to its top (4.9). Colours are the sprite's palette indices: greys 0x03 0x06 0x0a 0x0c, blue-grey 0x6a,
blues 0x32 0x36 0x37 0x38 0x39 0x3a 0x3b 0x3d; emissions in their own blues: the strips 0.3, the orb 0.3-0.35, the
canister 0.2, the lamps 0.55.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera. Built about the
axis x = 0 (the middle of column 12: px(c, r) = (c - 12.5, 14 - r) for a pixel corner (column c, row r)), the left
half's outlines mirrored, then moved by AXIS_X so that the sprite's centre (its pixel corner 12, 14) is the origin.

Replaces wave1_d.py's ring_frame (its "# --- The ring frame (sheet 3 271)" section: relabel() and ring_frame() with its
@model registration; the "# --- The sprites' origin" section, SPRITE_ORIGIN, which only ring_frame() reads; the
ring_frame line of its docstring) and wave1_d_art.py's RING, which only ring_frame() reads. wave1_d.py's pincer is the
FLEET agent's this round.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against
enemy_3.png), --preview <prefix>.
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
from polish_ring_machine import relief, Region, chaikin, ccw, round_edge, px, to_model, mirrored  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402

AXIS_X = 0.5

# The device's outline, its left half from the top middle down to the bottom middle (column, row): the neck's cap
# (rows 1-3) and waist (row 4), the ring's shoulder, the notch between the neck and the post (down to row 7.6 at
# column 5.6), the post (columns 1-4 from row 3), the frame's straight left side (column 1, rows 6-11) stepping in
# to column 3 (rows 13-16), the crossbar's end (column 2, rows 17-19), the canister's foot (columns 3-5, rows 20-26).
OUTLINE_LEFT = [(12.5, 0.95), (10.0, 0.95), (9.2, 1.35), (7.6, 1.95), (7.0, 2.5), (7.5, 3.0), (8.4, 3.5),
                (8.9, 4.2), (8.7, 4.9), (8.0, 5.2), (7.3, 5.6), (6.8, 6.2), (6.3, 6.75), (6.0, 7.25), (5.5, 8.0),
                (5.05, 7.3), (5.0, 6.4), (5.0, 4.6), (4.7, 3.5), (4.1, 2.95), (3.2, 2.95), (2.45, 3.55),
                (2.0, 4.4), (1.75, 5.4), (1.2, 6.2), (1.0, 7.2), (1.0, 11.2), (1.4, 12.1), (2.2, 12.7),
                (2.85, 13.4), (3.0, 14.4), (3.0, 16.3), (2.5, 16.9), (2.05, 17.5), (2.0, 19.4), (2.5, 19.9),
                (3.0, 20.5), (3.05, 21.7), (3.6, 22.4), (4.4, 22.8), (4.95, 23.4), (5.0, 25.3), (5.6, 25.95),
                (8.5, 26.0), (12.5, 26.0)]
# The hole: its middle, half-width and half-height (pixel corners: columns 7-18, rows 7-17) and its corners'
# roundness (a superellipse of this power: 2 an ellipse, larger squarer).
HOLE_CENTRE, HOLE_HALF, HOLE_POWER = (12.5, 12.55), (5.5, 4.55), 4.6
# The orb: its middle (column, row), radius in plan and height; its glare's middle and size, its bands.
ORB_CENTRE, ORB_RADII, ORB_Z = (12.5, 11.0), (4.45, 4.0, 4.0), 0.9
GLARE, GLARE_SIZE, GLARE_BANDS = (11.4, 9.9), (2.0, 1.8), (0.3, 1.0)
# The neck (its blue strips: columns 11 and 13, rows 1.6-5.6), the posts (the strip: column 3, rows 3.8-8.4).
NECK = [(12.5, 1.1), (10.3, 1.1), (8.9, 1.4), (7.7, 1.9), (7.35, 2.5), (7.9, 3.1), (8.75, 3.7), (9.1, 4.3),
        (8.9, 5.0), (8.1, 5.5), (7.8, 6.1), (8.6, 6.7), (12.5, 6.7)]
NECK_STRIPS = [(11.05, 11.95, 1.7, 5.9), (13.05, 13.95, 1.7, 5.9)]
POST = [(4.8, 4.5), (4.5, 3.4), (3.95, 3.05), (3.3, 3.05), (2.6, 3.6), (2.15, 4.5), (1.95, 5.6), (1.95, 7.6),
        (2.5, 8.6), (3.6, 9.0), (4.6, 8.4), (4.95, 7.2)]
POST_STRIP = (2.75, 4.25, 3.85, 8.4)
# The crossbar under the hole (its lit top: rows 17.6-19.4) and the canister lying under it (axis along y; its
# ends at rows 19.2 and 25.9, its radius, its axis' height), two grey bands round it.
CROSSBAR = [(12.5, 17.05), (3.2, 17.05), (2.6, 17.6), (2.5, 19.2), (3.4, 19.7), (8.2, 19.9), (12.5, 19.9)]
CAN_ENDS, CAN_RADIUS, CAN_Z = (19.2, 25.9), 3.05, 0.45
CAN_BANDS = (21.9, 24.6)
# The lamps at the lower corners (middle, half-axes in plan).
LAMP, LAMP_RADII = (5.5, 21.4), (1.25, 1.05)
# The feet beside the canister.
FOOT = [(5.3, 22.7), (8.6, 22.0), (8.9, 23.5), (8.8, 25.6), (5.6, 25.7), (5.2, 25.0)]

# The ring round the hole (the sprite's light band, 0a and 6a: columns 5-7 and 17-19, row 6, the crossbar's top):
# its outer edge a superellipse this much wider and higher than the hole's, the same power.
RING_OUT, RING_POWER = (1.95, 1.75), 3.6
# Heights: the frame's top, its underside, its rounded outer edge; the ring over the frame and its rounded edges;
# the neck, the posts, the crossbar, the feet.
FRAME_TOP, FRAME_BOTTOM, FRAME_RIM = 2.0, -2.2, 1.4
RING_TOP, RING_RIM = 3.0, 0.7
NECK_TOP, POST_TOP, BAR_TOP, FOOT_TOP = 3.4, 4.2, 2.7, 2.2


def full(left):
    """A symmetric outline: the left half (from the top middle down to the bottom middle) and its mirror image."""
    pts = to_model(left)
    right = [(-x, y) for x, y in reversed(pts[1:-1])]
    return ccw(pts + right)


def hole(grow=(0.0, 0.0), power=None):
    cx, cy = px(*HOLE_CENTRE)
    ax, ay = HOLE_HALF[0] + grow[0], HOLE_HALF[1] + grow[1]
    p = power or HOLE_POWER
    out = []
    for i in range(112):
        a = 2 * math.pi * i / 112
        c, s = math.cos(a), math.sin(a)
        out.append((cx + ax * math.copysign(abs(c) ** (2 / p), c), cy + ay * math.copysign(abs(s) ** (2 / p), s)))
    return ccw(out)


def materials():
    pal = k.level_palette()

    def m(name, index, metallic, roughness, glow=None, strength=0.0):
        extra = dict(emission=pal[glow], emission_strength=strength) if glow is not None else {}
        return k.material("ringf_" + name, palette=index, metallic=metallic, roughness=roughness, **extra)
    return {
        "frame": m("frame", 0x06, 0.5, 0.38),
        "frame_light": m("frame_light", 0x0a, 0.45, 0.32),
        "frame_side": m("frame_side", 0x03, 0.5, 0.45),
        "bead": m("bead", 0x6a, 0.45, 0.28),
        "bar_light": m("bar_light", 0x0c, 0.45, 0.28),
        "dark": m("dark", 0x32, 0.45, 0.35),
        "strip": m("strip", 0x39, 0.3, 0.25, 0x37, 0.3),
        "orb": m("orb", 0x36, 0.25, 0.2, 0x35, 0.3),
        "orb_glare": m("orb_glare", 0x3a, 0.2, 0.18, 0x38, 0.3),
        "orb_core": m("orb_core", 0x3d, 0.15, 0.15, 0x3b, 0.35),
        "can": m("can", 0x37, 0.35, 0.25, 0x34, 0.2),
        "can_light": m("can_light", 0x3b, 0.3, 0.22, 0x38, 0.2),
        "lamp": m("lamp", 0x38, 0.1, 0.25, 0x39, 0.55),
    }


def frame(mats):
    """The frame: the whole outline round the hole, its outer edge rounded."""
    return relief("frame", [full(OUTLINE_LEFT), hole()],
                  lambda x, y, d: FRAME_TOP - 1.4 + 1.4 * round_edge(d, FRAME_RIM), mats,
                  paint=lambda x, y, d: "frame_side" if d < 0.3 else "frame", side="frame_side",
                  bottom=FRAME_BOTTOM, spacing=0.75, borders=[(lambda x, y, d: d, 0.3)], band=1.1)


def ring(mats):
    """The light ring round the hole, standing on the frame: rounded edges, its inner half blue-grey."""
    inner = Region([hole()])

    def to_hole(x, y):
        return float(inner.distance([(x, y)])[0])

    def paint(x, y, d):
        return "bead" if to_hole(x, y) < 0.85 else "frame_light"
    return relief("ring", [hole(RING_OUT, RING_POWER), hole()], lambda x, y, d: 1.0 + (RING_TOP - 1.0) *
                  round_edge(d, RING_RIM), mats, paint=paint, side="frame_side", bottom=0.0, spacing=0.46,
                  borders=[(lambda x, y, d: to_hole(x, y), 0.85)])


def strip_paint(boxes):
    """paint() and borders for blue strips (column and row boxes) laid in a part's top."""
    model = []
    for c0, c1, r0, r1 in boxes:
        (x0, y1), (x1, y0) = px(c0, r0), px(c1, r1)
        model.append((min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1)))

    def inside(x, y):
        return any(x0 < x < x1 and y0 < y < y1 for x0, x1, y0, y1 in model)
    borders = []
    for x0, x1, y0, y1 in model:
        borders += [(lambda x, y, d: x, x0), (lambda x, y, d: x, x1), (lambda x, y, d: y, y0),
                    (lambda x, y, d: y, y1)]
    return inside, borders


def neck(mats):
    inside, borders = strip_paint(NECK_STRIPS)
    poly = ccw(chaikin(full(NECK), 1))

    def height(x, y, d):
        return 1.0 + (NECK_TOP - 1.0) * round_edge(d, 1.0)

    def paint(x, y, d):
        if d < 0.3:
            return "frame_side"
        return "strip" if inside(x, y) else "frame"
    return relief("neck", [poly], height, mats, paint=paint, side="frame_side", bottom=0.0, spacing=0.68,
                  borders=[(lambda x, y, d: d, 0.3)] + borders)


def posts(mats):
    out = []
    for side in (1, -1):
        pts = to_model(POST)
        c0, c1, r0, r1 = POST_STRIP
        if side == -1:
            pts = mirrored(pts)
            c0, c1 = 25.0 - c1, 25.0 - c0
        inside, borders = strip_paint([(c0, c1, r0, r1)])
        poly = ccw(chaikin(pts, 1))

        def height(x, y, d):
            return 1.2 + (POST_TOP - 1.2) * round_edge(d, 1.1)

        def paint(x, y, d, inside=inside):
            if d < 0.3:
                return "frame_side"
            return "strip" if inside(x, y) else "dark"
        out.append(relief("post_l" if side == 1 else "post_r", [poly], height, mats, paint=paint, side="frame_side",
                          bottom=0.0, spacing=0.5, borders=[(lambda x, y, d: d, 0.3)] + borders))
    return out


def crossbar(mats):
    poly = ccw(chaikin(full(CROSSBAR), 1))

    def height(x, y, d):
        return 1.2 + (BAR_TOP - 1.2) * round_edge(d, 0.9)
    return relief("crossbar", [poly], height, mats, paint=lambda x, y, d: "frame_side" if d < 0.3 else "bar_light",
                  side="frame_side", bottom=0.0, spacing=0.7, borders=[(lambda x, y, d: d, 0.3)])


def feet(mats):
    out = []
    for side in (1, -1):
        pts = to_model(FOOT)
        if side == -1:
            pts = mirrored(pts)
        poly = ccw(chaikin(pts, 1))
        out.append(relief("foot_l" if side == 1 else "foot_r", [poly],
                          lambda x, y, d: 0.8 + (FOOT_TOP - 0.8) * round_edge(d, 0.8), mats,
                          paint=lambda x, y, d: "frame_side" if d < 0.25 else "frame", side="frame_side",
                          bottom=0.0, spacing=0.5, borders=[(lambda x, y, d: d, 0.25)]))
    return out


def orb(mats):
    """The orb: a ball lofted from explicit rings, hanging in the hole, its glare at the upper left."""
    cx, cy = px(*ORB_CENTRE)
    obj = k.ellipsoid("orb", (cx, cy, ORB_Z), ORB_RADII, None, 30, 14)
    gx, gy = px(*GLARE)
    for key in ("orb", "orb_glare", "orb_core"):
        obj.data.materials.append(mats[key])
    for poly in obj.data.polygons:
        c = poly.center
        q = ((c.x - gx) / GLARE_SIZE[0]) ** 2 + ((c.y - gy) / GLARE_SIZE[1]) ** 2
        poly.material_index = 0 if c.z < ORB_Z + 0.8 or q >= GLARE_BANDS[1] else (1 if q >= GLARE_BANDS[0] else 2)
    return k.smooth(obj, 70)


def canister(mats):
    """The canister lying down the screen under the crossbar: lathed along y, rounded ends, two grey bands, its
    top lit."""
    y_top, y_bot = px(0, CAN_ENDS[0])[1], px(0, CAN_ENDS[1])[1]
    r = CAN_RADIUS
    prof = [(y_bot, 0.01), (y_bot + 0.08, r * 0.55), (y_bot + 0.35, r * 0.82), (y_bot + 0.9, r * 0.97),
            (y_bot + 1.6, r), (y_top - 1.4, r), (y_top - 0.7, r * 0.93), (y_top - 0.25, r * 0.72),
            (y_top, 0.01)]
    obj = k.lathe("canister", prof, None, 28, axis_x=0.0, axis_z=CAN_Z)
    obj.data.materials.append(mats["can"])
    obj.data.materials.append(mats["can_light"])
    for poly in obj.data.polygons:
        c = poly.center
        poly.material_index = 1 if (c.z - CAN_Z) > 0.78 * r and c.x < 1.4 else 0
    k.smooth(obj, 50)
    bands = []
    for row in CAN_BANDS:
        y = px(0, row)[1]
        band = k.lathe("can_band", [(y - 0.42, r - 0.05), (y - 0.3, r + 0.28), (y + 0.3, r + 0.28),
                                    (y + 0.42, r - 0.05)], mats["frame"], 28, axis_x=0.0, axis_z=CAN_Z)
        bands.append(k.smooth(band, 50))
    return [obj] + bands


def lamps(mats):
    out = []
    lx, ly = px(*LAMP)
    for name, x in (("lamp_l", lx), ("lamp_r", -lx)):
        obj = k.ellipsoid(name, (x, ly, 0.9), (LAMP_RADII[0], LAMP_RADII[1], 1.0), mats["lamp"], 16, 8)
        out.append(k.smooth(obj, 60))
    return out


def build_device(mats):
    frame(mats)
    ring(mats)
    neck(mats)
    posts(mats)
    crossbar(mats)
    feet(mats)
    orb(mats)
    canister(mats)
    lamps(mats)
    objs = mk.meshes()
    for obj in objs:
        obj.data.transform(Matrix.Translation((AXIS_X, 0.0, 0.0)))
    return objs


def build():
    options = k.args()
    k.reset()
    objs = build_device(materials())
    parts = triangulate(objs)
    bpy.context.view_layer.update()
    for obj in parts:
        print("  %-12s %6d triangles" % (obj.name, mk.triangles([obj])))
    if "check" in options:
        sheet = os.path.join(options["check"], "enemy_3.png")
        mk.compare("ring_frame (3 271)", mk.coverage(parts, 24, 28), k.sprite_mask(sheet, 271))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mk.report("ring_frame", parts, os.path.join(mk.outdir(options), "ring_frame.glb"))
    if "preview" in options:
        mk.preview(options["preview"] + "ring_frame", parts)


if __name__ == "__main__":
    build()
