"""SURFACE's stepped pyramid on the sand (sheet 3 sprites 153 and 155 above 191 and 193, 2x2 each: one 48 x 56
picture; ground layer; enemies 208-211) and its golden capstone (sheet 3 sprite 3, 1x1; ground2 layer; enemies
225-227, frames 3 4 5 5 5 4 4 4 3 when it fires), polished (2026-10-19; they replace wave3_n_rocks.py's
pyramid_whole() and pyramid_cap(), bevelled boxes in flat shades). models.cfg: model pyramid_153 / pyramid_155 /
pyramid_191 / pyramid_193 / pyramid_cap ... origin (and pyramid_cap_4, pyramid_cap_5, frame models); sprite 3 153
pyramid_153 yaw=0 height=-4 (and 155, 191, 193), sprite 3 3 pyramid_cap yaw=0 height=-4, frame 3 4 pyramid_cap_4,
frame 3 5 pyramid_cap_5. (A glow option on the capstone shows nothing: the game draws a glow at its layer's height,
4 pixels up, inside the pyramid under the capstone, which stands CAP_BASE higher; its own emission is its glow.)
The levels place the four as a block (event 12, "4-part enemy": 208 (191) at (x, y), 209 (193) at
(x + 24, y), 210 (153) at (x, y - 28), 211 (155) at (x + 24, y - 28)) and the capstone on its top (event 10, on the
ground2 layer: x + 10, y - 33, every time: SURFACE's events 916 to 5704): its sprite's centre is the picture's pixel
(22, 9). Both layers are the ground enemies' (4 pixels up). None of these sprites is another sprite's pixels mirrored
or recoloured; the pyramid's sprites draw the capstone (3 3's pixels) on top, the capstone's enemy draws it again over
them (and can be shot away: the model leaves the platform bare for that).

As the sprites and their 4x upscales draw it (ramp 1's golden browns; the sand round it is the map's, ramp 10, left
out): four levels, symmetric about the picture's column 21 (x = -2.5 here), each smaller and higher than the one
under it: a broad base (columns 2-40, its front a tall dark face, rows 37-42), three tiers on it (their fronts dark
risers two rows tall, rows 31-32, 25-26 and 19-20, their treads four rows deep in front of them, lighter towards
their fronts' edges), the sides stepping in by three or four columns a level, lit on the left (1a-1d) and in a mid
shade on the right (15-17); the back stepping up the screen two rows a level (rows 11, 9, 7, 5: the levels' backs
seen over each other); on the top platform the capstone, a pyramid of gold (rows 2-15, columns 16-27), its left
face lit, its front in shadow, which brightens to a glow in its frames 4 and 5 (each two shades lighter).

Built as such a pyramid of golden stone, so that seen from above its levels lie where the sprites draw them and the
game's slanted camera sees its fronts: each level a block from below the sand to its top, its back upright (each
reaching further back than the one under it, as the sprites' backs step up), its front and sides battered (the
base's front a broad talus, the tiers' fronts steep risers), its top edges bevelled; courses of stone along the
risers (thin grooves) and joints across the treads; the faces painted as the sprites shade them (fronts dark, left
sides lit, right sides mid, treads mid, their front edges lit). The capstone a pyramidion of gold on a plinth,
standing on the top platform at CAP_BASE: its model's origin is its sprite's centre, so it stands where the
levels put it; a little emission in its own shades, more in its frame models (pyramid_cap_4, pyramid_cap_5).
The levels reach SKIRT below the sand (z = 0), so the pyramid stands on the terrain with height=-4 or without it
(the capstone with the same height option as the pyramid).

The pyramid is built whole and cut along the sprites' edges into the four pieces (polish_arch.py's cut(): the
pieces keep the whole's shading across the cuts), each moved so its sprite's centre is its origin.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the sand (z = 0); the
whole's origin is the corner where the four sprites meet: P(c, r) turns the picture's pixel edges (column c, row r)
into these coordinates (x = c - 24, y = 28 - r).

Replaces wave3_n_rocks.py's pyramid: remove PYRAMID_ORIGIN, CAP_CENTRE, CAP_BASE, TIERS, frustum(),
pyramid_whole(), pyramid_piece(), its n.pieced("pyramid", ...) registration and pyramid_cap() (with its
@n.model("pyramid_cap", ...) line); the rock arch stays.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the
whole and of each piece against the pyramid's pixels in enemy_3.png, the capstone's against 3 3), --preview
<prefix>, --only <model,...>.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_arch import cut  # noqa: E402  (polish_machine_kit.cut without its material indices shifted twice)

# The pieces: (name, sprite, the box it covers in the whole's coordinates (x0, x1, y0, y1)).
PIECES = [("pyramid_153", 153, (-24.0, 0.0, 0.0, 28.0)), ("pyramid_155", 155, (0.0, 24.0, 0.0, 28.0)),
          ("pyramid_191", 191, (-24.0, 0.0, -28.0, 0.0)), ("pyramid_193", 193, (0.0, 24.0, -28.0, 0.0))]
SPRITE_AT = {153: (0, 0), 155: (24, 0), 191: (0, 28), 193: (24, 28)}  # top left corners in the 48 x 56 picture


def P(c, r):
    """A pixel edge of the 48 x 56 picture (column c, row r) in the whole's coordinates."""
    return (c - 24.0, 28.0 - r)


AXIS_X = -2.5
SKIRT = -4.0
# The levels (pixel edges of the picture): the left side's foot and top, the right side's foot and top, the front's
# foot and top, the back (columns and rows), and the level's top height.
LEVELS = [
    (2, 3, 41, 40, 43, 37, 11, 4.6),
    (5, 6, 38, 37, 33, 31, 9, 7.8),
    (9, 10, 34, 33, 27, 25, 7, 11.0),
    (12, 13, 31, 30, 21, 19, 3.2, 14.2),
]
BEVEL = 0.32                           # the levels' top edges
CORNER = 0.35                          # their corners' radius (seen from above)
COURSE = 1.6                           # the stone courses along the risers: their height
JOINT = 4.0                            # the joints across the treads: how far apart

# The capstone (its own model): its sprite's centre in the whole, where its pyramidion stands (relative to that), its
# plinth (half-width, height) and its pyramidion (half-width at its foot, height).
CAP_CENTRE = P(22, 9)
CAP_AT = (AXIS_X - CAP_CENTRE[0], P(0, 9.3)[1] - CAP_CENTRE[1])
CAP_BASE = LEVELS[-1][7]
CAP_PLINTH = (6.1, 0.6)
CAP_BODY = (5.6, 9.0)
CAP_TIP = 0.72                         # its gilded tip: above this share of its height
# The capstone's frames: (model, sprite, how many shades lighter, emission strength).
CAP_FRAMES = [("pyramid_cap", 3, 0, 0.3), ("pyramid_cap_4", 4, 2, 0.6), ("pyramid_cap_5", 5, 4, 1.0)]


def materials():
    def mat(name, index, metallic=0.3, roughness=0.5):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)
    return {
        "tread": mat("pyr_tread", 0x19, 0.45, 0.32),
        "edge": mat("pyr_edge", 0x1c, 0.5, 0.24),
        "south": mat("pyr_south", 0x16, 0.4, 0.38),
        "west": mat("pyr_west", 0x1c, 0.45, 0.3),
        "east": mat("pyr_east", 0x19, 0.45, 0.32),
        "north": mat("pyr_north", 0x17, 0.4, 0.35),
        "groove": mat("pyr_groove", 0x12, 0.2, 0.7),
        "seam": mat("pyr_seam", 0x12, 0.2, 0.7),
    }


# --- Helpers ------------------------------------------------------------------------------------------------------

def rrect(x0, x1, y0, y1, r, z, steps=3):
    """A rectangle with rounded corners at height z, counter-clockwise; every corner steps + 1 points."""
    out = []
    for (ox, oy, a0) in ((x0 + r, y0 + r, 180), (x1 - r, y0 + r, 270), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90)):
        for i in range(steps + 1):
            a = math.radians(a0 + 90 * i / steps)
            out.append(Vector((ox + r * math.cos(a), oy + r * math.sin(a), z)))
    return out


def level_plan(spec):
    """A level's plan at its foot and at its top: (x0, x1, y0, y1) each."""
    wf, wt, ef, et, ff, ft, back, _ = spec
    yb = P(0, back)[1]
    foot = (P(wf, 0)[0], P(ef, 0)[0], P(0, ff)[1], yb)
    top = (P(wt, 0)[0], P(et, 0)[0], P(0, ft)[1], yb)
    return foot, top


def classify(n, c, z_top):
    """Which of a level's faces a face is: its tread, the bevel along its top edges, or a side by its direction."""
    if n.z > 0.97:
        return "tread"
    if c.z > z_top - BEVEL - 0.03 and n.z > 0.3:
        return "edge"
    if abs(n.y) >= abs(n.x):
        return "south" if n.y < 0 else "north"
    return "west" if n.x < 0 else "east"


# --- The pyramid --------------------------------------------------------------------------------------------------

def level(i, spec, z0, m):
    """A level: a block from below the sand, upright under the level below's top, battered from there to its own
    top, its top edges bevelled."""
    foot, top = level_plan(spec)
    z1 = spec[7]
    rings = [rrect(*foot, CORNER, SKIRT), rrect(*foot, CORNER, z0)]
    steps = 4
    for s in range(1, steps + 1):  # the batter
        f = s / steps
        plan = [a + (b - a) * f for a, b in zip(foot, top)]
        rings.append(rrect(*plan, CORNER, z0 + (z1 - BEVEL - z0) * f))
    for a in (30, 60, 90):  # the bevel over the top edge
        t = math.radians(a)
        inset = BEVEL * (1 - math.cos(t))
        x0, x1, y0, y1 = top
        rings.append(rrect(x0 + inset, x1 - inset, y0 + inset, y1 - inset, max(CORNER - inset, 0.05),
                           z1 - BEVEL + BEVEL * math.sin(t)))
    x0, x1, y0, y1 = top
    obj = k.loft(f"level{i}", rings, m["tread"], start_point=((foot[0] + foot[1]) / 2, (foot[2] + foot[3]) / 2, SKIRT),
                 end_point=((x0 + x1) / 2, (y0 + y1) / 2, z1))
    k.smooth(obj, 35)
    mk.paint(obj, lambda c, n: m[classify(n, c, z1)])
    return obj


def courses(i, spec, z0, m):
    """The masonry of a level's front: grooves along it (courses of stone, about COURSE high) and joints between the
    blocks (staggered course by course): dark strips just proud of the face."""
    foot, top = level_plan(spec)
    z1 = spec[7]
    dy, dz = top[2] - foot[2], z1 - BEVEL - z0
    n = Vector((0.0, -dz, dy)).normalized()      # out of the face
    up = Vector((0.0, dy, dz)).normalized()      # up the face

    def at(x, f, lift=0.03):
        """The point on the front at x and at the share f of its height."""
        return Vector((x, foot[2] + dy * f, z0 + dz * f)) + n * lift

    def side(f):
        return foot[0] + (top[0] - foot[0]) * f + CORNER + 0.1, foot[1] + (top[1] - foot[1]) * f - CORNER - 0.1
    count = max(1, round(dz / COURSE))
    verts, faces = [], []

    def strip(p0, p1, across):
        base = len(verts)
        verts.extend([p0 - across, p1 - across, p1 + across, p0 + across])
        faces.append((base, base + 1, base + 2, base + 3))
    for j in range(1, count):  # the courses
        f = j / count
        x0, x1 = side(f)
        strip(at(x0, f), at(x1, f), up * 0.08)
    for j in range(count):  # the joints, staggered
        fa, fb = j / count + 0.04, (j + 1) / count - 0.04
        x0, x1 = side(fb)
        x = AXIS_X + (JOINT * 0.75 if j % 2 else 0.0)
        xs = []
        while x - JOINT * 1.5 > x0:
            x -= JOINT * 1.5
        while x < x1 - 0.4:
            if x > x0 + 0.4:
                xs.append(x)
            x += JOINT * 1.5
        for x in xs:
            strip(at(x, fa), at(x, fb), Vector((0.07, 0.0, 0.0)))
    obj = k.mesh_object(f"masonry{i}", verts, faces, m["groove"])
    for poly in obj.data.polygons:
        if poly.normal.dot(n) < 0:
            poly.flip()
    obj.data.update()
    return obj


def joints(i, spec, next_spec, m):
    """Joints across a level's tread between its front edge and the next level's front foot: short dark lines
    running back from the front edge every JOINT pixels."""
    foot, top = level_plan(spec)
    z1 = spec[7]
    y_front = top[2] + BEVEL
    y_back = level_plan(next_spec)[0][2] - 0.2 if next_spec else top[2] + 4.0
    made = []
    x = AXIS_X - JOINT * 0.5
    xs = []
    while x > top[0] + 1.0:
        xs.append(x)
        x -= JOINT
    x = AXIS_X + JOINT * 0.5
    while x < top[1] - 1.0:
        xs.append(x)
        x += JOINT
    for j, x in enumerate(xs):
        made.append(k.mesh_object(f"joint{i}_{j}", [(x - 0.08, y_front, z1 + 0.02), (x + 0.08, y_front, z1 + 0.02),
                                                    (x + 0.08, y_back, z1 + 0.02), (x - 0.08, y_back, z1 + 0.02)],
                                  [(0, 1, 2, 3)], m["groove"]))
    return made


def build_whole(m):
    z0 = 0.0
    for i, spec in enumerate(LEVELS):
        level(i, spec, z0, m)
        courses(i, spec, z0, m)
        joints(i, spec, LEVELS[i + 1] if i + 1 < len(LEVELS) else None, m)
        z0 = spec[7]
    whole = mk.meshes()
    for obj in whole:
        mk.apply(obj)
    bpy.context.view_layer.update()
    return whole


# --- The capstone -------------------------------------------------------------------------------------------------

def cap_materials(lighter, strength):
    glow = k.level_palette()

    def mat(name, index, metallic=0.45, roughness=0.32):
        index = min(index + lighter, 0x1f)
        return k.material(f"{name}_{index:x}", palette=index, metallic=metallic, roughness=roughness,
                          emission=glow[index], emission_strength=strength)
    return {"west": mat("cap_west", 0x1b), "south": mat("cap_south", 0x18), "east": mat("cap_east", 0x19),
            "north": mat("cap_north", 0x17), "edge": mat("cap_edge", 0x1c), "plinth": mat("cap_plinth", 0x15),
            "tread": mat("cap_plinth_top", 0x18), "tip": mat("cap_tip", 0x1d, 0.55, 0.25)}


def capstone(m):
    """The capstone: a plinth and a pyramidion of gold, its edges bevelled, its faces painted as the sprite shades
    them; at its sprite's centre's offset CAP_AT, standing on the platform (CAP_BASE)."""
    cx, cy = CAP_AT
    hw, ph = CAP_PLINTH
    plinth = mk.box("cap_plinth", cx - hw, cx + hw, cy - hw, cy + hw, CAP_BASE - 0.2, CAP_BASE + ph, m["plinth"])
    mk.bevel(plinth, 0.18, 2, 35)
    mk.shade(plinth, 35)
    mk.paint(plinth, lambda c, n: m["tread"] if n.z > 0.9 else None)
    bw, bh = CAP_BODY
    z = CAP_BASE + ph
    bm = bmesh.new()
    base = [bm.verts.new((cx + sx * bw, cy + sy * bw, z)) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    apex = bm.verts.new((cx, cy, z + bh))
    for i in range(4):
        bm.faces.new((base[i], base[(i + 1) % 4], apex))
    bm.faces.new(list(reversed(base)))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new("cap")
    bm.to_mesh(mesh)
    bm.free()
    body = mk._link("cap", mesh, m["south"])
    mk.bevel(body, 0.22, 2, 30)
    # The gilded tip's edge: a cut round the pyramidion.
    bm = bmesh.new()
    bm.from_mesh(body.data)
    mk.split_along(bm, {v: v.co.z for v in bm.verts}, z + bh * CAP_TIP)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    bm.to_mesh(body.data)
    bm.free()
    mk.shade(body, 30)

    def pick(c, n):
        if n.z < -0.5:
            return m["plinth"]
        if c.z > z + bh * CAP_TIP:
            return m["tip"]
        h = Vector((n.x, n.y, 0.0))
        if h.length < 0.35:
            return m["edge"]
        if abs(abs(n.x) - abs(n.y)) < 0.12:
            return m["edge"]  # the ridges between the faces
        if abs(n.y) >= abs(n.x):
            return m["south"] if n.y < 0 else m["north"]
        return m["west"] if n.x < 0 else m["east"]
    mk.paint(body, pick)
    return [plinth, body]


# --- Checks and build ---------------------------------------------------------------------------------------------

def pyramid_mask(sheet):
    """The pyramid's pixels: those not in the sand's ramp (10)."""
    import sys as _sys
    _sys.path.insert(0, os.path.join(HERE, "..", ".."))
    from sprite_profile import sprite_indices
    mask = [[False] * 48 for _ in range(56)]
    for sprite, (c0, r0) in SPRITE_AT.items():
        g = sprite_indices(sheet, sprite)
        for r in range(28):
            for c in range(24):
                v = g[r][c]
                mask[r0 + r][c0 + c] = v is not None and v >> 4 != 10
    return mask


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    sheet = os.path.join(options["check"], "enemy_3.png") if "check" in options else None
    k.reset()
    m = materials()
    whole = build_whole(m)
    print("whole pyramid: %d triangles, %d objects" % (mk.triangles(whole), len(whole)))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    if sheet:
        mk.compare("whole (3 153 + 155 above 191 + 193)", mk.coverage(whole, 48, 56), pyramid_mask(sheet))
    if "preview" in options:
        # The whole with its capstone in place.
        before = set(mk.meshes())
        stone = capstone(cap_materials(0, CAP_FRAMES[0][3]))
        for obj in stone:
            mk.apply(obj)
            obj.data.transform(Matrix.Translation((CAP_CENTRE[0], CAP_CENTRE[1], 0.0)))
        mk.preview(options["preview"] + "pyramid_whole", whole + stone, size=(48, 56), scale=8, distance=1.8)
        for obj in stone:
            bpy.data.objects.remove(obj)
    mask = pyramid_mask(sheet) if sheet else None
    for name, sprite, box in PIECES:
        if only and name not in only:
            continue
        pieces = [p for p in (cut(src, box, m["seam"]) for src in whole) if p is not None]
        mk.transform(pieces, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
        bpy.context.view_layer.update()
        for src in whole:
            src.hide_render = True
        if mask:
            c0, r0 = SPRITE_AT[sprite]
            mk.compare("%s (3 %d)" % (name, sprite), mk.coverage(pieces, 24, 28),
                       [row[c0:c0 + 24] for row in mask[r0:r0 + 28]])
        mk.report(name, pieces, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, pieces)
        for obj in pieces:
            bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False
    # The capstone and its frames.
    for name, sprite, lighter, strength in CAP_FRAMES:
        if only and name not in only:
            continue
        k.reset()
        parts = capstone(cap_materials(lighter, strength))
        for obj in parts:
            mk.apply(obj)
        bpy.context.view_layer.update()
        bpy.context.scene.view_settings.view_transform = "Standard"
        if sheet:
            sys.path.insert(0, os.path.join(HERE, "..", ".."))
            mk.compare("%s (3 %d)" % (name, sprite), mk.coverage(parts, 12, 14), k.sprite_mask(sheet, sprite, False))
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts, size=(12, 14), scale=24)


if __name__ == "__main__":
    build()
