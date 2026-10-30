"""The Laser's beams (shots sheet sprites 286-293, all 1x1: 12 x 14 cells), modelled (2026-10-29, round 2 of the energy
shots' models; until then each was drawn as its sprite with volume, flat, with the automatic glow: a column of separate
rounded capsules in a white haze).

Who fires them: the Laser (front weapon port 4, weapons 188-198 for power levels 1-11): one segment a game frame
(shotrepeat 0), each 14 pixels long and flying up 14 pixels a frame (sy 14) while following the ship (sx 101), so the
segments join end to end into one beam whose pattern scrolls up the screen; its positions take turns (max), so:
  power 1: 289 293 293          power 5: 286 287                 power 9:  293/289 between 287/286 beams at -10/+10
  power 2: 289 289 293          power 6: two 287 286 288 286     power 10: 290/291 between 289/293 beams
  power 3: 286                           beams at -6/+6          power 11: 290/291 between 287/286 beams
  power 4: 286 287 286 288      power 7: 290 291 290 292
  power 8: 286/287 between 289/293 beams at -10/+10
Also the MegaLaser Dual special (286 in two beams), and enemies: weapon 9 (286 287 286 288) in the third turret of
episodes 1-3's enemy 1 (sheet 4) and the second of SAVARA's 359 and 362 (sheet I), once Enemy Fire Override events give
them a frequency (ASSASSIN's ...), and in episode 4 weapons 145 (LAVA RUN, LAVA EXIT, SIDE EXIT, CORE, DREAD-NOT), 130
(ICE EXIT, BRAINIAC, DREAD-NOT, ICESECRET) and 79 (four beams side by side: UNDERDELI, LAVA RUN, DREAD-NOT, BRAINIAC):
the turret slots turn the records' sideways (-14, 0) into (0, 14), so the enemies' beams fall down the screen (130's
rises), the segments drawn as they are.

As the sprites draw them: vertical beams of the fire's ramp 7 filling the cell's 14 rows, in three widths: 7 pixels
(289: 0x71 0x75 0x79 0x7c 0x79 0x75 0x71, a yellow middle; columns 3-9), 9 (286: a white middle, 0x71 0x75 0x79 0x7c
0x7f ...; columns 2-10) and 12 (290: 0x71 0x75 0x79 0x7c 0x7e 0x7f 0x7f 0x7e ...; the whole cell). Their variants keep
the width: bursts (287, 291) where the middle swells into a white diamond (rows 3-10) and the edges light up orange
round it (287 a column wider each side); dimmed sections (288, 292, 293) where the beam darkens towards its middle
rows to a dark red lens, a thin bright thread (288: the middle column, 0x7f at the ends to 0x79; 292: two, a pixel and
a half either side) running on through it (293: none, its middle columns 0x79 to 0x72).

The models: each segment a length of beam 14 pixels long (y -7 to 7), so that the segments join into one rod: a
half-body (round on top, flat underneath), its section a flattened half-ellipse (DEPTH) of the sprite's width, the same
at both ends for every model of a width (and the same height, see below). Its fire is in bands of ramp 7 by an
idealized heat across the beam (the sprite's columns: ACROSS) and, for the bursts and the dimmed sections, along it;
the mesh is built on the bands (the pulse's method): rings across the rod, each point at its own place along it where
the heat there crosses a band's border (the heat is monotone along the rod at every point: rising to a burst's middle,
falling to a dimmed section's), so that every face lies in one band and none is cut along a border; the points across
the section are the borders where they meet the segment's end and middle (each twice, its rings taken as just inside
and as just outside, then welded, so that a border running along the beam lies on its point), with points between to
keep the section round (GAP). A hot core line stands out of the top down the middle, a shade hotter than the beam under
it (0x7f; the 7-pixel beam's 0x7e), dimming in the dimmed sections (288's thread; 292's two threads). A burst's middle
is hotter, the more the further out (the sprite's white diamond and orange halo), and a star of white light stands out
of it (a four-pointed star: polish_shot_starburst's Star and polar mesh, its arms along and across the beam, white,
pale yellow and yellow; 287's across arms reach a pixel out over the rod's edges, where the sprite is a column wider;
a swollen rod there folded faces where the borders cross the swell, so the star's arms do it). A dimmed section darkens
in lenses pointed at their ends (293's one in the middle, 288's either side of its thread, 292's between and outside
its threads). Each segment's bottom end is rounded (a third of the half-width long, inside the segment below where
they join: an enemy's falling beam shows its front end, a broken beam its pieces' ends; a flat end read as a V of the
bands at the camera's slant), the core line's closed, the top ends open (they always face away from the camera). One
material per palette index (the rod's, the core line's and the star's alike), 3-8 a model, each glowing in its own
colour by its shade at 0.8 of the shots' table (0.17-0.5: a beam's hot bands are wide); 161-183 triangles a plain
segment, 221-635 the others.

Heights: the game centres a shot model in height on its bounds, so a model taller than its neighbours would sit lower
and step at the joints: the bursts (their stars), 293 (no core line) and 292 (its threads lower on the rod's curve)
take a height= in models.cfg (half the difference of their bounds' middles against their width's plain beam's),
printed by the build ("height=").

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the origin at the
cell's centre (pixel 6, 7: the 7- and 9-pixel beams' middles are half a pixel right of it, column 6); the beams stand
on z = 0.

models.cfg (the shots section; height= from the build, glow= a halo along each segment, weaker than a lone shot's: the
segments' glows overlap):
    model shot_laser     shots/shot_laser.glb
    model shot_laser_287 shots/shot_laser_287.glb
    model shot_laser_288 shots/shot_laser_288.glb
    model shot_laser_289 shots/shot_laser_289.glb
    model shot_laser_290 shots/shot_laser_290.glb
    model shot_laser_291 shots/shot_laser_291.glb
    model shot_laser_292 shots/shot_laser_292.glb
    model shot_laser_293 shots/shot_laser_293.glb
    shot shots 286 shot_laser                  glow=13:0.25:123:0.5:0
    shot shots 287 shot_laser_287 height=0.12  glow=18:0.42:125:0.5:0
    shot shots 288 shot_laser_288              glow=11:0.15:121:0.5:0
    shot shots 289 shot_laser_289              glow=11:0.22:122:0.5:0
    shot shots 293 shot_laser_293 height=-0.15 glow=9:0.1:120:0.5:0
    shot shots 290 shot_laser_290              glow=16:0.28:124:0:0
    shot shots 291 shot_laser_291 height=0.15  glow=20:0.42:125:0:0
    shot shots 292 shot_laser_292 height=-0.06 glow=14:0.16:122:0:0

Run: Blender -b --factory-startup -P tools/blender/models/shots/polish_shot_laser.py -- [--only <name,...>]
     [--outdir <dir>] (default assets/models/shots) [--check <sheets dir>] (each model's top view against its sprite
     in <dir>/shots.png) [--preview <prefix>] (top, three-quarter and game-camera views, and <prefix>beams_game.png:
     the beams of power 4, 7 and 8 as segments joined end to end)
"""
import math
import os
import sys

import bpy
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
ENEMIES = os.path.join(HERE, "..", "enemies")
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, ENEMIES)
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_flame_drop import monotone  # noqa: E402
from polish_launched_flames import lit, check_frames, turn  # noqa: E402
from polish_shot_starburst import Star, polar_mesh, spoke_angles, glow_of, game_camera  # noqa: E402

OUTDIR = os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "shots")
HALF = 7.0  # half a segment's length (the cell's 14 rows)

# --- The sprites (palette indices; rows top to bottom) ----------------------------------------------------------------

SPRITES = {
    286: ".. .. 71 75 79 7c 7f 7c 79 75 71 ..",  # every row the same
    289: ".. .. .. 71 75 79 7c 79 75 71 .. ..",
    290: "71 75 79 7c 7e 7f 7f 7e 7c 79 75 71",
    287: """
.. 70 72 75 79 7c 7f 7c 79 75 72 70
.. 71 73 75 79 7c 7f 7c 79 75 73 71
.. 72 74 75 79 7c 7f 7c 79 75 74 72
.. 73 76 78 7b 7f 7f 7f 7b 78 76 73
.. 75 78 7a 7c 7f 7f 7f 7c 7a 78 75
.. 77 7a 7c 7f 7f 7f 7f 7f 7c 7a 77
.. 79 7c 7f 7f 7f 7f 7f 7f 7f 7c 7a
(rows 7-13 mirror rows 6-0)""",
    288: """
.. .. 71 75 79 79 7f 79 79 75 71 ..
.. .. 71 75 78 76 7e 76 78 75 71 ..
.. .. 71 75 77 73 7d 73 76 75 71 ..
.. .. 71 75 75 74 7c 74 75 75 71 ..
.. .. 71 75 74 72 7b 72 74 75 71 ..
.. .. 71 75 73 72 7a 72 73 75 71 ..
.. .. 71 75 73 72 79 72 73 75 71 ..
(rows 7-13 mirror rows 6-0)""",
}

# --- The beams --------------------------------------------------------------------------------------------------------
# Across a beam: u, the way out from its middle line to its edge (0-1, the edge at its half-width); its heat at the
# segment's ends (in shades of ramp 7) from the sprite's columns (their middles at u = 2 k / width), a little hotter
# (the camera sees the rod's sides, and the sun leaves one in shade: the sprite's own widths made it read red).
ACROSS = {
    7: ((0.0, 12.8), (0.286, 10.4), (0.571, 6.6), (0.857, 2.8), (1.0, 1.4)),
    9: ((0.0, 15.2), (0.222, 13.4), (0.444, 10.6), (0.667, 6.8), (0.889, 2.8), (1.0, 1.4)),
    12: ((0.0, 15.3), (0.083, 15.0), (0.25, 14.0), (0.417, 12.4), (0.583, 10.0), (0.75, 6.6), (0.917, 2.8), (1.0, 1.4)),
}
# The section: a half-ellipse DEPTH times the half-width high (flattened: a rod, not a pipe).
DEPTH = 0.6
# The fire's bands (lowest heat, palette index): the edges' dark red to the yellow-white along the middle; the flat
# underside and the bottom end's cap take the band beside them. Each glows in its own colour by its shade.
BANDS = ((-99.0, 0x72), (3.2, 0x75), (7.0, 0x79), (10.4, 0x7c), (13.4, 0x7e))
FIRE_ROUGHNESS = 0.5
# The bands' glow against the shots' table (glow_of): a beam is long, its hot bands wide, and its segments' glows
# overlap (at 1.0 the power 11 beams burned into one yellow-white mass in deep space at 2x).
EMISSION = 0.8
# Points across the section between the borders where they lie further apart than GAP (radians round the section), so
# that it stays round; a border's two section points take their rings as BORDER_SIDE inside and outside it.
GAP = math.radians(18.0)
BORDER_SIDE = 1e-4
# The core line: half its width, how far it stands out of the rod's top, its bands along it by its heat (lowest heat,
# palette index), its points round.
CORE_HALF = 0.65
CORE_LIFT = 0.3
CORE_BANDS = ((-99.0, 0x7a), (11.5, 0x7c), (12.6, 0x7d), (13.6, 0x7e), (14.5, 0x7f))
CORE_ROUGHNESS = 0.4
CORE_SEGMENTS = 6
CORE_BOOST = 1.0  # (a shade hotter than the beam's middle under it)
# The bottom end's rounding: its length (times the half-width) and its rings (fractions of the way to its point).
CAP = 0.36
CAP_RINGS = (0.4, 0.75, 0.94)
# The dimmed sections' lens: how much nearer the middle rows (pixels) the dimming begins at the edge than at the middle.
LENS = 3.2


def curve(points):
    """A smooth curve through ((x, y), ...) (in any order of x)."""
    points = sorted(points)
    return monotone([p[0] for p in points], [p[1] for p in points])


class Beam:
    """A segment's model: its width (7, 9 or 12 pixels), its middle's x, how its heat changes along it (none, a burst or
    a dimmed section), its core line(s) and its star."""

    def __init__(self, name, sprite, width, centre, kind="plain", threads=(0.0,), thread_heat=None, star=None,
                 dim=None, boost=None):
        self.name, self.sprite, self.width, self.centre, self.kind = name, sprite, width, centre, kind
        self.half = width / 2.0
        self.threads = threads  # the core lines' x against the middle (none: ())
        self.thread_heat = thread_heat  # heat along a core line: f(|y|), None: the beam's middle heat at the ends
        self.star = star  # (Star, its lift over the rod's top at its middle, its across arms' stretch) or None
        self.dim = dim  # (along: ((|y|, how much of it)...), by u: ((u, shades darker)...)) or None
        self.boost = boost  # a burst's: (along: ((|y|, how much of it)...), by u: ((u, shades hotter)...)) or None
        self._across = curve(ACROSS[width])
        if dim is not None:
            self._dim_y, self._dim_u, self.lenses = curve(dim[0]), curve(dim[1]), dim[2]
        if boost is not None:
            self._boost_y, self._boost_u = curve(boost[0]), curve(boost[1])

    def half_width(self, y):
        """The rod's half-width (the same all along: the segments join)."""
        return self.half

    def heat(self, y, u):
        """The fire's heat at y along the segment, u out across it."""
        u = min(abs(u), 1.0)
        h = self._across(u)
        if self.kind == "burst":
            # (hotter round the middle, the more the further out: the sprite's white diamond and orange halo)
            h = min(h + self._boost_y(abs(y)) * self._boost_u(u), 15.5)
        elif self.kind == "dim":
            # (the further from a lens's middle line, the nearer the middle rows it begins: pointed lenses)
            off = min(min(abs(u - c) / hw for c, hw in self.lenses), 1.0)
            h = h - self._dim_y(abs(y) + LENS * off) * self._dim_u(u)
        return h

    def top(self, x, y):
        """The rod's top over (x, y) (0 outside it)."""
        w = self.half_width(y)
        u = (x - self.centre) / w
        return DEPTH * w * math.sqrt(max(0.0, 1.0 - u * u)) if abs(u) < 1.0 else 0.0


def mesh_with_bands(name, verts, faces, bands, materials):
    """A mesh whose faces take their bands' materials (only the materials used, one slot each)."""
    obj = k.mesh_object(name, verts, faces)
    slots = []
    for band in bands:
        if materials[band] not in slots:
            slots.append(materials[band])
    for m in slots:
        obj.data.materials.append(m)
    for poly, band in zip(obj.data.polygons, bands):
        poly.material_index = slots.index(materials[band])
    return obj


def angle_of(u):
    """The angle round the section of the point u out (90 degrees at the middle line, 0 at the edge)."""
    return math.acos(min(max(u, -1.0), 1.0))


def heat_t(beam, t, u):
    """The heat on the top half at t (0 the segment's top end, y 7; 1 its middle, y 0)."""
    return beam.heat(HALF * (1.0 - t), u)


def section_points(beam):
    """The points across the right half of the section, from the middle (u 0) to the edge (u 1): (u, its rings' side):
    the middle, the edge, every border where it meets the end and the middle sections (twice: its rings as just inside
    it and as just outside, so that a border running along the beam lies exactly on the point), and points between
    where they lie further apart than GAP round the section."""
    borders = set()
    for t in (0.0, 1.0):
        for lowest, _ in BANDS[1:]:
            steps = 400
            for i in range(steps):
                u0, u1 = i / steps, (i + 1) / steps
                h0, h1 = heat_t(beam, t, u0) - lowest, heat_t(beam, t, u1) - lowest
                if h0 * h1 < 0:
                    lo, hi = u0, u1
                    for _ in range(40):
                        mid = (lo + hi) / 2
                        if (heat_t(beam, t, mid) - lowest) * h0 > 0:
                            lo = mid
                        else:
                            hi = mid
                    borders.add(round((lo + hi) / 2, 6))
    us = sorted({0.0, 1.0} | borders)
    merged = [us[0]]
    for u in us[1:]:
        if u - merged[-1] > 0.025:
            merged.append(u)
        elif u == 1.0:
            merged[-1] = 1.0
    points = [(merged[0], 0.0)]
    for u in merged[1:]:
        start = angle_of(points[-1][0])
        gap = start - angle_of(u)
        extra = int(gap / GAP)
        points += [(math.cos(start - gap * j / (extra + 1)), 0.0) for j in range(1, extra + 1)]
        if 0.0 < u < 1.0 and any(abs(u - b) < 0.026 for b in borders):
            points += [(u, -BORDER_SIDE), (u, BORDER_SIDE)]
        else:
            points.append((u, 0.0))
    return points


def ring_ts(beam, points):
    """The rings of the top half along t (0 the top end, 1 the middle), each a t per section point, and the band of the
    faces after each: a ring on each band border (at each point where the heat along it crosses the border: rising to a
    burst's middle, falling to a dimmed section's; where it doesn't, at the end it is past or the middle it doesn't
    reach), and the ends' rings (no rings between: the rod is straight). Every face between two rings lies in one
    band."""
    rising = beam.kind == "burst"
    values = [(lowest, band) for band, (lowest, _) in enumerate(BANDS) if band > 0]
    values = sorted(values) if rising else sorted(values, reverse=True)
    rings, after = [], []
    for value, band in values:
        ring = []
        for u, side in points:
            us = min(max(u + side, 0.0), 1.0)
            h0, h1 = heat_t(beam, 0.0, us), heat_t(beam, 1.0, us)
            if (h0 - value) * (h1 - value) >= 0:
                # (no crossing: the border lies before the end or past the middle at this point)
                passed = (h0 >= value) if rising else (h0 < value)
                ring.append(0.0 if passed else 1.0)
                continue
            lo, hi = 0.0, 1.0
            for _ in range(40):
                mid = (lo + hi) / 2
                if (heat_t(beam, mid, us) - value) * (h0 - value) > 0:
                    lo = mid
                else:
                    hi = mid
            ring.append((lo + hi) / 2)
        rings.append(ring)
        # (the faces after a rising border are its band; after a falling border, the band below it)
        after.append(band if rising else band - 1)
    for r in range(1, len(rings)):
        rings[r] = [max(a, b) for a, b in zip(rings[r], rings[r - 1])]
    first = 0 if rising else len(BANDS) - 1  # (the band before the first border)
    out, bands = [[0.0] * len(points)], []
    current = first
    for ring, band in list(zip(rings, after)) + [([1.0] * len(points), None)]:
        out.append(ring)
        bands.append(current)
        if band is not None:
            current = band
    return out, bands


def body(name, beam, materials):
    """The rod: rings across it (from its top end to its bottom end, mirrored about its middle), each a point per
    section point (from the right edge over the top to the left edge), the band borders on the rings; its flat
    underside; its bottom end closed (each wedge of the cap the band of its stretch of the edge)."""
    points = section_points(beam)
    half, half_bands = ring_ts(beam, points)
    top = [[HALF * (1.0 - t) for t in ring] for ring in half]  # (y per section point, top end to the middle)
    rings = top + [[-y for y in ring] for ring in reversed(top[:-1])]
    ring_bands = half_bands + list(reversed(half_bands))
    # The section from the right edge over the top to the left edge: (signed u, the point's index).
    order = ([(points[i][0], i) for i in range(len(points) - 1, 0, -1)] +
             [(-points[i][0], i) for i in range(len(points))])
    verts, faces, bands = [], [], []
    index = {}
    for r, ring in enumerate(rings):
        for c, (su, pi) in enumerate(order):
            y = ring[pi]
            w = beam.half_width(y)
            index[r, c] = len(verts)
            verts.append((round(beam.centre + su * w, 7), round(y, 7),
                          round(DEPTH * w * math.sqrt(max(0.0, 1.0 - su * su)), 7)))
    for r in range(len(rings) - 1):
        for c in range(len(order) - 1):
            quad = [index[r, c], index[r, c + 1], index[r + 1, c + 1], index[r + 1, c]]
            pts = []
            for v in quad:
                if not pts or verts[v] != verts[pts[-1]]:
                    pts.append(v)
            if len(pts) > 1 and verts[pts[0]] == verts[pts[-1]]:
                pts.pop()
            if len(pts) < 3 or len({verts[v] for v in pts}) < 3:
                continue
            faces.append(tuple(pts))
            bands.append(ring_bands[r])
    last = len(order) - 1
    for r in range(len(rings) - 1):  # (facing down)
        quad = [index[r, 0], index[r + 1, 0], index[r + 1, last], index[r, last]]
        if verts[quad[0]] != verts[quad[1]]:
            faces.append(tuple(quad))
            bands.append(0)
    # The bottom end: rounded, the end's section shrinking to a point CAP times the half-width below it (inside the
    # segment below where they join; a falling beam's front, a broken beam's pieces' ends), each column its end's band.
    w = beam.half_width(-HALF)
    length = CAP * w
    cap = []
    for f in CAP_RINGS:
        shrink = math.sqrt(max(0.0, 1.0 - f * f))
        ring = []
        for su, _ in order:
            ring.append(len(verts))
            verts.append((round(beam.centre + su * w * shrink, 7), round(-HALF - f * length, 7),
                          round(DEPTH * w * math.sqrt(max(0.0, 1.0 - su * su)) * shrink, 7)))
        cap.append(ring)
    tip = len(verts)
    verts.append((beam.centre, -HALF - length, 0.0))
    end_bands = [band_of(beam, -HALF + 0.01, (abs(order[c][0]) + abs(order[c + 1][0])) / 2)
                 for c in range(len(order) - 1)]
    previous = [index[len(rings) - 1, c] for c in range(len(order))]
    for ring in cap + [None]:
        for c in range(len(order) - 1):
            if ring is None:
                face = (previous[c], previous[c + 1], tip)
            else:
                face = (previous[c], previous[c + 1], ring[c + 1], ring[c])
            if len({verts[v] for v in face}) == len(face):
                faces.append(face)
                bands.append(end_bands[c])
        # (its underside, facing down)
        if ring is None:
            faces.append((previous[0], tip, previous[-1]))
        else:
            faces.append((previous[0], ring[0], ring[-1], previous[-1]))
        bands.append(0)
        previous = ring
    obj = mesh_with_bands(name, verts, faces, bands, materials)
    weld(obj)
    return k.smooth(obj, 60), sorted(set(bands))


def weld(obj):
    """Merges the points that lie on one another (a border's two section points; rings meeting at a point)."""
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.dissolve_degenerate(bm, dist=1e-6, edges=bm.edges)
    bm.to_mesh(obj.data)
    bm.free()


def band_of(beam, y, u):
    h = beam.heat(y, u)
    return max(i for i, b in enumerate(BANDS) if h >= b[0])


def core_heat(beam, y):
    if beam.thread_heat is not None:
        return beam.thread_heat(abs(y))
    return beam.heat(y, 0.0) + CORE_BOOST


def core_line(name, beam, x_off, materials):
    """A core line along the rod's top at x_off from its middle: a thin half-body standing CORE_LIFT out of the top,
    its bands along it by its heat (rings on the borders), its ends running into the joints."""
    ys = [HALF, -HALF]
    # (rings where its heat crosses a border, between the ends)
    crossings = set()
    for lowest, _ in CORE_BANDS[1:]:
        steps = 280
        for i in range(steps):
            y0 = HALF - 2 * HALF * i / steps
            y1 = HALF - 2 * HALF * (i + 1) / steps
            h0, h1 = core_heat(beam, y0), core_heat(beam, y1)
            if (h0 - lowest) * (h1 - lowest) < 0:
                lo, hi = y0, y1
                for _ in range(40):
                    mid = (lo + hi) / 2
                    if (core_heat(beam, mid) - lowest) * (h0 - lowest) > 0:
                        lo = mid
                    else:
                        hi = mid
                crossings.add(round((lo + hi) / 2, 6))
    ys = sorted(set(ys) | crossings, reverse=True)

    def band_at(h):
        return max(i for i, b in enumerate(CORE_BANDS) if h >= b[0])
    angles = [math.pi * j / CORE_SEGMENTS for j in range(CORE_SEGMENTS + 1)]
    verts, faces, bands = [], [], []
    for y in ys:
        cx = beam.centre + x_off
        base = beam.top(cx, y)
        for a in angles:
            dx = CORE_HALF * math.cos(a)
            z = (beam.top(cx + dx, y) - 0.05) + (base + CORE_LIFT - (beam.top(cx + dx, y) - 0.05)) * math.sin(a)
            verts.append((cx + dx, y, z))
    n = len(angles)
    for i in range(len(ys) - 1):
        h = core_heat(beam, (ys[i] + ys[i + 1]) / 2)
        for j in range(n - 1):
            faces.append((i * n + j, i * n + j + 1, (i + 1) * n + j + 1, (i + 1) * n + j))
            bands.append(band_at(h))
    # (its bottom end closed, facing down the screen: a falling beam's front)
    last = (len(ys) - 1) * n
    centre = len(verts)
    verts.append((beam.centre + x_off, ys[-1], beam.top(beam.centre + x_off, ys[-1]) - 0.05))
    for j in range(n - 1):
        faces.append((centre, last + j, last + j + 1))
        bands.append(bands[-1])
    obj = mesh_with_bands(name, verts, faces, bands, materials)  # (wound outwards as built: a strip on the top)
    return k.smooth(obj, 60), sorted(set(bands))


STAR_SPOKES = (0.0, 4.0, 12.0, 26.0, 45.0)
STAR_RINGS = (0.3, 0.52, 0.78, 0.92, 1.0)  # (fractions of the way out to its edge on each spoke)
STAR_BANDS = ((0.0, 0x7f), (0.52, 0x7e), (0.78, 0x7d), (0.92, 0x7c))  # (from the fraction out, palette index)


def flare(name, beam, materials):
    """A burst's star: four-pointed, its arms along and across the beam (the across ones stretched, 287's out over the
    rod's edges), standing out of the rod's top in the middle, its edge sunk a little into the rod (not below z 0);
    bands out from its middle: white, pale yellow, yellow."""
    star, lift, stretch = beam.star
    phis = spoke_angles(STAR_SPOKES)
    edges = [star.outline(p) for p in phis]
    rings = []
    for f in STAR_RINGS:
        band = max(i for i, b in enumerate(STAR_BANDS) if f >= b[0] - 1e-9)
        rings.append(([f * e for e in edges], band))

    def top(x, y):
        # (x, y: the star's own, its across arms stretched; on the rod's top at the beam's middle)
        bx, by = beam.centre + x * stretch, y
        rise = 1.0 if abs(x) < 1e-9 and abs(y) < 1e-9 else star.height(x, y) / (star.depth * star.w0)
        return max(beam.top(bx, by) + lift * rise - (0.1 if rise < 1e-6 else 0.0), 0.0)
    obj = polar_mesh(name, phis, rings, 0, top, materials)
    # (its across arms stretched, onto the beam's middle)
    for v in obj.data.vertices:
        v.co.x = beam.centre + v.co.x * stretch
    return k.smooth(obj, 80), sorted(set(b for _, b in rings) | {0})


# The models: name, sprite, width, the middle's x, and what changes along it. The dimmed sections: how much of the
# dimming at |y| (a little at the ends, all of it in the middle rows 3-10) and how many shades darker at u (the
# sprites' middle rows against their ends: 288's columns beside the thread 10 darker, its 0x75 column none; 293's middle
# 10; 292's the middle and the columns outside the threads); the threads' heat along them. The bursts: how much hotter
# at |y| (rows 3-10) and u (the more the further out: the rod yellow round the white star, its edges orange; hotter,
# the star read pale on a white middle in deep space).
DIM_9 = (((7.0, 0.22), (6.5, 0.3), (5.5, 0.62), (4.5, 0.9), (3.5, 1.0), (0.0, 1.0)),
         ((0.0, 6.2), (0.12, 8.5), (0.222, 11.4), (0.444, 7.6), (0.6, 2.5), (0.7, 0.0), (1.0, 0.0)),
         ((0.31, 0.22),))  # (the lenses: (middle u, half-width))
DIM_7 = (((7.0, 0.32), (6.5, 0.4), (5.5, 0.65), (4.5, 0.9), (3.5, 1.0), (0.0, 1.0)),
         ((0.0, 10.8), (0.286, 7.4), (0.45, 3.5), (0.571, 1.0), (0.65, 0.0), (1.0, 0.0)),
         ((0.0, 0.5),))
DIM_12 = (((7.0, 0.2), (6.5, 0.3), (5.5, 0.62), (4.5, 0.9), (3.5, 1.0), (0.0, 1.0)),
          ((0.0, 10.3), (0.12, 9.5), (0.2, 5.5), (0.25, 4.6), (0.32, 8.0), (0.417, 11.0), (0.583, 7.4), (0.7, 3.0),
           (0.8, 0.5), (1.0, 0.0)),
          ((0.06, 0.17), (0.5, 0.2)))
# 288's thread: 0x79 in the middle, 0x7f at the ends (292's threads 0x7a in the middle)
THREAD_9 = curve(((0.0, 9.2), (0.5, 9.2), (6.5, 15.0), (7.0, 15.0)))
THREAD_12 = curve(((0.0, 9.6), (0.5, 9.6), (6.5, 15.0), (7.0, 15.0)))
BOOST_9 = (((0.0, 1.3), (1.5, 1.05), (2.5, 0.8), (3.5, 0.6), (4.5, 0.3), (5.5, 0.12), (7.0, 0.0)),
           ((0.0, 0.0), (0.444, 1.5), (0.667, 3.8), (0.889, 5.5), (1.0, 6.2)))
BOOST_12 = (((0.0, 1.3), (1.5, 1.05), (2.5, 0.8), (3.5, 0.6), (4.5, 0.3), (5.5, 0.12), (7.0, 0.0)),
            ((0.0, 0.0), (0.417, 1.2), (0.583, 2.5), (0.75, 4.5), (0.917, 6.5), (1.0, 7.0)))
BURST_9 = (Star(tip=4.5, w0=2.2, taper=1.0, depth=1.0, section=1.8), 0.55, 1.25)  # (star, lift, across stretch)
BURST_12 = (Star(tip=4.5, w0=2.5, taper=1.0, depth=1.0, section=1.8), 0.6, 1.3)

MODELS = [
    Beam("shot_laser", 286, 9, 0.5),
    Beam("shot_laser_287", 287, 9, 0.5, kind="burst", star=BURST_9, boost=BOOST_9),
    Beam("shot_laser_288", 288, 9, 0.5, kind="dim", dim=DIM_9, thread_heat=THREAD_9),
    Beam("shot_laser_289", 289, 7, 0.5),
    Beam("shot_laser_293", 293, 7, 0.5, kind="dim", dim=DIM_7, threads=()),
    Beam("shot_laser_290", 290, 12, 0.0),
    Beam("shot_laser_291", 291, 12, 0.0, kind="burst", star=BURST_12, boost=BOOST_12),
    Beam("shot_laser_292", 292, 12, 0.0, kind="dim", dim=DIM_12, threads=(-1.5, 1.5), thread_heat=THREAD_12),
]
FAMILY_BASE = {7: "shot_laser_289", 9: "shot_laser", 12: "shot_laser_290"}


def material(index):
    """The model's material of a palette index (one per index, the rod's, the core line's and the star's alike: every
    material is a draw), glowing by its shade (times EMISSION); the hottest a little smoother."""
    return lit(f"laser_{index:02x}", index, round(glow_of(index & 15) * EMISSION, 3),
               roughness=CORE_ROUGHNESS if index >= 0x7d else FIRE_ROUGHNESS)


def materials_for(bands):
    return [material(index) for _, index in bands]


def build_model(beam):
    parts = []
    rod, _ = body(f"{beam.name}_rod", beam, materials_for(BANDS))
    parts.append(rod)
    for n, x_off in enumerate(beam.threads):
        line, _ = core_line(f"{beam.name}_core{n}", beam, x_off, materials_for(CORE_BANDS))
        parts.append(line)
    if beam.star is not None:
        star, _ = flare(f"{beam.name}_star", beam, materials_for(STAR_BANDS))
        parts.append(star)
    return triangulate(parts)


def facing(parts):
    """(faces facing up, facing down, others) over all the parts: the tops must face up, the undersides down."""
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
    """The middle of the model's height bounds, twice (the game centres a model on it): its top when it stands on 0."""
    zs = [(p.matrix_world @ v.co).z for p in parts for v in p.data.vertices]
    return max(zs) + min(zs)


# --- Previews ---------------------------------------------------------------------------------------------------------

def game_view(prefix, objects):
    mk.preview(prefix, objects, size=(12, 14), scale=32, distance=0.42)
    scene = bpy.context.scene
    cam, sun = game_camera(scene, 16.0, (512, 512))
    scene.render.filepath = prefix + "_game.png"
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam)
    bpy.data.objects.remove(sun)


BEAMS_VIEW = [  # (x, the sprites from the bottom up): power 4's beam, power 7's, power 8's three
    (-30.0, (286, 287, 286, 288) * 2),
    (-8.0, (290, 291, 290, 292) * 2),
    (12.0, (289, 293) * 4),
    (22.0, (286, 287) * 4),
    (32.0, (289, 293) * 4),
]


def beams_view(prefix, heights):
    """Beams of segments joined end to end as the game shows them (each at its models.cfg height)."""
    k.reset()
    scene = bpy.context.scene
    scene.view_settings.view_transform = "Standard"
    by_sprite = {b.sprite: b for b in MODELS}
    for x, sprites in BEAMS_VIEW:
        for n, sprite in enumerate(sprites):
            beam = by_sprite[sprite]
            parts = build_model(beam)
            lift = heights.get(beam.name, 0.0) - top_of(parts) / 2  # (centred in height, as the game does)
            mk.transform(parts, Matrix.Translation((x, (n - 3.5) * 2 * HALF, lift)))
    bpy.context.view_layer.update()
    cam, sun = game_camera(scene, 120.0, (900, 1200))
    scene.render.filepath = prefix + "beams_game.png"
    bpy.ops.render.render(write_still=True)


def build():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    outdir = options.get("outdir", OUTDIR)
    tops = {}
    for beam in MODELS:
        k.reset()
        parts = build_model(beam)
        tops[beam.name] = top_of(parts)
    heights = {name: round((top - tops[FAMILY_BASE[b.width]]) / 2, 2) for b in MODELS for name, top in tops.items()
               if name == b.name}
    for beam in MODELS:
        if only is not None and beam.name not in only:
            continue
        k.reset()
        parts = build_model(beam)
        bpy.context.view_layer.update()
        print(f"== {beam.name} (shots {beam.sprite}): {beam.width}-pixel beam, {beam.kind}; top {tops[beam.name]:.3f}, "
              f"height={heights[beam.name]:g}; faces up/down/sideways {facing(parts)}")
        if "check" in options:
            check_frames(parts, os.path.join(options["check"], "shots.png"),
                         [(beam.sprite, turn(0), f"shots {beam.sprite}")], move_to_frame=False)
        bpy.context.scene.view_settings.view_transform = "Standard"
        mk.report(beam.name, parts, os.path.join(outdir, beam.name + ".glb"))
        if "preview" in options:
            game_view(options["preview"] + beam.name, parts)
    if "preview" in options and only is None:
        beams_view(options["preview"], heights)


if __name__ == "__main__":
    build()
