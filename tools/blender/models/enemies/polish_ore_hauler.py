"""The ore hauler of ASTEROID2 and AST ROCK (sheet D sprite 115, 2x2: 24 x 28 pixels; enemies 283 (ASTEROID2, armour 8)
and 1080 (AST ROCK, armour 10), the sky), polished (2026-10-22, round 37; it replaces wave2_g.py's ore_hauler(), parts
inflated from the sprite's regions). models.cfg: model ore_hauler enemies/ore_hauler.glb (unchanged); sprite d 115
ore_hauler yaw=0 (unchanged; the sky: the game centres it in height).

Where the levels send it (the level events, tools/content/tyrevents.py; the enemy data, tools/content/tyrdata.py): four in
ASTEROID2 and one in AST ROCK, flying down the screen (ymove 2 and 3) and firing (283: gun 5; 1080: gun 116 every 10
ticks). One frame; no other enemy shows D 115; no twin. Not in episode 6.

As the sprite and its 4x upscale draw it (columns and rows; ramps 10 (browns 0xa0-0xaf) and 7 (reds and yellows
0x70-0x7e)): a hauler flying down the screen, nose first: a heavy crossbar at its back (columns 2-22, rows 2-7), a red-hot
light bar glowing over its middle behind it (columns 7-16, rows 0-1); from the crossbar a keeled spine running down to
a point (columns 8-17 narrowing to 11-13 at row 26), a pale ridge down its middle (columns 12-14) between dark grooves,
dark vents on it (rows 9-11); along both sides of the spine red engine pods (columns 4-7 and 18-21, rows 8-21) glowing
yellow-hot in places (0x7a-0x7e: the left one at rows 13-17, the right one at rows 14-17, both at row 10).

Built for the game's camera in the picture's plane (polish_asteroid_kit; sheared y - z tan 20 afterwards): the crossbar a
bevelled bar with rounded ends and bolts; the spine a hull lofted from rounded sections across it (SPINE: its half width
and height along it, falling to the point), its ridge a bar on it, its grooves and vents dark inlays; the pods long
capsules lofted along the spine's sides (PODS), red, lit and shaded by the game's sun, their hot spots glowing inlays
(HOT: 0x7a 0.4, 0x7c 0.5, 0x7e 0.6); the light bar a glowing red capsule (0x76, 0.45) half under the crossbar. Its
underside rounded (it flies): the hull's sections are closed below, a little flatter. Every face is triangulated.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the origin is the
sprite's middle (column c's left edge x = c - 12, row r's top edge y = 14 - r). The game centres it in height.

Replaces wave2_g.py's section "D 115: the ore hauler" (ore_hauler()); with it wave2_g.py builds nothing: it goes, and so
does wave2_g_art.py (D115 and V38, read by nothing else); wave1_d_shapes.py stays (many kits import it).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (its outline as the camera sees
it against its sprite), --preview <prefix>.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_asteroid_kit as ak  # noqa: E402

BAR = (-10.0, 11.0, 5.4, 12.4)         # the crossbar (x0, x1, y0, y1): columns 2-22, rows 2-8
BAR_Z = (-2.4, 3.0)                    # its underside and top (the hull's middle plane at z 0)
GLOW = ((-5.0, 13.0), (5.0, 13.0), 1.2, 0.9)   # the light bar: its ends (x, y), radius, how high its axis stands
# The spine: (y, half width, top height, underside depth) from the crossbar down to its point.
SPINE = [(7.2, 5.6, 3.0, 1.9), (4.0, 5.6, 3.2, 2.0), (0.0, 5.5, 3.2, 2.0), (-4.0, 5.2, 3.0, 1.9), (-7.0, 4.6, 2.8, 1.7),
         (-9.0, 3.8, 2.5, 1.5), (-10.8, 2.7, 2.1, 1.2), (-12.0, 1.6, 1.6, 0.9), (-12.8, 0.4, 1.0, 0.5)]
SPINE_X = 1.0                          # its middle (columns 12-13)
RIDGE = (1.2, 0.9)                     # the ridge's middle (x) and half width
# The pods: (x of their axis, y from, y to, radius); the hot spots: (x, y, radii, palette index, glow).
PODS = [(-5.0, 5.8, -9.8, 2.75), (7.0, 5.8, -9.2, 2.75)]
HOT = [(-5.8, 3.6, (1.1, 1.1), 0x7b, 0.45), (7.6, 3.6, (1.0, 1.0), 0x7a, 0.42), (-6.0, -2.6, (1.4, 2.6), 0x79, 0.4),
       (-6.0, -2.6, (0.9, 1.6), 0x7e, 0.6), (7.9, -2.4, (1.3, 2.2), 0x79, 0.4), (7.9, -2.4, (0.8, 1.3), 0x7c, 0.52)]
VENTS = [(-1.6, 4.1), (3.8, 4.1), (-1.6, 2.6), (3.8, 2.6)]   # dark vents on the spine (x, y)


def materials():
    def m(name, index, metallic=0.45, roughness=0.4, glow=0.0, glow_index=None):
        return ak.pal("hauler_" + name, index, metallic, roughness, glow, glow_index)
    out = {"brown": m("brown", 0xa7), "brown_lit": m("brown_lit", 0xaa, 0.45, 0.35), "brown_dark": m("brown_dark", 0xa4),
           "ridge": m("ridge", 0xac, 0.45, 0.32), "groove": m("groove", 0xa2, 0.3, 0.6),
           "red": m("red", 0x74, 0.25, 0.35, 0.1), "red_lit": m("red_lit", 0x77, 0.25, 0.3, 0.15),
           "red_dark": m("red_dark", 0x72, 0.25, 0.4, 0.06), "light": m("light", 0x76, 0.0, 0.3, 0.45, 0x78),
           "vent": m("vent", 0x01, 0.1, 0.8)}
    for x, y, r, index, glow in HOT:
        out["hot_%x" % index] = m("hot_%x" % index, index, 0.0, 0.3, glow)
    return out


def lit(obj, light, base, dark, t=(0.78, 0.35)):
    mk.paint(obj, lambda c, n: light if ak.sunlit(n) > t[0] else base if ak.sunlit(n) > t[1] else dark)


def crossbar(m):
    x0, x1, y0, y1 = BAR
    outline = []
    for i in range(9):                          # rounded ends (half circles of the bar's half depth)
        a = math.pi / 2 + math.pi * i / 8
        outline.append((x0 + (y1 - y0) / 2 + (y1 - y0) / 2 * math.cos(a), (y0 + y1) / 2 + (y1 - y0) / 2 * math.sin(a)))
    for i in range(9):
        a = -math.pi / 2 + math.pi * i / 8
        outline.append((x1 - (y1 - y0) / 2 + (y1 - y0) / 2 * math.cos(a), (y0 + y1) / 2 + (y1 - y0) / 2 * math.sin(a)))
    bar = mk.prism("crossbar", outline, BAR_Z[0], BAR_Z[1], m["brown"])
    k.recalc_normals(bar)
    mk.bevel(bar, 1.1, 3, 30)
    mk.shade(bar, 35)
    lit(bar, m["brown_lit"], m["brown"], m["brown_dark"])
    parts = [bar]
    for i, x in enumerate((x0 + 2.2, x1 - 2.2)):
        parts.append(mk.dome("bolt%d" % i, (x, (y0 + y1) / 2 + 0.3), (1.0, 1.0, 0.6), BAR_Z[1] - 0.1, m["ridge"], 16, 4))
    (ax, ay), (bx, by), r, z = GLOW
    glow = ak.beam("light_bar", (ax, ay, z), (bx, by, z), ak.disc_profile(r, 16, 0.8), (0, 0, 1), m["light"])
    k.smooth(glow, 60)
    parts.append(glow)
    for i, x in enumerate((ax, bx)):
        parts.append(mk.ball("light_end%d" % i, (x, ay, z), (r, r, r * 0.8), m["light"], 14, 7))
    return parts


def spine(m):
    sections = []
    around = 20
    for y, hw, top, under in SPINE:
        ring = []
        for j in range(around):
            a = 2 * math.pi * j / around
            c, s = math.cos(a), math.sin(a)
            sx = math.copysign(abs(c) ** 0.7, c)
            z = (top if s > 0 else under) * math.copysign(abs(s) ** 0.9, s)
            ring.append((SPINE_X + hw * sx, y, z))
        sections.append(ring)
    tip = (SPINE_X, SPINE[-1][0] - 0.6, 0.0)
    obj = k.loft("spine", sections, m["brown"], cap_start=True, cap_end=True,
                 start_point=(SPINE_X, SPINE[0][0] + 0.5, 0.0), end_point=tip)
    k.smooth(obj, 50)

    def pick(c, n):
        if abs(c.x - RIDGE[0]) < RIDGE[1] + 1.4 and abs(c.x - RIDGE[0]) > RIDGE[1] + 0.4 and n.z > 0.6 and c.y > -10.0:
            return m["groove"]
        return m["brown_lit"] if ak.sunlit(n) > 0.8 else m["brown"] if ak.sunlit(n) > 0.35 else m["brown_dark"]
    mk.paint(obj, pick)
    parts = [obj]
    ridge_top = SPINE[1][2]
    ridge = ak.beam("ridge", (RIDGE[0], 7.0, ridge_top - 0.2), (RIDGE[0], -10.8, 1.9),
                    ak.round_profile(RIDGE[1], 8, 0.7, below=0.8), (0, 0, 1), m["ridge"])
    k.smooth(ridge, 50)
    parts.append(ridge)
    for i, (x, y) in enumerate(VENTS):
        parts.append(mk.box("vent%d" % i, x - 0.7, x + 0.7, y - 0.35, y + 0.35, 2.6, 3.3, m["vent"]))
    return parts


def pods(m):
    parts = []
    for i, (x, y0, y1, r) in enumerate(PODS):
        rings = []
        n = 9
        for q in range(n):
            t = q / (n - 1)
            y = y0 + (y1 - y0) * t
            rr = r * (0.55 + 0.45 * math.sin(math.pi * min(1.0, 0.15 + 0.85 * t))) if t < 0.5 else \
                r * (0.35 + 0.65 * math.sin(math.pi * t))
            rings.append([Vector((x + rr * math.cos(2 * math.pi * j / 20), y, 0.4 + rr * 1.05 *
                                  math.sin(2 * math.pi * j / 20))) for j in range(20)])
        pod = k.loft("pod%d" % i, rings, m["red"], start_point=(x, y0 + 0.5, 0.4), end_point=(x, y1 - 0.6, 0.4))
        k.smooth(pod, 60)
        lit(pod, m["red_lit"], m["red"], m["red_dark"], (0.75, 0.3))
        parts.append(pod)
    for i, (x, y, (rx, ry), index, glow) in enumerate(HOT):
        pod = min(PODS, key=lambda p: abs(p[0] - x))
        z = 0.4 + pod[3] * 1.0 + 0.05 * i
        parts.append(mk.ball("hot%d" % i, (x, y, z - 0.35), (rx, ry, 0.5), m["hot_%x" % index], 16, 6))
    return parts


def build():
    options = k.args()
    out = mk.outdir(options)
    k.reset()
    bpy.context.scene.view_settings.view_transform = "Standard"
    m = materials()
    parts = crossbar(m) + spine(m) + pods(m)
    mask = k.sprite_mask(os.path.join(options["check"], "enemy_D.png"), 115) if "check" in options else None
    ak.finish("ore_hauler", parts, (0.0, 0.0), out, options, mask, label="ore_hauler (D 115) as the camera sees it")


if __name__ == "__main__":
    build()
