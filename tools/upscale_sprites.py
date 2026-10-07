#!/usr/bin/env python3
"""Upscales the sprite atlases with ESRGAN models (plan M5.1).

usage: <python with torch> tools/upscale_sprites.py <model.pth> <in> <out dir> [--prescale N] [--tile T]

<in> is a PNG or a directory of them (upscale/in from tools/make_atlases.py). Each picture is
upscaled 4x by the model (ESRGAN "old" or "new" key layout, e.g. from https://openmodeldb.info)
and written to <out dir> under the same name, with alpha:

- Colour: transparent pixels take the colour of the nearest opaque pixel first, so the model sees
  no black fringe around the sprites.
- Alpha: run through the model as a grey picture, so the outline follows the upscaled shapes.

--prescale N enlarges the input N times (nearest) before the model and scales the result back to
4x (Lanczos), for models trained on "large pixels". Runs on Apple's GPU (MPS) when it can.
"""
import argparse
import math
import os
import sys

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image


# --- RRDBNet (ESRGAN) -----------------------------------------------------------------------

class RDB(nn.Module):
    def __init__(self, nf, gc):
        super().__init__()
        self.conv1 = nn.Conv2d(nf, gc, 3, 1, 1)
        self.conv2 = nn.Conv2d(nf + gc, gc, 3, 1, 1)
        self.conv3 = nn.Conv2d(nf + 2 * gc, gc, 3, 1, 1)
        self.conv4 = nn.Conv2d(nf + 3 * gc, gc, 3, 1, 1)
        self.conv5 = nn.Conv2d(nf + 4 * gc, nf, 3, 1, 1)

    def forward(self, x):
        lrelu = lambda t: F.leaky_relu(t, 0.2)
        x1 = lrelu(self.conv1(x))
        x2 = lrelu(self.conv2(torch.cat((x, x1), 1)))
        x3 = lrelu(self.conv3(torch.cat((x, x1, x2), 1)))
        x4 = lrelu(self.conv4(torch.cat((x, x1, x2, x3), 1)))
        x5 = self.conv5(torch.cat((x, x1, x2, x3, x4), 1))
        return x5 * 0.2 + x


class RRDB(nn.Module):
    def __init__(self, nf, gc):
        super().__init__()
        self.rdb1, self.rdb2, self.rdb3 = RDB(nf, gc), RDB(nf, gc), RDB(nf, gc)

    def forward(self, x):
        return self.rdb3(self.rdb2(self.rdb1(x))) * 0.2 + x


class RRDBNet(nn.Module):
    def __init__(self, nf=64, nb=23, gc=32):
        super().__init__()
        self.conv_first = nn.Conv2d(3, nf, 3, 1, 1)
        self.body = nn.Sequential(*[RRDB(nf, gc) for _ in range(nb)])
        self.conv_body = nn.Conv2d(nf, nf, 3, 1, 1)
        self.conv_up1 = nn.Conv2d(nf, nf, 3, 1, 1)
        self.conv_up2 = nn.Conv2d(nf, nf, 3, 1, 1)
        self.conv_hr = nn.Conv2d(nf, nf, 3, 1, 1)
        self.conv_last = nn.Conv2d(nf, 3, 3, 1, 1)

    def forward(self, x):
        lrelu = lambda t: F.leaky_relu(t, 0.2)
        feat = self.conv_first(x)
        feat = feat + self.conv_body(self.body(feat))
        feat = lrelu(self.conv_up1(F.interpolate(feat, scale_factor=2, mode="nearest")))
        feat = lrelu(self.conv_up2(F.interpolate(feat, scale_factor=2, mode="nearest")))
        return self.conv_last(lrelu(self.conv_hr(feat)))


def new_keys(sd):
    """The original ESRGAN key names ("model.N...") as the new ones."""
    if "conv_first.weight" in sd:
        return sd
    out = {}
    fixed = {"model.0": "conv_first", "model.1.sub.%d": "conv_body", "model.3": "conv_up1",
             "model.6": "conv_up2", "model.8": "conv_hr", "model.10": "conv_last"}
    nb = 1 + max(int(k.split(".")[3]) for k in sd if k.startswith("model.1.sub.") and "RDB" in k)
    for k, v in sd.items():
        parts = k.split(".")
        if k.startswith("model.1.sub.") and "RDB" in k:
            # model.1.sub.<b>.RDB<r>.conv<c>.0.<weight|bias>
            out["body.%s.rdb%s.%s.%s" % (parts[3], parts[4][3:], parts[5], parts[7])] = v
        elif k.startswith("model.1.sub.%d." % nb):
            out["conv_body." + parts[-1]] = v
        else:
            prefix = ".".join(parts[:2])
            out[fixed[prefix] + "." + parts[-1]] = v
    return out


def load_model(path, device):
    sd = torch.load(path, map_location="cpu", weights_only=True)
    for key in ("params_ema", "params"):
        if key in sd:
            sd = sd[key]
    sd = new_keys(sd)
    nf = sd["conv_first.weight"].shape[0]
    nb = 1 + max(int(k.split(".")[1]) for k in sd if k.startswith("body."))
    gc = sd["body.0.rdb1.conv1.weight"].shape[0]
    model = RRDBNet(nf, nb, gc)
    model.load_state_dict(sd, strict=True)
    return model.eval().to(device)


# --- Pictures -------------------------------------------------------------------------------

def run(model, device, rgb, tile, pad=16):
    """rgb: float32 HxWx3 in 0..1. Upscaled 4x in tiles with overlap."""
    h, w = rgb.shape[:2]
    out = np.zeros((h * 4, w * 4, 3), np.float32)
    for y0 in range(0, h, tile):
        for x0 in range(0, w, tile):
            y1, x1 = min(y0 + tile, h), min(x0 + tile, w)
            ya, xa = max(y0 - pad, 0), max(x0 - pad, 0)
            yb, xb = min(y1 + pad, h), min(x1 + pad, w)
            t = torch.from_numpy(rgb[ya:yb, xa:xb].transpose(2, 0, 1).copy())[None].to(device)
            with torch.no_grad():
                r = model(t)[0].clamp(0, 1).cpu().numpy().transpose(1, 2, 0)
            out[y0 * 4:y1 * 4, x0 * 4:x1 * 4] = r[(y0 - ya) * 4:(y1 - ya) * 4, (x0 - xa) * 4:(x1 - xa) * 4]
    return out


def bleed(rgb, alpha):
    """Transparent pixels take the colour of the nearest opaque one (a few passes of dilation)."""
    rgb = rgb.copy()
    known = alpha > 0.5
    for _ in range(64):
        if known.all():
            break
        acc = np.zeros_like(rgb)
        cnt = np.zeros(known.shape, np.float32)
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            k = np.roll(known, (dy, dx), (0, 1))
            acc += np.roll(rgb, (dy, dx), (0, 1)) * k[..., None]
            cnt += k
        grow = ~known & (cnt > 0)
        rgb[grow] = acc[grow] / cnt[grow][:, None]
        known = known | grow
    return rgb


def upscale_file(model, device, src, dst, prescale, tile):
    img = Image.open(src).convert("RGBA")
    w, h = img.size
    if prescale > 1:
        img = img.resize((w * prescale, h * prescale), Image.NEAREST)
    a = np.asarray(img, np.float32) / 255
    rgb, alpha = bleed(a[..., :3], a[..., 3]), a[..., 3]
    colour = run(model, device, rgb, tile)
    if alpha.min() < 1:
        alpha_up = run(model, device, np.repeat(alpha[..., None], 3, 2), tile).mean(axis=2)
        # The model's outline, kept crisp: a narrow ramp around the middle.
        alpha_up = np.clip((alpha_up - 0.5) * 3 + 0.5, 0, 1)
    else:
        alpha_up = np.ones(colour.shape[:2], np.float32)
    out = np.dstack((colour, alpha_up))
    result = Image.fromarray((out * 255 + 0.5).astype(np.uint8), "RGBA")
    if prescale > 1:
        result = result.resize((w * 4, h * 4), Image.LANCZOS)
    result.save(dst)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("model")
    parser.add_argument("input")
    parser.add_argument("out_dir")
    parser.add_argument("--prescale", type=int, default=1)
    parser.add_argument("--tile", type=int, default=192)
    parser.add_argument("--only", default="", help="comma-separated file names")
    args = parser.parse_args()

    device = "mps" if torch.backends.mps.is_available() else "cpu"
    model = load_model(args.model, device)
    if os.path.isdir(args.input):
        names = sorted(n for n in os.listdir(args.input) if n.endswith(".png"))
        if args.only:
            names = [n for n in names if n in args.only.split(",")]
        files = [os.path.join(args.input, n) for n in names]
    else:
        files = [args.input]
    os.makedirs(args.out_dir, exist_ok=True)
    for f in files:
        print("upscaling", os.path.basename(f), flush=True)
        upscale_file(model, device, f, os.path.join(args.out_dir, os.path.basename(f)), args.prescale, args.tile)
    print("wrote", len(files), "pictures to", args.out_dir)


if __name__ == "__main__":
    sys.exit(main())
