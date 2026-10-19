"""The pink torpedo of IXMUCANE and SAWBLADES lying on its side, drawn from two sprites of sheet 8 (2x2 each, 24 x 28;
not animated; on the ground and on top): the front with the glowing muzzle (8 125, enemy 91, which launches its
shots) at x and the rear (8 127, enemy 92) at x + 24 on one row, one link (IXMUCANE's events 500, 600, 2800-2940,
4080-4140), moving together. Polished (2026-10-19; it replaces wave2_g.py's torpedo_half()). models.cfg: model
pink_torpedo_front / pink_torpedo_rear ... origin (unchanged); sprite 8 125 pink_torpedo_front yaw=0
glow=10:0.3:122:-9:-2.5 (the muzzle), sprite 8 127 pink_torpedo_rear yaw=0 glow=8:0.15:120:-5.5:-2.5 (the slits). No
other enemy shows these sprites. (IXMUCANE's red pod lying with its nose up
the screen, 8 153 above 191, ixm_pod_top / ixm_pod_body, is this torpedo turned: its 48 x 23 pixels are these
transposed, shade for shade; it is cut along y instead and its frames pulse its lights.)

As the sprites and their 4x upscales draw the whole (48 x 28, its axis along row 11), muzzle to the left: a glowing
muzzle cap (columns 0-5: two hot yellow bands between red rings, 0x72-0x7f) with a small red knob above and below it;
a grey ring and a grey receiver (columns 6-16) with a dark window in its top showing brown inside (columns 7-13,
rows 9-13); an olive collar (columns 13-21) with two swept armour fins reaching up and down the screen (rows 0-4 and
18-22), their outer edges tipped pink; then the bulbous pink body (ramp 4) from column 20 to the rounded end at
the far right (column 47), widest in its middle (rows 2-20), a raised band near its front (127's columns 3-7) cut by
two glowing slits (columns 5 and 7, rows 8-13), and a crease along its top between two lit lobes.

The torpedo is a body of revolution about its axis (y 2.5, along x), its sections ellipses a little flatter than
wide (it lies on the ground: z = 0 under its widest part), the receiver's boxier, the body's creased along the top;
the fins are swept plates in the plane of the axis; the muzzle and the slits glow in their own colours. It is built
whole and cut along the sprites' common edge (polish_machine_kit.cut: the halves keep the whole's shading, the cut
capped), each half moved so that its sprite's centre is its origin.

Replaces wave2_g.py's torpedo (build_torpedo(), torpedo_half(), WHOLES["torpedo"] and the two model(...) lines for
pink_torpedo_front / pink_torpedo_rear, and the pink_torpedo lines of the docstring; wave2_g_art.py's E8_125, which
nothing reads): remove them so that they don't overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the whole
and of each half against enemy_8.png), --preview <prefix> (each half's top and 3/4 view and the whole's).
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
import polish_machine_kit as mk  # noqa: E402
from polish_jets import Curve  # noqa: E402
from polish_redjet import chaikin, facet, resample  # noqa: E402
from polish_squid_ship import ccw, rounded_rect, tube  # noqa: E402

# name, sprite, the box it covers (x0, x1, y0, y1), its sprite's centre x
PIECES = [("pink_torpedo_front", 125, (-24.0, 0.0, -14.0, 14.0), -12.0),
          ("pink_torpedo_rear", 127, (0.0, 24.0, -14.0, 14.0), 12.0)]

AXIS_Y = 2.5            # row 11
SQUASH = 0.72           # the sections' height over their half-width
R_MAX = 9.15
AXIS_Z = SQUASH * R_MAX + 0.3  # the widest part (its band) rests on the ground

# The radius along x (1/3 pixel inside the outline), by part.
MUZZLE = [(-23.72, 0.0), (-23.68, 1.5), (-23.45, 2.45), (-22.9, 3.35), (-22.0, 4.05), (-20.9, 4.35), (-19.6, 4.4),
          (-18.6, 4.3), (-18.2, 4.1)]
RECEIVER = (-18.2, -6.6, 5.15)     # x from, to; half-width (a boxy section)
COLLAR = (-7.2, -3.4, 6.45)
BODY = Curve([(-4.0, 6.9), (-1.0, 7.15), (1.5, 7.4), (3.0, 8.4), (4.6, 9.15), (9.5, 9.15), (13.8, 9.1), (15.6, 8.3),
              (17.6, 7.2), (19.5, 6.15), (21.3, 5.05), (22.5, 4.0), (23.2, 2.9), (23.55, 1.8), (23.7, 0.0)])
BODY_X = (-4.0, 23.7)
BAND = (2.6, 8.5)                  # the raised band round the body's front
SLITS = (5.5, 7.5)                 # the glowing slits across it
CREASE_DEPTH, CREASE_WIDTH = 0.12, 0.22   # the crease along the body's top (in units of the half-width)
# The upper fin (the lower one is its mirror image across the axis): its plan (x, distance from the axis).
FIN = [(-11.3, 5.3), (-10.3, 6.4), (-8.6, 8.1), (-7.1, 9.6), (-6.2, 10.45), (-5.2, 10.67), (-3.3, 10.67), (-2.4, 10.25),
       (-1.5, 9.1), (-0.8, 7.6)]
FIN_ROOT = 4.6                             # the fins' roots, inside the receiver and the body
FIN_TIP = [(-5.85, 10.05), (-3.25, 10.05)]  # the pink tip along its outer edge
WINDOW = (-16.9, -9.7, -2.45, 2.45)        # the window in the receiver's top (x from, to; across from, to)


def materials():
    pal = k.level_palette()

    def hot(name, index, strength, rough=0.4):
        return k.material(name, palette=index, metallic=0.0, roughness=rough, emission=pal[index],
                          emission_strength=strength)
    return {
        "muzzle_core": hot("torpedo_muzzle_core", 0x7c, 2.0),
        "muzzle_band": hot("torpedo_muzzle_band", 0x7a, 1.5),
        "muzzle_ring": hot("torpedo_muzzle_ring", 0x74, 0.6),
        "knob": k.material("torpedo_knob", palette=0x45, metallic=0.3, roughness=0.3),
        "grey": k.material("torpedo_grey", palette=0x07, metallic=0.55, roughness=0.3),
        "grey_light": k.material("torpedo_grey_light", palette=0x0b, metallic=0.55, roughness=0.25),
        "frame": k.material("torpedo_frame", palette=0x41, metallic=0.3, roughness=0.5),
        "inside": k.material("torpedo_inside", palette=0x14, metallic=0.2, roughness=0.6),
        "olive": k.material("torpedo_olive", palette=0x16, metallic=0.4, roughness=0.3),
        "olive_dark": k.material("torpedo_olive_dark", palette=0xa3, metallic=0.35, roughness=0.4),
        "pink": k.material("torpedo_pink", palette=0x47, metallic=0.3, roughness=0.28),
        "pink_light": k.material("torpedo_pink_light", palette=0x4b, metallic=0.3, roughness=0.26),
        "slit": hot("torpedo_slit", 0x7b, 1.7),
        "cut": k.material("torpedo_cut", palette=0x42, metallic=0.2, roughness=0.6),
    }


# --- Sections round the axis ---------------------------------------------------------------------------------

def section(x, r, segments=36, power=2.0, crease=0.0):
    """A cross-section at x round the axis: half-width r (along y), height SQUASH * r, a superellipse of the given
    power; crease sinks its top's middle."""
    pts = []
    for j in range(segments):
        a = 2 * math.pi * j / segments
        c, s = math.cos(a), math.sin(a)
        py = math.copysign(abs(c) ** (2 / power), c) * r
        pz = math.copysign(abs(s) ** (2 / power), s) * r * SQUASH
        if s > 0 and crease > 0:
            pz -= crease * r * SQUASH * math.exp(-(c / CREASE_WIDTH) ** 2) * s
        pts.append(Vector((x, AXIS_Y + py, AXIS_Z + pz)))
    return pts


def lathe_x(name, profile, mat, segments=36, power=2.0, crease=None):
    """A part turned about the axis: profile [(x, r)] in increasing x, closed at both ends."""
    rings = [section(x, max(r, 0.03), segments, power, crease(x) if crease else 0.0) for x, r in profile]
    first, last = profile[0][0], profile[-1][0]
    obj = k.loft(name, rings, mat, start_point=(first, AXIS_Y, AXIS_Z), end_point=(last, AXIS_Y, AXIS_Z))
    return obj


def surface_z(x, y, r):
    """The top of a section of half-width r at (x, y) (no crease)."""
    d = (y - AXIS_Y) / r
    if abs(d) >= 1:
        return AXIS_Z
    return AXIS_Z + SQUASH * r * math.sqrt(1 - d * d)


def paint_x(obj, bands):
    """Faces take the material of the band their centre's x lies in: bands [(x from, material)] ascending."""
    for _, mat in bands:
        mk.slot_of(obj, mat)
    for poly in obj.data.polygons:
        x = poly.center.x
        chosen = None
        for x0, mat in bands:
            if x >= x0:
                chosen = mat
        if chosen is not None:
            poly.material_index = mk.slot_of(obj, chosen)


# --- The parts ------------------------------------------------------------------------------------------------

def muzzle(m):
    profile = [(x, r) for x, r in k.profile([(x, r) for x, r in MUZZLE], 0.25)]
    cap = lathe_x("muzzle", profile, m["muzzle_core"], segments=32)
    # Two hot bands between red rings, as the sprite's columns 1-5.
    paint_x(cap, [(-30.0, m["muzzle_core"]), (-22.0, m["muzzle_ring"]), (-21.35, m["muzzle_band"]),
                  (-20.1, m["muzzle_ring"])])
    k.smooth(cap, 50)
    for side in (-1, 1):  # the red knobs above and below it
        k.smooth(k.ellipsoid(f"knob{side}", (-19.6, AXIS_Y + side * 4.55, AXIS_Z + 0.2), (1.2, 0.95, 1.0), m["knob"],
                             14, 7), 60)


def receiver(m):
    x0, x1, r = RECEIVER
    profile = [(x0, r * 0.9), (x0 + 0.25, r), (x1 - 0.3, r), (x1, r * 0.92)]
    rings = []
    for x, rr in profile:
        rings.append(section(x, rr, 40, power=3.8))
    body = k.loft("receiver", rings, m["grey"], start_point=(x0 - 0.05, AXIS_Y, AXIS_Z), end_point=(x1, AXIS_Y, AXIS_Z))
    mk.paint(body, lambda c, n: m["grey_light"] if n.z > 0.75 else None)
    k.smooth(body, 35)
    # The grey ring at its front (column 6).
    ring = [(x0 - 0.65, r * 0.85), (x0 - 0.5, r * 1.04), (x0 + 0.4, r * 1.06), (x0 + 0.6, r * 0.9)]
    k.smooth(lathe_x("receiver_ring", ring, m["grey_light"], segments=36), 40)
    # The window in its top: a dark frame round brown inside.
    wx0, wx1, wy0, wy1 = WINDOW
    top = lambda x, y: AXIS_Z + SQUASH * r * 0.98 - 0.35  # noqa: E731
    facet("window_frame", resample(rounded_rect(wx0, wx1, AXIS_Y + wy0, AXIS_Y + wy1, 0.5), 0.45), top, 0.55,
          m["frame"], rim=0.25, steps=2, dome=0.0, dome_rings=1, sink=0.3)
    facet("window_inside", resample(rounded_rect(wx0 + 0.7, wx1 - 0.7, AXIS_Y + wy0 + 0.65, AXIS_Y + wy1 - 0.65,
                                                 0.3), 0.4), top, 0.42, m["inside"], rim=0.15, steps=1, dome=-0.1,
          dome_rings=1, sink=0.3)
    # Bars across the receiver's top either side of the window (the upscale's clamps).
    for i, x in enumerate((-9.2, -17.3)):
        line = [Vector((x, AXIS_Y + v, surface_z(x, AXIS_Y + v, r) + 0.05))
                for v in [-3.6 + 7.2 * j / 8 for j in range(9)]]
        tube(f"clamp{i}", line, [0.55] * len(line), m["grey_light"], segments=8, squash=0.7)


def collar(m):
    x0, x1, r = COLLAR
    profile = [(x0, r * 0.7), (x0 + 0.35, r * 0.96), (x0 + 0.9, r), (x1 - 0.9, r), (x1 - 0.35, r * 0.96),
               (x1, r * 0.75)]
    band = lathe_x("collar", profile, m["olive"], segments=40)
    paint_x(band, [(-99.0, m["olive"]), (x1 - 1.3, m["olive_dark"])])
    k.smooth(band, 40)


def fins(m):
    """The two swept armour fins, plates in the plane of the axis reaching up and down the screen, pink tips."""
    for side in (-1, 1):
        pts = [(x, AXIS_Y + side * d) for x, d in FIN]
        pts = pts + [(FIN[-1][0], AXIS_Y + side * FIN_ROOT), (FIN[0][0], AXIS_Y + side * FIN_ROOT)]
        outline = resample(chaikin(ccw(pts), 2), 0.45)
        thick = 1.5
        fin = facet(f"fin{side}", outline, lambda x, y: AXIS_Z - thick / 2, thick, m["olive"], rim=0.5, steps=2,
                    dome=0.1, dome_rings=1, sink=0.0)
        k.smooth(fin, 45)
        tip = [Vector((x, AXIS_Y + side * d, AXIS_Z + 0.2)) for x, d in FIN_TIP]
        path = [tip[0].lerp(tip[1], t / 6) for t in range(7)]
        tube(f"fin_tip{side}", path, [0.95] * len(path), m["pink_light"], segments=10, squash=0.85)


def body(m):
    x0, x1 = BODY_X
    xs = [x0 + (x1 - x0) * i / 56 for i in range(57)]
    xs = sorted(set([round(x, 3) for x in xs] + [BAND[0] - 0.3, BAND[0], BAND[1], BAND[1] + 0.3]))

    def crease(x):
        # The crease along the top fades out at both ends of the body.
        t = min(1.0, max(0.0, (x - 8.6) / 2.0)) * min(1.0, max(0.0, (22.0 - x) / 6.0))
        return CREASE_DEPTH * t * t * (3 - 2 * t)
    profile = [(x, BODY(x)) for x in xs]
    obj = lathe_x("body", profile, m["pink"], segments=40, crease=crease)
    k.smooth(obj, 50)
    # The raised band round its front, the glowing slits across it.
    b0, b1 = BAND
    band = [(b0 - 0.1, BODY(b0) * 0.98), (b0 + 0.3, BODY(b0 + 0.3) + 0.35), (b1 - 0.3, BODY(b1 - 0.3) + 0.35),
            (b1 + 0.1, BODY(b1) * 0.98)]
    k.smooth(lathe_x("band", band, m["pink_light"], segments=44), 40)
    for i, x in enumerate(SLITS):
        r = BODY(x) + 0.42
        pts = []
        for j in range(13):
            a = math.radians(32 + 116 * j / 12)
            pts.append(Vector((x, AXIS_Y + r * math.cos(a), AXIS_Z + SQUASH * r * math.sin(a) - 0.12)))
        tube(f"slit{i}", pts, [0.36] * len(pts), m["slit"], segments=8, squash=1.0)


def build_whole(m):
    muzzle(m)
    receiver(m)
    collar(m)
    fins(m)
    body(m)


# --- Checks and build -----------------------------------------------------------------------------------------

def masks(sheets):
    front = k.sprite_mask(os.path.join(sheets, "enemy_8.png"), 125)
    rear = k.sprite_mask(os.path.join(sheets, "enemy_8.png"), 127)
    return front, rear, [front[y] + rear[y] for y in range(28)]


def build():
    options = k.args()
    out = mk.outdir(options)
    k.reset()
    bpy.context.scene.view_settings.view_transform = "Standard"
    m = materials()
    build_whole(m)
    whole = mk.meshes()
    print("whole torpedo: %d triangles, %d objects" % (mk.triangles(whole), len(whole)))
    if "check" in options:
        front, rear, both = masks(options["check"])
        mk.compare("whole (8 125 beside 8 127)", mk.coverage(whole, 48, 28), both)
    if "preview" in options:
        mk.preview(options["preview"] + "pink_torpedo_whole", whole, size=(48, 28), scale=10, distance=1.4)
        bpy.context.view_layer.update()
    for name, sprite, box, centre_x in PIECES:
        parts = [p for p in (mk.cut(src, box, m["cut"]) for src in whole) if p is not None]
        mk.transform(parts, Matrix.Translation((-centre_x, 0.0, 0.0)))
        if "check" in options:
            mk.compare("%s (8 %d)" % (name, sprite), mk.coverage(parts, 24, 28), front if sprite == 125 else rear)
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts)
        for obj in parts:
            bpy.data.objects.remove(obj)


if __name__ == "__main__":
    build()
