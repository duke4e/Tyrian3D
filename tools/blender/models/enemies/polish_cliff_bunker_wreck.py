"""The wreck of the sentry box at the foot of TORM's grey cliffs (sheet G 153 above 191: cliff_bunker_top over
cliff_bunker_base), stage 4 of the clean ground (2026-10-25): what the maps paint where the bunkers stand, which
tools/terrain/make_cleanground.py erases and the game shows as stand-ins (models.cfg "wreck g 153
cliff_bunker_top_wreck", "wreck g 191 cliff_bunker_base_wreck", drawn with the live sprite lines' options: yaw=0).

The maps paint two things there (whole coordinates as below):
- On TORM's and BONUS' cliff tiles, where the levels stack 153 over 191 (the top's only painting, 10 of the 28 top
  stand-ins; BOTANY A's 17 tops stand over its pipe, where nothing is erased): the box wrecked and burning, a little
  shorter and lower than the live one (its frame from y 9 down to -3.5, x -10..10), its shutter gone, red and orange
  fire in its window (tongues at x -8..-6, -4..-1, 0..3, 3..7), its frame and brackets standing (the right bracket up
  to y 12), the mount on its top burst and glowing red at (-1, 13), the strut gone; red embers and bits of metal under
  it (y -4..-8).
- Under most bases (BOTANY A's pairs and lone bases, ROOST's, BONUS' and TORM's lone bases: 44 of the 54 base
  stand-ins): what the box stood on, a dark post leaning back (x -2..2, from its foot at y -11 up to y -1) with a fork
  of two thin curved prongs at its top (their tips at (-6, 0) and (6, 0), the left one lit), its foot in a pile of
  broken grey stone (x -4..4, y -10..-15, lit on top).
So the top wreck is the burning box, kept wholly above the sprites' edge (y > 0), and the base wreck the fork post on
its rubble with a few embers: on TORM's cliffs the burnt box stands on its post, and under the pipes and on the
leaves the post stands alone, as the maps paint them.

Built on polish_cliff_bunker.py: its box, frame and brackets with its measures changed for the wreck (the face's foot
higher and lower, its height 8.6 instead of 16.2: the box sunk and crumpled), the shutter and the eye left out (the
window black, fire in it: lumps glowing in palette ramp 7, emission 0.2-0.42), the roll charred and a slat hanging from
it, the mount burst (a bite out of it, an ember in it), a stub of the strut, one hinge knob fallen; the post, the fork
and the rubble built for the base; scorched round the window and the mount (polish_jaw_gun_wreck.scorch). Cut along
y = 0 as the live bunker (polish_arch.py's cut(); only the post's fork reaches near it).

Coordinates as in polish_cliff_bunker.py: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground
(z = 0); the whole's origin is the edge between the two sprites.

models.cfg: model cliff_bunker_top_wreck enemies/cliff_bunker_top_wreck.glb origin; model cliff_bunker_base_wreck
enemies/cliff_bunker_base_wreck.glb origin; wreck g 153 cliff_bunker_top_wreck; wreck g 191 cliff_bunker_base_wreck.

Options after "--": --outdir <dir> (default assets/models/enemies), --preview <prefix>, --whole <file.glb>.
"""
import math
import os
import sys

import bpy
import mathutils.noise as noise
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_arch import cut  # noqa: E402
import polish_cliff_bunker as cb  # noqa: E402
import polish_jaw_gun_wreck as wk  # noqa: E402  (the shared wreck helpers)

# The live box's measures changed for the wreck (polish_cliff_bunker reads them when it builds): sunk and crumpled.
WRECK_MEASURES = {
    "FACE_FOOT": (0.5, 0.4),
    "BOX_H": 8.6,
    "FRAME_S": (0.1, 8.5),
    "WINDOW_S": (0.9, 7.6),
    "KNOB_S": 4.8,
    "MOUNT": (-0.6, 6.6, 8.3, 10.1, -4.2, -0.6),
}
# The fire in the window: tongues (x, s up the face, half-width, half-length, height off the window's floor) in the
# face's frame, the rim's and the core's glow.
FIRE = [(-0.6, 4.2, 7.2, 3.4, 0.5, "dim", "dim"),
        (-6.5, 4.4, 0.7, 2.9, 1.0, "mid", "hot"), (-4.2, 3.2, 0.8, 2.0, 0.9, "dim", "mid"),
        (-2.0, 4.8, 0.9, 2.8, 1.3, "mid", "hot"), (0.6, 3.6, 0.8, 2.2, 1.2, "mid", "hot"),
        (2.6, 5.0, 0.8, 2.4, 1.1, "mid", "hot"), (4.9, 3.8, 0.8, 2.6, 1.0, "dim", "mid"),
        (-4.6, 6.8, 1.6, 0.7, 0.7, "dim", "mid"), (1.8, 7.0, 1.4, 0.6, 0.6, "dim", "mid")]
GLOWS = {"dim": (0x73, 0.22), "mid": (0x76, 0.32), "hot": (0x79, 0.42)}
SLATS = [(4.2, 6.6, -34.0)]      # the slat hanging from the roll at the window's right: x0, x1, turn (degrees)
MOUNT_BITE = ((-0.4, 9.2, -1.6), 1.9)           # the burst in the mount (face frame: x, s, n), radius
MOUNT_EMBER = ((-0.6, 9.0, -1.4), (1.5, 0.9, 0.8))
STRUT_STUB = [(4.6, 9.8, -3.6), (4.4, 11.8, -4.6), (3.6, 13.0, -4.4)]   # (face frame) the strut's broken stub
# The base: the post (from its foot up to its top: x, y, z, radius), the fork's prongs (the left one; mirrored about
# POST_X), the rubble (centre, radii), the embers (centre, radii, rim, core).
POST_X = 0.3
POST = [(POST_X, -11.6, 0.5, 2.0), (POST_X, -8.4, 1.6, 1.8), (POST_X, -5.0, 2.8, 1.65), (POST_X, -1.6, 3.9, 1.55)]
PRONG = [(POST_X - 1.3, -6.6, 2.6, 0.55), (POST_X - 3.4, -5.6, 3.1, 0.5), (POST_X - 4.8, -3.8, 3.6, 0.45),
         (POST_X - 5.3, -1.8, 4.0, 0.4), (POST_X - 5.1, -0.5, 4.2, 0.3)]
RUBBLE = [((-2.0, -12.0, 0.0), (2.3, 2.0, 2.1)), ((2.1, -12.4, 0.0), (2.4, 2.1, 2.2)),
          ((0.0, -14.0, 0.0), (2.4, 1.5, 1.5)), ((-0.2, -10.4, 0.0), (1.9, 1.4, 1.8)),
          ((3.6, -10.6, 0.0), (1.3, 1.2, 1.1)), ((-3.6, -10.2, 0.0), (1.2, 1.1, 1.0))]
BASE_EMBERS = [((1.2, -11.6, 1.9), (0.7, 0.5, 0.3), "dim", "mid"), ((-4.6, -6.6, 0.3), (0.9, 0.5, 0.3), "dim", "dim"),
               ((5.2, -4.4, 0.3), (0.8, 0.45, 0.3), "dim", "dim")]
BITS = [([(-3.0, -5.2), (-1.4, -4.6), (-1.8, -6.6)], 0.0, 0.3, (12.0, -10.0)),
        ([(3.4, -7.4), (5.0, -7.0), (4.6, -8.6), (3.4, -8.4)], 0.0, 0.3, (-8.0, 12.0)),
        ([(-6.6, -9.0), (-5.0, -8.6), (-5.6, -10.2)], 0.0, 0.25, (6.0, 0.0))]
BURN = [((-0.5, 4.2, 2.6), (9.0, 6.0, 6.0), 1.0), ((-0.5, 9.6, 3.8), (4.5, 2.5, 3.5), 0.9)]


def burn(co):
    value = 0.0
    for centre, radii, strength in BURN:
        d = Vector(((co.x - centre[0]) / radii[0], (co.y - centre[1]) / radii[1], (co.z - centre[2]) / radii[2]))
        value += strength * math.exp(-1.3 * d.length_squared)
    return value + 0.18 * noise.noise(co * 0.5 + Vector((2.3, 5.1, -0.7)))


def materials():
    m = cb.materials(((0x70, 0.0), (0x71, 0.0)), None)
    m["soot"] = k.material("soot", palette=0x10, metallic=0.2, roughness=0.8)
    m["stone"] = k.material("cbunker_stone", palette=0x09, metallic=0.1, roughness=0.7)
    m["stone_lit"] = k.material("cbunker_stone_lit", palette=0x0b, metallic=0.1, roughness=0.65)
    for key, (index, strength) in GLOWS.items():
        m[key] = wk.ember_material(index, strength)
    return m


def top_wreck(m):
    """The burnt box (y > 0), in the live box's frame with the wreck's measures."""
    for name, value in WRECK_MEASURES.items():
        setattr(cb, name, value)
    cb.box(m)
    cb.frame(m)
    cb.brackets(m)
    by = {o.name: o for o in mk.meshes()}
    # One hinge knob fallen (the left), two rivets lost; the brow bent.
    wk.delete([by.pop("knob0"), by.pop("rivet1"), by.pop("rivet2")])
    brow = by["brow"]
    pivot = cb.to_world(cb.FRAME_X[1], cb.WINDOW_S[1], 0.4)
    brow.data.transform(Matrix.Translation(pivot) @ Matrix.Rotation(math.radians(-7.0), 4, "Y") @
                        Matrix.Translation(-pivot))
    # The roll at the window's top, charred, and a slat hanging bent from it.
    wx0, wx1 = cb.WINDOW_X
    ws0, ws1 = cb.WINDOW_S
    roll_r = 0.5
    rc = ws1 - roll_r - 0.05
    rings = [[Vector((xx, rc + roll_r * math.cos(2 * math.pi * j / 16), cb.SHUTTER_N - 0.1 +
                      roll_r * math.sin(2 * math.pi * j / 16))) for j in range(16)] for xx in (wx0 + 0.05, wx1 - 0.05)]
    roll = k.loft("roll", rings, m["dark"])
    k.smooth(roll, 50)
    cb.placed(roll)
    for i, (x0, x1, angle) in enumerate(SLATS):
        slat = mk.box(f"slat{i}", x0, x1, rc - 3.2, rc - 0.4, cb.SHUTTER_N - 0.2, cb.SHUTTER_N + 0.1, m["shutter"])
        mk.bevel(slat, 0.1, 1, 35)
        hinge = Vector(((x0 + x1) / 2, rc - 0.4, cb.SHUTTER_N))
        slat.data.transform(Matrix.Translation(hinge) @ Matrix.Rotation(math.radians(angle), 4, "Y") @
                            Matrix.Rotation(math.radians(-25.0), 4, "X") @ Matrix.Translation(-hinge))
        mk.shade(slat, 35)
        cb.placed(slat)
    # The fire in the window: glowing tongues on its floor.
    floor = -cb.RECESS + 0.05
    for i, (x, s, hw, hl, h, rim, core) in enumerate(FIRE):
        for obj in wk.ember(f"fire{i}", (x, s, floor + 0.3 * h), (hw, hl, h), (m[rim], m[core]), 61.0 + 1.9 * i):
            cb.placed(obj)
    # The mount burst, an ember in it; a stub of the strut.
    x0, x1, s0, s1, n0, n1 = cb.MOUNT
    mount = mk.box("mount", x0, x1, s0, s1, n0, n1, m["dark"])
    mk.bevel(mount, 0.4, 2, 35)
    centre, radius = MOUNT_BITE
    mk.boolean(mount, mk.ball("mount_bite", centre, (radius, radius * 0.8, radius), m["pit"], 16, 8), "DIFFERENCE")
    mk.cleanup(mount, dissolve=0.0)
    mk.shade(mount, 35)
    cb.placed(mount)
    for obj in wk.ember("mount_ember", MOUNT_EMBER[0], MOUNT_EMBER[1], (m["mid"], m["hot"]), 71.0):
        cb.placed(obj)
    wk.bent_bar("strut_stub", [tuple(cb.to_world(*p)) + (r,) for p, r in zip(STRUT_STUB, (0.95, 0.85, 0.6))], 0.9,
                m["steel"], 10)


def base_wreck(m):
    """The fork post on its rubble (y < 0), with embers."""
    post = mk.smooth_tube("post", POST, m["dark"], 14, iterations=2)
    k.smooth(post, 60)
    # Its left flank lit, as painted.
    mk.paint(post, lambda c, n: m["roll"] if n.x < -0.6 and n.z > -0.2 else m["frame"] if n.x < -0.25 else None)
    mk.ball("post_cap", POST[-1][:3], (POST[-1][3] * 0.95, POST[-1][3] * 0.6, POST[-1][3] * 0.9), m["dark"], 14, 7)
    for side in (1, -1):
        path = [(p[0] if side > 0 else 2 * POST_X - p[0], p[1], p[2], p[3]) for p in PRONG]
        prong = mk.smooth_tube("prong" + ("_l" if side > 0 else "_r"), path, m["dark"], 10, iterations=2)
        k.smooth(prong, 60)
        lit = m["roll"] if side > 0 else m["frame"]
        mk.paint(prong, lambda c, n, lit=lit: lit if n.z > 0.35 and n.x * side < 0.3 else None)
    for i, (c, radii) in enumerate(RUBBLE):
        stone = wk.rock(f"rubble{i}", c, radii, m["stone"], 81.0 + 1.7 * i, flat=0.0)
        mk.paint(stone, lambda c_, n: m["stone_lit"] if n.z > 0.7 and n.x < 0.2 else
                 m["dark"] if n.z < 0.2 else None)
    for i, (outline, z, th, tilt) in enumerate(BITS):
        wk.shard(f"bit{i}", outline, z, th, m["steel"], tilt)
    for i, (c, radii, rim, core) in enumerate(BASE_EMBERS):
        wk.ember(f"base_ember{i}", c, radii, (m[rim], m[core]), 91.0 + 2.1 * i)


def build_whole():
    m = materials()
    top_wreck(m)
    base_wreck(m)
    parts = mk.meshes()
    for obj in parts:
        mk.apply(obj)
        wk.clip_below(obj, 0.0)
    for obj in parts:
        if obj.name.startswith(("fire", "mount_ember", "base_ember", "rubble", "bit")):
            continue
        wk.scorch(obj, burn, levels=(0.3, 0.72), step=1.2 if obj.name in ("box", "frame", "mount") else None)
        wk.reshade(obj, 35 if obj.name in ("box", "frame", "brow", "mount", "bracket0", "bracket1") else 55,
                   obj.name not in ("box", "frame", "brow", "mount", "bracket0", "bracket1"))
    bpy.context.view_layer.update()
    return [o for o in mk.meshes() if len(o.data.polygons) > 0], m


def build():
    k.reset()
    options = k.args()
    out = mk.outdir(options)
    whole, m = build_whole()
    print("whole cliff bunker wreck: %d triangles, %d objects" % (mk.triangles(whole), len(whole)))
    bpy.context.scene.view_settings.view_transform = "Standard"
    if "whole" in options:
        mk.export(whole, options["whole"])
    if "preview" in options:
        mk.preview(options["preview"] + "cliff_bunker_wreck_whole", whole, size=(24, 56), scale=8, distance=1.4)
    for (name, sprite, (y0, y1)) in cb.PIECES:
        box_xy = (-12.0, 12.0, y0, y1)
        pieces = [p for p in (cut(src, box_xy, m["dark"]) for src in whole) if p is not None]
        mk.transform(pieces, Matrix.Translation((0, -(y0 + y1) / 2, 0)))
        bpy.context.view_layer.update()
        for src in whole:
            src.hide_render = True
        mk.report(name + "_wreck", pieces, os.path.join(out, name + "_wreck.glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name + "_wreck", pieces)
        for obj in pieces:
            bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False


if __name__ == "__main__":
    build()
