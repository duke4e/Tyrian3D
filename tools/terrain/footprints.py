#!/usr/bin/env python3
"""What the ground enemies' models cover of the ground, seen from straight above: per look (models.cfg's
sprite rules: a sheet letter and the first sprite), the model's triangles turned and scaled as the renderer
turns them (render_gpu.c object_transform: the look's yaw, the model's own yaw, pitch and roll, its size,
centred unless drawn at its own origin), projected onto the ground and rasterized at a pixel. Two masks: all
of it, and its low part (triangles reaching below LOW pixels over the model's lowest point: what grass blades
would poke through). For make_vegetation.py (plants kept off the models' real footprints) and
make_cleanground.py (the art a model stands on).

usage: <python with numpy and PIL> tools/terrain/footprints.py check   (the boxes against the renderer's
       groundmodel lines in export/terrain/ground.txt)
"""
import json
import math
import os
import struct
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODELS = os.path.join(ROOT, "assets", "models")
LOW = 7.0          # game pixels over the model's lowest point: its low part
SUPERSAMPLE = 2

_cfg = None
_glb = {}
_prints = {}


def sheet_letter(text):
    """A models.cfg sheet: a letter, coins, powerups, or x<hex> for a symbol."""
    if len(text) == 3 and text[0] == "x":
        try:
            return chr(int(text[1:], 16))
        except ValueError:
            pass
    return {"coins": "$", "powerups": "+"}.get(text, text).lower()


def models_cfg():
    """(rules {(letter, sprite): (appearance, options)}, models {name: dict}, frames {(letter, sprite): model})."""
    global _cfg
    if _cfg is not None:
        return _cfg
    rules, models, frames = {}, {}, {}
    for line in open(os.path.join(MODELS, "models.cfg")):
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        p = line.split()
        if p[0] == "model" and len(p) >= 3:
            nums, origin = [], False
            for t in p[3:]:
                if t == "origin":
                    origin = True
                else:
                    try:
                        nums.append(float(t))
                    except ValueError:
                        pass
            nums += [0.0] * (4 - len(nums))
            models[p[1]] = dict(file=p[2], size=nums[0], yaw=nums[1], pitch=nums[2], roll=nums[3], origin=origin)
        elif p[0] == "sprite" and len(p) >= 4:
            try:
                key = (sheet_letter(p[1]), int(p[2]))
            except ValueError:
                continue
            opts = {}
            for t in p[4:]:
                k, _, v = t.partition("=")
                opts[k] = v if _ else True
            rules.setdefault(key, (p[3], opts))
        elif p[0] == "frame" and len(p) >= 4:
            try:
                frames[(sheet_letter(p[1]), int(p[2]))] = p[3]
            except ValueError:
                pass
    _cfg = (rules, models, frames)
    return _cfg


def read_glb(path):
    """A GLB's triangles with the scene's node transforms applied: (points N x 3, triangles M x 3)."""
    if path in _glb:
        return _glb[path]
    raw = open(path, "rb").read()
    magic, version, length = struct.unpack_from("<4sII", raw, 0)
    o = 12
    doc, binary = None, b""
    while o < length:
        size, kind = struct.unpack_from("<I4s", raw, o)
        chunk = raw[o + 8:o + 8 + size]
        if kind == b"JSON":
            doc = json.loads(chunk.decode("utf-8"))
        elif kind == b"BIN\x00":
            binary = chunk
        o += 8 + size
    comps = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}
    types = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}

    def accessor(i):
        a = doc["accessors"][i]
        view = doc["bufferViews"][a["bufferView"]]
        dtype = np.dtype(types[a["componentType"]])
        n, k = a["count"], comps[a["type"]]
        start = view.get("byteOffset", 0) + a.get("byteOffset", 0)
        stride = view.get("byteStride", 0) or dtype.itemsize * k
        buf = np.frombuffer(binary, np.uint8, count=stride * (n - 1) + dtype.itemsize * k, offset=start)
        rows = np.lib.stride_tricks.as_strided(buf, shape=(n, dtype.itemsize * k), strides=(stride, 1))
        return np.ascontiguousarray(rows).view(dtype).reshape(n, k)

    def local(node):
        if "matrix" in node:
            return np.array(node["matrix"], np.float64).reshape(4, 4).T
        m = np.eye(4)
        t = node.get("translation", [0, 0, 0])
        q = node.get("rotation", [0, 0, 0, 1])
        s = node.get("scale", [1, 1, 1])
        x, y, z, w = q
        r = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                      [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                      [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
        m[:3, :3] = r * np.array(s)[None, :]
        m[:3, 3] = t
        return m

    points, tris = [], []
    base = 0

    def walk(i, parent):
        nonlocal base
        node = doc["nodes"][i]
        m = parent @ local(node)
        if "mesh" in node:
            for prim in doc["meshes"][node["mesh"]]["primitives"]:
                if prim.get("mode", 4) != 4 or "POSITION" not in prim["attributes"]:
                    continue
                pos = accessor(prim["attributes"]["POSITION"]).astype(np.float64)
                with np.errstate(all="ignore"):  # (Accelerate's matmul warns for nothing)
                    pos = (np.c_[pos, np.ones(len(pos))] @ m.T)[:, :3]
                idx = accessor(prim["indices"]).reshape(-1) if "indices" in prim else np.arange(len(pos))
                points.append(pos)
                tris.append(idx.reshape(-1, 3).astype(np.int64) + base)
                base += len(pos)
        for c in node.get("children", []):
            walk(c, m)

    scene = doc["scenes"][doc.get("scene", 0)]
    for n in scene["nodes"]:
        walk(n, np.eye(4))
    out = (np.concatenate(points) if points else np.zeros((0, 3)), np.concatenate(tris) if tris else np.zeros((0, 3), np.int64))
    _glb[path] = out
    return out


def rot(axis, degrees):
    """render_gpu.c mat4_rotation as a 3 x 3 matrix acting on column vectors."""
    a = math.radians(degrees)
    c, s = math.cos(a), math.sin(a)
    i, j = (axis + 1) % 3, (axis + 2) % 3
    r = np.eye(3)
    r[i, i] = c
    r[j, i] = s   # (column i, row j)... m[i * 4 + j] = s is column i, row j
    r[i, j] = -s
    r[j, j] = c
    return r


def look_yaws(opts):
    """The headings a look is drawn at (degrees): its yaw option; turning ones all round."""
    yaw = opts.get("yaw", "180")
    if isinstance(yaw, str) and yaw.startswith("frames"):
        n = int(yaw.split(":")[1]) if ":" in yaw else 8
        return [360.0 * k / n for k in range(n)]
    if yaw in ("velocity", "aim"):
        return [45.0 * k for k in range(8)]
    try:
        return [float(yaw)]
    except (TypeError, ValueError):
        return [180.0]


def placed(model_name, yaw):
    """The model's points as the renderer turns and centres them (object_transform without its position):
    x right, y up, z down the screen; and its triangles."""
    rules, models, frames = models_cfg()
    m = models[model_name]
    pts, tris = read_glb(os.path.join(MODELS, m["file"]))
    if len(pts) == 0:
        return pts, tris
    lo, hi = pts.min(0), pts.max(0)
    centre = (lo + hi) / 2
    footprint = max(hi[0] - lo[0], hi[2] - lo[2])
    scale = m["size"] / footprint if m["size"] > 0 and footprint > 0 else 1.0
    t = np.array([-centre[0] if m["size"] > 0 else 0.0, 0.0 if m["origin"] else -centre[1], -centre[2] if m["size"] > 0 else 0.0])
    r = rot(1, -yaw) @ rot(1, m["yaw"]) @ rot(0, m["pitch"]) @ rot(2, m["roll"])
    with np.errstate(all="ignore"):
        return ((pts + t) * scale) @ r.T, tris


def model_of(letter, sprite):
    rules, models, frames = models_cfg()
    app, opts = rules.get((letter, sprite), (None, {}))
    return (app, opts) if app in models else (None, opts)


def box(letter, sprite):
    """The footprint box as the renderer logs it (its bounds' corners turned): x0, y0, x1, y1, height."""
    name, opts = model_of(letter, sprite)
    if name is None:
        return None
    rules, models, frames = models_cfg()
    pts, _ = read_glb(os.path.join(MODELS, models[name]["file"]))
    lo, hi = pts.min(0), pts.max(0)
    corners = np.array([[lo[0] if k & 1 == 0 else hi[0], lo[1] if k & 2 == 0 else hi[1], lo[2] if k & 4 == 0 else hi[2]]
                        for k in range(8)])
    out = None
    for yaw in look_yaws(opts)[:1]:
        m = models[name]
        centre = (lo + hi) / 2
        fp = max(hi[0] - lo[0], hi[2] - lo[2])
        scale = m["size"] / fp if m["size"] > 0 and fp > 0 else 1.0
        t = np.array([-centre[0] if m["size"] > 0 else 0.0, 0.0 if m["origin"] else -centre[1], -centre[2] if m["size"] > 0 else 0.0])
        r = rot(1, -yaw) @ rot(1, m["yaw"]) @ rot(0, m["pitch"]) @ rot(2, m["roll"])
        with np.errstate(all="ignore"):
            c = ((corners + t) * scale) @ r.T
        out = (c[:, 0].min(), c[:, 2].min(), c[:, 0].max(), c[:, 2].max(), c[:, 1].max() - c[:, 1].min())
    return out


def footprint(letter, sprite, frames=()):
    """(full, low, x0, y0): masks (rows: game y, columns: game x, a pixel each) of what the look's model covers
    seen from above, all of it and its low part, their top left (x0, y0) relative to the object's centre; None
    for a look without a model. frames: the sprites of its animation (their frame models join in); a look
    that spins (spin=) is taken all round."""
    key = (letter, sprite, tuple(frames))
    if key in _prints:
        return _prints[key]
    name, opts = model_of(letter, sprite)
    if name is None:
        _prints[key] = None
        return None
    rules, models, frame_models = models_cfg()
    names = [name] + sorted({frame_models[(letter, f)] for f in frames if (letter, f) in frame_models} - {name})
    yaws = look_yaws(opts)
    if "spin" in opts:
        yaws = [y + 45.0 * k for y in yaws[:1] for k in range(8)]
    S = SUPERSAMPLE
    results = []
    for n in names:
        if n not in models:
            continue
        for yaw in yaws:
            pts, tris = placed(n, yaw)
            if len(tris) == 0:
                continue
            results.append((pts, tris))
    if not results:
        _prints[key] = None
        return None
    allp = np.concatenate([p for p, _ in results])
    x0, y0 = int(math.floor(allp[:, 0].min())) - 1, int(math.floor(allp[:, 2].min())) - 1
    x1, y1 = int(math.ceil(allp[:, 0].max())) + 1, int(math.ceil(allp[:, 2].max())) + 1
    w, h = (x1 - x0) * S, (y1 - y0) * S
    full = Image.new("1", (w, h), 0)
    low = Image.new("1", (w, h), 0)
    df, dl = ImageDraw.Draw(full), ImageDraw.Draw(low)
    for pts, tris in results:
        bottom = pts[:, 1].min()
        xy = np.c_[(pts[:, 0] - x0) * S, (pts[:, 2] - y0) * S]
        lowest = pts[tris, 1].min(1) - bottom
        for t, l in zip(tris, lowest):
            poly = [tuple(xy[k]) for k in t]
            df.polygon(poly, fill=1)
            if l < LOW:
                dl.polygon(poly, fill=1)
    def down(img):
        a = np.asarray(img, bool).reshape(h // S, S, w // S, S)
        return a.any(axis=(1, 3))
    _prints[key] = (down(full), down(low), x0, y0)
    return _prints[key]


def stamp(mask, fp, x, y, which="full", grow=0):
    """Marks a footprint on a map-sized mask at the object's centre (x, y)."""
    if fp is None:
        return
    full, low, x0, y0 = fp
    m = full if which == "full" else low
    if grow:
        from scipy import ndimage
        m = ndimage.binary_dilation(np.pad(m, grow), iterations=grow)
        x0, y0 = x0 - grow, y0 - grow
    H, W = mask.shape
    ax, ay = int(round(x)) + x0, int(round(y)) + y0
    sx0, sy0 = max(ax, 0), max(ay, 0)
    sx1, sy1 = min(ax + m.shape[1], W), min(ay + m.shape[0], H)
    if sx1 > sx0 and sy1 > sy0:
        mask[sy0:sy1, sx0:sx1] |= m[sy0 - ay:sy1 - ay, sx0 - ax:sx1 - ax]


def check():
    """Our boxes against the renderer's (groundmodel lines): how many looks agree to half a pixel."""
    logged = {}
    with open(os.path.join(ROOT, "export", "terrain", "ground.txt"), errors="replace") as f:
        for line in f:
            if not line.startswith("groundmodel: "):
                continue
            p = line.split()
            try:
                logged[(int(p[1]), int(p[2]))] = [float(v) for v in p[4:9]]
            except (ValueError, IndexError):
                pass
    good, bad = 0, []
    for (sheet, sprite), b in logged.items():
        letter = chr(sheet).lower()
        ours = box(letter, sprite)
        if ours is None:
            continue
        d = max(abs(ours[0] - b[0]), abs(ours[1] - b[1]), abs(ours[2] - b[2]), abs(ours[3] - b[3]))
        if d <= 0.6:
            good += 1
        else:
            bad.append((letter, sprite, model_of(letter, sprite)[0], [round(v, 1) for v in ours[:4]], [round(v, 1) for v in b[:4]]))
    print(f"{good} looks agree, {len(bad)} differ")
    for row in bad[:40]:
        print(" ", row)
    return 0 if not bad else 1


if __name__ == "__main__":
    if sys.argv[1:] == ["check"]:
        sys.exit(check())
    print(__doc__)
