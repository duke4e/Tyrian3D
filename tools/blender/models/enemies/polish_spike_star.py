"""The grey star of BRAINIAC, ICE EXIT, ICESECRET, LAVA RUN and SIDE EXIT (sheet 3 sprite 246, 2x2: 23 x 25
pixels in the 24 x 28 cell; sky and top layers, about 70 of them; not animated), polished (2026-10-19; it
replaces wave2_f.py's spike_star(), a flat hub with four blades and four tubes). models.cfg: sprite 3 246
spike_star yaw=0.

As the sprite and its 4x upscale draw it: a steel star of eight spikes round a hub. Four are grey
steel blades pointing up, down, left and right (to rows 2 and 26, columns 1 and 23), each a pyramid
with a sharp ridge along its middle, lit on the side towards the upper left, dark on the other; four
are red rods on the diagonals (the sprite's ramp 4, columns 3-7 of rows 5-9 and so on), lit along
their middles, standing a little apart from the hub (a dark gap round their inner ends). The hub
(columns 6-17 of rows 10-18) is an eight-sided steel boss whose upper rim catches the light (row 10);
in its middle sits the red-lit core (columns 9-14 of rows 11-16): two red lobes side by side, lit
along their middles, a steel rib between them.

The model: the hub an eight-sided boss, its corners running into the four steel spikes (pyramids
with softly rounded ridges, a little concave towards their points), a socket in its top holding the
core, two glowing red capsules lying up the screen either side of a steel rib; the red spikes rods of
glossy red with rounded points on dark steel stems out of the hub's corners on the diagonals, a dark
collar round each one's foot. The steel is painted as polished steel shows the sky (polish_spike_mine.py's
chrome: bands of the surface's slope, brightest along the ridges and the rim, a dark line where it
turns away), so the spikes show the sprite's bright ridges, and the game's sun lights it from the top
left as the sprite is lit; the core glows in its reds and the rods a little, so that they stay red on
the side the game's camera sees. One mesh (the parts joined).

Origin at the sprite's centre (pixel 12, 14); +Y up the screen, +Z towards the camera. The star's
middle is at (0.5, -0.5) (the spikes' ridges run along column 12 and row 14); its middle plane is
z = 0 (the game centres sky objects in height).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the
silhouette against 3 246 in <dir>/enemy_3.png), --preview <prefix>.
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
from polish_spike_mine import chrome, join  # noqa: E402

CENTRE = Vector((0.5, -0.5, 0.0))
# The steel, painted as polished steel shows the sky (polish_spike_mine.py's chrome): bands of the
# surface's normal z from the bottom up, (lowest normal z, palette index, metallic, roughness, emission
# strength in its own grey): its underside, its steep sides, a dark line where it turns from the sky,
# the facets and, along the ridges and the rim, the brightest.
STEEL = [(-9.0, 0x04, 0.45, 0.35, 0.05), (0.3, 0x06, 0.45, 0.3, 0.06), (0.58, 0x03, 0.5, 0.35, 0.03),
         (0.66, 0x08, 0.45, 0.25, 0.06), (0.84, 0x0b, 0.45, 0.2, 0.08), (0.95, 0x0d, 0.4, 0.18, 0.12)]
# The hub: an octagon (its corners towards the steel spikes), as (corner radius, z) from its underside
# up over its rim and down into the socket, whose floor the core lies on.
HUB = [(4.5, -1.5), (5.5, -0.75), (5.6, 0.7), (5.2, 1.5), (4.6, 2.05), (4.0, 2.2), (3.85, 1.9), (3.75, 1.3),
       (3.7, 0.55)]
SOCKET = 3.7            # the socket's corner radius (inside the rim: its walls and floor are dark)
# The steel spikes: (heading, degrees from +X; the tip's distance from the middle). Each is a rounded
# diamond in section (a superellipse of power SPIKE_POWER), BASE_HALF wide either side, BASE_TOP high
# above the middle plane and BASE_UNDER below it where it leaves the hub (at BASE_AT from the middle),
# narrowing to its point a little faster than straight (CONCAVE).
SPIKES = [(90.0, 12.0), (270.0, 12.0), (180.0, 11.3), (0.0, 11.0)]
BASE_AT, BASE_HALF, BASE_TOP, BASE_UNDER = 5.0, 2.75, 2.1, 1.25
SPIKE_POWER, CONCAVE = 1.3, 1.18
# The red spikes on the diagonals: (heading, degrees); each a rod from ROD_FROM to ROD_TO from the
# middle, ROD_RADIUS at its foot to ROD_POINT at the start of its rounded point, its axis ROD_Z above
# the middle plane; a dark stem from inside the hub out to it and a dark collar round its foot.
RODS = [45.0, 135.0, 225.0, 315.0]
ROD_FROM, ROD_TO, ROD_RADIUS, ROD_POINT, ROD_Z = 6.9, 12.8, 1.3, 1.05, 0.35
STEM_RADIUS, COLLAR = 0.55, (1.5, 0.55)     # the collar: its radius and length
# The core: two capsules lying up the screen, LOBE_X either side of the middle, LOBE_RADIUS thick and
# LOBE_HALF long either side, on the socket's floor; and the steel rib between them (its half-width,
# half-length and top).
LOBE_X, LOBE_RADIUS, LOBE_HALF, LOBE_Z = 1.32, 1.12, 2.25, 1.15
RIB = (0.42, 2.9, 2.15)


def materials():
    pal = k.level_palette()
    m = {
        "steel": [(lowest, k.material(f"star_steel_{index:02x}", palette=index, metallic=metallic, roughness=roughness,
                                      emission=pal[index], emission_strength=glow))
                  for lowest, index, metallic, roughness, glow in STEEL],
        "dark": k.material("star_dark", palette=0x02, metallic=0.4, roughness=0.45),
        "rod": k.material("star_rod", palette=0x48, metallic=0.15, roughness=0.24, emission=pal[0x48],
                          emission_strength=0.22),
    }
    # The core's lobes: dark red at their sides, red, bright along their tops, glowing.
    for key, index, glow in (("lobe_side", 0x43, 0.3), ("lobe", 0x46, 0.4), ("lobe_top", 0x4b, 0.6)):
        m[key] = k.material(f"star_{key}", palette=index, metallic=0.0, roughness=0.2, emission=pal[index],
                            emission_strength=glow)
    return m


def steel_band(m, n):
    """The steel's material for a face whose normal is n."""
    return m["steel"][sum(n.z > lowest for lowest, _ in m["steel"][1:])][1]


def place(obj, heading, z=0.0):
    """Turns a part built along +Y from the middle to the heading, about the star's middle."""
    obj.data.transform(Matrix.Translation(CENTRE + Vector((0, 0, z))) @
                       Matrix.Rotation(math.radians(heading - 90.0), 4, "Z"))
    return obj


def hub(m):
    obj = mk.lathe("hub", HUB, (0.0, 0.0), m["steel"][0][1], segments=8)
    place(obj, 90.0)
    mk.bevel(obj, 0.22, 2, 35)
    c = CENTRE

    def pick(p, n):
        if 0.4 < p.z < 1.95 and math.hypot(p.x - c.x, p.y - c.y) < SOCKET + 0.15:
            return m["dark"]   # the socket's walls and floor
        return steel_band(m, n)
    mk.paint(obj, pick)
    return mk.shade(obj, 40)


def spike(name, heading, length, m):
    rings = []
    steps = 12
    start = 2.2
    for i in range(steps):
        t = start + (length - start) * i / steps
        u = max(0.0, (t - BASE_AT) / (length - BASE_AT))
        f = (1 - u) ** CONCAVE if t >= BASE_AT else 1.0 + (BASE_AT - t) * 0.04
        rings.append(k.ring(t, BASE_HALF * f, 1.0, 16, z=0.0, top=BASE_TOP * f, bottom=BASE_UNDER * f,
                            power=SPIKE_POWER))
    obj = k.loft(name, rings, None, end_point=(0.0, length, 0.0))
    place(obj, heading)
    k.smooth(obj, 50)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bpy.data.objects.remove(obj)
    return k.smooth(chrome(name, bm, m["steel"]), 50)


def rod(name, heading, m):
    """The red rod with its rounded point, its collar and its stem, built along +Y."""
    profile = [(ROD_FROM - 0.05, 0.0), (ROD_FROM - 0.05, ROD_RADIUS * 0.8), (ROD_FROM + 0.15, ROD_RADIUS)]
    point_at = ROD_TO - ROD_POINT * 1.15
    for i in range(1, 5):
        y = ROD_FROM + 0.15 + (point_at - ROD_FROM - 0.15) * i / 4
        profile.append((y, ROD_RADIUS + (ROD_POINT - ROD_RADIUS) * i / 4))
    for i in range(1, 6):
        a = (math.pi / 2) * i / 6
        profile.append((point_at + (ROD_TO - point_at) * math.sin(a), ROD_POINT * math.cos(a)))
    profile.append((ROD_TO, 0.0))
    body = k.lathe(name, profile, m["rod"], segments=16)
    collar = k.lathe(name + "_collar", [(ROD_FROM - 0.2, 0.0), (ROD_FROM - 0.2, COLLAR[0] - 0.15),
                                        (ROD_FROM - 0.05, COLLAR[0]), (ROD_FROM + COLLAR[1], COLLAR[0]),
                                        (ROD_FROM + COLLAR[1] + 0.12, COLLAR[0] - 0.2),
                                        (ROD_FROM + COLLAR[1] + 0.12, 0.0)], m["dark"], segments=16)
    stem = k.lathe(name + "_stem", [(4.4, 0.0), (4.4, STEM_RADIUS), (ROD_FROM, STEM_RADIUS), (ROD_FROM, 0.0)],
                   m["dark"], segments=10)
    for obj, angle in ((body, 60), (collar, 40), (stem, 50)):
        obj.data.transform(Matrix.Translation((0, 0, ROD_Z)))
        place(obj, heading)
        k.smooth(obj, angle)


def core(m):
    c = CENTRE
    for side in (-1, 1):
        x = c.x + side * LOBE_X
        lobe = k.ellipsoid(f"lobe{side}", (x, c.y, LOBE_Z), (LOBE_RADIUS, LOBE_HALF + LOBE_RADIUS * 0.4, LOBE_RADIUS),
                           m["lobe"], 20, 14)
        mk.paint(lobe, lambda p, n: m["lobe_top"] if n.z > 0.86 else m["lobe"] if n.z > 0.45 else m["lobe_side"])
        k.smooth(lobe, 70)
    hw, hl, top = RIB
    rib = mk.box("rib", c.x - hw, c.x + hw, c.y - hl, c.y + hl, 0.4, top, m["steel"][0][1])
    mk.bevel(rib, 0.2, 2, 35)
    mk.paint(rib, lambda p, n: steel_band(m, n))
    mk.shade(rib, 40)


def build():
    options = k.args()
    k.reset()
    m = materials()
    hub(m)
    for i, (heading, length) in enumerate(SPIKES):
        spike(f"spike{i}", heading, length, m)
    for i, heading in enumerate(RODS):
        rod(f"rod{i}", heading, m)
    core(m)
    parts = [join("spike_star", mk.meshes())]
    if "check" in options:
        k.check_silhouette(os.path.join(options["check"], "enemy_3.png"), 246)
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mk.report("spike_star", parts, os.path.join(mk.outdir(options), "spike_star.glb"))
    if "preview" in options:
        mk.preview(options["preview"] + "spike_star", parts)


if __name__ == "__main__":
    build()
