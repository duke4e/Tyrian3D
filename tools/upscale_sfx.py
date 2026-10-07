#!/usr/bin/env python3
"""Upscales the game's sound effects and voices with AudioSR (plan M10).

usage: <python with audiosr> tools/upscale_sfx.py <in dir> <out dir> [--steps N] [--guidance G]
                                                   [--seed S] [--only a.wav,b.wav]

<in dir> holds the sounds as the game has them (TYR3D_EXPORT_SFX=<dir>: 8-bit, 11025 Hz, as WAV).
Each is run through AudioSR (48 kHz out), cut back to its original length, kept as loud as the
original (by RMS, with AudioSR's sharper peaks softly limited) and kept silent where the original is (AudioSR adds a little hiss to silence), and
written to <out dir> under the same name as 16-bit WAV. The game uses the files it finds in the
"sfx" directory beside its data (e.g. data/tyrian2000/sfx); TYR3D_ORIGINAL_SFX=1 ignores them.

AudioSR (https://github.com/haoheliu/versatile_audio_super_resolution) runs in its own Python
environment, e.g. ~/Library/Caches/Tyrian3D/audiosr/bin/python.
"""
import argparse
import os
import sys

import numpy as np
import soundfile as sf


def envelope(signal, window):
    """RMS over windows of the given length, one value per sample."""
    padded = np.pad(signal.astype(np.float64) ** 2, (window // 2, window - window // 2 - 1), mode="edge")
    kernel = np.ones(window) / window
    return np.sqrt(np.convolve(padded, kernel, mode="valid"))


def upscale(model, audiosr, path, out_path, steps, guidance, seed):
    original, rate = sf.read(path, dtype="float32")
    if original.ndim > 1:
        original = original.mean(axis=1)

    waveform = audiosr.super_resolution(model, path, seed=seed, guidance_scale=guidance, ddim_steps=steps,
                                        latent_t_per_second=12.8)
    result = np.asarray(waveform, dtype=np.float64).reshape(-1)
    out_rate = 48000

    # The original's length.
    length = int(round(len(original) * out_rate / rate))
    result = result[:length]
    if len(result) < length:
        result = np.pad(result, (0, length - len(result)))

    # Silent where the original is: the original's envelope at the new rate as a gate.
    positions = np.linspace(0, len(original) - 1, length)
    original_up = np.interp(positions, np.arange(len(original)), original)
    gate_level = 10 ** (-48 / 20)
    env = envelope(original_up, int(out_rate * 0.01))
    gate = np.clip((env - gate_level) / gate_level, 0.0, 1.0)
    result *= gate

    # As loud as the original (RMS), with a soft limit where AudioSR's sharper peaks would clip.
    rms_in = np.sqrt(np.mean(original.astype(np.float64) ** 2))
    rms_out = np.sqrt(np.mean(result ** 2))
    if rms_out > 0:
        result *= min(rms_in / rms_out, 4.0)
    result = np.where(np.abs(result) > 0.9, np.sign(result) * (0.9 + 0.1 * np.tanh((np.abs(result) - 0.9) / 0.1)),
                      result)
    sf.write(out_path, result.astype(np.float32), out_rate, subtype="PCM_16")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("in_dir")
    parser.add_argument("out_dir")
    parser.add_argument("--steps", type=int, default=50)
    parser.add_argument("--guidance", type=float, default=3.5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--only", default="")
    parser.add_argument("--device", default="auto")
    args = parser.parse_args()

    import audiosr  # noqa: E402 (only in AudioSR's environment)
    import torch  # noqa: E402
    import torchaudio  # noqa: E402

    # Newer torchaudio reads files only through TorchCodec; AudioSR just needs the samples.
    def load(path, *args, **kwargs):
        data, rate = sf.read(path, dtype="float32", always_2d=True)
        return torch.from_numpy(data.T.copy()), rate
    torchaudio.load = load

    os.makedirs(args.out_dir, exist_ok=True)
    names = sorted(n for n in os.listdir(args.in_dir) if n.endswith(".wav"))
    if args.only:
        wanted = set(args.only.split(","))
        names = [n for n in names if n in wanted]
    model = audiosr.build_model(model_name="basic", device=args.device)
    for name in names:
        print("upscaling", name, flush=True)
        upscale(model, audiosr, os.path.join(args.in_dir, name), os.path.join(args.out_dir, name),
                args.steps, args.guidance, args.seed)
    print("wrote", len(names), "sounds to", args.out_dir)


if __name__ == "__main__":
    sys.exit(main())
