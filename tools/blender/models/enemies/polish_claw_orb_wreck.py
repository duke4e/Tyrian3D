"""What is left of the black orb of the asteroid levels once it is destroyed (sheet S sprites 39 and 41 above 77 and 79:
their stand-ins, what the maps paint where the orb stands, before it comes, once it is shot and where none comes; 17 of
them in ASTEROID1, ASTEROID2, ASTEROID?, ASTCITY, AST. CITY, AST ROCK and GREY MOON), stage 4 of the clean ground
(2026-10-25), built on polish_claw_orb.py. models.cfg: model claw_orb_tl_wreck / _tr_wreck / _bl_wreck / _br_wreck
enemies/claw_orb_*_wreck.glb origin; wreck s 39 claw_orb_tl_wreck, wreck s 41 claw_orb_tr_wreck, wreck s 77
claw_orb_bl_wreck, wreck s 79 claw_orb_br_wreck (drawn with the live sprite lines' options, yaw=0 height=-4).

As the maps paint it at 4x (the asteroid tiles under the orb, the same on every map; ASTEROID1 14a0d01cd2b01f4c at 504,
757; columns and rows of the 48 x 56 picture): the same machine, its outline unchanged, but dead: the orb's glass black
(0x01) and cracked, its glint and reflections gone; light cracks (0x03-0x0c) across it: a long curved one from its upper
left towards its middle (columns 13-20 of rows 8-13), a short one at its left (columns 9-11 of rows 10-14), a chevron at
its right (columns 27-32 of rows 14-22), a forked one at its upper right (columns 28-31 of rows 8-13), short ones at its
top (columns 16 and 20, rows 6-9) and its left middle (columns 11-15 of rows 20-22); a hole punched into it below its
middle (columns 21-28 of rows 21-29), black inside, its broken edge catching the light; cracks under the hole (columns
22-28 of rows 28-31). The bronze shoulders and the band burnt (0x10-0x16 where they were 0x13-0x19, the right shoulder
darker), the band's ribs still a little lit; the claws' roots tan (0xa1-0xa7), their lower parts charred nearly black
(0x40, 0x10); the small ball dark, cracked across its lower left (a light crescent, columns 18-24 of rows 44-50), its
right rim lit. No embers: nothing glows.

The model: polish_claw_orb.py's parts in their cold frame (the shoulders, the claws, the band and its ribs, the cup, the
pit, the ball), then broken: the orb rebuilt as its ellipsoid of even triangles painted black glass (0x01) with the
cracks cut in along smooth contours (polish_orb_red.band_split) of their distance as the camera sees them (light cores
0x0c, edges 0x08, dark halos 0x04), the hole pressed 2.8 pixels into the orb (its inside black, a light rim 0x08-0x0c
round its broken edge); the ball painted the same way (black, its crescent crack, its lit rim) and pressed in a little
along the crack; the bronze and the tan scorched by noise fields along their contours (polish_jaw_gun_wreck.scorch:
three shades darker, or the brown-black 0x10), the claws more the farther down they reach, the right shoulder more than
the left; a few black shards of the orb's glass lying in the pit round the ball. Cut along the sprites' edges as the
live orb (polish_claw_orb.export_piece: polish_savara_boss.cut, the caps in each part's inside colour).

Coordinates as polish_claw_orb.py's: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground (z = 0);
the whole's origin is the corner where the four sprites meet; the camera's view of a point is polish_claw_orb.view().

Options after "--": --outdir <dir> (default assets/models/enemies), --preview <prefix>, --only <name,...>.
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
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
import polish_claw_orb as live  # noqa: E402
from polish_orb_red import band_split, icosphere, smoothstep  # noqa: E402
from polish_panel_pills_wreck import fbm  # noqa: E402
from polish_jaw_gun_wreck import scorch, shard  # noqa: E402

PIECES = [(name + "_wreck", box) for name, _, box in live.PIECES]

# The cracks across the orb as the camera sees them: polylines of the picture's (column, row), and their half-width.
CRACKS = [([(12.4, 7.8), (14.4, 9.5), (16.6, 11.3), (18.6, 12.7), (19.8, 13.3)], 1.2),
          ([(9.2, 10.0), (9.9, 12.0), (10.8, 14.2)], 0.85),
          ([(15.8, 5.8), (16.5, 7.4)], 0.65), ([(19.6, 7.6), (20.5, 9.2)], 0.65),
          ([(32.6, 14.0), (29.8, 16.0), (27.4, 18.0), (29.6, 20.0), (32.2, 22.2)], 1.0),
          ([(27.8, 7.8), (29.2, 10.2), (30.2, 12.8)], 0.75), ([(29.2, 10.2), (31.4, 8.8)], 0.55),
          ([(10.8, 20.2), (13.4, 20.5), (15.2, 22.4)], 0.65),
          ([(21.4, 28.6), (23.4, 30.2), (26.0, 31.2), (28.2, 30.2)], 0.7),
          ([(14.0, 15.2), (15.4, 15.4)], 0.45), ([(30.0, 15.4), (31.2, 16.2)], 0.45),
          ([(22.6, 15.6), (24.2, 17.6)], 0.5), ([(16.4, 25.6), (18.2, 27.4), (19.0, 29.6)], 0.55)]
# The hole punched in below the middle (picture corners), how deep it is pressed in, its rim's width.
HOLE = [(21.0, 22.4), (23.2, 21.0), (26.6, 21.2), (28.6, 23.0), (28.4, 26.6), (26.8, 28.8), (23.2, 29.0),
        (21.2, 27.2), (20.6, 24.6)]
HOLE_DEPTH, HOLE_RIM = 2.8, 1.1
# The ball's crack (its crescent) and its lit right rim.
BALL_CRACKS = [([(18.4, 44.2), (19.0, 46.8), (20.6, 49.0), (23.2, 50.2)], 0.65),
               ([(27.4, 42.4), (28.3, 45.0), (27.9, 48.0)], 0.5)]
ORB_BANDS = [(-9.0, 0x01), (-0.4, 0x04), (0.0, 0x08), (0.5, 0x0c)]
# Shards of the orb's glass lying in the pit (outline in the picture's corners, tilt about x and y).
SHARDS = [([(13.0, 44.0), (15.2, 43.2), (15.6, 45.4), (13.6, 46.2)], (10.0, -12.0)),
          ([(29.8, 44.6), (31.6, 43.6), (31.8, 45.8)], (-8.0, 14.0)),
          ([(17.6, 51.0), (19.8, 51.6), (18.6, 53.0)], (6.0, 8.0))]


def seg_distance(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-9)))
    return (p - (a + ab * t)).length


def crack_value(v, cracks):
    """1 on a crack's line, 0 at its half-width, falling below beyond (v: the camera's view, picture rows down)."""
    best = -9.0
    for line, w in cracks:
        pts = [Vector((c, r)) for c, r in line]
        d = min(seg_distance(v, a, b) for a, b in zip(pts, pts[1:]))
        best = max(best, 1.0 - d / w)
    return best


def to_picture(p):
    """The picture's (column, row) the camera shows the point p at."""
    v = live.view(p)
    return Vector((v.x + 24.0, 28.0 - v.y))


def inside(pt, poly):
    return live.inside((pt.x, pt.y), poly)


def hole_distance(pt):
    """How far the picture's point lies outside the hole's outline (negative inside)."""
    pts = [Vector(p) for p in HOLE]
    d = min(seg_distance(pt, a, b) for a, b in zip(pts, pts[1:] + pts[:1]))
    return -d if inside(pt, HOLE) else d


def orb_wreck(m):
    """The orb's ellipsoid (as polish_claw_orb.orb() builds it), black glass with the cracks cut in, the hole pressed
    in, its inside black and its broken edge lit."""
    obj = icosphere("orb", tuple(live.ORB_C), live.ORB_R, subdivisions=5)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if max(v.co.z for v in f.verts) < -1.2], context="FACES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    bm.to_mesh(obj.data)
    bm.free()
    towards = Vector((0.0, -math.sin(math.radians(20)), math.cos(math.radians(20))))

    def value(co):
        if live.orb_normal(co).dot(towards) <= 0.0:
            return -9.0
        pt = to_picture(co)
        h = hole_distance(pt)
        if h < 0.0:
            return -9.0                                # (inside the hole: black)
        if h < HOLE_RIM:
            return 0.25 + 0.5 * (1.0 - h / HOLE_RIM)   # its broken edge, lit
        return crack_value(pt, CRACKS)
    band_split(obj, [value(v.co) for v in obj.data.vertices], [(t, m["crack"][i]) for t, i in ORB_BANDS])
    # The hole pressed in towards the orb's middle (its edge torn: the press falls off over half a pixel).
    for v in obj.data.vertices:
        h = hole_distance(to_picture(v.co))
        if h < 0.5:
            press = HOLE_DEPTH * smoothstep(0.5, -0.6, h)
            v.co = v.co + (Vector(live.ORB_C) - v.co).normalized() * press
    k.smooth(obj, 80)
    return obj


def ball_wreck(m, ball):
    """The small ball repainted: black glass, its crescent crack and lit rim, pressed in a little along the crack."""
    band_split(ball, [crack_value(to_picture(v.co), BALL_CRACKS) for v in ball.data.vertices],
               [(t, m["crack"][i]) for t, i in ORB_BANDS])
    for v in ball.data.vertices:
        c = crack_value(to_picture(v.co), BALL_CRACKS[:1])
        if c > 0.0:
            v.co = v.co + (Vector(live.BALL_C) - v.co).normalized() * 0.5 * c
    k.smooth(ball, 80)
    return ball


def burn_field(name):
    """The scorch over the bronze and the tan: noise everywhere, the right shoulder more, the claws more the farther
    down the screen (the lower the row) they reach."""
    def shoulder(co, side):
        base = 0.62 if side > 0 else 0.36
        return base + 0.35 * fbm(co.x * 0.32 + 4.0 * side, co.y * 0.32, co.z * 0.3, 3)

    def claw(co):
        row = to_picture(co).y
        return 0.4 + smoothstep(31.0, 35.5, row) * 0.6 + 0.25 * fbm(co.x * 0.4, co.y * 0.4 + 7.0, co.z * 0.4, 2)

    def band(co):
        return 0.62 + 0.35 * fbm(co.x * 0.4 + 9.0, co.y * 0.4, co.z * 0.3, 2)
    if name.startswith("shoulder"):
        side = 1 if name.endswith("1") and not name.endswith("-1") else -1
        return lambda co: shoulder(co, side)
    if name.startswith("claw"):
        return claw
    if name.startswith("rib"):
        return lambda co: 0.45 + 0.2 * fbm(co.x, co.y, co.z, 1)
    return band


def build_whole():
    m = live.materials(0)
    # The cracks' shades: the orb's black and greys, and a light grey of their own (the live 0x0b glows a little).
    m["crack"] = {0x01: m["orb"][0x01], 0x04: m["orb"][0x04],
                  0x08: k.material("cowreck_crack", palette=0x08, metallic=0.35, roughness=0.2),
                  0x0c: k.material("cowreck_crack_light", palette=0x0c, metallic=0.35, roughness=0.18)}
    parts = [orb_wreck(m)]
    for side in (-1, 1):
        parts += live.shoulder_parts(m, side)
        parts += live.claw_parts(m, side)
    parts += live.band_parts(m)
    ball_parts = live.ball_parts(m, 0)
    ball_wreck(m, ball_parts[0])
    parts += ball_parts
    for obj in parts:
        mk.apply(obj)
    for obj in parts:
        if obj.name.startswith(("shoulder", "claw", "band", "rib")):
            scorch(obj, burn_field(obj.name), levels=(0.3, 0.72), step=1.2 if obj.name.startswith("band") else None)
            k.smooth(obj, 50 if not obj.name.startswith("rib") else 35)
    for i, (outline, tilt) in enumerate(SHARDS):
        pts = [(c - 24.0, 28.0 - r) for c, r in outline]
        shard(f"shard{i}", pts, 0.12, 0.3, m["orb"][0x01] if i != 1 else m["orb"][0x03], tilt)
    whole = [o for o in mk.meshes() if len(o.data.polygons) > 0]
    for obj in whole:
        mk.apply(obj)
    bpy.context.view_layer.update()
    return whole, m


def build():
    options = k.args()
    only = options["only"].split(",") if "only" in options else None
    k.reset()
    whole, m = build_whole()
    print("whole claw orb wreck: %d triangles" % mk.triangles(whole))
    if "preview" in options:
        mk.preview(options["preview"] + "claw_orb_wreck_whole", whole, size=(48, 56), scale=8, distance=1.9)
    for name, box in PIECES:
        if only and name not in only:
            continue
        live.export_piece(whole, m, name, box, options, None, name)


if __name__ == "__main__":
    build()
