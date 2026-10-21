"""MARKERS' small blue torpedoes on the ground (sheet V sprite 235, 2x2: 24 x 16 pixels in the 24 x 28 cell, its nose to
the right, and V 237, the same picture mirrored pixel for pixel about the cell's middle, nose to the left; custom enemies
of episode 2, not animated), polished (2026-10-21; it replaces wave3_t_ships.py's torpedo(), a lathed body with chamfered
wings). models.cfg: sprite v 235 blue_torpedo yaw=0, sprite v 237 blue_torpedo_l yaw=0 (unchanged).

MARKERS' events make them in pairs (custom enemies, events 49 and 52: V 237 at x 130 on the ground layer, V 235 at x
170 on ground 2, armour 10, links 1-6; ticks 1045-1065, 1185-1285, 2545-2565, 2845-2865), move them down the screen
(event 19, 2 pixels a tick) and then accelerate each sideways towards its nose (event 20: V 237 to the left, V 235 to the
right), so they fly apart nose first: as the sprites are drawn (yaw=0). No other enemy shows V 235 or V 237, and no other
sprite of any sheet is their pixels mirrored, turned or in other ramps.

As the sprite draws V 235 (columns and rows of the 24 x 28 cell; a black outline, palette index 1, drawn round it all,
is not geometry): a steel-blue torpedo (ramp 3) lying across the screen, its axis along row 12.5 (y 1.0), its nose to the
right. From the tail: a ring round the tail seen edge-on (columns 1-2 of rows 9-16: 8 pixels across, 2 deep, lit at rows
11 and 14) with a gap behind it (column 3); a narrow dark motor section (columns 4-7 of rows 11-14: radius 2) with two
blue lights on short struts sticking out either side (columns 5 and 7 of rows 8-9 and 16-17; ramp 9); a lit collar
(column 8); the wing section (columns 9-10: radius 3) carrying a pair of square swept wings in the plane of the screen
(columns 9-12 of rows 6-9 and 16-19); a dark joint round the body (column 11); the forward body (columns 12-19: radius
3, brightest along rows 11-12 just ahead of the joint), a pair of small swept canards (columns 16-19 of rows 8-9 and
16-17), and the blunt nose (columns 20-22, rounding in to the tip at column 22).

Built as turned parts about the axis (polish_pink_torpedo's way): the body one profile turned round it (the motor
section with two lit ribs, the collar, the wing section, the joint's groove, the forward body, a seam behind the nose
cap and the nose), the tail ring a round band of rounded section with a short dark nozzle inside it, held by four thin
struts; the wings and the canards thin plates in the plane of the axis (prisms of their plans, their edges well rounded
by a bevel), a lit crease along each wing (rows 8 and 17: a thin bar); the lights small blue lamps on short pylons
(small tapering plates) out from the motor section, glowing a little in their own colour (well under 1: the bloom
adds). V 237 is the finished model mirrored about x = 0.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground (z = 0); origin at
the sprite's centre (pixel 12, 14): column c is x = c + 0.5 - 12, row r is y = 13.5 - r. It lies on the ground (the ring's
underside at z = 0; the game centres ground models in height and lifts them onto the ground).

Replaces wave3_t_ships.py's torpedo(), blue_torpedo() and blue_torpedo_l() (its "# --- V 235 and its mirror image V 237"
section with the two @model registrations, and the docstring's blue_torpedo lines), and wave3_t_art.py's TORPEDO (which
nothing reads): remove them so that they don't overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against the
torpedo's own pixels in enemy_V.png, its outline left out), --preview <prefix>, --only <name,...>.
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402

NAMES = ("blue_torpedo", "blue_torpedo_l")
SPRITES = {"blue_torpedo": 235, "blue_torpedo_l": 237}
AXIS_Y, AXIS_Z = 1.0, 4.0     # the axis (between rows 12 and 13), at the tail ring's radius above the ground
SEGMENTS = 32
# The body's profile along x: (x, radius) from the motor's back to the nose's tip.
BODY = [(-8.55, 0.0), (-8.5, 1.3), (-8.3, 1.65), (-7.8, 1.78), (-4.6, 1.8), (-4.35, 1.95), (-4.15, 2.3), (-3.75, 2.35),
        (-3.45, 2.3), (-3.25, 2.55), (-3.05, 2.85), (-2.7, 2.98), (-1.35, 3.0), (-1.05, 2.88), (-0.85, 2.62),
        (-0.3, 2.6), (-0.1, 2.85), (0.2, 2.98), (8.0, 3.0), (8.25, 2.82), (8.45, 2.82), (8.7, 2.97), (8.9, 2.93), (9.7, 2.72), (10.3, 2.38), (10.75, 1.9),
        (11.05, 1.3), (11.22, 0.65), (11.28, 0.0)]
# Where the profile's parts begin and end (for the paint): the collar, the joint's groove, the seam behind the nose.
COLLAR = (-4.2, -3.4)
JOINT = (-1.05, -0.1)
SEAM = (8.1, 8.6)
# The tail ring: its middle along x, half its depth, its inner and outer radii; the nozzle inside it.
RING = (-10.0, 1.0, 3.15, 4.0)
NOZZLE = [(-9.9, 0.0), (-9.85, 0.85), (-9.6, 1.15), (-8.9, 1.35), (-8.5, 1.4)]
RING_STRUTS = (1.25, 3.25, 0.26, -9.3)   # from radius, to radius, bar radius, x
# The wing (upper; the lower is its mirror image about the axis): its plan, (x, distance from the axis).
WING = [(-3.05, 2.2), (1.0, 2.2), (1.0, 5.4), (0.4, 6.6), (-0.3, 7.0), (-2.5, 7.0), (-3.05, 6.55)]
WING_THICK = 0.62
CANARD = [(3.95, 2.2), (8.1, 2.2), (8.1, 2.95), (6.3, 4.95), (4.4, 4.95), (3.95, 4.55)]
CANARD_THICK = 0.5
# The motor section's two lit ribs (columns 5 and 6): x, half their width, their radius.
RIBS = [(-6.5, 0.28, 2.08), (-5.5, 0.28, 2.08)]
# The struts with the blue lights (columns 5 and 7): x, the lamp's distance from the axis, its radius.
LIGHTS = [(-6.5, 3.5, 0.5), (-4.5, 3.95, 0.56)]
STRUT_FROM = 1.6
# The lit crease along each wing (rows 8 and 17): its distance from the axis, its radius.
WING_RIB = (4.35, 0.3)


def materials():
    pal = k.level_palette()
    return {
        "body": k.material("torp_body", palette=0x3b, metallic=0.55, roughness=0.24),
        "light": k.material("torp_light", palette=0x3d, metallic=0.55, roughness=0.2),
        "wing": k.material("torp_wing", palette=0x3a, metallic=0.55, roughness=0.26),
        "dark": k.material("torp_dark", palette=0x34, metallic=0.5, roughness=0.38),
        "motor": k.material("torp_motor", palette=0x34, metallic=0.55, roughness=0.34),
        "rib": k.material("torp_rib", palette=0x38, metallic=0.55, roughness=0.26),
        "nozzle": k.material("torp_nozzle", palette=0x31, metallic=0.4, roughness=0.5),
        "lamp": k.material("torp_lamp", palette=0x9a, metallic=0.1, roughness=0.15, emission=pal[0x9c],
                           emission_strength=0.45),
    }


# --- Helpers ---------------------------------------------------------------------------------------------------------

def lathe_x(name, profile, mat, segments=SEGMENTS, y=AXIS_Y, z=AXIS_Z):
    """A part turned about the axis along x (through y, z): profile [(x, radius), ...] in increasing x; ends of radius 0
    close to the axis."""
    rings = []
    for x, r in profile:
        if r <= 1e-6:
            continue
        rings.append([Vector((x, y + r * math.cos(2 * math.pi * j / segments), z + r * math.sin(2 * math.pi * j / segments)))
                      for j in range(segments)])
    start = Vector((profile[0][0], y, z))
    end = Vector((profile[-1][0], y, z))
    obj = k.loft(name, rings, mat, cap_start=True, cap_end=True, start_point=start, end_point=end)
    return k.smooth(obj, 50)


def band(name, x0, x1, r0, r1, mat, rounding=0.3, steps=4, segments=SEGMENTS):
    """A round band about the axis: from x0 to x1, its inner radius r0 and outer r1, all four edges rounded."""
    pts = []
    corners = [(x1, r1, 0.0), (x0, r1, 90.0), (x0, r0, 180.0), (x1, r0, 270.0)]
    for cx, cr, start in corners:
        ox = cx - rounding if cx == x1 else cx + rounding
        orad = cr - rounding if cr == r1 else cr + rounding
        for i in range(steps + 1):
            a = math.radians(start + 90.0 * i / steps)
            pts.append((ox + rounding * math.cos(a), orad + rounding * math.sin(a)))
    verts, faces = [], []
    n = len(pts)
    for j in range(segments):
        a = 2 * math.pi * j / segments
        for x, r in pts:
            verts.append((x, AXIS_Y + r * math.cos(a), AXIS_Z + r * math.sin(a)))
    for j in range(segments):
        for i in range(n):
            a0, a1 = j * n + i, j * n + (i + 1) % n
            b0, b1 = ((j + 1) % segments) * n + i, ((j + 1) % segments) * n + (i + 1) % n
            faces.append((a0, a1, b1, b0))
    obj = k.mesh_object(name, verts, faces, mat)
    k.recalc_normals(obj)
    return k.smooth(obj, 50)


def plate(name, plan, thick, mat, side, bevel=0.24):
    """A thin plate in the plane of the axis (plan: (x, distance from the axis); side +1 up the screen, -1 down)."""
    outline = [(x, AXIS_Y + side * d) for x, d in plan]
    if side < 0:
        outline = outline[::-1]
    obj = mk.prism(name, outline, AXIS_Z - thick / 2, AXIS_Z + thick / 2, mat)
    mk.bevel(obj, bevel, segments=3, angle=30.0)
    return k.smooth(obj, 40)


# --- The parts -------------------------------------------------------------------------------------------------------

def body(m):
    obj = lathe_x("body", BODY, m["body"])

    def pick(c, n):
        if COLLAR[0] <= c.x <= COLLAR[1]:
            return m["light"]
        if JOINT[0] <= c.x <= JOINT[1] or SEAM[0] <= c.x <= SEAM[1]:
            return m["dark"]
        if c.x < COLLAR[0]:
            return m["motor"]
        return None
    mk.paint(obj, pick)
    parts = [obj]
    for i, (x, half, r) in enumerate(RIBS):
        parts.append(band(f"rib{i}", x - half, x + half, 1.6, r, m["rib"], rounding=0.12, steps=2, segments=24))
    return parts


def tail(m):
    xm, half, r0, r1 = RING
    parts = [band("tail_ring", xm - half, xm + half, r0, r1, m["body"], rounding=0.32)]
    mk.paint(parts[0], lambda c, n: m["light"] if abs(n.x) > 0.7 else None)
    parts.append(lathe_x("nozzle", NOZZLE, m["nozzle"], 24))
    a0, a1, rr, x = RING_STRUTS
    for i in range(4):
        a = math.radians(45 + 90 * i)
        p0 = Vector((x, AXIS_Y + a0 * math.cos(a), AXIS_Z + a0 * math.sin(a)))
        p1 = Vector((x, AXIS_Y + a1 * math.cos(a), AXIS_Z + a1 * math.sin(a)))
        parts.append(k.smooth(mk.tube(f"ring_strut{i}", [p0, p1], rr, m["motor"], 8), 60))
    return parts


def fins(m):
    parts = []
    for side in (1, -1):
        tag = "u" if side > 0 else "d"
        parts.append(plate(f"wing_{tag}", WING, WING_THICK, m["wing"], side))
        d, rr = WING_RIB
        rib = [Vector((x, AXIS_Y + side * d, AXIS_Z + WING_THICK / 2 - 0.12)) for x in (-2.85, 0.85)]
        parts.append(k.smooth(mk.tube(f"wing_rib_{tag}", rib, rr, m["light"], 8), 60))
        parts.append(plate(f"canard_{tag}", CANARD, CANARD_THICK, m["wing"], side, bevel=0.2))
        for i, (x, d, r) in enumerate(LIGHTS):
            # A short pylon (a small plate tapering out from the body) with the lamp at its tip.
            pylon = [(x - 0.55, STRUT_FROM), (x + 0.55, STRUT_FROM), (x + 0.3, d - r * 0.4), (x - 0.3, d - r * 0.4)]
            parts.append(plate(f"pylon_{tag}{i}", pylon, 0.5, m["motor"], side, bevel=0.14))
            parts.append(mk.ball(f"lamp_{tag}{i}", (x, AXIS_Y + side * d, AXIS_Z), (r, r, r * 0.85), m["lamp"], 14, 8))
    return parts


def torpedo():
    m = materials()
    return body(m) + tail(m) + fins(m)


# --- Checks and building ------------------------------------------------------------------------------------------------

def own_mask(sheet, sprite):
    """The torpedo's own pixels: the sprite's, less its black outline (palette index 1)."""
    mask = k.sprite_mask(sheet, sprite)
    raw = open(sheet[:-4] + ".idx", "rb").read()
    x0, y0 = (sprite - 1) % 19 * 12, (sprite - 1) // 19 * 14
    return [[mask[r][c] and raw[(y0 + r) * 228 + x0 + c] != 1 for c in range(24)] for r in range(28)]


def mirrored(objects):
    mk.transform(objects, Matrix.Scale(-1, 4, (1, 0, 0)))
    for obj in objects:
        obj.data.flip_normals()
        obj.data.update()
    return objects


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    for name in NAMES:
        if only and name not in only:
            continue
        k.reset()
        parts = torpedo()
        if name == "blue_torpedo_l":
            mirrored(parts)
        triangulate(parts)
        bpy.context.view_layer.update()
        if "check" in options:
            sheet = os.path.join(options["check"], "enemy_V.png")
            mk.compare("%s (V %d)" % (name, SPRITES[name]), mk.coverage(parts, 24, 28), own_mask(sheet, SPRITES[name]))
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts, distance=0.7)


if __name__ == "__main__":
    build()
