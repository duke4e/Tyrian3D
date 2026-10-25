"""What is left of the vent in the ice of CAMANIS and DEEP ICE once it is destroyed (sheet 7 sprite 55's stand-in: what
the ice maps paint where the vent stands, before it comes, once it is shot and where none comes; 45 of them, CAMANIS
89e6d1810ded7622 and DEEP ICE a15166868146cdd3), stage 4 of the clean ground (2026-10-25), built on
polish_ice_vent.py. models.cfg: model ice_vent_wreck enemies/ice_vent_wreck.glb origin; wreck 7 55 ice_vent_wreck
(drawn with sprite 7 55's options, yaw=0 height=-4; its glow= is not drawn for stand-ins).

As the maps paint it at 4x (the same on both maps; CAMANIS at 492, 2563; columns and rows from the sprite's centre): the
same low cone of ice with its ridges, but the orb is gone and the pit blown open, wider (about 12 pixels across where
the live pit is 9, x -6.5..5.5, y -2.5..8.5) and black (0x02) inside; a ring of charred slate round it (ramp 6,
0x63-0x67, where the live lip is white ice); in the pit the burst orb's embers: a hot cluster at its upper left (0x72
0x76 0x7a, the brightest 0x7e, x -4.5..-1.5, y 2.5..6.5) and a crescent of red along its lower right inside (0x70-0x77,
x 0.5..3.5, y -1.5..3.5); dark cracks (0x30-0x33, black at their roots) running out from the pit: straight down the
screen (x 1.5, to y -8), down to the left (x -4.5, y -7), down to the right (to x 8.5, y -4.5), up to the left and up to
the right (to x -7.5, y 11.5 and x 9.5, y 10.5); a few white chips of ice thrown up on the pit's upper right rim (0x3e).

The model: polish_ice_vent.py's ice cone (its ice(), with its fields() replaced: the pit wider and deeper, the lip
broken by gaps and lower, the cracks the painting's, deeper and black at their roots, ridges and cracks as before
otherwise), its colours: the pit's floor black (0x02), its wall charred slate (0x63), the lip charred (0x66, 0x64 where
it is broken), the cracks 0x31, the ice round the pit scorched a few shades darker by a noise field (0x3b -> 0x38 ->
0x35, the ridges 0x3e -> 0x3b); in the pit the burst orb: the live orb's lower part as a bowl (the orb hollowed and
broken off along a jagged fracture, 0.6-2.4 over the ice), its outside charred (0x02, 0x70), its inside and fracture
dark red (0x70); the embers lying in it (ramp 7 glowing faintly in its own colours: 0x74 / 0x77 / 0x79 at 0.28-0.36, the
hot cluster's core 0x7c at 0.42, under the bloom's white); three small shards of the shell thrown onto the rim (charred
plates lying nearly flat, two of them still glowing dimly), white ice chips on the upper right rim. Lower than the live
vent (its top 2.6 where the orb's was 5.66; the model has the origin flag, so the game places it as the live one).

Coordinates as polish_ice_vent.py's: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground (z = 0);
origin at the sprite's centre (pixel 12, 14).

Options after "--": --outdir <dir> (default assets/models/enemies), --preview <prefix>.
"""
import math
import os
import random
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
import polish_ice_vent as live  # noqa: E402
from polish_panel_pills_wreck import clip_below, fbm, heightfield_cutter, perlin  # noqa: E402
from polish_jaw_gun_wreck import ember, ember_material, rock, shard  # noqa: E402
from polish_pyramid_wreck import canonical, triangulate  # noqa: E402

SEED = 55
# The blown pit: its wall's foot and floor, the broken lip round it (radius, height, width), the lip's gaps.
PIT_R, PIT_FLOOR = 5.3, 0.12
LIP_R, LIP_H, LIP_W = 6.15, 0.8, 1.0
LIP_GAPS = [(-90.0, 22.0), (146.0, 18.0)]   # (direction, half-width in degrees: where the big cracks run out)
# The cracks (polish_ice_vent's streaks: from (direction, distance) to (direction, distance), depth, half-width,
# branch): the painting's five, deeper than the live ones.
CRACKS = [(-86.0, 5.6, -83.0, 11.6, 0.8, 1.2, False), (-116.0, 6.0, -108.0, 9.6, 0.5, 0.6, False),
          (-32.0, 6.2, -40.0, 9.8, 0.55, 0.7, False), (146.0, 5.8, 136.0, 10.4, 0.5, 0.85, False),
          (58.0, 6.0, 50.0, 9.4, 0.4, 0.55, False)]
# The ridges kept from the live vent (the white ones that still run out from the lip), shortened a little.
RIDGES = [(-130.0, 6.2, -128.0, 12.0, 1.4, 1.3, False), (-70.0, 6.2, -63.0, 11.4, 1.3, 1.25, False),
          (10.0, 6.2, 4.0, 9.4, 1.0, 1.05, False), (176.0, 6.2, 184.0, 9.6, 1.05, 1.1, False),
          (118.0, 6.4, 112.0, 8.0, 0.6, 0.85, False), (-142.0, 8.6, -156.0, 11.6, 0.85, 0.85, True)]
# The burst orb: the live orb's middle and radii; the fracture's height (mean, how much it wanders), the shell's wall.
ORB_C = Vector((live.CENTRE[0], live.CENTRE[1], live.ORB_Z))
ORB_RADII = (live.ORB_R, live.ORB_R * 0.96, live.ORB_R * 0.92)
FRACTURE_Z, FRACTURE_JAG, SHELL = 1.15, 0.6, 0.6
# The embers: (x, y, z), radii, rim and core (palette, strength).
HOT = ((0x79, 0.36), (0x7c, 0.42))
RED = ((0x74, 0.28), (0x77, 0.34))
EMBERS = [((-2.8, 4.5, 0.4), (2.1, 1.8, 0.8), HOT), ((-1.4, 6.0, 0.4), (1.2, 0.9, 0.55), HOT),
          ((1.2, 0.1, 0.4), (1.5, 1.1, 0.6), RED), ((2.6, 1.0, 0.4), (1.3, 1.4, 0.65), RED),
          ((3.0, 2.7, 0.4), (1.0, 1.3, 0.6), RED), ((-0.4, -0.5, 0.4), (1.1, 0.8, 0.5), RED)]
# Lumps of the burst shell in the pit (x, y), size.
LUMPS = [((-0.8, 1.6), 1.4), ((0.8, 4.4), 1.2), ((-3.6, 2.0), 1.0), ((1.6, 5.6), 0.9), ((-0.6, 6.4), 0.9)]
# Shards of the shell thrown out: outline round (x, y) (as offsets), z, thickness, tilt (degrees about x, y), glowing.
SHARDS = [((6.4, 6.0), [(-0.8, -0.6), (0.9, -0.4), (0.2, 0.8)], (-6.0, 8.0), True),
          ((-6.6, 0.8), [(-0.8, -0.4), (0.7, -0.6), (0.6, 0.5), (-0.5, 0.6)], (4.0, 6.0), False),
          ((-2.2, 8.4), [(-0.7, -0.4), (0.7, -0.5), (0.3, 0.5), (-0.4, 0.5)], (8.0, 2.0), True)]
# White chips of ice thrown up on the pit's upper right rim (x, y), size.
CHIPS = [((3.4, 8.4), 1.1), ((4.6, 7.6), 0.8), ((2.2, 9.0), 0.7)]


def smoothstep(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def gap(theta):
    """How much the lip is broken away in the direction theta (0 standing, 1 gone)."""
    d = math.degrees(theta)
    out = 0.0
    for a, w in LIP_GAPS:
        delta = (d - a + 180.0) % 360.0 - 180.0
        out = max(out, 1.0 - smoothstep(w * 0.55, w, abs(delta)))
    return out


def fields(r, theta):
    """polish_ice_vent.fields() for the wreck: the cone, the lip lower and broken by gaps, the ridges kept and the
    deeper cracks; inside the lip the blown pit."""
    s = r / live.edge_r(theta)
    cone = live.CONE_H * max(0.0, 1.0 - s * s) ** 1.6 / max(1e-3, (1.0 - (LIP_R / live.edge_r(theta)) ** 2) ** 1.6)
    cone = min(cone, live.CONE_H * 1.25)
    wobble = 1.0 + 0.3 * perlin(math.cos(theta) * 2.2 + 3.1, math.sin(theta) * 2.2 - 1.7, 0.4)
    lip = LIP_H * wobble * (1.0 - 0.85 * gap(theta)) * math.exp(-((r - LIP_R - 0.2 * math.sin(5 * theta + 1.3))
                                                                  / LIP_W) ** 2)
    p = Vector((r * math.cos(theta), r * math.sin(theta), 0.0))
    ridge = height = 0.0
    for seg in RIDGES:
        f, t = live.streak(p, seg)
        h = seg[4] * (1.0 - 0.5 * t) * (1.0 + 0.1 * math.sin(9.0 * t + seg[0]))
        if f * h > height:
            height, ridge = f * h, f
    crack = depth = 0.0
    for seg in CRACKS:
        f, _ = live.streak(p, seg)
        if f * seg[4] > depth:
            depth, crack = f * seg[4], f
    z = cone + lip + height * smoothstep(PIT_R, LIP_R, r) - depth
    if r < LIP_R:  # the fall into the pit inside the lip
        f = smoothstep(PIT_R - 0.7, LIP_R - 0.1, r)
        z = PIT_FLOOR + (z - PIT_FLOOR) * f
    z *= smoothstep(1.0, 0.85, s)
    return max(z, 0.0), ridge, crack


def ring_radii():
    """The rings' radii (polish_ice_vent.ring_radii() for the wider pit): dense over the pit's wall and the lip."""
    inner = [1.6, 2.6, 3.4, 4.0, 4.45, 4.8, 5.05, 5.3, 5.55, 5.8, 6.05, 6.3, 6.6, 6.95, 7.35]
    outer = [7.35 + (live.EDGE_R - 7.35) * (i / 12) ** 0.92 for i in range(1, 13)]
    return inner, outer


def materials():
    ice_ = dict(metallic=0.1, roughness=0.28)
    m = {
        "ice": k.material("ventwreck_ice", palette=0x3b, **ice_),
        "ice_light": k.material("ventwreck_lip", palette=0x66, metallic=0.15, roughness=0.55),
        "ice_white": k.material("ventwreck_ice_white", palette=0x3e, metallic=0.1, roughness=0.22),
        "crack": k.material("ventwreck_crack", palette=0x31, metallic=0.1, roughness=0.5),
        "scorch": k.material("ventwreck_pit_wall", palette=0x63, metallic=0.15, roughness=0.65),
        "scorch_hot": k.material("ventwreck_pit", palette=0x02, metallic=0.1, roughness=0.8),
    }
    m["lip_broken"] = k.material("ventwreck_lip_broken", palette=0x64, metallic=0.15, roughness=0.6)
    m["ice_burnt"] = k.material("ventwreck_ice_burnt", palette=0x38, **ice_)
    m["ice_dark"] = m["ice_burnt"]   # (the skirt, under the ground)
    m["ice_char"] = k.material("ventwreck_ice_char", palette=0x35, metallic=0.1, roughness=0.4)
    m["shell"] = m["scorch_hot"]   # (the orb's charred shell: the pit's black)
    m["shell_red"] = k.material("ventwreck_shell_red", palette=0x70, metallic=0.2, roughness=0.6)
    m["inside"] = m["shell_red"]
    for key, (index, strength) in (("rim_hot", HOT[0]), ("core_hot", HOT[1]), ("rim_red", RED[0]),
                                   ("core_red", RED[1])):
        m[key] = ember_material(index, strength)   # (ember_material names them by colour: shared where alike)
    return m


def burn(x, y):
    """The scorch round the pit: strongest at its rim, torn by noise."""
    r = math.hypot(x - live.CENTRE[0], y - live.CENTRE[1])
    near = 1.0 if r <= 6.0 else math.exp(-((r - 6.0) / 1.7) ** 2)
    return near + 0.4 * fbm(x * 0.35 + 7.0, y * 0.35 - 3.0, 0.5, 3)


def ice(m):
    live.PIT_R, live.PIT_FLOOR, live.LIP_R, live.LIP_H, live.LIP_W = PIT_R, PIT_FLOOR, LIP_R, LIP_H, LIP_W
    live.fields = fields
    live.ring_radii = ring_radii
    live.SEGMENTS = 96
    obj = live.ice(m)
    cx, cy = live.CENTRE
    # The lip broken where its gaps are; the ice round the pit scorched darker.
    slots = {mat.name: i for i, mat in enumerate(obj.data.materials)}
    lip, white, plain = slots.get(m["ice_light"].name), slots.get(m["ice_white"].name), slots.get(m["ice"].name)
    for poly in obj.data.polygons:
        c = poly.center
        if c.z < -0.02:
            continue
        theta = math.atan2(c.y - cy, c.x - cx)
        b = burn(c.x, c.y)
        if poly.material_index == lip and gap(theta) > 0.4:
            poly.material_index = mk.slot_of(obj, m["lip_broken"])
        elif poly.material_index == plain and b > 0.95:
            poly.material_index = mk.slot_of(obj, m["ice_char"])
        elif poly.material_index == plain and b > 0.55:
            poly.material_index = mk.slot_of(obj, m["ice_burnt"])
        elif poly.material_index == white and b > 0.8:
            poly.material_index = mk.slot_of(obj, m["ice"])
    return obj


def fracture_z(x, y):
    return FRACTURE_Z + FRACTURE_JAG * fbm(x * 0.42 + 2.0, y * 0.42 - 5.0, 1.3, 3) + \
        0.5 * smoothstep(1.0, 4.0, x - live.CENTRE[0])   # (higher at its right, as the painting's dark rim runs)


def burst_orb(m):
    """The orb's lower part: a bowl (the orb less a smaller orb inside it) broken off along a jagged fracture."""
    shell = mk.ball("orb_shell", tuple(ORB_C), ORB_RADII, m["shell"], 36, 18)
    inner = mk.ball("orb_inner", tuple(ORB_C), tuple(r - SHELL for r in ORB_RADII), m["inside"], 28, 14)
    cut = heightfield_cutter("orb_fracture", ORB_C.x - 5.0, ORB_C.x + 5.0, ORB_C.y - 5.0, ORB_C.y + 5.0, 0.5,
                             fracture_z, 9.0, m["inside"])
    mk.apply(shell)
    mk.boolean(shell, [cut, inner], "DIFFERENCE")
    mk.cleanup(shell, dissolve=0.0)
    canonical(shell)
    clip_below([shell], PIT_FLOOR - 0.4)   # (the rest lies in the ice)
    # The shell's outside charred in patches of dark red; its broken edge and inside dark red.
    slot_red = mk.slot_of(shell, m["shell_red"])
    slot_shell = mk.slot_of(shell, m["shell"])
    for poly in shell.data.polygons:
        c = poly.center
        if poly.material_index == slot_shell and fbm(c.x * 0.6 + 1.0, c.y * 0.6, c.z * 0.6, 2) > 0.25:
            poly.material_index = slot_red
    k.smooth(shell, 50)
    return shell


def debris(m):
    rng = random.Random(SEED)
    parts = []
    for i, (centre, radii, (rim, core)) in enumerate(EMBERS):
        mats = (m["rim_hot"], m["core_hot"]) if rim == HOT[0] else (m["rim_red"], m["core_red"])
        parts += ember(f"ember{i}", centre, radii, mats, 3.0 + 1.7 * i)
    for i, ((x, y), size) in enumerate(LUMPS):
        parts.append(rock(f"lump{i}", (x, y, PIT_FLOOR - 0.1), (size * 0.6, size * 0.5, size * 0.4),
                          (m["shell"], m["shell_red"])[i % 2], 9.0 + i, flat=0.0))
    for i, ((x, y), outline, tilt, glowing) in enumerate(SHARDS):
        z = fields(math.hypot(x - live.CENTRE[0], y - live.CENTRE[1]),
                   math.atan2(y - live.CENTRE[1], x - live.CENTRE[0]))[0]
        pts = [(x + dx, y + dy) for dx, dy in outline]
        parts.append(shard(f"shard{i}", pts, z - 0.1, 0.28, m["rim_red"] if glowing else m["shell_red"], tilt))
    for i, ((x, y), size) in enumerate(CHIPS):
        z = fields(math.hypot(x - live.CENTRE[0], y - live.CENTRE[1]),
                   math.atan2(y - live.CENTRE[1], x - live.CENTRE[0]))[0]
        parts.append(rock(f"chip{i}", (x, y, z - 0.15), (size * 0.6, size * 0.45, size * 0.55), m["ice_white"],
                          21.0 + rng.uniform(0, 5), flat=z - 0.15))
    return parts


def build():
    options = k.args()
    k.reset()
    m = materials()
    ice(m)
    burst_orb(m)
    debris(m)
    parts = [o for o in mk.meshes() if len(o.data.polygons) > 0]
    for obj in parts:
        mk.apply(obj)
    triangulate(parts)
    bpy.context.view_layer.update()
    bpy.context.scene.view_settings.view_transform = "Standard"
    mk.report("ice_vent_wreck", parts, os.path.join(mk.outdir(options), "ice_vent_wreck.glb"))
    if "preview" in options:
        mk.preview(options["preview"] + "ice_vent_wreck", parts)


if __name__ == "__main__":
    build()
