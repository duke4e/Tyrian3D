"""UNDERDELI's blue cruiser flying sideways (sheet ^, x5e in models.cfg), polished (2026-10-21; it replaces wave3_i.py's
cruiser_whole(), ellipsoids and slabs). Three 2x2 sprites, each an enemy of its own, make one 60 x 28 picture: 198,
200 and 201 its parts from left to right (201 overlaps 200 by 12 pixels, where their pixels are the same), and 206,
204 and 203 the same pixels mirrored (the ship facing the other way). models.cfg: model cruiser_rear / cruiser_mid /
cruiser_nose / cruiser_rear_l / cruiser_mid_l / cruiser_nose_l ... origin; sprite x5e 198 cruiser_rear yaw=0 (200
cruiser_mid, 201 cruiser_nose, 206 cruiser_rear_l, 204 cruiser_mid_l, 203 cruiser_nose_l), as before.

The levels (UNDERDELI only, every wave; no episode 6 level takes them): the left-facing ship from enemies 49, 50, 51
(203 at x 0, 204 at x 12, 206 at x 36: the sheet's own layout, mirrored), the right-facing one from 55, 56, 57 (198
at x 220, 200 at x 242, 201 at x 254: 201 over 200 as in the sheet, but 198 two pixels closer to 200 than in the
sheet, so the 2D game draws 200's first two columns over 198's last two). They rise from the bottom of the screen
(events 18 and 23, vy -5), the left ship along the left edge, the right one along the right edge; each piece is a
launcher (elaunchtype 1052-1054, 1058-1060: launch special 1, "in line with the player"), and when the ship comes
level with the player every piece launches its twin (enemies 52-54, 58-60: the same sprite, one frame) at its own
place and vanishes (its second frame is 999). The twins dash across the screen, accelerating (xcaccel 4: the left
ship to the right, the right ship to the left). Both ships fly with the round segmented end first (models.cfg's
"rear", 198 / 206) and their swept-back wings and fins (the "nose", 201 / 203) behind.

As the sprites and their 4x upscales draw it (the right-facing ship; the picture's columns c 0-59 and rows r 0-27; the
ship is symmetric about the middle of row 13, the light from the top of the screen):
- The head (columns 1-25): a segmented prow of glossy blue bulbs along the axis: a big round one at the front
  (columns 1-8), a narrow neck (9-12), a second bulb (13-19) and a third (20-25) going into the hull; dark creases
  between them. On each flank two curved armour scales (columns 6-15 and 16-23, rows 5-10 and 16-21) sloping down
  outwards (lit above the axis, dark below it), studs on their outer edges (columns 12-14, 16-18) and a pale
  fairing before the wing's root (20-22).
- The hull (columns 24-50): a long blue cylinder lit along its top, its front a cone over the third bulb (the
  sprite's chevron) with a raised ring behind it; from a seam at column 40 its tail section, darker, tapers to a
  blunt end (column 50), a groove along its top holding a pale rod that runs out past the end through a dark sleeve
  (columns 42-53: a spine, rows 12-13).
- The wings (columns 23-40, rows 1-6 and 20-25): broad swept-back plates from the hull's flanks, a raised pale rim
  round their leading and outer edges and a recessed panel in them (blue above the axis, dark teal below it, the
  sprite's ramp 13), drooping a little (anhedral 8 degrees) so the game's sun lights the upper one and leaves the
  lower one darker, as the sprite draws them.
- The tail fins (columns 38-54, rows 1-9 and 17-25): two swept fins at the hull's end, pale blue above, teal below,
  their tips reaching out behind the hull.

Built as bodies of revolution (the head's bulbs: one lathe whose radius is the largest of the bulbs', creased where
they meet; the hull: a lathe, its groove cut by an exact boolean; the ring, the rod and its sleeve), the scales as
superellipsoid plates bent round the axis (their inner edges straight along the bulbs, their outer edges curved), the
studs and the fairing as ellipsoids, the wings and fins as plates (prisms, the panels' recesses cut by booleans,
bevelled). Colours are the sprites' palette indices (ramp 3's blues, ramp 13's teals): the round parts in bands of
how much they face the light from the top of the screen and above (polish_orb_red.band_split; the band light has no x
part, so the mirrored pieces are painted alike): the hull and scales 0x34 0x36 0x37 0x39, the bulbs 0x35 0x37 0x39
0x3b, glossy, with a little emission in their own blues (0.12-0.14: round, they would read near black from the
slanted camera); the plates by face: rims, the upper fin and the rod 0x3d, bevels 0x39, the panels 0x3a (upper wing)
and 0xd4 (lower wing), the lower fin 0xd8, undersides, the groove and the sleeve 0x33, cut caps 0x30. The whole ship
is then cut along the sprites' edges (polish_savara_boss.cut: the pieces keep the whole's shading across the cuts,
their cuts capped; cuts across x stand edge-on to the game's camera) into 198 (columns 0-23), 200 (24-47) and 201
(36-59, which keeps all it shows, so the overlap is drawn by both: the same faces where both are), each moved so that
its sprite's centre is its origin; 206, 204 and 203 are those pieces mirrored (their custom normals mirrored with
them). The right ship's 198 sits 2 pixels into 200: what it has in its last two columns (the third bulb, the
fairing's end) lies inside 200's cone and wing roots. Every mesh is triangulated before the export
(polish_k_pod.triangulate), each piece's parts joined into one mesh.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up (towards the camera) from the
layer; the whole's origin is the picture's middle (pixel edge 30, 14): column c's left edge is x = c - 30, row r's
top edge y = 14 - r. The ship is built about Y = 0 (the middle of row 13) and moved there (AXIS_Y); its axis lies
ZC over the layer.

Replaces wave3_i.py's cruiser: cruiser_whole(), the w.WHOLES["cruiser"] entry and the loop registering cruiser_rear
... cruiser_nose_l, their lines in its docstring ("cruiser," in its --whole usage line), and wave3_i_art.py's SHIP
(only cruiser_whole() reads it), so that they don't overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the whole
and of each piece against enemy_x5e.png), --preview <prefix> (the whole's and each piece's top and 3/4 views),
--only <model,...>, --whole <file.glb> (the uncut ship as well, for looking at), --stats 1.
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
import polish_deli_boss as db  # noqa: E402  (join, drop_unused)
from polish_k_pod import triangulate  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_savara_boss import cut  # noqa: E402  (polish_arch.cut keeping the faces' winding)

AXIS_Y = 0.5                # the middle of row 13, where the built ship's Y = 0 goes
ZC = 6.0                    # the axis' height over the layer
SQ = 0.86                   # the hull's cross-section: its height over its width
BAKE = Vector((0.0, 0.5, 0.866))    # the light the colours are banded by: from the top of the screen and above

# The pieces: model, sprite, its columns in the whole (x0, x1); the mirrored twins of the left-facing ship.
PIECES = [("cruiser_rear", 198, (-30.0, -6.0)), ("cruiser_mid", 200, (-6.0, 18.0)), ("cruiser_nose", 201, (6.0, 30.0))]
TWINS = {"cruiser_rear": ("cruiser_rear_l", 206), "cruiser_mid": ("cruiser_mid_l", 204),
         "cruiser_nose": ("cruiser_nose_l", 203)}
# The sprites' top left corners in the 60 x 28 picture (for the whole's silhouette).
CELLS = {198: 0, 200: 24, 201: 36}


# --- Materials ---------------------------------------------------------------------------------------------------

def materials():
    pal = k.level_palette()

    def mat(name, index, metallic=0.45, roughness=0.32, glow=0.0):
        kw = dict(emission=pal[index], emission_strength=glow) if glow else {}
        return k.material("cruiser_" + name, palette=index, metallic=metallic, roughness=roughness, **kw)
    return {
        "black": mat("black", 0x30, 0.3, 0.55),
        "deep": mat("deep", 0x33, 0.4, 0.4),
        "hull1": mat("hull1", 0x34),
        "hull2": mat("hull2", 0x36),
        "hull3": mat("hull3", 0x37),
        "hull4": mat("hull4", 0x39, 0.45, 0.28),
        "bulb1": mat("bulb1", 0x35, 0.5, 0.18, 0.12),
        "bulb2": mat("bulb2", 0x37, 0.5, 0.16, 0.12),
        "bulb3": mat("bulb3", 0x39, 0.5, 0.14, 0.12),
        "bulb4": mat("bulb4", 0x3b, 0.5, 0.12, 0.14),
        "rim": mat("rim", 0x3d, 0.4, 0.3),
        "panel": mat("panel", 0x3a, 0.25, 0.5),
        "panel_s": mat("panel_s", 0xd4, 0.25, 0.5),
        "fin_s": mat("fin_s", 0xd8, 0.4, 0.3),
    }


def bake_bands(obj, bands, angle=40.0):
    """Gives the faces of obj the material of their band of how much they face BAKE (bands: [(lowest value,
    material)], ascending), the bands' borders smooth contours (band_split)."""
    values = [v.normal.dot(BAKE) for v in obj.data.vertices]
    band_split(obj, values, bands)
    return k.smooth(obj, angle)


def hull_bands(m):
    return [(-9.0, m["hull1"]), (0.1, m["hull2"]), (0.55, m["hull3"]), (0.86, m["hull4"])]


def bulb_bands(m):
    return [(-9.0, m["bulb1"]), (0.2, m["bulb2"]), (0.62, m["bulb3"]), (0.9, m["bulb4"])]


# --- Shapes ------------------------------------------------------------------------------------------------------

def lathe_x(name, profile, mat, segments=40, squash=SQ, power=2.0, y0=0.0, z0=ZC):
    """A body of revolution about the line (y0, z0) along X: profile [(x, r), ...] from its front (smallest x) back;
    its ends close to the axis at the first and last x. Cross-sections: superellipses (power) of half-width r and
    half-height r * squash."""
    unit = [mk.superellipse_point(2 * math.pi * j / segments, power) for j in range(segments)]
    rings = [[Vector((x, y0 + r * u, z0 + r * squash * v)) for u, v in unit] for x, r in profile if r > 1e-4]
    return k.loft(name, rings, mat, start_point=(profile[0][0], y0, z0), end_point=(profile[-1][0], y0, z0))


def pillow(name, centre, radii, tilt, mat, power=2.6, lift=2.6, segments=36, rings=14):
    """A scale: a superellipsoid of half-lengths radii (a along x, b across, c thick), its plan a superellipse of
    power, its section fuller (lift), turned about its x axis by tilt (radians, positive raises its +y side) and
    moved to centre."""
    a, b, c = radii
    unit = [mk.superellipse_point(2 * math.pi * j / segments, power) for j in range(segments)]
    loops = []
    for i in range(1, rings):
        t = -math.pi / 2 + math.pi * i / rings
        s = math.copysign(abs(math.sin(t)) ** (2 / lift), math.sin(t))
        w = abs(math.cos(t)) ** (2 / lift)
        loops.append([Vector((a * w * u, b * w * v, c * s)) for u, v in unit])
    obj = k.loft(name, loops, mat, start_point=(0, 0, -c), end_point=(0, 0, c))
    obj.data.transform(Matrix.Translation(centre) @ Matrix.Rotation(tilt, 4, "X"))
    k.recalc_normals(obj)
    return obj


def mirror_y(obj, name):
    """A copy of obj mirrored across Y = 0 (the ship's axis)."""
    copy = obj.copy()
    copy.data = obj.data.copy()
    copy.name = name
    copy.data.name = name
    bpy.context.scene.collection.objects.link(copy)
    copy.data.transform(Matrix.Scale(-1, 4, (0, 1, 0)))
    copy.data.flip_normals()
    copy.data.update()
    return copy


# --- The head: the bulbs, the scales and their studs -----------------------------------------------------------------
# Each bulb: (middle x, half-length in front, behind, radius, superellipse powers of its profile in front, behind):
# the big front bulb, a neck, the second bulb and the third.
BULBS = [(-25.15, 3.95, 4.7, 4.65, 2.2, 2.7), (-19.15, 2.45, 2.45, 3.25, 3.0, 3.0), (-13.75, 2.95, 2.95, 4.0, 2.3, 2.3),
         (-7.6, 3.4, 3.4, 4.2, 2.3, 2.3)]
HEAD_SQ = 0.95
# The scales on the upper flank (the lower ones mirrored): bent round the line along X through SCALE_ARC (y, z over
# the axis) at a radius, from the angle phi0 to phi1 (degrees from straight up towards +y); (middle x, half-length,
# radius, phi0, phi1, thickness, how much narrower in front than behind).
SCALE_ARC = (0.9, -4.3)
SCALES = [(-18.75, 5.05, 7.4, 16.0, 59.0, 1.15, 0.3), (-10.95, 3.75, 7.4, 16.0, 62.0, 1.15, 0.1)]
# The studs on the scales' outer edges: (x, y, half-length); and the fairing in front of the wing's root (centre,
# radii).
STUDS = [(-16.3, 7.5, 1.5), (-12.5, 7.55, 1.5)]
FAIRING = ((-7.9, 7.75, ZC + 0.9), (2.1, 1.55, 1.0))


def bulb_profile(bulb, x):
    xc, hf, hb, r, pf, pb = bulb
    h, p = (hf, pf) if x < xc else (hb, pb)
    t = abs(x - xc) / h
    return r * (1 - t ** p) ** (1 / p) if t < 1.0 else 0.0


def bulb_radius(x):
    return max(bulb_profile(b, x) for b in BULBS)


def head_stations():
    """The x of the bulbs' rings: closer where their outline turns (the ends and the creases)."""
    front, back = BULBS[0][0] - BULBS[0][1], BULBS[-1][0] + BULBS[-1][2]
    xs = []
    x = front + 0.03
    while x < back - 0.03:
        xs.append(x)
        h = 0.02
        slope = abs(bulb_radius(x + h) - bulb_radius(x - h)) / (2 * h)
        x += max(0.14, min(0.7, 0.7 / (1.0 + 0.9 * slope)))
    creases = []
    for a, b in zip(BULBS, BULBS[1:]):
        lo, hi = b[0] - b[1], a[0] + a[2]      # where the two overlap: the crease is where their radii are equal
        for _ in range(50):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if bulb_profile(a, mid) > bulb_profile(b, mid) else (lo, mid)
        creases.append((lo + hi) / 2)
    xs = sorted([x for x in xs if all(abs(x - c) > 0.08 for c in creases)] + creases)
    return front, back, xs


def shell_plate(name, xc, a, radius, phi0, phi1, thick, skew, mat, power=2.0, lift=2.2, segments=32, rings=10):
    """A scale bent round the line along X through SCALE_ARC: 2a long, its inner edge a straight line along X at the
    angle phi0 (from straight up towards +y) at radius (its underside), its outer edge reaching phi1 at its middle
    and coming back to the inner edge at its ends (a superellipse of power), the back further out than the front by
    skew, thick at its middle and domed (lift)."""
    p0, p1 = math.radians(phi0), math.radians(phi1)
    b = 1.0
    obj = pillow(name, (0.0, 0.0, 0.0), (a, b, thick / 2), 0.0, mat, power, lift, segments, rings)
    yc, zc = SCALE_ARC
    for v in obj.data.vertices:
        X, Y, Z = v.co
        w = (1.0 - min(1.0, abs(X / a)) ** power) ** (1.0 / power)     # the outermost ring's half-width here
        f = (Y + b * w) / (2 * b) * (1.0 + skew * X / a)               # 0 on the inner edge, w at the outer one
        phi = p0 + (p1 - p0) * f
        r = radius + thick / 2 + Z
        v.co = Vector((xc + X, yc + r * math.sin(phi), ZC + zc + r * math.cos(phi)))
    obj.data.update()
    k.recalc_normals(obj)
    return obj


def head(m):
    front, back, xs = head_stations()
    prof = [(front, 0.0)] + [(x, bulb_radius(x)) for x in xs] + [(back, 0.0)]
    bulbs = lathe_x("bulbs", prof, m["bulb2"], segments=30, squash=HEAD_SQ)
    bake_bands(bulbs, bulb_bands(m), 38.0)
    parts = [bulbs]
    for i, (xc, a, radius, phi0, phi1, thick, skew) in enumerate(SCALES):
        scale = shell_plate("scale%d" % i, xc, a, radius, phi0, phi1, thick, skew, m["hull3"], segments=28, rings=9)
        bake_bands(scale, hull_bands(m), 50.0)
        parts.append(scale)
    yc, zc = SCALE_ARC
    for i, (x, y, r) in enumerate(STUDS):
        phi = math.asin(min(1.0, (y - yc) / 8.0))
        z = ZC + zc + 8.0 * math.cos(phi) + 0.1
        stud = k.ellipsoid("stud%d" % i, (x, y, z), (r, 0.98, 0.68), m["hull3"], 14, 7)
        bake_bands(stud, hull_bands(m), 60.0)
        parts.append(stud)
    centre, radii = FAIRING
    fairing = k.ellipsoid("fairing", centre, radii, m["hull4"], 18, 9)
    fairing.data.transform(Matrix.Translation(centre) @ Matrix.Rotation(math.radians(-18.0), 4, "X") @
                           Matrix.Translation(-Vector(centre)))
    bake_bands(fairing, [(-9.0, m["hull2"]), (0.3, m["hull3"]), (0.65, m["hull4"]), (0.88, m["rim"])], 60.0)
    parts.append(fairing)
    for obj in parts[1:]:
        parts.append(mirror_y(obj, obj.name + "_s"))
    return parts


# --- The hull, its groove and the rod -------------------------------------------------------------------------
# Its outline (x, radius): a cone over the third bulb, the long middle, a seam (x 10.6) where the tail section
# begins, the tail tapering to a blunt end.
HULL = [(-7.25, 0.0), (-7.2, 2.3), (-7.0, 3.7), (-6.6, 4.45), (-5.6, 4.95), (-4.2, 5.45), (-3.0, 5.85), (-2.0, 6.02),
        (2.0, 6.05), (9.6, 6.02), (10.25, 5.98), (10.45, 5.62), (10.85, 5.62), (11.05, 5.95), (13.0, 5.85),
        (15.5, 5.45), (17.6, 4.85), (19.3, 4.1), (20.5, 3.15), (21.2, 2.0), (21.45, 0.9), (21.5, 0.0)]
COLLAR = [(-3.35, 5.62), (-3.0, 6.02), (-2.6, 6.22), (-2.0, 6.28), (-1.5, 6.12)]   # a raised ring behind the cone
GROOVE = (11.3, 0.5, 1.55, 2.6)     # its start x, middle y, half-width, floor over the axis
ROD = (11.6, 25.0, 0.5, 3.75, 1.2)  # from x, to x, y, height over the axis, radius
SOCKET = (19.0, 23.0, 1.7)           # the sleeve round the rod at the hull's end: from x, to x, radius
TAIL_DARK = 0.22                     # how much darker (in the bands' value) the tail section is painted


def tail_darkening(x):
    return TAIL_DARK * mk.smoothstep(10.4, 11.4, x)


def hull(m):
    prof = k.profile([(x, r) for x, r in HULL[1:-1]], step=0.7)
    body = lathe_x("hull", [HULL[0]] + prof + [HULL[-1]], m["hull2"], segments=40)
    x0, yc, hw, floor = GROOVE
    groove = mk.box("groove", x0, 40.0, yc - hw, yc + hw, ZC + floor, ZC + 20.0, m["deep"])
    mk.boolean(body, groove, "DIFFERENCE")
    mk.cleanup(body, dissolve=0.0)
    values = [v.normal.dot(BAKE) - tail_darkening(v.co.x) for v in body.data.vertices]
    band_split(body, values, hull_bands(m))
    k.smooth(body, 35.0)
    # The groove's walls and floor dark.
    for poly in body.data.polygons:
        c = poly.center
        if c.x > x0 - 0.01 and abs(c.y - yc) < hw + 0.02 and ZC + floor - 0.05 < c.z < ZC + 5.5:
            poly.material_index = mk.slot_of(body, m["deep"])
    # The collar: a ring a little proud of the hull's front, lighter.
    collar = lathe_x("collar", [(COLLAR[0][0], 0.0)] + k.profile(COLLAR, step=0.2) + [(COLLAR[-1][0], 0.0)],
                     m["hull3"], segments=40)
    bake_bands(collar, [(-9.0, m["hull2"]), (0.2, m["hull3"]), (0.6, m["hull4"]), (0.9, m["rim"])], 40.0)
    xa, xb, y, h, r = ROD
    rod_prof = [(xa, 0.0)] + [(xa + r * (1 - math.cos(a)), r * math.sin(a)) for a in
                              [math.radians(d) for d in (25, 50, 75, 90)]]
    rod_prof += [(xb - 1.8, r), (xb - 0.8, r * 0.8), (xb - 0.25, r * 0.45), (xb, 0.0)]
    rod = lathe_x("rod", rod_prof, m["rim"], segments=20, squash=1.0, y0=y, z0=ZC + h)
    bake_bands(rod, [(-9.0, m["hull2"]), (0.35, m["hull4"]), (0.75, m["rim"])], 50.0)
    # The socket the rod leaves the tail by: a dark sleeve round it past the hull's end.
    x0s, x1s, rs = SOCKET
    sleeve = lathe_x("socket", [(x0s, 0.0), (x0s, rs), (x1s - 0.5, rs), (x1s - 0.15, rs * 0.85), (x1s, r * 1.02),
                                (x1s, 0.0)], m["deep"], segments=20, squash=1.0, y0=y, z0=ZC + h - 0.35)
    bake_bands(sleeve, [(-9.0, m["deep"]), (0.45, m["hull1"]), (0.8, m["hull2"])], 40.0)
    return [body, collar, rod, sleeve]


# --- The wings and the fins ----------------------------------------------------------------------------------------
# The upper wing's plan (the lower one is its mirror image): its root inside the hull.
WING = [(-7.6, 4.4), (-7.4, 5.4), (-7.0, 6.4), (-2.3, 11.6), (-1.6, 12.45), (10.3, 12.45), (11.0, 11.6), (10.5, 10.0),
        (9.4, 8.8), (8.9, 6.5), (8.9, 4.4)]
PANEL = [(-5.6, 4.4), (-4.8, 6.2), (-1.5, 9.75), (7.4, 9.75), (7.2, 6.2), (7.2, 4.4)]
WING_Z, WING_T, PANEL_D = -0.25, 1.3, 0.42      # the wing's middle over the axis, its thickness, the panel's depth
ANHEDRAL = 8.0
ROOT_Y = 5.4
FIN = [(8.0, 4.2), (8.3, 6.6), (10.3, 9.6), (12.3, 11.6), (14.3, 12.45), (19.2, 12.45), (21.0, 11.5), (22.8, 10.0),
       (24.2, 8.3), (25.0, 7.0), (24.3, 6.0), (22.9, 5.1), (21.6, 3.9), (20.0, 3.0), (17.0, 3.0)]
# The lower fin's plan, mirrored to the upper side: the sprite draws its tip a row nearer the axis and its back a
# column shorter than the upper fin's mirror image.
FIN_S = [(8.0, 4.2), (8.3, 6.4), (10.2, 9.2), (12.2, 10.9), (13.4, 11.45), (19.2, 11.45), (21.0, 10.7), (22.4, 9.5),
         (23.6, 8.0), (24.2, 6.7), (23.6, 5.6), (22.4, 4.8), (21.2, 3.9), (20.0, 3.0), (17.0, 3.0)]
FIN_Z, FIN_T = -1.1, 1.0
FIN_ANHEDRAL = 10.0


def droop(obj, angle):
    """Turns a part of the upper side about the line along X at its root, its outer side down by angle (degrees)."""
    pivot = Vector((0.0, ROOT_Y, ZC))
    obj.data.transform(Matrix.Translation(pivot) @ Matrix.Rotation(-math.radians(angle), 4, "X") @
                       Matrix.Translation(-pivot))
    obj.data.update()


def paint_plate(obj, top, edge, side, under, panel=None, inside=None):
    """Plate faces by their facing: tops (top, or panel where inside(x, y)), bevels (edge), walls (side), undersides."""
    for poly in obj.data.polygons:
        n, c = poly.normal, poly.center
        if n.z > 0.92:
            mat = panel if panel is not None and inside(c.x, c.y) and c.z < ZC + WING_Z + WING_T / 2 - 0.1 else top
        elif n.z > 0.45:
            mat = edge
        elif n.z > -0.45:
            mat = side
        else:
            mat = under
        poly.material_index = mk.slot_of(obj, mat)


def inside_poly(poly, x, y):
    hit = False
    for i in range(len(poly)):
        (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % len(poly)]
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            hit = not hit
    return hit


def wing(m, south=False):
    z0, z1 = ZC + WING_Z - WING_T / 2, ZC + WING_Z + WING_T / 2
    body = mk.prism("wing", WING, z0, z1, m["rim"])
    recess = mk.prism("wing_recess", PANEL, z1 - PANEL_D, z1 + 2.0, m["panel"])
    mk.boolean(body, recess, "DIFFERENCE")
    mk.cleanup(body)
    mk.bevel(body, 0.32, segments=2, angle=30.0)
    paint_plate(body, m["rim"], m["hull4"], m["hull2"], m["deep"], m["panel"],
                lambda x, y: inside_poly(PANEL, x, y))
    droop(body, ANHEDRAL)
    k.smooth(body, 30.0)
    if not south:
        return body
    low = mirror_y(body, "wing_s")
    bpy.data.objects.remove(body)
    for poly in low.data.polygons:      # the lower wing's panel in the sprite's dark teal
        if low.data.materials[poly.material_index].name == m["panel"].name:
            poly.material_index = mk.slot_of(low, m["panel_s"])
    return low


def fin(m, south=False):
    z0, z1 = ZC + FIN_Z - FIN_T / 2, ZC + FIN_Z + FIN_T / 2
    body = mk.prism("fin", FIN_S if south else FIN, z0, z1, m["rim"])
    mk.cleanup(body)
    mk.bevel(body, 0.3, segments=2, angle=30.0)
    paint_plate(body, m["rim"], m["hull4"], m["hull1"], m["deep"])
    droop(body, FIN_ANHEDRAL)
    k.smooth(body, 30.0)
    if not south:
        return body
    low = mirror_y(body, "fin_s")
    bpy.data.objects.remove(body)
    for poly in low.data.polygons:
        if low.data.materials[poly.material_index].name == m["rim"].name:
            poly.material_index = mk.slot_of(low, m["fin_s"])
    return low


# --- Build ---------------------------------------------------------------------------------------------------------

def build_whole():
    m = materials()
    head(m)
    hull(m)
    wing(m)
    wing(m, south=True)
    fin(m)
    fin(m, south=True)
    whole = [o for o in mk.meshes() if len(o.data.polygons) > 0]
    for obj in whole:
        mk.apply(obj)
        obj.data.transform(Matrix.Translation((0.0, AXIS_Y, 0.0)))
        obj.data.update()
    bpy.context.view_layer.update()
    return whole, m


def whole_mask(sheet):
    """The three sprites' silhouettes placed as the sheet lays them out (the left ship's layout, mirrored): 60 x 28."""
    mask = [[False] * 60 for _ in range(28)]
    for sprite, col in CELLS.items():
        part = k.sprite_mask(sheet, sprite)
        for y in range(28):
            for x in range(24):
                if part[y][x]:
                    mask[y][col + x] = True
    return mask


def mirrored(obj, name):
    """A copy of a piece mirrored across X = 0 (its sprite's middle), its custom normals mirrored with it."""
    mesh = obj.data
    corner = {}
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            n = mesh.corner_normals[li].vector
            corner[(poly.index, mesh.loops[li].vertex_index)] = (-n.x, n.y, n.z)
    copy = obj.copy()
    copy.data = mesh.copy()
    copy.name = name
    copy.data.name = name
    bpy.context.scene.collection.objects.link(copy)
    copy.data.transform(Matrix.Scale(-1, 4, (1, 0, 0)))
    copy.data.flip_normals()
    normals = [None] * len(copy.data.loops)
    for poly in copy.data.polygons:
        for li in poly.loop_indices:
            normals[li] = corner[(poly.index, copy.data.loops[li].vertex_index)]
    copy.data.normals_split_custom_set(normals)
    copy.data.update()
    return copy


def export_pieces(whole, m, options, sheet=None):
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    for name, sprite, (x0, x1) in PIECES:
        twin, twin_sprite = TWINS[name]
        if only and name not in only and twin not in only:
            continue
        parts = [p for p in (cut(src, (x0, x1, -14.0, 14.0), m["black"]) for src in whole) if p is not None]
        db.drop_unused(parts)
        mk.transform(parts, Matrix.Translation((-(x0 + x1) / 2, 0.0, 0.0)))
        bpy.context.view_layer.update()
        triangulate(parts)
        if "stats" in options:
            for obj in sorted(parts, key=lambda o: -mk.triangles([o]))[:12]:
                print("    %-22s %6d" % (obj.name, mk.triangles([obj])))
        piece = db.join(parts, name)
        piece.data.name = name
        left = mirrored(piece, twin)
        for src in whole:
            src.hide_render = True
        for obj, label, spr in ((piece, name, sprite), (left, twin, twin_sprite)):
            if only and label not in only:
                continue
            others = [o for o in (piece, left) if o is not obj]
            for o in others:
                o.hide_render = True
            if sheet:
                mk.compare("%s (x5e %d)" % (label, spr), mk.coverage([obj], 24, 28), k.sprite_mask(sheet, spr))
            mk.report(label, [obj], os.path.join(out, label + ".glb"))
            if "preview" in options:
                mk.preview(options["preview"] + label, [obj])
            for o in others:
                o.hide_render = False
        for obj in (piece, left):
            bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False


def build():
    k.reset()
    options = k.args()
    whole, m = build_whole()
    print("whole cruiser: %d triangles, %d objects" % (mk.triangles(whole), len(whole)))
    for obj in sorted(whole, key=lambda o: -mk.triangles([o]))[:16]:
        print("   %-22s %6d" % (obj.name, mk.triangles([obj])))
    sheet = os.path.join(options["check"], "enemy_x5e.png") if "check" in options else None
    if sheet:
        mk.compare("whole (x5e 198 200 201)", mk.coverage(whole, 60, 28), whole_mask(sheet))
    bpy.context.scene.view_settings.view_transform = "Standard"
    if "preview" in options:
        mk.preview(options["preview"] + "cruiser_whole", whole, size=(60, 28), scale=8, distance=1.8)
    if "whole" in options:
        triangulate(whole)
        mk.export(whole, options["whole"])
    if options.get("only") != "none":
        export_pieces(whole, m, options, sheet)


if __name__ == "__main__":
    build()
