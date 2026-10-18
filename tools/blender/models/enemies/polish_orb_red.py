"""The dark red orb of BUBBLES, ** ALE **, STARGATE, LAVA EXIT, ASTEROIDS and COLLECTOR (sheet E sprite
233, 2x2: 24 x 28 pixels), polished (2026-10-18; it replaces later_episodes.py's plain dark sphere).

WORK IN PROGRESS
"""
import math
import os
import sys

import bmesh
import bpy
import mathutils.noise as noise
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import tyrkit as k  # noqa: E402


# --- Heat painted on a surface -------------------------------------------------------------------

def smoothstep(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def band_split(obj, values, bands):
    """Gives the faces of obj the material of their band of a value per vertex, cutting faces along
    the bands' borders so the borders are smooth contours (bands: [(lowest value, material)],
    ascending; materials may repeat)."""
    mesh = obj.data
    co = [v.co.copy() for v in mesh.vertices]
    vals = list(values)
    thresholds = [b[0] for b in bands]
    cuts = {}

    def cut(a, b, t):
        key = (min(a, b), max(a, b), t)
        if key not in cuts:
            f = (t - vals[a]) / (vals[b] - vals[a])
            co.append(co[a].lerp(co[b], f))
            vals.append(t)
            cuts[key] = len(co) - 1
        return cuts[key]

    def clip(poly, t, above):
        out = []
        for i in range(len(poly)):
            a, b = poly[i], poly[(i + 1) % len(poly)]
            ina, inb = (vals[a] >= t) == above, (vals[b] >= t) == above
            if ina:
                out.append(a)
            if ina != inb:
                out.append(cut(a, b, t))
        return out

    faces, materials = [], []
    for poly in mesh.polygons:
        indices = list(poly.vertices)
        low, high = min(vals[i] for i in indices), max(vals[i] for i in indices)
        for b in range(len(bands)):
            lo = thresholds[b] if b > 0 else -1e9
            hi = thresholds[b + 1] if b + 1 < len(bands) else 1e9
            if high < lo or low >= hi:
                continue
            piece = indices
            if b > 0 and low < lo:
                piece = clip(piece, lo, True)
            if b + 1 < len(bands) and high >= hi:
                piece = clip(piece, hi, False)
            if len(piece) >= 3:
                faces.append(piece)
                materials.append(bands[b][1])
    slots = []
    for m in materials:
        if m not in slots:
            slots.append(m)
    new = bpy.data.meshes.new(mesh.name)
    new.from_pydata([tuple(c) for c in co], [], faces)
    for m in slots:
        new.materials.append(m)
    for poly, m in zip(new.polygons, materials):
        poly.material_index = slots.index(m)
    new.validate()
    obj.data = new
    bm = bmesh.new()
    bm.from_mesh(new)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-4)
    bm.to_mesh(new)
    bm.free()
    k.recalc_normals(obj)
    return obj


def icosphere(name, centre, radii, subdivisions=4):
    """An ellipsoid of even triangles (an icosphere scaled to radii)."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdivisions, radius=1.0)
    for v in bm.verts:
        d = v.co.normalized()
        v.co = Vector((centre[0] + d.x * radii[0], centre[1] + d.y * radii[1], centre[2] + d.z * radii[2]))
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


# --- The orb -------------------------------------------------------------------------------------

CENTRE = Vector((0.0, -0.5, 0.0))   # the sprite's columns 4-19, rows 7-21
RADII = Vector((8.0, 7.7, 7.3))

# The glowing spots, in the top view: (x, y, heat at the middle, radius of the falloff, raise).
SPOTS = [
    (-2.5, 1.5, 1.08, 1.25, 0.32),   # the big white-hot one at the upper left (column 9, row 12)
    (1.6, 2.5, 0.66, 0.75, 0.15),    # the small red one at the upper right (column 13, row 11)
    (0.5, -1.25, 0.95, 0.72, 0.15),  # the small yellow one below the middle (column 12, rows 14-15)
]

# The hot crescent along the lower right rim (columns 14-18, rows 16-20): its path in the top view.
CRESCENT = [(7.0, -1.2), (6.6, -2.8), (5.7, -4.2), (4.5, -5.5), (3.0, -6.4), (1.4, -6.9)]

# The bands of heat: (lowest heat, palette index, emission strength in the palette colour).
BANDS = [
    (-9.0, 0x70, 0.0),
    (0.08, 0x71, 0.0),
    (0.16, 0x72, 0.05),
    (0.24, 0x73, 0.35),
    (0.32, 0x74, 0.5),
    (0.41, 0x76, 0.65),
    (0.5, 0x77, 0.7),
    (0.58, 0x78, 0.9),
    (0.66, 0x79, 1.1),
    (0.74, 0x7a, 1.3),
    (0.82, 0x7c, 1.5),
    (0.9, 0x7d, 1.8),
    (0.98, 0x7e, 2.1),
    (1.06, 0x7f, 2.5),
]


def rim_direction(x, y):
    """The direction from the orb's middle to the point of its surface seen at (x, y) from above."""
    u, v = (x - CENTRE.x) / RADII.x, (y - CENTRE.y) / RADII.y
    flat = min(math.hypot(u, v), 0.999)
    angle = math.atan2(v, u)
    return Vector((flat * math.cos(angle), flat * math.sin(angle), math.sqrt(1 - flat * flat)))


CRESCENT_DIRS = []
for _a, _b in zip(CRESCENT, CRESCENT[1:]):
    for _i in range(8):
        CRESCENT_DIRS.append(rim_direction(*(Vector(_a).lerp(Vector(_b), _i / 8))))
CRESCENT_DIRS.append(rim_direction(*CRESCENT[-1]))


def heat_at(p):
    """The heat (0: the dark shell, 1 and more: white hot) at the surface point p."""
    rel = p - CENTRE
    d = Vector((rel.x / RADII.x, rel.y / RADII.y, rel.z / RADII.z)).normalized()
    # The glow under the shell shows through round its rim (the sprite's red outline: brighter
    # towards the bottom of the screen, dimmer on the right) and, patchy, all under it.
    patches = noise.noise(d * 2.2 + Vector((1.0, 5.0, 2.0)))
    rim = smoothstep(0.72, 0.44, d.z) * (0.29 + 0.18 * smoothstep(0.1, -0.85, d.y) - 0.07 * smoothstep(0.3, 0.95, d.x))
    under = smoothstep(0.3, -0.4, d.z) * (0.3 + 0.1 * patches)
    heat = max(rim, under)
    # The shell: faint dark red clouds in the black glass.
    heat += max(0.0, 0.07 * noise.noise(d * 2.6 + Vector((3.0, 1.0, 7.0))) + 0.035) * smoothstep(0.3, 0.8, d.z)
    # The crescent.
    for i, c in enumerate(CRESCENT_DIRS):
        t = i / (len(CRESCENT_DIRS) - 1)
        taper = math.sin(math.pi * (0.06 + 0.88 * t)) ** 0.7
        a = d.angle(c) / (0.12 * (0.5 + 0.5 * taper))
        if a < 4:
            heat = max(heat, 0.95 * taper * math.exp(-a * a))
    # The spots, seen from above.
    if d.z > 0.2:
        for x, y, peak, radius, _ in SPOTS:
            r = math.hypot(p.x - x, p.y - y)
            heat = max(heat, peak * math.exp(-(r / radius) ** 2) + 0.1 * math.exp(-(r / (2.0 * radius)) ** 2))
    return heat


def build():
    k.reset()
    # Glossy black-red glass; the hotter bands glow in their own colour.
    mats = {}
    for _, index, glow in BANDS:
        mats[index] = k.material(f"orb_{index:x}", palette=index, metallic=0.15, roughness=0.2,
                                 emission=k.level_palette()[index] if glow > 0 else None, emission_strength=glow)
    orb = icosphere("orb", CENTRE, RADII, subdivisions=5)
    values = []
    for v in orb.data.vertices:
        p = v.co.copy()
        values.append(heat_at(p))
        # The spots are lenses, raised a little out of the shell.
        rel = p - CENTRE
        d = Vector((rel.x / RADII.x, rel.y / RADII.y, rel.z / RADII.z)).normalized()
        if d.z > 0.2:
            raise_by = sum(lift * math.exp(-(math.hypot(p.x - x, p.y - y) / (0.9 * radius)) ** 4)
                           for x, y, _, radius, lift in SPOTS)
            v.co = p + Vector((d.x * RADII.x, d.y * RADII.y, d.z * RADII.z)).normalized() * raise_by
    band_split(orb, values, [(lowest, mats[index]) for lowest, index, _ in BANDS])
    k.smooth(orb, 80)
    print("triangles:", sum(len(p.vertices) - 2 for p in orb.data.polygons), "materials:", len(orb.data.materials))

    # The game shows colours as they are (no filmic tone mapping): so do the previews.
    bpy.context.scene.view_settings.view_transform = "Standard"
    k.finish(os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies", "orb_red.glb"))


if __name__ == "__main__":
    build()
