"""Batch Y of wave 3 (sheet 8: IXMUCANE and SAWBLADES), the objects the game draws in pieces, modelled as
their sprites look (models.cfg: yaw=0), each built whole and cut into its sprites' pieces, drawn at their
own origins (origin) so they meet. The level events place the pieces as the sheet arranges them. The kit is
wave3_y_kit.py, the pixels wave3_y_art.py.

- ixm_dock_tl, _tc, _tr, _bl, _bc, _br (8 39, 41, 43 above 77, 79, 81; event 7, all on the top layer):
  IXMUCANE's red ship docked between two grey engines, 72 x 56: the engines are blocks with louvred vents
  on top, red caps at their front, a red light and a glowing exhaust grille with fins at their back; between
  them the red ship, a keel with three cross bars (the widest, its wings, joins the engines) and a spike at
  its tail, lies over a grey dome with two grey pods under its tail.
- ixm_pod_top, ixm_pod_body (8 153 above 191; events 6 and 10, both on the ground): the red pod lying on
  the ground, its nose up the screen: a big red sack with two glowing slits (191's frames pulse them), a
  brown flared collar, a grey head with a dark window in a red frame and a red lamp glowing on its nose
  (153's frames pulse it).
- ixm_spider_l, ixm_spider_r (8 229 beside 231; event 7, both on the top layer): the big tan spider:
  a red heart-shaped body with a red spike at its front and a dark head, two grey fangs under it and four
  tan legs a side, curving out and up the screen at their ends (its frames 233/235, 273/275 move the legs a
  little; the model keeps the first).

usage: Blender -b --factory-startup -P wave3_y_boss.py -- [--only names] [--preview <prefix>] [--check 1]
       [--whole <prefix>]
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_y_kit as y  # noqa: E402
from wave3_y_kit import k, sh, pal, tube, sphere, lathe_axis, smoothstep  # noqa: E402


# --- 8 39 41 43 / 77 79 81: the docked ship ----------------------------------------------------------

BOSS = y.frame("BOSS", 72, (36, 28))
AX = -0.5  # the object's axis of symmetry


def dock_mats():
    m = {f"g{s_}": pal(f"dock_grey{s_}", s_, metallic=0.5, roughness=0.32) for s_ in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)}
    m.update({
        "red": pal("dock_red", 0x46, metallic=0.4, roughness=0.32),
        "red_light": pal("dock_red_light", 0x49, metallic=0.4, roughness=0.28),
        "red_dark": pal("dock_red_dark", 0x43, metallic=0.35, roughness=0.4),
        "glow": pal("dock_glow", 0x77, metallic=0.0, roughness=0.3, glow=2.0),
        "glow_hot": pal("dock_glow_hot", 0x79, metallic=0.0, roughness=0.25, glow=2.4),
        "well": pal("dock_well", 0x01, metallic=0.2, roughness=0.7),
    })
    return m


def engine(m, side):
    """One engine (side -1 left, 1 right): x 11..33 from the axis, y -26..17."""
    def X(v):
        return AX + side * v
    cx = X(22.0)
    top = 11.0
    body = y.block(f"engine{side}", (cx, -4.6), 10.9, 21.6, top, m["g7"], rounding=1.6, power=6.0, segments=40)
    y.paint_faces(body, lambda c, nrm: m["g9"] if nrm.z > 0.8 else m["g5"] if nrm.z > -0.2 else m["g3"])
    # The louvred vent: a dark recess with slats across, a lighter cover at its front.
    y.rounded_box(f"vent_well{side}", (X(23.5), 5.4, top - 0.2), (11.2, 15.4, 1.0), m["g3"], bevel=0.3)
    y.rounded_box(f"vent_cover{side}", (X(23.5), 11.6, top + 0.35), (10.6, 3.0, 0.9), m["g10"], bevel=0.35)
    for i, yy in enumerate((8.5, 6.5, 4.5, 2.5, 0.5)):
        y.prism_x(f"slat{side}_{i}", [(yy - 0.75, top - 0.2), (yy + 0.75, top - 0.2), (yy + 0.55, top + 0.75),
                                             (yy - 0.45, top + 0.6)], X(28.6) if side < 0 else X(18.4),
                         X(18.4) if side < 0 else X(28.6), m["g11"], bevel=0.12, segments=1)
    # The rail along its inner side.
    y.rounded_box(f"rail{side}", (X(15.4), 1.0, top + 0.4), (4.2, 24.0, 1.4), m["g8"], bevel=0.5)
    # The red caps at its front.
    y.rounded_box(f"cap_a{side}", (X(25.6), 15.9, top - 1.4), (8.4, 3.0, 3.4), m["red"], bevel=0.8)
    y.rounded_box(f"cap_b{side}", (X(17.0), 15.9, top - 1.4), (2.8, 3.0, 3.4), m["red"], bevel=0.6)
    # The lower panel with its red light.
    y.rounded_box(f"panel{side}", (X(22.0), -6.4, top + 0.25), (15.0, 7.6, 0.9), m["g8"], bevel=0.35)
    y.rounded_box(f"light{side}", (X(22.4), -5.8, top + 0.75), (7.6, 2.2, 0.8), m["red_light"], bevel=0.3)
    # The exhaust grille at its back: a glowing well with fins.
    y.rounded_box(f"grille_frame{side}", (X(22.0), -17.6, top - 0.6), (17.4, 13.6, 1.8), m["g4"], bevel=0.4)
    y.rounded_box(f"grille{side}", (X(22.0), -17.6, top - 0.1), (15.6, 11.8, 1.4), m["glow"], bevel=0.3)
    y.rounded_box(f"grille_core{side}", (X(22.0), -17.6, top + 0.15), (11.0, 7.0, 1.2), m["glow_hot"], bevel=0.4)
    for i in range(6):
        x = X(15.5 + 2.6 * i)
        y.rounded_box(f"fin{side}_{i}", (x, -17.6, top + 0.35), (0.7, 12.0, 1.4), m["g5"], bevel=0.2)


def build_dock():
    m = dock_mats()
    for side in (-1, 1):
        engine(m, side)
    # The grey dome under the ship and the two pods under its tail.
    dome = sphere("dome", (AX, 12.6, 1.0), (10.4, 9.8, 10.0), m["g7"], 32, 16)
    y.paint_faces(dome, lambda c, nrm: m["g9"] if nrm.z > 0.4 else m["g6"] if nrm.z > -0.2 else m["g3"])
    for side in (-1, 1):
        pod = sphere(f"pod{side}", (AX + side * 5.6, -17.0, 2.5), (3.0, 7.0, 4.6), m["g7"], 20, 12)
        y.paint_faces(pod, lambda c, nrm: m["g10"] if nrm.z > 0.8 else m["g7"] if nrm.z > 0.3 else m["g4"])
    # The ship: a keel down the middle, three cross bars, a head plate and the tail spike.
    keys = [(-26.6, 0.15, 5.4), (-24.4, 0.8, 6.0), (-21.5, 1.2, 6.8), (-18.0, 1.6, 7.6), (-15.6, 2.4, 8.4),
            (-13.2, 3.6, 9.0), (-10.6, 4.6, 9.8), (-7.0, 4.4, 10.6), (-3.5, 3.6, 11.2), (0.0, 3.3, 11.5),
            (4.0, 3.2, 11.8), (7.4, 4.2, 12.0), (10.0, 3.6, 12.0), (12.0, 1.9, 11.8), (14.2, 1.4, 11.5),
            (15.8, 0.25, 11.0)]
    secs = [(yy, AX, zc, hw, max(0.5, 0.45 * hw + 0.9), max(0.5, 0.45 * hw + 0.9)) for yy, hw, zc in keys]
    keel = y.loft_y("keel", y.smooth_sections(secs, 0.6), m["red"], segments=20, power=2.4)
    y.paint_faces(keel, lambda c, nrm: m["red_light"] if nrm.z > 0.6 and c.x < AX - 0.8 else
                  m["red"] if nrm.z > 0.3 else m["red_dark"])

    def bar(name, yy, depth, half, z, height, sweep=0.0):
        """A cross bar at yy, `half` either side of the axis, its ends swept back by `sweep`."""
        outline = [(AX - half, yy - depth / 2 - sweep), (AX + half, yy - depth / 2 - sweep),
                   (AX + half, yy + depth / 2 - sweep * 0.6), (AX + 1.2, yy + depth / 2 + 0.4),
                   (AX - 1.2, yy + depth / 2 + 0.4), (AX - half, yy + depth / 2 - sweep * 0.6)]
        obj = y.slab(name, outline, z - height / 2, z + height / 2, m["red"], bevel=0.6, segments=2)
        y.paint_faces(obj, lambda c, nrm: m["red_light"] if nrm.z > 0.7 and c.x < AX - 2 else
                      m["red"] if nrm.z > 0.4 else m["red_dark"])
        return obj
    bar("bar_top", 3.6, 2.8, 7.6, 12.2, 1.8)
    bar("bar_mid", -3.9, 3.6, 8.2, 11.4, 1.9, sweep=0.8)
    bar("wings", -8.3, 4.6, 12.4, 10.2, 1.9, sweep=1.4)
    head = y.slab("head", [(AX - 5.2, 6.0), (AX + 5.2, 6.0), (AX + 5.4, 10.4), (AX + 3.6, 12.0), (AX - 3.6, 12.0),
                           (AX - 5.4, 10.4)], 10.6, 13.0, m["red"], bevel=0.6, segments=2)
    y.paint_faces(head, lambda c, nrm: m["red_light"] if nrm.z > 0.7 else m["red_dark"])
    y.rounded_box("head_slot", (AX, 9.0, 13.1), (5.2, 1.2, 0.5), m["red_dark"], bevel=0.2)
    y.cone("spike", (AX, -24.0, 5.6), (0, -1, -0.15), 4.0, 0.9, m["red_light"], segments=12)
    y.cone("nose", (AX, 14.6, 11.2), (0, 1, -0.1), 3.0, 0.8, m["red_light"], segments=12)


_DOCK = [("ixm_dock_tl", -24.0, 14.0, (0, 24, 0, 28)), ("ixm_dock_tc", 0.0, 14.0, (24, 48, 0, 28)),
         ("ixm_dock_tr", 24.0, 14.0, (48, 72, 0, 28)), ("ixm_dock_bl", -24.0, -14.0, (0, 24, 28, 56)),
         ("ixm_dock_bc", 0.0, -14.0, (24, 48, 28, 56)), ("ixm_dock_br", 24.0, -14.0, (48, 72, 28, 56))]
y.pieced("ixm_dock", build_dock, (72, 56),
         [(name, (cx - 12.0, cx + 12.0, cy - 14.0, cy + 14.0), (cx, cy), (lambda b=box: y.frame_mask(BOSS, b)))
          for name, cx, cy, box in _DOCK])


# --- 8 153 above 191: the red pod --------------------------------------------------------------------

POD = y.frame("POD", 24, (12, 28))


def build_pod():
    ax = -0.5
    red = pal("pod_red", 0x46, metallic=0.25, roughness=0.4)
    red_light = pal("pod_red_light", 0x4a, metallic=0.25, roughness=0.35)
    red_dark = pal("pod_red_dark", 0x42, metallic=0.2, roughness=0.5)
    slit = pal("pod_slit", 0x79, metallic=0.0, roughness=0.3, glow=2.0)
    slit_rim = pal("pod_slit_rim", 0x72, metallic=0.1, roughness=0.35, glow=0.6)
    collar = pal("pod_collar", 0x15, metallic=0.25, roughness=0.5)
    collar_light = pal("pod_collar_light", 0x18, metallic=0.25, roughness=0.45)
    collar_dark = pal("pod_collar_dark", 0x12, metallic=0.2, roughness=0.55)
    grey = pal("pod_grey", 0x08, metallic=0.5, roughness=0.3)
    grey_light = pal("pod_grey_light", 0x0b, metallic=0.5, roughness=0.28)
    grey_dark = pal("pod_grey_dark", 0x04, metallic=0.45, roughness=0.4)
    window = pal("pod_window", 0x11, metallic=0.3, roughness=0.2)
    lamp = pal("pod_lamp", 0x78, metallic=0.0, roughness=0.3, glow=2.0)
    lamp_hot = pal("pod_lamp_hot", 0x7c, metallic=0.0, roughness=0.25, glow=2.6)
    lamp_rim = pal("pod_lamp_rim", 0x45, metallic=0.35, roughness=0.35)

    # The sack: an egg lying down the screen, fullest low.
    keys = [(0.0, 0.01), (0.6, 2.6), (1.6, 4.8), (3.5, 6.6), (6.0, 8.0), (9.0, 9.0), (12.0, 9.5), (15.0, 9.5),
            (18.0, 8.9), (21.0, 7.6), (23.6, 5.6), (25.6, 3.4), (27.0, 1.2), (27.5, 0.01)]
    sack = lathe_axis("sack", k.profile(keys, 0.5), red, (ax, 4.0, 6.6), (0, -1, 0), segments=32, squash=0.72)
    y.paint_faces(sack, lambda c, nrm: red_light if nrm.z > 0.75 and nrm.x < 0.1 else red if nrm.z > 0.3 else red_dark)
    # The two glowing slits across its back.
    for i, yy in enumerate((-5.6, -7.6)):
        z = 6.6 + 0.72 * 9.4 - 0.25
        y.rounded_box(f"slit_rim{i}", (ax - 0.5, yy, z), (7.4, 1.6, 1.0), slit_rim, bevel=0.4)
        y.rounded_box(f"slit{i}", (ax - 0.5, yy, z + 0.3), (6.0, 0.9, 0.8), slit, bevel=0.3)
    # A few folds down the sack.
    prof = k.profile(keys, 0.5)

    def sack_z(x, yy):
        r = y.interp(prof, 4.0 - yy)
        return 6.6 + 0.72 * math.sqrt(max(0.0, r * r - (x - ax) ** 2))
    for side in (-1, 1):
        path = [(ax + side * 3.4, 1.0), (ax + side * 4.9, -6.0), (ax + side * 5.2, -13.0), (ax + side * 3.8, -19.6)]
        pts = [(p.x, p.y, sack_z(p.x, p.y) - 0.2) for p in y.catmull([(px, py, 0.0) for px, py in path], 0.6)]
        tube(f"fold{side}", pts, 0.5, red_dark, 8)
    # The collar: a flared brown skirt round the head's foot.
    lathe_axis("collar", [(0.0, 9.4), (0.5, 10.5), (1.5, 10.9), (2.8, 10.2), (4.2, 8.8), (5.8, 7.4), (7.2, 6.6)],
               collar, (ax, 2.4, 6.6), (0, 1, 0), segments=32, squash=0.74)
    # The head: a grey drum along the axis, the dark window in a red frame on top.
    head = lathe_axis("head", [(0.0, 6.4), (0.4, 6.6), (6.6, 6.4), (7.2, 6.0), (7.6, 5.0)], grey, (ax, 9.6, 6.6),
                      (0, 1, 0), segments=32, squash=0.9)
    y.paint_faces(head, lambda c, nrm: grey_light if nrm.z > 0.8 and c.x < ax - 1 else grey if nrm.z > 0.3 else grey_dark)
    y.rounded_box("frame", (ax - 0.5, 13.8, 12.3), (6.4, 7.8, 1.2), red, bevel=0.45)
    y.rounded_box("window", (ax - 0.5, 13.8, 12.75), (4.0, 5.6, 0.8), window, bevel=0.35)
    # The lamp on its nose.
    sphere("lamp", (ax + 0.4, 18.4, 6.8), (4.8, 5.2, 4.4), lamp, 24, 12)
    sphere("lamp_core", (ax + 0.4, 20.2, 8.4), (2.4, 2.4, 2.0), lamp_hot, 16, 8)
    y.torus("lamp_rim", (ax + 0.2, 17.6, 6.6), 5.0, 0.7, lamp_rim, 32, 10, scale_y=0.5)


y.pieced("ixm_pod", build_pod, (24, 56),
         [("ixm_pod_top", (-12.0, 12.0, 0.0, 28.0), (0.0, 14.0), lambda: y.frame_mask(POD, (0, 24, 0, 28))),
          ("ixm_pod_body", (-12.0, 12.0, -28.0, 0.0), (0.0, -14.0), lambda: y.frame_mask(POD, (0, 24, 28, 56)))])


# --- 8 229 beside 231: the big spider ------------------------------------------------------------------

SPIDER = y.frame("SPIDER", 48, (24, 14))


def build_spider():
    ax = -0.5
    tan = pal("spider_tan", 0x17, metallic=0.25, roughness=0.5)
    tan_dark = pal("spider_tan_dark", 0x13, metallic=0.2, roughness=0.55)
    red = pal("spider_red", 0x47, metallic=0.3, roughness=0.35)
    red_light = pal("spider_red_light", 0x4b, metallic=0.3, roughness=0.3)
    red_dark = pal("spider_red_dark", 0x43, metallic=0.25, roughness=0.45)
    dark = pal("spider_head", 0x03, metallic=0.4, roughness=0.4)
    fang = pal("spider_fang", 0x09, metallic=0.6, roughness=0.25)
    fang_dark = pal("spider_fang_dark", 0x05, metallic=0.55, roughness=0.3)

    # The body: two red lobes (a heart), the dark head before them, the red spike at the front.
    for side in (-1, 1):
        lobe = sphere(f"lobe{side}", (ax + side * 1.75, -2.4, 4.4), (2.5, 3.9, 3.2), red, 20, 10)
        y.paint_faces(lobe, lambda c, nrm: red_light if nrm.z > 0.85 else red if nrm.z > 0.2 else red_dark)
    sphere("head", (ax, 3.4, 4.4), (2.6, 2.8, 2.6), dark, 18, 9)
    y.cone("spike", (ax, 5.2, 5.4), (0, 1, 0.1), 6.0, 1.5, red, segments=14)
    for side in (-1, 1):
        # The fang under the body.
        path = [(ax + side * 3.0, -3.0, 3.6), (ax + side * 5.4, -5.6, 3.2), (ax + side * 5.8, -8.8, 2.4),
                (ax + side * 4.6, -11.4, 1.6)]
        pts = y.resample(path, 14)
        secs = [(max(0.3, 1.1 - 0.75 * i / 13), max(0.3, 0.9 - 0.6 * i / 13)) for i in range(14)]
        f = y.loft_path(f"fang{side}", pts, secs, fang, segments=10)
        y.paint_faces(f, lambda c, nrm: fang if nrm.z > 0.3 else fang_dark)
        # The legs.
        legs = [
            ([(3.0, 1.2, 4.8), (6.0, 4.2, 7.0), (8.6, 7.4, 6.6), (10.2, 10.4, 4.4), (10.6, 13.4, 2.0)], 2.5, 0.8),
            ([(3.6, 0.0, 4.8), (8.6, 1.0, 6.8), (12.4, 1.8, 5.8), (13.9, 3.6, 3.6), (14.6, 5.8, 1.8)], 2.4, 0.8),
            ([(4.0, -4.4, 4.4), (10.6, -5.0, 6.2), (16.4, -5.0, 4.8), (18.2, -2.4, 3.0), (18.6, 2.6, 1.4)], 2.2, 0.8),
            ([(5.0, -6.6, 4.0), (10.0, -9.4, 5.4), (16.8, -9.7, 4.6), (21.6, -9.3, 3.0), (22.9, -7.0, 2.0),
              (23.2, -3.8, 1.2)], 2.1, 0.75),
        ]
        for i, (path, w0, w1) in enumerate(legs):
            pts = y.resample([(ax + side * px, py, pz) for px, py, pz in path], 26)
            secs = []
            for j in range(len(pts)):
                t = j / (len(pts) - 1)
                hw = w0 + (w1 - w0) * t ** 2.2
                secs.append((hw, hw * 0.8))
            leg = y.loft_path(f"leg{side}_{i}", pts, secs, tan, segments=10)
            y.paint_faces(leg, lambda c, nrm: tan if nrm.z > -0.1 else tan_dark)


y.pieced("ixm_spider", build_spider, (48, 28),
         [("ixm_spider_l", (-24.0, 0.0, -14.0, 14.0), (-12.0, 0.0), lambda: y.frame_mask(SPIDER, (0, 24, 0, 28))),
          ("ixm_spider_r", (0.0, 24.0, -14.0, 14.0), (12.0, 0.0), lambda: y.frame_mask(SPIDER, (24, 48, 0, 28)))])


if __name__ == "__main__":
    y.run()
