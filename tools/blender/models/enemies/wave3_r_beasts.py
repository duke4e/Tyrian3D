"""Enemies of wave 3, batch R (sheet G), the creatures and ships of GRYPHON, GEM WAR, MARKERS, GYGES,
MISTAKES and SOH JIN; modelled as their sprites look (models.cfg: yaw=0). The grey machines on TORM's
leaves are in wave3_r.py.

- orb_tower (G 201): GRYPHON's blue tower (custom events 51, 144 of them): a glowing pale blue orb on a
  collar at the top of a tapering body with a square port through it, two pillars down its front, a
  wing block out to each side and brown claws at its foot.
- blue_chevron (G 163): GEM WAR's and MARKERS' blue chevron rising from the bottom of the screen (enemy
  809): an armoured arrowhead pointing up the screen, two shoulder plates with pale rims, two red eyes
  glowing in the crease under them, broad plates sweeping down to red-tipped wings and a notch between
  them.
- violet_pincer (G 121): GYGES' and MISTAKES' violet pincer (enemy 184): a glossy violet ball of a head
  and two arms of three jointed segments hanging from it in an arch, ending in golden fangs curving in
  (its frames close the arms a little and brighten the head).
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

@r.model("orb_tower", [(201, True)])
def orb_tower():
    """A pale blue orb glowing on a collar at the top of a tapering blue body with a port through it and
    two light pillars down its front, a wing block out to each side, brown claws at its foot."""
    g = w.grid(art.TOWER, 24)
    bands = ramp_bands("tower", 3, [1, 3, 5, 7, 9, 0xb, 0xd], metallic=0.15, roughness=0.35)
    orb = pal("tower_orb", 0x3b, metallic=0.05, roughness=0.12, glow=0.6)
    orb_hot = pal("tower_orb_hot", 0x3e, metallic=0.0, roughness=0.1, glow=1.1)
    claw = pal("tower_claw", 0xa5, metallic=0.2, roughness=0.45)
    claw_light = pal("tower_claw_light", 0xa9, metallic=0.2, roughness=0.4)
    paint = painter(g, lambda v: v >> 4 == 3, bands, lift=1.0)

    def body_char(v, c, row):
        if v >> 4 != 3 or v == 0x30:
            return "."  # the outline (the darkest blue) is left to the parts' grown edges
        if row <= 7:
            return "o"
        if 13 <= row <= 18 and (c <= 5 or c >= 17):
            return "w"
        return "b"
    rows = w.regions(g, body_char)

    # The body: high under the orb, lower towards its foot; the port goes through it.
    def body_z(x, y, z):
        return z * (0.5 + 0.5 * r.smoothstep(-12.0, 5.0, y))
    body = r.inflated("body", rows, "b", bands[3][1], sh.pillow_profile(8.6, 2.4, crown=0.8), z_fn=body_z, grow=0.95,
                      spacing=0.6)
    w.paint_faces(body, paint)
    wings = r.inflated("wings", rows, "w", bands[3][1], sh.pillow_profile(4.6, 1.5, crown=0.4), grow=0.95,
                       spacing=0.6)
    w.paint_faces(wings, paint)
    # The pillars down the front (columns 6-7 and 15-16).
    for c in (6.5, 15.5):
        x = px(c)
        top = [(x, y, body_z(x, y, 8.6) + 0.15) for y in (py(12.5), py(16), py(19.5), py(21.5))]
        w.tube(f"pillar{c}", w.catmull(top, 0.8), 0.8, bands[4][1], 10, squash=0.6)
    # The collar and the orb, its top glowing brighter.
    ox, oy = px(11), py(4.3)
    w.hoop("collar", (ox, oy - 1.4, 6.6), [(3.2, -0.6), (4.6, -0.5), (4.8, 0.3), (3.6, 0.8)], bands[4][1], 32,
           scale_y=0.8)
    ball = w.sphere("orb", (ox, oy, 9.4), (5.3, 4.9, 4.6), orb, 28, 14)
    w.sphere("orb_core", (ox - 0.6, oy + 0.5, 11.0), (3.5, 3.4, 3.6), orb_hot, 24, 12)
    # The claws at its foot, curling out and down.
    for s in (-1, 1):
        cx0 = ox + s * 4.2
        path = [(cx0, py(20.5), 3.0), (cx0 + s * 2.4, py(21.5), 2.6), (cx0 + s * 4.6, py(22.5), 1.4),
                (cx0 + s * 5.4, py(24.0), 0.3)]
        pts = w.catmull(path, 0.6)
        w.tube(f"claw{s}", pts, [1.35 - 0.85 * (i / (len(pts) - 1)) ** 1.5 for i in range(len(pts))], claw, 10)
        w.sphere(f"claw_knuckle{s}", (cx0 + s * 2.2, py(21.2), 3.2), (1.3, 1.1, 0.9), claw_light, 12, 6)
    r.budget(4800, floor=600)


# --- G 163: the blue chevron ---------------------------------------------------------------------------

@r.model("blue_chevron", [(163, True)])
def blue_chevron():
    """An armoured blue arrowhead pointing up the screen: two shoulder plates with pale rims,
    two red eyes glowing in the crease under them, broad plates sweeping down to red-tipped wings, a
    notch between them."""
    g = w.grid(art.CHEVRON, 24)
    bands = ramp_bands("chevron", 3, [1, 3, 5, 7, 9, 0xb, 0xd], metallic=0.25, roughness=0.32)
    tan_light = pal("chevron_rim", 0x8a, metallic=0.3, roughness=0.3)
    eye = pal("chevron_eye", 0x74, metallic=0.1, roughness=0.15, glow=1.0)
    eye_hot = pal("chevron_eye_hot", 0x77, metallic=0.0, roughness=0.1, glow=1.5)
    tip = pal("chevron_tip", 0x75, metallic=0.1, roughness=0.2, glow=1.0)
    paint = painter(g, lambda v: v >> 4 == 3, bands, lift=0.8)

    rows = w.regions(g, lambda v, c, row: "b")

    # The plates: a ridge down the middle, the shoulders and the wings' plates as soft bulges.
    def shape(x, y, z):
        ax = abs(x)
        ridge = 1.6 * math.exp(-(ax / 2.2) ** 2) * r.smoothstep(-8.0, 6.0, y)
        shoulder = 1.4 * math.exp(-(((ax - 4.2) / 2.4) ** 2 + ((y - 3.0) / 2.2) ** 2))
        wing = 1.1 * math.exp(-(((ax - 6.5) / 3.4) ** 2 + ((y + 4.5) / 2.6) ** 2))
        crease = -0.9 * math.exp(-((y - 0.2) / 0.6) ** 2) * r.smoothstep(1.0, 3.0, ax)
        return z + ridge + shoulder + wing + crease
    body = r.inflated("body", rows, "b", bands[3][1], sh.round_profile(0.55, max_height=4.6, min_height=1.2),
                      grow=0.1, z_fn=shape, spacing=0.5, bottom=0.35)
    w.paint_faces(body, paint)
    # The light rims along the shoulders' upper edges (row 8, ramp 8: pale cyan in the levels' palette).
    for sgn in (-1, 1):
        rim = [(sgn * 6.0, py(9.3), 0.0), (sgn * 3.9, py(8.4), 0.0), (sgn * 1.4, py(7.6), 0.0)]
        rim = [(x, y, sh.surface_z(body, x, y, 3.0) + 0.1) for x, y, _ in rim]
        w.tube(f"rim{sgn}", w.catmull(rim, 0.5), 0.55, tan_light, 8, squash=0.7)
    # The eyes slanting in the crease and the wings' red tips.
    for sgn in (-1, 1):
        x = sgn * 3.0
        e = w.sphere(f"eye{sgn}", (0, 0, 0), (0.95, 1.8, 0.8), eye, 14, 7)
        e.data.transform(Matrix.Translation((x, py(15.0), sh.surface_z(body, x, py(15.0), 3.0) - 0.1)) @
                         Matrix.Rotation(math.radians(30 * sgn), 4, "Z"))
        e2 = w.sphere(f"eye_hot{sgn}", (0, 0, 0), (0.45, 0.9, 0.4), eye_hot, 10, 5)
        e2.data.transform(Matrix.Translation((x, py(15.0), sh.surface_z(body, x, py(15.0), 3.0) + 0.45)) @
                          Matrix.Rotation(math.radians(30 * sgn), 4, "Z"))
        w.lathe_axis(f"tip{sgn}", [(0.0, 1.1), (0.8, 1.0), (1.6, 0.6), (2.0, 0.01)], tip,
                     (sgn * 10.2, py(24.6), 1.3), (sgn * 0.6, -0.8, -0.1), 12)
    r.budget(4800, floor=600)


# --- G 121: the violet pincer ---------------------------------------------------------------------------

@r.model("violet_pincer", [(121, True)])
def violet_pincer():
    """A glossy violet ball of a head; from its lower sides two arms of jointed segments hang in an arch,
    each ending in a golden fang that curves in."""
    skin = pal("pincer_skin", 0x57, metallic=0.3, roughness=0.3)
    skin_light = pal("pincer_skin_light", 0x58, metallic=0.3, roughness=0.28)
    joint = pal("pincer_joint", 0x54, metallic=0.2, roughness=0.4)
    head = pal("pincer_head", 0x56, metallic=0.35, roughness=0.2)
    head_hot = pal("pincer_head_hot", 0x5e, metallic=0.1, roughness=0.15, glow=0.4)
    gold = pal("pincer_gold", 0x1b, metallic=0.6, roughness=0.25)
    axis = 0.5

    def pod(name, centre, radii, angle, mat, segments=20):
        """An ellipsoid turned by angle (degrees) about Z at centre."""
        obj = w.sphere(name, (0, 0, 0), radii, mat, segments, segments // 2)
        obj.data.transform(Matrix.Translation(centre) @ Matrix.Rotation(math.radians(angle), 4, "Z"))
        return obj

    # The head, its highlight glowing a little.
    hx, hy = axis, py(4.4)
    w.sphere("head", (hx, hy, 7.2), (5.6, 5.0, 4.9), head, 26, 13)
    w.sphere("head_hot", (hx - 1.3, hy + 1.1, 10.9), (2.0, 1.7, 1.2), head_hot, 14, 7)
    # The arms: an upper and a lower segment down each side, joints between, the fangs at their ends.
    for s_ in (-1, 1):
        def X(dx):
            return axis + s_ * dx
        pod(f"upper{s_}", (X(5.0), py(11.6), 5.4), (3.3, 4.2, 2.8), s_ * 40, skin_light)
        w.sphere(f"elbow{s_}", (X(7.0), py(14.6), 4.4), (1.9, 1.6, 1.7), joint, 14, 7)
        pod(f"lower{s_}", (X(7.8), py(17.2), 4.0), (3.8, 3.7, 2.9), s_ * 10, skin)
        w.sphere(f"wrist{s_}", (X(7.8), py(19.8), 3.2), (2.2, 1.6, 1.8), joint, 14, 7)
        # The fang: down from the wrist, curving in to its point.
        path = [(X(8.2), py(19.8), 3.2), (X(8.5), py(22.0), 2.6), (X(7.6), py(24.2), 1.8), (X(5.4), py(25.6), 1.2),
                (X(3.6), py(26.0), 1.0)]
        pts = w.catmull(path, 0.45)
        w.tube(f"fang{s_}", pts, [2.2 * (1.0 - i / (len(pts) - 1)) ** 0.8 + 0.15 for i in range(len(pts))], gold, 12)
    r.budget(4800, floor=600)

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
