"""FLEET's lamp gun (sheet K sprite 278, 2x2: enemy 706 of episode 3, FLEET, sky and top layers; one frame, not animated)
and CAMANIS' two white sparks (K 124 and K 125, 1x1: enemies 1002 and 1001 of episode 3, CAMANIS' random enemies,
falling at 2 and 3 pixels a tick, armour 0), polished (2026-10-22, round 36; they replace wave3_o_machines.py's
k_lampgun() and wave3_o.py's spark_dot() and spark_glint()). models.cfg: model k_lampgun enemies/k_lampgun.glb,
sprite k 278 k_lampgun yaw=0 glow=12:0.22:125:0.5:-7.5 (the lamp); model spark_dot enemies/spark_dot.glb, model
spark_glint enemies/spark_glint.glb, sprite k 124 spark_dot yaw=0 glow=10:0.35, sprite k 125 spark_glint yaw=0
glow=10:0.35 (as before).

THE LAMP GUN: the sprite is two others' pixels put together (as K 281, the turret, is): its rows 0-13 are the
pincer machine's crossbar (the whole's rows 28-41 of K 153 above K 191, its lamp lit as in frame 193) upside down,
its outline drawn dark red (0x70) instead of black: the lamp in its housing, the knuckles, two short legs pointing up
the screen (columns 1-3 and 21-23 of rows 0-10), the stubs of the machine's arms and neck where it meets the block
(row 13); its rows 14-27 are FLEET's claw block's block (K 283's rows 0-13, polish_k_clawblock.py) upside down, but
for its middle and its flanges: a salmon bracket where the claw block has its window (columns 9-15 of rows 15-26: a
bar across at rows 16-17, two bars down from it to the roof's tip, a grey spine between them, dark red gaps), tan
window frames where it has its flanges (columns 2-4 and 19-21 of rows 15-18 and 20-23, grey panes), the two small
dark blue lamps by the roof (columns 4 and 19 of row 24). Enemy 706's launch type is 710 (K 171, FLEET's small
fireball, polish_fleet_fireball.py), its launch frequency 0 until FLEET's event 31 gives it one: from the clock 1672
on it lets fall strings of them.
Built from its families' parts: polish_pincer_boss.crossbar() (its 193 lamp, the legs ending at the sprite's top
edge, no knee rings) mirrored up the screen (y -> 14 - y); polish_k_clawblock's roof and its block's prism (here
without the window: polish_k_clawblock.block() cuts one) mirrored across y = 0; the bracket and the window frames
bevelled prisms on its top. Its underside at z -0.6 (the game centres sky and top enemies in height).

THE SPARKS (K 124, K 125): a white bead (columns 4-7 of rows 5-8: white-hot in its middle, light grey round it) and a
four-pointed glint (columns 4-8 of rows 4-8: a white core, short points up, down and to the sides, pale grey round
them): a glowing ball, lit a little lighter towards the sun; a glowing core with four tapering points (lofted diamonds)
on a pale glowing bead (the sprite's dim octagon round them). Their sprites are 1x1 (12 x 14), the origin their middle (pixel edge 6, 7).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up; the lamp gun's origin its sprite's
centre (pixel 12, 14): column c's left edge x = c - 12, row r's top edge y = 14 - r.

Replaces wave3_o_machines.py's k_lampgun() and wave3_o.py (the sparks: all it built), with polish_pincer_boss.py
replacing the rest of wave3_o_machines.py: delete wave3_o.py, wave3_o_machines.py and wave3_o_art.py (read only by
them), and take wave3_o_kit.py's "import wave3_o_art as art" and its build helpers (K, model, whole, run, char_rows,
at) out (wave3_q_kit and wave3_u_kit use only its cutting, mirroring, joining and budget helpers).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes against
enemy_K.png), --preview <prefix>, --only <model,...>.
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
import polish_k_clawblock as clawblock  # noqa: E402
import polish_k_pod as kp  # noqa: E402
from polish_k_pod import triangulate, mirror_y  # noqa: E402
import polish_pincer_boss as pb  # noqa: E402

# --- The lamp gun ---------------------------------------------------------------------------------------------------
FOOT_Y = 0.6                      # the legs end here in the machine's frame (the sprite's top edge once turned)
# The salmon bracket (K 278's frame): the bar across (x0, x1, y0, y1), the two bars down (x ranges) to y, the grey
# spine between them; how proud of the block's top.
BRACKET_BAR = (-2.0, 3.0, -4.0, -1.9)
BRACKET_LEGS = [(-2.0, -1.0), (2.0, 3.0)]
BRACKET_Y = (-13.2, -1.9)
SPINE = (0.05, 0.95, -13.0, -4.2)
BRACKET_UP = 0.45
# The tan window frames (the left ones; mirrored): x0, x1, y0, y1; their panes inset.
WINDOWS = [(-10.0, -7.0, -5.0, -1.0), (-10.0, -7.0, -10.0, -6.0)]
PANE_IN = 0.8
LAMPS = [(-7.5, -10.35), (7.5, -10.35)]   # the dark blue lamps by the roof (columns 4 and 19 of row 24)


def lampgun_materials():
    m = pb.materials()
    m["hi"], m["slot"] = m["light"], m["dark"]           # (at most 15 materials: the crossbar's shades merged)

    def mat(name, index, metallic=0.5, roughness=0.34):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)
    m.update({
        "slot_floor": mat("kpin_slot_floor", 0x06), "lamp": mat("kpin_bluelamp", 0x31, 0.2, 0.15),
        "tan": mat("kpin_tan", 0x1b, 0.45, 0.34), "tan_light": mat("kpin_tan_light", 0x1d, 0.45, 0.3),
        "salmon": mat("kpin_salmon", 0x46, 0.35, 0.32),
        "salmon_light": mat("kpin_salmon_light", 0x4a, 0.35, 0.3),
    })
    return m


def block(m):
    """polish_k_clawblock's block without its window, its roof, the blue lamps; turned across y = 0 (K 278's rows
    14-27)."""
    x0, x1, y0, y1, r, top, bev = clawblock.BLOCK
    body = mk.prism("lg_block", clawblock.rect(x0, x1, y0, y1, r, 64), 0.0, top, m["grey"])
    mk.bevel(body, bev, 3, 30)
    mk.shade(body, 35)
    mk.paint(body, lambda c, n: m["light"] if (0.3 < n.z < 0.8 and n.y > 0.3) else m["side"] if n.z < 0.3 else None)
    before = set(mk.meshes())
    clawblock.roof(m)
    roof = [o for o in mk.meshes() if o not in before]
    parts = [body] + roof
    for i, (x, y) in enumerate(LAMPS):
        lamp = mk.dome(f"lg_bluelamp{i}", (x, -y), (0.6, 0.45, 0.35), top - 0.1, m["lamp"], 16, 4)  # (turned below)
        k.smooth(lamp, 60)
        parts.append(lamp)
    for obj in parts:
        mk.apply(obj)
    mirror_y(parts)
    return parts


def bracket(m):
    """The salmon bracket on the block's top: a bar across, two bars down to the roof's tip, the grey spine between."""
    top = clawblock.BLOCK[5]
    parts = []
    x0, x1, y0, y1 = BRACKET_BAR
    bar = mk.box("lg_bracket_bar", x0, x1, y0, y1, top - 0.5, top + BRACKET_UP, m["salmon"])
    parts.append(bar)
    def strip(a, b, y0, y1):
        """A plan from y0 up to y1 with corners where the roof's facet begins (so the top follows it)."""
        ya = -clawblock.ROOF[0][1]
        ys = [y0] + [y for y in (ya - 0.05, ya + 0.05) if y0 < y < y1] + [y1]
        return [(a, y) for y in ys] + [(b, y) for y in reversed(ys)]
    for i, (a, b) in enumerate(BRACKET_LEGS):
        leg = mk.wedge(f"lg_bracket_leg{i}", list(reversed(strip(a, b, BRACKET_Y[0], BRACKET_Y[1]))), 0.0,
                       lambda x, y: roof_top(y) + BRACKET_UP, m["salmon"], bottom=lambda x, y: roof_top(y) - 0.6)
        parts.append(leg)
    a, b, c0, c1 = SPINE
    spine = mk.wedge("lg_spine", list(reversed(strip(a, b, c0, c1))), 0.0, lambda x, y: roof_top(y) + 0.2,
                     m["light"], bottom=lambda x, y: roof_top(y) - 0.6)
    parts.append(spine)
    for obj in parts:
        mk.bevel(obj, 0.22, 2, 30)
        mk.shade(obj, 35)
    for obj in parts[:3]:
        mk.paint(obj, lambda c, n: m["salmon_light"] if (n.z > 0.8 and c.y > -4.5) else None)
    return parts


def roof_top(y):
    """The block's top along the bracket (K 278's frame): flat over the block, then down the roof's back facet."""
    z0, z1 = clawblock.ROOF_Z
    top = clawblock.BLOCK[5]
    ya, yb = -clawblock.ROOF[0][1], -clawblock.ROOF[2][1]       # the roof's front (y -10) and back (y -13.75)
    if y >= ya:
        return top
    return z0 + (z1 - z0) * (y - ya) / (yb - ya)


def windows(m):
    """The tan window frames where the claw block has its flanges: bevelled frames, grey panes."""
    top = clawblock.BLOCK[5]
    parts = []
    for sign in (1, -1):
        for i, (x0, x1, y0, y1) in enumerate(WINDOWS):
            xa, xb = sorted((x0 if sign < 0 else -x1, x1 if sign < 0 else -x0))   # (the block's axis is x = 0)
            frame = mk.box(f"lg_window{sign}{i}", xa, xb, y0, y1, top - 0.5, top + 0.5, m["tan"])
            mk.bevel(frame, 0.25, 2, 30)
            mk.shade(frame, 35)
            mk.paint(frame, lambda c, n: m["tan_light"] if n.z > 0.8 else None)
            pane = mk.box(f"lg_pane{sign}{i}", xa + PANE_IN, xb - PANE_IN, y0 + PANE_IN, y1 - PANE_IN, top,
                          top + 0.6, m["grey"])
            parts += [frame, pane]
    return parts


def lampgun(m):
    bar = pb.crossbar(m, lit=True, prefix="lg_bar", foot_y=FOOT_Y, knee=False)
    mirror_y(bar)
    mk.transform(bar, Matrix.Translation((0.0, 14.0, 0.0)))
    parts = bar + block(m) + bracket(m) + windows(m)
    for obj in parts:
        mk.apply(obj)
    return parts


# --- The sparks -----------------------------------------------------------------------------------------------------
DOT = ((0.0, 0.0, 1.6), 1.75)                    # the bead: centre, radius
GLINT = ((0.5, 0.5, 1.6), 1.15, 2.75, 1.0)        # the glint: centre, core radius, the points' length, half-width


def spark_materials():
    glow = k.level_palette()

    def lit(name, index, strength, alpha=None):
        extra = {} if alpha is None else {"alpha": alpha}
        return k.material(name, palette=index, metallic=0.0, roughness=0.25, emission=glow[index],
                          emission_strength=strength, **extra)
    return {"white": lit("spark_white", 0x0f, 0.62), "pale": lit("spark_pale", 0x0b, 0.45),
            "grey": lit("spark_grey", 0x08, 0.32), "ray": lit("spark_ray", 0x0d, 0.55), "rim": lit("spark_rim", 0x09, 0.4)}


def spark_dot(m):
    (cx, cy, cz), r = DOT
    ball = k.ellipsoid("spark_dot", (cx, cy, cz), (r, r, r), m["pale"], 24, 12)
    from polish_orb_red import band_split
    band_split(ball, [Vector((v.co.x - cx, v.co.y - cy, v.co.z - cz)).normalized().dot(Vector((-0.35, 0.35, 1.0))
                                                                                       .normalized())
                      for v in ball.data.vertices], [(-9.0, m["grey"]), (0.15, m["pale"]), (0.6, m["white"])])
    k.smooth(ball, 80)
    return [ball]


def spark_glint(m):
    (cx, cy, cz), r, length, hw = GLINT
    core = k.ellipsoid("glint_core", (cx, cy, cz + 0.35), (r, r, r), m["white"], 20, 10)
    k.smooth(core, 80)
    # the pale bead the sprite's dim rim draws round the star (its 5 x 5 octagon)
    bead = k.ellipsoid("glint_bead", (cx, cy, cz - 0.25), (2.4, 2.4, 0.9), m["rim"], 24, 10)
    k.smooth(bead, 80)
    parts = [core, bead]
    for i, (dx, dy) in enumerate(((1, 0), (0, 1), (-1, 0), (0, -1))):
        # a thin diamond-sectioned point from inside the core out to its tip
        rings = []
        for t in (0.0, 0.35, 1.0):
            w = hw * (1.0 - t) + 0.02
            d = r * 0.3 + (length - r * 0.3) * t
            px, py = cx + dx * d, cy + dy * d
            ax, ay = -dy, dx
            pz = cz + 0.45 * (1.0 - t)
            rings.append([Vector((px + ax * w, py + ay * w, pz)), Vector((px, py, pz + w * 0.55)),
                          Vector((px - ax * w, py - ay * w, pz)), Vector((px, py, pz - w * 0.55))])
        point = k.loft(f"glint_point{i}", rings, m["ray"], end_point=(cx + dx * length * 1.05, cy + dy * length * 1.05,
                                                                       cz))
        k.smooth(point, 30)
        parts.append(point)
    return parts


# --- Main -----------------------------------------------------------------------------------------------------------
MODELS = [("k_lampgun", 278, True), ("spark_dot", 124, False), ("spark_glint", 125, False)]


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    sheet = None
    if "check" in options:
        sheets = options["check"]
        sheet = os.path.join(sheets, "enemy_K.png") if os.path.isdir(sheets) else sheets
    for name, sprite, large in MODELS:
        if only and name not in only:
            continue
        k.reset()
        if name == "k_lampgun":
            parts = lampgun(lampgun_materials())
        elif name == "spark_dot":
            parts = spark_dot(spark_materials())
        else:
            parts = spark_glint(spark_materials())
        triangulate(parts)
        bpy.context.view_layer.update()
        bpy.context.scene.view_settings.view_transform = "Standard"
        w, h = (24, 28) if large else (12, 14)
        if sheet:
            mk.compare("%s (K %d)" % (name, sprite), mk.coverage(parts, w, h), k.sprite_mask(sheet, sprite, large))
        obj = pb.fw.join(parts, name)
        obj.data.name = name
        mk.report(name, [obj], os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, [obj], size=(w, h), scale=16 if large else 24)


if __name__ == "__main__":
    build()
