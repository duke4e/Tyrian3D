"""TYRIAN's hooded turret in the rocks (sheet 2 sprite 153, 2x2: 24 x 28 pixels; enemy 40 of episodes 1 and 3, top
layer, TYRIAN and TYRIAN X; its animation 153 155 157 157 155 155 155 153 153 brightens its eye), polished (2026-10-19;
it replaces wave3_p.py's hood_turret(), a lofted hood on a carpet of grey pebbles). models.cfg: model hood_turret /
hood_turret_155 / hood_turret_157 ... origin; sprite 2 153 hood_turret yaw=0 height=-6; frame 2 155 hood_turret_155;
frame 2 157 hood_turret_157 (no other enemy shows sheet 2's 155 or 157).

The ground round it is the map's: the levels set the turret on the cobbles of TYRIAN's rocky outcrops (background 3,
tile 132: the sprite's border pixels are that tile's, and its grey cobbles and tan stones go on under the turret), so
the model leaves them out; it is what the sprite adds: a dark pit in the cobbles, ringed by black glossy boulders
(columns 1-9 and 13-22 of rows 1-11: their glints at columns 2, 6, 15 and 18-19), and in it the turret: a grey hood like
a pointed cowl (columns 6-17 of rows 0-11, a white ridge down column 11, its left face lit, its right in shade, its
foot lit along row 11); below it (down the screen) a band of dark red armour across (columns 5-18 of rows 12-15) with
the eye in its middle (columns 9-14 of rows 12-17: a glowing red lens, hottest at its upper left); grey cheek guards
from the band's lower corners in to the chin (rows 16-19); the chin, a pink lip over dark red (columns 9-13 of rows
18-20); and two red claws gripping the rocks either side (columns 2-7 and 15-20 of rows 20-25), their tips bronze
(rows 24-27).

Built as a CAD modeller would: the hood a prism of its plan cut by three planes, its two faces (meeting in the ridge,
which rises from the hood's point to its foot) and a small front facet over the band (lit, as row 11 is), its edges
bevelled, the ridge ground off into a narrow lit facet; the band a rounded block, its top edges well rounded, a socket
cut into its middle; the eye a lens turned about its axis, facing down the screen and up (towards the game's camera),
cut along smooth contours into a hot core at its upper left, a bright ring and a darker rim, glowing in them; the cheek
guards wedges sloping down towards the chin; the chin a rounded block with its lip; the claws bent bars of round
sections, their tips bronze (cut along smooth contours); under them a dark core. The pit is a dark plate with a skirt
(it covers the map's cobbles there), the boulders squashed, lumpy balls, glossy black.

The frames only brighten the eye (155 yellower, 157 white-hot in a broad core): the frame models are the same meshes,
the eye's materials changed, so their bounds are the same.

Where it stands: the top layer's enemies are drawn 6 pixels above background 3 (layer heights 38 and 32, both raised
by the terrain's headroom), whose rocks are a solid with its plane at its layer's height; models with origin are drawn
at their origin without lifting. So "height=-6" on the sprite line sets the pit on the rocks (without it the turret
floats 6 pixels over them; the skirt below the pit hides the gap only at its edge).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the rocks (z = 0); origin at the
sprite's centre (pixel 12, 14): column c's left edge is x = c - 12, row r's top edge y = 14 - r.

Replaces wave3_p.py's hood_turret(): remove it with its @model("hood_turret", [153]) registration, the P() helper
(only hood_turret() uses it) and the hood_turret lines of its docstring; and wave3_p_art.py's TURRET and TURRET_HOT
(only hood_turret() reads TURRET; nothing reads TURRET_HOT), so that it doesn't overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each frame's silhouette
against the turret's own pixels, the cobbles round it left out, written below), --preview <prefix>, --only <name,...>.
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
from polish_orb_red import band_split  # noqa: E402

AXIS_X = -0.4
# The pit: its outline (pixel edges, rounded), its top and how far its skirt goes down.
PIT = [(-6.8, 13.4), (-3.0, 13.85), (2.0, 13.85), (6.8, 13.4), (9.4, 11.2), (10.9, 8.6), (11.2, 4.2), (10.5, 1.0),
       (10.0, -3.0), (8.4, -5.4), (8.4, -9.2), (7.6, -11.9), (3.0, -12.4), (-3.0, -12.4), (-8.4, -11.6), (-9.0, -9.0),
       (-8.2, -5.5), (-9.4, -3.0), (-9.6, 1.0), (-10.8, 4.2), (-11.0, 8.6), (-9.4, 11.2)]
PIT_Z, SKIRT = 0.45, 2.0
# The boulders round the pit: centre (x, y), radii (x, y, height), sunk this far below the pit's top.
BOULDERS = [((-7.9, 6.6), (3.3, 4.2, 2.3), 0.6), ((-5.2, 11.4), (2.2, 2.0, 1.9), 0.5), ((4.0, 11.5), (2.3, 2.0, 1.8), 0.5),
            ((7.4, 6.2), (3.3, 4.3, 2.2), 0.6), ((-9.0, 0.6), (1.4, 1.9, 1.3), 0.4), ((8.5, 0.4), (1.4, 1.9, 1.3), 0.4)]
# The hood: its plan (pixel edges, a little in), the ridge along x = AXIS_X rising from RIDGE_Z[0] at its point
# (y 14) to RIDGE_Z[1] at its foot (y HOOD_FOOT), the faces falling from it (pixels of height per pixel out).
HOOD = [(-2.0, 14.0), (1.0, 14.0), (1.1, 10.6), (2.1, 9.9), (3.1, 8.7), (4.1, 7.3), (5.0, 5.4), (5.9, 3.6),
        (6.2, 2.4), (-6.2, 2.4), (-5.9, 3.6), (-5.0, 5.4), (-4.4, 7.3), (-3.4, 9.2), (-2.3, 10.4)]
HOOD_FOOT = 2.4
RIDGE_Z = (3.3, 9.6)
FACE_SLOPE = (0.95, 1.0)        # left, right
FRONT = (6.1, 2.2)              # its front facet over the band: its height at the hood's foot, its rise per pixel back
RIDGE_W = 0.45
# The band: x0, x1, y0, y1, top, the rounding of its top edges; the socket in its middle (radius).
BAND = (-7.3, 6.7, -2.2, 2.55, 6.4, 1.9)
SOCKET_R = 3.0
# The eye: its centre, radius, how far it bulges (along its axis), its axis (down the screen and up).
EYE = (Vector((AXIS_X + 0.2, -0.3, 4.4)), 2.65, 1.35)
EYE_AXIS = Vector((0.0, -0.55, 0.84)).normalized()
HOT_DIR = Vector((-0.25, 0.22, 1.0)).normalized()   # where its core is (from the axis towards its upper left)
# The cheek guards (the left one; mirrored about AXIS_X): plan, top at the band and at the chin.
CHEEK = [(-8.9, -1.5), (-6.2, -1.5), (-2.9, -4.9), (-3.5, -6.5), (-4.9, -5.8), (-8.9, -2.9)]
CHEEK_Z = (4.6, 2.6)
# The chin: centre x, y, half-width, half-depth, height; the lip along its back.
CHIN = (AXIS_X, -5.6, 2.6, 1.6, 3.4)
# The claws: paths of (x, y, z, radius), the last point the tip; the tips' share bronze.
CLAWS = [[(-4.9, -5.2, 2.6, 1.55), (-6.2, -7.2, 2.3, 2.0), (-6.6, -9.3, 1.6, 2.0), (-6.3, -10.9, 0.95, 1.6),
          (-5.8, -11.9, 0.5, 0.9)],
         [(3.9, -5.6, 2.6, 1.55), (5.3, -7.7, 2.3, 1.95), (5.9, -9.9, 1.6, 1.95), (6.4, -12.0, 0.95, 1.6),
          (6.6, -13.2, 0.5, 0.9)]]
CLAW_TIP_FROM = 0.62            # the share of a claw's length from where it is bronze
CORE = (AXIS_X, -1.6, 5.4, 4.6, 3.6)    # the dark core under the band and chin: x, y, half-width, half-depth, top

# The eye's colours by frame: rim, ring, core (palette index, glow).
FRAMES = [("hood_turret", 153, [(0x72, 0.9), (0x77, 1.6), (0x7b, 2.3)]),
          ("hood_turret_155", 155, [(0x74, 1.1), (0x7b, 2.0), (0x7f, 2.6)]),
          ("hood_turret_157", 157, [(0x77, 1.5), (0x7e, 2.4), (0x7f, 3.2)])]
EYE_BANDS = (0.55, 0.86)        # the ring and the core: from these cosines of the angle to HOT_DIR

# The turret's own pixels (rows: first, last, spans): the hood, the band, the eye, the cheeks, the chin, the claws and
# their tips, and the pit's black (the sprite's darkest greys round them); not the cobbles and tan stones.
OWN = [(0, 0, [(10, 12)]), (1, 1, [(6, 8), (10, 13), (15, 17)]), (2, 2, [(5, 5), (7, 14), (16, 18)]),
       (3, 3, [(5, 18)]), (4, 4, [(2, 21)]), (5, 5, [(1, 1), (3, 22)]), (6, 6, [(0, 0), (4, 17), (21, 23)]),
       (7, 7, [(0, 1), (3, 23)]), (8, 8, [(0, 23)]), (9, 9, [(0, 22)]), (10, 10, [(1, 22)]), (11, 11, [(2, 21)]),
       (12, 12, [(3, 21)]), (13, 13, [(4, 22)]), (14, 15, [(3, 22)]), (16, 16, [(3, 18), (20, 20)]),
       (17, 18, [(4, 20)]), (19, 19, [(4, 18), (20, 20)]), (20, 20, [(5, 7), (9, 13), (15, 19)]),
       (21, 21, [(4, 13), (15, 20)]), (22, 22, [(3, 20)]), (23, 23, [(2, 20)]), (24, 24, [(3, 11), (13, 20)]),
       (25, 25, [(4, 7), (9, 11), (14, 18)]), (26, 26, [(16, 16), (20, 20)]), (27, 27, [(17, 20)])]


def materials(eye):
    glow = k.level_palette()

    def lit(name, index, strength, roughness=0.15):
        return k.material(name, palette=index, metallic=0.0, roughness=roughness, emission=glow[index],
                          emission_strength=strength)
    m = {
        "pit": k.material("hood_pit", palette=0x01, metallic=0.0, roughness=0.85),
        "boulder": k.material("hood_boulder", palette=0x02, metallic=0.3, roughness=0.38),
        "hood": k.material("hood_grey", palette=0x06, metallic=0.55, roughness=0.3),
        "hood_lit": k.material("hood_grey_lit", palette=0x08, metallic=0.55, roughness=0.28),
        "ridge": k.material("hood_ridge", palette=0x0d, metallic=0.55, roughness=0.22),
        "dark": k.material("hood_dark", palette=0x03, metallic=0.45, roughness=0.4),
        "band": k.material("hood_band", palette=0x43, metallic=0.35, roughness=0.32),
        "band_lit": k.material("hood_band_lit", palette=0x48, metallic=0.35, roughness=0.3),
        "socket": k.material("hood_socket", palette=0x70, metallic=0.2, roughness=0.4),
        "lip": k.material("hood_lip", palette=0x4b, metallic=0.3, roughness=0.3),
        "bronze": k.material("hood_bronze", palette=0x16, metallic=0.7, roughness=0.3),
    }
    for role, (index, strength) in zip(("eye_rim", "eye_ring", "eye_core"), eye):
        m[role] = lit(f"hood_{role}_{index:x}", index, strength)
    return m


def plane_box(name, top, size=40.0):
    """Everything under the plane z = top(x, y), for intersecting with (polish_arch.py's)."""
    s = size
    return mk.wedge(name, [(-s, -s), (s, -s), (s, s), (-s, s)], 0.0, top, bottom=lambda x, y: top(x, y) - 200.0)


# --- The pit and its boulders ----------------------------------------------------------------------------------

def pit(m):
    """The dark pit: a plate over the cobbles, rounded at its edge, its skirt going down."""
    outline = mk.chaikin(PIT, 1)
    plate = mk.prism("pit", outline, -SKIRT, PIT_Z, m["pit"])
    mk.bevel(plate, 0.25, 2, 30)
    mk.shade(plate, 35)


def boulders(m):
    """The black glossy boulders ringing the pit's upper half and its sides."""
    for i, ((x, y), (rx, ry, h), sink) in enumerate(BOULDERS):
        rock = k.ellipsoid(f"boulder{i}", (x, y, PIT_Z - sink), (rx, ry, h + sink), m["boulder"], 20, 10)
        # Lumpy: a gentle wobble round it, its underside cut flat under the pit.
        for v in rock.data.vertices:
            a = math.atan2(v.co.y - y, v.co.x - x)
            v.co.x += 0.18 * math.cos(3 * a + i) * (v.co.x - x) / rx
            v.co.y += 0.18 * math.sin(2 * a + i) * (v.co.y - y) / ry
            v.co.z = max(v.co.z, -SKIRT)
        k.smooth(rock, 80)


# --- The turret ------------------------------------------------------------------------------------------------

def hood(m):
    """The hood: a prism of its plan cut by its two faces' planes, meeting in the ridge (rising from the point to the
    foot), and by its front facet's; its edges bevelled, the ridge's facet and the front facet lit, the left face
    lighter than the right."""
    body = mk.prism("hood", HOOD, 0.0, RIDGE_Z[1] + 2.0, m["hood"])
    rise = (RIDGE_Z[1] - RIDGE_Z[0]) / (14.0 - HOOD_FOOT)

    def ridge(y):
        return RIDGE_Z[0] + rise * (14.0 - y)
    left = lambda x, y: ridge(y) - FACE_SLOPE[0] * (AXIS_X - x)
    right = lambda x, y: ridge(y) - FACE_SLOPE[1] * (x - AXIS_X)
    front = lambda x, y: FRONT[0] + FRONT[1] * (y - HOOD_FOOT)
    for i, top in enumerate((left, right, front)):
        mk.boolean(body, plane_box(f"hood_plane{i}", top), "INTERSECT")
    mk.cleanup(body)
    mk.bevel(body, RIDGE_W, 2, 20)
    mk.shade(body, 25)

    def pick(c, n):
        if abs(c.x - AXIS_X) < RIDGE_W * 1.2 and n.z > 0.8:
            return m["ridge"]
        if n.y < -0.5 and n.z > 0.2:  # the front facet over the band, lit (row 11)
            return m["ridge"]
        if n.y < -0.7:
            return m["dark"]
        if n.z > 0.3 and c.x < AXIS_X:
            return m["hood_lit"]
        return None
    mk.paint(body, pick)


def band(m):
    """The band of armour across under the hood: a rounded block, its top edges rounded, the eye's socket cut into its
    middle; lit along its top towards the eye (the sprite's columns 8 and 15)."""
    x0, x1, y0, y1, top, rounding = BAND
    plan = mk.rounded_rect_ring(((x0 + x1) / 2, (y0 + y1) / 2), (x1 - x0) / 2, (y1 - y0) / 2, 1.2, 0.0, 48)
    body = mk.prism("band", [(p.x, p.y) for p in plan], 0.0, top, m["band"])
    mk.bevel(body, rounding, 6, 30)
    centre, radius, bulge = EYE
    socket = k.ellipsoid("socket_cut", tuple(centre), (SOCKET_R, SOCKET_R, SOCKET_R), m["socket"], 32, 16)
    mk.boolean(body, socket, "DIFFERENCE")
    mk.cleanup(body)
    mk.shade(body, 40)

    def pick(c, n):
        if (Vector(c) - centre).length < SOCKET_R + 0.05:
            return m["socket"]
        if n.z > 0.55 and abs(c.x - centre.x) < SOCKET_R + 1.8:
            return m["band_lit"]
        return None
    mk.paint(body, pick)


def eye(m):
    """The eye: a lens turned about its axis (down the screen and up), its colours cut along smooth contours: a core at
    its upper left, a ring round it, the rim."""
    centre, radius, bulge = EYE
    seg, steps = 32, 10
    profile = []
    for i in range(steps + 1):
        t = (math.pi / 2) * i / steps
        profile.append((max(0.01, radius * math.cos(t)), bulge * math.sin(t)))
    # Built about +Z at the origin, then turned to its axis and moved to its centre.
    lens = mk.lathe("eye", [(r, z - 0.6) for r, z in profile], (0.0, 0.0), m["eye_rim"], seg)
    turn = EYE_AXIS.to_track_quat("Z", "Y").to_matrix().to_4x4()
    lens.data.transform(Matrix.Translation(centre) @ turn)
    values = []
    for v in lens.data.vertices:
        d = (v.co - centre).normalized()
        values.append(d.dot(HOT_DIR))
    band_split(lens, values, [(-9.0, m["eye_rim"]), (EYE_BANDS[0], m["eye_ring"]), (EYE_BANDS[1], m["eye_core"])])
    k.smooth(lens, 70)


def cheeks(m):
    """The grey cheek guards: wedges from the band's lower corners in to the chin, sloping down towards it (down the
    screen)."""
    for side in (1, -1):
        plan = [(AXIS_X + side * (x - AXIS_X), y) for x, y in CHEEK]
        if side < 0:
            plan.reverse()
        high, low = CHEEK_Z

        def top(x, y):
            t = min(1.0, max(0.0, (CHEEK[0][1] - y) / (CHEEK[0][1] - CHEEK[3][1])))
            return high + (low - high) * t
        guard = mk.wedge(f"cheek{side}", plan, 0.0, top, m["hood"])
        mk.bevel(guard, 0.3, 2, 30)
        mk.shade(guard, 35)
        mk.paint(guard, lambda c, n: m["dark"] if n.z < 0.2 else m["hood_lit"] if n.z > 0.75 else None)


def chin(m):
    """The chin under the eye: a rounded block, dark red, its back edge a pink lip."""
    x, y, hw, hd, h = CHIN
    block = k.pillow("chin", hw, hd, h, m["band"], rounding=0.9, dome=0.3, power=3.0)
    block.data.transform(Matrix.Translation((x, y, 0.0)))
    mk.paint(block, lambda c, n: m["lip"] if n.z > 0.35 and c.y > y + 0.2 else None)


def claws(m):
    """The claws: bent bars of round sections from under the band out and down to the rocks, their tips bronze; lit
    along their tops."""
    for i, path in enumerate(CLAWS):
        bar = mk.smooth_tube(f"claw{i}", path, m["band"], 14)
        ys = [p[1] for p in path]
        tip_y = ys[0] + (ys[-1] - ys[0]) * CLAW_TIP_FROM
        # The tip bronze below tip_y, the top lit above it: cut along smooth contours.
        values = [(tip_y - v.co.y) * 10.0 if v.co.y < tip_y else min(0.0, 0.5 - v.normal.z) for v in bar.data.vertices]
        band_split(bar, values, [(-9.0, m["band_lit"]), (-0.32, m["band"]), (0.0, m["bronze"])])
        k.smooth(bar, 60)


def core(m):
    """The dark core under the band, the cheeks and the chin (mostly hidden)."""
    x, y, hw, hd, h = CORE
    block = k.pillow("core", hw, hd, h, m["pit"], rounding=1.2, dome=0.2, power=3.0)
    block.data.transform(Matrix.Translation((x, y, 0.0)))


def own_mask():
    mask = [[False] * 24 for _ in range(28)]
    for r0, r1, spans in OWN:
        for r in range(r0, r1 + 1):
            for c0, c1 in spans:
                for c in range(c0, c1 + 1):
                    mask[r][c] = True
    return mask


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    for name, sprite, eye_colours in FRAMES:
        if only and name not in only:
            continue
        k.reset()
        m = materials(eye_colours)
        pit(m)
        boulders(m)
        core(m)
        hood(m)
        band(m)
        eye(m)
        cheeks(m)
        chin(m)
        claws(m)
        parts = mk.meshes()
        for obj in parts:
            mk.apply(obj)
        bpy.context.view_layer.update()
        if "check" in options:
            mk.compare("%s (2 %d, its own pixels)" % (name, sprite), mk.coverage(parts, 24, 28), own_mask())
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts)


if __name__ == "__main__":
    build()
