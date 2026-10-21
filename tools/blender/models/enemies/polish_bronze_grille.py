"""SOH JIN's bronze grille (sheet A sprite 89, 2x2: 24 x 28 pixels; enemy 842 of episode 1, on the ground, 26 of
them; one frame, not animated), polished (2026-10-21; it replaces wave3_q_bronze.py's bronze_grille(), a heightfield
of the sprite's pixels painted in its shades with three red pills laid in its slots). models.cfg: model bronze_grille
enemies/bronze_grille.glb origin, sprite a 89 bronze_grille yaw=0 height=-4 glow=14:0.18:118 (see below). No other
enemy shows A 89, and it is no other sprite's pixels mirrored, turned or in other ramps.

As the sprite and its 4x upscale draw it: a bronze plate lying on the ground, an octagon taller than it is wide
(columns 3-20 of rows 2-24): a short top and bottom (rows 2 and 24), its sides falling at 45 degrees to two upright
sides (columns 3-4 and 19-20) that lean a pixel to the right as they go down, a dark outline (shade 1) and a narrow
rim (shade 6, darker, shades 2-3, along the lower right). Most of it is three slots side by side, slanting up to the
right at about 47 degrees: the top left one (rows 5-12), the middle one, the longest and widest (rows 8-19), and the
lower right one, the narrowest (rows 14-20); in each a red bar glows (ramp 7: 2-4 at its edges and ends, 6-9 along
its middle, b, almost yellow, in the middle of the middle bar). Each slot has its own raised lip (shades 9-13, lit
along its upper left, where the sun falls on it), and where two lips meet between the slots a dark crease (shades
3-4) runs along them.

Built as a CAD modeller would (polish_machine_kit): the plate a prism of the octagon, bevelled round its top edge
into a darker rim, standing 2 pixels proud of the ground; the slots cut into it down to a floor; their lips swept
round each slot (a stadium: the slot's straight sides and round ends) as rounded rims, side by side, so that where
two meet their round crests leave a V-shaped crease between them; in each slot a red bar, a rounded capsule lying on
the slot's dark red floor, cut into bands of heat (polish_orb_red.band_split, smooth contours) hottest along its
middle and coolest at its ends, each band glowing in its own colour, well under 1 (the game's bloom and the cfg's
glow halo add to them). The slots' places, angles, lengths and widths are fitted to the sprite's red pixels. Bronze
in the shades of the SOH JIN bronze family (polish_disc_turret.py, polish_bronze_whorl.py): ramp 1, metallic.

Where it stands: drawn at its origin (origin), its z = 0 is the ground enemies' layer, 4 pixels above the terrain;
height=-4 lays it on the ground (its foot reaches 0.6 below z = 0, so that it doesn't float where the ground under
it is not quite level). Without origin the game would centre the thin plate on the layer's height and it would
hover 2.5 pixels over the ground. The glow halo is the bars' red (palette 118), faint.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground (z = 0); origin
at the sprite's centre (pixel 12, 14): column c is x = c + 0.5 - 12, row r is y = 13.5 - r.

Replaces wave3_q_bronze.py (delete it: bronze_grille() was all it still built; nothing imports it or its bronze()
and segment_distance()) and wave3_q_art.py's HEX (only bronze_grille() read it); the "wave3_q_bronze.py" mentions in
wave3_q.py's and wave3_q_kit.py's docstrings and models.cfg's batch Q comment then point here.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against
enemy_A.png: all of the sprite's pixels are the plate's), --preview <prefix>.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_orb_red import band_split  # noqa: E402

NAME, SPRITE = "bronze_grille", 89

# The plate's plan: the octagon through the middles of the outline's stairs (its top and bottom rows 2 and 24, the
# 45-degree sides, the upright sides at columns 3-4 and 19-20 leaning to the right going down).
PLAN = [(-1.6, 12.0), (-9.0, 4.6), (-8.0, -6.5), (-3.5, -11.0), (1.6, -11.0), (9.0, -3.6), (8.2, 5.4), (1.6, 12.0)]
FOOT = -0.6          # the plate's underside, below the ground
TOP = 2.1            # the plate's top
RIM = 1.15           # the bevel rounding its top edge into the rim
FLOOR = 0.75         # the slots' floor

# The slots, fitted to the sprite's red pixels: centre (x, y), angle (degrees from +x), half-length of the straight
# part, radius (half the width) of the red; the hottest band each bar reaches.
SLOTS = [((-2.80, 5.52), 45.0, 3.24, 1.42, 3), ((-0.45, 0.52), 48.8, 5.06, 1.73, 4),
         ((2.12, -3.82), 46.4, 3.27, 1.11, 3)]
LIP_W = 1.0          # the lips' width (the frames round the slots: they meet between the slots)
LIP_TOP = 2.85       # the lips' crests
LIP_ROUND = 0.5      # how far the crest's rounding reaches down
BAR_GAP = 0.04       # between a bar's edge (the red's) and its lip
BAR_TOP = 2.05       # the bars' tops

# The bars' heat bands: (lowest heat, palette index, emission); the hottest (b) only in the middle bar.
HEAT = [(-99.0, 0x73, 0.16), (0.30, 0x75, 0.24), (0.52, 0x77, 0.33), (0.72, 0x79, 0.43), (0.9, 0x7b, 0.52)]


def materials():
    pal = k.level_palette()
    m = {
        "top": k.material("grille_top", palette=0x18, metallic=0.5, roughness=0.32),
        "rim": k.material("grille_rim", palette=0x16, metallic=0.45, roughness=0.36),
        "side": k.material("grille_side", palette=0x12, metallic=0.3, roughness=0.55),
        "lip": k.material("grille_lip", palette=0x1b, metallic=0.55, roughness=0.24),
        "wall": k.material("grille_wall", palette=0x13, metallic=0.35, roughness=0.45),
        "floor": k.material("grille_floor", palette=0x71, metallic=0.1, roughness=0.5, emission=pal[0x72],
                            emission_strength=0.14),
    }
    for _, index, glow in HEAT:
        m[("heat", index)] = k.material("grille_bar_%x" % index, palette=index, metallic=0.0, roughness=0.18,
                                        emission=pal[index], emission_strength=glow)
    return m


# --- Stadiums ----------------------------------------------------------------------------------------------------

def stadium(slot, r, ends=14, sides=1):
    """Points round a slot's stadium at radius r from its axis, counter-clockwise, and the outward normals there: each
    straight side in `sides` segments, each round end in `ends`."""
    (cx, cy), angle, hl, _, _ = slot
    a = math.radians(angle)
    u, n = Vector((math.cos(a), math.sin(a))), Vector((math.sin(a), -math.cos(a)))   # n: right of u
    c = Vector((cx, cy))
    out = []
    for i in range(sides):                       # the right side, from the bottom end up
        out.append((c + n * r + u * (-hl + 2 * hl * i / sides), n))
    for i in range(ends):                        # round the top end
        t = math.pi * i / ends
        nrm = n * math.cos(t) + u * math.sin(t)
        out.append((c + u * hl + nrm * r, nrm))
    for i in range(sides):                       # the left side, from the top end down
        out.append((c - n * r + u * (hl - 2 * hl * i / sides), -n))
    for i in range(ends):                        # round the bottom end
        t = math.pi * i / ends
        nrm = -n * math.cos(t) - u * math.sin(t)
        out.append((c - u * hl + nrm * r, nrm))
    return out


def axis_distance(slot, x, y):
    """How far (x, y) is from a slot's axis segment, and where along it (-1 to 1 over the straight part)."""
    (cx, cy), angle, hl, _, _ = slot
    a = math.radians(angle)
    dx, dy = x - cx, y - cy
    t = dx * math.cos(a) + dy * math.sin(a)
    tc = max(-hl, min(hl, t))
    return math.hypot(dx - tc * math.cos(a), dy - tc * math.sin(a)), t / max(hl, 1e-6)


# --- Parts -------------------------------------------------------------------------------------------------------

def plate(m):
    """The octagon, bevelled round its top into the rim, the slots cut down to their floor."""
    body = mk.prism("plate", PLAN, FOOT, TOP, m["top"])
    mk.bevel(body, RIM, 4, 30)
    cutters = []
    for i, slot in enumerate(SLOTS):
        r = slot[3] + BAR_GAP + 0.06   # a little wider than the lip's inner wall, which hides the cut's wall
        cutters.append(mk.prism("slot_cut%d" % i, [(p.x, p.y) for p, _ in stadium(slot, r, 12)], FLOOR, TOP + 1.0,
                                m["wall"]))
    mk.boolean(body, cutters, "DIFFERENCE")
    mk.cleanup(body)

    def pick(c, n):
        if n.z < -0.5:
            return m["side"]
        if c.z < FLOOR + 0.02 and n.z > 0.9:
            return m["floor"]
        if any(axis_distance(s, c.x, c.y)[0] < s[3] + BAR_GAP + 0.2 for s in SLOTS) and n.z < 0.9:
            return m["wall"]
        if n.z > 0.97:
            return m["top"]
        return m["rim"] if n.z > 0.25 else m["side"]
    mk.paint(body, pick)
    return mk.shade(body, 35)


def lip(m, i, slot):
    """A slot's lip: a rounded rim swept round its stadium, its inner wall down to the slot's floor, its outer wall
    down into the plate."""
    r_mid = slot[3] + BAR_GAP + LIP_W / 2
    hw = LIP_W / 2
    profile = [(-hw, FLOOR - 0.05)]
    steps = 6
    for j in range(steps + 1):
        a = math.pi * j / steps
        profile.append((-hw * math.cos(a), LIP_TOP - LIP_ROUND + LIP_ROUND * math.sin(a) ** 0.8))
    profile += [(hw, TOP - 0.6), (0.0, FLOOR - 0.05)]
    path = stadium(slot, r_mid, 14, 1)
    rings = [[Vector((p.x + nrm.x * d, p.y + nrm.y * d, z)) for d, z in profile] for p, nrm in path]
    count, width = len(rings), len(profile)
    verts = [v for ring in rings for v in ring]
    faces = []
    for a in range(count):
        b = (a + 1) % count
        for j in range(width):
            jj = (j + 1) % width
            faces.append((a * width + j, b * width + j, b * width + jj, a * width + jj))
    obj = k.mesh_object("lip%d" % i, verts, faces, m["lip"])
    k.recalc_normals(obj)

    def pick(c, n):
        d, _ = axis_distance(slot, c.x, c.y)
        if d < r_mid - 0.05 and c.z < LIP_TOP - LIP_ROUND - 0.1:
            return m["wall"]
        return None
    mk.paint(obj, pick)
    return k.smooth(obj, 50)


def bar(m, i, slot):
    """The slot's red bar: a capsule lying on the floor, round across and at its ends, in bands of heat."""
    radius = slot[3]
    hottest = slot[4]
    rings, steps = [], 7
    sides = max(4, round(2 * slot[2] / 0.55))
    for j in range(1, steps + 1):
        s = math.sin((math.pi / 2) * j / steps)          # from the axis out to the bar's edge
        z = FLOOR + (BAR_TOP - FLOOR) * math.cos((math.pi / 2) * j / steps) ** 0.75
        rings.append([Vector((p.x, p.y, z)) for p, _ in stadium(slot, max(0.04, radius * s), 12, sides)])
    rings.append([Vector((p.x, p.y, FLOOR - 0.02)) for p, _ in stadium(slot, radius, 12, sides)])
    obj = k.loft("bar%d" % i, rings, m[("heat", HEAT[0][1])], cap_start=True, cap_end=True)
    k.recalc_normals(obj)

    def heat(v):
        d, t = axis_distance(slot, v.x, v.y)
        return 1.0 - 0.8 * (d / radius) ** 1.5 - 0.4 * min(1.0, abs(t)) ** 2 - (0.0 if hottest >= 4 else 0.06)
    bands = [(lo, m[("heat", index)]) for lo, index, _ in HEAT[:hottest + 1]]
    band_split(obj, [heat(v.co) for v in obj.data.vertices], bands)
    return k.smooth(obj, 60)


def build_grille():
    m = materials()
    plate(m)
    for i, slot in enumerate(SLOTS):
        lip(m, i, slot)
        bar(m, i, slot)
    parts = mk.meshes()
    for obj in parts:
        mk.apply(obj)
    triangulate(parts)
    bpy.context.view_layer.update()
    return parts


def build():
    options = k.args()
    out = mk.outdir(options)
    k.reset()
    parts = build_grille()
    if "check" in options:
        sheets = options["check"]
        sheet = os.path.join(sheets, "enemy_A.png") if os.path.isdir(sheets) else sheets
        mk.compare("%s (A %d)" % (NAME, SPRITE), mk.coverage(parts, 24, 28), k.sprite_mask(sheet, SPRITE))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mk.report(NAME, parts, os.path.join(out, NAME + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + NAME, parts)


if __name__ == "__main__":
    build()
