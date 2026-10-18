"""The flying pod machine of BONUS, New Deli, VAULT, DELI RUIN and DEEP ICE (sheet C sprite 191, 2x2:
24 x 28 pixels; sky and top layers) and the same machine on BONUS's ground (C 155, the sprite turned
upside down: models.cfg turns the model round, yaw=180), polished (2026-10-18; it replaces
wave2_f_more.py's pod_turret(), two blue ellipsoids with green caps under two grey cans). models.cfg:
sprite c 191 pod_turret yaw=0, sprite c 155 pod_turret yaw=180, frame c 193 pod_turret_193, frame c 195
pod_turret_195, frame c 157 pod_turret_193, frame c 159 pod_turret_195.

As the 4x upscale draws it: two blue shells side by side (the sprite's ramp 3, rows 17-24 and the full
width; a notch between them at the bottom, columns 11-12), rounded at their outer lower corners, where a
green fin runs along their rim (ramp 2: columns 0-4 of rows 18-24 and the mirror); on the shells' upper
corners two steel cups (ramp 6, columns 1-7 and 16-22 of rows 9-17), their dark bores facing up and up
the screen, a light lip round them, their lit sides below; between them a grey cowl (ramp 0, columns 7-16
of rows 3-12), its rounded end up the screen, two dark slots in its top either side of a light middle
rib; and in front of the cowl, over the shells' middle, a pink nozzle (ramp 5, columns 9-14 of rows
13-22), leaning up the screen, its dark mouth at its upper end.

The animation (191 193 195 195 195 195 193 193 193 193 191; on the ground 155 157 159 ...) only lights
the fins: dark green (191), lighter (193), bright green (195, the vivid ramp 12). One model per frame:
pod_turret (191, 155), pod_turret_193 (193, 157) and pod_turret_195 (195, 159), the same shapes with the
fins' own colours and glow. Their bounds are the same, so the game centres them alike.

The sprite is symmetric about the edge between its columns 11 and 12 (x = 0 here), so the model is
built about x = 0 and its left parts mirrored. Origin at the sprite's centre (pixel 12, 14); +Y up the
sprite, +Z towards the camera.

Replaces wave2_f_more.py's pod_turret() (its @model registration): remove it so that it doesn't overwrite
these models (pod_parts() and pod_materials() stay: pod_dome uses them).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette
against enemy_C.png: 191 as built, and 155 with the model turned round), --preview <prefix>.
"""
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
from polish_jets import Curve  # noqa: E402
from polish_sphere_nozzle import split_along  # noqa: E402

# The frames: (model, sprites (in the air, on the ground), the fins' colours: their face and their
# rim (palette index, emission strength)).
FRAMES = [
    ("pod_turret", (191, 155), {"fin": (0x26, 0.35), "fin_edge": (0x28, 0.45)}),
    ("pod_turret_193", (193, 157), {"fin": (0x29, 0.7), "fin_edge": (0x2b, 0.8)}),
    ("pod_turret_195", (195, 159), {"fin": (0xc8, 1.15), "fin_edge": (0xcb, 1.3)}),
]

# The left shell: its middle and half-sizes in plan (a superellipse of power PLAN_POWER: columns 0-11 of
# rows 13-24, the outline two thirds covered), the height of its rim, of its crown above the rim and
# the power of its dome (higher: fuller), how far its edge tucks under below the rim.
SHELL_CENTRE, SHELL_RADII, PLAN_POWER = Vector((-5.75, -5.2)), (5.95, 6.5), 3.0
SHELL_RIM, SHELL_CROWN, DOME_POWER, SHELL_TUCK = 1.4, 3.6, 2.2, 1.2
# The fin along the shell's rim: the angles round its middle (degrees from +x, counter-clockwise: from
# the outer side round the lower corner to the bottom) and how far in from the outline it reaches
# (as a fraction of the plan's radius, in its middle; it narrows to nothing at its ends); the brighter
# edge band within it.
FIN_ANGLES, FIN_REACH, FIN_EDGE = (168.0, 278.0), 0.72, 0.88

# The left cup: its mouth's middle in plan (x, y), its height, the tilt of its axis (up the screen and
# outwards, degrees), its outer radius, length, the lip and the bore's depth.
CUP_MOUTH, CUP_Z = Vector((-7.25, 2.05)), 7.3
CUP_TILT, CUP_LEAN = 44.0, 13.0
CUP_R, CUP_LENGTH, CUP_LIP, CUP_BORE = 3.05, 5.6, 0.48, 1.25

# The cowl: along y, its half-width and its top's height (it stands on COWL_BASE): rows 3-12, columns
# 7-16, its rounded end up the screen.
COWL_BASE = 1.2
COWL = Curve([(0.2, 4.5, 5.3), (1.5, 4.6, 6.1), (5.5, 4.6, 6.4), (7.5, 4.45, 6.35), (8.8, 4.0, 6.05),
              (9.6, 3.4, 5.6), (10.2, 2.6, 5.0), (10.55, 1.6, 4.2), (10.7, 0.4, 3.4)])
COWL_Y = (0.2, 10.7)
# The slots in its top (columns 9-10 and 13-14 of rows 7-11): middle x, from y, to y, half-width; and the
# rib between them (columns 11-12 of rows 5-12).
SLOT_X, SLOT_Y, SLOT_HALF = 2.05, (2.0, 7.3), 1.08
RIB_Y, RIB_HALF, RIB_RISE = (0.5, 9.3), 0.75, 0.38

# The nozzle: its base (inside the shells), the tilt of its axis up the screen (degrees), its length to
# the lip, its radius at the base and at the mouth, the lip and the bore's depth.
NOZZLE_BASE, NOZZLE_TILT = Vector((0.0, -7.0, 2.4)), 41.0
NOZZLE_LENGTH, NOZZLE_R0, NOZZLE_R1, NOZZLE_LIP, NOZZLE_BORE = 8.1, 2.45, 3.0, 0.42, 1.2


# --- Helpers ----------------------------------------------------------------------------------------

def superellipse(theta, rx, ry, power):
    c, s = math.cos(theta), math.sin(theta)
    return (rx * math.copysign(abs(c) ** (2 / power), c), ry * math.copysign(abs(s) ** (2 / power), s))


def turned(name, profile, start, direction, segments, up=(0, 0, 1)):
    """A part turned about an axis: profile is (t, radius) pairs along `direction` from `start` (t may
    go back, for lips and bores; the ends close to the axis). Returns the object and, per profile
    step, the index of its first face (the loft's faces go ring pair by ring pair)."""
    rings = []
    d = Vector(direction).normalized()
    side = d.cross(Vector(up))
    if side.length < 1e-6:
        side = d.cross(Vector((1, 0, 0)))
    side.normalize()
    upv = side.cross(d).normalized()
    for t, r in profile:
        if r < 1e-4:
            continue  # an end on the axis: closed by the fan
        c = Vector(start) + d * t
        rings.append([c + (side * math.cos(2 * math.pi * j / segments) + upv * math.sin(2 * math.pi * j / segments)) * r
                      for j in range(segments)])
    obj = k.loft(name, rings, None, start_point=Vector(start) + d * profile[0][0],
                 end_point=Vector(start) + d * profile[-1][0])
    return obj


def paint(obj, mats, key):
    """Gives each face the material key(face index, face) names (keys of mats)."""
    keys = [key(i, poly) for i, poly in enumerate(obj.data.polygons)]
    names = []
    for name in keys:
        if name not in names:
            names.append(name)
    obj.data.materials.clear()
    for name in names:
        obj.data.materials.append(mats[name])
    for poly, name in zip(obj.data.polygons, keys):
        poly.material_index = names.index(name)
    return obj


def axis(tilt, lean=0.0, side=-1):
    """A direction tilted `tilt` degrees from straight up towards +y, and `lean` degrees outwards
    (towards side * x)."""
    t, l = math.radians(tilt), math.radians(lean)
    return Vector((side * math.sin(l), math.sin(t) * math.cos(l), math.cos(t) * math.cos(l))).normalized()


# --- The parts (left side) ---------------------------------------------------------------------------

def fin_field(x, y, edge=False):
    """Positive on the fin (or on its edge band): how far past the fin's inner border a point of the
    left shell's plan lies."""
    dx, dy = x - SHELL_CENTRE.x, y - SHELL_CENTRE.y
    angle = math.degrees(math.atan2(dy / SHELL_RADII[1], dx / SHELL_RADII[0])) % 360
    rho = ((abs(dx) / SHELL_RADII[0]) ** PLAN_POWER + (abs(dy) / SHELL_RADII[1]) ** PLAN_POWER) ** (1 / PLAN_POWER)
    a0, a1 = FIN_ANGLES
    taper = max(0.0, 1 - ((angle - (a0 + a1) / 2) / ((a1 - a0) / 2)) ** 4) if a0 <= angle <= a1 else 0.0
    reach = FIN_EDGE if edge else FIN_REACH
    return rho - (1 - (1 - reach) * taper) + 1e-3


def shell(mats):
    """The left blue shell: rings in plan from under its tucked edge over the rim to the crown, cut
    along the fin's borders; the fin along its outer lower rim."""
    rings_spec = []
    for i in range(4):  # the edge tucking under, up to the rim
        a = (math.pi / 2) * i / 4
        rings_spec.append((1 - 0.12 * math.cos(a), SHELL_RIM - SHELL_TUCK * math.cos(a)))
    for i in range(0, 13):  # the dome from the rim to the crown
        a = (math.pi / 2) * i / 13
        rings_spec.append((math.cos(a) ** (2 / DOME_POWER), SHELL_RIM + SHELL_CROWN * math.sin(a) ** (2 / DOME_POWER)))
    segments = 52
    rings = []
    for scale, z in rings_spec:
        ring = []
        for j in range(segments):
            px, py = superellipse(2 * math.pi * j / segments, SHELL_RADII[0] * scale, SHELL_RADII[1] * scale,
                                  PLAN_POWER)
            ring.append(Vector((SHELL_CENTRE.x + px, SHELL_CENTRE.y + py, z)))
        rings.append(ring)
    obj = k.loft("shell", rings, None, start_point=(SHELL_CENTRE.x, SHELL_CENTRE.y, SHELL_RIM - SHELL_TUCK),
                 end_point=(SHELL_CENTRE.x, SHELL_CENTRE.y, SHELL_RIM + SHELL_CROWN))
    # The fin's borders cut into the faces, so that they run smoothly.
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    for edge in (False, True):
        split_along(bm, {v: fin_field(v.co.x, v.co.y, edge) for v in bm.verts}, 0.0)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bm.to_mesh(obj.data)
    bm.free()
    k.recalc_normals(obj)

    def key(i, poly):
        c = poly.center
        if fin_field(c.x, c.y, True) > 0:
            return "fin_edge"
        if fin_field(c.x, c.y) > 0:
            return "fin"
        return "shell"
    paint(obj, mats, key)
    return k.smooth(obj, 50)


def rolled(t_end, r, lip, bore, rin_scale=0.95, steps=5):
    """The end of a turned part with a rolled lip and a bore: (t, r) from the wall's top over the lip
    into the bore; the bore's floor closes it (the profile's last point, on the axis)."""
    out = [(t_end - lip, r)]
    for i in range(1, steps + 1):
        a = math.pi * i / steps
        out.append((t_end - lip + lip * math.sin(a), r - lip + lip * math.cos(a)))
    rin = r - 2 * lip
    return out + [(t_end - lip - 0.3, rin), (t_end - bore, rin * rin_scale), (t_end - bore - 0.05, 0.0)]


def cup(mats):
    """The left steel cup: its wall, a rolled lip, its dark bore."""
    d = axis(CUP_TILT, CUP_LEAN, -1)
    mouth = Vector((CUP_MOUTH.x, CUP_MOUTH.y, CUP_Z))
    start = mouth - d * CUP_LENGTH
    r = CUP_R
    profile = [(0.0, r * 0.85), (0.3, r * 0.98), (0.7, r)] + rolled(CUP_LENGTH, r, CUP_LIP, CUP_BORE)
    obj = turned("cup", profile, start, d, 32)
    n = 32
    # Ring pairs: 0-2 the wall, 3-7 the lip, 8-9 the bore; then the fans closing the foot and the bore.
    parts = ["cup"] * 3 + ["cup_lip"] * 5 + ["cup_bore"] * 2

    def key(i, poly):
        pair = i // n
        if pair < len(parts):
            return parts[pair]
        return "cup" if pair == len(parts) else "cup_bore"
    paint(obj, mats, key)
    return k.smooth(obj, 50)


def cowl(mats):
    """The grey cowl: arched sections along y, its upper end rounded."""
    y0, y1 = COWL_Y
    ys = [y0 + (y1 - y0) * i / 26 for i in range(26)]
    ys = sorted(set(ys + [y1 - 0.9 * (1 - math.cos(math.pi / 2 * i / 6)) for i in range(6)]))
    rings = []
    for y in ys:
        hw, top = COWL(y)
        rings.append(k.ring(y, max(hw, 0.05), max(top - COWL_BASE, 0.05), 24, z=COWL_BASE, top=1.0, bottom=0.25,
                            power=2.6))
    obj = k.loft("cowl", rings, mats["cowl"], start_point=(0, y0, COWL_BASE), end_point=(0, y1, COWL_BASE + 1.2))
    k.smooth(obj, 50)
    parts = [obj]

    def top_z(x, y):
        hw, top = COWL(y)
        u = min(abs(x) / max(hw, 0.05), 1.0)
        return COWL_BASE + (top - COWL_BASE) * (1 - u ** 2.6) ** (1 / 2.6)
    # The two slots: dark pads lying in the top, a little proud of it, so they read as openings.
    for side in (-1, 1):
        rings = []
        ya, yb = SLOT_Y
        for i in range(1, 16):
            t = i / 16
            y = ya + (yb - ya) * t
            f = math.sqrt(max(0.0, 1 - (2 * t - 1) ** 6))
            x = side * SLOT_X
            rings.append(k.ring(y, SLOT_HALF * f, 0.3, 12, x=x, z=top_z(x, y) - 0.17, top=1.0, bottom=1.0))
        x = side * SLOT_X
        slot = k.loft(f"slot{side}", rings, mats["slot"], start_point=(x, ya, top_z(x, ya) - 0.2),
                      end_point=(side * SLOT_X, yb, top_z(side * SLOT_X, yb) - 0.2))
        parts.append(k.smooth(slot, 60))
    # The light rib down the middle.
    rings = []
    ya, yb = RIB_Y
    for i in range(1, 20):
        t = i / 20
        y = ya + (yb - ya) * t
        f = math.sqrt(max(0.0, 1 - (2 * t - 1) ** 8))
        rings.append(k.ring(y, RIB_HALF * f, RIB_RISE + 0.3, 12, z=top_z(0.0, y) - 0.3, top=1.0, bottom=0.3, power=2.4))
    rib = k.loft("rib", rings, mats["rib"], start_point=(0, ya, top_z(0, ya) - 0.3),
                 end_point=(0, yb, top_z(0, yb) - 0.3))
    parts.append(k.smooth(rib, 60))
    return parts


def nozzle(mats):
    """The pink nozzle: a tube widening to its mouth, a rolled lip, the dark bore."""
    d = axis(NOZZLE_TILT)
    L, r0, r1 = NOZZLE_LENGTH, NOZZLE_R0, NOZZLE_R1
    profile = [(0.0, r0)]
    for i in range(1, 9):
        t = i / 8
        profile.append(((L - NOZZLE_LIP) * 0.9 * t, r0 + (r1 - r0) * t ** 1.8))
    profile += rolled(L, r1, NOZZLE_LIP, NOZZLE_BORE, 0.9)
    obj = turned("nozzle", profile, NOZZLE_BASE, d, 32)
    n = 32
    # Ring pairs: 0-8 the tube, 9-13 the lip, 14-15 the bore; then the fans closing the base and the bore.
    parts = ["nozzle"] * 9 + ["nozzle_lip"] * 5 + ["nozzle_bore"] * 2

    def key(i, poly):
        pair = i // n
        if pair < len(parts):
            return parts[pair]
        return "nozzle" if pair == len(parts) else "nozzle_bore"
    paint(obj, mats, key)
    return k.smooth(obj, 50)


def materials(fins):
    pal = k.level_palette()
    m = {
        "shell": k.material("podt_shell", palette=0x3a, metallic=0.4, roughness=0.3),
        "cup": k.material("podt_cup", palette=0x6c, metallic=0.45, roughness=0.26),
        "cup_lip": k.material("podt_cup_lip", palette=0x6d, metallic=0.45, roughness=0.22),
        "cup_bore": k.material("podt_cup_bore", palette=0x62, metallic=0.2, roughness=0.6),
        "cowl": k.material("podt_cowl", palette=0x08, metallic=0.4, roughness=0.3),
        "rib": k.material("podt_rib", palette=0x0b, metallic=0.4, roughness=0.25),
        "slot": k.material("podt_slot", palette=0x01, metallic=0.2, roughness=0.6),
        "nozzle": k.material("podt_nozzle", palette=0x5c, metallic=0.25, roughness=0.3),
        "nozzle_lip": k.material("podt_nozzle_lip", palette=0x5e, metallic=0.25, roughness=0.26),
        "nozzle_bore": k.material("podt_nozzle_bore", palette=0x52, metallic=0.1, roughness=0.6),
    }
    for key, (index, strength) in fins.items():
        m[key] = k.material(f"podt_{key}_{index:x}", palette=index, roughness=0.3, emission=pal[index],
                            emission_strength=strength)
    return m


def build_model(fins):
    k.reset()
    mats = materials(fins)
    left = [shell(mats), cup(mats)]
    for part in left:
        mirror = k.mirror_x(part, part.name + "_r")
        mirror.data.name = mirror.name
        k.smooth(mirror, 50)
    cowl(mats)
    nozzle(mats)


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


def bounds():
    zs = [(obj.matrix_world @ v.co).z for obj in bpy.context.scene.objects if obj.type == "MESH"
          for v in obj.data.vertices]
    return min(zs), max(zs)


def check(sheet, sprites):
    """The silhouette in the air (191) as built, on the ground (155) turned round as models.cfg turns it."""
    k.check_silhouette(sheet, sprites[0])
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    for obj in meshes:
        obj.matrix_world = Matrix.Rotation(math.pi, 4, "Z")
    print("-- turned round (yaw 180) against C %d:" % sprites[1])
    k.check_silhouette(sheet, sprites[1])
    for obj in meshes:
        obj.matrix_world = Matrix.Identity(4)


def build():
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    for name, sprites, fins in FRAMES:
        build_model(fins)
        used = {m.name for o in bpy.context.scene.objects if o.type == "MESH" for m in o.data.materials}
        print("== %s (C %d, %d): %d triangles, %d materials, z %.2f to %.2f: %s" % (
            name, *sprites, triangles(), len(used), *bounds(), ", ".join(sorted(used))))
        if "check" in options and name == FRAMES[0][0]:
            sheet = options["check"]
            check(os.path.join(sheet, "enemy_C.png") if os.path.isdir(sheet) else sheet, sprites)
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        path = os.path.join(outdir, name + ".glb")
        k.export(path)
        print("%s: %.1f KB" % (path, os.path.getsize(path) / 1024))
        if "preview" in options:
            k.preview(options["preview"] + name)


if __name__ == "__main__":
    build()
