"""The batch L objects that the game draws from several sprites of sheet 5 (wave3_l.py registers them): each
is built whole, in shared coordinates, from its pixel art (wave3_l_art.py) and cut along its sprites'
edges into the pieces, each moved to its sprite's centre (models.cfg: origin, so that they meet again).
The levels place the pieces as the sheet arranges them (checked in the level files' enemy events).

- redjet_left, redjet_right, redjet_nose: the grey and red jet of APPROACH and SAVARA IV, nose down:
  sprites 229 (left wing) and 231 (right wing) above 268 (the nose), 48 x 56 pixels.
- ringship_pod, ringship_ring (39, 41) and their mirror images ringship_ring_r, ringship_pod_r (43, 45):
  HARVEST's machine on a ring frame, a blue pod and a grey housing round a blue sphere.
- longship_left, longship_mid, longship_right (115, 117, 119): the long grey ship of APPROACH and SAVARA IV.
- drip_top, drip_bottom (53 above 91): NOSE DRIP's twisted drip of fire.
- fire_bowl_left, fire_bowl_right (156, 158): NOSE DRIP's bowl of flames.
- brain_* (196, 198, 200 / 233, 235, 237, 239 / 272, 274, 276): BRAINIAC's brain, 96 x 84 pixels.
"""
import math

import wave3_l_art as art
import wave3_l_kit as w
from wave3_l_kit import k, sh, pal


# --- The jet (229 and 231 above 268) ------------------------------------------------------------

JET = w.Art(art.JET, (24, 28))
JET_AXIS = 0.5  # the jet's middle (pixel column 24)
JET_PIECES = {"redjet_left": (-24, 0, 0, 28), "redjet_right": (0, 24, 0, 28), "redjet_nose": (-12, 12, -28, 0)}


def jet_materials():
    return {
        "hull": pal("redjet_hull", 0x07, metallic=0.5, roughness=0.35),
        "light": pal("redjet_light", 0x0a, metallic=0.55, roughness=0.28),
        "dark": pal("redjet_dark", 0x03, metallic=0.4, roughness=0.5),
        "wing": pal("redjet_wing", 0x06, metallic=0.5, roughness=0.38),
        "red": pal("redjet_red", 0x46, metallic=0.35, roughness=0.35),
        "red_light": pal("redjet_red_light", 0x48, metallic=0.35, roughness=0.3),
        "glass": pal("redjet_glass", 0x02, metallic=0.3, roughness=0.08),
    }


def jet_sym(points):
    """Points (x, y) of the left side and their mirror images on the right (about the jet's middle),
    as two polygons."""
    right = [(2 * JET_AXIS - x, y) for x, y in reversed(points)]
    return points, right


def build_jet():
    """The jet, nose down the screen: a round fuselage from the tail (row 3) to the pointed nose (row
    51) with a dark canopy in three panes near the nose, two intakes as humps at the wings' roots with
    a red shield between them, broad wings with red flaps at their roots and red strakes along the
    fuselage, upright fins at the wing tips (red at their fronts), the tail planes at the top with red
    fairings under them and a tall fin with a red top edge."""
    m = jet_materials()
    a = JET
    ax = JET_AXIS
    zc = 1.2

    # The fuselage: (y, half width) from the art's rows, round, the nose drooping a little.
    widths = [(-23.7, 0.15), (-22.6, 1.0), (-21.0, 1.7), (-19.0, 2.5), (-16.5, 3.4), (-14.0, 4.3), (-12.0, 5.0),
              (-10.0, 5.4), (-6.0, 5.6), (0.0, 5.6), (6.0, 5.5), (12.0, 5.1), (17.0, 4.7), (21.0, 4.3), (23.5, 3.8),
              (25.0, 3.2), (25.6, 2.6)]
    sections = []
    for y, hw in widths:
        droop = -0.9 * w.smoothstep(-8.0, -23.7, y)
        sections.append((y, ax, zc + droop, hw, hw * 0.86, hw * 0.62))
    body = w.loft_y("fuselage", sections, m["hull"], segments=28, power=2.3, start=(ax, -23.9, zc - 0.9),
                  end=(ax, 25.7, zc))
    # The nozzle at the tail end: a dark ring.
    w.lathe_axis("nozzle", [(0.0, 2.9), (0.3, 3.1), (1.0, 3.0), (1.2, 2.2), (1.25, 0.01)], m["dark"],
                 (ax, 25.2, zc), (0, 1, 0), 24)

    def top_z(y):
        hw = 5.6
        for (y0, h0), (y1, h1) in zip(widths, widths[1:]):
            if y0 <= y <= y1:
                hw = h0 + (h1 - h0) * (y - y0) / (y1 - y0)
        return zc - 0.9 * w.smoothstep(-8.0, -23.7, y) + hw * 0.86

    # The canopy: dark glass in three panes (rows 33-42), its frame along the middle and across.
    cy, cl = -9.6, 5.5
    canopy = w.sphere("canopy", (ax, cy, top_z(cy) - 1.0), (2.9, cl, 2.3), m["glass"], 24, 12)
    w.tube("canopy_frame", w.catmull([(ax, cy + cl * 0.98, top_z(cy + cl) - 0.1), (ax, cy, top_z(cy) + 1.25),
                                      (ax, cy - cl * 0.98, top_z(cy - cl) - 0.1)], 0.5), 0.42, m["light"], 8)
    for yb in (-8.3, -11.4):
        t = (yb - cy) / cl
        r = math.sqrt(max(0.0, 1 - t * t))
        pts = []
        for i in range(9):
            u = -1 + 2 * i / 8
            xx = ax + u * 2.9 * r
            zz = top_z(cy) - 1.0 + 2.3 * r * math.sqrt(max(0.0, 1 - u * u)) + 0.05
            pts.append((xx, yb, zz))
        w.tube(f"canopy_bar{yb}", pts, 0.32, m["light"], 8)
    # A light spine from the canopy back to the fin (the sprite's bright line).
    w.tube("spine", w.catmull([(ax - 0.3, cy + cl - 0.5, top_z(cy + cl) - 0.25), (ax - 0.3, 0.0, top_z(0.0) - 0.05),
                               (ax - 0.2, 10.0, top_z(10.0) - 0.1)], 0.6), 0.45, m["light"], 8)

    # The wings (pixel corners of the left one), thicker at the roots, the tips a little raised.
    left = w.poly_px(a, [(4.3, 14.2), (7.5, 16.4), (9.5, 17.4), (10.6, 16.0), (11.2, 15.0), (16.0, 15.0),
                         (19.6, 15.0), (19.6, 33.0), (17.8, 33.0), (15.5, 31.5), (13.0, 28.8), (9.5, 26.4),
                         (6.0, 22.6), (4.3, 21.4)])
    def wing_z(x, y, z):
        # Thicker at the root, the tips raised a little (dihedral).
        d = abs(x - ax)
        return z * (1.0 + 0.7 * (1.0 - w.smoothstep(6.0, 16.0, d))) + 0.9 * w.smoothstep(8.0, 20.0, d)

    for i, poly in enumerate(jet_sym(left)):
        w.bevelled_slab(f"wing{i}", poly, -0.7, 0.9, m["wing"], bevel=0.45, z_fn=wing_z)

    # The wing-tip fins: rounded upright fins, red at the front (rows 20-27).
    for side, x in ((-1, a.x(3)), (1, a.x(45))):
        secs = []
        for i in range(14):
            t = i / 13
            y = 15.3 - 15.8 * t
            end = math.sqrt(max(0.0, 1.0 - (2 * abs(t - 0.5)) ** 6))
            secs.append((y, x, 0.8, 1.45 * max(end, 0.15), (2.0 + 2.6 * (1 - t)) * max(end, 0.2), 1.6 * max(end, 0.2)))
        fin = w.loft_y(f"tip_fin{side}", secs[::-1], m["hull"], segments=16, power=2.4, angle=50)
        w.paint(fin, lambda c, n: 1 if c.y < 7.6 else 0, [m["hull"], m["red"]])

    # The intakes: humps along the wing roots beside the fuselage (rows 8-17).
    for side in (-1, 1):
        xc = ax + side * 6.6
        secs = []
        for y, hw, top in ((20.6, 0.4, 0.4), (20.0, 2.0, 2.2), (18.5, 3.0, 3.4), (16.0, 3.3, 3.8), (13.5, 3.1, 3.6),
                           (11.0, 2.4, 2.8), (8.5, 1.4, 1.6), (6.5, 0.3, 0.3)):
            secs.append((y, xc, zc + 0.3, hw, top, 2.2))
        w.loft_y(f"intake{side}", secs[::-1], m["hull"], segments=20, power=2.2)
        # The intake's mouth at its rear end (it faces back, up the screen): a dark scoop.
        w.sphere(f"intake_mouth{side}", (xc, 19.6, zc + 1.2), (1.7, 0.8, 1.6), m["dark"], 16, 8)

    # The red shield between the intakes (rows 10-16), around the fin's root.
    shield = w.poly_px(a, [(21.0, 10.0), (28.0, 10.0), (29.2, 12.0), (28.6, 14.2), (26.6, 15.8), (24.5, 16.6),
                           (22.4, 15.8), (20.4, 14.2), (19.8, 12.0)])
    sh_obj = w.simplify_flat(w.plate("shield", [shield], m["red"], 0.9, radius=0.8, base=0.0, spacing=0.45))
    for v in sh_obj.data.vertices:
        v.co.z += top_z(v.co.y) - 0.35 + 0.5 * w.smoothstep(16.0, 11.0, v.co.y)

    # The red swooshes over the wings' roots (rows 15-29): from the wing's rear edge, curving down beside the
    # intake and on along the fuselage as a thin strake.
    swoosh = w.poly_px(a, [(10.0, 15.9), (11.2, 15.0), (15.2, 15.0), (16.4, 17.0), (19.8, 17.2), (19.8, 29.6),
                           (18.4, 29.6), (17.8, 25.0), (16.6, 22.0), (14.8, 19.8), (12.6, 18.8)])
    for i, sw in enumerate(jet_sym(swoosh)):
        def swoosh_z(x, y, z):
            # Rising against the fuselage, lying on the wing elsewhere.
            return z * (1.0 + 1.4 * w.smoothstep(4.5, 1.0, abs(x - ax) - 3.0))
        s_ = w.plate(f"swoosh{i}", [sw], m["red"], 0.8, radius=0.6, spacing=0.45, z_fn=swoosh_z)
        for v in s_.data.vertices:
            v.co.z += 1.15 + 0.35 * w.smoothstep(8.0, 14.0, abs(v.co.x - ax))
        w.simplify_flat(s_)

    # The tail planes (rows 1-5), their outer ends raised, with red fairings under them sweeping down to the
    # fuselage (rows 5-9).
    tail = w.poly_px(a, [(9.0, 2.2), (10.0, 1.0), (17.0, 1.0), (18.8, 2.4), (20.6, 3.6), (20.6, 5.4), (12.0, 5.4),
                         (9.4, 5.4)])
    fairing = w.poly_px(a, [(11.0, 4.6), (20.8, 4.6), (20.8, 9.0), (17.6, 9.4), (15.6, 8.2), (13.4, 6.6)])
    for i, (tl, fr) in enumerate(zip(jet_sym(tail), jet_sym(fairing))):
        t = w.bevelled_slab(f"tail{i}", tl, -0.6, 0.6, m["hull"], bevel=0.4,
                            z_fn=lambda x, y, z: z + zc + 2.9 + 1.3 * w.smoothstep(4.0, 15.0, abs(x - ax)))
        w.paint(t, lambda c, n: 1 if n.z > 0.6 and c.y > 26.0 else 0, [m["hull"], m["light"]])
        f = w.plate(f"fairing{i}", [fr], m["red"], 1.5, radius=1.0, base=0.0, bottom=0.6, spacing=0.55)
        for v in f.data.vertices:
            v.co.z += zc + 1.4 + 0.9 * w.smoothstep(19.0, 23.5, v.co.y)

    # The tall fin with its red top edge (rows 0-13).
    path = []
    for i in range(12):
        t = i / 11
        y = 28.0 - 13.0 * t
        z_top = 12.0 - 6.2 * t ** 1.3
        path.append((y, ax, zc + 2.0, z_top))
    fin = w.fin_blade("fin", path, m["hull"], thickness=1.8, segments=12)
    w.paint(fin, lambda c, n: 1 if n.z > 0.45 else 0, [m["hull"], m["red"]])

    for obj in w.meshes():
        k.recalc_normals(obj)


def jet_piece(name):
    def build():
        build_jet()
        return w.cut_piece(*JET_PIECES[name])
    return build


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


# --- The long ship (115, 117, 119) --------------------------------------------------------------

LONG = w.Art(art.LONGSHIP, (36, 14))
LONG_PIECES = {"longship_left": (-36, -12, -14, 14), "longship_mid": (-12, 12, -14, 14),
               "longship_right": (12, 36, -14, 14)}


def build_longship():
    """APPROACH's and SAVARA IV's long grey ship flying down the screen: a long tube across the screen
    (rows 9-18) with bright rounded pods at its ends, red rings and red bands along its front, small
    pylons with red tips above and below it, and across its middle the fuselage, its blunt nose down
    (row 26) with dark slots, a small fin with red canards at the top (rows 0-4)."""
    a = LONG
    grey = pal("longship_grey", 0x05, metallic=0.55, roughness=0.35)
    pod = pal("longship_pod", 0x08, metallic=0.55, roughness=0.3)
    light = pal("longship_light", 0x0b, metallic=0.6, roughness=0.25)
    dark = pal("longship_dark", 0x02, metallic=0.4, roughness=0.5)
    red = pal("longship_red", 0x45, metallic=0.35, roughness=0.35)
    red_light = pal("longship_red_light", 0x47, metallic=0.35, roughness=0.3)
    yc, zc, squash = 0.0, 0.0, 0.8
    # The tube, along x: (x, radius) for its left half, mirrored.
    half = [(-34.4, 0.02), (-34.3, 2.6), (-33.9, 3.7), (-33.0, 4.35), (-31.6, 4.65), (-25.4, 4.65), (-24.8, 4.1),
            (-23.6, 4.1), (-23.0, 4.3), (-6.0, 4.3)]
    prof = [(x + 34.4, r) for x, r in half] + [(-x + 34.4, r) for x, r in reversed(half[:-1])]
    tube = w.lathe_axis("tube", prof, grey, (-34.4, yc, zc), (1, 0, 0), 28, squash=squash)
    w.paint(tube, lambda c, n: 1 if abs(c.x) > 24.9 else 0, [grey, pod])
    # A light seam round each end pod.
    for side in (-1, 1):
        x = side * 28.0
        w.lathe_axis(f"pod_ring{side}", [(0.0, 4.5), (0.15, 4.85), (0.85, 4.85), (1.0, 4.5)], light,
                     (x - 0.5, yc, zc), (1, 0, 0), 28, squash=squash)
    # The red rings (columns 16-18 and their mirror images) and the red bands along the front (rows 13-16).
    for side in (-1, 1):
        for i, x in enumerate((-19.6, -17.4)):
            xx = side * x
            w.lathe_axis(f"red_ring{side}{i}", [(0.0, 4.1), (0.2, 4.75), (1.0, 4.75), (1.2, 4.1)], red,
                         (xx - 0.6, yc, zc), (1, 0, 0), 28, squash=squash)
        x0, x1 = (-16.2, -4.0) if side < 0 else (4.0, 16.2)
        w.arc_band(f"red_band{side}", x0, x1, yc, zc, 4.0, 4.6, 8.0, 80.0, red_light, squash=squash)
    # The pylons above and below the tube, with red tips: (x centre, half width, reach up, reach down, tip).
    for side in (-1, 1):
        for i, (xc, hw, up, down, tip) in enumerate(((-28.0, 2.6, 7.0, 8.0, 1.6), (-17.8, 3.6, 8.6, 6.9, 2.0),
                                                     (-9.0, 2.0, 7.0, 6.8, 0.0))):
            x = side * xc
            for j, (sy, r) in enumerate(((1, up), (-1, down))):
                w.rounded_box(f"pylon{side}{i}{j}", (x, yc + sy * (r / 2 + 1.0), zc + 0.6),
                              (2 * hw, r - 1.4, 3.2), grey, bevel=0.6)
                if tip:
                    w.rounded_box(f"pylon_tip{side}{i}{j}", (x, yc + sy * (r - 0.5), zc + 0.9), (2 * hw - 0.6, tip, 2.6),
                                  red, bevel=0.45)
                else:
                    w.sphere(f"knob{side}{i}{j}", (x, yc + sy * (r - 1.2), zc + 1.2), (1.5, 1.5, 1.3), light, 12, 6)
    # The fuselage along y, its blunt nose down.
    ax = 0.5
    widths = [(-12.6, 0.3), (-12.2, 1.6), (-11.4, 2.6), (-10.0, 3.6), (-7.5, 4.3), (-4.0, 4.6), (0.0, 4.7),
              (4.0, 4.6), (5.0, 4.2), (6.0, 3.4), (7.5, 2.6), (9.5, 2.6), (11.5, 2.3), (13.0, 1.5), (13.8, 0.4)]
    secs = [(y, ax, zc + 0.3, hw, hw * 1.08, hw * 0.75) for y, hw in widths]
    body = w.loft_y("fuselage", secs, grey, segments=24, power=2.2)
    w.tube("spine", w.catmull([(ax - 0.4, -11.0, zc + 2.6), (ax - 0.4, -6.0, zc + 4.7), (ax - 0.4, 2.0, zc + 5.2),
                               (ax - 0.4, 8.0, zc + 4.4), (ax - 0.3, 12.0, zc + 1.8)], 0.6), 0.5, light, 8)
    # Dark slots on the fuselage's lower part (rows 18-23).
    for i, x in enumerate((ax - 2.4, ax + 2.4)):
        w.tube(f"slot{i}", [(x, -4.8, zc + 4.0), (x, -9.0, zc + 2.6)], 0.5, dark, 8)
    # The small fin and red canards at the top.
    w.fin_blade("fin", [(13.9, ax, zc + 1.0, zc + 3.2), (11.5, ax, zc + 2.6, zc + 5.4), (7.5, ax, zc + 3.8, zc + 5.6)],
                light, thickness=1.2)
    # The head: a bar across the fuselage's top end (rows 2-4), its arms red.
    w.rounded_box("head", (ax, 10.9, zc + 2.6), (10.6, 2.6, 2.2), grey, bevel=0.6)
    for side in (-1, 1):
        w.rounded_box(f"head_arm{side}", (ax + side * 3.5, 10.9, zc + 3.6), (3.0, 1.6, 0.8), red, bevel=0.3)
    for obj in w.meshes():
        k.recalc_normals(obj)


def long_piece(name):
    def build():
        build_longship()
        return w.cut_piece(*LONG_PIECES[name])
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
for _name, _sprite in (("redjet_left", 229), ("redjet_right", 231), ("redjet_nose", 268)):
    PIECES.append((_name, _sprite, jet_piece(_name)))
w.whole("redjet", build_jet, (48, 56), JET.mask())
# The ring ship: the left one's pod (39) and ring (41); the right one (43, 45) is its mirror image.
PIECES.append(("ringship_pod", 39, ring_piece("ringship_pod", False)))
PIECES.append(("ringship_ring", 41, ring_piece("ringship_ring", False)))
PIECES.append(("ringship_ring_r", 43, ring_piece("ringship_ring", True)))
PIECES.append(("ringship_pod_r", 45, ring_piece("ringship_pod", True)))
w.whole("ringship", build_ringship, (48, 28), RING.mask())
for _name, _sprite in (("longship_left", 115), ("longship_mid", 117), ("longship_right", 119)):
    PIECES.append((_name, _sprite, long_piece(_name)))
w.whole("longship", build_longship, (72, 28), LONG.mask())
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
