"""Minimal glTF 2.0 binary (.glb) writer, standard library only.

Tyrian3D model convention: Y up, nose towards -Z, 1 unit = 1 game pixel.
"""
import json
import struct


class Material:
    def __init__(self, name, color=(0.8, 0.8, 0.8, 1.0), metallic=0.0, roughness=0.6, emissive=(0.0, 0.0, 0.0)):
        self.name = name
        self.color = tuple(color) if len(color) == 4 else tuple(color) + (1.0,)
        self.metallic = metallic
        self.roughness = roughness
        self.emissive = tuple(emissive)


class Mesh:
    """Triangle mesh with flat or smooth normals; one material."""

    def __init__(self, material, positions=None, normals=None, indices=None, name="mesh"):
        self.material = material
        self.positions = positions or []
        self.normals = normals or []
        self.indices = indices or []
        self.name = name


def _pad4(data, fill=b"\x00"):
    return data + fill * ((4 - len(data) % 4) % 4)


def write_glb(path, meshes):
    materials = []
    material_index = {}
    for mesh in meshes:
        if id(mesh.material) not in material_index:
            material_index[id(mesh.material)] = len(materials)
            materials.append(mesh.material)

    binary = bytearray()
    buffer_views = []
    accessors = []
    gltf_meshes = []
    nodes = []

    def add_view(data, target):
        offset = len(binary)
        binary.extend(_pad4(data))
        buffer_views.append({"buffer": 0, "byteOffset": offset, "byteLength": len(data), "target": target})
        return len(buffer_views) - 1

    for mesh in meshes:
        if not mesh.indices:
            continue
        pos = b"".join(struct.pack("<3f", *p) for p in mesh.positions)
        nor = b"".join(struct.pack("<3f", *n) for n in mesh.normals)
        idx = b"".join(struct.pack("<I", i) for i in mesh.indices)
        mins = [min(p[k] for p in mesh.positions) for k in range(3)]
        maxs = [max(p[k] for p in mesh.positions) for k in range(3)]

        pos_view = add_view(pos, 34962)
        accessors.append({"bufferView": pos_view, "componentType": 5126, "count": len(mesh.positions),
                          "type": "VEC3", "min": mins, "max": maxs})
        pos_accessor = len(accessors) - 1
        nor_view = add_view(nor, 34962)
        accessors.append({"bufferView": nor_view, "componentType": 5126, "count": len(mesh.normals), "type": "VEC3"})
        nor_accessor = len(accessors) - 1
        idx_view = add_view(idx, 34963)
        accessors.append({"bufferView": idx_view, "componentType": 5125, "count": len(mesh.indices), "type": "SCALAR"})
        idx_accessor = len(accessors) - 1

        gltf_meshes.append({
            "name": mesh.name,
            "primitives": [{
                "attributes": {"POSITION": pos_accessor, "NORMAL": nor_accessor},
                "indices": idx_accessor,
                "material": material_index[id(mesh.material)],
            }],
        })
        nodes.append({"mesh": len(gltf_meshes) - 1, "name": mesh.name})

    document = {
        "asset": {"version": "2.0", "generator": "Tyrian3D modelkit"},
        "scene": 0,
        "scenes": [{"nodes": list(range(len(nodes)))}],
        "nodes": nodes,
        "meshes": gltf_meshes,
        "materials": [{
            "name": m.name,
            "pbrMetallicRoughness": {"baseColorFactor": list(m.color), "metallicFactor": m.metallic,
                                     "roughnessFactor": m.roughness},
            "emissiveFactor": list(m.emissive),
            "doubleSided": True,
        } for m in materials],
        "buffers": [{"byteLength": len(binary)}],
        "bufferViews": buffer_views,
        "accessors": accessors,
    }

    json_chunk = _pad4(json.dumps(document, separators=(",", ":")).encode("utf-8"), b" ")
    bin_chunk = _pad4(bytes(binary))
    total = 12 + 8 + len(json_chunk) + 8 + len(bin_chunk)
    with open(path, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, total))
        f.write(struct.pack("<II", len(json_chunk), 0x4E4F534A))
        f.write(json_chunk)
        f.write(struct.pack("<II", len(bin_chunk), 0x004E4942))
        f.write(bin_chunk)
