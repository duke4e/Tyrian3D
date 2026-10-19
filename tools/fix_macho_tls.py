#!/usr/bin/env python3
"""Makes pip's scipy load on macOS 27: its wheels' extension modules have a zero-fill thread-local section
(__DATA,__thread_bss) with a nonzero file offset, which the new dyld refuses ("has a zero-fill section type,
but offset field is not zero"). The offset of a zero-fill section means nothing (it has no bytes in the file),
so this sets it to 0 and signs the module again (ad hoc: arm64 runs only signed code).

usage: python3 tools/fix_macho_tls.py <site-packages or a module>...    (lists and fixes; --dry lists only)
e.g.   python3 tools/fix_macho_tls.py ~/Library/Caches/Tyrian3D/tools-venv/lib/python3.10/site-packages/scipy
"""
import os
import struct
import subprocess
import sys

ZEROFILL = (0x01, 0x0c, 0x12)  # S_ZEROFILL, S_GB_ZEROFILL, S_THREAD_LOCAL_ZEROFILL


def zerofill_offsets(data):
    """The (position, segment, section) of each zero-fill section with a file offset in a thin 64-bit Mach-O."""
    if data[:4] != b"\xcf\xfa\xed\xfe":
        return []
    found = []
    ncmds, = struct.unpack_from("<I", data, 16)
    pos = 32
    for _ in range(ncmds):
        cmd, size = struct.unpack_from("<II", data, pos)
        if cmd == 0x19:  # LC_SEGMENT_64: its sections (80 bytes each) follow its 72 bytes
            nsects, = struct.unpack_from("<I", data, pos + 64)
            for i in range(nsects):
                s = pos + 72 + 80 * i
                offset, = struct.unpack_from("<I", data, s + 48)
                flags, = struct.unpack_from("<I", data, s + 64)
                if flags & 0xff in ZEROFILL and offset:
                    found.append((s, data[s + 16:s + 32].rstrip(b"\0").decode(), data[s:s + 16].rstrip(b"\0").decode()))
        pos += size
    return found


def fix(path, dry):
    with open(path, "rb") as f:
        data = bytearray(f.read())
    found = zerofill_offsets(data)
    if not found:
        return False
    print(path, ", ".join(f"{seg},{sect}" for _, seg, sect in found))
    if not dry:
        for s, _, _ in found:
            struct.pack_into("<I", data, s + 48, 0)
        with open(path, "wb") as f:
            f.write(data)
        subprocess.run(["codesign", "-f", "-s", "-", path], check=True, capture_output=True)
    return True


def main():
    dry = "--dry" in sys.argv
    paths = [a for a in sys.argv[1:] if a != "--dry"]
    if not paths:
        sys.exit(__doc__)
    count = 0
    for top in paths:
        files = [top] if os.path.isfile(top) else [os.path.join(d, f) for d, _, fs in os.walk(top) for f in fs
                                                   if f.endswith((".so", ".dylib"))]
        count += sum(fix(f, dry) for f in sorted(files))
    print(f"{count} modules {'to fix' if dry else 'fixed'}")


if __name__ == "__main__":
    main()
