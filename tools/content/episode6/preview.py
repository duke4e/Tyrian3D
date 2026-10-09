"""Pictures of maps and tiles' materials, for designing episode 6 (needs numpy and PIL)."""
import os

import numpy as np
from PIL import Image

DATA = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "tyrian2000"))
_tiles = {}


def palette(index=5):
    """A palette of palette.dat (5: the levels')."""
    d = open(os.path.join(DATA, "palette.dat"), "rb").read()[index * 768:(index + 1) * 768]
    return np.array([[min(255, v * 4) for v in d[i * 3:i * 3 + 3]] for i in range(256)], dtype=np.uint8)


def tiles(letter):
    """shapesX.dat: shape number -> 28x24 palette indices (None for blank ones)."""
    if letter not in _tiles:
        data = open(os.path.join(DATA, f"shapes{letter}.dat"), "rb").read()
        o, out = 0, {}
        for z in range(600):
            if o >= len(data):
                break
            blank = data[o]
            o += 1
            if blank:
                out[z + 1] = None
            else:
                out[z + 1] = np.frombuffer(data[o:o + 24 * 28], dtype=np.uint8).reshape(28, 24)
                o += 24 * 28
        _tiles[letter] = out
    return _tiles[letter]


def materials(letter, references, used):
    """Each tile's share of pixels nearest each reference colour (name -> RGB)."""
    pal = palette().astype(float)
    t = tiles(letter)
    names = list(references)
    ref = np.array([references[n] for n in names], dtype=float)
    out = {}
    for s in used:
        img = t.get(s)
        if img is None:
            # A blank tile (space): all of the material named "space", if there is one.
            out[s] = {n: (1.0 if n == "space" else 0.0) for n in names}
            continue
        rgb = pal[img.reshape(-1)]
        nearest = ((rgb[:, None, :] - ref[None, :, :]) ** 2).sum(axis=2).argmin(axis=1)
        share = np.bincount(nearest, minlength=len(names)) / len(nearest)
        out[s] = {n: float(share[i]) for i, n in enumerate(names)}
    return out


def picture(layers, letter):
    """The layers drawn over each other (blank tiles see through), as an RGB image."""
    pal = palette()
    t = tiles(letter)
    h, w = len(layers[0]), max(len(layers[0][0]), *(len(l[0]) for l in layers))
    img = np.zeros((h * 28, w * 24), dtype=np.uint8)
    for k, layer in enumerate(layers):
        rows = len(layer)
        scale = rows // h  # layers 2 and 3 have twice the rows (they scroll slower)
        for y in range(0, rows, max(1, scale)):
            for x in range(len(layer[0])):
                s = t.get(layer[y][x])
                if s is None:
                    continue
                yy = (y // max(1, scale)) * 28
                region = img[yy:yy + 28, x * 24:(x + 1) * 24]
                if k == 0:
                    region[:] = s
                else:
                    mask = s != 0
                    region[mask] = s[mask]
    return Image.fromarray(pal[img])


def strips(image, path, count=4, scale=0.4):
    """A tall map as count strips side by side (the top of the map at the left strip's top)."""
    h = image.height // count
    out = Image.new("RGB", (image.width * count + 10 * (count - 1), h), (255, 255, 255))
    for i in range(count):
        out.paste(image.crop((0, i * h, image.width, (i + 1) * h)), (i * (image.width + 10), 0))
    out.resize((int(out.width * scale), int(out.height * scale))).save(path)
