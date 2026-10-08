"""Batch X of wave 3 (sheet C: DELI, New Deli, BONUS and others), modelled as their sprites look (models.cfg:
yaw=0). DELI's tall tower and the gun on its mast are in wave3_x_tower.py, its long cannons in
wave3_x_cannon.py; the kit is wave3_x_kit.py, the pixels wave3_x_art.py.

- glass_hatch (C 1): the square glass hatch let into DELI's floor tiles: a raised pale frame round a pane of
  tinted glass with a diagonal glint (the sprite's first frame), and under the glass, rising from a dark pit
  in the tiles, the red machine the hatch hides: a red dome with three glowing slots (the frames 3-13 fade it
  in and light the slots; the model shows it through the glass, its slots glowing) and two grey claws.
- slit_bunker (C 39): the grey bunker with a rounded back, a raised spine down its middle with two slits in it
  (the frames 41, 43 light them red; the slits glow), a band across it and four ribs at its front reaching
  down to the floor tiles it stands on.
- blue_eye_helm (C 49): the blue armoured helm with the red eye of DELI and HARVEST: a curved hood over its
  upper left, a ribbed plate on its right, the eye glowing in a dark socket in the middle (the frames 51, 53
  brighten it) and a base with two pale slats and vents.

usage: Blender -b --factory-startup -P wave3_x.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1]
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_x_kit as x  # noqa: E402
from wave3_x_kit import art, k, sh, w, pal, px, py  # noqa: E402


# --- C 1: the glass hatch ------------------------------------------------------------------------------

@x.model("glass_hatch", [(1, True)])
def glass_hatch():
    """The tiles as a pad, a raised pale frame (cols 2-20, rows 3-24) round a glass pane, the dark pit in the
    tiles under it and the red machine rising from it to just under the glass."""
    shut = x.grid(art.HATCH, 24)
    hot = x.grid(art.HATCH_HOT, 24)
    origin = (12, 14)
    pad_top = 1.2

    # The tiles: the shut frame's floor, the glint on the glass left out (inside the frame the open frame's
    # tiles where it has them) and the frame's shadow (col 21, row 25) given the floor's shades.
    def inside(c, r):
        return 3 <= c <= 19 and 4 <= r <= 23

    merged = []
    for r in range(28):
        row = []
        for c in range(24):
            v = shut[r][c]
            if inside(c, r):
                h = hot[r][c]
                v = h if h is not None and h >> 4 == 6 else (0x60 | min(v & 15, 6))
            row.append(v)
        merged.append(row)
    shadow = lambda v, c, r: (c == 21 and 4 <= r <= 25) or (r == 25 and 2 <= c <= 21)
    fg = x.floor_grid(merged, lambda v, c, r: v >> 4 in (0, 6), shadow, seed=5)
    x.floor_bed("tiles", fg, origin, top=pad_top, prefix="gh_floor")

    # The pit in the tiles under the machine: the open frame's hole and the dark blue below the dome.
    pit_rows = x.regions(hot, lambda v, c, r: "#" if inside(c, r) and v >> 4 in (0, 3, 7) else ".")
    pit_rows = [("".join("#" if (ch == "#" or (hot[r][c] is None and inside(c, r))) else "." for c, ch in enumerate(line)))
                for r, line in enumerate(pit_rows)]
    pits = sh.outlines(pit_rows, "#", origin, smooth=2, epsilon=0.4, min_area=1.0)
    pit_mat = pal("gh_pit", 0x01, metallic=0.1, roughness=0.8)
    for i, poly in enumerate(pits):
        k.slab(f"pit{i}", x.t.ccw(sh.inset(poly, -0.3)), pad_top - 0.2, pad_top + 0.08, pit_mat)

    # The case: a pale steel sill on the tiles, glass walls and a pale steel rim round the glass top, posts at
    # its corners.
    frame_lo = pal("gh_frame", 0x69, metallic=0.55, roughness=0.3)
    frame_hi = pal("gh_frame_top", 0x6b, metallic=0.55, roughness=0.25)
    frame_dark = pal("gh_frame_dark", 0x65, metallic=0.5, roughness=0.35)
    top = 6.6
    outer, inner = (-10.25, 9.25, -11.25, 11.25), (-9.0, 8.0, -10.0, 10.0)
    paint = lambda c, n: frame_hi if n.z > 0.7 else frame_dark if n.x > 0.5 or n.y < -0.5 else None
    w.paint_faces(x.frame_mesh("sill", outer, inner, 0.0, pad_top + 1.0, frame_lo, bevel=0.3), paint)
    w.paint_faces(x.frame_mesh("rim", outer, inner, top - 1.1, top, frame_lo, bevel=0.3), paint)
    for cx in (-9.6, 8.6):
        for cy in (-10.6, 10.6):
            w.rounded_box(f"post{cx}{cy}", (cx, cy, top / 2 + 0.15), (1.9, 1.9, top + 0.3), frame_hi, bevel=0.45, segments=1)
    walls = x.glass("gh_wall", 0x67, 0.25)
    for name, centre, size in (("wall_n", (-0.5, 10.6, top / 2), (18.0, 0.25, top - 1.0)),
                               ("wall_s", (-0.5, -10.6, top / 2), (18.0, 0.25, top - 1.0)),
                               ("wall_w", (-9.6, 0.0, top / 2), (0.25, 20.0, top - 1.0)),
                               ("wall_e", (8.6, 0.0, top / 2), (0.25, 20.0, top - 1.0))):
        k.box(name, centre, size, walls)

    # The machine: a red dome with three glowing slots, a dark blue body under it, two grey claws.
    red = pal("gh_red", 0x75, metallic=0.4, roughness=0.3)
    red_dark = pal("gh_red_dark", 0x72, metallic=0.35, roughness=0.4)
    slot_glow = pal("gh_slot", 0x7b, metallic=0.0, roughness=0.3, glow=2.0)
    slot_core = pal("gh_slot_core", 0x7d, metallic=0.0, roughness=0.3, glow=2.6)
    body = pal("gh_body", 0x32, metallic=0.4, roughness=0.4)
    grey = {s: pal(f"gh_grey{s}", s, metallic=0.55, roughness=0.32) for s in (4, 6, 8, 10)}
    cx, cy = px(11), py(10.6)
    w.rounded_box("body", (cx, py(17.5), pad_top + 1.4), (5.6, 6.5, 2.8), body, bevel=0.8)
    w.tube("neck", [(cx, py(14.5), pad_top), (cx, py(13.0), 3.4)], 2.2, body, 14)
    dome = w.sphere("dome", (cx, cy, 2.8), (4.7, 4.3, 2.9), red, 24, 12)
    w.paint_faces(dome, lambda c, n: red_dark if n.z < 0.3 else None)
    # The slots: vertical lozenges set into the dome (left, middle and right), the middle one widest.
    for sx, wd, mat in ((px(8.2), 0.8, slot_glow), (px(11.0), 1.15, slot_core), (px(13.8), 0.8, slot_glow)):
        zt = 2.8 + 2.9 * math.sqrt(max(0.0, 1 - ((sx - cx) / 4.7) ** 2)) - 0.35
        w.sphere(f"slot{sx:.1f}", (sx, cy + 0.6, zt), (wd, 2.4, 0.55), mat, 12, 6)
    # Dark ribs between the slots.
    for rx in (px(9.6), px(12.4)):
        zt = 2.8 + 2.9 * math.sqrt(max(0.0, 1 - ((rx - cx) / 4.7) ** 2)) - 0.15
        w.sphere(f"rib{rx:.1f}", (rx, cy + 0.4, zt), (0.45, 2.9, 0.5), red_dark, 10, 6)

    # The claws: a shoulder by the dome, an arm out and down, a hooked foot on the tiles.
    for side in (-1, 1):
        sx = cx + side * 5.9
        w.sphere(f"shoulder{side}", (cx + side * 4.4, py(12.2), 3.0), (1.4, 1.4, 1.2), grey[8], 10, 6)
        w.tube(f"arm{side}", [(cx + side * 4.4, py(12.2), 3.0), (sx, py(13.8), 3.4), (sx + side * 0.4, py(16.5), 2.8)],
               0.95, grey[6], 10)
        w.sphere(f"elbow{side}", (sx + side * 0.4, py(16.5), 2.8), (1.25, 1.25, 1.1), grey[10], 10, 6)
        w.tube(f"leg{side}", [(sx + side * 0.4, py(16.5), 2.8), (sx, py(19.0), 2.2), (sx - side * 0.3, py(20.6), 1.6)],
               0.85, grey[6], 10)
        w.rounded_box(f"foot{side}", (sx - side * 0.2, py(21.0), 1.6), (2.6, 1.6, 1.0), grey[4], bevel=0.35)

    # The glass pane under the frame's top, and the glint across it (the shut frame's diagonal).
    pane = x.glass("gh_glass", 0x68, 0.22)
    w.rounded_box("pane", (-0.5, 0.0, top - 0.55), (17.4, 20.4, 0.3), pane, bevel=0.1)
    glint = x.glass("gh_glint", 0x6c, 0.3, roughness=0.02)
    a, b = Vector((px(4.5), py(5.0), top - 0.36)), Vector((px(19.0), py(21.0), top - 0.36))
    d = (b - a).normalized()
    side = Vector((-d.y, d.x, 0.0)) * 1.1
    verts = [a - side, a + side, b + side * 0.6, b - side * 0.6]
    obj = k.mesh_object("glint", verts, [(0, 3, 2, 1)], glint)
    if obj.data.polygons[0].normal.z < 0:
        obj.data.flip_normals()
    x.report()


# --- C 39: the bunker with the slits ---------------------------------------------------------------------

@x.model("slit_bunker", [(39, True)])
def slit_bunker():
    """A grey block with a rounded back and chamfered back corners: a raised spine down its middle (cols 8-16)
    with two slits in it, a pale band across the spine between them, the sides falling away in tiers, and at
    its front four ribs reaching down to the floor tiles round it."""
    g = x.grid(art.BUNKER, 24)
    origin = (12, 14)
    m = {s_: pal(f"sb_grey{s_}", s_, metallic=0.3, roughness=0.45) for s_ in range(2, 13)}
    slit_dark = pal("sb_slit", 0x02, metallic=0.2, roughness=0.6)
    glow = pal("sb_glow", 0x77, metallic=0.0, roughness=0.3, glow=1.6)
    core = pal("sb_core", 0x79, metallic=0.0, roughness=0.3, glow=2.2)

    is_body = lambda v, c, r: v >> 4 == 0 and r <= 24 and 1 <= c <= 22
    shadow = lambda v, c, r: ((c >= 20 and 4 <= r <= 26) or (r >= 24 and c >= 2)) and v & 15 <= 3
    fg = x.floor_grid(g, lambda v, c, r: True, lambda v, c, r: shadow(v, c, r) or is_body(v, c, r), seed=9)
    x.floor_bed("tiles", fg, origin, top=0.35, prefix="sb_floor")

    xc = px(12)           # the spine's middle
    top = 9.4
    slits = [(py(7.0), py(4.0)), (py(13.2), py(11.0))]   # (y0, y1) of each slit, cols 9-14

    def z_of(xx, yy, e):
        z = top
        # The back: rounded over its last 3 pixels.
        if yy > 9.0:
            t = min(1.0, (yy - 9.0) / 4.2)
            z -= 3.2 * (1 - math.sqrt(max(0.0, 1 - t * t)))
        # The front: falling to the floor from row 17.
        if yy < -3.0:
            t = min(1.0, (-3.0 - yy) / 8.2)
            z -= 6.6 * t ** 1.4
        # The sides: falling away beside the spine, in tiers.
        dx = abs(xx - xc)
        if dx > 4.6:
            z -= 1.0 + 0.55 * (dx - 4.6)
        # The slits: sunk into the spine.
        for y0, y1 in slits:
            if abs(xx - xc) < 3.1 and y0 < yy < y1:
                z -= 2.2
        return 0.4 + (z - 0.4) * math.sqrt(e * (2 - e))

    polys = x.pixel_polys(g, is_body, origin, smooth=2, epsilon=0.35)
    body = x.q.heightfield("body", polys, z_of, m[7], spacing=0.45, edge=1.1)
    w.simplify_bottom(body)
    x.decimate(body, 2300)
    k.smooth(body, 35)
    shade = x.shades(g, origin, lambda v: v >> 4 == 0, blur=1)

    def paint(c, n):
        if c.z < 1.0:
            return m[3]
        for y0, y1 in slits:
            if abs(c.x - xc) < 3.0 and y0 + 0.2 < c.y < y1 - 0.2 and c.z < top - 0.6:
                return slit_dark
        s_ = shade(c.x, c.y) + 1.0
        if n.z < 0.45:
            s_ -= 1.5
        if abs(c.x - xc) < 4.6 and n.z > 0.8:
            s_ += 0.8
        return m[int(min(12, max(2, round(s_))))]
    w.paint_faces(body, paint)

    # The glow in the slits: a red bar along each slit's floor, brightest in the middle.
    for i, (y0, y1) in enumerate(slits):
        zz = top - 2.2 + 0.1
        w.rounded_box(f"slit_glow{i}", (xc, (y0 + y1) / 2 - 0.3, zz), (5.8, (y1 - y0) * 0.55, 0.6), glow, bevel=0.25)
        w.sphere(f"slit_core{i}", (xc, (y0 + y1) / 2 - 0.3, zz + 0.3), (2.0, (y1 - y0) * 0.22, 0.25), core, 12, 6)
    # The pale band across the spine between the slits.
    w.rounded_box("band", (xc, py(9.2), top + 0.15), (7.4, 2.4, 0.8), m[9], bevel=0.3)

    # The ribs at the front: four rounded toes from the spine's foot down to the floor.
    for i, col in enumerate((6.3, 10.2, 13.8, 17.6)):
        xx = px(col)
        path = [(xx, py(15.5), z_of(xx, py(15.5), 1.0) - 0.4), (xx, py(19.0), z_of(xx, py(19.0), 1.0) + 0.3),
                (xx, py(22.0), z_of(xx, py(22.0), 1.0) + 0.5), (xx, py(23.6), 0.9)]
        rib = w.tube(f"toe{i}", x.catmull(path, 0.8), 1.15, m[7], 8, squash=0.6)
        w.paint_faces(rib, lambda c, n: m[9] if n.z > 0.75 else m[5] if n.z < 0.2 else None)
    # The tiers on the sides: shallow grooves running down and out from the spine.
    for side in (-1, 1):
        for i, row in enumerate((4.5, 9.5, 14.5)):
            a = (xc + side * 4.9, py(row))
            b = (xc + side * 10.2, py(row + 2.4))
            x.q.groove(f"tier{side}{i}", [a, b], lambda xx, yy: z_of(xx, yy, 1.0), m[3], radius=0.38, sink=0.12,
                       step=1.4)
    x.report()


# --- C 49: the blue helm with the red eye ------------------------------------------------------------------

@x.model("blue_eye_helm", [(49, True)])
def blue_eye_helm():
    """A blue armoured helm: a thick curved hood over its upper left with a pale crest, the face inside it
    stepping down to a dark socket in which the red eye glows, a ribbed plate on its right with dark vents
    under it, and a base across its bottom with two pale slats and a row of vents."""
    g = x.grid(art.DOME, 24)
    origin = (12, 14)
    blue = {s_: pal(f"bh_blue{s_:x}", 0x30 | s_, metallic=0.5, roughness=0.3) for s_ in range(2, 14)}
    outline_dark = pal("bh_edge", 0x31, metallic=0.4, roughness=0.4)
    socket = pal("bh_socket", 0x01, metallic=0.2, roughness=0.5)
    eye = pal("bh_eye", 0x76, metallic=0.0, roughness=0.15, glow=1.3)
    eye_core = pal("bh_eye_core", 0x7b, metallic=0.0, roughness=0.1, glow=2.6)
    ex, ey = px(11.2), py(13.0)        # the eye's centre

    def smooth01(a, b, v):
        return sh.smoothstep(a, b, v)

    def z_of(xx, yy, e):
        r = math.hypot(xx - ex, yy - ey)
        ang = math.degrees(math.atan2(yy - ey, xx - ex)) % 360
        # The face: a shallow dish round the eye.
        z = 6.4 + 0.12 * r
        # The hood over the upper left (angles 70-250 degrees from the eye), its crest at r 8-9.5.
        rim = 8.8 + 1.7 * max(0.0, math.sin(math.radians(ang))) ** 2
        hood = smooth01(rim - 2.2, rim - 0.8, r) * smooth01(55.0, 80.0, ang) * (1.0 - smooth01(235.0, 262.0, ang))
        z += hood * 3.6
        # The plate on the right.
        plate = smooth01(px(16.0), px(17.2), xx) * smooth01(py(19.5), py(18.5), yy) * smooth01(py(1.0), py(4.5), yy)
        z = max(z, 6.2 + plate * 2.2)
        # The base across the bottom.
        base = smooth01(py(18.0), py(19.5), yy)
        z = z * (1 - base) + 5.0 * base
        if py(23.6) < yy < py(21.6) or py(20.6) < yy < py(19.6):
            z += 0.5 * base
        return 0.35 + (z - 0.35) * math.sqrt(e * (2 - e))

    polys = x.pixel_polys(g, lambda v, c, r: True, origin, smooth=2, epsilon=0.35)
    body = x.q.heightfield("body", polys, z_of, blue[6], spacing=0.4, edge=1.6)
    w.simplify_bottom(body)
    x.decimate(body, 3400)
    k.smooth(body, 40)
    shade = x.shades(g, origin, lambda v: v >> 4 == 3, blur=1)

    def paint(c, n):
        if c.z < 0.9 or n.z < -0.2:
            return outline_dark
        s_ = shade(c.x, c.y) + 0.5
        if n.z < 0.4:
            s_ -= 1.5
        return blue[int(min(13, max(2, round(s_))))]
    w.paint_faces(body, paint)

    # The socket and the eye.
    zf = z_of(ex, ey, 1.0)
    x.torus("socket_rim", (ex, ey, zf + 0.1), 3.9, 0.55, blue[4], 28, 6, squash=0.8)
    w.sphere("socket", (ex, ey, zf - 0.2), (3.6, 3.6, 0.6), socket, 20, 6)
    w.sphere("eye", (ex, ey, zf + 0.3), (3.0, 3.0, 1.9), eye, 20, 10)
    w.sphere("eye_core", (ex - 0.6, ey + 0.6, zf + 1.6), (1.3, 1.3, 0.75), eye_core, 12, 6)
    # The hood's crest: a pale rib along it.
    pts = []
    for i in range(15):
        a = math.radians(78 + (248 - 78) * i / 14)
        rr = 8.8 + 1.7 * max(0.0, math.sin(a)) ** 2
        xx, yy = ex + rr * math.cos(a), ey + rr * math.sin(a)
        pts.append((xx, yy, z_of(xx, yy, 1.0) + 0.05))
    w.tube("crest", pts, 0.6, blue[11], 8, squash=0.7)
    # The plate's ribs and the vents under it.
    for i, xx in enumerate((px(18.5), px(20.3))):
        w.rounded_box(f"plate_rib{i}", (xx, py(10.5), 8.45), (0.9, 12.0, 0.7), blue[8], bevel=0.3, segments=1)
    for i, xx in enumerate((px(17.6), px(19.0), px(20.4))):
        w.rounded_box(f"vent{i}", (xx, py(16.2), 7.8), (0.7, 2.6, 1.2), socket, bevel=0.2, segments=1)
    # The base's vents along its bottom edge.
    for i in range(6):
        xx = px(7.5 + 2.0 * i)
        w.rounded_box(f"base_vent{i}", (xx, py(26.2), 4.6), (0.8, 1.6, 1.0), socket, bevel=0.2, segments=1)
    x.report()


if __name__ == "__main__":
    x.run()
