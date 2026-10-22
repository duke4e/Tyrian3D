"""ASTEROID?'s tan launcher (sheet P sprite 277 and its frames 275 273 271, 2x2: 24 x 28 pixels; enemy 197, armour 40)
and its wreck (P 235), polished (2026-10-22, round 37; it replaces wave3_w_launcher.py's tan_launcher(), a box with two
stubby barrels always drawn in, and wave3_ao_works.py's tan_launcher_wreck(), that model with its barrels shifted and
pixelated). models.cfg: model tan_launcher enemies/tan_launcher.glb origin (unchanged), model tan_launcher_wreck
(unchanged), new model tan_launcher_275 / _273 / _271 enemies/*.glb origin, frame p 275 tan_launcher_275, frame p 273
tan_launcher_273, frame p 271 tan_launcher_271; the sprite lines of P 277 and 235 get height=-4.

Where the level puts it (ASTEROID?'s events, tools/content/tyrevents.py; the enemy data, tools/content/tyrdata.py): twice,
t888 at x 114 and 162 (event 6, the ground; links 1 and 2), on the plain asteroid floor (tile 372, terrain flat 0): the
floor its sprites draw round it and under its barrels (columns 0-1 and 21-23, rows 22-27, the gap between the barrels)
is the map's, left out. In the data it does not animate (animate 0), but at t938 event 24 (ani 7, start 1, once) plays
277 275 275 273 273 271 271 and leaves it at 271, its barrels run out; from t948 it fires (event 31, freq 50). The
data's eighth frame (0) never shows. No other enemy shows P 277 275 273 271 or 235; so 275, 273 and 271 are frame
models. Shot, it turns into P 235 (dgr, dlevel -1: it stays), which draws the launcher with its barrels out (as 271),
scorched. Not in episode 6. No sprite of these is another's pixels mirrored or recoloured.

As the sprites and their 4x upscales draw it (columns and rows of the sprite): a tan housing (ramp 10, 0xa0-0xaf, lit at
its left and back) arched over the gap between its two legs (columns 3-8 and 14-19, rows 6-12), a raised frame along its
back and over its legs and a stem down its middle, dark blue panes beside the stem (0x62-0x66, rows 7-8); two blue-grey
lamps at its back edge (columns 6-9 and 14-17, rows 0-1, with pale highlights); red fins at its sides (columns 1-2 and
20-22, rows 4-11, 0x71-0x76). From under each leg a barrel runs out down the screen: a blue-grey breech, tan rings, a
blue-grey tube, a tan muzzle round a red bore (277: the bores at rows 18-20, the rings packed together); the frames run
the tubes out (the bores at rows 19-21, 22-23, 24-25), blue-grey showing between the rings. P 235: the same with the
barrels out, the housing sooted in patches, the panes and lamps dead, the bores dark.

Built for the game's camera where the world has it (one sprite: no pieces): the housing a block lofted from rounded
rectangles (polish_block_house.rrect) up to its rounded top (HOUSING), its top HOUSE_H high where the camera sees it at
rows 2-11, a dark arch under it between the legs; on its top the frame and the stem as bevelled bars, the panes sunk
dark glass with a glint; the lamps glassy domes in collars on its back edge; the fins red plates on its sides. Each
barrel turned along its axis (ELEVATION degrees up from straight down the screen, from its breech on the housing's front
at BREECH): the breech collar and the sleeve fixed, two tubes telescoping out of it (each stage a tan ring at its end)
and the muzzle a tan can with a rounded lip round the bore (glowing red 0.45, a darker ring inside); RUN_OUT gives each
frame's run along the axis (0, 1.3, 4.6, 7.3: where the camera sees the bores at rows 19, 20, 22.5 and 24.5). The wreck
is 271 sooted (a fixed pattern over the housing, split finer for it, and the barrels' parts; the stem, the right rail and
the back block burnt whole), its panes, lamps and bores dark. Painted in the sprites' tans and blue-greys by how the
game's sun reaches each face.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground (z 0); the origin is
the sprite's middle (column c's left edge x = c - 12; a point at height z is seen at y + z tan 20, row r's top edge at
14 - r). height=-4 sets it on the terrain (its walls reach SKIRT below it).

Replaces wave3_w_launcher.py (all of it) and wave3_ao_works.py's section "P 235: the tan launcher's wreck" (LAUNCHER,
LAUNCHER_DMG, tan_launcher_wreck()); see polish_block_parts.py for the rest of wave3_ao_works.py and the kits that go.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each model's outline as the
camera sees it against its sprite's own pixels), --preview <prefix>, --only <model,...>.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_asteroid_kit as ak  # noqa: E402
from polish_block_house import rrect  # noqa: E402

HOUSING = (-9.6, 8.0, 0.45, 9.6)       # the housing's plan (x0, x1, y0, y1)
HOUSE_R = (3.0, 3.0, 3.6, 3.6)         # its corners' radii (front left, front right, back right, back left)
HOUSE_H, HOUSE_EDGE = 7.0, 1.4         # its top and its rounded edge
SKIRT = -4.0
ARCH = (-3.2, 1.9, 4.4)                # the dark arch under it between the legs: x0, x1, its top
FRAME_Z = 0.75                         # how far the frame and the stem stand over the top
PANES = [(-5.5, -2.2), (1.2, 4.5)]     # the dark panes (x0, x1), between y 1.7 and 5.8
LAMPS = [(-4.4, 10.0), (3.6, 10.0)]    # the lamps on its back edge (x, y)
BARRELS = (-7.5, 5.5)                  # the barrels' axes (x): the bores at columns 3-5 and 16-18
BREECH = (0.55, 3.5)                   # the breech on the housing's front (y, z)
ELEVATION = 25.0                       # the barrels' axis: up from straight down the screen
RUN_OUT = {277: 0.0, 275: 1.3, 273: 4.6, 271: 7.3, 235: 7.3}
# The barrel along its axis (from the breech, retracted): (from, to, radius, part); the tubes run out in two stages.
SLEEVE = [(0.0, 1.2, 3.4, "collar"), (1.2, 3.0, 3.2, "sleeve")]
TUBE1 = (2.7, 3.1)                     # the first tube: its start (along the axis, retracted) and radius
RING1 = (4.0, 1.0, 3.45)               # its ring: start (retracted), length, radius
TUBE2 = (4.9, 2.9)
MUZZLE = (5.0, 4.65, 3.5)              # the muzzle: start (retracted), length, radius (its front at 9.65)
SOOT = 0.15                            # the wreck: how much of the housing is sooted (a share, by a fixed pattern)


def materials(wreck=False):
    def m(name, index, metallic=0.4, roughness=0.42, glow=0.0, glow_index=None):
        return ak.pal("launcher_" + name, index, metallic, roughness, glow, glow_index)
    out = {"tan": m("tan", 0xa8), "tan_lit": m("tan_lit", 0xab, 0.4, 0.38), "tan_dark": m("tan_dark", 0xa5),
           "blue": m("blue", 0x67, 0.5, 0.35), "blue_dark": m("blue_dark", 0x64, 0.5, 0.4),
           "glass": m("glass", 0x63, 0.4, 0.1), "red": m("red", 0x74, 0.3, 0.4), "red_lit": m("red_lit", 0x77, 0.3, 0.38),
           "dark": m("dark", 0x01, 0.1, 0.8), "inside": m("inside", 0xa3, 0.2, 0.7),
           "lamp": m("lamp", 0x69, 0.3, 0.15, 0.0 if wreck else 0.18, 0x6a)}
    if wreck:
        out.update({"glint": m("glint", 0x65, 0.4, 0.2), "bore": m("bore", 0x71, 0.1, 0.6),
                    "soot": m("soot", 0xa2, 0.1, 0.8), "char": m("char", 0x02, 0.05, 0.9)})
    else:
        out.update({"glint": m("glint", 0x6c, 0.2, 0.15, 0.25), "bore": m("bore", 0x74, 0.0, 0.5, 0.45, 0x76)})
    return out


# --- The housing -------------------------------------------------------------------------------------------------------

def housing(m):
    x0, x1, y0, y1 = HOUSING
    steps = 6
    rings = [rrect(x0, x1, y0, y1, HOUSE_R, SKIRT, steps), rrect(x0, x1, y0, y1, HOUSE_R, HOUSE_H - HOUSE_EDGE, steps)]
    for a in (30, 60, 90):
        t = math.radians(a)
        inset = HOUSE_EDGE * (1 - math.cos(t))
        rings.append(rrect(x0 + inset, x1 - inset, y0 + inset, y1 - inset, [max(r - inset, 0.05) for r in HOUSE_R],
                           HOUSE_H - HOUSE_EDGE + HOUSE_EDGE * math.sin(t), steps))
    body = k.loft("housing", rings, m["tan"], start_point=((x0 + x1) / 2, (y0 + y1) / 2, SKIRT),
                  end_point=((x0 + x1) / 2, (y0 + y1) / 2, HOUSE_H))

    def pick(c, n):
        if n.z > 0.95:
            return m["tan"]
        if n.z > 0.2:
            return m["tan_lit"] if (n.x < -0.3 or n.y > 0.3) else m["tan_dark"]
        if n.x < -0.5 or n.y > 0.5:
            return m["tan"]
        return m["tan_dark"]
    mk.paint(body, pick)
    mk.shade(body, 35)
    parts = [body]
    # The dark arch under it between the legs (a recess in its front).
    ax0, ax1, top = ARCH
    arch = []
    for i in range(9):
        a = math.pi * i / 8
        arch.append(((ax0 + ax1) / 2 + (ax1 - ax0) / 2 * math.cos(a), top - 1.6 + 1.6 * math.sin(a)))
    outline = [(ax1, 0.0)] + arch + [(ax0, 0.0)]
    recess = mk.prism("arch", [(x, z) for x, z in outline], y0 - 0.12, y0 + 0.6, m["dark"], axis="y")
    k.recalc_normals(recess)
    parts.append(recess)
    return parts


def bar(name, x0, x1, y0, y1, z0, z1, mat, m):
    obj = mk.box(name, x0, x1, y0, y1, z0, z1, mat)
    mk.bevel(obj, 0.28, 2, 35)
    mk.shade(obj, 35)
    mk.paint(obj, lambda c, n: m["tan_lit"] if n.z > 0.2 and (n.x < -0.3 or n.y > 0.3) else
             m["tan_dark"] if n.z < 0.9 else None)
    return obj


def top_parts(m):
    """The frame along the back and over the legs, the stem, the panes and the lamps."""
    x0, x1, y0, y1 = HOUSING
    z0, z1 = HOUSE_H - 0.3, HOUSE_H + FRAME_Z
    parts = [bar("frame_back", x0 + 1.3, x1 - 1.3, 6.4, y1 - 1.1, z0, z1, m["tan_lit"], m),
             bar("frame_l", x0 + 1.1, x0 + 3.9, y0 + 1.0, 7.0, z0, z1, m["tan"], m),
             bar("frame_r", x1 - 3.7, x1 - 1.1, y0 + 1.0, 7.0, z0, z1, m["tan"], m),
             bar("stem", -1.6, 0.6, y0 + 0.9, 6.8, z0, z1 + 0.1, m["tan_lit"], m)]
    parts.append(bar("back_block", -2.1, 1.1, y1 - 1.4, y1 + 1.7, z0 - 0.4, z1 - 0.1, m["tan_lit"], m))
    for i, (px0, px1) in enumerate(PANES):
        pane = mk.box("pane%d" % i, px0, px1, 1.7, 5.8, HOUSE_H - 0.3, HOUSE_H + 0.14, m["glass"])
        mk.bevel(pane, 0.12, 1, 35)
        parts.append(pane)
        parts.append(mk.ball("pane_glint%d" % i, (px0 + 0.9, 4.7, HOUSE_H + 0.12), (0.6, 0.32, 0.1), m["glint"], 10, 4))
    for i, (x, y) in enumerate(LAMPS):
        collar = mk.lathe("lamp_collar%d" % i, [(2.0, HOUSE_H - 0.5), (2.0, HOUSE_H + 0.35), (1.55, HOUSE_H + 0.5)],
                          (x, y), m["blue_dark"], 24)
        k.smooth(collar, 40)
        parts.append(collar)
        parts.append(mk.dome("lamp%d" % i, (x, y), (1.5, 1.5, 1.2), HOUSE_H + 0.35, m["lamp"], 24, 8))
        parts.append(mk.ball("lamp_glint%d" % i, (x - 0.5, y + 0.35, HOUSE_H + 1.35), (0.45, 0.4, 0.2), m["glint"], 10,
                             4))
    return parts


def fins(m):
    """The red fins at its sides: plates along y, their tops sloping down to the front."""
    out = []
    for i, (fx0, fx1) in enumerate(((HOUSING[0] - 1.5, HOUSING[0] + 0.3), (HOUSING[1] - 0.2, HOUSING[1] + 2.8))):
        outline = [(0.8, 0.0), (0.9, 3.0), (1.8, 4.6), (5.0, 4.9), (5.7, 3.8), (5.7, 0.0)]
        fin = mk.prism("fin%d" % i, outline, fx0, fx1, m["red"], axis="x")
        k.recalc_normals(fin)
        mk.bevel(fin, 0.3, 2, 35)
        mk.shade(fin, 35)
        mk.paint(fin, lambda c, n: m["red_lit"] if n.z > 0.3 or n.x < -0.5 else None)
        out.append(fin)
    return out


# --- The barrels -------------------------------------------------------------------------------------------------------

def axis():
    e = math.radians(ELEVATION)
    return Vector((0.0, -math.cos(e), math.sin(e)))


def can(name, x, t0, t1, r, mat, lip=0.0, back=0.25):
    """A round part along the barrel's axis from t0 to t1 (rounded at its ends), radius r."""
    b = Vector((x, BREECH[0], BREECH[1]))
    d = axis()
    profile = [(t0, r - back), (t0 + back * 0.6, r), (t1 - lip - 0.25, r), (t1 - 0.12, r - 0.25 - lip * 0.5),
               (t1, r - 0.6 - lip)]
    obj = ak.lathe_axis(name, profile, b, d, 20)
    obj.data.materials.append(mat)
    return obj


def barrel(m, x, run):
    """A barrel at x run out by run along its axis: the breech collar and sleeve, two tubes and their rings, the muzzle
    and its bore."""
    parts = []
    for i, (t0, t1, r, part) in enumerate(SLEEVE):
        parts.append(can("%s%g" % (part, x), x, t0, t1, r, m["blue_dark"] if part == "collar" else m["tan"]))
    s1 = run / 2                       # the first stage's run, the second's
    parts.append(can("tube1_%g" % x, x, TUBE1[0], RING1[0] + s1 + 0.2, TUBE1[1], m["blue"]))
    parts.append(can("ring1_%g" % x, x, RING1[0] + s1, RING1[0] + RING1[1] + s1, RING1[2], m["tan_lit"]))
    parts.append(can("tube2_%g" % x, x, TUBE2[0] + s1, MUZZLE[0] + run + 0.3, TUBE2[1], m["blue"]))
    t0 = MUZZLE[0] + run
    t1 = t0 + MUZZLE[1]
    r = MUZZLE[2]
    b = Vector((x, BREECH[0], BREECH[1]))
    d = axis()
    # The muzzle: a can with a rounded lip, its mouth open (a dark inner wall) down to the bore.
    profile = [(t0, r - 0.25), (t0 + 0.15, r), (t1 - 0.4, r), (t1 - 0.08, r - 0.3), (t1, r - 0.75), (t1, 2.05),
               (t1 - 0.25, 1.85), (t1 - 0.7, 1.75), (t1 - 0.72, 0.01)]
    muzzle = ak.lathe_axis("muzzle%g" % x, profile, b, d, 24)
    muzzle.data.materials.append(m["tan"])
    mk.paint(muzzle, lambda c, n: m["dark"] if (c - b - d * (c - b).dot(d)).length < 2.0 else None)
    parts.append(muzzle)
    # The bore: a red glowing disc at the mouth's bottom.
    parts.append(ak.lathe_axis("bore%g" % x, [(0.0, 1.62), (0.12, 1.62), (0.14, 0.01)], tuple(b + d * (t1 - 0.8)),
                               tuple(d), 24))
    parts[-1].data.materials.append(m["bore"])
    for p in parts:
        shade_barrel(p, m)
    return parts


def shade_barrel(obj, m):
    """The barrel's tans and blue-greys lit on the side the game's sun reaches, darker underneath."""
    base = obj.data.materials[0]
    darker = {m["tan"].name: m["tan_dark"], m["tan_lit"].name: m["tan"], m["blue"].name: m["blue_dark"]}
    lighter = {m["tan"].name: m["tan_lit"]}
    if base.name not in darker:
        return
    mk.paint(obj, lambda c, n: darker[base.name] if n.dot(ak.SUN) < 0.15 else
             lighter.get(base.name) if n.dot(ak.SUN) > 0.8 else None)


# --- The wreck ---------------------------------------------------------------------------------------------------------

def soot(objects, m):
    """The wreck's soot: patches of the housing and the barrels' parts painted dark by a fixed pattern."""
    def pattern(c):
        return math.sin(1.7 * c.x + 0.9 * c.y) + math.sin(1.1 * c.y - 2.3 * c.x + 0.6) + 0.6 * math.sin(2.9 * c.z)
    tans = {m["tan"].name, m["tan_lit"].name, m["tan_dark"].name}
    for obj in objects:
        names = [mat.name for mat in obj.data.materials]
        if obj.name == "housing":
            dense(obj, 1.6)
        if obj.name in ("stem", "frame_r", "back_block"):       # burnt whole, the panes dead
            mk.paint(obj, lambda c, n: m["char"] if n.z > 0.3 else m["soot"])
            continue
        if obj.name.startswith("pane"):
            mk.paint(obj, lambda c, n: m["char"])
            continue
        mk.paint(obj, lambda c, n: (m["char"] if pattern(c) > 1.2 else m["soot"]) if pattern(c) > 0.45 and
                 names[0] in tans else None)


def dense(obj, size):
    """Splits the object's faces until no edge is much longer than size (so the soot's pattern can follow)."""
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    for _ in range(6):
        long = [e for e in bm.edges if e.calc_length() > size]
        if not long:
            break
        bmesh.ops.subdivide_edges(bm, edges=long, cuts=1, use_grid_fill=False)
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    bm.to_mesh(obj.data)
    bm.free()


# --- Build -------------------------------------------------------------------------------------------------------------

def own_mask(sheets, sprite):
    """The launcher's own pixels: its sprite's pixels that are not the map's floor (ramp 0's greys outside its parts:
    the floor round it, under its barrels and between them)."""
    from sprite_profile import sprite_indices
    pix = sprite_indices(os.path.join(sheets, "enemy_P.png"), sprite, True)
    rows = []
    for r in range(28):
        row = []
        for c in range(24):
            v = pix[r][c]
            dark_arch = v is not None and v >> 4 == 0 and (v & 15) <= 3 and 8 <= c <= 13 and r <= 13
            row.append(v is not None and ((v >> 4) in (6, 7, 10) or dark_arch))
        rows.append(row)
    return rows


def models():
    return [("tan_launcher", 277), ("tan_launcher_275", 275), ("tan_launcher_273", 273), ("tan_launcher_271", 271),
            ("tan_launcher_wreck", 235)]


def build_model(sprite):
    wreck = sprite == 235
    m = materials(wreck)
    parts = housing(m) + top_parts(m) + fins(m)
    for x in BARRELS:
        parts += barrel(m, x, RUN_OUT[sprite])
    if wreck:
        soot(parts, m)
    return parts


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    for name, sprite in models():
        if only and name not in only:
            continue
        k.reset()
        bpy.context.scene.view_settings.view_transform = "Standard"
        parts = build_model(sprite)
        mask = own_mask(options["check"], sprite) if "check" in options else None
        ak.finish(name, parts, (0.0, 0.0), out, options, mask, world=True,
                  label="%s (P %d) as the camera sees it, its own pixels" % (name, sprite))


if __name__ == "__main__":
    build()
