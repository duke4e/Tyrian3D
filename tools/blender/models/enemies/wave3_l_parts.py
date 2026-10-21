"""The batch L objects that the game draws from several sprites of sheet 5 (wave3_l.py registers them): each
is built whole, in shared coordinates, from its pixel art (wave3_l_art.py) and cut along its sprites'
edges into the pieces, each moved to its sprite's centre (models.cfg: origin, so that they meet again).
The levels place the pieces as the sheet arranges them (checked in the level files' enemy events).
(The grey and red jet, redjet_left / redjet_right / redjet_nose, is built by polish_redjet.py; the long grey ship,
longship_left / longship_mid / longship_right, by polish_longship.py; HARVEST's ring ship, 5 39 41 / 43 45, by
polish_ringship.py.)

- fire_bowl_left, fire_bowl_right (156, 158): NOSE DRIP's bowl of flames.
- brain_* (196, 198, 200 / 233, 235, 237, 239 / 272, 274, 276): BRAINIAC's brain, 96 x 84 pixels.
"""
import math

import wave3_l_art as art
import wave3_l_kit as w
from wave3_l_kit import k, sh, pal


# --- NOSE DRIP's fire (the drip, 53 above 91, is polish_drip.py's) -----------------------------------


def drip_bands():
    return [(lowest, pal(f"drip_{index:x}", index, metallic=0.0, roughness=0.5, glow=glow))
            for lowest, index, glow in ((-9.0, 0x72, 0.35), (3.0, 0x74, 0.5), (5.0, 0x76, 0.7), (7.0, 0x78, 0.9),
                                        (9.0, 0x7a, 1.1), (11.0, 0x7c, 1.35))]


# --- NOSE DRIP's bowl of flames (156 and 158) -----------------------------------------------------

BOWL = w.Art(art.FIRE_BOWL, (24, 14))
BOWL_PIECES = {"fire_bowl_left": (-24, 0, -14, 14), "fire_bowl_right": (0, 24, -14, 14)}


def build_fire_bowl():
    """A bowl of fire, 48 pixels wide: a molten trough bulging where the sprite is bright, glowing
    white-yellow low in the bowl and dark red at the rim, with tongues of flame rising from the rim
    and leaning up the screen (the sprite's spikes)."""
    a = BOWL
    bands = drip_bands()
    shade = w.shade_field(a, blur=1, skip="k")
    polys = a.polys(smooth=2, epsilon=0.45)
    body = w.rounded("bowl", polys, bands[0][1], aspect=0.8, max_height=5.5, spacing=0.7,
                     z_fn=lambda x, y, z: z + 0.35 * (shade(x, y) - 6.0) * w.smoothstep(0.5, 2.0, z))
    w.simplify_flat(body)
    w.band_split(body, [shade(v.co.x, v.co.y) for v in body.data.vertices], bands, smooth_angle=55)
    # The tongues: tapered tubes rising from inside the rim and leaning up the screen to the spikes' tips.
    for i, (c, tip_r, base_r) in enumerate(((3.5, 0.0, 9.0), (9.2, 1.0, 9.5), (16.0, 4.0, 10.0), (21.5, 5.0, 10.5),
                                            (26.2, 5.0, 10.5), (32.5, 4.0, 10.0), (39.6, 1.0, 9.5), (45.0, 0.0, 9.0))):
        x = a.x(c)
        y0, y1 = a.y(base_r), a.y(tip_r)
        z0 = sh.surface_z(body, x, y0, 3.0) - 1.0
        pts = [(x + 0.4 * math.sin(3.0 * t + i), y0 + (y1 - y0) * t, z0 + 3.2 * math.sin(math.pi * t * 0.9))
               for t in [j / 10 for j in range(11)]]
        radii = [1.5 * (1 - t) ** 0.8 + 0.08 for t in [j / 10 for j in range(11)]]
        tongue = w.tube(f"tongue{i}", pts, 1.0, bands[0][1], 8, radii=radii)
        tongue.data.update()
        w.band_split(tongue, [8.0 - 5.5 * (v.co.y - y0) / max(y1 - y0, 1e-3) for v in tongue.data.vertices],
                     bands, smooth_angle=60)
    w.bake()
    sh.flat_bottom(w.meshes())


def bowl_piece(name):
    def build():
        build_fire_bowl()
        return w.cut_piece(*BOWL_PIECES[name])
    return build


# --- BRAINIAC's brain (196, 198, 200 / 233, 235, 237, 239 / 272, 274, 276) ----------------------------

BRAIN = w.Art(art.BRAIN, (48, 42))
BRAIN_PIECES = {
    "brain_top_l": (-36, -12, 14, 42), "brain_top_m": (-12, 12, 14, 42), "brain_top_r": (12, 36, 14, 42),
    "brain_mid_1": (-48, -24, -14, 14), "brain_mid_2": (-24, 0, -14, 14), "brain_mid_3": (0, 24, -14, 14),
    "brain_mid_4": (24, 48, -14, 14),
    "brain_bot_l": (-36, -12, -42, -14), "brain_bot_m": (-12, 12, -42, -14), "brain_bot_r": (12, 36, -42, -14),
}


def build_brain():
    """BRAINIAC's brain, 96 x 84 pixels in ten sprites: two hemispheres domed towards the camera with a
    deep fissure between them, folded into gyri and sulci as the sprite shades them, two blue glands
    under them and nerves hanging below in loops."""
    a = BRAIN
    shade = w.shade_field(a, blur=1, letters={"k": 0.0}, skip="b")
    flesh = [pal(f"brain2_{i:x}", 0x40 + i, metallic=0.15, roughness=0.35) for i in (3, 5, 7, 9, 11)]
    blue = pal("brain2_gland", 0x37, metallic=0.2, roughness=0.12, glow=0.35)
    blue_light = pal("brain2_gland_light", 0x3a, metallic=0.2, roughness=0.1, glow=0.5)
    # The hemispheres: the flesh above row 64.
    mass = a.polys(rows=a.select(lambda c, r, ch: r <= 63 and ch != "b"), smooth=2, epsilon=0.5, min_area=20.0)

    def mass_z(x, y, z):
        fissure = 4.0 * math.exp(-((x - 0.2) / 1.5) ** 2) * w.smoothstep(-24.0, -14.0, y)
        return z + (0.55 * (shade(x, y) - 6.0) - fissure) * w.smoothstep(1.0, 5.0, z)
    body = w.rounded("hemispheres", mass, flesh[2], aspect=0.5, max_height=15.0, spacing=0.6, z_fn=mass_z,
                     sigma=3.0)
    w.simplify_flat(body)
    w.band_split(body, [shade(v.co.x, v.co.y) if v.co.z > 1.5 else 4.0 for v in body.data.vertices],
                 [(-9.0, flesh[0]), (2.2, flesh[1]), (4.4, flesh[2]), (6.6, flesh[3]), (8.8, flesh[4])],
                 smooth_angle=55)
    # The nerves below (rows 64-83): thin strands inflated round from their pixels.
    nerves = a.polys(rows=a.select(lambda c, r, ch: r >= 60 and ch != "b"), smooth=1, epsilon=0.3, min_area=2.0)
    strands = w.rounded("nerves", nerves, flesh[2], aspect=0.9, max_height=3.0, bottom=0.6, base=1.4,
                        spacing=0.5)
    w.decimate(strands, 5000)
    w.band_split(strands, [shade(v.co.x, v.co.y) for v in strands.data.vertices],
                 [(-9.0, flesh[0]), (3.0, flesh[1]), (5.5, flesh[2]), (7.5, flesh[3])], smooth_angle=55)
    # The glands.
    glands = a.polys(rows=a.select(lambda c, r, ch: ch == "b"), smooth=2, epsilon=0.4, min_area=4.0)
    g = w.rounded("glands", glands, blue, aspect=0.9, max_height=4.5, bottom=0.3, base=2.5, spacing=0.5)
    w.decimate(g, 1000)
    w.paint(g, lambda c, n: 1 if n.z > 0.6 and n.x < 0.1 and n.y > -0.1 else 0, [blue, blue_light])
    w.bake()
    sh.flat_bottom(w.meshes())


def brain_piece(name):
    def build():
        build_brain()
        return w.cut_piece(*BRAIN_PIECES[name])
    return build


# --- Registry -----------------------------------------------------------------------------------

PIECES = []  # (name, sprite, builder)
for _name, _sprite in (("fire_bowl_left", 156), ("fire_bowl_right", 158)):
    PIECES.append((_name, _sprite, bowl_piece(_name)))
w.whole("fire_bowl", build_fire_bowl, (48, 28), BOWL.mask())
for _name, _sprite in (("brain_top_l", 196), ("brain_top_m", 198), ("brain_top_r", 200), ("brain_mid_1", 233),
                       ("brain_mid_2", 235), ("brain_mid_3", 237), ("brain_mid_4", 239), ("brain_bot_l", 272),
                       ("brain_bot_m", 274), ("brain_bot_r", 276)):
    PIECES.append((_name, _sprite, brain_piece(_name)))
w.whole("brain", build_brain, (96, 84), BRAIN.mask())
