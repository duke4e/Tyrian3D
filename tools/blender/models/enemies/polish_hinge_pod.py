"""The small steel pod of SOH JIN and GAUNTLET, drawn from two sprites of sheet A side by side (2x2 each): its left
half, 161, and its right half, 163, 24 pixels right of it (mirror images: the 48 x 28 picture is symmetric about
the edge between them; not animated), polished (2026-10-19; it replaces wave3_q.py's pod_whole(), a heightfield
half dome with ribs painted in the sprite's shades). models.cfg: model hinge_pod_l / hinge_pod_r ... origin; sprite
a 161 hinge_pod_l yaw=0, sprite a 163 hinge_pod_r yaw=0.

SOH JIN puts the halves side by side on the ground layer (custom ground enemies, graphic 161 at x and 163 at x + 24,
events 580-940), then pulls them apart: the left half accelerates to the left, the right one to the right
(event 20, excc -10 / +10), so each half must stand on its own; GAUNTLET sends single halves across the screen on
the top layer. So each half is a complete shell with half of the hinge on its flat side.

As the sprite draws it (columns and rows of the 48 x 28 picture; the left half, the right one mirrors it): a lens-
shaped shell (columns 6-22 of rows 6-21), pointed at its outer end (column 6, rows 13-14), 16 pixels deep where it
is widest (columns 15-20), narrower at its inner end by the hinge (rows 8-19 of columns 21-22); its back (up the
screen, rows 6-13) lit, carrying two raised ribs running up the screen (columns 15-17 and 19-20, their ridges the
sprite's brightest steel), its front (rows 15-21) a darker skirt falling away down the screen, a light band along
the crest between them (row 14); a dark eye near the outer end (columns 9-13 of rows 9-13), a glint at its upper
right; and between the halves the hinge (columns 23-24 of rows 9-18): a grey barrel with light rings, its ends
glowing red (row 9 and rows 17-18).

Built whole and cut along the sprites' edge (x = 0) into the two halves (polish_arch.py's cut(): they keep the
whole's shading across the cut; the barrel's halves get flat caps), each moved so that its sprite's centre is its
origin. The shell is a solid over its plan (polish_ring_machine.relief()) whose top follows the sections: a steep
round front up to a crest a little below the middle, a gentler slope at the back (the sun, from the upper left of
the screen, lights the back and leaves the front skirt dark, as the sprite shades them); the ribs are bars laid on
it, the eye a glossy lens in a socket rim, the barrel and its caps lathed.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground (z = 0); the
whole's x = 0 is the edge between the sprites, y = 0 its middle: a point (column, row) of the picture's pixel grid is
(c - 24, 14 - r).

Replaces wave3_q.py's pod: remove its section (POD_ORIGIN, POD_FLAT, POD_EYE, pod_whole() with its @q.whole("pod",
...) registration, pod_piece() and the loop registering hinge_pod_l / hinge_pod_r), the hinge_pod lines of its
docstring and "pod" from its --whole choices, and k from its wave3_q_kit import (only pod_whole() used it); and
wave3_q_art.py's CAPSULE (nothing else reads it).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the
whole and of each half against enemy_A.png), --preview <prefix> (the whole's and each half's views).
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
from polish_arch import cut  # noqa: E402
from polish_jets import Curve  # noqa: E402
from polish_ring_machine import ccw, relief  # noqa: E402

PIECES = [("hinge_pod_l", 161, (-24.0, 0.0, -14.0, 14.0)), ("hinge_pod_r", 163, (0.0, 24.0, -14.0, 14.0))]


# The left shell's plan: its half-depth in y along x (it is symmetric about y = 0): pointed at the outer end
# (x -17.95), 8 deep where widest (columns 15-20), 6 at the inner end by the hinge (columns 21-22).
HALF = Curve([(-17.95, 0.0), (-17.7, 0.75), (-17.0, 1.45), (-16.0, 2.45), (-15.0, 3.45), (-14.0, 4.4), (-13.0, 5.25),
              (-12.0, 5.95), (-11.0, 6.5), (-10.0, 7.15), (-9.0, 7.75), (-8.4, 7.93), (-4.0, 7.93), (-3.5, 7.8),
              (-3.0, 7.25), (-2.5, 6.55), (-2.0, 6.2), (-1.0, 6.05)])
TIP, INNER = -17.95, -1.0
# Its crest's height along x, and where the crest runs (y): a steep round front below it, a gentler back above.
CREST = Curve([(-17.95, 0.35), (-17.0, 1.55), (-16.0, 2.5), (-15.0, 3.3), (-14.0, 4.0), (-12.0, 5.0), (-10.0, 5.55),
               (-8.0, 5.85), (-6.0, 5.95), (-4.0, 5.85), (-3.0, 5.4), (-2.0, 4.6), (-1.0, 4.3)])
CREST_Y = -0.7
FRONT_POWER, BACK_POWER = 2.3, 1.55
LIGHT_BAND = (-1.6, 0.2)          # the crest's light band (y)
# The ribs on the back (x middle, half-width) from the back edge to the crest.
RIBS = [(-7.45, 1.15), (-4.05, 0.8)]
RIB_PROUD = 0.5
# The eye: its middle (x, y), radius; the glint.
EYE = (-12.55, 3.15, 1.85)
GLINT = (-11.6, 4.4, 0.42)
# The hinge: the barrel along y at x = 0 (height of its axis, radius, from, to), its light rings (y), its red caps
# (from, to along y; the bottom one longer, as the sprite draws it).
HINGE_Z, HINGE_R = 3.15, 1.08
HINGE_Y = (-4.2, 4.15)
RINGS = (2.35, 0.2, -1.6)
CAP_TOP = (4.15, 5.0)
CAP_BOTTOM = (-4.95, -2.95)


def materials():
    glow = k.level_palette()
    steel = dict(metallic=0.5, roughness=0.32)
    return {
        "shell": k.material("hpod_shell", palette=0x6a, **steel),
        "shell_dark": k.material("hpod_shell_dark", palette=0x67, **steel),
        "band": k.material("hpod_band", palette=0x6b, **steel),
        "rib": k.material("hpod_rib", palette=0x6d, metallic=0.55, roughness=0.24),
        "socket": k.material("hpod_socket", palette=0x64, metallic=0.4, roughness=0.4),
        "eye": k.material("hpod_eye", palette=0x61, metallic=0.3, roughness=0.06),
        "glint": k.material("hpod_glint", palette=0x6d, metallic=0.1, roughness=0.1, emission=glow[0x6c],
                            emission_strength=0.6),
        "hinge": k.material("hpod_hinge", palette=0x0a, metallic=0.65, roughness=0.25),
        "hinge_dark": k.material("hpod_hinge_dark", palette=0x07, metallic=0.6, roughness=0.3),
        "red": k.material("hpod_red", palette=0x74, metallic=0.1, roughness=0.3, emission=glow[0x75],
                          emission_strength=1.3),
        "red_dark": k.material("hpod_red_dark", palette=0x72, metallic=0.1, roughness=0.35, emission=glow[0x73],
                               emission_strength=1.0),
        "seam": k.material("hpod_seam", palette=0x62, metallic=0.4, roughness=0.5),
    }


# --- The shell ---------------------------------------------------------------------------------------------------

def shell_z(x, y):
    """The left shell's top at (x, y) (x < 0)."""
    w = max(HALF(x), 0.05)
    h = CREST(x)
    yc = CREST_Y * min(1.0, w / 3.0)
    if y <= yc:
        t = min(1.0, (yc - y) / max(w + yc, 0.05))
        p = FRONT_POWER
    else:
        t = min(1.0, (y - yc) / max(w - yc, 0.05))
        p = BACK_POWER
    return h * max(0.0, 1.0 - t ** p) ** (1.0 / p)


def shell_outline():
    """The left shell's plan: from the pointed tip along the front edge to the inner end and back along the back
    edge (denser towards the tip, where it curves)."""
    xs = [TIP + (INNER - TIP) * (1 - math.cos(math.pi * i / 2 / 40)) for i in range(41)]
    xs = sorted(set([round(x, 4) for x in xs] + [round(TIP + (INNER - TIP) * i / 60, 4) for i in range(61)]))
    front = [(x, -HALF(x)) for x in xs if x > TIP]
    back = [(x, HALF(x)) for x in reversed(xs) if x > TIP]
    return ccw([(TIP, 0.0)] + front + back)


def shell(m):
    poly = shell_outline()

    def height(x, y, d):
        return max(0.22, shell_z(x, y))

    def paint(x, y, d):
        if LIGHT_BAND[0] < y < LIGHT_BAND[1] and x < -3.2:
            return "band"
        if y < LIGHT_BAND[0] - 3.6:
            return "shell_dark"
        return "shell"
    obj = relief("shell", [poly], height, m, paint=paint, side="shell_dark", bottom=0.0, spacing=0.36,
                 borders=[(lambda x, y, d: y, LIGHT_BAND[0]), (lambda x, y, d: y, LIGHT_BAND[1]),
                          (lambda x, y, d: y, LIGHT_BAND[0] - 3.6)], smooth_angle=60.0)
    return obj


def ribs(m, hit):
    out = []
    for i, (xr, hw) in enumerate(RIBS):
        y0, y1 = HALF(xr) - 0.55, CREST_Y + 0.9
        points, ups = [], []
        for j in range(13):
            y = y0 + (y1 - y0) * j / 12
            h = hit(xr, y)
            points.append(Vector((xr, y, h[0].z if h else shell_z(xr, y))))
            ups.append(h[1] if h else Vector((0, 0, 1)))
        bar = mk.bar(f"rib{i}", points, ups, hw, RIB_PROUD, 0.5, m["rib"], 20, 2.0)
        # Rounded off at its ends.
        for v in bar.data.vertices:
            t = (v.co.y - y1) / (y0 - y1)
            f = min(1.0, t / 0.08, (1 - t) / 0.08) if 0 <= t <= 1 else 0.0
            h = hit(v.co.x, v.co.y)
            base = h[0].z if h else shell_z(v.co.x, v.co.y)
            if v.co.z > base:
                v.co.z = base + (v.co.z - base) * (0.35 + 0.65 * math.sqrt(max(0.0, f)))
        bar.data.update()
        k.smooth(bar, 70)
        out.append(bar)
    return out


def eye(m, hit):
    ex, ey, r = EYE
    h = hit(ex, ey)
    z = h[0].z if h else shell_z(ex, ey)
    rim = k.lathe("eye_rim", [(-0.45, r + 0.05), (-0.25, r + 0.4), (0.05, r + 0.38), (0.15, r - 0.1)], m["socket"], 32)
    rim.data.transform(Matrix.Translation((ex, ey, z - 0.1)) @ Matrix.Rotation(math.radians(90), 4, "X"))
    k.smooth(rim, 45)
    lens = mk.ball("eye", (ex, ey, z - 0.35), (r - 0.1, r - 0.1, 0.85), m["eye"], 28, 12)
    gx, gy, gr = GLINT
    glint = mk.ball("glint", (gx, gy, (z + 0.35)), (gr, gr, gr * 0.6), m["glint"], 12, 6)
    return [rim, lens, glint]


def hinge(m):
    y0, y1 = HINGE_Y
    barrel = k.lathe("hinge", [(y0, HINGE_R * 0.9), (y0 + 0.15, HINGE_R), (y1 - 0.15, HINGE_R), (y1, HINGE_R * 0.9)],
                     m["hinge"], 24, axis_x=0.0, axis_z=HINGE_Z)
    k.smooth(barrel, 40)
    out = [barrel]
    for i, y in enumerate(RINGS):
        ring = k.lathe(f"hinge_ring{i}", [(y - 0.3, HINGE_R - 0.02), (y - 0.18, HINGE_R + 0.2),
                                          (y + 0.18, HINGE_R + 0.2), (y + 0.3, HINGE_R - 0.02)],
                       m["hinge_dark"] if i == 1 else m["hinge"], 24, axis_x=0.0, axis_z=HINGE_Z)
        out.append(k.smooth(ring, 40))
    # The red caps: glowing, rounded at their outer ends.
    a, b = CAP_TOP
    prof = [(a - 0.1, HINGE_R * 0.95), (a + 0.2, HINGE_R + 0.06)]
    for j in range(1, 6):
        t = (math.pi / 2) * j / 6
        prof.append((a + 0.2 + (b - a - 0.2) * math.sin(t), (HINGE_R + 0.06) * math.cos(t) ** 0.7))
    out.append(k.smooth(k.lathe("cap_top", prof, m["red"], 24, axis_x=0.0, axis_z=HINGE_Z), 50))
    a, b = CAP_BOTTOM
    prof = []
    for j in range(6):
        t = (math.pi / 2) * (5 - j) / 6
        prof.append((b - 0.2 - (b - a - 0.2) * math.sin(t), (HINGE_R + 0.06) * math.cos(t) ** 0.7))
    prof += [(b - 0.2, HINGE_R + 0.06), (b + 0.1, HINGE_R * 0.95)]
    cap = k.lathe("cap_bottom", prof, m["red"], 24, axis_x=0.0, axis_z=HINGE_Z)
    mk.paint(cap, lambda c, n: m["red_dark"] if c.y < (a + b) / 2 - 0.3 else None)
    out.append(k.smooth(cap, 50))
    return out


# --- Build -------------------------------------------------------------------------------------------------------

def build_whole():
    k.reset()
    m = materials()
    body = shell(m)
    bpy.context.view_layer.update()
    hit = mk.surface([body])
    ribs(m, hit)
    eye(m, hit)
    left = mk.meshes()
    for obj in left:
        mk.apply(obj)
        mirror = k.mirror_x(obj, obj.name + "_r")
        mirror.data.name = mirror.name
    hinge(m)
    whole = mk.meshes()
    for obj in whole:
        mk.apply(obj)
    return whole, m


def whole_mask(sheet):
    left, right = k.sprite_mask(sheet, 161), k.sprite_mask(sheet, 163)
    return [a + b for a, b in zip(left, right)]


def build():
    options = k.args()
    outdir = mk.outdir(options)
    sheets = options.get("check")
    sheet = (os.path.join(sheets, "enemy_A.png") if os.path.isdir(sheets) else sheets) if sheets else None
    whole, m = build_whole()
    low, high = mk.bounds(whole)
    print("== whole pod (A 161 | 163): %d triangles, %d objects, %d materials, x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f"
          % (mk.triangles(whole), len(whole), len(mk.materials_of(whole)), low.x, high.x, low.y, high.y, low.z, high.z))
    if sheet:
        mk.compare("whole (A 161 | 163)", mk.coverage(whole, 48, 28), whole_mask(sheet))
    bpy.context.scene.view_settings.view_transform = "Standard"
    if "preview" in options:
        mk.preview(options["preview"] + "hinge_pod_whole", whole, size=(48, 28), scale=10, distance=1.6)
    for name, sprite, box in PIECES:
        pieces = [p for p in (cut(src, box, m["seam"]) for src in whole) if p is not None]
        mk.transform(pieces, Matrix.Translation((-(box[0] + box[1]) / 2, 0.0, 0.0)))
        for o in whole:
            o.hide_render = True
        if sheet:
            mk.compare("%s (A %d)" % (name, sprite), mk.coverage(pieces, 24, 28), k.sprite_mask(sheet, sprite))
        bpy.context.view_layer.update()
        mk.report(name, pieces, os.path.join(outdir, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, pieces)
        for o in pieces:
            bpy.data.objects.remove(o)
        for o in whole:
            o.hide_render = False


if __name__ == "__main__":
    build()
