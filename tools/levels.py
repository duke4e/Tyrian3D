#!/usr/bin/env python3
"""List the level sections of the Tyrian episode scripts (levelsN.dat).

Each line is "<episode>:<section> <level name>", usable as TYR3D_START.

usage: tools/levels.py [data_dir] [episode...]
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
    """(section, level name) for every section with a ]L (load level) command."""
    result = []
    section = 0
    seen = set()
    for s in read_strings(path):
        if s.startswith("*"):
            section += 1
        elif s.startswith("]L") and section not in seen:
            seen.add(section)
            result.append((section, s[13:22].strip()))  # levelName: 9 chars at 13
    return result


def main():
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    data_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(root, "data", "tyrian2000")
    episodes = [int(e) for e in sys.argv[2:]] or [1, 2, 3, 4, 5]
    for episode in episodes:
        path = os.path.join(data_dir, f"levels{episode}.dat")
        if not os.path.exists(path):
            continue
        for section, name in level_sections(path):
            print(f"{episode}:{section} {name}")


if __name__ == "__main__":
    main()
