"""Wave 3, batch L of the enemy models: the remaining enemies of sheet 5 (episode 4), authored as their sprites
look (models.cfg: yaw=0 unless noted):

- tan_fighter (5 49): APPROACH's tan fighter, nose down: a V tail, broad wings over grey rails, a
  brass canopy and canards by the nose.
- ember (5 76): BRAINIAC's small spiked ember on the ground, glowing where the sprite is bright.
- visor_post (5 133): DREAD-NOT's small grey post with a glowing red visor, lying as drawn.
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

from mathutils import Matrix, Vector

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


# --- 5 76: the ember ----------------------------------------------------------------------------

def spike(name, base, tip, radius, mat, segments=10):
    """A rounded cone from base to tip."""
    base, tip = Vector(base), Vector(tip)
    length = (tip - base).length
    return w.lathe_axis(name, [(0.0, radius), (0.35 * length, radius * 0.72), (0.75 * length, radius * 0.3),
                               (length, 0.02)], mat, base, tip - base, segments, smooth_angle=60)


def lava_bands(prefix, levels):
    """Materials for molten parts in the fire ramp: [(lowest shade, palette index, glow)]."""
    return [(lowest, pal(f"{prefix}_{index:x}", index, metallic=0.0, roughness=0.55, glow=glow))
            for lowest, index, glow in levels]


@model("ember", 76, large=False)
def ember():
    """A small spiked ember on the ground (as BRAINIAC's lava star, 5 278): a lumpy crust over the
    sprite's outline, a blob with four short spikes, bulging and glowing where the sprite is bright."""
    a = w.Art(art.EMBER, (6, 7))
    shade = w.shade_field(a, blur=0, letters={"k": 0})
    bands = lava_bands("ember", ((0.0, 0x72, 0.3), (2.5, 0x74, 0.5), (4.0, 0x76, 0.7), (5.5, 0x77, 0.85),
                                 (7.0, 0x79, 1.0), (9.0, 0x7b, 1.25), (11.0, 0x7d, 1.5)))
    polys = a.polys(smooth=1, epsilon=0.35)

    def bulge(x, y, z):
        lumps = 0.25 * math.sin(2.3 * x + 1.1) * math.sin(2.1 * y + 0.4)
        return z + (0.9 * max(0.0, shade(x, y) - 4.0) / 10.0 + lumps) * min(1.0, z / 1.2)
    blob = w.rounded("blob", polys, bands[0][1], aspect=0.85, max_height=4.2, spacing=0.3, z_fn=bulge, angle=40)
    w.simplify_flat(blob)
    w.paint_bands(blob, lambda c, n: shade(c.x, c.y) + 0.8 * max(0.0, n.z) - 0.4, bands)


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
    shadow = pal("ear_shadow", 0x17, metallic=0.15, roughness=0.45)
    light = pal("ear_light", 0x1b, metallic=0.2, roughness=0.35)
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

    shade = w.shade_field(a, blur=2, letters={"k": 2})

    def height(x, y):
        d = edge(x, y)
        h = 1.6 + 2.2 * w.round_edge(d, 4.5)
        # The sprite's shading as relief (bright ridges, dark hollows), and the shapes it suggests: the
        # helix rolled round the top and outer side, the hollow, the Y-shaped ridge, the tragus, the lobe.
        h += 0.42 * (shade(x, y) - 8.0) * w.smoothstep(0.3, 1.6, d)
        side = w.smoothstep(hr * 0.6, hr * 1.2, math.hypot(x - hcx, y - hcy))
        h += side * (1.3 * math.exp(-((d - 1.5) / 1.2) ** 2) - 0.7 * math.exp(-((d - 3.4) / 0.9) ** 2))
        h -= 1.8 * concha(x, y)
        ridge = min(w.seg_distance(x, y, anti), w.seg_distance(x, y, crus))
        h += 1.0 * math.exp(-(ridge / 1.3) ** 2)
        h -= 0.8 * w.gauss(x, y, fossa[0], fossa[1], *f["fossa"][1])
        h += 1.0 * w.gauss(x, y, tragus[0], tragus[1], *f["tragus"][1])
        h += 0.6 * w.gauss(x, y, lobe[0], lobe[1], *f["lobe"][1])
        return max(h, 0.7)

    body = w.plate("ear", polys, skin, 1.0, radius=1.3, bottom=0.0, spacing=0.45,
                   z_fn=lambda x, y, z: 0.05 + max(0.0, min(1.0, z - 0.05)) * height(x, y), angle=60)
    w.simplify_flat(body)
    tone = w.shade_field(a, blur=1, letters={"k": 2})
    w.band_split(body, [tone(v.co.x, v.co.y) - 3.0 * concha(v.co.x, v.co.y) if v.co.z > 0.2 else 8.0
                        for v in body.data.vertices], [(-99.0, deep), (4.6, shadow), (6.6, skin), (10.6, light)],
                 smooth_angle=60)
    w.lift(body, -2.0)


for _ear in EARS:
    model(_ear, EARS[_ear]["sprite"])(lambda name=_ear: ear(name))


# --- The objects drawn in pieces (wave3_l_parts.py) ---------------------------------------------

for _name, _sprite, _builder in parts.PIECES:
    model(_name, _sprite)(_builder)

w.main()
