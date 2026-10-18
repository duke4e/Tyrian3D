"""The blue ice crystal of CAMANIS, ICE EXIT and ICESECRET (sheet 7 sprite 53, 2x2: 24 x 28 pixels),
polished (2026-10-18; it replaces later_episodes.py's low-poly gem).

WORK IN PROGRESS
"""
import math
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import tyrkit as k  # noqa: E402


# --- Cutting a crystal from planes ---------------------------------------------------------------

class Lin:
    """A linear function of the top view's x and y: a + bx * x + by * y (a facet's height)."""

    def __init__(self, a, bx=0.0, by=0.0):
        self.a, self.bx, self.by = a, bx, by

    def __add__(self, other):
        return Lin(self.a + other.a, self.bx + other.bx, self.by + other.by)

    def __sub__(self, other):
        return Lin(self.a - other.a, self.bx - other.bx, self.by - other.by)

    def __rmul__(self, s):
        return Lin(s * self.a, s * self.bx, s * self.by)

    def __call__(self, x, y):
        return self.a + self.bx * x + self.by * y


def X(c=0.0):
    """x + c"""
    return Lin(c, 1.0, 0.0)


def Y(c=0.0):
    """y + c"""
    return Lin(c, 0.0, 1.0)


def across(nx, ny, c=0.0):
    """The distance along the unit direction (nx, ny) in the top view, + c."""
    length = math.hypot(nx, ny)
    return Lin(c, nx / length, ny / length)


# Plane maths in double precision (mathutils vectors are single precision): vectors are tuples.

def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def norm(a):
    return math.sqrt(dot(a, a))


def unit_plane(n, d):
    length = norm(n)
    return (n[0] / length, n[1] / length, n[2] / length), d / length


def under(f):
    """The half-space under the facet z = f(x, y): (unit normal, offset), n . p <= d."""
    return unit_plane((-f.bx, -f.by, 1.0), f.a)


def over(f):
    """The half-space over z = f(x, y) (the crystal's underside)."""
    return unit_plane((f.bx, f.by, -1.0), -f.a)


def wall(nx, ny, d):
    """The half-space nx * x + ny * y <= d (a vertical facet)."""
    return unit_plane((nx, ny, 0.0), d)


def chamfer(a, b, width):
    """A narrow facet cut along the edge where the half-spaces a and b meet, `width` wide: its
    normal halves the angle between theirs (as a gem cutter grinds a ridge)."""
    (na, da), (nb, db) = a, b
    angle = math.acos(max(-1.0, min(1.0, dot(na, nb))))
    s = (na[0] + nb[0], na[1] + nb[1], na[2] + nb[2])
    depth = 0.5 * width * math.tan(angle / 2)
    n, d = unit_plane(s, da + db)
    return n, d - depth


def solid(planes, eps=1e-9):
    """The convex solid where every half-space of `planes` (a list of (normal, d)) holds: its
    vertices and its faces (vertex indices, counter-clockwise seen from outside) with the index of
    the plane each face lies on."""
    n = len(planes)
    points = []
    for i in range(n):
        ni, di = planes[i]
        for j in range(i + 1, n):
            nj, dj = planes[j]
            cij = cross(ni, nj)
            if norm(cij) < 1e-9:
                continue
            for m in range(j + 1, n):
                nm, dm = planes[m]
                det = dot(cij, nm)
                if abs(det) < 1e-9:
                    continue
                a, b = cross(nj, nm), cross(nm, ni)
                p = tuple((a[c] * di + b[c] * dj + cij[c] * dm) / det for c in range(3))
                if all(dot(nq, p) <= dq + eps for nq, dq in planes):
                    if not any(norm((q[0] - p[0], q[1] - p[1], q[2] - p[2])) < 1e-7 for q in points):
                        points.append(p)
    faces, owners = [], []
    for m, (nm, dm) in enumerate(planes):
        on = [i for i, p in enumerate(points) if abs(dot(nm, p) - dm) < 1e-7]
        if len(on) < 3:
            continue
        centre = tuple(sum(points[i][c] for i in on) / len(on) for c in range(3))
        rel = {i: tuple(points[i][c] - centre[c] for c in range(3)) for i in on}
        u = rel[on[0]]
        u = tuple(c / norm(u) for c in u)
        w = cross(nm, u)
        on.sort(key=lambda i: math.atan2(dot(rel[i], w), dot(rel[i], u)))
        # Drop points that are (nearly) on a straight line between their neighbours.
        loop = []
        for idx, i in enumerate(on):
            a, b, c = points[on[idx - 1]], points[i], points[on[(idx + 1) % len(on)]]
            if norm(cross(tuple(b[t] - a[t] for t in range(3)), tuple(c[t] - b[t] for t in range(3)))) > 1e-9:
                loop.append(i)
        if len(loop) >= 3:
            faces.append(loop)
            owners.append(m)
    return points, faces, owners


def shared_edges(planes, points, min_length=0.05):
    """The pairs of planes that meet in an edge of the solid (at least min_length long): on a
    convex solid, those with two vertices on both of them."""
    on = [set(i for i, p in enumerate(points) if abs(dot(n, p) - d) < 1e-7) for n, d in planes]
    pairs = set()
    for a in range(len(planes)):
        for b in range(a + 1, len(planes)):
            common = [points[i] for i in on[a] & on[b]]
            if len(common) >= 2 and max(math.dist(p, q) for p in common for q in common) >= min_length:
                pairs.add((a, b))
    return pairs


def crystal(name, facets, ridges):
    """A flat-faceted crystal: facets {name: (half-space, material)}, ridges [(facet, facet, width,
    material)] cut as narrow facets where those facets meet (ridges whose facets don't meet are
    left out). Returns the object."""
    names = list(facets)
    planes = [facets[f][0] for f in names]
    materials = [facets[f][1] for f in names]
    points, faces, owners = solid(planes)
    meeting = shared_edges(planes, points)
    for a, b, width, mat in ridges:
        ia, ib = names.index(a), names.index(b)
        if (min(ia, ib), max(ia, ib)) in meeting:
            planes.append(chamfer(planes[ia], planes[ib], width))
            materials.append(mat)
        else:
            print(f"crystal: {a} and {b} don't meet")
    points, faces, owners = solid(planes)
    obj = k.mesh_object(name, points, faces)
    slots = []
    for o in owners:
        if materials[o] not in slots:
            slots.append(materials[o])
    for m in slots:
        obj.data.materials.append(m)
    for poly, owner in zip(obj.data.polygons, owners):
        poly.material_index = slots.index(materials[owner])
        poly.use_smooth = False
    return obj


# --- The crystal ---------------------------------------------------------------------------------

# The outline (the girdle), counter-clockwise from above: the sprite's octagon, its outline pixels
# included.
OUTLINE = [(4.0, 12.0), (-4.0, 12.0), (-10.0, 5.0), (-10.0, -6.0), (-4.0, -12.0), (4.0, -12.0), (10.0, -6.0),
           (10.0, 5.0)]
OUTLINE_NAMES = ["top", "upper_left", "left", "lower_left", "bottom", "lower_right", "right", "upper_right"]
GIRDLE_TOP, GIRDLE_BOTTOM = 5.4, 4.4
BEZEL_SLOPE, PAVILION_SLOPE, CULET = 2.6, 1.25, -3.5


def outline_facets(outline, names, girdle_top, girdle_bottom, bezel_slope, pavilion_slope, culet, cap_sides=()):
    """The girdle round the outline (vertical walls), the steep bezel above it and the pavilion
    below it: {name: (half-space, material name)}. outline: counter-clockwise from above."""
    facets = {}
    for idx, (p, q) in enumerate(zip(outline, outline[1:] + outline[:1])):
        nx, ny = q[1] - p[1], -(q[0] - p[0])
        length = math.hypot(nx, ny)
        nx, ny = nx / length, ny / length
        d = nx * p[0] + ny * p[1]
        side = names[idx]
        facets["girdle_" + side] = (wall(nx, ny, d), "girdle")
        facets["bezel_" + side] = (under(Lin(girdle_top + bezel_slope * d, -bezel_slope * nx, -bezel_slope * ny)),
                                   "cap_bezel" if side in cap_sides else "bezel")
        facets["pavilion_" + side] = (over(Lin(girdle_bottom - pavilion_slope * d, pavilion_slope * nx,
                                              pavilion_slope * ny)), "pavilion")
    facets["culet"] = (over(Lin(culet)), "pavilion")
    return facets


def design():
    """The crystal's facets {name: (half-space, material name)}, its ridges [(facet, facet, width,
    material name)] and its materials' palette indices {material name: index}."""
    sq = math.sqrt(2)
    # The table: highest along the sprite's light line across it (row 12), falling off a little
    # both ways; across, a gentle barrel of four strips (their edges at columns 8, 11 and 14), so
    # that the cap above it falls in the sprite's bands.
    crest = Lin(12.0)
    upper = crest - 0.10 * Y(-1.5)
    lower = crest + 0.13 * Y(-1.5)
    strip_b = 0.05 * X(1.0)
    strip_c = -0.03 * X(1.0)
    strip_a = Lin(strip_b(-4.0, 0)) + 0.14 * X(4.0)
    strip_d = Lin(strip_c(2.5, 0)) - 0.12 * X(-2.5)
    f = {}
    for half, base in (("u", upper), ("l", lower)):
        for strip, g in (("a", strip_a), ("b", strip_b), ("c", strip_c), ("d", strip_d)):
            f[f"table_{strip}{half}"] = base + g
    k_left, k_right = 1.43, 0.85
    for half in "ul":
        # The sides, from the ridges down the sprite's white lines (columns 5 and 17).
        f["side_l" + half] = f["table_a" + half] + k_left * X(6.5)
        f["side_r" + half] = f["table_d" + half] - k_right * X(-5.5)
    # The lower end: three facets below the table's lower edges (the white lines from column 5
    # down to row 20, along row 20, and from column 17 down to it).
    f["lower_left"] = f["table_al"] + 1.0 * across(1, 1, 8 / sq)
    f["lower_mid"] = f["table_cl"] + 0.85 * Y(6.5)
    f["lower_right"] = f["table_dl"] - sq * k_right * across(1, -1, -9 / sq)
    # The upper end (the sprite's dark cap): each strip of the top turned down from row 7.
    for strip in "abcd":
        f["cap_" + strip] = f[f"table_{strip}u"] - 1.1 * Y(-7.0)
    f["cap_left"] = f["side_lu"] - 1.4 * Y(-7.0)
    f["cap_right"] = f["side_ru"] - 1.3 * Y(-7.0)

    facets = {name: (under(fn), name) for name, fn in f.items()}
    facets.update(outline_facets(OUTLINE, OUTLINE_NAMES, GIRDLE_TOP, GIRDLE_BOTTOM, BEZEL_SLOPE, PAVILION_SLOPE,
                                 CULET, cap_sides=("top", "upper_left", "upper_right")))
    palette = {
        "table_au": 0x98, "table_bu": 0x98, "table_cu": 0x9a, "table_du": 0x9b,
        "table_al": 0x9b, "table_bl": 0x9c, "table_cl": 0x9d, "table_dl": 0x9c,
        "side_lu": 0x9d, "side_ll": 0x9c, "side_ru": 0x9d, "side_rl": 0x9b,
        "lower_left": 0x9a, "lower_mid": 0x98, "lower_right": 0x9d,
        "cap_a": 0x37, "cap_b": 0x3d, "cap_c": 0x35, "cap_d": 0x3a, "cap_left": 0x37, "cap_right": 0x32,
        "bezel": 0x96, "cap_bezel": 0x32, "girdle": 0x93, "pavilion": 0x96,
        "white": 0x8f, "light": 0x9f,
    }
    white, light = 0.85, 0.6
    ridges = [
        ("table_au", "side_lu", white, "white"), ("table_al", "side_ll", white, "white"),
        ("table_al", "lower_left", white, "white"), ("table_bl", "lower_left", white, "white"),
        ("table_cl", "lower_mid", white, "white"), ("table_bl", "lower_mid", white, "white"),
        ("table_du", "side_ru", light, "light"), ("table_dl", "side_rl", white, "white"),
        ("table_dl", "lower_right", white, "white"), ("table_cl", "lower_right", white, "white"),
        ("lower_mid", "lower_right", white, "white"),
        ("side_rl", "lower_right", white, "white"),
        ("table_au", "table_al", light, "light"), ("table_bu", "table_bl", light, "light"),
        ("table_cu", "table_cl", light, "light"), ("table_du", "table_dl", light, "light"),
        ("side_lu", "side_ll", white, "white"), ("side_ru", "side_rl", white, "white"),
        ("side_ru", "bezel_right", white, "white"), ("side_rl", "bezel_right", white, "white"),
        ("lower_right", "bezel_right", white, "white"), ("lower_right", "bezel_lower_right", white, "white"),
        ("side_lu", "bezel_left", light, "light"), ("side_ll", "bezel_left", light, "light"),
        ("table_bl", "table_cl", 0.45, "light"),
        ("lower_left", "lower_mid", light, "light"),
    ]
    return facets, ridges, palette


def materials(palette, prefix):
    """The crystal's materials by name: glossy palette shades (ramp 3: the dark cap; the white
    lines; the blue ice)."""
    mats = {}
    for name, index in palette.items():
        if index >> 4 == 3:
            mats[name] = k.material(f"{prefix}_cap_{index:x}", palette=index, metallic=0.3, roughness=0.16)
        elif name in ("white", "light"):
            mats[name] = k.material(f"{prefix}_line_{index:x}", palette=index, metallic=0.1, roughness=0.1,
                                    emission=k.level_palette()[index], emission_strength=0.3)
        else:
            # Ice lets light through: its shaded facets keep some of their blue.
            mats[name] = k.material(f"{prefix}_ice_{index:x}", palette=index, metallic=0.2, roughness=0.12,
                                    emission=k.level_palette()[index], emission_strength=0.15)
    return mats


def build():
    k.reset()
    facets, ridges, palette = design()
    mats = materials(palette, "crystal")
    obj = crystal("crystal", {name: (plane, mats[m]) for name, (plane, m) in facets.items()},
                  [(a, b, w, mats[m]) for a, b, w, m in ridges])
    print("triangles:", sum(len(p.vertices) - 2 for p in obj.data.polygons), "materials:", len(obj.data.materials))
    # The game shows colours as they are (no filmic tone mapping): so do the previews.
    bpy.context.scene.view_settings.view_transform = "Standard"
    k.finish(os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies", "crystal_blue.glb"))


if __name__ == "__main__":
    build()
