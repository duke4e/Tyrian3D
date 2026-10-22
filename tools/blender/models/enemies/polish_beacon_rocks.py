"""The two sky rocks of the asteroid levels with lights in them: the rock with a red beacon (sheet D sprite 93, 2x2:
24 x 28 pixels, and its frames 55 and 18; enemy 462, armour 20, worth 25: sent by the random enemies of ASTEROID2,
ASTEROID?, ASTCITY, AST. CITY and AST ROCK, placed in ASTEROIDS at t1130; sky layer) and the rock with a blue eye (D 229
and its frames 231, 233 and 235; enemy 286, armour 8, worth 50: sent by ASTEROID1's random enemies; sky layer), polished
(2026-10-22, round 33; they replace wave3_j_rocks.py's rock_beacon() and rock_blue_eye(), noisy faceted hulls over the
sprites' outlines built by its sky_rock(), with a box and a ball for the lamp, a ring and four balls for the eye).
models.cfg: model rock_beacon / rock_blue_eye (as they are) and the new rock_beacon_55, rock_beacon_18,
rock_blue_eye_231, _233, _235 (no origin: centred in height, as the rocks), frame d 55 rock_beacon_55 ... frame d 235
rock_blue_eye_235; sprite d 93 rock_beacon yaw=0 and sprite d 229 rock_blue_eye yaw=0 (the lines as they are).

The animations: 462 runs 93 55 18 18 18 55 55 55 93 (ani 9, animate 2: its beacon pulsing; it fires, tur 116), 286
runs 229 231 231 233 233 235 235 233 233 231 231 229 (ani 12, animate 1: its eye lighting up and going out). No other
enemy (launched ones included) shows D 93, 55, 18, 229, 231, 233 or 235: frame models. They are the lumpy asteroid's
family, and two of its rocks: D 93 is D 5's pixels (polish_asteroid_lumpy.py's ROCK) with a lamp set into its right (15
pixels differ, columns 18-21 of rows 10-14), and D 229 is D 123's rock (polish_sky_rocks.py's ROCK_C: 644 of 672 pixels
equal) with a socket where its knob's lower left face is (columns 11-14 of rows 12-16) and a few lighter pixels along a
crease (columns 7-9 of rows 7-13, left as ROCK_C has them). Their frames are the rock's pixels with the lights' and
the light they throw on the rock round them.

As the sprites and their 4x upscales draw them (columns and rows of the 24 x 28 sprite):
- rock_beacon: the lumpy asteroid, and on its lower right block a lens three pixels wide and five tall (columns 18-20 of
  rows 10-14) in a dark bezel (columns 17 and 21): dark grey glass in 93 (0x03-0x06), red in 55 (0x73-0x78, a 0x7c
  middle), brighter in 18 (0x75-0x7a, a 0x7e middle) with the rock round it lit (0x0a-0x0e, rows 9-15).
- rock_blue_eye: D 123's rock, and in a dark socket where its knob meets the lower left block (columns 11-13 of rows
  13-15) a blue light: dark in 229, a small blue cross in 231 (0x97, 0x9a), a larger one with the rock round it lit in
  233 (0x96-0x9d; 0x0a-0x0d round it, columns 9-17 of rows 10-18) and the largest, white-blue in its middle, in 235
  (0x9a-0x9f, 0x8d; 0x0a-0x0e round it, columns 6-17 of rows 9-19); the upscales draw it as a blue diamond (a square
  turned 45 degrees), small in 231, all lit in 233, lighter in 235; the 231 frame lights only its middle.

Built as their rocks are (the same specs and machinery: polish_asteroid_lumpy.build_rock(), polish_asteroids: lumps,
creases, welts, weathering; the rock built once per object and copied for its frames, as RockBlock widens its caps each
time it is built), with the light set into the rock's surface where the sprite draws it, facing along the surface's
normal there: the beacon a domed oval lens (radii 1.3 x 2.6) in a thin raised bezel ring (the rock's dark 0x05), the
eye a gem cut as a low four-sided pyramid, its corners up, down, left and right (half its diagonal 2.7: the sprites'
cross of light is such a diamond drawn in pixels, as the upscale shows) in a rhombus socket (0x04). The frames change
only the lens's, the gem's and the rock's paint (the same geometry and bounds): the light in bands
(polish_orb_red.band_split, by the distance from its middle (the gem's diamond distance): rim, body, core, hot spot;
emission 0.3-0.65, the game's bloom adds), the rock round the light (within LIGHT_REACH) a shade or more lighter where
the sprites light it, cut along smooth circles (polish_coral_manta.split_contour). Unlit, the beacon's lens is glossy
dark glass (0x04), the eye's a dark blue-grey glass (0x65, 0x67).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up; origin at the sprite's centre
(pixel corner 12, 14): column c is x = c - 12, row r is y = 14 - r. Flat underneath, the rocks' heights; the game
centres them in height on their layer.

Replaces wave3_j_rocks.py (all of it: rock_beacon() and rock_blue_eye() are the last models it builds, sky_rock() served
only them; nothing imports it now that wave3_ao_works.py's stone face section is gone (round 30)) and wave3_j_art.py's
D93 and D229 (read only by wave3_j_rocks.py), D18 and D235 (their lit frames' pixels, read by nothing).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each frame's silhouette from
above against its sprite in enemy_D.png), --preview <prefix> (top and 3/4 views), --only <name,...>.
"""
import copy
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_asteroid_lumpy as lumpy  # noqa: E402
import polish_sky_rocks as sky  # noqa: E402
from polish_coral_manta import split_contour  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_orb_red import band_split  # noqa: E402

# --- The lights (pixel corners of the sprite, sizes) -------------------------------------------------------------
BEACON = dict(c=19.5, r=12.5, rx=1.3, ry=2.6, rise=0.55, bezel=0.22)
EYE = dict(c=12.5, r=14.5, half=2.7, height=0.85, socket=0.45)   # the gem: middle, half its diagonal
# How far the light reaches over the rock in each lit frame (radius in pixels, shades added inside it, the inner
# radius and its shades).
BEACON_FRAMES = [("rock_beacon", 93, None), ("rock_beacon_55", 55, "dim"), ("rock_beacon_18", 18, "bright")]
EYE_FRAMES = [("rock_blue_eye", 229, 0), ("rock_blue_eye_231", 231, 1), ("rock_blue_eye_233", 233, 2),
              ("rock_blue_eye_235", 235, 3)]
LIGHT_REACH = {"bright": (3.8, 2, 2.6, 3), 2: (3.9, 1, 3.0, 2), 3: (4.8, 2, 3.4, 3)}


def P(c, r):
    return Vector((c - 12.0, 14.0 - r))


def glow_mat(name, index, strength, roughness=0.15, glow_index=None):
    pal = k.level_palette()
    return k.material(name, palette=index, metallic=0.0, roughness=roughness,
                      emission=pal[glow_index if glow_index is not None else index], emission_strength=strength)


# --- Helpers -----------------------------------------------------------------------------------------------------

def place(rock, c, r, reach):
    """Where the light sits on the rock: the surface's height round (c, r) (the highest of the samples within reach,
    so that it does not sink into a crease) and its mean normal there."""
    hit = mk.surface([rock])
    p = P(c, r)
    zs, normal = [], Vector()
    for i in range(12):
        a = 2 * math.pi * i / 12
        for f in (0.0, 0.5, 1.0):
            h = hit(p.x + reach[0] * f * math.cos(a), p.y + reach[1] * f * math.sin(a))
            if h is not None:
                zs.append(h[0].z)
                normal += h[1]
    zs.sort()
    z = zs[int(len(zs) * 0.75)]
    n = normal.normalized()
    return Vector((p.x, p.y, z)), n


def oriented(obj, centre, normal):
    """Turns an object built about the origin (its axis +z) to stand along normal at centre."""
    rot = Vector((0.0, 0.0, 1.0)).rotation_difference(normal).to_matrix().to_4x4()
    obj.data.transform(Matrix.Translation(centre) @ rot)
    obj.data.update()
    return obj


def lens_values(obj, centre, normal, rx, ry):
    """How far each point of a lens lies from its middle (0 at the rim, 1 in the middle), in its own plane."""
    side = Vector((1.0, 0.0, 0.0))
    side = (side - normal * side.dot(normal)).normalized()
    other = normal.cross(side)
    vals = []
    for v in obj.data.vertices:
        d = v.co - centre
        u, w = d.dot(side) / rx, d.dot(other) / ry
        vals.append(1.0 - math.sqrt(u * u + w * w))
    return vals


def grey_index(mat):
    return int(mat.name.split("@")[1].split(".")[0])


def light_rock(rock, grey, centre, reach):
    """The rock round the light lit as the sprites draw it: within radius `outer` `add` shades lighter, within `inner`
    `add2` (cut along smooth circles round the light)."""
    outer, add, inner, add2 = reach
    bm = bmesh.new()
    bm.from_mesh(rock.data)
    vals = {"d": {v: math.hypot(v.co.x - centre.x, v.co.y - centre.y) for v in bm.verts}}
    for t in (outer, inner):
        split_contour(bm, vals, "d", t)
    mats = list(rock.data.materials)
    for f in bm.faces:
        d = sum(vals["d"][v] for v in f.verts) / len(f.verts)
        if d >= outer or f.normal.z < 0.05:
            continue
        mat = mats[f.material_index]
        if "@" not in mat.name or not mat.name.split("@")[0].endswith("_rock"):
            continue
        index = grey_index(mat)
        if index >> 4 != 0:
            continue
        new = min(0x0e, index + (add2 if d < inner else add))
        f.material_index = mk.slot_of(rock, grey(new))
        mats = list(rock.data.materials)
    bm.to_mesh(rock.data)
    bm.free()


def copies(objects):
    out = []
    for src in objects:
        obj = src.copy()
        obj.data = src.data.copy()
        bpy.context.scene.collection.objects.link(obj)
        out.append(obj)
    return out


def export(parts, name, sprite, options):
    drop_unused(parts)
    triangulate(parts)
    if "check" in options:
        sheet = os.path.join(options["check"], "enemy_D.png")
        mk.compare("%s (D %d)" % (name, sprite), mk.coverage(parts, 24, 28), k.sprite_mask(sheet, sprite))
    parts = [join(parts, name)]
    parts[0].data.name = name
    bpy.context.scene.view_settings.view_transform = "Standard"   # previews in the game's colours
    mk.report(name, parts, os.path.join(mk.outdir(options), name + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + name, parts, size=(24, 28), scale=16, distance=0.7)
    for obj in parts:
        data = obj.data
        bpy.data.objects.remove(obj)
        if data.users == 0:
            bpy.data.meshes.remove(data)


# --- The beacon (D 93) ----------------------------------------------------------------------------------------------

def beacon_parts(rock):
    b = BEACON
    centre, normal = place(rock, b["c"], b["r"], (b["rx"], b["ry"]))
    bez = k.material("beacon_bezel", palette=0x05, metallic=0.35, roughness=0.4)
    rx, ry = b["rx"] + b["bezel"], b["ry"] + b["bezel"]
    prof = [(0.01, -1.2), (rx, -1.2), (rx, 0.15), (rx - 0.3, b["rise"] - 0.05), (b["rx"] + 0.05, b["rise"] - 0.1),
            (b["rx"], 0.05), (0.01, 0.05)]
    bezel = mk.lathe("beacon_bezel", prof, (0.0, 0.0), bez, 40, squash=(1.0, ry / rx))
    k.smooth(bezel, 40)
    oriented(bezel, centre, normal)
    lens = mk.dome("beacon_lens", (0.0, 0.0), (b["rx"], b["ry"], b["rise"] + 0.45), 0.0, bez, 36, 8)
    oriented(lens, centre, normal)
    return centre, normal, bezel, lens


def paint_beacon(lens, centre, normal, state):
    b = BEACON
    vals = lens_values(lens, centre, normal, b["rx"], b["ry"])
    if state is None:
        glass = k.material("beacon_glass", palette=0x04, metallic=0.3, roughness=0.12)
        rim = k.material("beacon_glass_rim", palette=0x03, metallic=0.3, roughness=0.15)
        band_split(lens, vals, [(-9.0, rim), (0.25, glass)])
    elif state == "dim":
        band_split(lens, vals, [(-9.0, glow_mat("beacon_rim55", 0x73, 0.3)),
                                (0.18, glow_mat("beacon_red55", 0x75, 0.38)),
                                (0.5, glow_mat("beacon_core55", 0x78, 0.45)),
                                (0.78, glow_mat("beacon_hot55", 0x7c, 0.5))])
    else:
        band_split(lens, vals, [(-9.0, glow_mat("beacon_rim18", 0x75, 0.4)),
                                (0.18, glow_mat("beacon_red18", 0x77, 0.5)),
                                (0.5, glow_mat("beacon_core18", 0x7a, 0.58)),
                                (0.78, glow_mat("beacon_hot18", 0x7e, 0.65))])
    k.smooth(lens, 60)


def build_beacon(options, only):
    k.reset()
    rock, grey = lumpy.build_rock(lumpy.ROCK)
    centre, normal, bezel, lens = beacon_parts(rock)
    for obj in (rock, bezel, lens):
        mk.apply(obj)
        obj.hide_render = True
    for name, sprite, state in BEACON_FRAMES:
        if only and name not in only:
            continue
        r, bz, ln = copies([rock, bezel, lens])
        for obj in (r, bz, ln):
            obj.hide_render = False
        paint_beacon(ln, centre, normal, state)
        if state == "bright":
            light_rock(r, grey, centre, LIGHT_REACH[state])
        export([r, bz, ln], name, sprite, options)


# --- The blue eye (D 229) -------------------------------------------------------------------------------------------

def diamond(name, centre, normal, half, height, mat, steps=6):
    """A gem cut as a low four-sided pyramid, its corners up, down, left and right on the screen (the sprites' cross of
    light is such a diamond drawn in pixels), standing along normal at centre: a grid of quads over the rhombus
    |u| + |w| <= half, raised height at its middle, sunk a little at its edges."""
    side = Vector((1.0, 0.0, 0.0))
    side = (side - normal * side.dot(normal)).normalized()
    other = normal.cross(side)
    n = steps * 2
    verts, faces = [], []
    index = {}
    for i in range(n + 1):
        for j in range(n + 1):
            a, b = -1 + 2 * i / n, -1 + 2 * j / n           # a square, turned 45 degrees: the rhombus
            u, w = (a + b) / 2 * half, (b - a) / 2 * half
            d = (abs(u) + abs(w)) / half
            z = height * (1.0 - d) - 0.25
            index[(i, j)] = len(verts)
            verts.append(centre + side * u + other * w + normal * z)
    for i in range(n):
        for j in range(n):
            faces.append((index[(i, j)], index[(i + 1, j)], index[(i + 1, j + 1)], index[(i, j + 1)]))
    # its rim, down into the rock
    rim = [index[(i, 0)] for i in range(n + 1)] + [index[(n, j)] for j in range(1, n + 1)] + \
          [index[(i, n)] for i in range(n - 1, -1, -1)] + [index[(0, j)] for j in range(n - 1, 0, -1)]
    base = len(verts)
    for vi in rim:
        verts.append(verts[vi] - normal * 1.0)
    m = len(rim)
    for q in range(m):
        a, b = rim[q], rim[(q + 1) % m]
        faces.append((a, base + q, base + (q + 1) % m, b))
    faces.append(tuple(base + q for q in range(m - 1, -1, -1)))
    obj = k.mesh_object(name, verts, faces, mat)
    k.recalc_normals(obj)
    k.smooth(obj, 30)
    return obj, side, other


def eye_parts(rock):
    e = EYE
    centre, normal = place(rock, e["c"], e["r"], (e["half"] * 0.7, e["half"] * 0.7))
    sock = k.material("eye_socket", palette=0x04, metallic=0.1, roughness=0.6)
    # the socket: a dark rim round the gem, set into the rock
    r_out = e["half"] + e["socket"]
    prof = [(0.01, -1.2), (r_out + 0.2, -1.2), (r_out + 0.2, -0.3), (r_out, 0.06), (r_out - 0.35, 0.0),
            (r_out - 0.5, -0.35), (0.01, -0.35)]
    socket = mk.lathe("eye_socket", prof, (0.0, 0.0), sock, 24, power=1.15)    # (a rhombus, as the gem)
    k.smooth(socket, 30)
    oriented(socket, centre, normal)
    gem, side, other = diamond("eye_gem", centre, normal, e["half"], e["height"], sock)
    return centre, normal, socket, gem, side, other


def paint_eye(gem, centre, normal, side, other, level):
    """The gem's light: dark (229), lit only at its middle (231: the small cross), lit all over (233), lighter, white
    at its middle (235); bands of the diamond distance from its middle."""
    e = EYE
    vals = []
    for v in gem.data.vertices:
        d = v.co - centre
        u, w = d.dot(side), d.dot(other)
        vals.append(1.0 - (abs(u) + abs(w)) / e["half"])
    if level == 0:
        bands = [(-9.0, k.material("eye_stone_dark", palette=0x65, metallic=0.3, roughness=0.2)),
                 (0.35, k.material("eye_stone", palette=0x67, metallic=0.3, roughness=0.15))]
    elif level == 1:
        bands = [(-9.0, k.material("eye_stone_dark", palette=0x65, metallic=0.3, roughness=0.2)),
                 (0.42, glow_mat("eye_blue1", 0x97, 0.32)), (0.7, glow_mat("eye_core1", 0x9a, 0.4))]
    elif level == 2:
        bands = [(-9.0, glow_mat("eye_rim2", 0x96, 0.36)), (0.12, glow_mat("eye_blue2", 0x98, 0.44)),
                 (0.42, glow_mat("eye_core2", 0x9a, 0.5)), (0.75, glow_mat("eye_hot2", 0x9d, 0.56))]
    else:
        bands = [(-9.0, glow_mat("eye_rim3", 0x9a, 0.45)), (0.12, glow_mat("eye_blue3", 0x9c, 0.52)),
                 (0.42, glow_mat("eye_core3", 0x9e, 0.58)), (0.72, glow_mat("eye_hot3", 0x8d, 0.65))]
    band_split(gem, vals, bands)
    k.smooth(gem, 30)


def build_eye(options, only):
    k.reset()
    spec = copy.deepcopy(sky.ROCK_C)        # (RockBlock.planes widens the caps of the spec it is given)
    rock, grey = lumpy.build_rock(spec)
    centre, normal, socket, gem, side, other = eye_parts(rock)
    for obj in (rock, socket, gem):
        mk.apply(obj)
        obj.hide_render = True
    for name, sprite, level in EYE_FRAMES:
        if only and name not in only:
            continue
        parts = copies([rock, socket, gem])
        for obj in parts:
            obj.hide_render = False
        r, s, g = parts
        paint_eye(g, centre, normal, side, other, level)
        if level >= 2:
            light_rock(r, grey, centre, LIGHT_REACH[level])
        export(parts, name, sprite, options)


def build():
    options = k.args()
    only = options["only"].split(",") if "only" in options else None
    if not only or any(n in only for n, _, _ in BEACON_FRAMES):
        build_beacon(options, only)
    if not only or any(n in only for n, _, _ in EYE_FRAMES):
        build_eye(options, only)


if __name__ == "__main__":
    build()
