"""DELI's long blue cannons cracked (sheet C; DELI, New Deli, VAULT, DEEP ICE): the damaged looks the game shows in
place of each piece once it is hit hard (the enemy data's dgr, dlevel 8): pointing right C 231, 233, 235 and the 1x1 237
(of 269, 271, 273, 275; enemies 228-231), pointing left the 1x1 C 276, 277, 279, 281 (of 238, 239, 241, 243; enemies
232-235). Each piece is damaged on its own, so a damaged piece must meet its neighbours, damaged or not. models.cfg:
model deli_cannon_dmg_breech / _dmg_mount / _dmg_barrel / _dmg_muzzle and deli_cannon_l_dmg_muzzle / _l_dmg_barrel /
_l_dmg_mount / _l_dmg_breech ... origin; sprite c 231 deli_cannon_dmg_breech yaw=0 height=-6 and so on, as the intact
pieces. Polished (2026-10-21; it replaces wave3_ao_deli.py's cannon_damaged_whole() and cannon_damaged_piece(), which
holed and repainted wave3_x_cannon.py's old cannon pixel by pixel).

The cannon is polish_deli_cannon.py's (its parts imported, unchanged), built whole and upright, damaged as the damaged
sprites draw it, then leaned, cut at the platform and cut along the sprites' edges into the same pieces at the same
origins as that script cuts the intact ones (the left cannon the damaged whole mirrored, as the intact one), so that
any damaged piece meets any intact one: the parts are split along the cuts first (polish_deli_cannon.presplit(), as
the intact build splits them), nothing is moved within 1.2 pixels of the cuts (x = -18, 6, 30: the dents and grooves
fade out towards them), and the corner normals there are set back to the undamaged part's (restore_normals()): the
pieces' cuts are the intact pieces' to the vertex, their shading at the cuts the same (checked: positions equal,
normals within 0.0004).

What the damaged sprites draw differently (pixel by pixel; C 276 + 277 + 279 + 281 are C 231 + 233 + 235 + 237
mirrored but for the muzzle cap's tip and the lighting, as the intact pair; no other sprite of any sheet is these
mirrored, turned or in other ramps):
- the breech's rear half burnt black (columns 1-11 of rows 4-10), its edges scorched darker grey, red cracks in it
  crossing (down column 7, along row 7 back to the rear end, a branch down column 4, hottest where they cross) and down
  its rounded end (column 2);
- the handle scorched darker, a black hole in it (columns 10-13 of rows 10-11), its knob's foot charred;
- the finned block's rounded end burnt black (columns 8-11), a red cross on the fins (down column 13, along row 15);
- the tall block at the breech's front burnt black across its middle (rows 5-7), scorched round it;
- a red cross at the receiver's lower rear (columns 28-30 of rows 10-15) running down into the trunnion's top;
- a red cross on the sight's face (down column 37, along row 6), black round it, its top scorched;
- a red crack along the receiver's front under the hull (row 7, columns 44-48), black over it;
- a black hole in the trunnion's base (columns 34-36 of rows 20-23), scorched round it;
- a black hole in the barrel (columns 61-63 of rows 6-7), its top scorched;
- the muzzle housing cracked red (columns 69-72 of rows 5-7), its cap's top lip black, its top scorched; the port's
  glow out: the lens dark, a dying ember at its heart, the strip along the port's floor dead.
How (polish_ball_mast_dmg.py's way, in the picture's coordinates, which the game's camera sees face on): where a
burn's contour crosses the faces the camera sees, and by the cracks and pits, the faces are cut finer; then cut along
the burns' ragged contours (noise, split_along), repainted (black, 0x01, where the sprites draw black; a scorched rim
round each burn, every shade two darker) and pressed in along their normals where the camera looks at them squarely:
grooves along the cracks, pits at the holes and the cracks' ends, the burns crumpled a little; the cracks are jagged
glowing strips laid on the parts along the camera's view (0x74 glowing 0.35, 0x76 0.5 and wider where they cross),
the dying ember 0x72 0.15. Materials: polish_deli_cannon.py's (the port's glows gone) and the damage's, 15 at most.

Coordinates as in polish_deli_cannon.py: the upright frame's x along the gun, h up (the picture's y: column c is x =
c + 0.5 - 42, row r is h = 13.5 - r), d back; leaned by that script's LEAN.

Replaces wave3_ao_deli.py's cannon section: remove C_FRAMES, cannon_damaged_whole() with its two x.whole(...)
registrations ("cannon_damaged", "cannon_l_damaged"), DMG_NAMES, cannon_damaged_piece() and the model loop over
cannon.PIECES, the line cannon = kit.quiet_import("wave3_x_cannon"), the deli_cannon_dmg bullet of its docstring and
"and its long cannons" / "wave3_x_cannon.py" in its first lines; and wave3_ao_art.py's CANNON_DMG and CANNON_L_DMG
(only C_FRAMES reads them). The tower's damaged look stays (deli_painter() and holes_of() too: the tower uses them).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the whole's and each piece's
silhouette against the damaged sprites in enemy_C.png, the platform's pixels left out), --preview <prefix>,
--only <name,...>, --whole <prefix> (the leaned damaged wholes, as <prefix>cannon_dmg.glb and <prefix>cannon_dmg_l.glb).
"""
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Vector, noise
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
import polish_deli_cannon as cn  # noqa: E402

DMG_NAMES = {"deli_cannon_breech": ("deli_cannon_dmg_breech", 231),
             "deli_cannon_mount": ("deli_cannon_dmg_mount", 233),
             "deli_cannon_barrel": ("deli_cannon_dmg_barrel", 235),
             "deli_cannon_muzzle": ("deli_cannon_dmg_muzzle", 237),
             "deli_cannon_l_muzzle": ("deli_cannon_l_dmg_muzzle", 276),
             "deli_cannon_l_barrel": ("deli_cannon_l_dmg_barrel", 277),
             "deli_cannon_l_mount": ("deli_cannon_l_dmg_mount", 279),
             "deli_cannon_l_breech": ("deli_cannon_l_dmg_breech", 281)}
# The pieces, as polish_deli_cannon.py's (the same boxes and origins), with the damaged sprites.
PIECES = [(DMG_NAMES[name][0], DMG_NAMES[name][1], large, box) for name, _, large, box in cn.PIECES]
PIECES_L = [(DMG_NAMES[name][0], DMG_NAMES[name][1], large, box) for name, _, large, box in cn.PIECES_L]
LAYOUT = {False: [(231, True, 0), (233, True, 24), (235, True, 48), (237, False, 72)],
          True: [(276, False, 0), (277, True, 12), (279, True, 36), (281, True, 60)]}
SEED = 231

# Where the pieces meet (polish_deli_cannon.CUTS: x of the cuts across the gun, pointing right): nothing moves within
# FADE[0] of them, the dents grow to their full depth by FADE[1]; no faces are cut finer for the cracks within FADE[1].
CUTS = cn.CUTS
FADE = (1.2, 2.0)

# --- The damage map, in the picture's coordinates (x, h) --------------------------------------------------------------
# Burns: rounded rectangles (x0, x1, h0, h1, corner radius, how burnt: 1 black, 0.5 scorched), their edges made ragged
# by noise (amplitude, frequency): black where the sprites draw black, a scorched rim round each (RIM wider, its
# corners rounder); faces burnt above CHAR are black, above SCORCH every shade darker.
BURNS = [(-40.9, -30.6, 3.8, 10.1, 1.4, 1.0),      # the breech's rear half
         (-31.6, -28.5, 2.3, 4.1, 0.7, 1.0),       # the hole in the handle
         (-38.6, -35.3, -1.3, 0.4, 0.6, 1.0),      # the knob's foot
         (-34.8, -30.3, -4.1, -1.1, 0.8, 1.0),     # the finned block's end
         (-21.4, -15.4, 6.3, 9.6, 0.8, 1.0),       # across the tall block's middle
         (-14.0, -10.8, -1.0, 3.9, 0.9, 0.8),      # round the receiver's lower rear cross
         (-6.6, -2.6, 5.2, 9.9, 1.0, 0.9),         # round the sight's cross
         (2.0, 7.4, 6.15, 7.9, 0.5, 1.0),          # over the receiver's front crack
         (-7.6, -4.4, -9.6, -6.3, 0.7, 1.0),       # the hole in the trunnion's base
         (19.2, 22.0, 6.0, 8.1, 0.6, 1.0),         # the hole in the barrel
         (27.3, 33.9, 6.0, 8.7, 0.8, 0.9)]         # the muzzle's crack, the cap's top lip
RIM = (1.1, 1.0, 0.5)               # how much wider, how much rounder, how burnt
FINE_BURN = 1.0                    # the faces where burns are painted: edges cut until shorter than this
RAGGED = (0.24, 0.9)
CHAR, SCORCH = 0.62, 0.3
# The cracks: lines made jagged (a point every JAG_STEP moved up to JAG across); the strips' half-width (wider where
# they cross: HOT spots, (x, h), radius) and lift off the surface; the grooves under them; the pits ((x, h), radius,
# depth): the holes and the cracks' ends.
CRACKS = [[(-34.5, 9.7), (-34.42, 8.2), (-34.58, 6.6), (-34.5, 4.5)],            # the breech
          [(-39.7, 6.5), (-38.5, 6.6), (-37.4, 6.45), (-36.2, 6.55), (-34.5, 6.5)],
          [(-37.5, 8.7), (-37.45, 7.6), (-37.5, 6.5)],
          [(-39.6, 6.5), (-39.5, 5.2), (-39.62, 3.9)],
          [(-28.5, -0.3), (-28.45, -1.5), (-28.55, -3.0), (-28.5, -4.3), (-29.3, -5.2)],   # the fins
          [(-29.6, -1.5), (-28.5, -1.55), (-27.4, -1.45), (-26.4, -1.5)],
          [(-11.5, 3.7), (-11.45, 2.3), (-11.55, 0.8), (-11.5, -1.7)],         # the receiver's lower rear
          [(-13.7, 1.5), (-12.6, 1.55), (-11.5, 1.5)],
          [(-13.5, 2.7), (-13.55, 1.5), (-13.5, 0.4)],
          [(-4.5, 9.7), (-4.45, 8.4), (-4.55, 7.0), (-4.5, 5.3)],              # the sight
          [(-6.7, 7.5), (-5.5, 7.55), (-4.5, 7.45), (-3.4, 7.5)],
          [(2.3, 6.5), (3.5, 6.56), (4.5, 6.42), (5.5, 6.05), (6.7, 6.4)],     # the receiver's front
          [(27.3, 7.5), (28.5, 7.56), (29.6, 7.4), (30.7, 7.55)],              # the muzzle housing
          [(28.5, 8.6), (28.45, 7.5), (28.6, 6.5)]]
HOT = [((-37.5, 6.5), 0.9), ((-34.5, 6.5), 0.7), ((-28.5, -1.5), 0.8), ((-12.5, 1.5), 0.8), ((-4.5, 7.5), 0.9),
       ((4.5, 6.5), 0.7), ((28.5, 7.5), 0.8)]
JAG_STEP, JAG = 0.5, 0.16
STRIP_HALF, STRIP_HOT, STRIP_LIFT, STRIP_STEP = 0.3, 0.16, 0.06, 0.25
GROOVE_HALF, GROOVE_DEPTH = 0.6, 0.3
PITS = [((-30.0, 3.2), 1.25, 0.7), ((-6.0, -8.0), 1.6, 0.8), ((20.6, 7.05), 1.15, 0.6),
        ((-34.5, 4.4), 0.45, 0.45), ((-39.6, 3.8), 0.42, 0.4), ((-29.3, -5.2), 0.42, 0.4), ((-11.5, -1.8), 0.45, 0.4),
        ((-4.5, 5.2), 0.45, 0.4), ((6.7, 6.4), 0.4, 0.35), ((30.7, 7.55), 0.4, 0.35)]
CRUMPLE = (0.1, 0.85)
FINE = 0.8
# The dead port: the lens's heart a dying ember (radius as a share of the lens's).
EMBER_HEART = 0.38
# The parts pressed in (the others are only repainted); the parts left as they are.
PRESSED = {"breech", "handle", "fin_block", "lower_box", "sight", "hull", "lower_block", "trunnion", "barrel",
           "housing", "base_strip", "collar1", "side_block", "rear_block", "small_box"}
UNTOUCHED = {"lens", "glow_strip", "core"}


def materials():
    """polish_deli_cannon.py's materials and the damage's: black, the embers and the dying ember."""
    pal = k.level_palette()
    m = cn.materials()

    def mat(name, index, metallic=0.2, roughness=0.6, glow=0.0):
        if glow > 0:
            return k.material(name, palette=index, metallic=0.0, roughness=roughness, emission=pal[index],
                              emission_strength=glow)
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)
    m.update({
        "char": mat("dcand_char", 0x01, 0.0, 0.85),
        "ember": mat("dcand_ember", 0x74, roughness=0.45, glow=0.35),
        "ember_hot": mat("dcand_ember_hot", 0x76, roughness=0.4, glow=0.5),
        "ember_dim": mat("dcand_ember_dim", 0x72, roughness=0.5, glow=0.15),
    })
    return m


# What each material becomes where scorched: every shade darker (no new shade is brought in).
SCORCHED = {"be": "ba", "bc": "b8", "ba": "b6", "b8": "b4", "b6": "b4", "b4": "b4", "b2": "b2",
            "gd": "g9", "gb": "g7", "g9": "g7", "g7": "g5", "g5": "g5", "seam": "seam", "char": "char"}


# --- The damage -------------------------------------------------------------------------------------------------------

def smoothstep(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def near_cut(x):
    return min(abs(x - c) for c in CUTS)


def fade(x):
    """0 within FADE[0] of a cut, 1 beyond FADE[1]."""
    return smoothstep(FADE[0], FADE[1], near_cut(x))


def jagged(points, rng):
    """A crack's line resampled every JAG_STEP, each inner point moved across it at random."""
    out = []
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        n = max(1, round(math.hypot(x1 - x0, y1 - y0) / JAG_STEP))
        out += [(x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n) for i in range(n)]
    out.append(points[-1])
    moved = [out[0]]
    for i in range(1, len(out) - 1):
        tx, ty = out[i + 1][0] - out[i - 1][0], out[i + 1][1] - out[i - 1][1]
        length = math.hypot(tx, ty) or 1.0
        o = rng.uniform(-JAG, JAG)
        moved.append((out[i][0] - ty / length * o, out[i][1] + tx / length * o))
    return moved + [out[-1]]


def resample(points, step):
    out, along = [points[0]], [0.0]
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        length = math.hypot(x1 - x0, y1 - y0)
        n = max(1, round(length / step))
        for i in range(1, n + 1):
            out.append((x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n))
            along.append(along[-1] + length / n)
    return out, along


class Damage:
    """The burns, cracks and pits of the cannon, in the picture's coordinates (a point's x and h)."""

    def __init__(self, seed):
        rng = random.Random(seed * 7919)
        self.lines = [jagged(line, rng) for line in CRACKS]
        self.offset = Vector((seed * 3.17, -seed * 1.91, seed * 0.77))

    def burn(self, p):
        x, y = p.x, p.z
        a, f = RAGGED
        wob = a * noise.noise(Vector((x * f, y * f, 0.0)) + self.offset)
        best = 0.0
        grow, round_, rim = RIM
        for x0, x1, y0, y1, r, level in BURNS:
            cx, cy, hw, hh = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2, (y1 - y0) / 2
            d = mk.rounded_rect_distance(x - cx, y - cy, hw, hh, min(r, hw, hh)) + wob * 2.0
            best = max(best, level * (1.0 - smoothstep(-0.35, 0.35, d)))
            d = mk.rounded_rect_distance(x - cx, y - cy, hw + grow, hh + grow, min(r + round_, hw + grow, hh + grow))
            best = max(best, rim * level * (1.0 - smoothstep(-0.4, 0.4, d + wob * 2.5)))
        return best

    def in_burn(self, lo, hi, margin=0.6):
        """Whether a box (lo, hi: (x, h) corners) meets a burn or its rim."""
        grow = RIM[0] + margin
        return any(lo[0] < x1 + grow and hi[0] > x0 - grow and lo[1] < y1 + grow and hi[1] > y0 - grow
                   for x0, x1, y0, y1, _, _ in BURNS)

    def crack(self, p):
        x, y = p.x, p.z
        best = 1e9
        for line in self.lines:
            for (ax, ay), (bx, by) in zip(line, line[1:]):
                dx, dy = bx - ax, by - ay
                t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / max(dx * dx + dy * dy, 1e-9)))
                best = min(best, math.hypot(x - ax - t * dx, y - ay - t * dy))
        return best

    def heat(self, x, y):
        return max([1.0 - smoothstep(0.0, 2.0 * r, math.hypot(x - c[0], y - c[1])) for c, r in HOT] + [0.0])

    def depth(self, p):
        """How far the surface is pressed in at p: the grooves, the pits, the burns' crumpling; nothing at the cuts."""
        x, y = p.x, p.z
        d = 0.0
        b = self.burn(p)
        if b > SCORCH:
            a, f = CRUMPLE
            d += b * a * (0.6 + noise.noise(Vector((x * f, y * f, 1.3)) + self.offset))
        c = self.crack(p)
        if c < GROOVE_HALF:
            d += GROOVE_DEPTH * (1 - (c / GROOVE_HALF) ** 2)
        for (cx, cy), r, depth in PITS:
            t = math.hypot(x - cx, y - cy) / r
            if t < 1:
                d += depth * (1 - t * t) ** 1.5
        return d * fade(x)

    def near(self, p, reach=0.75):
        """Whether p needs fine faces: by a crack or a pit, not by a cut."""
        if near_cut(p.x) < FADE[1]:
            return False
        return self.crack(p) < reach or any(math.hypot(p.x - c[0], p.z - c[1]) < r + reach for c, r, _ in PITS)


def seen(n):
    """Whether a face with normal n faces the game's camera (the upright frame's front, -d)."""
    return n.y < -0.05


def crossed(f, dmg):
    """Whether a burn's contour (CHAR or SCORCH) crosses a face: its corners', edges' middles' and middle's burns
    straddle a threshold."""
    pts = [v.co for v in f.verts] + [(e.verts[0].co + e.verts[1].co) / 2 for e in f.edges] + [f.calc_center_median()]
    xs, hs = [p.x for p in pts], [p.z for p in pts]
    if not dmg.in_burn((min(xs), min(hs)), (max(xs), max(hs))):
        return False
    values = [dmg.burn(p) for p in pts]
    lo, hi = min(values), max(values)
    return any(lo < t < hi for t in (CHAR, SCORCH))


def refine(bm, dmg, press):
    """Cuts the edges of the faces the camera sees: where a burn's contour crosses them (so that it can be cut into
    them) until shorter than FINE_BURN, by the cracks and pits (where they are pressed in) until shorter than FINE."""
    for i in range(3):
        edges = set()
        for f in bm.faces:
            if not seen(f.normal):
                continue
            if i < 2 and f.normal.y < -0.4 and crossed(f, dmg):
                edges |= {e for e in f.edges if e.calc_length() > FINE_BURN}
            elif press and dmg.near(f.calc_center_median()):
                edges |= {e for e in f.edges if e.calc_length() > FINE}
        if not edges:
            break
        bmesh.ops.subdivide_edges(bm, edges=list(edges), cuts=1, use_grid_fill=True)
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3])
        bm.normal_update()


def restore_normals(obj, source, everywhere):
    """The part's corner normals as they were (source: a NormalSource of the undamaged part) within FADE[0] of the cuts,
    where nothing moved (so that the pieces meet intact ones without a seam in their shading), or everywhere."""
    mesh = obj.data
    normals = [tuple(n.vector) for n in mesh.corner_normals]
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            co = mesh.vertices[mesh.loops[li].vertex_index].co
            if everywhere or near_cut(co.x) < FADE[0] + 0.02:
                n = source.normal(co, poly.center)
                if n is not None:
                    normals[li] = tuple(n)
    mesh.normals_split_custom_set(normals)


def damage(obj, dmg, m, press=True):
    """Burns and dents a part (its modifiers applied, upright): finer faces by the cracks, its faces cut along the
    burns' contours, repainted (black where burnt, a shade darker where scorched), pressed in along its normals where
    the camera sees it (nothing near the cuts)."""
    names = {mat.name: key for key, mat in m.items()}
    source = mk.NormalSource(obj)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.normal_update()
    refine(bm, dmg, press)
    values = {v: dmg.burn(v.co) for v in bm.verts}
    for threshold in (CHAR, SCORCH):
        mk.split_along(bm, values, threshold)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    bm.normal_update()
    slots = list(obj.data.materials)

    def slot(key):
        if m[key] not in slots:
            obj.data.materials.append(m[key])
            slots.append(m[key])
        return slots.index(m[key])
    for f in bm.faces:
        key = names.get(slots[f.material_index].name) if f.material_index < len(slots) else None
        if key is None:
            continue
        b = sum(values.get(v, 0.0) for v in f.verts) / len(f.verts)
        if b > CHAR:
            key = "char"
        elif b > SCORCH:
            key = SCORCHED.get(key, key)
        f.material_index = slot(key)
    moved = False
    if press:
        for v in bm.verts:
            facing = smoothstep(0.25, 0.7, -v.normal.y)     # pressed where the camera looks at it squarely
            if facing > 0.0:
                dd = dmg.depth(v.co) * facing
                if dd > 1e-4:
                    v.co -= v.normal * dd
                    moved = True
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    if moved:
        mk.shade(obj, 35)
    restore_normals(obj, source, not moved)
    return obj


def strips(name, targets, dmg, m):
    """The cracks: glowing strips along them, each edge point dropped onto the parts along the camera's view and lifted
    a little off them, narrowing to their ends, wider and red where they glow hottest."""
    verts, tris = [], []
    for obj in targets:
        base = len(verts)
        verts += [obj.matrix_world @ v.co for v in obj.data.vertices]
        obj.data.calc_loop_triangles()
        tris += [tuple(base + i for i in t.vertices) for t in obj.data.loop_triangles]
    bvh = BVHTree.FromPolygons(verts, tris)
    bm = bmesh.new()
    keys = []

    def lay(run):
        for (l0, r0, n0, h0), (l1, r1, n1, h1) in zip(run, run[1:]):
            face = bm.faces.new([bm.verts.new(c) for c in (l0, r0, r1, l1)])
            face.normal_update()
            if face.normal.dot(n0 + n1) < 0:
                face.normal_flip()
            keys.append("ember_hot" if (h0 + h1) / 2 > 0.45 else "ember")

    for line in dmg.lines:
        points, along = resample(line, STRIP_STEP)
        total = along[-1]
        run = []
        for i, (x, y) in enumerate(points):
            a, b = points[max(i - 1, 0)], points[min(i + 1, len(points) - 1)]
            tx, ty = b[0] - a[0], b[1] - a[1]
            length = math.hypot(tx, ty) or 1.0
            sx, sy = -ty / length, tx / length
            heat = dmg.heat(x, y)
            ends = smoothstep(0.0, 0.6, along[i]) * smoothstep(0.0, 0.6, total - along[i])
            w = (STRIP_HALF + STRIP_HOT * heat) * (0.35 + 0.65 * ends)
            hits = []
            for sign in (1.0, -1.0):
                origin = Vector((x + sx * w * sign, -30.0, y + sy * w * sign))
                direction = Vector((0.0, 1.0, 0.0))
                loc, normal, _, _ = bvh.ray_cast(origin, direction)
                if loc is None:
                    break
                if normal.dot(direction) > 0:
                    normal = -normal
                hits.append((loc + normal * STRIP_LIFT, normal))
            if len(hits) < 2:
                lay(run)
                run = []
                continue
            run.append((hits[0][0], hits[1][0], hits[0][1] + hits[1][1], heat))
        lay(run)
    if not keys:
        bm.free()
        return None
    names = sorted(set(keys))
    mesh = bpy.data.meshes.new(name)
    for key in names:
        mesh.materials.append(m[key])
    bm.faces.ensure_lookup_table()
    for f, key in zip(bm.faces, keys):
        f.material_index = names.index(key)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return k.smooth(obj, 60)


def dead_port(m):
    """The port's glow out: the lens dark, a dying ember at its heart; the strip along the port's floor dead."""
    lx, lh, lr = cn.LENS
    for obj in mk.meshes():
        base = obj.name.split(".")[0]
        if base == "lens":
            cn.paint(obj, m, lambda c, n: "ember_dim" if math.hypot(c.x - lx, c.z - lh) < EMBER_HEART * lr else "char")
        elif base == "glow_strip":
            cn.paint(obj, m, lambda c, n: "seam")


def damaged_parts(m):
    """polish_deli_cannon.py's parts, upright (split along the cuts as that script splits them), damaged as the
    damaged sprites draw them, the cracks laid on them."""
    parts = cn.upright_parts(m)
    dmg = Damage(SEED)
    for obj in parts:
        base = obj.name.split(".")[0]
        if base in UNTOUCHED:
            continue
        damage(obj, dmg, m, press=base in PRESSED)
    dead_port(m)
    bpy.context.view_layer.update()
    strips("cracks", [o for o in parts if o.name.split(".")[0] not in UNTOUCHED], dmg, m)
    bpy.context.view_layer.update()


def build():
    options = k.args()

    def make(mirror):
        m = materials()
        return cn.build_whole(m, mirror, damaged_parts), m
    cn.run(options, "cannon_dmg", (PIECES, PIECES_L), make, layout=LAYOUT)


if __name__ == "__main__":
    build()
