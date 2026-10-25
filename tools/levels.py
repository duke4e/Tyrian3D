#!/usr/bin/env python3
"""List the level sections of the Tyrian episode scripts (levelsN.dat).

Each line is "<episode>:<section> <level name>", usable as TYR3D_START. Custom episodes
(data/custom/<name>/, or TYR3D_CUSTOM_DIR: see src/episodes.h) follow as "<name>:<section> <level name>".

usage: tools/levels.py [data_dir] [episode or custom episode name...]
"""
import os
import sys

CRYPT_KEY = [204, 129, 63, 255, 71, 19, 25, 62, 1, 99]


def read_strings(path):
    """Encrypted Pascal strings, decrypted as in helptext.c decrypt_string()."""
    with open(path, "rb") as f:
        data = f.read()
    strings = []
    i = 0
    while i < len(data):
        length = data[i]
        s = bytearray(data[i + 1:i + 1 + length])
        i += 1 + length
        for j in range(length - 1, -1, -1):
            s[j] ^= CRYPT_KEY[j % len(CRYPT_KEY)]
            if j > 0:
                s[j] ^= s[j - 1]
        strings.append(s.decode("latin1"))
    return strings


def level_sections(path):
    """(section, level name) for every section with a ]L (load level) command.

    Timed battle sections are left out: they belong to a separate game mode, and starting one
    with TYR3D_START does not set that mode up.
    """
    result = []
    section = 0
    seen = set()
    timed_battle = False
    for s in read_strings(path):
        if s.startswith("*"):
            section += 1
            timed_battle = "timed battle" in s.lower()
        elif s.startswith("]L") and section not in seen and not timed_battle:
            seen.add(section)
            result.append((section, s[13:22].strip()))  # levelName: 9 chars at 13
    return result


def custom_episodes(root, data_dir):
    """{folder name: its script} for the custom episodes, as the game finds them (episodes.c)."""
    found = {}
    for base in (os.environ.get("TYR3D_CUSTOM_DIR", os.path.join(root, "data", "custom")),
                 os.path.join(data_dir, "custom")):
        if not os.path.isdir(base):
            continue
        for name in sorted(os.listdir(base)):
            folder = os.path.join(base, name)
            if name in found or name.startswith(".") or not os.path.isdir(folder):
                continue
            files = {f.lower(): os.path.join(folder, f) for f in os.listdir(folder)}
            for n in range(1, 10):
                if f"levels{n}.dat" in files and f"tyrian{n}.lvl" in files:
                    found[name] = files[f"levels{n}.dat"]
                    break
    return found


def main():
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    data_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(root, "data", "tyrian2000")
    customs = custom_episodes(root, data_dir)
    episodes = [int(e) if e.isdigit() else e for e in sys.argv[2:]] or [1, 2, 3, 4, 5, 6] + list(customs)
    for episode in episodes:
        path = os.path.join(data_dir, f"levels{episode}.dat")
        if episode == 6:  # Tyrian3D's episode 6 is content (tools/content/episode6)
            path = os.path.join(root, "assets", "content", "episode6", "levels6.dat")
        if isinstance(episode, str):
            path = customs.get(episode, "")
        if not os.path.exists(path):
            continue
        for section, name in level_sections(path):
            print(f"{episode}:{section} {name}")


if __name__ == "__main__":
    main()
