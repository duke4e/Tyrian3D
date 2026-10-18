"""Wave 3, batch L of the enemy models: the remaining enemies of sheet 5 (episode 4), authored as their sprites
look (models.cfg: yaw=0 unless noted):

- tan_fighter (5 49): APPROACH's tan fighter, nose down: a V tail, broad wings over grey rails, a
  brass canopy and canards by the nose.
- visor_post (5 133): DREAD-NOT's small grey post with a glowing red visor, lying as drawn.
- purple_beacon (5 3): HARVEST's purple machine with horned lobes and two glowing green slots.
- flesh_stinger (5 207): BRAINIAC's fleshy stinger, a capped beak of two halves.
- green_eye (5 79): EYESPY's green eyeball, authored looking up the screen (models.cfg: yaw=aim).
- eye_hatch (5 164): BRAINIAC's floor hatch with a red eye glowing between two lids (the purple octagon and
  the dark corners the sprite draws round it are the map's floor, not modelled).
- stone_fist, stone_fist_r (5 81, 5 83): BRAINIAC's faceted grey stones at the screen's edges (mirror images).
- red_link (5 168): a link of BRAINIAC's chain of red brains in steel clamps (as brain_clamp, 5 166).
- hanging_pod (5 170): BRAINIAC's grey pod with a red eye hanging from a steel bracket.
- arrow_left, arrow_right (5 247, 5 266): DREAD-NOT's and EYESPY's glowing green arrows (mirror images).
- ear_right, ear_left (5 245, 5 284): EYESPY's flying ears, facing the camera: a rolled rim, the
  hollow, the Y-shaped ridge, the tragus and the lobe, each from its own sprite.

The objects drawn from several sprites are in wave3_l_parts.py; the pixel art in wave3_l_art.py.

usage: blender -b --factory-startup -P wave3_l.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1]
       blender -b --factory-startup -P wave3_l.py -- --whole <prefix> [--only object] [--check 1]
--preview renders <prefix><name>_top.png and _3q.png for each model; --check prints each model's
silhouette overlap with its sprite; --whole renders the objects the game draws in pieces, whole.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_l_art as art  # noqa: E402
import wave3_l_kit as w  # noqa: E402
import wave3_l_parts as parts  # noqa: E402
from wave3_l_kit import k, sh, pal, model  # noqa: E402


# --- 5 49: the tan fighter ----------------------------------------------------------------------

@model("tan_fighter", 49)
def tan_fighter():
    """A tan fighter, nose down the screen: a round fuselage (columns 9-15) narrowing to the nose (row
    26) with a brass canopy (rows 13-16), broad straight wings (rows 6-11) over two grey rails that
    show in front of and behind them, a V tail at the top (rows 0-3) and canards by the nose (rows
    17-20)."""
    a = w.Art(art.TAN_FIGHTER, (12, 14))
    ax = 0.5
    tan = pal("tanf_hull", 0x17, metallic=0.45, roughness=0.4)
    light = pal("tanf_light", 0x1a, metallic=0.45, roughness=0.32)
    grey = pal("tanf_grey", 0x08, metallic=0.6, roughness=0.3)
    glass = pal("tanf_canopy", 0x1b, metallic=0.4, roughness=0.08)
    zc = 1.0
    widths = [(-12.9, 0.12), (-12.0, 0.9), (-11.0, 1.4), (-9.5, 2.0), (-7.5, 2.5), (-5.5, 2.9), (-2.5, 3.3),
              (1.5, 3.5), (6.5, 3.5), (9.5, 3.0), (11.5, 2.1), (13.3, 1.2)]
    secs = [(y, ax, zc - 0.5 * w.smoothstep(-6.0, -12.9, y), hw, hw * 0.92, hw * 0.6) for y, hw in widths]
    w.loft_y("fuselage", secs, tan, segments=24, power=2.2, start=(ax, -13.1, zc - 0.5), end=(ax, 13.5, zc))
    # A light spine along the top, from the canopy back to the tail.
    w.tube("spine", w.catmull([(ax, 1.0, zc + 3.15), (ax, 6.5, zc + 3.2), (ax, 11.5, zc + 1.9),
                               (ax, 13.4, zc + 0.9)], 0.6), 0.55, light, 8)
    w.sphere("canopy", (ax, -0.9, zc + 2.7), (1.9, 2.4, 1.7), glass, 24, 12)
    # The wings (one plate across), a little thicker at the root, the tips tilted up.
    wing = w.poly_px(a, [(1.2, 6.6), (23.0, 6.6), (23.0, 9.6), (21.4, 10.6), (17.6, 11.6), (16.0, 12.6), (9.0, 12.6),
                         (7.4, 11.6), (3.6, 10.6), (1.2, 9.6)])
    w.bevelled_slab("wing", wing, -0.5, 0.7, tan, bevel=0.4,
                    z_fn=lambda x, y, z: z * (1.0 + 0.5 * w.smoothstep(7.0, 2.0, abs(x - ax))) + zc + 0.4 +
                    0.7 * w.smoothstep(4.0, 11.0, abs(x - ax)))
    # A light edge along the wings' rear (the sprite's bright row 7).
    for side in (-1, 1):
        x0, x1 = ax + side * 3.6, ax + side * 10.6
        w.tube(f"wing_edge{side}", [(x0, 7.0, zc + 1.4), (x1, 7.0, zc + 1.95)], 0.42, light, 8)
    # The grey rails under the wings (rows 4-12), showing in front of and behind them.
    for side, x in ((-1, a.x(3)), (1, a.x(21))):
        w.lathe_axis(f"rail{side}", [(0.0, 0.05), (1.2, 0.55), (2.2, 0.8), (7.4, 0.8), (8.4, 0.6), (8.7, 0.05)], grey,
                     (x, 1.2, zc - 0.1), (0, 1, 0), 12)
    # The V tail (rows 0-3): two fins leaning out from the fuselage's end, and a short spine between them.
    fin = w.poly_px(a, [(5.0, 0.3), (9.0, 0.3), (11.0, 2.2), (11.6, 4.4), (9.6, 4.6), (7.0, 3.0), (5.0, 1.8)])
    for i, poly in enumerate((fin, w.mirrored(fin, ax))):
        w.bevelled_slab(f"tail_fin{i}", poly, -0.45, 0.45, tan, bevel=0.3,
                        z_fn=lambda x, y, z: z + zc + 2.0 + 0.95 * (abs(x - ax) - 1.0))
    w.fin_blade("tail_spine", [(13.8, ax, zc + 0.5, zc + 1.6), (12.0, ax, zc + 1.5, zc + 3.4),
                               (9.0, ax, zc + 2.5, zc + 3.9)], light, thickness=1.2)
    # The canards (rows 17-20).
    canard = w.poly_px(a, [(5.2, 17.4), (19.8, 17.4), (19.6, 18.8), (17.0, 20.0), (16.4, 21.0), (8.6, 21.0),
                           (8.0, 20.0), (5.4, 18.8)])
    w.bevelled_slab("canards", canard, -0.4, 0.4, tan, bevel=0.3,
                    z_fn=lambda x, y, z: z + zc + 0.3 + 0.35 * w.smoothstep(2.5, 7.0, abs(x - ax)))


# --- 5 133: DREAD-NOT's post ---------------------------------------------------------------------

@model("visor_post", 133, large=False)
def visor_post():
    """A small grey post lying along the screen's y, as drawn (it travels up the screen): a round head
    (rows 1-8) with a glowing red visor round it (row 5), a narrow neck and a flared base (rows 10-13)."""
    grey = pal("post_grey", 0x05, metallic=0.6, roughness=0.28)
    dark = pal("post_dark", 0x02, metallic=0.4, roughness=0.5)
    red = pal("post_visor", 0x75, metallic=0.1, roughness=0.2, glow=1.4)
    zc, squash = 2.4, 0.85
    # (y, radius) from the base (row 13) to the head's top (row 1).
    prof = [(-6.9, 0.02), (-6.85, 2.6), (-6.5, 3.0), (-5.0, 3.0), (-4.0, 2.4), (-3.2, 1.3), (-2.4, 1.0), (-1.7, 1.3),
            (-1.0, 2.1), (0.0, 2.8), (2.5, 3.0), (4.0, 2.7), (5.2, 1.9), (5.9, 1.0), (6.1, 0.02)]
    w.lathe_axis("body", [(y + 6.9, r) for y, r in prof], grey, (0.0, -6.9, zc), (0, 1, 0), 24, squash=squash)
    w.lathe_axis("visor", [(0.0, 2.9), (0.15, 3.25), (1.15, 3.25), (1.3, 2.9)], red, (0.0, 0.85, zc), (0, 1, 0), 24,
                 squash=squash)
    w.lathe_axis("base_ring", [(0.0, 2.85), (0.1, 3.15), (0.6, 3.15), (0.7, 2.85)], dark, (0.0, -4.9, zc), (0, 1, 0),
                 24, squash=squash)


# --- 5 245, 5 284: EYESPY's ears ------------------------------------------------------------------

# Features of each ear in its pixels (column, row): the helix's side ("helix_off": where the rim fades,
# a point and radius), the concha's hollow, the antihelix's ridges (a stem and two crura), the
# triangular fossa between the crura, the tragus and the lobe.
EARS = {
    "ear_right": dict(art=art.EAR_RIGHT, sprite=245,
                      helix_off=((4.5, 19.0), 6.5), concha=((8.0, 12.4), (3.5, 5.4), -15.0),
                      antihelix=[(10.8, 19.0), (11.4, 15.0), (11.6, 11.0), (10.6, 8.0), (8.4, 5.6)],
                      crus=[(11.6, 11.0), (13.0, 8.0), (14.4, 5.4)], fossa=((11.6, 6.8), (1.6, 1.8)),
                      tragus=((5.6, 16.4), (1.6, 1.9)), lobe=((9.0, 22.4), (3.4, 2.6))),
    "ear_left": dict(art=art.EAR_LEFT, sprite=284,
                     helix_off=((19.5, 20.0), 6.5), concha=((14.8, 12.8), (3.5, 5.4), 15.0),
                     antihelix=[(13.0, 19.4), (12.2, 15.0), (11.8, 11.0), (12.6, 8.0), (14.8, 5.6)],
                     crus=[(11.8, 11.0), (10.4, 8.0), (9.0, 5.2)], fossa=((11.6, 6.6), (1.6, 1.8)),
                     tragus=((18.4, 16.0), (1.6, 1.9)), lobe=((15.4, 22.6), (3.4, 2.6))),
}


def ear(name):
    """An ear facing the camera: an auricle over the sprite's outline with a rolled rim (the helix)
    round its top and outer side, a deep hollow (the concha), the Y-shaped ridge of the antihelix
    with the small hollow between its arms, the tragus by the hollow and a soft lobe."""
    f = EARS[name]
    a = w.Art(f["art"], (12, 14))
    skin = pal("ear_skin", 0x19, metallic=0.2, roughness=0.4)
    deep = pal("ear_deep", 0x15, metallic=0.15, roughness=0.5)
    polys = a.polys(smooth=2, epsilon=0.45)
    edge = w.distance_to(polys)

    def P(c, r):
        return a.x(c - 0.5), a.y(r - 0.5)  # pixel corners as model points
    (hc, hr), ((cc, cr), (crx, cry), cang) = f["helix_off"], f["concha"]
    hcx, hcy = P(*hc)
    ccx, ccy = P(cc, cr)
    anti = [P(c, r) for c, r in f["antihelix"]]
    crus = [P(c, r) for c, r in f["crus"]]
    fossa = P(*f["fossa"][0])
    tragus = P(*f["tragus"][0])
    lobe = P(*f["lobe"][0])

    def concha(x, y):
        return w.gauss(x, y, ccx, ccy, crx, cry, cang)

    shade = w.shade_field(a, blur=2, skip="01k")

    def height(x, y):
        d = edge(x, y)
        h = 1.6 + 2.2 * w.round_edge(d, 4.5)
        # The sprite's shading as relief (bright ridges, dark hollows), and the shapes it suggests: the
        # helix rolled round the top and outer side, the hollow, the Y-shaped ridge, the tragus, the lobe.
        h += 0.55 * (shade(x, y) - 8.0) * w.smoothstep(1.6, 3.2, d)
        side = w.smoothstep(hr * 0.6, hr * 1.2, math.hypot(x - hcx, y - hcy))
        h += side * (1.3 * math.exp(-((d - 1.5) / 1.2) ** 2) - 0.7 * math.exp(-((d - 3.4) / 0.9) ** 2))
        h -= 1.8 * concha(x, y)
        ridge = min(w.seg_distance(x, y, anti), w.seg_distance(x, y, crus))
        h += 1.0 * math.exp(-(ridge / 1.3) ** 2)
        h -= 0.8 * w.gauss(x, y, fossa[0], fossa[1], *f["fossa"][1])
        h += 1.0 * w.gauss(x, y, tragus[0], tragus[1], *f["tragus"][1])
        h += 0.6 * w.gauss(x, y, lobe[0], lobe[1], *f["lobe"][1])
        return max(h, 0.7)

    body = w.plate("ear", polys, skin, 1.0, radius=2.0, bottom=0.0, spacing=0.45,
                   z_fn=lambda x, y, z: 0.05 + max(0.0, min(1.0, z - 0.05)) * height(x, y), angle=60)
    w.simplify_flat(body)
    w.band_split(body, [concha(v.co.x, v.co.y) - 0.07 * (shade(v.co.x, v.co.y) - 6.0) if v.co.z > 0.2 else -1.0
                        for v in body.data.vertices], [(-9.0, skin), (0.45, deep)], smooth_angle=60)
    w.lift(body, -2.0)


for _ear in EARS:
    model(_ear, EARS[_ear]["sprite"])(lambda name=_ear: ear(name))


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


# --- 5 207: BRAINIAC's stinger ---------------------------------------------------------------------

@model("flesh_stinger", 207)
def flesh_stinger():
    """BRAINIAC's fleshy stinger lying as drawn, its point down the screen: a broad cap at the back (rows
    0-4) behind a grooved collar and a ring (rows 5-9), then a beak of two halves meeting along a seam
    (rows 10-26), narrowing to the point."""
    flesh = pal("stinger_flesh", 0x47, metallic=0.15, roughness=0.35)
    light = pal("stinger_light", 0x4a, metallic=0.15, roughness=0.3)
    dark = pal("stinger_dark", 0x42, metallic=0.1, roughness=0.5)
    ax, zc, squash = 0.5, 3.4, 0.82
    prof = [(-12.9, 0.02), (-12.5, 0.55), (-11.0, 1.25), (-9.0, 2.3), (-7.0, 3.3), (-5.0, 4.25), (-3.0, 4.8),
            (-1.5, 5.4), (2.0, 5.55), (3.4, 6.3), (6.5, 6.55), (7.4, 5.6), (7.9, 5.3), (8.5, 5.7), (9.3, 6.6),
            (10.0, 6.8), (10.4, 6.5), (10.8, 7.0), (11.6, 7.65), (12.8, 7.4), (13.5, 6.4), (13.95, 4.2), (14.0, 0.02)]
    body = w.lathe_axis("body", [(y + 12.9, r) for y, r in prof], flesh, (ax, -12.9, zc), (0, 1, 0), 32,
                        squash=squash, smooth_angle=50)
    w.paint(body, lambda c, n: 2 if 7.2 < c.y < 8.2 or 10.1 < c.y < 10.7 else 1 if c.y > 10.7 and n.z > 0.2 else 0,
            [flesh, light, dark])
    # The seam between the beak's halves, along its top, and two side seams.
    for i, (u, y0) in enumerate(((0.0, 4.0), (-0.62, 1.5), (0.62, 1.5))):
        pts = []
        for j in range(14):
            y = y0 - (y0 + 11.8) * j / 13
            rad = next(r1 + (r2 - r1) * (y - y1) / (y2 - y1) for (y1, r1), (y2, r2) in zip(prof, prof[1:])
                       if y1 <= y <= y2)
            ang = math.pi / 2 + u
            pts.append((ax + rad * math.cos(ang) * 0.98, y, zc + rad * math.sin(ang) * squash * 0.98))
        w.tube(f"seam{i}", pts, 0.3 if i else 0.38, dark, 8)


# --- 5 79: EYESPY's green eyeball ------------------------------------------------------------------

@model("green_eye", 79)
def green_eye():
    """A green eyeball (21 pixels across), its dark iris and pupil looking up the screen and a little up
    at the camera, the cornea bulging over them: with yaw=aim it looks at the player, as the sprite's
    eye looks down at him (as EYESPY's grey eye, 5 202)."""
    pupil = pal("geye_pupil", 0x21, metallic=0.0, roughness=0.06)
    iris = pal("geye_iris", 0x24, metallic=0.1, roughness=0.12)
    iris_rim = pal("geye_iris_rim", 0x27, metallic=0.1, roughness=0.18)
    ring = pal("geye_ring", 0x22, metallic=0.0, roughness=0.25)
    ball = pal("geye_ball", 0x29, metallic=0.1, roughness=0.12)
    back = pal("geye_back", 0x26, metallic=0.05, roughness=0.3)
    centre, radius, flat = Vector((0.5, 1.5, 0.0)), 10.4, 0.8
    look = Vector((0.0, math.sin(math.radians(24)), math.cos(math.radians(24))))
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=32, radius=1.0)
    values = []
    for v in bm.verts:
        n = v.co.normalized()
        angle = math.degrees(n.angle(look))
        bulge = 0.05 * (1 - w.smoothstep(0, 32, angle)) - 0.03 * (1 - w.smoothstep(5, 10, angle))
        p = n * radius * (1 + bulge)
        v.co = centre + Vector((p.x, p.y, p.z * flat))
        values.append(-angle)
    mesh = bpy.data.meshes.new("eye")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("eye", mesh)
    bpy.context.scene.collection.objects.link(obj)
    w.band_split(obj, values, [(-999, back), (-105, ball), (-33, ring), (-30, iris_rim), (-25, iris), (-11, pupil)],
                 smooth_angle=80)


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


# --- 5 168: BRAINIAC's red link, 5 170: the hanging pod ----------------------------------------------

@model("red_link", 168)
def red_link():
    """A link of BRAINIAC's chain of red brains (the level stacks them down the screen, as the brain
    held by clamps, 5 166, lies across it): a folded red mass glowing along a seam, held by a steel
    strap down its left and a clamp at its right, with steel plates at its top and bottom where the
    links meet."""
    flesh = [pal(f"link_{i:x}", 0x70 + i, metallic=0.1, roughness=0.35, glow=g) for i, g in ((3, 0.15), (5, 0.25),
                                                                                              (7, 0.4), (9, 0.6))]
    seam = pal("link_seam", 0x79, metallic=0.0, roughness=0.3, glow=1.4)
    metal = pal("link_metal", 0x68, metallic=0.65, roughness=0.3)
    light = pal("link_metal_light", 0x6a, metallic=0.65, roughness=0.25)
    a = w.Art(art.RED_LINK, (12, 14))
    shade = w.shade_field(a, blur=1, letters={"s": 4.0}, skip="")
    mass = w.poly_px(a, [(5.0, 4.6), (19.4, 4.6), (19.6, 22.6), (17.6, 23.6), (7.0, 23.6), (5.0, 22.0)])

    def folds(x, y):
        return math.sin(0.95 * x + 1.5 * math.sin(0.5 * y + 0.35 * x)) * math.sin(0.85 * y + 0.9 * math.sin(0.5 * x))
    body = w.plate("mass", [mass], flesh[1], 5.4, radius=2.6, base=0.0, spacing=0.7,
                   z_fn=lambda x, y, z: z + 0.45 * folds(x, y) * w.smoothstep(1.0, 3.0, z))
    w.simplify_flat(body)
    w.band_split(body, [folds(v.co.x, v.co.y) + 0.12 * (shade(v.co.x, v.co.y) - 5.0) if v.co.z > 1.2 else -2.0
                        for v in body.data.vertices],
                 [(-9.0, flesh[0]), (-0.3, flesh[1]), (0.5, flesh[2]), (1.1, flesh[3])], smooth_angle=60)
    top = lambda x, y: sh.surface_z(body, x, y, 5.0)  # noqa: E731
    path = w.catmull([(x, y, top(x, y) - 0.2) for x, y in ((-1.0, 3.6), (-0.4, 1.0), (1.0, -1.6), (0.6, -4.6))], 0.5)
    w.tube("seam", path, 0.55, seam, 8)
    # The steel: plates at both ends (rows 0-3, 24-27), the strap down the left and the clamp at the right.
    for y in (12.0, -12.0):
        w.rounded_box(f"plate{y}", (0.5, y, 2.6), (9.6, 4.4, 4.2), metal, bevel=0.6)
        w.rounded_box(f"plate_light{y}", (0.0, y, 4.6), (1.4, 4.0, 0.5), light, bevel=0.2)
    strap = [(-1.0, 10.2), (-1.4, 7.0), (-4.6, 6.4), (-5.2, 3.0), (-4.8, -2.0), (-1.4, -6.0), (-1.2, -10.2)]
    w.tube("strap", w.catmull([(x, y, top(x, y) + 0.1) for x, y in strap], 0.9), 0.85, metal, 8)
    w.rounded_box("clamp", (5.8, -0.4, 3.2), (3.4, 8.4, 5.2), metal, bevel=0.7)
    w.rounded_box("clamp_light", (5.4, -0.4, 5.8), (1.0, 7.4, 0.5), light, bevel=0.2)


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
