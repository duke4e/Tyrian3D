"""Enemies of wave 3, batch M (sheet J: TORM, BOTANY A, BONUS), the green machines; modelled as their
sprites look (models.cfg: yaw=0). The building, the field gun and the small ground machines are in
wave3_m_ground.py, the big green shell of ?TUNNEL? in wave3_m_shell.py.
(The small green machine of TORM and BONUS, green_scarab (J 131), is built by polish_green_scarab.py, the green
tower, J 13 15 / 51 53, by polish_green_tower.py.)

- green_skiff_rear, green_skiff_nose (J 169, 207): the green skiff the events bring in from the left
  (169 beside 207), drawn from the tower's parts: the tower's pod (its left half, with the lamp and
  the claw) for a stern and a hull with the outline of the right half of the tower's plate for a bow,
  hovering on a strut; built whole and cut (origin).
- green_skiff_l_nose, green_skiff_l_rear (J 245, 283): its mirror image, coming in from the right.
- green_pod_ship (J 117): the green ship of TORM with bulging red pods at its sides, two lights glowing
  in each, a red crest with two lights at its top and its green hull narrowing to a point down the
  screen.

The pale parts are the light end of the green ramp (0x2c-0x2f), the claws the red ramp (0x70s).

usage: Blender -b --factory-startup -P wave3_m.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1] [--whole skiff|skiff_l --preview <prefix>]
"""
import math
import os
import sys

from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_m_kit as w  # noqa: E402
from wave3_m_kit import art, k, sh, pal, px, py, model, whole, J  # noqa: E402


def greens(prefix):
    """The green machines' materials, by shade."""
    return {
        "dark": pal(f"{prefix}_green_dark", 0x23, metallic=0.35, roughness=0.45),
        "deep": pal(f"{prefix}_green_deep", 0x25, metallic=0.4, roughness=0.4),
        "green": pal(f"{prefix}_green", 0x28, metallic=0.45, roughness=0.35),
        "mid": pal(f"{prefix}_green_mid", 0x29, metallic=0.45, roughness=0.32),
        "light": pal(f"{prefix}_green_light", 0x2a, metallic=0.45, roughness=0.3),
        "pale": pal(f"{prefix}_pale", 0x2c, metallic=0.2, roughness=0.25),
        "cream": pal(f"{prefix}_cream", 0x2d, metallic=0.15, roughness=0.18),
        "glass": pal(f"{prefix}_canopy", 0x2e, metallic=0.1, roughness=0.08),
        "red": pal(f"{prefix}_red", 0x74, metallic=0.4, roughness=0.35),
        "red_dark": pal(f"{prefix}_red_dark", 0x71, metallic=0.35, roughness=0.45),
        "red_light": pal(f"{prefix}_red_light", 0x76, metallic=0.4, roughness=0.3),
        "core": pal(f"{prefix}_core", 0x7c, metallic=0.0, roughness=0.3, glow=1.6),
        "lamp": pal(f"{prefix}_lamp", 0x77, metallic=0.0, roughness=0.25, glow=1.1),
        "orange": pal(f"{prefix}_orange", 0x7a, metallic=0.0, roughness=0.3, glow=1.4),
        "slot": pal(f"{prefix}_slot", 0x21, metallic=0.3, roughness=0.6),
    }


# --- J 131: the green scarab -----------------------------------------------------------------------

# --- The green pod and plate: the tower's parts, of which the skiffs are made too -------------------

def X(col, ox=24):
    """A pixel column's centre in a 48 pixel wide object's coordinates."""
    return col + 0.5 - ox


def pod_radius(x, x_end=22.2, cap=17.0, R=9.4, grooves=(-3.8, 4.3)):
    """The green pod's radius along its axis: rounded ends from |x| = cap, shallow grooves between
    its three segments, the middle one a little slimmer."""
    ax = abs(x)
    f = math.sqrt(max(0.0, 1.0 - ((ax - cap) / (x_end - cap)) ** 2)) if ax > cap else 1.0
    g = 1.0 - sum(0.12 * math.exp(-((x - gx) / 0.9) ** 2) for gx in grooves)
    seg = 0.93 + 0.07 * sh.smoothstep(3.0, 5.6, ax)
    # Each outer segment bulges in its middle.
    seg *= 1.0 + 0.03 * math.exp(-((ax - 10.6) / 4.0) ** 2)
    return R * f * g * seg


def pod(m, axis_y, axis_z, x0=-22.2, x1=22.2, R=9.4, squash=0.72, claws=(-1, 1), slot=True, prefix="pod"):
    """The long green pod lying across the screen at (axis_y, axis_z): three pale bulging segments
    on top, ribbed rounded ends with a red lamp each, a dark slot across its front (the side down
    the screen) and red claws hooking in under its ends. x0..x1: the part of it to build (the
    skiff's stern is its left half)."""
    count = max(8, int(round((x1 - x0) / 0.7)))
    xs = [x0 + (x1 - x0) * i / count for i in range(count + 1)]

    def radius(x):
        r = pod_radius(x, R=R)
        if x1 < 22.0:  # cut short (the skiff's stern): rounded off into the plate
            cap = 3.0
            if x > x1 - cap:
                r *= math.sqrt(max(0.0, 1.0 - 0.8 * ((x - (x1 - cap)) / cap) ** 2))
        return max(0.01, r)
    profile = [(x - x0, radius(x)) for x in xs]
    body = w.lathe_axis(f"{prefix}_body", profile, m["green"], (x0, axis_y, axis_z), (1, 0, 0), 36, squash=squash,
                        smooth_angle=50)

    def paint(c, n):
        rel = c.y - axis_y
        if slot and abs(c.x) < 6.8 and -8.9 < rel < -5.0 and c.z > axis_z:
            return m["slot"]
        if slot and abs(c.x) < 7.2 and -5.0 <= rel < -3.8 and c.z > axis_z:
            return m["pale"]
        if n.z > 0.8:
            return m["cream"] if abs(c.x) > 4.8 and abs(c.x) < 16.6 else m["pale"]
        if n.z > 0.35:
            return m["light"] if n.y > -0.2 else None
        if n.z > -0.3:
            return None
        return m["deep"]
    w.paint_faces(body, paint)
    # The ribs round the ends.
    for side in (-1, 1):
        for xr in (15.6, 18.6):
            x = side * xr
            if not (x0 <= x <= x1):
                continue
            r = pod_radius(x, R=R)
            w.lathe_axis(f"{prefix}_rib{side}{xr}", [(-0.55, r * 0.98), (-0.3, r + 0.45), (0.3, r + 0.45), (0.55, r * 0.98)],
                         m["mid"], (x, axis_y, axis_z), (1, 0, 0), 40, squash=squash)
    # The red lamps at the ends' backs, the claws hooking in under their fronts.
    def on_pod(x, dy, lift):
        r = pod_radius(x, R=R)
        return axis_z + r * squash * math.sqrt(max(0.0, 1.0 - (dy / r) ** 2)) + lift
    for side in claws:
        x = side * 17.6
        w.lamp(f"{prefix}_lamp{side}", (x, axis_y + 7.0, on_pod(x, 7.0, -0.3)), 1.6, m["lamp"], m["red_dark"])
        xc = side * 18.9
        w.claw(f"{prefix}_claw{side}", (xc, axis_y - 1.4, on_pod(xc, -1.4, 0.9)), (xc, axis_y - 6.6, on_pod(xc, -6.6, 1.0)),
               (side * 14.8, axis_y - 9.3, axis_z - 1.5), 2.0, m["red"], m["core"], (0.2, 0.85), segments=12)
    return body


def plate_outline(cx, cy, half_w, top, bottom, x_min=None, count=72):
    """The plate's outline: a superellipse, flatter towards the top of the screen than towards
    the bottom; x_min cuts it off on the left (the skiff's bow)."""
    pts = []
    for i in range(count):
        a = 2 * math.pi * i / count
        c, sn = math.cos(a), math.sin(a)
        p = 2.9 if sn >= 0 else 2.2
        x = cx + math.copysign(abs(c) ** (2 / p), c) * half_w
        y = cy + math.copysign(abs(sn) ** (2 / p), sn) * (top if sn >= 0 else bottom)
        pts.append((max(x, x_min) if x_min is not None else x, y))
    if x_min is not None:  # drop the points squashed onto the cut but its ends
        out = []
        for i, p in enumerate(pts):
            prev, nxt = pts[i - 1], pts[(i + 1) % len(pts)]
            if p[0] == x_min and prev[0] == x_min and nxt[0] == x_min:
                continue
            out.append(p)
        pts = out
    return pts


def plate(name, outline, m, z0=0.0, height=4.4):
    """The wide green plate: a thick disc over the outline, its rim rounded, its front (down the
    screen) darker."""
    obj = sh.inflate(name, [outline], m["green"], sh.pillow_profile(height, 3.6, crown=0.7), base=z0,
                     bottom=0.0 if z0 <= 0 else 0.35, spacing=0.6, sigma=1.6)
    if z0 <= 0:
        w.simplify_bottom(obj)
    w.decimate(obj, 1800)
    k.smooth(obj, 50)
    w.paint_faces(obj, lambda c, n: m["deep"] if n.y < -0.45 and n.z < 0.75 else m["mid"] if n.z > 0.9 else
                  m["light"] if n.y > 0.45 and n.z < 0.8 else None)
    return obj


def plate_details(m, cx, cy, z_of, half_w, half_h, xmin=-99.0, prefix="plate", outline=None):
    """The plate's two ribs running up the screen and a raised lip round its top (outline: the
    plate's outline, inset for the lip)."""
    if outline is not None:
        lip = sh.inset(outline, 2.0)
        pts = [(x, y, z_of(x, y) - 0.15) for x, y in lip if x > xmin + 0.5]
        if xmin < -90:
            pts.append(pts[0])
            pts = w.catmull(pts, 0.8)
        else:  # an open lip from the cut round to the cut
            start = max(range(len(pts)), key=lambda i: abs(pts[i][0] - pts[i - 1][0]) + abs(pts[i][1] - pts[i - 1][1]))
            pts = pts[start:] + pts[:start]
        w.tube(f"{prefix}_lip", pts, 0.7, m["light"], 8, squash=0.8)
    for x in (cx - 10.8, cx + 11.2):
        if x < xmin:
            continue
        pts = [(x, y, z_of(x, y) - 0.05) for y in [cy + half_h * 0.6 - i * 1.0 for i in range(int(half_h * 1.15) + 1)]]
        w.ribbon(f"{prefix}_rib{x:.0f}", pts, 1.8, 0.8, m["light"])


# --- J 169 beside 207 (and 245 beside 283): the green skiff ---------------------------------------------

def bow_y(x, cy, half_w, top, bottom):
    """The plate outline's north and south edges at x (as plate_outline draws it)."""
    t = min(1.0, abs(x) / half_w)
    return cy + top * (1 - t ** 2.9) ** (1 / 2.9), cy - bottom * (1 - t ** 2.2) ** (1 / 2.2)


def bow_radius(x):
    """The skiff bow's half-height in y where it meets the pod (for the band there)."""
    n, s_ = bow_y(x, 0.4, 22.8, 7.6, 10.2)
    return (n - s_) / 2


def bow_hull(name, m, x0, x1, cy, top, bottom, axis_z, squash=0.66, steps=40, segments=36):
    """The skiff's bow: the tower plate's right half as the outline from above, a hull as deep as
    the pod where it starts and thinning towards its rounded nose; dark along its belly."""
    rings = []
    for i in range(steps + 1):
        x = x0 + (x1 - x0) * i / steps
        n, s_ = bow_y(min(x, x1 - 0.02), cy, 22.8, top, bottom)
        if x < 0:  # the outline's widest middle on under the pod
            n, s_ = bow_y(0.0, cy, 22.8, top, bottom)
        yc, hy = (n + s_) / 2, (n - s_) / 2
        hz = min(hy * squash, 6.2) * (1.0 - 0.35 * sh.smoothstep(0.0, 22.0, x))
        rings.append([Vector((x, yc + hy * math.cos(2 * math.pi * j / segments),
                              axis_z + hz * math.sin(2 * math.pi * j / segments) *
                              (1.0 if math.sin(2 * math.pi * j / segments) > 0 else 0.8)))
                      for j in range(segments)])
    obj = k.loft(name, rings, m["green"], end_point=(x1 + 0.3, cy - 0.5, axis_z))
    k.smooth(obj, 50)
    w.paint_faces(obj, lambda c, n: m["dark"] if n.z < -0.2 else m["deep"] if n.y < -0.3 and n.z < 0.8 else
                  m["light"] if n.z > 0.92 else m["mid"] if n.z > 0.45 else None)
    return obj


def skiff_whole(mirror=False):
    """The tower's pod (its left half, with a lamp and a claw) for a stern and the right half of the
    tower's plate for a bow, the plate's ribs and lip on it, hovering on a strut under the pod.
    mirror: the skiff coming in from the right (its sprites mirror the other's about x = 0.5)."""
    m = greens("skiff")
    axis_y, axis_z = 0.0, 9.6
    pod(m, axis_y, axis_z, x0=-22.2, x1=-1.6, claws=(-1,), prefix="pod")
    bow = bow_hull("bow", m, -6.0, 22.8, 0.4, 7.6, 10.2, axis_z)
    # The rib along the bow's top and the fluted band where the bow meets the pod.
    pts = [(11.2, y, sh.surface_z(bow, 11.2, y, axis_z) - 0.1) for y in [5.6 - i * 1.0 for i in range(12)]]
    w.ribbon("bow_rib", pts, 1.8, 0.8, m["light"])
    band = [(t, bow_radius(-3.2 + t)) for t in (0.0, 0.5, 2.7, 3.2)]
    w.fluted("band", [(t, r * 1.02) for t, r in band], m["mid"], (-3.2, 0.4, axis_z), (1, 0, 0), flutes=14, depth=0.05,
             segments=42, light=m["pale"], squash=0.68)
    # The strut under the pod, down to a foot.
    w.tube("strut", [(-8.5, -4.0, 5.0), (-8.5, -8.5, 3.0), (-8.5, -12.2, 1.4)], 1.1, m["green"], 10)
    w.sphere("strut_foot", (-8.5, -12.5, 1.2), (1.4, 1.4, 1.1), m["pale"], 10, 5)
    if mirror:
        w.bake()
        w.transform(w.meshes(), Matrix.Translation((1.0, 0, 0)) @ Matrix.Scale(-1, 4, (1, 0, 0)))


whole("skiff", (48, 28))(lambda: skiff_whole(False))
whole("skiff_l", (48, 28))(lambda: skiff_whole(True))


def skiff_piece(mirror, x0, x1):
    skiff_whole(mirror)
    w.bake()
    w.piece(w.meshes(), x0, x1, -14, 14)


model("green_skiff_rear", [(J, 169, True)])(lambda: skiff_piece(False, -24, 0))
model("green_skiff_nose", [(J, 207, True)])(lambda: skiff_piece(False, 0, 24))
model("green_skiff_l_nose", [(J, 245, True)])(lambda: skiff_piece(True, -24, 0))
model("green_skiff_l_rear", [(J, 283, True)])(lambda: skiff_piece(True, 0, 24))


# --- J 117: the green pod ship -----------------------------------------------------------------------

@model("green_pod_ship", [(J, 117, True)])
def green_pod_ship():
    """A wide green collar with a red crest along its top edge (two lights glowing in it), a green
    hull below it narrowing to a point down the screen with a ridge along its middle, and a red pod
    at each side of the hull, bulging lower down, with two lights glowing in it."""
    g = w.grid(art.J117, 24)
    m = greens("podship")
    rows = w.regions(g, lambda v, c, r: "h" if v >> 4 == 2 and r >= 2 else ".")

    def ridge(x, y, z):
        return z + 0.5 * math.exp(-((x - 0.5) / 0.9) ** 2) * min(1.0, max(0.0, z - 1.0) / 2.0)
    hull = w.part("hull", rows, "h", m["green"], sh.round_profile(0.75, max_height=5.4), bottom=0.3, z_fn=ridge,
                  spacing=0.5, epsilon=0.35, sigma=1.4)
    w.decimate(hull, 1800)
    k.smooth(hull, 50)
    w.paint_faces(hull, lambda c, n: m["deep"] if n.z < 0.25 else m["light"] if n.z > 0.85 and c.y > 7.0 else
                  m["mid"] if n.z > 0.9 else None)
    # The collar's rim along the top of the hull, the ridge down its middle.
    w.tube("collar_rim", [(-9.0, 8.4, 3.0), (-4.0, 7.2, 4.6), (0.5, 7.0, 5.0), (5.0, 7.2, 4.6), (10.0, 8.4, 3.0)], 0.7,
           m["mid"], 8)
    w.tube("ridge", [(0.5, 6.5, 5.6), (0.5, 0.0, 5.3), (0.5, -6.0, 4.2), (0.5, -10.5, 2.2)], 0.5, m["light"], 8)
    # The red crest along the top edge and its two lights.
    crest = w.sphere("crest", (0.5, 12.4, 2.6), (6.6, 2.0, 2.0), m["red_light"], 24, 10)
    w.paint_faces(crest, lambda c, n: m["red_dark"] if n.z < 0.1 else None)
    for x in (-2.0, 3.2):
        w.sphere(f"crest_light{x}", (x, 12.7, 4.1), (1.3, 0.8, 0.6), m["orange"], 12, 6)
    # The pods at the hull's sides, bulging lower down, two lights glowing in each.
    pod_profile = k.profile([(0.0, 0.01), (0.5, 1.3), (2.0, 1.85), (7.0, 2.2), (11.0, 2.35), (13.2, 1.9), (14.4, 0.01)],
                            0.6)
    for x in (-6.0, 7.0):
        w.lathe_axis(f"pod{x}", pod_profile, m["red_light"], (x, 6.8, 2.7), (0, -1, 0), 18)
        for y, size in ((3.4, 0.8), (-3.8, 1.15)):
            w.sphere(f"pod_light{x}{y}", (x + (0.4 if x < 0 else -0.4), y, 4.5), (size, size * 1.5, 0.55), m["orange"], 12, 6)


w.run()
