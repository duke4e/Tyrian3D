"""The glossy red ball that IXMUCANE's and SAWBLADES' pink torpedo (8 125, enemy 91) and red pod (8 153, enemy 100)
leave behind them (sheet 8 sprite 102, 1x1: the whole 12 x 14 cell; enemy 454 of episode 3, which they launch every
10 and 30 game ticks; it lies still where it is made: move 0, 0; armour 20), and its cracked look (8 140: the game
shows it in its place when 10 armour is left: dgr 140, dlevel 10, and models are keyed by the first sprite).
Polished (2026-10-21; neither had a model: the game drew a pixelated stand-in). models.cfg: model red_ball
enemies/red_ball.glb origin, model red_ball_cracked enemies/red_ball_cracked.glb origin; sprite 8 102 red_ball yaw=0
height=-4, sprite 8 140 red_ball_cracked yaw=0 height=-4. No other enemy shows either sprite, and neither is another
sprite's pixels mirrored, turned or in other ramps. The launchers are ground enemies, so the balls are made on
ground 2 (slots 75-99), drawn on the ground, and the torpedo moves on at 4 pixels a tick and the pod at 1, so the
balls lie in a trail behind them; the models stand on z = 0 and are drawn at their origin, and height=-4 sets them
on the ground (IXMUCANE's and SAWBLADES' rolling relief too; a model centred in height would sink 2 pixels into
raised ground). On the top layer (SAWBLADES' torpedoes on top) they float 4 pixels lower.

As the sprite draws it (the 4x upscales have no picture of it): a glossy ball of the pink torpedo's red (palette ramp
4, as its body) 12 pixels across and 14 high, lit from the upper left: a soft glare of pale pink, white in its middle
(shade 15 round column 4 of row 4), the ball darker red below it and towards the lower left, a bright crescent inside
its rim at the lower right (rows 7-12, brightest at columns 8-9 of rows 10-11, shade 14), where the light through
it gathers as in a marble, and a dark outline, black at the right and the bottom.

8 140 draws the same ball broken: its shell shattered on the side seen, the black hollow inside showing through a
big ragged hole in its lower left (columns 0-7 of rows 6-10) with a notch at the bottom and a reach to the right
(columns 7-8 of row 9), cracks running up from the hole through the shell to its top (column 4 of rows 1-3) and to
the right (column 9 of row 6, column 8 of row 3), the shell dulled (its glare five shades darker, shade 10 at most),
the crescent still bright but broken, and splinters of the shell lying in the hollow (columns 3-4 of rows 9-10).

Built as a ball painted for the game's camera (polish_dark_orb.py's way): an ellipsoid (6 x 6.9 pixels, 6 high) of
even triangles, finer where the camera sees it, standing on the ground (z = 0), its shades a smooth field (the body
lighter towards the top, the glare, the crescent, the dark outline where the surface turns away from the camera)
laid out as the sprite draws it seen from VIEW_TILT degrees off straight down from the bottom of the screen (the
game's camera is 20 degrees off), so that the glare and the crescent sit where the sprite draws them in the game's
view; faces cut along the bands of shade (polish_orb_red.band_split) into palette materials of ramp 4. The game's
camera sees much of the ball's side away from its sun, so the body is a shade lighter than the sprite's and every
band glows faintly in its own colour (0.1, the crescent's and the glare's up to 0.52), so that the ball reads red,
not black (the game's bloom adds to it).
The cracked ball is the same ball: the hole and its notches cut out of the shell along their ragged outlines (the
sprite's black, laid out for the game's camera too), their edges turned in to a broken edge THICK pixels deep; inside,
the hollow: a black ball just inside the shell; the cracks painted black and pressed in along their lines; the
splinters small curved shards of the shell lying in the hollow; the glare dulled.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground; origin at the
sprite's centre (pixel 6, 7: column c is x = c + 0.5 - 6, row r is y = 6.5 - r); the ball's middle is there, RZ up.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each model's silhouette
against its sprite in enemy_8.png), --preview <prefix>, --only <name,...> (red_ball, red_ball_cracked).
"""
import math
import os
import sys

import bmesh
import bpy
import mathutils.noise as noise
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_orb_red import band_split, smoothstep  # noqa: E402
from polish_sphere_nozzle import split_along  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402

RAMP = 4
SPRITES = {"red_ball": 102, "red_ball_cracked": 140}

# The ball: radii (the sprite's 12 x 14 with its outline; the height a ball's), standing on the ground.
RX, RY, RZ = 6.0, 6.9, 6.0
CENTRE = Vector((0.0, 0.0, RZ))
SPRITE_HALF = (6.0, 7.0)       # the sprite's ball, half its width and height
# The painting is laid out as the sprite draws it seen from this many degrees off straight down (from the bottom of
# the screen; the game's camera: 20).
VIEW_TILT = 20.0
T = math.radians(VIEW_TILT)
TOWARDS_VIEW = Vector((0.0, -math.sin(T), math.cos(T)))
VIEW_H = math.hypot(RY * math.cos(T), RZ * math.sin(T))

# The shades (of ramp 4, 0-15): the body, lighter towards the top (BODY: at the bottom and at the top of the ball),
# on the side the camera doesn't see BODY_BACK; the glare (its middle in the sprite's pixels, radius, peak over the
# body); the crescent (the angle round the ball's middle it peaks at (degrees from +x, as the sprite draws it), its
# spread, the distance out it lies at (a fraction of the radius), its half-width and peak); the outline (where it
# starts to darken, a fraction of the radius, and the shade at the edge: at the upper left and at the lower right).
BODY = (4.2, 6.6)
BODY_BACK = 4.0
GLARE, GLARE_R, GLARE_PEAK = Vector((-1.5, 2.5)), 2.3, 10.5
CRESCENT_AT, CRESCENT_SPREAD, CRESCENT_RHO, CRESCENT_W, CRESCENT_PEAK = -52.0, 42.0, 0.79, 0.13, 9.8
OUTLINE_FROM, OUTLINE_EDGE = 0.86, (2.0, 0.2)

# The bands: (lowest shade, palette index, emission strength in the band's own colour). 0x41 is left out (fifteen
# materials at most).
BANDS = [(-99.0, 0x40, 0.0), (1.5, 0x42, 0.1), (2.5, 0x43, 0.1), (3.5, 0x44, 0.1), (4.5, 0x45, 0.1),
         (5.5, 0x46, 0.1), (6.5, 0x47, 0.12), (7.5, 0x48, 0.15), (8.5, 0x49, 0.2), (9.5, 0x4a, 0.26),
         (10.5, 0x4b, 0.32), (11.5, 0x4c, 0.4), (12.5, 0x4d, 0.48), (13.5, 0x4e, 0.52), (14.5, 0x4f, 0.45)]
FINISH = dict(metallic=0.1, roughness=0.22)

# The cracked ball (8 140): the glare's peak (dulled), the crescent's (broken by the cracks, as bright), the body's.
CRACKED_GLARE, CRACKED_CRESCENT, CRACKED_BODY = 5.0, 9.0, (3.0, 4.6)
# The hole: rounded blobs in the sprite's pixels (middle, half sizes), their union's outline made ragged by noise
# (RAGGED pixels); its broken edge THICK deep; the hollow inside (black).
HOLE = [((-2.2, -1.1), (3.8, 2.0)), ((-4.6, -0.4), (1.3, 1.3)), ((-4.3, -2.8), (1.4, 1.2)),
        ((-1.0, -3.9), (0.8, 1.0)), ((1.9, -2.4), (1.0, 0.7)), ((0.2, 0.2), (0.9, 0.7))]
RAGGED, RAGGED_SCALE = 0.55, 0.9
THICK = 0.5
# The cracks: polylines in the sprite's pixels (from the hole outwards), their half-width and how far they are
# pressed in.
CRACKS = [[(-1.6, 0.6), (-1.4, 2.1), (-1.6, 3.6), (-1.4, 5.0), (-1.8, 6.1)],
          [(-1.5, 4.4), (-0.4, 4.6), (0.3, 5.6)],
          [(1.6, -1.6), (2.7, -1.2), (3.4, -0.2), (3.4, 0.7), (2.6, 2.4), (2.6, 3.5), (3.6, 4.0)],
          [(-4.2, 0.6), (-4.8, 1.8), (-5.5, 2.6)],
          [(2.4, -2.8), (3.1, -4.2), (3.4, -5.3)]]
CRACK_W, CRACK_SINK = 0.38, 0.3
# The splinters in the hollow: (middle in the sprite's pixels, size, turn (degrees), palette index).
SPLINTERS = [((-1.6, -2.4), 1.05, 25.0, 0x47), ((-2.7, -3.4), 0.95, -40.0, 0x48), ((-3.9, -1.2), 0.7, 70.0, 0x45)]
HOLLOW_INDEX, EDGE_INDEX = 0x01, 0x45


def angle_off(a, b):
    return (a - b + 180.0) % 360.0 - 180.0


def view(p):
    """Where the point p of the ball's surface shows in the view the painting is laid out in, in the sprite's pixels
    (x right, y up, from the sprite's centre), its distance out (a fraction of the radius), the angle round the
    middle (degrees) and whether the view sees it."""
    rel = p - CENTRE
    u = rel.x / RX
    v = (rel.y * math.cos(T) + rel.z * math.sin(T)) / VIEW_H
    normal = Vector((rel.x / RX ** 2, rel.y / RY ** 2, rel.z / RZ ** 2))
    seen = normal.dot(TOWARDS_VIEW) > 0.0
    sprite = Vector((u * SPRITE_HALF[0], v * SPRITE_HALF[1]))
    return sprite, math.hypot(u, v), math.degrees(math.atan2(v, u)), seen


def shade_at(p, glare_peak=GLARE_PEAK, crescent_peak=CRESCENT_PEAK, body=BODY):
    """The shade of ramp 4 at the ball's surface point p."""
    sprite, rho, angle, seen = view(p)
    if not seen:
        return BODY_BACK
    s = body[0] + (body[1] - body[0]) * smoothstep(-5.5, 5.0, sprite.y)
    s += glare_peak * math.exp(-((sprite - GLARE).length / GLARE_R) ** 2)
    s += crescent_peak * (math.exp(-(angle_off(angle, CRESCENT_AT) / CRESCENT_SPREAD) ** 2) *
                          math.exp(-((rho - CRESCENT_RHO) / CRESCENT_W) ** 2))
    # The outline: dark red at the upper left, black at the lower right.
    edge = OUTLINE_EDGE[0] + (OUTLINE_EDGE[1] - OUTLINE_EDGE[0]) * (0.5 - 0.5 * math.cos(math.radians(angle - 135.0)))
    return s + (edge - s) * smoothstep(OUTLINE_FROM, 1.0, rho)


def ball_bmesh():
    """An icosphere mapped onto the ball, twice as fine where the game's camera sees it."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=3, radius=1.0)

    def seen(v):
        d = v.co.normalized()
        n = Vector((d.x / RX, d.y / RY, d.z / RZ))
        return n.dot(TOWARDS_VIEW) > -0.25

    edges = [e for e in bm.edges if all(seen(v) for v in e.verts)]
    bmesh.ops.subdivide_edges(bm, edges=edges, cuts=1, use_grid_fill=True)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    for v in bm.verts:
        d = v.co.normalized()
        v.co = CENTRE + Vector((d.x * RX, d.y * RY, d.z * RZ))
    return bm


def outward(p):
    rel = p - CENTRE
    return Vector((rel.x / RX ** 2, rel.y / RY ** 2, rel.z / RZ ** 2)).normalized()


def to_object(name, bm):
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def materials():
    pal = k.level_palette()
    mats = {}
    for _, index, glow in BANDS:
        mats[index] = k.material(f"redball_{index:02x}", palette=index, emission=pal[index] if glow > 0 else None,
                                 emission_strength=glow, **FINISH)
    return mats


def paint(obj, shade, mats):
    values = [shade(v.co.copy()) for v in obj.data.vertices]
    band_split(obj, values, [(lowest, mats[index]) for lowest, index, _ in BANDS])
    return obj


# --- The cracked ball -----------------------------------------------------------------------------------------------

def hole_field(p):
    """How far inside the hole the point p is (pixels in the sprite; negative outside); only on the side seen."""
    sprite, rho, angle, seen = view(p)
    if not seen:
        return -9.0
    inside = -9.0
    for (cx, cy), (hx, hy) in HOLE:
        q = Vector(((sprite.x - cx) / hx, (sprite.y - cy) / hy))
        inside = max(inside, (1.0 - q.length) * min(hx, hy))
    rag = noise.noise(Vector((sprite.x * RAGGED_SCALE, sprite.y * RAGGED_SCALE, 3.7)))
    rag += 0.5 * noise.noise(Vector((sprite.x * RAGGED_SCALE * 2.3, sprite.y * RAGGED_SCALE * 2.3, 8.1)))
    return inside + RAGGED * rag


def segment_distance(q, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (q - a).dot(ab) / ab.length_squared))
    return (q - (a + ab * t)).length


def crack_field(p):
    """0-1: how deep in a crack's line the point p is."""
    sprite, rho, angle, seen = view(p)
    if not seen:
        return 0.0
    best = 9.0
    for line in CRACKS:
        pts = [Vector(c) for c in line]
        for a, b in zip(pts, pts[1:]):
            best = min(best, segment_distance(sprite, a, b))
    # A little wobble along the lines, so that they don't read ruled.
    best += 0.12 * noise.noise(Vector((sprite.x * 1.7, sprite.y * 1.7, 5.3)))
    return math.exp(-(max(0.0, best) / CRACK_W) ** 2)


def cracked_shade(p):
    s = shade_at(p, CRACKED_GLARE, CRACKED_CRESCENT, CRACKED_BODY)
    c = crack_field(p)
    return s + (-9.0 - s) * smoothstep(0.35, 0.6, c)


def cracked_shell(mats):
    """The shell with the hole cut out and the cracks pressed in, and the hole's broken edge: its outline turned in,
    THICK deep (a strip of its own, facing into the hole)."""
    bm = ball_bmesh()
    split_along(bm, {v: hole_field(v.co) for v in bm.verts}, 0.0)
    split_along(bm, {v: crack_field(v.co) for v in bm.verts}, 0.47)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    gone = [f for f in bm.faces if hole_field(f.calc_center_median()) > 0.0]
    bmesh.ops.delete(bm, geom=gone, context="FACES")
    for v in bm.verts:
        c = crack_field(v.co)
        if c > 0.05:
            v.co -= outward(v.co) * CRACK_SINK * c
    verts, faces = [], []
    for e in bm.edges:
        if not e.is_boundary:
            continue
        a, b = e.verts[0].co.copy(), e.verts[1].co.copy()
        quad = [a, b, b - outward(b) * THICK, a - outward(a) * THICK]
        # Facing into the hole: away from the shell's face along the edge.
        side = e.link_faces[0].calc_center_median()
        normal = (quad[1] - quad[0]).cross(quad[3] - quad[0])
        if normal.dot((a + b) / 2 - side) < 0:
            quad = quad[::-1]
        base = len(verts)
        verts += quad
        faces.append((base, base + 1, base + 2, base + 3))
    shell = to_object("red_ball_cracked_shell", bm)
    paint(shell, cracked_shade, mats)
    k.smooth(shell, 60)
    rim = k.mesh_object("red_ball_cracked_edge", verts, faces, mats[EDGE_INDEX])
    bm = bmesh.new()
    bm.from_mesh(rim.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bm.to_mesh(rim.data)
    bm.free()
    return [shell, k.smooth(rim, 50)]


def hollow():
    """The black hollow just inside the shell."""
    mat = k.material("redball_hollow", palette=HOLLOW_INDEX, metallic=0.0, roughness=0.8)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=3, radius=1.0)
    for v in bm.verts:
        d = v.co.normalized()
        v.co = CENTRE + Vector((d.x * (RX - THICK), d.y * (RY - THICK), d.z * (RZ - THICK)))
    obj = to_object("red_ball_hollow", bm)
    obj.data.materials.append(mat)
    k.recalc_normals(obj)
    return k.smooth(obj, 80)


def find_inner_point(sx, sy):
    """The point of the hollow's far wall that the view sees at the sprite's pixel (sx, sy): along the view ray."""
    u, v = sx / SPRITE_HALF[0] * RX, sy / SPRITE_HALF[1] * VIEW_H
    # A point on the view's plane through the middle, then down the ray (away from the camera) to the hollow's wall.
    up = Vector((0.0, math.cos(T), math.sin(T)))
    start = CENTRE + Vector((u, 0.0, 0.0)) + up * v
    a = Vector((RX - THICK, RY - THICK, RZ - THICK))
    d = -TOWARDS_VIEW
    # Solve |(start + t d - centre) / a| = 1 for the larger t (the far wall).
    o = start - CENTRE
    oa = Vector((o.x / a.x, o.y / a.y, o.z / a.z))
    da = Vector((d.x / a.x, d.y / a.y, d.z / a.z))
    qa, qb, qc = da.dot(da), 2 * oa.dot(da), oa.dot(oa) - 1.0
    disc = max(0.0, qb * qb - 4 * qa * qc)
    t = (-qb + math.sqrt(disc)) / (2 * qa)
    return start + d * t


def splinters(mats):
    """Small curved shards of the shell lying on the hollow's floor where the sprite draws them (in the shell's
    band materials)."""
    objs = []
    for i, ((sx, sy), size, turn, index) in enumerate(SPLINTERS):
        mat = mats[index]
        at = find_inner_point(sx, sy)
        n = -outward(at)                            # the hollow's floor faces into the ball
        t1 = n.cross(Vector((0.0, 0.0, 1.0)) if abs(n.z) < 0.9 else Vector((1.0, 0.0, 0.0))).normalized()
        t2 = n.cross(t1).normalized()
        a = math.radians(turn)
        t1, t2 = t1 * math.cos(a) + t2 * math.sin(a), t2 * math.cos(a) - t1 * math.sin(a)
        # A jagged triangle-ish shard, bowed like a piece of the shell, THICK thick.
        outline = [(1.0, 0.0), (0.15, 0.75), (-0.8, 0.35), (-0.55, -0.6), (0.35, -0.7)]
        top, bottom = [], []
        for ox, oy in outline:
            p = at + n * 0.25 + (t1 * ox + t2 * oy) * size
            bow = 0.25 * (1.0 - (ox * ox + oy * oy) * 0.6) * size
            top.append(p + n * (THICK * 0.8 + bow))
            bottom.append(p + n * bow)
        verts = top + bottom
        m = len(outline)
        faces = [tuple(range(m)), tuple(range(2 * m - 1, m - 1, -1))]
        faces += [(j, (j + 1) % m, m + (j + 1) % m, m + j) for j in range(m)]
        obj = k.mesh_object(f"splinter{i}", verts, faces, mat)
        k.recalc_normals(obj)
        mk.bevel(obj, 0.08, 1, 30)
        objs.append(obj)
    return objs


# --- Build ----------------------------------------------------------------------------------------------------------

def build_ball(mats):
    obj = to_object("red_ball", ball_bmesh())
    paint(obj, shade_at, mats)
    return [k.smooth(obj, 80)]


def build_cracked(mats):
    return [hollow()] + cracked_shell(mats) + splinters(mats)


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    for name, builder in (("red_ball", build_ball), ("red_ball_cracked", build_cracked)):
        if only and name not in only:
            continue
        k.reset()
        mats = materials()
        objects = builder(mats)
        triangulate(objects)  # the same split every run (with and without --check)
        bpy.context.view_layer.update()
        if "check" in options:
            sheets = options["check"]
            sheet = os.path.join(sheets, "enemy_8.png") if os.path.isdir(sheets) else sheets
            mk.compare("%s (8 %d)" % (name, SPRITES[name]), mk.coverage(objects, 12, 14),
                       k.sprite_mask(sheet, SPRITES[name], large=False))
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, objects, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, objects, size=(12, 14), scale=32, distance=0.45)


if __name__ == "__main__":
    build()
