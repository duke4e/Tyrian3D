"""Helpers for the batch AL models of wave 3 (sheet %, written x25 in models.cfg: FRUIT's hex-socketed machines and
CORAL's great domed citadel; wave3_al.py, the hex sockets, pods, glyph tiles, pillars, crystal and capsule;
wave3_al_ball.py, the geodesic ball; wave3_al_citadel.py, the citadel): the sprites' pixels (wave3_al_art.py), and
the kits of batches AE and AJ (wave3_ae_kit, wave3_aj_kit: pixel frames, painting faces by the sprite's pixel
under them, reliefs, discs, rings, limbs; stand-alone models and whole objects cut into their sprites' pieces, the
silhouette check and the build loop), with heightfield parts (wave3_q_kit), and a few of their own: the hexagonal
socket nearly every FRUIT sprite of the sheet stands in, heightfield parts painted pixel by pixel, parts leaning up
the screen from their foot (things the sprites draw standing, seen from the side and above).

Coordinates as in tyrkit: 1 unit = 1 game pixel, X right, Y up the screen, Z up (towards the camera);
the origin is the sprite's centre (or the whole object's, for objects the game draws in pieces).
Pixel (column c, row r) of an art with origin (ox, oy) covers x = c - ox .. c + 1 - ox,
y = oy - r - 1 .. oy - r.
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
import tyrkit as k  # noqa: E402,F401
import wave1_d_shapes as sh  # noqa: E402,F401
import wave3_j_kit as w  # noqa: E402,F401
import wave3_n_kit as n  # noqa: E402,F401
import wave3_q_kit as q  # noqa: E402,F401
import wave3_v_kit as v  # noqa: E402,F401
import wave3_ae_kit as ae  # noqa: E402,F401
import wave3_aj_kit as aj  # noqa: E402,F401
import wave3_al_art as art  # noqa: E402,F401
from wave3_j_kit import (pal, paint_faces, lathe_axis, hoop, catmull, sphere, rounded_box, meshes, bake,  # noqa: E402,F401
                         transform)
from wave3_v_kit import (Frame, Painter, paint_sprite, pixelate, merge_flat, relief, outlines_of,  # noqa: E402,F401
                         mirror_copies, lift, smoothstep)
from wave3_ae_kit import (displace_z, bumps, plate, limb, band_y, pipe, disc, ellipse_ring, superellipse,  # noqa: E402,F401
                          surface_z, delete_faces, join, flatten_under, bisect_mesh, rotate_z)

model = n.model
pieced = n.pieced
run = ae.run
PROTECT = ae.PROTECT
lens = ae.lens
loft_path = ae.loft_path
torus = ae.torus
piece = aj.piece
smin = aj.smin
smax = aj.smax
heightfield = q.heightfield
cone = q.cone


def frame(name, width, origin):
    """A Frame of one of wave3_al_art's pixel arts."""
    return Frame(getattr(art, name), width, origin)


# --- The hexagonal socket ----------------------------------------------------------------------------------
#
# The FRUIT sprites of the sheet stand in the same hexagonal socket: a regular hexagon 16 pixels across its
# corners (left and right) and 14 from its flat top to its flat bottom, filling the lower half of a 24 x 28
# sprite (columns 4-19, rows 14-27): centre (0, -7) in the sprite's coordinates. Its rim is drawn in two rings
# (light blue-grey outside, darker inside), lit from the upper left.

HEX_R = 8.0          # centre to the left and right corners
HEX_IN = 7.0         # centre to the flat top and bottom
_SLANT = Vector((7.0, 4.0)).normalized()   # the outward normal of the four slanted sides (right, up)
_SLANT_D = _SLANT.x * HEX_R                 # their distance from the centre


def hex_dist(x, y, cx=0.0, cy=-7.0, scale=1.0):
    """How far (x, y) lies inside the socket's hexagon (negative outside), the hexagon scaled by `scale`."""
    dx, dy = abs(x - cx), abs(y - cy)
    return min(HEX_IN * scale - dy, _SLANT_D * scale - (_SLANT.x * dx + _SLANT.y * dy))


def hex_outline(cx=0.0, cy=-7.0, scale=1.0, inset=0.0):
    """The socket's hexagon as a counter-clockwise polygon (scaled by `scale`), moved in by about `inset`."""
    return hex_points(cx, cy, scale - inset / HEX_IN, 6)


def hex_points(cx=0.0, cy=-7.0, scale=1.0, count=6):
    """The six corners (count=6) or the six sides' middles (count=-6) of the socket's hexagon."""
    if count == 6:
        return [(cx + HEX_R * scale, cy), (cx + HEX_R * scale / 2, cy + HEX_IN * scale),
                (cx - HEX_R * scale / 2, cy + HEX_IN * scale), (cx - HEX_R * scale, cy),
                (cx - HEX_R * scale / 2, cy - HEX_IN * scale), (cx + HEX_R * scale / 2, cy - HEX_IN * scale)]
    corners = hex_points(cx, cy, scale, 6)
    return [((corners[i][0] + corners[(i + 1) % 6][0]) / 2, (corners[i][1] + corners[(i + 1) % 6][1]) / 2)
            for i in range(6)]


SOCKET_H = 3.2      # the socket's rim above the ground
SOCKET_FLOOR = 2.4  # its floor inside the rim


def socket_z(x, y, cx=0.0, cy=-7.0, height=SOCKET_H, floor=SOCKET_FLOOR, rim=2.0, scale=1.0):
    """The socket's top: its outer edge rounded down over a pixel, the rim's flat top 2 pixels wide, sloping
    down inside to the floor."""
    d = hex_dist(x, y, cx, cy, scale)
    edge = math.sqrt(max(0.0, min(1.0, d / 1.1) * (2.0 - min(1.0, d / 1.1))))
    z = (height - 0.9) + 0.9 * edge
    inner = smoothstep(rim - 0.3, rim + 0.7, d)
    return z - (height - floor) * inner


def pixel_part(name, polys, z_of, f, painter, spacing=0.5, wall_steps=-2, blur=0, keep=None, default=None,
               merge=True, probe=-0.6, shade_shift=0.0, ramp_of=None):
    """A heightfield part over the polygons (top z_of(x, y), flat bottom at 0), cut along the pixel grid and
    painted by the sprite's pixels (walls `wall_steps` shades lighter, negative darker)."""
    obj = heightfield(name, polys, z_of, None, spacing=spacing, smooth_angle=40)
    pixelate(obj, f)
    paint_sprite(obj, f, painter, wall_steps=wall_steps, default=default, keep=keep, probe=probe, blur=blur,
                 shade_shift=shade_shift, ramp_of=ramp_of)
    if merge:
        merge_flat(obj)
    return k.smooth(obj, 40)


def socket_painter(prefix, extra=None, glow=None):
    """The socket's blues (ramp 3) and whatever else a sprite needs (extra: ramp -> allowed shades)."""
    shades = {3: (4, 5, 6, 7, 8, 9, 0xa, 0xb, 0xc, 0xd)}
    shades.update(extra or {})
    return Painter(prefix, shades=shades, metallic=0.35, roughness=0.35, glow=glow,
                   finish={3: (0.4, 0.32), 0: (0.6, 0.3), 6: (0.55, 0.32)})


def socket(name, f, painter, inner=None, cx=0.0, cy=-7.0, height=SOCKET_H, floor=SOCKET_FLOOR, rim=2.0, floor_keep=None,
           floor_index=0x39):
    """The hexagonal socket under a sprite: its rim and floor as one part. The rim takes the socket's blues by the
    way its faces look (its flat top, the bevel outside, the slope inside); the floor is painted pixel by pixel
    by the sprite (floor_keep(index) -> False: the floor's own blue, floor_index, there instead); inner(x, y, z)
    -> z reshapes the floor (reliefs drawn on it)."""
    def z_of(x, y):
        z = socket_z(x, y, cx, cy, height, floor, rim)
        if inner is not None and hex_dist(x, y, cx, cy) > rim + 0.2:
            z = inner(x, y, z)
        return z
    obj = heightfield(name, [hex_outline(cx, cy, inset=0.05)], z_of, None, spacing=0.5, smooth_angle=40)
    pixelate(obj, f)
    top, bevel, slope, under = painter(0x3b), painter(0x39), painter(0x37), painter(0x35)

    def pick(c, nrm):
        if nrm.z < -0.5:
            return under
        d = hex_dist(c.x, c.y, cx, cy)
        if d < 0.9:
            return top if nrm.z > 0.92 else bevel
        if d < rim + 0.45:
            return top if nrm.z > 0.97 else slope
        val = f.at(c.x, c.y)
        if val is None or (floor_keep is not None and not floor_keep(val)):
            val = floor_index
        return painter(val) if nrm.z > 0.45 else painter.shifted(val, -2)
    paint_faces(obj, pick)
    merge_flat(obj)
    return k.smooth(obj, 40)


def stroke_polys(segments, radius, origin, size=(24, 28), res=4, smooth=2, epsilon=0.3):
    """The outline of a set of strokes (segments ((x0, y0), (x1, y1)) in model coordinates, each a capsule
    `radius` wide on either side), traced from a raster `res` times finer than the pixels."""
    wd, ht = size[0] * res, size[1] * res
    ox, oy = origin
    rows = []
    for j in range(ht):
        line = []
        y = oy - (j + 0.5) / res
        for i in range(wd):
            x = (i + 0.5) / res - ox
            hit = False
            for (ax, ay), (bx, by) in segments:
                dx, dy = bx - ax, by - ay
                ll = dx * dx + dy * dy
                t = 0.0 if ll < 1e-9 else max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / ll))
                if (x - ax - t * dx) ** 2 + (y - ay - t * dy) ** 2 <= radius * radius:
                    hit = True
                    break
            line.append("#" if hit else ".")
        rows.append("".join(line))
    polys = sh.outlines(rows, "#", (ox * res, oy * res), smooth=smooth, epsilon=epsilon, min_area=1.0)
    return [[(px / res, py / res) for px, py in poly] for poly in polys]


def pixel_strokes(f, keep):
    """Strokes joining the pixels keep(index) accepts to their neighbours (diagonal neighbours only where no
    straight path joins them): (segments, the pixels' centres)."""
    cells = {(c, r) for r in range(f.height) for c in range(f.width) if f.get(c, r) is not None and keep(f.get(c, r))}
    segs = []
    for (c, r) in sorted(cells):
        p = (f.X(c), f.Y(r))
        for dc, dr in ((1, 0), (0, 1)):
            if (c + dc, r + dr) in cells:
                segs.append((p, (f.X(c + dc), f.Y(r + dr))))
        for dc, dr in ((1, 1), (-1, 1)):
            if (c + dc, r + dr) in cells and (c + dc, r) not in cells and (c, r + dr) not in cells:
                segs.append((p, (f.X(c + dc), f.Y(r + dr))))
        segs.append((p, p))
    return segs, [(f.X(c), f.Y(r)) for c, r in cells]


# --- Leaning parts -------------------------------------------------------------------------------------------

def lean_matrix(foot, angle):
    """Turns a part built standing upright on `foot` (its axis along +Z) so that it leans up the screen: its
    axis tilted towards +Y until it makes `angle` degrees with the ground."""
    fx, fy, fz = foot
    return (Matrix.Translation((fx, fy, fz)) @ Matrix.Rotation(math.radians(angle - 90.0), 4, "X") @
            Matrix.Translation((-fx, -fy, -fz)))


def lean(objects, foot, angle):
    m = lean_matrix(foot, angle)
    for obj in objects:
        sh.apply_modifiers(obj)
        obj.data.transform(m)
        k.recalc_normals(obj)
    return objects


def prism(name, sections, mat, x=0.0, y=0.0, sides=6, phase=0.0, smooth_angle=30):
    """An upright prism of `sides` sides standing at (x, y): sections [(z, radius)] from its foot up (a radius of
    0 closes it to a point); the corners turned by `phase` degrees."""
    rings = []
    for z, r in sections:
        rr = max(r, 1e-3)
        rings.append([Vector((x + rr * math.cos(math.radians(phase) + 2 * math.pi * i / sides),
                              y + rr * math.sin(math.radians(phase) + 2 * math.pi * i / sides), z))
                      for i in range(sides)])
    start = (x, y, sections[0][0])
    end = (x, y, sections[-1][0])
    obj = k.loft(name, rings, mat, start_point=start, end_point=end)
    return k.smooth(obj, smooth_angle)


def glossy(prefix, index, alpha=None, metallic=0.1, roughness=0.08, glow=None):
    """A smooth (glass, ice, lens) palette material."""
    m = pal(f"{prefix}_{index:02x}", index, metallic=metallic, roughness=roughness, glow=glow)
    if alpha is not None:
        bsdf = m.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Alpha"].default_value = alpha
        m.surface_render_method = "BLENDED"
    return m


def scale_about(objects, s, pivot):
    m = Matrix.Translation(Vector(pivot)) @ Matrix.Scale(s, 4) @ Matrix.Translation(-Vector(pivot))
    for obj in objects:
        sh.apply_modifiers(obj)
        obj.data.transform(m)
    return objects


def clip_below(obj, z0=0.0):
    """Cuts away what lies below z0 (closing the cut)."""
    return sh.flat_bottom([obj], z0)


def cut_plane(obj, point, normal):
    """Cuts away what lies on the side of a plane its normal points to, closing the cut."""
    return sh.cut_planes([obj], [(tuple(point), tuple(normal))])
