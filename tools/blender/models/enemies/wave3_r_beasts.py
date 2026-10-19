"""Enemies of wave 3, batch R (sheet G), the creatures and ships of GRYPHON, GEM WAR, MARKERS, GYGES,
MISTAKES and SOH JIN; modelled as their sprites look (models.cfg: yaw=0). The grey machines on TORM's
leaves are in wave3_r.py.
(GRYPHON's blue orb tower, orb_tower (G 201), is built by polish_orb_tower.py, GEM WAR's blue chevron (G 163) by
polish_blue_chevron.py and GYGES' violet pincer (G 121) by polish_violet_pincer.py.)

- tusk_beetle (G 49): SOH JIN's and MISTAKES' golden beetle (enemy 778): a ridged carapace, two horns
  sweeping up and out from its shoulders, a leaf-shaped plate on each side and two long tusks curving
  down round an open ring under it (its frames close the tusks a little).
- violet_shell (G 55): GYGES' violet shell (custom events 51): a ribbed violet dome over a lower shell of
  two lobes, a blue gem glowing in a socket in its front and three red dots over it.

G 77 (enemies 186-189, the molten crystal of GYGES and MISTAKES) has no model: its frames turn a pyramid
into a ball and the ball into a cube and back, which no one static model can show; its sprite's volume
follows the frames.

usage: Blender -b --factory-startup -P wave3_r_beasts.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1]
"""
import math
import os
import sys

from mathutils import Matrix

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_r_kit as r  # noqa: E402
from wave3_r_kit import art, k, sh, w, pal  # noqa: E402

px, py = w.px, w.py


def ramp_bands(prefix, ramp, shades, metallic=0.4, roughness=0.4):
    """Materials of one palette ramp by shade: bands [(lowest shade, material)] for the given shades."""
    out = []
    for i, s in enumerate(shades):
        lowest = 0 if i == 0 else (shades[i - 1] + s) / 2
        out.append((lowest, pal(f"{prefix}_{s:x}", ramp * 16 + s, metallic=metallic, roughness=roughness)))
    return out


def painter(g, keep, bands, origin=(12, 14), wall_drop=2.0, under=None, blur=1, lift=0.0):
    """paint_faces function: faces take the band of the sprite's shade under them (the pixels keep(index)
    accepts), steep faces a band `wall_drop` darker, faces looking down `under` (default the darkest)."""
    shade = w.sampler(g, origin, value=lambda v: v & 15, blur=blur, keep=lambda v: v is not None and keep(v))

    def pick(c, n):
        if n.z < -0.4:
            return under or bands[0][1]
        s = shade(c.x, c.y) + lift
        if n.z < 0.45:
            s -= wall_drop
        return r.band(s, bands)
    return pick


# --- G 201: the orb tower ---------------------------------------------------------------------------

# --- G 49: the tusked beetle ----------------------------------------------------------------------------

@r.model("tusk_beetle", [(49, True)])
def tusk_beetle():
    """A golden beetle: a ridged carapace, two horns sweeping up and out from its shoulders, a leaf-shaped
    plate on each side and two long tusks curving down round an open ring under it."""
    shell = pal("beetle_shell", 0x17, metallic=0.55, roughness=0.3)
    ridge = pal("beetle_ridge", 0x1c, metallic=0.5, roughness=0.2)
    tusk_light = pal("beetle_tusk", 0x18, metallic=0.5, roughness=0.25)
    axis = 0.5

    def pod(name, centre, radii, angle, mat, segments=20):
        obj = w.sphere(name, (0, 0, 0), radii, mat, segments, segments // 2)
        obj.data.transform(Matrix.Translation(centre) @ Matrix.Rotation(math.radians(angle), 4, "Z"))
        return obj

    # The carapace: a wide shield, broad at its top, narrowing to its rear, a ridge down its middle.
    cx = -0.4
    sections = [(py(12.8), 2.4, 2.6), (py(11.5), 3.6, 3.8), (py(9.5), 4.6, 4.8), (py(6.5), 5.2, 5.4), (py(3.5), 5.2, 5.6),
                (py(1.5), 4.7, 5.2), (py(0.3), 3.6, 4.2), (py(-0.3), 2.0, 3.0)]
    rings = [k.ring(y, hw, h, 32, z=0.0, x=cx, top=1.0, bottom=0.35, power=2.4) for y, hw, h in sections]
    body = k.loft("carapace", rings, shell, start_point=(cx, sections[0][0] - 0.3, 0.8),
                  end_point=(cx, sections[-1][0] + 0.3, 1.2))
    k.smooth(body, 50)
    body.data.transform(Matrix.Translation((0, 0, 0.6)))
    w.tube("ridge", w.catmull([(cx - 0.3, py(-0.2), 3.6), (cx - 0.5, py(2.0), 5.8), (cx - 0.4, py(6.0), 6.2),
                               (cx - 0.2, py(10.0), 5.0), (cx, py(12.4), 2.8)], 0.5), 0.8, ridge, 10, squash=0.7)
    for s_ in (-1, 1):
        def X(dx):
            return axis + s_ * dx
        # The leaf-shaped side plate, and the horn sweeping up and out of it to a point.
        pod(f"plate{s_}", (X(5.6), py(8.0), 3.0), (3.0, 4.9, 2.0), s_ * 35, shell)
        path = [(X(4.0), py(8.5), 3.6), (X(6.2), py(5.5), 4.6), (X(8.4), py(3.0), 5.2), (X(10.0), py(0.6), 5.2)]
        pts = w.catmull(path, 0.45)
        w.tube(f"horn{s_}", pts, [2.3 * (1.0 - i / (len(pts) - 1)) ** 0.9 + 0.2 for i in range(len(pts))],
                      shell, 12)
        # The tusk: from under the carapace, out and down, back in to its point.
        path = [(X(2.6), py(12.3), 3.0), (X(4.4), py(15.2), 3.4), (X(6.4), py(18.6), 3.0), (X(6.6), py(22.0), 2.2),
                (X(5.4), py(25.2), 1.4), (X(3.6), py(26.6), 0.9)]
        pts = w.catmull(path, 0.45)
        w.tube(f"tusk{s_}", pts, [2.2 - 1.5 * (i / (len(pts) - 1)) ** 1.4 for i in range(len(pts))], tusk_light, 12)
    r.budget(4800, floor=600)


# --- G 55: the violet shell -----------------------------------------------------------------------------

@r.model("violet_shell", [(55, True)])
def violet_shell():
    """A ribbed violet dome over a lower shell of two lobes, a blue gem glowing in a socket in its front,
    three red dots over the gem."""
    g = w.grid(art.SHELL, 24)
    bands = ramp_bands("shell", 5, [1, 2, 3, 5, 7, 9, 0xb, 0xc], metallic=0.3, roughness=0.32)
    gem = pal("shell_gem", 0x93, metallic=0.1, roughness=0.1, glow=0.9)
    gem_hot = pal("shell_gem_hot", 0x95, metallic=0.0, roughness=0.1, glow=1.4)
    dot = pal("shell_dot", 0x43, metallic=0.1, roughness=0.3, glow=0.6)
    socket = pal("shell_socket", 0x50, metallic=0.2, roughness=0.5)
    paint = painter(g, lambda v: v >> 4 == 5, bands, lift=0.6, wall_drop=1.5)
    rows = w.regions(g, lambda v, c, row: "b")
    cx = px(11)

    def shape(x, y, z):
        # The dome (rows 0-11) high, its ribs; the lower lobes lower; a groove between dome and lobes.
        dome = 3.2 * math.exp(-(((x - cx) / 6.5) ** 2 + ((y - 5.0) / 6.0) ** 2))
        ribs = 0.35 * math.cos((x - cx) * 2 * math.pi / 3.2) * r.smoothstep(2.0, 8.0, y) * (abs(x - cx) < 6.5)
        groove = -0.8 * math.exp(-((y + 0.2) / 0.7) ** 2) * r.smoothstep(2.5, 5.0, abs(x - cx))
        return z + dome + ribs + groove
    body = r.inflated("body", rows, "b", bands[3][1], sh.round_profile(0.6, max_height=4.5, min_height=1.0),
                      grow=0.1, z_fn=shape, spacing=0.45, bottom=0.3)
    w.paint_faces(body, paint)
    # The gem in its socket (rows 13-15), the red dots over it (rows 9-10).
    gz = sh.surface_z(body, cx, py(14.0), 4.0)
    w.hoop("socket", (cx, py(14.0), gz - 0.4), [(1.8, -0.3), (2.9, -0.3), (2.9, 0.3), (2.0, 0.6)], socket, 24,
           scale_y=0.7)
    w.sphere("gem", (cx, py(14.0), gz - 0.2), (2.3, 1.6, 1.2), gem, 16, 8)
    w.sphere("gem_hot", (cx - 0.4, py(13.8), gz + 0.6), (0.9, 0.7, 0.45), gem_hot, 10, 5)
    for i, (c, row) in enumerate(((11, 9), (10, 10), (12, 10))):
        x, y = px(c), py(row)
        w.sphere(f"dot{i}", (x, y, sh.surface_z(body, x, y, 4.0) - 0.1), (0.55, 0.55, 0.35), dot, 10, 5)
    r.budget(4800, floor=600)


if __name__ == "__main__":
    r.run()
