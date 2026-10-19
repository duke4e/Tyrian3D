"""The long grey ship of APPROACH, SAVARA IV and GREY MOON, drawn from three sprites of sheet 5 side by side:
115 (left), 117 (middle) and 119 (right) (models.cfg: model longship_left / longship_mid / longship_right ...
origin; sprite 5 115 longship_left yaw=0 and so on). The levels place them as one 72 x 28 picture: 739 (115)
at x, 740 (117) at x + 24 and 741 (119) at x + 48, on one row (APPROACH's events at 1100, 1800 and 2000,
SAVARA IV's from 700 to 3290: always so), and they move together.

The ship is built whole, its nose down the screen, and cut along the sprites' edges into the three pieces,
each moved so that its sprite's centre is its origin (base on the layer, as polish_redjet.py does): drawn at
their own places, they meet again. The normals of the cut pieces are taken from the whole ship, so the
shading runs on across the cuts as if nothing was cut.

As the sprites draw it (polish, 2026-10-19, after the 4x upscale): a long round beam across the screen (rows
10-16 of the 72 x 28 picture) carrying a gun pod at either end and, across its middle, the hull.
- The gun pods (columns 2-10 and their mirror images): light grey, bigger round than the beam, their outer
  ends blunt and rounded; a red fin fore and aft at their middles (columns 6-9, the red caps above and
  below them). A dark neck joins each pod to a dark housing with two red rings (columns 16 and 18); on the
  housing a broad fin fore and aft, grey on its outer side and red on its inner side, the red part longer
  (the grey knobs of columns 14-17 and the red caps of columns 18-21).
- The beam: grey, with two red bands along its front from the housings into the hull (the upper band from
  column 24, the lower from column 20, rows 13-16) and a grey tooth fore and aft at columns 25-28.
- The hull (columns 32-41, rows 0-26): a long body like a bomb, its blunt nose down the screen (row 26),
  widest over the beam (rows 8-23), narrowing up the screen to a waist (rows 5-6) and a tail bulb with
  red canards across it (row 3) and a small dorsal fin; a light spine down its back (columns 35-36), two
  dark vent slots on its front (columns 34 and 38, rows 18-22) and a dark nose cone (rows 23-26).

The picture is symmetric about its column 36's centre (x 0.5 here): the ship is built about u = 0 (u = x -
AXIS_X), its left parts mirrored. Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the
screen (picture row r is y = 13.5 - r), +Z towards the camera; the ship's origin is the middle sprite's
centre (picture pixel 36, 14), its base on z = 0.

Replaces wave3_l_parts.py's long ship (LONG, LONG_PIECES, build_longship, long_piece and its PIECES and
w.whole lines): remove them so that it doesn't overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <enemy_5.png or the sheets
directory> (the silhouettes of the whole and of the pieces), --preview <prefix> (each piece's top and 3/4
view, and the whole ship's).
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
from polish_redjet import (Curve, check_mask, cut, end_round, export, facet, move, preview, resample,  # noqa: E402
                           smoothstep, triangles)

AXIS_X = 0.5
# name, sprite, the box it covers in the ship's coordinates (x0, x1, y0, y1)
PIECES = [("longship_left", 115, (-36.0, -12.0, -14.0, 14.0)),
          ("longship_mid", 117, (-12.0, 12.0, -14.0, 14.0)),
          ("longship_right", 119, (12.0, 36.0, -14.0, 14.0))]
SPRITE_CELLS = {115: 0, 117: 24, 119: 48}  # left edges in the 72 x 28 picture

# --- The beam -----------------------------------------------------------------------------------------
# Its axis (y, z) and its stations along u from the left pod's tip to the middle: (u, half-width in plan,
# half-height); the right half is the mirror image. The pods' and housings' sections are a little boxy.
BEAM_Y, BEAM_Z = 0.4, 0.0
POD_TIP, POD_ROUND = -34.17, 2.5     # the pod's outer end (2/3 into column 2's outline), its rounding
POD = (4.95, 4.45)                   # the pod's half-width and half-height
NECK = (4.5, 4.05)
HOUSING = (4.85, 4.35)
SPAR = (4.1, 3.6)
POD_END, NECK_END, HOUSING_END, SPAR_START = -25.5, -21.3, -17.2, -16.2
RINGS = (-20.0, -18.0)               # the red rings (columns 16 and 18)


def beam_stations():
    """[(u, half-width, half-height, power, part)] from the left tip to the right tip."""
    left = []
    for i in range(1, 9):  # the pod's rounded end, from the tip in
        d = POD_ROUND * (1 - math.cos(0.5 * math.pi * i / 8))
        f = (1 - ((POD_ROUND - d) / POD_ROUND) ** 2.6) ** (1 / 2.6)
        left.append((POD_TIP + d, POD[0] * max(f, 0.05), POD[1] * max(f, 0.05), 2.6, "pod"))
    for u in (-30.0, -28.0, -26.6):
        left.append((u, POD[0], POD[1], 2.6, "pod"))
    left += [(POD_END - 0.25, POD[0] - 0.05, POD[1] - 0.05, 2.6, "pod"), (POD_END, POD[0] - 0.25, POD[1] - 0.25, 2.5, "pod"),
             (POD_END + 0.1, NECK[0], NECK[1], 2.4, "dark"), (-24.0, NECK[0], NECK[1], 2.4, "dark"),
             (-22.5, NECK[0], NECK[1], 2.4, "dark"), (NECK_END - 0.1, NECK[0], NECK[1], 2.4, "dark"),
             (NECK_END, HOUSING[0] - 0.15, HOUSING[1] - 0.15, 2.5, "dark"),
             (NECK_END + 0.25, HOUSING[0], HOUSING[1], 2.5, "dark"), (-19.0, HOUSING[0], HOUSING[1], 2.5, "dark"),
             (HOUSING_END - 0.2, HOUSING[0], HOUSING[1], 2.5, "dark"),
             (HOUSING_END, HOUSING[0] - 0.12, HOUSING[1] - 0.15, 2.4, "dark"),
             (HOUSING_END + 0.15, HOUSING[0] - 0.25, HOUSING[1] - 0.3, 2.3, "hull"),
             (SPAR_START - 0.35, SPAR[0] + 0.05, SPAR[1] + 0.06, 2.2, "hull"), (SPAR_START, SPAR[0], SPAR[1], 2.2, "hull")]
    for i in range(1, 4):
        u = SPAR_START + (0.0 - SPAR_START) * i / 4
        left.append((u, SPAR[0], SPAR[1], 2.2, "hull"))
    right = [(-u, w, h, p, part) for u, w, h, p, part in reversed(left)]
    return left + [(0.0, SPAR[0], SPAR[1], 2.2, "hull")] + right


def beam_section(u, hw, hh, power, n=36):
    """A cross-section of the beam at u (points in the YZ plane round the axis)."""
    out = []
    for j in range(n):
        a = 2 * math.pi * j / n
        c, s = math.cos(a), math.sin(a)
        out.append(Vector((u, BEAM_Y + math.copysign(abs(c) ** (2 / power), c) * hw,
                           BEAM_Z + math.copysign(abs(s) ** (2 / power), s) * hh)))
    return out


def beam_radius(u):
    """The beam's (half-width, half-height) at u (its plain sections, for the parts lying on it)."""
    au = abs(u)
    if au > -POD_END:
        return POD
    if au > -NECK_END:
        return NECK
    if au > -HOUSING_END:
        return HOUSING
    return SPAR


def beam(m):
    stations = beam_stations()
    rings = [beam_section(u, w, h, p) for u, w, h, p, _ in stations]
    obj = k.loft("beam", rings, None, start_point=(POD_TIP - 0.02, BEAM_Y, BEAM_Z),
                 end_point=(-POD_TIP + 0.02, BEAM_Y, BEAM_Z))
    names = ["hull", "pod", "dark"]
    for name in names:
        obj.data.materials.append(m[name])
    n = len(rings[0])
    for poly in obj.data.polygons:
        i = poly.index // n
        if i < len(stations) - 1:
            part = stations[i][4] if stations[i][4] == stations[i + 1][4] else stations[i + 1][4] \
                if abs(stations[i + 1][0]) < abs(stations[i][0]) else stations[i][4]
            poly.material_index = names.index(part)
        else:
            poly.material_index = names.index("pod")  # the end fans: the pods' tips
    k.smooth(obj, 38)
    return obj


def lathe_x(name, profile, mat, segments=36, power=2.4):
    """A ring round the beam: profile [(u, half-width, half-height)] along u."""
    rings = []
    for u, hw, hh in profile:
        rings.append(beam_section(u, hw, hh, power, segments))
    return k.smooth(k.loft(name, rings, mat, cap_start=False, cap_end=False), 50)


def rings(m):
    """The red rings round each housing (columns 16 and 18), standing proud of it."""
    out = []
    for side in (-1, 1):
        for i, u0 in enumerate(RINGS):
            u = side * u0
            hw, hh = HOUSING
            prof = [(u - 0.45, hw - 0.05, hh - 0.05), (u - 0.42, hw + 0.2, hh + 0.2), (u - 0.25, hw + 0.3, hh + 0.3),
                    (u + 0.25, hw + 0.3, hh + 0.3), (u + 0.42, hw + 0.2, hh + 0.2), (u + 0.45, hw - 0.05, hh - 0.05)]
            out.append(lathe_x(f"ring{side}{i}", prof, m["red"], power=2.5))
    # Thin dark seams round each pod: where its rounded end begins and near its inner end.
    for side in (-1, 1):
        for i, u0 in enumerate((POD_TIP + POD_ROUND + 0.15, POD_END - 0.9)):
            u = side * u0
            hw, hh = POD
            prof = [(u - 0.14, hw - 0.1, hh - 0.1), (u - 0.1, hw + 0.04, hh + 0.04), (u + 0.1, hw + 0.04, hh + 0.04),
                    (u + 0.14, hw - 0.1, hh - 0.1)]
            out.append(lathe_x(f"pod_seam{side}{i}", prof, m["seam"], power=2.6))
    return out


def band(name, u0, u1, a0, a1, mat, lift=0.13, sink=0.3, steps=9, stations=8):
    """A band lying on the spar along u from u0 to u1, round its section from angle a0 to a1 (degrees from
    its top towards the front, down the screen): a thick arc lofted along u, standing `lift` proud, its
    ends bevelled."""
    hw, hh = SPAR
    rings_ = []
    us = [u0, u0 + 0.12] + [u0 + (u1 - u0) * i / stations for i in range(1, stations)] + [u1 - 0.12, u1]
    for i, u in enumerate(us):
        f = 0.45 if i in (0, len(us) - 1) else 1.0
        ring = []
        for j in range(steps + 1):  # the outer face, then back along the inner one
            a = math.radians(a0 + (a1 - a0) * j / steps)
            ring.append(Vector((u, BEAM_Y - (hw + lift * f) * math.sin(a), BEAM_Z + (hh + lift * f) * math.cos(a))))
        for j in range(steps, -1, -1):
            a = math.radians(a0 + (a1 - a0) * j / steps)
            ring.append(Vector((u, BEAM_Y - (hw - sink) * math.sin(a), BEAM_Z + (hh - sink) * math.cos(a))))
        rings_.append(ring)
    obj = k.loft(name, rings_, mat)
    return k.smooth(obj, 50)


def bands(m):
    """The two red bands along the beam's front (rows 13-14 and 15-16 as the sprite sees them; lying a
    little further round towards the front, as the game's camera, slanted from the bottom of the screen,
    sees the beam): the upper from column 24 (x -11.8), the lower from column 20."""
    return [band("band_upper", -12.3, 12.3, 6.0, 36.0, m["red_light"]),
            band("band_lower", -16.4, 16.4, 39.0, 74.0, m["red"])]


FIN_Z, FIN_THICK = -0.2, 1.35  # the fins' undersides and thickness (they stand out of the beam's sides)


def blade(name, u0, u1, y_root, y_tip, mat, taper=0.8, corner=0.75, sweep=0.0):
    """A fin lying flat fore or aft of the beam: a plate whose root (across u from u0 to u1) lies inside the
    beam at y_root and whose tip, `taper` as wide and shifted `sweep` along u, lies at y_tip; its tip's
    corners rounded (corner), its top edge rounded (polish_redjet.facet)."""
    w = u1 - u0
    t0, t1 = u0 + 0.5 * (1 - taper) * w + sweep, u1 - 0.5 * (1 - taper) * w + sweep
    sign = 1 if y_tip > y_root else -1
    # The tip's corners rounded on quarter circles; the root's corners square (inside the beam).
    r = min(corner, 0.45 * (t1 - t0), 0.45 * abs(y_tip - y_root))
    tip = []
    for cx, a0 in ((t1 - r, 0.0), (t0 + r, 90.0)):
        for i in range(6):
            a = math.radians(a0 + 90.0 * i / 5)
            tip.append((cx + r * math.cos(a), y_tip - sign * r + sign * r * math.sin(a)))
    outline = [(u0, y_root), (u1, y_root)] + tip
    # Counter-clockwise seen from above.
    area = sum(outline[i][0] * outline[(i + 1) % len(outline)][1] - outline[(i + 1) % len(outline)][0] * outline[i][1]
               for i in range(len(outline)))
    if area < 0:
        outline = outline[::-1]
    outline = resample(outline, 0.32)
    obj = facet(name, outline, lambda x, y: BEAM_Z + FIN_Z, FIN_THICK, mat, rim=0.42, steps=3, dome=0.0,
                dome_rings=1, sink=0.0)
    return obj


# The fins fore and aft of the beam (left side; mirrored): (name, u0, u1, the rear tip's y, the front
# tip's y, material, taper, sweep). Tips 2/3 into the sprite's outline pixels.
FINS = [("pod_fin", -31.0, -25.95, 6.75, -7.75, "red", 0.86, 0.0),         # the red caps of columns 6-9
        ("housing_fin", -22.65, -18.5, 7.75, -6.75, "knob", 0.86, 0.2),    # the grey knobs of columns 14-17
        ("housing_tip", -18.3, -14.3, 8.75, -6.75, "red", 0.86, 0.0),      # the red caps of columns 18-21
        ("tooth", -11.15, -7.85, 6.75, -6.75, "knob", 0.8, 0.0)]           # the grey teeth of columns 25-28


def fins(m):
    out = []
    for name, u0, u1, rear, front, mat, taper, sweep in FINS:
        hw, _ = beam_radius(0.5 * (u0 + u1))
        for tag, tip in (("r", rear), ("f", front)):
            root = BEAM_Y + (hw - 1.2) * (1 if tip > BEAM_Y else -1)
            b = blade(f"{name}_{tag}_l", u0, u1, root, tip, m[mat], taper=taper, sweep=sweep)
            mirror = k.mirror_x(b, f"{name}_{tag}_r")
            mirror.data.name = mirror.name
            out += [b, mirror]
    return out


# --- The hull -----------------------------------------------------------------------------------------
# Along y (2/3 into the sprite's outline): its half-width in plan, its top's height above the axis and
# its underside's depth below it: the tail tip (row 0), the tail bulb (rows 1-4, the canards across it at
# row 3), the waist (rows 5-6), the body (rows 8-23) and the nose (rows 23-26), whose height falls away
# faster than its width (an ogive, as a bomb's nose).
HULL_TAIL, HULL_NOSE = 13.67, -12.67
HULL = Curve([(-12.67, 0.0, 0.0, 0.0), (-12.45, 1.05, 0.55, 0.45), (-12.0, 1.75, 0.95, 0.75), (-11.4, 2.3, 1.4, 1.05),
              (-10.6, 3.05, 1.95, 1.4), (-9.8, 3.75, 2.5, 1.75), (-9.0, 4.1, 2.95, 2.05), (-8.0, 4.17, 3.4, 2.35),
              (-6.5, 4.17, 3.95, 2.7), (-4.5, 4.17, 4.4, 2.95), (-2.0, 4.17, 4.65, 3.1), (4.6, 4.17, 4.65, 3.1),
              (5.4, 3.95, 4.45, 3.0),
              (6.2, 3.35, 4.0, 2.75), (6.9, 2.6, 3.4, 2.35), (7.6, 2.0, 2.85, 1.95), (8.3, 1.8, 2.55, 1.8),
              (9.0, 2.25, 2.55, 1.8), (9.6, 2.55, 2.55, 1.8), (10.4, 2.35, 2.45, 1.7), (11.4, 2.15, 2.25, 1.6),
              (12.4, 1.95, 1.95, 1.4), (13.0, 1.6, 1.6, 1.15), (13.4, 1.05, 1.1, 0.8), (13.67, 0.0, 0.0, 0.0)])
HULL_Z = 1.0            # the axis' height (above the beam's) ...
NOSE_DROOP = 0.7        # ... drooping this much towards the nose
NOSE_CONE = -9.4        # the nose cone below this


def hull_z(y):
    return HULL_Z - NOSE_DROOP * smoothstep(-5.0, HULL_NOSE, y)


def hull_section(y):
    """The hull's half-width, top height and underside depth at y."""
    hw, top, bottom = HULL(y)
    return max(hw, 0.0), max(top, 0.0), max(bottom, 0.0)


def hull_top(u, y):
    """The hull's top surface at (u, y)."""
    hw, top, _ = hull_section(y)
    if hw <= 0.05 or abs(u) >= hw:
        return hull_z(y)
    return hull_z(y) + top * (1 - (abs(u) / hw) ** 2.2) ** (1 / 2.2)


def hull(m):
    ys = []
    for y0, y1, step in ((-12.6, -9.0, 0.3), (-9.0, 4.6, 0.7), (4.6, 9.8, 0.35), (9.8, 13.6, 0.3)):
        count = max(1, int(round((y1 - y0) / step)))
        ys += [y0 + (y1 - y0) * i / count for i in range(count)]
    ys.append(13.6)
    rings_ = []
    for y in ys:
        hw, top, bottom = hull_section(y)
        rings_.append(k.ring(y, max(hw, 0.05), 1.0, 32, z=hull_z(y), top=max(top, 0.05), bottom=max(bottom, 0.05),
                             power=2.2))
    body = k.loft("hull", rings_, None, start_point=(0, HULL_NOSE, hull_z(HULL_NOSE) - 0.1),
                  end_point=(0, HULL_TAIL, HULL_Z + 0.2))
    body.data.materials.append(m["body"])
    body.data.materials.append(m["nose"])
    for poly in body.data.polygons:
        poly.material_index = 1 if poly.center.y < NOSE_CONE else 0
    k.smooth(body, 40)
    # A seam round the hull where the body flares from the waist.
    out = [body]
    for i, y in enumerate((5.55,)):
        hw, top, bottom = hull_section(y)
        prof = []
        for dy, grow in ((-0.18, -0.08), (-0.12, 0.07), (0.12, 0.07), (0.18, -0.08)):
            prof.append(k.ring(y + dy, hw + grow, 1.0, 32, z=hull_z(y), top=top + grow, bottom=bottom + grow, power=2.2))
        out.append(k.smooth(k.loft(f"hull_seam{i}", prof, m["seam"], cap_start=False, cap_end=False), 50))
    return out


def spine(m):
    """The light ridge down the hull's back (columns 35-36, rows 6-23)."""
    y0, y1 = -10.2, 7.4
    rings_ = []
    for i in range(36):
        y = y0 + (y1 - y0) * i / 35
        f = end_round(y, y0, y1, 1.6, 1.4)
        rings_.append(k.ring(y, 0.95 * max(f, 0.1), 1.0, 12, z=hull_top(0.0, y) - 0.3, top=0.3 + 0.45 * f,
                             bottom=0.4, power=2.4))
    return k.smooth(k.loft("spine", rings_, m["spine"]), 55)


def pad(name, outline, mat, lift=0.06, sink=0.5, dome=-0.12):
    """A thin plate lying in the hull's top (outline counter-clockwise seen from above): a recessed slot
    when dome is negative."""
    n = len(outline)
    cx, cy = sum(p[0] for p in outline) / n, sum(p[1] for p in outline) / n
    rings_ = []
    for f, dz in ((1.0, -sink), (1.0, lift - 0.04), (0.9, lift), (0.45, lift + dome)):
        rings_.append([Vector((cx + (x - cx) * f, cy + (y - cy) * f, hull_top(cx + (x - cx) * f, cy + (y - cy) * f) + dz))
                       for x, y in outline])
    verts = [v for r in rings_ for v in r]
    faces = []
    for r in range(len(rings_) - 1):
        for i in range(n):
            j = (i + 1) % n
            faces.append((r * n + i, r * n + j, (r + 1) * n + j, (r + 1) * n + i))
    verts.append(Vector((cx, cy, hull_top(cx, cy) + lift + dome)))
    top = (len(rings_) - 1) * n
    faces += [(top + i, top + (i + 1) % n, len(verts) - 1) for i in range(n)]
    verts.append(Vector((cx, cy, hull_top(cx, cy) - sink)))
    faces += [((i + 1) % n, i, len(verts) - 1) for i in range(n)]
    obj = k.mesh_object(name, verts, faces, mat)
    k.recalc_normals(obj)
    return k.smooth(obj, 50)


def slot_outline(u, y0, y1, half):
    """A stadium along y round the segment (u, y0)-(u, y1), counter-clockwise."""
    out = []
    for i in range(8):
        a = math.pi * i / 7
        out.append((u + half * math.cos(a), y1 + half * math.sin(a)))
    for i in range(8):
        a = math.pi + math.pi * i / 7
        out.append((u + half * math.cos(a), y0 + half * math.sin(a)))
    return out


def vents(m):
    """Two dark slots on the hull's front either side of the spine (columns 34 and 38, rows 18-22)."""
    return [pad(f"vent{side}", slot_outline(side * 2.0, -8.6, -4.4, 0.42), m["seam"], lift=0.12, dome=-0.02)
            for side in (-1, 1)]


def tail(m):
    """The tail: red canards across the tail bulb (row 3) and a small dorsal fin on it (rows 0-4)."""
    out = []
    # The canards: thin rounded wings from inside the bulb out to 2/3 into columns 7 and 17's outlines.
    span = [0.0, 1.2, 2.2, 3.0, 3.6, 4.1, 4.5, 4.8, 5.0, 5.1]
    rings_ = []
    for s in span:
        f = end_round(s, -1.0, 5.1, 0.0, 0.7)
        chord = 2.2 * (1 - 0.3 * s / 5.1) * max(f, 0.12)
        yc = 10.6 + 0.05 * s
        th = 0.3 * max(f, 0.3)
        zc = HULL_Z + 0.9 + 0.08 * s
        ring = []
        for j in range(16):
            a = 2 * math.pi * j / 16
            c, sn = math.cos(a), math.sin(a)
            ring.append(Vector((-s, yc + 0.5 * chord * math.copysign(abs(c) ** 0.8, c), zc + th * sn * (1.0 if sn > 0 else 0.6))))
        rings_.append(ring)
    left = k.loft("canard_l", rings_, m["red"], end_point=(-5.17, 10.6 + 0.05 * 5.1, HULL_Z + 0.9 + 0.41))
    k.smooth(left, 50)
    right = k.mirror_x(left, "canard_r")
    right.data.name = "canard_r"
    out += [left, right]
    # The dorsal fin, low, from the tail tip down to the waist.
    y0, y1 = 8.6, 13.3
    rings_ = []
    for i in range(14):
        y = y0 + (y1 - y0) * i / 13
        f = end_round(y, y0, y1, 1.2, 0.7)
        base = hull_top(0.0, y) - 0.4
        height = 0.4 + 1.0 * f
        ring = []
        for j in range(12):
            a = 2 * math.pi * j / 12
            c, sn = math.cos(a), math.sin(a)
            ring.append(Vector((0.32 * max(f, 0.3) * c, y, base + height * (0.5 + 0.5 * sn))))
        rings_.append(ring)
    out.append(k.smooth(k.loft("dorsal", rings_, m["spine"]), 50))
    return out


# --- Checks and build --------------------------------------------------------------------------------

def whole_mask(sheet):
    """The three sprites' silhouettes placed as the levels place them: 72 x 28."""
    mask = [[False] * 72 for _ in range(28)]
    for sprite, cx in SPRITE_CELLS.items():
        part = k.sprite_mask(sheet, sprite)
        for y in range(28):
            for x in range(24):
                if part[y][x]:
                    mask[y][cx + x] = True
    return mask


def materials():
    return {
        "hull": k.material("longship_hull", palette=6, metallic=0.35, roughness=0.36),
        "body": k.material("longship_body", palette=7, metallic=0.3, roughness=0.34),
        "pod": k.material("longship_pod", palette=9, metallic=0.35, roughness=0.3),
        "dark": k.material("longship_dark", palette=5, metallic=0.35, roughness=0.42),
        "nose": k.material("longship_nose", palette=6, metallic=0.3, roughness=0.32),
        "knob": k.material("longship_knob", palette=6, metallic=0.35, roughness=0.4),
        "red": k.material("longship_red", palette=0x47, metallic=0.3, roughness=0.36),
        "red_light": k.material("longship_red_light", palette=0x48, metallic=0.3, roughness=0.34),
        "spine": k.material("longship_spine", palette=10, metallic=0.4, roughness=0.3),
        "seam": k.material("longship_seam", palette=2, metallic=0.3, roughness=0.55),
    }


def build():
    k.reset()
    options = k.args()
    m = materials()
    beam(m)
    rings(m)
    bands(m)
    fins(m)
    hull(m)
    spine(m)
    vents(m)
    tail(m)
    whole = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    low = min((o.matrix_world @ v.co).z for o in whole for v in o.data.vertices)
    for obj in whole:  # its base on z = 0, its axis on the sprites' column 36
        obj.data.transform(Matrix.Translation((AXIS_X, 0, -low)))
    high = max((o.matrix_world @ v.co).z for o in whole for v in o.data.vertices)
    used = {mat.name for o in whole for mat in o.data.materials}
    print("whole ship: %d triangles, %d objects, z 0 to %.2f, %d materials: %s" % (
        triangles(whole), len(whole), high, len(used), ", ".join(sorted(used))))

    sheet = options.get("check")
    if sheet and os.path.isdir(sheet):
        sheet = os.path.join(sheet, "enemy_5.png")
    if sheet:
        check_mask(whole_mask(sheet), "whole (115 + 117 + 119)", whole)
    bpy.context.scene.view_settings.view_transform = "Standard"
    if "preview" in options:
        preview(options["preview"] + "whole", whole, size=(72, 28), scale=8, distance=2.2)

    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    for name, sprite, box in PIECES:
        pieces = [p for p in (cut(src, box, m["seam"]) for src in whole) if p is not None]
        move(pieces, -(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2)
        mats = {mat.name for o in pieces for mat in o.data.materials}
        print("== %s (5 %d): %d triangles, %d objects, %d materials" % (name, sprite, triangles(pieces), len(pieces),
                                                                       len(mats)))
        if sheet:
            check_mask(k.sprite_mask(sheet, sprite), "%s (5 %d)" % (name, sprite), pieces)
        path = os.path.join(outdir, name + ".glb")
        export(pieces, path)
        print("%s: %.1f KB" % (path, os.path.getsize(path) / 1024))
        if "preview" in options:
            preview(options["preview"] + name, pieces)
        for obj in pieces:
            bpy.data.objects.remove(obj)


if __name__ == "__main__":
    build()
