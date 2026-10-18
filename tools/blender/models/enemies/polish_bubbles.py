"""The blister cluster of BUBBLES (sheet E sprite 153, 2x2: 24 x 25 pixels in the 24 x 28 cell; ground
layer, 120 of them; not animated), polished (2026-10-18; it replaces rounds.py's bubbles(), a few
smooth red spheres). models.cfg: sprite e 153 bubbles yaw=0.

As the 4x upscale draws it: a cluster of dull brick-red cushions (the sprite's ramp 4, shades 1-13)
swelling from the ground and pressed against each other, dark creases between them and a dark edge
where they meet the ground. Through the cluster, from the upper left to the lower right, runs a long
pill narrowing towards its lower end (columns 0-17 of rows 2-17), a raised pad on its upper half and
a ridge along its lower half, grooves round them; round it a rounded diamond at the upper right
(columns 13-22, rows 2-10), a small dome at the right (columns 18-23, rows 10-15), a cushion at the
lower left (columns 0-10, rows 14-23), a small dome right of the middle (columns 14-19, rows 15-19)
and a cushion at the bottom (columns 9-17, rows 19-26). The diamond and the two cushions are
blisters on blisters too: a low rim round a raised middle, a groove between them, the middle a little
towards the upper right (the sprite shows their side walls on the lower left). The sprite draws a highlight along each
one's upper right edge; the model is lit by the game's sun (from the upper left).

The sprite is all the cluster: BUBBLES' ground is black space and glossy orange-red bubbles (ramp 7),
none of which the sprite paints in, so nothing of it is left out. (The same shape glows, red to
yellow, in the animated cluster E 155-165, which has no model of its own here.)

The footprints (superellipses, the pill's narrowing) were fitted to the sprite's outline. Each part
is a lathe of its footprint along a profile; where parts meet, the faces near the other part are
painted dark (a crease between the cushions, a groove round the pill's pad and ridge), cut along a
smooth line, and faces deep inside another part are left out.

Origin at the sprite's centre (pixel 12, 14); +Y up the sprite, +Z towards the camera; the cluster
stands on z = 0.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the
silhouette against enemy_E.png), --preview <prefix>.
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
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
from polish_sphere_nozzle import split_along  # noqa: E402


def pixel(col, row):
    """A sprite pixel's centre (column, row; fractions allowed) in model coordinates."""
    return Vector((col + 0.5 - 12, 13.5 - row))


# The parts: (name, middle (sprite column, row), half-sizes along and across their axis (across: the
# mean), the axis' angle (degrees, counter-clockwise from +X), the power of their outline (2: an
# ellipse, higher: squarer), how much narrower their +axis end is than their -axis end (1: not),
# the height of their foot and their own height, their profile, segments round, and their group
# (parts of one group meet in a groove, others in a crease)).
PARTS = [
    ("pill", (8.95, 10.05), (9.65, 5.45), -39.0, 3.2, 0.75, 0.0, 3.9, "tray", 56, "pill"),
    ("pill_pad", (5.77, 7.15), (3.65, 4.3), -39.0, 2.8, 1.0, 2.1, 2.9, "dome", 40, "pill"),
    ("pill_ridge", (11.94, 12.08), (4.45, 3.25), -39.0, 2.6, 1.0, 2.1, 3.3, "dome", 40, "pill"),
    ("upper_right", (17.8, 6.3), (4.0, 4.5), -39.0, 3.3, 1.0, 0.0, 5.2, "pad", 40, "upper_right"),
    ("right", (20.29, 12.41), (2.84, 2.7), -44.0, 3.2, 1.0, 0.0, 3.6, "dome", 28, "right"),
    ("lower_left", (5.05, 17.88), (5.62, 4.88), -8.0, 1.9, 1.0, 0.0, 4.8, "pad", 44, "lower_left"),
    ("small", (16.8, 16.95), (2.7, 2.4), -54.0, 2.8, 1.0, 0.0, 3.4, "dome", 28, "small"),
    ("bottom", (13.0, 21.69), (4.6, 4.51), 2.0, 1.85, 1.0, 0.0, 5.2, "pad", 40, "bottom"),
]

# Profiles from the outline (r 1) to the middle (r 0): (r, height as a fraction of the part's).
# "pad": a rim swelling to 0.62 at r 0.84, a groove (lowest at r 0.7) and a raised middle;
# "tray": a rim round a low floor (the pill's, under its pad and ridge); "dome": a plain swelling.
PROFILES = {
    "pad": [(1.0, 0.0), (0.996, 0.14), (0.982, 0.3), (0.958, 0.43), (0.925, 0.53), (0.885, 0.59), (0.84, 0.62),
            (0.79, 0.6), (0.745, 0.555), (0.705, 0.53), (0.67, 0.56), (0.64, 0.65), (0.61, 0.75), (0.57, 0.84),
            (0.51, 0.9), (0.42, 0.95), (0.28, 0.985), (0.0, 1.0)],
    "tray": [(1.0, 0.0), (0.995, 0.2), (0.982, 0.42), (0.96, 0.6), (0.93, 0.73), (0.89, 0.81), (0.85, 0.85),
             (0.8, 0.84), (0.72, 0.8), (0.55, 0.76), (0.3, 0.75), (0.0, 0.75)],
    "dome": [(1.0, 0.0), (0.995, 0.18), (0.975, 0.38), (0.94, 0.55), (0.89, 0.68), (0.82, 0.79), (0.72, 0.88),
             (0.58, 0.95), (0.38, 0.99), (0.0, 1.0)],
}
# Where the profiles are painted, on their rings' radii: the pad profile's groove (between these r)
# and raised middle (r below PAD), the profiles' steep sides (r above SIDE) and the dome's top.
GROOVE = (0.67, 0.745)
PAD = 0.67
SIDE = {"pad": 0.925, "tray": 0.93, "dome": 0.94}
DOME_TOP = 0.82
RIM_TOP = 0.84          # the pad profile's rim's crest
# The pad profile's raised middles sit towards the upper right of their rims, as the sprite draws
# them (their side walls show on the lower left): how far (pixels) and which way.
SHIFT = 0.6 * Vector((1.0, 1.0)).normalized()
CREASE = 0.6            # paint a crease where a part of another group is this near (pixels)
GROOVE_WIDTH = 0.35     # paint a groove where a part of the same group is this near
HIDDEN = -0.6           # leave out faces this deep inside another part
FOOT = 0.4              # the dark edge along the ground: z below this
# A gentle unevenness, so that the blisters look grown rather than turned: (amplitude, scale), pixels.
LUMPS = (0.2, 3.2)


class Part:
    def __init__(self, name, centre, half, angle, power, taper, z0, height, profile, segments, group):
        self.name = name
        self.centre = pixel(*centre)
        self.a, self.b = half
        self.angle = math.radians(angle)
        self.power = power
        self.taper = taper
        self.z0 = z0
        self.height = height
        self.kind = profile
        self.profile = PROFILES[profile]
        self.segments = segments
        self.group = group

    def across(self, u):
        """The half-size across the axis at u along it (the narrowing)."""
        t = min(1.0, max(0.0, (u / self.a + 1) / 2))
        return self.b * (1 + (self.taper - 1) * t) / ((1 + self.taper) / 2)

    def shift(self, r):
        """How far the ring at plan radius r is moved towards the upper right (the pad profile's middle)."""
        if self.kind != "pad":
            return Vector((0.0, 0.0))
        t = min(1.0, max(0.0, (RIM_TOP - r) / (RIM_TOP - 0.55)))
        return SHIFT * (t * t * (3 - 2 * t))

    def plan(self, t, scale=1.0):
        """The outline's point at parameter t (radians), shrunk by scale towards the middle."""
        c, s = math.cos(t), math.sin(t)
        cu, sv = math.copysign(abs(c) ** (2 / self.power), c), math.copysign(abs(s) ** (2 / self.power), s)
        u = cu * self.a * scale
        v = sv * self.across(cu * self.a) * scale
        ca, sa = math.cos(self.angle), math.sin(self.angle)
        return self.centre + self.shift(scale) + Vector((u * ca - v * sa, u * sa + v * ca))

    def plan_radius(self, p, shift=None):
        """0 at the middle, 1 on the outline, of the point p (x, y)."""
        d = Vector((p[0], p[1])) - self.centre - (shift if shift is not None else Vector((0.0, 0.0)))
        ca, sa = math.cos(self.angle), math.sin(self.angle)
        u, v = d.x * ca + d.y * sa, -d.x * sa + d.y * ca
        r = 1.0
        for _ in range(3):  # the narrowing depends on where along the outline: settle it
            across = self.across(u / max(r, 1e-3))
            r = (abs(u / self.a) ** self.power + abs(v / across) ** self.power) ** (1 / self.power)
        return r

    def surface_r(self, p):
        """The plan radius of the ring over the point p (x, y), the raised middle's shift accounted for."""
        r = self.plan_radius(p)
        for _ in range(3):
            r = self.plan_radius(p, self.shift(r))
        return r

    def height_at(self, r):
        """The surface's height over plan radius r (below 1) and its slope (height per pixel outwards)."""
        size = min(self.a, self.b)
        for (r0, h0), (r1, h1) in zip(self.profile, self.profile[1:]):  # r decreasing
            if r1 <= r <= r0 and r0 > r1:
                f = (r0 - r) / (r0 - r1)
                return self.z0 + self.height * (h0 + (h1 - h0) * f), self.height * (h0 - h1) / (r0 - r1) / size
        return self.z0 + self.height * self.profile[-1][1], 0.0

    def outer_radius(self, z):
        """The outermost plan radius (0-1) where the surface reaches height z (above its highest
        ring: that ring's)."""
        h = (z - self.z0) / self.height
        if h <= 0:
            return 1.0
        for (r0, h0), (r1, h1) in zip(self.profile, self.profile[1:]):
            if h1 >= h:
                return r0 + (r1 - r0) * (h - h0) / (h1 - h0) if h1 > h0 else r1
        top = max(hh for _, hh in self.profile)
        return max(rr for rr, hh in self.profile if hh >= top)

    def side_gap(self, p):
        """How far the point p is from the part's side at its height (pixels, roughly; negative
        within it), the part's rim taken as solid: where parts press together, the creases."""
        size = min(self.a, self.b)
        if p[2] < self.z0:
            return (self.z0 - p[2]) + max(0.0, self.plan_radius(p) - 1) * size
        top = self.z0 + self.height * max(h for _, h in self.profile)
        r = self.outer_radius(min(p[2], top))
        out = (self.plan_radius(p, self.shift(r)) - r) * size
        if p[2] > top:  # above it: the distance to its highest ring
            return math.hypot(max(0.0, out), p[2] - top)
        return out

    def gap(self, p):
        """How far the point p is outside the part (pixels, roughly; negative inside): the part is
        the ground under its surface, from its foot up, over its outline."""
        r = self.surface_r(p)
        if r >= 1.0:
            return (r - 1.0) * min(self.a, self.b) + max(0.0, self.z0 - p[2])
        if p[2] < self.z0:
            return self.z0 - p[2]
        h, slope = self.height_at(r)
        return (p[2] - h) / math.sqrt(1 + slope * slope)

    def rings(self):
        """(r, z) of the rings from the foot up, with one at FOOT."""
        out = [(r, self.z0 + h * self.height) for r, h in self.profile]
        for (r0, z0), (r1, z1) in zip(out, out[1:]):
            if z0 < FOOT < z1:
                out.append((r0 + (r1 - r0) * (FOOT - z0) / (z1 - z0), FOOT))
                break
        return sorted(out, key=lambda rz: -rz[0])

    def mesh(self):
        rings = []
        for r, z in self.rings()[:-1]:
            rings.append([Vector((*self.plan(2 * math.pi * i / self.segments, r), z)) for i in range(self.segments)])
        top = self.centre + self.shift(0.0)
        return k.loft(self.name, rings, None, cap_start=False,
                      end_point=(top.x, top.y, self.z0 + self.height * self.profile[-1][1]))


def materials():
    return {
        "pad": k.material("bubbles_pad", palette=0x46, roughness=0.46),
        "rim": k.material("bubbles_rim", palette=0x45, roughness=0.48),
        "side": k.material("bubbles_side", palette=0x44, roughness=0.5),
        "groove": k.material("bubbles_groove", palette=0x43, roughness=0.55),
        "crease": k.material("bubbles_crease", palette=0x42, roughness=0.65),
    }


def paint(part, r, z):
    """The colour of the band of the part's faces between two rings (r and z: its middle)."""
    if z < FOOT:
        return "crease"
    if r > SIDE[part.kind]:
        return "side"
    if part.kind == "pad":
        if GROOVE[0] < r < GROOVE[1]:
            return "groove"
        return "pad" if r < PAD else "rim"
    if part.kind == "tray":
        return "rim"
    return "pad" if r < DOME_TOP else "rim"


def unevenness(obj, seed):
    """Moves the surface in and out a little along its normals, not at the ground."""
    amplitude, scale = LUMPS
    offset = Vector((seed * 7.3, seed * 3.1, seed * 5.7))
    for v in obj.data.vertices:
        fade = min(1.0, max(0.0, (v.co.z - FOOT) / 1.2))
        if fade > 0:
            v.co += v.normal * amplitude * fade * noise.noise(v.co / scale + offset)


def build_cluster(mats):
    parts = [Part(*p) for p in PARTS]
    objects = []
    for part in parts:
        others = [o for o in parts if o is not part]
        kin = [o for o in others if o.group == part.group]
        # (Parts standing inside another, the pill's pad and ridge, meet other groups through it.)
        strangers = [o for o in others if o.group != part.group and o.z0 <= 0]

        def nearest(p, among, side=True):
            return min([o.side_gap(p) if side else o.gap(p) for o in among] or [99.0])

        obj = part.mesh()
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        # Each face's band between two rings (the loft makes them band by band, the top's fan last),
        # kept by the faces the cuts below make of it.
        rings = part.rings()
        band = bm.faces.layers.int.new("band")
        bm.faces.ensure_lookup_table()
        for f in bm.faces:
            f[band] = min(f.index // part.segments, len(rings) - 2)
        # Cut along the creases' and grooves' borders and round the hidden faces (triangles first:
        # a border crosses a triangle at most once). Creases: where another cushion's side is near;
        # grooves: where the surface of another part of the pill is.
        for among, threshold, side in ((strangers, CREASE, True), (kin, GROOVE_WIDTH, False), (others, HIDDEN, False)):
            bmesh.ops.triangulate(bm, faces=bm.faces[:])
            split_along(bm, {v: nearest(v.co, among, side) for v in bm.verts}, threshold)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        hidden = [f for f in bm.faces if nearest(f.calc_center_median(), others, side=False) < HIDDEN]
        bmesh.ops.delete(bm, geom=hidden, context="FACES")
        keys = []
        for f in bm.faces:
            c = f.calc_center_median()
            if nearest(c, strangers) < CREASE:
                keys.append("crease")
            elif nearest(c, kin, side=False) < GROOVE_WIDTH:
                keys.append("groove")
            else:
                (r0, z0), (r1, z1) = rings[f[band]], rings[f[band] + 1]
                keys.append(paint(part, (r0 + r1) / 2, (z0 + z1) / 2))
        bm.to_mesh(obj.data)
        bm.free()
        names = []
        for poly, key in zip(obj.data.polygons, keys):
            if mats[key].name not in names:
                names.append(mats[key].name)
                obj.data.materials.append(mats[key])
            poly.material_index = names.index(mats[key].name)
        k.recalc_normals(obj)
        unevenness(obj, len(objects) + 1)
        k.smooth(obj, 60)
        objects.append(obj)
    return objects


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
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    k.reset()
    build_cluster(materials())
    used = {m.name for obj in bpy.context.scene.objects if obj.type == "MESH" for m in obj.data.materials}
    print("== bubbles (E 153): %d triangles, %d materials" % (triangles(), len(used)))
    if "check" in options:
        sheet = options["check"]
        k.check_silhouette(os.path.join(sheet, "enemy_E.png") if os.path.isdir(sheet) else sheet, 153)
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    path = os.path.join(outdir, "bubbles.glb")
    k.export(path)
    print("%s: %d bytes" % (path, os.path.getsize(path)))
    if "preview" in options:
        k.preview(options["preview"] + "bubbles")


if __name__ == "__main__":
    build()
