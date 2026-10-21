"""The squat grey lens pod of LAVA RUN and UNDERDELI (sheet 9 sprite 41, 2x2: 24 x 28 pixels; enemies 325 and 326 of
episode 4, ground layer, each one alone; one frame) and its blue twin of EYESPY (9 43, enemy 357, top layer), polished
(2026-10-21; it replaces wave3_aj.py's pod(), lens_pod_grey() and lens_pod_blue(): a heightfield painted pixel by pixel
with three balls and a lens). models.cfg: model lens_pod_grey enemies/lens_pod_grey.glb origin; sprite 9 41
lens_pod_grey yaw=0 height=-4; model lens_pod_blue enemies/lens_pod_blue.glb (unchanged: on top, centred in height);
sprite 9 43 lens_pod_blue yaw=0 (unchanged).

9 43 is 9 41's picture in other ramps, pixel for pixel (the same mask, every shade the same): its ramp 0 (the black
parts) is ramp 6 there, ramp 6 (the armour) ramp 9, ramp 15 (the lens) ramp 6. color=sprite can't do that (it gives
every material one ramp), so the blue pod is this model with those materials: the same shapes, its lens dark glass. No
other sprite has their pixels mirrored or turned, and no other enemy shows them.

As the sprite and its 4x upscale draw it (columns 1-22 of rows 1-26; the armour ramp 6's grey-blues, the black parts
ramp 0): at the top a hood (columns 5-18 of rows 2-8) of two lobes either side of a V-shaped notch (columns 9-14 of row 3
narrowing to 11-12 at row 5), the left lobe lit (0x6a-0x6c), the right darker (0x66-0x68), and in the notch a dark knob
(columns 10-13 of rows 2-4, 0x04-0x0a); from the hood's foot a neck (columns 9-14 of rows 8-12) runs down the middle;
either side of it a black ball joint in a socket (columns 3-8 and 15-20 of rows 8-13, a glint 0x0c at the left one's
upper left); round them the yoke, the upper armour, its lower edge a bright lip in a broad V (from the shoulders,
columns 2-3 and 20-21 of rows 12-13, down to row 17 in the middle: 0x6c-0x6f); below the lip the lower body (rows 17-24),
its sides sloping down to its chamfered foot (0x63-0x69, lit to the left); and at its front, bulging out below it, a
round lens of dark crimson glass (columns 8-15 of rows 19-26: ramp 15, 0xf1-0xf5, two upright glints of orange and
gold, 0xf8-0xfd, in its upper middle) in a black socket (row 18 and columns 7 and 16).

Built as a CAD modeller would (polish_machine_kit): the lower body a smooth skirt lofted through rounded ovals from
its foot up (its sides steep, its front a rounded slope from the foot up to the lip, as the upscale paints it); the yoke
a prism of its plan (the lip's V in front) under two planes meeting in a ridge down its middle and one sloping to the
lip, its edges bevelled, the sockets cut into it, and along its front edge the lip, a rounded bead (bright: the sprite's
white V); the neck a bevelled ridge; the hood a bevelled block whose top rises from the notch to the lobes' outer edges,
the notch cut into it; the knob, the balls and the socket's cup ellipsoids; the lens an ellipsoid bulging out of the cup,
cut along smooth contours (polish_orb_red.band_split) into bands of its shine, painted for the game's camera (VIEW_TILT
degrees off straight down) so the glints sit where the sprite draws them; the grey pod's lens glows in its own colours
(0.12-0.45; the blue pod's is dark glass). Seen from straight above the pod covers the sprite's pixels.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground (z = 0); origin at the
sprite's centre (pixel 12, 14): column c's left edge is x = c - 12, row r's top edge y = 14 - r. Symmetric about x = 0.

Where it stands: the grey pod is drawn at its origin (models.cfg origin), height=-4 sets it on the terrain (as the other
polished ground models of UNDERDELI: the core machine, the mite, the floor eye); the blue one flies on the top layer,
centred in height.

Replaces wave3_aj.py (its pod(), pod_v_row(), pod_height(), AXIS_C, POD, POD_BLUE, lens_pod_grey() and lens_pod_blue():
all the file builds, so it can go) and wave3_aj_art.py's TURRET and TURRET_BLUE (only wave3_aj.py reads them; check
with grep before removing). Nothing imports wave3_aj.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes against
enemy_9.png), --preview <prefix>, --only <name,...>.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k, smoothstep  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_k_pod import triangulate, plane_box  # noqa: E402

VIEW_TILT = 20.0

# The lower body: a loft of rounded ovals (superellipses with their own depth up and down the screen) from its foot up:
# (z, half-width, y of its front edge, y of its back edge, power). Its sides stand steep, then round in; its front
# recedes as it rises, a rounded slope from the foot (row 24) up to the yoke's lip (row 17); its top (under the yoke)
# is flat.
BODY = [(0.0, 10.5, -10.55, 4.45, 3.1), (1.3, 10.6, -10.5, 4.55, 3.1), (2.5, 10.55, -10.25, 4.55, 3.2),
        (3.5, 10.35, -9.55, 4.55, 3.3), (4.4, 9.95, -8.4, 4.5, 3.4), (5.25, 9.4, -7.0, 4.45, 3.6),
        (6.0, 8.6, -5.45, 4.3, 3.8), (6.6, 7.5, -4.1, 4.1, 4.0), (7.0, 6.2, -3.25, 3.8, 4.0)]

# The yoke: its lip (the V of the sprite's bright pixels, from the left shoulder down to the middle and up to the right)
# and its back edge; its ridge's height (at RIDGE_Y) and its slopes to the sides and to the lip; its bottom.
LIP = [(-10.6, 1.8), (-8.5, 0.5), (-6.6, -1.4), (-5.0, -2.75), (-3.4, -3.55), (3.4, -3.55), (5.0, -2.75), (6.6, -1.4),
       (8.5, 0.5), (10.6, 1.8)]
YOKE_BACK = [(10.6, 3.6), (9.4, 4.6), (-9.4, 4.6), (-10.6, 3.6)]
RIDGE_Z, RIDGE_Y, RIDGE_SLOPE, YOKE_FRONT_SLOPE = 9.6, 1.0, 0.17, 0.25
YOKE_BOTTOM = 2.2
YOKE_BEVEL = 0.6
# The lip's bead: a rounded rod along the yoke's front edge (the sprite's bright V): how far under the yoke's top
# edge its middle lies, its radius.
BEAD_DOWN, BEAD_R = 0.42, 0.72

# The neck down the middle (columns 9-14 of rows 8-12): half-width, its ends (y), its top at the hood and its fall.
NECK = (2.75, 0.3, 6.6, 10.4, 0.1)
# The hood (columns 5-18 of rows 2-8): its plan, its top; the notch (apex, its half-width at the back, its floor).
HOOD_PLAN = [(-4.2, 5.2), (4.2, 5.2), (6.6, 7.0), (6.6, 11.2), (5.6, 12.3), (-5.6, 12.3), (-6.6, 11.2), (-6.6, 7.0)]
HOOD_TOP = 10.6                     # its top at the notch; it rises to the lobes' outer edges by HOOD_RISE
HOOD_RISE = 0.9
NOTCH = ((0.0, 8.5), 3.3, 9.0)
# The knob in the notch (columns 10-13 of rows 2-4): middle, radii.
KNOB = ((0.0, 10.9, 10.0), (2.05, 1.85, 1.65))
# The balls (columns 3-8 and 15-20 of rows 8-13): middles (x mirrored), radius; their sockets' radius.
BALL = ((5.9, 3.15, 7.55), 2.75)
SOCKET_R = 3.05

# The lens (columns 8-15 of rows 19-26) and the black cup it sits in: middle, radii; the cup's middle and radii.
LENS = ((0.0, -9.0, 3.15), (4.15, 4.05, 3.2))
CUP = ((0.0, -8.4, 3.0), (4.85, 4.45, 3.0))
# Its shine in the camera's view (offsets from its middle as the sprite draws them, pixels): brighter towards the top;
# two upright glints (x, half-width, the span of y they cover, strength).
GLINTS = [(-1.45, 0.62, (-2.2, 1.6), 0.62), (1.55, 0.6, (-1.9, 1.2), 0.5)]
# The lens' bands: (lowest shine, palette index, glow); the blue pod's in ramp 6, no glow.
LENS_BANDS = [(-9.0, 0xf1, 0.12), (0.2, 0xf2, 0.16), (0.34, 0xf3, 0.2), (0.5, 0xf5, 0.26), (0.66, 0xf8, 0.34),
              (0.8, 0xfb, 0.42)]

# The two looks: (model, sprite, ramp of the armour, of the black parts, of the lens, the lens glows).
LOOKS = [("lens_pod_grey", 41, 0x6, 0x0, 0xf, True), ("lens_pod_blue", 43, 0x9, 0x6, 0x6, False)]


def materials(armour, black, lens_ramp, glows):
    pal = k.level_palette()

    def mat(name, index, metallic=0.3, roughness=0.34):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)
    a, b = armour << 4, black << 4
    m = {
        "lit": mat("lpod_lit", a | 0xc),
        "plate": mat("lpod_plate", a | 0xb),
        "wall": mat("lpod_wall", a | 0x8, 0.3, 0.38),
        "lip": mat("lpod_lip", a | 0xe, 0.3, 0.26),
        "dark": mat("lpod_dark", a | 0x4, 0.3, 0.42),
        "ball": mat("lpod_ball", b | 0x3, 0.6, 0.18),
        "knob": mat("lpod_knob", b | 0x6, 0.55, 0.3),
        "black": mat("lpod_black", b | 0x1, 0.4, 0.5),
    }
    bands = []
    for lowest, index, strength in LENS_BANDS:
        index = (lens_ramp << 4) | (index & 15)
        if glows:
            bands.append((lowest, k.material(f"lpod_lens_{index:x}", palette=index, metallic=0.1, roughness=0.1,
                                             emission=pal[index], emission_strength=strength)))
        else:
            bands.append((lowest, k.material(f"lpod_lens_{index:x}", palette=index, metallic=0.2, roughness=0.12)))
    m["lens"] = bands
    return m


# --- The parts ------------------------------------------------------------------------------------------------------

def oval(z, hw, yf, yb, power, segments=96):
    """A superellipse at height z: half-width hw, from yf (its front, down the screen) to yb (its back)."""
    cy, h = (yf + yb) / 2, (yb - yf) / 2
    return [Vector((hw * u, cy + h * v, z)) for u, v in
            (mk.superellipse_point(2 * math.pi * j / segments, power) for j in range(segments))]


def body(m):
    rings = [oval(*row) for row in BODY]
    last = BODY[-1]
    obj = k.loft("body", rings, m["plate"], start_point=(0.0, (BODY[0][2] + BODY[0][3]) / 2, 0.0),
                 end_point=(0.0, (last[2] + last[3]) / 2, last[0]))
    k.smooth(obj, 60)

    def pick(c, n):
        if c.z < 1.3:
            return m["dark"]          # the foot (the sprite's dark lowest row)
        if n.z < 0.45:
            return m["wall"]          # the steep sides and the front's lower part (0x63-0x68)
        return None
    mk.paint(obj, pick)
    return obj


def yoke_top(x, y):
    return min(RIDGE_Z - RIDGE_SLOPE * abs(x), RIDGE_Z + YOKE_FRONT_SLOPE * (y - RIDGE_Y))


def yoke(m):
    plan = list(reversed(LIP)) + YOKE_BACK[::-1]
    obj = mk.prism("yoke", plan, YOKE_BOTTOM, 14.0, m["plate"])
    for i, top in enumerate((lambda x, y: RIDGE_Z + RIDGE_SLOPE * x, lambda x, y: RIDGE_Z - RIDGE_SLOPE * x,
                             lambda x, y: RIDGE_Z + YOKE_FRONT_SLOPE * (y - RIDGE_Y))):
        mk.boolean(obj, plane_box(f"yoke_plane{i}", top), "INTERSECT")
    mk.cleanup(obj)
    mk.bevel(obj, YOKE_BEVEL, 3, 30)
    (bx, by, bz), _ = BALL
    for i, sx in enumerate((-1, 1)):
        mk.boolean(obj, mk.ball(f"socket{i}", (sx * bx, by, bz), (SOCKET_R, SOCKET_R, SOCKET_R), m["black"], 32, 16),
                   "DIFFERENCE")
    mk.cleanup(obj)
    mk.shade(obj, 35)

    def pick(c, n):
        (bx_, by_, bz_), _ = BALL
        if min(math.dist((c.x, c.y, c.z), (sx * bx_, by_, bz_)) for sx in (-1, 1)) < SOCKET_R + 0.05:
            return m["black"]                       # the sockets' insides
        if n.z < 0.35:
            return m["wall"]
        # The lip: the rounded front edge, facing the camera (down the screen and up).
        if n.y < -0.25 and n.z > 0.35:
            return m["lip"]
        if c.x < 0.0:
            return m["lit"]                         # the left plane (lit, as the sprite's), up to the ridge
        return None
    mk.paint(obj, pick)
    return obj


def bead(m):
    """The lip: a rounded rod along the yoke's front edge, bright where it catches the light."""
    pts = []
    for (x0, y0), (x1, y1) in zip(LIP[:-1], LIP[1:]):
        steps = max(1, int(math.hypot(x1 - x0, y1 - y0) / 1.0))
        for i in range(steps):
            x, y = x0 + (x1 - x0) * i / steps, y0 + (y1 - y0) * i / steps
            pts.append((x, y, yoke_top(x, y) - BEAD_DOWN))
    pts.append((LIP[-1][0], LIP[-1][1], yoke_top(*LIP[-1]) - BEAD_DOWN))
    pts = [(x, y, z, BEAD_R) for x, y, z in mk.chaikin(pts, 1, closed=False)]
    obj = mk.smooth_tube("bead", pts, m["lip"], 10, 0)
    return k.smooth(obj, 60)


def neck(m):
    hw, y0, y1, z1, fall = NECK
    plan = [(-hw, y0), (hw, y0), (hw, y1), (-hw, y1)]
    obj = mk.wedge("neck", plan, YOKE_BOTTOM + 1.0, lambda x, y: z1 - fall * (y1 - y), m["lit"])
    mk.bevel(obj, 0.9, 3, 30)
    mk.shade(obj, 35)
    mk.paint(obj, lambda c, n: m["wall"] if n.z < 0.35 else (m["plate"] if n.x > 0.3 else None))
    return obj


def hood(m):
    obj = mk.prism("hood", HOOD_PLAN, YOKE_BOTTOM + 1.0, HOOD_TOP + HOOD_RISE + 1.0, m["plate"])
    # its top: two planes rising from the notch to the lobes' outer edges
    for i, sx in enumerate((-1, 1)):
        mk.boolean(obj, plane_box(f"hood_plane{i}", lambda x, y, sx=sx: HOOD_TOP + HOOD_RISE * sx * x / 6.6),
                   "INTERSECT")
    mk.cleanup(obj)
    mk.bevel(obj, 1.0, 4, 25)
    (ax, ay), half, floor = NOTCH
    cutter = mk.prism("notch", [(ax, ay), (ax + half, ay + 4.6), (ax - half, ay + 4.6)], floor, HOOD_TOP + 3.0,
                      m["black"])
    mk.boolean(obj, cutter, "DIFFERENCE")
    mk.cleanup(obj)
    mk.shade(obj, 35)

    def pick(c, n):
        if c.z < HOOD_TOP - 0.5 and abs(c.x - ax) < half + 0.2 and c.y > ay - 0.2 and n.z < 0.9:
            return m["black"]                       # the notch's walls (the sprite's black V)
        if n.z < 0.35:
            return m["wall"]
        if c.x < 0.0:
            return m["lit"]                         # the left lobe, up to the saddle's middle
        return None
    mk.paint(obj, pick)
    return obj


def knob(m):
    centre, radii = KNOB
    return mk.ball("knob", centre, radii, m["knob"], 28, 14)


def balls(m):
    (bx, by, bz), r = BALL
    return [mk.ball(f"ball{i}", (sx * bx, by, bz), (r, r, r), m["ball"], 28, 14) for i, sx in enumerate((-1, 1))]


def cup(m):
    centre, radii = CUP
    return mk.ball("cup", centre, radii, m["black"], 32, 16)


def lens(m):
    (cx, cy, cz), radii = LENS
    obj = k.ellipsoid("lens", (cx, cy, cz), radii, None, 40, 20)
    t = math.radians(VIEW_TILT)

    def shine(p):
        # where the camera sees the point, as the sprite draws it: across, and up its picture from the lens' middle
        u = p.x - cx
        v = ((p.y - cy) * math.cos(t) + (p.z - cz) * math.sin(t)) / math.cos(t)
        facing = (p.z - cz) / radii[2]
        s = 0.42 + 0.1 * v / radii[1] - 0.22 * (u / radii[0]) ** 2
        s -= 0.3 * (1.0 - smoothstep(-0.4, 0.55, facing))     # darker where it turns away (its rim, its foot)
        for gx, gw, (g0, g1), strength in GLINTS:
            across = math.exp(-((u - gx) / gw) ** 2)
            along = smoothstep(g0 - 0.6, g0 + 0.4, v) * (1.0 - smoothstep(g1 - 0.4, g1 + 0.6, v))
            s += strength * across * along
        return s
    band_split(obj, [shine(v.co) for v in obj.data.vertices], m["lens"])
    k.recalc_normals(obj)
    return k.smooth(obj, 80)


def build_pod(look):
    name, sprite, armour, black, lens_ramp, glows = look
    k.reset()
    m = materials(armour, black, lens_ramp, glows)
    parts = [body(m), yoke(m), bead(m), neck(m), hood(m), knob(m)] + balls(m) + [cup(m), lens(m)]
    parts = triangulate(parts)
    if "stats" in k.args():
        for obj in parts:
            print("   %-10s %6d triangles" % (obj.name, len(obj.data.polygons)))
    return parts


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    for look in LOOKS:
        name, sprite = look[0], look[1]
        if only and name not in only:
            continue
        parts = build_pod(look)
        bpy.context.view_layer.update()
        if "check" in options:
            sheet = os.path.join(options["check"], "enemy_9.png")
            mk.compare("%s (9 %d)" % (name, sprite), mk.coverage(parts, 24, 28), k.sprite_mask(sheet, sprite))
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts, distance=0.6)


if __name__ == "__main__":
    build()
