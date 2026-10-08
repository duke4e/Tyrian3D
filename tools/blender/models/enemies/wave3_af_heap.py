"""Batch AF of wave 3 (sheet R): IXMUCANE's boss, a machine set in a heap of boulders and the heap of boulders that
covers it, modelled as their sprites look (models.cfg: yaw=0). The kit is wave3_af_kit.py, the pixels
wave3_af_art.py (ROCKS_L, ROCKS_R, EYE, LIGHTS).

IXMUCANE (event time 4300) lays the boss out in two heaps of 2x2 sprites, 24 x 28 pixels each:
- the machine heap (events 6, ground: 642-657 at x 124 + 24 i, y -84 + 28 j, linked 142): R 159 161 163 165 /
  197 199 201 203 / 235 237 239 241 / 273 275 277 279, 96 x 112: a grey machine on its left, its big red eye
  in a silver ring and three lamps under it down a spine, finned vents above it, pipes off to its left, and
  tan and brown boulders heaped over its right side and top;
- the eye (658, R 167: frames 167, 205, 243, 281 cool it from yellow-white to red) at (134, -53) and the lamps
  (659, R 169: 207, 245, 283) at (134, -25), drawn over the machine's own;
- the cover (events 10, ground 2, drawn after the ground enemies: 630-641 at x 100 + 24 i, y -84 + 28 j,
  linked 141): R 153 155 157 / 191 193 195 / 229 231 233 / 267 269 271, 72 x 112, a heap of brown-grey
  boulders 24 pixels left of the machine heap, hiding the machine until the two heaps slide apart (the events
  then rock them up and down, each its own way).

Models (all drawn at their own origin, base on the ground layer):
- ixm_cover_<sprite> (the 12 pieces of the cover): a mound of boulders up to about 20 pixels high, each
  boulder an angular hull over the patch of the sprite it fills (the patches found between the sprite's dark
  crevices), its facets in the sprite's shades, on a dark mound that fills the crevices.
- ixm_boss_<sprite> (the 16 pieces of the machine heap): the machine as a dark grey housing whose lit parts
  (the fins, ribs and rails the sprite draws light) stand out, a spine down its middle carrying a silver ring
  round a dull red eye and three dull lamps in silver sockets, and the boulders heaped over its right; the
  machine's left edge is cut where the sprites end (the cover hides it).
- ixm_boss_eye (R 167): the eye lit: a bright orb, yellow-white in its middle and red at its edge, in its silver
  ring, set over the machine's eye (3 pixels higher in its sprite than the sprite draws it: the event places the
  sprite so that its orb lies 3 pixels below the machine's own eye; the model sits in the ring). It glows; its
  colours are those of its frames halfway from yellow-white to red.
- ixm_boss_lamps (R 169): the three lamps lit, in their silver sockets over the machine's. They glow.

usage: Blender -b --factory-startup -P wave3_af_heap.py -- [--only names] [--preview <prefix>] [--check 1]
       [--whole <prefix>] [--stats 1]
"""
import math
import os
import random
import sys
from collections import deque

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_af_kit as a  # noqa: E402
import wave3_q_kit as q  # noqa: E402
from wave3_af_kit import k, sh, w, pal, sphere  # noqa: E402

COVER = a.frame("ROCKS_L", 72, (36, 56))
BOSS = a.frame("ROCKS_R", 96, (48, 56))
EYE = a.frame("EYE", 24, (12, 14))
LIGHTS = a.frame("LIGHTS", 24, (12, 14))
EYE_AT = (10, 31)      # the eye's and the lamps' sprites' top left pixels in BOSS (the events' offsets)
LAMPS_AT = (10, 59)


def is_machine(f, c, r):
    """The machine's pixels in the machine heap: its greys and reds left of the boulders."""
    if f is not BOSS:
        return False
    v = f.get(c, r)
    if v is None or v >> 4 not in (0, 7):
        return False
    return (12 <= r <= 34 and c <= 27) or (35 <= r <= 86 and c <= 36)


# --- Boulders ----------------------------------------------------------------------------------------

def segment(f, rock, threshold=4, min_size=5):
    """The boulders the sprite draws: patches of rock pixels lighter than `threshold` (the dark crevices between
    boulders part them), grown back over the crevices. rock(c, r) -> the pixel is rock. Returns [cells]."""
    h, wd = f.height, f.width
    lab = [[-1] * wd for _ in range(h)]
    cores = []

    def core(c, r):
        return rock(c, r) and (f.g[r][c] & 15) > threshold
    for r in range(h):
        for c in range(wd):
            if lab[r][c] >= 0 or not core(c, r):
                continue
            stack, cells = [(r, c)], []
            lab[r][c] = len(cores)
            while stack:
                rr, cc = stack.pop()
                cells.append((rr, cc))
                for r2, c2 in ((rr + 1, cc), (rr - 1, cc), (rr, cc + 1), (rr, cc - 1)):
                    if 0 <= r2 < h and 0 <= c2 < wd and lab[r2][c2] < 0 and core(c2, r2):
                        lab[r2][c2] = len(cores)
                        stack.append((r2, c2))
            cores.append(cells)
    for cells in cores:
        if len(cells) < min_size:
            for rr, cc in cells:
                lab[rr][cc] = -1
    queue = deque((r, c) for r in range(h) for c in range(wd) if lab[r][c] >= 0)
    while queue:
        r, c = queue.popleft()
        for r2, c2 in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= r2 < h and 0 <= c2 < wd and lab[r2][c2] < 0 and rock(c2, r2):
                lab[r2][c2] = lab[r][c]
                queue.append((r2, c2))
    regions = {}
    for r in range(h):
        for c in range(wd):
            if lab[r][c] >= 0:
                regions.setdefault(lab[r][c], []).append((r, c))
    return [cells for _, cells in sorted(regions.items())]


def rock_outline(f, rock):
    rows = ["".join("#" if rock(c, r) else "." for c in range(f.width)) for r in range(f.height)]
    return sh.outlines(rows, "#", (f.ox, f.oy), smooth=2, epsilon=0.4, min_area=6.0)


def distance_to(polys):
    """(x, y) -> the distance to the polygons' outlines (0 outside them)."""
    import numpy as np
    seg_a, seg_b = sh._segments(polys)

    def d(x, y):
        pt = np.array([(x, y)], dtype=float)
        if not sh._inside(pt, seg_a, seg_b)[0]:
            return 0.0
        return float(sh._distance(pt, seg_a, seg_b)[0])
    return d


class Heap:
    """A heap of boulders over a frame's rock pixels: a dark mound `mound` high (reached `edge` pixels in from
    the outline) and on it the boulders the sprite draws."""

    def __init__(self, prefix, f, rock, mound=7.0, edge=14.0, height_scale=1.0, seed=3, threshold=4):
        self.prefix, self.f, self.rock = prefix, f, rock
        self.mound_height, self.edge = mound, edge
        self.height_scale, self.seed, self.threshold = height_scale, seed, threshold
        self.polys = rock_outline(f, rock)
        self.dist = distance_to(self.polys)
        self.mats = {}
        self.shade_shift = 1.2

    def mound_z(self, x, y):
        e = min(1.0, self.dist(x, y) / self.edge)
        return 0.3 + self.mound_height * math.sqrt(e * (2.0 - e))

    def mat(self, ramp, shade_):
        shade_ = max(1, min(12, int(round(shade_))))
        key = (ramp, shade_)
        if key not in self.mats:
            self.mats[key] = pal(f"{self.prefix}_{ramp:x}{shade_:x}", ramp * 16 + shade_, metallic=0.05,
                                 roughness=0.8)
        return self.mats[key]

    def build_mound(self):
        dark = pal(f"{self.prefix}_crevice", 0xa1, metallic=0.05, roughness=0.9)
        obj = q.heightfield(f"{self.prefix}_mound", self.polys, lambda x, y, e: 0.3 + self.mound_height *
                            math.sqrt(max(0.0, e * (2.0 - e))), dark, spacing=1.6, smooth_angle=60, edge=self.edge)
        w.simplify_bottom(obj)
        return obj

    def build_boulders(self):
        f = self.f
        rng = random.Random(self.seed)
        outline = max(self.polys, key=len)
        out = []
        for i, cells in enumerate(segment(f, self.rock, self.threshold)):
            pts = [(f.X(c), f.Y(r)) for r, c in cells]
            cx = sum(p[0] for p in pts) / len(pts)
            cy = sum(p[1] for p in pts) / len(pts)
            ramps = {}
            for r, c in cells:
                v = f.g[r][c]
                if (v & 15) > 2:
                    ramps[v >> 4] = ramps.get(v >> 4, 0) + 1
            ramp = max(ramps, key=ramps.get) if ramps else 0xa
            # The patch's outline (its pixels' edges), a little out so that neighbours touch.
            rows = ["".join("#" if (r, c) in set(cells) else "." for c in range(f.width)) for r in range(f.height)]
            polys = sh.outlines(rows, "#", (f.ox, f.oy), smooth=1, epsilon=0.7, min_area=0.5)
            if not polys:
                continue
            foot = sh.inset(max(polys, key=len), -0.35)
            reach = lambda ang: w._ray_polygon(foot, (cx, cy), (math.cos(ang), math.sin(ang)))  # noqa: E731
            base = self.mound_z(cx, cy) - 1.2
            size = math.sqrt(len(cells))
            h = self.height_scale * (1.4 + 0.42 * size)
            points = [(x, y, self.mound_z(x, y) - 0.8) for x, y in foot]
            # Its shoulders, then its broad top tilted a little towards the light (up and to the left).
            turn = rng.uniform(0, 2 * math.pi)
            count = 6 + int(size > 12) + int(size > 18)
            tilt_x, tilt_y = -0.08 * h / max(size, 1.0), 0.06 * h / max(size, 1.0)
            for ring_t, ring_z, spread in ((0.8, 0.5, 0.08), (0.5, 0.9, 0.06)):
                for j in range(count):
                    ang = turn + 2 * math.pi * (j + 0.5 * (ring_t < 0.6)) / count + rng.uniform(-0.25, 0.25)
                    rr = reach(ang) * (ring_t + rng.uniform(-0.08, 0.08))
                    x, y = cx + rr * math.cos(ang), cy + rr * math.sin(ang)
                    z = base + h * (ring_z + rng.uniform(-spread, spread))
                    if ring_t < 0.6:
                        z += tilt_x * (x - cx) * -1.0 + tilt_y * (y - cy)
                    points.append((x, y, z))
            points.append((cx + rng.uniform(-0.1, 0.1) * size, cy + rng.uniform(-0.1, 0.1) * size, base + h))
            rock = a.convex_rock(f"{self.prefix}_boulder{i}", points)
            clamp(rock, outline, (cx, cy))
            shade = f.shade((ramp,), blur=1)
            a.paint_facets(rock, lambda x, y, shade=shade: shade(x, y) + self.shade_shift,
                           lambda s_, ramp=ramp: self.mat(ramp, s_), wall_drop=1.0,
                           under=self.mat(ramp, 1))
            k.smooth(rock, 20)
            out.append(rock)
        return out


def clamp(obj, poly, centre):
    """Pulls the vertices that stick out of the outline back onto it, along rays from centre."""
    cx, cy = centre
    for v in obj.data.vertices:
        dx, dy = v.co.x - cx, v.co.y - cy
        d = math.hypot(dx, dy)
        if d < 1e-6:
            continue
        limit = w._ray_polygon(poly, (cx, cy), (dx / d, dy / d))
        if limit > 0 and d > limit:
            v.co.x, v.co.y = cx + dx * limit / d, cy + dy * limit / d


# --- The cover ------------------------------------------------------------------------------------------

def cover_rock(c, r):
    return COVER.get(c, r) is not None


def cover():
    heap = Heap("cover", COVER, cover_rock, mound=8.5, edge=10.0, height_scale=1.0, seed=5)
    heap.build_mound()
    heap.build_boulders()


COVER_SPRITES = [153, 155, 157, 191, 193, 195, 229, 231, 233, 267, 269, 271]
a.pieced("ixm_cover", cover, (72, 112),
         a.grid_pieces([f"ixm_cover_{s_}" for s_ in COVER_SPRITES], COVER, 3, 4))


# --- The machine heap -------------------------------------------------------------------------------------

EYE_C = (-26.5, 8.5)      # the machine's eye (BOSS pixels 11-31, rows 39-55) and its radii
EYE_R = (10.6, 8.6)
LAMPS = [((-26.0, -7.5), (6.2, 3.6)), ((-26.0, -17.5), (4.2, 2.7)), ((-26.0, -24.0), (3.2, 2.4))]
DECK = 3.0                # the machine housing's top
SPINE = 4.4               # the spine's top, under the eye and the lamps


def boss_rock(c, r):
    return BOSS.get(c, r) is not None and not is_machine(BOSS, c, r)


def machine_level(c, r):
    """The machine's height at a pixel: its deck, the spine down its middle higher, its light parts (fins, ribs,
    the silver rings) standing out."""
    v = BOSS.get(c, r)
    z = SPINE if (9 <= c <= 33 and 36 <= r <= 86) else DECK
    if v >> 4 == 0:
        s_ = v & 15
        if s_ >= 9:
            z += 1.1
        elif s_ >= 6:
            z += 0.6
    return round(z, 2)


def stepped(prefix, f, keep, level, mat, bevel=0.15, floor=1.0):
    """A blocky relief over the pixels keep(c, r) accepts, each pixel's column level(c, r) high: a slab from
    `floor` up for each height over the pixels of that height (their walls meet their neighbours')."""
    levels = sorted({level(c, r) for r in range(f.height) for c in range(f.width) if keep(c, r)})
    out = []
    for i, lv in enumerate(levels):
        rows = ["".join("#" if keep(c, r) and level(c, r) == lv else "." for c in range(f.width))
                for r in range(f.height)]
        polys = sh.outlines(rows, "#", (f.ox, f.oy), smooth=0, epsilon=0.05, min_area=0.9)
        for j, poly in enumerate(polys):
            obj = a.slab(f"{prefix}{i}_{j}", poly, 0.0 if i == 0 else floor, lv, mat, bevel=bevel, segments=1)
            w.simplify_bottom(obj)
            out.append(obj)
    return out


def machine():
    painter = a.Painter("mach", shades={0: (1, 3, 5, 7, 9, 11), 7: (2, 4, 6)},
                        metallic=0.6, roughness=0.35, finish={7: (0.1, 0.3)})
    dark = pal("mach_dark", 0x02, metallic=0.5, roughness=0.45)

    def keep(c, r):
        return is_machine(BOSS, c, r) or (BOSS.get(c, r) is not None and BOSS.get(c, r) >> 4 == 7)
    for obj in stepped("mach_", BOSS, keep, machine_level, dark, bevel=0.0):
        a.pixelate(obj, BOSS)
        a.paint_sprite(obj, BOSS, painter, wall_steps=-2, under=dark,
                       keep=lambda v: v >> 4 in (0, 7), probe=-0.3)
        a.paint_faces(obj, lambda c, nrm: painter(0x03) if abs(nrm.z) < 0.45 and (BOSS.at(c.x, c.y) or 0) >> 4 == 7
                      else None)
        a.merge_flat(obj)
    silver = pal("mach_silver", 0x0a, metallic=0.85, roughness=0.2)
    silver_light = pal("mach_silver_light", 0x0d, metallic=0.85, roughness=0.15)
    # The eye's silver ring and the dull red eye in it (the eye enemy's model lies over it).
    ex, ey = EYE_C
    rx, ry = EYE_R
    ring = a.hoop("eye_ring", (ex, ey, SPINE), [(rx - 1.6, 0.0), (rx + 0.4, 0.0), (rx + 0.4, 0.9), (rx - 0.2, 1.6),
                                                 (rx - 1.6, 1.2)], silver, segments=48, scale_y=ry / rx)
    a.paint_faces(ring, lambda c, nrm: silver_light if nrm.z > 0.5 and (nrm.x < 0.1 or nrm.y > 0.1) else None)
    dull = pal("mach_eye", 0x74, metallic=0.1, roughness=0.3, glow=0.5)
    sphere("eye_dull", (ex, ey, SPINE + 0.2), (rx - 1.4, ry - 1.4, 2.4), dull, 24, 8)
    for i, ((lx, ly), (lrx, lry)) in enumerate(LAMPS):
        sock = a.hoop(f"lamp_ring{i}", (lx, ly, SPINE), [(lrx - 0.9, 0.0), (lrx + 0.4, 0.0), (lrx + 0.4, 0.6),
                                                          (lrx - 0.1, 1.0), (lrx - 0.9, 0.7)], silver, segments=24,
                      scale_y=lry / lrx)
        a.paint_faces(sock, lambda c, nrm: silver_light if nrm.z > 0.5 and nrm.y > 0.1 else None)
        sphere(f"lamp_dull{i}", (lx, ly, SPINE + 0.1), (lrx - 0.7, lry - 0.6, 1.3), dull, 16, 6)


def boss():
    heap = Heap("boss", BOSS, boss_rock, mound=7.0, edge=14.0, height_scale=1.0, seed=9)
    heap.build_mound()
    heap.build_boulders()
    machine()


BOSS_SPRITES = [159, 161, 163, 165, 197, 199, 201, 203, 235, 237, 239, 241, 273, 275, 277, 279]
a.pieced("ixm_boss", boss, (96, 112),
         a.grid_pieces([f"ixm_boss_{s_}" for s_ in BOSS_SPRITES], BOSS, 4, 4))


# --- The eye and the lamps, lit --------------------------------------------------------------------------

# Their sprites in BOSS coordinates: the eye's orb is drawn 3 pixels lower (and half a pixel left) than the
# machine's eye; its pixels are laid 3 pixels higher, on the machine's eye.
EYE_ON = a.Frame(a.art.EYE, 24, (BOSS.ox - EYE_AT[0] - 0.5, BOSS.oy - EYE_AT[1] + 3.0))
LAMPS_ON = a.Frame(a.art.LIGHTS, 24, (BOSS.ox - LAMPS_AT[0], BOSS.oy - LAMPS_AT[1]))


def hot(prefix):
    """Glowing materials for the reds and yellows (ramp 7), brighter by shade."""
    cache = {}

    def mat(index):
        # Two shades down from the first (brightest) frame: the eye halfway through its cooling.
        s_ = max(2, min(13, (index & 15) - 2))
        s_ = min((3, 5, 7, 9, 11, 13), key=lambda q: abs(q - s_))
        if s_ not in cache:
            cache[s_] = pal(f"{prefix}_{s_:x}", 0x70 + s_, metallic=0.0, roughness=0.25,
                            glow=0.5 + 0.12 * s_)
        return cache[s_]
    return mat


def lit_lens(name, f, centre, radii, height, z0, mat_of, segments=32):
    """A glowing lens: a flattened dome painted with the frame's reds and yellows (its other pixels and the
    edge in the darkest red)."""
    cx, cy = centre
    obj = sphere(name, (cx, cy, z0), (radii[0], radii[1], height), mat_of(0x73), segments, max(8, segments // 3))
    sh.flat_bottom([obj], z0)
    a.pixelate(obj, f)

    def pick(c, nrm):
        v = f.at(c.x, c.y)
        if v is None or v >> 4 != 7 or nrm.z < 0.3:
            return mat_of(0x73)
        return mat_of(v)
    a.paint_faces(obj, pick)
    return obj


def eye():
    ex, ey = EYE_C
    rx, ry = EYE_R
    lit_lens("eye_lit", EYE_ON, (ex, ey), (rx - 0.9, ry - 0.9), 3.4, SPINE + 0.3, hot("eye"), 40)


def lamps():
    mat_of = hot("lamp")
    for i, ((lx, ly), (lrx, lry)) in enumerate(LAMPS):
        lit_lens(f"lamp_lit{i}", LAMPS_ON, (lx, ly), (lrx - 0.4, lry - 0.3), 1.8, SPINE + 0.2, mat_of, 28)


def sprite_box(at):
    """A 2x2 sprite's box in BOSS coordinates (its top left pixel at `at`) and its centre."""
    x0, y1 = at[0] - BOSS.ox, BOSS.oy - at[1]
    e = 0.01
    return (x0 + e, x0 + 24 - e, y1 - 28 + e, y1 - e), (x0 + 12, y1 - 14)


_box, _centre = sprite_box(EYE_AT)
a.pieced("ixm_boss_eye_whole", eye, (24, 28), [("ixm_boss_eye", _box, _centre, lambda: EYE.mask())])
_box, _centre = sprite_box(LAMPS_AT)
a.pieced("ixm_boss_lamps_whole", lamps, (24, 28), [("ixm_boss_lamps", _box, _centre, lambda: LIGHTS.mask())])


if __name__ == "__main__":
    a.run()
