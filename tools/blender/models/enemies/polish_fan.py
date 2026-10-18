"""The spinning fan (sheet 3 sprite 6, 2x2: 24 x 28 pixels; SIDE EXIT, LAVA RUN and ROOST, sky and
top layers; models.cfg: sprite 3 6 fan yaw=0 spin=6). The sprite has no animation: the game turns
the model 6 degrees a frame (clockwise seen from above).

A four-bladed rotor: a red glass ball on a dark steel hub (the sprite's columns 10-13 of rows
11-14), four broad grey paddle blades on the diagonals, each an elongated octagon (pointed at the
root, its outer corners clipped: the sprite's lobes, their dark outline included) bulging like a
pillow, with a darker rim. A polished steel strap clamps each blade's root to the hub, a rivet near
its end (the lighter stem and bright pixel by each lobe's root). The blades
are pitched (their leading edges, clockwise, higher), so the turning model reads as a rotor, and
droop a little towards their tips, so each faces out from the hub as the sprite shades them.

The sprite draws the rotor round its pixel (12, 13); the game turns the model about its origin
(the sprite's centre, pixel (12, 14)), so the rotor is centred on the origin: it turns in place
rather than wobbling round a circle, one pixel lower than the sprite draws it. Four-fold
symmetric about the origin.

Polish (2026-10-18): replaces later_episodes.py's fan (four flat ellipsoid petals).
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import tyrkit as k  # noqa: E402

# A blade in its own frame: u along it, out from the hub, v across it (to the counter-clockwise
# side), z up. Half its outline from the root's point to the middle of its tip (the other half
# mirrored): the root's point under the hub, the sides from u 5.2 to 11.5, the clipped corners and
# the flat tip at u 13.25 (the sprite's lobes, measured along their diagonals).
BLADE_HALF = [(1.6, 0.0), (5.2, 3.95), (11.45, 3.95), (13.25, 2.2), (13.25, 0.0)]
BLADE_MID = 0.15        # the blade's middle plane (local z) at its rim
BLADE_TOP = 1.2         # how far its top bulges above the rim's middle, at its centre
BLADE_BOTTOM = 0.55     # and its underside below it
RIM = 0.38              # the rounded rim's radius
CORNER = 1.3            # the outline's corners' radius
DOME = (8.6, 5.9, 4.1)  # the top's bulge: its middle (u) and half length and width
PITCH = -12.0           # degrees about u: the clockwise side (leading edge) up
DIHEDRAL = -5.0         # degrees the blade rises towards its tip: they droop a little, so each faces
                        # out from the hub (the sprite's upper left lobe is lit, its lower right dark)

HUB_TOP = 1.25          # the collar's top
BALL = (2.15, 2.0)      # the red ball: radius, centre height
STRAP = [(2.3, 1.25), (3.5, 1.18), (4.7, 1.08), (5.4, 0.95), (5.75, 0.6)]  # (u, half width)
STRAP_Z = (0.3, 1.12)   # its bottom (sunk into the blade) and top, local z
RIVET = 4.75            # the rivet on it, u


def fillet(points, radii, spacing=1.35, steps=3):
    """A convex counter-clockwise polygon with its corners rounded (circular arcs of the given
    radii, one per corner), its straight edges cut into pieces about `spacing` long."""
    n = len(points)
    arcs = []
    for i in range(n):
        p0, p, p2 = points[i - 1], points[i], points[(i + 1) % n]
        d1, d2 = (p - p0).normalized(), (p2 - p).normalized()
        turn = d1.angle(d2, 0.0)
        t = min(radii[i] * math.tan(turn / 2), 0.45 * (p - p0).length, 0.45 * (p2 - p).length)
        r = t / math.tan(turn / 2) if turn > 1e-6 else 0.0
        a, b = p - d1 * t, p + d2 * t
        centre = a + Vector((-d1.y, d1.x)) * r
        a0 = math.atan2(a.y - centre.y, a.x - centre.x)
        arcs.append([centre + Vector((math.cos(a0 + turn * j / steps), math.sin(a0 + turn * j / steps))) * r
                     for j in range(steps + 1)])
    out = []
    for i in range(n):
        out += arcs[i]
        a, b = arcs[i][-1], arcs[(i + 1) % n][0]
        pieces = max(1, int(round((b - a).length / spacing)))
        out += [a.lerp(b, j / pieces) for j in range(1, pieces)]
    return out


def inset(points, d):
    """A convex counter-clockwise polygon moved d inwards (each corner along its bisector)."""
    n = len(points)
    out = []
    for i in range(n):
        p0, p1, p2 = points[i - 1], points[i], points[(i + 1) % n]
        e1, e2 = (p1 - p0).normalized(), (p2 - p1).normalized()
        n1, n2 = Vector((-e1.y, e1.x)), Vector((-e2.y, e2.x))
        m = (n1 + n2).normalized()
        out.append(p1 + m * d / max(m.dot(n1), 0.5))
    return out


def blade_outline():
    """Counter-clockwise from the root's point: out along the -v side, across the tip, back along +v."""
    half = [Vector(p) for p in BLADE_HALF[:-1]]  # without the tip's middle
    full = [half[0]] + [Vector((p.x, -p.y)) for p in half[1:]] + [p for p in reversed(half[1:])]
    radii = [0.5] + [CORNER] * (len(full) - 1)
    return fillet(full, radii)


def blade(name, mat, rim_mat, angle):
    """One blade: a pillow on the outline, its rim rounded; the rim takes rim_mat."""
    outline = blade_outline()
    centre = sum(outline, Vector((0, 0))) / len(outline)
    centre = Vector((centre.x + 0.6, 0.0))
    rim_steps = 4
    rings = []
    # The underside, from near its middle out to the rim.
    edge_in = inset(outline, RIM)
    for f in (0.6,):
        z = BLADE_MID - RIM - (BLADE_BOTTOM - RIM) * (1 - f * f)
        rings.append([Vector((*(centre.lerp(p, f)), z)) for p in edge_in])
    # The rounded rim, from below round to the top.
    for i in range(rim_steps + 1):
        a = -math.pi / 2 + math.pi * i / rim_steps
        ring = inset(outline, RIM * (1 - math.cos(a)))
        rings.append([Vector((p.x, p.y, BLADE_MID + RIM * math.sin(a))) for p in ring])
    rim_rings = len(rings) - 1
    # The top, bulging to the middle: heights from a smooth dome (a superellipse round the blade's
    # broad part) rather than ring by ring, so no creases run to the outline's corners.
    for f in (0.84, 0.62, 0.4, 0.18):
        ring = []
        for p in edge_in:
            q = centre.lerp(p, f)
            rho = ((abs(q.x - DOME[0]) / DOME[1]) ** 3 + (abs(q.y) / DOME[2]) ** 3) ** (1 / 3)
            fade = min(1.0, (1 - f) / 0.45)  # from the rim's top
            bulge = max(0.0, 1 - rho ** 1.8) * fade * fade * (3 - 2 * fade)
            ring.append(Vector((q.x, q.y, BLADE_MID + RIM + (BLADE_TOP - RIM) * bulge)))
        rings.append(ring)
    top = max(0.0, 1 - (abs(centre.x - DOME[0]) / DOME[1]) ** 1.8)
    obj = k.loft(name, rings, mat, start_point=(centre.x, centre.y, BLADE_MID - BLADE_BOTTOM),
                 end_point=(centre.x, centre.y, BLADE_MID + RIM + (BLADE_TOP - RIM) * top))
    obj.data.materials.append(rim_mat)
    n = len(outline)
    for poly in obj.data.polygons[:(len(rings) - 1) * n]:
        if 0 <= poly.index // n <= rim_rings - 1:  # ring pairs: the underside's outer strip and the rim
            poly.material_index = 1
    place(obj, angle)
    return k.smooth(obj, 50)


def place(obj, angle, pitch=True):
    """From the blade's frame to the model's: pitched about u, raised towards the tip, turned to
    the blade's diagonal."""
    m = Matrix.Rotation(math.radians(angle), 4, "Z") @ Matrix.Rotation(math.radians(-DIHEDRAL), 4, "Y")
    if pitch:
        m = m @ Matrix.Rotation(math.radians(PITCH), 4, "X")
    obj.data.transform(m)


def revolve(name, profile, mat, segments=32, cx=0.0, cy=0.0):
    """A round part about a vertical axis: profile [(radius, z)] from the bottom up, closed by fans."""
    vertices, faces = [], []
    m = len(profile)
    for r, z in profile:
        for s in range(segments):
            a = 2 * math.pi * s / segments
            vertices.append((cx + r * math.cos(a), cy + r * math.sin(a), z))
    for i in range(m - 1):
        for s in range(segments):
            t = (s + 1) % segments
            faces.append((i * segments + s, i * segments + t, (i + 1) * segments + t, (i + 1) * segments + s))
    vertices.append((cx, cy, profile[0][1]))
    faces += [((s + 1) % segments, s, len(vertices) - 1) for s in range(segments)]
    vertices.append((cx, cy, profile[-1][1]))
    base = (m - 1) * segments
    faces += [(base + s, base + (s + 1) % segments, len(vertices) - 1) for s in range(segments)]
    obj = k.mesh_object(name, vertices, faces, mat)
    k.recalc_normals(obj)
    return obj


def strap(name, mat, rivet_mat, angle):
    """The polished strap clamping a blade's root to the hub (the lighter stem of each lobe in the
    sprite), a rivet near its end (the bright pixel by the root)."""
    rings = []
    for u, half_width in k.profile(STRAP, 0.4):
        rings.append(k.ring(u, half_width, STRAP_Z[1] - STRAP_Z[0], 12, z=STRAP_Z[0], power=4.0, bottom=0.05))
    end = STRAP[-1][0]
    bar = k.loft(name, rings, mat, start_point=(0, STRAP[0][0], STRAP_Z[0]), end_point=(0, end + 0.35, STRAP_Z[0] + 0.2))
    bar.data.transform(Matrix.Rotation(math.radians(-90), 4, "Z"))  # along +u
    place(bar, angle)
    k.smooth(bar, 45)
    rivet = k.ellipsoid(name + "_rivet", (RIVET, 0.0, STRAP_Z[1] - 0.05), (0.55, 0.55, 0.28), rivet_mat, 10, 5)
    place(rivet, angle)
    k.smooth(rivet, 60)


def triangles():
    depsgraph = bpy.context.evaluated_depsgraph_get()
    total = 0
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            evaluated = obj.evaluated_get(depsgraph)
            mesh = evaluated.to_mesh()
            mesh.calc_loop_triangles()
            total += len(mesh.loop_triangles)
            evaluated.to_mesh_clear()
    return total


def build():
    k.reset()
    grey = k.material("fan_blade", palette=10, metallic=0.35, roughness=0.38)
    rim = k.material("fan_rim", palette=4, metallic=0.35, roughness=0.45)
    steel = k.material("fan_strap", palette=11, metallic=0.45, roughness=0.25)
    bolt = k.material("fan_rivet", palette=13, metallic=0.4, roughness=0.2)
    hub = k.material("fan_hub", palette=3, metallic=0.45, roughness=0.35)
    red = k.material("fan_ball", palette=72, metallic=0.1, roughness=0.16, emission=(200, 40, 20),
                     emission_strength=0.25)

    for i in range(4):
        angle = 45 + 90 * i
        blade(f"blade{i}", grey, rim, angle)
        strap(f"strap{i}", steel, bolt, angle)

    # The hub: a dark steel collar the blades and straps run into, the red ball on it.
    collar = [(1.6, -1.45), (2.5, -1.1), (2.95, -0.45), (3.05, 0.35), (2.85, 0.95), (2.35, HUB_TOP),
              (1.8, HUB_TOP + 0.05)]
    k.smooth(revolve("collar", collar, hub, 24), 50)
    k.smooth(k.ellipsoid("ball", (0, 0, BALL[1]), (BALL[0], BALL[0], BALL[0] * 0.92), red, 18, 9), 60)

    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    print("triangles:", triangles())
    options = k.args()
    if "check" in options:  # also compared where the sprite draws the rotor (one pixel up)
        sheet, index = options["check"].rsplit(":", 1)
        meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
        for shift in (Matrix.Translation((0, 1, 0)), Matrix.Translation((0, -1, 0))):
            for obj in meshes:
                obj.data.transform(shift)
            if shift[1][3] > 0:
                print("moved to the sprite's rotor centre, pixel (12, 13):")
                k.check_silhouette(sheet, [int(i) for i in index.split("+")])
        print("as built (centred on the origin, the game's pivot):")
    here = os.path.dirname(os.path.abspath(__file__))
    k.finish(os.path.join(here, "..", "..", "..", "..", "assets", "models", "enemies", "fan.glb"))


build()
