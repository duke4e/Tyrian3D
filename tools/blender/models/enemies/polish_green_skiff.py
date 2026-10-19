"""The green skiff of TORM and BOTANY A, drawn from two sprites of sheet J side by side (2x2 each, not animated;
custom ground2 enemies): coming in from the left, its stern 169 at x and its bow 207 at x + 24 (TORM's events
430-510 and 1810, from x -48), and its mirror image coming in from the right, its bow 245 at x and its stern 283 at
x + 24 (TORM's 500-580 and 1830, BOTANY A's 1300-1550, from x 300). The mirror image is the other's pixels mirrored
about the middle of the picture's column 24 (column c of the one is column 48 - c of the other), so its model is
the whole skiff mirrored about x = 0.5, cut again. Polished (2026-10-19; it replaces wave3_m.py's skiff_whole(), the
old tower's pod and plate stuck together). models.cfg: model green_skiff_rear / green_skiff_nose / green_skiff_l_nose
/ green_skiff_l_rear ... origin; sprite j 169 green_skiff_rear yaw=0, sprite j 207 green_skiff_nose yaw=0, sprite j
245 green_skiff_l_nose yaw=0, sprite j 283 green_skiff_l_rear yaw=0.

The sprite's artist made it of the green tower's parts (J 13 15 / 51 53, polish_green_tower.py), and so is the model:
its stern is the left end of the tower's pod, the same shape, colours, rib, lamp and claw (columns 2-21 of the 48 x 28
picture, as in the tower's picture: the dark green cap with its light rib (column 5) and its red lamp on the back
(columns 5-7 of rows 6-7), the pale segment (columns 10-19 of rows 5-14), the red claw with its glowing slit hooking
down under the cap (columns 4-11 of rows 16-23)); a ribbed collar joins it to the bow (the light rings of columns 23,
25 and 27, rows 8-13); the bow is a hull with the tower plate's top, tapering to a round nose (column 46): light green,
a pair of ribs across it (columns 34 and 36-37 of rows 9-15), a raised hatch by its front edge (columns 28-30 of rows
14-17), a light rim round the nose (columns 44-45); its front, down the screen, a dark apron with two light slats along
it (rows 19-23 from column 17: the tower neck's grille); under the stern the tower neck's prong as a strut leaning
down to the ground (columns 13-16 of rows 19-26) and one of its red lamps under the apron's end (columns 18-22 of rows
24-26). It hovers: the hull's underside 1.6 pixels up, the strut and the claw's tip reaching down to the ground.

Built whole (the pod, the claw and the lamp by polish_green_tower.py's own pod() and claw(), moved here, the right
half of the pod cut away; the hull a solid over its plan, polish_ring_machine.relief()), and cut along the sprites'
edge (x = 0) into the two pieces (polish_arch.py's cut(): they keep the whole's shading across the cut), each moved
so that its sprite's centre is its origin; the mirror image likewise, from the whole mirrored about x = 0.5.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground (z = 0); the
whole's x = 0 is the edge between the sprites, y = 0 the picture's middle: a point (column, row) of the picture's
pixel grid is (c - 24, 14 - r) (px()).

Replaces wave3_m.py's skiff: remove the skiff's and the pod and plate's sections (X(), pod_radius(), pod(),
plate_outline(), plate(), plate_details(), bow_y(), bow_radius(), bow_hull(), skiff_whole(), the whole("skiff", ...)
and whole("skiff_l", ...) registrations, skiff_piece() and the four model("green_skiff_...") lines: only the skiff used
them; greens() stays, the green pod ship uses it), the skiff lines of its docstring and its --whole usage, and the
imports only they used (from mathutils import Matrix, Vector; px, py and whole from wave3_m_kit).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the
wholes and of each piece against enemy_J.png), --preview <prefix> (the wholes' and each piece's views), --only
<name,...>.
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
import polish_green_tower as tower  # noqa: E402
from polish_arch import cut  # noqa: E402
from polish_ring_machine import ccw, relief, round_edge  # noqa: E402
from polish_jets import Curve  # noqa: E402

PIECES = [("green_skiff_rear", 169, (-24.0, 0.0, -14.0, 14.0), False),
          ("green_skiff_nose", 207, (0.0, 24.0, -14.0, 14.0), False),
          ("green_skiff_l_nose", 245, (-24.0, 0.0, -14.0, 14.0), True),
          ("green_skiff_l_rear", 283, (0.0, 24.0, -14.0, 14.0), True)]
MIRROR_X = 0.5            # the mirror image's pixels mirror the other's about the middle of column 24


def px(c, r):
    return (c - 24.0, 14.0 - r)


# The stern: the tower's pod moved from its place in the tower (its axis at tower.POD_Y, tower.POD_Z, about the
# tower's x = 0) to the skiff's (its cap's end at the picture's column 2, its axis at row 12.4, 8 pixels up), its
# right part (beyond POD_CUT) cut away inside the collar.
POD_AXIS_Y, POD_AXIS_Z = 2.2, 8.0
POD_SHIFT = Vector((0.5, POD_AXIS_Y - tower.POD_Y, POD_AXIS_Z - tower.POD_Z))
POD_SCALE = 1.07          # the skiff's pod is a little fuller than the tower's (rows 5-19)
POD_CUT = -1.2
# The claw under the cap: the tower's claw (x, y, depth below the pod's axis, half-width, half-height), shortened to
# the skiff's (rows 16-23): y as in the tower (its pod's axis at tower.POD_Y).
CLAW = [(-19.0, tower.POD_Y - 3.3, 3.0, 1.75, 1.3), (-19.3, tower.POD_Y - 5.7, 4.9, 1.9, 1.35),
        (-18.6, tower.POD_Y - 7.9, 6.3, 1.75, 1.25), (-16.8, tower.POD_Y - 9.6, 7.15, 1.4, 1.05),
        (-14.7, tower.POD_Y - 10.6, 7.5, 0.9, 0.7), (-12.9, tower.POD_Y - 10.9, 7.6, 0.18, 0.18)]
# The collar joining the stern to the bow: lathed along x (from, to, radius in y; squashed as the pod), its light
# rings (x).
COLLAR = (-3.4, 4.4, 6.75)
COLLAR_RINGS = (-0.6, 1.45, 3.4)
# The bow: its plan's back edge and the apron's front edge along x, the deck's front edge (y), the nose's tip.
BACK = Curve([(-15.6, 8.2), (1.5, 8.6), (6.5, 7.65), (11.5, 6.65), (15.5, 5.65), (19.5, 4.6), (21.4, 3.55),
              (22.2, 2.2)])
FRONT = Curve([(-15.6, -5.0), (-14.0, -6.9), (-12.4, -8.9), (-10.8, -10.6), (2.5, -10.7), (7.5, -9.75), (12.5, -8.75),
               (16.5, -7.7), (19.5, -6.65), (21.4, -5.55), (22.2, -4.1)])
DECK_FRONT = -4.6
BOW_X0, NOSE = -15.6, 22.65
# Heights: the deck's edge and its crown along x; the apron's foot; the hull's underside.
DECK = Curve([(-15.6, 9.6, 10.6), (2.0, 9.6, 10.6), (10.0, 8.5, 9.4), (17.0, 7.1, 7.9), (22.65, 5.6, 6.2)])
APRON_FOOT, UNDERSIDE, DECK_RIM = 2.3, 1.6, 0.85
SLATS = [(-6.5, -7.2, 16.2), (-8.55, -7.2, 8.6)]   # the apron's slats: y, from x, to x
RIBS = [(10.55, 0.5), (12.85, 0.55)]               # the ribs across the deck: x, half-width
RIB_Y = (5.4, -2.2)
HATCH = (4.15, 6.95, -4.0, -0.25)                  # x from, to, y from, to
STRUT = [(-9.0, -4.3, 9.2), (-9.0, -7.0, 6.2), (-9.0, -9.9, 3.1), (-9.0, -12.2, 0.6)]
STRUT_W = [1.45, 1.5, 1.45, 1.3]
LAMP = (-3.8, -11.25, 1.3)                         # the red lamp under the apron's end


def materials():
    m = tower.materials()
    m["rim"] = m["light"]
    m["deck"] = k.material("skiff_deck", palette=0x2a, metallic=0.35, roughness=0.38)
    return m


# --- The stern -----------------------------------------------------------------------------------------------------

def stern(m):
    """The tower's pod and its left claw, moved to the skiff's place; the right half of the pod (its cap, rib and
    lamp) dropped, the body cut at POD_CUT."""
    before = set(bpy.context.scene.objects)
    body = tower.pod(m)
    saved = tower.CLAW
    tower.CLAW = CLAW
    try:
        tower.claw(m, -1)
    finally:
        tower.CLAW = saved
    made = [o for o in bpy.context.scene.objects if o not in before]
    fuller = (Matrix.Translation((0, tower.POD_Y, tower.POD_Z)) @ Matrix.Diagonal((1.0, POD_SCALE, POD_SCALE, 1.0)) @
              Matrix.Translation((0, -tower.POD_Y, -tower.POD_Z)))
    for obj in made:
        mk.apply(obj)
        if not obj.name.startswith(("claw", "slit")):
            obj.data.transform(fuller)
        obj.data.transform(Matrix.Translation(POD_SHIFT))
    keep = []
    for obj in made:
        xs = [v.co.x for v in obj.data.vertices]
        if obj is not body and min(xs) > 0.0:
            bpy.data.objects.remove(obj)
            continue
        keep.append(obj)
    bm = bmesh.new()
    bm.from_mesh(body.data)
    result = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5,
                                    plane_co=(POD_CUT, 0, 0), plane_no=(1, 0, 0), clear_outer=True)
    edges = [e for e in result["geom_cut"] if isinstance(e, bmesh.types.BMEdge) and e.is_valid]
    bmesh.ops.holes_fill(bm, edges=[e for e in edges if len(e.link_faces) == 1], sides=0)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(body.data)
    bm.free()
    k.smooth(body, 60)
    return keep


def collar(m):
    """The ribbed collar where the stern meets the bow."""
    x0, x1, r = COLLAR
    sq = tower.POD_SQUASH
    rings = []
    for i in range(25):
        x = x0 + (x1 - x0) * i / 24
        rr = r * (1 - 0.05 * max(0.0, abs(x - (x0 + x1) / 2) / ((x1 - x0) / 2)) ** 6)
        rings.append([Vector((x, POD_AXIS_Y + rr * math.cos(2 * math.pi * j / 40),
                              POD_AXIS_Z + rr * sq * math.sin(2 * math.pi * j / 40))) for j in range(40)])
    body = k.loft("collar", rings, m["green"], start_point=(x0, POD_AXIS_Y, POD_AXIS_Z), end_point=(x1, POD_AXIS_Y,
                                                                                                   POD_AXIS_Z))
    k.smooth(body, 50)
    mk.paint(body, lambda c, n: m["dark"] if n.z < -0.45 else None)
    out = [body]
    for i, xr in enumerate(COLLAR_RINGS):
        prof = [(-0.42, r * 0.99), (-0.24, r + 0.36), (0.24, r + 0.36), (0.42, r * 0.99)]
        ring = k.loft(f"collar_ring{i}", [[Vector((xr + t, POD_AXIS_Y + rr * math.cos(2 * math.pi * j / 40),
                                                   POD_AXIS_Z + rr * sq * math.sin(2 * math.pi * j / 40)))
                                           for j in range(40)] for t, rr in prof], m["pale"], cap_start=False,
                      cap_end=False)
        k.smooth(ring, 50)
        mk.paint(ring, lambda c, n: m["green_side"] if n.z < -0.3 else None)
        out.append(ring)
    return out


# --- The bow -------------------------------------------------------------------------------------------------------

def bow_outline():
    xs = [BOW_X0 + (NOSE - BOW_X0) * i / 80 for i in range(81)]
    xs = sorted(set(round(x, 4) for x in xs + [NOSE - 2.5 * (1 - math.cos(math.pi / 2 * i / 10)) for i in range(11)]))
    back = [(x, BACK(x)) for x in reversed(xs) if x < NOSE - 1e-3]
    front = [(x, FRONT(x)) for x in xs if x < NOSE - 1e-3]
    # The round nose: from the front edge's end round to the back edge's.
    yb, yf = BACK(NOSE - 0.6), FRONT(NOSE - 0.6)
    yc, ry = (yb + yf) / 2, (yb - yf) / 2
    nose = [(NOSE - 0.6 + 0.6 * math.sin(math.pi * i / 12), yc - ry * math.cos(math.pi * i / 12)) for i in range(1, 12)]
    return ccw(front + nose + back)


def deck_z(x, y):
    """The deck's top (above DECK_FRONT): its edge height rising to a crown along its middle."""
    edge, crown = DECK(min(max(x, BOW_X0), NOSE))
    yb = BACK(x)
    mid, half = (yb + DECK_FRONT) / 2, max((yb - DECK_FRONT) / 2, 0.3)
    t = min(1.0, abs(y - mid) / half)
    return edge + (crown - edge) * (1 - t * t)


def bow_z(x, y):
    """The hull's top: the deck, and in front of its front edge the apron falling to its foot."""
    if y >= DECK_FRONT:
        return deck_z(x, y)
    edge, _ = DECK(min(max(x, BOW_X0), NOSE))
    yf = FRONT(x)
    t = min(1.0, (DECK_FRONT - y) / max(DECK_FRONT - yf, 0.2))
    return edge - (edge - APRON_FOOT) * t ** 0.9


def bow(m):
    def height(x, y, d):
        return max(UNDERSIDE + 0.2, bow_z(x, y) - DECK_RIM + DECK_RIM * round_edge(d, DECK_RIM))

    def paint(x, y, d):
        if y < DECK_FRONT - 0.05:
            return "dark"
        if d < 0.55 and x > 17.0:
            return "rim"
        return "deck"
    body = relief("bow", [bow_outline()], height, m, paint=paint, side="green_side", bottom=UNDERSIDE, spacing=0.4,
                  band=1.6, borders=[(lambda x, y, d: y, DECK_FRONT - 0.05)], smooth_angle=40.0)
    return body


def bow_details(m, hit):
    out = []
    # The slats along the apron.
    for i, (y, xa, xb) in enumerate(SLATS):
        pts = []
        for j in range(17):
            x = xa + (xb - xa) * j / 16
            h = hit(x, y)
            pts.append((x, y, (h[0].z if h else bow_z(x, y)) + 0.08, 0.36))
        slat = mk.smooth_tube(f"slat{i}", pts, m["slat"], 10, iterations=1)
        for v in slat.data.vertices:  # flattened onto the apron
            h = hit(v.co.x, v.co.y)
            if h and v.co.z > h[0].z:
                v.co.z = h[0].z + (v.co.z - h[0].z) * 0.6
        out.append(k.smooth(slat, 60))
    # The pair of ribs across the deck.
    for i, (x, hw) in enumerate(RIBS):
        y0, y1 = min(RIB_Y[0], BACK(x) - 0.7), RIB_Y[1]
        points, ups = [], []
        for j in range(10):
            y = y0 + (y1 - y0) * j / 9
            h = hit(x, y)
            points.append(Vector((x, y, h[0].z if h else bow_z(x, y))))
            ups.append(h[1] if h else Vector((0, 0, 1)))
        bar = mk.bar(f"rib{i}", points, ups, hw, 0.38, 0.3, m["light"], 10, 3.0)
        out.append(k.smooth(bar, 50))
    # The hatch by the deck's front edge: a raised plate with a rounded edge.
    x0, x1, y0, y1 = HATCH
    zt = max(bow_z(x, y) for x in (x0, x1) for y in (y0, y1))
    plate = mk.box("hatch", x0, x1, y0, y1, zt - 1.0, zt + 0.3, m["light"])
    mk.bevel(plate, 0.3, 2, 35.0)
    mk.shade(plate, 40.0)
    out.append(plate)
    # The light rim round the nose: a bead just inside the deck's edge, from the back edge round the nose to the
    # deck's front edge.
    pts = [(x, BACK(x) - 0.62) for x in [NOSE - 4.6 + 3.6 * i / 8 for i in range(9)]]
    yb = BACK(NOSE - 0.8) - 0.9
    pts += [(NOSE - 0.62, yb + (DECK_FRONT + 0.55 - yb) * i / 5) for i in range(6)]
    bead_pts = []
    for x, y in pts:
        h = hit(x, y)
        bead_pts.append((x, y, (h[0].z if h else bow_z(x, y)) + 0.02, 0.32))
    bead = mk.smooth_tube("nose_rim", bead_pts, m["light"], 8, iterations=2)
    out.append(k.smooth(bead, 60))
    return out


def strut(m):
    """The prong under the stern: a rounded post leaning down to the ground in front, its foot darker."""
    pts = [Vector(p) for p in STRUT]
    rings = []
    n = len(pts)
    dense = []
    for i in range(n - 1):
        for j in range(4):
            t = j / 4
            dense.append((pts[i].lerp(pts[i + 1], t), STRUT_W[i] + (STRUT_W[i + 1] - STRUT_W[i]) * t))
    dense.append((pts[-1], STRUT_W[-1]))
    for i, (p, w) in enumerate(dense):
        a = dense[max(i - 1, 0)][0]
        b = dense[min(i + 1, len(dense) - 1)][0]
        t = (b - a).normalized()
        up = Vector((0, 0, 1)) - t * t.z
        up.normalize()
        across = t.cross(up).normalized()
        ring = []
        for j in range(16):
            u, v = mk.superellipse_point(2 * math.pi * j / 16, 3.0)
            ring.append(p + across * u * w + up * v * w * 0.8)
        rings.append(ring)
    post = k.loft("strut", rings, m["green"], start_point=dense[0][0] + Vector((0, 0.4, 0.4)),
                  end_point=dense[-1][0] - Vector((0, 0.3, 0.3)))
    k.smooth(post, 45)
    mk.paint(post, lambda c, nn: m["dark"] if c.z < 1.6 or nn.x < -0.55 else None)
    foot = mk.dome("strut_foot", (STRUT[-1][0], STRUT[-1][1] - 0.2), (1.75, 1.5, 0.75), 0.0, m["dark"], 16, 4)
    return [post, foot]


def lamp(m):
    """The red lamp hanging under the apron's end: a glowing lens in a dark red seat."""
    x, y, z = LAMP
    seat = mk.ball("lamp_seat", (x, y + 0.35, z + 0.35), (2.2, 1.25, 0.95), m["red_dark"], 18, 8)
    lens = mk.ball("lamp", (x - 0.15, y - 0.2, z), (1.4, 1.0, 1.0), m["lamp"], 16, 8)
    return [seat, lens]


# --- Build ---------------------------------------------------------------------------------------------------------

def build_whole(m):
    stern(m)
    collar(m)
    body = bow(m)
    bpy.context.view_layer.update()
    hit = mk.surface([body])
    bow_details(m, hit)
    strut(m)
    lamp(m)
    whole = mk.meshes()
    for obj in whole:
        mk.apply(obj)
        if min(v.co.z for v in obj.data.vertices) < -1e-4:  # nothing below the ground
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=(0, 0, 0),
                                   plane_no=(0, 0, -1), clear_outer=True)
            bm.to_mesh(obj.data)
            bm.free()
    bpy.context.view_layer.update()
    return [o for o in whole if len(o.data.polygons) > 0]


def mirrored(whole):
    """The whole mirrored about x = MIRROR_X (the skiff coming in from the right), as new objects."""
    out = []
    for obj in whole:
        copy = k.mirror_x(obj, obj.name + "_m")
        copy.data.name = copy.name
        copy.data.transform(Matrix.Translation((2 * MIRROR_X, 0, 0)))
        out.append(copy)
    bpy.context.view_layer.update()
    return out


def whole_mask(sheet, left, right):
    a, b = k.sprite_mask(sheet, left), k.sprite_mask(sheet, right)
    return [p + q for p, q in zip(a, b)]


def build():
    options = k.args()
    out = mk.outdir(options)
    k.reset()
    m = materials()
    whole = build_whole(m)
    mirror = mirrored(whole)
    bpy.context.scene.view_settings.view_transform = "Standard"
    sheet = os.path.join(options["check"], "enemy_J.png") if "check" in options else None
    for label, objects, sprites in (("skiff", whole, (169, 207)), ("skiff_l", mirror, (245, 283))):
        others = mirror if objects is whole else whole
        for o in others:
            o.hide_render = True
        low, high = mk.bounds(objects)
        print("== whole %s (J %d | %d): %d triangles, %d objects, %d materials, x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f"
              % (label, sprites[0], sprites[1], mk.triangles(objects), len(objects), len(mk.materials_of(objects)),
                 low.x, high.x, low.y, high.y, low.z, high.z))
        if sheet:
            mk.compare("whole %s (J %d | %d)" % (label, sprites[0], sprites[1]), mk.coverage(objects, 48, 28),
                       whole_mask(sheet, *sprites))
        if "preview" in options:
            mk.preview(options["preview"] + "green_" + label + "_whole", objects, size=(48, 28), scale=10,
                       distance=1.6)
        for o in others:
            o.hide_render = False
    only = options.get("only", "").split(",") if "only" in options else None
    for name, sprite, box, is_mirror in PIECES:
        if only and name not in only:
            continue
        source = mirror if is_mirror else whole
        pieces = [p for p in (cut(src, box, m["seam"]) for src in source) if p is not None]
        mk.transform(pieces, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
        bpy.context.view_layer.update()
        for src in whole + mirror:
            src.hide_render = True
        if sheet:
            mk.compare("%s (J %d)" % (name, sprite), mk.coverage(pieces, 24, 28), k.sprite_mask(sheet, sprite))
        mk.report(name, pieces, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, pieces)
        for obj in pieces:
            bpy.data.objects.remove(obj)
        for src in whole + mirror:
            src.hide_render = False


if __name__ == "__main__":
    build()
