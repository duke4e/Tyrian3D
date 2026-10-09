"""Writing Tyrian's data formats, for content made by tools (episode 6): the encrypted text files
(levelsN.dat, cubetxtN.dat) and the level files (tyrianN.lvl).

A level file is a count (u16), the entries' offsets (s32 each) and the entries: each level is two,
its header and events (map files, sizes, the random enemies, the events) and its maps (three
tables of 128 tile numbers, big-endian, and the three maps: 14x300, 14x600, 15x600 bytes); in
episodes 4 and later the last entry is the episode's item data (src/episodes.c).
"""
import os
import struct
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import levels  # noqa: E402

CRYPT_KEY = levels.CRYPT_KEY
MAP_ENTRY_SIZE = 3 * 128 * 2 + 14 * 300 + 14 * 600 + 15 * 600


def encrypt(text):
    """The inverse of helptext.c decrypt_string."""
    plain = text.encode("latin1")
    out = bytearray(len(plain))
    for j, p in enumerate(plain):
        c = p ^ CRYPT_KEY[j % len(CRYPT_KEY)]
        if j > 0:
            c ^= out[j - 1]
        out[j] = c
    return bytes(out)


def write_strings(path, strings):
    """A file of encrypted Pascal strings (a length byte, then the bytes)."""
    with open(path, "wb") as f:
        for s in strings:
            data = encrypt(s)
            assert len(data) < 256, s
            f.write(bytes([len(data)]) + data)


def read_level_file(path):
    """The entries of a level file, as bytes."""
    data = open(path, "rb").read()
    count = struct.unpack_from("<H", data, 0)[0]
    pos = list(struct.unpack_from(f"<{count}i", data, 2)) + [len(data)]
    return [data[pos[i]:pos[i + 1]] for i in range(count)]


def write_level_file(path, entries):
    header = struct.pack("<H", len(entries))
    offset = len(header) + 4 * len(entries)
    offsets = []
    for e in entries:
        offsets.append(offset)
        offset += len(e)
    with open(path, "wb") as f:
        f.write(header + struct.pack(f"<{len(entries)}i", *offsets) + b"".join(entries))


def level_line(next_section, name, song, file_number, bonus=False):
    """A script's ]L command: the section after the level, its name (9 characters), its song and
    its two entries in the level file (file_number counts levels from 1)."""
    assert len(name) <= 9 and 0 < file_number < 100 and 0 < song < 100
    return f"]L[ 9999 {next_section:03d} {name:<9}{song:02d} {file_number:02d}" + ("$$" if bonus else "")
