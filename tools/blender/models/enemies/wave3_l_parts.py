"""The batch L objects that the game draws from several sprites of sheet 5 (wave3_l.py registers them): each
is built whole, in shared coordinates, from its pixel art (wave3_l_art.py) and cut along its sprites'
edges into the pieces, each moved to its sprite's centre (models.cfg: origin, so that they meet again).
The levels place the pieces as the sheet arranges them (checked in the level files' enemy events).
(The grey and red jet, redjet_left / redjet_right / redjet_nose, is built by polish_redjet.py; the long grey ship,
longship_left / longship_mid / longship_right, by polish_longship.py.)

- ringship_pod, ringship_ring (39, 41) and their mirror images ringship_ring_r, ringship_pod_r (43, 45):
  HARVEST's machine on a ring frame, a blue pod and a grey housing round a blue sphere.
- drip_top, drip_bottom (53 above 91): NOSE DRIP's twisted drip of fire.
- fire_bowl_left, fire_bowl_right (156, 158): NOSE DRIP's bowl of flames.
- brain_* (196, 198, 200 / 233, 235, 237, 239 / 272, 274, 276): BRAINIAC's brain, 96 x 84 pixels.
"""
import math

import wave3_l_art as art
import wave3_l_kit as w
from wave3_l_kit import k, sh, pal


# --- HARVEST's ring ship (39 and 41; 43 and 45 its mirror image) ----------------------------------

RING = w.Art(art.RINGSHIP, (24, 14))
RING_PIECES = {"ringship_pod": (-24, 0, -14, 14), "ringship_ring": (0, 24, -14, 14)}


def ring_materials():
    return {
        "blue": pal("ringship_blue", 0x37, metallic=0.4, roughness=0.3),
        "blue_light": pal("ringship_blue_light", 0x3a, metallic=0.4, roughness=0.25),
        "blue_dark": pal("ringship_blue_dark", 0x33, metallic=0.4, roughness=0.4),
        "grey": pal("ringship_grey", 0x06, metallic=0.55, roughness=0.35),
        "light": pal("ringship_light", 0x0a, metallic=0.6, roughness=0.25),
        "dark": pal("ringship_dark", 0x02, metallic=0.4, roughness=0.5),
        "window": pal("ringship_window", 0x3b, metallic=0.2, roughness=0.15, glow=0.7),
        "sphere": pal("ringship_sphere", 0x36, metallic=0.3, roughness=0.12),
    }


def build_ringship():
    """HARVEST's machine standing on the ground, lying along the screen's x (the left one; the right
    one is its mirror image): a blue bullet pod pointing left with a grey rail along its top, a grey
    collar and two small blue fins behind it, a grey shaft with a glowing light blue window leading to
    a grey housing round a ring, in which a blue sphere sits (the ring open beside it), a blue block
    at the right end and blue claws at the housing's corners."""
    m = ring_materials()
    a = RING
    yc = 0.5  # the machine's middle (row 13)
    zc = 4.3  # the pod's axis

    def pod_r(x):
        pts = [(-22.3, 0.0), (-22.0, 1.8), (-21.5, 2.7), (-20.5, 3.7), (-19.5, 4.6), (-18.5, 5.4), (-17.0, 6.2),
               (-15.0, 6.9), (-13.0, 7.25), (-11.4, 7.3)]
        for (x0, r0), (x1, r1) in zip(pts, pts[1:]):
            if x0 <= x <= x1:
                return r0 + (r1 - r0) * (x - x0) / (x1 - x0)
        return 7.3
    squash = 0.62
    prof = [(t, pod_r(-22.3 + t)) for t in (0.0, 0.3, 0.8, 1.8, 2.8, 3.8, 5.3, 7.3, 9.3, 10.9)]
    prof[0] = (0.0, 0.02)
    prof.append((11.1, 6.6))
    prof.append((11.2, 0.02))
    w.lathe_axis("pod", prof, m["blue"], (-22.3, yc, zc), (1, 0, 0), 32, squash=squash)
    # Panel lines round the pod (dark rings) and the grey rail along its top.
    for i, x in enumerate((-18.6, -15.0)):
        r = pod_r(x) + 0.05
        w.lathe_axis(f"pod_seam{i}", [(0.0, r - 0.3), (0.12, r + 0.12), (0.5, r + 0.12), (0.62, r - 0.3)],
                     m["blue_dark"], (x - 0.3, yc, zc), (1, 0, 0), 32, squash=squash)
    rail = [(x, yc, zc + pod_r(x) * squash - 0.05) for x in (-21.4, -20.6, -19.5, -17.5, -15.0, -12.5, -11.2)]
    w.tube("pod_rail", w.catmull(rail, 0.5), 0.75, m["light"], 10)
    # The collar behind the pod.
    w.lathe_axis("collar", [(0.0, 6.6), (0.2, 7.55), (1.5, 7.55), (1.7, 6.6)], m["light"], (-12.2, yc, zc), (1, 0, 0),
                 32, squash=squash)
    # Small blue fins behind the collar, up and down the screen.
    fin = w.poly_px(a, [(13.4, 7.6), (16.6, 7.4), (19.4, 8.5), (20.2, 10.0), (13.4, 10.3)])
    for i, poly in enumerate((fin, [(x, 2 * yc - y) for x, y in reversed(fin)])):
        w.bevelled_slab(f"fin{i}", poly, zc - 0.45, zc + 0.45, m["blue"], bevel=0.3)
    # The shaft and its light blue window with a grey rib over it.
    w.lathe_axis("shaft", [(0.0, 3.4), (11.0, 3.4)], m["grey"], (-11.0, yc, zc - 1.0), (1, 0, 0), 20, squash=0.75)
    w.rounded_box("window", (-4.7, yc, zc + 1.45), (7.4, 3.2, 1.0), m["window"], bevel=0.35)
    w.tube("window_rib", [(-8.6, yc, zc + 2.0), (-0.8, yc, zc + 2.0)], 0.45, m["light"], 8)

    # The housing: everything right of column 22, open where the sprite is (beside the sphere).
    rows = a.select(lambda c, r, ch: c >= 22)
    polys = a.polys(rows=rows, smooth=2, epsilon=0.4, min_area=0.5)
    ring_c, ring_r = (5.6, yc), (5.7, 6.6)

    def housing_z(x, y, z):
        # Sloping down into the ring's opening.
        q = math.hypot((x - ring_c[0]) / ring_r[0], (y - ring_c[1]) / ring_r[1])
        return z - 1.2 * w.smoothstep(1.15, 0.9, q) * min(1.0, z / 2.0)
    housing = w.plate("housing", polys, m["grey"], 3.6, radius=1.4, spacing=0.5, z_fn=housing_z)
    w.planar(w.simplify_flat(housing), 2.0)
    # The bright ring round the opening.
    ring = []
    for i in range(40):
        t = 2 * math.pi * i / 40
        x, y = ring_c[0] + ring_r[0] * math.cos(t), ring_c[1] + ring_r[1] * math.sin(t)
        ring.append((x, y, sh.surface_z(housing, x, y, 3.0) + 0.1))
    ring_obj = k.loft("ring", w.frame_rings(ring + ring[:1], 0.8, 10, squash=0.9), m["light"], cap_start=False,
                      cap_end=False)
    k.smooth(ring_obj, 60)
    # The sphere in the ring, at its left.
    w.sphere("sphere", (3.0, 0.7, 3.6), (4.3, 4.3, 3.7), m["sphere"], 28, 14)
    # The blue block at the right end (columns 37-43), raised over the housing.
    block = w.poly_px(a, [(37.0, 6.4), (41.0, 6.6), (43.6, 8.6), (44.0, 12.0), (44.0, 15.0), (43.6, 18.4),
                          (41.0, 20.4), (37.0, 20.6)])
    w.planar(w.simplify_flat(w.plate("block", [block], m["blue"], 5.2, radius=1.6, spacing=0.45)), 2.0)
    w.rounded_box("block_light", (a.x(38.5), yc, 5.1), (1.6, 9.0, 0.6), m["blue_light"], bevel=0.25)
    # The claws at the housing's corners: blue prongs leaning out.
    claws = [
        [(20.4, 3.6), (26.6, 3.4), (26.6, 5.6), (21.0, 5.8)],
        [(33.6, 3.4), (37.0, 3.6), (40.4, 5.6), (43.0, 7.2), (42.6, 8.4), (38.4, 7.0), (35.0, 5.6)],
    ]
    for i, claw in enumerate(claws):
        poly = w.poly_px(a, claw)
        for j, pl in enumerate((poly, [(x, 2 * yc - y) for x, y in reversed(poly)])):
            w.bevelled_slab(f"claw{i}{j}", pl, 0.0, 3.0, m["blue"], bevel=0.45,
                            z_fn=lambda x, y, z: z + 1.0 * w.smoothstep(0.0, 3.0, z) * w.smoothstep(4.0, 12.0,
                                                                                                abs(y - yc)))
    w.bake()
    sh.flat_bottom(w.meshes())
    for obj in w.meshes():
        k.recalc_normals(obj)


def ring_piece(name, mirror):
    def build():
        build_ringship()
        if mirror:
            w.mirror_objects(w.meshes())
        x0, x1, y0, y1 = RING_PIECES[name]
        if mirror:
            x0, x1 = -x1, -x0
        return w.cut_piece(x0, x1, y0, y1)
    return build


# --- NOSE DRIP's twisted drip (53 above 91) ----------------------------------------------------------

DRIP = w.Art(art.DRIP, (12, 28))
DRIP_PIECES = {"drip_top": (-12, 12, 0, 28), "drip_bottom": (-12, 12, -28, 0)}


def drip_bands():
    return [(lowest, pal(f"drip_{index:x}", index, metallic=0.0, roughness=0.5, glow=glow))
            for lowest, index, glow in ((-9.0, 0x72, 0.35), (3.0, 0x74, 0.5), (5.0, 0x76, 0.7), (7.0, 0x78, 0.9),
                                        (9.0, 0x7a, 1.1), (11.0, 0x7c, 1.35))]


def build_drip():
    """NOSE DRIP's drip of fire, two sprites tall: two glowing strands twisting round each other down
    the screen, thin at the top (row 0), crossing twice with gaps between them (rows 10 and 16-19),
    and thickening into a lumpy braid at the bottom (rows 28-53) over a molten core; glowing where
    the sprite is bright."""
    a = DRIP
    bands = drip_bands()
    shade = w.shade_field(a, blur=1)
    # The art's extent along each row: (centre x, half width).
    extent = {}
    for r in range(a.h):
        cols = [c for c in range(a.w) if a.rows[r][c] != "."]
        if cols:
            extent[r] = ((cols[0] + cols[-1] + 1) / 2.0 - a.ox, (cols[-1] + 1 - cols[0]) / 2.0)

    def ext(y):
        r = min(max(a.oy - y - 0.5, 0.0), 53.0)
        r0 = int(math.floor(r))
        r1 = min(r0 + 1, 53)
        f = r - r0
        (c0, h0), (c1, h1) = extent[r0], extent[r1]
        return c0 + (c1 - c0) * f, h0 + (h1 - h0) * f

    zc = 4.6
    for k_ in range(2):
        pts, radii = [], []
        for i in range(96):
            r = 0.4 + 53.0 * i / 95
            y = a.oy - r
            cx, hw = ext(y)
            rs = 0.7 + 1.6 * w.smoothstep(0.0, 14.0, r) + 0.9 * w.smoothstep(20.0, 40.0, r)  # the strand's radius
            reach = max(0.0, hw - rs * 0.9)                          # how far it swings out
            phase = 2 * math.pi * (r / 14.5) + math.pi * k_ + 0.6
            pts.append((cx + reach * math.cos(phase), y, zc + reach * 0.85 * math.sin(phase)))
            radii.append(rs * (0.35 + 0.65 * w.smoothstep(0.0, 3.0, r)))
        strand = w.tube(f"strand{k_}", pts, 1.0, bands[0][1], 11, radii=radii)
        strand.data.update()
        normals = [v.normal for v in strand.data.vertices]
        w.band_split(strand, [shade(v.co.x, v.co.y) + 1.5 * n.z - 0.5 for v, n in zip(strand.data.vertices, normals)],
                     bands, smooth_angle=60)
    # The molten core of the lower braid (rows 26-53), lumpy.
    rows = a.select(lambda c, r, ch: r >= 26)
    polys = a.polys(rows=rows, smooth=2, epsilon=0.4)
    for p in polys:
        for i, (x, y) in enumerate(p):
            p[i] = (x * 0.86, y)
    core = w.rounded("core", polys, bands[0][1], aspect=0.9, max_height=6.4, bottom=0.0, base=zc - 3.0, spacing=0.8,
                     z_fn=lambda x, y, z: z + 0.25 * (shade(x, y) - 6.0) * w.smoothstep(zc, zc + 2.0, z))
    w.simplify_flat(core)
    core.data.update()
    w.band_split(core, [shade(v.co.x, v.co.y) + 1.0 * v.normal.z - 1.0 for v in core.data.vertices], bands,
                 smooth_angle=55)
    w.bake()
    sh.flat_bottom(w.meshes())


def drip_piece(name):
    def build():
        build_drip()
        return w.cut_piece(*DRIP_PIECES[name])
    return build


# --- NOSE DRIP's bowl of flames (156 and 158) -----------------------------------------------------

BOWL = w.Art(art.FIRE_BOWL, (24, 14))
BOWL_PIECES = {"fire_bowl_left": (-24, 0, -14, 14), "fire_bowl_right": (0, 24, -14, 14)}


def build_fire_bowl():
    """A bowl of fire, 48 pixels wide: a molten trough bulging where the sprite is bright, glowing
    white-yellow low in the bowl and dark red at the rim, with tongues of flame rising from the rim
    and leaning up the screen (the sprite's spikes)."""
    a = BOWL
    bands = drip_bands()
    shade = w.shade_field(a, blur=1, skip="k")
    polys = a.polys(smooth=2, epsilon=0.45)
    body = w.rounded("bowl", polys, bands[0][1], aspect=0.8, max_height=5.5, spacing=0.7,
                     z_fn=lambda x, y, z: z + 0.35 * (shade(x, y) - 6.0) * w.smoothstep(0.5, 2.0, z))
    w.simplify_flat(body)
    w.band_split(body, [shade(v.co.x, v.co.y) for v in body.data.vertices], bands, smooth_angle=55)
    # The tongues: tapered tubes rising from inside the rim and leaning up the screen to the spikes' tips.
    for i, (c, tip_r, base_r) in enumerate(((3.5, 0.0, 9.0), (9.2, 1.0, 9.5), (16.0, 4.0, 10.0), (21.5, 5.0, 10.5),
                                            (26.2, 5.0, 10.5), (32.5, 4.0, 10.0), (39.6, 1.0, 9.5), (45.0, 0.0, 9.0))):
        x = a.x(c)
        y0, y1 = a.y(base_r), a.y(tip_r)
        z0 = sh.surface_z(body, x, y0, 3.0) - 1.0
        pts = [(x + 0.4 * math.sin(3.0 * t + i), y0 + (y1 - y0) * t, z0 + 3.2 * math.sin(math.pi * t * 0.9))
               for t in [j / 10 for j in range(11)]]
        radii = [1.5 * (1 - t) ** 0.8 + 0.08 for t in [j / 10 for j in range(11)]]
        tongue = w.tube(f"tongue{i}", pts, 1.0, bands[0][1], 8, radii=radii)
        tongue.data.update()
        w.band_split(tongue, [8.0 - 5.5 * (v.co.y - y0) / max(y1 - y0, 1e-3) for v in tongue.data.vertices],
                     bands, smooth_angle=60)
    w.bake()
    sh.flat_bottom(w.meshes())


def bowl_piece(name):
    def build():
        build_fire_bowl()
        return w.cut_piece(*BOWL_PIECES[name])
    return build


# --- BRAINIAC's brain (196, 198, 200 / 233, 235, 237, 239 / 272, 274, 276) ----------------------------

BRAIN = w.Art(art.BRAIN, (48, 42))
BRAIN_PIECES = {
    "brain_top_l": (-36, -12, 14, 42), "brain_top_m": (-12, 12, 14, 42), "brain_top_r": (12, 36, 14, 42),
    "brain_mid_1": (-48, -24, -14, 14), "brain_mid_2": (-24, 0, -14, 14), "brain_mid_3": (0, 24, -14, 14),
    "brain_mid_4": (24, 48, -14, 14),
    "brain_bot_l": (-36, -12, -42, -14), "brain_bot_m": (-12, 12, -42, -14), "brain_bot_r": (12, 36, -42, -14),
}


def build_brain():
    """BRAINIAC's brain, 96 x 84 pixels in ten sprites: two hemispheres domed towards the camera with a
    deep fissure between them, folded into gyri and sulci as the sprite shades them, two blue glands
    under them and nerves hanging below in loops."""
    a = BRAIN
    shade = w.shade_field(a, blur=1, letters={"k": 0.0}, skip="b")
    flesh = [pal(f"brain2_{i:x}", 0x40 + i, metallic=0.15, roughness=0.35) for i in (3, 5, 7, 9, 11)]
    blue = pal("brain2_gland", 0x37, metallic=0.2, roughness=0.12, glow=0.35)
    blue_light = pal("brain2_gland_light", 0x3a, metallic=0.2, roughness=0.1, glow=0.5)
    # The hemispheres: the flesh above row 64.
    mass = a.polys(rows=a.select(lambda c, r, ch: r <= 63 and ch != "b"), smooth=2, epsilon=0.5, min_area=20.0)

    def mass_z(x, y, z):
        fissure = 4.0 * math.exp(-((x - 0.2) / 1.5) ** 2) * w.smoothstep(-24.0, -14.0, y)
        return z + (0.55 * (shade(x, y) - 6.0) - fissure) * w.smoothstep(1.0, 5.0, z)
    body = w.rounded("hemispheres", mass, flesh[2], aspect=0.5, max_height=15.0, spacing=0.6, z_fn=mass_z,
                     sigma=3.0)
    w.simplify_flat(body)
    w.band_split(body, [shade(v.co.x, v.co.y) if v.co.z > 1.5 else 4.0 for v in body.data.vertices],
                 [(-9.0, flesh[0]), (2.2, flesh[1]), (4.4, flesh[2]), (6.6, flesh[3]), (8.8, flesh[4])],
                 smooth_angle=55)
    # The nerves below (rows 64-83): thin strands inflated round from their pixels.
    nerves = a.polys(rows=a.select(lambda c, r, ch: r >= 60 and ch != "b"), smooth=1, epsilon=0.3, min_area=2.0)
    strands = w.rounded("nerves", nerves, flesh[2], aspect=0.9, max_height=3.0, bottom=0.6, base=1.4,
                        spacing=0.5)
    w.decimate(strands, 5000)
    w.band_split(strands, [shade(v.co.x, v.co.y) for v in strands.data.vertices],
                 [(-9.0, flesh[0]), (3.0, flesh[1]), (5.5, flesh[2]), (7.5, flesh[3])], smooth_angle=55)
    # The glands.
    glands = a.polys(rows=a.select(lambda c, r, ch: ch == "b"), smooth=2, epsilon=0.4, min_area=4.0)
    g = w.rounded("glands", glands, blue, aspect=0.9, max_height=4.5, bottom=0.3, base=2.5, spacing=0.5)
    w.decimate(g, 1000)
    w.paint(g, lambda c, n: 1 if n.z > 0.6 and n.x < 0.1 and n.y > -0.1 else 0, [blue, blue_light])
    w.bake()
    sh.flat_bottom(w.meshes())


def brain_piece(name):
    def build():
        build_brain()
        return w.cut_piece(*BRAIN_PIECES[name])
    return build


# --- Registry -----------------------------------------------------------------------------------

PIECES = []  # (name, sprite, builder)
# The ring ship: the left one's pod (39) and ring (41); the right one (43, 45) is its mirror image.
PIECES.append(("ringship_pod", 39, ring_piece("ringship_pod", False)))
PIECES.append(("ringship_ring", 41, ring_piece("ringship_ring", False)))
PIECES.append(("ringship_ring_r", 43, ring_piece("ringship_ring", True)))
PIECES.append(("ringship_pod_r", 45, ring_piece("ringship_pod", True)))
w.whole("ringship", build_ringship, (48, 28), RING.mask())
for _name, _sprite in (("drip_top", 53), ("drip_bottom", 91)):
    PIECES.append((_name, _sprite, drip_piece(_name)))
w.whole("drip", build_drip, (24, 56), DRIP.mask())
for _name, _sprite in (("fire_bowl_left", 156), ("fire_bowl_right", 158)):
    PIECES.append((_name, _sprite, bowl_piece(_name)))
w.whole("fire_bowl", build_fire_bowl, (48, 28), BOWL.mask())
for _name, _sprite in (("brain_top_l", 196), ("brain_top_m", 198), ("brain_top_r", 200), ("brain_mid_1", 233),
                       ("brain_mid_2", 235), ("brain_mid_3", 237), ("brain_mid_4", 239), ("brain_bot_l", 272),
                       ("brain_bot_m", 274), ("brain_bot_r", 276)):
    PIECES.append((_name, _sprite, brain_piece(_name)))
w.whole("brain", build_brain, (96, 84), BRAIN.mask())
