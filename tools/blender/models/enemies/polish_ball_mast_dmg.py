"""DELI's gun on the mast over the ball, burnt: sheet C sprites 229 above 267 (2x2 each), the damaged looks of 245 and
283 (enemies 145 and 146 of DELI and New Deli; VAULT and DELI RUIN show 267 under no gun), which the game shows in
their place. models.cfg: model ball_mast_dmg_gun / ball_mast_dmg_ball ... origin; sprite c 229 ball_mast_dmg_gun yaw=0
height=-4, sprite c 267 ball_mast_dmg_ball yaw=0 height=-4 (as the intact pieces). Polished (2026-10-21; it replaces
wave3_ao_deli.py's mast_damaged_whole() and mast_damaged_piece(), which burnt wave3_x_tower.py's old mast pixel by
pixel).

The mast is polish_ball_mast.py's (its parts imported, unchanged), built whole, damaged as the damaged sprites draw it,
leaned and cut along the sprites' edge (y = 0) into the same two pieces at the same origins, so that a damaged piece
meets its partner, damaged or not: the rods, the only parts across the cut, keep their shape (only their paint
changes), and the intact fin ends above the cut.

What C 229 and 267 draw differently from C 245 and 283 (pixel by pixel; no sprite of any sheet is either mirrored,
turned or in other ramps):
- every blue and pale blue part burnt grey: the strip along the barrel's face, the rods, the ball's panels;
- the gun burnt black from the barrel's underside (columns 7-12 of row 6) down through the grip and the receiver's front
  (columns 9-16 of rows 7-11), the lower barrel's back half darkened (columns 6-8), the stub scorched, the receiver's
  foot grey metal (columns 13-15 of rows 12-14); in the black, dark red embers in cracks crossing like a double cross:
  along row 9 (columns 9-14) and down columns 11 (rows 7-11) and 13 (rows 8-11);
- the fin shot away: only its grey mounting arm is left, curving up out of the receiver over to the right and down
  (columns 15-21 of rows 8-14), its end torn; a charred lump of it stuck beside the yoke's right arm (columns 16-19 of
  rows 17-20); the yoke as it was;
- the ball burnt grey all over, its pale left panel black with two red cracks down it (columns 4 and 6 of rows 3-7)
  and pitted, its lower half dark, a red crack down the right of its middle band (column 14 of rows 11-14) turning
  across its foot (columns 10-12 of rows 14-15), the metal there dented.
How: the parts' faces are repainted by maps of burns (rounded patches in the picture's coordinates, their edges made
ragged by noise and cut along smooth contours: polish_sphere_nozzle's split_along; each face judged by its vertices'
mean, which the cuts keep on one side), the blue paint mapped to greys, the ball's grey mottled with soot (noise
contours, where the camera looks); the burnt panel and the cracked foot pressed in and crumpled (finer faces first,
where the cracks run); the cracks are jagged glowing strips laid where the camera sees them (on the ball along the game
camera's direction, on the gun from above), dark red, red where they cross, glowing well under 1 (0.3 and 0.45), in
grooves pressed under them, pits at their ends. The fin's arm is a bent round bar, its end jagged and black, a black
shred of the fin's skin inside its bend; the lump a squashed, lumpy ball. The ball's panels keep a little light of
their own (scorched greys, 0.05-0.12).

Coordinates as in polish_ball_mast.py: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the floor; the
whole's origin the middle of the sprites' common edge (column c of the picture is x = c + 0.5 - 12, row r y = 27.5 -
r). The gun's damage is placed by the picture seen from straight above, the ball's by the picture the game's camera
sees (the ball's bands are set for that camera).

Replaces wave3_ao_deli.py's burnt mast: remove M_INT, M_DMG, mast_damaged_whole() with its x.whole("mast_damaged",
(24, 56)) registration, mast_damaged_piece() and the ball_mast_dmg_gun / ball_mast_dmg_ball model loop, and the
ball_mast_dmg bullet of its docstring; and wave3_ao_art.py's MAST_DMG (only M_DMG reads it). The tower's and the
cannons' damaged looks stay (deli_painter() and holes_of() too).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the whole's and each piece's
silhouette against enemy_C.png, the floor left out), --preview <prefix>, --only <name,...>, --whole <file.glb>.
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
import polish_ball_mast as bmast  # noqa: E402

PIECES = [("ball_mast_dmg_gun", 229, (-12.0, 12.0, 0.0, 28.0)), ("ball_mast_dmg_ball", 267, (-12.0, 12.0, -28.0, 0.0))]
SEED = 229

# --- The damage maps -------------------------------------------------------------------------------------------------
# Burns: rounded rectangles in the picture's coordinates (x0, x1, y0, y1, corner radius, how burnt: 1 black, 0.5
# scorched); their edges ragged (noise: amplitude, frequency). Faces burnt above CHAR are black, above SCORCH scorched.
GUN_BURNS = [(-3.35, 3.4, 16.1, 21.25, 0.8, 1.0),     # the grip's top, the receiver's front, the barrel's underside
             (-3.3, 0.2, 12.5, 16.6, 0.6, 0.82),      # the grip's foot
             (-5.6, 3.4, 19.8, 21.3, 0.5, 1.0),       # the lower barrel's back half
             (3.4, 5.8, 15.6, 22.2, 0.6, 0.85),       # the receiver's back
             (-6.8, -2.0, 12.6, 16.4, 0.8, 0.55)]     # the stub
BALL_BURNS = [(-8.9, -2.9, -8.4, -3.2, 1.6, 1.0),     # the pale left panel
              (-2.6, 3.3, -16.0, -11.0, 2.2, 0.85),   # round the cracked foot of the middle band
              (-9.5, 9.5, -20.0, -12.4, 2.0, 0.42)]   # the lower half, scorched dark
RAGGED = {"gun": (0.16, 0.85), "ball": (0.38, 1.05)}
CHAR, SCORCH = 0.62, 0.3
MOTTLE = (0.55, 0.3)             # soot mottling the ball's grey: noise frequency, darker above this
# The cracks: lines (picture coordinates) made jagged (a point every JAG_STEP moved up to JAG across); their strips'
# half-width (wider where they cross: HOT spots, (x, y), radius) and lift off the surface; the grooves under them;
# the pits at their ends ((x, y), radius).
GUN_CRACKS = [[(-3.0, 18.5), (-1.6, 18.62), (-0.5, 18.45), (0.6, 18.55), (1.5, 18.5), (2.9, 18.56)],
              [(-0.5, 21.1), (-0.46, 19.8), (-0.55, 18.5), (-0.48, 17.3), (-0.52, 16.2)],
              [(1.5, 20.3), (1.55, 19.2), (1.46, 18.0), (1.52, 16.2)]]
GUN_HOT = [((-0.5, 18.5), 0.9), ((1.5, 18.5), 0.8)]
BALL_CRACKS = [[(-7.5, -3.4), (-7.42, -4.6), (-7.58, -5.9), (-7.46, -7.0), (-7.52, -8.1)],
               [(-5.5, -3.3), (-5.44, -4.5), (-5.56, -5.7), (-5.47, -6.8), (-5.5, -7.9)],
               [(2.5, -11.2), (2.44, -12.3), (2.56, -13.5), (2.42, -14.6)],
               [(-2.2, -15.1), (-1.1, -14.86), (0.1, -15.02), (1.3, -14.76), (2.42, -14.6)]]
BALL_HOT = [((-7.5, -5.5), 0.9), ((-5.5, -5.0), 0.7), ((2.45, -13.4), 0.8), ((2.42, -14.6), 0.6)]
JAG_STEP, JAG = 0.5, 0.16
STRIP_HALF, STRIP_HOT, STRIP_LIFT, STRIP_STEP = 0.17, 0.12, 0.06, 0.28
GROOVE_HALF, GROOVE_DEPTH = 0.6, 0.32
BALL_PITS = [((-7.52, -8.3), 0.62), ((-5.5, -3.0), 0.5), ((2.5, -11.0), 0.5), ((-2.4, -15.15), 0.5)]
PIT_DEPTH = 0.5
# Dents on the ball ((x, y), radius, depth) and the crumpling in its burns (amplitude, frequency).
BALL_DENTS = [((-5.9, -5.6), 3.0, 0.55), ((0.6, -13.6), 2.8, 0.42)]
CRUMPLE = (0.12, 0.8)
# The fin's arm left on the receiver: its path (x, y on the picture, radius), its end torn; the charred lump of the fin
# beside the yoke ((x, y), radii (x, d, h)).
FIN_ARM = [(3.8, 16.3, 1.0), (4.7, 18.0, 1.0), (5.9, 19.4, 1.0), (7.3, 19.95, 1.02), (8.5, 19.4, 1.08),
           (9.05, 17.9, 1.15), (9.0, 16.1, 1.15), (8.7, 14.6, 1.05), (8.45, 13.3, 0.8)]
SHRED = [(5.5, 16.7), (6.1, 18.2), (7.3, 18.8), (8.1, 18.1), (8.0, 16.3), (7.4, 15.4), (6.6, 16.1)]
LUMP = ((5.7, 9.3), (1.95, 0.95, 1.65))
# The fine faces where cracks and pits are pressed: edges are cut until shorter than this near them.
FINE = 0.75


def materials():
    """polish_ball_mast.py's materials and the damage's: blacks and scorched greys (the ball's with a little light of
    their own) and the embers."""
    pal = k.level_palette()
    m = bmast.materials()

    def mat(name, index, metallic=0.45, roughness=0.5, glow=0.0):
        if glow > 0:
            return k.material(name, palette=index, metallic=metallic, roughness=roughness, emission=pal[index],
                              emission_strength=glow)
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)
    m.update({
        "char": mat("mastd_char", 0x02, 0.2, 0.62),
        "soot": m["shadow"],
        "scorch": m["grey_dark"],
        "ash": mat("mastd_ash", 0x06, 0.45, 0.42),
        "metal": m["grey"],
        "ball_char": mat("mastd_ball_char", 0x02, 0.2, 0.66, 0.05),
        "ball_soot": mat("mastd_ball_soot", 0x05, 0.35, 0.58, 0.1),
        "ball_ash": mat("mastd_ball_ash", 0x07, 0.4, 0.52, 0.12),
        "ball_metal": mat("mastd_ball_metal", 0x08, 0.45, 0.46, 0.12),
        "ember": mat("mastd_ember", 0x72, 0.0, 0.45, 0.3),
        "ember_hot": mat("mastd_ember_hot", 0x74, 0.0, 0.4, 0.45),
    })
    return m


# What each intact material becomes: burnt grey all over (no blue is left), darker where scorched.
BURNT = {"pale_lit": "steel", "pale": "metal", "pale_dark": "scorch", "sky": "steel", "blue_lit": "metal",
         "blue": "scorch", "blue_dark": "soot", "ball_cap": "ball_metal", "ball_pale": "ball_ash",
         "ball_grey": "ball_ash", "ball_blue": "ball_soot", "ball_dark": "ball_soot", "ball_window": "ball_ash"}
SCORCHED = {"steel": "scorch", "steel_lit": "metal", "glint": "metal", "grey": "scorch", "metal": "scorch",
            "grey_dark": "soot", "scorch": "soot", "shadow": "char", "soot": "char", "ash": "scorch",
            "ball_metal": "ball_ash", "ball_ash": "ball_soot", "ball_soot": "ball_soot", "seam": "seam"}


# --- Where the camera sees the damage ---------------------------------------------------------------------------------

CAM_UP = Vector((0.0, math.cos(math.radians(bmast.CAMERA)), math.sin(math.radians(bmast.CAMERA))))
CAM_VIEW = Vector((0.0, math.sin(math.radians(bmast.CAMERA)), -math.cos(math.radians(bmast.CAMERA))))


def pic_plan(p):
    """A point's place on the picture seen from straight above (the gun's damage)."""
    return (p.x, p.y)


def pic_camera(p):
    """A point's place on the picture the game's camera sees, about the ball's middle (the ball's damage)."""
    return (p.x, bmast.BALL_C.y + (Vector(p) - bmast.BALL_C).dot(CAM_UP))


def ray_plan(x, y):
    return Vector((x, y, 200.0)), Vector((0.0, 0.0, -1.0))


def ray_camera(x, y):
    origin = bmast.BALL_C + Vector((x, 0.0, 0.0)) + CAM_UP * (y - bmast.BALL_C.y)
    return origin - CAM_VIEW * 200.0, CAM_VIEW.copy()


def rounded_rect_sdf(x, y, x0, x1, y0, y1, r):
    cx, cy, hw, hh = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2, (y1 - y0) / 2
    return mk.rounded_rect_distance(x - cx, y - cy, hw, hh, min(r, hw, hh))


class Damage:
    """The burns, cracks, pits and dents of one part of the mast (the gun's or the ball's), in picture coordinates."""

    def __init__(self, burns, cracks, hot, pits, dents, pic, ray, seed, ragged):
        self.burns, self.hot, self.pits, self.dents, self.ragged = burns, hot, pits, dents, ragged
        self.pic, self.ray = pic, ray
        rng = random.Random(seed * 7919)
        self.lines = [jagged(line, rng) for line in cracks]
        self.offset = Vector((seed * 3.17, -seed * 1.91, seed * 0.77))

    def burn(self, p):
        """How burnt (0 as it was, 1 black) at a point: the patches' blend, their edges ragged."""
        x, y = self.pic(p)
        a, f = self.ragged
        wob = a * noise.noise(Vector((x * f, y * f, 0.0)) + self.offset)
        best = 0.0
        for x0, x1, y0, y1, r, level in self.burns:
            d = rounded_rect_sdf(x, y, x0, x1, y0, y1, r) + wob * 2.0
            best = max(best, level * (1.0 - mk.smoothstep(-0.35, 0.35, d)))
        return best

    def crack(self, p):
        """The distance to the nearest crack on the picture."""
        x, y = self.pic(p)
        best = 1e9
        for line in self.lines:
            for (ax, ay), (bx, by) in zip(line, line[1:]):
                dx, dy = bx - ax, by - ay
                t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / max(dx * dx + dy * dy, 1e-9)))
                best = min(best, math.hypot(x - ax - t * dx, y - ay - t * dy))
        return best

    def heat(self, x, y):
        return max([1.0 - mk.smoothstep(0.0, 2.0 * r, math.hypot(x - c[0], y - c[1])) for c, r in self.hot] + [0.0])

    def depth(self, p):
        """How far the surface is pressed in at p: the dents, the crumpling in the burns, the grooves, the pits."""
        x, y = self.pic(p)
        d = 0.0
        for (cx, cy), r, depth in self.dents:
            t = math.hypot(x - cx, y - cy) / r
            if t < 1:
                d += depth * (1 - t * t) ** 2
        b = self.burn(p)
        if b > SCORCH:
            a, f = CRUMPLE
            d += b * a * (0.6 + noise.noise(Vector((x * f, y * f, 1.3)) + self.offset))
        c = self.crack(p)
        if c < GROOVE_HALF:
            d += GROOVE_DEPTH * (1 - (c / GROOVE_HALF) ** 2)
        for (cx, cy), r in self.pits:
            t = math.hypot(x - cx, y - cy) / r
            if t < 1:
                d += PIT_DEPTH * (1 - t * t) ** 1.5
        return d

    def mottle(self, p):
        """Soot mottling (noise over the picture): faces above MOTTLE's threshold are a shade darker."""
        x, y = self.pic(p)
        f = MOTTLE[0]
        return noise.noise(Vector((x * f, y * f, 2.7)) - self.offset)

    def near(self, p, reach=0.75):
        """Whether p needs fine faces: by a crack, a pit or a dent's rim."""
        x, y = self.pic(p)
        return self.crack(p) < reach or any(math.hypot(x - c[0], y - c[1]) < r + reach for c, r in self.pits)


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


# --- Damaging a part --------------------------------------------------------------------------------------------------

def seen(n, ball):
    """Whether a face with normal n faces the view its damage is placed by (the camera's for the ball, above for the
    gun)."""
    return (-CAM_VIEW).dot(n) > 0.05 if ball else n.z > 0.05


def refine(bm, dmg, ball):
    """Cuts the edges of the faces by the cracks and pits (where the camera sees them) until shorter than FINE."""
    for _ in range(2):
        edges = set()
        for f in bm.faces:
            if seen(f.normal, ball) and dmg.near(f.calc_center_median()):
                edges |= {e for e in f.edges if e.calc_length() > FINE}
        if not edges:
            break
        bmesh.ops.subdivide_edges(bm, edges=list(edges), cuts=1, use_grid_fill=True)
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3])
        bm.normal_update()


def damage(obj, dmg, m, ball=False, press=True, mottled=False, smooth_angle=40.0):
    """Burns, dents and grooves a part (its modifiers applied, in the world): finer faces by the cracks, its faces
    cut along the burns' contours, repainted (every blue to grey, darker where scorched, black where burnt), pressed in
    along its undamaged normals where it is seen."""
    names = {mat.name: key for key, mat in m.items()}
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.normal_update()
    if press:
        refine(bm, dmg, ball)
    # The fields per vertex, the faces cut along their contours (new vertices take the threshold); a face is then
    # judged by its vertices' mean, which the cuts keep on one side of each contour.
    fields = {"burn": {v: dmg.burn(v.co) for v in bm.verts}}
    cuts = [("burn", CHAR), ("burn", SCORCH)]
    if mottled:   # only where the camera looks: no cuts round the back
        fields["mottle"] = {v: dmg.mottle(v.co) if seen(v.normal, ball) else -1.0 for v in bm.verts}
        cuts.append(("mottle", MOTTLE[1]))
    for key, threshold in cuts:
        values = fields[key]
        made = mk.split_along(bm, values, threshold)
        for other, vals in fields.items():
            for v in made:
                if v not in vals:
                    vals[v] = threshold if other == key else (dmg.burn(v.co) if other == "burn" else dmg.mottle(v.co))
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    bm.normal_update()
    slots = list(obj.data.materials)

    def slot(key):
        if m[key] not in slots:
            obj.data.materials.append(m[key])
            slots.append(m[key])
        return slots.index(m[key])

    def mean(key, f):
        vals = fields[key]
        return sum(vals.get(v, 0.0) for v in f.verts) / len(f.verts)
    for f in bm.faces:
        key = names.get(slots[f.material_index].name, None) if f.material_index < len(slots) else None
        if key is None:
            continue
        key = BURNT.get(key, key)
        b = mean("burn", f)
        if b > CHAR:
            key = "ball_char" if ball else "char"
        elif b > SCORCH or (mottled and mean("mottle", f) > MOTTLE[1]):
            key = SCORCHED.get(key, key)
        f.material_index = slot(key)
    if press:
        for v in bm.verts:
            if seen(v.normal, ball):
                v.co -= v.normal * dmg.depth(v.co)
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    return k.smooth(obj, smooth_angle)


def resample(points, step):
    out, along = [points[0]], [0.0]
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        length = math.hypot(x1 - x0, y1 - y0)
        n = max(1, round(length / step))
        for i in range(1, n + 1):
            out.append((x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n))
            along.append(along[-1] + length / n)
    return out, along


def strips(name, targets, dmg, m):
    """The cracks over damaged parts: glowing strips along them, each edge point dropped onto the parts along the view
    the damage is placed by and lifted a little off them, narrowing to their ends, wider and red where they glow
    hottest."""
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
            ends = mk.smoothstep(0.0, 0.6, along[i]) * mk.smoothstep(0.0, 0.6, total - along[i])
            w = (STRIP_HALF + STRIP_HOT * heat) * (0.35 + 0.65 * ends)
            hits = []
            for sign in (1.0, -1.0):
                origin, direction = dmg.ray(x + sx * w * sign, y + sy * w * sign)
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


# --- What is new: the fin's arm and the lump -------------------------------------------------------------------------

def fin_arm(m):
    """The fin's grey mounting arm, left on the receiver once the fin is shot away: a bent round bar curving up and over
    to the right and down, its end torn (jagged, black); built upright in the fin's plane."""
    d = bmast.D0 + bmast.FIN_D + 0.3
    pts = [(x, d, bmast.h_at(y, d), r) for x, y, r in FIN_ARM]
    arm = mk.smooth_tube("fin_arm", pts, m["metal"], 14)
    rng = random.Random(SEED)
    end = Vector(pts[-1][:3])
    for v in arm.data.vertices:
        t = (v.co - end).length
        if t < 1.2:
            v.co += Vector((rng.uniform(-0.18, 0.18), rng.uniform(-0.12, 0.12), rng.uniform(-0.25, 0.1))) * (1.2 - t)
    arm.data.update()
    k.smooth(arm, 55)
    mk.paint(arm, lambda c, n: m["char"] if (Vector(c) - end).length < 0.9 else m["steel_lit"] if n.y < -0.6 and
             n.z > 0.2 else m["scorch"] if n.z < -0.4 else None)
    return arm


def shred(m):
    """The fin's burnt skin left inside its arm: a thin jagged plate, black, crumpled a little."""
    d = bmast.D0 + bmast.FIN_D + 0.1
    outline = [(x, bmast.h_at(y, d)) for x, y in SHRED]
    obj = mk.prism("shred", outline, d - 0.28, d + 0.28, m["char"], axis="y")
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=2, use_grid_fill=True)
    off = Vector((SEED * 0.61, -2.3, 0.4))
    for v in bm.verts:
        v.co.y += 0.35 * noise.noise(v.co * 0.9 + off)
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    k.recalc_normals(obj)
    k.smooth(obj, 50)
    return obj


def lump(m):
    """The charred lump of the fin stuck beside the yoke's right arm: a squashed, lumpy ball, black."""
    (x, y), (rx, rd, rh) = LUMP
    d = bmast.D0 - 0.2
    centre = Vector((x, d, bmast.h_at(y, d)))
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0)
    off = Vector((SEED * 0.37, 1.7, -0.9))
    for v in bm.verts:
        dvec = v.co.normalized()
        s = 1.0 + 0.28 * noise.noise(dvec * 1.8 + off)
        v.co = centre + Vector((dvec.x * rx, dvec.y * rd, dvec.z * rh)) * s
    mesh = bpy.data.meshes.new("lump")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("lump", mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(m["char"])
    k.smooth(obj, 70)
    return obj


# --- The whole --------------------------------------------------------------------------------------------------------

def build_whole(m):
    """The intact mast's parts (but the fin), the fin's arm, its shred and the lump, leaned; then the gun and the ball
    damaged as the damaged sprites draw them and the cracks laid on them."""
    sphere = bmast.ball(m)
    mk.apply(sphere)
    bmast.lean([sphere], bmast.BALL_TO_WORLD)
    bmast.rods(m)
    bmast.yoke(m)
    bmast.barrels(m)
    bmast.grip(m)
    bmast.receiver(m)
    fin_arm(m)
    shred(m)
    lump(m)
    mast = [o for o in mk.meshes() if o is not sphere]
    for obj in mast:
        mk.apply(obj)
    bmast.lean(mast)
    bmast.floor_cut([sphere] + mast)
    bpy.context.view_layer.update()
    gun = Damage(GUN_BURNS, GUN_CRACKS, GUN_HOT, [], [], pic_plan, ray_plan, SEED, RAGGED["gun"])
    ball_dmg = Damage(BALL_BURNS, BALL_CRACKS, BALL_HOT, BALL_PITS, BALL_DENTS, pic_camera, ray_camera, SEED + 38,
                      RAGGED["ball"])
    pressed = {"grip", "receiver", "barrel", "barrel2"}
    for obj in mast:
        base = obj.name.split(".")[0]
        if base in ("lump", "shred"):
            continue
        damage(obj, gun, m, press=base in pressed)
    damage(sphere, ball_dmg, m, ball=True, mottled=True)
    bpy.context.view_layer.update()
    strips("cracks_gun", [o for o in mast if o.name.split(".")[0] in pressed], gun, m)
    strips("cracks_ball", [sphere], ball_dmg, m)
    bpy.context.view_layer.update()
    return [o for o in mk.meshes() if len(o.data.polygons) > 0]


def build():
    options = k.args()
    k.reset()
    m = materials()
    whole = build_whole(m)
    print("whole damaged mast: %d triangles, %d objects" % (mk.triangles(whole), len(whole)))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    sprite_masks = None
    if "check" in options:
        sprite_masks = bmast.check(whole, os.path.join(options["check"], "enemy_C.png"), 229, 267,
                                   "whole (C 229 above 267)")
    if "preview" in options:
        mk.preview(options["preview"] + "ball_mast_dmg_whole", whole, size=(24, 56), scale=10, distance=1.6)
    if "whole" in options:
        mk.export(whole, options["whole"])
    bmast.export_pieces(whole, m, options, PIECES, sprite_masks)


if __name__ == "__main__":
    build()
