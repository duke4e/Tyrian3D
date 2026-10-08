"""Batch AC of wave 3 (sheet 7: CAMANIS and ICESECRET), the stand-alone models, modelled as their sprites look
(models.cfg: yaw=0). The objects the game draws in pieces (the bunker, the sphere on its legs, the red dome
with its arm) are in wave3_ac_ice.py; the kit is wave3_ac_kit.py, the pixels wave3_ac_art.py.

- ice_vent (7 55): the crater in the ice plateau with a red-hot orb in it: a round mound of ice about 20
  pixels across round the orb, whose relief follows the sprite's shades, a lip round the pit, light ridges
  running down from it with dark cracks between them, its edge falling away to the plateau (about 7 pixels high
  with the orb); the orb glows, a yellow-white core breaking through it up and to the left (its frames 93, 131
  make it flare when it fires). The plateau the sprite draws round it out to its edges is the map's ice (the
  3D ground shows it): the mound ends well inside them. Drawn at its own origin (its foot on the ground
  layer).
- cross_beacon (7 13): the grey frame flying in CAMANIS: two dark crossbars with vents, joined by two grey bows
  that bend in towards the middle where they turn blue, a blue crystal pinched at its waist between them, a red
  beacon on each crossbar's outer edge (its frames 15, 17 light the beacons up: they glow).

usage: Blender -b --factory-startup -P wave3_ac.py -- [--only name,name] [--preview <prefix>] [--check 1]
       [--stats 1]
"""
import math
import os
import sys

import bmesh
import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ac_kit as a  # noqa: E402
from wave3_ac_kit import k, pal, sphere, smoothstep  # noqa: E402


# --- 7 55: the ice vent ------------------------------------------------------------------------------

VENT = a.frame("CRATER", 24, (12, 14))
ORB = (0.0, 3.0)        # the orb's centre (x, y): the sprite's pixels 7-16 across, rows 7-14
ORB_R = 4.7


def pixel_relief(name, fr, keep, z_of, paint, step=1.0):
    """A heightfield on the pixel grid (cells `step` pixels wide) over the pixels keep(column, row) accepts:
    each cell's corners at z_of(x, y), each cell painted paint(column, row) (a material); its outer edges
    turned down to z = 0 (no bottom: the camera looks down on it)."""
    bm = bmesh.new()
    verts = {}
    mats, index = [], {}

    def vert(x, y):
        key = (round(x, 4), round(y, 4))
        if key not in verts:
            verts[key] = bm.verts.new((x, y, z_of(x, y)))
        return verts[key]
    count = int(round(1 / step))
    for r in range(len(fr.g)):
        for c in range(fr.width):
            if not keep(c, r):
                continue
            m = paint(c, r)
            if m.name not in index:
                index[m.name] = len(mats)
                mats.append(m)
            for i in range(count):
                for j in range(count):
                    x0 = fr.left(c) + i * step
                    y0 = fr.bottom(r) + j * step
                    face = bm.faces.new((vert(x0, y0), vert(x0 + step, y0), vert(x0 + step, y0 + step),
                                         vert(x0, y0 + step)))
                    face.material_index = index[m.name]
    border = [e for e in bm.edges if len(e.link_faces) == 1]
    if border:
        made = bmesh.ops.extrude_edge_only(bm, edges=border)
        for v in made["geom"]:
            if isinstance(v, bmesh.types.BMVert):
                v.co.z = 0.0
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.normal_update()
    if sum(f.normal.z * f.calc_area() for f in bm.faces) < 0:
        bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    for m in mats:
        obj.data.materials.append(m)
    return k.smooth(obj, 50)


@a.model("ice_vent", lambda: VENT.mask(), size=(24, 28))
def ice_vent():
    """The mound of ice round the orb (not the plateau round it: that is the map's ice): the ground's level
    at its round edge, rising to the lip round the pit (about 4 pixels high); the light ridges stand out and the
    dark cracks sink in, as the sprite shades them. The orb sits in the pit, half sunk."""
    ice = a.Painter("vent_ice", shades={3: (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14)}, metallic=0.05,
                    roughness=0.32)
    shade = VENT.shade(3, blur=1)
    broad = VENT.shade(3, blur=3)
    ox, oy = ORB
    outline_rx, outline_ry = 10.0, 10.5   # the mound's round outline, centred on the orb

    def inside(x, y):
        """How far inside the mound's outline (0 at it, about the distance in pixels)."""
        rr = math.hypot((x - ox) / outline_rx, (y - oy) / outline_ry)
        return (1.0 - rr) * min(outline_rx, outline_ry)

    def z_of(x, y):
        d = math.hypot((x - ox) / 1.0, (y - oy) / 0.85)
        fade = smoothstep(0.0, 4.5, inside(x, y))
        # The mound: highest at the lip, the ridges running down the screen from it.
        lip = 3.6 * math.exp(-((d - ORB_R - 0.6) / 2.2) ** 2)
        mound = 1.6 * smoothstep(13.0, 4.0, d) + lip
        relief = 0.55 * (broad(x, y) - 9.0) + 0.22 * (shade(x, y) - broad(x, y))
        pit = d < ORB_R + 0.2
        z = 0.35 + mound + relief * (0.4 if pit else 1.0)
        if pit:
            z = min(z, 0.9 + 3.0 * smoothstep(ORB_R - 1.6, ORB_R + 0.2, d))
        return max(0.08, 0.08 + (z - 0.08) * fade)

    def keep(c, r):
        return inside(VENT.X(c), VENT.Y(r)) > -0.35

    def paint(c, r):
        v = VENT.g[r][c]
        if a.is_ice(v):
            # The pixel's shade, a little smoothed (less pixel noise on the relief).
            x, y = VENT.X(c), VENT.Y(r)
            return ice(0x30 + max(1, min(14, int(round(0.6 * (v & 15) + 0.4 * shade(x, y))))))
        d = math.hypot(VENT.X(c) - ox, (VENT.Y(r) - oy) / 0.85)
        return ice(0x33 if d < ORB_R - 0.5 else 0x3d)
    pixel_relief("vent_mound", VENT, keep, z_of, paint)

    # The orb: red-hot, its glow brightest up and to the left (as the sprite lights it): a red ball, an orange
    # swell and a yellow-white core breaking through its surface there.
    red = pal("vent_orb", 0x76, metallic=0.0, roughness=0.3, glow=1.3)
    orange = pal("vent_orb_hot", 0x7a, metallic=0.0, roughness=0.25, glow=2.2)
    core = pal("vent_orb_core", 0x7e, metallic=0.0, roughness=0.2, glow=3.0)
    sphere("vent_orb", (ox, oy, 2.9), (ORB_R, ORB_R * 0.9, ORB_R * 0.85), red, 28, 14)
    sphere("vent_orb_swell", (ox - 0.6, oy + 0.4, 4.3), (3.2, 2.9, 3.0), orange, 20, 10)
    sphere("vent_orb_core", (ox - 0.8, oy + 0.6, 5.3), (1.8, 1.6, 2.2), core, 16, 8)


# --- 7 13: the cross beacon -------------------------------------------------------------------------

XF = a.frame("XFRAME", 24, (12, 14))
XAX = -0.5   # the sprite's axis (column 11); it is symmetric about y = 0 too


@a.model("cross_beacon", lambda: XF.mask(), size=(24, 28))
def cross_beacon():
    """Two dark crossbars (top and bottom) with vents and a red beacon on their outer edge, joined by two grey
    bows that bend in towards the middle, where they turn blue; between them a blue crystal pinched at its
    waist, held by two grey stubs. About 6 pixels high."""
    steel = pal("xb_steel", 8, metallic=0.65, roughness=0.3)
    light = pal("xb_light", 10, metallic=0.65, roughness=0.25)
    dark = pal("xb_dark", 3, metallic=0.55, roughness=0.4)
    darker = pal("xb_darker", 1, metallic=0.3, roughness=0.6)
    blue = pal("xb_blue", 0x38, metallic=0.4, roughness=0.25)
    blue_light = pal("xb_blue_light", 0x3c, metallic=0.4, roughness=0.2)
    crystal = pal("xb_crystal", 0x37, metallic=0.2, roughness=0.08, glow=0.3, emission=(60, 120, 180))
    streak = pal("xb_streak", 0x3e, metallic=0.1, roughness=0.1, glow=0.8, emission=(170, 210, 235))
    red = pal("xb_red", 0x76, roughness=0.2, glow=2.5, emission=(255, 60, 20))
    hot = pal("xb_hot", 0x7c, roughness=0.2, glow=4.0, emission=(255, 210, 90))
    for sy in (1, -1):
        def Y(v):
            return v * sy
        # The crossbar: a dark block with a lighter top, vent slots across it.
        bar = a.block(f"bar{sy}", (XAX, Y(8.9)), 5.9, 2.6, 3.6, dark, rounding=0.9, power=5.0, segments=28)
        a.paint_faces(bar, lambda c, nrm: steel if nrm.z > 0.75 else None)
        for i, dx in enumerate((-3.0, -1.0, 1.0, 3.0)):
            a.rounded_box(f"vent{sy}_{i}", (XAX + dx, Y(8.4), 3.65), (0.8, 1.9, 0.5), darker, bevel=0.2, segments=1)
        a.rounded_box(f"lip{sy}", (XAX, Y(6.7), 2.6), (9.0, 0.9, 1.6), darker, bevel=0.3, segments=1)
        # The beacon on its outer edge.
        sphere(f"beacon{sy}", (XAX, Y(10.9), 3.4), (2.0, 1.6, 1.6), red, 16, 8)
        sphere(f"beacon_core{sy}", (XAX, Y(11.2), 4.4), (0.9, 0.7, 0.8), hot, 10, 5)
        # The core's stubs: grey studs from the bows to the crystal.
    for sx in (-1, 1):
        def X(v):
            return XAX + sx * v
        # The bow: from the top crossbar's end out, down the side, in towards the middle and back.
        path = [(X(5.2), 9.4, 2.3), (X(7.5), 9.6, 2.5), (X(8.8), 8.5, 2.5), (X(9.1), 6.5, 2.4), (X(9.0), 4.5, 2.4),
                (X(8.3), 2.8, 2.5), (X(7.1), 1.2, 2.6), (X(6.6), 0.0, 2.7)]
        path = path + [(xx, -yy, zz) for xx, yy, zz in reversed(path[:-1])]
        pts = a.catmull(path, 0.8)
        radii = [1.15 + 0.3 * smoothstep(4.5, 1.5, abs(p.y)) for p in pts]
        bow = a.tube(f"bow{sx}", pts, radii, steel, 9)
        a.paint_faces(bow, lambda c, nrm: (blue_light if nrm.z > 0.5 else blue) if abs(c.y) < 3.6 else
                      light if nrm.z > 0.6 else None)
        # The stub between the bow and the crystal.
        a.rounded_box(f"stub{sx}", (X(4.6), 0.0, 2.6), (3.4, 3.4, 1.6), steel, bevel=0.5)
        a.rounded_box(f"stub_cap{sx}", (X(4.4), 0.0, 3.4), (1.0, 1.4, 0.4), light, bevel=0.2)
    # The crystal: a faceted blue gem along y, pinched at its waist, a light streak down its middle.
    half = [(6.7, 0.6), (5.8, 1.9), (4.6, 2.6), (3.5, 3.9), (2.5, 3.9), (1.5, 2.8), (0.5, 2.0)]
    keys = [(-yy, hw) for yy, hw in half] + [(0.0, 1.9)] + [(yy, hw) for yy, hw in reversed(half)]
    secs = [(yy, XAX, 3.0, hw, 0.5 + 0.75 * hw, 0.4 + 0.5 * hw) for yy, hw in keys]
    gem = a.loft_y("crystal", a.smooth_sections(secs, 0.5), crystal, segments=8, power=1.4, smooth_angle=25)
    a.paint_faces(gem, lambda c, nrm: blue if nrm.z < 0.2 else None)
    # The streak follows the gem's ridge (its sections' tops).
    ridge = [(XAX, yy, 3.0 + 0.5 + 0.75 * hw - 0.12) for yy, hw in keys[1:-1]]
    a.tube("streak", a.catmull(ridge, 0.7), 0.32, streak, 8)
    # The dark frame round the crystal (the sprite's rows 7 and 20).
    for sy in (1, -1):
        a.rounded_box(f"frame{sy}", (XAX, sy * 6.4, 1.6), (9.2, 1.2, 1.4), darker, bevel=0.3, segments=1)


if __name__ == "__main__":
    a.run()
