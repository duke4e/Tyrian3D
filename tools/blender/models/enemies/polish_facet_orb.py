"""The faceted orbs of GEM WAR and TIME WAR, polished (2026-10-21; they replace wave2_e.py's facet_orb(), a gem
of sixteen crown points round a diamond table): one cut gem in the shades of the blue orb's ramp, which models.cfg's
color=sprite gives each sprite's colour, and two frame models for its pulse.

The sprites (sheet V, 2x2: an 18 x 18 orb in the 24 x 28 cell), the same picture in three ramps, pixel for pixel
(every shade equal; checked over all 276 pixels): V 153 in ramp 3 (light blue), V 191 in ramp 2 (green), V 123 in
ramp 4 (pink); each pulses darker: 155, 193 and 125 are the same picture two shades darker (one pixel of 125 a shade
off), 157, 195 and 127 four shades darker (the darkest shades clamped at 0); V 229, 231 and 233 are the same in yet
another ramp (no enemy shows them). Who shows them:
- GEM WAR (episode 2): the orbs the gem launchers (V 91, enemies 807, 808, 797) launch: enemy 802 (153 155 157 155,
  four game frames each; still, homing in on the player), 803 (191 193 195 193; moving down) and 799 (123 125 127
  125; moving down, homing across; also STATION and GRYPHON); on the launcher's layer (sky, ground 2, top).
- TIME WAR (episode 4): enemies 673 (V 153), 674 (155 157 159 ..., once when it fires; 159 is another picture) and
  675 (195 193 191 ..., the green one).
models.cfg: model facet_orb, facet_orb_155, facet_orb_157 enemies/....glb; sprite v 153 / 155 / 195 facet_orb yaw=0
color=sprite (unchanged) and sprite v 191 / 123 facet_orb yaw=0 color=sprite (new); frame v 155, 193, 125
facet_orb_155 and frame v 157, 195, 127 facet_orb_157: the darker frames show the darker models, whichever enemy
shows them (the frames are the same pictures darker, so they fit every one of them).

As the sprites and the 4x upscales of V 153 and V 191 draw it: a cushion-cut gem in a rounded outline (columns 3-20
of rows 5-22, a circle squared off a little, the girdle a dark outline), lit from the upper left. In its middle a
table like a diamond (a square turned 45 degrees, its corners up, down, left and right, |x| + |y| below 4.8),
light, glowing white in its middle (0x3f, columns 12-13 of rows 14-15); round it a dark channel (0x35-0x38, |x| + |y|
4.8-6.4); outside it the crown, in four corners each with a light ridge running from the channel out to the
girdle's corner (the upscale's X of light streaks), the facets either side light blue (0x3a-0x3d), brightest in the
lower right corner (0x3e, 0x3f: the light through the gem), and a dark band inside the girdle.

Built as such a gem, of flat facets (flat shaded, as a cut stone): the table a very low pyramid (its four facets
catch the light differently) with its glint (emission 0.16 in white: white is every ramp's lightest shade, so
color=sprite needs no other colour of it; the light facets glow a little in white too, 0.02-0.06) in the middle; the
channel a shallow V cut round it; the crown four roofs,
each two planar facets meeting along a raised ridge over the diagonal (from the channel's edge, where the ridge is
highest, out and down to the girdle's corner) and sloping down to valleys over the axes, so the girdle undulates with
them; the ridges' strips (RIDGE_W either side) and the lower right corner lighter, a dark band RIM_IN wide inside the
girdle; the girdle a band of the outline's dark blue round the gem; the pavilion below, eight facets down to a point.
The game's camera sees the facets lit and shaded by its sun, so the shades are the sprite's lighter ones (the crown
0x3c, the table 0x3e: checked in the game's view). Palette materials of ramp 3 only, so
color=sprite gives every one of them the frame's ramp; the frame models are the same gem in shades two and four
darker (their glint dimmer). The faces are split along the ridges' strips (polish_sphere_nozzle.split_along) and
triangulated before export (the same split every run).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; origin at the
sprite's centre (pixel 12, 14), the gem's middle there (columns 3-20, rows 5-22: pixel 11.5, 13.5 is x 0, y 0); the
game centres it in height (on the ground it lifts it onto the ground).

Replaces wave2_e.py's facet_orb(): remove the function with its @model("facet_orb", "V", 153) line and the "TIME WAR's
faceted orbs" section header, and the facet_orb bullet of its docstring (wave3_ap_station.py loads wave2_e with
kit.load for station_end() only; nothing else reads facet_orb).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each model's silhouette
against its sprite in enemy_V.png), --preview <prefix>, --only <name,...> (facet_orb, facet_orb_155, facet_orb_157),
--ramp <0-15> (for checks: the models in another ramp, as color=sprite shows them, written as <name>_r<ramp>.glb).
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_sphere_nozzle import split_along  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402

# name, sprite, how many shades darker than 153
MODELS = [("facet_orb", 153, 0), ("facet_orb_155", 155, 2), ("facet_orb_157", 157, 4)]
RAMP = 3

# The plan: the girdle a superellipse (half size, power: a circle squared off a little), the table, the channel's
# floor and the crown's inner edge diamonds (|x| + |y| = these).
GIRDLE_HALF, GIRDLE_POWER = 9.0, 2.45
TABLE_L1, CHANNEL_L1, CROWN_L1, GLINT_L1 = 4.8, 5.6, 6.4, 2.3
# Heights: the table's edge and how much its middle rises (a low pyramid); the channel's floor; the crown's inner edge
# at the diamond's corners (the valleys) and at its edges' middles (the ridges' tops); the girdle's corner (the ridges'
# ends); the girdle band's height; the pavilion's point.
TABLE_Z, TABLE_DOME, CHANNEL_Z = 4.6, 0.35, 2.95
CROWN_Z_CORNER, CROWN_Z_RIDGE, GIRDLE_Z_CORNER = 3.25, 3.9, 1.15
GIRDLE_H, CULET_Z = 0.7, -3.6
STEPS = 8          # directions per quadrant (11.25 degrees apart): the rings' points
RIDGE_W = 0.38     # the ridges' light strips: this far either side of the ridge, in plan

# The materials: (key, shade of 153's ramp, roughness, white emission strength).
SHADES = {
    "glint": (15, 0.15, 0.16),
    "table": (14, 0.18, 0.04),
    "channel": (9, 0.3, 0.0),
    "crown": (12, 0.22, 0.02),
    "crown_lit": (14, 0.2, 0.05),       # the lower right corner, where the light through the gem shows
    "ridge": (15, 0.18, 0.06),
    "rim": (7, 0.3, 0.0),               # the crown's outer band, inside the girdle (the sprite's dark ring)
    "girdle": (2, 0.35, 0.0),
    "pavilion": (5, 0.3, 0.0),
}
RIM_IN = 1.0       # the crown's dark outer band: this far in from the girdle (in plan)
WHITE = (205, 205, 205)


def superellipse(theta):
    """The girdle's point in the direction theta (radians)."""
    c, s = math.cos(theta), math.sin(theta)
    r = GIRDLE_HALF / (abs(c) ** GIRDLE_POWER + abs(s) ** GIRDLE_POWER) ** (1.0 / GIRDLE_POWER)
    return Vector((r * c, r * s))


def diamond(theta, l1):
    c, s = math.cos(theta), math.sin(theta)
    r = l1 / (abs(c) + abs(s))
    return Vector((r * c, r * s))


def quadrant_signs(theta):
    q = int(math.floor(theta / (math.pi / 2) + 1e-9)) % 4
    return [(1, 1), (-1, 1), (-1, -1), (1, -1)][q]


class Crown:
    """The crown's facets: in each quadrant two planes through the ridge (from the crown's inner edge at the diagonal,
    CROWN_Z_RIDGE high, to the girdle's corner) and the diamond's corners (CROWN_Z_CORNER high)."""

    def __init__(self):
        g = superellipse(math.pi / 4)
        m = CROWN_L1 / 2
        self.m, self.g = Vector((m, m, CROWN_Z_RIDGE)), Vector((g.x, g.y, GIRDLE_Z_CORNER))
        # The plane of the first quadrant's facet towards +x (through the corner (CROWN_L1, 0)).
        c = Vector((CROWN_L1, 0.0, CROWN_Z_CORNER))
        n = (self.m - c).cross(self.g - c)
        if n.z < 0:
            n = -n
        self.n, self.c = n, c

    def z(self, x, y):
        """The crown's height over the point (x, y)."""
        sx, sy = (1 if x >= 0 else -1), (1 if y >= 0 else -1)
        u, v = abs(x), abs(y)
        if v > u:               # the facet towards +y: the mirror image across the diagonal
            u, v = v, u
        n, c = self.n, self.c
        return c.z - (n.x * (u - c.x) + n.y * (v - c.y)) / n.z


def ridge_distance(p):
    """How far the plan point p is from the nearest ridge (the diagonals, outside the crown's inner edge)."""
    return abs(abs(p.x) - abs(p.y)) / math.sqrt(2.0)


def gem_bmesh():
    """The gem as rings of points in the same directions (STEPS a quadrant, the diagonals and the axes among them),
    joined by quads; each face tagged with its part."""
    crown = Crown()
    n = 4 * STEPS
    thetas = [2 * math.pi * i / n for i in range(n)]
    bm = bmesh.new()
    part = bm.faces.layers.int.new("part")

    def ring(points):
        return [bm.verts.new(p) for p in points]

    def table_z(l1):
        return TABLE_Z + TABLE_DOME * (1.0 - l1 / TABLE_L1)

    rings = []
    rings.append(("glint", ring([diamond(t, GLINT_L1).to_3d() + Vector((0, 0, table_z(GLINT_L1))) for t in thetas])))
    rings.append(("table", ring([diamond(t, TABLE_L1).to_3d() + Vector((0, 0, TABLE_Z)) for t in thetas])))
    rings.append(("channel", ring([diamond(t, CHANNEL_L1).to_3d() + Vector((0, 0, CHANNEL_Z)) for t in thetas])))
    crown_in = [diamond(t, CROWN_L1) for t in thetas]
    rings.append(("channel", ring([Vector((p.x, p.y, crown.z(p.x, p.y))) for p in crown_in])))
    girdle = [superellipse(t) for t in thetas]
    rim = [p * ((p.length - RIM_IN) / p.length) for p in girdle]
    rings.append(("crown", ring([Vector((p.x, p.y, crown.z(p.x, p.y))) for p in rim])))
    rings.append(("rim", ring([Vector((p.x, p.y, crown.z(p.x, p.y))) for p in girdle])))
    rings.append(("girdle", ring([Vector((p.x, p.y, crown.z(p.x, p.y) - GIRDLE_H)) for p in girdle])))
    top = bm.verts.new((0.0, 0.0, table_z(0.0)))
    culet = bm.verts.new((0.0, 0.0, CULET_Z))
    # The glint: a fan round the table's top.
    first = rings[0][1]
    for i in range(n):
        f = bm.faces.new((top, first[i], first[(i + 1) % n]))
        f[part] = 0
    names = ["glint", "table", "channel", "channel_out", "crown", "rim", "girdle"]
    for r in range(len(rings) - 1):
        inner, outer = rings[r][1], rings[r + 1][1]
        kind = names.index(rings[r + 1][0] if r + 1 != 3 else "channel_out")
        for i in range(n):
            j = (i + 1) % n
            f = bm.faces.new((inner[i], outer[i], outer[j], inner[j]))
            f[part] = kind
    last = rings[-1][1]
    for i in range(n):
        f = bm.faces.new((last[(i + 1) % n], last[i], culet))
        f[part] = 7
    bm.normal_update()
    return bm, part


def materials(darker):
    mats = {}
    for key, (shade, rough, glow) in SHADES.items():
        s = max(0, shade - darker)
        strength = glow * (1.0 - darker * 0.14)
        mats[key] = k.material(f"facet_{key}_{s:x}", palette=16 * RAMP + s, metallic=0.15, roughness=rough,
                               emission=WHITE if strength > 0 else None, emission_strength=max(0.0, strength))
    return mats


def build_gem(darker):
    mats = materials(darker)
    bm, part = gem_bmesh()
    # The ridges' strips: the crown's faces cut along RIDGE_W from the diagonals.
    split_along(bm, {v: ridge_distance(v.co) for v in bm.verts}, RIDGE_W)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    keys = []
    for f in bm.faces:
        c = f.calc_center_median()
        kind = ["glint", "table", "channel", "channel", "crown", "rim", "girdle", "pavilion"][f[part]]
        if kind == "crown":
            if ridge_distance(c) < RIDGE_W:
                kind = "ridge"
            elif c.x > 0 and c.y < 0:
                kind = "crown_lit"
        keys.append(kind)
    mesh = bpy.data.meshes.new("facet_orb")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("facet_orb", mesh)
    bpy.context.scene.collection.objects.link(obj)
    order = [key for key in SHADES if key in keys]      # the materials the faces use, in SHADES' order
    for key in order:
        mesh.materials.append(mats[key])
    for poly, key in zip(mesh.polygons, keys):
        poly.material_index = order.index(key)
        poly.use_smooth = False
    k.recalc_normals(obj)
    return [obj]


def recolour(objects, ramp):
    """The models in another ramp, as color=sprite shows them (for checks)."""
    for obj in objects:
        for i, m in enumerate(obj.data.materials):
            name, index = m.name.rsplit("@", 1)
            new = k.material(name + "_r%d" % ramp, palette=16 * ramp + (int(index) & 15), metallic=0.15,
                             roughness=m.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value)
            new.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 0.15
            bsdf = m.node_tree.nodes["Principled BSDF"]
            nb = new.node_tree.nodes["Principled BSDF"]
            nb.inputs["Emission Color"].default_value = bsdf.inputs["Emission Color"].default_value
            nb.inputs["Emission Strength"].default_value = bsdf.inputs["Emission Strength"].default_value
            obj.data.materials[i] = new


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    ramp = int(options["ramp"]) if "ramp" in options else None
    for name, sprite, darker in MODELS:
        if only and name not in only:
            continue
        k.reset()
        objects = build_gem(darker)
        triangulate(objects)  # the same split every run (with and without --check)
        bpy.context.view_layer.update()
        if "check" in options:
            sheets = options["check"]
            sheet = os.path.join(sheets, "enemy_V.png") if os.path.isdir(sheets) else sheets
            mk.compare("%s (V %d)" % (name, sprite), mk.coverage(objects, 24, 28), k.sprite_mask(sheet, sprite))
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        suffix = ""
        if ramp is not None:
            recolour(objects, ramp)
            suffix = "_r%d" % ramp
        mk.report(name + suffix, objects, os.path.join(out, name + suffix + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name + suffix, objects, scale=20, distance=0.55)


if __name__ == "__main__":
    build()
