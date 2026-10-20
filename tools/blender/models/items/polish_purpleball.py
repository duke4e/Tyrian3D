"""Purple ball (the power-ups sheet's sprite 41, enemy type 628 with value 30000: the ball enemies leave most often,
power for the weapons, experience in a rogue run; 2x2, 24 x 28 pixels; about 1000 of them in the levels, the item
seen most), polished (2026-10-20; it replaces purpleball.py's plain glossy sphere). models.cfg: sprite powerups 41
purpleball spin=2 glow=-1.25:0.5:#66023c. One sprite, no animation; no other enemy shows it.

As the sprite and its 4x upscale draw it: a glossy glass marble 21 pixels across with its dark outline (columns
2-22, rows 3-23), a muted purple (palette ramp 5), a white highlight above its middle on the left (columns 8-10,
rows 8-10), darker towards the lower right, and a bright crescent inside its rim at the lower right, where the
light through the glass gathers.

The user chose its colour: Tyrian purple (#66023c), for the ball and its glow. Tyrian purple is dark, and the game's
camera sees mostly the ball's side away from the sun (the plain sphere read as a dark blob), so the ball is a marble
of Tyrian purple glass with light inside it, a vortex of lighter magenta and pink energy:

- the glass: a sphere of radius GLASS_R (the sprite's ball with its outline), glossy (the game's sun puts its glint
  above the middle on the left, where the sprite draws its highlight), see-through, glowing faintly in magenta so
  that its shaded side stays purple. Thick glass is darker where one looks through more of it, round its sides, and
  the camera always looks down on the ball (20 degrees from straight down, whichever way it turns), so the glass is
  in bands by height: dense lower down (a dark rim round the ball, as the sprite's outline), clearest at its top (a
  window onto the core); the band under its middle glows more (the caustic: the sprite's bright crescent inside its
  lower rim, a ring so that it stays below whichever way the ball turns; the camera sees it as a lighter rim);
- the core: a sphere of radius CORE_R in the middle that gives its own light (emission in its colours over a darkened
  base colour, so that the sun doesn't wash it out and nothing passes the game's bloom threshold), shaded from its
  top: darkest round its middle (where the camera sees its edge), lightest at its top; over it four ribbons of pink
  light swirl out from its top, each with a lighter line along its inner part, arching a little over the core, and
  a small dome of the lightest pink where they meet (the eye).

The game draws see-through materials blended, in the order of their materials and then of their triangles, without
culling and without writing depth: the glass's bands are its last materials, from the bottom up, and its faces are
sorted from the bottom up, so that its far side is drawn before its near side for any turn (the camera looks down
on it). Emission strengths stay well under 1 (the bloom and the cfg glow add on top); only the sun's glint on the
glass passes 1.0, over about a game pixel (as the plain sphere's glint).

The ball turns (spin=2: clockwise seen from above, the swirl's arms trailing); it is centred on the origin (the
sprite's centre; the sprite draws it half a pixel right of and above it) so that it turns in place.

Options after "--": --outdir <dir> (default assets/models/items), --check <sheets dir> (the silhouette against
powerups.png), --preview <prefix>.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_item_kit as kit  # noqa: E402
from polish_item_kit import k  # noqa: E402

NAME = "purpleball"
SPRITE = 41
# Where the sprite draws the ball's middle (for the silhouette check): pixel (12.5, 13.5) of 24 x 28.
SPRITE_CENTRE = (0.5, 0.5)

# Tyrian purple and lighter colours of its hue (325 degrees): sRGB 0-255.
TYRIAN = (0x66, 0x02, 0x3c)
MAGENTA = (217, 11, 131)
PINK = (255, 77, 181)
HOT = (255, 166, 218)

# The glass: its radius, finish and icosphere. Its bands by height, from the bottom up: (the band's lower border as
# the normal's z, alpha, emission colour, emission strength): dense up to above its middle, the caustic under the
# middle in three steps, clearer towards the top in three.
GLASS_R = 10.25
GLASS_FINISH = dict(metallic=0.0, roughness=0.19)
GLASS_SUBDIVISIONS = 5
GLASS_BANDS = [(-1.0, 0.8, MAGENTA, 0.15), (-0.62, 0.8, PINK, 0.18), (-0.46, 0.79, PINK, 0.3),
               (-0.24, 0.8, PINK, 0.18), (-0.1, 0.8, MAGENTA, 0.15), (0.35, 0.73, MAGENTA, 0.14),
               (0.52, 0.65, MAGENTA, 0.12), (0.68, 0.57, MAGENTA, 0.1)]

# The core: its radius and icosphere; its bands by height, from the bottom up: (the band's lower border as the
# normal's z, colour, emission strength); its base colour is the colour darkened (CORE_ALBEDO times the sRGB
# values).
CORE_R = 8.0
CORE_SUBDIVISIONS = 4
CORE_BANDS = [(-1.0, TYRIAN, 0.5), (0.2, (125, 4, 75), 0.42), (0.4, (160, 6, 97), 0.42), (0.55, MAGENTA, 0.42),
              (0.7, (235, 40, 155), 0.48), (0.84, PINK, 0.55)]
CORE_ALBEDO = 0.55
CORE_FINISH = dict(metallic=0.0, roughness=0.35)
# The swirl: FILAMENTS ribbons over the core from its top (the polar angle FILAMENT_FROM, degrees) down to
# FILAMENT_TO, turning TWIST radians round the core for each radian down (counter-clockwise outwards seen from
# above: trailing as the ball turns clockwise); each FILAMENT_W pixels across at its widest, tapering to its ends,
# FILAMENT_LIFT over the core and arching FILAMENT_ARCH higher along its middle, in the core's top colour; along its
# first FILAMENT_HOT of its length a lighter line (LIGHT) FILAMENT_CORE of its width. The eye: a dome of radius
# EYE_R at the top, EYE_SINK into the core, in LIGHT.
FILAMENTS, TWIST = 4, 2.2
FILAMENT_FROM, FILAMENT_TO = 6.0, 78.0
FILAMENT_W, FILAMENT_CORE, FILAMENT_HOT = 1.3, 0.42, 0.62
FILAMENT_LIFT, FILAMENT_ARCH = 0.05, 0.5
FILAMENT_SEGMENTS = 40
EYE_R, EYE_SINK = 1.25, 0.5
LIGHT = (HOT, 0.6)


def painted_sphere(name, radius, subdivisions, borders, pick, mats):
    """An icosphere of the radius, its faces cut along the heights borders (the normal's z, so that the colours meet
    along smooth circles), then painted: pick(the normal's z at a face's middle) gives its material's index in
    mats."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdivisions, radius=1.0)
    for t in borders:
        kit.split_along(bm, {v: v.co.normalized().z for v in bm.verts}, t)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    keys = [pick(f.calc_center_median().normalized().z) for f in bm.faces]
    for v in bm.verts:
        v.co = v.co.normalized() * radius
    obj = kit.from_bmesh(name, bm)
    for poly, key in zip(obj.data.polygons, keys):
        poly.material_index = kit.slot_of(obj, mats[key])
    k.recalc_normals(obj)
    return k.smooth(obj, 80.0)


def glass(mats):
    """The glass sphere in its bands (mats: a material per band, from the bottom up), its faces in order from the
    bottom up."""
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
    """A ribbon over the core along the swirl from FILAMENT_FROM down to FILAMENT_TO (or length of the way),
    starting at the azimuth phase (radians), width pixels across at its widest, tapering to both ends, lift over the
    core and arching FILAMENT_ARCH higher along its middle."""
    left, right = [], []
    n = max(4, int(round(FILAMENT_SEGMENTS * length)))
    for i in range(n + 1):
        t = i / n
        radius = CORE_R + lift + FILAMENT_ARCH * math.sin(math.pi * t * length)
        theta = math.radians(FILAMENT_FROM + (FILAMENT_TO - FILAMENT_FROM) * t * length)
        phi = phase + TWIST * theta
        d = Vector((math.sin(theta) * math.cos(phi), math.sin(theta) * math.sin(phi), math.cos(theta)))
        # Along the swirl: the derivative of d by theta.
        along = Vector((math.cos(theta) * math.cos(phi) - TWIST * math.sin(theta) * math.sin(phi),
                        math.cos(theta) * math.sin(phi) + TWIST * math.sin(theta) * math.cos(phi),
                        -math.sin(theta))).normalized()
        side = d.cross(along).normalized()
        # Widest a third of the way, pointed at both ends.
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
    # Normals as the sphere's (outwards), so that the ribbon shades as the core under it.
    mesh.normals_split_custom_set_from_vertices([v.co.normalized() for v in mesh.vertices])
    return obj


def join(name, objects):
    """Joins the objects into one (their custom normals kept)."""
    with bpy.context.temp_override(selected_editable_objects=objects, active_object=objects[0],
                                   selected_objects=objects):
        bpy.ops.object.join()
    objects[0].name = name
    objects[0].data.name = name
    return objects[0]


def core(mats):
    """The core with its swirl and eye, one object."""
    borders = [band[0] for band in CORE_BANDS[1:]]
    ball = painted_sphere("core", CORE_R, CORE_SUBDIVISIONS, borders, lambda z: sum(z > t for t in borders),
                          mats["core"])
    parts = [ball]
    for i in range(FILAMENTS):
        phase = 2 * math.pi * i / FILAMENTS
        parts.append(filament(f"filament{i}", phase, FILAMENT_W, FILAMENT_LIFT, mats["core"][-1]))
        parts.append(filament(f"filament{i}_line", phase, FILAMENT_W * FILAMENT_CORE, FILAMENT_LIFT * 2,
                              mats["light"], FILAMENT_HOT))
    parts.append(k.smooth(k.ellipsoid("eye", (0.0, 0.0, CORE_R - EYE_SINK), (EYE_R, EYE_R, EYE_R), mats["light"],
                                      16, 8), 80.0))
    return join("core", parts)


def materials():
    mats = {"glass": [k.material(f"{NAME}_glass{i}", color=TYRIAN, alpha=alpha, emission=colour,
                                 emission_strength=strength, **GLASS_FINISH)
                      for i, (_, alpha, colour, strength) in enumerate(GLASS_BANDS)]}
    def glowing(name, colour, strength):
        return k.material(name, color=tuple(c * CORE_ALBEDO for c in colour), emission=colour,
                          emission_strength=strength, **CORE_FINISH)
    mats["core"] = [glowing(f"{NAME}_core{i}", colour, strength)
                    for i, (_, colour, strength) in enumerate(CORE_BANDS)]
    mats["light"] = glowing(f"{NAME}_light", *LIGHT)
    return mats


def check(opts, objects):
    """The silhouette against the sprite (powerups.png), also with the ball moved to where the sprite draws it."""
    if "check" not in opts:
        return
    sheet = opts["check"]
    if os.path.isdir(sheet):
        sheet = os.path.join(sheet, "powerups.png")
    mask = kit.sprite_mask(sheet, SPRITE, True)
    kit.compare("purpleball (powerups 41)", kit.coverage(objects, 24, 28), mask)
    kit.compare("purpleball moved by (%g, %g)" % SPRITE_CENTRE, kit.coverage(objects, 24, 28, shift=SPRITE_CENTRE),
                mask)


def build():
    opts = kit.options()
    k.reset()
    mats = materials()
    # The core first, the glass last: its bands' materials are the model's last, from the bottom up.
    parts = [core(mats), glass(mats["glass"])]
    check(opts, parts)
    bpy.context.scene.view_settings.view_transform = "Standard"
    path = os.path.join(kit.outdir(opts), NAME + ".glb")
    kit.report(NAME, parts, path)
    if "preview" in opts:
        kit.preview(opts["preview"] + NAME, parts, (24, 28), scale=16, distance=0.6)
    return path


if __name__ == "__main__":
    build()
