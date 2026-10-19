"""MINERS's ore tug and the red ore lump it tows (sheet L, episode 5; ground layers, enemies 1162-1169), polished
(2026-10-19; it replaces wave3_z.py's tug_whole(), tow_ring(), hook_parts() and ore_whole()). models.cfg: model
miners_tug_l / miners_tug_r / miners_tow_ring / miners_tow_hook / miners_ore_tl / miners_ore_tr / miners_ore_bl /
miners_ore_br ... origin; sprite l 131 miners_tug_l yaw=0, sprite l 93 miners_tug_r yaw=0, sprite l 95 miners_tow_ring
yaw=0, sprite l 114 miners_tow_hook yaw=0, sprite l 17 miners_ore_tl yaw=0, sprite l 169 miners_ore_tr yaw=0, sprite l
55 miners_ore_bl yaw=0, sprite l 207 miners_ore_br yaw=0.

How the level puts them together (MINERS's events at 200-700 and 1350-2390): the tug's halves (L 131 left, 93 right;
2x2) side by side, 28 pixels below their row the ore's upper quarters (L 17, 169) and 28 below those its lower ones
(L 55, 207); the tow ring (L 95, 1x1) 16 pixels below the tug's centre, the hook (L 114, 1x1) 10 below the ring, both
on the tug's middle. Two objects: the tug with its ring and hook (links of their own, but moved together: when the
tug lifts away, at 270, ring and hook go with it and the ore stays), and the ore, which the level also drops alone as
a 4-part enemy (1200-1300) and swings like a pendulum under the hook (1940-2390, the hook swinging a little with it;
those events set ore and hook 2 pixels right of the tug and ring). The sprites' centres in the whole (y up the
screen, the tug's centre the origin): tug halves (-12, 0) and (12, 0), ring (0, -16), hook (0, -26), ore quarters
(-12, -28), (12, -28), (-12, -56), (12, -56).

As the sprites and their 4x upscales draw them:
- The tug (48 x 28, symmetric about the edge between its halves): a tan flying wing, swept forward at its leading
  edge (row 1 by the middle, row 4 at the tanks), its trailing edge notched (row 14 at columns 14-17) beside a tail
  boom that narrows down to the hitch (rows 15-22), wing and boom one smooth surface with a keel along the tail; a
  glossy black lens-shaped canopy on its middle (columns 20-27 of rows 1-14); a ribbed brass tank at each tip
  (columns 2-9, rows 0-18: three shallow bands between dark grooves, a rounded front) whose blue thruster bell points
  down the screen (rows 19-27, its mouth 10 pixels across, a lighter band round it); a grey hitch at the boom's end
  (rows 24-26): a flat lug, its pin down through the ring.
- The ring (12 x 12): a steel ring lying flat, its hole 6 pixels across; the hitch's pin through its near side.
- The hook (12 x 14): a link standing up through the ring's far side (rows 0-3), a flat link (rows 4-7), a short shank
  (row 8) and a grapple: a crescent blade arched across (rows 9-10, columns 1-10), its broad back lit, its face dark,
  its pale blue steel edge (row 12) and horns (rows 12-13) turned down the screen and down onto the ore.
- The ore (48 x 56, the lump in columns 8-40 of rows 8-42): a lump of red ore made of rounded pebbles, their upper
  left lit, dark creases between them, a dark rim at the ground.

Built as one assembly on the ground (z = 0): the tug flying with its wing and its tanks' axes at Z_TUG, the ring lying
at Z_RING, the chain running back to the grapple, whose edge reaches the ore's surface (the ore lies on the ground:
pebbles (ellipsoids along the long axes the upscale draws them, about a pixel down and right of the sprite's
highlights) lying on a squat core, voxel-remeshed into one surface; the creases dark where the surface lies about as
far out of one pebble as of the next, or away from all of them, the pebbles' tops lighter, the colours cut in along
those fields' contours). The tug is cut along its middle into its halves and the ore along its sprites' edges into
its quarters (polish_arch.py's cut(): the pieces keep the whole's shading across the cuts); ring and hook are whole.
Each piece is moved so that its sprite's centre is its origin (models.cfg origin: base on the layer).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground; a pixel edge
(column c, row r) of the tug's 48 x 28 picture is (c - 24, 14 - r); of the ore's 48 x 56 picture (c - 24, -14 - r).

Replaces wave3_z.py: remove TUG, ORE, RING, HOOK, TUG_AT, RING_AT, HOOK_AT, ORE_AT, WING_Z, RING_Z, ROCK_TOP,
tug_whole() and its kit.pieced("miners_tug", ...), tow_ring() and its kit.model("miners_tow_ring", ...), hook_parts()
and its kit.model("miners_tow_hook", ...), ore_whole() and its kit.pieced("miners_ore", ...), the kit.assembly(
"miners_tow", ...) line: that is all the file builds, so delete wave3_z.py; with it go wave3_z_art.py's TUG, ORE,
RING and HOOK (only it reads them) and wave3_z_kit.py's docstring's mention of it.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each piece's and the
wholes' silhouettes against enemy_L.png), --preview <prefix> (the assembly's and each piece's views), --only
<name,...>.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_arch import cut  # noqa: E402
from polish_redjet import Curve, naca, smoothstep  # noqa: E402
from polish_ring_machine import ccw, chaikin, relief, round_edge  # noqa: E402

Z_TUG = 16.0          # the tug's wing (its middle) and its tanks' axes
Z_RING = 14.1         # the ring's middle
TANK_X = 18.0        # the tanks' axes (columns 2-9 and 38-45)
RING_Y, RING_R, RING_TUBE = -16.0, 4.25, 1.52
PIN_Y = -14.0

# name, sprite, large, the box it covers in the whole (x0, x1, y0, y1), the sprite's centre, the source
PIECES = [("miners_tug_l", 131, True, (-24.0, 0.0, -20.0, 16.0), (-12.0, 0.0), "tug"),
          ("miners_tug_r", 93, True, (0.0, 24.0, -20.0, 16.0), (12.0, 0.0), "tug"),
          ("miners_tow_ring", 95, False, None, (0.0, -16.0), "ring"),
          ("miners_tow_hook", 114, False, None, (0.0, -26.0), "hook"),
          ("miners_ore_tl", 17, True, (-24.0, 0.0, -42.0, -14.0), (-12.0, -28.0), "ore"),
          ("miners_ore_tr", 169, True, (0.0, 24.0, -42.0, -14.0), (12.0, -28.0), "ore"),
          ("miners_ore_bl", 55, True, (-24.0, 0.0, -70.0, -42.0), (-12.0, -56.0), "ore"),
          ("miners_ore_br", 207, True, (0.0, 24.0, -70.0, -42.0), (12.0, -56.0), "ore")]


def materials():
    return {
        "wing": k.material("tug_wing", palette=0xa6, metallic=0.12, roughness=0.5),
        "wing_dark": k.material("tug_wing_dark", palette=0xa4, metallic=0.12, roughness=0.55),
        "canopy": k.material("tug_canopy", palette=0x02, metallic=0.35, roughness=0.07),
        "tank": k.material("tug_tank", palette=0xb8, metallic=0.55, roughness=0.3),
        "groove": k.material("tug_tank_groove", palette=0xb3, metallic=0.5, roughness=0.4),
        "bell": k.material("tug_bell", palette=0x37, metallic=0.5, roughness=0.3),
        "bell_band": k.material("tug_bell_band", palette=0x3a, metallic=0.5, roughness=0.28),
        "bell_dark": k.material("tug_bell_dark", palette=0x32, metallic=0.4, roughness=0.45),
        "steel": k.material("tow_steel", palette=0x0b, metallic=0.7, roughness=0.22),
        "steel_dark": k.material("tow_steel_dark", palette=0x08, metallic=0.65, roughness=0.3),
        "blade": k.material("tow_blade", palette=0x8c, metallic=0.35, roughness=0.2),
        "ore": k.material("ore_red", palette=0x47, metallic=0.0, roughness=0.58),
        "ore_light": k.material("ore_red_light", palette=0x48, metallic=0.0, roughness=0.5),
        "ore_dark": k.material("ore_red_dark", palette=0x43, metallic=0.0, roughness=0.7),
        "ore_rim": k.material("ore_rim", palette=0xa2, metallic=0.0, roughness=0.75),
        "seam": k.material("tow_seam", palette=0x03, metallic=0.3, roughness=0.6),
    }


def lathe_y(name, profile, cx, cz, mat, segments=32, close=True):
    """A part turned about an axis along y through (cx, cz): profile [(y, radius)]."""
    rings = []
    for y, r in profile:
        r = max(r, 0.02)
        rings.append([Vector((cx + r * math.sin(2 * math.pi * j / segments), y,
                              cz + r * math.cos(2 * math.pi * j / segments))) for j in range(segments)])
    return k.loft(name, rings, mat, cap_start=close, cap_end=close, start_point=(cx, profile[0][0], cz),
                  end_point=(cx, profile[-1][0], cz))


def lathe_z(name, profile, cx, cy, mat, segments=24):
    """A part turned about a vertical axis through (cx, cy): profile [(z, radius)] from its bottom up."""
    rings = [[Vector((cx + max(r, 0.02) * math.cos(2 * math.pi * j / segments),
                      cy + max(r, 0.02) * math.sin(2 * math.pi * j / segments), z)) for j in range(segments)]
             for z, r in profile]
    return k.loft(name, rings, mat, start_point=(cx, cy, profile[0][0]), end_point=(cx, cy, profile[-1][0]))


def swept_loop(name, path, radius, mat, segments=10, axis=None):
    """A closed tube (a ring, a chain link) round a closed path of points; axis: the loop's normal (for the
    tube's frame)."""
    n = len(path)
    verts, faces = [], []
    for i, p in enumerate(path):
        t = (path[(i + 1) % n] - path[i - 1]).normalized()
        out = axis.cross(t).normalized()
        for j in range(segments):
            a = 2 * math.pi * j / segments
            verts.append(p + (out * math.cos(a) + axis * math.sin(a)) * radius)
    for i in range(n):
        for j in range(segments):
            a, b = i * segments + j, i * segments + (j + 1) % segments
            c, d = ((i + 1) % n) * segments + (j + 1) % segments, ((i + 1) % n) * segments + j
            faces.append((a, b, c, d))
    obj = k.mesh_object(name, verts, faces, mat)
    k.recalc_normals(obj)
    return k.smooth(obj, 60)


# --- The tug ------------------------------------------------------------------------------------------------------
# Its wing's outline: the leading edge (|x|, y) from the middle to the tanks; the trailing edge from the tail's end
# (the boom down to the hitch, rows 15-22) to the notch (row 14) and to the tanks; 2/3 into the sprite's outline
# pixels. The wing and the boom are one surface, a keel along the middle.
WING_LE = Curve([(0.0, 13.05), (2.0, 12.9), (4.0, 12.65), (6.0, 12.45), (7.5, 12.3), (8.5, 12.0), (9.5, 11.55),
                 (10.5, 11.05), (11.5, 10.5), (12.5, 9.95), (13.5, 9.35), (14.7, 8.7)])
WING_TE = Curve([(0.0, -9.35), (0.55, -9.25), (1.0, -9.0), (1.25, -8.3), (1.4, -7.0), (1.75, -6.2), (2.5, -5.4),
                 (3.15, -4.45), (3.6, -3.45), (4.35, -2.55), (5.1, -1.7), (5.55, -0.95), (5.95, -0.5), (6.4, -0.35),
                 (9.6, -0.35), (10.4, -0.6), (11.4, -1.15), (12.4, -1.75), (13.4, -2.6), (14.7, -3.4)])
WING_X = 14.7
KEEL = 0.7
# The canopy along y (sorted by y): half-width, height above the wing.
CANOPY = Curve(sorted([(13.45, 0.0, 0.0), (13.0, 0.8, 0.75), (12.0, 1.85, 1.45), (11.0, 2.65, 2.0),
                       (10.0, 3.25, 2.4), (9.0, 3.65, 2.65), (8.0, 3.82, 2.78), (7.0, 3.72, 2.72), (6.0, 3.4, 2.52),
                       (5.0, 2.95, 2.22), (4.0, 2.45, 1.86), (3.0, 1.95, 1.5), (2.0, 1.45, 1.14), (1.0, 0.95, 0.8),
                       (0.0, 0.5, 0.45), (-0.6, 0.0, 0.0)]))


def wing_outline():
    xs = sorted(set([WING_X * (i / 30) ** 0.9 for i in range(31)] + [0.25 * i for i in range(1, 28)]))
    left_le = [(-x, WING_LE(x)) for x in reversed(xs)]          # from the left tank to the middle
    right_le = [(x, WING_LE(x)) for x in xs[1:]]                # from the middle to the right tank
    right_te = [(x, WING_TE(x)) for x in reversed(xs)]          # back to the middle
    left_te = [(-x, WING_TE(x)) for x in xs[1:]]                # and to the left tank
    return ccw(chaikin(left_le + right_le + right_te + left_te, 1))


def wing_top(x, y, d):
    ax = min(abs(x), WING_X)
    le, te = WING_LE(ax), WING_TE(ax)
    c = min(1.0, max(0.0, (le - y) / max(le - te, 0.5)))
    thick = 0.95 + 1.2 * (1 - smoothstep(3.0, 13.0, ax))       # thicker towards the middle
    shape = 0.3 + 0.7 * naca(c)
    droop = 0.3 * smoothstep(7.0, 14.5, ax)                     # the wing's outer parts a little lower
    keel = KEEL * max(0.0, 1.0 - ax / 2.6) ** 1.6 * smoothstep(2.0, -3.0, y)  # the ridge along the tail
    return Z_TUG - 0.55 - droop + (thick * shape + keel) * round_edge(d, 1.3)


def wing(m):
    """The wing and the boom: a solid over their outline, its edges rounded, its walls and underside darker."""
    return relief("wing", [wing_outline()], wing_top, {"wing": m["wing"], "wing_dark": m["wing_dark"]},
                  side="wing_dark", bottom=Z_TUG - 1.0, spacing=0.45, smooth_angle=55.0,
                  paint=lambda x, y, d: "wing")


def canopy(m, wing_obj):
    hit = mk.surface([wing_obj])
    ys = [13.45 - (13.45 + 0.6) * (i / 34) for i in range(35)]
    rings = []
    for y in ys[1:-1]:
        w, h = CANOPY(y)
        h0 = hit(0.0, y)
        base = (h0[0].z if h0 else Z_TUG + 1.5) - 0.45
        rings.append(k.ring(y, max(w, 0.05), 1.0, 32, z=base, top=max(h + 0.45, 0.05), bottom=0.8))
    h_top = hit(0.0, 13.3)
    h_end = hit(0.0, -0.5)
    obj = k.loft("canopy", rings, m["canopy"],
                 start_point=(0, 13.45, (h_top[0].z if h_top else Z_TUG + 1) - 0.4),
                 end_point=(0, -0.6, (h_end[0].z if h_end else Z_TUG + 1) - 0.4))
    return k.smooth(obj, 60)  # (its glint, rows 5-7, is the sun's: the glass is glossy)


# The tank along y (y, radius): its rounded front, three bulging bands between two grooves, the rounded back.
TANK = [(13.67, 0.0), (13.62, 0.9), (13.48, 1.65), (13.22, 2.3), (12.85, 2.85), (12.35, 3.3), (11.7, 3.58),
        (11.0, 3.68), (10.0, 3.7), (9.2, 3.62), (8.75, 3.45), (8.35, 3.3), (8.0, 3.26), (7.65, 3.3), (7.25, 3.45),
        (6.8, 3.62), (6.0, 3.7), (4.0, 3.72), (2.9, 3.64), (2.35, 3.47), (1.9, 3.32), (1.5, 3.28), (1.1, 3.32),
        (0.65, 3.47), (0.1, 3.64), (-0.8, 3.72), (-2.0, 3.68), (-2.9, 3.5), (-3.6, 3.2), (-4.2, 2.88),
        (-4.75, 2.7)]
GROOVES = ((8.0, 0.62), (1.5, 0.62))
# The thruster bell along y: its collar, the bell widening to its mouth, the lip and the dark throat inside.
BELL = [(-4.6, 2.62), (-5.0, 2.6), (-6.4, 2.62), (-6.8, 2.85), (-7.3, 3.3), (-8.0, 3.8), (-8.8, 4.25), (-9.6, 4.55),
        (-10.6, 4.68), (-12.4, 4.68), (-13.1, 4.55), (-13.55, 4.25), (-13.65, 3.85), (-13.4, 3.6), (-12.0, 3.25),
        (-10.6, 2.6), (-9.4, 1.6), (-8.8, 0.0)]
BELL_BAND = (-11.0, -12.3)       # the light band round the bell's widest part (rows 23-25)


def tanks(m):
    made = []
    for side in (-1, 1):
        cx = side * TANK_X
        tank = lathe_y(f"tank{side:+d}", TANK, cx, Z_TUG, m["tank"], segments=32)
        k.smooth(tank, 50)
        mk.paint(tank, lambda c, n: m["groove"] if any(abs(c.y - g) < w for g, w in GROOVES) or c.y < -3.5 else None)
        made.append(tank)
        bell = lathe_y(f"bell{side:+d}", BELL, cx, Z_TUG, m["bell"], segments=32)
        k.smooth(bell, 45)

        def pick(c, n, cx=cx):
            radial = Vector((c.x - cx, 0.0, c.z - Z_TUG))
            r = radial.length
            if c.y > -6.7:
                return m["bell_dark"]  # the collar
            if r < 3.75 and c.y > -13.5:
                return m["bell_dark"]  # the throat inside
            if BELL_BAND[1] < c.y < BELL_BAND[0] and r > 4.5:
                return m["bell_band"]
            return None
        mk.paint(bell, pick)
        made.append(bell)
    return made


def hitch(m):
    """The grey hitch at the boom's end (rows 24-26): a flat lug with a round eye, its pin down through the ring."""
    made = []
    rings = []
    z0 = Z_TUG - 0.55
    for y, w in ((-8.2, 0.95), (-9.0, 0.95), (-11.5, 0.85), (-12.8, 0.85)):
        rings.append(k.ring(y, w, 1.0, 16, z=z0, top=0.42, bottom=0.42, power=3.0))
    lug = k.loft("lug", rings, m["steel"])
    k.smooth(lug, 40)
    made.append(lug)
    eye = lathe_z("lug_eye", [(z0 - 0.45, 1.1), (z0 - 0.3, 1.25), (z0 + 0.3, 1.25), (z0 + 0.45, 1.1)], 0.0, PIN_Y,
                  m["steel"], segments=20)
    made.append(k.smooth(eye, 45))
    pin = lathe_z("pin", [(Z_RING - 2.3, 0.0), (Z_RING - 2.3, 0.7), (Z_RING - 2.0, 0.9), (Z_RING - 1.7, 0.72),
                          (Z_RING - 1.6, 0.52), (z0 + 0.6, 0.52), (z0 + 0.62, 0.8), (z0 + 0.85, 0.8), (z0 + 0.95, 0.0)],
                  0.0, PIN_Y, m["steel_dark"], segments=16)
    made.append(k.smooth(pin, 45))
    return made


def tug(m):
    w = wing(m)
    made = [w, canopy(m, w)]
    made += tanks(m)
    made += hitch(m)
    return made


# --- The ring and the hook ----------------------------------------------------------------------------------------

def ring(m):
    path = [Vector((RING_R * math.cos(2 * math.pi * i / 44), RING_Y + RING_R * math.sin(2 * math.pi * i / 44), Z_RING))
            for i in range(44)]
    return [swept_loop("ring", path, RING_TUBE, m["steel"], segments=14, axis=Vector((0, 0, 1)))]


def stadium(centre, half_len, half_wid, u, v, count=28):
    """A closed stadium path round centre: half_len along u, half_wid along v."""
    pts = []
    straight = max(half_len - half_wid, 0.0)
    for i in range(count):
        a = 2 * math.pi * i / count
        c, s = math.cos(a), math.sin(a)
        along = straight * (1 if c >= 0 else -1) + half_wid * c
        pts.append(centre + u * along + v * (half_wid * s))
    return pts


def hook(m, ore_hit):
    made = []
    X, Y, Z = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))
    # Link 1 stands up (in the plane x = 0) round the ring's far side, its wire thick (the sprite draws it 2 pixels
    # wide); link 2 lies flat through link 1's far end.
    made.append(swept_loop("link1", stadium(Vector((0.0, -20.4, Z_RING)), 2.45, 2.3, Y, Z), 0.72, m["steel"],
                           segments=10, axis=X))
    made.append(swept_loop("link2", stadium(Vector((0.0, -24.55, Z_RING - 0.3)), 1.6, 0.72, Y, X), 0.5,
                           m["steel_dark"], segments=10, axis=Z))
    # The grapple: the shank, the crown, and a crescent blade arched across, its back up the screen, its sharp pale
    # edge and horns turned down the screen and down into the ore.
    zc = Z_RING - 0.6
    made.append(k.smooth(mk.tube("shank", [(0.0, -25.9, zc + 0.1), (0.0, -28.5, zc + 0.1)], 0.58, m["steel"], 12), 50))
    made.append(k.smooth(k.ellipsoid("crown", (0.0, -28.7, zc + 0.35), (1.2, 0.85, 0.75), m["steel_dark"], 14, 8), 60))
    made.append(crescent(m, ore_hit, zc))
    return made


# The crescent's middle line (x, y) from the left horn's tip to the right one's, and its cross-section: how far its
# back stands out of the line (up the screen, outwards), how far its edge reaches in, the back's height above and
# below zc and how far down the edge goes (into the ore).
CRESCENT = [(-3.0, -33.1), (-4.25, -32.2), (-4.75, -31.1), (-4.45, -30.2), (-3.3, -29.7), (-1.7, -29.5),
            (0.0, -29.45), (1.7, -29.5), (3.3, -29.7), (4.45, -30.2), (4.75, -31.1), (4.25, -32.2), (3.0, -33.1)]
# Its cross-section across the line (out: towards its back, up the screen; z above the line): the back, the broad top,
# the face sloping down to the edge, the edge, the underside. SLOPE and EDGE (indices of the faces from one point to
# the next) are painted dark and pale.
CRESCENT_SECTION = [(-1.0, 0.42), (-0.3, 0.6), (0.95, 0.45), (1.6, -0.22), (2.35, -0.42), (2.25, -0.95),
                    (0.9, -0.66), (-1.0, -0.42)]
CRESCENT_SLOPE, CRESCENT_EDGE, CRESCENT_DIG = (2,), (3, 4), (4, 5)


def crescent(m, ore_hit, zc):
    pts = [Vector((x, y, 0.0)) for x, y in mk.chaikin(CRESCENT, 2, closed=False)]
    n = len(pts)
    centre = Vector((0.0, -32.0, 0.0))
    rings = []
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized()
        inward = Vector((0, 0, 1)).cross(t).normalized()
        if inward.dot(centre - p) < 0:
            inward = -inward
        u = i / (n - 1)
        end = math.sin(math.pi * u) ** 0.35           # the horns thin to their tips
        z_line = zc - 1.1 * (1 - end) ** 1.5          # and curl down
        h = ore_hit(p.x, p.y)
        dig = 0.0
        if h is not None:                           # the edge down to the ore's surface
            edge_z = z_line + CRESCENT_SECTION[5][1] * (0.45 + 0.55 * end)
            dig = max(0.0, edge_z - h[0].z)
        ring = []
        for j, (a, z) in enumerate(CRESCENT_SECTION):
            f = 0.45 + 0.55 * end
            zz = z * f - (dig if j in CRESCENT_DIG else 0.0)
            ring.append(p + inward * a * (0.35 + 0.65 * end) + Vector((0, 0, z_line + zz)))
        rings.append(ring)
    first, last = pts[0], pts[-1]
    obj = k.loft("crescent", rings, m["steel"], start_point=tuple(rings[0][5] * 0.5 + rings[0][1] * 0.5),
                 end_point=tuple(rings[-1][5] * 0.5 + rings[-1][1] * 0.5))
    k.recalc_normals(obj)
    k.smooth(obj, 38)
    ns = len(CRESCENT_SECTION)
    side = (n - 1) * ns
    slots = {key: mk.slot_of(obj, m[key]) for key in ("steel", "steel_dark", "blade")}
    for poly in obj.data.polygons:
        if poly.index >= side:
            poly.material_index = slots["blade"]       # the horns' tips
            continue
        j = poly.index % ns
        poly.material_index = slots["steel_dark" if j in CRESCENT_SLOPE else "blade" if j in CRESCENT_EDGE else
                                    "steel"]
    return obj


# --- The ore ------------------------------------------------------------------------------------------------------
# Nodules, read off the 4x upscale (the ore's 48 x 56 picture): the middle (column, row), the long and the short
# half-length, the long axis's angle (degrees from the picture's x, turning down the picture). The sprite paints them
# as rounded pebbles lit at their upper left, dark creases between them.
NODULES = [(19.0, 23.6, 5.9, 3.5, 66), (21.0, 12.6, 3.9, 2.9, 25), (30.0, 11.0, 3.6, 2.6, 20),
           (28.6, 18.0, 4.4, 2.8, 14), (28.6, 24.2, 4.3, 3.1, 58), (34.0, 23.2, 3.3, 2.3, 72),
           (29.1, 31.0, 4.4, 3.1, 42), (35.0, 30.5, 3.0, 2.3, 62), (22.0, 34.6, 4.0, 2.9, 42),
           (27.5, 38.0, 4.1, 2.8, 18), (13.0, 17.0, 3.6, 2.7, 62), (11.6, 24.0, 3.2, 2.5, 82),
           (13.0, 30.6, 3.6, 2.7, 30), (17.6, 29.6, 3.1, 2.5, 45), (17.2, 35.6, 3.1, 2.3, 18),
           (16.2, 12.2, 2.9, 2.1, 18), (24.0, 22.0, 2.9, 2.3, 72), (25.6, 14.0, 2.8, 2.1, 8),
           (34.0, 35.0, 2.5, 2.1, 30), (23.0, 39.6, 2.6, 2.0, 10), (36.5, 26.6, 2.3, 1.9, 80),
           (31.6, 14.6, 2.6, 2.0, 30), (10.6, 28.0, 2.4, 1.9, 70)]
NODULE_HEIGHT = 0.95    # their height, of their short half-length
ORE_VOXEL, ORE_SMOOTH, ORE_DECIMATE = 0.3, 10, 0.12
# The mass the nodules lie on: its middle (column, row), half-lengths, height; and its core, inside.
MASS_C, MASS_RX, MASS_RY, MASS_H = (24.5, 25.0), 16.5, 17.0, 13.6
CORE_SCALE = 0.8
CREVICE_FAR, CREVICE_GAP, CREVICE_IN = 1.3, 0.1, 0.95  # crevice(): farther than this from every nodule; or within
#                                                       this of two, beyond this into them
RIM_Z = 1.0


def ore_px(c, r):
    """A point (column, row) of the ore's 48 x 56 picture in the whole."""
    return (c - 24.0, -14.0 - r)


def mass_height(x, y):
    cx, cy = ore_px(*MASS_C)
    u = ((x - cx) / MASS_RX) ** 2 + ((y - cy) / MASS_RY) ** 2
    return MASS_H * math.sqrt(max(0.0, 1.0 - u)), u


def nodules():
    """The nodules as (centre, radii, angle): their tops on the mass's surface; those beyond its rim on the ground."""
    out = []
    for c, r, a, b, ang in NODULES:
        x, y = ore_px(c + 0.5, r + 0.5)
        h, u = mass_height(x, y)
        height = b * NODULE_HEIGHT
        z = max(h - height * 0.92, height * 0.45)
        # Down the picture is -y here: the angle turns the other way.
        out.append((Vector((x, y, z)), Vector((a + 0.35, b + 0.35, height)), -math.radians(ang)))
    return out


def nodule_object(name, centre, radii, angle, mat):
    obj = k.ellipsoid(name, (0.0, 0.0, 0.0), tuple(radii), mat, 24, 14)
    obj.data.transform(Matrix.Translation(centre) @ Matrix.Rotation(angle, 4, "Z"))
    return obj


def ore(m):
    cx, cy = ore_px(*MASS_C)
    parts = [k.ellipsoid("ore_core", (cx, cy, 0.0), (MASS_RX * CORE_SCALE, MASS_RY * CORE_SCALE, MASS_H * 0.86),
                         m["ore"], 40, 24)]
    nods = nodules()
    for i, (c, radii, ang) in enumerate(nods):
        parts.append(nodule_object(f"nodule{i}", c, radii, ang, m["ore"]))
    with bpy.context.temp_override(selected_editable_objects=parts, selected_objects=parts, active_object=parts[0],
                                   object=parts[0]):
        bpy.ops.object.join()
    rock = parts[0]
    rock.name = "ore"
    mk.soften(rock, voxel=ORE_VOXEL, iterations=ORE_SMOOTH, factor=0.6)
    # Flat on the ground.
    bm = bmesh.new()
    bm.from_mesh(rock.data)
    res = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=(0, 0, 0.0),
                                 plane_no=(0, 0, -1), clear_outer=True)
    edges = [e for e in res["geom_cut"] if isinstance(e, bmesh.types.BMEdge) and e.is_valid and len(e.link_faces) == 1]
    if edges:
        bmesh.ops.holes_fill(bm, edges=edges, sides=0)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(rock.data)
    bm.free()
    dec = rock.modifiers.new("decimate", "DECIMATE")
    dec.ratio = ORE_DECIMATE
    mk.apply(rock)
    k.smooth(rock, 70)
    paint_ore(rock, m, nods)
    rock.data.validate(clean_customdata=False)  # (a face the bottom's fill duplicates, now and then)
    return rock


def nodule_distances(p, nods):
    """The two smallest of p's distances to the nodules, each in its own radii (1: on its surface)."""
    best, second = 1e9, 1e9
    for c, r, ang in nods:
        d = p - c
        ca, sa = math.cos(-ang), math.sin(-ang)
        lx, ly = d.x * ca - d.y * sa, d.x * sa + d.y * ca
        v = math.sqrt((lx / r.x) ** 2 + (ly / r.y) ** 2 + (d.z / r.z) ** 2)
        if v < best:
            best, second = v, best
        elif v < second:
            second = v
    return best, second


def crevice(p, nods):
    """Below 0 in a crevice: about as far out of one nodule as of the next, or away from all of them."""
    s1, s2 = nodule_distances(p, nods)
    return min(CREVICE_FAR - s1, max(s2 - s1 - CREVICE_GAP, CREVICE_IN - s1))


def nodule_top(p, normal, nods):
    """Below 0 on a nodule's top."""
    s1, _ = nodule_distances(p, nods)
    return max(s1 - 1.1, 0.7 - normal.z)


def paint_ore(rock, m, nods):
    """The rim at the ground darkest, the crevices between the nodules dark, the nodules' tops light: the faces cut
    along those fields' contours first, so that the colours meet along smooth lines."""
    bm = bmesh.new()
    bm.from_mesh(rock.data)
    fields = (lambda v: v.co.z - RIM_Z, lambda v: crevice(v.co, nods), lambda v: nodule_top(v.co, v.normal, nods))
    for field in fields:
        bm.normal_update()
        values = {v: field(v) for v in bm.verts}
        mk.split_along(bm, values, 0.0)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bm.normal_update()
    slots = {key: mk.slot_of(rock, m[key]) for key in ("ore", "ore_light", "ore_dark", "ore_rim")}
    for f in bm.faces:
        c = f.calc_center_median()
        if c.z < RIM_Z or f.normal.z < -0.35:
            key = "ore_rim"
        elif crevice(c, nods) < 0:
            key = "ore_dark"
        elif nodule_top(c, f.normal, nods) < 0:
            key = "ore_light"
        else:
            key = "ore"
        f.material_index = slots[key]
    bm.to_mesh(rock.data)
    bm.free()
    k.smooth(rock, 70)


# --- Checks and build ---------------------------------------------------------------------------------------------

def masks(sheet):
    def block(cells, w, h):
        out = [[False] * w for _ in range(h)]
        for sprite, (c0, r0) in cells.items():
            part = k.sprite_mask(sheet, sprite)
            for y in range(28):
                for x in range(24):
                    if part[y][x]:
                        out[r0 + y][c0 + x] = True
        return out
    return {"tug": block({131: (0, 0), 93: (24, 0)}, 48, 28),
            "ore": block({17: (0, 0), 169: (24, 0), 55: (0, 28), 207: (24, 28)}, 48, 56)}


def build():
    options = k.args()
    out = mk.outdir(options)
    k.reset()
    m = materials()
    groups = {}
    groups["ore"] = [ore(m)]
    ore_hit = mk.surface(groups["ore"])
    groups["tug"] = tug(m)
    groups["ring"] = ring(m)
    groups["hook"] = hook(m, ore_hit)
    for objs in groups.values():
        for obj in objs:
            mk.apply(obj)
    bpy.context.view_layer.update()
    everything = [o for objs in groups.values() for o in objs]
    bpy.context.scene.view_settings.view_transform = "Standard"
    sheet = os.path.join(options["check"], "enemy_L.png") if "check" in options else None
    for label in ("tug", "ore"):
        objects = groups[label]
        low, high = mk.bounds(objects)
        print("== whole %s: %d triangles, %d objects, %d materials, x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (
            label, mk.triangles(objects), len(objects), len(mk.materials_of(objects)), low.x, high.x, low.y, high.y,
            low.z, high.z))
        if sheet:
            w, h = (48, 28) if label == "tug" else (48, 56)
            mk.compare("whole " + label, mk.coverage(objects, w, h, centre=(0.0, 0.0 if label == "tug" else -42.0)),
                       masks(sheet)[label])
    if "preview" in options:
        mk.preview(options["preview"] + "miners_whole", everything, size=(48, 84), scale=8, distance=2.2,
                   centre=(0.0, -28.0))
    bpy.context.view_layer.update()  # (the preview moved the objects and back: their bounds again, for cut())
    only = options.get("only", "").split(",") if "only" in options else None
    for name, sprite, large, box, centre, source in PIECES:
        if only and name not in only:
            continue
        if box is None:
            pieces = []
            for src in groups[source]:
                copy = src.copy()
                copy.data = src.data.copy()
                bpy.context.scene.collection.objects.link(copy)
                pieces.append(copy)
        else:
            pieces = [p for p in (cut(src, box, m["seam"]) for src in groups[source]) if p is not None]
        mk.transform(pieces, Matrix.Translation((-centre[0], -centre[1], 0)))
        bpy.context.view_layer.update()
        for src in everything:
            src.hide_render = True
        if sheet:
            w, h = (24, 28) if large else (12, 14)
            mk.compare("%s (L %d)" % (name, sprite), mk.coverage(pieces, w, h), k.sprite_mask(sheet, sprite, large))
        mk.report(name, pieces, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, pieces, size=(24, 28) if large else (12, 14))
        for obj in pieces:
            bpy.data.objects.remove(obj)
        for src in everything:
            src.hide_render = False


if __name__ == "__main__":
    build()
