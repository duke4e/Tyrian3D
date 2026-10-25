#!/usr/bin/env python3
"""Puts pictures drawn anew (pic_NN.png and tshp2.png, from TYR3D_EXPORT_PICTURES' export, redrawn in the same
frame at any size) where the game finds them: data/hd/pictures, as RGB (a picture with alpha laid on black, as the
originals' empty parts are: what image generators leave behind there doesn't show).
usage: <python with PIL> tools/hd_pictures.py <dir with the new pictures> [data/hd/pictures]
"""
import glob
import os
import re
import sys

from PIL import Image


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    src = sys.argv[1]
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dst = sys.argv[2] if len(sys.argv) > 2 else os.path.join(root, "data", "hd", "pictures")
    os.makedirs(dst, exist_ok=True)
    for path in sorted(glob.glob(os.path.join(src, "*.png"))):
        name = os.path.basename(path)
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
