"""BRAINIAC's eye hatch's wreck (sheet 5 sprite 164's stand-in: what BRAINIAC's floor paints where eye_hatch stands
once it is destroyed, before it comes and where none comes: its tile 154, the hatch blown open; 16 of them), built on
polish_eye_hatch.py (2026-10-25, the clean ground's stage 4).

As the map paints it at 4x (BRAINIAC 33fc79a5b8f29c38 at 684, 6147, tile 154): the floor's round pit blown open, its
raised rim torn into black jagged blades flung out over the floor round it (the longest down to the lower left, past
the pit's edge to row 24, others to the upper left, the upper right and out to the right, columns 2-21 of rows 4-24),
the rim's purple left only in broken arcs between them, dark; the socket inside still ribbed with its slats, black
between them; the eye still there, a dull red band across the middle (rows 11-14, columns 7-16), the bar from the top
still lying over it (grey, its rails lit), the slot's housing gone (black over the floor's groove there); the block
from the bottom broken, dark, its top edge lit.

The model: the live hatch (polish_eye_hatch's socket, slats, eye, bar and block, its materials; the eye in
164's reds a little dimmer, 0x70-0x75 glowing 0.12-0.32) broken: the rim lofted as the live one but torn down to the
socket's floor in five jagged sectors (rim_ring lowered there by a noisy tear), the rest of it scorched (its purples
three shades darker, burnt brown-black in patches); black blades (0x50, their torn edges a dim 0x53) bent out from
the tears over the floor, each tilted down from the rim's top to its tip on the floor; the bar snapped at the pit's
edge, knocked askew and sooted; the block broken off at a jagged line and sagging into the
socket, dark but for its top edge; the slot's housing blown away (dark chunks of it at the slot); a few dark chunks in
the socket. Every mesh triangulated (polish_k_pod.triangulate) and joined into one, as the live hatch.

The same frame as eye_hatch: origin at the sprite's centre (pixel 12, 14), +Y up the sprite, +Z up from the floor
(z = 0); origin flag as the live line. models.cfg: model eye_hatch_wreck enemies/eye_hatch_wreck.glb origin;
wreck 5 164 eye_hatch_wreck (drawn with sprite 5 164's options, yaw=0 height=-4).

Options after "--": --outdir <dir> (default assets/models/enemies), --preview <prefix>.
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
import polish_eye_hatch as live  # noqa: E402
import polish_panel_pills_wreck as wk  # noqa: E402
from polish_deli_boss import join  # noqa: E402
from polish_jaw_gun_wreck import ccw, jagged, rock, scorch  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402

NAME = "eye_hatch_wreck"
EYE = ((0x70, 0.12), (0x72, 0.24), (0x74, 0.3), (0x75, 0.32))   # the eye's rim, body, core, glint (dimmer than 164's)
FRAME = 164
# The rim's tears: (angle round the pit, degrees from +x; half width, degrees). Inside them the rim is torn down to
# the socket's floor (a little jagged).
TEARS = [(-16.0, 24.0), (58.0, 16.0), (132.0, 22.0), (205.0, 16.0), (246.0, 26.0)]
# The blades flung out from the tears over the floor: (angle, its base's half width (degrees), how far its tip reaches
# past the rim's foot, a bend of its tip aside (degrees)).
BLADES = [(-26.0, 12.0, 3.6, -14.0), (-4.0, 9.0, 2.6, 10.0), (58.0, 9.0, 3.0, 12.0), (124.0, 11.0, 4.4, 16.0),
          (146.0, 7.0, 2.2, 6.0), (206.0, 10.0, 3.0, -10.0), (238.0, 13.0, 6.4, -8.0), (264.0, 9.0, 2.8, 12.0)]
BLADE_THICK = 0.28
# The bar knocked askew (turned about z round its tip, degrees; lifted at its tip); the block broken at a jagged line
# across it (y), its lower part gone, sagging (degrees about x round its top edge).
BAR_TURN, BAR_LIFT, BAR_SNAP = 4.0, 0.25, 7.4
BLOCK_BREAK, BLOCK_SAG = -4.6, 11.0
# Dark chunks in the socket: (x, y, radius).
CHUNKS = [(-2.6, -2.8, 0.7), (3.0, -3.4, 0.6), (-3.8, 3.6, 0.55), (2.2, 4.2, 0.5), (-1.6, 10.2, 0.8),
          (1.4, 10.8, 0.7), (0.2, 9.4, 0.55)]


def angle_of(x, y):
    return math.degrees(math.atan2((y - live.PIT[1]) / live.OUTER[1], (x - live.PIT[0]) / live.OUTER[0]))


def tear(angle):
    """How far the rim is torn down at an angle (1: down to the socket's floor), jagged by noise."""
    t = 0.0
    for a, half in TEARS:
        off = abs((angle - a + 180.0) % 360.0 - 180.0)
        jag = half * (1.0 + 0.35 * wk.perlin(angle * 0.21 + a, 1.7, 0.4))
        t = max(t, 1.0 - live.smoothstep(jag * 0.55, jag, off))
    # (and crumpled a little all round)
    return max(t, 0.45 + 0.15 * wk.perlin(angle * 0.13, 4.2, 0.9))


def torn_ring(u, z):
    """live.rim_ring with the rim torn down in the tears (its top lowered to the socket's floor)."""
    ring = ORIGINAL_RING(u, z)
    out = []
    for p in ring:
        if p.z > live.FLOOR:
            t = tear(angle_of(p.x, p.y))
            p = Vector((p.x, p.y, live.FLOOR + (p.z - live.FLOOR) * (1.0 - 0.92 * t)))
        out.append(p)
    return out


ORIGINAL_RING = live.rim_ring


def burn(co):
    """The scorch: strongest at the tears, over the whole rim a little."""
    t = tear(angle_of(co.x, co.y))
    return 0.55 + 0.5 * t + 0.25 * wk.perlin(co.x * 0.6 + 3.0, co.y * 0.6 - 1.0, 0.2)


def block_burn(co):
    """The block burnt dark (its purples three shades darker) but along its top edge (lit, as painted)."""
    top = live.FRAMES[FRAME][2]
    return 0.1 if co.y > top - 0.9 else 0.6


def blade(name, angle, half, reach, bend, mats):
    """A torn blade of the rim bent out over the floor: its base along the rim's top across the tear, its tip on the
    floor past the rim's foot, a thin plate (its upper face, its underside and torn edges)."""
    cx, cy = live.PIT
    top_r = (live.OUTER[0] + live.INNER[0]) / 2

    def at(a, r, z):
        a = math.radians(a)
        return Vector((cx + r * math.cos(a) * live.OUTER[0] / live.OUTER[1], cy + r * math.sin(a), z))
    tip_a = angle + bend
    pts = [at(angle - half, top_r - 0.4, live.RIM_TOP * 0.75), at(angle - half * 0.35, top_r + 0.9, 1.0),
           at(tip_a, live.OUTER[1] + reach, 0.12), at(angle + half * 0.4, top_r + 1.1, 0.95),
           at(angle + half, top_r - 0.4, live.RIM_TOP * 0.75), at(angle, top_r - 1.2, live.RIM_TOP * 0.55)]
    # (the outline in plan roughened, its heights kept from the nearest of the points)
    plan = jagged([(p.x, p.y) for p in pts], 2.0 + angle * 0.03, 0.22, 0.6)

    def height(x, y):
        w = [(1.0 / max((Vector((x, y)) - p.xy).length, 0.05) ** 2, p.z) for p in pts]
        return sum(a * b for a, b in w) / sum(a for a, _ in w)
    n = len(plan)
    top = [Vector((x, y, height(x, y))) for x, y in plan]
    bottom = [p - Vector((0, 0, BLADE_THICK)) for p in top]
    centre = sum(top, Vector()) / n
    verts = top + bottom + [centre, centre - Vector((0, 0, BLADE_THICK))]
    faces = [(i, (i + 1) % n, 2 * n) for i in range(n)] + [(n + (i + 1) % n, n + i, 2 * n + 1) for i in range(n)]
    faces += [((i + 1) % n, i, n + i, n + (i + 1) % n) for i in range(n)]
    obj = k.mesh_object(name, [tuple(v) for v in verts], faces, mats[0])
    k.recalc_normals(obj)
    mk.paint(obj, lambda c, nrm: mats[0] if nrm.z > 0.5 else mats[2] if nrm.z > -0.5 else mats[1])
    return mk.shade(obj, 30)


def build_wreck():
    m = live.materials(EYE)
    m["blade"] = k.material("hatchwreck_blade", palette=0x50, metallic=0.0, roughness=0.85)
    m["blade_under"] = m["blade"]
    m["blade_edge"] = m["shadow"]
    # The rim torn down in the tears.
    live.rim_ring = torn_ring
    try:
        rim = live.rim(m)
    finally:
        live.rim_ring = ORIGINAL_RING
    parts = [rim, live.socket(m)]
    for i, spec in enumerate(live.SLATS):
        parts.append(live.slat(f"slat{i}", m, *spec))
    parts.append(live.eye(m))
    bar = live.bar(m, live.FRAMES[FRAME][1])
    house = []   # (the slot's housing blown away: chunks of it lie at the slot)
    block = live.block(m, live.FRAMES[FRAME][2])
    for obj in parts + bar + house + [block]:
        mk.apply(obj)
    # The bar knocked askew about its tip, its tip lifted.
    tip = Vector((0.0, live.FRAMES[FRAME][1], live.BAR_Z[0]))
    turn = (Matrix.Translation(tip) @ Matrix.Rotation(math.radians(BAR_TURN), 4, "Z") @
            Matrix.Rotation(math.radians(-4.0), 4, "X") @ Matrix.Translation(-tip))
    snapped = []
    for obj in bar:
        # (snapped where it ran into the housing, at the pit's edge)
        gone = wk.split_piece(obj, (0.0, BAR_SNAP, 0.0), (0.0, 1.0, 0.0), m["socket"], obj.name + "_gone")
        if gone is not None:
            bpy.data.objects.remove(gone)
        if not obj.data.polygons:
            bpy.data.objects.remove(obj)
            continue
        obj.data.transform(turn)
        obj.data.transform(Matrix.Translation((0.0, 0.0, BAR_LIFT * 0.5)))
        snapped.append(obj)
    bar = snapped
    # The block broken off at a jagged line, its lower part gone, sagging into the socket.
    x0, x1 = live.BLOCK_X
    line = jagged([(x0 - 1.0, BLOCK_BREAK - 0.4), (0.0, BLOCK_BREAK + 0.5), (x1 + 1.0, BLOCK_BREAK - 0.2),
                   (x1 + 1.0, live.BLOCK_FOOT - 2.0), (x0 - 1.0, live.BLOCK_FOOT - 2.0)], 6.0, 0.35, 0.5)
    mk.boolean(block, mk.prism("block_break", ccw(line), -2.0, 6.0, m["socket"]), "DIFFERENCE")
    mk.cleanup(block, dissolve=0.0)
    edge = Vector((0.0, live.FRAMES[FRAME][2], live.BLOCK_TOP))
    block.data.transform(Matrix.Translation(edge) @ Matrix.Rotation(math.radians(BLOCK_SAG), 4, "X") @
                         Matrix.Translation(-edge))
    mk.shade(block, 35)
    # Scorched: the rim (most at the tears), the slats, the bar and the block.
    slats = [o for o in parts if o.name.startswith("slat")]
    for obj in [rim] + slats + bar + [block]:
        scorch(obj, burn if obj is rim else block_burn if obj is block else
               (lambda co: 0.7 + 0.35 * wk.perlin(co.x * 0.7, co.y * 0.7, 1.3)), levels=(0.3, 0.88))
    k.smooth(rim, 60)
    # The blades flung out from the tears, the chunks in the socket.
    for i, (angle, half, reach, bend) in enumerate(BLADES):
        blade(f"blade{i}", angle, half, reach, bend, (m["blade"], m["blade_under"], m["blade_edge"]))
    for i, (x, y, r) in enumerate(CHUNKS):
        rock(f"chunk{i}", (x, y, live.FLOOR), (r, r * 0.85, r * 0.6), m["socket"], 4.0 + i)
    whole = mk.meshes()
    for obj in whole:
        mk.apply(obj)
    bpy.context.view_layer.update()
    triangulate(whole)
    obj = join(whole, NAME)
    obj.data.name = NAME
    return obj


def build():
    options = k.args()
    k.reset()
    obj = build_wreck()
    wk.drop_unused([obj])
    bpy.context.scene.view_settings.view_transform = "Standard"
    mk.report(NAME, [obj], os.path.join(mk.outdir(options), NAME + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + NAME, [obj])


if __name__ == "__main__":
    build()
