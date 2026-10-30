"""The sidekicks' energy shots (shots sheet sprites 252 253 254, 50 51, 27, 48, 233-237, 30, 262 and the Wild Ball's
263, all 1x1: 12 x 14 cells), modelled (2026-10-30, round 3 of the energy shots' models; until then each was drawn as
its sprite with volume and the automatic glow). This script also holds the kit polish_shot_nort.py and
polish_shot_zica.py build with: Path (a smoothed curve in the screen's plane), Tube (a half-body along a curve, built
on its bands' borders) and the bands' materials.

Who fires them (sidekicks by their number in the shop's lists; each fires from its own place beside the ship):
  252 253 254  the Charge Cannon (sidekick 3, shop 1:8): its charge levels (weapons 101-103: 252 at 12 pixels a game
               frame, 253 at 10, 254 at 8); a charge sidekick fires only with its own button (Tyrian 2000), the charge
               growing every 20 frames it holds fire
  50 51        the Companion Ship Warfly (sidekick 19, shop 1:2; weapon 726: one every 5 frames at 10 a frame, the two
               frames by turns: a player's shot shows weapani + 1 frames)
  27           the Mint-O-Ship (sidekick 16, the first shop; weapon 452: one every 4 frames at 10)
  48           the Companion Ship Gerund (sidekick 21, shop 1:5; weapon 728: one every 4 frames at 9)
  233-237      the Wobbley (sidekick 5, shop 3:11; weapon 366, also port 16's option weapons at power 4): two bolts 8
               apart by turns, one every 3 frames, slowly (6 a frame), wriggling through the five frames; and
               Tyrian3D's Wobble Cannon (port 49, assets/content/items.cfg: weapons 830-840, two to six circling)
  30           the Beno Wallop Beam (sidekick 27, shop 4:4; weapon 736: one every 20 frames at 10; the item data's
               unnamed sidekicks 33-37 fire it too, but Tyrian3D's content gives them weapons of their own)
  262          the MicroSol FrontBlaster II (sidekick 26, shop 4:3; weapon 718: two at once, 18 apart, at 12)
  263          the Wild Ball (rear port 14, shop 1:6) at power 10 and 11, both modes (weapons 342 343 353 354): two
               capsules fired backwards, falling back and then flying up the screen (mode 2: up, falling back), with
               its steel balls (126) and green orbs (214)
None of them picks its sprite by heading: every model is authored as its sprite is drawn (yaw 0).

As the sprites draw them (ramps: 9 blue 0x90-0x9f, 8 the pale blue-white 0x80-0x8f, 7 the fire 0x70-0x7f, 12 green
0xc0-0xcf, 13 0xd0-0xdf):
- 252 the Pulse-Cannon's bolt (58) in blue, two shades lighter, a column to the left (columns 3-6, rows 0-10); 253 a
  5-pixel drop (columns 2-6, rows 0-10) with a white head (0x8f, 0x8c); 254 a 10-pixel blob (columns 0-9) of light
  blue round a white hood (0x8f) with three drips hanging from it (columns 1, 4-5 and 8, rows 11-13).
- 50 a diamond (columns 0-10, rows 0-12) of rings round a white-yellow middle: orange, dark red, red, orange-yellow,
  a red rim; 51 the same darker, its outer orange ring black (the star pulsing). (The models' rings a shade or two
  hotter: dark rings read as holes in the pyramid from the game's camera.)
- 27 a green gem (columns 4-8, rows 4-12), pointed at both ends, a white highlight in its upper middle.
- 48 three blue drops: a 6-pixel one (columns 3-8, rows 0-9) with a white head, and 3-pixel ones either side lower
  (columns 0-2 and 9-11, rows 3-9), white at row 5.
- 233-237 a blue bolt 2-3 pixels thick, its head white-blue (0x8d), wriggling: a diagonal (233, 236 the other way),
  hooks (234, 237) and an S (235).
- 30 an arch of fire (columns 1-10, rows 0-9): a white-yellow crest (0x7f, 0x7e) near its outer edge, darker towards
  its inside, its legs cooling to dark red.
- 262 a capsule 8 pixels wide and 14 long (columns 1-8): a dark red rim, red, orange-yellow, a white middle two
  columns wide; 263 the same 9 wide (columns 1-9), its white middle three columns wide.

The models (the energy shots' method, polish_shot_pulse.py: half-bodies, round on top and flat underneath, since the
game's camera only ever sees shots from above; palette materials glowing in their own colours by their shade; an
idealized heat in bands whose borders are the mesh's own rings and section points, so that no face is cut; raised hot
cores; at most 10 materials):
- 252: the pulse's own bolt (polish_shot_pulse.sheath and core) in ramp 9, its core light blue.
- 253, 48: drops lofted along the screen's y (polish_shot_fireball.Loft), a white core standing out of each head
  (polish_shot_fireball.core); 254 a body with drips (polish_shot_fireball.build_drop) and a white hood (dome_core).
- 50/51: a low four-sided pyramid (flat facets, sharp ridges along its diagonals) on the sprite's rings: one mesh,
  two sets of materials.
- 27: a table-cut gem: flat facets from its outline up to a flat table, glassy green, a white highlight on the table.
- 233-237: Tubes (this kit) along each frame's curve, round-headed and tapering, a white-blue core in the head.
- 30: a Tube along the arch's middle line (the right half built, the left half its mirror image), the crest a band
  near its outer edge, the legs cooling.
- 262, 263: capsules of fire lofted along the screen's y (as the Widget Beam's, polish_shot_widget.py), a white
  spine standing out of the top.

The kit: Path(points, closed) smooths a polyline (Chaikin) and measures it; Tube(path, width, heat, bands) is a
half-body along it: its section a half-ellipse (depth times the half-width high), its heat(t, u) given along it (t: 0
its start, 1 its end) and across it (u: 1 its left edge as it runs, -1 its right), falling along it at every u. Its
mesh: section points across it where the bands' borders run along it (each twice, its rings taken just inside and just
outside the border, then welded), points between to keep the section round; rings along it where the heat at each
section point falls through a border; rings between them every gap along it (stopping at the next ring, so a short
stretch gets no more faces than it needs); a flat underside; ends closed (a fan) where it doesn't taper to a point;
every face wound outwards as it is made. floor(x, y) raises it onto a host's top (cores); fixed: rings at given t only,
for a heat that changes only across the tube (each face then takes the band of the heat at its middle). stream(tube,
...) builds a tube the other way round, for bands' borders that run mostly along it (long V's down a tail): its section
points follow the borders from ring to ring, so the borders lie on mesh lines however they wander (rings across the
body cut by such borders at a slant folded faces).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the origin at the
sprite's centre (pixel 6, 7 of the cell: column c is x = c + 0.5 - 6, row r is y = 6.5 - r, its top edge y = 7 - r);
built on z = 0 (the game centres shot models in height on the player's layer).

models.cfg: see the block's comment (glow= on every line in place of the automatic glow).

Run: Blender -b --factory-startup -P tools/blender/models/shots/polish_shot_sidekick.py -- [--only <name,...>]
     [--outdir <dir>] (default assets/models/shots) [--check <sheets dir>] (each model's top view against its
     sprite in <dir>/shots.png, from TYR3D_EXTRACT) [--preview <prefix>] (top, three-quarter and game-camera views)
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_shot_fireball as kit  # noqa: E402
from polish_shot_fireball import k, mk, triangulate, view  # noqa: E402
from polish_launched_flames import lit, grid, shades  # noqa: E402
from polish_flame_drop import Heat  # noqa: E402
import polish_shot_pulse as pulse  # noqa: E402
from polish_shot_starburst import glow_of, polar_mesh  # noqa: E402

OUTDIR = kit.OUTDIR
TOP = 7.0
FIRE_ROUGHNESS, CORE_ROUGHNESS = 0.5, 0.4


# === The kit ==========================================================================================================

def shade_of(index):
    """A palette index's brightness in shades: ramp 8's upper shades (the pale blue-white) count as hotter than ramp
    9's lightest (16 = 0x89 .. 22 = 0x8f), so one heat scale runs from dark blue to white."""
    if index >> 4 == 8:
        return 16 + max(0, (index & 15) - 9)
    return index & 15


def band_material(prefix, index, factor=1.0, roughness=None):
    """A palette material glowing in its own colour by its shade (glow_of, times factor); the hottest smoother."""
    shade = min(index & 15, 15)
    if roughness is None:
        roughness = CORE_ROUGHNESS if shade >= 13 else FIRE_ROUGHNESS
    return lit(f"{prefix}_{index:02x}", index, round(glow_of(shade) * factor, 3), roughness=roughness)


def chaikin(points, iterations=3, closed=False):
    """A polyline rounded by corner cutting (the ends kept when open)."""
    pts = [tuple(p) for p in points]
    for _ in range(iterations):
        n = len(pts)
        out = [] if closed else [pts[0]]
        for i in range(n if closed else n - 1):
            a, b = pts[i], pts[(i + 1) % n]
            out.append((0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]))
            out.append((0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1]))
        if not closed:
            out.append(pts[-1])
        pts = out
    return pts


class Path:
    """A curve in the screen's plane through points (x, y), smoothed (smooth: Chaikin rounds), measured along its
    length: point(t), tangent(t), normal(t) (its left as it runs) for t 0 (its start) .. 1 (its end)."""

    def __init__(self, points, closed=False, smooth=3):
        pts = chaikin(points, smooth, closed) if smooth else [tuple(p) for p in points]
        if closed:
            pts = pts + [pts[0]]
        self.closed = closed
        self.pts = [Vector((p[0], p[1])) for p in pts]
        self.cum = [0.0]
        for a, b in zip(self.pts, self.pts[1:]):
            self.cum.append(self.cum[-1] + (b - a).length)
        self.length = self.cum[-1]

    def point(self, t):
        if self.closed:
            t %= 1.0
        s = min(max(t, 0.0), 1.0) * self.length
        lo, hi = 0, len(self.cum) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if self.cum[mid] <= s:
                lo = mid
            else:
                hi = mid
        seg = self.cum[hi] - self.cum[lo]
        f = (s - self.cum[lo]) / seg if seg > 1e-12 else 0.0
        return self.pts[lo].lerp(self.pts[hi], f)

    def tangent(self, t):
        h = 0.35 / max(self.length, 1e-6)
        if self.closed:
            d = self.point(t + h) - self.point(t - h)
        else:
            d = self.point(min(t + h, 1.0)) - self.point(max(t - h, 0.0))
        return d.normalized() if d.length > 1e-9 else Vector((0.0, -1.0))

    def normal(self, t):
        d = self.tangent(t)
        return Vector((-d.y, d.x))


def band_index(bands, h):
    return max(i for i, b in enumerate(bands) if h >= b[0])


class Tube:
    """A half-body along a Path (see the module's docstring): width(t) its half-width, heat(t, u) its heat (falling
    along t at every u), bands [(lowest heat, palette index)] ascending; depth its height over its half-width; floor(x,
    y) what it stands on (default 0); shift(t) moves its middle line across (pixels, to its left); gap the longest
    stretch (pixels) between rings; angle_gap the widest step round the section (radians); border_ts where along it the
    borders running along it are measured; lift(t, u) raises its top (pixels, added to the section's height)."""

    def __init__(self, path, width, heat, bands, depth=0.85, floor=None, gap=0.8, angle_gap=math.radians(24.0),
                 border_ts=(0.0,), lift=None, merge=0.03, caps=(True, True), fixed=None):
        self.path, self.width, self.heat, self.bands, self.depth = path, width, heat, bands, depth
        self.fixed = fixed  # rings at these t only (the heat changing across the tube only: each face's band its own)
        self.caps = caps  # (close the start, close the end) where the tube doesn't taper to a point there
        self.floor = floor if floor is not None else (lambda x, y: 0.0)
        self.gap, self.angle_gap, self.border_ts, self.lift, self.merge = gap, angle_gap, border_ts, lift, merge

    # --- geometry -------------------------------------------------------------------------------------------------
    def position(self, t, u):
        p = self.path.point(t)
        n = self.path.normal(t)
        w = max(self.width(t), 0.0)
        x, y = p.x + u * w * n.x, p.y + u * w * n.y
        z = self.floor(x, y) + self.depth * w * math.sqrt(max(0.0, 1.0 - u * u))
        if self.lift is not None:
            z += self.lift(t, u)
        return Vector((x, y, z))

    def top(self, x, y, steps=64):
        """The tube's top over (x, y) (0 outside it), for cores standing on it: the nearest section's (by t)."""
        best = None
        for i in range(steps + 1):
            t = i / steps
            p = self.path.point(t)
            d = (Vector((x, y)) - p).length
            if best is None or d < best[0]:
                best = (d, t)
        _, t = best
        lo, hi = max(0.0, t - 1.0 / steps), min(1.0, t + 1.0 / steps)
        for _ in range(30):  # (refine: the t whose section passes through the point)
            m1, m2 = lo + (hi - lo) / 3, hi - (hi - lo) / 3
            if (Vector((x, y)) - self.path.point(m1)).length < (Vector((x, y)) - self.path.point(m2)).length:
                hi = m2
            else:
                lo = m1
        t = (lo + hi) / 2
        p, n, w = self.path.point(t), self.path.normal(t), self.width(t)
        if w < 1e-6:
            return 0.0
        u = (Vector((x, y)) - p).dot(n) / w
        if abs(u) >= 1.0:
            return 0.0
        return self.floor(x, y) + self.depth * w * math.sqrt(1.0 - u * u) + (self.lift(t, u) if self.lift else 0.0)

    # --- the bands' borders -------------------------------------------------------------------------------------
    def section_points(self):
        """[(u, side)] from the left edge (u 1) over the top to the right edge (u -1): the borders where they cross
        the sections at border_ts (each twice: its rings as just inside and just outside it), points between where
        the step round the section is wider than angle_gap."""
        found = set()
        for t in self.border_ts:
            for lowest, _ in self.bands[1:]:
                steps = 400
                for i in range(steps):
                    u0, u1 = 1.0 - 2.0 * i / steps, 1.0 - 2.0 * (i + 1) / steps
                    h0, h1 = self.heat(t, u0) - lowest, self.heat(t, u1) - lowest
                    if h0 * h1 < 0:
                        lo, hi = u0, u1
                        for _ in range(40):
                            mid = (lo + hi) / 2
                            if (self.heat(t, mid) - lowest) * h0 > 0:
                                lo = mid
                            else:
                                hi = mid
                        found.add(round((lo + hi) / 2, 6))
        us = sorted(found, reverse=True)
        merged = []
        for u in us:
            if abs(u) > 1.0 - self.merge:
                continue
            if merged and merged[-1] - u < self.merge:
                continue
            merged.append(u)
        points = [(1.0, 0.0)]
        for u in merged + [-1.0]:
            start = math.acos(points[-1][0])
            end = math.acos(u)
            extra = int((end - start) / self.angle_gap)
            points += [(math.cos(start + (end - start) * j / (extra + 1)), 0.0) for j in range(1, extra + 1)]
            if u == -1.0:
                points.append((-1.0, 0.0))
            else:
                points += [(u, 1e-4), (u, -1e-4)]
        return points

    def ring_ts(self, points):
        """The rings along t (each a t per section point) and the band of the faces after each: [start, the borders
        where the heat falls through them (hottest first), end], bands per interval."""
        values = sorted(((b[0], i) for i, b in enumerate(self.bands) if i > 0), reverse=True)
        rings = []
        for value, band in values:
            ring = []
            for u, side in points:
                us = min(max(u + side, -1.0), 1.0)
                h0, h1 = self.heat(0.0, us), self.heat(1.0, us)
                if h0 < value:
                    ring.append(0.0)
                    continue
                if h1 >= value:
                    ring.append(1.0)
                    continue
                lo, hi = 0.0, 1.0
                for _ in range(40):
                    mid = (lo + hi) / 2
                    if self.heat(mid, us) >= value:
                        lo = mid
                    else:
                        hi = mid
                ring.append((lo + hi) / 2)
            rings.append(ring)
        for r in range(1, len(rings)):
            rings[r] = [max(a, b) for a, b in zip(rings[r], rings[r - 1])]
        out, bands = [[0.0] * len(points)], [len(self.bands) - 1]
        for ring, (value, band) in zip(rings, values):
            out.append(ring)
            bands.append(band - 1)
        out.append([1.0] * len(points))
        # (rings between rings further apart than gap along the curve: every gap from the earlier ring, stopping at the
        # later one, so that a short stretch at one section point gets no more faces than it needs)
        step = self.gap / max(self.path.length, 1e-6)
        full, full_bands = [out[0]], []
        for i in range(len(out) - 1):
            a, b = out[i], out[i + 1]
            longest = max(y - x for x, y in zip(a, b))
            n = int(longest / step)
            if n > 0 and longest - n * step < 0.35 * step:
                n -= 1  # (no sliver before the later ring)
            for j in range(1, n + 1):
                full.append([min(x + j * step, y) for x, y in zip(a, b)])
                full_bands.append(bands[i])
            full.append(b)
            full_bands.append(bands[i])
        return full, full_bands

    def build(self, name, materials, under=True):
        """The mesh; materials: one per band (bands sharing a material share its slot); under: a flat underside at
        the floor. Every face is wound outwards as it is made (away from the curve on top, down underneath, along the
        curve at the ends' fans)."""
        points = self.section_points()
        if self.fixed is not None:
            rings, ring_bands = [[t] * len(points) for t in self.fixed], None
        else:
            rings, ring_bands = self.ring_ts(points)
        verts, index, faces, fbands = [], {}, [], []
        for r, ring in enumerate(rings):
            for c, ((u, _), t) in enumerate(zip(points, ring)):
                index[r, c] = len(verts)
                v = self.position(t, u)
                verts.append((round(v.x, 6), round(v.y, 6), round(v.z, 6)))
        n = len(points)

        def add(face, band, outward):
            pts = []
            for v in face:
                if not pts or verts[v] != verts[pts[-1]]:
                    pts.append(v)
            if len(pts) > 1 and verts[pts[0]] == verts[pts[-1]]:
                pts.pop()
            if len(pts) < 3 or len({verts[v] for v in pts}) < 3:
                return
            normal = newell([verts[v] for v in pts])
            if normal.dot(outward) < 0:
                pts.reverse()
            faces.append(tuple(pts))
            fbands.append(band)
        for r in range(len(rings) - 1):
            for c in range(n - 1):
                quad = [index[r, c], index[r, c + 1], index[r + 1, c + 1], index[r + 1, c]]
                centre = sum((Vector(verts[v]) for v in quad), Vector()) / 4
                t = (rings[r][c] + rings[r][c + 1] + rings[r + 1][c] + rings[r + 1][c + 1]) / 4
                p = self.path.point(t)
                outward = Vector((centre.x - p.x, centre.y - p.y, centre.z - self.floor(p.x, p.y) + 1e-3))
                if ring_bands is None:
                    u = (points[c][0] + points[c][1] + points[c + 1][0] + points[c + 1][1]) / 2
                    band = band_index(self.bands, self.heat(t, u))
                else:
                    band = ring_bands[r]
                add(quad, band, outward)
            if under:
                add([index[r, 0], index[r + 1, 0], index[r + 1, n - 1], index[r, n - 1]], 0, Vector((0, 0, -1)))
        # (the ends: closed by a fan to the middle of the end section where the tube doesn't taper to a point)
        for (r, t), cap, sign in zip(((0, 0.0), (len(rings) - 1, 1.0)), self.caps, (-1.0, 1.0)):
            if self.width(t) < 1e-4 or not cap:
                continue
            p = self.path.point(t)
            d = self.path.tangent(t) * sign
            centre = len(verts)
            verts.append((round(p.x, 6), round(p.y, 6), round(self.floor(p.x, p.y), 6)))
            for c in range(n - 1):
                u = (points[c][0] + points[c + 1][0]) / 2
                add([index[r, c], index[r, c + 1], centre], band_index(self.bands, self.heat(t, u)),
                    Vector((d.x, d.y, 0.0)))
        obj = k.mesh_object(name, verts, faces)
        slots = []
        for band in sorted(set(fbands)):
            if materials[band] not in slots:
                slots.append(materials[band])
        for m in slots:
            obj.data.materials.append(m)
        for poly, band in zip(obj.data.polygons, fbands):
            poly.material_index = slots.index(materials[band])
        weld(obj)
        return obj


def stream(tube, name, materials, ts, under=True, caps=(True, True)):
    """A Tube built the other way round, for a heat falling outwards from its middle line at every t (heat(t, u)
    falling in |u|) whose bands' borders run mostly along it: the section points follow the borders (at every ring the
    border's u, found where the heat crosses it), so the borders lie on mesh lines however they wander; rings at ts
    (t, ascending, 0 .. 1). Every face lies in one band: between two border lines, or a border line and the edge or
    the middle line (points between them keep the section round)."""
    thresholds = [b[0] for b in tube.bands[1:]]

    def border_u(t, v):
        if tube.heat(t, 0.0) < v:
            return 0.0
        if tube.heat(t, 1.0) >= v:
            return 1.0
        lo, hi = 0.0, 1.0
        for _ in range(40):
            mid = (lo + hi) / 2
            if tube.heat(t, mid) >= v:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2
    # the left half's lines at each ring: the edge, the borders (coolest first), the middle; their angles round the
    # section; the points between each pair (one count for all rings, from the widest gap)
    lines = [[1.0] + [border_u(t, v) for v in thresholds] + [0.0] for t in ts]
    count = len(lines[0])
    fills = []
    for i in range(count - 1):
        widest = max(math.acos(min(ring[i + 1], 1.0)) - math.acos(min(ring[i], 1.0)) for ring in lines)
        fills.append(int(widest / tube.angle_gap))
    # (u per point per ring, the left half from the edge to the middle, then the right half back out)
    left = []
    for ring in lines:
        us = []
        for i in range(count - 1):
            a0, a1 = math.acos(ring[i]), math.acos(ring[i + 1])
            us.append(ring[i])
            us += [math.cos(a0 + (a1 - a0) * j / (fills[i] + 1)) for j in range(1, fills[i] + 1)]
        us.append(0.0)
        left.append(us)
    bands_left = []
    for i in range(count - 1):
        bands_left += [i] * (fills[i] + 1)
    rows = [us + [-u for u in reversed(us[:-1])] for us in left]
    point_bands = bands_left + list(reversed(bands_left))  # (the band of the faces between point j and j + 1)
    verts, index, faces, fbands = [], {}, [], []
    for r, (t, us) in enumerate(zip(ts, rows)):
        for c, u in enumerate(us):
            index[r, c] = len(verts)
            v = tube.position(t, u)
            verts.append((round(v.x, 6), round(v.y, 6), round(v.z, 6)))
    n = len(rows[0])

    def add(face, band, outward):
        pts = []
        for v in face:
            if not pts or verts[v] != verts[pts[-1]]:
                pts.append(v)
        if len(pts) > 1 and verts[pts[0]] == verts[pts[-1]]:
            pts.pop()
        if len(pts) < 3 or len({verts[v] for v in pts}) < 3:
            return
        if newell([verts[v] for v in pts]).dot(outward) < 0:
            pts.reverse()
        faces.append(tuple(pts))
        fbands.append(band)
    for r in range(len(ts) - 1):
        for c in range(n - 1):
            quad = [index[r, c], index[r, c + 1], index[r + 1, c + 1], index[r + 1, c]]
            centre = sum((Vector(verts[v]) for v in quad), Vector()) / 4
            p = tube.path.point((ts[r] + ts[r + 1]) / 2)
            add(quad, point_bands[c], Vector((centre.x - p.x, centre.y - p.y,
                                              centre.z - tube.floor(p.x, p.y) + 1e-3)))
        if under:
            add([index[r, 0], index[r + 1, 0], index[r + 1, n - 1], index[r, n - 1]], 0, Vector((0, 0, -1)))
    for (r, t), cap, sign in zip(((0, ts[0]), (len(ts) - 1, ts[-1])), caps, (-1.0, 1.0)):
        if tube.width(t) < 1e-4 or not cap:
            continue
        p = tube.path.point(t)
        d = tube.path.tangent(t) * sign
        centre = len(verts)
        verts.append((round(p.x, 6), round(p.y, 6), round(tube.floor(p.x, p.y), 6)))
        for c in range(n - 1):
            add([index[r, c], index[r, c + 1], centre], point_bands[c], Vector((d.x, d.y, 0.0)))
    obj = k.mesh_object(name, verts, faces)
    slots = []
    for band in sorted(set(fbands)):
        if materials[band] not in slots:
            slots.append(materials[band])
    for m in slots:
        obj.data.materials.append(m)
    for poly, band in zip(obj.data.polygons, fbands):
        poly.material_index = slots.index(materials[band])
    weld(obj)
    return obj


def newell(points):
    """A polygon's normal (Newell's method: any winding, any count)."""
    nx = ny = nz = 0.0
    for i, a in enumerate(points):
        b = points[(i + 1) % len(points)]
        nx += (a[1] - b[1]) * (a[2] + b[2])
        ny += (a[2] - b[2]) * (a[0] + b[0])
        nz += (a[0] - b[0]) * (a[1] + b[1])
    return Vector((nx, ny, nz))


def weld(obj, dist=1e-5):
    """Merges the points that lie on one another (a border's two section points, rings meeting at a point) and
    dissolves the faces left without area."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=dist)
    bmesh.ops.dissolve_degenerate(bm, dist=dist, edges=bm.edges[:])
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def mirrored(obj, name, axis_x=0.0):
    """A copy of obj mirrored about the line x = axis_x (its faces turned back outwards)."""
    copy = obj.copy()
    copy.data = obj.data.copy()
    copy.name = name
    bpy.context.scene.collection.objects.link(copy)
    m = Matrix.Translation((axis_x, 0, 0)) @ Matrix.Scale(-1, 4, (1, 0, 0)) @ Matrix.Translation((-axis_x, 0, 0))
    copy.data.transform(m)
    copy.data.flip_normals()
    return copy


def join(objects, name):
    """One object of several (their material slots merged)."""
    for o in objects:
        o.select_set(False)
    with bpy.context.temp_override(selected_editable_objects=objects, active_object=objects[0], object=objects[0]):
        bpy.ops.object.join()
    objects[0].name = name
    return objects[0]


def facing(parts):
    """(faces facing up, facing down, others) over all the parts."""
    up = down = side = 0
    for p in parts:
        for poly in p.data.polygons:
            z = poly.normal.z
            if z > 0.2:
                up += 1
            elif z < -0.2:
                down += 1
            else:
                side += 1
    return up, down, side


def top_of(parts):
    """The middle of the model's height bounds, twice (the game centres a model on it)."""
    zs = [(p.matrix_world @ v.co).z for p in parts for v in p.data.vertices]
    return max(zs) + min(zs)


def px(col, row):
    """A pixel's centre (column, row of the cell; fractions allowed) in model coordinates."""
    return (col + 0.5 - 6.0, 6.5 - row)


# === The Charge Cannon's charges (252 253 254) and the Gerund's drops (48) ============================================

# 252: the pulse's bolt (58) in ramp 9, two shades lighter (the sprite is 58's pixels moved a column left, every ramp-7
# shade s drawn as ramp-9 shade s + 2); its fire's bands as the pulse's, its core light blue.
SPRITE_252 = """
.. .. .. .. 97 98 .. .. .. .. .. ..
.. .. .. 97 9e 9d 98 .. .. .. .. ..
.. .. .. 98 9d 9c 99 .. .. .. .. ..
.. .. .. 9a 9c 9b 9a .. .. .. .. ..
.. .. .. 9a 99 9a 99 .. .. .. .. ..
.. .. .. 97 98 99 97 .. .. .. .. ..
.. .. .. 96 99 99 96 .. .. .. .. ..
.. .. .. 95 97 97 95 .. .. .. .. ..
.. .. .. 94 95 94 94 .. .. .. .. ..
.. .. .. .. 94 93 .. .. .. .. .. ..
.. .. .. .. 93 .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
"""
BOLT_252 = pulse.Bolt(-1.0, TOP, TOP - 11, 2.0, "wedge")
BOLT_FIRE_252 = [0x95, 0x96, 0x97, 0x98, 0x99, 0x9a, 0x9b, 0x9c]  # (the pulse's eight fire bands, in ramp 9)
BOLT_CORE_252 = [0x8b, 0x9f]  # (its wedge: pale blue at its front, light blue behind)


def build_252(name):
    heat = Heat(shades(grid(SPRITE_252), 9), TOP, sigma=(0.55, 0.7))
    fire = [band_material("charge_fire", i) for i in BOLT_FIRE_252]
    core = [band_material("charge_core", i) for i in BOLT_CORE_252]
    return [pulse.sheath(name + "_bolt", BOLT_252, heat, fire), pulse.core(name + "_core", BOLT_252, heat, core)]


# The drops (253, 48): (x, nose y, tail y, half-width along it (t: 0 the nose, 1 the tail), the heat along its middle
# line and how much less at its edges (shades of the one blue-white scale: shade_of), the core: (how far behind the
# nose it begins and how long it is (fractions of the drop's length), its half-width, its lift)).
BLUE_BANDS = [(-99.0, 0x92), (3.0, 0x94), (5.2, 0x96), (7.2, 0x98), (9.2, 0x9a), (11.2, 0x9c), (13.2, 0x9e)]
DROP_CORE_BANDS = ((0.0, 0x8f, 0.62), (0.45, 0x8c, 0.58))
DROPS = {
    "253": dict(x=-1.5, nose=7.0, tail=-4.0,
                width=((0.0, 0.0), (0.02, 1.2), (0.07, 2.05), (0.14, 2.45), (0.3, 2.5), (0.52, 2.35), (0.62, 1.75),
                       (0.78, 1.25), (0.9, 0.75), (1.0, 0.0)),
                along=((0.0, 11.0), (0.12, 14.6), (0.25, 15.2), (0.38, 13.4), (0.5, 11.5), (0.62, 9.6), (0.75, 7.6),
                       (0.88, 5.2), (1.0, 2.6)),
                across=((0.0, 2.0), (0.25, 4.0), (0.5, 5.0), (0.75, 4.0), (1.0, 3.0)),
                core=(0.06, 0.34, 1.05, 0.42)),
    "48_middle": dict(x=0.0, nose=7.0, tail=-3.0,
                      width=((0.0, 0.0), (0.02, 1.5), (0.08, 2.6), (0.18, 3.0), (0.36, 2.85), (0.48, 2.15),
                             (0.62, 1.9), (0.8, 1.45), (0.93, 0.8), (1.0, 0.0)),
                      along=((0.0, 9.0), (0.1, 13.8), (0.25, 15.6), (0.38, 13.0), (0.5, 11.0), (0.65, 9.0),
                             (0.8, 6.8), (1.0, 3.2)),
                      across=((0.0, 3.0), (0.25, 5.0), (0.5, 5.0), (0.75, 3.6), (1.0, 2.4)),
                      core=(0.12, 0.32, 1.25, 0.42)),
    "48_left": dict(x=-4.5, nose=4.0, tail=-3.0,
                    width=((0.0, 0.0), (0.03, 0.9), (0.12, 1.4), (0.3, 1.55), (0.5, 1.45), (0.7, 1.15), (0.88, 0.7),
                           (1.0, 0.0)),
                    along=((0.0, 8.0), (0.15, 12.0), (0.3, 15.0), (0.45, 12.5), (0.6, 10.0), (0.8, 6.5), (1.0, 3.2)),
                    across=((0.0, 2.0), (0.3, 4.5), (0.6, 4.5), (1.0, 3.0)),
                    core=(0.18, 0.32, 0.7, 0.32), segments=6),
}
DROPS["48_right"] = dict(DROPS["48_left"], x=4.5)


def blue_drop(name, spec):
    """A blue drop (Loft) with a white core standing out of its head (core)."""
    length = spec["nose"] - spec["tail"]
    fire = [band_material("drop_blue", i) for _, i in BLUE_BANDS]
    bands = [(lo, i, 0.0) for lo, i in BLUE_BANDS]
    body = kit.Loft(spec["x"], spec["nose"], spec["tail"], kit.curve(spec["width"]),
                    kit.loft_heat(spec["along"], spec["across"]), bands, depth=0.88, segments=spec.get("segments", 8),
                    tongues=(2.5, 0.02, 1.9), gap=0.2, width_gap=0.6, head_fractions=(0.15, 0.45),
                    tail_fractions=(0.5,))
    parts = [body.build(name + "_fire", fire)]
    behind, core_length, w, lift = spec["core"]
    cmats = [band_material("drop_core", i) for _, i, _ in DROP_CORE_BANDS]
    parts.append(kit.core(name + "_core", spec["x"], spec["nose"] - behind * length, core_length * length, w, lift,
                          body.top, DROP_CORE_BANDS, cmats, cap=0.4, taper=0.85))
    return parts


# 254: a blob of light blue (columns 0-9, its middle x -1) round a white hood (0x8f over 0x8d), three drips hanging
# from it (columns 1, 4-5 and 8).
DROP_254 = dict(
    x=-1.0, nose=7.0, tail=-7.0, depth=0.84, segments=12,
    width=((0.0, 0.0), (0.012, 1.2), (0.035, 2.1), (0.08, 2.9), (0.13, 3.4), (0.2, 4.0), (0.27, 4.55), (0.33, 4.95),
           (0.53, 4.95), (0.58, 4.4), (0.63, 4.05), (0.73, 3.75), (0.79, 2.5), (0.83, 1.7), (0.88, 1.15), (0.95, 0.8),
           (1.0, 0.0)),
    # the heat: a field round the hood's middle (white there, falling to the blob's rim), down the middle drip by y
    heat=kit.blob_heat((-1.0, 2.8), 4.9, 4.2, 6.4,
                       ((0.0, 19.6), (0.28, 18.4), (0.42, 16.4), (0.56, 14.4), (0.72, 12.4), (0.88, 10.2), (1.0, 8.6),
                        (1.2, 5.0), (2.0, 2.0)),
                       ((-7.0, 1.2), (-6.0, 2.5), (-5.0, 4.0), (-4.0, 6.5), (-3.0, 99.0))),
    tongues=[(-4.4, -1.6, -6.9, 0.62), (2.4, -1.6, -6.9, 0.62)],
    tongue_along=((0.0, 10.0), (0.35, 8.0), (0.7, 5.0), (1.0, 2.5)),
    tongue_across=((0.0, 1.5), (1.0, 2.0)),
    core=(-1.0, 3.25, 2.05, 1.45, 0.38),
    waves=(2.5, 0.02, 1.9),
)
BANDS_254 = [(-99.0, 0x93, 0.24), (4.0, 0x96, 0.33), (7.0, 0x99, 0.45), (10.0, 0x9c, 0.56), (12.8, 0x9e, 0.6),
             (15.6, 0x8b, 0.56), (18.0, 0x8d, 0.58)]
CORE_254 = ((0.0, 0x8f, 0.62), (0.6, 0x8e, 0.6))


def build_254(name):
    bands = [(lo, i, round(glow_of(min(i & 15, 15)), 3)) for lo, i, _ in BANDS_254]
    return kit.build_drop(name, DROP_254, "charge_blob", bands, CORE_254)


# === The capsules (262, 263) ==========================================================================================

# The fire's bands, the dark red rim, red, amber round the white middle, as the sprite's columns go (0x71 0x75 0x7b
# 0x7f, a pixel each; 0x7a and 0x76 in the rows by the ends), with a thin step between each two; the spine: white in its
# middle, pale yellow at its ends. Heat on the capsule's middle line by the distance from its nearer end (pixels), less
# towards its edges (s, the top view's fraction of the half-width) by the distance from the nearer end: amber to s 0.5,
# red to 0.75, dark red beyond, the bands converging towards the ends.
CAPSULE_BANDS = [(-99.0, 0x71, 0.2), (7.1, 0x73, 0.25), (7.94, 0x75, 0.31), (10.2, 0x7a, 0.5), (10.75, 0x7b, 0.53)]
CAPSULE_SPINE = ((0.0, 0x7e, 0.6), (0.5, 0x7f, 0.62))
CAPSULE_ALONG = ((0.0, 4.0), (0.7, 7.6), (1.5, 10.5), (2.3, 12.4), (3.0, 13.0), (99.0, 13.0))
CAPSULE_ACROSS = ((0.0, 2.0), (0.7, 4.0), (1.5, 6.5), (2.5, 9.0), (99.0, 9.0))
# name: (sprite, its middle x, half-width, the spine's half-width at its foot (most of it inside the body: what stands
# out of the body's top is the sprite's white, 2 and 3 pixels), what it is)
CAPSULES = {
    "shot_sidekick_capsule": (262, -1.0, 4.0, 2.0, "a capsule of fire 8 wide, its white middle 2 wide"),
    "shot_sidekick_capsule_2": (263, -0.5, 4.5, 2.85, "the same 9 wide, its white middle 3 wide"),
}
SPINE_INSET, SPINE_LIFT = 2.0, 0.38  # (the spine's ends from the capsule's, pixels; how far it stands out)


def capsule(name, x, half, spine_w, nose=7.0, tail=-7.0, cap=2.2, depth=0.78):
    length = nose - tail
    along, across = kit.curve(CAPSULE_ALONG), kit.curve(CAPSULE_ACROSS)

    def end_distance(t):
        return min(t, 1.0 - t) * length

    def width(t):
        d = end_distance(t)
        return half * (max(0.0, 1.0 - (1.0 - d / cap) ** 2) ** 0.5 if d < cap else 1.0)

    def heat(t, s):
        d = end_distance(t)
        return along(d) - across(d) * min(abs(s), 1.3) ** 2
    mats = kit.materials("capsule_fire", CAPSULE_BANDS)
    body = kit.Loft(x, nose, tail, width, heat, CAPSULE_BANDS, depth=depth, segments=8, tongues=(3.0, 0.015, 2.3),
                    gap=0.2, width_gap=0.6, head_fractions=(0.15, 0.5), tail_fractions=(0.5, 0.85))
    parts = [body.build(name + "_fire", mats)]
    spine = kit.materials("capsule_spine", CAPSULE_SPINE, CORE_ROUGHNESS)
    # (a pill of white standing out of the top, its ends round: the sprite's white middle columns)
    parts.append(kit.core(name + "_spine", x, nose - SPINE_INSET, length - 2 * SPINE_INSET, spine_w, SPINE_LIFT,
                          body.top, ((0.0, 0x7e, 0.6), (0.12, 0x7f, 0.62), (0.88, 0x7e, 0.6)), spine + [spine[0]],
                          cap=0.14, ends="capsule", segments=6, rings=(0.05, 0.12, 0.5, 0.88, 0.95)))
    return parts


# === The Warfly's diamond (50 51) =====================================================================================

# A diamond (columns 0-10, rows 0-12) round its middle (column 5, row 6: x -0.5, y 0.5), its sprite's colours lying in
# rings of m = |dx| / 5.5 + |dy| / 6.5 (the rhombus: 1 on its rim): a low pyramid of fire with flat facets and sharp
# ridges along its diagonals, terraced so that the bright rings stand a little proud of the dark one between them; the
# same mesh for both frames, other materials (51: the star dimmed, its outer bright ring gone dark).
DIAMOND = dict(centre=(-0.5, 0.5), a=5.5, b=6.5, height=1.9)
# the rings: (m of the ring, height there as a fraction of the middle's); the faces outside each ring take the band of
# the next entry of the frames' lists below
DIAMOND_RINGS = ((0.1, 0.93), (0.25, 0.8), (0.32, 0.7), (0.42, 0.66), (0.6, 0.5), (0.7, 0.44), (0.8, 0.3), (1.0, 0.0))
DIAMOND_FRAMES = {  # name: (the middle's band, then the band outside each ring, the last the rim; outermost last)
    # (a shade or two hotter than the sprite's own rings: the dark rings read as holes in a pyramid seen at a slant)
    "shot_sidekick_warfly": (0x7d, 0x79, 0x76, 0x76, 0x77, 0x7b, 0x7b, 0x77),
    "shot_sidekick_warfly_51": (0x7a, 0x78, 0x75, 0x75, 0x74, 0x73, 0x73, 0x75),
}


def diamond(name, frame):
    cx, cy = DIAMOND["centre"]
    a, b, height = DIAMOND["a"], DIAMOND["b"], DIAMOND["height"]
    indices = DIAMOND_FRAMES[frame]
    mats = {}
    for i in indices:
        if i not in mats:
            # (the darker bands glow a little more than the table's: seen at a slant they face away from the sun)
            mats[i] = band_material("warfly", i, factor=1.0 if (i & 15) >= 9 else 1.35,
                                    roughness=0.45 if (i & 15) >= 4 else 0.75)
    # the spokes: the rhombus's four corners (its ridges) and the middles of its sides
    phis = [math.radians(d) for d in (0, 45, 90, 135, 180, 225, 270, 315)]

    def reach(phi, m):
        c, s = abs(math.cos(phi)), abs(math.sin(phi))
        return m / (c / a + s / b)
    heights = dict(DIAMOND_RINGS)

    def top(x, y):
        m = abs(x) / a + abs(y) / b
        if m < 1e-9:
            return height
        lo = (0.0, 1.0)
        for ring_m, f in DIAMOND_RINGS:
            if m <= ring_m + 1e-9:
                f0 = lo[1] + (f - lo[1]) * (m - lo[0]) / (ring_m - lo[0])
                return height * f0
            lo = (ring_m, f)
        return 0.0
    rings = [([reach(p, m) for p in phis], i + 1) for i, (m, _) in enumerate(DIAMOND_RINGS)]
    materials = [mats[i] for i in indices]
    obj = polar_mesh(name, phis, rings, 0, top, materials, under=len(indices) - 1)
    obj.data.transform(Matrix.Translation((cx, cy, 0)))
    return [k.smooth(obj, 20)]


# === The Mint-O-Ship's gem (27) =======================================================================================

# A gem cut with a table (columns 4-8, rows 4-12: its middle column 6, x 0.5): the girdle (its outline: pointed at both
# ends, a short top, a long bottom), crown facets rising from it to a flat table (the outline drawn in towards the
# gem's middle), the table's upper part a white highlight; glassy green, by facet: the upper facets bright, the lower
# ones dark, as the sprite's rows go.
GEM_OUTLINE = ((-1.0, 3.0), (2.0, 3.0), (3.0, 2.0), (3.0, -4.0), (2.0, -5.0), (0.5, -6.0), (-1.0, -5.0),
               (-2.0, -4.0), (-2.0, 2.0))  # (x, y), clockwise from the top left
GEM_CENTRE, GEM_TABLE, GEM_HEIGHT, GEM_TABLE_HEIGHT = (0.5, -0.9), 0.5, 2.2, 1.0


def gem(name):
    cx, cy = GEM_CENTRE
    n = len(GEM_OUTLINE)
    girdle = [Vector((x, y, 0.0)) for x, y in GEM_OUTLINE]
    # (the crown: the outline raised a little, then drawn in to the table)
    crown = [Vector((cx + (x - cx) * 0.82, cy + (y - cy) * 0.86, GEM_HEIGHT * 0.55)) for x, y in GEM_OUTLINE]
    table = [Vector((cx + (x - cx) * GEM_TABLE, cy + (y - cy) * GEM_TABLE * 1.05, GEM_HEIGHT)) for x, y in GEM_OUTLINE]
    verts = girdle + crown + table + [Vector((cx, cy, GEM_HEIGHT)), Vector((cx, cy, 0.0))]
    centre, bottom = 3 * n, 3 * n + 1
    faces, idx = [], []

    def colour_of(y_mid, level):
        # (by the facet's height on the gem and its tier: the sprite's rows, bright above, dark below)
        if level == 2:
            return 0xdf if y_mid > 0.4 else 0xcd
        if level == 1:
            return 0xcf if y_mid > 1.0 else 0xcb if y_mid > -2.5 else 0xc8
        return 0xcb if y_mid > 1.0 else 0xc9 if y_mid > -2.5 else 0xc5
    for i in range(n):
        j = (i + 1) % n
        y_mid = (GEM_OUTLINE[i][1] + GEM_OUTLINE[j][1]) / 2
        faces.append((i, j, n + j, n + i))
        idx.append(colour_of(y_mid, 0))
        faces.append((n + i, n + j, 2 * n + j, 2 * n + i))
        idx.append(colour_of(y_mid, 1))
        faces.append((2 * n + i, 2 * n + j, centre))
        idx.append(colour_of((table[i].y + table[j].y + cy) / 3 - cy + cy, 2))
        faces.append((j, i, bottom))
        idx.append(0xc5)
    mats = {}
    for i in idx:
        if i not in mats:
            mats[i] = lit(f"gem_{i:02x}", i, 0.62 if i >= 0xdd else round(glow_of(i & 15) * 0.95, 3),
                          roughness=0.22, metallic=0.05)
    obj = k.mesh_object(name, verts, faces)
    order = sorted(mats)
    for i in order:
        obj.data.materials.append(mats[i])
    for poly, i in zip(obj.data.polygons, idx):
        poly.material_index = order.index(i)
    k.recalc_normals(obj)
    return [k.smooth(obj, 15)]


# === The Wobbley's wriggling bolt (233-237) ===========================================================================

# Each frame's bolt along its curve (pixel centres (column, row), the head first): round-headed, tapering to its tail,
# its heat falling from the head's light blue to the tail's near black, a little cooler at its edges; a white-blue core
# standing out of the head (the sprite's 0x8d, 0x8b).
WOBBLE_PATHS = {
    233: ((8.75, 0.75), (8.2, 1.7), (7.1, 2.85), (5.95, 3.95), (4.7, 4.9), (3.65, 5.9), (2.9, 6.95), (2.55, 8.0),
          (2.5, 9.0), (3.0, 10.8)),
    234: ((7.75, 0.8), (8.2, 2.0), (8.7, 3.2), (8.95, 4.3), (8.85, 5.3), (8.1, 6.3), (7.0, 7.2), (5.6, 8.1), (4.2, 9.0),
          (3.1, 10.0), (2.2, 11.6)),
    235: ((3.75, 0.8), (4.05, 1.9), (5.0, 2.9), (6.35, 3.8), (7.55, 4.7), (8.75, 5.7), (9.2, 6.8), (9.1, 7.9),
          (8.5, 9.0), (7.5, 10.0), (6.1, 11.4)),
    236: ((2.0, 0.7), (2.1, 1.9), (2.6, 3.1), (3.5, 4.2), (4.5, 5.2), (5.6, 6.2), (6.8, 7.1), (7.9, 8.0), (8.6, 9.0),
          (9.0, 10.0), (9.0, 11.7)),
    237: ((4.55, 0.8), (4.25, 1.9), (3.25, 3.0), (2.45, 4.1), (2.2, 5.2), (2.35, 6.2), (3.15, 7.1), (4.3, 8.0),
          (5.5, 8.9), (6.75, 9.8), (8.2, 11.2)),
}
WOBBLE_WIDTH = ((0.0, 0.0), (0.02, 1.0), (0.06, 1.55), (0.12, 1.75), (0.25, 1.62), (0.45, 1.35), (0.7, 1.1),
                (0.88, 0.85), (0.96, 0.55), (1.0, 0.0))
WOBBLE_ALONG = ((0.0, 15.2), (0.12, 14.6), (0.25, 13.0), (0.4, 11.0), (0.55, 9.2), (0.7, 7.0), (0.85, 4.6), (1.0, 2.0))
WOBBLE_BANDS = [(-99.0, 0x92), (4.0, 0x95), (7.2, 0x98), (10.2, 0x9b), (13.0, 0x9e)]
WOBBLE_CORE = dict(start=0.03, end=0.3, width=0.62, lift=0.32)
WOBBLE_CORE_BANDS = [(-99.0, 0x9e), (0.8, 0x8d)]  # (its heat: 2 at its front falling to 0 at its end)


def wobble(name, sprite):
    path = Path([px(c, r) for c, r in WOBBLE_PATHS[sprite]], smooth=3)
    width = kit.curve(WOBBLE_WIDTH)
    along = kit.curve(WOBBLE_ALONG)

    def heat(t, u):
        return along(t) - 2.6 * u * u
    mats = [band_material("wobble", i) for _, i in WOBBLE_BANDS]
    body = Tube(path, width, heat, WOBBLE_BANDS, depth=0.85, gap=0.75, angle_gap=math.radians(30.0))
    parts = [k.smooth(body.build(name + "_bolt", mats), 70)]
    c = WOBBLE_CORE
    start, end = c["start"], c["end"]
    core_path = Path([tuple(path.point(start + (end - start) * i / 12)) for i in range(13)], smooth=0)

    def core_width(t):
        return c["width"] * (math.sqrt(max(0.0, 1.0 - (1.0 - t / 0.25) ** 2)) if t < 0.25
                             else ((1.0 - t) / 0.75) ** 0.8)

    def core_heat(t, u):
        return 2.0 * (1.0 - t)

    def floor(x, y):
        return body.top(x, y) - 0.06
    core = Tube(core_path, core_width, core_heat, WOBBLE_CORE_BANDS, depth=c["lift"] / c["width"], floor=floor,
                gap=0.6, angle_gap=math.radians(45.0))
    cmats = [band_material("wobble", i) for _, i in WOBBLE_CORE_BANDS]
    parts.append(k.smooth(core.build(name + "_core", cmats), 70))
    return parts


# === The Beno Wallop Beam's arch (30) =================================================================================

# The arch's middle line (pixel centres), from its top (column 5.5) down the right leg to its tip, and its half-width
# along it; the left half is its mirror image. The heat: a crest near the outer edge (u = ARCH_CREST), cooling fast
# towards the outer edge and slowly towards the inside, and along the arch from the top to the leg's tip.
ARCH_PATH = ((5.5, 3.0), (6.3, 3.0), (7.4, 3.25), (8.5, 4.0), (9.0, 5.2), (9.15, 6.5), (9.5, 7.8), (9.95, 9.0),
             (10.15, 9.85))
ARCH_WIDTH = ((0.0, 3.5), (0.12, 3.45), (0.24, 3.3), (0.38, 2.95), (0.5, 2.35), (0.63, 1.8), (0.77, 1.2), (0.91, 0.72),
              (1.0, 0.0))
ARCH_ALONG = ((0.0, 16.0), (0.25, 15.6), (0.45, 14.2), (0.62, 12.0), (0.78, 9.0), (0.9, 6.4), (1.0, 4.0))
ARCH_CREST, ARCH_OUT, ARCH_IN = 0.3, 21.0, 7.4
ARCH_BANDS = [(-99.0, 0x72), (3.6, 0x75), (6.6, 0x78), (9.6, 0x7a), (12.0, 0x7c), (14.0, 0x7e)]
ARCH_CORE = dict(end=0.62, width=0.7, lift=0.34)
ARCH_CORE_BANDS = [(-99.0, 0x7e), (0.7, 0x7f)]


def arch(name):
    path = Path([px(c, r) for c, r in ARCH_PATH], smooth=3)
    width = kit.curve(ARCH_WIDTH)
    along = kit.curve(ARCH_ALONG)

    def heat(t, u):
        d = u - ARCH_CREST
        return along(t) - (ARCH_OUT if d > 0 else ARCH_IN) * d * d
    mats = [band_material("arch", i) for _, i in ARCH_BANDS]
    body = Tube(path, width, heat, ARCH_BANDS, depth=0.62, gap=1.0, angle_gap=math.radians(30.0), caps=(False, True))
    right = body.build(name + "_fire", mats)
    # (the crest's core: a thin raised line along the crest, white at the top, pale yellow down the leg)
    end = ARCH_CORE["end"]

    def crest_point(t):
        p, n = path.point(t), path.normal(t)
        return tuple(p + n * (ARCH_CREST * width(t)))
    core_path = Path([crest_point(end * i / 14) for i in range(15)], smooth=0)

    def core_width(t):
        return ARCH_CORE["width"] * (((1.0 - t) / 0.4) ** 0.7 if t > 0.6 else 1.0)

    def core_heat(t, u):
        return 1.0 - t

    def floor(x, y):
        return body.top(x, y) - 0.06
    core = Tube(core_path, core_width, core_heat, ARCH_CORE_BANDS, depth=ARCH_CORE["lift"] / ARCH_CORE["width"],
                floor=floor, gap=0.9, angle_gap=math.radians(45.0), caps=(False, True))
    cmats = [band_material("arch_core", i) for _, i in ARCH_CORE_BANDS]
    core_right = core.build(name + "_crest", cmats)
    left, core_left = mirrored(right, name + "_fire_l"), mirrored(core_right, name + "_crest_l")
    fire = weld(join([right, left], name + "_fire"))
    crest = weld(join([core_right, core_left], name + "_crest"))
    return [k.smooth(fire, 65), k.smooth(crest, 65)]


# === The models =======================================================================================================

def build_model(name):
    if name == "shot_sidekick_charge":
        return build_252(name)
    if name == "shot_sidekick_charge_2":
        return blue_drop(name, DROPS["253"])
    if name == "shot_sidekick_charge_3":
        return build_254(name)
    if name == "shot_sidekick_gerund":
        parts = []
        for key in ("48_middle", "48_left", "48_right"):
            parts += blue_drop(name + "_" + key.split("_")[1], DROPS[key])
        return parts
    if name in CAPSULES:
        sprite, x, half, spine_w, _ = CAPSULES[name]
        return capsule(name, x, half, spine_w)
    if name in DIAMOND_FRAMES:
        return diamond(name, name)
    if name == "shot_sidekick_mint":
        return gem(name)
    if name.startswith("shot_sidekick_wobbley_"):
        return wobble(name, int(name.rsplit("_", 1)[1]))
    if name == "shot_sidekick_wallop":
        return arch(name)
    raise KeyError(name)


# name: (the sprites it draws, what it is, its hot point for the checks' glow (model coordinates))
MODELS = {
    "shot_sidekick_charge": ((252,), "the Charge Cannon's first charge: the pulse's bolt in blue", (-1.0, 4.6)),
    "shot_sidekick_charge_2": ((253,), "its second: a blue drop, a white head", (-1.5, 4.5)),
    "shot_sidekick_charge_3": ((254,), "its third: a blob of light blue round a white hood, three drips", (-1.0, 3.0)),
    "shot_sidekick_gerund": ((48,), "three blue drops, white heads, the middle one larger", (0.0, 4.0)),
    "shot_sidekick_capsule": ((262,), CAPSULES["shot_sidekick_capsule"][4], (-1.0, 0.0)),
    "shot_sidekick_capsule_2": ((263,), CAPSULES["shot_sidekick_capsule_2"][4], (-0.5, 0.0)),
    "shot_sidekick_warfly": ((50,), "a low pyramid of fire, rings round a white-yellow middle", (-0.5, 0.5)),
    "shot_sidekick_warfly_51": ((51,), "the same dimmed, its outer bright ring dark", (-0.5, 0.5)),
    "shot_sidekick_mint": ((27,), "a green gem cut with a table, a white highlight", (0.5, 0.5)),
    "shot_sidekick_wobbley_233": ((233,), "a blue bolt, diagonal", px(8.0, 2.0)),
    "shot_sidekick_wobbley_234": ((234,), "a blue bolt, hooked", px(8.5, 2.5)),
    "shot_sidekick_wobbley_235": ((235,), "a blue bolt, bent like an S", px(4.5, 2.5)),
    "shot_sidekick_wobbley_236": ((236,), "a blue bolt, the other diagonal", px(2.0, 2.5)),
    "shot_sidekick_wobbley_237": ((237,), "a blue bolt, hooked the other way", px(3.5, 2.5)),
    "shot_sidekick_wallop": ((30,), "an arch of fire, a white crest near its outer edge", (0.0, 4.5)),
}


def build():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    outdir = options.get("outdir", OUTDIR)
    for name, (sprites, what, hot) in MODELS.items():
        if only is not None and name not in only:
            continue
        k.reset()
        parts = triangulate(build_model(name))
        bpy.context.view_layer.update()
        print(f"== {name} (shots {' '.join(str(s) for s in sprites)}): {what}; top {top_of(parts):.3f}; "
              f"faces up/down/sideways {facing(parts)}")
        if "check" in options:
            kit.check_lines(name, parts, os.path.join(options["check"], "shots.png"),
                            [(s, 0, 0, 0) for s in sprites], hot)
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, parts, os.path.join(outdir, name + ".glb"))
        if "preview" in options:
            view(options["preview"] + name, parts)


if __name__ == "__main__":
    build()
