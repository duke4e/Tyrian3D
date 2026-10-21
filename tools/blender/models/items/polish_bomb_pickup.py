"""Super bomb pick-up (the coins sheet's sprite 89, enemy type 800, value -4: the item that gives a super bomb; 2x2, 24 x
28 pixels; about 45 of them in the levels: ** ALE **, ASTCITY, SAVARA IV, GREY MOON), polished (2026-10-21; it replaces
wave2_g.py's bomb_pickup(), letters inflated from the sprite glowing up to 1.2 on a backing and a squashed lathed
bomb). models.cfg: model bomb_pickup items/bomb_pickup.glb (unchanged) and sprite coins 89 bomb_pickup yaw=0 (no
spin, so that the word stays readable). One sprite, no animation; no other enemy shows it and it is no other sprite's
pixels mirrored or in other ramps.

As the sprite and its 4x upscale draw it: down its left side (columns 3-10, rows 2-26) the word BOMB in letters of
fire (ramp 7: shades 2-12, lightest at each letter's upper left, darkest at its lower right) in a dark red border
(shade 1, which also fills the letters' counters), one letter above the other, five pixels tall and six wide with a
row of border between them; the M's right stem a single pixel. To the right (columns 11-23, rows 2-24) a blue bomb
lying nose up the screen, its axis at column 17: a steel-blue nose (ramp 3, rows 2-9, 11 pixels across, rounding
off over its last three rows), a band glowing blue under it (ramp 9, rows 10-14, two pixels narrower, lightest on
its left), a ribbed collar (row 15), and the tail (rows 16-23): its cone, a fin either side out to columns 11 and 23
and one standing up the middle (seen edge on), the fins' ends notched at the bottom (rows 23-24).

Built as:

- the word: the sprite's own pixels as a pixel font, raised and clean: each letter's fire pixels a block LETTER_H
  high with its edges bevelled, its top painted pixel by pixel in the sprite's fire shades (five bands, lightest at
  the upper left), its sides darker; under them a plate of the border's pixels (the letters' outline, counters and
  all), PLATE_H thick, bevelled, dark red; all glowing in their own colours (emission well under 1: the bloom adds
  on top), the plate least. The word lies at about the height of the bomb's axis (its plate's underside at
  WORD_Z), so that the game's camera sees it and the bomb side by side as the sprite draws them;
- the bomb: a glossy steel-blue aerial bomb lying on its side, its axis along the screen's y at AXIS_X, AXIS_Z: an
  ogive nose with its fuze at the tip (a brass cap with a small arming vane), under it the band, a ring of blue
  glass glowing from inside, round across (lightest along its middle), between thin rims, then a knurled collar
  and the tail cone with its fins (left, right and up; a fin down would only show as a stick under the tail from
  the game's camera), their trailing ends notched as the sprite's, their edges bevelled; a seam round the nose; a
  little emission in the shell's own blue (rounded things read near black from the slanted camera).

Palette colours as the sprite's: ramp 7 for the word, ramp 3 for the bomb, ramp 9 for the band; brass is ramp 1's
tan, metallic.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the origin is
the sprite's centre (pixel 12, 14): column c is x = c + 0.5 - 12, row r is y = 13.5 - r. The model keeps the
sprite's place (it doesn't turn); it lies on z = 0, the nose's underside (the game centres items in height
anyway).

Replaces wave2_g.py's bomb_pickup() (its "coins 89: the bomb pick-up" section with the @model("bomb_pickup", "coins",
89, kind="items") registration) and the bomb_pickup entry of its docstring; wave2_g_art.py's BOMB (only
bomb_pickup() reads it).

Options after "--": --outdir <dir> (default assets/models/items), --check <sheets dir> (the silhouette against
coins.png), --preview <prefix>.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_item_kit as kit  # noqa: E402
from polish_item_kit import k  # noqa: E402

NAME, SPRITE = "bomb_pickup", 89

# The word's pixels: the sprite's columns 3-10 (WORD_COL...) of rows 2-26 (WORD_ROW...), palette indices in hex
# ("..": nothing; 71 the border, 72-7c the fire).
WORD_COL, WORD_ROW = 3, 2
WORD = """
.. 71 71 71 71 71 .. ..
71 7c 7b 7a 79 78 71 ..
71 7b 7a 71 71 77 76 71
71 7a 79 78 77 76 71 ..
71 79 78 71 71 75 73 71
71 78 77 76 75 73 71 ..
.. 71 71 71 71 71 .. ..
.. 71 7b 7a 79 78 71 ..
71 7b 7a 71 71 77 76 71
71 7a 79 71 71 76 75 71
71 79 78 71 71 75 73 71
.. 71 77 76 75 73 71 ..
.. 71 71 71 71 71 71 ..
71 7c 7b 71 .. 71 77 71
71 7b 7a 79 71 77 76 71
71 7a 79 71 77 71 75 71
71 79 78 71 71 71 73 71
71 78 77 71 .. 71 72 71
.. 71 71 71 71 71 71 ..
71 7c 7b 7a 79 78 71 ..
71 7b 7a 71 71 77 76 71
71 7a 79 78 77 76 71 ..
71 79 78 71 71 75 73 71
71 78 77 76 75 73 71 ..
.. 71 71 71 71 71 .. ..
"""
# The word's heights: the plate's underside and top, the letters' top; the bevels.
WORD_Z = 3.8
PLATE_H, LETTER_H = 0.8, 1.7
PLATE_BEVEL, LETTER_BEVEL = 0.3, 0.26
# The fire's bands: the sprite's shades (palette indices) each band takes, and the band's palette index and glow.
FIRE = [((0x7b, 0x7c), 0x7c, 0.5), ((0x79, 0x7a), 0x7a, 0.46), ((0x77, 0x78), 0x78, 0.42),
        ((0x75, 0x76), 0x76, 0.36), ((0x72, 0x73, 0x74), 0x74, 0.3)]
SIDE = (0x74, 0.26)                   # the letters' sides
BORDER = (0x71, 0.16)                 # the plate

# The bomb: its axis (x, z); its nose's profile along the axis (y, radius) from the band's top up, the fuze's, the
# band (y from, to, radius), the collar, the tail cone's; the fins (FIN_T thick) and their plan (distance out from
# the axis, y).
AXIS_X, AXIS_Z = 5.5, 5.35
NOSE = [(3.95, 4.35), (4.0, 5.05), (4.15, 5.3), (8.3, 5.3), (9.0, 5.02), (9.75, 4.3), (10.5, 3.45), (11.1, 2.6),
        (11.4, 2.1)]
FUZE = [(11.0, 2.15), (11.25, 2.15), (11.33, 1.9), (11.43, 1.9), (11.5, 2.0), (11.77, 1.95), (11.97, 1.7),
        (12.13, 1.25), (12.21, 0.6), (12.23, 0.0)]
NOSE_SEAM = 8.0                       # the seam round the nose (y)
BAND = (-1.0, 3.95, 4.3)
BAND_BULGE = 0.3                      # how much the band's edges sink under its middle
COLLAR = (-2.0, -1.0, 4.45, 12)       # y from, to, radius, ribs
TAIL = [(-2.05, 4.25), (-3.4, 3.95), (-5.4, 3.45), (-7.4, 2.95), (-9.0, 2.6), (-9.65, 2.4), (-9.85, 2.1), (-10.0, 1.8),
        (-10.35, 1.62), (-10.5, 1.2), (-10.5, 0.0)]
FIN_T = 0.5
FIN_PLAN = [(3.9, -2.2), (6.3, -3.4), (6.3, -9.9), (5.9, -10.55), (3.6, -10.55), (3.25, -9.75), (2.35, -9.7)]
VANE = (12.05, 1.9, 0.55, 0.12, 40.0)  # the fuze's arming vane: y, blade length, width, thickness, pitch (degrees)
SEGMENTS = 32


def materials():
    pal = k.level_palette()

    def glowing(name, index, strength, roughness=0.4, metallic=0.1):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness, emission=pal[index],
                          emission_strength=strength)
    mats = {"fire%d" % i: glowing("bomb_fire", index, glow, 0.35) for i, (_, index, glow) in enumerate(FIRE)}
    mats["side"] = glowing("bomb_fire_side", SIDE[0], SIDE[1], 0.45)
    mats["border"] = glowing("bomb_border", BORDER[0], BORDER[1], 0.5, 0.2)
    mats["shell"] = glowing("bomb_shell", 0x3c, 0.08, 0.2, 0.45)
    mats["shell_dark"] = k.material("bomb_shell_dark", palette=0x39, metallic=0.45, roughness=0.28)
    mats["band"] = k.material("bomb_band", palette=0x9b, metallic=0.0, roughness=0.08, emission=pal[0x9b],
                              emission_strength=0.38)
    mats["band_rim"] = glowing("bomb_band_rim", 0x95, 0.15, 0.3, 0.3)
    mats["brass"] = k.material("bomb_brass", palette=0x1b, metallic=0.85, roughness=0.25)
    return mats


# --- The word -------------------------------------------------------------------------------------------------------

def word_cells():
    """{(column, row): palette index} of the word's pixels (the sprite's columns and rows)."""
    cells = {}
    for r, line in enumerate(WORD.strip("\n").split("\n")):
        for c, code in enumerate(line.split()):
            if code != "..":
                cells[(WORD_COL + c, WORD_ROW + r)] = int(code, 16)
    return cells


def pixel_x(c):
    return c - 12.0


def pixel_y(r):
    return 14.0 - r


def blocks(name, cells, z0, z1, top_key, side_key, mats, bevel):
    """The cells as one block solid from z0 to z1: a box per pixel, the walls between neighbours left out and the
    corners shared (but not where two pixels touch only at a corner: there each keeps its own, so that the solid
    stays clean for the bevel); top_key(cell) names each top face's material, side_key the walls'; the edges
    bevelled."""
    bm = bmesh.new()
    verts = {}
    pinches = set()
    for (c, r) in cells:
        for dc, dr in ((1, 1), (1, -1)):
            if (c + dc, r + dr) in cells and (c + dc, r) not in cells and (c, r + dr) not in cells:
                pinches.add((c + max(dc, 0), r + max(dr, 0)))

    def v(cell, corner, z):
        cc, rr = corner
        key = (cc, rr, z, cell if corner in pinches else None)
        if key not in verts:
            verts[key] = bm.verts.new((pixel_x(cc), pixel_y(rr), z))
        return verts[key]

    order = []

    def slot(key):
        if key not in order:
            order.append(key)
        return order.index(key)
    for cell in sorted(cells):
        c, r = cell
        # The cell's corners (column, row of pixel edges): r is the top edge, r + 1 the bottom one.
        tl, tr, br, bl = (c, r), (c + 1, r), (c + 1, r + 1), (c, r + 1)
        bm.faces.new((v(cell, bl, z1), v(cell, br, z1), v(cell, tr, z1), v(cell, tl, z1))).material_index = slot(
            top_key(cell))
        bm.faces.new((v(cell, tl, z0), v(cell, tr, z0), v(cell, br, z0), v(cell, bl, z0))).material_index = slot(
            side_key)
        for (dc, dr), (a, b) in (((1, 0), (br, tr)), ((-1, 0), (tl, bl)), ((0, -1), (tr, tl)), ((0, 1), (bl, br))):
            if (c + dc, r + dr) in cells:
                continue
            bm.faces.new((v(cell, a, z0), v(cell, b, z0), v(cell, b, z1), v(cell, a, z1))).material_index = slot(
                side_key)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    # Flat runs of one material merged (the undersides, the plate's top, a letter's pixels of one band), to keep the
    # model light.
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(1.0), verts=bm.verts[:], edges=bm.edges[:],
                             delimit={"MATERIAL"})
    obj = kit.from_bmesh(name, bm)
    for key in order:
        obj.data.materials.append(mats[key])
    kit.bevel(obj, bevel, segments=2, angle=30.0)
    kit.weighted(obj, 35.0)
    return obj


def word(mats):
    cells = word_cells()
    fire = {cell: index for cell, index in cells.items() if index != 0x71}

    def band(cell):
        for i, (shades, _, _) in enumerate(FIRE):
            if fire[cell] in shades:
                return "fire%d" % i
        return "side"
    plate = blocks("word_plate", cells, WORD_Z, WORD_Z + PLATE_H, lambda cell: "border", "border", mats, PLATE_BEVEL)
    letters = blocks("word_letters", fire, WORD_Z + PLATE_H - 0.2, WORD_Z + PLATE_H + LETTER_H, band, "side", mats,
                     LETTER_BEVEL)
    return [plate, letters]


# --- The bomb -------------------------------------------------------------------------------------------------------

def point(theta, y, r):
    """The point at angle theta round the bomb's axis (radians, from +X towards +Z), y along it, r out from it."""
    return Vector((AXIS_X + r * math.cos(theta), y, AXIS_Z + r * math.sin(theta)))


def lathe(name, profile, mat, segments=SEGMENTS, cap=True):
    """A part turned round the bomb's axis: profile [(y, radius), ...]; a zero radius closes it to a point."""
    bm = bmesh.new()
    rings = []
    for y, r in profile:
        if r < 1e-6:
            rings.append([bm.verts.new(point(0.0, y, 0.0))])
        else:
            rings.append([bm.verts.new(point(2 * math.pi * j / segments, y, r)) for j in range(segments)])
    for a, b in zip(rings, rings[1:]):
        for j in range(segments):
            jj = (j + 1) % segments
            if len(a) == 1:
                bm.faces.new((a[0], b[jj], b[j]))
            elif len(b) == 1:
                bm.faces.new((a[j], a[jj], b[0]))
            else:
                bm.faces.new((a[j], a[jj], b[jj], b[j]))
    if cap and len(rings[0]) > 1:
        bm.faces.new(rings[0])
    if cap and len(rings[-1]) > 1:
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = kit.from_bmesh(name, bm, mat)
    return k.smooth(obj, 40.0)


def fin(name, theta, mats):
    """A fin standing out from the axis at angle theta: FIN_PLAN in (distance out, y), FIN_T thick, bevelled."""
    out = Vector((math.cos(theta), 0.0, math.sin(theta)))
    across = Vector((-math.sin(theta), 0.0, math.cos(theta)))
    centre = Vector((AXIS_X, 0.0, AXIS_Z))
    bm = bmesh.new()
    lo = [bm.verts.new(centre + out * d + Vector((0.0, y, 0.0)) - across * FIN_T / 2) for d, y in FIN_PLAN]
    hi = [bm.verts.new(centre + out * d + Vector((0.0, y, 0.0)) + across * FIN_T / 2) for d, y in FIN_PLAN]
    bm.faces.new(lo)
    bm.faces.new(hi)
    n = len(FIN_PLAN)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = kit.from_bmesh(name, bm, mats["shell"])
    kit.bevel(obj, 0.16, segments=2, angle=30.0)
    return kit.weighted(obj, 35.0)


def collar(mats):
    """The knurled collar between the band and the tail: a ring with COLLAR ribs round it."""
    y0, y1, r, ribs = COLLAR
    segments = ribs * 4
    bm = bmesh.new()
    ys = [y0 - 0.02, y0 + 0.12, y1 - 0.12, y1 + 0.02]
    rings = []
    for n, y in enumerate(ys):
        ring = []
        for j in range(segments):
            theta = 2 * math.pi * j / segments
            rib = 0.16 * max(0.0, math.cos(ribs * theta)) ** 2 if 0 < n < 3 else 0.0
            ring.append(bm.verts.new(point(theta, y, (r - 0.18 if n in (0, 3) else r) + rib)))
        rings.append(ring)
    for a, b in zip(rings, rings[1:]):
        for j in range(segments):
            jj = (j + 1) % segments
            bm.faces.new((a[j], a[jj], b[jj], b[j]))
    bm.faces.new(rings[0])
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = kit.from_bmesh("collar", bm, mats["shell_dark"])
    return k.smooth(obj, 50.0)


def vane(mats):
    """The fuze's arming vane: two small blades across the tip, twisted a little."""
    y, length, width, thick, twist_deg = VANE
    parts = []
    for side in (-1, 1):
        bm = bmesh.new()
        corners = []
        for u in (0.0, length):
            for w in (-width / 2, width / 2):
                twist = math.radians(twist_deg) * side
                d = Vector((side * u, 0.0, 0.0))
                off = Vector((0.0, w * math.sin(twist), w * math.cos(twist)))
                corners.append(d + off)
        box = []
        for c in corners:
            for t in (-thick / 2, thick / 2):
                box.append(c + Vector((0.0, t, 0.0)))
        vs = [bm.verts.new(Vector((AXIS_X, y, AXIS_Z)) + p) for p in box]
        # corners: (u0,w0),(u0,w1),(u1,w0),(u1,w1), each with t0,t1: indices 0..7
        quads = [(0, 2, 6, 4), (1, 5, 7, 3), (0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6)]
        for q in quads:
            bm.faces.new([vs[i] for i in q])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        parts.append(kit.flat_shade(kit.from_bmesh("vane%d" % side, bm, mats["brass"])))
    return parts


def bomb(mats):
    parts = [lathe("nose", NOSE, mats["shell"]), lathe("fuze", FUZE, mats["brass"])]
    y0, y1, r = BAND
    # Round across like a ring of glass: lightest along its middle, as the sprite's (rows 11-13 over 10 and 14).
    profile = [(y0 + (y1 - y0) * t, r - BAND_BULGE + BAND_BULGE * math.sin(math.pi * t) ** 0.6)
               for t in (0.0, 0.08, 0.2, 0.35, 0.5, 0.65, 0.8, 0.92, 1.0)]
    parts.append(lathe("band", profile, mats["band"], cap=False))
    for name, y in (("band_rim_top", y1 - 0.1), ("band_rim_bottom", y0 + 0.1)):
        parts.append(lathe(name, [(y - 0.13, r - 0.05), (y - 0.07, r + 0.06), (y + 0.07, r + 0.06), (y + 0.13, r - 0.05)],
                           mats["band_rim"], segments=SEGMENTS))
    parts.append(collar(mats))
    parts.append(lathe("tail", TAIL, mats["shell"]))
    for i, theta in enumerate((0.0, math.pi / 2, math.pi)):   # right, up, left (the fourth, down, would only show
        parts.append(fin("fin%d" % i, theta, mats))           # as a stick under the tail from the game's camera)
    # The seam where the nose cap meets the body.
    y = NOSE_SEAM
    parts.append(lathe("nose_seam", [(y - 0.12, 5.22), (y - 0.06, 5.34), (y + 0.06, 5.34), (y + 0.12, 5.22)],
                       mats["shell_dark"]))
    parts += vane(mats)
    return parts


def triangulate(obj):
    """Splits the faces into triangles here, the same way every run (the exporter's split of the word's long merged
    faces otherwise depends on what was rendered before: --check gave other triangles)."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="FIXED", ngon_method="EAR_CLIP")
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


def build():
    opts = kit.options()
    k.reset()
    mats = materials()
    parts = word(mats) + bomb(mats)
    for obj in parts:
        kit.drop_unused_materials(obj)
        triangulate(obj)
    bpy.context.view_layer.update()
    if "stats" in opts:
        for obj in sorted(parts, key=lambda o: -kit.triangles([o]))[:8]:
            print("    %s: %d triangles" % (obj.name, kit.triangles([obj])))
    kit.finish(opts, NAME, parts, SPRITE, large=True, distance=0.8)


if __name__ == "__main__":
    build()
