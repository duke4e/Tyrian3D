"""Episode 7's derrick (tools/content/gbc/new_enemies.json "derrick"): the mining rig the GBC ASTEROID2 stands on its
stone floors, which no PC level has. Built as the levels' tall ground objects are (polish_ball_mast.py): upright, then
leaned back up the screen, 70 degrees from upright about its feet (the game's camera, 20 degrees from straight down,
sees it from the side, face on, as a sprite draws it). A wooden top beam on four splayed legs (two outer ones, two
inner ones crossing behind), braced with crossbars and an iron strut, an iron pulley block under the beam's middle, a
chain from it down to a heavy rusted wrecking ball that hangs between the legs.

It is a 4-part enemy (event 12: a 2x2 block of 2x2 sprites, 48 x 56 pixels, part 0 lower left, 1 lower right, 2 upper
left, 3 upper right): built whole, cut along the sprites' edges (polish_arch.cut) into four pieces, each moved to its
sprite's centre (models.cfg: model gbc_derrick_* ... origin; sprite w <first sprite> gbc_derrick_* yaw=0). Its sprites
(sheet W, newshw.shp) are drawn from this model: --sprite renders the top view that
tools/content/gbc/sheet.py turns into them.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the floor; the whole's origin
is the middle of the block. Built upright (z up the rig's height, y its depth, the front at -y), then leaned.

Options after "--": --outdir <dir> (default assets/models/enemies), --preview <prefix>, --sprite <png>.
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
from polish_arch import cut  # noqa: E402
from polish_ball_mast import drop_unused, floor_cut  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402

# The pieces: (name, the box it covers in the whole's coordinates (x0, x1, y0, y1)), in event 12's order.
PIECES = [("gbc_derrick_ll", (-24.0, 0.0, -28.0, 0.0)), ("gbc_derrick_lr", (0.0, 24.0, -28.0, 0.0)),
          ("gbc_derrick_ul", (-24.0, 0.0, 0.0, 28.0)), ("gbc_derrick_ur", (0.0, 24.0, 0.0, 28.0))]

BETA = math.radians(70.0)
FEET_Y = -25.0                   # the feet's line on the picture
LEAN = Matrix.Translation((0.0, FEET_Y, 0.0)) @ Matrix.Rotation(-BETA, 4, "X")
SIN, COS = math.sin(BETA), math.cos(BETA)
TOP = 54.0                       # the beam's top, up the rig (upright: z)
BEAM = (-22.5, 21.5, 49.5, TOP, 2.6)   # x0, x1, z0, z1, half-depth
# The legs: foot (x, y, z) and head (x, y, z), half-thickness.
LEGS = [((-21.0, -3.0, -2.0), (-12.5, -1.2, 50.0), 1.5),
        ((20.0, -3.0, -2.0), (12.0, -1.2, 50.0), 1.5),
        ((-9.0, 3.6, -2.0), (4.5, 1.4, 50.0), 1.2),
        ((10.0, 3.6, -2.0), (-4.0, 1.4, 50.0), 1.2)]
CROSSBARS = [(19.0, -1.0), (33.0, -1.0)]   # heights up the rig, depth
STRUT = [(21.0, -1.0, 50.5), (14.9, -1.9, 33.0)]   # from the beam's right end down to the right leg
PULLEY_Z = 46.0
BALL_C = (0.0, -1.0, 17.0)
BALL_R = 7.4
LINK = 1.25                      # a chain link's length / 2


def materials():
    pal = k.level_palette()

    def mat(name, index, metallic=0.0, roughness=0.6, glow=0.0):
        if glow > 0:
            return k.material(name, palette=index, metallic=metallic, roughness=roughness, emission=pal[index],
                              emission_strength=glow)
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)
    return {
        "wood_dark": mat("derrick_wood_dark", 0xa3, 0.0, 0.7),
        "wood": mat("derrick_wood", 0xa6, 0.0, 0.65),
        "wood_lit": mat("derrick_wood_lit", 0xa8, 0.0, 0.6),
        "iron_dark": mat("derrick_iron_dark", 0x03, 0.6, 0.4),
        "iron": mat("derrick_iron", 0x06, 0.6, 0.35),
        "iron_lit": mat("derrick_iron_lit", 0x09, 0.6, 0.3),
        "rust": mat("derrick_rust", 0xe4, 0.45, 0.45),
        # The ball, with a little light of its own (a ball seen by the slanted camera shows mostly its dark side).
        "ball": mat("derrick_ball", 0xe5, 0.5, 0.4, 0.12),
        "ball_band": mat("derrick_ball_band", 0x07, 0.6, 0.35, 0.1),
        "seam": mat("derrick_seam", 0x01, 0.3, 0.6),
    }


def bar(name, a, b, half, mat, bevel=0.35):
    """A square wooden bar from a to b (its sides square to the rig's front)."""
    a, b = Vector(a), Vector(b)
    axis = b - a
    length = axis.length
    obj = mk.box(name, -half, half, -half, half, 0.0, length, mat)
    up = axis.normalized()
    side = Vector((0, 1, 0)).cross(up).normalized()
    front = up.cross(side).normalized()
    rot = Matrix((side, front, up)).transposed().to_4x4()
    obj.data.transform(Matrix.Translation(a) @ rot)
    obj.data.update()
    mk.bevel(obj, bevel, segments=2)
    mk.apply(obj)
    return obj


def paint_wood(obj, m):
    """The bars' faces by the light they catch: lit up the rig and to the left, dark below and to the right."""
    def pick(centre, normal):
        n = Vector(normal)
        lit = n.z * 0.4 - n.x * 0.5 - n.y * 0.6
        return m["wood_lit"] if lit > 0.35 else m["wood_dark"] if lit < -0.3 else m["wood"]
    mk.paint(obj, pick)


def chain(m, top, bottom):
    """Links from top down to bottom (z), alternately face on and edge on."""
    links = []
    z = top
    i = 0
    while z - 2 * LINK > bottom:
        cz = z - LINK
        ring = bpy.data.meshes.new("link%d" % i)
        obj = bpy.data.objects.new("link%d" % i, ring)
        bpy.context.scene.collection.objects.link(obj)
        import bmesh
        bm = bmesh.new()
        segs, minor = 10, 0.42
        verts = []
        for s in range(segs):
            a = 2 * math.pi * s / segs
            cx, cz_ = 0.55 * math.cos(a), LINK * math.sin(a)
            row = []
            for t in range(6):
                b = 2 * math.pi * t / 6
                rx = cx + minor * math.cos(b) * math.cos(a)
                rz = cz_ + minor * math.cos(b) * math.sin(a)
                ry = minor * math.sin(b)
                row.append(bm.verts.new((rx, ry, rz)))
            verts.append(row)
        for s in range(segs):
            for t in range(6):
                bm.faces.new((verts[s][t], verts[(s + 1) % segs][t], verts[(s + 1) % segs][(t + 1) % 6],
                              verts[s][(t + 1) % 6]))
        bm.to_mesh(ring)
        bm.free()
        ring.materials.append(m["iron"])
        turn = Matrix.Rotation(math.pi / 2 if i % 2 else 0.0, 4, "Z")
        ring.transform(Matrix.Translation((BALL_C[0], BALL_C[1], cz)) @ turn)
        ring.update()
        k.smooth(obj, 60.0)
        links.append(obj)
        z -= 2 * LINK * 0.82
        i += 1
    return links


def ball(m):
    cx, cy, cz = BALL_C
    obj = mk.ball("ball", (cx, cy, cz), (BALL_R, BALL_R, BALL_R), m["ball"], segments=32, rings=16)
    band = mk.lathe("ball_band", [(BALL_R + 0.25, cz - 0.9), (BALL_R + 0.45, cz), (BALL_R + 0.25, cz + 0.9)],
                    (cx, cy), m["ball_band"], segments=32)
    k.smooth(band, 60.0)
    shackle = mk.tube("shackle", [(cx - 1.4, cy, cz + BALL_R - 0.6), (cx - 1.4, cy, cz + BALL_R + 1.6),
                                  (cx, cy, cz + BALL_R + 2.6), (cx + 1.4, cy, cz + BALL_R + 1.6),
                                  (cx + 1.4, cy, cz + BALL_R - 0.6)], 0.55, m["iron_dark"], segments=8)
    k.smooth(shackle, 60.0)
    # rivets round the band
    rivets = []
    for j in range(10):
        a = 2 * math.pi * j / 10
        rivets.append(mk.ball("rivet%d" % j, (cx + (BALL_R + 0.45) * math.cos(a), cy + (BALL_R + 0.45) * math.sin(a), cz),
                              (0.5, 0.5, 0.5), m["iron_lit"], segments=8, rings=4))
    return [obj, band, shackle] + rivets


def build_rig(m):
    x0, x1, z0, z1, hd = BEAM
    # the beam: two planks, a dark seam between them
    planks = []
    for lo, hi in ((z0, z0 + 2.05), (z0 + 2.35, z1)):
        plank = mk.box("beam", x0, x1, -hd, hd, lo, hi, m["wood"])
        mk.bevel(plank, 0.4, segments=2)
        mk.apply(plank)
        paint_wood(plank, m)
        planks.append(plank)
    planks.append(mk.box("beam_seam", x0 + 0.5, x1 - 0.5, -hd + 0.3, hd - 0.3, z0 + 1.9, z0 + 2.5, m["seam"]))
    caps = []
    for x in (x0 - 0.6, x1 - 2.4):
        cap = mk.box("cap", x, x + 3.0, -hd - 0.4, hd + 0.4, z0 - 0.4, z1 + 0.4, m["iron"])
        mk.bevel(cap, 0.3, segments=1)
        mk.apply(cap)
        caps.append(cap)
    legs = []
    for i, (a, b, half) in enumerate(LEGS):
        leg = bar("leg%d" % i, a, b, half, m["wood"])
        paint_wood(leg, m)
        legs.append(leg)
        if i >= 2:
            continue  # (the inner legs' feet are under the floor once leaned)
        foot = mk.box("foot%d" % i, a[0] - 2.2, a[0] + 2.2, a[1] - 2.2, a[1] + 2.2, -2.0, 1.6, m["iron_dark"])
        mk.bevel(foot, 0.3, segments=1)
        mk.apply(foot)
        legs.append(foot)
        # an iron bracket where the leg meets the beam, two bolts through it
        bx = b[0]
        plate = mk.box("bracket%d" % i, bx - 2.6, bx + 2.6, -hd - 0.5, -hd + 0.2, z0 - 3.4, z0 + 2.0, m["iron"])
        mk.bevel(plate, 0.25, segments=1)
        mk.apply(plate)
        legs.append(plate)
        for bz in (z0 - 2.0, z0 + 0.8):
            legs.append(mk.ball("bracket_bolt", (bx, -hd - 0.6, bz), (0.55, 0.45, 0.55), m["iron_lit"], segments=8,
                                rings=4))
    bars = []
    for z, d in CROSSBARS:
        # between the outer legs at that height
        (fa, ha, _), (fb, hb, _) = LEGS[0], LEGS[1]
        ta, tb = (z - fa[2]) / (ha[2] - fa[2]), (z - fb[2]) / (hb[2] - fb[2])
        xa = fa[0] + (ha[0] - fa[0]) * ta
        xb = fb[0] + (hb[0] - fb[0]) * tb
        cb = bar("crossbar", (xa, d - 1.6, z), (xb, d - 1.6, z), 0.95, m["wood"], bevel=0.25)
        paint_wood(cb, m)
        bars.append(cb)
        for x in (xa + 1.2, xb - 1.2):
            bars.append(mk.ball("crossbar_bolt", (x, d - 2.6, z), (0.5, 0.4, 0.5), m["iron_lit"], segments=8, rings=4))
    strut = mk.tube("strut", [STRUT[0], STRUT[1]], 0.75, m["iron"], segments=8)
    k.smooth(strut, 50.0)
    bolts = [mk.ball("bolt", p, (0.9, 0.9, 0.9), m["iron_lit"], segments=10, rings=5) for p in STRUT]
    # the pulley block under the beam's middle: cheeks and a wheel
    cy = BALL_C[1]
    block = mk.box("pulley", -2.4, 2.4, cy - 1.6, cy + 1.6, PULLEY_Z - 2.2, z0 + 0.2, m["iron_dark"])
    mk.bevel(block, 0.4, segments=2)
    mk.apply(block)
    wheel = mk.lathe("wheel", [(0.01, -1.9), (2.0, -1.9), (2.4, -1.2), (1.9, 0.0), (2.4, 1.2), (2.0, 1.9),
                               (0.01, 1.9)], (0.0, 0.0), m["iron_lit"], segments=20)
    wheel.data.transform(Matrix.Translation((0.0, cy - 1.9, PULLEY_Z)) @ Matrix.Rotation(math.pi / 2, 4, "X"))
    wheel.data.update()
    k.smooth(wheel, 50.0)
    hook = chain(m, PULLEY_Z - 2.0, BALL_C[2] + BALL_R + 2.0)
    return planks + caps + legs + bars + [strut] + bolts + [block, wheel] + hook + ball(m)


def build_whole(m):
    build_rig(m)
    whole = mk.meshes()
    for obj in whole:
        mk.apply(obj)
        obj.data.transform(LEAN)
        obj.data.update()
    floor_cut(whole)
    bpy.context.view_layer.update()
    return [o for o in whole if len(o.data.polygons) > 0]


def render_sprite(whole, path, scale=8):
    """The top view framed like the block (48 x 56), at scale times its pixels: the source of its sprites."""
    scene = bpy.context.scene
    scene.view_settings.view_transform = "Standard"
    mk.preview(path[:-4], whole, size=(48, 56), scale=scale)
    os.replace(path[:-4] + "_top.png", path)
    os.remove(path[:-4] + "_3q.png")


def build():
    options = k.args()
    k.reset()
    m = materials()
    whole = build_whole(m)
    print("whole derrick: %d triangles, %d objects" % (mk.triangles(whole), len(whole)))
    bpy.context.scene.view_settings.view_transform = "Standard"
    if "sprite" in options:
        render_sprite(whole, options["sprite"])
    if "preview" in options:
        mk.preview(options["preview"] + "gbc_derrick_whole", whole, size=(48, 56), scale=10, distance=1.6)
    out = mk.outdir(options)
    for name, box in PIECES:
        pieces = [p for p in (cut(src, box, m["seam"]) for src in whole) if p is not None]
        drop_unused(pieces)
        mk.transform(pieces, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
        bpy.context.view_layer.update()
        triangulate(pieces)
        for src in whole:
            src.hide_render = True
        mk.report(name, pieces, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, pieces)
        for obj in pieces:
            bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False


if __name__ == "__main__":
    build()
