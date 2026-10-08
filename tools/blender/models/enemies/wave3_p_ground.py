"""Wave 3, batch P of the enemy models, continued (wave3_p.py has the machines): sheet 2's ground sprites drawn
on rock and dirt, modelled as their sprites look (models.cfg: yaw=0), the rock and dirt as round boulders
and cobbles where the sprites draw them (wave3_p_kit.boulders).

- purple_pad_tl, purple_pad_t, purple_pad_tr, purple_pad_l, purple_pad_r, purple_pad_bl, purple_pad_b,
  purple_pad_br (2 279, 281, 283, 245, 207, 273, 275, 277) and eye_block (2 169): TYRIAN's panel of
  purple pads: the events lay them out in rows three sprites wide (279, 281, 283 above 245, 169, 207 above
  273, 275, 277, or the corners alone as two rows of two), each a bevelled octagonal pad on a ribbed
  purple floor that runs into grey rocks at the panel's edges; the middle one (eye_block) is a purple
  housing with a blue glass eye, two blue capsules and a grille of teeth (origin, so the floors meet).
- gold_domes_tl, _tr, _bl, _br (2 77, 79 above 115, 117): the dark steel housing on the dirt of TYRIAN
  and HOLES with four golden domes (a big one with a raised plate between two slots, two at its sides
  in steel clamps fed by golden pipes, one at the bottom with a dark port); event 12 places the four
  sprites as the sheet arranges them. Built whole and cut (origin).
- gold_pyramid_tl, _tr, _bl, _br (2 81, 83 above 119, 121): its neighbour: a dark steel capsule with
  two fangs, a golden pyramid lying on it pointing up the screen, a golden rod down from it and golden
  horns curling out over the dirt. Built whole and cut (origin).
- red_works_tl, _tr, _bl, _br (2 15, 17 above 53, 55): TYRIAN's red works in the rocks: a steel deck
  crowded with red blocks and pipes, a column of two glowing yellow grilles, a tan box with a red
  button, a dark recess with a tan floor and tan rails. Built whole and cut (origin).

usage: Blender -b --factory-startup -P wave3_p_ground.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1]
       [--whole gold_domes,gold_pyramid,red_works --preview <prefix>]
"""
import math
import os
import sys

import numpy as np
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_p_kit as w  # noqa: E402
from wave3_p_kit import art, k, sh, pal, model, whole, grid, regions, ramp, shade  # noqa: E402


# --- TYRIAN's purple pads ----------------------------------------------------------------------------

OCTAGON = w.octagon(0.0, 2.0, 9.0, 8.0, 5.0)  # the pad: columns 3-20, rows 4-19


def purple_mats(prefix):
    return {
        "groove": pal(f"{prefix}_purple6", 0x56, metallic=0.25, roughness=0.45),
        "floor": pal(f"{prefix}_purple8", 0x58, metallic=0.25, roughness=0.4),
        "rib": pal(f"{prefix}_purple10", 0x5a, metallic=0.25, roughness=0.38),
        "light": pal(f"{prefix}_purple11", 0x5b, metallic=0.25, roughness=0.35),
        "dark": pal(f"{prefix}_purple5", 0x55, metallic=0.25, roughness=0.45),
    }


def purple_floor(name, g, keep, m, z_groove=2.25, z_floor=2.4, z_rib=2.55):
    """The ribbed purple floor over the pixels keep(index, column, row) accepts: the light strips stand
    proud as ribs, the dark ones sink as grooves."""
    h, wd = len(g), len(g[0])
    heights = np.zeros((h, wd))
    index = np.zeros((h, wd), dtype=int)
    kept = np.zeros((h, wd), dtype=bool)
    for r in range(h):
        for c in range(wd):
            v = g[r][c]
            if not keep(v, c, r):
                continue
            kept[r, c] = True
            s = shade(v)
            if s >= 10:
                heights[r, c], index[r, c] = z_rib, 2
            elif s >= 8:
                heights[r, c], index[r, c] = z_floor, 1
            else:
                heights[r, c], index[r, c] = z_groove, 0
    return w.bed(name, heights, index, [m["groove"], m["floor"], m["rib"]], (12, 14), keep=kept, dissolve=0.5)


def octagon_pad(prefix, m, top=6.0):
    """The bevelled octagonal pad: its top-left bevels catch the light, the right and bottom ones dark."""
    pad = w.chamfered(prefix + "_pad", OCTAGON, 0.0, top, m["floor"], chamfer=1.3)

    def paint(c, n):
        if n.z > 0.95:
            return None
        if n.z < -0.5:
            return m["dark"]
        if n.x < -0.2 or n.y > 0.35:
            return m["light"]
        if n.x > 0.2:
            return m["groove"]
        return m["rib"]
    w.paint_faces(pad, paint)
    # A shallow inset panel in its top.
    inner = w.octagon(0.0, 2.0, 6.6, 5.6, 3.6)
    w.chamfered(prefix + "_pad_panel", inner, top - 0.5, top + 0.25, m["rib"], chamfer=0.35)
    return pad


def pad_tile(art_text, prefix):
    g = grid(art_text, 24)
    m = purple_mats(prefix)

    def in_octagon(c, r):
        x, y = c + 0.5 - 12, 14 - r - 0.5
        return abs(x) <= 9 and -6 <= y <= 10 and abs(x) + y <= 14 and abs(x) - y <= 10

    def purple(v, c, r):
        return v is not None and ramp(v) == 5
    # The floor runs on under the pad; the rocks fill the rest (and the odd transparent pixel).
    purple_floor(prefix + "_floor", g, purple, m)
    w.grey_rocks(prefix + "_rocks", g, lambda v, c, r: v is not None and ramp(v) in (0, 0xa) and not in_octagon(c, r),
                 prefix=prefix, keep_base=lambda v, c, r: not purple(v, c, r))
    octagon_pad(prefix, m)


for _name, _art, _sprite in (("purple_pad_tl", "PAD_BL", 279), ("purple_pad_t", "PAD_BM", 281),
                             ("purple_pad_tr", "PAD_BR", 283), ("purple_pad_l", "PAD_ML", 245),
                             ("purple_pad_r", "PAD_MR", 207), ("purple_pad_bl", "PAD_TL", 273),
                             ("purple_pad_b", "PAD_TM", 275), ("purple_pad_br", "PAD_TR", 277)):
    def _build(a=_art, n=_name):
        pad_tile(getattr(art, a), n)
    model(_name, [_sprite])(_build)



def PX(col, row):
    """A pixel's centre (column, row) of a 24 x 28 sprite as (x, y)."""
    return (col + 0.5 - 12.0, 14.0 - row - 0.5)


@model("eye_block", [169])
def eye_block():
    """The middle of the panel: a raised purple housing on the ribbed floor, a dark blue glass eye
    in a light rim, two blue capsules slanting below it like cheeks and a grille of four teeth."""
    g = grid(art.EYE, 24)
    m = purple_mats("eyeb")
    glass = pal("eyeb_glass", 0x34, metallic=0.35, roughness=0.05)
    glass_hi = pal("eyeb_glass_hi", 0x3d, metallic=0.2, roughness=0.05, glow=0.6)
    capsule = pal("eyeb_capsule", 0x38, metallic=0.35, roughness=0.08)
    capsule_hi = pal("eyeb_capsule_hi", 0x3c, metallic=0.25, roughness=0.06)
    recess = pal("eyeb_recess", 0x52, metallic=0.2, roughness=0.6)
    purple_floor("eyeb_floor", g, lambda v, c, r: v is not None, m)
    # The housing: a rounded block over most of the sprite, its top edge lit.
    house = w.block("eyeb_housing", (0.0, 1.0), 10.6, 11.6, 4.2, m["floor"], rounding=1.6, power=3.2, segments=32,
                    dome=0.4)
    w.paint_faces(house, lambda c, n: m["light"] if n.z < 0.9 and (n.x < -0.3 or n.y > 0.3) else
                  m["groove"] if n.z < 0.9 and (n.x > 0.3 or n.y < -0.3) else None)
    # The eye in its rim.
    ex, ey = PX(12.0, 10.5)
    w.hoop("eyeb_rim", (ex, ey, 4.4), [(6.3, -0.6), (7.6, -0.3), (7.7, 0.5), (6.6, 0.9), (6.0, 0.3)], m["rib"], 40)
    w.sphere("eyeb_eye", (ex, ey, 4.0), (6.4, 5.9, 4.4), glass, 24, 12)
    w.sphere("eyeb_glint", (ex - 2.4, ey + 2.2, 7.7), (1.6, 1.3, 0.6), glass_hi, 14, 7)
    # The capsules, slanting in towards the grille.
    for side, a, b in ((-1, PX(2.0, 16.8), PX(5.6, 21.2)), (1, PX(21.6, 17.2), PX(18.0, 21.4))):
        w.tube(f"eyeb_capsule{side}", [(a[0], a[1], 4.7), (b[0], b[1], 4.7)], 1.7, capsule, 14, squash=0.8)
        w.tube(f"eyeb_capsule_hi{side}", [(a[0] - 0.4, a[1] + 0.3, 5.9), (b[0] - 0.4, b[1] + 0.3, 5.9)], 0.45,
               capsule_hi, 6)
    # The grille: a dark recess, a lip over it and four teeth.
    w.rounded_box("eyeb_recess", (PX(11.5, 20.5)[0], PX(11.5, 20.5)[1], 4.0), (9.4, 5.6, 1.4), recess, bevel=0.4)
    w.rounded_box("eyeb_lip", (PX(11.5, 18.0)[0], PX(11.5, 18.0)[1], 4.8), (8.4, 1.4, 1.2), m["light"], bevel=0.4)
    for col in (8, 10, 12, 14):
        x, y = PX(col, 20.6)
        w.rounded_box(f"eyeb_tooth{col}", (x, y, 4.6), (1.1, 4.0, 1.4), m["light"], bevel=0.35)


# --- TYRIAN's golden machines on the dirt (48 x 56, built whole and cut into four sprites) ------------

def XY(col, row):
    """A pixel's centre of a 48 x 56 object as (x, y)."""
    return (col + 0.5 - 24.0, 28.0 - row - 0.5)


def dirtish(v, c=0, r=0):
    """The dirt's pixels: the dark browns (ramp 1, shades 0-4)."""
    return v is not None and ramp(v) in (1, 0xa) and shade(v) <= 4


def machine_mask(g):
    """The machine's pixels: the largest region not reachable through the dirt from the border, its
    holes filled."""
    dirt = w.flood(g, dirtish)
    rest = [[not dirt[r][c] and g[r][c] is not None for c in range(len(g[0]))] for r in range(len(g))]
    return w.fill_holes(w.largest_component(rest))


def gold_mats(prefix):
    return {
        "gold": pal(f"{prefix}_gold9", 0x19, metallic=0.75, roughness=0.3),
        "light": pal(f"{prefix}_gold12", 0x1c, metallic=0.75, roughness=0.25),
        "dark": pal(f"{prefix}_gold5", 0x15, metallic=0.7, roughness=0.35),
        "deep": pal(f"{prefix}_gold2", 0x12, metallic=0.4, roughness=0.5),
        "steel": pal(f"{prefix}_steel", 0x05, metallic=0.6, roughness=0.35),
        "steel_light": pal(f"{prefix}_steel_light", 0x09, metallic=0.6, roughness=0.3),
        "steel_dark": pal(f"{prefix}_steel_dark", 0x02, metallic=0.5, roughness=0.45),
    }


def housing(name, outline, m, height, radius=1.4, crown=0.6):
    """The dark steel housing: a plate over an outline (pixel corners (column, row) of the 48 x 56
    object), its corners rounded."""
    poly = [(c - 24.0, 28.0 - r) for c, r in outline]
    area = sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
               for i in range(len(poly)))
    if area < 0:
        poly = poly[::-1]
    poly = sh._chaikin(poly, 2)
    obj = sh.inflate(name, [poly], m["steel"], sh.pillow_profile(height, radius, crown=crown), bottom=0.0, base=0.0,
                     rim=0.2, spacing=0.8)
    k.smooth(w.simplify_bottom(obj), 45)
    return k.smooth(w.planar(obj, 2.5), 45)


def inside_outline(outline, col, row):
    """Whether a pixel's centre lies inside an outline of pixel corners."""
    x, y, inside = col + 0.5, row + 0.5, False
    n = len(outline)
    for i in range(n):
        (x0, y0), (x1, y1) = outline[i], outline[(i + 1) % n]
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            inside = not inside
    return inside


DOMES_HOUSING = [(5, 8), (9, 5), (31, 5), (34.5, 8), (37.5, 13), (37.5, 37), (35, 41), (34, 46), (29.5, 50.5),
                 (16, 51), (10.5, 46.5), (7.5, 44), (7, 40), (3, 38.5), (2, 35), (2, 14)]
PYRAMID_HOUSING = [(15, 3), (26, 3), (29, 4.5), (31, 7.5), (31.5, 12), (31.5, 41), (31, 44), (29.5, 48), (28, 51),
                   (26.5, 50.5), (23, 46), (21.5, 46), (21, 48), (19.5, 51.5), (17.5, 51), (14, 47), (10.5, 44),
                   (9, 41), (9, 12), (9.5, 7.5), (11.5, 4.5)]


def domes_whole():
    """A dark steel housing on the dirt carrying four golden domes: a big one at the top with a raised
    plate between two dark slots, two at its sides held by steel clamps and fed by golden pipes from
    the big one, and one at the bottom with a dark port."""
    g = grid(art.DOMES, 48)
    m = gold_mats("gdome")
    mask = machine_mask(g)
    under = [[mask[r][c] or inside_outline(DOMES_HOUSING, c, r) for c in range(48)] for r in range(56)]
    w.brown_dirt("dirt", g, lambda v, c, r: not under[r][c] and v is not None, prefix="gdome", origin=(24, 28),
                 keep_base=lambda v, c, r: True)
    housing("housing", DOMES_HOUSING, m, 2.6)
    domes = {"big": ((-4.5, 16.4, 1.6), (12.2, 10.9, 8.2)), "left": ((-16.0, -3.0, 1.4), (7.2, 5.4, 4.8)),
             "right": ((7.0, -3.0, 1.4), (6.8, 5.4, 4.8)), "bottom": ((-4.5, -12.6, 1.4), (6.8, 5.8, 5.0))}
    for key, (c, r) in domes.items():
        w.sphere(f"dome_{key}", c, r, m["gold"], 32 if key == "big" else 24, 14 if key == "big" else 10)
    # The big dome's face: a raised plate (an arch over a block) between two dark slots.
    bc, br = domes["big"]
    for i, (x0, x1, y0, y1, grow) in enumerate(((-9.6, 0.6, 16.5, 22.5, 0.7), (-7.6, -1.4, 8.6, 17.0, 1.1))):
        cap = w.sphere(f"plate{i}", bc, (br[0] + grow, br[1] + grow, br[2] + grow), m["light"], 32, 16)
        sh.cut_box([cap], x0, x1, y0, y1)
    for x in (-11.0, 2.0):
        pts = [(x, y, w.on_ellipsoid(bc, br, x, y, -0.15)) for y in (19.5, 17.0, 14.5, 12.0)]
        w.tube(f"slot{x:.0f}", pts, 0.9, m["deep"], 8, squash=0.7)
    # The pipes from the big dome down into the side domes.
    for side, pts in ((-1, [(-12.0, 8.6, 5.6), (-14.2, 5.6, 5.4), (-15.4, 2.6, 5.0)]),
                      (1, [(3.0, 8.6, 5.6), (5.3, 5.6, 5.4), (6.4, 2.6, 5.0)])):
        w.tube(f"pipe{side}", w.catmull(pts, 0.5), 1.15, m["gold"], 10)
    # Steel clamps on the side domes, a dark port in the bottom one.
    for key, x in (("left", -15.5), ("right", 6.5)):
        c, r = domes[key]
        for dx in (-1.1, 1.1):
            xx = x + dx
            pts = [(xx, y, w.on_ellipsoid(c, r, xx, y, 0.1)) for y in (-1.0, -3.0, -5.0, -6.8)]
            w.tube(f"clamp_{key}{dx:.0f}", pts, 0.75, m["steel_light"], 8, squash=0.8)
    c, r = domes["bottom"]
    w.sphere("port", (-5.0, -13.6, w.on_ellipsoid(c, r, -5.0, -13.6, -0.5)), (1.5, 1.3, 0.8), m["steel_dark"], 12, 6)


def pyramid_whole():
    """A dark steel capsule on the dirt, rounded at the top, two fangs at the bottom with a dark slot
    between them, panels on its upper part; a golden pyramid lies on it pointing up the screen, its left
    face lit and its right one dark, a golden rod running down from it; golden horns curl out over the
    dirt either side."""
    g = grid(art.PYRAMID, 48)
    m = gold_mats("gpyr")
    inside = [[inside_outline(PYRAMID_HOUSING, c, r) for c in range(48)] for r in range(56)]
    horn_px = [[v is not None and ramp(v) == 1 and shade(v) >= 5 and not inside[r][c] and r < 26
                for c, v in enumerate(row)] for r, row in enumerate(g)]
    w.brown_dirt("dirt", g, lambda v, c, r: not inside[r][c] and not horn_px[r][c] and v is not None,
                 prefix="gpyr", origin=(24, 28), keep_base=lambda v, c, r: True)
    body = housing("housing", PYRAMID_HOUSING, m, 5.0, radius=1.8, crown=0.8)
    top = lambda x, y: sh.surface_z(body, x, y, 5.0)  # noqa: E731
    # Panels on the upper part, a slot between the fangs below.
    for x0, x1 in ((-11.5, -7.5), (-0.5, 3.5)):
        cx = (x0 + x1) / 2
        w.rounded_box(f"panel{x0:.0f}", (cx, 18.5, top(cx, 18.5) - 0.3), (x1 - x0, 10.0, 1.2), m["steel_light"],
                      bevel=0.45)
    w.tube("slot", [(-2.5, y, top(-2.5, y) - 0.15) for y in (-9.0, -12.0, -15.0, -18.0, -20.5)], 0.85,
           m["steel_dark"], 8, squash=0.45)
    # The pyramid: its point up the screen, its ridge rising to its front edge.
    zb = top(-3.5, 6.0) - 0.4
    apex, left, right, front = (-3.5, 15.2, zb + 0.6), (-18.6, -0.6, zb), (11.6, -0.6, zb), (-3.5, 0.4, zb + 9.0)
    import bmesh
    import bpy
    bm = bmesh.new()
    vs = [bm.verts.new(p) for p in (apex, left, right, front)]
    for face in ((vs[0], vs[1], vs[3]), (vs[0], vs[3], vs[2]), (vs[1], vs[2], vs[3]), (vs[0], vs[2], vs[1])):
        bm.faces.new(face)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    mesh = bpy.data.meshes.new("pyramid")
    bm.to_mesh(mesh)
    bm.free()
    pyr = bpy.data.objects.new("pyramid", mesh)
    bpy.context.scene.collection.objects.link(pyr)
    pyr.data.materials.append(m["gold"])
    k.bevel(pyr, 0.45, 2)
    w.paint_faces(w.sh.apply_modifiers(pyr), lambda c, n: m["light"] if n.x < -0.25 and n.z > 0.2 else
                  m["dark"] if n.x > 0.25 and n.z > 0.2 else m["deep"] if n.z <= 0.2 and n.y < -0.5 else None)
    # The rod down from its front edge, a collar where it leaves.
    w.tube("rod", [(-3.5, 0.0, zb + 1.6), (-3.5, -3.5, top(-3.5, -3.5) + 0.5), (-3.5, -7.5, top(-3.5, -7.5) + 0.3)],
           1.1, m["gold"], 10)
    w.rounded_box("rod_collar", (-3.5, -0.9, zb + 1.2), (3.4, 1.4, 2.4), m["dark"], bevel=0.5)
    # The horns curling out over the dirt.
    for i, pts in enumerate((((10.0, 8.6), (7.0, 10.5), (5.0, 12.6), (4.2, 15.0)),
                             ((10.0, 14.6), (7.5, 16.5), (5.5, 18.6), (4.6, 21.2)),
                             ((30.6, 9.5), (33.0, 11.5), (35.0, 13.5), (36.4, 15.6)),
                             ((31.4, 15.5), (33.6, 17.5), (35.4, 19.5), (36.4, 21.2)))):
        path = []
        for j, (c, r) in enumerate(pts):
            x, y = XY(c, r)
            path.append((x, y, 3.4 - 2.2 * j / (len(pts) - 1)))
        path = w.catmull(path, 0.5)
        radii = [1.0 - 0.35 * j / (len(path) - 1) for j in range(len(path))]
        w.tube(f"horn{i}", path, radii, m["gold"], 8)


def quarters(name, sprites, builder):
    """Registers the four sprites of a 48 x 56 object built whole: top left, top right, bottom left,
    bottom right."""
    for (suffix, sprite), (x0, y0) in zip((("tl", sprites[0]), ("tr", sprites[1]), ("bl", sprites[2]),
                                           ("br", sprites[3])), ((-24, 0), (0, 0), (-24, -28), (0, -28))):
        def build(x0=x0, y0=y0):
            builder()
            w.bake()
            w.piece(w.meshes(), x0, x0 + 24, y0, y0 + 28)
        model(f"{name}_{suffix}", [sprite])(build)
    whole(name, (48, 56))(builder)



# --- TYRIAN's red works in the rocks (48 x 56, built whole and cut into four sprites) -----------------

WORKS_OUTLINE = [(2.5, 4), (36.5, 4), (36.5, 48.5), (6.5, 48.5), (6.5, 30), (0, 30), (0, 16), (2.5, 15.5)]


def works_whole():
    """A low steel deck in the rocks crowded with red machinery: red blocks at its top left and in the
    middle, a column of two glowing yellow grilles, red pipes along it and down its right side, a tan
    box with a red button at its left, a dark recess with a tan floor, a tan block at its lower left
    and tan rails."""
    g = grid(art.WORKS, 48)
    steel = pal("works_steel", 0x04, metallic=0.55, roughness=0.4)
    steel_light = pal("works_steel_light", 0x07, metallic=0.55, roughness=0.35)
    dark = pal("works_dark", 0x01, metallic=0.4, roughness=0.6)
    red = pal("works_red", 0x46, metallic=0.4, roughness=0.32)
    red_light = pal("works_red_light", 0x4a, metallic=0.4, roughness=0.28)
    tan = pal("works_tan", 0xa8, metallic=0.2, roughness=0.5)
    tan_light = pal("works_tan_light", 0xab, metallic=0.2, roughness=0.45)
    glow = pal("works_glow", 0x7b, metallic=0.0, roughness=0.2, glow=2.0)
    glow_hot = pal("works_glow_hot", 0x7d, metallic=0.0, roughness=0.15, glow=3.0)

    def XYc(c, r):
        return (c - 24.0, 28.0 - r)
    inside = [[inside_outline(WORKS_OUTLINE, c, r) for c in range(48)] for r in range(56)]
    w.grey_rocks("rocks", g, lambda v, c, r: v is not None and not inside[r][c] and ramp(v) in (0, 0xa), prefix="works",
                 origin=(24, 28), keep_base=lambda v, c, r: True)
    # The deck: a low steel slab over the machine, lighter where the sprite is light.
    h = np.zeros((56, 48))
    idx = np.zeros((56, 48), dtype=int)
    for r in range(56):
        for c in range(48):
            v = g[r][c]
            light = v is not None and ramp(v) == 0 and shade(v) >= 5
            h[r, c] = 2.2 + (0.4 if light else 0.0)
            idx[r, c] = 1 if light else 0
    w.bed("deck", h, idx, [steel, steel_light], (24, 28), keep=inside, dissolve=0.5)

    def box(name, c0, r0, c1, r1, z0, z1, mat, bevel=0.6, paint=None):
        (x0, y0), (x1, y1) = XYc(c0, r0), XYc(c1, r1)
        obj = w.rounded_box(name, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), (x1 - x0, y0 - y1, z1 - z0), mat,
                            bevel=bevel)
        if paint:
            w.paint_faces(obj, lambda cc, n: paint if n.z > 0.6 and n.x < 0.3 else None)
        return obj
    # Red blocks.
    box("red_tl", 3.5, 7, 16.8, 11, 1.5, 7.0, red, 0.9, red_light)
    box("red_tl_drop", 3.0, 10.5, 9.8, 15.5, 1.5, 6.2, red, 0.8, red_light)
    box("red_mid", 21.8, 7.8, 28.2, 15.4, 1.5, 6.6, red, 0.8, red_light)
    box("red_low", 12.6, 38.6, 18.6, 47.0, 1.5, 5.8, red, 0.8, red_light)
    box("red_right_low", 28.8, 32.8, 34.6, 47.6, 1.5, 4.8, red, 0.7, red_light)
    box("red_left_mid", 10.8, 21.6, 18.6, 29.4, 1.5, 5.0, red, 0.7, red_light)
    # The red pipes: along the middle, down the right side and across below the recess.
    zp = 4.6
    for name, pts in (("pipe_mid", [(11.0, 16.6), (24.0, 16.6), (34.5, 16.6)]),
                      ("pipe_right", [(34.5, 16.6), (34.5, 30.0), (34.5, 47.5)]),
                      ("pipe_low", [(21.0, 27.5), (28.0, 27.5), (34.5, 27.5)])):
        path = [(XYc(c, r)[0], XYc(c, r)[1], zp) for c, r in pts]
        pipe = w.tube(name, w.catmull(path, 1.0), 1.15, red, 10)
        w.paint_faces(pipe, lambda cc, n: red_light if n.z > 0.7 else None)
    for i, (c, r) in enumerate(((34.5, 16.6), (34.5, 27.5))):
        x, y = XYc(c, r)
        w.sphere(f"pipe_joint{i}", (x, y, zp), (1.7, 1.7, 1.6), red_light, 12, 6)
    # The column of glowing grilles.
    box("grille_column", 13.2, 10.6, 19.4, 21.6, 1.5, 7.4, dark, 0.6)
    for i, r0 in enumerate((11.6, 17.6)):
        box(f"grille{i}", 14.0, r0, 18.8, r0 + 3.4, 6.6, 7.9, glow, 0.4)
        for j in range(3):
            c = 14.8 + 1.6 * j
            box(f"grille_bar{i}{j}", c, r0 + 0.2, c + 0.5, r0 + 3.2, 7.4, 8.2, dark, 0.15)
        x, y = XYc(16.4, r0 + 1.7)
        w.sphere(f"grille_hot{i}", (x, y, 7.9), (1.4, 0.9, 0.35), glow_hot, 10, 5)
    # The tan box with its red button, the recess with its tan floor, the tan block and rails.
    box("tan_box", 0.2, 16.8, 10.0, 29.8, 1.5, 5.4, tan, 0.8, tan_light)
    x, y = XYc(5.0, 22.5)
    w.sphere("button_rim", (x, y, 5.2), (3.0, 2.6, 0.9), steel, 18, 8)
    w.sphere("button", (x, y, 5.5), (2.3, 2.0, 1.4), red, 18, 9)
    w.sphere("button_hi", (x - 0.7, y + 0.6, 6.6), (0.8, 0.6, 0.3), red_light, 8, 4)
    box("recess_frame", 21.0, 17.8, 31.0, 27.0, 1.5, 4.4, steel_light, 0.6)
    box("recess_floor", 22.6, 20.6, 29.8, 26.2, 1.5, 4.7, tan, 0.4)
    box("recess_shade", 22.6, 19.4, 29.8, 20.8, 1.5, 4.8, dark, 0.3)
    box("tan_block", 7.0, 33.0, 12.0, 47.8, 1.5, 6.0, tan, 0.8, tan_light)
    box("tan_rail", 15.0, 3.6, 28.0, 5.0, 1.5, 3.4, tan_light, 0.5)
    box("tan_rod", 31.0, 7.0, 33.0, 15.8, 1.5, 5.6, tan_light, 0.6)

quarters("gold_domes", (77, 79, 115, 117), domes_whole)
quarters("gold_pyramid", (81, 83, 119, 121), pyramid_whole)
quarters("red_works", (15, 17, 53, 55), works_whole)

w.run()
