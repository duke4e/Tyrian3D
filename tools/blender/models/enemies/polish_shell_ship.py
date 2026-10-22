"""The ship of two dark shells round a red eye of the asteroid levels (sheet D sprite 157, 2x2: 24 x 28 pixels, and its
frames 159 and 161; enemy 285, armour 8, worth 250: ASTEROID1 on the ground layer (event 6 at t3000, 4000, 5000),
ASTEROID2 (t2500 ... 2700) and ASTEROIDS (t800 ... 1460) in the sky), polished (2026-10-22, round 33; it replaces
wave3_j.py's shell_ship(), two lathed half-eggs and a box, and wave3_at_d.py's shell_ship_159 / _161, the same moved).
models.cfg: model shell_ship / shell_ship_159 / shell_ship_161 (centred in height, no origin) and sprite d 157
shell_ship yaw=0, frame d 159 shell_ship_159, frame d 161 shell_ship_161 (the lines as they are).

Enemy 285 animates 157 159 159 161 161 159 159 157 over and over (ani 8, animate 2) and fires as it closes (tur 24).
No other enemy (launched ones included) shows D 157, 159 or 161; none of them is another sprite's pixels mirrored,
turned or in other ramps (the shells are the same pixels in all three, moved).

As the sprites and their 4x upscales draw it (columns and rows of the 24 x 28 sprite): an egg of glossy black metal,
round at the top (row 1), pointed at the bottom (row 23), 14 pixels wide at its widest (rows 6-15), split down its
length into two shells: in 157 they stand apart (the left one columns 1-8, the right one 15-22), a dark hub between
them (columns 9-14 of rows 5-12) carrying the eye, a red lens hot yellow-white in its middle (columns 10-13 of rows
7-10: 0x75-0x7f), and under the hub two thin legs down the shells' inner faces (columns 9 and 14 of rows 13-16), the
sky between them; in 159 the shells slide in over the hub's ends (its middle four columns showing, the eye whole), in
161 they meet (columns 4-10 and 11-17), the eye shut inside; 159 and 161 draw the ship a pixel left of 157. The left
shell is lit from the upper left (0x05-0x0a, a white gleam 0x0d-0x0f at columns 5-6 of rows 4-6), the right one dark
(0x02-0x05) but for its inner edge (0x0a-0x0b, rows 3-9) and a gleam along its lower right rim (0x09-0x0a, rows 14-19).

Built as such an egg cut in two: each shell is half of one egg (its long axis along y; the profile of half-widths along
it the closed frame's outline, its heights 0.75 of them: SHELL_H), bounded by the flat plane it was cut along, so that
its crest is its inner edge (which is why the right shell's inner edge catches the light while the rest of it faces
away, as the sprite draws it); lofted from explicit D-shaped rings (half an ellipse and the straight inner face). The
hub a rounded block between them (0x03), its top lit along its back (0x07), the lens a glowing oval on its top in a
dark bezel: its red rim 0x75 and core 0x7c with a hot spot 0x7e (emission 0.35-0.6), its lower part shadowed (0x70);
the legs thin plates down the shells' inner faces. The shells are painted in bands of how their faces meet the light
(LIGHT: the game's sun from the upper left) plus a gleam where they mirror it to the camera and a rim light along the
right one's lower right edge, cut along smooth contours (polish_orb_red.band_split): 0x02 (the undersides and the
inner faces), 0x04, 0x06, 0x08, 0x0a, 0x0d (the gleam, a little emission: 0.18) - a shade or two lighter than the
sprite's, as the game's camera and its dark sky make glossy greys read darker. Glossy (metallic 0.45, roughness 0.22).

The frames are the same parts moved: the shells' inner faces at x -3.6 and 3.6 (157, each shell tilted open 11 degrees
about its equator's line, so that its dark inner face shows as the sprite's black inner outline, and recentred in
height), -3 and 1 (159), -1 and -1 (161, the egg closed, the hub inside it); the hub and the eye at x 0 (157) and -1
(159, 161); the hub's legs only in 157. Every frame has the same height bounds (z -5.3 to 5.3: the shells are the
tallest parts), as the game centres the ship in height on its bounds (no origin).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up; origin at the sprite's centre
(pixel corner 12, 14): column c is x = c - 12 (its left edge), row r is y = 14 - r (its top edge); the egg's equator at
z 0 (it is round underneath too: a flying ship).

Replaces wave3_j.py's shell_ship (its section "D 157: the shell ship": shell_ship() and its @model registration, and
the shell_ship bullet of its docstring) and wave3_at_d.py (all of it: it builds only shell_ship_159 and _161, from
wave3_j.shell_ship(); nothing imports it).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each frame's silhouette from
above against its sprite in enemy_D.png), --preview <prefix> (top and 3/4 views), --only <name,...>.
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_orb_red import band_split, smoothstep  # noqa: E402

LIGHT = Vector((-0.55, 0.45, 0.7)).normalized()   # towards the game's sun (from the upper left)
VIEW = Vector((0.0, -math.sin(math.radians(20.0)), math.cos(math.radians(20.0))))   # towards the game's camera
HALF = (LIGHT + VIEW).normalized()

# The egg's half-widths along y (the closed frame 161's outline, its dark edge included), from its top down.
PROFILE = [(13.0, 0.0), (12.75, 1.9), (12.5, 2.9), (11.5, 4.2), (10.5, 5.15), (9.5, 5.85), (8.5, 6.4), (7.5, 6.8),
           (6.0, 7.0), (2.0, 7.05), (-0.5, 7.0), (-1.5, 6.85), (-2.5, 6.5), (-3.5, 6.0), (-4.5, 5.45), (-5.5, 4.8),
           (-6.5, 4.0), (-7.5, 3.1), (-8.5, 2.15), (-9.4, 1.15), (-9.85, 0.45), (-10.0, 0.0)]
SHELL_H = 0.75                 # the shells' half-heights against their half-widths
SEGMENTS = 22                  # points round a shell's half-ellipse
# The frames: the shells' inner faces (left, right) and the hub's middle.
# The frames: the shells' inner faces (left, right), how far they are tilted open (degrees, about their equators), the
# hub's middle.
FRAMES = [("shell_ship", 157, (-3.6, 3.6), 11.0, 0.0), ("shell_ship_159", 159, (-3.0, 1.0), 0.0, -1.0),
          ("shell_ship_161", 161, (-1.0, -1.0), 0.0, -1.0)]
# The hub (its half-width, y range, top and bottom), the lens on it, the legs under it.
HUB = dict(hw=3.0, y0=1.2, y1=8.8, top=3.1, bottom=-2.2)
LENS = dict(y=5.6, rx=2.05, ry=1.75, z=3.05)
LEGS = dict(y0=-2.8, y1=1.6, top=1.8, bottom=-2.0, t=0.75)


def materials():
    pal = k.level_palette()

    def mat(name, index, metallic=0.45, roughness=0.22, glow=0.0, glow_index=None):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness,
                          emission=pal[glow_index if glow_index is not None else index] if glow > 0 else None,
                          emission_strength=glow)
    return {
        "shell_2": mat("shell_02", 0x02),
        "shell_3": mat("shell_03", 0x03),
        "shell_4": mat("shell_04", 0x04),
        "shell_6": mat("shell_06", 0x06),
        "shell_8": mat("shell_08", 0x08),
        "shell_a": mat("shell_0a", 0x0a),
        "gleam": mat("shell_gleam", 0x0d, 0.3, 0.2, 0.18),
        "hub": mat("shell_hub", 0x03, 0.5, 0.35),
        "hub_lit": mat("shell_hub_lit", 0x07, 0.5, 0.3),
        "bezel": mat("shell_bezel", 0x01, 0.3, 0.45),
        "lens_dark": mat("shell_lens_dark", 0x70, 0.0, 0.3, 0.25, 0x73),
        "lens": mat("shell_lens", 0x75, 0.0, 0.18, 0.4, 0x77),
        "lens_core": mat("shell_lens_core", 0x7c, 0.0, 0.15, 0.5),
        "lens_hot": mat("shell_lens_hot", 0x7e, 0.0, 0.12, 0.6),
    }


def half_width(y):
    for (ya, wa), (yb, wb) in zip(PROFILE, PROFILE[1:]):
        if yb <= y <= ya:
            t = (y - ya) / (yb - ya)
            # smooth between the points (cosine)
            return wa + (wb - wa) * (1 - math.cos(math.pi * t)) / 2
    return 0.0


def stations():
    """The y of the shells' rings: dense near the tips."""
    ys = []
    n = 34
    y_top, y_bot = PROFILE[0][0], PROFILE[-1][0]
    for i in range(1, n):
        t = i / n
        u = (1 - math.cos(math.pi * t)) / 2        # denser at both ends
        ys.append(y_top + (y_bot - y_top) * u)
    return ys


def shell(name, x_in, side, m):
    """One shell: half the egg on the given side (-1 left, +1 right) of the plane x = x_in, closed by its flat inner
    face; D-shaped rings lofted along y, fans to the tips."""
    rings = []
    for y in stations():
        w = half_width(y)
        h = w * SHELL_H
        ring = []
        for j in range(SEGMENTS + 1):            # over the outside, from the crest down to the keel
            a = math.pi * j / SEGMENTS
            ring.append(Vector((x_in + side * w * math.sin(a), y, h * math.cos(a))))
        for j in range(1, 6):                     # back up the flat inner face
            ring.append(Vector((x_in, y, -h + 2 * h * j / 6)))
        if side > 0:
            ring.reverse()
        rings.append(ring)
    obj = k.loft(name, rings, m["shell_6"], start_point=(x_in, PROFILE[0][0], 0.0),
                 end_point=(x_in, PROFILE[-1][0], 0.0))
    k.smooth(obj, 50)
    return obj


def vertex_normals(obj):
    mesh = obj.data
    normals = [Vector() for _ in mesh.vertices]
    for poly in mesh.polygons:
        for vi in poly.vertices:
            normals[vi] += poly.normal * poly.area
    return [n.normalized() for n in normals]


def paint_shell(obj, x_in, side, m, rot):
    """Bands of the light each point gets, a gleam where the shell mirrors the sun to the camera, a rim light along
    the right shell's lower right edge; the inner face and the underside dark."""
    values = []
    for v in obj.data.vertices:
        x, y, z = v.co
        w = half_width(y)
        h = w * SHELL_H
        dx = (x - x_in) * side
        if dx < 1e-4 and abs(z) < h - 1e-3:
            values.append(-9.0)                 # the flat inner face
            continue
        if w < 1e-3:
            n = Vector((0.0, 1.0 if y > 0 else -1.0, 0.0))
        else:
            dw = (half_width(y + 0.05) - half_width(y - 0.05)) / 0.1
            n = Vector((side * dx / (w * w), -dw / w, z / (SHELL_H * SHELL_H * w * w))).normalized()
        n = rot @ n
        val = n.dot(LIGHT)
        # the gleam: where it mirrors the sun to the camera, on its upper part only (columns 5-6 of rows 4-6)
        spec = max(0.0, n.dot(HALF)) ** 60 * smoothstep(3.0, 7.0, y) * (1.0 - smoothstep(10.5, 12.5, y))
        val += 2.6 * spec
        if side > 0:
            # its inner edge catching the light (column 16 of rows 3-9), the rim light along its lower right edge
            # (columns 17-20 of rows 14-19)
            val += 0.4 * smoothstep(0.86, 0.99, n.z) * smoothstep(-2.0, 3.0, y)
            rim = smoothstep(0.3, 0.7, n.x) * smoothstep(-1.0, -4.0, y) * smoothstep(-10.0, -7.8, y)
            val += 1.2 * rim * smoothstep(-0.25, 0.25, n.z)
        if n.z < -0.25:
            val = min(val, -1.0)
        values.append(val)
    band_split(obj, values, [(-9.5, m["shell_2"]), (-0.05, m["shell_3"]), (0.3, m["shell_4"]), (0.55, m["shell_6"]),
                             (0.8, m["shell_8"]), (1.05, m["shell_a"]), (1.45, m["gleam"])])
    k.smooth(obj, 50)


def hub(dx, m):
    h = HUB
    obj = mk.box("hub", dx - h["hw"], dx + h["hw"], h["y0"], h["y1"], h["bottom"], h["top"], m["hub"])
    mk.bevel(obj, 0.6, 2, 35)
    mk.shade(obj, 35)
    mk.paint(obj, lambda c, n: m["hub_lit"] if (n.z > 0.4 and c.y > h["y1"] - 1.4) or n.dot(LIGHT) > 0.8 else None)
    parts = [obj]
    ln = LENS
    bezel = mk.dome("lens_bezel", (dx, ln["y"]), (ln["rx"] + 0.45, ln["ry"] + 0.45, 0.35), ln["z"] - 0.12, m["bezel"],
                    28, 4)
    parts.append(bezel)
    lens = mk.dome("lens", (dx, ln["y"]), (ln["rx"], ln["ry"], 0.75), ln["z"], m["lens"], 32, 8)
    # the lens: its lower part shadowed, a hot core, a hotter spot at its upper middle
    values = []
    for v in lens.data.vertices:
        r = math.hypot((v.co.x - dx) / ln["rx"], (v.co.y - ln["y"] - 0.25) / ln["ry"])
        val = 1.0 - r
        if v.co.y < ln["y"] - 0.9:
            val -= 0.8 * smoothstep(ln["y"] - 0.9, ln["y"] - 1.6, v.co.y)
        values.append(val)
    band_split(lens, values, [(-9.0, m["lens_dark"]), (-0.12, m["lens"]), (0.35, m["lens_core"]),
                              (0.62, m["lens_hot"])])
    k.smooth(lens, 60)
    parts.append(lens)
    return parts


def legs(x_left, x_right, m):
    """The thin legs under the hub, down the shells' inner faces."""
    g = LEGS
    out = []
    for i, x in enumerate((x_left + g["t"] / 2 + 0.05, x_right - g["t"] / 2 - 0.05)):
        obj = mk.box(f"leg{i}", x - g["t"] / 2, x + g["t"] / 2, g["y0"], g["y1"], g["bottom"], g["top"], m["hub"])
        mk.bevel(obj, 0.2, 1, 35)
        mk.shade(obj, 35)
        mk.paint(obj, lambda c, n: m["hub_lit"] if n.z > 0.5 else None)
        out.append(obj)
    return out


def build_frame(x_left, x_right, tilt, dx, m):
    parts = []
    for name, x_in, side in (("shell_l", x_left, -1), ("shell_r", x_right, 1)):
        obj = shell(name, x_in, side, m)
        # tilted open about its equator's line along its inner face: the crest outwards, the inner face showing
        rot = Matrix.Rotation(math.radians(-side * tilt), 3, "Y")
        paint_shell(obj, x_in, side, m, rot)
        obj.data.transform(Matrix.Translation((x_in, 0.0, 0.0)) @ rot.to_4x4() @ Matrix.Translation((-x_in, 0.0, 0.0)))
        # centred in height again (the tilt lifts its outer side): every frame keeps the same height bounds
        zs = [v.co.z for v in obj.data.vertices]
        obj.data.transform(Matrix.Translation((0.0, 0.0, -(max(zs) + min(zs)) / 2)))
        obj.data.update()
        parts.append(obj)
    parts += hub(dx, m)
    if x_right - x_left > 2.0 * HUB["hw"] - 0.5:     # the legs show only while the shells stand apart (157)
        parts += legs(x_left, x_right, m)
    for obj in parts:
        mk.apply(obj)
    bpy.context.view_layer.update()
    return parts


def build():
    options = k.args()
    only = options["only"].split(",") if "only" in options else None
    for name, sprite, (x_left, x_right), tilt, dx in FRAMES:
        if only and name not in only:
            continue
        k.reset()
        m = materials()
        parts = build_frame(x_left, x_right, tilt, dx, m)
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


if __name__ == "__main__":
    build()
