"""The dark red glass orb of FLEET, STATION and THE CORE (sheet K sprite 195, 2x2: 24 x 28 pixels; enemy 734 of
episodes 3 and 6, 1056 of episode 5, sky layer, indestructible (armour 255); one frame, not animated), polished
(2026-10-21; it replaces wave1_c.py's orb_crimson(), a plain see-through sphere over a core, with a halo glowing at
2.4 and an ember at 4.0 that the game's bloom burnt white). models.cfg: model orb_crimson enemies/orb_crimson.glb;
sprite k 195 orb_crimson yaw=0 (unchanged; no glow: the levels send the orbs in columns, two to six of them one
every five steps at the same place, moving down together (FLEET and STATION six over the pincer's machine, on its
link), so that they overlap by half and their halos would add up).

No other sprite has its pixels (mirrored, turned or in other ramps), and no other enemy shows it.

As the sprite and its 4x upscale draw it: a glass ball 21 pixels across in its dark outline (columns 2-22, rows 2-22),
very dark red (palette ramp 7, shades 0-3), lighter towards the upper left, darker to the lower right; up on its left
a white-hot spot (columns 8-11 of rows 7-11: shades 12-15) in rings of orange and red; inside its rim at the lower
right a bright crescent (columns 13-21 of rows 12-21, hottest at column 18, row 18), where the light through the
glass gathers.

Built as such a marble (polish_purpleball.py's method): the glass a sphere of radius GLASS_R, glossy (the game's sun
puts its glint up on the left, where the sprite has its spot) and see-through, glowing faintly in its own dark red
so that its shaded side stays red; in bands by height, as the camera always looks down on it (20 degrees from
straight down): dense round its sides (the dark outline), clearer towards its top; the crescent painted on its lower
right side where the camera sees it inside the rim, an arc in three bands glowing red to orange; over the ember a
window, clearer and lit by it in three bands (the upscale's orange glow round the spot). Inside, under the spot, the
ember: a lumpy coal (an icosphere pushed in and out by Perlin noise at fixed offsets: the same every run) glowing
white-hot on top, orange and red down its sides, darker crust in patches; its base colours dark, so that it shows
its own light rather than the sun's. Emission strengths stay well under 1 (0.15-0.65; the bloom adds to them).

The game draws see-through materials blended, in the order of their materials and then of their triangles, without
culling and without writing depth: the ember is opaque; the glass is the model's last object, its materials from
the bottom up (the crescent's between its lower and upper bands, the window's last) and its faces sorted from the
bottom up, so that its far side is drawn before its near side.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; origin at the
sprite's centre (pixel 12, 14). The ball's middle is where the sprite draws it, half a pixel right of and a pixel and
a half above the origin (it does not turn); the game centres it in height.

Replaces wave1_c.py's orb_crimson(): remove it together with its MODELS entry ("orb_crimson": (orb_crimson, "K",
195); wave3_ap_deli.py loads wave1_c for deli_arm(), and an entry left naming a removed function would break that
load) and its lines in the docstring; the "Round ones" header, ellipsoid_part() and the file's other helpers stay
(purple_pod() and the others use them).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against
enemy_K.png), --preview <prefix>.
"""
import math
import os
import sys

import bmesh
import bpy
import mathutils.noise as noise
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402

NAME = "orb_crimson"
CENTRE = Vector((0.5, 1.5, 0.0))     # the sprite's ball: columns 2-22, rows 2-22

# The glass: its radius, finish, icosphere. Its bands by height, from the bottom up: (the band's lower border as the
# normal's z, palette index, alpha, emission index, strength). Two lit regions painted over them, with their bands
# (lowest heat, palette index, alpha, emission index, strength): the crescent inside the rim at the lower right (its
# direction in plan, degrees from +x, and spread in radians; the normal's z it rises from, peaks at, falls to), and
# the window over the ember, clearer and lit by it (the upscale's orange glow round the spot: its direction, a unit
# vector from the ball's middle, and spread). The materials go from the bottom up: the glass's two lower bands, the
# crescent's, the upper bands, the window's.
GLASS_R = 10.3
GLASS_FINISH = dict(metallic=0.0, roughness=0.12)
GLASS_SUBDIVISIONS = 5
GLASS_BANDS = [(-1.0, 0x71, 0.86, 0x72, 0.15), (0.3, 0x72, 0.78, 0x72, 0.18), (0.62, 0x72, 0.68, 0x73, 0.2),
               (0.8, 0x73, 0.6, 0x73, 0.22)]
CRESCENT = (-48.0, 0.72, (0.17, 0.43, 0.7))
CRESCENT_BANDS = [(0.22, 0x73, 0.8, 0x74, 0.26), (0.45, 0x75, 0.78, 0x76, 0.36), (0.72, 0x77, 0.74, 0x79, 0.46)]
CRESCENT_AFTER = 1
# The ember: its middle (from the ball's), radius, how lumpy, its icosphere; the heat over it (from its top, the
# crust's patches) and its bands: (lowest heat, palette index of its base colour, of its light, strength); the base
# colours are dark, so that it shows its own light rather than the sun's.
EMBER = (Vector((-2.2, 1.9, 2.4)), 2.4, 0.07, 4)
EMBER_CRUST = 0.15
EMBER_BANDS = [(-9.0, 0x71, 0x76, 0.36), (0.5, 0x72, 0x79, 0.48), (0.72, 0x73, 0x7b, 0.56), (0.88, 0x74, 0x7e, 0.65)]
WINDOW = ((EMBER[0] + Vector((0.0, 0.0, 7.0))).normalized(), 0.38)
WINDOW_BANDS = [(0.22, 0x72, 0.6, 0x75, 0.22), (0.48, 0x73, 0.5, 0x77, 0.3), (0.74, 0x74, 0.42, 0x79, 0.38)]


def materials():
    pal = k.level_palette()

    def glassy(name, bands):
        return [k.material(f"{name}{i}", palette=index, alpha=alpha, emission=pal[glow], emission_strength=strength,
                           **GLASS_FINISH) for i, (_, index, alpha, glow, strength) in enumerate(bands)]
    ember = [k.material(f"orb_ember{i}", palette=index, metallic=0.0, roughness=0.6, emission=pal[glow],
                        emission_strength=strength)
             for i, (_, index, glow, strength) in enumerate(EMBER_BANDS)]
    return {"glass": glassy("orb_glass", GLASS_BANDS), "crescent": glassy("orb_crescent", CRESCENT_BANDS),
            "window": glassy("orb_window", WINDOW_BANDS), "ember": ember}


def from_bmesh(name, bm):
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def crescent_heat(d):
    """The crescent's heat at the glass's direction d (a unit vector from the ball's middle): an arc round the rim."""
    angle, spread, (z0, zp, z1) = CRESCENT
    off = math.atan2(d.y, d.x) - math.radians(angle)
    off = (off + math.pi) % (2 * math.pi) - math.pi
    return math.exp(-(off / spread) ** 2) * mk.smoothstep(z0, zp, d.z) * mk.smoothstep(z1, zp, d.z)


def window_heat(d):
    """The window's heat at the glass's direction d: round the point over the ember."""
    direction, spread = WINDOW
    return math.exp(-(d.angle(direction) / spread) ** 2)


def glass(mats):
    """The glass sphere in its bands, the crescent and the window over the ember, its materials from the bottom up
    and its faces sorted from the bottom up."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=GLASS_SUBDIVISIONS, radius=1.0)
    borders = [band[0] for band in GLASS_BANDS[1:]]
    for t in borders:
        mk.split_along(bm, {v: v.co.normalized().z for v in bm.verts}, t)
    for heat, bands in ((crescent_heat, CRESCENT_BANDS), (window_heat, WINDOW_BANDS)):
        for lowest, *_ in bands:
            mk.split_along(bm, {v: heat(v.co.normalized()) for v in bm.verts}, lowest)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    for v in bm.verts:
        v.co = CENTRE + v.co.normalized() * GLASS_R
    bm.faces.ensure_lookup_table()
    bm.faces.sort(key=lambda f: f.calc_center_median().z)
    bm.faces.index_update()
    order = mats["glass"][:CRESCENT_AFTER + 1] + mats["crescent"] + mats["glass"][CRESCENT_AFTER + 1:] + mats["window"]
    keys = []
    for f in bm.faces:
        d = (f.calc_center_median() - CENTRE).normalized()
        mat = mats["glass"][sum(d.z > t for t in borders)]
        for heat_of, bands, lit in ((crescent_heat, CRESCENT_BANDS, mats["crescent"]),
                                    (window_heat, WINDOW_BANDS, mats["window"])):
            heat = heat_of(d)
            for (lowest, *_), band_mat in zip(bands, lit):
                if heat > lowest:
                    mat = band_mat
        keys.append(order.index(mat))
    obj = from_bmesh("glass", bm)
    for mat in order:
        obj.data.materials.append(mat)
    for poly, key in zip(obj.data.polygons, keys):
        poly.material_index = key
    k.recalc_normals(obj)
    return k.smooth(obj, 80.0)


def ember(mats):
    """The lumpy coal inside, under the sprite's spot, in bands of heat (white-hot on top, crust in patches)."""
    offset, radius, lumps, subdivisions = EMBER
    middle = CENTRE + offset
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdivisions, radius=1.0)
    heat = {}
    for v in bm.verts:
        d = v.co.normalized()
        bump = noise.noise(d * 1.7 + Vector((4.0, 2.0, 9.0)))
        v.co = middle + d * radius * (1.0 + lumps * bump)
        crust = noise.noise(d * 2.9 + Vector((1.0, 7.0, 3.0)))
        heat[v] = 0.5 + 0.5 * d.z - EMBER_CRUST * max(0.0, crust)
    for lowest, *_ in EMBER_BANDS[1:]:
        mk.split_along(bm, heat, lowest)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    keys = []
    for f in bm.faces:
        h = sum(heat[v] for v in f.verts) / len(f.verts)
        keys.append(sum(h > band[0] for band in EMBER_BANDS[1:]))
    obj = from_bmesh("ember", bm)
    for mat in mats["ember"]:
        obj.data.materials.append(mat)
    for poly, key in zip(obj.data.polygons, keys):
        poly.material_index = key
    k.recalc_normals(obj)
    return k.smooth(obj, 80.0)


def build():
    options = k.args()
    out = mk.outdir(options)
    k.reset()
    mats = materials()
    parts = [ember(mats), glass(mats)]       # the glass last: its materials are the model's last
    bpy.context.view_layer.update()
    if "check" in options:
        sheet = os.path.join(options["check"], "enemy_K.png")
        mk.compare("orb_crimson (K 195)", mk.coverage(parts, 24, 28), k.sprite_mask(sheet, 195))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mk.report(NAME, parts, os.path.join(out, NAME + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + NAME, parts, distance=0.6)


if __name__ == "__main__":
    build()
