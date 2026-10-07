"""Procedural shapes for Tyrian3D models (flat-shaded, low-poly).

All shapes use the Tyrian3D convention: Y up, nose towards -Z, units are game pixels.
Shapes return a Mesh; combine and position them with the transform helpers.
"""
import math

from .gltf import Mesh


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _normalize(v):
    length = math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2) or 1.0
    return (v[0] / length, v[1] / length, v[2] / length)


class Builder:
    """Accumulates flat-shaded triangles."""

    def __init__(self, material, name="mesh"):
        self.mesh = Mesh(material, name=name)

    def tri(self, a, b, c):
        n = _normalize(_cross(_sub(b, a), _sub(c, a)))
        base = len(self.mesh.positions)
        self.mesh.positions += [a, b, c]
        self.mesh.normals += [n, n, n]
        self.mesh.indices += [base, base + 1, base + 2]

    def quad(self, a, b, c, d):
        self.tri(a, b, c)
        self.tri(a, c, d)

    def polygon(self, points):
        """Convex polygon as a fan."""
        for i in range(1, len(points) - 1):
            self.tri(points[0], points[i], points[i + 1])


def extrude(material, outline, bottom, top, name="extrusion"):
    """Prism from a convex 2D outline in the XZ plane (counter-clockwise seen from above)."""
    b = Builder(material, name)
    low = [(x, bottom, z) for x, z in outline]
    high = [(x, top, z) for x, z in outline]
    b.polygon(high[::-1])
    b.polygon(low)
    for i in range(len(outline)):
        j = (i + 1) % len(outline)
        b.quad(low[i], low[j], high[j], high[i])
    return b.mesh


def loft(material, sections, name="loft"):
    """Hull through cross-sections along Z. Each section is (z, [(x, y), ...]) with the same
    number of points, ordered counter-clockwise when looking towards -Z. Ends are capped."""
    b = Builder(material, name)
    rings = [[(x, y, z) for x, y in points] for z, points in sections]
    for r0, r1 in zip(rings, rings[1:]):
        n = len(r0)
        for i in range(n):
            j = (i + 1) % n
            b.quad(r0[i], r0[j], r1[j], r1[i])
    b.polygon(rings[0][::-1])
    b.polygon(rings[-1])
    return b.mesh


def ellipse_section(z, rx, ry, segments=8, y0=0.0, x0=0.0):
    points = [(x0 + rx * math.cos(2 * math.pi * k / segments), y0 + ry * math.sin(2 * math.pi * k / segments))
              for k in range(segments)]
    return (z, points)


def cylinder(material, radius, length, segments=10, name="cylinder"):
    """Along Z, centred on the origin."""
    return loft(material, [ellipse_section(-length / 2, radius, radius, segments),
                           ellipse_section(length / 2, radius, radius, segments)], name)


def transform(mesh, scale=(1, 1, 1), rotate_y=0.0, translate=(0, 0, 0)):
    """Scales, rotates about Y (degrees) and translates a mesh in place; returns it."""
    c, s = math.cos(math.radians(rotate_y)), math.sin(math.radians(rotate_y))
    flip = (scale[0] < 0) != (scale[1] < 0) != (scale[2] < 0)

    def apply(p):
        x, y, z = p[0] * scale[0], p[1] * scale[1], p[2] * scale[2]
        x, z = x * c + z * s, -x * s + z * c
        return (x + translate[0], y + translate[1], z + translate[2])

    def apply_normal(n):
        x, y, z = n[0] / scale[0], n[1] / scale[1], n[2] / scale[2]
        x, z = x * c + z * s, -x * s + z * c
        return _normalize((x, y, z))

    mesh.positions = [apply(p) for p in mesh.positions]
    mesh.normals = [apply_normal(n) for n in mesh.normals]
    if flip:  # mirroring reverses the winding
        for i in range(0, len(mesh.indices), 3):
            mesh.indices[i + 1], mesh.indices[i + 2] = mesh.indices[i + 2], mesh.indices[i + 1]
    return mesh


def mirror_x(mesh):
    """A copy of the mesh mirrored across X (for symmetric ships)."""
    copy = Mesh(mesh.material, list(mesh.positions), list(mesh.normals), list(mesh.indices), mesh.name + "_mirror")
    return transform(copy, scale=(-1, 1, 1))
