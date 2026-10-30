"""The second player's linked turret's ring bursts (shots sheet sprites 157 and 158, both 1x1: 12 x 14 cells), modelled
(2026-10-30, round 4 of the energy shots' models; until then each was drawn as its sprite with volume and the automatic
glow). Built with polish_shot_sonic.py's Wave (a band between two edges, closed round a ring, on its bands' borders) as
polish_shot_megaring.py builds its ring, imported and never changed.

Who fires them: the second player in two-player games, as the turret linked to player 1's ship (TYR3D_MODE=twin, or
two once the ships are linked), when its rear port is 26 (the Hot Dog's rear gun: a pickup, enemy value -5, gives both
players port 26; the item data's linkGunWeapons[25] is weapon 564): one every 4 frames of the game at 8 pixels a frame,
whichever way the turret points (the sprite is drawn the same every way: port 26 is not among
player_shot_set_direction's headings); weapani 1: a player's shot shows weapani + 1 frames, 157 and 158 by turns.

As the sprites draw them (ramp 7, the fire: 0x70 black-red .. 0x77 red .. 0x7a orange .. 0x7c yellow .. 0x7e pale
yellow): a disc of fire 12 across, in rings: an outer ring, dark red at its rim (0x72, 0x75), orange (0x79), its inner
edge bright yellow (0x7c, 0x7d) a third of the way in; inside it a dark ring (0x72-0x74); inside that a hot inner ring
(157: 0x7a-0x7e, its brightest at the lower right, so that the rings read as a swirl) round a dark eye (0x71); 158 the
same a pixel smaller, its inner ring dim (0x76, a fleck of 0x7a and 0x7c) round a dark red middle (0x73): the burst
pulsing.

The models (shot_turret_157, shot_turret_158; the energy shots' method: half-bodies, palette materials glowing by
shade, the heat in bands whose borders are the mesh's own rows; at most 10 materials): two rings, each a closed Wave
between two circles, round on top, its heat across it from the sprite's rings (ACROSS: the outer ring brightest near
its inner edge, the inner ring in its middle) and a little brighter on one side (SWIRL); between and inside them a dark
membrane (0x72, no glow) a little above the ground (polish_shot_megaring.py's eye). Authored as the sprites are drawn
(yaw 0).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the origin at the
sprite's centre (pixel 6, 7: column c is x = c + 0.5 - 6, row r is y = 6.5 - r); built on z = 0.

models.cfg: see the block's comment; --cfg <file> appends the model and shot lines.

Run: Blender -b --factory-startup -P tools/blender/models/shots/polish_shot_turret.py -- [--only <name,...>]
     [--outdir <dir>] (default assets/models/shots) [--check <sheets dir>] (silhouettes against <dir>/shots.png, from
     TYR3D_EXTRACT) [--preview <prefix>] (top, three-quarter and game-camera views) [--cfg <file>]
"""
import math
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_shot_fireball as kit  # noqa: E402
import polish_shot_sonic as sonic  # noqa: E402
from polish_shot_fireball import k, mk, triangulate, view  # noqa: E402
from polish_shot_zflame import prune  # noqa: E402

OUTDIR = kit.OUTDIR

# The bands of the fire (lowest heat, palette index, emission) and the membrane's index (no glow).
BANDS = [(-99.0, 0x72, 0.22), (3.4, 0x74, 0.26), (5.2, 0x76, 0.33), (7.2, 0x78, 0.4), (9.0, 0x79, 0.46),
         (10.8, 0x7b, 0.52), (12.2, 0x7c, 0.56), (13.4, 0x7e, 0.6)]
MEMBRANE = (0x72, 0.18)  # (palette index, its height over the ground)

# The frames: the disc's middle; each ring's outer and inner radius, its crest's height, where its crest lies across
# (s: 0 its outer edge, 1 its inner edge), how its back falls, its heat across (s, heat: rising to its peak and
# falling), the swirl (how much brighter, towards which way: degrees counter-clockwise from right); the membrane's
# radius; the glow (size, strength, palette index).
FRAMES = {
    157: dict(
        centre=(0.25, -0.4),
        rings=[dict(outer=6.25, inner=2.75, height=1.55, crest=0.62, back=1.1,
                    across=((0.0, 3.6), (0.18, 6.6), (0.34, 8.8), (0.5, 10.4), (0.66, 11.8), (0.84, 13.2), (0.93, 11.0),
                            (1.0, 4.8)), swirl=(0.07, -45.0)),
               dict(outer=1.95, inner=0.55, height=1.05, crest=0.45, back=1.0,
                    across=((0.0, 5.0), (0.25, 10.0), (0.5, 13.6), (0.72, 12.0), (1.0, 4.0)), swirl=(0.1, -45.0))],
        membrane=3.0, glow=(17, 0.5, 0x7a)),
    158: dict(
        centre=(0.0, 0.0),
        rings=[dict(outer=6.0, inner=2.55, height=1.5, crest=0.62, back=1.1,
                    across=((0.0, 3.4), (0.18, 6.2), (0.34, 8.4), (0.5, 10.0), (0.68, 11.4), (0.86, 12.8), (0.94, 10.6),
                            (1.0, 4.6)), swirl=(0.07, 135.0)),
               dict(outer=1.85, inner=0.35, height=0.85, crest=0.45, back=1.0,
                    across=((0.0, 4.2), (0.3, 6.6), (0.55, 7.6), (0.78, 6.8), (1.0, 3.6)), swirl=(0.12, 135.0))],
        membrane=2.85, glow=(17, 0.45, 0x7a)),
}
SAMPLES = (40, 20)  # (points round the outer ring, round the inner one)


def build_frame(name, spec):
    mats = kit.materials("turret_fire", BANDS)
    cx, cy = spec["centre"]
    parts = []
    for i, ring in enumerate(spec["rings"]):
        n = SAMPLES[min(i, 1)]
        thetas = [-math.pi + 2 * math.pi * j / n for j in range(n)]
        outer = [(cx + ring["outer"] * math.cos(t), cy + ring["outer"] * math.sin(t)) for t in thetas]
        inner = [(cx + ring["inner"] * math.cos(t), cy + ring["inner"] * math.sin(t)) for t in thetas]
        us = [t / math.pi for t in thetas]
        across = kit.curve(ring["across"])
        amount, towards = ring["swirl"]
        towards = math.radians(towards)

        def heat(s, u, across=across, amount=amount, towards=towards):
            return across(min(max(s, 0.0), 1.0)) * (1.0 + amount * math.cos(u * math.pi - towards))
        wave = sonic.Wave(outer, inner, us, lambda u, h=ring["height"]: h, heat, BANDS, crest=ring["crest"],
                          back=ring["back"], closed=True, waves=(4.0, 0.02, 1.9), gap=0.3)
        parts.append(prune(wave.build("%s_ring%d" % (name, i), mats)))
    # The membrane: a flat disc a little above the ground under the rings (the dark ring and the eye).
    index, height = MEMBRANE
    mat = kit.lit("turret_membrane_%02x" % index, index, 0.0, roughness=0.6)
    count = 32
    r = spec["membrane"]
    rim = [2 * math.pi * j / count for j in range(count)]
    verts = [(cx, cy, height)] + [(cx + r * math.cos(a), cy + r * math.sin(a), height) for a in rim]
    faces = [(0, 1 + j, 1 + (j + 1) % count) for j in range(count)]
    disc = k.mesh_object(name + "_membrane", verts, faces, mat)
    if disc.data.polygons[0].normal.z < 0:
        disc.data.flip_normals()
    parts.append(disc)
    return parts


def build():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    outdir = options.get("outdir", OUTDIR)
    for sprite, spec in FRAMES.items():
        name = "shot_turret_%d" % sprite
        if only is not None and name not in only:
            continue
        k.reset()
        parts = triangulate(build_frame(name, spec))
        bpy.context.view_layer.update()
        cx, cy = spec["centre"]
        print("== %s (shots %d): rings of fire round a dark eye" % (name, sprite))
        if "check" in options:
            kit.check_lines(name, parts, os.path.join(options["check"], "shots.png"), [(sprite, 0, 0, 0)], (cx, cy))
        bpy.context.scene.view_settings.view_transform = "Standard"
        mk.report(name, parts, os.path.join(outdir, name + ".glb"))
        if "cfg" in options:
            size, strength, index = spec["glow"]
            with open(options["cfg"], "a") as out:
                out.write("model %-18s shots/%s.glb\n" % (name, name))
                out.write("shot shots %-3d %-18s glow=%d:%.2f:%d:%.2f:%.2f\n" % (sprite, name, size, strength, index,
                                                                              cx + 0.0, -cy + 0.0))
        if "preview" in options:
            view(options["preview"] + name, parts)


if __name__ == "__main__":
    build()
