"""FLEET's round grey pod (sheet K sprite 276, 2x2: 24 x 28 pixels; enemy 702 of episode 3 in FLEET, sky and top
layers; THE CORE's enemy 1671 of episode 6, sky; one frame, not animated), polished (2026-10-21; it replaces
wave3_o_machines.py's k_pod(), two pixel-art pillows (its helmet()) with a belt and lugs laid on). models.cfg:
model k_pod enemies/k_pod.glb; sprite k 276 k_pod yaw=0 glow=10:0.2:120:0.5:0 (a faint orange light round the
slot).

The sprite is its own mirror image across the middle of its height (rows 15-27 are rows 12-0, index for index):
two helmets back to back, the top one and its mirror image. No other sprite has its pixels (the pincer's machine,
K 153, has the same helmet on top but not its pixels), and no other enemy shows it.

As the sprite and its 4x upscale draw the top helmet (rows 0-12; the bottom one is its mirror image): an octagon
of grey armour plate, the full width (columns 0-23) from the belt up to row 8, its corners cut off on the diagonal
from there up to row 3 (where it is columns 5-19); on top a flat crown whose middle is a panel (columns 10-14) with
a grille of two dark slots (columns 11 and 13 of rows 8-11, a dark lintel over them at row 7), a deep groove either
side of the panel (columns 9 and 15), a lit rail outside each groove (columns 7-8 and 16-17) and, falling away to
the sides, the shoulders (lit down the left at column 3, darker to the right; the upscale draws a line down each,
columns 2 and 22); towards the end the crown slopes down to a dark seam (row 3) behind a cap (row 2, columns 6-18)
with a handle: two posts (columns 6-8 and 16-18 of row 1, the sky between them) and a bar across their ends (row
0). Round the middle a dark belt (rows 13-14) with lighter clamps across it (columns 3-5 and 19-20) and in its
middle a glowing slot (columns 9-15 of rows 12-15): a dark red rim round a lens white-hot in its middle (columns
11-12), orange towards its ends.

Built as a CAD modeller would (polish_machine_kit): each helmet a prism of its plan cut by the planes of its crown,
shoulders and end (a hip roof where they meet), its edges bevelled and its flat faces kept flat; the grooves, the
grille and a seam down each shoulder cut with exact booleans; the rails, the rib in the grille, the cap and the
handle laid on as bevelled bars. The top helmet is built and mirrored across the belt (y = 0). The belt is a dark
core sunk between the helmets' edges, bridged by two bevelled clamps with two bolts each; the slot a dark red bezel
set into both helmets' edges, a lens bulging out of its window, cut into bands of heat (polish_orb_red.band_split)
that glow in their own colours, well under 1 (the game's bloom and the cfg's glow add to them). The pod is a flying
machine: flat underneath (the camera never sees its belly), 9.5 pixels high, centred in height by the game.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; origin at the
sprite's centre (pixel 12, 14): column c's left edge is x = c - 12, row r's top edge y = 14 - r. The details are
symmetric about the middle of column 12 (x = 0.5); the plan follows the sprite (x -12 .. 12).

Replaces wave3_o_machines.py's k_pod(): remove its section ("# --- K 276: the round pod", the
@o.model("k_pod", [(276, True)]) registration and k_pod()) and k_pod's line in the docstring, and wave3_o_art.py's
K276 (only k_pod() reads it). helmet(), grey_rows(), paint_grey() and mats() stay (the pincer's machine uses them).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against
enemy_K.png), --preview <prefix>.
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
from polish_orb_red import band_split  # noqa: E402

NAME = "k_pod"
MID = 0.5                       # the details' middle (column 12's)

# The top helmet's plan: from the belt up to its end, its corners cut on the diagonal (through the middles of the
# sprite's steps: y = x + 17.5 on the left, y = 18.5 - x on the right).
BELT_EDGE = 1.0                 # the helmets' edges at the belt (rows 13-14 are the belt)
END = 10.6                      # the helmet's end (row 3, the seam behind the cap)
PLAN = [(-12.0, BELT_EDGE), (12.0, BELT_EDGE), (12.0, 6.5), (7.9, END), (-6.9, END), (-12.0, 5.5)]
# Heights: the underside, the crown; the crown's edges (the shoulders from x CROWN_X, the end from y CROWN_Y) and
# the slopes falling from them.
BOTTOM, CROWN = -3.0, 6.0
CROWN_X = (-6.0, 7.0)
CROWN_Y = 7.0
SHOULDER_SLOPE = 0.6            # 2.4 at the sides (x -12; 3.0 at x 12)
END_SLOPE = 0.72                # 3.4 at the end
BEVEL = 0.45
# The deep grooves either side of the panel (columns 9 and 15): x ranges; their depth.
GROOVES = [(-3.0, -2.05), (3.05, 4.0)]
GROOVE_DEPTH = 0.75
# The rails (columns 7-8 and 16-17): x ranges, how proud of the crown, where they start and end (y).
RAILS = [(-5.0, -3.0), (4.0, 6.0)]
RAIL_UP, RAIL_Y = 0.5, (1.25, 10.45)
# The grille in the panel: the recess (x0, x1, y0, y1, corner radius, depth), the rib down its middle (half-width,
# its top below the crown, its upper end).
GRILLE = (-1.0, 2.0, 2.45, 7.15, 0.75, 1.55)
RIB = (0.36, 0.35, 6.0)
# A panel seam down each shoulder (columns 2 and 22): its x, width and depth.
SEAMS = [(-9.55, 0.45, 0.35), (10.55, 0.45, 0.35)]
# The cap behind the end (row 2): x0, x1, y0, y1, corner radius, its top. The handle: posts (x ranges) from the cap
# to the bar, the bar's y, its radius and height.
CAP = (-6.0, 7.0, 10.0, 12.1, 0.55, 3.0)
POSTS = [(-5.5, -3.45), (4.45, 6.5)]
POST_Y = (11.4, 13.55)
POST_Z = (1.4, 2.75)
BAR_Y, BAR_R, BAR_Z = 13.45, 0.55, 2.1
# The belt: its half-width across and half-height up the screen; how far its top lies under the helmets'.
BELT = (11.7, 1.1)
BELT_SINK = 1.7
# The clamps across the belt (x ranges; they lie on the shoulders), how proud, their half-height; the bolts on them
# (radius, height; at y = +-BOLT_Y).
CLAMPS = [(-9.3, -6.45), (7.45, 10.3)]
CLAMP_UP, CLAMP_HALF = 0.45, 1.75
BOLT_R, BOLT_H, BOLT_Y = 0.55, 0.32, 1.05
# The slot: the bezel (x0, x1, y0, y1, corner radius; its top under the crown), its window (inset, depth); the
# notch cut for it into the helmets (how far round the bezel, how deep).
BEZEL = (-3.1, 4.1, -2.05, 2.05, 0.95, 0.35)
WINDOW = (0.75, 0.95)
NOTCH = (0.1, 3.4)
# The lens: its middle, radii (x, y, z); the heat over it: (x, y of the hottest point, falloff across x and y, the
# slant of the hot streak); the bands (lowest heat, palette index, glow).
LENS = ((0.5, 0.0, CROWN - 1.45), (2.95, 1.25, 1.0))
HEAT = (0.15, 0.0, 2.7, 1.1, -0.18)
LENS_BANDS = [(-9.0, 0x75, 0.3), (0.3, 0x78, 0.4), (0.52, 0x7a, 0.5), (0.76, 0x7d, 0.6)]


def materials():
    glow = k.level_palette()

    def mat(name, index, metallic=0.55, roughness=0.32):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)

    def lit(name, index, strength, roughness=0.22, emission_index=None):
        return k.material(name, palette=index, metallic=0.0, roughness=roughness,
                          emission=glow[index if emission_index is None else emission_index],
                          emission_strength=strength)
    m = {
        "plate": mat("kpod_plate", 0x0a),
        "side": mat("kpod_side", 0x07, 0.55, 0.36),
        "light": mat("kpod_light", 0x0b, 0.55, 0.28),
        "bright": mat("kpod_bright", 0x0d, 0.55, 0.25),
        "groove": mat("kpod_groove", 0x05, 0.5, 0.42),
        "belt": mat("kpod_belt", 0x03, 0.45, 0.5),
        "bezel": lit("kpod_bezel", 0x71, 0.15, 0.3, 0x72),
    }
    for _, index, strength in LENS_BANDS:
        m[("lens", index)] = lit(f"kpod_lens_{index:x}", index, strength)
    return m


# --- Shapes ------------------------------------------------------------------------------------------------------

def rect(x0, x1, y0, y1, r, segments=48):
    ring = mk.rounded_rect_ring(((x0 + x1) / 2, (y0 + y1) / 2), (x1 - x0) / 2, (y1 - y0) / 2, r, 0.0, segments)
    return [(p.x, p.y) for p in ring]


def plane_box(name, top, size=40.0):
    """Everything under the plane z = top(x, y), for intersecting with."""
    s = size
    return mk.wedge(name, [(-s, -s), (s, -s), (s, s), (-s, s)], 0.0, top, bottom=lambda x, y: top(x, y) - 200.0)


def shoulder_l(x, y):
    return CROWN - SHOULDER_SLOPE * (CROWN_X[0] - x)


def shoulder_r(x, y):
    return CROWN - SHOULDER_SLOPE * (x - CROWN_X[1])


def end_slope(x, y):
    return CROWN - END_SLOPE * (y - CROWN_Y)


def crown_top(y):
    """The crown's height up the screen (along the panel and the rails): flat, then the end's slope."""
    return CROWN if y <= CROWN_Y else end_slope(0.0, y)


def along_crown(name, x0, x1, y0, y1, up, down, mat):
    """A bar across x0..x1 from y0 to y1 lying along the crown (flat, then sloping down to the end): its top up
    over the crown, its bottom down under it (a prism of its side profile extruded across)."""
    ys = [y0] + ([CROWN_Y] if y0 < CROWN_Y < y1 else []) + [y1]
    top = [(y, crown_top(y) + up) for y in ys]
    bottom = [(y, crown_top(y) - down) for y in reversed(ys)]
    return mk.prism(name, top + bottom, x0, x1, mat, axis="x")


def mirror_y(objects):
    """Mirrors objects across y = 0 in place, keeping their shading (corner normals) and materials."""
    flip = Matrix.Scale(-1, 4, (0, 1, 0))
    for obj in objects:
        mk.apply(obj)
        mesh = obj.data
        corner = {}
        for poly in mesh.polygons:
            for li in poly.loop_indices:
                n = mesh.corner_normals[li].vector
                corner[(poly.index, mesh.loops[li].vertex_index)] = (n.x, -n.y, n.z)
        mesh.transform(flip)
        mesh.flip_normals()
        normals = [None] * len(mesh.loops)
        for poly in mesh.polygons:
            for li in poly.loop_indices:
                normals[li] = corner[(poly.index, mesh.loops[li].vertex_index)]
        mesh.normals_split_custom_set(normals)
        mesh.update()
    return objects


def triangulate(objects):
    """Splits every face into triangles (the same split every run, the custom normals kept), so that the export
    doesn't split the n-gons itself (its split of them changed when a --check render had evaluated the meshes)."""
    for obj in objects:
        mod = obj.modifiers.new("triangulate", "TRIANGULATE")
        mod.quad_method = "BEAUTY"
        mod.ngon_method = "BEAUTY"
        mod.min_vertices = 4
        mod.keep_custom_normals = True
        mk.apply(obj)
    return objects


# --- The helmet ----------------------------------------------------------------------------------------------------

def helmet(m, prefix):
    """The top helmet: its body (the plan cut by the crown's planes, bevelled; the grooves, the grille and the slot's
    notch cut into it), the rails, the rib, the cap and the handle."""
    body = mk.prism(f"{prefix}_body", PLAN, BOTTOM, CROWN, m["plate"])
    for i, top in enumerate((shoulder_l, shoulder_r, end_slope)):
        mk.boolean(body, plane_box(f"{prefix}_plane{i}", top), "INTERSECT")
    mk.cleanup(body)
    mk.bevel(body, BEVEL, 3, 30)
    # The grooves along the crown, the grille's recess, the slot's notch.
    cutters = [along_crown(f"{prefix}_groove{i}", x0, x1, BELT_EDGE - 1.0, END + 1.0, 3.0, GROOVE_DEPTH, m["groove"])
               for i, (x0, x1) in enumerate(GROOVES)]
    gx0, gx1, gy0, gy1, gr, gd = GRILLE
    cutters.append(mk.prism(f"{prefix}_grille", rect(gx0, gx1, gy0, gy1, gr), CROWN - gd, CROWN + 2.0, m["belt"]))
    bx0, bx1, by0, by1, br, _ = BEZEL
    around, deep = NOTCH
    cutters.append(mk.prism(f"{prefix}_notch", rect(bx0 - around, bx1 + around, by0 - around, by1 + around,
                                                    br + around), CROWN - deep, CROWN + 2.0, m["groove"]))
    for i, ((sx, sw, sd), top) in enumerate(zip(SEAMS, (shoulder_l, shoulder_r))):
        cutters.append(mk.wedge(f"{prefix}_seam{i}", [(sx - sw / 2, BELT_EDGE - 1.0), (sx + sw / 2, BELT_EDGE - 1.0),
                                                     (sx + sw / 2, END + 1.0), (sx - sw / 2, END + 1.0)], 0.0,
                                lambda x, y, top=top: top(x, y) + 3.0, m["groove"],
                                bottom=lambda x, y, top=top, sd=sd: top(x, y) - sd))
    mk.boolean(body, cutters, "DIFFERENCE")
    mk.cleanup(body)
    mk.shade(body, 35)

    def pick(c, n):
        if gx0 - 0.05 < c.x < gx1 + 0.05 and gy0 - 0.05 < c.y < gy1 + 0.05 and c.z < CROWN - 0.05:
            return m["belt"] if n.z > 0.8 else m["side"]              # the grille's floor and walls
        for x0, x1 in GROOVES:
            if x0 - 0.02 < c.x < x1 + 0.02 and c.z < crown_top(c.y) - 0.05:
                return m["groove"]
        for (sx, sw, sd), top in zip(SEAMS, (shoulder_l, shoulder_r)):
            if abs(c.x - sx) < sw / 2 + 0.02 and c.z < top(c.x, c.y) - 0.05:
                return m["groove"]
        if c.y < by1 + around + 0.05 and bx0 - around - 0.05 < c.x < bx1 + around + 0.05 and c.z < CROWN - 0.05:
            return m["groove"]                                            # the notch
        if n.z < 0.3:
            return m["side"]
        return None
    mk.paint(body, pick)
    parts = [body]
    # The rails, lit along their tops.
    for i, (x0, x1) in enumerate(RAILS):
        rail = along_crown(f"{prefix}_rail{i}", x0, x1, RAIL_Y[0], RAIL_Y[1], RAIL_UP, 0.6, m["light"])
        mk.bevel(rail, 0.3, 2, 30)
        mk.shade(rail, 35)
        mk.paint(rail, lambda c, n: m["side"] if n.z < 0.3 else None)
        parts.append(rail)
    # The rib down the grille's middle.
    half, below, y1 = RIB
    rib = mk.box(f"{prefix}_rib", MID - half, MID + half, gy0 - 0.3, y1, CROWN - gd - 0.1, CROWN - below,
                 m["light"])
    mk.bevel(rib, 0.15, 2, 30)
    mk.shade(rib, 35)
    parts.append(rib)
    # The cap behind the end, lit on top; the handle's posts and bar.
    x0, x1, y0, y1, r, top = CAP
    cap = mk.prism(f"{prefix}_cap", rect(x0, x1, y0, y1, r), BOTTOM + 2.0, top, m["plate"])
    mk.bevel(cap, 0.35, 2, 30)
    mk.shade(cap, 35)
    mk.paint(cap, lambda c, n: m["light"] if n.z > 0.8 else m["side"] if n.z < 0.3 else None)
    parts.append(cap)
    for i, (px0, px1) in enumerate(POSTS):
        post = mk.box(f"{prefix}_post{i}", px0, px1, POST_Y[0], POST_Y[1], POST_Z[0], POST_Z[1], m["plate"])
        mk.bevel(post, 0.3, 2, 30)
        mk.shade(post, 35)
        mk.paint(post, lambda c, n: m["light"] if n.z > 0.8 else m["side"] if n.z < 0.3 else None)
        parts.append(post)
    bar = mk.tube(f"{prefix}_bar", [(POSTS[0][0] + 0.25, BAR_Y, BAR_Z), (POSTS[1][1] - 0.25, BAR_Y, BAR_Z)], BAR_R,
                  m["groove"], 16)
    k.smooth(bar, 50)
    parts.append(bar)
    return parts


# --- The belt and the slot -----------------------------------------------------------------------------------------

def belt(m):
    """The dark core between the helmets' edges, its top BELT_SINK under theirs; the clamps across it with their
    bolts."""
    hw, hh = BELT
    core = mk.box("belt", -hw, hw, -hh, hh, BOTTOM + 0.4, CROWN, m["belt"])
    for i, top in enumerate((shoulder_l, shoulder_r)):
        mk.boolean(core, plane_box(f"belt_plane{i}", lambda x, y, top=top: top(x, y) - BELT_SINK), "INTERSECT")
    mk.boolean(core, plane_box("belt_top", lambda x, y: CROWN - BELT_SINK), "INTERSECT")
    mk.cleanup(core)
    mk.shade(core, 35)
    parts = [core]
    for i, ((x0, x1), top) in enumerate(zip(CLAMPS, (shoulder_l, shoulder_r))):
        clamp = mk.wedge(f"clamp{i}", rect(x0, x1, -CLAMP_HALF, CLAMP_HALF, 0.45, 32), 0.0,
                         lambda x, y, top=top: top(x, y) + CLAMP_UP, m["plate"],
                         bottom=lambda x, y, top=top: top(x, y) - 1.6)
        mk.bevel(clamp, 0.3, 2, 30)
        mk.shade(clamp, 35)
        mk.paint(clamp, lambda c, n: m["side"] if n.z < 0.3 else None)
        parts.append(clamp)
        cx = (x0 + x1) / 2
        for j, by in enumerate((-BOLT_Y, BOLT_Y)):
            z = top(cx, by) + CLAMP_UP - 0.08
            bolt = mk.dome(f"bolt{i}{j}", (cx, by), (BOLT_R, BOLT_R, BOLT_H), z, m["bright"], 16, 4)
            parts.append(bolt)
    return parts


def slot(m):
    """The bezel in the helmets' notch, its window, the lens bulging out of it in bands of heat."""
    x0, x1, y0, y1, r, below = BEZEL
    top = CROWN - below
    bezel = mk.prism("bezel", rect(x0, x1, y0, y1, r, 64), CROWN - NOTCH[1] - 0.2, top, m["bezel"])
    mk.bevel(bezel, 0.25, 2, 30)
    inset, depth = WINDOW
    window = mk.prism("window", rect(x0 + inset, x1 - inset, y0 + inset, y1 - inset, r - inset * 0.5, 64),
                      top - depth, top + 2.0, m["bezel"])
    mk.boolean(bezel, window, "DIFFERENCE")
    mk.cleanup(bezel)
    mk.shade(bezel, 35)
    centre, radii = LENS
    lens = k.ellipsoid("lens", centre, radii, m[("lens", LENS_BANDS[0][1])], 40, 20)
    hx, hy, fx, fy, slant = HEAT

    def heat(p):
        u, v = p.x - hx - slant * (p.y - hy) * 4.0, p.y - hy
        return 1.0 - math.hypot(u / fx, v / fy)
    band_split(lens, [heat(v.co) for v in lens.data.vertices],
               [(lowest, m[("lens", index)]) for lowest, index, _ in LENS_BANDS])
    k.smooth(lens, 80)
    return [bezel, lens]


def build():
    options = k.args()
    out = mk.outdir(options)
    k.reset()
    m = materials()
    top = helmet(m, "top")
    bottom = mirror_y(helmet(m, "bottom"))
    parts = triangulate(top + bottom + belt(m) + slot(m))
    bpy.context.view_layer.update()
    if "check" in options:
        sheet = os.path.join(options["check"], "enemy_K.png")
        mk.compare("k_pod (K 276)", mk.coverage(parts, 24, 28), k.sprite_mask(sheet, 276))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mk.report(NAME, parts, os.path.join(out, NAME + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + NAME, parts, distance=0.6)


if __name__ == "__main__":
    build()
