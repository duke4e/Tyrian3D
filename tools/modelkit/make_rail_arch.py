#!/usr/bin/env python3
"""The stone arch STARFALL's flight goes through (src/rail.c, arches): assets/models/rail/arch.glb.

Two pillars of stacked blocks on plinths, imposts, and a half-round arch of voussoirs with a keystone, in three shades
of sandstone; game pixels, Y up, the opening along Z, the base at y = 0 (drawn at its origin: models.cfg "origin").
The pillars go below the base, into the ground. rail.c's ARCH_* match: opening INNER wide either side of the middle,
the arch springing at SPRING, its outer edge OUTER.

usage: python tools/modelkit/make_rail_arch.py
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from modelkit.gltf import Material, Mesh, write_glb  # noqa: E402

INNER = 60.0   # the opening's half width, and the arch's inner radius
OUTER = 86.0   # the pillars' outer face, and the arch's outer radius
SPRING = 64.0  # where the arch springs from the pillars
DEPTH = 26.0   # along the flight
BELOW = -40.0  # the pillars' foot, in the ground
GAP = 0.7      # between the blocks
OUT = os.path.join(HERE, "..", "..", "assets", "models", "rail", "arch.glb")


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def unit(v):
    length = math.sqrt(dot(v, v)) or 1.0
    return (v[0] / length, v[1] / length, v[2] / length)


def block(mesh, corners):
    """A six-faced block from its eight corners, c[x + 2 y + 4 z] (x, y, z each 0 or 1 along its own edges); each face
    flat and facing out."""
    centre = tuple(sum(c[k] for c in corners) / 8.0 for k in range(3))
    faces = [(0, 2, 6, 4), (1, 3, 7, 5), (0, 1, 5, 4), (2, 3, 7, 6), (0, 1, 3, 2), (4, 5, 7, 6)]
    for face in faces:
        p = [corners[i] for i in face]
        middle = tuple(sum(q[k] for q in p) / 4.0 for k in range(3))
        n = unit(cross(sub(p[1], p[0]), sub(p[2], p[0])))
        if dot(n, sub(middle, centre)) < 0:
            p = p[::-1]
            n = (-n[0], -n[1], -n[2])
        for tri in ((p[0], p[1], p[2]), (p[0], p[2], p[3])):
            base = len(mesh.positions)
            mesh.positions += list(tri)
            mesh.normals += [n, n, n]
            mesh.indices += [base, base + 1, base + 2]


def box(mesh, x0, x1, y0, y1, z0, z1):
    block(mesh, [(x1 if i & 1 else x0, y1 if i & 2 else y0, z1 if i & 4 else z0) for i in range(8)])


def main():
    random.seed(7)
    shades = [Material("sandstone_%d" % i, color, roughness=0.92) for i, color in
              enumerate([(0.66, 0.58, 0.46), (0.58, 0.51, 0.41), (0.71, 0.64, 0.52)])]
    meshes = {id(m): Mesh(m, name=m.name) for m in shades}

    def shade():
        return meshes[id(random.choice(shades))]

    half = DEPTH / 2
    for side in (-1, 1):
        def span(a, b):
            return (min(side * a, side * b), max(side * a, side * b))
        # The plinth, wider and deeper, its top a little over the ground.
        x0, x1 = span(INNER - 4, OUTER + 4)
        box(shade(), x0, x1, BELOW, 6, -half - 3, half + 3)
        # The pillar's courses, of alternating heights, each a little rough (its faces set in or out a hair).
        y = 6.0
        heights = [14, 11, 13, 10, 10]
        for k, h in enumerate(heights):
            top = min(y + h, SPRING - 4)
            if top - y < 3:
                break
            a, b = INNER + random.uniform(-0.4, 0.4), OUTER + random.uniform(-0.4, 0.4)
            if k % 2:
                # (Two blocks side by side on every other course.)
                mid = (a + b) / 2 + random.uniform(-2, 2)
                for lo, hi in ((a, mid - GAP / 2), (mid + GAP / 2, b)):
                    x0, x1 = span(lo, hi)
                    box(shade(), x0, x1, y + GAP / 2, top - GAP / 2, -half, half)
            else:
                x0, x1 = span(a, b)
                box(shade(), x0, x1, y + GAP / 2, top - GAP / 2, -half, half)
            y = top
        # The impost the arch springs from.
        x0, x1 = span(INNER - 3, OUTER + 2)
        box(shade(), x0, x1, SPRING - 4, SPRING, -half - 2, half + 2)
    # The voussoirs, round from one impost to the other; the keystone deeper and standing out.
    count = 13
    for k in range(count):
        a0 = math.pi * k / count + GAP / 120
        a1 = math.pi * (k + 1) / count - GAP / 120
        key = k == count // 2
        r0, r1 = INNER + GAP / 2 - (2 if key else 0), OUTER + random.uniform(-0.6, 0.6) + (4 if key else 0)
        z0, z1 = (-half - 2, half + 2) if key else (-half, half)
        corners = []
        for i in range(8):
            a = a1 if i & 1 else a0
            r = r1 if i & 2 else r0
            corners.append((-math.cos(a) * r, SPRING + math.sin(a) * r, z1 if i & 4 else z0))
        block(shade(), corners)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    write_glb(OUT, list(meshes.values()))
    print("%s: %d triangles" % (os.path.normpath(OUT), sum(len(m.indices) // 3 for m in meshes.values())))


if __name__ == "__main__":
    main()
