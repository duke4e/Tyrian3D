"""The grey block house of the asteroid levels (sheet P sprites 153 and 155 above 191 and 193, 2x2 each: one 48 x 56
picture; ground layer; enemies 313-316 in ASTEROID2, ASTEROID?, ASTCITY and AST. CITY, 1567-1570 in GREY MOON),
polished (2026-10-19; it replaces wave3_w.py's block_house_whole(), a slab with raised plates and the three hatches
always half sunk). models.cfg: model block_house_tl / block_house_tr / block_house_bl / block_house_br ... origin
and their frame models (below); sprite p 153 block_house_tl yaw=0 height=-4, sprite p 155 block_house_tr yaw=0
height=-4, sprite p 191 block_house_bl yaw=0 height=-4, sprite p 193 block_house_br yaw=0 height=-4. The levels
always put the four together (event 12, "4-part enemy": 313 (191) at (x, y), 314 (193) at (x + 24, y), 315 (153) at
(x, y - 28), 316 (155) at (x + 24, y - 28)). None of these sprites is another sprite's pixels mirrored or recoloured
(191's frames 195 and 199 are nearly it).

As the sprites and their 4x upscales draw it (all of it in the grey ramp 0): a block, its roof columns 4-42 of rows
0-42 of the picture (its corners rounded, most at the bottom left), laid with fifteen raised slabs (pixels 09; the
model's are 0a, as the game's light dims them; their top and left edges lit 0a-0e, dark grooves between them: the
slabs of wave3_w_kit.py's HOUSE_PANELS); its front
(rows 43-52) a dark wall ribbed every four columns (columns 12-40); the asteroid floor round it (left of column 4,
below row 52) and its shadow on it (right of column 42) are the map's and the game's, left out. Animated (enemies
313-316 run frames 1 1 1 1 2 2 3 3 2 2 1 ... over and over): three of the slabs are hatches that sink into the roof,
a little in the second frames (157, 159, 195, 197: they darken to 08 in dark rims) and deep in the third (161, 163,
199, 201: 05-06, shadowed along their upper and left edges by the wells' walls): d (columns 12-25 of rows 7-19), f
(38-42 of 11-18) and l (20-32 of 27-34). d spans the two top pieces, l all four: every piece changes.

Built as such a block of armoured concrete: its body lofted from rounded rectangles (the corners' radii as the
sprites round them), its back and sides upright, its front a battered glacis from the roof's edge (row 43) down to
its foot on the floor (row 53), so that the game's slanted camera sees it as the sprites' front wall; ribs down the
glacis where the sprites draw them; the roof's edge rounded (lit along the back and the left in the game's sun); the
slabs raised plates with chamfered edges (painted lit towards the upper left and shaded towards the lower right, as
the sprites draw them), bolted at their corners; slab j, three pixels wide (columns 16-18 of rows 21-42), a conduit
in clamps; a vent on slab b; the hatches plates in wells cut into the roof (dark walls), hinged along their upper
edge, flush with the slabs in the first frame, HATCH_DROP lower in the others and darker as the sprites draw them.
The walls reach SKIRT below the floor (z = 0), so the house stands on the terrain with height=-4 or without it.

Built whole and cut along the sprites' edges into the four pieces (polish_arch.py's cut(): the pieces keep the
whole's shading across the cuts), each moved so its sprite's centre is its origin; one set of pieces per frame:
block_house_tl, _tr, _bl, _br (frames 153, 155, 191, 193), block_house_tl_157, _tr_159, _bl_195, _br_197 and
block_house_tl_161, _tr_163, _bl_199, _br_201 (models.cfg: frame p 157 block_house_tl_157 and so on).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the floor (z = 0); the
whole's origin is the corner where the four sprites meet: P(c, r) turns the picture's pixel edges (column c, row r)
into these coordinates (x = c - 24, y = 28 - r).

Replaces wave3_w.py's block house: remove HOUSE, block_house_whole() and its kit.pieced("block_house", ...)
registration; wave3_w_kit.py's house() and its HOUSE_* tables stay (wave3_w_works.py builds the pump, the cargo pod
and the drilling rig on them).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the
whole and of each piece against the house's pixels in enemy_P.png), --preview <prefix> (the whole's and each piece's
top and 3/4 views), --only <model,...> (pieces by model name), --frames 1,2,3.
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
from polish_arch import cut  # noqa: E402  (polish_machine_kit.cut without its material indices shifted twice)

# The pieces: (name, its sprite in each frame, the box it covers in the whole's coordinates (x0, x1, y0, y1)).
PIECES = [("block_house_tl", (153, 157, 161), (-24.0, 0.0, 0.0, 28.0)),
          ("block_house_tr", (155, 159, 163), (0.0, 24.0, 0.0, 28.0)),
          ("block_house_bl", (191, 195, 199), (-24.0, 0.0, -28.0, 0.0)),
          ("block_house_br", (193, 197, 201), (0.0, 24.0, -28.0, 0.0))]
SPRITE_AT = {"tl": (0, 0), "tr": (24, 0), "bl": (0, 28), "br": (24, 28)}  # top left corners in the picture
# The frames: how far the hatches are sunk below the slabs, their shade.
FRAMES = [(0.0, 0x0a), (1.0, 0x08), (2.7, 0x06)]


def P(c, r):
    """A pixel edge of the 48 x 56 picture (column c, row r) in the whole's coordinates."""
    return (c - 24.0, 28.0 - r)


X0, X1 = P(4, 0)[0], P(43, 0)[0]       # the house's sides
Y_BACK = P(0, 0.05)[1]                 # its back (just inside the top pieces' edge)
Y_FRONT = P(0, 43)[1]                  # the roof's front edge
Y_FOOT = P(0, 53)[1]                   # the glacis' foot
RADII = (5.0, 4.0, 2.4, 2.0)           # the corners' radii: bottom left, bottom right, top right, top left
H = 10.0                               # the roof
EDGE = 0.65                            # the roof's rounded edge: its width and drop
SKIRT = -4.0                           # how far the walls reach below the floor
PANEL_H, PANEL_CHAMFER = 0.62, 0.3     # the slabs: how far they stand above the roof, their chamfer
# The slabs (pixel columns and rows, inclusive), as the sprites lay them; hatches are marked.
PANELS = [
    ("a", 4, 25, 0, 5), ("b", 27, 42, 0, 9), ("c", 4, 10, 7, 19), ("d", 12, 25, 7, 19, "hatch"),
    ("e", 27, 36, 11, 14), ("f", 38, 42, 11, 18, "hatch"), ("g", 27, 36, 16, 25), ("h", 38, 42, 20, 25),
    ("i", 4, 14, 21, 29), ("k", 20, 25, 21, 25), ("l", 20, 32, 27, 34, "hatch"), ("m", 34, 42, 27, 42),
    ("n", 20, 32, 36, 42), ("o", 4, 14, 31, 42),
]
CONDUIT = (16, 18, 21, 42)             # slab j: the conduit (columns, rows)
WELL_DEPTH = 3.6                       # the hatches' wells below the roof
WELL_GAP = 0.18                        # the gap round a hatch in its well
RIB_COLUMNS = (12, 16, 20, 24, 28, 32, 36)  # the ribs down the glacis (their pixel columns)
RIB_W, RIB_PROUD = 0.9, 0.42
VENT = ("b", 6)                        # the vent: on slab b, with this many slats


def materials(hatch_shade):
    def mat(name, index, metallic=0.3, roughness=0.55):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)
    return {
        "roof": mat("house_roof", 0x0a),
        "lit": mat("house_lit", 0x0c),
        "shade": mat("house_shade", 0x07),
        "groove": mat("house_groove", 0x05),
        "wall": mat("house_wall", 0x06),
        "glacis": mat("house_glacis", 0x04, 0.25, 0.6),
        "well": mat("house_well", 0x02, 0.2, 0.7),
        "hatch": mat(f"house_hatch_{hatch_shade:x}", hatch_shade),
        "conduit": mat("house_conduit", 0x08, 0.5, 0.35),
        "seam": mat("house_seam", 0x03, 0.2, 0.7),
    }


# --- Helpers ------------------------------------------------------------------------------------------------------

def rrect(x0, x1, y0, y1, radii, z, steps=7):
    """A rectangle with rounded corners (radii: bottom left, bottom right, top right, top left) at height z,
    counter-clockwise from its bottom left corner's arc; every corner gets steps + 1 points (equal counts, for
    lofting)."""
    out = []
    for (cx, cy, r, a0) in ((x0, y0, radii[0], 180), (x1, y0, radii[1], 270), (x1, y1, radii[2], 0),
                            (x0, y1, radii[3], 90)):
        r = max(r, 0.02)
        ox = cx + (r if a0 in (180, 90) else -r)
        oy = cy + (r if a0 in (180, 270) else -r)
        for i in range(steps + 1):
            a = math.radians(a0 + 90 * i / steps)
            out.append(Vector((ox + r * math.cos(a), oy + r * math.sin(a), z)))
    return out


def paint_plate(obj, m, top):
    """A raised plate's faces: its top `top`, its chamfers lit towards the upper left and shaded towards the lower
    right (as the sprites draw the slabs' edges), its sides as the walls."""
    def pick(c, n):
        if n.z > 0.95:
            return top
        if n.z > 0.3:
            return m["lit"] if (n.x < -0.25 or n.y > 0.25) else m["shade"]
        return m["wall"]
    mk.paint(obj, pick)


def panel_box(spec):
    """A slab's plan: its pixels less a little (the grooves), kept inside the roof's rounded edge, its outer corners
    rounded with the roof's where it reaches them."""
    name, c0, c1, r0, r1 = spec[:5]
    (x0, y1), (x1, y0) = P(c0, r0), P(c1 + 1, r1 + 1)
    x0, x1, y0, y1 = x0 + 0.08, x1 - 0.08, y0 + 0.08, y1 - 0.08
    inset = EDGE + 0.3
    x0, x1 = max(x0, X0 + inset), min(x1, X1 - inset)
    y0, y1 = max(y0, Y_FRONT + inset), min(y1, Y_BACK - inset)
    radii = []
    for (cx, cy), r in zip(((X0, Y_FRONT), (X1, Y_FRONT), (X1, Y_BACK), (X0, Y_BACK)), RADII):
        px = x0 if cx == X0 else x1
        py = y0 if cy == Y_FRONT else y1
        near = abs(px - (cx + (inset if cx == X0 else -inset))) < 0.05 and \
            abs(py - (cy + (inset if cy == Y_FRONT else -inset))) < 0.05
        radii.append(max(r - inset, 0.25) if near else 0.25)
    return x0, x1, y0, y1, radii


def plate(name, x0, x1, y0, y1, radii, z0, z1, m, top):
    outline = [(p.x, p.y) for p in rrect(x0, x1, y0, y1, radii, 0.0, 4)]
    obj = mk.prism(name, outline, z0, z1, m["wall"])
    mk.bevel(obj, PANEL_CHAMFER, 1, 35, profile=0.5)
    mk.shade(obj, 35)
    paint_plate(obj, m, top)
    return obj


# --- The parts ----------------------------------------------------------------------------------------------------

def body(m):
    """The block: lofted from rounded rectangles, from below the floor up its upright back and sides and its battered
    front, over the roof's rounded edge to the roof."""
    rings = []
    top_z = H - EDGE
    rings.append(rrect(X0, X1, Y_FOOT, Y_BACK, RADII, SKIRT))
    for i in range(7):  # the glacis, the back and the sides
        f = i / 6
        y0 = Y_FOOT + (Y_FRONT - Y_FOOT) * f
        rings.append(rrect(X0, X1, y0, Y_BACK, RADII, top_z * f))
    for a in (25, 50, 75, 90):  # the rounded edge
        t = math.radians(a)
        inset = EDGE * (1 - math.cos(t))
        rings.append(rrect(X0 + inset, X1 - inset, Y_FRONT + inset, Y_BACK - inset,
                           [max(r - inset, 0.05) for r in RADII], top_z + EDGE * math.sin(t)))
    obj = k.loft("house", rings, m["wall"], start_point=(0.0, 0.0, SKIRT),
                 end_point=((X0 + X1) / 2, (Y_FRONT + Y_BACK) / 2, H))
    return obj


def wells(m, hatches):
    """Cuts the hatches' wells into the roof (dark walls)."""
    house = bpy.data.objects["house"]
    for name, (x0, x1, y0, y1, radii) in hatches.items():
        outline = [(p.x, p.y) for p in rrect(x0 - WELL_GAP, x1 + WELL_GAP, y0 - WELL_GAP, y1 + WELL_GAP,
                                            [r + WELL_GAP for r in radii], 0.0, 4)]
        cutter = mk.prism(f"well_{name}", outline, H - WELL_DEPTH, H + 2.0, m["well"])
        mk.boolean(house, cutter, "DIFFERENCE")
    mk.cleanup(house)
    k.smooth(house, 40)

    def pick(c, n):
        top = c.z > H - 0.02 and n.z > 0.95
        g = WELL_GAP + 0.01
        for x0, x1, y0, y1, _ in hatches.values():
            if x0 - g <= c.x <= x1 + g and y0 - g <= c.y <= y1 + g and c.z < H - 0.01:
                return m["well"]
        if top:
            return m["groove"]
        if n.z > 0.3 and c.z > H - EDGE - 0.05:  # the roof's rounded edge
            return m["lit"] if (n.x < -0.3 or n.y > 0.3) else m["shade"]
        if n.y < -0.4 and n.z > 0.2 and c.z > -0.01:
            return m["glacis"]
        return None
    mk.paint(house, pick)


def slabs(m, drop):
    """The slabs and the hatches (drop: how far the hatches are sunk), bolts at the slabs' corners."""
    hatches = {}
    for spec in PANELS:
        x0, x1, y0, y1, radii = panel_box(spec)
        if len(spec) > 5:
            hatches[spec[0]] = (x0, x1, y0, y1, radii)
            continue
        plate(f"slab_{spec[0]}", x0, x1, y0, y1, radii, H - 0.1, H + PANEL_H, m, m["roof"])
        if min(x1 - x0, y1 - y0) > 3.2:
            for i, (bx, by) in enumerate(((x0 + 0.8, y0 + 0.8), (x1 - 0.8, y0 + 0.8), (x1 - 0.8, y1 - 0.8),
                                          (x0 + 0.8, y1 - 0.8))):
                mk.dome(f"bolt_{spec[0]}{i}", (bx, by), (0.26, 0.26, 0.16), H + PANEL_H - 0.04, m["lit"], 8, 2)
    for name, (x0, x1, y0, y1, radii) in hatches.items():
        z0 = H - 0.1 - drop
        plate(f"hatch_{name}", x0, x1, y0, y1, radii, z0, H + PANEL_H - drop, m, m["hatch"])
        # Hinges along its upper edge: short rods lying across it.
        spots = (x0 + 1.4, x1 - 1.4) if x1 - x0 >= 4.0 else ((x0 + x1) / 2,)
        for j, hx in enumerate(spots):
            hz = H + PANEL_H - drop + 0.05
            round_ = [(0.3 * math.cos(2 * math.pi * q / 10), 0.3 * math.sin(2 * math.pi * q / 10)) for q in range(10)]
            rod = [[Vector((hx + dx, y1 - 0.55 + u, hz + v)) for u, v in round_] for dx in (-0.6, 0.6)]
            k.smooth(k.loft(f"hinge_{name}{j}", rod, m["conduit"]), 50)
    return hatches


def conduit(m):
    """Slab j: a conduit along the roof in clamps."""
    c0, c1, r0, r1 = CONDUIT
    x = (P(c0, 0)[0] + P(c1 + 1, 0)[0]) / 2
    y_top = P(0, r0)[1] - 0.2
    y_end = Y_FRONT + EDGE + 0.4
    pts, ups = [], []
    for i in range(9):
        y = y_top + (y_end - y_top) * i / 8
        pts.append(Vector((x, y, H - 0.05)))
        ups.append(Vector((0, 0, 1)))
    pipe = mk.bar("conduit", pts, ups, 1.05, 0.85, 0.2, m["conduit"], 14, 2.2)
    k.smooth(pipe, 50)
    for i in range(4):
        y = y_top - 1.2 - i * (y_top - y_end - 2.4) / 3
        clamp = mk.box(f"clamp{i}", x - 1.35, x + 1.35, y - 0.32, y + 0.32, H - 0.05, H + 0.95, m["shade"])
        mk.bevel(clamp, 0.22, 2, 35)
        mk.shade(clamp, 35)
    return pipe


def vent(m):
    """A vent on a slab: a frame round slats."""
    spec = next(s for s in PANELS if s[0] == VENT[0])
    x0, x1, y0, y1, _ = panel_box(spec)
    cx, cy = (x0 + x1) / 2 + 2.0, (y0 + y1) / 2 - 0.4
    w, d = 6.0, 4.6
    z = H + PANEL_H
    frame = mk.box("vent", cx - w / 2, cx + w / 2, cy - d / 2, cy + d / 2, z - 0.1, z + 0.28, m["shade"])
    mk.bevel(frame, 0.12, 1, 35)
    mk.shade(frame, 35)
    mk.paint(frame, lambda c, n: m["roof"] if n.z > 0.95 else None)
    pit = mk.box("vent_pit", cx - w / 2 + 0.45, cx + w / 2 - 0.45, cy - d / 2 + 0.45, cy + d / 2 - 0.45, z + 0.2,
                 z + 0.3, m["well"])
    for i in range(VENT[1]):
        sy = cy - d / 2 + 0.75 + i * (d - 1.5) / (VENT[1] - 1)
        slat = mk.box(f"slat{i}", cx - w / 2 + 0.5, cx + w / 2 - 0.5, sy - 0.2, sy + 0.2, z + 0.15, z + 0.42, m["lit"])
        mk.bevel(slat, 0.08, 1, 35)
        mk.shade(slat, 35)
        mk.paint(slat, lambda c, n: m["shade"] if n.y < -0.3 else None)
    return pit


def ribs(m):
    """Ribs down the glacis, where the sprites draw them."""
    top_z = H - EDGE
    d = Vector((Y_FRONT - Y_FOOT, top_z)).normalized()
    n = Vector((-d.y, d.x))  # out of the glacis (down the screen and up)
    foot, top = Vector((Y_FOOT, 0.0)), Vector((Y_FRONT, top_z))
    inner_foot, inner_top = foot - n * 0.2, top - n * 0.2 - d * 0.1
    outer_top, outer_foot = top + n * (RIB_PROUD * 0.5) - d * 0.3, foot + n * RIB_PROUD
    outline = [(outer_foot.x, SKIRT), tuple(outer_foot), tuple(outer_top), tuple(inner_top), tuple(inner_foot),
               (inner_foot.x, SKIRT)]
    made = []
    for c in RIB_COLUMNS:
        xc = P(c + 0.5, 0)[0]
        rib = mk.prism(f"rib{c}", outline, xc - RIB_W / 2, xc + RIB_W / 2, m["wall"], axis="x")
        mk.bevel(rib, 0.14, 1, 35)
        mk.shade(rib, 35)
        made.append(rib)
    return made


# --- Build --------------------------------------------------------------------------------------------------------

def build_whole(m, drop):
    body(m)
    hatches = slabs(m, drop)
    wells(m, hatches)
    conduit(m)
    vent(m)
    ribs(m)
    whole = mk.meshes()
    for obj in whole:
        mk.apply(obj)
    bpy.context.view_layer.update()
    return whole


def house_mask():
    """The house's pixels: its roof and its front wall (columns 4-42 of rows 0-52), corners rounded."""
    outline = [(p.x, p.y) for p in rrect(X0, X1, Y_FOOT, Y_BACK + 0.05, RADII, 0.0, 8)]

    def inside(x, y):
        hit = False
        j = len(outline) - 1
        for i in range(len(outline)):
            (ax, ay), (bx, by) = outline[i], outline[j]
            if (ay > y) != (by > y) and x < (bx - ax) * (y - ay) / (by - ay) + ax:
                hit = not hit
            j = i
        return hit
    return [[inside(c + 0.5 - 24.0, 28.0 - r - 0.5) for c in range(48)] for r in range(56)]


def piece_mask(corner):
    c0, r0 = SPRITE_AT[corner]
    return [row[c0:c0 + 24] for row in house_mask()[r0:r0 + 28]]


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    frames = [int(f) for f in options.get("frames", "1,2,3").split(",")]
    for f in frames:
        drop, shade = FRAMES[f - 1]
        k.reset()
        m = materials(shade)
        whole = build_whole(m, drop)
        print("whole block house, frame %d: %d triangles, %d objects" % (f, mk.triangles(whole), len(whole)))
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        if "check" in options and f == 1:
            mk.compare("whole (P 153 + 155 above 191 + 193, the house)", mk.coverage(whole, 48, 56), house_mask())
        if "preview" in options:
            mk.preview(options["preview"] + "block_house_whole_%d" % f, whole, size=(48, 56), scale=8, distance=1.8)
        for name, sprites, box in PIECES:
            model = name if f == 1 else "%s_%d" % (name, sprites[f - 1])
            if only and model not in only and name not in only:
                continue
            pieces = [p for p in (cut(src, box, m["seam"]) for src in whole) if p is not None]
            mk.transform(pieces, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
            bpy.context.view_layer.update()
            for src in whole:
                src.hide_render = True
            if "check" in options and f == 1:
                mk.compare("%s (P %d)" % (model, sprites[f - 1]), mk.coverage(pieces, 24, 28),
                           piece_mask(name.rsplit("_", 1)[1]))
            mk.report(model, pieces, os.path.join(out, model + ".glb"))
            if "preview" in options:
                mk.preview(options["preview"] + model, pieces)
            for obj in pieces:
                bpy.data.objects.remove(obj)
            for src in whole:
                src.hide_render = False


if __name__ == "__main__":
    build()
