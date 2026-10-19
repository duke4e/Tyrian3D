"""TYRIAN's long grey rods that push in from the screen's sides (sheet 2, 2x2 sprites, 24 x 28 pixels, not animated;
ground layers; enemies 18-23 of episodes 1 and 3: TYRIAN and TYRIAN X), polished (2026-10-19; it replaces
wave3_p.py's rod_whole(), its six pieces and their --whole preview). models.cfg: model rod_butt / rod_segment /
rod_tip / rod_tip_l / rod_segment_l / rod_butt_r ... origin; sprite 2 1 rod_butt yaw=0, sprite 2 3 rod_segment yaw=0,
sprite 2 5 rod_tip yaw=0, sprite 2 7 rod_tip_l yaw=0, sprite 2 9 rod_segment_l yaw=0, sprite 2 11 rod_butt_r yaw=0.

The events lay each rod out of sprites side by side on one row, 24 pixels apart: the rod from the left a butt (2 1,
enemy 23), a row of segments (2 3, enemy 22, seven of them in TYRIAN's events at 4930 and 4970) and a tip (2 5, enemy
21); the rod from the right a tip pointing left (2 7, enemy 18), segments (2 9, enemy 19) and a butt (2 11, enemy 20)
(events at 4912 and 4952). Their xcaccel (16, -16) swings them in and out from the sides. 7, 9 and 11 are 5, 3 and 1's
pixels mirrored (11 one pixel further right than an exact mirror image: left out, so that the butt meets the
segments), so the pieces from the right are the whole rod mirrored and cut again.

As the sprites and their 4x upscales draw it: a round rod lying across the screen (rows 7-18 with the outline: its
axis between rows 12 and 13, a radius of 5.65), made of grey barrel-shaped beads with dark joints between them, red
bands between beads (3 pixels wide, a pixel less round than the beads), a red collar standing out round it once a
segment (columns 3-6 of 2 3, rows 6-19: a radius of 6.65), the butt's collar bigger (columns 19-22 of 2 1, rows 5-20),
the collars' lower edges drawn open as the clamps' ears; the butt a long bead, its end rounded off to a dark end plate
(column 0); the tip a polished ogive, the full radius at its base (columns 0-5 of 2 5) narrowing to its point (column
20). Along a segment: the end of a bead (columns 0-2, it began in the previous segment's column 23), the collar
(3-6), a bead (7-11), a band (12-14), a bead (15-19), a band (20-22), the next bead's start (23). The butt: the long
bead (0-10), a band (11-13), a bead (14-18), the big collar (19-22), a bead's start (23).

The rod is built whole (a butt, three segments and a tip) and cut along the sprites' edges (polish_arch.py's cut(),
polish_redjet.py's method: the pieces keep the whole's shading across the cuts); the segment is the middle one, cut
through the beads that straddle its edges, so its two edges have the same cross-section (the profile repeats every
24 pixels) and any two pieces meet without a seam. The tip begins with the same bead start, so it meets a segment
too. The whole's features stand where the sprites draw them; each piece is moved so that its sprite's centre is its
origin. The rod lies on the ground: its axis 7.77 up, the butt's collar on the ground, the other collars' feet
reaching down to it.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground; the whole's x is
the picture's pixel edge (the butt's sprite covers 0-24), y as in a sprite (row r is y = 13.5 - r).

Replaces wave3_p.py's rods (2026-10-19: wave3_p.py, which built only them by then, and wave3_p_art.py's ROD were
removed; wave3_p_kit.py's mirror_all() stays: wave3_ap_miners.py uses it).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each piece's silhouette
against enemy_2.png), --preview <prefix> (the wholes' and each piece's top and 3/4 views), --only <name,...>.
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
from polish_arch import cut  # noqa: E402
from polish_redjet import Curve  # noqa: E402

R_BEAD, R_BAND, R_CORE = 5.65, 4.7, 3.6
R_COLLAR, R_COLLAR_BIG = 6.65, 7.65
COLLAR_CROWN = 0.12
AXIS_Y, AXIS_Z = 1.0, R_COLLAR_BIG + COLLAR_CROWN
SEGMENTS = 40                       # around the rod
N_SEG = 3                           # segments in the whole
TIP_X = 24.0 * (N_SEG + 1)          # the tip sprite's left edge
# The clamps' ears: how far round from the top they stand out (degrees, towards the bottom of the screen), their length.
EAR_ANGLE, EAR_LEN = 124.0, 2.0
# Bead ends: rounded on quarter ellipses BEAD_FX long and BEAD_FR deep; their middles bulge by BEAD_BULGE.
BEAD_FX, BEAD_FR, BEAD_BULGE = 1.45, 1.9, 0.12
# name, sprite, the box it covers in the whole (x0, x1, y0, y1), mirrored
PIECES = [("rod_butt", 1, (0.0, 24.0, -14.0, 14.0), False),
          ("rod_segment", 3, (48.0, 72.0, -14.0, 14.0), False),
          ("rod_tip", 5, (TIP_X, TIP_X + 24.0, -14.0, 14.0), False),
          ("rod_tip_l", 7, (-TIP_X - 24.0, -TIP_X, -14.0, 14.0), True),
          ("rod_segment_l", 9, (-72.0, -48.0, -14.0, 14.0), True),
          ("rod_butt_r", 11, (-24.0, 0.0, -14.0, 14.0), True)]
# The tip's ogive from its full radius (x from the tip sprite's left edge, radius), 2/3 into the outline pixels.
TIP_OGIVE = Curve([(4.0, R_BEAD), (4.6, 5.63), (5.4, 5.48), (6.5, 5.17), (8.0, 4.74), (10.0, 4.18), (12.0, 3.62),
                   (14.0, 3.05), (15.5, 2.6), (17.0, 2.1), (18.2, 1.66), (19.3, 1.17), (20.1, 0.7), (20.55, 0.32),
                   (20.8, 0.0)])
TIP_END = 20.8


def materials():
    return {
        "bead": k.material("rod_bead", palette=0x09, metallic=0.4, roughness=0.3),
        "joint": k.material("rod_joint", palette=0x04, metallic=0.5, roughness=0.38),
        "band": k.material("rod_band", palette=0x48, metallic=0.3, roughness=0.3),
        "collar": k.material("rod_collar", palette=0x49, metallic=0.3, roughness=0.28),
        "collar_dark": k.material("rod_collar_dark", palette=0x44, metallic=0.35, roughness=0.35),
        "core": k.material("rod_core", palette=0x02, metallic=0.4, roughness=0.5),
        "tip": k.material("rod_tip", palette=0x0b, metallic=0.65, roughness=0.14),
        "end": k.material("rod_end", palette=0x03, metallic=0.5, roughness=0.4),
        "bolt": k.material("rod_bolt", palette=0x07, metallic=0.6, roughness=0.3),
        "seam": k.material("rod_seam", palette=0x03, metallic=0.4, roughness=0.5),
    }


# --- Profiles ---------------------------------------------------------------------------------------------------

def bead_end(a, sign, steps=7):
    """A bead's rounded end at x = a (sign 1: its left end, rising to the right; -1: its right end), from the end
    inwards: [(x, radius)]."""
    out = []
    for i in range(steps + 1):
        t = (math.pi / 2) * i / steps
        out.append((a + sign * BEAD_FX * (1 - math.cos(t)), R_BEAD - BEAD_FR + BEAD_FR * math.sin(t)))
    return out


def bead_profile(a, b, bulge=BEAD_BULGE):
    """A barrel from x = a to b: rounded ends, its middle bulging a little."""
    left = bead_end(a, 1)
    right = bead_end(b, -1)[::-1]
    middle = []
    x0, x1 = left[-1][0], right[0][0]
    count = max(2, int(round((x1 - x0) / 0.6)))
    for i in range(1, count):
        u = i / count
        middle.append((x0 + (x1 - x0) * u, R_BEAD + bulge * math.sin(math.pi * u)))
    return left + middle + right


def butt_profile(a=0.33, b=11.0, face=3.3, fillet=2.3):
    """The butt's long bead: its left end rounded off to a flat end face (radius `face`), its right end a bead's."""
    out = [(a, face * f) for f in (0.0, 0.5, 0.85)]
    out.append((a, face))
    for i in range(1, 9):
        t = (math.pi / 2) * i / 8
        out.append((a + fillet * (1 - math.cos(t)), face + (R_BEAD - face) * math.sin(t)))
    right = bead_end(b, -1)[::-1]
    x0, x1 = out[-1][0], right[0][0]
    count = int(round((x1 - x0) / 0.8))
    for i in range(1, count):
        u = i / count
        out.append((x0 + (x1 - x0) * u, R_BEAD))
    return out + right


def band_profile(a, b, fillet=0.4):
    out = []
    for i in range(5):
        t = (math.pi / 2) * i / 4
        out.append((a + fillet * (1 - math.cos(t)), R_BAND - fillet + fillet * math.sin(t)))
    for i in range(4, -1, -1):
        t = (math.pi / 2) * i / 4
        out.append((b - fillet * (1 - math.cos(t)), R_BAND - fillet + fillet * math.sin(t)))
    return out


def tip_profile(a):
    """The tip from x = a - 1 (where the bead it replaces would begin, in the last segment's column 23): that bead's
    rounded start (the same rings: cut at x = a, the tip's edge has the segments' section and shading), its full
    radius, the ogive to the point."""
    out = bead_end(a - 1.0, 1)
    for x in (a + 1.1, a + 1.9, a + 2.8, a + 3.5):
        out.append((x, R_BEAD))
    xs = [4.0 + (TIP_END - 4.0) * (i / 28) ** 0.85 for i in range(29)]
    for x in xs:
        out.append((a + x, max(0.0, TIP_OGIVE(x))))
    return out


def lathe_x(name, profile, mat, segments=SEGMENTS, close=True):
    """A part turned about the rod's axis: profile [(x, radius)] along x; its ends closed on the axis."""
    rings = []
    for x, r in profile:
        r = max(r, 0.02)
        rings.append([Vector((x, AXIS_Y + r * math.sin(2 * math.pi * j / segments),
                              AXIS_Z + r * math.cos(2 * math.pi * j / segments))) for j in range(segments)])
    obj = k.loft(name, rings, mat, cap_start=close, cap_end=close,
                 start_point=(profile[0][0], AXIS_Y, AXIS_Z), end_point=(profile[-1][0], AXIS_Y, AXIS_Z))
    return obj


# --- Parts ------------------------------------------------------------------------------------------------------

def layout():
    """The whole's features along x: beads (a, b, kind), bands (a, b), collars (a, b, radius)."""
    beads = [(0.33, 11.0, "butt"), (14.0, 19.0, "bead")]
    bands = [(11.0, 14.0)]
    collars = [(19.0, 23.0, R_COLLAR_BIG)]
    for i in range(N_SEG):
        s = 24.0 * (i + 1)
        beads += [(s - 1.0, s + 3.0, "bead"), (s + 7.0, s + 12.0, "bead"), (s + 15.0, s + 20.0, "bead")]
        bands += [(s + 12.0, s + 15.0), (s + 20.0, s + 23.0)]
        collars.append((s + 3.0, s + 7.0, R_COLLAR))
    return beads, bands, collars


def bead(m, name, a, b, kind):
    prof = butt_profile(a, b) if kind == "butt" else bead_profile(a, b)
    obj = lathe_x(name, prof, m["bead"])
    k.smooth(obj, 50)

    def pick(c, n):
        if kind == "butt" and c.x < a + 0.05 and n.x < -0.9:
            return m["end"]
        if abs(n.x) > 0.62:
            return m["joint"]  # the rounded ends: the dark joints between the beads
        return None
    mk.paint(obj, pick)
    return obj


def band(m, name, a, b):
    obj = lathe_x(name, band_profile(a, b), m["band"])
    return k.smooth(obj, 50)


def collar(m, name, a, b, radius):
    """A red clamp ring round the rod, its edges rounded, a little crowned; under it, on its side towards the bottom
    of the screen, its two ears with a bolt through them (the sprite's collar drawn open below the rod), and a foot
    down to the ground."""
    made = []
    e = 0.55
    prof = [(a, R_CORE + 0.1), (a, radius - e)]
    for i in range(1, 6):
        t = (math.pi / 2) * i / 5
        prof.append((a + e * (1 - math.cos(t)), radius - e + e * math.sin(t)))
    mid = (a + b) / 2
    prof.append((mid, radius + COLLAR_CROWN))
    for i in range(5, -1, -1):
        t = (math.pi / 2) * i / 5
        prof.append((b - e * (1 - math.cos(t)), radius - e + e * math.sin(t)))
    prof.append((b, R_CORE + 0.1))
    ring = lathe_x(name, prof, m["collar"])
    k.smooth(ring, 45)
    made.append(ring)
    # The ears: the clamp's ends bent out from its lower side (towards the bottom of the screen, EAR_ANGLE round from
    # its top), either side of its split, the bolt through them across the split.
    ang = math.radians(EAR_ANGLE)
    u = Vector((0.0, -math.sin(ang), math.cos(ang)))         # out along the radius
    t = Vector((0.0, math.cos(ang), math.sin(ang)))          # across the split
    base = radius - 0.35
    place = Matrix.Translation((0.0, AXIS_Y + u.y * base, AXIS_Z + u.z * base)) @ Matrix.Rotation(ang, 4, "X")
    for i, (s0, s1) in enumerate(((-1.05, -0.32), (0.32, 1.05))):
        ear = mk.box(f"{name}_ear{i}", a + 0.35, b - 0.35, s0, s1, -0.4, EAR_LEN, m["collar"])
        mk.bevel(ear, 0.22, 2, 30)
        ear.data.transform(place)
        k.smooth(ear, 40)
        made.append(ear)
    centre = Vector((0.5 * (a + b), AXIS_Y, AXIS_Z)) + u * (base + EAR_LEN * 0.55)
    bolt = k.loft(f"{name}_bolt", [[centre + t * s_ + (Vector((1, 0, 0)) * math.cos(2 * math.pi * j / 10) +
                                                         u * math.sin(2 * math.pi * j / 10)) * 0.42 for j in range(10)]
                                   for s_ in (-1.35, 1.35)], m["bolt"])
    k.smooth(bolt, 50)
    made.append(bolt)
    for s_, r_ in ((1.35, 0.62), (-1.35, 0.55)):  # the nut and the bolt's head
        hexagon = [Vector((1, 0, 0)) * math.cos(2 * math.pi * j / 6) + u * math.sin(2 * math.pi * j / 6)
                   for j in range(6)]
        nut = k.loft(f"{name}_nut{s_:+.0f}", [[centre + t * (s_ + d) + h * r_ for h in hexagon] for d in (-0.3, 0.3)],
                     m["bolt"])
        made.append(nut)
    # The foot: a block from the ring's bottom down to the ground (the big collar stands on it itself).
    low = AXIS_Z - radius
    if low > 0.05:
        foot = mk.box(f"{name}_foot", a + 0.45, b - 0.45, AXIS_Y - 2.6, AXIS_Y + 2.6, 0.0, low + 0.6, m["collar_dark"])
        mk.bevel(foot, 0.25, 2, 30)
        k.smooth(foot, 35)
        made.append(foot)
    return made


def core(m, x0, x1):
    """The dark core inside, showing in the joints."""
    return k.smooth(lathe_x("core", [(x0, R_CORE), (x1, R_CORE)], m["core"]), 50)


def tip(m):
    obj = lathe_x("tip", tip_profile(TIP_X), m["tip"], segments=SEGMENTS)
    k.smooth(obj, 60)
    # Its base's bead start joins the beads: painted as a bead's joint where it rounds.
    mk.paint(obj, lambda c, n: m["joint"] if c.x < TIP_X + 0.3 and abs(n.x) > 0.62 else None)
    return obj


def end_boss(m):
    """A low boss on the butt's end plate."""
    rings = [[Vector((x, AXIS_Y + r * math.sin(2 * math.pi * j / 24), AXIS_Z + r * math.cos(2 * math.pi * j / 24)))
              for j in range(24)] for x, r in ((0.4, 2.0), (0.22, 1.95), (0.1, 1.72), (0.02, 1.15))]
    obj = k.loft("end_boss", rings, m["end"], start_point=(0.4, AXIS_Y, AXIS_Z), end_point=(0.0, AXIS_Y, AXIS_Z))
    return k.smooth(obj, 50)


def build_whole(m):
    beads, bands, collars = layout()
    for i, (a, b, kind) in enumerate(beads):
        bead(m, f"bead{i}", a, b, kind)
    for i, (a, b) in enumerate(bands):
        band(m, f"band{i}", a, b)
    for i, (a, b, r) in enumerate(collars):
        collar(m, f"collar{i}", a, b, r)
    core(m, 1.0, TIP_X + 3.0)
    tip(m)
    end_boss(m)
    whole = mk.meshes()
    for obj in whole:
        mk.apply(obj)
    bpy.context.view_layer.update()
    return whole


def mirrored(whole):
    """The whole mirrored about x = 0 (the rod from the right), as new objects."""
    out = []
    for obj in whole:
        copy = k.mirror_x(obj, obj.name + "_m")
        copy.data.name = copy.name
        out.append(copy)
    bpy.context.view_layer.update()
    return out


# --- Checks and build -------------------------------------------------------------------------------------------

def build():
    options = k.args()
    out = mk.outdir(options)
    k.reset()
    m = materials()
    whole = build_whole(m)
    mirror = mirrored(whole)
    bpy.context.scene.view_settings.view_transform = "Standard"
    sheet = os.path.join(options["check"], "enemy_2.png") if "check" in options else None
    for label, objects, others in (("rod", whole, mirror), ("rod_l", mirror, whole)):
        for o in others:
            o.hide_render = True
        low, high = mk.bounds(objects)
        print("== whole %s: %d triangles, %d objects, %d materials, x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (
            label, mk.triangles(objects), len(objects), len(mk.materials_of(objects)), low.x, high.x, low.y, high.y,
            low.z, high.z))
        if "preview" in options:
            mk.preview(options["preview"] + label + "_whole", objects, size=(120, 28), scale=6, distance=3.0,
                       centre=(60.0 if label == "rod" else -60.0, 0.0))
        for o in others:
            o.hide_render = False
    bpy.context.view_layer.update()  # (the previews moved the objects and back: their bounds again, for cut())
    only = options.get("only", "").split(",") if "only" in options else None
    for name, sprite, box, is_mirror in PIECES:
        if only and name not in only:
            continue
        source = mirror if is_mirror else whole
        pieces = [p for p in (cut(src, box, m["seam"]) for src in source) if p is not None]
        cx, cy = (box[0] + box[1]) / 2, (box[2] + box[3]) / 2
        mk.transform(pieces, Matrix.Translation((-cx, -cy, 0)))
        bpy.context.view_layer.update()
        for src in whole + mirror:
            src.hide_render = True
        if sheet:
            mk.compare("%s (2 %d)" % (name, sprite), mk.coverage(pieces, 24, 28), k.sprite_mask(sheet, sprite))
        mk.report(name, pieces, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, pieces)
        for obj in pieces:
            bpy.data.objects.remove(obj)
        for src in whole + mirror:
            src.hide_render = False


if __name__ == "__main__":
    build()
