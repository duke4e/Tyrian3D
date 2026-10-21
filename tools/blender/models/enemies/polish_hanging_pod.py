"""BRAINIAC's and GRAVITRON's grey pod with a red eye, hanging in a steel bracket (sheet 5 sprite 170, 2x2: the whole
cell; static; top layer; enemy 540 of episode 4: 10 in BRAINIAC, and 1663 of episode 6: 9 in GRAVITRON), polished
(2026-10-21; it replaces wave3_l.py's hanging_pod(), a lofted grey pod on two posts under a bar). models.cfg: model
hanging_pod enemies/hanging_pod.glb (unchanged: centred in height, as its neighbours), sprite 5 170 hanging_pod yaw=0
(unchanged).

The levels put it alone or two side by side, 24 pixels apart, in the rows of BRAINIAC's brains in their clamps (5 166)
but never against them (BRAINIAC's events 108: x 168; 2068: 216 and 240; 2740, 4196, 6940: 72; 4896, 5876: 216; 6268:
48 and 72; GRAVITRON's 666, 1194: 216; 762, 3119, 5297: 72; 1521, 4478: 48 and 72). No other enemy, launched ones
included, shows the sprite, and it is no other sprite's pixels mirrored, turned or in other ramps; it is its own
mirror image in coverage (IoU 0.996; its shading is not: lit from the upper left).

As the sprite and its 4x upscale draw it (columns and rows of the 24 x 28 sprite; blue-grey steel of ramp 6, greys of
ramp 0, ramp 7's reds): a steel bar across the top (rows 2-4, lit at row 3), its south face dark under it (rows 5-6),
a boss in its middle (columns 11-13 of rows 1-3); at each end a post (columns 0-2 and 21-23: dark outlines, a lit
middle) rising a little over the bar (rows 0-1) and running down to row 12, where it hooks in to the pod's side (row
13, columns 3 and 20), gaps between the posts and the pod above that (rows 7-10); the pod a grey body hanging from
the boss by a grey neck (columns 11-13 of rows 4-6): its rear a dome lit at its upper left (rows 7-13), its front a
round dark face (rows 14-25, columns 3-20) in a grey lip, seen as if tilted towards the viewer (an ellipse 18 x 13);
in the face four grey shutter blades on its diagonals (the large upper ones at columns 5-10 and 13-19 of rows 14-17,
the small lower ones at columns 7-9 and 14-17 of rows 21-23), the dark cross between them, and in its middle a red
eye (columns 9-14 of rows 18-22) with two hot points either side of its middle (0x7a at columns 10 and 13 of row 20).
The posts' tops are half brackets, as the brain clamp's (5 166) ends: side by side, a pod's columns 21-23 and the
next one's columns 0-2 draw one steel arch over the seam (its two legs either side of it, the lit top over both).

Built as such a pod slung in a gimbal: the boss and the arch over the seam are solids over their outlines
(polish_ring_machine.relief, as polish_brain_clamp.py's and polish_red_link.py's brackets: flat tops with rounded
rims, steel 0x6a with dark steel 0x66 sides, the clamp's heights), the bar a profile run across the sprite (its back
edge rounded, its flat top a little lower than the arch's, its south face sloping down; its ends flush with the
sprite's edges, so that two bars meet); the arch is built
whole over the seam at x = 12 (its top block, the two legs with the hooks at their feet) and cut there
(polish_savara_boss.cut, which keeps the uncut shading and each face's winding): the part left of the seam is this
sprite's right end, the part right of it, moved 24 pixels left, its left end, so that side by side two pods meet into
one arch. The pod is lathed about its axis, which leans POD_TILT degrees from straight up towards the bottom of the
screen, so that its face looks at the game's camera and seen from above lies where the sprite draws it (a round face
18 pixels across seen as 18 x 13); its body then squashed in height (POD_SQUASH: the outline seen from above stays,
the pod doesn't tower over its neighbours): the lip and the dark socket of the face, the body and the rear dome
painted in bands of grey by how they face the game's sun (cut along smooth contours, polish_orb_red.band_split), the
shutter blades plates on the socket's floor, the eye a glowing red dome with its two hot points (glowing 0.35-0.62 in
their own reds), a grey neck up to the boss. Every mesh is triangulated before the export (polish_k_pod.triangulate:
the output is the same with and without --check) and joined into one.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; origin at the
sprite's centre (pixel 12, 14): the pixel edge of column c, row r is x = c - 12, y = 14 - r.

Replaces wave3_l.py's hanging_pod() (its section "# --- 5 170: the hanging pod": the @model("hanging_pod", 170)
function, and the hanging_pod line of its docstring): remove them so that they don't overwrite this model.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <dir with enemy_5.png, or the sheet itself>
(the silhouette), --preview <prefix>, --pair <prefix> (two side by side, as BRAINIAC places them: <prefix>_top.png and
_3q.png).
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_balls import Ellipsoid, painted_ball  # noqa: E402
from polish_deli_boss import join  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_ring_machine import ccw, chaikin, relief, round_edge  # noqa: E402
from polish_savara_boss import cut  # noqa: E402
from polish_sphere_nozzle import smoothstep  # noqa: E402

NAME, SPRITE = "hanging_pod", 170
SUN = Vector((-0.6, 0.6, 1.0)).normalized()      # towards the game's sun (from above and the top left)
T = math.radians(20.0)
TOWARDS_VIEW = Vector((0.0, -math.sin(T), math.cos(T)))


# --- The steel (the arch's heights as polish_brain_clamp.py's bracket: BRACKET_TOP 4.6, LEG_TOP 3.7, rim 1.0,
# bottom -2.4; the bar a little lower, under the arch's top where they meet) ---------------------------------------
BAR = (7.2, 12.2)            # the bar across the top: from its south face's foot to its back edge (y)
BAR_TOP, BAR_FALL = 4.2, (9.1, 7.2, 1.2)   # its top; the south face falls from y 9.1 to 7.2, down to z 1.2
BOSS = (1.65, 9.7, 13.2, 5.0)               # the boss in its middle: half-width, from y, to y, top
ARCH_TOP, LEG_TOP, RIM, BOTTOM = 4.6, 3.7, 1.0, -2.4
# The arch over the seam (x' about the seam, y): its top block over both legs, the legs either side of a groove at
# the seam, each hooking out at its foot towards its pod (the left leg is this sprite's right end).
ARCH = [(0.0, 14.0), (-2.3, 14.0), (-2.85, 13.75), (-3.05, 13.1), (-3.05, 2.9), (-3.3, 2.1), (-4.0, 1.25),
        (-4.9, 0.55), (-5.5, 0.15), (-5.6, -0.35), (-5.1, -0.55), (-4.2, -0.2), (-3.0, 0.4), (-1.6, 1.15),
        (-0.6, 1.8), (-0.35, 2.6), (-0.35, 10.3), (0.0, 10.55)]
ARCH_STEP = (9.3, 8.3)       # where the arch's top block steps down to the legs (y)
HOOK_DROP = 1.1              # how far the hooks fall towards their tips

# --- The pod: its face's middle (seen from above) and height, the axis's lean, the profile along the axis ---------
FACE = Vector((0.0, -5.9, 4.6))
POD_TILT = 42.0              # degrees from straight up, towards the bottom of the screen
POD_SQUASH = 0.62            # its heights squashed about the face's middle
SEGMENTS = 44
POWER = 2.5                  # the cross-sections: superellipses (squarer than circles, as the sprite's outline)
R_SCALE = 1.025              # the profiles' radii scaled
# The body from its front edge (the lip's outer edge, t = 0) back along the axis (t, radius): the side, the rear dome.
BODY = [(0.0, 8.7), (0.6, 8.82), (2.5, 8.85), (5.0, 8.8), (7.0, 8.7), (8.6, 8.4), (9.6, 7.8), (10.5, 6.8),
        (11.2, 5.3), (11.7, 3.5), (12.0, 1.5), (12.1, 0.0)]
# The face: the lip (from the body's front edge round to the socket) and the socket (its wall and floor).
LIP = [(0.0, 8.7), (-0.35, 8.55), (-0.55, 8.2), (-0.5, 7.7), (-0.3, 7.45)]
SOCKET = [(-0.3, 7.45), (0.5, 7.3), (1.0, 7.0), (1.1, 6.0), (1.15, 3.0), (1.15, 0.0)]
SOCKET_FLOOR = 1.15
# The shutter blades: (angle of the middle (degrees, 0 = across to the right, 90 = up the face), half its spread at
# the rim, inner radius, outer radius), their thickness.
BLADES = [(45.0, 31.0, 2.9, 6.9), (135.0, 31.0, 2.9, 6.9), (225.0, 22.0, 3.2, 6.3), (315.0, 22.0, 3.2, 6.3)]
BLADE_T = 0.65
EYE_R, EYE_H = 2.75, 1.75    # the eye: radius on the face, height over the socket's floor
HOT = [(-1.35, -0.1), (1.35, -0.1)]   # its two hot points (on the face: across, up)
HOT_R = 0.62
NECK_R = 1.45

MATS = {  # name: (palette index, metallic, roughness, emission strength in its own colour or None)
    "steel": (0x6a, 0.45, 0.25, None), "steel_dark": (0x66, 0.45, 0.35, None),
    "pod_light": (0x0a, 0.5, 0.28, 0.05), "pod": (0x07, 0.5, 0.3, 0.05), "pod_dark": (0x04, 0.5, 0.35, None),
    "lip": (0x06, 0.5, 0.3, None), "socket": (0x01, 0.3, 0.5, None),
    "blade": (0x06, 0.55, 0.3, None), "blade_lit": (0x08, 0.55, 0.26, None),
    "eye_rim": (0x72, 0.0, 0.25, 0.35), "eye": (0x76, 0.0, 0.18, 0.55), "eye_hot": (0x7a, 0.0, 0.15, 0.62),
}


def materials():
    pal = k.level_palette()
    m = {}
    for name, (index, metallic, roughness, glow) in MATS.items():
        extra = dict(emission=pal[index], emission_strength=glow) if glow else {}
        m[name] = k.material(f"hpod_{name}", palette=index, metallic=metallic, roughness=roughness, **extra)
    return m


# --- The steel -----------------------------------------------------------------------------------------------------

def bar(m):
    """The bar across the top: a profile (its back edge rounded, a flat top, the front edge rounded into the south
    face, which falls away under it) run across the sprite, its ends flush with the sprite's edges (side by side, two
    bars meet)."""
    y0, y1 = BAR
    fy0, fy1, fz = BAR_FALL
    r = 0.9
    profile = [(y1, BOTTOM)]
    for i in range(7):                                  # the back edge, rounded
        a = math.radians(90.0 * i / 6)
        profile.append((y1 - r + r * math.cos(a), BAR_TOP - r + r * math.sin(a)))
    slope = math.atan2(BAR_TOP - fz, fy0 - fy1)         # the south face's fall
    for i in range(1, 7):                               # the front edge, rounded into the south face
        a = math.radians(90.0) + (math.radians(90.0) - slope) * i / 6
        profile.append((fy0 + 0.6 + 0.6 * math.cos(a), BAR_TOP - 0.6 + 0.6 * math.sin(a)))
    profile += [(y0, fz), (y0, BOTTOM)]
    obj = mk.prism("bar", ccw(profile), -12.0, 12.0, m["steel"], axis="x")
    mk.shade(obj, 40)
    mk.paint(obj, lambda c, n: m["steel"] if n.z > 0.75 and c.y > fy0 - 0.3 else m["steel_dark"])
    return obj


def boss(m):
    hw, y0, y1, top = BOSS
    poly = ccw(chaikin([(-hw, y0), (hw, y0), (hw, y1), (-hw, y1)], 2))
    return relief("boss", [poly], lambda x, y, d: BAR_TOP - 0.4 + (top - BAR_TOP + 0.4) * round_edge(d, 0.7), m,
                  paint=lambda x, y, d: "steel" if d > 0.3 else "steel_dark", side="steel_dark", bottom=BAR_TOP - 1.5,
                  spacing=0.3, borders=[(lambda x, y, d: d, 0.3)])


def arch(m):
    """The arch over the seam at x = 12, whole (cut into the sprite's two ends afterwards)."""
    left = ARCH
    right = [(-x, y) for x, y in reversed(left[1:-1])]
    poly = ccw(chaikin([(12.0 + x, y) for x, y in left + right], 2))
    s0, s1 = ARCH_STEP

    def height(x, y, d):
        top = LEG_TOP + (ARCH_TOP - LEG_TOP) * smoothstep(s1, s0, y)
        top -= HOOK_DROP * smoothstep(2.4, 0.2, y)
        return 1.0 + (top - 1.0) * round_edge(d, RIM)

    def paint(x, y, d):
        return "steel" if d > 0.3 else "steel_dark"
    return relief("arch", [poly], height, m, paint=paint, side="steel_dark", bottom=BOTTOM, spacing=0.3,
                  borders=[(lambda x, y, d: d, 0.3)], band=1.3)


# --- The pod -------------------------------------------------------------------------------------------------------

def frame():
    """The pod's frame: back (along its axis, away from the face), up (across the face, up the screen), out (the
    face's normal), unsquashed."""
    a = math.radians(POD_TILT)
    back = Vector((0.0, math.sin(a), -math.cos(a)))
    up = Vector((0.0, math.cos(a), math.sin(a)))
    out = -back
    return back, up, out


def squash(obj):
    """The pod's heights squashed about the face's middle."""
    obj.data.transform(Matrix.Translation((0, 0, FACE.z)) @ Matrix.Diagonal((1.0, 1.0, POD_SQUASH, 1.0)) @
                       Matrix.Translation((0, 0, -FACE.z)))
    obj.data.update()
    return obj


def lathe(name, profile, mat):
    """A closed solid turned about the axis through the face's middle: rings at (t, radius) along it (t > 0: back),
    from the socket floor's middle (radius 0) round to the rear dome's apex (radius 0)."""
    back, up, _ = frame()
    x = Vector((1.0, 0.0, 0.0))
    rings = []
    unit = [mk.superellipse_point(2 * math.pi * j / SEGMENTS, POWER) for j in range(SEGMENTS)]
    for t, r in profile[1:-1]:
        c = FACE + back * t
        rings.append([c + (x * a + up * b) * r * R_SCALE for a, b in unit])
    return k.loft(name, rings, mat, start_point=tuple(FACE + back * profile[0][0]),
                  end_point=tuple(FACE + back * profile[-1][0]))


def axial(c):
    """Where a point of the (squashed) pod lies along its axis and how far out from it: (t, radius)."""
    back, _, _ = frame()
    q = Vector((c.x, c.y, FACE.z + (c.z - FACE.z) / POD_SQUASH)) - FACE
    t = q.dot(back)
    return t, (q - back * t).length


def shell(m):
    """The pod's shell: the socket's floor and wall, the lip, the body and the rear dome, one closed solid turned
    about its axis and squashed; the body in bands of grey by how it faces the game's sun (cut along smooth
    contours), the lip grey, the socket dark."""
    profile = SOCKET[::-1] + LIP[::-1][1:] + BODY[1:]
    obj = squash(lathe("pod_shell", profile, m["pod"]))
    k.recalc_normals(obj)
    mesh = obj.data
    normals = [Vector((0, 0, 0)) for _ in mesh.vertices]
    for poly in mesh.polygons:
        for v in poly.vertices:
            normals[v] += poly.normal * poly.area
    values = []
    for v, n in zip(mesh.vertices, normals):
        t, _ = axial(v.co)
        values.append(0.5 if t < 0.02 else (n.normalized().dot(SUN) if n.length > 0 else 0.0))
    band_split(obj, values, [(-9.0, m["pod_dark"]), (0.38, m["pod"]), (0.8, m["pod_light"])])
    slots = {}
    for poly in obj.data.polygons:
        t, r = axial(poly.center)
        key = "socket" if (r < 7.42 and t < 1.3) else "lip" if t < 0.02 else None
        if key:
            if key not in slots:
                slots[key] = mk.slot_of(obj, m[key])
            poly.material_index = slots[key]
    return k.smooth(obj, 60)


def on_face(s, v, w):
    """A point of the face's own frame (across, up, out from the socket's floor) in the model, unsquashed."""
    back, up, out = frame()
    return FACE + Vector((s, 0.0, 0.0)) + up * v + out * (w - SOCKET_FLOOR)


def blades(m):
    """The four shutter blades on the socket's floor, on its diagonals."""
    out = []
    for i, (mid, spread, r0, r1) in enumerate(BLADES):
        pts = []
        for j in range(9):
            a = math.radians(mid - spread + 2 * spread * j / 8)
            pts.append((r1 * math.cos(a), r1 * math.sin(a)))
        inner = spread * 0.55
        for j in range(5):
            a = math.radians(mid + inner - 2 * inner * j / 4)
            pts.append((r0 * math.cos(a), r0 * math.sin(a)))
        obj = mk.prism(f"blade{i}", ccw(pts), -0.2, BLADE_T, m["blade"])
        mk.bevel(obj, 0.18, 2, 30)
        mk.shade(obj, 35)
        back, up, outn = frame()
        basis = Matrix(((1.0, up.x, outn.x, 0.0), (0.0, up.y, outn.y, 0.0), (0.0, up.z, outn.z, 0.0), (0, 0, 0, 1)))
        obj.data.transform(Matrix.Translation(on_face(0.0, 0.0, 0.0)) @ basis)
        squash(obj)
        mk.paint(obj, lambda c, n: m["blade_lit"] if n.dot(SUN) > 0.75 else None)
        out.append(obj)
    return out


class OnFace(Ellipsoid):
    """An ellipsoid in the face's frame (radii across, up, out), squashed with the pod."""

    def point(self, d):
        back, up, outn = frame()
        r = self.radii
        local = Vector((d.x * r.x, d.y * r.y, d.z * r.z))
        p = self.centre + Vector((local.x, 0, 0)) + up * local.y + outn * local.z
        p.z = FACE.z + (p.z - FACE.z) * POD_SQUASH
        nl = Vector((d.x / r.x, d.y / r.y, d.z / r.z))
        n = Vector((nl.x, 0, 0)) + up * nl.y + outn * nl.z
        n.z /= POD_SQUASH
        return p, n.normalized()


def eye(m):
    """The red eye: a glowing dome on the socket's floor, darker round its foot, with its two hot points."""
    centre = on_face(0.0, 0.0, 0.0)
    shape = OnFace(centre, (EYE_R, EYE_R * 0.96, EYE_H))
    _, _, outn = frame()

    def rim(p, n):
        return n.dot(TOWARDS_VIEW)
    parts = [painted_ball("eye", shape, [(rim, (0.45,), ("eye_rim", "eye"))], m, subdivisions=3)]
    for i, (s, v) in enumerate(HOT):
        hot = OnFace(on_face(s, v, EYE_H * 0.78), (HOT_R, HOT_R, HOT_R * 0.7))
        parts.append(painted_ball(f"eye_hot{i}", hot, [(rim, (-2.0,), ("eye_hot", "eye_hot"))], m, subdivisions=2))
    return parts


def neck(m):
    """The grey neck from the pod's rear dome up to the boss."""
    back, up, _ = frame()
    start = FACE + back * 9.0 + up * 6.4
    start.z = FACE.z + (start.z - FACE.z) * POD_SQUASH
    end = Vector((0.0, BOSS[1] + 0.6, BAR_TOP - 0.1))
    pts = [start.lerp(end, i / 6) for i in range(7)]
    obj = mk.tube("neck", [tuple(p) for p in pts], NECK_R, m["pod"], 16)
    k.smooth(obj, 60)
    mk.paint(obj, lambda c, n: m["pod_light"] if n.dot(SUN) > 0.7 else m["pod_dark"] if n.dot(SUN) < 0.2 else None)
    return obj


# --- Build, checks, export -----------------------------------------------------------------------------------------

def build_pod(m):
    parts = [bar(m), boss(m)]
    whole_arch = arch(m)
    mk.apply(whole_arch)
    right_end = cut(whole_arch, (-100.0, 12.0, -100.0, 100.0), m["steel_dark"])
    left_end = cut(whole_arch, (12.0, 100.0, -100.0, 100.0), m["steel_dark"])
    left_end.data.transform(Matrix.Translation((-24.0, 0.0, 0.0)))
    right_end.name, left_end.name = "arch_right", "arch_left"
    bpy.data.objects.remove(whole_arch)
    parts += [right_end, left_end]
    parts += [shell(m)] + blades(m) + eye(m) + [neck(m)]
    for obj in parts:
        mk.apply(obj)
    bpy.context.view_layer.update()
    return parts


def pair_preview(prefix, objects):
    """Two side by side, as BRAINIAC places them (renders <prefix>_top.png and _3q.png)."""
    copies = []
    for obj in objects:
        copy = obj.copy()
        copy.data = obj.data.copy()
        bpy.context.scene.collection.objects.link(copy)
        copy.location.x += 24.0
        copies.append(copy)
    mk.preview(prefix, objects + copies, size=(48, 28), scale=10, distance=1.4, centre=(12.0, 0.0))
    for obj in copies:
        bpy.data.objects.remove(obj)


def build():
    options = k.args()
    out = mk.outdir(options)
    k.reset()
    m = materials()
    parts = build_pod(m)
    triangulate(parts)
    pod = join(parts, NAME)
    pod.data.name = NAME
    if "check" in options:
        sheet = options["check"]
        sheet = os.path.join(sheet, "enemy_5.png") if os.path.isdir(sheet) else sheet
        mk.compare("5 %d" % SPRITE, mk.coverage([pod], 24, 28), k.sprite_mask(sheet, SPRITE))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mk.report(NAME, [pod], os.path.join(out, NAME + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + NAME, [pod])
    if "pair" in options:
        pair_preview(options["pair"], [pod])


if __name__ == "__main__":
    build()
