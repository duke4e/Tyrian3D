"""SOH JIN's bronze whorl (sheet A sprite 91, 2x2: 24 x 28 pixels; enemy 838, on the ground, 34 of them; its animation
91 129 129 129 91 plays when it fires), polished (2026-10-19; it replaces wave3_q_bronze.py's bronze_whorl(), a
torus open at the lower left with a red lens in the gap). models.cfg: sprite a 91 bronze_whorl yaw=0 (unchanged),
frame a 129 bronze_whorl_129. No other enemy shows A 91 or A 129.

A 91 is F 39's picture, the bronze disc turret of SAVARA, SOH JIN and DIG SITE (polish_disc_turret.py), for 634 of its
672 pixels: the same pale dome on its ring in the same sand, the same knob leaning out at the upper right, the same
short gun down the screen, the same shadows. Only two places differ: where F 39's red eye glows in the dome's crown
(columns 7-11 of rows 10-13) A 91 has dull bronze (shades 13-16, the dark dished middle its 4x upscale draws as a
whorl), and on the dome's lower left flank A 91 has a red slit F 39 doesn't (columns 3-8 of rows 13-18: a narrow
lens running down to the right, its middle 75-79, its edge 70-71). So the whorl is the disc turret, not modelled
again: this script builds polish_disc_turret's ring, dome, knob and gun (its geometry and colours, its materials
renamed) and gives it A 91's two differences: the eye's socket closed by a bronze iris whose six blades swirl
into the middle (the whorl), and a slit cut into the dome's flank along its curve, a red glass glowing in it. Frame
129 lights the slit (seven pixels of its middle, 74-7b): bronze_whorl_129, the same model, its glass two shades
hotter and glowing more. The sand and the shadows round it are the map's ground and the turret's own shadow, as for
the disc turret.

Origin at the sprite's centre (pixel 12, 14); +Y up the screen, +Z up from the ground (z = 0).

Replaces wave3_q_bronze.py's bronze_whorl() (its @q.model("bronze_whorl", [(91, True)]) function, WHORL, WHORL_R,
WHORL_TUBE and WHORL_GAP, the bronze_whorl lines of its docstring; bronze_grille() stays): remove them so that they
don't overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against the
turret's own pixels, polish_disc_turret's TURRET, which are A 91's too), --preview <prefix>, --only <name,...>.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_disc_turret as dt  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_orb_red import band_split  # noqa: E402

# The iris in the eye's socket: its blades, how far each turns from the rim to the middle (radians), its dish's
# depth; each blade lit along its leading half and darker where it slides under the next (bands of the sine of the
# blades' phase), a dark seam along its edge.
BLADES, TWIST, DISH = 6, 2.4, 0.3
IRIS_BANDS = (0.0, 0.8)
# The slit (the sprite's columns 3-8 of rows 13-18): its middle in plan, how far it reaches along the dome's curve
# either side (pixels), its half-height across (along the dome's slope) and depth; the glass in it, a little narrower
# and sunk below the dome's surface.
SLIT_AT = Vector((-6.0, -2.05))
SLIT_HALF, SLIT_WIDE, SLIT_DEEP = 2.95, 0.78, 0.85
GLASS_SINK, GLASS_DEEP = 0.55, 0.45   # the glass's middle below the surface; its half-depth (of the slit's)
# The frames: (model, sprite, the glass from its middle out and the slit's walls: (palette index, emission)).
FRAMES = [
    ("bronze_whorl", 91, [(0x79, 1.5), (0x75, 1.1), (0x73, 0.75), (0x71, 0.35)]),
    ("bronze_whorl_129", 129, [(0x7b, 2.5), (0x79, 1.9), (0x75, 1.3), (0x73, 0.55)]),
]
GLASS_BANDS = (0.42, 0.72)   # where the glass's colours change (its elliptical distance from the middle)


def materials(slit):
    """polish_disc_turret's materials, renamed for the whorl; the iris's bronzes; the slit's glass."""
    m = dt.materials([])
    for mat in m.values():
        mat.name = mat.name.replace("discturret", "whorl")
    m["iris"] = k.material("whorl_iris", palette=0x16, metallic=0.5, roughness=0.3)
    m["iris_dark"] = k.material("whorl_iris_dark", palette=0x14, metallic=0.5, roughness=0.35)
    m["seam"] = k.material("whorl_iris_seam", palette=0x11, metallic=0.3, roughness=0.5)
    pal = k.level_palette()
    for i, (index, glow) in enumerate(slit):
        m[("slit", i)] = k.material(f"whorl_slit_{index:x}", palette=index, metallic=0.0, roughness=0.12,
                                    emission=pal[index], emission_strength=glow)
    return m


def iris(m, crown):
    """The closed iris in the socket: a shallow dish of BLADES blades, each overlapping the next along a curve that
    swirls into the middle."""
    floor = crown - 0.45
    radius = dt.EYE_R + 0.02
    rings, around = 7, 72
    verts, faces = [Vector((dt.AXIS.x, dt.AXIS.y, floor + 0.05))], []
    for i in range(1, rings + 1):
        r = radius * i / rings
        for j in range(around):
            a = 2 * math.pi * j / around
            verts.append(Vector((dt.AXIS.x + r * math.cos(a), dt.AXIS.y + r * dt.SQUASH[1] * math.sin(a),
                                 floor + 0.05 + DISH * (i / rings) ** 1.6)))
    for j in range(around):
        faces.append((0, 1 + j, 1 + (j + 1) % around))
    for i in range(rings - 1):
        for j in range(around):
            a, b = 1 + i * around + j, 1 + i * around + (j + 1) % around
            faces.append((a, a + around, b + around, b))
    obj = k.mesh_object("iris", verts, faces, m["iris"])

    def blade(v):
        d = v - Vector((dt.AXIS.x, dt.AXIS.y, v.z))
        if d.length < 0.15:
            return -1.0   # the middle, where the blades meet: dark
        return math.sin(BLADES * (math.atan2(d.y, d.x) + TWIST * d.length / radius))
    band_split(obj, [blade(v.co) for v in obj.data.vertices],
               [(-9.0, m["iris_dark"]), (IRIS_BANDS[0], m["iris"]), (IRIS_BANDS[1], m["seam"])])
    return k.smooth(obj, 60)


def dome_height(x, y):
    """The dome's top at (x, y), as polish_disc_turret.dome() shapes it (its rings' superellipse plan)."""
    r = dt.radius_of(Vector((x, y, 0.0)))
    if r >= dt.DOME_R:
        return dt.DOME_Z
    return dt.DOME_Z + dt.DOME_H * (1 - (r / dt.DOME_R) ** dt.DOME_POWER) ** (1 / dt.DOME_POWER)


def along_slit(t, lift=0.0):
    """A point of the slit's middle line at t (-1 to 1 along it), on the dome's surface (raised by lift along its
    normal), and the dome's normal there: the line keeps the slit's height round the dome."""
    centre = Vector((dt.AXIS.x, dt.AXIS.y, 0.0))
    at = Vector((SLIT_AT.x, SLIT_AT.y, 0.0)) - centre
    radius = at.length
    a = math.atan2(at.y, at.x) + t * SLIT_HALF / radius
    p = centre + Vector((radius * math.cos(a), radius * math.sin(a) * dt.SQUASH[1], 0.0))
    p.z = dome_height(p.x, p.y)
    e = 0.05
    n = Vector((-(dome_height(p.x + e, p.y) - dome_height(p.x - e, p.y)) / (2 * e),
                -(dome_height(p.x, p.y + e) - dome_height(p.x, p.y - e)) / (2 * e), 1.0)).normalized()
    return p + n * lift, n


def lens(name, half_wide, half_deep, lift, mat, steps=22, around=14):
    """A lens-shaped solid along the slit's line: its section an ellipse (half_wide along the dome's slope,
    half_deep along its normal), narrowing to points at the slit's ends."""
    rings = []
    for i in range(1, steps):
        t = -1.0 + 2.0 * i / steps
        p, n = along_slit(t, lift)
        q, _ = along_slit(min(1.0, t + 0.01), lift)
        tangent = (q - p).normalized()
        across = n.cross(tangent).normalized()   # along the dome's slope
        width = math.sqrt(max(0.0, 1.0 - t * t)) ** 0.8
        ring = []
        for j in range(around):
            b = 2 * math.pi * j / around
            ring.append(p + across * (half_wide * width * math.cos(b)) + n * (half_deep * width * math.sin(b)))
        rings.append(ring)
    start, _ = along_slit(-1.0, lift)
    end, _ = along_slit(1.0, lift)
    obj = k.loft(name, rings, mat, start_point=tuple(start), end_point=tuple(end))
    return k.smooth(obj, 60)


def slit(m):
    """The slit cut into the dome along its curve (its walls the glass's dark red edge) and the glass in it, glowing
    hottest in its middle."""
    dome = bpy.data.objects["dome"]
    cutter = lens("slit_cut", SLIT_WIDE, SLIT_DEEP, 0.0, m[("slit", 3)], steps=26, around=14)
    mk.boolean(dome, cutter, "DIFFERENCE")
    k.smooth(dome, 50)
    glass = lens("slit_glass", SLIT_WIDE * 0.86, SLIT_DEEP * GLASS_DEEP, -GLASS_SINK, m[("slit", 2)])
    centre, n0 = along_slit(0.0, -GLASS_SINK)
    slope = n0.cross(Vector((0.0, 0.0, 1.0))).normalized().cross(n0)

    def rho(c):
        """The elliptical distance from the glass's middle: along the slit (by the angle round the dome) and
        across it."""
        p = Vector((c.x - dt.AXIS.x, c.y - dt.AXIS.y))
        q = Vector((SLIT_AT.x - dt.AXIS.x, SLIT_AT.y - dt.AXIS.y))
        along = math.atan2(p.x * q.y - p.y * q.x, p.dot(q)) * q.length / SLIT_HALF
        across = (c - centre).dot(slope) / (SLIT_WIDE * 0.86)
        return math.hypot(along, across)
    band_split(glass, [-rho(v.co) for v in glass.data.vertices],
               [(-99.0, m[("slit", 2)]), (-GLASS_BANDS[1], m[("slit", 1)]), (-GLASS_BANDS[0], m[("slit", 0)])])
    return k.smooth(glass, 60)


def build_model(slit_shades):
    k.reset()
    m = materials(slit_shades)
    dt.base_ring(m)
    crown = dt.dome(m)
    iris(m, crown)
    dt.knob(m)
    dt.gun(m)
    slit(m)
    return mk.meshes()


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    for name, sprite, slit_shades in FRAMES:
        if only is not None and name not in only:
            continue
        parts = build_model(slit_shades)
        if "check" in options:
            mk.compare("%s (A %d, the turret's own pixels)" % (name, sprite), mk.coverage(parts, 24, 28),
                       dt.turret_mask())
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        bpy.context.view_layer.update()
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts)


if __name__ == "__main__":
    build()
