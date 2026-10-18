"""The big red gem set in the ground of the asteroid levels (sheet S sprite 229, 2x2: 24 x 28 pixels;
ASTEROID1, ASTEROID2, ASTEROID?, ASTCITY, AST. CITY, AST ROCK, GREY MOON; ground layer, 123 of them;
its animation 229 229 229 233 233 233 235 235 235 233 233 233 231 231 231 229 229 229), polished
(2026-10-18; it replaces misc.py's red_gem_panel(), a red pillow on a grey bezel with four clips).
models.cfg: sprite s 229 redgem_panel yaw=0 glow=22:0.2:118:-0.5:0 (the gem's light), frame s 231
redgem_panel_231, frame s 233 redgem_panel_233, frame s 235 redgem_panel_235.

As the 4x upscale draws it: a glossy red gem cut as a cushion, a rounded rectangle (columns 4-18 of
rows 4-23) whose rounded edge catches the light along its top and left sides (the sprite's lightest
reds, columns 5 and rows 5-7) and again at its lower right (rows 19-22), its dark sides the gem's
dark red outline, swirls of lighter red winding over its dark top. Four dark iron clamps hold it,
one at each side: above (columns 8-15 of rows 2-3), below (columns 8-14 of rows 24-25), left
(columns 1-3 of rows 8-18) and right (columns 19-21 of rows 8-18).

The grey stone round them is the asteroid city's ground: the map draws the same weave of stone
blocks (and a red gem: tile 348 of ASTEROID1, under every one of these at col 4 row 150 and the
others) pixel for pixel; the sprite only adds the gem and the clamps. So no plate here: the clamps
and the gem's thin dark bezel stand on the ground (z = 0).

The animation brightens the gem and dims it again: 231, 233 and 235 draw it one, two and four
shades of ramp 7 lighter. One model per frame, the same geometry with the gem's colours and glow
raised: redgem_panel (229), redgem_panel_231, redgem_panel_233 and redgem_panel_235.

Origin at the sprite's centre (pixel 12, 14); +Y up the sprite, +Z up from the ground (z = 0).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the
silhouette against the gem's and the clamps' pixels, written below), --preview <prefix>.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402

# The gem's and the clamps' pixels in S 229 (the stone round them left out): '#'.
PANEL = """
........................
........................
........########........
........########........
......###########.......
.....#############......
....###############.....
....###############.....
.#####################..
.#####################..
.#####################..
.#####################..
.#####################..
.#####################..
.#####################..
.#####################..
.#####################..
.#####################..
.#####################..
....###############.....
....###############.....
....###############.....
.....#############......
......###########.......
........#######.........
........#######.........
........................
........................
"""

CENTRE = (-0.5, 0.0)        # the gem (columns 4-18, rows 4-23)
HALF = (7.2, 9.7)           # its half-width and half-depth
CORNER = 3.1                # the radius of its corners in plan
SEGMENTS = 88
# The gem from its foot up, (inset from its outline, z): upright sides, the rounded edge (a quarter
# circle of EDGE_R), then the cushion's top bulging DOME higher in the middle.
FOOT, SIDE_TOP, EDGE_R, DOME = 0.25, 1.7, 2.3, 0.75
TOP_RINGS = 15
# Its thin dark bezel round its foot: (outward offset, z).
BEZEL = [(0.75, 0.0), (0.75, 0.45), (0.55, 0.8), (0.25, 0.92), (-0.05, 0.85), (-0.15, 0.4)]
# The clamps' plans (x0, x1, y0, y1), each with two bolts along its top, and their height.
CLAMPS = [(-4.15, 3.75, 9.95, 12.2), (-4.15, 3.25, -12.15, -9.95), (-11.15, -7.95, -5.2, 6.2), (6.95, 10.15, -5.2, 6.2)]
CLAMP_H = 1.55
# Swirls on the gem's top: a spiral stripe of lighter red where swirl(x, y) is above SWIRL, lighter
# still along its middle (above SWIRL_CORE).
SWIRL, SWIRL_CORE = 0.42, 0.86

# The frames: (model, sprite, shade offset of ramp 7, the glow of the gem's top and swirls).
FRAMES = [("redgem_panel", 229, 0, 0.28), ("redgem_panel_231", 231, 1, 0.4), ("redgem_panel_233", 233, 2, 0.58),
          ("redgem_panel_235", 235, 4, 0.92)]
# The gem's parts in frame 229 (the sprite's shades): its sides, its top, the swirl and its core, the
# rounded edge, lighter along the top and the left side (where the sprite's lightest reds lie) and
# round the lower right corner, where the light comes through the gem.
SHADES = {"side": 0x71, "top": 0x72, "swirl": 0x73, "swirl_core": 0x75, "edge": 0x74, "edge_lit": 0x76,
          "rim": 0x77}
RIM_AT = (-72.0, -22.0)     # where round the gem the lower right light lies (degrees, see around())


def swirl(x, y):
    """A spiral winding out from a middle a little up and to the right of the gem's, as the
    sprite's loops wind (two turns to the edge), its stripe wider in places: -1 to 1, the stripe
    where it is high. The angle only appears inside the sines, so it runs on without a seam."""
    dx, dy = (x - CENTRE[0] - 0.8) / 5.4, (y - CENTRE[1] - 1.0) / 7.2
    r = math.hypot(dx, dy)
    a = math.atan2(dy, dx)
    r += 0.05 * math.sin(4 * a)
    return math.sin(a - 2 * math.pi * 1.8 * r) + 0.22 * math.sin(3 * a + 4.0 * r) - 0.1


def around(c):
    """Where round the gem a point lies (degrees, its plan made square)."""
    return math.degrees(math.atan2((c.y - CENTRE[1]) / HALF[1], (c.x - CENTRE[0]) / HALF[0]))


def gem_rings():
    """The gem's rings from its foot up: its sides and its rounded edge (rounded rectangles inset
    from its outline), then its top, the edge's inner ring drawn in towards the middle (so the
    top's faces stay well shaped for the swirls' borders) and bulging DOME at the middle."""
    profile = [(0.0, FOOT), (0.0, SIDE_TOP)]
    for i in range(1, 8):
        a = (math.pi / 2) * i / 8
        profile.append((EDGE_R * (1 - math.cos(a)), SIDE_TOP + EDGE_R * math.sin(a)))
    rings = [mk.rounded_rect_ring(CENTRE, HALF[0] - d, HALF[1] - d, CORNER - d, z, SEGMENTS) for d, z in profile]
    edge, top = rings[-1], SIDE_TOP + EDGE_R
    for i in range(1, TOP_RINGS + 1):
        s = 1 - i / (TOP_RINGS + 1)
        rings.append([Vector((CENTRE[0] + (p.x - CENTRE[0]) * s, CENTRE[1] + (p.y - CENTRE[1]) * s,
                              top + DOME * (1 - s * s))) for p in edge])
    return rings, top + DOME


def materials(shift, glow):
    palette = k.level_palette()
    m = {
        "clamp": k.material("redgem_clamp", palette=0x03, metallic=0.55, roughness=0.42),
        "clamp_top": k.material("redgem_clamp_top", palette=0x06, metallic=0.55, roughness=0.36),
        "bezel": k.material("redgem_bezel", palette=0x02, metallic=0.4, roughness=0.5),
        "bolt": k.material("redgem_bolt", palette=0x08, metallic=0.6, roughness=0.3),
    }
    strengths = {"side": 0.4, "top": 0.8, "swirl": 0.9, "swirl_core": 1.0, "edge": 0.8, "edge_lit": 0.95,
                 "rim": 1.05}
    for part, index in SHADES.items():
        i = index + shift
        m[part] = k.material(f"redgem_{part}_{i:x}", palette=i, metallic=0.0, roughness=0.12, emission=palette[i],
                             emission_strength=glow * strengths[part])
    return m


def gem(m):
    rings, top_z = gem_rings()
    obj = k.loft("gem", rings, m["top"], start_point=(*CENTRE, FOOT), end_point=(*CENTRE, top_z))
    # The swirls' borders cut into the top so they run smoothly.
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    values = {v: swirl(v.co.x, v.co.y) for v in bm.verts}
    for edge in (SWIRL, SWIRL_CORE):
        mk.split_along(bm, values, edge)
    bm.to_mesh(obj.data)
    bm.free()
    def pick(c, n):
        if n.z < 0.35:
            return m["side"]
        if n.z < 0.93:
            if RIM_AT[0] < around(c) < RIM_AT[1]:
                return m["rim"]
            return m["edge_lit"] if n.y - n.x > 0.3 else m["edge"]
        f = swirl(c.x, c.y)
        return m["swirl_core"] if f > SWIRL_CORE else m["swirl"] if f > SWIRL else m["top"]
    mk.paint(obj, pick)
    k.smooth(obj, 50)
    return obj


def bezel(m):
    rings = [mk.rounded_rect_ring(CENTRE, HALF[0] + d, HALF[1] + d, CORNER + d, z, SEGMENTS) for d, z in BEZEL]
    obj = k.loft("bezel", rings, m["bezel"], cap_start=False, cap_end=False)
    k.smooth(obj, 50)


def clamps(m):
    for i, (x0, x1, y0, y1) in enumerate(CLAMPS):
        body = mk.box(f"clamp{i}", x0, x1, y0, y1, 0.0, CLAMP_H, m["clamp"])
        mk.bevel(body, 0.38, 3, 35)
        mk.paint(body, lambda c, n: m["clamp_top"] if n.z > 0.9 else None)
        mk.shade(body, 40)
        # Two bolts along each clamp's top.
        long_x = (x1 - x0) > (y1 - y0)
        for t in (0.25, 0.75):
            x = x0 + (x1 - x0) * (t if long_x else 0.5)
            y = y0 + (y1 - y0) * (0.5 if long_x else t)
            mk.ball(f"bolt{i}_{t}", (x, y, CLAMP_H - 0.05), (0.42, 0.42, 0.3), m["bolt"], 10, 5)


def panel_mask():
    return [[c == "#" for c in line] for line in PANEL.strip().splitlines()]


def build():
    options = k.args()
    out = mk.outdir(options)
    for name, sprite, shift, glow in FRAMES:
        k.reset()
        m = materials(shift, glow)
        gem(m)
        bezel(m)
        clamps(m)
        parts = mk.meshes()
        if "check" in options:
            mk.compare("%s (S %d: the gem and the clamps)" % (name, sprite), mk.coverage(parts, 24, 28), panel_mask())
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts)


if __name__ == "__main__":
    build()
