"""Crystal (the coins sheet's sprites 39, 77 and 115: the orange, green and purple crystals of 1000, 2500 and 5000
credits; 2x2, 24 x 28 pixels; about 170 of them in the levels), polished (2026-10-20; it replaces crystal.py's plain
hexagonal prism with pointed ends). models.cfg: sprite coins 39/77/115 crystal roll=frames:108 color=sprite glow.

The three are one picture in three ramps, shade for shade (and so are their frames): 39 in ramp 7 (orange), 77 in
ramp 2 (green), 115 in ramp 5 (purple). Their animations (39 41 43 45 47 49, three game frames each; 77-87 and
115-125 likewise) keep the outline and sweep the light over the crystal as it turns about its long axis:
models.cfg rolls the model about the screen's vertical axis, a sixth of a turn in the 18 game frames, so the
crystal must look the same every sixth of a turn (every face alike). No frame models: color=sprite takes each
frame's ramp.

As the sprite and its 4x upscales draw it: a long six-sided crystal standing up the screen, 13 pixels wide (columns
5-17) and 23 long (rows 2-24), its sides straight from row 8 to row 18, its ends pointed (a pixel a row: 45
degrees), a bright ridge down its middle (column 11, the edge between two faces towards the camera) and its right
edge lit, the faces left of the ridge lighter than those right of it, dark red faces with bright lines through
them, kinked like cracks: the fractures inside the stone catching the light, which flares over the upper left as
it turns (41, 43).

Built as a crystal is cut, from planes, every facet flat (polish_item_kit.convex): a hexagonal prism (an edge
towards the camera when not turned) with six-sided points, each face broken along a slanting fracture (from its
lower left to its upper right) into two facets turned FRACTURE_TILT degrees apart: round the crystal the six
fractures run as a zigzag of cracks, and as it rolls the two facets of a face catch the game's sun one after the
other, so that the light flares over a face and moves on, as in the sprite's frames. Each fracture is ground into
a narrow bright facet and the facets either side of it are lighter in steps towards it (the light in the crack);
the six edges along the crystal and the shoulders are ground narrow too. Palette shades of ramp 0 without
emission (polish_item_kit): color=sprite gives them the frame's ramp; the models.cfg glow lights the crystal in
that ramp.

The crystal's axis is the model's Y axis through the origin (the roll's axis): the sprite's column 11 is half a
pixel left of it; its middle (row 13) is at y = 0.5. The crystal is a little wider than the sprite's 13 pixels
across its edges (it is 12.5 to 14.4 pixels wide as it rolls), so that it is not thinner on average.

Options after "--": --outdir <dir> (default assets/models/items), --check <sheets dir> (the silhouette against
coins.png), --preview <prefix>, --only <name,...>, --ramp <0-15> (built in that ramp, written as _r<ramp>).
"""
import math
import os
import sys

import bmesh
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_item_kit as kit  # noqa: E402
from polish_item_kit import k  # noqa: E402

# The prism: its corners RADIUS from the axis (an edge towards the camera), its sides from SIDE_LOW to SIDE_HIGH
# (rows 18 and 8), its points at TIP_LOW and TIP_HIGH (rows 24 and 2).
RADIUS = 7.2
SIDE_LOW, SIDE_HIGH = -5.0, 6.0
TIP_LOW, TIP_HIGH = -10.8, 11.8
SPRITE_CENTRE = (-0.5, 0.0)  # how far the sprite draws the crystal's axis from the model's (for the check)
# Each face's fracture runs from its lower left (FRACTURE_FROM above the lower shoulder) to its upper right
# (FRACTURE_TO below the upper shoulder), seen from outside; its two facets are turned FRACTURE_TILT degrees
# either way about it. The narrow facets' widths: the fractures, the edges along the crystal and the shoulders.
FRACTURE_FROM, FRACTURE_TO, FRACTURE_TILT = 1.0, 2.0, 8.0
FRACTURE_W, EDGE_W, SHOULDER_W = 0.45, 0.5, 0.45
# The light in the cracks: the facets either side of a fracture are lighter in steps towards it (GLOW: how far
# each step reaches from the fracture's middle line, and its shade).
GLOW = [(0.7, 11), (1.5, 9)]

SHADES = {"face": 7, "fracture": 14, "edge": 10, "shoulder_high": 10, "shoulder_low": 10, "cap_high": 8, "cap_low": 8}
GLOSS = dict(metallic=0.25, roughness=0.16)
FINISH = {"fracture": dict(metallic=0.25, roughness=0.1), "edge": dict(metallic=0.25, roughness=0.1)}


def rotate(v, axis, degrees):
    """v turned about a unit axis (Rodrigues)."""
    a = math.radians(degrees)
    v, axis = np.asarray(v, float), np.asarray(axis, float)
    return v * math.cos(a) + np.cross(axis, v) * math.sin(a) + axis * np.dot(axis, v) * (1 - math.cos(a))


def design():
    """The crystal's half-spaces, what each is (its key) and each face's fracture (its normal and the line)."""
    planes, keys, groups = [], [], []

    def add(plane, key, group):
        planes.append(plane)
        keys.append(key)
        groups.append(group)

    apothem = RADIUS * math.cos(math.radians(30))
    half = RADIUS / 2
    up = np.array((0.0, 1.0, 0.0))
    fractures = []
    for i in range(6):
        theta = math.radians(60.0 * i)  # the face's normal, round the axis from +X towards +Z
        n = np.array((math.cos(theta), 0.0, math.sin(theta)))
        t = np.array((-math.sin(theta), 0.0, math.cos(theta)))  # across the face: the left seen from outside
        centre = n * apothem
        start = centre + t * half + up * (SIDE_LOW + FRACTURE_FROM)
        end = centre - t * half + up * (SIDE_HIGH - FRACTURE_TO)
        axis = (end - start) / np.linalg.norm(end - start)
        for normal in (rotate(n, axis, FRACTURE_TILT), rotate(n, axis, -FRACTURE_TILT)):
            add(kit.general(normal, start), "face", ("face", i))
        fractures.append((n, start, end))
        # The points: a facet through the face's shoulder edge and the tip.
        for tip, side, key in ((TIP_HIGH, SIDE_HIGH, "cap_high"), (TIP_LOW, SIDE_LOW, "cap_low")):
            p0 = centre + t * half + up * side
            p1 = centre - t * half + up * side
            p2 = np.array((0.0, tip, 0.0))
            normal = np.cross(p1 - p0, p2 - p0)
            if np.dot(normal, n) < 0:
                normal = -normal
            add(kit.general(normal, p0), key, (key, i))
    # The narrow facets where two facets meet: the fractures (a face's two facets), the edges (facets of
    # neighbouring faces) and the shoulders (a face's facets and its points' facets).
    points = kit.convex(planes)[0]
    base = len(planes)
    for a in range(base):
        for b in range(a + 1, base):
            (ga, ia), (gb, ib) = groups[a], groups[b]
            if ga == "face" and gb == "face":
                key, width = ("fracture", FRACTURE_W) if ia == ib else ("edge", EDGE_W)
            elif ga == "face" or gb == "face":
                cap = gb if ga == "face" else ga
                key, width = "shoulder" + cap[3:], SHOULDER_W
            else:
                continue
            if kit.meets(planes, a, b, points):
                add(kit.chamfer(planes[a], planes[b], width), key, (key, -1))
    return planes, keys, fractures


def glow(obj, fractures, shade):
    """Lights the facets along each face's fracture: they are cut along lines parallel to it (GLOW's steps) and
    the strips painted in the steps' shades (shade(value) gives the material)."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    layer = bm.faces.layers.int.get("part")
    parts = list(obj["parts"])

    def facets(i):
        out = []
        for f in bm.faces:
            if parts[f[layer]] == "face":
                n = f.normal
                if int(round(math.degrees(math.atan2(n.z, n.x)) / 60.0)) % 6 == i:
                    out.append(f)
        return out

    for i, (n, start, end) in enumerate(fractures):
        side = np.cross(n, (end - start) / np.linalg.norm(end - start))
        for width, _ in GLOW:
            for sign in (1.0, -1.0):
                faces = facets(i)
                geom = list({v for f in faces for v in f.verts}) + list({e for f in faces for e in f.edges}) + faces
                bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=tuple(start + side * sign * width),
                                       plane_no=tuple(side))
        line = end - start
        for f in facets(i):
            c = np.array(tuple(f.calc_center_median()))
            u = min(1.0, max(0.0, float(np.dot(c - start, line) / np.dot(line, line))))
            d = float(np.linalg.norm(start + line * u - c))
            for width, value in GLOW:
                if d < width:
                    f.material_index = kit.slot_of(obj, shade(value))
                    break
    bm.to_mesh(obj.data)
    bm.free()


def build():
    opts = kit.options()
    ramp, _ = kit.ramp_of(opts)
    if not kit.wanted(opts, "crystal"):
        return
    k.reset()
    planes, keys, fractures = design()
    made = {}

    def shade(value, finish="gloss"):
        """The material of a shade and finish (parts alike share one)."""
        if (value, finish) not in made:
            made[value, finish] = kit.shade(f"crystal_{finish}_{value}", value, ramp, **FINISH.get(finish, GLOSS))
        return made[value, finish]
    mats = {key: shade(v, key if key in FINISH else "gloss") for key, v in SHADES.items()}
    obj = kit.solid("crystal", planes, keys, mats)
    glow(obj, fractures, shade)
    kit.drop_parts(obj)
    kit.finish(opts, "crystal", [obj], 39, large=True, distance=0.8, shift=SPRITE_CENTRE)


if __name__ == "__main__":
    build()
