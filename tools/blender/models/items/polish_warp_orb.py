"""The warp orb (sheet P sprite 85, 2x2, 24 x 28 pixels: enemies 577, 591, 593, 688, 690, 695, 823 and 843 of episodes 1-4
and 1500 of episode 6, armour 0, value 10000 + the secret level's number: flying into it takes the player to a secret
level; about 15 in ASTEROID1, MINEMAZE, ASTEROID2, ASTEROID?, TYRIAN, GYGES, ASTCITY, STARGATE, LAVA EXIT, SURFACE, ICE
EXIT and GREY MOON, mostly dropped by enemies, a few placed on the ground or in the sky), polished (2026-10-22, round 32;
it replaces wave2_g.py's warp_orb(), a dome painted in the sprite's shades over a darker ball). Its animation 85 85 131
131 233 233 131 131 (one game frame each) brightens it and back: 131 is 85 about two shades lighter, 233 five (to
white), shade for shade. No other enemy shows P 85, 131 or 233; it is no other sprite's pixels mirrored, turned or in
other ramps.

As the sprite and its 4x upscales draw it: a ball of fire 21 pixels across in a black outline (columns 1-21, rows
4-24), all in ramp 7: dark reds round its lower left (0x70-0x74), oranges, a white-hot spot at its upper left
(columns 7-9 of rows 10-11, 0x7f), and lighter streaks of fire curling round it from the hot spot down to its lower
right (columns 13-18 of rows 17-21): a swirl.

It is a pick-up like the purple ball (powerups 41, polish_purpleball.py: a marble of Tyrian purple glass with a vortex
of light inside it), so it is built as its fiery sibling, a marble of dark red glass with a vortex of fire inside:
- the glass: a sphere of radius GLASS_R (the sprite's ball with its outline), glossy, see-through, in bands by height
  (dense and dark red lower down, a dark rim round the ball as the sprite's outline; clearer towards its top, a window
  onto the core; the band under its middle glowing more: the light gathering in the glass), glowing faintly in red
  so that its shaded side stays red;
- the core: a sphere of radius CORE_R giving its own light (emission in its colours over a darkened base colour),
  shaded from its top: orange-red round its middle (where the camera sees its edge), through orange to yellow at its
  top; over it FILAMENTS tongues of yellow flame swirling out from its top, each with a pale line along its inner
  part, arching over the core, and a pale dome where they meet (the eye).
The game draws see-through materials blended in the order of their materials and then of their triangles, without
culling and without writing depth: the glass's bands are its last materials, from the bottom up, its faces sorted from
the bottom up (polish_purpleball.py's order). Emission strengths stay under 1 (the bloom and the cfg glow add on top).
The frames 131 and 233: the same meshes, the glass one and two palette shades lighter, the core one and three (to 0x7e:
white-hot behind red glass would read pink) and glowing more (frame models warp_orb_131, warp_orb_233: the same
bounds).

The orb turns (spin=2, the swirl's tongues trailing, as the purple ball turns); it is centred on the origin (the sprite's
centre; the sprite draws it half a pixel left of and below it) so that it turns in place.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; origin at the
sprite's centre (pixel 12, 14). The game centres it in height on its layer.

models.cfg: model warp_orb items/warp_orb.glb (was enemies/warp_orb.glb: the old GLB assets/models/enemies/warp_orb.glb
goes), new model warp_orb_131 items/warp_orb_131.glb and model warp_orb_233 items/warp_orb_233.glb; sprite p 85
warp_orb spin=2 glow (was yaw=0 glow); new frame p 131 warp_orb_131 and frame p 233 warp_orb_233.

Replaces wave2_g.py's warp orb: its section "P 85: the warp orb" (shade_bands() and warp_orb() with its @model
registration; sampler() and gauss() only they used), its docstring line, and wave2_g_art.py's P85.

Options after "--": --outdir <dir> (default assets/models/items), --check <sheets dir> (the silhouette against
enemy_P.png, also moved to where the sprite draws the ball), --preview <prefix>, --only <name,...>.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "enemies"))
import polish_item_kit as kit  # noqa: E402
from polish_item_kit import k  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402

SPRITE_CENTRE = (-0.5, -0.5)      # where the sprite draws the ball's middle (for the silhouette check)
FRAMES = [("warp_orb", 85, 0), ("warp_orb_131", 131, 1), ("warp_orb_233", 233, 2)]   # (model, sprite, step)

# The glass: radius, finish, icosphere; its bands from the bottom up: (lower border as the normal's z, palette index,
# alpha, emission strength); each frame step lightens them by a shade.
GLASS_R = 10.35
GLASS_FINISH = dict(metallic=0.0, roughness=0.18)
GLASS_SUBDIVISIONS = 4
GLASS_BANDS = [(-1.0, 0x73, 0.85, 0.2), (-0.6, 0x75, 0.8, 0.28), (-0.42, 0x76, 0.78, 0.36), (-0.2, 0x75, 0.78, 0.26),
               (0.0, 0x74, 0.72, 0.2), (0.4, 0x75, 0.58, 0.18), (0.62, 0x76, 0.48, 0.16)]
# The core: radius, icosphere; its bands from the bottom up: (lower border as the normal's z, palette index, emission);
# its base colour the palette colour darkened (CORE_ALBEDO), each frame step a shade lighter.
CORE_R = 8.1
CORE_SUBDIVISIONS = 4
CORE_BANDS = [(-1.0, 0x76, 0.46), (0.25, 0x78, 0.5), (0.5, 0x7a, 0.53), (0.7, 0x7c, 0.57), (0.86, 0x7d, 0.6)]
CORE_ALBEDO = 0.55
CORE_FINISH = dict(metallic=0.0, roughness=0.35)
FRAME_GLOW = (0.0, 0.06, 0.14)    # added to every core strength in each frame step
CORE_STEP = (0, 1, 3)             # and the core's shades lighter by this
# The swirl (polish_purpleball.py's): FILAMENTS tongues from the top (polar angle FILAMENT_FROM, degrees) down to
# FILAMENT_TO, turning TWIST radians for each radian down; each FILAMENT_W across at its widest, FILAMENT_LIFT over the
# core and arching FILAMENT_ARCH higher along its middle, in the top's colour; along its first FILAMENT_HOT of its
# length a lighter line FILAMENT_CORE of its width; the eye at the top.
FILAMENTS, TWIST = 5, 2.3
FILAMENT_FROM, FILAMENT_TO = 6.0, 80.0
FILAMENT_W, FILAMENT_CORE, FILAMENT_HOT = 1.45, 0.42, 0.6
FILAMENT_LIFT, FILAMENT_ARCH = 0.05, 0.55
FILAMENT_SEGMENTS = 36
EYE_R, EYE_SINK = 1.3, 0.5
TONGUE = 3                        # the tongues take the core's band of this index (the line and the eye: LIGHT)
LIGHT = (0x7e, 0.62)


def shade(index, step, top=0x7e):
    return min(top, index + step) if index >> 4 == 7 else index


def glowing(name, index, strength):
    """A palette colour giving its own light: emission in it over the colour darkened (so the sun doesn't wash it out
    and nothing passes the bloom's threshold)."""
    pal = k.level_palette()
    colour = pal[index]
    return k.material(name, color=tuple(c * CORE_ALBEDO for c in colour), emission=colour, emission_strength=strength,
                      **CORE_FINISH)


def materials(step):
    pal = k.level_palette()
    m = {"glass": [k.material(f"warp{step}_glass{i}", palette=shade(index, step), alpha=alpha,
                              emission=pal[shade(index, step)], emission_strength=strength, **GLASS_FINISH)
                   for i, (_, index, alpha, strength) in enumerate(GLASS_BANDS)]}
    extra = FRAME_GLOW[step]
    m["core"] = [glowing(f"warp{step}_core{i}", shade(index, CORE_STEP[step]), strength + extra)
                 for i, (_, index, strength) in enumerate(CORE_BANDS)]
    m["tongue"] = m["core"][TONGUE]
    m["light"] = glowing(f"warp{step}_light", shade(LIGHT[0], step, 0x7f), min(0.68, LIGHT[1] + extra))
    return m


def painted_sphere(name, radius, subdivisions, borders, mats):
    """An icosphere, its faces cut along the heights borders (the normal's z), each band its material (from the
    bottom up)."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdivisions, radius=1.0)
    for t in borders:
        kit.split_along(bm, {v: v.co.normalized().z for v in bm.verts}, t)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    keys = [sum(f.calc_center_median().normalized().z > t for t in borders) for f in bm.faces]
    for v in bm.verts:
        v.co = v.co.normalized() * radius
    obj = kit.from_bmesh(name, bm)
    for mat in mats:
        obj.data.materials.append(mat)
    for poly, key in zip(obj.data.polygons, keys):
        poly.material_index = key
    k.recalc_normals(obj)
    return k.smooth(obj, 80.0)


def glass(mats):
    """The glass sphere in its bands, its faces in order from the bottom up (drawn far side first: the camera looks
    down on it)."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=GLASS_SUBDIVISIONS, radius=1.0)
    borders = [band[0] for band in GLASS_BANDS[1:]]
    for t in borders:
        kit.split_along(bm, {v: v.co.normalized().z for v in bm.verts}, t)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    for v in bm.verts:
        v.co = v.co.normalized() * GLASS_R
    bm.faces.ensure_lookup_table()
    bm.faces.sort(key=lambda f: f.calc_center_median().z)
    bm.faces.index_update()
    bands = [sum(f.calc_center_median().z / GLASS_R > t for t in borders) for f in bm.faces]
    obj = kit.from_bmesh("glass", bm)
    for mat in mats:
        obj.data.materials.append(mat)
    for poly, band in zip(obj.data.polygons, bands):
        poly.material_index = band
    k.recalc_normals(obj)
    return k.smooth(obj, 80.0)


def filament(name, phase, width, lift, mat, length=1.0):
    """A tongue over the core along the swirl, width across at its widest, tapering to both ends, lift over the core,
    arching FILAMENT_ARCH higher along its middle (polish_purpleball.filament)."""
    left, right = [], []
    n = max(4, int(round(FILAMENT_SEGMENTS * length)))
    for i in range(n + 1):
        t = i / n
        radius = CORE_R + lift + FILAMENT_ARCH * math.sin(math.pi * t * length)
        theta = math.radians(FILAMENT_FROM + (FILAMENT_TO - FILAMENT_FROM) * t * length)
        phi = phase + TWIST * theta
        d = Vector((math.sin(theta) * math.cos(phi), math.sin(theta) * math.sin(phi), math.cos(theta)))
        along = Vector((math.cos(theta) * math.cos(phi) - TWIST * math.sin(theta) * math.sin(phi),
                        math.cos(theta) * math.sin(phi) + TWIST * math.sin(theta) * math.cos(phi),
                        -math.sin(theta))).normalized()
        side = d.cross(along).normalized()
        w = width * math.sin(math.pi * t ** 0.75) ** 0.8 / 2
        left.append((d * radius + side * w).normalized() * radius)
        right.append((d * radius - side * w).normalized() * radius)
    faces = [(i, i + 1, n + 2 + i, n + 1 + i) for i in range(n)]
    obj = k.mesh_object(name, left + right, faces, mat)
    mesh = obj.data
    for poly in mesh.polygons:
        poly.use_smooth = True
        if poly.normal.dot(poly.center) < 0:
            poly.flip()
    mesh.normals_split_custom_set_from_vertices([v.co.normalized() for v in mesh.vertices])
    return obj


def join(name, objects):
    with bpy.context.temp_override(selected_editable_objects=objects, active_object=objects[0],
                                   selected_objects=objects):
        bpy.ops.object.join()
    objects[0].name = name
    objects[0].data.name = name
    return objects[0]


def core(m):
    borders = [band[0] for band in CORE_BANDS[1:]]
    parts = [painted_sphere("core", CORE_R, CORE_SUBDIVISIONS, borders, m["core"])]
    for i in range(FILAMENTS):
        phase = 2 * math.pi * i / FILAMENTS
        parts.append(filament(f"tongue{i}", phase, FILAMENT_W, FILAMENT_LIFT, m["tongue"]))
        parts.append(filament(f"tongue{i}_line", phase, FILAMENT_W * FILAMENT_CORE, FILAMENT_LIFT * 2, m["light"],
                              FILAMENT_HOT))
    parts.append(k.smooth(k.ellipsoid("eye", (0.0, 0.0, CORE_R - EYE_SINK), (EYE_R, EYE_R, EYE_R), m["light"],
                                      16, 8), 80.0))
    return join("core", parts)


def build():
    opts = kit.options()
    for name, sprite, step in FRAMES:
        if not kit.wanted(opts, name):
            continue
        k.reset()
        m = materials(step)
        parts = [core(m), glass(m["glass"])]
        triangulate(parts)
        obj = join(name, parts)
        bpy.context.view_layer.update()
        if "check" in opts:
            sheet = opts["check"]
            sheet = os.path.join(sheet, "enemy_P.png") if os.path.isdir(sheet) else sheet
            mask = kit.sprite_mask(sheet, sprite, True)
            kit.compare("%s (P %d)" % (name, sprite), kit.coverage([obj], 24, 28), mask)
            kit.compare("%s moved by (%g, %g)" % ((name,) + SPRITE_CENTRE),
                        kit.coverage([obj], 24, 28, shift=SPRITE_CENTRE), mask)
        bpy.context.scene.view_settings.view_transform = "Standard"
        kit.report(name, [obj], os.path.join(kit.outdir(opts), name + ".glb"))
        if "preview" in opts:
            kit.preview(opts["preview"] + name, [obj], (24, 28), scale=16, distance=0.6)


if __name__ == "__main__":
    build()
