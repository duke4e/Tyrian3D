"""Coin (the coins sheet's sprites 1, 7, 20 and 26: the green 10, gold 25, silver 75 and copper 50 credit coins; 1x1,
12 x 14 pixels; about 570 of them in the levels), polished (2026-10-20; it replaces coin.py's plain disc with a boss).
models.cfg: sprite coins 1/7/20/26 coin roll=frames:12 color=sprite.

The four coins are one picture in other ramps: 20 (silver) is 1 (green) in ramp 0 instead of 2, shade for shade;
7 (gold, ramp 1) and 26 (copper, ramp 4) are it two shades lighter (their outlines, ramps 10 and 4, a shade apart).
Each flips over in six frames (1-6: face on, turning, edge on at 4, turning on): models.cfg rolls the model about
the screen's vertical axis with them, 30 degrees a frame, half a turn in the six frames, so the next 1 shows the
back: both faces carry the same design. No frame models: color=sprite takes each frame's ramp.

As the sprite and its 4x upscales draw it: a disc 11 pixels across (its dark outline included; columns 0-10, rows
1-11), its face flat (shade 7 of the green coin), a raised rim lit at its upper left (shades 13, 10, 9) and darker at
its lower right (5, 4), lighter just inside it on the right (8).

A minted coin: a flat field with a raised rim, its inner side bevelled so it catches the light round the field, its
outer edge rounded into the coin's edge; on each face a raised five-pointed star, its ten facets meeting in ridges
from its middle to its points (so the game's sun lights half of them: it reads as a star at 12 pixels and when the
coin turns). 2.2 pixels thick, so that it is a bar, not a line, when edge on (the sprite's frame 4 is 3 pixels
wide). Glossy and a little metallic, so it shines in the sprite's colour. Palette shades of ramp 0 without
emission (polish_item_kit): color=sprite gives them the frame's ramp; the shades sit between the green coin's and
the gold one's, a little lighter (the game's light darkens what faces away from its sun).

The coin's axis is the screen's Z (its face looks at the camera), its middle at (0, 0.5): the sprite's middle row,
half a pixel right of its middle column, so that it turns in place.

Options after "--": --outdir <dir> (default assets/models/items), --check <sheets dir> (the silhouette against
coins.png), --preview <prefix>, --only <name,...>, --ramp <0-15> (built in that ramp, written as _r<ramp>).
"""
import math
import os
import sys

import bmesh

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_item_kit as kit  # noqa: E402
from polish_item_kit import k  # noqa: E402

CENTRE = (0.0, 0.5)
SPRITE_CENTRE = (-0.5, 0.0)  # how far the sprite draws the coin's middle from the model's (for the check)
SEGMENTS = 64
# The profile from the middle of the face out and down to the coin's middle plane: (radius, height, part of the
# segment from this point to the next). The field, the rim's inner bevel, the rim, its rounded outer edge, the edge.
PROFILE = [
    (0.0, 0.5, "field"), (3.45, 0.5, "bevel"), (3.95, 1.08, "rim"), (4.6, 1.08, "rim"), (4.95, 0.96, "outer"),
    (5.2, 0.72, "outer"), (5.32, 0.48, "edge"), (5.32, 0.0, None),
]
# The star: its points STAR_OUT from the middle, the corners between them STAR_IN, its middle STAR_RISE above the
# field (as high as the rim), its foot sunk into the field.
STAR_OUT, STAR_IN, STAR_RISE = 3.1, 1.38, 0.56

SHADES = {"field": 9, "bevel": 12, "rim": 11, "outer": 10, "edge": 8, "star": 12}
METAL = dict(metallic=0.35, roughness=0.3)
FINISH = {"bevel": dict(metallic=0.35, roughness=0.22), "star": dict(metallic=0.35, roughness=0.24)}


def materials(name, ramp):
    return {key: kit.shade(f"{name}_{key}", s, ramp, **FINISH.get(key, METAL)) for key, s in SHADES.items()}


def body(name, mats):
    """The coin without its stars: the profile turned round the axis, both faces."""
    half = [(r, z, part) for r, z, part in PROFILE]
    # Both faces: the upper half from the middle out, the lower half (mirrored) back in.
    profile = half[:-1] + [(r, -z, part) for r, z, part in reversed(half[:-1])]
    parts = [p[2] for p in half[:-1]] + [p[2] for p in reversed(half[:-2])]
    bm = bmesh.new()
    rings = []
    for r, z, _ in profile:
        if r < 1e-6:
            rings.append([bm.verts.new((CENTRE[0], CENTRE[1], z))])
        else:
            rings.append([bm.verts.new((CENTRE[0] + r * math.cos(2 * math.pi * j / SEGMENTS),
                                        CENTRE[1] + r * math.sin(2 * math.pi * j / SEGMENTS), z))
                          for j in range(SEGMENTS)])
    keys = list(mats)
    for i in range(len(rings) - 1):
        a, b = rings[i], rings[i + 1]
        part = parts[i] if i < len(parts) else "field"
        for j in range(SEGMENTS):
            if len(a) == 1:
                f = bm.faces.new((a[0], b[j], b[(j + 1) % SEGMENTS]))
            elif len(b) == 1:
                f = bm.faces.new((a[j], b[0], a[(j + 1) % SEGMENTS]))
            else:
                f = bm.faces.new((a[j], b[j], b[(j + 1) % SEGMENTS], a[(j + 1) % SEGMENTS]))
            f.material_index = keys.index(part)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = kit.from_bmesh(name, bm)
    for m in mats.values():
        obj.data.materials.append(m)
    # Smooth round the coin, sharp where the profile turns.
    k.smooth(obj, 35)
    return obj


def star(name, mat, face_z, up=True):
    """A raised five-pointed star on the face at height face_z: ten flat facets from its middle to its outline."""
    bm = bmesh.new()
    s = 1.0 if up else -1.0
    apex = bm.verts.new((CENTRE[0], CENTRE[1], s * (face_z + STAR_RISE)))
    outline, foot = [], []
    for i in range(10):
        a = math.radians(90.0 + 36.0 * i)
        r = STAR_OUT if i % 2 == 0 else STAR_IN
        p = (CENTRE[0] + r * math.cos(a), CENTRE[1] + r * math.sin(a))
        outline.append(bm.verts.new((p[0], p[1], s * (face_z + 0.03))))
        foot.append(bm.verts.new((p[0], p[1], s * (face_z - 0.15))))
    for i in range(10):
        j = (i + 1) % 10
        bm.faces.new((apex, outline[i], outline[j]))
        bm.faces.new((outline[i], foot[i], foot[j], outline[j]))
    bm.faces.new(list(reversed(foot)))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = kit.from_bmesh(name, bm, mat)
    return kit.flat_shade(obj)


def build():
    opts = kit.options()
    ramp, _ = kit.ramp_of(opts)
    if not kit.wanted(opts, "coin"):
        return
    k.reset()
    mats = materials("coin", ramp)
    parts = [body("coin", mats), star("coin_star", mats["star"], PROFILE[0][1]),
             star("coin_star_back", mats["star"], PROFILE[0][1], up=False)]
    kit.finish(opts, "coin", parts, 1, large=False, distance=0.3, shift=SPRITE_CENTRE)


if __name__ == "__main__":
    build()
