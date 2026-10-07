#!/usr/bin/env python3
"""Reverses the triangle winding of glTF binaries (.glb), keeping their normals.

BTBH's scene pipeline takes clockwise triangles as the front faces of static models and turns the
normals of back faces around. glTF's front faces are counter-clockwise, so models as exported by
glTF tools count as back faces outside and are lit from inside. Models for Tyrian3D get their
winding reversed once, when they are exported (tyrkit.export) or added to assets/models.

usage: tools/blender/glb_winding.py model.glb...
"""
import json
import struct
import sys


def reverse_winding(path):
    data = bytearray(open(path, "rb").read())
    json_length = struct.unpack_from("<I", data, 12)[0]
    document = json.loads(bytes(data[20:20 + json_length]))
    binary = 20 + json_length + 8
    formats = {5121: ("B", 1), 5123: ("H", 2), 5125: ("I", 4)}
    # Meshes of the same topology share their index accessor: reverse each one once.
    accessors = {p["indices"] for mesh in document["meshes"] for p in mesh["primitives"] if "indices" in p}
    for index in sorted(accessors):
        accessor = document["accessors"][index]
        view = document["bufferViews"][accessor["bufferView"]]
        offset = binary + view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
        code, size = formats[accessor["componentType"]]
        for t in range(accessor["count"] // 3):
            a, b = offset + (3 * t + 1) * size, offset + (3 * t + 2) * size
            i, j = struct.unpack_from("<" + code, data, a)[0], struct.unpack_from("<" + code, data, b)[0]
            struct.pack_into("<" + code, data, a, j)
            struct.pack_into("<" + code, data, b, i)
    open(path, "wb").write(data)


if __name__ == "__main__":
    for path in sys.argv[1:]:
        reverse_winding(path)
        print("reversed", path)
