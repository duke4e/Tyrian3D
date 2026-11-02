#!/usr/bin/env python3
"""Terrain for the 3D view's ground (background 1): heights for a whole map, computed offline from
the map's surfaces and stored as an asset (assets/terrain/<map>.ter), which the game loads.

The tiles only say what surface is where; the terrain doesn't follow them. Each pixel of the map
(exported with TYR3D_EXPORT_MAPS, with the generated columns beside it) is sorted into surface
classes by its brightness, texture and colour (k-means, the same every run); each class has a
height (tools/terrain/levels.json, by map; "~" takes the nearest other surface's height, for rims
and edges), and the heights are softened into slopes and cliffs, with a little relief of the
surface's own detail on top. Black space ("void", for the levels over space) can sink into a chasm
below the platforms.

The game lifts ground enemies onto the terrain (render_gpu.c stand_lift), so the terrain is level
under them (export/terrain/ground.txt, from tools/terrain/ground_log.sh: where they stand and move,
what their models cover, where on the screen and which object they are pieces of): a pad at one
height under what stands, as far as the terrain drawn under it reaches as the map scrolls (towards
the point below the camera, the more the higher it stands); and roads along what moves, at the
height of the ground under it, made gentle (ramps and shallow cuttings where a track crosses a
cliff's edge, a shelf where it runs along one), so that rigid models stand flat on the ground rather
than half in a slope or over a cliff.

usage: <python with numpy, scipy and PIL> tools/terrain/make_terrain.py classify <map hash>...
       ... make_terrain.py build <map hash>...      (or "all": every map in levels.json)
       ... make_terrain.py sheets                   (contact sheets of the built terrain)

classify writes export/terrain/<map>_classes.png (the map beside its classes, numbered, with how
many standing enemies each holds) for choosing the heights; build writes the asset and
export/terrain/<map>_relief.png (the map lit by its terrain, with its enemies and their tracks). The
game's ground stands at height 0: classes where ground enemies stand stay at 0; raised ground
(plateaus, mountains, walls) goes up to TERRAIN_MAX, chasms down to -TERRAIN_MAX.

levels.json, by map: "classes" (how many), "heights" ({class: height or "~"}), and optionally
"softness" (how far cliffs spread, pixels), "detail" (relief of the surface's detail), "rolling"
(the height of gentle hills and hollows over the whole map, for a map of one surface), "void"
(the height of black space, e.g. -40, or "hole": nothing there, the platforms' walls going down
into the dark, and the stars far below where the level has them; "rim" and "rim_depth" round the
platforms' edges off), "tiles" ({tile shape: height or "~"}: tiles the classes misread, such as
MINERS's heaps and ridges of hex rock on the plateau (0), sorted with its sunken hex rock, or its
craters: their surfaces other than the plain ground round them take the tile's height, found by
their pixels, so in the generated side columns too), "textured" ({"min": local contrast, "height"}:
where the surface is textured, a forest's canopy as opposed to the smooth floor of its clearings),
"ceiling" (the height of a flat background 2 drawn over the ground enemies, its plane with the
headroom, e.g. 48: standing enemies tall enough to show through it stand on lower ground: DELIANI's
towers under its girders), "roads": false (no roads along what moves, for maps where ground enemies
swim or hover over the terrain rather than walk on it).

Backgrounds 2 and 3 (their maps' entries with "solid": true) become solids: their plane on top,
rounded off over "bevel" pixels at the edges, walls down to the ground where they are clear or
where ground enemies are under them, round what their models cover and beyond their far sides as
far as the walls stand over them there (the game only makes them solid where they are drawn over the
ground's enemies, and keeps their tops below what flies). A background 2 that the game draws under
the ground's enemies and that covers the whole map (ICESECRET's ice, over a ground that never shows)
is the ground instead: its entry has "ground": true, and its terrain is made as the ground's is.
"""
import json
import os
import struct
import sys
import zlib

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from scipy.cluster.vq import kmeans2

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MAPS = os.path.join(ROOT, "export", "maps")
OUT = os.path.join(ROOT, "assets", "terrain")
REVIEW = os.path.join(ROOT, "export", "terrain")
GROUND = os.path.join(REVIEW, "ground.txt")
LEVELS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "levels.json")

SAMPLE = 2           # game pixels per height sample
TERRAIN_MAX = 60     # heights are stored as signed bytes, in game pixels
HOLE = -128          # a sample with nothing there (B3D_TERRAIN_HOLE)
REVIEW_ROWS = 2100   # the map's rows shown for review: its last (the level's start)
COLOURS = np.array([[230, 60, 60], [60, 200, 60], [60, 90, 230], [230, 200, 40], [200, 60, 200], [40, 200, 200],
                    [240, 240, 240], [140, 100, 60]], np.float32) / 255


def load_map(name):
    """The map's colours (RGBA, 0-1: backgrounds 2 and 3 are clear where they have nothing)."""
    info = json.load(open(os.path.join(MAPS, f"map_{name}.json")))
    parts = [np.asarray(Image.open(os.path.join(MAPS, p["file"])).convert("RGBA")) for p in info["parts"]]
    rgba = np.concatenate(parts, 0).astype(np.float32) / 255
    return info, rgba[..., :3], rgba[..., 3] > 0.5


def read_erasures(name):
    """The map's clean-up (assets/terrain/<map>.era, make_cleanground.py): [(x, y, mask, dx, dy)]."""
    path = os.path.join(OUT, f"{name}.era")
    if not os.path.exists(path):
        return []
    raw = open(path, "rb").read()
    magic, version, count = struct.unpack_from("<4sII", raw, 0)
    if magic != b"TYER":
        return []
    blob = zlib.decompress(raw[12:])
    out, o = [], 0
    for _ in range(count):
        x, y, w, h, dx, dy = struct.unpack_from("<HHBBhh", blob, o)
        o += 10
        out.append((x, y, np.frombuffer(blob[o:o + w * h], np.uint8).reshape(h, w).astype(bool), dx, dy))
        o += w * h
    return out


def cleaned(name, rgb):
    """The map as the 3D view draws it: its clean-up applied (each erased pixel the map's pixel at the offset)."""
    pieces = read_erasures(name)
    if not pieces:
        return rgb
    out = rgb.copy()
    H, W = rgb.shape[:2]
    for x, y, m, dx, dy in pieces:
        ys, xs = np.nonzero(m)
        ys, xs = ys + y, xs + x
        ok = (ys < H) & (xs < W) & (ys + dy >= 0) & (ys + dy < H) & (xs + dx >= 0) & (xs + dx < W)
        out[ys[ok], xs[ok]] = rgb[ys[ok] + dy, xs[ok] + dx]
    return out


def features(rgb):
    lum = rgb @ np.array([0.299, 0.587, 0.114], np.float32)
    mean = ndimage.uniform_filter(lum, 7)
    texture = np.sqrt(np.maximum(ndimage.uniform_filter(lum * lum, 7) - mean * mean, 0))
    chroma = ndimage.gaussian_filter(rgb, (2, 2, 0)) - ndimage.gaussian_filter(lum, 2)[..., None]
    return lum, np.dstack([ndimage.gaussian_filter(lum, 2) * 2, texture * 6, chroma[..., 0] * 4, chroma[..., 2] * 4,
                           ndimage.gaussian_filter(lum, 6) * 1.5])


def classify(rgb, k, fit=None):
    """Classes of the map's pixels; fit: the map the classes are found on (the map as exported, so a map's
    classes keep their numbers when its clean-up changes; rgb is then the clean ground)."""
    lum, feat = features(rgb)
    flat = feat.reshape(-1, feat.shape[2])
    fit_flat = flat if fit is None else features(fit)[1].reshape(-1, feat.shape[2])
    np.random.seed(1)
    centroids, _ = kmeans2(fit_flat[::13], k, seed=1, minit="++")
    labels = np.empty(flat.shape[0], np.int32)
    for start in range(0, flat.shape[0], 1 << 20):  # in chunks: the distances are k times the map
        chunk = flat[start:start + (1 << 20)]
        labels[start:start + len(chunk)] = ((chunk[:, None, :] - centroids[None]) ** 2).sum(2).argmin(1)
    labels = labels.reshape(lum.shape)
    # Smooth the classes (a vote over 5 x 5 pixels).
    votes = np.stack([ndimage.uniform_filter((labels == i).astype(np.float32), 5) for i in range(k)])
    return lum, votes.argmax(0), centroids


def textured(lum, threshold):
    """Where the surface is textured (local contrast above the threshold, smoothed): a forest's
    canopy, as opposed to the smooth floor of its clearings."""
    mean = ndimage.uniform_filter(lum, 7)
    texture = ndimage.gaussian_filter(np.sqrt(np.maximum(ndimage.uniform_filter(lum * lum, 7) - mean * mean, 0)), 3)
    square = np.ones((5, 5), bool)
    return ndimage.binary_opening(ndimage.binary_closing(texture > threshold, square), square)


def black_space(rgb):
    """Whether the map has black space wider than specks (where the stars would show)."""
    regions, count = ndimage.label(void_mask(rgb))
    return count > 0 and np.bincount(regions.ravel())[1:].max() > 100


def void_mask(rgb):
    """Black space: black pixels in areas wider than a few pixels (not a dark line or speck)."""
    black = rgb.max(2) < 0.045
    return ndimage.binary_opening(black, np.ones((5, 5), bool))


def settings(name):
    levels = json.load(open(LEVELS)) if os.path.exists(LEVELS) else {}
    return levels.get(name, {"classes": 5, "heights": {}})


_log = None


def read_ground_log(names=None):
    """The ground log (export/terrain/ground.txt, tools/terrain/ground_log.sh): its "ground:" lines by
    map, as text until a map needs them (the given maps', or all), added to those read before, and
    what the models of each sheet and first sprite cover ("groundmodel:", the renderer's; their union)."""
    global _log
    if _log is None:
        _log = {"lines": {}, "riding": {}, "models": {}, "read": set(), "all": False, "tracks": {}}
    lines, riding, models = _log["lines"], _log["riding"], {}
    wanted = set(names) - _log["read"] if names is not None else None
    if wanted is not None and not wanted:
        return
    for name in wanted if wanted is not None else ():
        lines[name] = []
    if os.path.exists(GROUND):
        with open(GROUND, errors="replace") as f:
            for line in f:
                if line.startswith("ground: "):
                    key = line[8:24]
                    if wanted is None or key in wanted:
                        lines.setdefault(key, []).append(line)
                elif line.startswith("riding: "):  # (the top enemies on background 3's map: make_cleanground.py)
                    key = line[8:24]
                    if wanted is None or key in wanted:
                        riding.setdefault(key, []).append(line)
                elif line.startswith("groundmodel: "):
                    parts = line.split()
                    if len(parts) not in (9, 11):
                        continue
                    try:
                        look, box = (int(parts[1]), int(parts[2])), [float(v) for v in parts[4:]]
                    except ValueError:
                        continue
                    if len(box) == 5:
                        box += [np.inf, -np.inf]  # (bottom and top not logged)
                    old = models.get(look, [np.inf, np.inf, -np.inf, -np.inf, 0.0, np.inf, -np.inf])
                    models[look] = [min(old[0], box[0]), min(old[1], box[1]), max(old[2], box[2]), max(old[3], box[3]),
                                    max(old[4], box[4]), min(old[5], box[5]), max(old[6], box[6])]
    _log["models"] = models
    if wanted is None:
        _log["all"] = True
    else:
        _log["read"] |= wanted


class Track:
    """One enemy's points on a map, in order: x, y (the map's pixels); where known (the log since its
    look, screen and object fields) sx, sy (where on the screen, game pixels), frame, and the object it
    is a piece of (group: the time of the event that made it + 1, 0 for launched and random enemies;
    link). look: (sheet, first sprite) or None; box: what its model covers round it (x0, y0, x1, y1,
    game pixels, from the renderer's groundmodel lines, else its sprite's size), its height, and how high
    its top is over the ground's plane before it is lifted (top; None: not known)."""

    def __init__(self, size, look, group, link):
        self.size, self.look, self.group, self.link = size, look, group, link
        self.points = []

    def finish(self, models):
        p = np.asarray(self.points, np.float32)
        self.x, self.y = p[:, 0], p[:, 1]
        self.sx = self.sy = self.frame = None
        if p.shape[1] > 2:
            self.sx, self.sy, self.frame = p[:, 2], p[:, 3], p[:, 4].astype(np.int64)
        self.standing = np.ptp(self.x) <= 10 and np.ptp(self.y) <= 10
        half = self.size / 2
        box = models.get(self.look) if self.look is not None else None
        self.modelled = box is not None
        self.box = tuple(box[:4]) if box is not None else (-half, -half * 7 / 6, half, half * 7 / 6)
        self.height = box[4] if box is not None else 2.0
        self.top = box[6] if box is not None and np.isfinite(box[6]) else None
        del self.points


def ground_tracks(name, riding=False):
    """The map's ground enemies as tracks (Track): each enemy slot's points in order, a new track where
    the slot's position jumps or its look changes (another enemy in it) or its frames start again
    (another run). riding: the top enemies riding the map (background 3's) instead."""
    if _log is None or not (_log["all"] or name in _log["read"]):
        read_ground_log([name])
    if (name, riding) in _log["tracks"]:
        return _log["tracks"][(name, riding)]
    tracks, last = [], {}
    for line in _log["riding" if riding else "lines"].get(name, []):
        parts = line.split()
        if len(parts) not in (6, 8, 10, 13):
            continue  # mixed up with another message
        try:
            v = [int(p) for p in parts[2:]]
        except ValueError:
            continue
        x, y, size, slot = v[0], v[1], v[2], v[3]
        look = (v[4], v[5]) if len(v) >= 6 else None
        extra = (v[6], v[7], v[8]) if len(v) == 11 else ()
        group, link = (v[9], v[10]) if len(v) == 11 else (None, None)
        t = last.get(slot)
        if (t is None or abs(t.points[-1][0] - x) + abs(t.points[-1][1] - y) > 40 or t.look != look or t.group != group or
                len(t.points[-1]) != 2 + len(extra) or (extra and extra[2] < t.points[-1][4])):
            t = Track(size, look, group, link)
            tracks.append(t)
            last[slot] = t
        t.points.append((x, y) + extra)
    for t in tracks:
        t.finish(_log["models"])
    _log["tracks"][(name, riding)] = tracks
    return tracks


def ground_enemies(name):
    """Where the map's ground enemies stand ((x, y, size), in its pixels) and the points they pass
    while moving over it, from the log: an enemy that stays within a few pixels stands."""
    standing, moving = [], []
    for t in ground_tracks(name):
        if t.standing:
            standing.append((float(t.x.mean()), float(t.y.mean()), t.size))
        else:
            moving.extend(zip(t.x.tolist(), t.y.tolist(), [t.size] * len(t.x)))
    return standing, moving


def footprint(shape, points, extra):
    """The pixels within each point's size (plus extra) of it."""
    mask = np.zeros(shape, bool)
    if not points:
        return mask
    pts = np.asarray(points, np.float32)
    for size in np.unique(pts[:, 2]):
        sel = pts[pts[:, 2] == size]
        xs = np.clip(np.round(sel[:, 0]).astype(int), 0, shape[1] - 1)
        ys = np.clip(np.round(sel[:, 1]).astype(int), 0, shape[0] - 1)
        centres = np.zeros(shape, bool)
        centres[ys, xs] = True
        r = int(round(size / 2 + extra))
        mask |= ndimage.maximum_filter(centres, size=2 * r + 1)
    return mask


# The 3D view's camera as the renderer fits it by default (render_gpu.c fit_camera: tilt 20, field of
# view 30, the wide playfield filling a 16:9 window, the layers over the terrain's headroom of 36): its
# height over the ground's plane and the point below it (game pixels); the ground's relief is drawn
# TERRAIN_DRAWN times as high (align_scale at its plane). Each plane is drawn enlarged about the point
# below the camera, the lower the more (render_gpu.c aligned), so a thing standing on raised ground stands
# over the terrain of a game position nearer that point than its own (stand_lift): by (its height over
# the ground's plane) / CAMERA_HEIGHT of the way; and a solid (backgrounds 2 and 3, drawn higher and
# less enlarged than a thing on the ground) stands over a thing's far side the other way.
CAMERA_HEIGHT = 426.5
CAMERA_X, CAMERA_Y = 160.0, 214.3
TERRAIN_DRAWN = 1.226
GROUND_BASE = 6.0                     # how high a ground enemy's model is placed (its layer's 4, and some)
SEEN_TOP = -90.0                      # how high up the screen ground enemies are seen (made 64 px above it)
SOLID_TOP = {2: 16.0, 3: 20.8}        # render_gpu.c solid_top, with the headroom
PLAYER_PLANE = 80.0                   # the player's plane (with the headroom), which the planes align about

PAD_MARGIN = 3       # pixels of level ground round what a standing enemy's model covers
ROAD_MARGIN = 3      # and round a moving one's, along its track
ROAD_SLOPE = 0.12    # at most this much rise per pixel on a road (rigid models on it stand flat)
ROAD_AREA = 40000    # an object whose boxes cover more of the map than this (pixels) roams (bosses): no road
ROAD_WEAVE = 1.5     # nor one whose steadiest piece turns more than this (radians a 100 pixels): it weaves
BLEND = 4.0          # pixels over which level ground blends into the terrain round it,
BLEND_PER_HEIGHT = 0.8  # and this many more for each pixel of height between them
SOLID_CLEAR = 4      # pixels a solid keeps clear round what a ground enemy's model covers
SOLID_SAME_WAY = 3   # launched or random enemies going one way so many times keep it clear too


def toward_camera(height, sx, sy):
    """How far from a thing's game position (sx, sy) the terrain drawn under it is when it stands on
    ground of this height (the ground's pixels): towards the point below the camera (dx, dy)."""
    f = (GROUND_BASE + TERRAIN_DRAWN * height + 0.05) / (CAMERA_HEIGHT + 0.05)
    return f * (CAMERA_X - np.asarray(sx, np.float32)), f * (CAMERA_Y - np.asarray(sy, np.float32))


def map_offset(tracks, width):
    """The map's x less the screen's (game x) for its enemies (the maps stand still sideways on the wide
    playfield), from the log; else as if the map's middle were the screen's."""
    diffs = np.concatenate([t.x - t.sx for t in tracks if t.sx is not None] or [np.zeros(0, np.float32)])
    return float(np.median(diffs)) if diffs.size else width / 2 - CAMERA_X


def ground_objects(tracks):
    """The tracks' objects (lists of track indices): pieces made by the level's events at one time, or
    with one link not long apart (as render_gpu.c compute_object_lifts joins them), side by side, standing
    or moving alike, are one; without the log's object fields, standing pieces side by side."""
    n = len(tracks)
    parent = list(range(n))

    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def near(a, b, slack):
        """Whether two tracks' boxes are within slack of each other at a time they share."""
        if a.standing != b.standing:
            return False
        if a.standing:
            ax, ay, bx, by = a.x.mean(), a.y.mean(), b.x.mean(), b.y.mean()
        else:
            if a.frame is None or b.frame is None:
                return False
            common = np.intersect1d(a.frame, b.frame)
            if common.size == 0:
                return False
            ia, ib = np.searchsorted(a.frame, common[0]), np.searchsorted(b.frame, common[0])
            ax, ay, bx, by = a.x[ia], a.y[ia], b.x[ib], b.y[ib]
        gap_x = max(ax + a.box[0], bx + b.box[0]) - min(ax + a.box[2], bx + b.box[2])
        gap_y = max(ay + a.box[1], by + b.box[1]) - min(ay + a.box[3], by + b.box[3])
        return gap_x <= slack and gap_y <= slack

    tagged = [i for i, t in enumerate(tracks) if t.group]
    order = sorted(tagged, key=lambda i: tracks[i].group)
    for k, i in enumerate(order):
        a = tracks[i]
        for j in order[k + 1:]:
            b = tracks[j]
            if b.group - a.group > 100:
                break
            if (a.group == b.group or (a.link and a.link == b.link)) and root(i) != root(j) and near(a, b, 4.0):
                parent[root(j)] = root(i)
    untagged = [i for i, t in enumerate(tracks) if t.group is None and t.standing]
    for k, i in enumerate(untagged):
        for j in untagged[k + 1:]:
            if root(i) != root(j) and near(tracks[i], tracks[j], 1.0):
                parent[root(j)] = root(i)
    objects = {}
    for i in range(n):
        objects.setdefault(root(i), []).append(i)
    return list(objects.values())


class Splat:
    """Heights wanted over rectangles of the map, averaged where they overlap."""

    def __init__(self, shape):
        self.sum = np.zeros(shape, np.float32)
        self.weight = np.zeros(shape, np.float32)

    def add(self, x0, y0, x1, y1, height):
        h, w = self.sum.shape
        x0, y0 = max(int(np.floor(x0)), 0), max(int(np.floor(y0)), 0)
        x1, y1 = min(int(np.ceil(x1)) + 1, w), min(int(np.ceil(y1)) + 1, h)
        if x0 < x1 and y0 < y1:
            self.sum[y0:y1, x0:x1] += height
            self.weight[y0:y1, x0:x1] += 1.0


def box_samples(h, valid, rects):
    """The terrain's heights at every other pixel of some rectangles (x0, y0, x1, y1), where it has any."""
    out = []
    H, W = h.shape
    for x0, y0, x1, y1 in rects:
        x0, y0 = max(int(round(x0)), 0), max(int(round(y0)), 0)
        x1, y1 = min(int(round(x1)) + 1, W), min(int(round(y1)) + 1, H)
        if x0 < x1 and y0 < y1:
            out.append(h[y0:y1:2, x0:x1:2][valid[y0:y1:2, x0:x1:2]])
    return np.concatenate(out) if out else np.zeros(0, np.float32)


def swept(x, y, box, margin, dx, dy):
    """What a box (x0, y0, x1, y1 round x, y, plus a margin) covers moved from where it is by up to dx, dy."""
    return (x + box[0] - margin + min(dx, 0.0), y + box[1] - margin + min(dy, 0.0),
            x + box[2] + margin + max(dx, 0.0), y + box[3] + margin + max(dy, 0.0))


def envelope(values, slope, lower):
    """The lower (or upper) envelope of values (inf, or -inf, where there are none) that rises (falls) at
    most `slope` a pixel away from them: chamfer passes down and up the rows, each row's own both ways."""
    b = values.astype(np.float32) * (1.0 if lower else -1.0)
    width = b.shape[1]
    ramp = np.arange(width, dtype=np.float32) * slope
    diagonal = slope * np.float32(1.41421356)

    def along(row):
        row = np.minimum(row, np.minimum.accumulate(row - ramp) + ramp)
        back = row[::-1]
        return np.minimum(back, np.minimum.accumulate(back - ramp) + ramp)[::-1]

    def onto(row, prev):
        near = prev + slope
        near[1:] = np.minimum(near[1:], prev[:-1] + diagonal)
        near[:-1] = np.minimum(near[:-1], prev[1:] + diagonal)
        return along(np.minimum(row, near))

    b[0] = along(b[0])
    for i in range(1, b.shape[0]):
        b[i] = onto(b[i], b[i - 1])
    for i in range(b.shape[0] - 2, -1, -1):
        b[i] = onto(b[i], b[i + 1])
    return b * (1.0 if lower else -1.0)


def object_steps(tracks):
    """A moving object's steps: the frames at which any of its pieces moved (or the points of its one
    track without frames), each piece's position and screen position then (NaN while it isn't there)."""
    if len(tracks) == 1 and tracks[0].frame is None:
        t = tracks[0]
        return [(t.x, t.y, None, None)]
    frames = np.unique(np.concatenate([t.frame for t in tracks]))
    out = []
    nan = np.float32(np.nan)
    for t in tracks:
        i = np.clip(np.searchsorted(t.frame, frames, side="right") - 1, 0, len(t.frame) - 1)
        alive = (frames >= t.frame[0]) & (frames <= t.frame[-1])
        out.append(tuple(np.where(alive, v[i], nan) for v in (t.x, t.y, t.sx, t.sy)))
    return out


def covered_area(pieces, shape):
    """How much of the map (pixels, to 4) the boxes of an object's pieces cover along their tracks."""
    cells = np.zeros(((shape[0] >> 2) + 2, (shape[1] >> 2) + 2), bool)
    for t in pieces:
        for x, y in zip(t.x.tolist(), t.y.tolist()):
            x0, y0 = max(int(x + t.box[0]) >> 2, 0), max(int(y + t.box[1]) >> 2, 0)
            cells[y0:(int(y + t.box[3]) >> 2) + 1, x0:(int(x + t.box[2]) >> 2) + 1] = True
    return int(cells.sum()) * 16


def weaving(pieces):
    """How much an object's steadiest piece turns along its track (radians a 100 pixels; pieces that
    went at least 40 pixels)."""
    least = None
    for t in pieces:
        d = np.hypot(np.diff(t.x), np.diff(t.y))
        if d.sum() < 40:
            continue
        heading = np.arctan2(np.diff(t.y), np.diff(t.x))
        turn = np.abs((np.diff(heading) + np.pi) % (2 * np.pi) - np.pi)
        w = float(turn.sum() / d.sum() * 100)
        least = w if least is None else min(least, w)
    return least or 0.0


def under_ceiling(top, ceiling):
    """How high (the ground's pixels) the ground under a thing whose top stands `top` over the ground's
    plane may be, for the thing to stay under a flat background drawn over the ground enemies at the
    height `ceiling` (its plane, with the headroom): it is lifted onto the ground and drawn the less
    enlarged the higher it stands (aligned about the player's plane)."""
    scale = top / (CAMERA_HEIGHT - PLAYER_PLANE)
    lift = (ceiling - 0.5 - CAMERA_HEIGHT * scale) / (1.0 - scale)
    return max(lift / TERRAIN_DRAWN, -4.0)


def level_under_enemies(name, h, hole, info, s):
    """The ground under its enemies (the game lifts them onto the terrain), level, so each stands flat
    and none goes through a slope or a cliff's edge. Under what stands, a pad at one height for a
    standing object (its pieces together): the median of the terrain under it as the map scrolls (its
    model's box, swept towards the point below the camera: toward_camera). Along what moves, roads: each
    place a moving piece passes takes the median of the terrain under it, the overlaps their mean, and
    all of it is made gentle (at most ROAD_SLOPE a pixel any way, as much cut as filled: envelope), so
    tracks over a cliff's edge get ramps and shallow cuttings, and tracks along one a shelf. Pads and
    roads blend into the terrain round them, over the more pixels the more they differ from it.
    Launched and random enemies (no object) get no road: their ways change from game to game; nor do
    objects that roam over much of the level (bosses) or weave about (fliers): a road would level all of
    it."""
    tracks = ground_tracks(name)
    if not tracks:
        return h, []
    valid = ~hole
    offset = map_offset(tracks, h.shape[1])
    own, pads, roads = Splat(h.shape), Splat(h.shape), Splat(h.shape)
    standing = []
    objects = ground_objects(tracks)
    for obj in objects:
        pieces = [tracks[i] for i in obj]
        if not pieces[0].standing:
            continue
        places = []
        for t in pieces:
            x, y = float(t.x.mean()), float(t.y.mean())
            sx = float(t.sx[0]) if t.sx is not None else x - offset
            places.append((t, x, y, sx))
            standing.append((x, y, t.size))
        mine = [swept(x, y, t.box, 0, 0, 0) for t, x, y, sx in places]
        under = box_samples(h, valid, mine)
        if under.size == 0:
            continue
        height = float(np.median(under))
        tops = [t.top for t in pieces if t.top is not None]
        cap = under_ceiling(max(tops), s["ceiling"]) if "ceiling" in s and tops else np.inf
        for _ in range(2):
            region = []
            for t, x, y, sx in places:
                dx, dy = toward_camera(min(height, cap), sx, SEEN_TOP)
                region.append(swept(x, y, t.box, PAD_MARGIN, float(dx), float(dy)))
            around = box_samples(h, valid, region)
            height = float(np.median(np.concatenate([around, under, under])))
        height = min(height, cap)
        for rect in region:
            pads.add(*rect, height)
        for x0, y0, x1, y1 in mine:
            own.add(x0 - PAD_MARGIN, y0 - PAD_MARGIN, x1 + PAD_MARGIN, y1 + PAD_MARGIN, height)
    for obj in objects:
        pieces = [tracks[i] for i in obj]
        if pieces[0].standing or all(t.group == 0 for t in pieces) or not s.get("roads", True):
            continue  # (launched or random: group 0)
        if covered_area(pieces, h.shape) > ROAD_AREA or weaving(pieces) > ROAD_WEAVE:
            continue  # roaming over much of the level (a boss) or weaving: a road would level all of it
        steps = object_steps(pieces)
        last = None
        for k in range(len(steps[0][0])):
            here = [(t, x[k], y[k], sx[k] if sx is not None else x[k] - offset, sy[k] if sy is not None else SEEN_TOP)
                    for t, (x, y, sx, sy) in zip(pieces, steps) if not np.isnan(x[k])]
            spot = tuple((round(float(x) / 2), round(float(y) / 2)) for _, x, y, _, _ in here)
            if spot == last:
                continue  # (where it was a moment ago)
            last = spot
            # The object's pieces at one height: the median of the terrain under all of them.
            first = box_samples(h, valid, [swept(x, y, t.box, 0, 0, 0) for t, x, y, _, _ in here])
            if first.size == 0:
                continue
            guess = float(np.median(first))
            rects = []
            for t, x, y, px, py in here:
                dx, dy = toward_camera(guess, px, py)
                rects.append(swept(x, y, t.box, 0, float(dx), float(dy)))
            under = box_samples(h, valid, rects)
            if under.size == 0:
                continue
            value = float(np.median(under))
            for x0, y0, x1, y1 in rects:
                roads.add(x0 - ROAD_MARGIN, y0 - ROAD_MARGIN, x1 + ROAD_MARGIN, y1 + ROAD_MARGIN, value)
    # Standing objects' own ground first, then theirs towards the camera, then roads.
    target = np.zeros(h.shape, np.float32)
    covered = np.zeros(h.shape, bool)
    fixed = None
    for splat in (own, pads, roads):
        new = (splat.weight > 0) & ~covered
        target[new] = splat.sum[new] / splat.weight[new]
        covered |= new
        if splat is pads:
            fixed = covered.copy()
    if not covered.any():
        return h, standing
    road = covered & ~fixed
    if road.any():
        # Gentle roads: within the area round them (the pads in it held), at most ROAD_SLOPE a pixel.
        ys, xs = np.nonzero(covered)
        pad_px = int(28.0 / ROAD_SLOPE) + 4
        y0, y1 = max(ys.min() - pad_px, 0), min(ys.max() + pad_px + 1, h.shape[0])
        x0, x1 = max(xs.min() - pad_px, 0), min(xs.max() + pad_px + 1, h.shape[1])
        part = target[y0:y1, x0:x1]
        seen = covered[y0:y1, x0:x1]
        lo = envelope(np.where(seen, part, np.inf), 2 * ROAD_SLOPE, True)
        hi = envelope(np.where(seen, part, -np.inf), 2 * ROAD_SLOPE, False)
        gentle = (lo + hi) / 2
        inner = road[y0:y1, x0:x1]
        part[inner] = gentle[inner]
    distance, (iy, ix) = ndimage.distance_transform_edt(~covered, return_indices=True)
    wanted = target[iy, ix]
    width = BLEND + BLEND_PER_HEIGHT * np.abs(wanted - h)
    keep = np.clip(1.0 - distance / width, 0.0, 1.0)
    keep = keep * keep * (3 - 2 * keep)  # (smoothly)
    return h + keep * (wanted - h), standing


def solid_clearance(name, shape, background):
    """Where a solid (background 2 or 3) keeps clear of the ground enemies under it: round what their
    models cover, and as far beyond their far sides (away from the point below the camera) as its walls
    stand over them there (it is drawn higher, so less enlarged: render_gpu.c aligned), the most when
    they are at the top of the screen. Launched and random enemies (no object) only where several go the
    same way (launched alike again and again), round their sprites as before: where one went once, it
    may go elsewhere next time, and the game hides it under the background as the solid does."""
    f = SOLID_TOP[background] / (CAMERA_HEIGHT - SOLID_TOP[background])  # (from a base on the ground: height=-4)
    mask = np.zeros(shape, bool)
    tracks = ground_tracks(name)
    if not tracks:
        return mask
    offset = map_offset(tracks, shape[1])
    H, W = shape
    # Launched and random enemies: how many of them pass each 4-pixel cell.
    ways = np.zeros(((H >> 2) + 2, (W >> 2) + 2), np.int32)
    for t in tracks:
        if t.standing or t.group != 0:
            continue
        cells = np.zeros(ways.shape, bool)
        r = t.size / 2 + SOLID_CLEAR
        for x, y in zip(t.x.tolist(), t.y.tolist()):
            cells[max(int(y - r), 0) >> 2:(int(y + r) >> 2) + 1, max(int(x - r), 0) >> 2:(int(x + r) >> 2) + 1] = True
        ways += cells
    if ways.max() >= SOLID_SAME_WAY:
        mask |= np.repeat(np.repeat(ways >= SOLID_SAME_WAY, 4, 0), 4, 1)[:H, :W]
    for t in tracks:
        if not t.standing and t.group == 0:
            continue
        xs, ys = (t.x[:1], t.y[:1]) if t.standing else (t.x, t.y)
        if t.standing:
            sx = t.sx[:1] if t.sx is not None else xs - offset
            sy = np.full(1, SEEN_TOP, np.float32)
        else:
            sx = t.sx if t.sx is not None else xs - offset
            sy = t.sy if t.sy is not None else np.full(len(xs), SEEN_TOP, np.float32)
        ex, ey = f * (sx - CAMERA_X), f * (sy - CAMERA_Y)
        last = None
        for x, y, dx, dy in zip(xs.tolist(), ys.tolist(), ex.tolist(), ey.tolist()):
            if last is not None and abs(x - last[0]) < 2 and abs(y - last[1]) < 2:
                continue
            last = (x, y)
            x0, y0, x1, y1 = swept(x, y, t.box, SOLID_CLEAR, dx, dy)
            x0, y0 = max(int(np.floor(x0)), 0), max(int(np.floor(y0)), 0)
            x1, y1 = min(int(np.ceil(x1)) + 1, W), min(int(np.ceil(y1)) + 1, H)
            if x0 < x1 and y0 < y1:
                mask[y0:y1, x0:x1] = True
    return mask


def cmd_classify(name):
    info, rgb, _ = load_map(name)
    s = settings(name)
    lum, labels, centroids = classify(rgb, s["classes"])
    standing, _ = ground_enemies(name)
    on = np.zeros(s["classes"], int)
    for x, y, _ in standing:
        if 0 <= int(y) < labels.shape[0] and 0 <= int(x) < labels.shape[1]:
            on[labels[int(y), int(x)]] += 1
    os.makedirs(REVIEW, exist_ok=True)
    h = rgb.shape[0]
    top = max(h - REVIEW_ROWS, 0)
    view = np.concatenate([rgb[top:], COLOURS[labels[top:]] * 0.65 + rgb[top:] * 0.35], 1)
    image = Image.fromarray((view * 255).astype(np.uint8)).resize((view.shape[1] // 2, view.shape[0] // 2))
    draw = ImageDraw.Draw(image)
    for x, y, _ in standing:
        if y >= top:
            px, py = (x + rgb.shape[1]) / 2, (y - top) / 2
            draw.ellipse((px - 3, py - 3, px + 3, py + 3), outline=(255, 255, 255))
    for i in range(s["classes"]):
        draw.rectangle((4, 4 + i * 16, 16, 16 + i * 16), fill=tuple(int(c * 255) for c in COLOURS[i]))
        draw.text((20, 4 + i * 16), f"{i}: {100 * (labels == i).mean():.0f}%  h={s['heights'].get(str(i), 0)}"
                  f"  stand {on[i]}", fill=(255, 255, 255))
    path = os.path.join(REVIEW, f"{name}_classes.png")
    image.save(path)
    print(f"{name} ({info.get('level', '?').strip()}): {path}; standing enemies by class {list(on)}")


def solid_heights(rgb, opaque, s):
    """Background 2 or 3 as a solid: its plane on top, rounded off at the edges, where it is clear
    a hole (the walls go down to the ground)."""
    lum = rgb @ np.array([0.299, 0.587, 0.114], np.float32)
    opaque = ndimage.binary_opening(opaque, np.ones((3, 3), bool))  # not single pixels
    inside = ndimage.distance_transform_edt(opaque)
    bevel = s.get("bevel", 4.0)
    h = -s.get("bevel_depth", 4.0) * np.clip(1 - inside / bevel, 0, 1) ** 2
    detail = ndimage.gaussian_filter(lum, 1.0) - ndimage.gaussian_filter(lum, 4.0)
    h += s.get("detail", 4.0) * detail
    return h, ~opaque


def tile_masks(rgb, info, tiles):
    """Where the map has the given tiles ({shape: height}), as {height: mask}: by the pixels of each
    shape's first place in the level's own columns, so the generated side columns' copies count too."""
    masks = {}
    tw, th = info["tile"]
    shapes = info["shapes"]
    rows, cols = len(shapes), rgb.shape[1] // tw
    cells = rgb[:rows * th, :cols * tw].reshape(rows, th, cols, tw, 3).transpose(0, 2, 1, 3, 4).reshape(rows, cols, -1)
    for shape, height in tiles.items():
        found = [(r, c) for r, row in enumerate(shapes) for c, s in enumerate(row) if s == int(shape)]
        if not found:
            continue
        r, c = found[0]
        same = (cells == cells[r, info.get("side_columns", 0) + c]).all(-1)
        mask = masks.setdefault(height, np.zeros(rgb.shape[:2], bool))
        for i, j in zip(*np.nonzero(same)):
            mask[i * th:(i + 1) * th, j * tw:(j + 1) * tw] = True
    return masks


def material_heights(rgb, labels, s):
    """Heights by material instead of by hand (generated maps: tools/content/episode6): each class
    gets the height of the material its mean colour is nearest ("materials": {"#rrggbb": height or
    "~"}); classes far from all of them take their surroundings' height."""
    refs = [(np.array([int(k[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255, v) for k, v in s["materials"].items()]
    out = {}
    for c in range(s["classes"]):
        mask = labels == c
        if not mask.any():
            continue
        mean = rgb[mask].mean(0)
        d, height = min(((float(((mean - ref) ** 2).sum()), v) for ref, v in refs), key=lambda x: x[0])
        out[str(c)] = height if d < 0.02 else "~"
    print("  classes by material:", out)
    return out


def heights(name, rgb, opaque, info, s, fit=None):
    """The heights (game pixels) and where there is nothing (holes). rgb: the clean ground; fit: the map as
    exported (its classes)."""
    if info["background"] > 1 and not s.get("ground"):
        h, hole = solid_heights(rgb, opaque, s)
        # Clear where ground enemies are under it (in the game hidden under the background): they
        # stand or move in notches and trenches rather than inside the rock.
        standing, _ = ground_enemies(name)
        hole |= solid_clearance(name, h.shape, info["background"])
        return h, hole, standing
    lum, labels, _ = classify(rgb, s["classes"], fit)
    target = np.zeros(labels.shape, np.float32)
    inherit = np.zeros(labels.shape, bool)
    class_heights = dict(s["heights"])
    if "materials" in s:
        class_heights = material_heights(rgb, labels, s)
    for c, height in class_heights.items():
        if height == "~":  # the height of the nearest other surface (rims, edges)
            inherit |= labels == int(c)
        else:
            target[labels == int(c)] = float(height)
    if "textured" in s:  # textured surface (a forest's canopy) at its own height
        canopy = textured(lum, s["textured"]["min"])
        target[canopy] = float(s["textured"]["height"])
        inherit &= ~canopy
    for height, where in tile_masks(rgb, info, s.get("tiles", {})).items():
        where &= (target != 0) | inherit  # the tile's own surfaces, not the plain ground round them
        if height == "~":
            inherit |= where
        else:
            target[where] = float(height)
            inherit &= ~where
    hole = np.zeros(labels.shape, bool)
    if "void" in s:
        space = void_mask(rgb)
        if s["void"] == "hole":  # nothing there: chasms with walls down into the dark
            hole = space
        else:
            target[space] = float(s["void"])
        inherit &= ~space
    if inherit.any():
        _, (iy, ix) = ndimage.distance_transform_edt(inherit, return_indices=True)
        target = target[iy, ix]
    # Slopes and cliffs: the classes' heights softened a little; the surface's own detail on top,
    # more of it on raised ground.
    h = ndimage.gaussian_filter(target, s.get("softness", 2.5))
    if s.get("rolling"):  # gentle hills and hollows (the same every run)
        rng = np.random.default_rng(int(name[:8], 16))
        noise = ndimage.gaussian_filter(rng.standard_normal(h.shape).astype(np.float32), 28, mode="wrap")
        h += s["rolling"] * noise / (np.abs(noise).max() + 1e-6)
    detail = ndimage.gaussian_filter(lum, 1.0) - ndimage.gaussian_filter(lum, 4.0)
    h += s.get("detail", 5.0) * detail * (0.5 + np.clip(h / 30.0, 0, 1))
    if hole.any():
        # The platforms' edges rounded off down into the chasms, as rocks' are.
        inside = ndimage.distance_transform_edt(~hole)
        rim = s.get("rim", 6.0)
        h -= s.get("rim_depth", 8.0) * np.clip(1 - inside / rim, 0, 1) ** 2

    h, standing = level_under_enemies(name, h, hole, info, s)
    return h, hole, standing


def relief_image(rgb, h, hole, standing, top, tracks=()):
    """The map lit by its terrain from the top left, deeper ground darker, holes blue-black,
    standing enemies ringed, the tracks of moving ones drawn (cyan; launched and random ones grey)."""
    h = np.where(hole, -TERRAIN_MAX, h)[top:]
    gy, gx = np.gradient(h)
    light = np.clip(1.0 + (-gx - gy) * 0.18, 0.35, 1.6)
    depth = np.clip(1.0 + h / 80.0, 0.35, 1.3)
    image = np.clip(rgb[top:] * (light * depth)[..., None], 0, 1)
    image[hole[top:]] = (0.05, 0.05, 0.12)
    out = Image.fromarray((image * 255).astype(np.uint8))
    draw = ImageDraw.Draw(out)
    for t in tracks:
        if not t.standing and t.y.max() >= top:
            colour = (150, 150, 150) if t.group == 0 else (0, 230, 255)
            draw.line(list(zip(t.x.tolist(), (t.y - top).tolist())), fill=colour)
    for x, y, _ in standing:
        if y >= top:
            draw.ellipse((x - 6, y - 6 - top, x + 6, y + 6 - top), outline=(255, 255, 0), width=2)
    return out.resize((out.width // 2, out.height // 2))


def cmd_build(name):
    info, exported, opaque = load_map(name)
    rgb = cleaned(name, exported) if info["background"] == 1 else exported  # (the clean ground, make_cleanground.py)
    s = settings(name)
    if info["background"] > 1 and not s.get("solid") and not s.get("ground"):
        return  # (an entry for its plants only: make_vegetation.py)
    h, hole, standing = heights(name, rgb, opaque, info, s, None if rgb is exported else exported)
    # Samples every SAMPLE pixels, at the samples' corners (the grid the game builds meshes on).
    grid = np.pad(h[::SAMPLE, ::SAMPLE], ((0, 1), (0, 1)), mode="edge")
    holes = np.pad(hole[::SAMPLE, ::SAMPLE], ((0, 1), (0, 1)), mode="edge")
    data = np.clip(np.round(grid), -TERRAIN_MAX, TERRAIN_MAX).astype(np.int8)
    data[holes] = HOLE
    os.makedirs(OUT, exist_ok=True)
    # Version 2: the stars (on the levels with them) show only through the holes, so the game shows
    # the terrain over them; also a ground with relief and no black space for them to show on, only
    # specks (MINERS, ** ALE **; a flat one leaves the game its relief by tiles there).
    covers = info["background"] == 1 and np.abs(grid).max() > 3 and not black_space(rgb)
    version = 2 if holes.any() or covers else 1
    header = struct.pack("<4sIIIII", b"TYTR", version, data.shape[1], data.shape[0], SAMPLE, info["side_columns"])
    with open(os.path.join(OUT, f"{name}.ter"), "wb") as f:
        f.write(header + zlib.compress(data.tobytes(), 9))
    os.makedirs(REVIEW, exist_ok=True)
    relief_image(rgb, h, hole, standing, max(rgb.shape[0] - REVIEW_ROWS, 0), ground_tracks(name)).save(
        os.path.join(REVIEW, f"{name}_relief.png"))
    surface = data[~holes]
    print(f"{name} ({info.get('level', '?').strip()} bg{info['background']}): {data.shape[1]} x {data.shape[0]} samples, "
          f"heights {surface.min() if surface.size else 0}..{surface.max() if surface.size else 0}, "
          f"{100 * holes.mean():.0f}% holes, {len(standing)} standing enemies")


def cmd_sheets():
    """The built reliefs four to a sheet (export/terrain/sheets/relief_NN.png), by level name."""
    levels = json.load(open(LEVELS))
    names = sorted((v.get("level", "?").strip(), k) for k, v in levels.items()
                   if os.path.exists(os.path.join(REVIEW, f"{k}_relief.png")))
    os.makedirs(os.path.join(REVIEW, "sheets"), exist_ok=True)
    for n in range(0, len(names), 4):
        images = [(level, key, Image.open(os.path.join(REVIEW, f"{key}_relief.png"))) for level, key in names[n:n + 4]]
        width = sum(i.width for _, _, i in images) + 8 * len(images)
        height = max(i.height for _, _, i in images) + 18
        sheet = Image.new("RGB", (width, height), (20, 20, 24))
        draw = ImageDraw.Draw(sheet)
        x = 0
        for level, key, image in images:
            sheet.paste(image, (x, 18))
            draw.text((x + 4, 3), f"{level} {key[:6]}", fill=(255, 230, 80))
            x += image.width + 8
        sheet.save(os.path.join(REVIEW, "sheets", f"relief_{n // 4:02d}.png"))
    print(f"{(len(names) + 3) // 4} sheets")


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "sheets":
        cmd_sheets()
        return 0
    if len(sys.argv) < 3 or sys.argv[1] not in ("classify", "build"):
        print(__doc__)
        return 1
    names = sys.argv[2:]
    if names == ["all"]:
        names = sorted(json.load(open(LEVELS)).keys())
    read_ground_log(names)  # (the log in one pass for all of them)
    for name in names:
        (cmd_classify if sys.argv[1] == "classify" else cmd_build)(name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
