"""BOTANY's eye pod (sheet 0 sprite 125, 2x2: a 17 x 13 creature in the 24 x 28 cell; enemy 819, on the ground of
BOTANY A and B, about 35 of them; its animation, which plays when it fires: 125 127 127 131 131 131 127 127 127 125),
polished (2026-10-19; it replaces wave3_ai.py's botany_eye_pod(), domed plates painted from the sprite). models.cfg:
sprite 0 125 botany_eye_pod yaw=0 glow=10:0.35:118 (unchanged), frame 0 127 botany_eye_pod_127, frame 0 131
botany_eye_pod_131. No other enemy shows these three sprites; they are no other sprites' pixels mirrored or in
other ramps.

As the sprite and its 4x upscales draw it (columns and rows of the cell): a steel-blue armoured pod (ramp 3) lit from
the upper left, symmetric about column 12. In its middle a red eye (columns 11-13 of rows 11-14) in a dark socket
(the ring of 32-33 round it, columns 10-14 of rows 9-15); over the socket two rounded plates (columns 8-11 and 13-16
of rows 7-10, their tops the sprite's lightest steel) parted by a notch at the top (column 12 of rows 6-7); under it
two small plates (columns 9-11 and 13-15 of rows 15-16, a notch between them at row 17). Down either side, apart
from the shell by a dark gap, a folded leg (columns 4-7 of rows 8-18): three segments, lit at the top and darker
below, touching the shell at rows 11 and 13, ending in a small foot turned in under the pod (column 7 of row 17).
The frames light the eye: 127 the same eye two shades hotter; 131 opens it, the red spreading over the socket
(columns 10-14 of rows 10-15) with a yellow-hot middle (7c).

Built as a small armoured creature crouching on the ground: a dark floor under it all (the gaps the sprite draws in
its outline's black); the shell one solid over its plan (polish_ring_machine.relief()) whose top is the plates, domes
joined smoothly with creases between them, falling into the socket, a dark bowl; in it the eye, a glossy ball glowing
in the sprite's reds painted in bands from its middle out (polish_balls.painted_ball), and its lids, a dark roll round
the eye's opening; down each side a folded leg, a tube pinched at its three joints and tapering into the foot's claw.
The steel is painted in the sprite's shades by how far it faces the camera, cut into bands along smooth contours. One
model per frame: the same pod, the eye's colours and glow changed and in 131 the lids drawn back round its widest
(the socket a little deeper); all span the same bounds, so the game, which centres them in height on their layer,
keeps them in place. The eye glows in its own colours; models.cfg's glow (red, 118) lights round it.

The pod is built about u = 0 and moved to the sprite's column 12 (x 0.5). Origin at the sprite's centre (pixel 12,
14); +Y up the screen, +Z towards the camera, the pod standing on z = 0.

Replaces wave3_ai.py's botany_eye_pod() (its @kit.model("botany_eye_pod", ...) function, EYE_POD, EYE_POD_PAINT and
AX_POD, the botany_eye_pod lines of its docstring; steel() and shade_by_slope() stayed for botany_beetle(), which polish_botany_beetle.py replaced with the rest
of wave3_ai.py) and
wave3_ai_art.py's EYE_POD and EYE_POD_131 (nothing else reads them): remove them so that they don't overwrite these
models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each frame's silhouette
against its sprite in enemy_0.png), --preview <prefix>, --only <name,...>.
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
from polish_balls import Ellipsoid, painted_ball  # noqa: E402
from polish_ring_machine import Region, ccw, relief, round_edge  # noqa: E402
from polish_sphere_nozzle import smoothstep  # noqa: E402

AXIS_X = 0.5

# The shell's plan, its left half (u, y) from the notch at the top round to the notch at the bottom (the sprite's
# outline half included); mirrored for the right half.
OUTLINE = [(0.0, 6.75), (-0.6, 7.45), (-1.6, 7.85), (-2.8, 7.85), (-3.7, 7.3), (-4.3, 6.4), (-4.6, 5.0), (-4.7, 3.0),
           (-4.7, 1.0), (-4.65, -0.8), (-4.4, -2.2), (-3.8, -3.2), (-2.8, -3.65), (-1.6, -3.7), (-0.6, -3.45),
           (0.0, -2.9)]
# The shell's plates, domes over the plan joined smoothly (the left ones; mirrored): (middle u, y, half-sizes,
# height, power of their plan: higher is squarer).
PLATES = [(-2.05, 5.1, 2.85, 2.75, 4.95, 2.3),   # the upper plates over the eye, parted by the notch
          (-3.45, 0.9, 1.5, 3.1, 3.3, 2.3),      # the shell's sides beside the socket
          (-1.9, -2.1, 1.95, 1.7, 3.15, 2.3)]    # the small plates under the eye
FLOOR = 1.4            # the shell's least height inside its plan
BLEND = 0.8            # how softly the plates meet (a smooth maximum; the creases between them)
DOME_POWER = 2.6       # the plates' profile: their height falls as 1 - q ** DOME_POWER from their middle (q 0) out
EDGE = 1.2             # the shell's top rounds down to its outline over this
# The socket: an oval round the eye's middle (SOCKET_AT; SOCKET radii) in which the shell falls from RIM_Z at its
# edge to a bowl round the eye (its floor per frame), dark; the plates meet it smoothly (SOCKET_BLEND). In it the
# lids, a dark roll round the eye's opening resting on the eye (per frame: the opening, the roll's radius, height).
SOCKET_AT, SOCKET, RIM_Z, SOCKET_BLEND = (0.0, 1.0), (3.15, 3.55), 3.75, 0.5
# The steel's shades by how far a surface faces the camera (its normal's z): borders and palette indices.
STEEL = ((0.25, 0.5, 0.72, 0.9), (0x37, 0x3a, 0x3c, 0x3d, 0x3e))
BASE = ((0.0, 0.9, 0.55), (6.9, 5.4, 0.55))   # the dark floor under it all, seen in the gaps: middle, radii
# The eye: middle and radii (mostly sunk in the socket).
EYE = (Vector((0.0, 1.0, 0.95)), Vector((2.3, 2.75, 2.45)))
EYE_BANDS = (0.55, 0.78, 0.92)   # the eye's colours change where its normal's z crosses these
# The leg (left): its path (u, y, z) from the hip under the upper plate down to the claw's tip, the joints along it
# (fractions of the path), its radii there.
LEG = [(-5.85, 5.3, 2.05), (-6.45, 3.4, 1.95), (-6.75, 1.5, 1.8), (-6.7, -0.2, 1.65), (-6.4, -1.5, 1.5),
       (-5.7, -2.65, 1.25), (-5.05, -3.5, 0.95), (-4.5, -4.15, 0.55)]
LEG_JOINTS = (0.36, 0.62, 0.8)
LEG_RADIUS = 1.3

# The frames: (model, sprite, the lids: (the eye's opening (half-width, half-height), the roll's radius, its height),
# the socket's floor, the eye's bands from its middle out: (palette index, emission)).
LIDS_SHUT = ((1.5, 2.0), 0.72, 2.85)
LIDS_OPEN = ((2.3, 2.75), 0.4, 1.2)
FRAMES = [
    ("botany_eye_pod", 125, LIDS_SHUT, 2.1, [(0x75, 1.2), (0x73, 0.9), (0x72, 0.7), (0x70, 0.5)]),
    ("botany_eye_pod_127", 127, LIDS_SHUT, 2.1, [(0x7a, 1.8), (0x77, 1.4), (0x74, 1.0), (0x72, 0.7)]),
    ("botany_eye_pod_131", 131, LIDS_OPEN, 0.8, [(0x7c, 2.4), (0x79, 1.9), (0x76, 1.4), (0x73, 1.0)]),
]


def smax(a, b, r):
    """A smooth maximum (rounded by r where a and b meet)."""
    h = min(1.0, max(0.0, 0.5 + 0.5 * (a - b) / r))
    return b + (a - b) * h + r * h * (1 - h)


def plates_z(u, y):
    z = FLOOR
    for cu, cy, ru, ry, h, p in PLATES:
        for side in (1.0, -1.0):
            q = (abs((u - side * cu) / ru) ** p + abs((y - cy) / ry) ** p) ** (1.0 / p)
            if q < 1.0:  # a dome rounded on top, meeting the floor at a slant (no vertical edge)
                z = smax(z, h * (1.0 - q ** DOME_POWER), BLEND)
    return z


def socket_s(u, y):
    return math.hypot((u - SOCKET_AT[0]) / SOCKET[0], (y - SOCKET_AT[1]) / SOCKET[1])


def smin(a, b, r):
    return -smax(-a, -b, r)


def shell_z(u, y, floor):
    z = plates_z(u, y)
    s = socket_s(u, y)
    if s < 1.3:
        dip = floor + (RIM_Z - floor) * smoothstep(0.62, 1.0, s) + 3.0 * max(0.0, s - 1.0)
        z = smin(z, dip, SOCKET_BLEND)
    return z


def materials(eye):
    m = {"base": k.material("eyepod_base", palette=0x31, metallic=0.2, roughness=0.6),
         "lid": k.material("eyepod_lid", palette=0x33, metallic=0.25, roughness=0.3),
         "lid_edge": k.material("eyepod_lid_edge", palette=0x36, metallic=0.3, roughness=0.25)}
    for index in STEEL[1]:
        m[index] = k.material(f"eyepod_steel_{index:x}", palette=index, metallic=0.15,
                              roughness=0.42 if index < 0x38 else 0.3 if index < 0x3c else 0.22)
    pal = k.level_palette()
    for i, (index, glow) in enumerate(eye):
        m[("eye", i)] = k.material(f"eyepod_eye_{index:x}", palette=index, metallic=0.0, roughness=0.1,
                                   emission=pal[index], emission_strength=glow)
    return m


def steel_key(nz):
    return STEEL[1][sum(nz > b for b in STEEL[0])]


def shell(m, floor):
    """The shell over its plan: the plates, the socket's bowl (dark, one colour, so no bands cut its steep sides),
    the steel painted in bands of how far it faces the camera."""
    right = [(-u, y) for u, y in reversed(OUTLINE[1:-1])]
    poly = ccw(mk.chaikin(OUTLINE + right, 2))

    region = Region([poly])

    def top(x, y, d):
        return max(0.25, shell_z(x, y, floor) * round_edge(d, EDGE))

    def nz(x, y, d=9.0):
        """How far the top faces the camera at (x, y): its normal's z, from the top's slopes."""
        if socket_s(x, y) < 0.98:
            return -1.0
        e = 0.08
        pts = [(x + e, y), (x - e, y), (x, y + e), (x, y - e)]
        z = [top(px, py, float(region.distance([(px, py)])[0]) if region.inside([(px, py)])[0] else 0.0)
             for px, py in pts]
        return Vector((-(z[0] - z[1]) / (2 * e), -(z[2] - z[3]) / (2 * e), 1.0)).normalized().z

    def paint(x, y, d):
        if socket_s(x, y) < 1.0:
            return "lid"
        return steel_key(nz(x, y, d))

    borders = [(lambda x, y, d: socket_s(x, y), 1.0)] + [(lambda x, y, d: nz(x, y, d), b) for b in STEEL[0]]
    keys = dict(m)
    keys.update({"side": m[STEEL[1][0]]})
    return relief("shell", [poly], top, keys, paint=paint, side="side", bottom=0.0, spacing=0.4, borders=borders,
                  smooth_angle=80.0)


def eye(m, lids):
    centre, radii = EYE
    bands = [(lambda p, n: n.z, EYE_BANDS, [("eye", 3), ("eye", 2), ("eye", 1), ("eye", 0)])]
    obj = painted_ball("eye", Ellipsoid(centre, radii), bands, m, subdivisions=3, smooth_angle=70)
    for v in obj.data.vertices:  # its hidden underside flattened above the ground
        v.co.z = max(v.co.z, 0.05)
    # The lids: a roll round the opening, its inner edge on the eye, its outer side sinking into the socket.
    (a, b), radius, height = lids
    segments, around = 40, 10
    verts, faces = [], []
    for i in range(segments):
        t = 2 * math.pi * i / segments
        c, s = math.cos(t), math.sin(t)
        out = Vector((c * b, s * a, 0.0)).normalized()     # the oval's outward normal in plan
        mid = Vector((centre.x + a * c, centre.y + b * s, height)) + out * radius
        for j in range(around):
            w = 2 * math.pi * j / around
            verts.append(mid + out * (radius * math.cos(w)) + Vector((0.0, 0.0, 0.85 * radius * math.sin(w))))
    for i in range(segments):
        for j in range(around):
            i1, j1 = (i + 1) % segments, (j + 1) % around
            faces.append((i * around + j, i1 * around + j, i1 * around + j1, i * around + j1))
    lid = k.mesh_object("lids", verts, faces, m["lid"])
    k.recalc_normals(lid)
    k.smooth(lid, 70)
    mk.paint(lid, lambda c, n: m["lid_edge"] if n.z > 0.55 else None)


def leg(m, side):
    """A folded leg down the pod's side: a tube through LEG pinched at its joints, its three segments swelling
    between them, tapering into the claw."""
    pts = [Vector((u * side, y, z)) for u, y, z in LEG]
    path = [Vector(p) for p in mk.chaikin([tuple(p) for p in pts], 2, closed=False)]
    n = len(path)
    radii = []
    for j in range(n):
        t = j / (n - 1)
        pinch = max(math.exp(-((t - jt) / 0.045) ** 2) for jt in LEG_JOINTS)
        taper = 1.0 - smoothstep(0.8, 1.0, t) * 0.88
        radii.append(LEG_RADIUS * taper * (1.0 - 0.3 * pinch) * (0.85 + 0.15 * smoothstep(0.0, 0.08, t)))
    obj = mk.tube("leg_" + ("r" if side < 0 else "l"), path, LEG_RADIUS, m[STEEL[1][3]], 10, radii=radii)
    for v in obj.data.vertices:  # resting on the ground
        v.co.z = max(v.co.z, 0.0)
    k.smooth(obj, 60)
    joints = [path[int(round(jt * (n - 1)))] for jt in LEG_JOINTS]

    def pick(c, nrm):
        if min((c - j).length for j in joints) < 0.42:
            return m["lid_edge"] if nrm.z > 0.3 else m["lid"]  # the joints dark
        return m[steel_key(nrm.z)]
    mk.paint(obj, pick)
    return obj


def build_model(lids, floor, eye_bands):
    k.reset()
    m = materials(eye_bands)
    (bx, by, bz), radii = BASE
    mk.ball("base", (bx, by, bz), radii, m["base"], 32, 10)
    shell(m, floor)
    eye(m, lids)
    for side in (-1.0, 1.0):
        leg(m, side)
    for obj in mk.meshes():
        obj.data.transform(Matrix.Translation((AXIS_X, 0.0, 0.0)))
    return mk.meshes()


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    for name, sprite, lids, floor, eye_bands in FRAMES:
        if only is not None and name not in only:
            continue
        parts = build_model(lids, floor, eye_bands)
        if "check" in options:
            mk.compare("%s (0 %d)" % (name, sprite), mk.coverage(parts, 24, 28),
                       k.sprite_mask(os.path.join(options["check"], "enemy_0.png"), sprite))
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        bpy.context.view_layer.update()
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts)


if __name__ == "__main__":
    build()
