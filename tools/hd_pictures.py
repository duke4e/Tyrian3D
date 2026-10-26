#!/usr/bin/env python3
"""Puts pictures drawn anew (pic_NN.png and tshp2.png, from TYR3D_EXPORT_PICTURES' export, redrawn in the same
frame at any size) where the game finds them: data/hd/pictures, as RGB (a picture with alpha laid on black, as the
originals' empty parts are: what image generators leave behind there doesn't show).

The data cubes' faces drawn anew (face_NN.png, any size, square or not, clear round the figure) are fitted into the
store's portrait window: the export's face_frame.png (the frame where the store draws it, its window clear; in the
pictures' folder or given with --frame) gives the window, the face covers it (as large as it takes, centred on it)
and is cut to its shape with a soft edge. Each goes to data/hd/pictures/face_NN.png over the whole portrait (screen
pixels FRAME_BOX at FACE_SCALE times, clear but for the window), as the game draws it (render_gpu.c find_hd_face).
usage: <python with PIL> tools/hd_pictures.py <dir with the new pictures> [data/hd/pictures] [--frame face_frame.png]
"""
import glob
import os
import re
import sys

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

FRAME_BOX = (1, 1, 146, 171)  # the store's portrait in screen pixels (x0, y0, x1, y1): game_menu.c fills and frames it
FACE_CENTRE = (77, 92)        # where the store centres a face (game_menu.c)
FACE_SCALE = 6                # output pixels per screen pixel


def face_window(frame_path):
    """The portrait window as a mask over FRAME_BOX: the frame's clear pixels joined to the face's centre."""
    frame = np.array(Image.open(frame_path).convert("RGBA"))
    clear = frame[..., 3] == 0
    labels, _ = ndimage.label(clear)
    window = labels == labels[FACE_CENTRE[1], FACE_CENTRE[0]]
    x0, y0, x1, y1 = FRAME_BOX
    return window[y0:y1, x0:x1]


def bake_face(face, window):
    """The face over the portrait, cut to the window's shape."""
    k = FACE_SCALE
    bh, bw = window.shape
    ys, xs = np.nonzero(window)
    wx0, wx1, wy0, wy1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    # As large as it takes to cover the window, centred on it.
    face = face.convert("RGBA")
    scale = max((wx1 - wx0) * k / face.width, (wy1 - wy0) * k / face.height)
    fw, fh = round(face.width * scale), round(face.height * scale)
    face = face.resize((fw, fh), Image.LANCZOS)
    out = Image.new("RGBA", (bw * k, bh * k), (0, 0, 0, 0))
    out.alpha_composite(face, (round((wx0 + wx1) * k / 2 - fw / 2), round((wy0 + wy1) * k / 2 - fh / 2)))
    # The window's shape, its edge soft over about half a screen pixel.
    mask = Image.fromarray((window * 255).astype(np.uint8)).resize((bw * k, bh * k), Image.BILINEAR)
    mask = mask.filter(ImageFilter.GaussianBlur(k * 0.25))
    alpha = np.array(out)[..., 3].astype(np.float32) * (np.array(mask).astype(np.float32) / 255)
    out.putalpha(Image.fromarray(alpha.round().astype(np.uint8)))
    return out


def main():
    args = [a for a in sys.argv[1:]]
    frame = None
    if "--frame" in args:
        i = args.index("--frame")
        frame = args[i + 1]
        del args[i:i + 2]
    if not args:
        sys.exit(__doc__)
    src = args[0]
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dst = args[1] if len(args) > 1 else os.path.join(root, "data", "hd", "pictures")
    os.makedirs(dst, exist_ok=True)
    frame = frame or os.path.join(src, "face_frame.png")
    window = None
    for path in sorted(glob.glob(os.path.join(src, "*.png"))):
        name = os.path.basename(path)
        if re.fullmatch(r"face_\d\d\.png", name):
            if window is None:
                if not os.path.exists(frame):
                    sys.exit(f"{name}: no {frame} (TYR3D_EXPORT_PICTURES writes it)")
                window = face_window(frame)
            bake_face(Image.open(path), window).save(os.path.join(dst, name))
            print(name, "fitted to the portrait window")
            continue
        if not re.fullmatch(r"pic_\d\d\.png|tshp2\.png", name):
            continue
        im = Image.open(path)
        if im.mode in ("RGBA", "LA", "P"):
            im = im.convert("RGBA")
            black = Image.new("RGBA", im.size, (0, 0, 0, 255))
            im = Image.alpha_composite(black, im)
        im.convert("RGB").save(os.path.join(dst, name))
        print(name, im.size)


if __name__ == "__main__":
    main()
