"""FLEET's and STATION's walker (sheet o, 31 2x2 sprites put together as one 192 x 140 picture) and the hatches in its
three bays (o 191 beside o 193; FLEET and DELI RUIN), with the hatches' lid opening as frame models; polished
(2026-10-22, round 36). It replaces wave3_am.py (the walker and the hatches: heightfields painted pixel by pixel, kit
wave3_am_kit.py, pixels wave3_am_art.py).

Where they appear (tools/content/tyrevents.py 3 FLEET, 5 STATION; episode 6 DELI RUIN):
- FLEET t 5020 (the boss, link 254 and the boss bar): custom ground enemies of bank 19 (events 49, armour 254; 118 and
  126 armour 60, links 141 and 42) 39-53 at (60 + 24 i, y - 84), 77-91 at (60 + 24 i, y - 56), 118-126 at (96 + 24 i,
  y - 28); the feet, enemies 735 (156) and 736 (164) at (96, y) and (192, y) (ground 2, links 141 and 42, armour 60,
  gun 133); 28 ticks (one row of scroll) later 1-15 at (60 + 24 i, y - 84) on ground 2 (event 52): the sheet's 192 x 140
  layout, its pixel (c, r) at the level's (c + 60, r - 112). The hatches (enemies 737 738, ground 2, armour 60, link
  254, launching enemy 703 (K 245, the core pod) every 80 ticks) at (68, y - 98) (92, ..), (195, ..) (219, ..) and
  (131, y - 68) (155, ..): over the walker's three bays, at the sheet's (8, 42), (135, 42) and (71, 72). All of it
  moves as one (the three links always get the same moves).
- STATION t 3320: the same walker (armour 255/60), but no hatches: its bays show the hull's own hatches.
- DELI RUIN (episode 6) takes FLEET's boss block (its placement "boss", episode 3, FLEET, at 5800), but the composer
  copies no custom enemies (events 49-52 are not in episode6/waves.py SPAWNS) and the feet's links are not the boss's:
  only the three hatches come, lying on the floor (at (68, ..) etc. as in FLEET).
The pieces are enemy 0 with their sprite (no animation, dgr 0: no damaged look); the hatches animate when they launch
(animate 2): 191 195 199 203 229 229 203 203 199 199 195 195 191 (and 193 197 201 205 231 ... 193): frame models
(no other enemy, launched ones included, shows o 195-231). No other sprite has these pixels; the walker is its own
mirror image about the middle of its column 95 (coverage IoU 0.985; the shading lit from the upper left): built
symmetric.

THE WALKER (fleet_walker_1 ... 164): as the sprites draw it (the picture's columns and rows, the left half; the right
half its mirror image): two broad shoulder pods, their tops of blue armour plate (columns 5-51 of rows 20-41: a light
blue bevel down the outer diagonal edge, a darker band along the front, a dark slot in it) with a grey strap (columns
41-48), a turret on each pod's back edge (columns 42-59 of rows 8-20: a box, its barrel's breech rising out of its back,
a white lamp) and a small box with a knob beside it (columns 30-42); under the armour the bay of a hatch (columns 9-54
of rows 44-66), a ribbed rail down the pod's outer side and a round rail down its inner side, the pod's lower body
(rows 64-83) chamfered at its outer corner, a grille of slats (columns 25-49 of rows 66-75) and two blue slots in it.
Between the pods the head: a raised grey block (rows 10-37) with vents along its back edge (rows 11-15), its shoulders
falling along a bevel to a deck beside the pods (rows 21-29), dark cavities and blue cheeks beside the nose (columns
70-88); the blue horseshoe's arms (columns 56-77 of rows 28-61) and its band under the head (rows 37-41) round a great
glossy black eye in a dark socket (columns 82-109 of rows 41-58), a thick grey bumper curving under it (rows 53-68);
under the bumper a box (rows 68-102) with the third bay in its blue frame, grey blocks along its lower edge, a tab up
to the bumper; hips (columns 56-68 of rows 56-84: a dark bed, two ball joints, pistons) and the legs reaching down the
screen (columns 40-57: the mount under the pod with an axle across it, the strut, two rods, a clamp, the housing, a
round armoured foot with a ringed hub and a lens, rows 120-131).
Built as such a machine: the armour, the pods round their bays (the bays holes through them, 0.15 outside the hatches'
frames, so the hatch enemies sit in them), the collar's arms: constrained Delaunay tops over the outlines of their
pixel masks (polish_ring_machine.relief; the outline through the midpoints of the boundary edges, smoothed; the
sprite's dark outline pixels given to the part beside them), their edges rounded, steps along mesh lines (the
strap, the slot, the grille and its slats, the slots, the front band); the head, the box, the hips, the legs and the
turrets the same kind of solid over hand-traced outlines (the head's shoulder a bevel along its edge, the cavities and
cheeks between contours a quarter pixel apart); the bumper a loft of rounded-box sections along its curve; the eye a
glossy ellipsoid with its glint banded on (polish_orb_red.band_split), the ball joints the same, lit towards the sun;
the rails, pistons, rods, barrels and the foot's ring tubes; the foot a dome. Faces are painted by how they meet the
game's sun (shade_by_sun: five shades of each part's ramp). In each bay the walker has its own hatch, flat (heights
times 0.28, all under the hatch enemy's floor): STATION, which puts no hatch enemies in them, shows those; FLEET's
hatch enemies cover them. Heights: z 0 the walker's base (the ground enemies' layer, 4 over the terrain: no height
option, so that it stays over STATION's background 2, drawn 2 over the terrain under the ground enemies); the bays'
floors 0, the lower bodies 11.2, the armour 14, the bumper 15.2, the turrets 16.4 (their barrels 19), the head 19.2;
the legs 7-8, the feet 5.2 (the old walker rose to 41: through FLEET's sky enemies).

THE HATCH (fleet_hatch_l, fleet_hatch_r; frames 195/197, 199/201, 203/205, 229/231): as the sprites draw it (48 x 28,
the picture's columns and rows): a raised steel frame (columns 1-46 of rows 2-23: a dark band, lit along its outer
top and left edge) round a dark lid (columns 5-42 of rows 5-19, a gap of shadow round it): a raised stepped plate in
its middle (columns 10-38 of rows 11-18 and 15-33 of rows 8-10), two vent slits at each side (rows 14 and 16), two
short seams above the plate, a lit rail along the lid's lower edge (row 19) broken where the seams run. The frames
swing the lid open on a hinge along its top edge: its visible part shrinks towards the hinge (cos 51, 60, 72, 80
degrees: the rail, seen as a lit bar, rises from row 19 to rows 14, 12, 9, 7) over the black well under it. Built as a
frame ring (a constrained Delaunay top over its outline with a chamfer along its outer edge), a black floor, and the
lid (the same kind of top: the plate's bevels, the slits and the seams as mesh lines), hinged at y = HINGE.
Heights: its foot on z 0 (the walker's base: it sits at the bottom of the walker's bay), the frame's top at 3.4, the
lid 2.5, the well's floor 1.0; the open lid rises to about 18.

Built in the picture's plane (x, y as the sprites draw them, z up) and sheared along the game camera's line of sight
(y - z tan 20, the normals with it: polish_lemon_beetle's shear_to_camera), so that the camera sees every point where
the sprites draw it; cut in the plane along the sprites' edges (polish_coral_manta.cut; the caps dark grey), each
piece moved so that its sprite's middle is its origin, triangulated (polish_k_pod.triangulate), joined
(polish_deli_boss.join), at most 15 materials a piece (the rarest merged into the nearest shade of their ramp:
merge_materials). Deterministic: no random numbers, no booleans.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up. The walker's whole: origin at its
picture's middle (pixel edge 96, 70): column c's left edge is x = c - 96, row r's top edge y = 70 - r; a piece whose
sprite's top left pixel is (c0, r0) has its origin at (c0 - 84, 56 - r0); the mirror line is x = -0.5 (the middle of
column 95). The hatch's whole: origin at its picture's middle (pixel edge 24, 14): x = c - 24, y = 14 - r; 191's
origin (-12, 0), 193's (12, 0); in the walker its middle at the bays' (BAYS).

The helpers here (mask_loops, InsideDistance, export_pieces, merge_materials, shear_to_camera) serve
polish_pincer_boss.py and polish_k_lampgun.py too.

Replaces wave3_am.py, wave3_am_kit.py and wave3_am_art.py (all of them: delete them; nothing else imports them) and so
wave3_aj_kit.py and wave3_aj_art.py, kept only for wave3_am_kit.py (delete them too).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes as the
camera sees them against enemy_O.png), --preview <prefix>, --only <model,...> (or the groups hatch, walker),
--whole <prefix> (the sheared wholes as GLBs, for looking at).
"""
import math
import os
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_coral_manta import cut  # noqa: E402
from polish_ring_machine import relief, Region, round_edge  # noqa: E402
from polish_gyges_wall import parse  # noqa: E402
from polish_orb_red import band_split  # noqa: E402

VIEW_TILT = 20.0                  # the game's camera: this far off straight down, from the bottom of the screen
TAN_T = math.tan(math.radians(VIEW_TILT))
LIGHT = Vector((-0.6, 0.6, 1.0)).normalized()   # towards the game's sun (from above and the top left)


def smoothstep(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


# --- Materials ------------------------------------------------------------------------------------------------------
# key: (palette index, metallic, roughness, emission strength in its own colour)
MATS = {
    # steel greys (ramp 0)
    "g1": (0x01, 0.3, 0.55, 0.0), "g2": (0x02, 0.35, 0.5, 0.0), "g3": (0x03, 0.4, 0.45, 0.0),
    "g4": (0x04, 0.45, 0.42, 0.0), "g5": (0x05, 0.45, 0.4, 0.0), "g6": (0x06, 0.45, 0.38, 0.0),
    "g7": (0x07, 0.45, 0.36, 0.0), "g8": (0x08, 0.45, 0.34, 0.0), "g9": (0x09, 0.45, 0.32, 0.0),
    "ga": (0x0a, 0.45, 0.3, 0.0), "gb": (0x0b, 0.45, 0.28, 0.0), "gc": (0x0c, 0.45, 0.26, 0.0),
    # the walker's blue armour (ramps 3 and 8: blues and light blues; ramp 6 dark blue-grey)
    "b6": (0x36, 0.4, 0.32, 0.0), "b8": (0x38, 0.4, 0.3, 0.0), "ba": (0x3a, 0.4, 0.28, 0.0),
    "l3": (0x83, 0.4, 0.28, 0.0), "l5": (0x85, 0.4, 0.26, 0.0), "d3": (0x63, 0.4, 0.4, 0.0), "d4": (0x64, 0.4, 0.38, 0.0),
    # the eye: glossy black, its glints
    "e1": (0x01, 0.25, 0.08, 0.0), "e2": (0x03, 0.25, 0.08, 0.0), "e3": (0x09, 0.2, 0.08, 0.0),
    "e4": (0x0f, 0.1, 0.1, 0.25),
    # the turrets' lamps, the feet's lenses
    "lamp": (0x0e, 0.1, 0.2, 0.45), "lens": (0x0a, 0.3, 0.1, 0.0),
}


def materials():
    pal = k.level_palette()
    m = {}
    for key, (index, metallic, roughness, glow) in MATS.items():
        extra = dict(emission=pal[index], emission_strength=glow) if glow > 0 else {}
        m[key] = k.material(f"fw_{key}", palette=index, metallic=metallic, roughness=roughness, **extra)
    return m


# --- Helpers --------------------------------------------------------------------------------------------------------

def rect(x0, x1, y0, y1):
    """A rectangle's outline, counter-clockwise."""
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def rect_sd(x, y, x0, x1, y0, y1):
    """Signed distance to a rectangle (negative inside)."""
    cx, cy, hw, hh = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2, (y1 - y0) / 2
    qx, qy = abs(x - cx) - hw, abs(y - cy) - hh
    return math.hypot(max(qx, 0.0), max(qy, 0.0)) + min(max(qx, qy), 0.0)


def poly_sd(x, y, poly):
    """Signed distance to a simple polygon (negative inside)."""
    d, inside = 1e9, False
    n = len(poly)
    for i in range(n):
        (ax, ay), (bx, by) = poly[i], poly[(i + 1) % n]
        ex, ey = bx - ax, by - ay
        t = max(0.0, min(1.0, ((x - ax) * ex + (y - ay) * ey) / max(ex * ex + ey * ey, 1e-12)))
        d = min(d, math.hypot(x - ax - t * ex, y - ay - t * ey))
        if (ay > y) != (by > y) and x < ax + (y - ay) * ex / (by - ay):
            inside = not inside
    return -d if inside else d


def paint_faces(obj, pick):
    """mk.paint with the face's centre and normal rounded (Blender's normals carry float noise from run to run)."""
    def rounded(c, n):
        return pick(Vector((round(c.x, 4), round(c.y, 4), round(c.z, 4))),
                    Vector((round(n.x, 4), round(n.y, 4), round(n.z, 4))))
    return mk.paint(obj, rounded)


def facing(n, lit, dark, flat=None, wall=None, flat_nz=0.92):
    """A material by how a face faces: flat (up), lit (towards the sun's side: up the screen or left), dark."""
    if n.z > flat_nz:
        return flat
    if wall is not None and n.z < 0.12:
        return wall
    return lit if (n.y - n.x) > 0.0 else dark


def shear_to_camera(objects):
    """polish_lemon_beetle's: every point moved along the game camera's line of sight to its height (y - z tan T), so
    that the camera sees each where the sprite draws it; the normals follow."""
    for obj in objects:
        mesh = obj.data
        normals = [Vector(cn.vector) for cn in mesh.corner_normals]
        for v in mesh.vertices:
            v.co.y -= v.co.z * TAN_T
        out = [Vector((n.x, n.y, n.z + TAN_T * n.y)).normalized() for n in normals]
        mesh.normals_split_custom_set([tuple(n) for n in out])
        mesh.update()


def copy_objects(objects, suffix):
    out = []
    for o in objects:
        c = o.copy()
        c.data = o.data.copy()
        c.name = o.name + suffix
        bpy.context.scene.collection.objects.link(c)
        out.append(c)
    return out


def remove(objects):
    for o in objects:
        mesh = o.data
        bpy.data.objects.remove(o)
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)


MAX_MATERIALS = 15


def merge_materials(obj, limit):
    """While obj has more than limit materials, the one covering the least area goes over to the nearest shade of its
    own ramp and kind (palette materials named <kind>_<key>@<index>: the same kind prefix and ramp)."""
    mesh = obj.data
    while len(mesh.materials) > limit:
        areas = [0.0] * len(mesh.materials)
        for poly in mesh.polygons:
            areas[poly.material_index] += poly.area
        names = [mt.name for mt in mesh.materials]

        def info(nm):
            base, _, idx = nm.partition("@")
            kind = base.rsplit("_", 1)[0] + "_" + base.rsplit("_", 1)[1][:1] if "_" in base else base
            return kind, int(idx) if idx.isdigit() else -1
        order = sorted(range(len(names)), key=lambda i: (areas[i], names[i]))
        merged = False
        for i in order:
            kind, idx = info(names[i])
            best = None
            for j, nm in enumerate(names):
                if j == i:
                    continue
                kj, ij = info(nm)
                if kj == kind and ij >= 0 and idx >= 0 and ij >> 4 == idx >> 4:
                    d = (abs(ij - idx), nm)
                    if best is None or d < best[0]:
                        best = (d, j)
            if best is None:
                continue
            j = best[1]
            for poly in mesh.polygons:
                if poly.material_index == i:
                    poly.material_index = j
            drop_unused([obj])
            merged = True
            break
        if not merged:
            break
    return obj


def export_pieces(whole, pieces, cap_of, options, sheet=None, label="o", only=None):
    """Cuts the whole (in the picture's plane) into its pieces (name, sprite, box (x0, x1, y0, y1), origin (x, y)),
    checks each against its sprite as the camera sees it, shears it for the camera, moves it to its origin and exports
    it (one joined mesh)."""
    out = mk.outdir(options)
    results = {}
    for spec in pieces:
        name, sprite, box, origin = spec[:4]
        cols = spec[4] if len(spec) > 4 else (0, 24)
        if only and name not in only:
            continue
        parts = [p for p in (cut(src, box, cap_of(src)) for src in whole) if p is not None]
        drop_unused(parts)
        for src in whole:
            src.hide_render = True
        score = None
        if sheet and sprite is not None:
            covered = mk.coverage(parts, 24, 28, centre=origin)
            mask = k.sprite_mask(sheet, sprite)
            for row_c, row_m in zip(covered, mask):
                for c in range(24):
                    if not cols[0] <= c < cols[1]:
                        row_c[c] = row_m[c] = False
            score = mk.compare("%s (%s %d%s), as the camera sees it" % (
                name, label, sprite, "" if cols == (0, 24) else ", columns %d-%d" % (cols[0], cols[1] - 1)),
                covered, mask)
        shear_to_camera(parts)
        mk.transform(parts, Matrix.Translation((-origin[0], -origin[1], 0.0)))
        bpy.context.view_layer.update()
        triangulate(parts)
        if "stats" in options:
            for obj in sorted(parts, key=lambda o: -mk.triangles([o]))[:8]:
                print("    %-24s %6d" % (obj.name, mk.triangles([obj])))
        obj = join(parts, name)
        obj.data.name = name
        merge_materials(obj, MAX_MATERIALS)
        mk.report(name, [obj], os.path.join(out, name + ".glb"))
        results[name] = score
        if "preview" in options and options.get("pieces") == "1":
            mk.preview(options["preview"] + name, [obj])
        remove([obj])
        for src in whole:
            src.hide_render = False
    return results


# --- Outlines of pixel masks ---------------------------------------------------------------------------------------

def smooth_loop(pts, sigma):
    """A closed loop's points averaged with their neighbours along it (a Gaussian of sigma points)."""
    if sigma <= 0:
        return pts
    n = len(pts)
    r = int(math.ceil(2.5 * sigma))
    w = [math.exp(-0.5 * (i / sigma) ** 2) for i in range(-r, r + 1)]
    total = sum(w)
    out = []
    for i in range(n):
        x = sum(w[j + r] * pts[(i + j) % n][0] for j in range(-r, r + 1)) / total
        y = sum(w[j + r] * pts[(i + j) % n][1] for j in range(-r, r + 1)) / total
        out.append((x, y))
    return out


def mask_loops(mask, left, top, chaikin=1, sigma=1.3):
    """The outlines of a pixel mask (rows, columns; pixel (r, c) covers x left + c .. + 1, y top - r - 1 .. top - r) as
    closed loops counter-clockwise round the inside, through the midpoints of its boundary edges (a staircase becomes
    a straight slope), smoothed along the loop (sigma points) and rounded by Chaikin."""
    h, w = mask.shape

    def inside(r, c):
        return 0 <= r < h and 0 <= c < w and mask[r, c]
    out_edges = {}
    for r in range(h):
        for c in range(w):
            if not mask[r, c]:
                continue
            x, y = c, -r
            if not inside(r + 1, c):
                out_edges.setdefault((x, y - 1), []).append((x + 1, y - 1))
            if not inside(r, c + 1):
                out_edges.setdefault((x + 1, y - 1), []).append((x + 1, y))
            if not inside(r - 1, c):
                out_edges.setdefault((x + 1, y), []).append((x, y))
            if not inside(r, c - 1):
                out_edges.setdefault((x, y), []).append((x, y - 1))
    used = set()
    loops = []
    for start in sorted(out_edges):
        for end in sorted(out_edges[start]):
            if (start, end) in used:
                continue
            loop = []
            a, b = start, end
            while (a, b) not in used:
                used.add((a, b))
                loop.append(((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0))
                nexts = [n for n in out_edges.get(b, []) if (b, n) not in used]
                if not nexts:
                    break
                # at a corner two regions touch: turn right (keep to this region)
                dx, dy = b[0] - a[0], b[1] - a[1]
                nexts.sort(key=lambda n: -((n[0] - b[0]) * dy - (n[1] - b[1]) * dx))
                a, b = b, nexts[0]
            pts = smooth_loop([(left + x, top + y) for x, y in loop], sigma if len(loop) > 12 else 0.0)
            if chaikin:
                pts = mk.chaikin(pts, chaikin, closed=True)
            loops.append(pts)
    return loops


def area(poly):
    return 0.5 * sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
                     for i in range(len(poly)))


class InsideDistance:
    """The distance inside polygons (even-odd) to their outlines on a grid, blurred (so its crest along their middles
    is rounded), sampled bilinearly; 0 outside."""

    def __init__(self, loops, step=0.25, sigma=0.9, margin=2.0):
        from polish_gyges_wall import blur
        xs = [p[0] for loop in loops for p in loop]
        ys = [p[1] for loop in loops for p in loop]
        self.x0, self.y0, self.step = min(xs) - margin, min(ys) - margin, step
        nx = int((max(xs) + margin - self.x0) / step) + 2
        ny = int((max(ys) + margin - self.y0) / step) + 2
        gx = self.x0 + step * np.arange(nx)
        gy = self.y0 + step * np.arange(ny)
        px, py = np.meshgrid(gx, gy)
        px, py = px.ravel(), py.ravel()
        a = np.array([p for loop in loops for p in loop], float)
        b = np.array([loop[(i + 1) % len(loop)] for loop in loops for i in range(len(loop))], float)
        d = np.full(px.shape, np.inf)
        inside = np.zeros(px.shape, bool)
        for (ax, ay), (bx, by) in zip(a, b):
            dx, dy = bx - ax, by - ay
            t = np.clip(((px - ax) * dx + (py - ay) * dy) / max(dx * dx + dy * dy, 1e-12), 0.0, 1.0)
            d = np.minimum(d, np.hypot(px - ax - t * dx, py - ay - t * dy))
            if ay != by:
                inside ^= ((ay > py) != (by > py)) & (px < ax + (bx - ax) * (py - ay) / (by - ay))
        field = np.where(inside, d, 0.0).reshape(ny, nx)
        self.f = blur(field, sigma / step)
        self.nx, self.ny = nx, ny

    def __call__(self, x, y):
        u, v = (x - self.x0) / self.step, (y - self.y0) / self.step
        i, j = int(math.floor(u)), int(math.floor(v))
        if not (0 <= i < self.nx - 1 and 0 <= j < self.ny - 1):
            return 0.0
        fu, fv = u - i, v - j
        f = self.f
        return float((f[j, i] * (1 - fu) + f[j, i + 1] * fu) * (1 - fv) + (f[j + 1, i] * (1 - fu) + f[j + 1, i + 1] * fu) * fv)


# --- The hatch ------------------------------------------------------------------------------------------------------
# The whole hatch (191 beside 193) about its picture's middle: x = c - 24, y = 14 - r.
FRAME_OUT = (-23.0, 23.0, -10.0, 12.0)      # the frame's outer edges (columns 1-46, rows 2-23)
FRAME_IN = (-20.0, 20.0, -7.0, 10.0)        # its opening (columns 4-43, rows 4-20: the dark gap round the lid)
FRAME_Z = 3.4                               # its top
CHAMFER = (1.0, 0.75)                       # the outer edge's chamfer: width, drop
INNER_ROUND = 0.3                           # the opening's edge, rounded
FLOOR_Z = 1.0                               # the well's black floor under the lid
LID = (-19.6, 19.6, -6.6, 9.6)              # the lid (columns 5-42 of rows 5-19, a little gap all round)
LID_Z, LID_T = 2.5, 0.7                     # its top and thickness
HINGE = (9.25, LID_Z - 0.35)                # the hinge along its top edge: (y, z)
# The raised stepped plate (columns 10-38 of rows 11-18, 15-33 of rows 8-10) and its bevel; how proud.
PLATE = [(-14.0, -5.0), (15.0, -5.0), (15.0, 3.0), (10.0, 3.0), (10.0, 6.0), (-9.0, 6.0), (-9.0, 3.0), (-14.0, 3.0)]
PLATE_UP, PLATE_BEVEL = 0.45, 0.45
# The vent slits (rows 14 and 16 of columns 5-9 and 39-42), the seams (columns 19-20 and 28-29 of rows 6-7): x0, x1,
# y0, y1; how deep.
SLITS = [(-19.6, -14.6, -0.9, -0.1), (-19.6, -14.6, -2.9, -2.1), (15.6, 19.6, -0.9, -0.1), (15.6, 19.6, -2.9, -2.1)]
SEAMS = [(-5.0, -3.4, 6.0, 9.6), (4.0, 5.6, 6.0, 9.6)]
SLOT_DEPTH = 0.4
# The rail along the lid's lower edge (row 19, columns 11-39), broken where the seams run (columns 20 and 28).
RAIL = [(-13.0, -4.0), (-3.0, 4.0), (5.0, 16.0)]
RAIL_Y = (-6.0, -5.0)
RAIL_UP = 0.3
# The frames' lid angles (degrees): the rail, seen as a lit bar, at rows 14, 12, 9, 7 (the hinge at row 4.5).
HATCH_FRAMES = [(195, 197, 51.0), (199, 201, 60.0), (203, 205, 72.0), (229, 231, 80.0)]


def frame_ring(m, zs=1.0, prefix="hatch"):
    """The frame: a ring over its outline, its top chamfered along the outer edge and rounded along the opening's;
    its walls straight down to z 0. Painted: its top dark steel (the sprite's band), the chamfer lit up the screen and
    to the left, dark the other way; the walls dark."""
    x0, x1, y0, y1 = FRAME_OUT
    ix0, ix1, iy0, iy1 = FRAME_IN
    cw, cd = CHAMFER

    def height(x, y, d):
        d_out = -rect_sd(x, y, x0, x1, y0, y1)
        d_in = rect_sd(x, y, ix0, ix1, iy0, iy1)
        z = FRAME_Z - cd * max(0.0, 1.0 - d_out / cw)
        if d_in < INNER_ROUND:
            t = max(0.0, d_in) / INNER_ROUND
            z -= 0.25 * (1.0 - math.sqrt(max(0.0, 1.0 - (1.0 - t) ** 2)))
        return z * zs

    def border(x, y, d):
        return -rect_sd(x, y, x0, x1, y0, y1)
    mats = {"top": m["g4"], "side": m["g2"]}
    obj = relief(f"{prefix}_frame", [rect(x0, x1, y0, y1), list(reversed(rect(ix0, ix1, iy0, iy1)))], height, mats,
                 side="side", bottom=0.0, spacing=0.6, borders=[(border, cw)], smooth_angle=30.0, band=1.3)

    def pick(c, n):
        if n.z < 0.3:
            return m["g2"]
        if n.z > 0.97:
            return m["g4"]
        if rect_sd(c.x, c.y, ix0, ix1, iy0, iy1) < INNER_ROUND + 0.1:
            return m["g3"]                  # the opening's rounded edge: in the gap's shadow
        return m["g8"] if (n.y - n.x) > 0.0 else m["g3"]
    paint_faces(obj, pick)
    return obj


def lid(m, zs=1.0, prefix="hatch"):
    """The lid: its top a mesh over the lid's outline, the stepped plate raised over it with bevels, the slits and
    seams sunk into it, the rail along its lower edge (mesh lines along all their edges); its walls down to its
    thickness. Painted: the lid dark, the plate's bevels lit up the screen and to the left, dark the other way, the
    slits and seams black, the rail lit."""
    lx0, lx1, ly0, ly1 = LID

    def plate_d(x, y):
        return poly_sd(x, y, PLATE)

    def rail_d(x, y):
        return min(rect_sd(x, y, a, b, RAIL_Y[0], RAIL_Y[1]) for a, b in RAIL)

    def slot_d(x, y):
        return min(rect_sd(x, y, *s) for s in SLITS + SEAMS)

    def height(x, y, d):
        z = LID_Z
        p = plate_d(x, y)
        if p < 0.0:
            z += PLATE_UP * min(1.0, -p / PLATE_BEVEL)
        if rail_d(x, y) < 0.0:
            z += RAIL_UP
        if slot_d(x, y) < 0.0:
            z -= SLOT_DEPTH
        return z * zs
    borders = [(lambda x, y, d: -plate_d(x, y), 0.0), (lambda x, y, d: -plate_d(x, y), PLATE_BEVEL),
               (lambda x, y, d: -rail_d(x, y), 0.0), (lambda x, y, d: -slot_d(x, y), 0.0)]

    def paint(x, y, d):
        if slot_d(x, y) < 0.0:
            return "slot"
        if rail_d(x, y) < 0.0:
            return "rail"
        return "top"
    mats = {"top": m["g3"], "side": m["g2"], "slot": m["g1"], "rail": m["g6"]}
    obj = relief(f"{prefix}_lid", [rect(lx0, lx1, ly0, ly1)], height, mats, paint=paint, side="side",
                 bottom=(LID_Z - LID_T) * zs, spacing=0.45, borders=borders, smooth_angle=30.0, band=1.0)

    def pick(c, n):
        if n.z > 0.97 or n.z < 0.3:
            return None
        # the plate's bevels
        if plate_d(c.x, c.y) < 0.05:
            return m["g6"] if (n.y - n.x) > 0.0 else m["g2"]
        return None
    paint_faces(obj, pick)
    return obj


def floor(m, zs=1.0, prefix="hatch"):
    """The well's black floor inside the frame's opening."""
    ix0, ix1, iy0, iy1 = FRAME_IN
    obj = mk.box(f"{prefix}_floor", ix0 + 0.01, ix1 - 0.01, iy0 + 0.01, iy1 - 0.01, 0.0, FLOOR_Z * zs, m["g1"])
    return obj


def hatch(m, angle=0.0, zs=1.0, prefix="hatch"):
    """The whole hatch about its picture's middle, its lid swung open by angle (degrees) about the hinge; zs scales its
    heights (the walker's own flat copies in its bays)."""
    parts = [frame_ring(m, zs, prefix), floor(m, zs, prefix)]
    top = lid(m, zs, prefix)
    if angle:
        hy, hz = HINGE
        rot = (Matrix.Translation((0.0, hy, hz * zs)) @ Matrix.Rotation(math.radians(-angle), 4, "X") @
               Matrix.Translation((0.0, -hy, -hz * zs)))
        top.data.transform(rot)
        top.data.update()
    parts.append(top)
    for obj in parts:
        mk.apply(obj)
    return parts


def hatch_pieces(frame_l=191, frame_r=193):
    """(name, sprite, box, origin) of the hatch's two pieces (cut at x = 0)."""
    suffix_l = "" if frame_l == 191 else "_%d" % frame_l
    suffix_r = "" if frame_r == 193 else "_%d" % frame_r
    return [("fleet_hatch_l" + suffix_l, frame_l, (-30.0, 0.0, -20.0, 20.0), (-12.0, 0.0)),
            ("fleet_hatch_r" + suffix_r, frame_r, (0.0, 30.0, -20.0, 20.0), (12.0, 0.0))]


def build_hatches(options, sheet, only):
    results = {}
    for frame_l, frame_r, angle in [(191, 193, 0.0)] + HATCH_FRAMES:
        names = [p[0] for p in hatch_pieces(frame_l, frame_r)]
        if only and not any(n in only for n in names):
            continue
        k.reset()
        m = materials()
        whole = hatch(m, angle)
        triangulate(whole)
        bpy.context.view_layer.update()
        bpy.context.scene.view_settings.view_transform = "Standard"
        low, high = mk.bounds(whole)
        print("== hatch %d/%d (lid %.0f deg): %d triangles, x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (
            frame_l, frame_r, angle, mk.triangles(whole), low.x, high.x, low.y, high.y, low.z, high.z))
        if "preview" in options and angle == 0.0:
            seen = copy_objects(whole, "_seen")
            shear_to_camera(seen)
            for o in whole:
                o.hide_render = True
            mk.preview(options["preview"] + "fleet_hatch", seen, size=(48, 28), scale=10)
            remove(seen)
            for o in whole:
                o.hide_render = False
        if "whole" in options:
            seen = copy_objects(whole, "_seen")
            shear_to_camera(seen)
            mk.export(seen, options["whole"] + "fleet_hatch_%d.glb" % frame_l)
            remove(seen)
        results.update(export_pieces(whole, hatch_pieces(frame_l, frame_r), lambda src: m["g2"], options, sheet,
                                     only=only))
    return results


# --- The walker -----------------------------------------------------------------------------------------------------
# The whole walker about its picture's middle (pixel edge 96, 70): x = c - 96, y = 70 - r. Its left half's pixels
# (columns 0-95 of rows 8-131; the right half is their mirror image about the middle of column 95: c -> 190 - c).
WX, WY = -96.0, 70.0
WALKER_ROW0 = 8
WALKER_LEFT = """
..............................................................................................01010101
............................................................................................01040605060101
..........................................................................................0103060b080706030101..........................................................010101010101010101010101
........................................................................................010203050907070606050301010101..............................................0101090707070309030903090309
....................................................................................010102030305070707060708080706060901........................................01010808090707070408040804080408
....................................................................................010504030304060707040403030204050701....................................010108080808090707070408040804080408
....................................................................................010504030101020406040708090702040701................................0101080808080808090707070508050805080508
........................................................................010101010101010504030104070a0904070e0a0804030601............................01010707080808080808090707070608060806080608
..............................................................010101010101040504030201050403010405070903060a070604010501........................010107070707080808080808090707070707070707070707
............................................................010104030201010408030201010504030104050708030609070604020501....................0101070808070707080808080808090707070707070707070707
............................................................010405080505040607030101010504030104050708030507070604020501................01010808080807070707080808080808090707070707070707070707
............................................................010405090101010505030101010504030104050708030506060503020501............010108080807070707060301010808080808090707070707070707070707
........................................................0101010405050101010101..0101010101010101010163010201010101010101010101010101080808080707070605010101010608080808090707070707070707070707
......................................................01010101040503..0101383939380707070707070808839e630807060707070707070709090a0a0a0909080707040101010101010408080808090707070707070707070707
....................................................01030403020101..3a3a3a3a3a3a3a8307070707070704393a360a07070707070707070707070707070707070401010101010101010107080808090707070707070707070707
..................................................01010201....3a3a3a3a3a3a3a3a3a3a0a080808080808033839380a070707070707070707070707070707070101010101010101010101050808080a0707070707070707070707
..................................................0101..3a3a3a3a3a3a3a3a3a3a3a3a3a0b080808080808033639390a0707070707070707070707070707070701010101010101010101010408080b080707070707070707070707
............................................0101..3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a0c090909090909033638390a07070707070707070707070707070707010101010102020101010103070a36060907070707070707070707
......................................01....3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a0b090909090909033638390a07070707070707070707070707070707040101010202020201010101083639838309070707070707070707
................................0101..3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a0a08080808080803363839090707070707070707070707070707070704010102020202020101010104383a838383090707070707070707
............................01013a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a0a080808080808033638390807070707070707070707070707070707070102020202020201010101048383838383830907070707070707
..........................02853a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a09070707070707033638390807070707060606060606060606393939060101020202020201010101028383838383830907070707070707
........................0183853a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a09070707070707033638390907070707069e8383838383833a3a3a3a3a3801020202020201010101018383838383830907070707070707
......................018383853a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a0907070707070703363839090707070705833a3a3a3a3a3a3a3a3a3a3a39..02020201010101....018383838383830907070707070707
....................01838383853a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a0907070707070703363839090707070705833a3a3a3a3a3a833a3a3a3a3a640101020101....6264808383838383830907070707070707
..................0183838383853a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a0907070707070703363939090707070705833a3a3a3a3a3a83833a3a3a3a39..010201..62643883838383838383830907070707070707
................018383838383863a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a3a09070707070707033639390a07070707053a3a3a3a3a3a3a83833a3a3a3a3964010201..65838383838383838383830907070707070707
..............0183838383839e86833a3a3a3a3a3a3a3a3a3a3a3a3a3a39393939393939393a3a3a08070707070707033839390a07070707053a3a3a3a3a3a3a83853a3a3a3a3a36010102..64838383838383838383830907070707070707
............0183838383839e859e85858585858585858585858585838364383838383839868383830807070707070703383a390b08080707043a3a3a3a3a3a3a83853a3a3a3a3a39..010201..388383838383833836640707070707070707
..........018383838383863a3838383838383838383838383838383838643838383838383a38383808070707070707043a83630707070707043a3a3a3a3a3a3a8385833a3a3a3a3a6301020101658383838339366464630101010101010101
..........0183838383863a383838383838383838383838383838383838633636363665653a383838040404040404040436386305040404040336393a3a3a3a3a8385833a3a3a3a3a3801010201633983393664646464646464646464646464
..........01838383863938383838383838383838383838383838383838633636363665653938383838383838383838383838630505050505050536383a3a3a3a838585833a3a3a3a39..010201013636646464646464646464646464646464
..........01838385393838383838383838383838383838383838383838383838383838383838383838383838383838383838630505050505050505643a3a3a3a838685833a3a3a3a3964010201016364646464646464010101010101010101
..........02833a3938383838383838383838383838383838383838383838383838383838383838383838383838383838383863050505050505050504393a3a3a838685833a3a3a3a3a36..01020101636464646402..010202020202020202
..........013938383a383939393939393939393939393939393939393939393939393939393939393939393939393939393906060603050505050502393a3a3a83868585833a3a3a3a39..0102010101646463010102020202040505030202
..........013838380c070707070707070707070707070707070707070707070707070707070707070707070707070707070707070703040505050502393a3a3a83868685833a3a3a3a3963010202010150..010202020303070b0d0b070302
..........0138383808040404040404040404040404040404040404040404040404040404040404040404040404040404040404040401030405050502053a3a3a83859e85833a3a3a3a3a38..0102010101020202020305080c0f0f0c070302
..........013838380604040101010101010101010101010101010101010101010101010101010101010101010101010101010104040102030405050303393a3a83859e8585833a3a3a3a39..0102020101020202020306080c0f0e0b060302
..........013838380604040101010101010101010101010101010101010101010101010101010101010101010101010101010104040102030405050303393a3a3a83858685853a3a3a3a3a640101020101020202020305070a0d0d09060302
..........01383838060404010202020202020202020202020202010102020202020202010102020202020202020202020202010404010203040505030138393a3a83839e8685853a3a3a3a38..010101010202020302040507090806040202
..........01646301060404010302020202020202020202020202010103020202020202010102020202020202020202020202010404010203040505030138393a3a3a83869e85853a3a3a3a3a64010101010202040903020303040303020202
..........01090502060404010302020202020202020201010101010102010101010101010101010101020202020202020202010404010203040505040236393a3a3a83859f8685833a3a3a3a39..0101010102020503020202020202020201
..........0107050306040401030202020202020202020103030303030303030303030303030303030102020202020202020201040401020304050504036338393a3a8383869e8585833a3a3a3a....01010102020202020205020202020101
..........0106050306040401030202020202020202020103020202020202020202020202020202020102020202020202020201040401020304050505030238393a3a3a8383869e8583833a3a3a3a..01010101010202020203020202010101
..........010202020604040103020202020101010101010302020202020202020202020202020202010101010101020202020104040102030405050503023639393a3a3a83869f9e8383393939390501010101010101020202020201010101
..........010906030604040103020202020103030303030302020202020202020202020202020202020303030302030202020104040102030405050504030236393a3a3a838385853938070808080706010101010101010101010101010101
..........01070503060404010302020202010302020202020202020202020202020202020202020202020202020103020202010404010203040505050403020338393a3a3a838338060a0a0908070707060503010101010101010101010101
..........01060503060404010201010101010302020202020202020202020202020202020202020202020202020102010101010404010203040505050403030238393a3a3a3a38070b0e0b0a08070707070706040301010101010101010202
..........0103030206040401050202020201030202020202020202020202020202020202020202020202020202010503020201040401020304050505050403020338393a3a3806090a0b0a0a09080707070707070706040401010101010101
..........010806030604040102010101010103020202020202020202020202020202020202020202020202020201020101010104040102030405050505040303013638073a0508080809090909080807070707070707070707070707070707
..........01080403060404010402020202010302020202020202020202020202020202020202020202020202020106030202010404010203040505050504030201013638380808070808080909090908070707070707070707070707070707
..........01060403060404010201010101010201010101010101010101010101010101010101010101010101010102010101010404010203040505050505010101020438360607070708080808080808080707070707070707070707070707
..........01060403060404010302020202020303030303030303030105030303030303010503030303030303030303020202010404010203040505050501010202010104360606070707070808080808080707070707070707070707070707
..........01060403060404010101010101010101010101010101010103010101010101010201010101010101010101010101010404010203040505050201020704040101640506060707070707070707070707070707070707070707070707
..........01060403060404040404040404040404040404040404040404040404040404040404040404040404040404040404040404010203040505020103080d09040302020405060606060707070707070707070707070707070707070707
..........01060403060404040404040404040404040404040404040404040404040404040404040404040404040404040404040404010203040503010101060909040302010204050606060606060606060606060606060606060606060606
..........01040403030101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010203040401020501020505040302020101020406060606060606060606060606060606060606060606
..........01030403030303030303030301010101010101010706060606060606060606060606060606060606060606060708010101010204040102040507010203030204040101010103040505050505050505050505050505050505050505
............010204030303030304060303020101010101010702020202020202020202020202020201010101010101010107010102020303010204050705050102020403010101010102030304050505050505050505050505050505050505
..............0102040303030303040603030202020101010703030202030303030303030303030202010101010101010106020303040501020404060505030203050201010101010204020303030404040404040404040404040404040404
................0102040303030303040803030303020101070306030204040404040404040303030202010401010101020502040505020203040505040303050501010101010101010101010101010101010101............0101010101
..................0102040303030303040805040202010107030403020609060505050505050505050202030101010105040505050301030405040303040604010101010101010101010101010101....010101636363636363..03020202
....................010204030303030304080903060606070304030202030404040404040303030202020301010103050505050501030404020102060503020201010101010101010101..0101010101636364646464646464..05030303
......................0102040303030303040703050505070204030205080605050505050505050503020301010305050505050301020202010307050201010102020101010101..01016364646436363665656536366565650106040404
........................010204030303030307030505050702040302020404040404040404030202010203020405050505050503020102020406030102020201010101010101016364363636383838383838383838383838380106040404
..........................0102040303030307030505050806030302050906050505050505050505010201040505050505050505030303060502010101010101010101010102073839393939393939393939393939393939060606060606
............................010204030303060305050505080603020103040404040404040302020102040505050505050505050505050301010102020101010101010263030c0707070707070707070707070707070707070707070707
..............................010204030305030505050505080603030303030303030303030303040505050505050505050505050504020201010101010102020101643664080404040404040404040404040404040404040404040404
................................0102040304030505050505050804853a833a0908080785838383080505050505050505050505030301010101010101030303020101633936060404010101010101010101010101010101010101010101
..................................01020404020505050505050504393838360605050439383836060505050505050505050403020202010101010102030304030201..3a36060404010101010101010101010101010101010101010101
....................................0102030105050505050505043938383606050504393838360605050505050505050302020202020101..010101020306040201..3a36060404010202020202020202020202020202010102020202
......................................0103010505050505050504393838360605050439383836060505050505050504020202020101........0101020304040201..3a36060404010302020202020202020202020202010103020202
........................................01010305050505050504393838360605050439383836060505050505050302010101010101........0101010203030201..3a36060404010302020202020202020201010101010102010101
..........................................010304050505050504393838360605050439383836060505050505030101010101010101..........01010202020201..3a36060404010302020202020202020201030303030303030303
............................................0103040505050504393838360605050439383836060505050501010101010101010101..........01010102020101..3a36060404010302020202020202020201030202020202020202
..............................................0101010101010101......0101010101......010101010101010101010101010101............010101010101..3a36060404010302020202010101010101030202020202020202
................................................................................0101010101010101010101020202020201..............0101010101..3a36060404010302020202010303030303030202020202020202
................................................................................0101010101010101020202020303030201..................010101..3a36060404010302020202010302020202020202020202020202
................................................................................0101010202020202020303030303030201..........................3936060404010201010101010302020202020202020202020202
................................................................................0103050404040404040404040404040201..........................3936060404010502020202010302020202020202020202020202
................................................................................010203060401010101010101010204030101....................01643938060404010201010101010302020202020202020202020202
................................................................................010202030501010101010101010103040701..................0102393838060404010402020202010302020202020202020202020202
................................................................................010202020301020202020202020101010101..................0183383838060404010201010101010201010101010101010101010101
................................................................................01020202010103030303030303030101........................83383838060404010302020202020303030303030303030105030303
..................................................................................0101010101030303040404040501..........................83383838060404010101010101010101010101010101010103010101
....................................................................................01010101030304050505050801..........................39393838060404040404040404040404040404040404040404040404
........................................................................................0102030304030101010201..........................643a3838060404040404040404040404040404040404040404040404
........................................................................................0102030304010101010101..........................64383938030101010101010101010101010101010101010101010101
........................................................................................0102030305010101010101..........................01643839386463636363636363010302020201036363010102020202
........................................................................................010203030501010101..............................63013639393864646464646464010503030302366464630104030303
........................................................................................010203030501......................................630136383939363636363636010604040402383636646305040404
........................................................................................010203030501............................................633636383838383838010705050502393838366483070707
........................................................................................0102030306010101............................................63646438383838010705050502393838366407050505
........................................................................................010103060707050101........................................................01010101010101....010104040404
........................................................................................010102020101070401..............................................................................01010101
........................................................................................010102030601060401
........................................................................................010102030601070401
........................................................................................010103030601080401
........................................................................................010103030801090401
......................................................................................01040102020a01090401
....................................................................................0101040101010a01090401
....................................................................................0104040405050b05090401
....................................................................................0104040404040b06090401
....................................................................................0101010101040a090a0501
....................................................................................01010101010305060a0601
....................................................................................01010202020304060a0601
....................................................................................01030303020304060806010101
....................................................................................0103040402020104060504040601
....................................................................................01030404020405070a090204060101
....................................................................................01040505020304060b090202050201
....................................................................................01040505020304070c080401020201
....................................................................................01010202020306080d090503010201
....................................................................................0101020202010101020203060201
....................................................................................0101010101010404060907010401
......................................................................................01010102040504070b09060101
......................................................................................01010104050201010102090501
......................................................................................01020105030101010201030701
......................................................................................01030105010102040302010701
......................................................................................01030104010103050501010501
......................................................................................01020104020105010501010401
......................................................................................01010101070203060301030401
......................................................................................01010101010703030301040101
........................................................................................0101010101060605040101
..................................................................................................01010101
"""
AXIS_X = -0.5                     # the mirror line (x -> -1 - x)
# The hatches' bays (the hatches' middles, polish_fleet_walker's hatch whole about them): left, right, middle.
BAYS = [(-64.0, 14.0), (63.0, 14.0), (-1.0, -16.0)]
BAY_GAP = 0.15                    # the bays' walls this far outside the hatches' frames
BAY_HATCH_ZS = 0.28               # the walker's own hatches in its bays (STATION has no hatch enemies): flat copies
# Heights (the picture's plane, z 0 the walker's base: on the terrain, models.cfg height=-4).
Z_ARMOUR, Z_ARMOUR_FRONT = 14.0, 12.2
Z_STRAP = 14.7
Z_TURRET, Z_TURRET_SMALL = 16.4, 15.0
Z_RAIL = 12.0
Z_LOWER = 11.2
Z_GRILLE, Z_SLAT = 9.4, 10.4
Z_HEAD, Z_CHEEK = 19.2, 17.0
Z_CAVITY = 6.0
Z_BAND = 12.4
Z_BOX = 12.4
Z_HIP = 7.0


def walker_art():
    rows = parse(WALKER_LEFT)
    a = np.full((140, 192), -1, int)
    for i, row in enumerate(rows):
        for c, v in enumerate(row[:96]):
            if v is not None:
                a[WALKER_ROW0 + i, c] = v
                if c <= 94:
                    a[WALKER_ROW0 + i, 190 - c] = v
    return a


def wcr(x, y):
    """Continuous (column, row, mirrored column) of a point of the plane."""
    c, r = x - WX, WY - y
    return c, r, (c if c <= 95.5 else 191.0 - c)


class Masks:
    """The walker's parts as pixel masks of its 192 x 140 picture (both halves), each pixel in one part."""

    def __init__(self):
        a = walker_art()
        self.a = a
        R, C = np.mgrid[0:140, 0:192]
        U = np.where(C <= 95, C, 190 - C)
        px = a >= 0
        ramp = np.where(px, a >> 4, -1)
        shade = np.where(px, a & 15, -1)
        blue = px & (ramp > 0)
        grey = px & (ramp == 0)
        self.R, self.C, self.U, self.px, self.blue, self.grey, self.shade = R, C, U, px, blue, grey, shade
        free = px.copy()

        def take(m):
            m = m & free
            free[m] = False
            return m
        self.turret = take(px & (R <= 20) & (U >= 42) & (U <= 59))
        self.turret_small = take(grey & (R >= 15) & (R <= 22) & (U >= 29) & (U <= 41))
        self.collar = take(blue & (R >= 28) & (R <= 61) & (U >= 56) & (U <= 77))
        self.strap = free & grey & (R >= 21) & (R <= 38) & (U >= 41) & (U <= 48)
        self.armour = take((blue & (R >= 20) & (R <= 41) & (U >= 5) & (U <= 51)) |
                           (blue & (R >= 42) & (R <= 48) & (U >= 5) & (U <= 8)) | self.strap)
        self.head = take(px & (R >= 9) & (R <= 36) & (U >= 61) & (U <= 95))
        self.cavity = self.head & grey & (R >= 19) & (U >= 65) & (U <= 82) & (shade <= 2)
        self.cheek = self.head & blue & (R >= 22) & (U >= 78) & (U <= 88)
        self.band = take(px & (R >= 37) & (R <= 42) & (U >= 74) & (U <= 95))
        self.eye = take(px & (R >= 41) & (R <= 58) & (U >= 79) & (U <= 95))
        self.bumper = take(px & (R >= 52) & (R <= 68) & (U >= 66) & (U <= 95))
        self.box = take(px & (R >= 68) & (R <= 102) & (U >= 62) & (U <= 95))
        self.hips = take(px & (R >= 52) & (R <= 83) & (U >= 58) & (U <= 68))
        self.legs = take(px & (R >= 84) & (U >= 36) & (U <= 60))
        self.pods = take(px & (((R >= 41) & (R <= 83) & (U >= 5) & (U <= 60)) |
                               ((R >= 20) & (R <= 42) & (U >= 51) & (U <= 57))))
        # The pixels left over (mostly the sprite's dark outline round the parts) go to the part beside them (but the
        # dark bits by the small turret's corner, which the sprite draws as the armour's outline: left out).
        free &= ~((R <= 24) & (U >= 24) & (U <= 34))
        parts = ["armour", "collar", "head", "band", "eye", "bumper", "box", "turret", "turret_small", "pods"]
        for _ in range(3):
            grow = {}
            for name in parts:
                mask = getattr(self, name)
                near = np.zeros_like(mask)
                near[1:, :] |= mask[:-1, :]
                near[:-1, :] |= mask[1:, :]
                near[:, 1:] |= mask[:, :-1]
                near[:, :-1] |= mask[:, 1:]
                grow[name] = near & free
            for name in parts:
                g = grow[name] & free
                setattr(self, name, getattr(self, name) | g)
                free[g] = False
        self.rest = free


def loops_of(mask, sigma=1.3, min_area=3.0):
    loops = mask_loops(mask, WX, WY, chaikin=1, sigma=sigma)
    return [p for p in loops if abs(area(p)) > min_area]


def bay_holes():
    """The bays' openings (polygons, clockwise: holes) round the hatches' frames."""
    x0, x1, y0, y1 = FRAME_OUT
    out = []
    for bx, by in BAYS:
        g = BAY_GAP
        out.append(list(reversed(rect(bx + x0 - g, bx + x1 + g, by + y0 - g, by + y1 + g))))
    return out


def bay_d(x, y):
    """The signed distance to the nearest bay's opening (negative inside one)."""
    x0, x1, y0, y1 = FRAME_OUT
    g = BAY_GAP
    return min(rect_sd(x, y, bx + x0 - g, bx + x1 + g, by + y0 - g, by + y1 + g) for bx, by in BAYS)


def mirror_x_obj(obj, name):
    """A copy mirrored about x = AXIS_X (faces turned back out, custom normals mirrored)."""
    c = obj.copy()
    c.data = obj.data.copy()
    c.name = name
    bpy.context.scene.collection.objects.link(c)
    mesh = c.data
    corner = {}
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            n = mesh.corner_normals[li].vector
            corner[(poly.index, mesh.loops[li].vertex_index)] = (-n.x, n.y, n.z)
    mesh.transform(Matrix.Translation((2 * AXIS_X, 0, 0)) @ Matrix.Scale(-1, 4, (1, 0, 0)))
    mesh.flip_normals()
    normals = [None] * len(mesh.loops)
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            normals[li] = corner[(poly.index, mesh.loops[li].vertex_index)]
    mesh.normals_split_custom_set(normals)
    mesh.update()
    return c


def shade_by_sun(m, keys, n, wall=None):
    """One of keys (dark to light) by how a face meets the game's sun; wall for steep faces."""
    if wall is not None and n.z < 0.2:
        return m[wall]
    lit = n.dot(LIGHT)
    i = 0 if lit < 0.42 else 1 if lit < 0.62 else 2 if lit < 0.8 else 3 if lit < 0.93 else 4
    return m[keys[min(i, len(keys) - 1)]]


def armour(mk_, m):
    """The pods' armour: a plate over its outline, its edge rounded, its top flat, its front band sloping down to the
    bays; the grey strap raised on it, the dark slot in the front band."""
    M = mk_
    loops = loops_of(M.armour, 2.6)
    strap = loops_of(M.strap, 0.8)
    slot_box = [(31.0, 37.0, 36.0, 40.0)]

    def strap_d(x, y):
        return min((poly_sd(x, y, p) for p in strap), default=9.0)

    def slot_d(x, y):
        c, r, u = wcr(x, y)
        return min(rect_sd(u, r, a, b, r0, r1) for a, b, r0, r1 in slot_box)

    def height(x, y, d):
        c, r, u = wcr(x, y)
        top = Z_ARMOUR if r < 36.0 else Z_ARMOUR - (Z_ARMOUR - Z_ARMOUR_FRONT) * min(1.0, (r - 36.0) / 7.0)
        z = top - 2.2 * (1.0 - round_edge(d, 2.0))
        sd = strap_d(x, y)
        if sd < 0.0:
            z = max(z, Z_STRAP - 0.5 * (1.0 - round_edge(-sd, 0.5)))
        if slot_d(x, y) < 0.0:
            z -= 0.6
        return z
    borders = [(lambda x, y, d: -strap_d(x, y), 0.0), (lambda x, y, d: -slot_d(x, y), 0.0),
               (lambda x, y, d: wcr(x, y)[1], 36.0)]

    def paint(x, y, d):
        if strap_d(x, y) < 0.0:
            return "strap"
        return "slot" if slot_d(x, y) < 0.0 else "top"
    mats = {"top": m["b8"], "side": m["d3"], "strap": m["g8"], "slot": m["d4"]}
    obj = relief("w_armour", loops, height, mats, paint=paint, side="side", bottom=0.0, spacing=0.6, borders=borders,
                 smooth_angle=35.0, band=2.5)

    def pick(c, n):
        cc, r, u = wcr(c.x, c.y)
        if strap_d(c.x, c.y) < 0.02:
            return shade_by_sun(m, ["g5", "g6", "g8", "g9", "ga"], n, "g4")
        if slot_d(c.x, c.y) < 0.02:
            return m["d4"]
        if n.z < 0.2:
            return m["d3"]
        if r > 36.0 and n.z > 0.9:
            return m["b8"]                                   # the front band, sloping to the bay
        return shade_by_sun(m, ["b6", "b8", "ba", "l3", "l5"], n)
    paint_faces(obj, pick)
    return [obj]


def pods(mk_, m):
    """The pods round the bays: the side rails, the lower bodies (their outer corners chamfered, the grille, the blue
    slots), the bays' walls; one relief over their outline with the bays as holes."""
    M = mk_
    loops = loops_of(M.pods) + bay_holes()[:2]

    def chamfer_s(u, r):
        # how far beyond the chamfer's inner line (from (14, 64) to (30, 80)) towards the outer corner
        return ((r - 64.0) - (u - 14.0)) / math.sqrt(2.0)

    def grille_d(u, r):
        return rect_sd(u, r, 25.0, 50.0, 66.0, 76.0)

    def slots_d(u, r):
        return min(rect_sd(u, r, 31.0, 35.0, 76.0, 83.5), rect_sd(u, r, 39.0, 43.0, 76.0, 83.5))

    def inner_rail(u, r):
        return 54.0 <= u <= 61.0 and 41.0 <= r <= 66.0

    def height(x, y, d):
        c, r, u = wcr(x, y)
        if r < 42.0:
            z = Z_RAIL + 0.6                                  # the band between the armour and the collar
        elif r < 64.0:
            z = Z_RAIL
        else:
            z = Z_LOWER
            s = chamfer_s(u, r)
            if s > 0.0:
                z -= 0.62 * s
            g = grille_d(u, r)
            if g < 0.0:
                z = Z_GRILLE + (Z_SLAT - Z_GRILLE) * (1.0 if (int(math.floor(r)) in (69, 71, 73)) else 0.0)
            if slots_d(u, r) < 0.0:
                z = Z_LOWER - 0.8
        z -= 1.6 * (1.0 - round_edge(d, 1.4))
        return max(z, 1.0)
    borders = [(lambda x, y, d: -grille_d(wcr(x, y)[2], wcr(x, y)[1]), 0.0),
               (lambda x, y, d: -slots_d(wcr(x, y)[2], wcr(x, y)[1]), 0.0),
               (lambda x, y, d: wcr(x, y)[1], 64.0)]
    borders += [(lambda x, y, d, rr=rr: wcr(x, y)[1], rr) for rr in (69.0, 70.0, 71.0, 72.0, 73.0, 74.0)]

    def paint(x, y, d):
        c, r, u = wcr(x, y)
        if slots_d(u, r) < 0.0:
            return "slot"
        if grille_d(u, r) < 0.0:
            return "grille"
        return "top"
    mats = {"top": m["g5"], "side": m["g3"], "grille": m["g3"], "slot": m["b8"]}
    obj = relief("w_pods", loops, height, mats, paint=paint, side="side", bottom=0.0, spacing=0.6, borders=borders,
                 smooth_angle=35.0, band=2.0)

    def pick(c, n):
        cc, r, u = wcr(c.x, c.y)
        if bay_d(c.x, c.y) < 0.3 and n.z < 0.5:
            return m["g2"]                                   # the bays' walls
        if slots_d(u, r) < 0.02:
            return m["b8"] if n.z > 0.9 else m["d4"]
        if grille_d(u, r) < 0.02:
            if n.z > 0.9:
                return m["g6"] if c.z > Z_GRILLE + 0.5 else m["g2"]
            return m["g3"]
        if n.z < 0.2:
            return m["g3"]
        return shade_by_sun(m, ["g4", "g6", "g7", "g8", "ga"], n)
    paint_faces(obj, pick)
    return [obj]


def wp(u, r):
    """A point of the plane from a (mirrored) column and a row of the picture, on the left half."""
    return (u + WX, WY - r)


def full(left):
    """A symmetric outline from its left half (from the axis at the top round to the axis at the bottom, (u, r)):
    the left half and its mirror image."""
    pts = [wp(u, r) for u, r in left]
    mirror = [(2 * AXIS_X - x, y) for x, y in reversed(pts)]
    out = pts + [p for p in mirror if all(abs(p[0] - q[0]) > 1e-6 or abs(p[1] - q[1]) > 1e-6 for q in pts[-1:])]
    if abs(out[-1][0] - out[0][0]) < 1e-6 and abs(out[-1][1] - out[0][1]) < 1e-6:
        out.pop()
    return out


def mirror_poly(pts):
    return [(2 * AXIS_X - x, y) for x, y in reversed(pts)]


# The head (the left half's outlines, (mirrored column, row) pixel edges): its outline round the shoulders, the deck
# beside it (rows 21-29) and the band under it (rows 37-41); the nose, the cavities, the cheeks.
HEAD = [(95.5, 9.6), (84.2, 9.6), (66.0, 18.8), (57.0, 20.6), (51.8, 20.8), (51.8, 29.2), (69.6, 29.2), (70.6, 31.5),
        (72.0, 36.8), (74.0, 37.0), (74.4, 41.2), (81.0, 41.6), (88.0, 40.4), (95.5, 40.4)]
CAVITY = [(70.0, 21.2), (75.6, 19.6), (79.4, 20.4), (80.2, 25.0), (80.0, 36.4), (73.2, 36.4), (71.2, 31.0),
          (70.0, 28.0)]
CHEEK = [(81.6, 24.6), (84.4, 24.4), (87.4, 25.6), (87.6, 37.4), (79.8, 37.4), (80.6, 35.0), (80.8, 26.0)]
NOSE_U = 87.5                     # the nose's edge (its lit column 87)
SHOULDER = ((84.2, 9.6), (57.0, 20.6))   # the shoulder's outer edge, falling from the head's top to the deck
Z_DECK = 13.6
SHOULDER_W = 3.2                  # the shoulder's bevel down to the deck, this wide


def head(mk_, m):
    """The head: its top flat over the nose and the head's back, its shoulders falling along their edge to the deck
    beside the pods, the vents along its back edge; the blue cheeks raised beside the nose, the dark cavities sunk
    between the cheeks and the collar's arms; the collar's band under it."""
    outline = full(HEAD)
    cheeks = [[wp(u, r) for u, r in CHEEK]]
    cheeks.append(mirror_poly(cheeks[0]))
    cavities = [[wp(u, r) for u, r in CAVITY]]
    cavities.append(mirror_poly(cavities[0]))
    (u0, r0), (u1, r1) = SHOULDER

    def cheek_d(x, y):
        return min(poly_sd(x, y, p) for p in cheeks)

    def cav_d(x, y):
        return min(poly_sd(x, y, p) for p in cavities)

    def shoulder_s(u, r):
        # how far inside the shoulder's edge line (pixels)
        ex, ey = u1 - u0, r1 - r0
        return ((u - u0) * ey - (r - r0) * ex) / math.hypot(ex, ey)

    def height(x, y, d):
        c, r, u = wcr(x, y)
        if r >= 37.0:
            z = Z_BAND
        elif r >= 21.0 and u < 70.5:
            z = Z_DECK
        else:
            z = Z_HEAD
            if r < 21.0:
                z -= (Z_HEAD - Z_DECK) * max(0.0, 1.0 - max(0.0, shoulder_s(u, r)) / SHOULDER_W)
            z -= 0.05 * max(0.0, r - 21.0)
            if 10.4 <= r <= 15.4 and u >= 87.6 and int(math.floor(u)) % 2 == 0:
                z -= 0.6                                       # the vents
        cd = cheek_d(x, y)
        if cd < 0.0:
            z = Z_CHEEK - 0.6 * (1.0 - round_edge(-cd, 0.6)) if cd < -0.24 else z
        vd = cav_d(x, y)
        if vd < -0.24:
            z = Z_CAVITY
        z -= 1.4 * (1.0 - round_edge(d, 1.2))
        return max(z, 1.0)
    # (each step between two contours a quarter pixel apart: its wall a clean band, not a sawtooth of the grid)
    borders = [(lambda x, y, d: -cheek_d(x, y), 0.0), (lambda x, y, d: -cav_d(x, y), 0.0),
               (lambda x, y, d: -cheek_d(x, y), 0.25), (lambda x, y, d: -cav_d(x, y), 0.25),
               (lambda x, y, d: wcr(x, y)[1], 37.0), (lambda x, y, d: wcr(x, y)[1], 21.0),
               (lambda x, y, d: shoulder_s(wcr(x, y)[2], wcr(x, y)[1]), SHOULDER_W)]
    borders += [(lambda x, y, d, uu=uu: wcr(x, y)[2], uu) for uu in (88.0, 89.0, 90.0, 91.0, 92.0, 93.0, 94.0, 95.0)]

    def paint(x, y, d):
        if cav_d(x, y) < 0.0:
            return "cavity"
        if cheek_d(x, y) < 0.0:
            return "cheek"
        return "band" if wcr(x, y)[1] >= 37.0 else "top"
    mats = {"top": m["g6"], "side": m["g3"], "cheek": m["b8"], "cavity": m["g1"], "band": m["d4"]}
    obj = relief("w_head", [outline], height, mats, paint=paint, side="side", bottom=0.0, spacing=0.55,
                 borders=borders, smooth_angle=35.0, band=2.0)

    def pick(c, n):
        cc, r, u = wcr(c.x, c.y)
        if cav_d(c.x, c.y) < 0.05:
            return m["g1"] if n.z > 0.5 else m["g2"]
        if cheek_d(c.x, c.y) < 0.05:
            return shade_by_sun(m, ["b6", "b8", "ba", "l3", "l5"], n, "d3")
        if r >= 37.0:
            return m["d4"] if n.z > 0.5 else m["d3"]
        if n.z < 0.2:
            return m["g3"]
        if 10.4 <= r <= 15.4 and u >= 87.6 and c.z < Z_HEAD - 0.05:
            return m["g2"] if n.z > 0.9 else m["g4"]          # the vents' floors and walls
        return shade_by_sun(m, ["g5", "g7", "g8", "g9", "gb"], n)
    paint_faces(obj, pick)
    return [obj]


# The box at the front (the left half's outline): its top frame chamfered at the corner, its side, its lower corner;
# the neck tab up to the bumper, the grey blocks and the tab along its lower edge (rectangles: u0, u1, r0, r1, top).
BOX = [(95.5, 68.0), (84.0, 68.0), (72.0, 71.2), (68.6, 74.2), (68.4, 96.0), (73.0, 100.4), (81.0, 101.4),
       (90.2, 101.4), (90.2, 102.4), (95.5, 102.4)]
BOX_BLOCKS = [(81.6, 86.4, 95.6, 101.0, 12.0), (91.8, 95.5, 95.6, 102.2, 11.8), (90.8, 95.5, 68.4, 73.6, 13.2)]


def box(mk_, m):
    """The box at the front: its blue frame round the middle bay, its grey lower edge with blocks, the neck tab up to
    the bumper."""
    outline = full(BOX)
    hole = bay_holes()[2]

    def height(x, y, d):
        c, r, u = wcr(x, y)
        z = Z_BOX if r < 95.6 else Z_BOX - 0.8
        z -= 1.6 * (1.0 - round_edge(d, 1.4))
        return z
    mats = {"top": m["b8"], "side": m["d3"]}
    obj = relief("w_box", [outline, hole], height, mats, side="side", bottom=0.0, spacing=0.6,
                 borders=[(lambda x, y, d: wcr(x, y)[1], 95.6)], smooth_angle=35.0, band=2.0)

    def pick(c, n):
        cc, r, u = wcr(c.x, c.y)
        if bay_d(c.x, c.y) < 0.3 and n.z < 0.5:
            return m["g2"]
        if n.z < 0.2:
            return m["d3"]
        if r > 95.6:
            return shade_by_sun(m, ["d3", "d4", "b6", "b8", "ba"], n)
        return shade_by_sun(m, ["b6", "b8", "ba", "l3", "l5"], n)
    paint_faces(obj, pick)
    parts = [obj]
    for i, (u0, u1, r0, r1, top) in enumerate(BOX_BLOCKS):
        (x0, y1), (x1, y0) = wp(u0, r0), wp(u1, r1)
        for j, (a, b) in enumerate([(x0, x1), (2 * AXIS_X - x1, 2 * AXIS_X - x0)]):
            if u1 >= 95.5 and j == 1:
                continue
            if u1 >= 95.5:
                b = 2 * AXIS_X - a
            blk = mk.box(f"w_box_block{i}{j}", a, b, y0, y1, 0.0, top, m["g5"])
            mk.bevel(blk, 0.45, 2, 30)
            mk.shade(blk, 35)
            paint_faces(blk, lambda c, n: shade_by_sun(m, ["g3", "g4", "g5", "g7", "g8"], n, "g3"))
            parts.append(blk)
    return parts


def collars(mk_, m):
    """The blue horseshoe's arms round the eye: rounded beams over their outlines (a low roof along their middles)."""
    M = mk_
    loops = loops_of(M.collar)
    inside = InsideDistance(loops)

    def height(x, y, d):
        return min(15.6, 10.6 + 1.8 * round_edge(d, 1.3) + 0.55 * max(0.0, inside(x, y) - 1.3))
    obj = relief("w_collar", loops, height, {"top": m["b8"], "side": m["d3"]}, side="side", bottom=0.0,
                 spacing=0.5, smooth_angle=60.0, band=3.0)
    paint_faces(obj, lambda c, n: shade_by_sun(m, ["b6", "b8", "ba", "l3", "l5"], n, "d3"))
    return [obj]


# The bumper: its middle line from its left end round under the eye to the axis ((mirrored column, row) and its
# half-height there (up the screen); its height (the bar's top); its cross-section's power (boxiness).
BUMPER = [(69.0, 58.6, 3.6), (71.0, 58.6, 4.8), (74.0, 59.6, 6.0), (78.0, 61.0, 6.6), (84.0, 62.2, 6.2),
          (90.0, 62.6, 5.6), (95.5, 62.7, 5.5)]
BUMPER_Z = (10.6, 4.6)            # the bar's axis height, its half-thickness (z)
BUMPER_POWER = 2.6


def bumper(mk_, m):
    """The thick grey bumper curving under the eye: a bar lofted along its middle line, rounded-box sections, its ends
    rounded off."""
    left = [(u, r, h) for u, r, h in BUMPER]
    pts = [Vector((wp(u, r)[0], wp(u, r)[1], BUMPER_Z[0])) for u, r, h in left]
    hs = [h for _, _, h in left]
    mirror = [Vector((2 * AXIS_X - p.x, p.y, p.z)) for p in reversed(pts[:-1])]
    path = pts + mirror
    halves = hs + list(reversed(hs[:-1]))
    dense = mk.chaikin([tuple(p) + (h,) for p, h in zip(path, halves)], 2, closed=False)
    stations = [(Vector(p[:3]), p[3]) for p in dense]
    rings = []
    n = len(stations)
    for i, (p, h) in enumerate(stations):
        t = (stations[min(i + 1, n - 1)][0] - stations[max(i - 1, 0)][0]).normalized()
        across = Vector((-t.y, t.x, 0.0))
        ring = []
        for j in range(24):
            a = 2 * math.pi * j / 24
            cx, sz = mk.superellipse_point(a, BUMPER_POWER)
            ring.append(p + across * (cx * h) + Vector((0, 0, sz * BUMPER_Z[1])))
        rings.append(ring)
    start = stations[0][0] - (stations[1][0] - stations[0][0]).normalized() * 1.2
    end = stations[-1][0] + (stations[-1][0] - stations[-2][0]).normalized() * 1.2
    obj = k.loft("w_bumper", rings, m["g7"], start_point=tuple(start), end_point=tuple(end))
    k.smooth(obj, 50)
    paint_faces(obj, lambda c, n: shade_by_sun(m, ["g5", "g7", "g8", "ga", "gc"], n))
    return [obj]


def eye(mk_, m):
    """The great glossy black eye in its socket: an ellipsoid, a bright glint up its left; the socket's dark floor."""
    M = mk_
    socket = relief("w_socket", loops_of(M.eye), lambda x, y, d: 4.5, {"top": m["g1"], "side": m["g1"]}, side="side",
                    bottom=0.0, spacing=0.8, smooth_angle=35.0)
    cx, cy = AXIS_X, WY - 49.5
    ball = k.ellipsoid("w_eye", (cx, cy, 6.0), (13.6, 8.6, 6.6), m["e1"], 48, 24)
    band_split(ball, [Vector((v.co.x - cx, v.co.y - cy, v.co.z - 6.0)).normalized().dot(EYE_GLINT)
                      for v in ball.data.vertices], [(-9.0, m["e1"]), (0.55, m["e2"]), (0.86, m["e3"]),
                                                     (0.95, m["e4"])])
    k.smooth(ball, 80)
    rim = mk.tube("w_eye_rim", [(cx + 14.1 * math.cos(2 * math.pi * j / 64), cy + 9.1 * math.sin(2 * math.pi * j / 64),
                                 6.4) for j in range(65)], 0.9, m["g2"], 10, cap=False)
    k.smooth(rim, 60)
    return [socket, ball, rim]


EYE_GLINT = Vector((-0.42, 0.55, 0.72)).normalized()


# The turrets' outlines (the left pod's; (column, row) pixel edges): the turret, a box with the barrel's breech
# rising out of its back, and the small box beside it.
TURRET = [(42.2, 20.6), (42.2, 12.2), (44.4, 11.0), (46.0, 9.2), (47.4, 8.3), (50.6, 8.3), (52.4, 9.4), (55.4, 11.0),
          (59.6, 11.8), (59.8, 20.6)]
TURRET_SMALL = [(30.4, 22.0), (30.4, 17.0), (32.4, 15.8), (36.2, 15.4), (42.4, 15.4), (42.4, 22.0)]


def turrets(mk_, m):
    """On each pod's back edge (the left one built, the right one its mirror image): the turret, a box with a barrel
    lying back up the screen and a lamp; the small box beside it with its knob."""
    loops = [[wp(u, r) for u, r in TURRET]]

    def height(x, y, d):
        return Z_TURRET - 1.8 * (1.0 - round_edge(d, 1.4))
    box_ = relief("w_turret", loops, height, {"top": m["g6"], "side": m["g3"]}, side="side", bottom=0.0,
                  spacing=0.45, smooth_angle=35.0)
    paint_faces(box_, lambda c, n: shade_by_sun(m, ["g3", "g5", "g6", "g8", "ga"], n, "g3"))
    sloops = [[wp(u, r) for u, r in TURRET_SMALL]]

    def sheight(x, y, d):
        return Z_TURRET_SMALL - 1.5 * (1.0 - round_edge(d, 1.2))
    sbox = relief("w_turret_small", sloops, sheight, {"top": m["g6"], "side": m["g3"]}, side="side",
                  bottom=0.0, spacing=0.45, smooth_angle=35.0)
    paint_faces(sbox, lambda c, n: shade_by_sun(m, ["g3", "g5", "g6", "g8", "ga"], n, "g3"))
    parts = [box_, sbox]
    bx = 48.9 + WX                                           # the barrel's axis (column 48.9)
    barrel = mk.tube("w_barrel", [(bx, WY - 20.0, Z_TURRET + 0.6), (bx, WY - 9.4, Z_TURRET + 0.6),
                                  (bx, WY - 8.6, Z_TURRET + 0.6)], 2.0, m["g7"], 20,
                     radii=[2.0, 2.0, 1.4])
    k.smooth(barrel, 45)
    paint_faces(barrel, lambda c, n: shade_by_sun(m, ["g4", "g6", "g7", "g9", "gb"], n))
    muzzle = mk.tube("w_muzzle", [(bx, WY - 8.7, Z_TURRET + 0.6), (bx, WY - 8.4, Z_TURRET + 0.6)], 1.0, m["g1"], 16)
    lamp = k.ellipsoid("w_lamp", (53.6 + WX, WY - 15.5, Z_TURRET - 0.1), (1.05, 1.05, 0.7), m["lamp"], 16, 8)
    k.smooth(lamp, 70)
    knob = k.ellipsoid("w_knob", (33.6 + WX, WY - 18.0, Z_TURRET_SMALL - 0.1), (1.3, 1.6, 1.0), m["g8"], 16, 8)
    k.smooth(knob, 70)
    parts += [barrel, muzzle, lamp, knob]
    for obj in parts:
        mk.apply(obj)
    return parts + [mirror_x_obj(o, o.name + "_r") for o in parts]


def rails(mk_, m):
    """The grey rails down the pods' inner sides between the bays and the collars: rounded bars along y."""
    parts = []
    x = 58.2 + WX
    rail = mk.tube("w_irail", [(x, WY - 41.5, 9.6), (x, WY - 66.0, 9.6)], 2.5, m["g5"], 20)
    k.smooth(rail, 45)
    paint_faces(rail, lambda c, n: shade_by_sun(m, ["g3", "g4", "g5", "g7", "g8"], n))
    parts.append(rail)
    for obj in parts:
        mk.apply(obj)
    return parts + [mirror_x_obj(o, o.name + "_r") for o in parts]


# The hips (the left one; (mirrored column, row)): the dark bed of the mechanism, its ball joints (column, row, radius,
# height), the pistons (paths of (column, row, height), radius).
HIP_BED = [(57.4, 56.0), (66.0, 56.0), (68.4, 60.0), (68.4, 84.0), (60.0, 84.0), (55.6, 80.0), (55.6, 68.0)]
HIP_BALLS = [(64.6, 62.6, 2.4, 9.2), (61.2, 66.8, 2.1, 9.0)]
HIP_PISTONS = [([(61.0, 67.5, 8.8), (58.6, 71.4, 8.2), (56.6, 74.6, 7.6)], 1.35),
               ([(64.6, 64.0, 8.6), (64.6, 75.0, 7.8), (64.6, 86.0, 7.0)], 1.5)]


def hips(mk_, m):
    """The hips between the pods, the bumper and the box: a dark bed, two ball joints, a piston down to the leg and one
    beside the box."""
    bed = relief("w_hip_bed", [[wp(u, r) for u, r in HIP_BED]], lambda x, y, d: Z_HIP - 1.2 * (1.0 - round_edge(d, 1.0)),
                 {"top": m["g2"], "side": m["g2"]}, side="side", bottom=0.0, spacing=0.6, smooth_angle=35.0)
    parts = [bed]
    for i, (u, r, rad, z) in enumerate(HIP_BALLS):
        x, y = wp(u, r)
        ball = k.ellipsoid(f"w_ball{i}", (x, y, z), (rad, rad, rad * 0.9), m["g7"], 20, 10)
        band_split(ball, [Vector((v.co.x - x, v.co.y - y, v.co.z - z)).normalized().dot(LIGHT)
                          for v in ball.data.vertices], [(-9.0, m["g3"]), (0.3, m["g6"]), (0.75, m["g9"]),
                                                         (0.93, m["gc"])])
        k.smooth(ball, 70)
        parts.append(ball)
    for i, (path, rad) in enumerate(HIP_PISTONS):
        pts = [(wp(u, r)[0], wp(u, r)[1], z) for u, r, z in path]
        piston = mk.tube(f"w_piston{i}", pts, rad, m["g6"], 14)
        k.smooth(piston, 50)
        paint_faces(piston, lambda c, n: shade_by_sun(m, ["g3", "g4", "g6", "g8", "g9"], n))
        parts.append(piston)
    for obj in parts:
        mk.apply(obj)
    return parts + [mirror_x_obj(o, o.name + "_r") for o in parts]


# The leg (the left one; (mirrored column, row) outlines): the mount under the pod with its axle, the strut, the
# housing; the rods between them (column, from row, to row, radius, height), the clamp; the foot (its middle, radii).
LEG_MOUNT = [(40.4, 83.6), (56.6, 83.6), (56.6, 90.4), (53.4, 91.0), (53.6, 93.6), (49.6, 94.4), (46.0, 94.0),
             (44.0, 92.4), (40.4, 90.4)]
LEG_STRUT = [(44.2, 93.0), (54.8, 93.0), (54.8, 96.8), (52.6, 97.8), (49.6, 101.4), (45.2, 101.4), (44.2, 100.0)]
LEG_HOUSING = [(42.4, 108.6), (52.6, 108.6), (52.8, 113.8), (56.2, 114.6), (56.6, 119.8), (42.4, 119.8)]
LEG_RODS = [(47.0, 100.0, 109.0, 1.9, 4.8), (51.0, 97.5, 110.0, 1.4, 5.4)]
LEG_AXLE = (41.0, 56.0, 86.8, 1.9, 6.4)          # from column, to column, row, radius, height
FOOT = (49.6, 125.4, 6.9, 6.2, 5.2)              # column, row, radii (x, y), height


def legs(mk_, m):
    """The legs reaching down the screen (the left one built, the right one its mirror image): the mount under the pod
    with its axle across, the strut, the rods (a cylinder and the piston beside it), the clamp, the housing, the round
    armoured foot with a ringed hub and a lens."""
    parts = []

    def block(name, outline, top, keys, edge=1.0):
        obj = relief(name, [[wp(u, r) for u, r in outline]], lambda x, y, d: top - 1.2 * (1.0 - round_edge(d, edge)),
                     {"top": m[keys[2]], "side": m["g2"]}, side="side", bottom=0.0, spacing=0.45, smooth_angle=35.0)
        paint_faces(obj, lambda c, n: shade_by_sun(m, keys, n, "g2"))
        return obj
    parts.append(block("w_leg_mount", LEG_MOUNT, 7.6, ["g2", "g3", "g3", "g5", "g6"]))
    parts.append(block("w_leg_strut", LEG_STRUT, 6.8, ["g2", "g3", "g4", "g6", "g8"]))
    parts.append(block("w_leg_housing", LEG_HOUSING, 7.0, ["g2", "g3", "g4", "g6", "g8"], 1.3))
    u0, u1, r, rad, z = LEG_AXLE
    axle = mk.tube("w_leg_axle", [(wp(u0, r)[0], wp(u0, r)[1], z), (wp(u1, r)[0], wp(u1, r)[1], z)], rad, m["g5"], 18)
    k.smooth(axle, 45)
    paint_faces(axle, lambda c, n: shade_by_sun(m, ["g3", "g4", "g5", "g7", "g8"], n))
    parts.append(axle)
    for i, (u, ra, rb, rad, z) in enumerate(LEG_RODS):
        rod = mk.tube(f"w_leg_rod{i}", [(wp(u, ra)[0], wp(u, ra)[1], z), (wp(u, rb)[0], wp(u, rb)[1], z)], rad,
                      m["g7"], 16)
        k.smooth(rod, 45)
        paint_faces(rod, lambda c, n: shade_by_sun(m, ["g3", "g5", "g7", "g9", "gb"], n))
        parts.append(rod)
    clamp = mk.box("w_leg_clamp", wp(43.2, 0)[0], wp(51.6, 0)[0], WY - 110.8, WY - 108.6, 0.0, 6.6, m["g6"])
    mk.bevel(clamp, 0.4, 2, 30)
    mk.shade(clamp, 35)
    paint_faces(clamp, lambda c, n: shade_by_sun(m, ["g3", "g4", "g6", "g8", "g9"], n, "g3"))
    parts.append(clamp)
    fu, fr, rx, ry, fh = FOOT
    x, y = wp(fu, fr)
    foot = mk.dome("w_foot", (x, y), (rx, ry, fh), 0.0, m["g4"], 44, 8, 2.6)
    paint_faces(foot, lambda c, n: shade_by_sun(m, ["g2", "g3", "g4", "g6", "g8"], n))
    ring = mk.tube("w_foot_ring", [(x + 4.3 * math.cos(2 * math.pi * j / 48), y + 3.9 * math.sin(2 * math.pi * j / 48),
                                    fh - 0.05) for j in range(49)], 0.75, m["g8"], 10, cap=False)
    k.smooth(ring, 60)
    hub = mk.dome("w_foot_hub", (x, y), (2.9, 2.6, 0.9), fh - 0.35, m["g1"], 28, 4)
    lens = k.ellipsoid("w_foot_lens", (x - 0.2, y + 0.2, fh + 0.35), (1.35, 1.25, 0.7), m["lens"], 16, 8)
    k.smooth(lens, 70)
    parts += [foot, ring, hub, lens]
    for obj in parts:
        mk.apply(obj)
    return parts + [mirror_x_obj(o, o.name + "_r") for o in parts]


def bay_hatches(m):
    """The walker's own hatches at the bottoms of its bays (flat: under the hatch enemies FLEET puts in them; STATION
    shows these)."""
    parts = []
    for i, (bx, by) in enumerate(BAYS):
        hp = hatch(m, 0.0, BAY_HATCH_ZS, prefix=f"w_bayhatch{i}")
        mk.transform(hp, Matrix.Translation((bx, by, 0.0)))
        parts += hp
    return parts


def walker_whole():
    k.reset()
    m = materials()
    M = Masks()
    parts = (armour(M, m) + pods(M, m) + head(M, m) + box(M, m) + collars(M, m) + bumper(M, m) + eye(M, m) +
             turrets(M, m) + rails(M, m) + hips(M, m) + legs(M, m) + bay_hatches(m))
    for obj in parts:
        mk.apply(obj)
    bpy.context.view_layer.update()
    return parts, m, M


# The pieces: (sprite, its top left pixel in the whole picture), as the level events lay them out.
WALKER_LAYOUT = ([(1 + 2 * i, 24 * i, 0) for i in range(8)] + [(39 + 2 * i, 24 * i, 28) for i in range(8)] +
                 [(77 + 2 * i, 24 * i, 56) for i in range(8)] + [(118 + 2 * i, 36 + 24 * i, 84) for i in range(5)] +
                 [(156, 36, 112), (164, 132, 112)])


def walker_pieces():
    out = []
    for sprite, c0, r0 in WALKER_LAYOUT:
        x0, y1 = WX + c0, WY - r0
        x1, y0 = x0 + 24, y1 - 28
        origin = ((x0 + x1) / 2, (y0 + y1) / 2)
        bx0 = x0 - 20.0 if c0 == 0 else x0
        bx1 = x1 + 20.0 if c0 + 24 == 192 else x1
        by1 = y1 + 20.0 if r0 == 0 else y1
        by0 = y0 - 20.0 if r0 + 28 == 140 else y0
        out.append((f"fleet_walker_{sprite}", sprite, (bx0, bx1, by0, by1), origin))
    return out


def walker_mask(sheet):
    mask = [[False] * 192 for _ in range(140)]
    for sprite, c0, r0 in WALKER_LAYOUT:
        for r, line in enumerate(k.sprite_mask(sheet, sprite)):
            for c, v in enumerate(line):
                if v:
                    mask[r0 + r][c0 + c] = True
    return mask


def build_walker(options, sheet, only):
    names = [p[0] for p in walker_pieces()]
    if only and not any(n in only for n in names) and "walker_whole" not in only:
        return {}
    whole, m, M = walker_whole()
    triangulate(whole)
    bpy.context.view_layer.update()
    bpy.context.scene.view_settings.view_transform = "Standard"
    low, high = mk.bounds(whole)
    print("== walker: %d triangles, %d materials, x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (
        mk.triangles(whole), len(mk.materials_of(whole)), low.x, high.x, low.y, high.y, low.z, high.z))
    if sheet:
        mk.compare("walker, as the camera sees it", mk.coverage(whole, 192, 140), walker_mask(sheet))
    if "whole" in options or "preview" in options:
        seen = copy_objects(whole, "_seen")
        shear_to_camera(seen)
        for o in whole:
            o.hide_render = True
        if "whole" in options:
            mk.export(seen, options["whole"] + "fleet_walker.glb")
        if "preview" in options:
            mk.preview(options["preview"] + "fleet_walker", seen, size=(192, 140), scale=5, distance=3.0)
        remove(seen)
        for o in whole:
            o.hide_render = False
    return export_pieces(whole, walker_pieces(), lambda src: m["g2"], options, sheet, only=only)


# --- Main -----------------------------------------------------------------------------------------------------------
GROUPS = {"hatch": [n for fl, fr, _ in [(191, 193, 0.0)] + HATCH_FRAMES for n, *_ in hatch_pieces(fl, fr)],
          "walker": ["fleet_walker_%d" % s for s, _, _ in WALKER_LAYOUT]}


def build():
    options = k.args()
    only = None
    if "only" in options:
        only = set()
        for name in options["only"].split(","):
            only |= set(GROUPS.get(name, [name]))
    sheet = None
    if "check" in options:
        sheets = options["check"]
        sheet = os.path.join(sheets, "enemy_O.png") if os.path.isdir(sheets) else sheets
    results = build_hatches(options, sheet, only)
    results.update(build_walker(options, sheet, only))
    if sheet:
        for name, score in results.items():
            if score is not None:
                print("overlap %-26s %.3f" % (name, score))


if __name__ == "__main__":
    build()
