"""Enemies of wave 3, batch AL (sheet %, written x25 in models.cfg): CORAL's great domed citadel at the end of the
level, modelled as its sprites look (models.cfg: yaw=0), on the ground. The kit is wave3_al_kit.py, the pixels
wave3_al_art.py (DOME); the rest of the sheet is in wave3_al.py and wave3_al_ball.py.

CORAL builds the citadel from 43 custom ground enemies (events of type 49 and 52, shape bank 36 = sheet %): at
t5450 the rows % 39-55, 77-93, 115-131 at (54 + 24 i, -84), (54 + 24 i, -56), (54 + 24 i, -28) and % 155-167 at
(78 + 24 i, 0); 28 ticks later the top row % 1-17 at (54 + 24 i, -84), on top of them as the ground has scrolled:
the sheet's own layout, 216 x 140 pixels (its top is cut straight: the sprites stop there). Its two blue eggs
(CORAL's enemies 1224 above 1225, wave3_ae_coral.py) are put into the two bays of its dome (x 92 and 210).

What it is: the near half of a huge round fortress on the sea floor. A stone dome laid with grey and blue-grey
blocks rises over a dark wall; in it two dark bays, each holding two pods lying side by side (the eggs sit in
them), and at its top a red core glowing in a dark ring, a thick pipe running from it up the screen. Round the
dome's foot runs a purple trench, parted by low walls into bays, a tall grey spike standing in each (one or two),
and round that a dark grey rampart.

- coral_citadel_1 ... _17, _39 ... _55, _77 ... _93, _115 ... _131 (odd numbers), _155 ... _167 (% the same
  sprites): the citadel, built whole as a relief over the sprites' pixels (each pixel's height by what it shows:
  the dome's blocks raised between their joints, its dark wall, the trench's floor and walls, the rampart's
  slopes), painted pixel by pixel, the spikes, the core, the pipe and the pods built as parts of their own; cut into
  its 43 pieces (origin).

usage: Blender -b --factory-startup -P wave3_al_citadel.py -- [--only name,name] [--preview <prefix>]
       [--check 1] [--stats 1] [--whole <prefix>]
"""
import math
import os
import sys
from collections import Counter, deque

import bmesh
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_al_kit as kit  # noqa: E402
from wave3_al_kit import k, sh, w, pal, Painter  # noqa: E402

ORIGIN = (108, 70)
DOME = kit.frame("DOME", 216, ORIGIN)
H, W = 140, 216
OX, OY = ORIGIN

BAYS = (-58.0, 60.0)        # the bays' middles (x), where the eggs are put
BAY_HALF = 12.0             # their half width
BAY_ROUND = 42.0            # where their rounded south ends start (y)

Z_TRENCH = 2.0              # the trench's floor
Z_DIVIDER = 4.6             # the low walls across it
Z_RAMPART = 7.0             # the rampart's top
Z_PIT = 0.4                 # the bays' floors


def X(c):
    return c + 0.5 - OX


def Y(r):
    return OY - r - 0.5


def ramp(v):
    return v >> 4


def shade(v):
    return v & 15


def in_bay(x, y):
    for cx in BAYS:
        dx = abs(x - cx)
        if dx <= BAY_HALF and y >= BAY_ROUND:
            return True
        if (dx / BAY_HALF) ** 2 + ((y - BAY_ROUND) / 11.5) ** 2 <= 1.0:
            return True
    return False


def dome_z(x, y):
    """The dome's surface: highest along the middle near the core, falling to its foot."""
    s = 1.0 - (x / 85.0) ** 2 - (max(0.0, 18.0 - y) / 58.0) ** 2
    return 4.5 + 5.5 * max(0.0, s) ** 0.65


def distance(mask_from, passable):
    """Distance in pixels (8-neighbour chamfer: 1 straight, 1.414 diagonal, close to the true distance) from the
    pixels mask_from marks, through the pixels passable marks (None where it cannot reach)."""
    inf = 1e9
    d = [[0.0 if mask_from[r][c] else inf for c in range(W)] for r in range(H)]
    diag = 2 ** 0.5
    fwd = ((-1, -1, diag), (0, -1, 1.0), (1, -1, diag), (-1, 0, 1.0))
    bwd = ((1, 1, diag), (0, 1, 1.0), (-1, 1, diag), (1, 0, 1.0))
    for _ in range(2):
        for r in range(H):
            for c in range(W):
                if not passable[r][c] and not mask_from[r][c]:
                    continue
                best = d[r][c]
                for dc, dr, wt in fwd:
                    cc, rr = c + dc, r + dr
                    if 0 <= cc < W and 0 <= rr < H and d[rr][cc] + wt < best:
                        best = d[rr][cc] + wt
                d[r][c] = best
        for r in range(H - 1, -1, -1):
            for c in range(W - 1, -1, -1):
                if not passable[r][c] and not mask_from[r][c]:
                    continue
                best = d[r][c]
                for dc, dr, wt in bwd:
                    cc, rr = c + dc, r + dr
                    if 0 <= cc < W and 0 <= rr < H and d[rr][cc] + wt < best:
                        best = d[rr][cc] + wt
                d[r][c] = best
    return [[None if v >= inf else v for v in row] for row in d]


def classify():
    """Each pixel's part: D dome block, J dome joint, C core, P pipe, B bay, V the dome's wall, T trench floor,
    I trench wall (divider), S spike (and its shadow), R rampart; None transparent. Returns (classes, the
    pixels' colours as painted, their target heights)."""
    g = DOME.g
    opaque = [[g[r][c] is not None for c in range(W)] for r in range(H)]

    def domeish(v):
        return (ramp(v) == 0 and shade(v) >= 6) or ramp(v) in (6, 7, 3, 2)
    dome = [[False] * W for _ in range(H)]
    q = deque([(108, 60)])
    dome[60][108] = True
    while q:
        c, r = q.popleft()
        for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            cc, rr = c + dc, r + dr
            if 13 <= cc <= 203 and 0 <= rr < H and not dome[rr][cc] and opaque[rr][cc] and domeish(g[rr][cc]) \
                    and not in_bay(X(cc), Y(rr)):
                dome[rr][cc] = True
                q.append((cc, rr))
    trench = [[False] * W for _ in range(H)]
    for r in range(H):
        cols = [c for c in range(W) if opaque[r][c] and ramp(g[r][c]) == 5]
        if not cols:
            continue
        for c in range(min(cols), max(cols) + 1):
            if opaque[r][c] and not dome[r][c] and not in_bay(X(c), Y(r)):
                trench[r][c] = True
    d_dome = distance(dome, opaque)
    cls = [[None] * W for _ in range(H)]
    for r in range(H):
        for c in range(W):
            v = g[r][c]
            if v is None:
                continue
            x, y = X(c), Y(r)
            if in_bay(x, y):
                cls[r][c] = "B"
            elif dome[r][c]:
                if ramp(v) == 7:
                    cls[r][c] = "C"
                elif ramp(v) == 6 and r < 10 and 95 < c < 122:
                    cls[r][c] = "P"
                else:
                    cls[r][c] = "D"
            elif trench[r][c]:
                if ramp(v) == 5:
                    cls[r][c] = "T"
                elif ramp(v) == 0 and shade(v) <= 2 and d_dome[r][c] is not None and d_dome[r][c] <= 5:
                    cls[r][c] = "V"
                elif ramp(v) == 0 and shade(v) in (3, 4, 5):
                    cls[r][c] = "I"
                else:
                    cls[r][c] = "S"
            else:
                cls[r][c] = "R"
    # The dark band under the dome where no trench runs (its sides): the dome's wall too.
    for r in range(H):
        for c in range(W):
            if cls[r][c] == "R" and shade(g[r][c]) <= 3 and d_dome[r][c] is not None and d_dome[r][c] <= 4 and r > 60:
                cls[r][c] = "V"
    # The dome's joints: the straight lines between its blocks (runs of 4 or more like pixels across which the
    # pixels on both sides differ from them).
    def run(c, r, dc, dr):
        n_ = 1
        for sgn in (1, -1):
            cc, rr = c + sgn * dc, r + sgn * dr
            while 0 <= cc < W and 0 <= rr < H and g[rr][cc] == g[r][c] and cls[rr][cc] == "D":
                n_ += 1
                cc, rr = cc + sgn * dc, rr + sgn * dr
        return n_

    def differs(c, r, dc, dr):
        """Whether the pixels on both sides of (c, r), along (dc, dr), differ from it."""
        for sgn in (1, -1):
            cc, rr = c + sgn * dc, r + sgn * dr
            if 0 <= cc < W and 0 <= rr < H and g[rr][cc] == g[r][c]:
                return False
        return True
    joints = [(c, r) for r in range(H) for c in range(W)
              if cls[r][c] == "D" and ramp(g[r][c]) == 0 and
              ((run(c, r, 1, 0) >= 4 and differs(c, r, 0, 1)) or (run(c, r, 0, 1) >= 4 and differs(c, r, 1, 0)))]
    for c, r in joints:
        cls[r][c] = "J"
    near_bay = [[any(in_bay(X(c) + dx, Y(r) + dy) for dx in (-4, 0, 4) for dy in (-4, 0, 4)) for c in range(W)]
                for r in range(H)]
    colour = [[g[r][c] for c in range(W)] for r in range(H)]
    # Colours: the blocks evened out (the game lights the dome), the joints dark, the trench's spikes and their
    # shadows the floor's purple round them, the pipe and core (covered by their parts) dark.
    for r in range(H):
        for c in range(W):
            k_ = cls[r][c]
            v = g[r][c]
            if k_ == "D":
                if near_bay[r][c] and ramp(v) == 0:
                    colour[r][c] = v
                else:
                    colour[r][c] = 0x6a if ramp(v) == 6 else (0x09 if shade(v) <= 9 else 0x0a)
            elif k_ == "J":
                colour[r][c] = 0x06
            elif k_ in ("C", "P"):
                colour[r][c] = 0x05
            elif k_ == "B":
                colour[r][c] = 0x01
            elif k_ == "S":
                near = Counter(g[rr][cc] for rr in range(max(0, r - 3), min(H, r + 4))
                               for cc in range(max(0, c - 4), min(W, c + 5)) if cls[rr][cc] == "T")
                colour[r][c] = near.most_common(1)[0][0] if near else 0x55
            elif k_ == "V":
                colour[r][c] = 0x02
    # Heights.
    trench_mask = [[cls[r][c] in ("T", "S", "I") for c in range(W)] for r in range(H)]
    d_trench = distance(trench_mask, opaque)
    outside = [[not opaque[r][c] or c == 0 or c == W - 1 for c in range(W)] for r in range(H)]
    d_out = distance(outside, [[True] * W for _ in range(H)])
    target = [[None] * W for _ in range(H)]
    for r in range(H):
        for c in range(W):
            k_ = cls[r][c]
            if k_ is None:
                continue
            x, y = X(c), Y(r)
            if k_ in ("D", "C", "P"):
                z = dome_z(x, y)
            elif k_ == "J":
                z = dome_z(x, y) - 0.75
            elif k_ == "B":
                z = Z_PIT
            elif k_ == "V":
                dd = d_dome[r][c] or 1
                z = Z_TRENCH + (dome_z(x, y) - Z_TRENCH) * max(0.0, 1.0 - dd / 5.0)
            elif k_ in ("T", "S"):
                z = Z_TRENCH
            elif k_ == "I":
                z = Z_DIVIDER
            else:  # the rampart: up from the outside, down into the trench
                do = d_out[r][c] if d_out[r][c] is not None else 9
                dt = d_trench[r][c] if d_trench[r][c] is not None else 99
                z = min(0.6 + 1.1 * do, Z_RAMPART, Z_TRENCH + 1.3 * dt)
            target[r][c] = z
    # The rampart and the dome's wall smoothed a little (their slopes follow the outline, not its pixel steps).
    for _ in range(2):
        out = [row[:] for row in target]
        for r in range(H):
            for c in range(W):
                if cls[r][c] not in ("R", "V"):
                    continue
                vals = [target[rr][cc] for rr in range(max(0, r - 1), min(H, r + 2))
                        for cc in range(max(0, c - 1), min(W, c + 2)) if cls[rr][cc] == cls[r][c]]
                out[r][c] = sum(vals) / len(vals)
        target = out
    return cls, colour, target


def relief(name, cls, colour, target, painter, under):
    """The citadel's body: a quad per pixel, its corners at the mean height of the pixels round them, walls down
    to the ground round its outline, a flat bottom; each pixel painted its colour."""
    zc = [[0.0] * (W + 1) for _ in range(H + 1)]
    for j in range(H + 1):
        for i in range(W + 1):
            vals = [target[r][c] for r in (j - 1, j) for c in (i - 1, i)
                    if 0 <= r < H and 0 <= c < W and target[r][c] is not None]
            zc[j][i] = sum(vals) / len(vals) if vals else 0.0
            # Round the outline (not the top edge, where the sprites stop): down to the ground there.
            if j > 0 and len(vals) < 4 and vals:
                zc[j][i] = min(zc[j][i], 0.3)
    bm = bmesh.new()
    top, low = {}, {}

    def vt(i, j):
        if (i, j) not in top:
            top[(i, j)] = bm.verts.new((i - OX, OY - j, zc[j][i]))
        return top[(i, j)]

    def vb(i, j):
        if (i, j) not in low:
            low[(i, j)] = bm.verts.new((i - OX, OY - j, 0.0))
        return low[(i, j)]
    mats, index = [], {}

    def mat_index(m):
        if m.name not in index:
            index[m.name] = len(mats)
            mats.append(m)
        return index[m.name]
    under_i = mat_index(under)
    for r in range(H):
        for c in range(W):
            if target[r][c] is None:
                continue
            mi = mat_index(painter(colour[r][c]))
            a, b, cc, d = vt(c, r + 1), vt(c + 1, r + 1), vt(c + 1, r), vt(c, r)   # counter-clockwise from above
            if abs(a.co.z - cc.co.z) <= abs(b.co.z - d.co.z):
                tris = ((a, b, cc), (a, cc, d))
            else:
                tris = ((a, b, d), (b, cc, d))
            for t in tris:
                f = bm.faces.new(t)
                f.material_index = mi
            f = bm.faces.new((vb(c, r), vb(c + 1, r), vb(c + 1, r + 1), vb(c, r + 1)))
            f.material_index = under_i
            # Walls where the outline runs.
            for (dc, dr), (p, q_) in (((0, -1), ((c + 1, r), (c, r))), ((0, 1), ((c, r + 1), (c + 1, r + 1))),
                                      ((-1, 0), ((c, r), (c, r + 1))), ((1, 0), ((c + 1, r + 1), (c + 1, r)))):
                rr, cc_ = r + dr, c + dc
                if 0 <= rr < H and 0 <= cc_ < W and target[rr][cc_] is not None:
                    continue
                f = bm.faces.new((vt(*p), vb(*p), vb(*q_), vt(*q_)))
                f.material_index = mi
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    for m in mats:
        obj.data.materials.append(m)
    # The flat bottom merged into few faces (the top keeps its quads: merged, its gentle curves would shade in
    # streaks).
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    low_v = [v for v in bm.verts if v.co.z < 1e-4]
    low_e = [e for e in bm.edges if all(v.co.z < 1e-4 for v in e.verts)]
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(1.0), verts=low_v, edges=low_e, delimit={"MATERIAL"})
    ngons = [f_ for f_ in bm.faces if len(f_.verts) > 3]
    bmesh.ops.triangulate(bm, faces=ngons, quad_method="BEAUTY", ngon_method="EAR_CLIP")
    bm.to_mesh(obj.data)
    bm.free()
    return k.smooth(obj, 32)


def blobs(cls, want):
    """The 8-connected groups of pixels of the classes in `want`: lists of (column, row)."""
    seen = set()
    out = []
    for r in range(H):
        for c in range(W):
            if cls[r][c] in want and (c, r) not in seen:
                group, q = [], deque([(c, r)])
                seen.add((c, r))
                while q:
                    cc, rr = q.popleft()
                    group.append((cc, rr))
                    for dc in (-1, 0, 1):
                        for dr in (-1, 0, 1):
                            n_ = (cc + dc, rr + dr)
                            if 0 <= n_[0] < W and 0 <= n_[1] < H and n_ not in seen and cls[n_[1]][n_[0]] in want:
                                seen.add(n_)
                                q.append(n_)
                out.append(group)
    return out


def spikes(cls):
    """The trench's spikes: grey cones standing in it, leaning up the screen to their points as the sprites draw
    them (each from its light pixels: its foot at their lowest row, its point at their highest)."""
    g = DOME.g
    steel = pal("citadel_spike", 0x0a, metallic=0.65, roughness=0.25)
    steel_tip = pal("citadel_spike_tip", 0x0d, metallic=0.6, roughness=0.2)
    count = 0
    lit = [[cls[r][c] == "S" and g[r][c] is not None and ramp(g[r][c]) in (0, 6) and shade(g[r][c]) >= 6
            for c in range(W)] for r in range(H)]
    for group in blobs([["S" if lit[r][c] else None for c in range(W)] for r in range(H)], {"S"}):
        if len(group) < 3:
            continue
        rows = [r for c, r in group]
        r0, r1 = min(rows), max(rows)
        foot = [c for c, r in group if r >= r1 - 1]
        tip = [c for c, r in group if r <= r0 + 1]
        widths = Counter(r for c, r in group)
        width = max(widths.values())
        fx, fy = X(sum(foot) / len(foot)), Y(r1) + 1.0
        tx, ty = X(sum(tip) / len(tip)), Y(r0) + 0.3
        run = max(1.0, ty - fy)
        hgt = max(2.5, min(9.0, 0.5 * run + 1.5))
        radius = max(0.9, min(3.4, width / 2.0 + 0.2))
        base = Vector((fx, fy, Z_TRENCH - 0.3))
        point = Vector((tx, ty, Z_TRENCH + hgt))
        axis = point - base
        length = axis.length
        cone = w.lathe_axis(f"spike{count}", [(0.0, radius * 1.15), (0.25, radius * 1.15), (0.6, radius),
                                              (length * 0.55, radius * 0.5), (length * 0.9, radius * 0.14),
                                              (length, 0.05)], steel, tuple(base), tuple(axis.normalized()), 12)
        w.paint_faces(cone, lambda cc, nrm, b=base, ax=axis.normalized(), L=length:
                      steel_tip if (cc - b).dot(ax) > 0.72 * L else None)
        count += 1
    return count


def core():
    """The red core glowing in a dark ring, painted by the sprite's reds (brighter, more light), and the pipe
    running from it up the screen."""
    cx, cy = 0.5, 49.5
    base = dome_z(cx, cy)
    # The core: hot yellow in its middle through orange to a dark red rim, as the sprite draws it.
    bands = [(0x7f, 3.0), (0x7e, 2.8), (0x7d, 2.6), (0x7c, 2.4), (0x7b, 2.2), (0x7a, 2.0), (0x79, 1.8), (0x78, 1.6),
             (0x77, 1.4), (0x76, 1.2), (0x75, 1.0), (0x74, 0.8), (0x73, 0.6)]
    mats = [pal(f"citadel_core_{i:02x}", i, metallic=0.0, roughness=0.2, glow=gl) for i, gl in bands]
    ball = w.sphere("core", (cx, cy, base - 1.0), (12.2, 13.6, 7.5), mats[6], 40, 20)

    def pick(c, nrm):
        t = math.hypot((c.x - cx) / 12.2, (c.y - cy - 0.5) / 13.6)
        return mats[min(len(mats) - 1, int(t ** 1.1 * len(mats)))]
    w.paint_faces(ball, pick)
    dark = pal("citadel_ring", 0x04, metallic=0.6, roughness=0.3)
    kit.torus("core_ring", (cx, cy, base - 0.2), 12.9, 1.3, dark, 40, 8, 1.0, 13.9 / 12.9)
    # The pipe: a thick grey cylinder from the core's far side to the sprites' top edge (and on beyond it).
    greys = {s_: pal(f"citadel_pipe_{s_:x}", 0x60 + s_, metallic=0.6, roughness=0.28) for s_ in (5, 7, 9, 0xb, 0xd)}
    pipe = w.lathe_axis("pipe", [(0.0, 7.6), (14.0, 7.6)], greys[9], (0.5, 58.0, base + 1.0), (0, 1, 0), 32,
                        squash=0.75)

    def pick(c, nrm):
        if nrm.z < -0.2:
            return greys[5]
        v = 5.0 + 8.0 * max(0.0, nrm.z) ** 1.3 + 2.0 * max(0.0, nrm.x)
        return greys[min(greys, key=lambda s_: abs(s_ - v))]
    w.paint_faces(pipe, pick)
    for i, yb in enumerate((62.5, 67.0)):
        band = kit.torus(f"pipe_band{i}", (0.0, 0.0, 0.0), 7.7, 0.55, greys[0xb], 24, 6)
        sh.apply_modifiers(band)
        band.data.transform(Matrix.Translation((0.5, yb, base + 1.0)) @ Matrix.Scale(0.75, 4, (0, 0, 1)) @
                            Matrix.Rotation(math.radians(90), 4, "X"))
    k.recalc_normals(pipe)


def pods():
    """The pods lying in the bays, two in each, their south ends rounded (mostly under the eggs)."""
    dark = pal("citadel_pod", 0x05, metallic=0.55, roughness=0.3)
    light = pal("citadel_pod_lit", 0x08, metallic=0.55, roughness=0.28)
    for cx in BAYS:
        for dx in (-6.0, 6.5):
            obj = w.lathe_axis(f"pod{cx:.0f}{dx:.0f}", [(0.0, 0.01), (0.6, 2.4), (1.6, 3.4), (3.0, 3.8), (26.0, 3.8),
                                                         (27.0, 3.5)], dark, (cx + dx, 34.0, Z_PIT + 1.4), (0, 1, 0),
                               20, squash=0.8)
            w.paint_faces(obj, lambda c, nrm: light if nrm.z > 0.75 else None)


def citadel_whole():
    cls, colour, target = classify()
    painter = Painter("citadel", shades={0: (1, 2, 3, 4, 5, 6, 7, 8, 9, 0xa, 0xb), 5: (2, 3, 4, 5, 6, 7),
                                         6: (0xa,), 3: (0, 4), 2: (2, 5)},
                      metallic=0.35, roughness=0.45, finish={5: (0.15, 0.6), 0: (0.4, 0.45)})
    relief("citadel_relief", cls, colour, target, painter, pal("citadel_under", 0x02, metallic=0.2, roughness=0.6))
    spikes(cls)
    core()
    pods()


kit.PROTECT.append("citadel_relief")  # painted pixel by pixel: the budget decimates the other parts first
ROWS = [(0, [1, 3, 5, 7, 9, 11, 13, 15, 17], 0), (28, [39, 41, 43, 45, 47, 49, 51, 53, 55], 0),
        (56, [77, 79, 81, 83, 85, 87, 89, 91, 93], 0), (84, [115, 117, 119, 121, 123, 125, 127, 129, 131], 0),
        (112, [155, 157, 159, 161, 163, 165, 167], 24)]
PIECES = [kit.piece(f"coral_citadel_{s}", DOME, c0 + 24 * i, r0) for r0, sprites, c0 in ROWS
          for i, s in enumerate(sprites)]
kit.pieced("coral_citadel", citadel_whole, (216, 140), PIECES)


if __name__ == "__main__":
    kit.run()
