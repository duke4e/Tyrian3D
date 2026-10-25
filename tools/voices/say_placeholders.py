#!/usr/bin/env python3
"""Placeholder voices from macOS's own `say`, to try the game's playback without ElevenLabs.

Reads data/voices/script.json (tools/voices/export_cubes.py) and writes, for the chosen cubes and
story texts, IMA ADPCM WAVs and a manifest.txt as generate.py does, into --out (never data/voices
unless asked: the real voices go there). Run the game with TYR3D_VOICES_DIR=<out> to hear them.

  say_placeholders.py --out DIR [--only E:N,...] [--stories] [--voice NAME]
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import wave

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SCRIPT = os.path.join(ROOT, "data", "voices", "script.json")


def render(text, path, voice):
    """`say` into a 24 kHz IMA ADPCM WAV; its duration in ms."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        aiff = os.path.join(tmp, "say.aiff")
        cmd = ["say", "-o", aiff] + (["-v", voice] if voice else []) + [text]
        subprocess.run(cmd, check=True)
        pcm = os.path.join(tmp, "say.wav")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", aiff, "-ar", "24000", "-ac", "1", "-c:a", "pcm_s16le", pcm],
                       check=True)
        with wave.open(pcm) as w:
            ms = round(w.getnframes() * 1000 / w.getframerate())
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", pcm, "-c:a", "adpcm_ima_wav", path], check=True)
    return ms


def spoken(text):
    return re.sub(r"\s+", " ", re.sub(r"\[[^\]]*\]", " ", text)).strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", required=True, help="where e<E>/<N>.wav, story/e<E>_<N>.wav and manifest.txt go")
    ap.add_argument("--only", action="append", default=[], help="cubes E:N (comma or repeat); default all")
    ap.add_argument("--stories", action="store_true", help="the story texts between levels too (E:101..., hints E:201...)")
    ap.add_argument("--voice", help="a `say` voice (say -v '?')")
    args = ap.parse_args()
    with open(SCRIPT, encoding="utf-8") as f:
        script = json.load(f)
    only = {o for arg in args.only for o in arg.split(",") if o}
    lines = ["# Placeholder voices (tools/voices/say_placeholders.py), as generate.py's manifest.txt"]
    for ep in script["episodes"]:
        for c in ep["cubes"] + (ep.get("stories", []) if args.stories else []):
            if c["skip"] or (only and c["id"] not in only):
                continue
            text = " ".join(spoken(p["text"]) for p in c["paragraphs"])
            ms = render(text, os.path.join(args.out, c["audio"]), args.voice)
            if c.get("kind") == "story":
                lines.append(f"story {c['text_hash']} {ms} {c['audio']}")
            else:
                lines.append(f"cube {c['episode']} {c['cube']} {c['text_hash']} {ms} {c['audio']} 0")
            print(f"{c['id']}: {c['audio']}, {ms / 1000:.1f} s")
    with open(os.path.join(args.out, "manifest.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"wrote {len(lines) - 1} voices and {os.path.join(args.out, 'manifest.txt')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
