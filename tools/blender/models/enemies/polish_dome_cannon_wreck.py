"""The brown dome cannon's wreck (sheet D sprites 245 above 283's stand-ins: what the asteroid maps paint where
dome_cannon_barrel and dome_cannon_dome stand once they are destroyed, before they come and where none comes; 22 of
each in ASTEROID1, ASTEROID2, ASTCITY, AST. CITY and AST ROCK), built on polish_dome_cannon.py (2026-10-25, the clean
ground's stage 4).

As the maps paint it at 4x (ASTEROID2 14a0d01cd2b01f4c at 588, 5670 and 5698; ASTCITY 6498eda0c182465c the same): the
cannon and the dome in their places, their outlines whole, but both burst: the shroud black and torn open at its upper
right (a pale torn edge running down from its top right towards its middle, columns 9-16 of 245's rows 0-9), its red
ring still under it, the cradle dark; the fluted collar gone, a dark breach in the dome's north end where it stood with
bronze shards of it bent up at its sides (the right one a pointed "<" at columns 13-17 of 283's rows 0-5); the red band
still across the dome with its pink lamps (no longer lit), the brown shell round it split by dark cracks, a diagonal
one from the upper left, and its south slope broken into ribs by dark splits running down it (columns 4-16 of rows
7-16), the seam gone into one of them.

Built as the live whole (polish_dome_cannon's dome, band, frame, lamps, cradle, neck, rings and shroud, its materials)
and broken: the dome's relief rebuilt with cracks cut into its height field (grooves along wandering lines, their
floors and walls black, cut along their edges), a breach where the collar stood (the relief lowered round the root,
black); the collar gone, bronze shards of it bent up at the breach's sides, dark chunks in it; the lamps' glass dark
pink, unlit (0x46, 0x48); the shroud torn open at its upper right by a lumpy exact boolean (its inside black), its
torn edge left bright (the chrome); everything scorched in patches (palette shades three darker, burnt brown-black
near the breaches). Cut in two at y = 0 as the live cannon (polish_savara_boss.cut, the cuts capped black), each piece
moved to its sprite's centre and joined.

Coordinates as polish_dome_cannon.py's (the whole's origin the middle of the two sprites' shared edge). models.cfg:
model dome_cannon_barrel_wreck enemies/dome_cannon_barrel_wreck.glb origin, model dome_cannon_dome_wreck
enemies/dome_cannon_dome_wreck.glb origin; wreck d 245 dome_cannon_barrel_wreck, wreck d 283 dome_cannon_dome_wreck
(drawn with the live sprite lines' options, yaw=0 height=-4, at the live pieces' places).

Options after "--": --outdir <dir> (default assets/models/enemies), --preview <prefix>, --only <name,...>.
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
import polish_deli_boss as db  # noqa: E402
import polish_dome_cannon as live  # noqa: E402
import polish_panel_pills_wreck as wk  # noqa: E402
from polish_jaw_gun_wreck import rock, scorch, shard  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_ring_machine import ccw, relief  # noqa: E402
from polish_savara_boss import cut  # noqa: E402

# The cracks in the dome: (points (x, y) along it, its half-width at its start and end, its depth).
CRACKS = [([(-10.2, 1.2), (-8.0, 0.2), (-6.2, -1.6), (-4.6, -2.4)], 1.0, 0.45, 2.0),
          ([(7.4, 0.6), (5.8, -1.2), (4.4, -2.6), (2.4, -3.4), (0.6, -4.4)], 0.9, 0.4, 1.8),
          ([(-9.8, -6.2), (-8.4, -8.4), (-7.4, -10.6), (-6.6, -12.8), (-5.4, -15.0), (-4.4, -16.8)], 0.6, 1.1, 2.2),
          ([(-4.6, -8.2), (-3.8, -10.8), (-4.1, -13.0), (-3.2, -15.4), (-3.0, -17.0)], 0.5, 1.0, 2.0),
          ([(-1.2, -7.6), (-0.8, -10.6), (-1.4, -12.8), (-1.0, -15.2), (-1.2, -17.0)], 0.7, 1.3, 2.4),
          ([(2.0, -7.4), (2.6, -10.0), (2.3, -12.4), (3.1, -14.6), (3.6, -16.4)], 0.55, 1.0, 2.0),
          ([(6.8, -6.8), (6.0, -9.0), (5.6, -11.2), (4.8, -13.4), (4.4, -15.2)], 0.5, 0.9, 1.8),
          ([(-10.6, -3.4), (-9.0, -4.2), (-7.6, -5.6), (-6.4, -6.6)], 0.55, 0.3, 1.4)]
# The breach where the collar stood: its middle (x, y), radii, depth below the shell at its middle.
BREACH = ((-1.5, 2.4), (5.6, 3.4), 3.2)
# Shards of the collar bent up at the breach's sides: (outline in plan, z, thickness, tilt about x and y), material.
SHARDS = [([(2.2, -0.6), (5.6, 0.4), (7.2, 4.6), (4.4, 2.8)], 6.4, 0.45, (-30.0, 46.0), "brown_lit"),
          ([(-5.2, -0.4), (-8.4, 0.8), (-9.2, 4.4), (-6.4, 3.0)], 6.2, 0.45, (-26.0, -42.0), "bronze"),
          ([(-3.4, 3.4), (0.2, 3.8), (0.8, 6.6), (-2.8, 6.0)], 5.8, 0.4, (-52.0, 8.0), "brown"),
          ([(-0.6, -0.2), (1.8, 0.2), (1.4, 2.6)], 6.6, 0.4, (-20.0, 30.0), "bronze")]
CHUNKS = [((-3.2, 2.0, 3.8), (1.2, 1.0, 0.8)), ((0.6, 1.4, 3.6), (1.0, 0.9, 0.7)), ((-1.2, 3.6, 3.9), (0.9, 0.8, 0.6))]
# The tear in the shroud: a lumpy blast at its upper right (centre, radii, seed).
TEAR = ((2.6, 23.8, 14.4), (6.6, 6.2, 5.6), 7.0)
# The scorch: patches over everything, burnt black near the breaches.
BURN_AT = [(Vector((-1.5, 2.0, 5.0)), 6.5), (Vector((1.9, 24.0, 12.0)), 5.5)]


def segment_distance(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-9)))
    return (p - (a + ab * t)).length, t


def crack_field(x, y):
    """Positive inside a crack: its half-width there less the distance to its line (and how deep it is there)."""
    best, depth = -9.0, 0.0
    p = Vector((x, y))
    for points, w0, w1, d in CRACKS:
        total = sum((Vector(b) - Vector(a)).length for a, b in zip(points, points[1:]))
        run = 0.0
        for a, b in zip(points, points[1:]):
            a, b = Vector(a), Vector(b)
            dist, t = segment_distance(p, a, b)
            s = (run + t * (b - a).length) / total
            w = w0 + (w1 - w0) * s
            w *= 1.0 + 0.3 * wk.perlin(x * 0.9 + 2.0, y * 0.9, 0.3)
            if w - dist > best:
                best, depth = w - dist, d
            run += (b - a).length
    return best, depth


def breach_field(x, y):
    (cx, cy), (rx, ry), _ = BREACH
    jag = 0.12 * wk.perlin(x * 0.8 + 5.0, y * 0.8, 1.0)
    return 1.0 - math.hypot((x - cx) / rx, (y - cy) / ry) + jag


def dome_top(x, y):
    z = live.dome_top(x, y)
    c, depth = crack_field(x, y)
    if c > 0:
        z -= depth * live.smoothstep(0.0, 0.18, c)
    b = breach_field(x, y)
    if b > 0:
        z -= BREACH[2] * live.smoothstep(0.0, 0.35, b)
    return max(z, live.DOME_BOTTOM + 0.6)


def cracked_dome(m):
    """live.dome() with the cracks and the breach in its height field, black along them."""
    plan = ccw(live.dome_plan())

    def paint(x, y, d):
        if crack_field(x, y)[0] > 0 or breach_field(x, y) > 0:
            return "black"
        if live.band_rise(y) > 0.16 and d > 0.5:
            return "red_dark" if y < live.BAND[0] + 0.45 else "red"
        if live.seam_field(x, y) > 0:
            return "brown_lit"
        if live.seam_field(x, y) > -live.SEAM_DARK + live.SEAM[3]:
            return "brown_dark"
        sh = live.shade(x, y)
        if sh > live.DOME_SHADE[1]:
            return "bronze"
        if sh < live.DOME_SHADE[0]:
            return "brown_dark"
        return "brown"

    borders = [(lambda x, y, d: live.band_rise(y), 0.16), (lambda x, y, d: y - live.BAND[0] - 0.45, 0.0),
               (lambda x, y, d: live.seam_field(x, y), 0.0),
               (lambda x, y, d: live.seam_field(x, y), -live.SEAM_DARK + live.SEAM[3]),
               (lambda x, y, d: live.shade(x, y), live.DOME_SHADE[0]),
               (lambda x, y, d: live.shade(x, y), live.DOME_SHADE[1]),
               (lambda x, y, d: crack_field(x, y)[0], 0.0), (lambda x, y, d: breach_field(x, y), 0.0)]
    mats = {key: m[key] for key in ("brown_dark", "brown", "bronze", "brown_lit", "red", "red_dark", "black")}
    obj = relief("dome", [plan], lambda x, y, d: dome_top(x, y), mats, paint=paint, side="brown_dark",
                 bottom=live.DOME_BOTTOM, spacing=0.6, borders=borders, smooth_angle=55)
    return obj


def burn(co):
    v = 0.56 + 0.36 * wk.perlin(co.x * 0.35 + 1.0, co.y * 0.35 - 3.0, co.z * 0.3)
    for centre, reach in BURN_AT:
        v += 0.75 * math.exp(-((co - centre).length / reach) ** 2)
    return v


def build_whole():
    m = live.materials(False)
    # The lamps unlit: dark pink glass.
    m["lamp"] = k.material("dcannon_lamp_dead", palette=0x46, metallic=0.2, roughness=0.3)
    m["lamp_core"] = k.material("dcannon_lamp_core_dead", palette=0x48, metallic=0.2, roughness=0.25)
    dome = cracked_dome(m)
    parts = [dome] + live.lamps(m, live.dome_top) + live.cradle(m) + live.neck(m) + live.shroud(m)
    for obj in parts:
        mk.apply(obj)
    # The shroud torn open at its upper right.
    shroud = bpy.data.objects["shroud"]
    (c, radii, seed) = TEAR
    wk.break_away(shroud, wk.rock("tear", c, radii, m["black"], seed, subdivisions=2, rough=0.35))
    k.smooth(shroud, 40)
    # The collar's shards bent up at the breach, dark chunks in it.
    for i, (outline, z, thick, tilt, key) in enumerate(SHARDS):
        shard(f"collar_shard{i}", outline, z, thick, m[key], tilt)
    for i, (centre, radii) in enumerate(CHUNKS):
        rock(f"chunk{i}", centre, radii, m["black"], 3.0 + i)
    whole = mk.meshes()
    for obj in whole:
        mk.apply(obj)
        if not obj.name.startswith(("chunk", "lamp")):
            scorch(obj, burn, levels=(0.62, 1.05))
    k.smooth(dome, 55)
    bpy.context.view_layer.update()
    return whole, m


PIECES = [(name + "_wreck", sprite, box) for name, sprite, box in live.PIECES]


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    k.reset()
    whole, m = build_whole()
    bpy.context.scene.view_settings.view_transform = "Standard"
    if "preview" in options:
        mk.preview(options["preview"] + "dome_cannon_wreck_whole", whole, size=(24, 56), scale=12, distance=1.6)
    for name, sprite, box in PIECES:
        if only and name not in only:
            continue
        parts = [p for p in (cut(src, box, m["black"]) for src in whole) if p is not None]
        db.drop_unused(parts)
        mk.transform(parts, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
        bpy.context.view_layer.update()
        triangulate(parts)
        parts = [db.join(parts, name)]
        parts[0].data.name = name
        for src in whole:
            src.hide_render = True
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts)
        for obj in parts:
            data = obj.data
            bpy.data.objects.remove(obj)
            if data.users == 0:
                bpy.data.meshes.remove(data)
        for src in whole:
            src.hide_render = False


if __name__ == "__main__":
    build()
