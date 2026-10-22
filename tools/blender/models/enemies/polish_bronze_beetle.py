"""ASTEROID?'s bronze beetle (sheet D sprite 16, 2x2: 24 x 28 pixels; enemy 461, armour 20, worth 20), polished (2026-10-22,
round 37; it replaces wave3_j.py's bronze_beetle(), a lathed body between two blocks with tube legs). models.cfg: model
bronze_beetle enemies/bronze_beetle.glb (unchanged) gets origin; sprite d 16 bronze_beetle yaw=0 height=-4.

Where the level puts it (ASTEROID?'s events, tools/content/tyrevents.py; the enemy data, tools/content/tyrdata.py): three
times at its start (t20 x 100, t40 x 180, t50 x 140; event 6, the ground, 20 pixels higher than usual, vy +2), crawling
down the screen over the floor (its ymove 1 and the event's 2) and pushed about by the events' global moves (links 15,
17, 19). One frame, no gun, no launch; no other enemy shows D 16; no twin (no sprite is its pixels mirrored, turned or
recoloured). Not in episode 6.

As the sprite and its 4x upscale draw it (columns and rows; ramps 1 (bronze 0x13-0x1d), 4 (reds 0x41-0x4b), 2 (greens
0x22-0x25) and 7 (0x73-0x75)): a beetle crawling down the screen, its back up the screen: two wing cases (columns 3-8 and
15-20, rows 1-16), each a bronze frame round two red panes (rows 3-8 and 10-14) parted by a bronze bar (row 9), their
tips pointed at the top; between them its body (columns 9-14), a bronze ridge down its middle, a red cap at its top end
(rows 3-5); under its front a pink plate (rows 13-16) with a dark hole (columns 11-12 of rows 15-16, the ground showing
through); from its front two hooked legs curving out and down to their points (rows 17-27; bronze outside, green
inside), a bronze bar between their roots (row 18), red claws inside them (row 21).

Built for the game's camera in the picture's plane (polish_asteroid_kit: x, y as the sprite draws them, z up; sheared y -
z tan 20 so that the camera sees every point where the sprite draws it): the wing cases bevelled prisms from the
sprite's outlines (CASE), their red panes inset in them, inside a bronze frame (PANES); the body a long dome (BODY) with the ridge, the cap a red
dome glowing a little; the plate a bevelled prism round the hole (a black floor in it); the legs round tubes along
curves (LEGS: points, radii), painted bronze where the game's sun reaches them and green on their inner sides, the claws
small red cones, the bar between them a tube. Mirrored about x = 0 (the sprite's columns 11 | 12).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground; the origin is the
sprite's middle (column c's left edge x = c - 12, row r's top edge y = 14 - r). Its feet at z 0 (origin; height=-4 sets
it on the terrain under it).

Replaces wave3_j.py (all of it: the beetle was all it still built; its kit wave3_j_kit.py and pixels wave3_j_art.py stay
if other scripts import them).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (its outline as the camera sees
it against its sprite), --preview <prefix>.
"""
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

# The left wing case's outline in the plane (pixel edges; the right one mirrored), its top and its panes' outlines.
CASE = [(-5.8, 13.0), (-7.4, 11.6), (-9.0, 9.8), (-9.0, 0.4), (-8.0, -1.5), (-6.4, -2.4), (-3.6, -1.8), (-3.0, -0.2),
        (-3.0, 11.2), (-3.5, 12.6), (-4.3, 13.0)]
CASE_TOP = 3.4
PANES = [[(-8.3, 10.2), (-8.3, 5.3), (-3.6, 5.3), (-3.6, 11.3), (-5.2, 12.1), (-6.6, 11.6)],
         [(-8.3, 3.9), (-8.3, 0.2), (-7.4, -1.3), (-3.6, -1.0), (-3.6, 3.9)]]
PANE_PROUD = 0.12                              # the panes stand this far over the case's top, inside its frame
BODY = ((0.0, 4.4), (3.1, 6.8), 4.6)          # the body: its middle, radii, height
CAP = ((0.0, 9.2), (2.5, 1.9), 4.4)           # the red cap at its top end (rows 3-6)
PLATE = [(-3.6, 1.1), (3.6, 1.1), (4.0, -0.6), (3.4, -3.6), (-3.4, -3.6), (-4.0, -0.6)]
HOLE = (-1.0, 1.0, -3.0, -1.0)                # the hole in the plate (x0, x1, y0, y1)
PLATE_Z = (0.4, 2.6)
# The left leg: points (x, y in the plane, z) and radii, from its root under the case to its point.
LEG = [(-4.4, -2.2, 2.0, 1.5), (-5.4, -3.6, 2.0, 1.75), (-6.4, -5.4, 1.9, 1.85), (-6.9, -7.4, 1.8, 1.8),
       (-6.0, -9.4, 1.6, 1.7), (-4.4, -11.4, 1.3, 1.45), (-3.6, -12.9, 0.9, 0.95), (-3.3, -13.8, 0.6, 0.35)]
CLAW = ((-2.4, -7.0, 1.0), (-1.6, -8.4, 0.7))  # a red claw inside each leg: root and tip (x, y, z), radius 0.45
BAR = ((-3.0, -4.4, 1.6), (3.0, -4.4, 1.6), 0.75)
JAW = ((-1.5, -5.7, 1.2), (1.5, -5.7, 1.2), 0.6)   # the mouth parts between the legs' roots (row 19)


def materials():
    def m(name, index, metallic=0.55, roughness=0.35, glow=0.0, glow_index=None):
        return ak.pal("beetle_" + name, index, metallic, roughness, glow, glow_index)
    return {"bronze": m("bronze", 0x18), "bronze_lit": m("bronze_lit", 0x1b, 0.55, 0.3),
            "bronze_dark": m("bronze_dark", 0x15), "red": m("red", 0x45, 0.2, 0.35),
            "red_lit": m("red_lit", 0x48, 0.2, 0.3), "pink": m("pink", 0x49, 0.2, 0.4),
            "cap": m("cap", 0x75, 0.1, 0.3, 0.25, 0x76), "green": m("green", 0x25, 0.4, 0.4),
            "claw": m("claw", 0x74, 0.2, 0.35, 0.18), "dark": m("dark", 0x01, 0.1, 0.8)}


def mirror_points(points):
    return [(-x, y) for x, y in reversed(points)]


def lit_paint(obj, lit, base, dark, threshold=(0.75, 0.35)):
    """Faces painted by how the game's sun lights them (the plane's normals sheared)."""
    mk.paint(obj, lambda c, n: lit if ak.sunlit(n) > threshold[0] else base if ak.sunlit(n) > threshold[1] else dark)


def cases(m):
    parts = []
    for side in (-1, 1):
        outline = CASE if side < 0 else mirror_points(CASE)
        case = mk.prism("case%d" % side, outline, 0.0, CASE_TOP, m["bronze"])
        k.recalc_normals(case)
        mk.bevel(case, 0.5, 2, 35)
        mk.shade(case, 35)
        lit_paint(case, m["bronze_lit"], m["bronze"], m["bronze_dark"])
        parts.append(case)
        for i, pane in enumerate(PANES):
            pts = pane if side < 0 else mirror_points(pane)
            p = mk.prism("pane%d_%d" % (side, i), pts, CASE_TOP - 0.6, CASE_TOP + PANE_PROUD, m["red"])
            k.recalc_normals(p)
            mk.bevel(p, 0.25, 2, 35)
            mk.shade(p, 35)
            lit_paint(p, m["red_lit"], m["red"], m["red"], (0.8, 0.0))
            parts.append(p)
    return parts


def domes(m):
    (bx, by), (rx, ry), h = BODY
    body = mk.dome("body", (bx, by), (rx, ry, h), 0.0, m["bronze"], 36, 10)
    lit_paint(body, m["bronze_lit"], m["bronze"], m["bronze_dark"], (0.78, 0.3))
    ridge = ak.beam("ridge", (0.0, by - ry * 0.85, h * 0.55), (0.0, by + ry * 0.55, h * 0.97),
                    ak.round_profile(0.55, 8, 0.7, below=1.0), (0, 0, 1), m["bronze_lit"])
    (cx, cy), (crx, cry), ch = CAP
    cap = mk.dome("cap", (cx, cy), (crx, cry, ch), 0.0, m["cap"], 28, 8)
    return [body, ridge, cap]


def plate(m):
    obj = mk.prism("plate", PLATE, PLATE_Z[0], PLATE_Z[1], m["pink"])
    k.recalc_normals(obj)
    mk.bevel(obj, 0.35, 2, 35)
    mk.shade(obj, 35)
    lit_paint(obj, m["pink"], m["pink"], m["red"], (0.8, 0.3))
    x0, x1, y0, y1 = HOLE
    hole = mk.box("hole", x0, x1, y0 - 0.05, y1, PLATE_Z[0] - 0.1, PLATE_Z[1] + 0.06, m["dark"])
    return [obj, hole]


def legs(m):
    parts = []
    for side in (-1, 1):
        pts = [Vector((side * x, y, z)) for x, y, z, _ in LEG]
        radii = [r for *_, r in LEG]
        leg = mk.tube("leg%d" % side, pts, 1.0, m["bronze"], 14, radii=radii)
        mid = Vector((0.0, -8.0, 0.0))

        def pick(c, n, side=side):
            inward = (mid - c)
            inward.z = 0
            if inward.length > 1e-6 and n.dot(inward.normalized()) > 0.1 and n.z < 0.85:
                return m["green"]
            return m["bronze_lit"] if ak.sunlit(n) > 0.78 else m["bronze"] if ak.sunlit(n) > 0.3 else m["bronze_dark"]
        mk.paint(leg, pick)
        k.smooth(leg, 60)
        parts.append(leg)
        (a, b) = CLAW
        claw = mk.tube("claw%d" % side, [Vector((side * a[0], a[1], a[2])), Vector((side * b[0], b[1], b[2]))], 0.45,
                       m["claw"], 10, radii=[0.5, 0.12])
        parts.append(claw)
    for name, (p0, p1, r) in (("bar", BAR), ("jaw", JAW)):
        bar = mk.tube(name, [Vector(p0), Vector(p1)], r, m["bronze_dark"], 12)
        lit_paint(bar, m["bronze_lit"], m["bronze"], m["bronze_dark"])
        parts.append(bar)
    return parts


def build():
    options = k.args()
    out = mk.outdir(options)
    k.reset()
    bpy.context.scene.view_settings.view_transform = "Standard"
    m = materials()
    parts = cases(m) + domes(m) + plate(m) + legs(m)
    mask = k.sprite_mask(os.path.join(options["check"], "enemy_D.png"), 16) if "check" in options else None
    ak.finish("bronze_beetle", parts, (0.0, 0.0), out, options, mask, label="bronze_beetle (D 16) as the camera sees it")


if __name__ == "__main__":
    build()
