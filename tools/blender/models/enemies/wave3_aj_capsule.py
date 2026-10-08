"""TIME WAR's blue capsule (wave 3, batch AJ; sheet 9), modelled as its sprites look (models.cfg: yaw=0); the rest of
the sheet is in wave3_aj.py, wave3_aj_head.py, wave3_aj_eye.py and wave3_aj_dread.py, the kit in wave3_aj_kit.py,
the pixels in wave3_aj_art.py.

The level draws it in the sky from eight sprites, two by two, 48 x 112 pixels (enemies 645, 646 at (100, -84),
(124, -84); 647, 648 at (100, -56) ..; 649, 650 at (100, -28) ..; 651, 652 at (100, 0) ..): 16 18 above 54 56
above 244 246 above 92 94 (time_capsule_<sprite>, origin). Its frames pulse the blue light of the glass and the
stripe (16 -> 168 -> 250 -> 168, 54 -> 206 -> 126, 92 -> 282 -> 130); the model's glass glows instead.

A long capsule lying along the screen, its nose up: a glossy blue glass dome over its front half, a grey spine
down its middle; a raised grey collar; a band of blue windows in grey frames; its grey tail with panel bands and
a glowing blue channel down its middle to the tip. It rises about 15 pixels.

usage: Blender -b --factory-startup -P wave3_aj_capsule.py -- [--only name,name] [--preview <prefix>] [--check 1]
       [--stats 1] [--whole <prefix>]
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_aj_kit as kit  # noqa: E402
from wave3_aj_kit import k, Painter, smoothstep  # noqa: E402

CAPSULE = kit.frame("CAPSULE", 48, (24, 56))
F = CAPSULE
AXIS = 24.0
HEIGHT = 14.0


def _rows():
    """Each row's middle and half-width (from the outline), smoothed over a few rows."""
    raw = {}
    for r in range(F.height):
        cols = [c for c in range(F.width) if F.get(c, r) is not None]
        if cols:
            raw[r] = ((cols[0] + cols[-1] + 1) / 2.0, (cols[-1] + 1 - cols[0]) / 2.0)
    out = {}
    for r in raw:
        near = [raw[q] for q in range(r - 2, r + 3) if q in raw]
        out[r] = (sum(v[0] for v in near) / len(near), max(1.0, sum(v[1] for v in near) / len(near)))
    return out


ROWS = _rows()


def row_shape(r):
    r0 = min(max(int(math.floor(r - 0.5)), min(ROWS)), max(ROWS))
    r1 = min(r0 + 1, max(ROWS))
    t = min(1.0, max(0.0, r - 0.5 - r0))
    a, b = ROWS.get(r0, (AXIS, 1.0)), ROWS.get(r1, (AXIS, 1.0))
    return a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t


def band(r, r0, r1, soft=0.6):
    return smoothstep(r0 - soft, r0 + soft, r) * (1.0 - smoothstep(r1 - soft, r1 + soft, r))


def hull_h(c, r):
    cc, hw = row_shape(r)
    # The hull's section: a flattened ellipse, as high as HEIGHT where the capsule is widest.
    h = HEIGHT * min(1.0, hw / 23.5) ** 0.5
    q = 1.0 - ((c - cc) / (hw + 0.3)) ** 2
    z = h * math.sqrt(max(q, 0.0))
    u = abs(c - AXIS)
    # The spine down the glass (rows 1-44), the raised collar (rows 45-58), the windows set in (rows 59-71), the
    # channel down the tail (rows 73-111).
    z += 1.5 * band(r, 1.5, 58.5) * (1.0 - smoothstep(5.2, 6.4, u))
    z += 0.9 * band(r, 45.0, 58.5)
    val = F.get(int(c), int(r))
    if 58.5 < r < 72.0 and val is not None and val >> 4 == 9:
        z -= 0.7
    if r > 72.5:
        z -= 0.9 * (1.0 - smoothstep(3.6, 4.6, u)) * band(r, 73.0, 112.0)
    return z


def capsule_whole():
    grey = Painter("tcap", shades={0: (1, 2, 3, 4, 5, 6, 7, 8, 9, 0xa, 0xb, 0xc, 0xe), 6: (2, 6, 7), 5: (2, 3, 4, 5, 6)},
                   metallic=0.45, roughness=0.32)
    glass = Painter("tcap_glass", shades={9: tuple(range(0, 16)), 3: (4, 8, 0xe, 0xf)}, metallic=0.15, roughness=0.07,
                    glow={**{0x90 + s: 0.25 + 0.04 * s for s in range(16)}, 0x3e: 0.8, 0x3f: 0.9})
    polys = kit.outlines_of(F, lambda val, c, r: True, smooth=2, epsilon=0.3)

    def z_of(x, y, e):
        c, r = x + F.ox, F.oy - y
        return 0.6 + (hull_h(c, r) - 0.6) * e
    body = kit.heightfield("tcap", polys, z_of, grey(0x05), spacing=1.0, edge=1.2)
    k.smooth(body, 40)
    kit.pixelate(body, F)

    def pick(c, nrm):
        val = F.at(c.x, c.y)
        if val is None:
            return None
        if val >> 4 in (9, 3):
            return glass(val)
        return None
    kit.paint_sprite(body, F, grey, wall_steps=-1, keep=lambda val: val >> 4 not in (9, 3), default=grey(0x03),
                     under=grey(0x01))
    kit.paint_faces(body, lambda c, nrm: glass(F.at(c.x, c.y)) if nrm.z > -0.3 and pick(c, nrm) else None)
    kit.merge_bottom(body)
    kit.flatten_under(kit.meshes(), 0.0)


PIECES = [(16, 0, 0), (18, 24, 0), (54, 0, 28), (56, 24, 28), (244, 0, 56), (246, 24, 56), (92, 0, 84), (94, 24, 84)]

kit.PROTECT += ["tcap"]
kit.pieced("time_capsule", capsule_whole, (48, 112), [kit.piece(f"time_capsule_{s}", F, c0, r0) for s, c0, r0 in PIECES])


if __name__ == "__main__":
    kit.run()
