"""The big red gem's wreck (sheet S sprite 229's stand-in: what the asteroid maps paint where redgem_panel stands once
it is destroyed, before it comes and where none comes; 122 of them in ASTEROID1, ASTEROID2, ASTEROID?, ASTCITY,
AST. CITY, AST ROCK and GREY MOON), built on polish_redgem_panel.py (2026-10-25, the clean ground's stage 4).

As the maps paint it at 4x (the asteroid tiles' 348 over 416, the most common of its paintings; ASTEROID2
14a0d01cd2b01f4c at 540, 1947): the gem's cushion in its place, its outline and the light along its rounded top and
left edges as the live gem has them (0x7a-0x7e, its lower right 0x76-0x78), but its top smashed: dark red inside
(0x70, nearly black) with jagged shards of orange-red across it (0x74-0x79); the four iron clamps that held it are
gone (the map's stone shows where they were), its thin dark bezel is left.

The model: the live gem (polish_redgem_panel.gem, frame 229's colours) broken away along a fracture that runs low over
its middle (2.3, wandering) and rises to its rounded edge (so the edge ring stands whole with its light, a bowl of
broken crystal inside): the fracture the gem's dark inside (0x70, 0x71) crazed with lighter cracks (0x72); shards of
the broken crown lying tilted in the hollow (0x74-0x79, two of them with an ember's faint glow, 0x77 at 0.3), one
spike of crystal standing up out of it to the live gem's height (4.75), so the wreck's bounds in height are the live
model's and the game, which centres these models in height on the ground enemies' layer, places the two alike; the
live bezel (polish_redgem_panel.bezel), no clamps.

The same frame as redgem_panel: origin at the sprite's centre (pixel 12, 14), +Y up the sprite, +Z up from the ground
(z = 0); drawn as the live model (models.cfg: model redgem_panel_wreck enemies/redgem_panel_wreck.glb; wreck s 229
redgem_panel_wreck, so the game draws it with sprite s 229's options, yaw=0; its glow is the live enemy's only).

Options after "--": --outdir <dir> (default assets/models/enemies), --preview <prefix>.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k, smoothstep  # noqa: E402
import polish_redgem_panel as live  # noqa: E402
import polish_panel_pills_wreck as wk  # noqa: E402

LIVE_TOP = live.SIDE_TOP + live.EDGE_R + live.DOME   # 4.75: the live gem's crown
# The fracture: its height over the gem's middle, how much it wanders, the height it rises to at the rounded edge and
# how far in from the gem's outline it begins to fall.
FRACTURE_Z, FRACTURE_JAG, EDGE_Z, EDGE_IN = 2.4, 0.22, 4.2, (0.9, 4.0)
# The broken crown's shards, laid along the gem's swirl as the painting's streaks run: (x, y, heading, length, width,
# rise, shade, glow, sides).
SHARDS = [(-4.6, 5.8, -30, 5.2, 2.6, 0.7, 0x78, 0.0, 4), (0.6, 6.6, 200, 4.6, 2.4, 0.6, 0x76, 0.0, 4),
          (-5.0, 1.0, 70, 4.4, 2.4, 0.65, 0x77, 0.0, 4), (-1.6, 2.2, 10, 5.0, 2.2, 0.6, 0x79, 0.3, 4),
          (3.4, 3.2, 255, 4.6, 2.2, 0.6, 0x75, 0.0, 4), (-4.4, -3.8, 20, 5.4, 2.6, 0.7, 0x77, 0.0, 4),
          (2.8, -1.6, 230, 4.4, 2.2, 0.6, 0x76, 0.0, 4), (-1.0, -6.6, 15, 5.2, 2.4, 0.65, 0x78, 0.3, 4),
          (4.2, -6.4, 110, 4.0, 2.0, 0.6, 0x75, 0.0, 3)]
# The spike of crystal standing in the middle, its tip at the live gem's height.
SPIKE = (0.6, -1.4, 100, 3.2, 1.6, 2.4, 0x7a)


def edge_distance(x, y):
    """How far inside the gem's outline (x, y) is (its rounded rectangle in plan)."""
    return -mk.rounded_rect_distance(x - live.CENTRE[0], y - live.CENTRE[1], live.HALF[0], live.HALF[1], live.CORNER)


def fracture_z(x, y):
    """The fracture's height under (x, y): low over the middle, rising to the rounded edge."""
    low = FRACTURE_Z + FRACTURE_JAG * wk.fbm(x * 0.3 + 4.0, y * 0.24 - 3.0, 1.5, 2)
    low -= 0.2 * (1.0 - min(1.0, abs(wk.perlin(x * 0.45, y * 0.35, 9.0)) * 3.0))
    rise = 1.0 - smoothstep(EDGE_IN[0], EDGE_IN[1], edge_distance(x, y))
    # the edge ring itself broken lower here and there (a notch on its right side, one at its lower left)
    edge = EDGE_Z - 0.9 * max(0.0, wk.perlin(x * 0.35 + 1.0, y * 0.35, 4.0)) * 2.0
    return low + (edge - low) * rise


def crazing(c):
    return wk.perlin(c.x * 0.32 + 2.0, c.y * 0.26, 5.0)


def build():
    options = k.args()
    k.reset()
    m = live.materials(0, 0.0)  # frame 229's colours, its light out
    # (at most 15 materials a model: the game colours no more from the palette; the gem's own shades serve the
    # fracture and the shards)
    inside, crack = m["side"], m["top"]
    hollow = wk.mat("redgemwreck_hollow", 0x70, 0.0, 0.18)
    fresh = wk.mat("redgemwreck_fracture", 0x70, 0.0, 0.18)  # (the fracture's faces until they are banded)
    panes = {0x74: m["edge"], 0x75: m["swirl_core"], 0x76: m["edge_lit"], 0x77: m["rim"],
             0x78: wk.mat("redgemwreck_shard_78", 0x78, 0.0, 0.15),
             0x7a: wk.mat("redgemwreck_shard_7a", 0x7a, 0.0, 0.15)}
    ember = wk.mat("redgemwreck_ember", 0x79, 0.0, 0.15, 0.3)
    gem = live.gem(m)
    x0, x1 = live.CENTRE[0] - live.HALF[0] - 0.5, live.CENTRE[0] + live.HALF[0] + 0.5
    y0, y1 = live.CENTRE[1] - live.HALF[1] - 0.5, live.CENTRE[1] + live.HALF[1] + 0.5
    cutter = wk.heightfield_cutter("cut", x0, x1, y0, y1, 0.55, fracture_z, 8.0, fresh)
    wk.break_away(gem, cutter)
    k.smooth(gem, 50)
    fracture = wk.split_off(gem, fresh, "fracture")
    wk.bands(fracture, crazing, [(-9.0, hollow), (-0.3, inside), (0.15, crack)])
    live.bezel(m)
    for j, (x, y, heading, length, width, rise, shade, glow, sides) in enumerate(SHARDS):
        mat_ = ember if glow else panes[shade]
        wk.shard(f"shard{j}", (x, y, fracture_z(x, y) - 0.15), heading, length, width, rise, mat_, 0.14,
                 0.2 * ((j % 3) - 1), sides)
    x, y, heading, length, width, rise, shade = SPIKE
    spike = wk.shard("spike", (x, y, fracture_z(x, y) - 0.3), heading, length, width, rise,
                     panes[shade], 0.3, -0.15, 3)
    wk.raise_to(spike, LIVE_TOP)
    wk.clip_below(mk.meshes())
    wk.finish("redgem_panel_wreck", options, LIVE_TOP)


if __name__ == "__main__":
    build()
