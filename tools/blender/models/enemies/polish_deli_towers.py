"""DELI's two ground towers (sheet U, written u in models.cfg) and their damaged looks: DELI and New Deli (enemies
245-258 of episodes 1 and 3, ground layer) and VAULT (episode 6: the turret, u 79, on its own: enemies 1582, 1588, 1589
and 1592). Polished (2026-10-22; it replaces wave3_ag_tower.py: reliefs raised pixel by pixel under a hull's curve and
painted pixel by pixel, spires lathed lying nearly flat, the turret on a slab of the map's floor). models.cfg (model
lines as before): model deli_tower_<sprite> enemies/deli_tower_<sprite>.glb origin for 1 3 5 39 41 43 79 15 17 19 38 53
55 7 9 11 127 77; sprite u <sprite> deli_tower_<sprite> yaw=0 height=-4 (height=-4 is new: the housing stands on the
floor; without it every piece floats 4 pixels over it).

Where the levels put them (DELIANI 1:19 and New Deli 3:23 have the same events; tools/content/tyrevents.py): tower A
(t3072 link 29, t3772 link 38): 245 246 247 (u 1 3 5) at x, x + 24, x + 48, 84 pixels up; 248 249 250 (u 39 41 43) 56
up; 251 (u 79) at x + 24, 28 up: one 72 x 84 picture, the turret under its middle column. Tower B (t3548 link 35, t3800
link 39): 253 254 (u 15 17) at x, x + 24, 84 up and 256 257 (u 53 55) 56 up, 258 (u 79) under 53, and two 1x1 pieces for
its bow, 252 (u 19) at x - 18, 78 up and 255 (u 38) at x - 18, 64 up (the small enemies' adjustment is off by then): in
tower A's frame tower B is its columns 12-72, u 19 and u 38 its columns 12-24 of rows 13-27 and 27-41. Every 2x2 piece
lands on the ground map's tile grid, the turret always on tile 591 (in DELIANI, New Deli and all six VAULT placements):
the turret's burnt-out housing painted on the floor (u 77 is nearly that picture). u 79's ramp-6 pixels round the
housing are that floor: the map's, left out (the silhouettes are checked without them).

The damaged looks (enemy data: dlevel 15, linked: when one piece is down to 15 armour, all its tower's pieces switch at
once): u 1, 3, 5 switch to u 7, 9, 11 (the spires snapped to scorched stumps, embers glowing in two cracks), u 15 and 17
to u 9 and 11 too (tower B's spires are tower A's: u 15 = u 3 and u 17 = u 5 in their rows 0-19), u 43 and u 55 to u 127
(the capsule shot away; its pixels are nearer 43's), u 79 to u 77 (the housing burnt out, an ember cross on it); u 39,
41, 38 and 53 play burning animations instead (dani 11: their first sprite stays, so do their models; no frame models
are made for the fire). u 19 (1x1) switches to u 7, whose 1x1 cell is blank: in 2D tower B's bow top vanishes; the
renderer keys models by sheet and sprite only, so in 3D it shows deli_tower_7 at its own centre, 6 pixels right of and 6
below tower A's corner: a burnt stump and a few scraps on the bow. No sprite of any sheet is these mirrored or turned; u
81 (u 79 with a red vent) is shown by no enemy. The capsules (250, 257) launch enemy 556 (C 19, deli_shell) every 50
ticks.

The layout (the family's: polish_red_tower.py, polish_ball_mast.py): the sprites draw the towers from the side, a turret
housing on the floor, a mast rising from it to a long hull lying across the screen, spires standing on the hull. Each
tower is built upright (x right, y back: its front, which the game's camera sees, towards -y; z up the mast) and leaned
back up the screen LEAN (70 degrees) from upright about its foot (FOOT: where the housing meets the floor under the
picture's row FOOT_ROW, 80), so that the camera, 20 degrees from straight down, sees it face on, as the sprites draw it:
a point h up the mast shows h / cos 20 rows up the picture from the foot whatever its depth, so the picture's row r is
the height H(r) = (FOOT_ROW - r) cos 20. The crystal's tip is 26 pixels over the floor, the hull's top 23, the
housing's 9.4. Seen from straight above everything lies nearer the foot than its sprite (12 percent of its height up
the picture: 9 pixels at the spires' tips), the cost of the lean in the top view; the game's camera sees every part
where its sprite is. The back halves near the foot, under the floor, are cut away (FLOOR_CUT, closed). The camera's
planes of sight through the sprites' edges are square to the leaned mast, so the pieces are cut along those planes and
the columns' (cut_planes: the faces' winding kept, every cut capped in the inside's dark grey 0x03), each piece moved so
that its sprite's centre is its origin: each holds what its sprite draws, 6 to 22 pixels below its origin.

As the sprites and their 4x upscales draw them (columns c and rows r of the 72 x 84 picture, pixel edges):
- The turret (u 79, both towers and VAULT; columns 24-48 of rows 60-80): a dark rounded housing whose bottom left rounds
  in towards the floor, a red plate standing off its left (columns 25-28 of rows 62-72), a lit grey bar beside it, the
  red collar where the mast comes in (columns 31-35 of rows 58-63), a purple vent with two red slats on its front right
  (columns 35-42 of rows 64-71), three small red lamps under the vent (row 73, glowing faintly), a lit edge down its
  right side; u 77: the plate, the collar and the edge greyed, the vent a dark hollow in a broken frame, a lit ledge
  where the lamps were, an ember cross over the vent.
- The mast (rows 45-61): a dark socket under the hull (columns 28-45 of rows 45-49, a grey band across its front), a
  narrow grey shaft (columns 32-35) on a dark backing, a purple plate on its left (columns 30-32 of rows 49-54), a
  purple pipe down its right (column 36) into the housing, a small red box beside it (columns 37-41 of rows 49-53), a
  lit collar at its foot (rows 55-57).
- Tower B's hull (columns 13-56 of rows 25-45): a smooth grey fuselage lying across the screen, lofted through
  superellipse sections (B_HULL), lit along its top, its nose at the left drooping (its underside curving up to the tip
  at rows 29-35), a red bump on the bow's top (columns 16-20), five red gill ribs in a dark recess on its lower front
  (columns 21-29), a box under its middle (columns 33-44 of rows 35-45) with a red hatch in its front (columns 36-42);
  under the stern and the capsule a bracket (columns 50-58 of rows 45-48, both towers).
- Tower A's hull (columns 7-56 of rows 25-48): the same fuselage stripped of its shell, longer to the left and open
  there: a dark core (CORE, half as deep as the shell) carrying the framework, A_PLATES: rectangles of the sprites'
  colour classes read off u 1, 39, 41 and 43 (purple skin plates, red machinery, light and mid grey girders, brown
  machinery; isolated pixels joined to their surroundings, each class's regions covered by greedy rectangles, single
  pixels left to the core), each a block lying on the core's front and standing proud of it by its class's LIFT (1 to
  3.3 pixels), bevelled, its lit faces a shade lighter; the darks between them are the core. Dark backings carry the red
  post at the open end and the red box left of S5, which stand above the core.
- The capsule (columns 54-71 of rows 29-45): a pill lying across the screen, its right end rounded and its bottom
  sloping up to it, an oval lens in its front (columns 55-66 of rows 32-39, in a dark bezel: purple 0x59 in tower A, red
  0x48 in tower B, glowing 0.22) with a bright bead (column 61, row 35; 0x5d / 0x4c, 0.4), a lit band under it. u 127:
  the capsule's lower half left as a crumpled, burnt wreck with a ragged top, a broken stub where it was fixed, embers
  at its root, the hull's end burnt.
- The spires (rows 0-28, the same in both towers; columns 2-3 of each spire's dark outline included): S1 (columns 29-34
  of rows 4-25), a grey column with a rounded lit cap, a red window on its front, its foot red and narrower; S3 (columns
  35-39 of rows 14-20), a red stub; S2 (columns 39-47), the tallest: a faceted purple crystal (rows 0-10) on a grey
  band, a red rail at its right (rows 5-12), a red body under them (rows 12-19) and its foot grey on the left; S4
  (columns 46-56 of rows 12-28), a grey cabin, its upper block domed, its lower block wider with a red window (columns
  50-53 of rows 22-28); S5 (columns 19-25 of rows 19-28), a small post with a grey cap and a red foot; a grey cross
  piece (columns 33-39 of rows 20-24) and a dark box (columns 26-29 of rows 20-25) among their feet. u 7, 9, 11: S1, S2
  and the cabin's lower block snapped off raggedly (their breaks charred, crumpled, sooted), S3, S5, the cross piece and
  the box standing, the crystal, its band and rail and the cabin's upper block gone, everything burnt (reds and purples
  greyed to shades of their brightness: BURN), embers glowing in a crack down S3's foot and a cross on the cabin.

Parts are CAD-like solids: rounded boxes, columns of rounded-square sections, bodies lofted through sections, plates
lying on curved surfaces (polish_red_tower.patch's kind), painted as the sprites shade them (lit faces a shade lighter,
undersides darker). Greys (metallic 0.5, roughness 0.32) 0x01-0x0d; reds (0.3, 0.38) 0x42-0x4c; purples (0.3, 0.35)
0x54-0x5d; browns 0x13; glowing (emission well under 1): the lenses 0.22, their beads 0.4, the housing's lamps 0x48
0.18, the embers 0x74 0.35 and 0x77 0.5. At most 15 materials a model (limit_materials: the least used plain ones give
their faces to the nearest shade of their ramp). Every mesh is triangulated before the export
(polish_k_pod.triangulate): the output is the same with and without --check.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the floor (z = 0); the whole's
origin is the middle of the 72 x 84 picture: column c is x = c - 36 at its left edge, the picture's row r is y = 42 - r
on the floor at its top edge; the pieces' centres: u 1 / 7 (-24, 28), 3 / 9 / 15 (0, 28), 5 / 11 / 17 (24, 28), 39 (-24,
0), 41 / 53 (0, 0), 43 / 55 / 127 (24, 0), 79 / 77 (0, -28), 19 (-18, 22), 38 (-18, 8).

Replaces wave3_ag_tower.py: delete it (it builds nothing else; nothing imports it) and wave3_ag_art.py (TOWER_A,
TOWER_B, TOWER_A_DMG: only wave3_ag_tower.py reads them), and take wave3_ag_kit.py's frame() and its import of
wave3_ag_art out (wave3_ag_kit.py stays: wave3_ak_kit, wave3_an_kit and wave3_ap_kit import it). Also wave2_g.py's
deli_tower_tl (u 1's old corner: no sprite line uses it since round 18) with rounded_rect(), wave2_g_art.py's U_TOWER
(read by nothing), the model line deli_tower_tl and its GLB.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each piece's and each tower's
silhouette as the game's camera sees it against the sprites' own pixels in enemy_U.png, the floor left out), --preview
<prefix>, --only <name,...>, --towers <a,b,a_dmg> (which wholes to build), --whole <prefix> (the leaned uncut towers as
<prefix>a.glb, b.glb, a_dmg.glb), --stats 1.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector, noise
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
import polish_deli_boss as db  # noqa: E402  (drop_unused, join)

# --- The layout ---------------------------------------------------------------------------------------------------
CAMERA = math.radians(20.0)
C20, S20, T20 = math.cos(CAMERA), math.sin(CAMERA), math.tan(CAMERA)
VIEW = Vector((0.0, S20, -C20))               # the camera's line of sight (world)
LEAN = math.radians(70.0)
FOOT_ROW = 80.0
FOOT = Vector((0.0, 42.0 - FOOT_ROW, 0.0))
TO_WORLD = Matrix.Translation(FOOT) @ Matrix.Rotation(-LEAN, 4, "X")
LIGHT = (TO_WORLD.to_3x3().inverted() @ Vector((-0.6, 0.6, 1.0))).normalized()   # towards the sun, upright
FLOOR_CUT = -0.8


def H(row):
    """The height up the upright mast that the camera shows at the picture's row (a pixel edge)."""
    return (FOOT_ROW - row) * C20


def ROW(h):
    return FOOT_ROW - h / C20


def X(col):
    return col - 36.0


def U(col, row, y=0.0):
    """A point of the upright frame at the picture's column and row (pixel edges), y back."""
    return Vector((X(col), y, H(row)))


# --- Materials ------------------------------------------------------------------------------------------------------

def materials():
    pal = k.level_palette()
    cache = {}

    def mat(index, metallic, roughness, glow=0.0, tag=""):
        key = (index, glow, tag)
        if key not in cache:
            name = "dtow_%02x%s%s" % (index, tag, "glow" if glow > 0 else "")
            if glow > 0:
                cache[key] = k.material(name, palette=index, metallic=0.0, roughness=roughness, emission=pal[index],
                                        emission_strength=glow)
            else:
                cache[key] = k.material(name, palette=index, metallic=metallic, roughness=roughness)
        return cache[key]
    m = {}
    for s in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13):
        m["g%x" % s] = mat(s, 0.5 if s > 3 else 0.35, 0.32 if s > 3 else 0.55)
    for s in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12):
        m["r%x" % s] = mat(0x40 | s, 0.3, 0.38)
    for s in (2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13):
        m["p%x" % s] = mat(0x50 | s, 0.3, 0.35)
    m["b3"] = mat(0x13, 0.2, 0.55)
    m["b1"] = mat(0x11, 0.2, 0.6)
    m["d2"] = mat(0xa2, 0.2, 0.6)
    m["lens_p"] = mat(0x59, 0.0, 0.18, glow=0.22)
    m["bead_p"] = mat(0x5d, 0.0, 0.15, glow=0.4)
    m["lens_r"] = mat(0x48, 0.0, 0.18, glow=0.22)
    m["bead_r"] = mat(0x4c, 0.0, 0.15, glow=0.4)
    m["lamp"] = mat(0x48, 0.0, 0.3, glow=0.18)
    m["ember"] = mat(0x74, 0.0, 0.5, glow=0.35)
    m["ember_hot"] = mat(0x77, 0.0, 0.5, glow=0.5)
    m["char"] = mat(0x01, 0.1, 0.85, tag="c")
    m["cap"] = m["g3"]                          # the inside, on every cut
    return m


# --- Builders (upright frame) ---------------------------------------------------------------------------------------

def link(name, mesh, mat=None):
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    if mat is not None:
        obj.data.materials.append(mat)
    return obj


def sq_point(a, power):
    return mk.superellipse_point(a, power)


def rings_loft(name, rings, mat, caps=(True, True), start=None, end=None, smooth=35.0):
    obj = k.loft(name, rings, mat, cap_start=caps[0], cap_end=caps[1], start_point=start, end_point=end)
    if smooth:
        k.smooth(obj, smooth)
    return obj


def post(name, sections, mat, segments=24, power=3.0, caps=(True, True), smooth=40.0):
    """A body standing up the mast: sections [(row, x centre, y centre, half width, half depth)] from its foot up
    (rounded-square rings, power 2 round, larger squarer); the ends closed flat."""
    unit = [sq_point(2 * math.pi * (j + 0.5) / segments, power) for j in range(segments)]
    rings = []
    for row, xc, yc, hw, hd in sections:
        h = H(row)
        rings.append([Vector((xc + hw * u, yc - hd * v, h)) for u, v in unit])
    first, last = sections[0], sections[-1]
    return rings_loft(name, rings, mat, caps, Vector((first[1], first[2], H(first[0]))),
                      Vector((last[1], last[2], H(last[0]))), smooth)


def along_x(name, sections, mat, segments=28, power=2.0, caps=(True, True), smooth=35.0, tips=(None, None)):
    """A body lying along x: sections [(x, z centre, y centre, half height, half depth)] from left to right."""
    unit = [sq_point(2 * math.pi * (j + 0.5) / segments, power) for j in range(segments)]
    rings = []
    for x, zc, yc, hz, hd in sections:
        rings.append([Vector((x, yc + hd * u, zc + hz * v)) for u, v in unit])
    first, last = sections[0], sections[-1]
    start = tips[0] if tips[0] is not None else Vector((first[0], first[2], first[1]))
    end = tips[1] if tips[1] is not None else Vector((last[0], last[2], last[1]))
    return rings_loft(name, rings, mat, caps, start, end, smooth)


def rbox(name, c0, c1, r0, r1, y0, y1, mat, bevel=0.0, segments=2):
    """A box in the upright frame: columns c0-c1, rows r0-r1 (pixel edges), depth y0 (front) to y1."""
    obj = mk.box(name, X(c0), X(c1), y0, y1, H(r1), H(r0), mat)
    if bevel > 0:
        mk.bevel(obj, bevel, segments, 35)
    mk.shade(obj, 35)
    return obj


def plate(name, surf, nu, nv, lift, depth, mats, axis_of, paint_outer=None):
    """A plate lying on a surface (polish_red_tower.patch, its outward direction axis_of(point) given): surf(u, v) the
    surface's point for u, v in 0..1 (nu x nv cells); its outer face lift above the surface, its inner face depth below
    it, side walls round its border; mats (outer, inner, side)."""
    eps = 1e-3
    grid_o, grid_i = [], []
    for i in range(nu + 1):
        for j in range(nv + 1):
            u, v = i / nu, j / nv
            p = surf(u, v)
            du = surf(min(u + eps, 1.0), v) - surf(max(u - eps, 0.0), v)
            dv = surf(u, min(v + eps, 1.0)) - surf(u, max(v - eps, 0.0))
            n = du.cross(dv)
            out = axis_of(p)
            if n.length < 1e-9:
                n = out.copy()
            n.normalize()
            if n.dot(out) < 0:
                n = -n
            grid_o.append(p + n * lift)
            grid_i.append(p - n * depth)
    verts = grid_o + grid_i
    off = len(grid_o)

    def idx(i, j):
        return i * (nv + 1) + j
    faces, roles = [], []
    for i in range(nu):
        for j in range(nv):
            a, b, c, d = idx(i, j), idx(i + 1, j), idx(i + 1, j + 1), idx(i, j + 1)
            faces.append((a, b, c, d))
            roles.append(0)
            faces.append((d + off, c + off, b + off, a + off))
            roles.append(1)
    border = []
    for i in range(nu):
        border.append((idx(i, 0), idx(i + 1, 0)))
    for j in range(nv):
        border.append((idx(nu, j), idx(nu, j + 1)))
    for i in range(nu, 0, -1):
        border.append((idx(i, nv), idx(i - 1, nv)))
    for j in range(nv, 0, -1):
        border.append((idx(0, j), idx(0, j - 1)))
    for a, b in border:
        faces.append((b, a, a + off, b + off))
        roles.append(2)
    obj = k.mesh_object(name, verts, faces)
    for mat in mats:
        obj.data.materials.append(mat)
    for poly, role in zip(obj.data.polygons, roles):
        poly.material_index = role
    k.recalc_normals(obj)
    if paint_outer is not None:
        for poly, role in zip(obj.data.polygons, roles):
            if role == 0:
                mat = paint_outer(poly.center, poly.normal)
                if mat is not None:
                    poly.material_index = mk.slot_of(obj, mat)
    return obj


def paint_lit(obj, base, lit=None, dark=None, under=None, lit_at=0.78, dark_at=-0.1, under_at=-0.55):
    """Paints faces by how they face the sun and the floor: lit (facing the sun), base, dark (turned away), under
    (facing down the mast)."""
    def pick(c, n):
        if under is not None and n.z < under_at:
            return under
        d = n.dot(LIGHT)
        if lit is not None and d > lit_at:
            return lit
        if dark is not None and d < dark_at:
            return dark
        return base
    mk.paint(obj, pick)
    return obj


def by_rows(obj, spec, keep=None):
    """Paints faces by the picture's row of their centre: spec [(row from, row to, material)] (first match wins);
    keep(centre, normal) True leaves a face as it is."""
    def pick(c, n):
        if keep is not None and keep(c, n):
            return None
        row = ROW(c.z)
        for r0, r1, mat in spec:
            if r0 <= row < r1:
                return mat
        return None
    mk.paint(obj, pick)
    return obj


def lathe_on_axis(name, prof, centre, axis, mat, segments=16, smooth=50.0):
    """A small part turned about an arbitrary axis: prof [(t along the axis, radius)]."""
    axis = Vector(axis).normalized()
    ref = Vector((1.0, 0.0, 0.0)) if abs(axis.x) < 0.9 else Vector((0.0, 1.0, 0.0))
    u = axis.cross(ref).normalized()
    w = axis.cross(u).normalized()
    rings = []
    for t, r in prof:
        c = Vector(centre) + axis * t
        rings.append([c + (u * math.cos(2 * math.pi * j / segments) + w * math.sin(2 * math.pi * j / segments)) * r
                      for j in range(segments)])
    obj = k.loft(name, rings, mat, start_point=Vector(centre) + axis * prof[0][0],
                 end_point=Vector(centre) + axis * prof[-1][0])
    if smooth:
        k.smooth(obj, smooth)
    return obj


def lerp_table(table, x, i):
    """Column i of a table [(x, ...)] at x (linear between rows, clamped)."""
    if x <= table[0][0]:
        return table[0][i]
    for a, b in zip(table, table[1:]):
        if a[0] <= x <= b[0]:
            t = (x - a[0]) / max(b[0] - a[0], 1e-9)
            return a[i] + (b[i] - a[i]) * t
    return table[-1][i]


class Shape:
    """A body lying along x through sections of a table [(column, top row, bottom row)], its depth a share of its
    half height (at most max_depth), its sections superellipses of the given power about y = yc."""

    def __init__(self, table, depth=0.85, max_depth=8.4, power=2.2, yc=0.0):
        self.table, self.depth, self.max_depth, self.power, self.yc = table, depth, max_depth, power, yc

    def section(self, col):
        top, bottom = H(lerp_table(self.table, col, 1)), H(lerp_table(self.table, col, 2))
        zc, hz = (top + bottom) / 2, (top - bottom) / 2
        return zc, hz, min(self.depth * hz, self.max_depth)

    def front(self, col, row, out=0.0):
        """The point of its front at the picture's column and row (out: that far out of the surface, along the
        direction from its axis)."""
        zc, hz, hd = self.section(col)
        v = max(-0.999, min(0.999, (H(row) - zc) / hz))
        f = (1.0 - abs(v) ** self.power) ** (1.0 / self.power)
        p = Vector((X(col), self.yc - hd * f, H(row)))
        if out:
            p += self.outward(p) * out
        return p

    def outward(self, p):
        zc, hz, hd = self.section(p.x + 36.0)
        d = Vector((0.0, (p.y - self.yc) / max(hd, 1e-6) ** 2, (p.z - zc) / max(hz, 1e-6) ** 2))
        return d.normalized() if d.length > 1e-9 else Vector((0.0, -1.0, 0.0))

    def body(self, name, mat, cols, segments=36, tips=(None, None), smooth=35.0, inset=0.0):
        sections = []
        for c in cols:
            zc, hz, hd = self.section(c)
            sections.append((X(c), zc, self.yc, max(0.2, hz - inset), max(0.2, hd - inset)))
        return along_x(name, sections, mat, segments, self.power, smooth=smooth, tips=tips)


# --- The turret and the mast (both towers) --------------------------------------------------------------------------
# The housing: rings up the mast [(row, left column, right column, front depth)], its back BACK deep.
HOUSING = [(79.8, 35.0, 43.0, 0.9), (79.0, 34.0, 44.4, 1.6), (78.0, 33.0, 45.6, 2.5), (77.0, 30.8, 46.4, 3.3),
           (76.0, 28.6, 46.8, 3.9), (75.0, 26.6, 47.2, 4.3), (74.0, 24.8, 47.4, 4.5), (72.0, 24.1, 47.8, 4.6),
           (70.0, 24.0, 48.0, 4.6), (68.0, 24.0, 47.6, 4.6), (66.0, 24.0, 46.6, 4.6), (64.0, 24.0, 46.0, 4.5),
           (63.0, 24.3, 45.4, 4.2), (62.0, 25.2, 44.6, 3.6), (61.0, 26.6, 43.2, 2.8), (60.4, 29.2, 41.6, 1.8)]
HOUSING_BACK = 5.0


def housing_front(col, row, out=0.0):
    """The housing's front at the picture's column and row."""
    xl, xr, df = (lerp_table(sorted(HOUSING), row, i) for i in (1, 2, 3))
    xc, hw = (X(xl) + X(xr)) / 2, (xr - xl) / 2
    yc, hd = (HOUSING_BACK - df) / 2, (HOUSING_BACK + df) / 2
    u = max(-0.999, min(0.999, (X(col) - xc) / hw))
    f = (1.0 - abs(u) ** 3.0) ** (1.0 / 3.0)
    return Vector((X(col), yc - hd * f - out, H(row)))


def housing(m, burnt=False):
    """The turret's housing on the floor (u 79): a dark rounded body, the red plate on its left, the lit bar beside it,
    the red collar where the mast comes in, the purple vent with its red slats, the lamps, the lit edge down its right.
    burnt (u 77): the plate, the collar and the edge greyed and sooted, the vent and lamps gone, an ember cross."""
    sections = []
    for row, xl, xr, df in HOUSING:
        sections.append((row, (X(xl) + X(xr)) / 2, (HOUSING_BACK - df) / 2, (xr - xl) / 2, (HOUSING_BACK + df) / 2))
    body = post("housing", sections, m["g3"], segments=36, power=3.0, caps=(True, True), smooth=40.0)
    paint_lit(body, m["g2"], lit=m["g4"] if not burnt else m["g3"], dark=m["g2"], under=m["g1"], lit_at=0.72)
    parts = [body]
    red_lo, red, red_hi = (m["g4"], m["g5"], m["g7"]) if burnt else (m["r3"], m["r6"], m["r9"])
    pl = rbox("housing_plate", 25.0, 28.0, 62.0, 72.0, -4.2, 1.5, red, bevel=0.35)
    paint_lit(pl, red, lit=red_hi, under=red_lo, lit_at=0.6)
    bar = rbox("housing_bar", 29.0, 31.0, 63.0, 67.4, -5.0, 0.0, m["g8"] if not burnt else m["g6"], bevel=0.3)
    paint_lit(bar, m["g8"] if not burnt else m["g6"], lit=m["gb"] if not burnt else m["g8"], under=m["g4"], lit_at=0.6)
    collar = rbox("housing_collar", 31.0, 35.0, 58.0, 63.0, -3.7, 2.4, red, bevel=0.35)
    by_rows(collar, [(57.0, 60.6, red_hi), (60.6, 62.0, red), (62.0, 64.0, m["b3"] if not burnt else m["g3"])])
    edge = rbox("housing_edge", 43.6, 45.7, 64.0, 74.0, -3.3, 0.5, m["g6"] if not burnt else m["g4"], bevel=0.3)
    paint_lit(edge, m["g6"] if not burnt else m["g4"], lit=m["g7"] if not burnt else m["g5"], under=m["g3"])
    parts += [pl, bar, collar, edge]
    if not burnt:
        vent = rbox("housing_vent", 35.0, 42.0, 64.6, 71.0, -5.3, 0.0, m["p9"], bevel=0.35)
        by_rows(vent, [(64.0, 65.6, m["pb"]), (65.6, 69.0, m["p9"]), (69.0, 72.0, m["p4"])])
        parts.append(vent)
        for i, c in enumerate((36.1, 39.1)):
            slat = rbox("housing_slat%d" % i, c, c + 0.9, 65.6, 69.2, -5.65, -4.8, m["r8"], bevel=0.15)
            by_rows(slat, [(65.0, 66.6, m["rb"]), (66.6, 70.0, m["r8"])])
            foot = rbox("housing_slat_foot%d" % i, c, c + 0.9, 69.2, 71.0, -5.5, -4.8, m["b3"])
            parts += [slat, foot]
        for i, c in enumerate((35.5, 37.5, 39.5)):
            p = housing_front(c, 73.5)
            parts.append(lathe_on_axis("housing_lamp%d" % i, [(-0.4, 0.62), (0.15, 0.6), (0.4, 0.42), (0.52, 0.0)], p,
                                       (0.0, -1.0, 0.0), m["lamp"], 12))
    else:
        # The vent's place: a dark hollow behind a broken frame; soot over the body; the ember cross.
        hollow = rbox("housing_hollow", 35.2, 41.8, 64.8, 71.0, -4.9, 0.0, m["g2"], bevel=0.3)
        parts.append(hollow)
        for i, (c0, c1, r0, r1) in enumerate(((35.0, 42.0, 64.6, 65.4), (35.0, 35.8, 64.6, 70.6),
                                             (40.4, 42.0, 66.2, 71.0))):
            parts.append(rbox("housing_frame%d" % i, c0, c1, r0, r1, -5.0, -3.0, m["g4"], bevel=0.12))
        ledge = rbox("housing_ledge", 31.0, 44.2, 72.0, 73.8, -4.9, 0.0, m["g5"], bevel=0.3)
        paint_lit(ledge, m["g5"], lit=m["g9"], under=m["g3"], lit_at=0.55)
        parts.append(ledge)
        parts += embers(m, "housing_ember", 37.5, 63.5, 2.6, 3.3, lambda c, r: housing_front(c, r, 0.05))
    return parts


def embers(m, name, col, row, half_w, half_h, front, width=0.55):
    """A glowing cross of cracks on a surface (the damaged looks' dark red crosses): two thin glowing bars, a hot
    core where they cross."""
    out = []
    for i, (c0, c1, r0, r1) in enumerate(((col - half_w, col + half_w, row - width / 2, row + width / 2),
                                         (col - width / 2, col + width / 2, row - half_h, row + half_h))):
        def surf(u, v, c0=c0, c1=c1, r0=r0, r1=r1):
            return front(c0 + (c1 - c0) * u, r0 + (r1 - r0) * v)
        out.append(plate("%s%d" % (name, i), surf, 4, 4, 0.12, 0.3, (m["ember"], m["g1"], m["g1"]),
                         lambda p: Vector((0.0, -1.0, 0.0))))
    core = front(col, row)
    out.append(lathe_on_axis(name + "_core", [(-0.2, 0.55), (0.1, 0.5), (0.25, 0.0)], core, (0.0, -1.0, 0.0),
                             m["ember_hot"], 10))
    return out


def mast(m, burnt=False):
    """The mast from the hull down into the housing: the socket under the hull, the shaft, the purple plate, the pipe,
    the red box, the collar at its foot."""
    parts = []
    socket = rbox("mast_socket", 28.0, 45.0, 45.0, 49.3, -4.3, 3.0, m["g3"], bevel=0.35)
    by_rows(socket, [(45.6, 47.8, m["g5"] if not burnt else m["g4"])], keep=lambda c, n: n.y > -0.7)
    shaft = post("mast_shaft", [(62.0, X(33.5), 0.0, 1.7, 1.8), (48.5, X(33.5), 0.0, 1.7, 1.8)], m["g5"], 16, 3.0)
    paint_lit(shaft, m["g4"], lit=m["g7"] if not burnt else m["g5"], dark=m["g3"], lit_at=0.55)
    purple_lo, purple, purple_hi = (m["g3"], m["g4"], m["g6"]) if burnt else (m["p5"], m["p6"], m["p8"])
    plate_ = rbox("mast_plate", 29.8, 32.0, 49.0, 54.6, -2.4, 0.5, purple, bevel=0.25)
    paint_lit(plate_, purple, lit=purple_hi, under=purple_lo, lit_at=0.6)
    pipe = k.smooth(mk.tube("mast_pipe", [U(36.5, 62.2, -1.25), U(36.5, 46.6, -1.25)], 0.55,
                            m["p8"] if not burnt else m["g5"], 10), 50)
    box = rbox("mast_box", 37.0, 41.0, 49.0, 53.0, -2.9, 0.8, m["r8"] if not burnt else m["g4"], bevel=0.25)
    by_rows(box, [(48.0, 50.1, m["g4"])])
    collar = rbox("mast_collar", 28.6, 34.4, 55.0, 57.0, -2.7, 2.7, m["g6"], bevel=0.3)
    paint_lit(collar, m["g6"], lit=m["g9"] if not burnt else m["g6"], under=m["g3"], lit_at=0.5)
    back = [rbox("mast_back", 29.8, 41.9, 48.6, 53.7, -1.2, 2.5, m["g2"], bevel=0.3),
            rbox("mast_back2", 31.4, 38.4, 53.4, 56.0, -1.2, 2.5, m["g2"], bevel=0.3),
            rbox("mast_foot", 29.6, 40.4, 55.6, 61.2, -2.2, 2.6, m["g2"], bevel=0.4)]
    parts += [socket, shaft, plate_, pipe, box, collar] + back
    return parts


# --- Tower B's hull and the capsule -----------------------------------------------------------------------------------
B_HULL = [(13.0, 29.5, 34.4), (13.5, 28.8, 35.2), (14.0, 28.4, 35.7), (15.0, 28.0, 36.4), (16.0, 27.6, 37.1),
          (17.0, 27.0, 37.7), (18.0, 26.5, 38.3), (19.0, 26.1, 38.9), (20.0, 25.7, 39.4), (22.0, 25.2, 40.3),
          (24.0, 25.0, 41.1), (27.0, 25.0, 42.3), (30.0, 25.0, 43.3), (33.0, 25.0, 43.9), (36.0, 25.0, 44.3),
          (44.0, 25.0, 44.6), (52.0, 25.0, 45.0), (54.0, 25.3, 44.6), (55.5, 25.8, 43.8), (56.5, 26.5, 42.8)]
B_TIP = (12.55, 32.0)
SHELL = Shape(B_HULL)
GILLS = [21.6, 23.3, 25.0, 26.7, 28.4]         # the red gill ribs (columns of their tops), slanting left downwards
GILL_ROWS = (33.6, 0.12)                       # their tops' row; how far they lean left per row down


def shell_paint(m, obj, sooted=False):
    """The shut hull's greys by how its faces turn: lit along the top, the front mid grey, darker under."""
    g = (lambda key: m[{"gc": "g9", "ga": "g8", "g8": "g6", "g6": "g5", "g4": "g3", "g2": "g2"}[key]]) if sooted else \
        (lambda key: m[key])

    def pick(c, n):
        d = n.dot(LIGHT)
        if n.z < -0.72:
            return g("g2")
        if n.z < -0.35:
            return g("g4")
        if d > 0.9:
            return g("gc")
        if n.z > 0.55:
            return g("ga")
        if n.z < -0.05:
            return g("g6")
        return g("g8")
    mk.paint(obj, pick)
    return obj


def hull_shut(m):
    """Tower B's hull: the fuselage with its drooping nose, the gills, the box under its middle with the red hatch, the
    bracket under its stern."""
    cols = [c for c, _, _ in B_HULL]
    tip = Vector((X(B_TIP[0]), 0.0, H(B_TIP[1])))
    body = SHELL.body("shell", m["g8"], cols, 40, tips=(tip, None), smooth=40.0)
    shell_paint(m, body)
    parts = [body]
    # The gills: a dark recess on the hull's lower front and five red ribs in it.
    def recess_surf(u, v):
        c = 20.6 + 8.9 * u
        bottom = lerp_table(B_HULL, c, 2) - 0.35
        return SHELL.front(c, 33.2 + (bottom - 33.2) * v)
    parts.append(plate("gill_recess", recess_surf, 12, 6, 0.05, 0.4, (m["g2"], m["g2"], m["g2"]), SHELL.outward))
    for i, c in enumerate(GILLS):
        def rib_surf(u, v, c=c):
            bottom = lerp_table(B_HULL, c - 3.0, 2) - 0.5
            row = GILL_ROWS[0] + (bottom - GILL_ROWS[0]) * v
            col = c - GILL_ROWS[1] * (row - GILL_ROWS[0]) * 0.5 + 0.9 * (u - 0.5)
            return SHELL.front(col, row)
        rib = plate("gill%d" % i, rib_surf, 2, 6, 0.45, 0.3, (m["r6"], m["r3"], m["r4"]), SHELL.outward,
                    paint_outer=lambda c, n: m["r9"] if n.dot(LIGHT) > 0.7 else None)
        parts.append(rib)
    # The box under its middle, the hatch in its front.
    box = rbox("hatch_box", 32.6, 44.2, 35.0, 45.2, -8.9, 0.0, m["g5"], bevel=0.4)
    paint_lit(box, m["g4"], lit=m["g9"], under=m["g2"], lit_at=0.62)
    by_rows(box, [(34.0, 36.3, m["gb"])], keep=lambda c, n: n.y > -0.5 and n.z < 0.5)
    hatch = rbox("hatch", 36.1, 41.9, 38.0, 44.7, -9.3, -8.4, m["r5"], bevel=0.2)
    by_rows(hatch, [(37.0, 39.4, m["r7"]), (39.4, 41.2, m["r5"]), (41.2, 43.0, m["r3"]), (43.0, 43.9, m["b1"]),
                    (43.9, 46.0, m["r2"])])
    parts += [box, hatch]
    return parts


CAPSULE = [(53.6, 29.2, 45.0), (56.0, 29.0, 45.0), (60.0, 29.0, 45.0), (63.0, 29.0, 44.8), (64.5, 29.1, 44.2),
           (66.0, 29.5, 43.4), (67.5, 30.0, 42.6), (68.8, 30.7, 41.8), (69.8, 31.6, 40.8), (70.6, 32.6, 39.6),
           (71.1, 34.0, 38.2)]
CAPSULE_TIP = (71.45, 36.0)
POD = Shape(CAPSULE, depth=0.8, max_depth=6.4, power=2.0, yc=-0.6)
LENS = (60.8, 35.5, 5.9, 3.75)                 # its middle (column, row), half width, half height
BEAD = (61.6, 35.4, 0.95)


def capsule(m, ramp):
    """The capsule at the hull's right end: the pill, the oval lens in its front (ramp 5 purple, ramp 4 red) with a dark
    bezel and a bright bead, the lit band under it."""
    cols = [c for c, _, _ in CAPSULE]
    tip = Vector((X(CAPSULE_TIP[0]), POD.yc, H(CAPSULE_TIP[1])))
    body = POD.body("capsule", m["g7"], cols, 36, tips=(None, tip), smooth=40.0)

    def pick(c, n):
        row = ROW(c.z)
        if n.z < -0.6:
            return m["g2"]
        if n.z < -0.25:
            return m["g3"]
        if 38.8 <= row < 41.3 and n.y < -0.3:
            return m["g9"]
        if n.dot(LIGHT) > 0.86:
            return m["ga"]
        if n.z > 0.45:
            return m["g8"]
        return m["g6"]
    mk.paint(body, pick)
    parts = [body]
    cx, cr, a, b = LENS

    def lens_point(f, t, lift):
        return POD.front(cx + a * f * math.cos(t), cr + b * f * math.sin(t), lift)
    segments = 32
    profile = [(1.12, 0.05), (1.06, 0.32), (1.0, 0.3), (0.96, 0.1), (0.9, 0.36), (0.75, 0.58), (0.55, 0.72),
               (0.3, 0.8)]
    rings = [[lens_point(f, 2 * math.pi * j / segments, lift) for j in range(segments)] for f, lift in profile]
    lens = k.loft("capsule_lens", rings, m["lens_p" if ramp == 5 else "lens_r"], cap_start=False, cap_end=True,
                  end_point=POD.front(cx, cr, 0.82))
    k.smooth(lens, 50)
    rim = m["g2"]
    for poly in lens.data.polygons:
        # The outer two bands: the bezel (dark).
        f = math.hypot((poly.center.x - X(cx)) / a, (ROW(poly.center.z) - cr) / b)
        if f > 0.97:
            poly.material_index = mk.slot_of(lens, rim)
    parts.append(lens)
    bc, br, rad = BEAD
    p = POD.front(bc, br, 0.78)
    parts.append(lathe_on_axis("capsule_bead", [(-0.3, rad), (0.15, rad * 0.9), (0.4, rad * 0.55), (0.52, 0.0)], p,
                               POD.outward(p), m["bead_p" if ramp == 5 else "bead_r"], 14))
    # The bracket under the hull's stern and the capsule's left end.
    bracket = rbox("stern_bracket", 49.6, 57.6, 44.6, 48.0, -3.6, 2.0, m["g4"], bevel=0.3)
    paint_lit(bracket, m["g4"], lit=m["g6"], under=m["g2"], lit_at=0.6)
    parts.append(bracket)
    return parts


# --- Tower A's stripped hull ---------------------------------------------------------------------------------------
# Its envelope (column, top row, bottom row): the fuselage of tower B, longer and open at the left; a dark core inside
# it, and on the core the framework: plates of the sprites' colour classes (purple skin plates, red machinery, light
# and mid grey girders, brown machinery), each a rectangle of the sprites' pixels (columns c0-c1, rows r0-r1, pixel
# edges) lying on the core's front and standing proud of it by its class's lift. The rectangles were read off the
# sprites u 1, 39, 41 and 43 (isolated pixels joined to their surroundings, each class's regions covered by greedy
# rectangles); the darks between them are the core.
A_HULL = [(7.0, 32.4, 40.4), (7.6, 30.6, 41.4), (8.6, 29.4, 42.6), (10.0, 28.8, 43.4), (12.0, 28.5, 43.8),
          (16.0, 28.2, 44.0), (20.0, 28.0, 44.6), (30.0, 28.0, 44.8), (52.0, 28.0, 44.8), (54.0, 28.2, 44.4),
          (55.5, 28.6, 43.6), (56.5, 29.0, 42.8)]
CORE = Shape(A_HULL, depth=0.5, max_depth=5.0, power=2.2)
A_PLATES = [
    ("P", 10, 36, 40, 29, 34), ("P", 6, 8, 11, 33, 40), ("P", 5, 12, 15, 36, 43), ("P", 8, 15, 16, 39, 43),
    ("P", 10, 25, 34, 39, 44), ("P", 8, 11, 12, 41, 43), ("R", 8, 8, 10, 26, 33), ("R", 8, 17, 19, 26, 31),
    ("R", 8, 19, 21, 28, 31), ("R", 6, 27, 29, 28, 30), ("R", 10, 42, 44, 28, 31), ("R", 4, 10, 11, 29, 30),
    ("R", 8, 25, 28, 30, 31), ("R", 8, 12, 15, 31, 33), ("R", 6, 20, 21, 31, 34), ("R", 8, 15, 16, 32, 33),
    ("R", 8, 31, 32, 32, 33), ("R", 5, 38, 39, 34, 43), ("R", 8, 29, 30, 35, 37), ("R", 5, 35, 38, 35, 40),
    ("R", 6, 27, 29, 36, 38), ("R", 10, 23, 27, 37, 38), ("R", 5, 45, 46, 39, 45), ("R", 9, 50, 54, 39, 41),
    ("R", 7, 18, 20, 40, 42), ("R", 4, 36, 38, 40, 41), ("R", 9, 21, 24, 41, 44), ("R", 4, 37, 38, 41, 42),
    ("R", 8, 51, 52, 41, 44), ("R", 5, 46, 47, 42, 45), ("R", 8, 20, 21, 43, 44), ("R", 5, 26, 28, 46, 47),
    ("L", 11, 30, 32, 28, 29), ("L", 8, 41, 42, 28, 30), ("L", 8, 16, 17, 29, 31), ("L", 9, 31, 32, 29, 30),
    ("L", 8, 40, 41, 29, 30), ("L", 8, 48, 51, 29, 31), ("L", 8, 47, 48, 30, 31), ("L", 8, 51, 53, 30, 34),
    ("L", 10, 50, 51, 31, 34), ("L", 8, 53, 54, 32, 33), ("L", 8, 42, 48, 33, 35), ("L", 9, 16, 20, 34, 37),
    ("L", 8, 41, 42, 34, 35), ("L", 10, 42, 47, 35, 36), ("L", 11, 31, 35, 36, 37), ("L", 8, 43, 44, 36, 37),
    ("M", 6, 32, 34, 28, 29), ("M", 6, 46, 48, 29, 30), ("M", 6, 51, 53, 29, 30), ("M", 6, 40, 42, 30, 32),
    ("M", 6, 53, 55, 30, 32), ("M", 7, 41, 44, 32, 33), ("M", 6, 54, 55, 32, 34), ("M", 6, 33, 34, 33, 36),
    ("M", 6, 48, 50, 33, 34), ("M", 6, 32, 33, 34, 36), ("M", 6, 39, 41, 34, 35), ("M", 6, 20, 22, 36, 38),
    ("M", 5, 44, 47, 36, 37), ("M", 6, 16, 20, 37, 38), ("M", 6, 43, 46, 37, 38), ("M", 6, 52, 54, 37, 38),
    ("M", 6, 43, 44, 38, 44), ("M", 6, 49, 50, 39, 43), ("B", 2, 22, 24, 28, 30), ("B", 2, 10, 11, 30, 33),
    ("B", 3, 23, 25, 30, 31), ("B", 1, 29, 30, 30, 33), ("B", 3, 32, 34, 30, 33), ("B", 2, 25, 26, 31, 33),
    ("B", 3, 18, 19, 32, 34), ("B", 2, 12, 18, 33, 34), ("B", 2, 21, 23, 33, 34), ("B", 7, 31, 33, 33, 34),
    ("B", 3, 12, 15, 34, 35), ("B", 2, 22, 23, 34, 39), ("B", 3, 35, 38, 34, 35), ("B", 2, 23, 24, 35, 37),
    ("B", 2, 27, 29, 35, 36), ("B", 3, 23, 30, 38, 39), ("B", 2, 44, 46, 38, 39), ("B", 0, 17, 21, 39, 40),
    ("B", 2, 44, 45, 39, 43), ("B", 2, 17, 18, 40, 42), ("B", 1, 35, 36, 40, 42), ("B", 1, 36, 37, 41, 43),
    ("B", 2, 50, 51, 41, 43), ("B", 3, 52, 54, 41, 44), ("B", 1, 37, 38, 42, 44), ("B", 3, 20, 24, 44, 47),
    ("B", 3, 24, 25, 45, 47), ("B", 3, 26, 28, 45, 46),
]
LIFT = {"P": 3.3, "R": 3.0, "L": 2.6, "M": 1.9, "B": 1.0}


def plate_mats(m, kind, shade):
    """A framework plate's materials by its class and mean shade: (front, lit, side)."""
    if kind == "P":
        key = "p6" if shade <= 5 else "p9" if shade <= 9 else "pc"
        return m[key], m["pc" if key != "pc" else "pd"], m["p6"]
    if kind == "R":
        key = "r6" if shade <= 5 else "r9" if shade <= 8 else "rc"
        return m[key], m["rc"], m["r3"]
    if kind == "L":
        key = "ga" if shade <= 10 else "gc"
        return m[key], m["gc"], m["g5"]
    if kind == "M":
        return m["g6"], m["g8"], m["g3"]
    return m["b3"], m["r6"], m["g2"]


def relief(name, c0, c1, r0, r1, front, lift, depth, mats, lit=None, step=2.2, bevel=0.0):
    """A plate on a surface front(col, row) (its front, which the camera sees face on), over columns c0-c1 and rows
    r0-r1: its outer face lift nearer the camera than the surface (along -y, so that the camera sees it where its
    pixels are), its inner face depth behind it, side walls round it; mats (outer, inner, side); lit: the outer faces
    facing the sun take this material."""
    nu, nv = max(1, int(math.ceil((c1 - c0) / step))), max(1, int(math.ceil((r1 - r0) / step)))

    def surf(u, v):
        return front(c0 + (c1 - c0) * u, r0 + (r1 - r0) * v) - Vector((0.0, lift, 0.0))
    obj = plate(name, surf, nu, nv, 0.0, lift + depth, mats, lambda p: Vector((0.0, -1.0, 0.0)))
    if bevel > 0:
        mk.bevel(obj, bevel, 2 if bevel > 0.25 else 1, 30)
    k.smooth(obj, 35)
    if lit is not None:
        mk.paint(obj, lambda c, n: lit if n.dot(LIGHT) > 0.84 and n.y < 0.3 else None)
    return obj


def hull_open(m):
    """Tower A's hull: the dark core and the framework of plates on it."""
    cols = [c for c, _, _ in A_HULL]
    core = CORE.body("core", m["g2"], cols, 36, smooth=40.0)
    paint_lit(core, m["g2"], lit=m["g3"], lit_at=0.7)
    parts = [core]
    # Dark backings behind the red post at the open end and the red box left of S5, which stand above the core.
    for i, (c0, c1, r0, r1) in enumerate(((7.2, 10.8, 25.2, 33.0), (15.8, 22.2, 24.8, 31.0))):
        back = rbox("frame_back%d" % i, c0, c1, r0, r1, -0.9, 2.0, m["g2"], bevel=0.25)
        parts.append(back)
    for i, (kind, shade, c0, c1, r0, r1) in enumerate(A_PLATES):
        if (c1 - c0) * (r1 - r0) < 2:
            continue                       # single pixels: the core's
        front, lit, side = plate_mats(m, kind, shade)
        size = min(c1 - c0, r1 - r0)
        parts.append(relief("frame_%s%d" % (kind, i), c0, c1, r0, r1, CORE.front, LIFT[kind], 0.6,
                            (front, m["g2"], side), lit, bevel=0.32 if size >= 2 else 0.18))
    return parts


# --- The spires (both towers) -----------------------------------------------------------------------------------------

def spires(m, tower):
    """S1, S3, S2 (crystal, band, rail, body), S4 (the cabin), S5, the cross piece and the dark box among their feet;
    tower B's red bump on its bow."""
    parts = []
    # S1: a grey column, its cap rounded and lit, a red window, its foot narrower and red.
    xc, yc = X(31.5), 1.2
    s1 = post("s1", [(28.5, X(32.0), yc, 1.75, 1.6), (17.9, X(32.0), yc, 1.75, 1.6), (17.6, xc, yc, 2.25, 2.0),
                     (8.8, xc, yc, 2.25, 2.0), (7.4, xc, yc, 2.2, 1.95), (6.2, xc, yc, 2.0, 1.8),
                     (5.3, xc, yc, 1.65, 1.5), (4.65, xc, yc, 1.1, 1.0), (4.3, xc, yc, 0.35, 0.3)], m["g8"], 24, 3.0)
    by_rows(s1, [(0.0, 6.2, m["ga"]), (6.2, 8.8, m["gc"]), (8.8, 17.7, m["g8"]), (17.7, 30.0, m["r6"])])
    win = rbox("s1_window", 31.0, 33.3, 10.9, 16.0, yc - 2.3, yc - 1.7, m["r6"], bevel=0.15)
    by_rows(win, [(10.0, 12.4, m["r9"]), (12.4, 14.8, m["b3"]), (14.8, 17.0, m["r3"])],
            keep=lambda c, n: c.x < X(31.9))
    parts += [s1, win]
    # S3: a red stub.
    xs = X(37.0)
    s3 = post("s3", [(28.0, xs, -0.4, 1.75, 1.4), (15.0, xs, -0.4, 1.75, 1.4), (14.5, xs, -0.4, 1.45, 1.2),
                     (14.2, xs, -0.4, 0.5, 0.4)], m["r9"], 16, 3.0)
    by_rows(s3, [(0.0, 16.2, m["rc"]), (16.2, 30.0, m["r9"])])
    parts.append(s3)
    # S2: the crystal on its band, the rail, the body.
    xk = X(41.5)
    crystal = post("s2_crystal", [(10.4, xk, 0.3, 2.3, 1.8), (3.0, xk, 0.3, 2.25, 1.75), (1.8, xk, 0.3, 1.6, 1.3),
                                  (0.8, xk, 0.3, 0.8, 0.6), (0.2, xk, 0.3, 0.12, 0.1)], m["p9"], 8, 2.0, smooth=0)
    mk.paint(crystal, lambda c, n: m["pd"] if n.dot(LIGHT) > 0.55 else m["p6"] if n.x > 0.45 else m["pc"]
             if ROW(c.z) < 4.0 else None)
    band = post("s2_band", [(12.6, X(41.9), 0.4, 2.65, 2.0), (9.8, X(41.9), 0.4, 2.65, 2.0)], m["g6"], 20, 3.0)
    by_rows(band, [(9.0, 11.0, m["g5"]), (11.0, 13.0, m["g8"])])
    xr = X(45.4)
    rail = post("s2_rail", [(12.6, xr, 0.9, 1.35, 1.15), (6.0, xr, 0.9, 1.35, 1.15), (5.55, xr, 0.9, 1.1, 0.95),
                            (5.2, xr, 0.9, 0.4, 0.35)], m["r9"], 16, 3.0)
    by_rows(rail, [(0.0, 7.6, m["rc"]), (7.6, 9.5, m["r9"]), (9.5, 13.0, m["r9"])])
    body = post("s2_body", [(28.5, X(43.4), 0.6, 3.1, 2.6), (12.9, X(43.4), 0.6, 3.1, 2.6),
                            (12.3, X(43.4), 0.6, 2.85, 2.4)], m["r9"], 24, 3.5)

    def s2_pick(c, n):
        row = ROW(c.z)
        if row < 13.6:
            return m["rc"]
        if row < 16.8:
            return m["r9"] if n.dot(LIGHT) < 0.7 else m["rc"]
        if row < 19.6:
            return m["ga"] if c.x < X(44.0) else m["r9"]
        return m["g8"] if n.dot(LIGHT) > 0.5 else m["g5"]
    mk.paint(body, s2_pick)
    parts += [crystal, band, rail, body]
    # S4: the cabin, its upper block domed, its lower block wider with the red window.
    xu = X(49.9)
    upper = post("s4_upper", [(20.6, xu, 1.6, 3.85, 3.0), (14.2, xu, 1.6, 3.85, 3.0), (13.2, xu, 1.6, 3.55, 2.8),
                              (12.6, xu, 1.6, 2.9, 2.3), (12.25, xu, 1.6, 1.7, 1.4)], m["g8"], 28, 4.0)
    paint_lit(upper, m["g6"], lit=m["ga"], dark=m["g5"], lit_at=0.66)
    lower = rbox("s4_lower", 46.1, 55.8, 20.2, 28.6, -3.0, 5.0, m["g6"], bevel=0.45)
    paint_lit(lower, m["g6"], lit=m["g8"], dark=m["g5"], under=m["g3"], lit_at=0.62)
    window = rbox("s4_window", 49.8, 53.1, 21.8, 28.0, -3.35, -2.6, m["r6"], bevel=0.18)
    by_rows(window, [(21.0, 22.8, m["r9"]), (22.8, 24.6, m["rc"]), (24.6, 29.0, m["r6"])])
    parts += [upper, lower, window]
    # S5: a small post, its grey cap lit, its foot red.
    x5 = X(22.0)
    s5 = post("s5", [(28.6, x5, 0.0, 2.5, 1.9), (22.7, x5, 0.0, 2.5, 1.9), (22.5, x5, 0.0, 2.65, 2.0),
                     (20.3, x5, 0.0, 2.65, 2.0), (19.75, x5, 0.0, 2.35, 1.75), (19.25, x5, 0.0, 1.5, 1.1)],
              m["r9"], 20, 3.0)
    by_rows(s5, [(0.0, 21.0, m["g8"]), (21.0, 22.6, m["gc"]), (22.6, 24.8, m["r9"]), (24.8, 30.0, m["r6"])])
    parts.append(s5)
    # The cross piece among the feet of S1, S3 and S2; the dark box left of S1.
    cross = rbox("cross", 33.0, 38.6, 19.8, 24.2, -1.6, 2.6, m["g5"], bevel=0.3)
    by_rows(cross, [(22.8, 25.0, m["ga"])], keep=lambda c, n: n.y > -0.6)
    box = rbox("dark_box", 26.1, 28.9, 19.9, 25.6, -1.4, 1.8, m["g2"], bevel=0.3)
    by_rows(box, [(20.8, 24.6, m["b3"])], keep=lambda c, n: n.y > -0.7 or abs(c.x - X(27.5)) > 0.55)
    parts += [cross, box]
    if tower == "b":
        bump = rbox("bow_bump", 16.3, 19.6, 25.0, 28.0, -4.2, 1.0, m["r6"], bevel=0.35)
        paint_lit(bump, m["r6"], lit=m["r9"], under=m["r3"], lit_at=0.62)
        parts.append(bump)
    return parts


# --- The damaged looks ----------------------------------------------------------------------------------------------
# What a burnt part's materials become: reds and purples greyed to shades of about their brightness (the damaged
# sprites' greys), browns charred.
BURN = {"r2": "g2", "r3": "g3", "r4": "g3", "r5": "g4", "r6": "g5", "r7": "g6", "r8": "g6", "r9": "g8", "ra": "g8",
        "rb": "g8", "rc": "g8", "p2": "g2", "p4": "g3", "p5": "g3", "p6": "g4", "p7": "g5", "p8": "g5", "p9": "g6",
        "pa": "g6", "pb": "g8", "pc": "g8", "pd": "ga", "b3": "g2", "b1": "g1", "d2": "g2"}
# The snapped spires (u 7, 9, 11): (part, its section (x centre, y centre, half width, half depth, power), its foot
# row, the rows its ragged top falls to at its left and its right, how ragged).
STUMPS = {"s1": ((X(32.0), 1.2, 1.75, 1.6, 3.0), 28.5, 18.5, 17.3, 1.6),
          "s2_body": ((X(43.4), 0.6, 3.1, 2.6, 3.5), 28.5, 13.4, 17.4, 2.2),
          "s4_lower": ((X(50.95), 1.0, 4.85, 4.0, 8.0), 28.6, 20.0, 22.4, 1.2)}
GONE = ("s2_crystal", "s2_band", "s2_rail", "s1_window", "s4_upper", "s4_window")
EMBERS_TOP = [(35.5, 25.2, 0.3, 2.4, -2.05), (47.4, 24.0, 1.3, 2.8, -3.1)]  # glowing cracks: column, row, half width,
#                                                                             half height, depth of the surface
WRECK = (34.6, 1.8, 0.7)                                            # the capsule's ragged top row, how ragged, crumpled
SEED = 33


def mat_key(m, mat):
    for key, value in m.items():
        if value == mat and not key.startswith(("lens", "bead", "lamp", "ember", "char", "cap")):
            return key
    return None


def burn(m, objects, inside=lambda c: True):
    """Greys the faces of the objects whose centre inside(centre) accepts (BURN)."""
    for obj in objects:
        keys = [mat_key(m, mat) for mat in obj.data.materials]
        for poly in obj.data.polygons:
            key = keys[poly.material_index]
            if key in BURN and inside(poly.center):
                poly.material_index = mk.slot_of(obj, m[BURN[key]])
                keys = [mat_key(m, mat) for mat in obj.data.materials]
        obj.data.update()
    return objects


def ragged_top(x, row_left, row_right, x0, x1, amount, seed, y=0.0):
    """The height of a break at x: a line falling from row_left at x0 to row_right at x1, torn by noise."""
    t = min(1.0, max(0.0, (x - x0) / max(x1 - x0, 1e-6)))
    top = H(row_left + (row_right - row_left) * t)
    if amount > 0:
        top -= amount * (0.5 + 0.5 * noise.noise(Vector((x * 1.4 + seed, y * 1.4 - seed, 0.37 * seed))))
    return top


def stump(m, name, section, foot, row_left, row_right, amount, seed):
    """A standing part snapped off: rings every 0.7 rows up to its break, the vertices above the torn line pulled down
    to it and the top crumpled; the break charred, a few torn edges catching the light."""
    xc, yc, hw, hd, power = section
    top_row = min(row_left, row_right) - 1.0
    rows = []
    r = foot
    while r > top_row:
        rows.append(r)
        r -= 0.7
    rows.append(top_row)
    obj = post(name, [(row, xc, yc, hw, hd) for row in rows], m["g6"], 32, power, smooth=0)
    x0, x1 = xc - hw, xc + hw
    for v in obj.data.vertices:
        top = ragged_top(v.co.x, row_left, row_right, x0, x1, amount, seed, v.co.y)
        if v.co.z > top:
            v.co.z = top
        depth = top - v.co.z
        # beaten all over, crumpled more towards the break
        push = (0.22 + 0.4 * max(0.0, 1.8 - depth)) * noise.noise(Vector((v.co.x * 1.7, v.co.y * 1.7 + v.co.z * 0.9,
                                                                           seed * 0.71)))
        v.co.x += push * (v.co.x - xc) / max(hw, 1e-6)
        v.co.y += push * (v.co.y - yc) / max(hd, 1e-6)
    obj.data.update()
    k.smooth(obj, 35)

    def pick(c, n):
        top = ragged_top(c.x, row_left, row_right, x0, x1, amount, seed, c.y)
        if c.z > top - 0.25 and n.z > 0.3:
            return m["g8"] if n.dot(LIGHT) > 0.85 else m["char"]
        if c.z > top - 1.1:
            return m["g2"]
        if noise.noise(Vector((c.x * 0.9 + seed, c.z * 0.9, 2.3))) > 0.25:
            return m["g3"]                                   # soot
        d = n.dot(LIGHT)
        return m["g8"] if d > 0.8 else m["g5"] if d > 0.2 else m["g3"]
    mk.paint(obj, pick)
    return obj


def stumps(m):
    """The spires snapped to stumps (u 7, 9, 11): S1, S2 and the cabin's lower block broken off raggedly, S3 and S5
    standing; the crystal, its band and rail and the cabin's upper block gone; all burnt; embers in two cracks."""
    parts = []
    for obj in spires(m, "a"):
        name = obj.name.split(".")[0]
        if name in GONE or name in STUMPS:
            remove([obj])
            continue
        parts.append(obj)
    for i, (name, (section, foot, r0, r1, amount)) in enumerate(sorted(STUMPS.items())):
        parts.append(stump(m, name + "_stump", section, foot, r0, r1, amount, SEED + 5 * i))
    burn(m, parts)
    for i, (c, r, hw, hh, y) in enumerate(EMBERS_TOP):
        parts += embers(m, "ember_top%d" % i, c, r, hw, hh, lambda col, row, y=y: Vector((X(col), y, H(row))))
    return parts


def wreck(m):
    """The capsule shot away (u 127): its lower half left as a crumpled, burnt wreck with a ragged top; a broken stub
    where it was fixed to the hull, embers glowing at its root; the bracket."""
    cols = [c for c, _, _ in CAPSULE]
    body = POD.body("wreck", m["g4"], cols, 36, tips=(None, Vector((X(CAPSULE_TIP[0]), POD.yc, H(CAPSULE_TIP[1])))),
                    smooth=30.0)
    mk.apply(body)
    row, amount, crumple = WRECK
    for v in body.data.vertices:
        top = H(row) - amount * (0.5 + 0.5 * noise.noise(Vector((v.co.x * 0.9 + 3.1, v.co.y * 0.9, 1.7))))
        if v.co.z > top:
            v.co.z = top
        # crumpled: pushed in and out
        v.co.y += crumple * noise.noise(Vector((v.co.x * 1.1, v.co.z * 1.1, 5.3)))
        v.co.z += 0.6 * crumple * noise.noise(Vector((v.co.x * 1.3, v.co.y * 1.3, 9.1)))
    body.data.update()

    def pick(c, n):
        if n.z > 0.35 and c.z > H(row) - amount - 0.3:
            return m["g8"] if n.dot(LIGHT) > 0.8 else m["g5"]        # the torn top, catching the light
        if n.z < -0.5:
            return m["g1"]
        return m["g3"] if n.dot(LIGHT) > 0.55 else m["g2"]
    mk.paint(body, pick)
    stub = stump(m, "wreck_stub", (X(56.1), -1.6, 2.3, 3.0, 6.0), 38.0, 31.6, 33.4, 1.0, SEED + 7)
    parts = [body, stub]
    parts += embers(m, "wreck_ember", 56.4, 34.0, 1.7, 2.0, lambda col, row: Vector((X(col), -4.75, H(row))))
    bracket = rbox("stern_bracket", 49.6, 57.6, 44.6, 48.0, -3.6, 2.0, m["g4"], bevel=0.3)
    paint_lit(bracket, m["g4"], lit=m["g5"], under=m["g2"], lit_at=0.6)
    parts.append(bracket)
    return parts


# --- The whole: leaned, cut under the floor and into its pieces ------------------------------------------------------

def lean(objects):
    for obj in objects:
        mk.apply(obj)
        obj.data.transform(TO_WORLD)
        obj.data.update()
    return objects


def cut_planes(source, planes, cap_mat, name):
    """The part of an object on the inner side of every plane (point, outward normal), its cuts capped with cap_mat
    (flat, facing out of their cut, given their material as soon as they are made), the faces' own winding kept, its
    normals the uncut object's (polish_coral_manta.cut with any planes). None if nothing is left."""
    obj = source.copy()
    obj.data = source.data.copy()
    obj.name = obj.data.name = name
    bpy.context.scene.collection.objects.link(obj)
    cap_index = mk.slot_of(obj, cap_mat)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    caps = set()
    for co, no in planes:
        if not bm.faces:
            break
        res = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6, plane_co=co,
                                     plane_no=no, clear_outer=True)
        edges = [e for e in res["geom_cut"] if isinstance(e, bmesh.types.BMEdge) and e.is_valid]
        open_edges = [e for e in edges if len(e.link_faces) == 1]
        if open_edges:
            filled = bmesh.ops.holes_fill(bm, edges=open_edges, sides=0)
            if filled["faces"]:
                for f in bmesh.ops.triangulate(bm, faces=filled["faces"])["faces"]:
                    f.normal_update()
                    if f.normal.dot(Vector(no)) < 0:
                        f.normal_flip()
                    f.material_index = cap_index
                    f.smooth = False
                    caps.add(f)
    caps = {f for f in caps if f.is_valid}
    if not bm.faces:
        bm.free()
        bpy.data.objects.remove(obj)
        return None
    bm.normal_update()
    bm.faces.index_update()
    cap_ids = {f.index for f in caps}
    bm.to_mesh(obj.data)
    bm.free()
    shading = mk.NormalSource(source)
    mesh = obj.data
    normals = []
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            n = None
            if poly.index not in cap_ids:
                n = shading.normal(mesh.vertices[mesh.loops[li].vertex_index].co, poly.center)
            normals.append(tuple(n if n is not None else poly.normal))
    mesh.normals_split_custom_set(normals)
    return obj


def floor_cut(objects, m):
    """Everything under FLOOR_CUT cut away (the floor hides it), the cut closed in the inside's dark."""
    out = []
    for obj in objects:
        if min(v.co.z for v in obj.data.vertices) >= FLOOR_CUT:
            out.append(obj)
            continue
        piece = cut_planes(obj, [((0.0, 0.0, FLOOR_CUT), (0.0, 0.0, -1.0))], m["g2"], obj.name)
        data = obj.data
        bpy.data.objects.remove(obj)
        if data.users == 0:
            bpy.data.meshes.remove(data)
        if piece is not None:
            out.append(piece)
    return out


def row_plane(row, below):
    """The plane of sight through the picture's row (square to the leaned mast): (point, outward normal) keeping what
    lies above the row (below=False) or below it."""
    axis = TO_WORLD.to_3x3() @ Vector((0.0, 0.0, 1.0))
    point = TO_WORLD @ Vector((0.0, 0.0, H(row)))
    return (tuple(point), tuple(axis if below else -axis))


def piece_planes(c0, c1, r0, r1):
    """The planes bounding a piece: columns c0-c1, rows r0-r1 (pixel edges)."""
    return [((X(c0), 0.0, 0.0), (-1.0, 0.0, 0.0)), ((X(c1), 0.0, 0.0), (1.0, 0.0, 0.0)),
            row_plane(r0, below=True), row_plane(r1, below=False)]


def finish_parts(objects, m):
    """Leans the upright parts and cuts away what is under the floor."""
    lean(objects)
    out = floor_cut(objects, m)
    bpy.context.view_layer.update()
    return out


# --- Checks -----------------------------------------------------------------------------------------------------------

SHEET_W = 228


def sprite_indices(sheet, sprite, large=True):
    mask = k.sprite_mask(sheet, sprite, large)
    raw = open(sheet[:-4] + ".idx", "rb").read()
    x0, y0 = (sprite - 1) % 19 * 12, (sprite - 1) // 19 * 14
    w, h = (24, 28) if large else (12, 14)
    return [[raw[(y0 + r) * SHEET_W + x0 + c] if mask[r][c] else None for c in range(w)] for r in range(h)]


def own_mask(sheet, sprite, large=True):
    """A sprite's own pixels: the floor's ramp-6 pixels and stray single pixels at its edge left out."""
    idx = sprite_indices(sheet, sprite, large)
    out = []
    for r, row in enumerate(idx):
        line = []
        for c, v in enumerate(row):
            keep = v is not None and v >> 4 != 6
            if keep and c == 0:
                neighbours = sum(1 for dr in (-1, 0, 1) for dc in (0, 1) if (dr or dc) and 0 <= r + dr < len(idx) and
                                 c + dc < len(row) and idx[r + dr][c + dc] is not None)
                keep = neighbours > 0
            line.append(keep)
        out.append(line)
    return out


def view_coverage(objects, c0, c1, r0, r1, sub=3):
    """Which pixels of the picture's columns c0-c1 and rows r0-r1 the camera sees the objects at: rays along its line
    of sight through each pixel's samples onto the floor (rows of bools)."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    trees = [BVHTree.FromObject(o, depsgraph) for o in objects]
    out = []
    for r in range(int(r0), int(r1)):
        line = []
        for c in range(int(c0), int(c1)):
            hits = 0
            for i in range(sub):
                for j in range(sub):
                    x = X(c + (i + 0.5) / sub)
                    y = 42.0 - (r + (j + 0.5) / sub)
                    origin = Vector((x, y, 0.0)) - VIEW * 200.0
                    if any(t.ray_cast(origin, VIEW, 400.0)[0] is not None for t in trees):
                        hits += 1
            line.append(hits * 2 > sub * sub)
        out.append(line)
    return out


# --- The towers -------------------------------------------------------------------------------------------------------
# The pieces: (model, sprite, columns c0-c1 and rows r0-r1 of the picture it covers, 2x2).
PIECES = {
    "a": [("deli_tower_1", 1, (0, 24, 0, 28), True), ("deli_tower_3", 3, (24, 48, 0, 28), True),
          ("deli_tower_5", 5, (48, 72, 0, 28), True), ("deli_tower_39", 39, (0, 24, 28, 56), True),
          ("deli_tower_41", 41, (24, 48, 28, 56), True), ("deli_tower_43", 43, (48, 72, 28, 56), True),
          ("deli_tower_79", 79, (24, 48, 56, 84), True)],
    "b": [("deli_tower_19", 19, (12, 24, 13, 27), False), ("deli_tower_38", 38, (12, 24, 27, 41), False),
          ("deli_tower_15", 15, (24, 48, 0, 28), True), ("deli_tower_17", 17, (48, 72, 0, 28), True),
          ("deli_tower_53", 53, (24, 48, 28, 56), True), ("deli_tower_55", 55, (48, 72, 28, 56), True)],
    "a_dmg": [("deli_tower_7", 7, (0, 24, 0, 28), True), ("deli_tower_9", 9, (24, 48, 0, 28), True),
              ("deli_tower_11", 11, (48, 72, 0, 28), True), ("deli_tower_127", 127, (48, 72, 28, 56), True),
              ("deli_tower_77", 77, (24, 48, 56, 84), True)],
}
# How the levels lay each tower's sprites out (for the whole's check): (sprite, column, row, 2x2).
LAYOUT = {"a": [(1, 0, 0, True), (3, 24, 0, True), (5, 48, 0, True), (39, 0, 28, True), (41, 24, 28, True),
                (43, 48, 28, True), (79, 24, 56, True)],
          "b": [(15, 24, 0, True), (17, 48, 0, True), (53, 24, 28, True), (55, 48, 28, True), (79, 24, 56, True),
                (19, 12, 13, False), (38, 12, 27, False)],
          "a_dmg": [(7, 0, 0, True), (9, 24, 0, True), (11, 48, 0, True), (39, 0, 28, True), (41, 24, 28, True),
                    (127, 48, 28, True), (77, 24, 56, True)]}


def build_tower(m, which):
    """A tower's parts, upright."""
    if which == "b":
        return housing(m) + mast(m) + hull_shut(m) + capsule(m, 4) + spires(m, "b")
    if which == "a":
        return housing(m) + mast(m) + hull_open(m) + capsule(m, 5) + spires(m, "a")
    if which == "a_dmg":
        hull = hull_open(m)
        burn(m, hull, lambda c: c.x > X(48.0) - 0.01 or ROW(c.z) < 28.0)
        return housing(m, burnt=True) + mast(m, burnt=True) + hull + wreck(m) + stumps(m)
    raise ValueError(which)


def whole_mask(sheet, which):
    mask = [[False] * 72 for _ in range(84)]
    for sprite, c0, r0, large in LAYOUT[which]:
        for r, row in enumerate(own_mask(sheet, sprite, large)):
            for c, v in enumerate(row):
                if v:
                    mask[r0 + r][c0 + c] = True
    return mask


def palette_of(mat):
    return int(mat.name.rsplit("@", 1)[1]) if "@" in mat.name else None


def limit_materials(obj, limit=15):
    """At most limit materials: the least used plain ones give their faces to the nearest shade of their ramp in use
    (or the nearest grey)."""
    mesh = obj.data
    while True:
        counts = {}
        for poly in mesh.polygons:
            counts[poly.material_index] = counts.get(poly.material_index, 0) + 1
        if len(counts) <= limit:
            break
        plain = [i for i in counts if mesh.materials[i].name.startswith("dtow_") and
                 mesh.materials[i].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value == 0]
        victim = min(plain, key=lambda i: (counts[i], i))
        v = palette_of(mesh.materials[victim])
        others = [i for i in counts if i != victim and i in plain]

        def distance(i):
            w = palette_of(mesh.materials[i])
            return (0 if w >> 4 == v >> 4 else 1 if w >> 4 == 0 else 2, abs((w & 15) - (v & 15)), i)
        target = min(others, key=distance)
        for poly in mesh.polygons:
            if poly.material_index == victim:
                poly.material_index = target
        mesh.update()
    db.drop_unused([obj])
    return obj


def remove(objects):
    for obj in objects:
        data = obj.data
        bpy.data.objects.remove(obj)
        if data.users == 0:
            bpy.data.meshes.remove(data)


def export_piece(whole, m, name, sprite, box, large, options, sheet, burnt=False):
    c0, c1, r0, r1 = box
    planes = piece_planes(c0, c1, r0, r1)
    parts = [p for p in (cut_planes(src, planes, m["cap"], "%s_%s" % (name, src.name)) for src in whole)
             if p is not None]
    if not parts:
        print("!! %s: nothing in its box" % name)
        return
    if burnt:
        burn(m, parts)                     # a damaged piece is burnt through, whatever crosses its edges
    for src in whole:
        src.hide_render = True
    bpy.context.view_layer.update()
    if sheet:
        mk.compare("%s (u %d), as the game's camera sees it" % (name, sprite), view_coverage(parts, c0, c1, r0, r1),
                   own_mask(sheet, sprite, large))
    cx, cy = X((c0 + c1) / 2.0), 42.0 - (r0 + r1) / 2.0
    db.drop_unused(parts)
    mk.transform(parts, Matrix.Translation((-cx, -cy, 0.0)))
    bpy.context.view_layer.update()
    triangulate(parts)
    if "stats" in options:
        for obj in sorted(parts, key=lambda o: -mk.triangles([o]))[:10]:
            print("    %-28s %6d" % (obj.name, mk.triangles([obj])))
    obj = db.join(parts, name)
    obj.data.name = name
    limit_materials(obj)
    bpy.context.scene.view_settings.view_transform = "Standard"
    mk.report(name, [obj], os.path.join(mk.outdir(options), name + ".glb"))
    if "preview" in options:
        # framed on the piece (it lies below its origin: the lean)
        low, high = mk.bounds([obj])
        mk.preview(options["preview"] + name, [obj], size=(24, 28) if large else (12, 14), scale=10, distance=1.1,
                   centre=((low.x + high.x) / 2, (low.y + high.y) / 2))
    remove([obj])
    for src in whole:
        src.hide_render = False


def build():
    options = k.args()
    only = options["only"].split(",") if "only" in options else None
    sheet = os.path.join(options["check"], "enemy_U.png") if "check" in options else None
    towers = options.get("towers", "a,b,a_dmg").split(",")
    for which in towers:
        k.reset()
        m = materials()
        whole = finish_parts(build_tower(m, which), m)
        print("whole %s: %d triangles, %d objects" % (which, mk.triangles(whole), len(whole)))
        if sheet:
            mk.compare("whole tower %s, as the game's camera sees it" % which, view_coverage(whole, 0, 72, 0, 84),
                       whole_mask(sheet, which))
        if "whole" in options:
            copies = []
            for obj in whole:
                c = obj.copy()
                c.data = obj.data.copy()
                bpy.context.scene.collection.objects.link(c)
                copies.append(c)
            triangulate(copies)
            for src in whole:
                src.hide_render = True
            mk.export(copies, options["whole"] + which + ".glb")
            remove(copies)
            for src in whole:
                src.hide_render = False
        for name, sprite, box, large in PIECES[which]:
            if only and name not in only:
                continue
            export_piece(whole, m, name, sprite, box, large, options, sheet, burnt=(which == "a_dmg"))


if __name__ == "__main__":
    build()
