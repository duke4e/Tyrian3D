"""WINDY's blue-white plasma ball, which the bronze blocks with the blue gem (M 17, block_gem, enemy 846 of episodes 1
and 4) launch every 50 and 100 game ticks (sheet M sprites 129 and 131, 2x2; enemy 850, frames 129 129 131 cycling;
still: move 0, 0; armour 15). The blocks are ground enemies moving down the screen 2 pixels a tick faster than the
ground (WINDY's events: type 6, dat3 2), so the balls, made on ground 2 (slots 75-99, drawn on the ground), stay
behind them on the ground in a trail. Polished (2026-10-21; it had no model: the game drew a pixelated stand-in).
models.cfg: model plasma_ball enemies/plasma_ball.glb origin, model plasma_ball_131 enemies/plasma_ball_131.glb
origin; sprite m 129 plasma_ball yaw=0 height=-4 glow=26:0.3:157 (drawn at their origin, height=-4 sets them on the
ground, WINDY's raised ground too: a model centred in height would sink 5 pixels into it), frame m 131
plasma_ball_131 (no other enemy shows M 129 or 131; ^ 163 and 165 are the same pixels, and no enemy shows those
either).

As the sprites draw it (the 4x upscales have no picture of it), round and the same all round (no light falls on it:
it shines): 129 a disc 18 pixels across round the cell's centre, white (0x8f) out to 4 pixels from its middle, then
rings of pale cyan (0x8d, 0x8b, 0x8a, 0x89), light blue (0x9e, 0x9d), blue (0x9b, 0x9a), dark blue and teal (ramps
3 and 13) and a dark violet outline (0x51) at 9 pixels; 131 is the same ball a pixel larger all round (20 pixels
across, the white out to 5), one game frame in three: it throbs.

Built as an energy ball: a white-hot core that gives its own light (an opaque sphere of radius CORE_R, white in its
middle and pale cyan round its edge as the camera sees it, glowing 0.42-0.6), in a corona (a see-through
sphere of pale cyan, radius CORONA_R, nearly clear over the core and denser round it), in a soft shell (a
see-through sphere of radius SHELL_R, the sprite's ball with its outline): nearly clear where the camera looks
straight through it, denser and bluer towards its rim as the camera sees it, the dark blue and teal at its very edge,
each band glowing faintly in its own colour (0.2-0.4; the game's bloom and the glow halo add on top). The game draws
see-through materials blended, in the order of their materials and then of their triangles, without culling and
without writing depth: the core comes first (opaque), then the corona, then the shell; the see-through spheres'
bands are set by how squarely the camera looks at a face, either way (the far half seen through the near one, as
clear in the middle and as dense at the rim, so that its bands lie under the near half's), and each band's faces are
sorted from the far side to the near side (the model doesn't turn). 131's model is 129's with every radius a pixel more
(a frame model: the sprite throbs, which the glow halo, the same for both frames, would not show; both stand on the
ground, so the larger one's middle is a pixel higher, as a swelling ball's).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground; origin at the
sprite's centre (pixel 12, 14), the ball's middle there, SHELL_R up (it stands on the ground).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each model's silhouette
against its sprite in enemy_M.png), --preview <prefix>, --only <name,...> (plasma_ball, plasma_ball_131).
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

# name, sprite, how much larger than 129 (pixels)
MODELS = [("plasma_ball", 129, 0.0), ("plasma_ball_131", 131, 1.0)]

VIEW_TILT = 20.0
T = math.radians(VIEW_TILT)
TOWARDS_VIEW = Vector((0.0, -math.sin(T), math.cos(T)))

# 129's radii: the core (the white), the corona (the pale cyan rings) and the shell (the ball with its outline).
CORE_R, CORONA_R, SHELL_R = 5.9, 7.4, 9.0
# The core: white in its middle, pale cyan round its edge as the camera sees it: (the view-facing factor (normal .
# towards the camera) the band starts at, palette index, emission strength).
CORE_BANDS = [(-1.0, 0x89, 0.42), (0.3, 0x8b, 0.48), (0.55, 0x8d, 0.52), (0.72, 0x8f, 0.6)]
# The corona: bands by how squarely the camera looks at it, either way: nearly clear over the core, pale cyan round it
# (lowest factor, palette index, alpha, emission strength).
CORONA_BANDS = [(-9.0, 0x89, 0.3, 0.4), (0.3, 0x8b, 0.36, 0.45), (0.6, 0x8d, 0.04, 0.4)]
# The shell: bands by the view-facing factor, from its middle out to its rim: (lowest factor, palette index, alpha,
# emission strength).
SHELL_BANDS = [(0.75, 0x9e, 0.06, 0.3), (0.63, 0x9d, 0.16, 0.34), (0.54, 0x9b, 0.3, 0.38), (0.45, 0x9a, 0.45, 0.38),
               (0.33, 0xd4, 0.6, 0.3), (0.2, 0xd3, 0.72, 0.25), (-0.3, 0x34, 0.82, 0.15)]


def facing(n):
    return n.dot(TOWARDS_VIEW)


def squarely(n):
    """How squarely the camera looks at a face of a see-through sphere, from the outside or through it."""
    return abs(n.dot(TOWARDS_VIEW))


def sphere_bmesh(centre, radius, subdivisions):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdivisions, radius=1.0)
    for v in bm.verts:
        v.co = centre + v.co.normalized() * radius
    return bm


def to_object(name, bm, mats, keys):
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    for m in mats:
        mesh.materials.append(m)
    for poly, key in zip(mesh.polygons, keys):
        poly.material_index = key
    k.recalc_normals(obj)
    return k.smooth(obj, 80.0)


def banded(name, centre, radius, subdivisions, field, bands, mats, far_first=False):
    """A sphere cut along the contours of field(direction) at the bands' borders, each face the material of its band
    (bands ascending: (lowest value, ...)); far_first: its faces sorted from the camera's far side to its near side."""
    bm = sphere_bmesh(centre, radius, subdivisions)
    for lowest, *_ in bands[1:]:
        split_along(bm, {v: field((v.co - centre).normalized()) for v in bm.verts}, lowest)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    if far_first:
        bm.faces.ensure_lookup_table()
        bm.faces.sort(key=lambda f: (f.calc_center_median() - centre).dot(TOWARDS_VIEW))
        bm.faces.index_update()
    keys = []
    for f in bm.faces:
        value = field((f.calc_center_median() - centre).normalized())
        keys.append(max(i for i, band in enumerate(bands) if i == 0 or value > band[0]))
    return to_object(name, bm, mats, keys)


def materials():
    pal = k.level_palette()
    core = [k.material(f"plasma_core_{index:02x}", palette=index, metallic=0.0, roughness=0.5, emission=pal[index],
                       emission_strength=strength) for _, index, strength in CORE_BANDS]
    corona = [k.material(f"plasma_corona_{index:02x}", palette=index, metallic=0.0, roughness=0.3, alpha=alpha,
                         emission=pal[index], emission_strength=strength) for _, index, alpha, strength in CORONA_BANDS]
    # The shell's bands from its rim in (ascending factors).
    shell = [k.material(f"plasma_shell_{index:02x}", palette=index, metallic=0.0, roughness=0.15, alpha=alpha,
                        emission=pal[index], emission_strength=strength)
             for _, index, alpha, strength in reversed(SHELL_BANDS)]
    return core, corona, shell


def build_ball(grow):
    core_mats, corona_mats, shell_mats = materials()
    shell_r = SHELL_R + grow
    centre = Vector((0.0, 0.0, shell_r))
    core = banded("plasma_core", centre, CORE_R + grow, 3, facing, CORE_BANDS, core_mats)

    corona = banded("plasma_corona", centre, CORONA_R + grow, 4, squarely, CORONA_BANDS, corona_mats, far_first=True)
    shell_bands = [(lowest,) for lowest, *_ in reversed(SHELL_BANDS)]
    shell_bands[0] = (-9.0,)
    shell = banded("plasma_shell", centre, shell_r, 4, squarely, shell_bands, shell_mats, far_first=True)
    return [core, corona, shell]   # in the order the game must draw them


def opaque_coverage(objects, w, h):
    """The top view's coverage with the see-through materials made opaque for it (the ball's own outline)."""
    saved = []
    for m in {m for obj in objects for m in obj.data.materials}:
        bsdf = m.node_tree.nodes["Principled BSDF"]
        saved.append((m, bsdf.inputs["Alpha"].default_value, m.surface_render_method))
        bsdf.inputs["Alpha"].default_value = 1.0
        m.surface_render_method = "DITHERED"
    covered = mk.coverage(objects, w, h)
    for m, alpha, method in saved:
        m.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = alpha
        m.surface_render_method = method
    return covered


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    for name, sprite, grow in MODELS:
        if only and name not in only:
            continue
        k.reset()
        objects = build_ball(grow)
        triangulate(objects)  # the same split every run (with and without --check)
        bpy.context.view_layer.update()
        if "check" in options:
            sheets = options["check"]
            sheet = os.path.join(sheets, "enemy_M.png") if os.path.isdir(sheets) else sheets
            mk.compare("%s (M %d)" % (name, sprite), opaque_coverage(objects, 24, 28), k.sprite_mask(sheet, sprite))
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, objects, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, objects, scale=20, distance=0.6)


if __name__ == "__main__":
    build()
