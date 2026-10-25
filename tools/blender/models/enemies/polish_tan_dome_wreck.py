"""MINERS's tan creature's wreck (sheet L sprites 199 and 201's stand-ins: what MINERS's map paints in the tiles under
the creature's lower half, its broken shell and its arms, where tan_dome_bl and tan_dome_br stand once destroyed and
before they come; 6 of each), built on polish_tan_dome.py (2026-10-25, the clean ground's stage 4). The upper pieces
stand in as their own looks (L 161 as tan_dome_tl_damaged, the crumbs of the shell's rim at its bottom edge; L 163 has
nothing painted).

As the map paints it at 4x (MINERS 8362fe151f78556b at 612 and 636, 4046): the creature's head and the top of its
torso gone, its torso left as a broken shell standing on the rock (columns 13-34 of the picture's rows 28-48), its rim
jagged (highest at the upper left, a deep notch at the right down to row 37), the hollow inside it dark brown, the
shell's grey-tan lit down its left and middle as the live body's, its broken edge catching the light; both arms still
standing as hooks from the shell's top corners down to their paws on the rock (columns 3-10 and 38-45 of rows 28-47),
their shoulders broken off short where they met the body.

Built as the live creature (polish_tan_dome.py's signed distance field on its grid: the leaning body of revolution,
the arms, the paws, its noise and relief, the surface nets, the shear to the camera, its colours from the picture's own
shades), broken: the body hollowed into a cup (its wall WALL thick, solid under FLOOR_Z), its head and the top of its
torso gone (beyond TOP_T along its axis, and above a jagged rim, RIM: a height per x, higher at the left, notched at
the right, so the camera looks down into the hollow), the arms clipped where they ran into the body and their
shoulders gone (their tops hooks under the pieces' cut); the faces of the hollow painted dark and dull (0xa0), the broken edge light
(0xa9); the nub and its collar gone with the head. Cut along the live pieces' planes (x = 0 and y + tan 20 z = 0) and
decimated as the live pieces (polish_tan_dome.pieces_of); only the lower pieces are exported (the upper ones hold
nothing of the wreck).

Coordinates as polish_tan_dome.py's (the whole's origin the corner where the four sprites meet). models.cfg:
model tan_dome_bl_wreck enemies/tan_dome_bl_wreck.glb origin, model tan_dome_br_wreck enemies/tan_dome_br_wreck.glb
origin; wreck l 199 tan_dome_bl_wreck, wreck l 201 tan_dome_br_wreck (drawn with the live sprite lines' options, yaw=0
height=-4, at the live pieces' places).

Options after "--": --outdir <dir> (default assets/models/enemies), --preview <prefix>, --whole <prefix>.
"""
import math
import os
import sys
import time

import bmesh
import bpy
import numpy as np
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_tan_dome as live  # noqa: E402
from polish_rock_arch import surface_nets, finish_whole, mesh_object, noise3, smax, face_data, assign  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_rock_column import drop_islands, shear_to_camera, TILT  # noqa: E402

WALL = 1.25                     # the shell's thickness
FLOOR_Z = 2.6                   # the hollow's floor (the shell is a cup: solid under it)
# The rim: the height the shell still reaches, by x (the picture's plane; the camera looks down into the hollow over
# it), and its jag; the head and the top of the torso gone beyond TOP_T along the axis.
RIM = [(-11.0, 13.6), (-8.0, 13.4), (-5.0, 12.6), (-2.0, 12.3), (0.6, 12.0), (2.4, 10.2), (3.6, 9.4), (4.8, 9.8),
       (6.4, 11.6), (8.6, 12.8), (11.0, 13.2)]
RIM_JAG = (0.6, 1.0)            # its noise's amplitude and scale
TOP_T = 16.2
# The arms without their shoulders (their tops a hook a little under the pieces' cut, where they met the shell).
ARM = [(-11.4, -3.2, 6.6, 2.3), (-14.6, -3.6, 6.6, 2.6), (-16.9, -6.4, 5.4, 2.8)] + live.ARM[4:]
DARK, EDGE = 0xa0, 0xa9
SPECS = [("tan_dome_bl_wreck", 199, live.PIECES[2][2], live.PIECES[2][3]),
         ("tan_dome_br_wreck", 201, live.PIECES[3][2], live.PIECES[3][3])]


def rim_z(x):
    """The height the shell reaches at x (jagged)."""
    xs = np.array([p[0] for p in RIM])
    ts = np.array([p[1] for p in RIM])
    amp, scale = RIM_JAG
    x = np.asarray(x, dtype=np.float64)
    t = np.interp(x, xs, ts)
    return t + amp * noise3(x / scale, np.zeros_like(x) + 0.37, np.zeros_like(x) + 1.3, 91)


def top_t(x):
    """How far along the axis the shell reaches at x (its back broken off there, jagged)."""
    x = np.asarray(x, dtype=np.float64)
    return TOP_T + 0.8 * noise3(x / 1.3, np.zeros_like(x) + 2.1, np.zeros_like(x) + 0.4, 93)


def axis_coords(gx, gy, gz):
    """(t along the axis from the foot ring, u across) of points in the picture's plane."""
    dy = gy - live.Y_FOOT
    return dy * live.SA + gz * live.CA, gx - live.X_AXIS


def arms(gx, gy, gz):
    """live.arms() with the shoulders' first lengths gone."""
    saved = live.ARM
    live.ARM = ARM
    try:
        return live.arms(gx, gy, gz)
    finally:
        live.ARM = saved


def solid(fl):
    """live.solid(): the body hollowed and broken off above the rim, the arms clipped by it."""
    t0 = time.time()
    gx = live.XS[:, None, None]
    gy = live.YS[None, :, None]
    gz = live.ZS[None, None, :].astype(np.float64)
    body = live.body_sdf(gx, gy, gz)
    t, _ = axis_coords(gx, gy, gz)
    rim = np.maximum(gz - rim_z(live.XS)[:, None, None], t - top_t(live.XS)[:, None, None])
    cavity = np.maximum(body + WALL, FLOOR_Z - gz)
    shell = np.maximum(np.maximum(body, -cavity), rim)
    limbs = np.maximum(arms(gx, gy, gz), -body)
    d = -smax(-shell, -limbs, 0.9)
    d = d.astype(np.float32)
    d -= (live.RELIEF * fl["relief"][:, :, None]).astype(np.float32)
    i, j, kz = np.nonzero(np.abs(d) < 2.0)
    x, y, zz = live.XS[i], live.YS[j], live.ZS[kz]
    detail = np.zeros(len(i))
    for n, (amp, scale) in enumerate(live.NOISE):
        detail += amp * noise3(x / scale, y / scale, zz / scale, 61 + n)
    d[i, j, kz] += detail.astype(np.float32)
    d = np.maximum(d, np.float32(-live.SKIRT) - live.ZS[None, None, :].astype(np.float32))
    for axis in range(3):
        p = np.pad(d, [(1, 1) if ax == axis else (0, 0) for ax in range(3)], mode="edge")
        d = 0.25 * np.take(p, range(0, d.shape[axis]), axis=axis) + 0.5 * d + \
            0.25 * np.take(p, range(2, d.shape[axis] + 2), axis=axis)
    print("wreck solid: %.1f s" % (time.time() - t0))
    return d.astype(np.float32)


LIVE_SHADES = live.shades


def shades(centres, normals, fl):
    """live.shades(), the hollow's faces dark and the broken edge light."""
    s = LIVE_SHADES(centres, normals, fl)
    x, y, z = centres[:, 0], centres[:, 1] + TILT * centres[:, 2], centres[:, 2]   # (back in the picture's plane)
    body = live.body_sdf(x, y, z)
    t, _ = axis_coords(x, y, z)
    rim = np.maximum(z - rim_z(x), t - top_t(x))
    arm = arms(x, y, z)
    edge = (np.abs(rim) < 0.45) & (body > -WALL - 0.4) & (arm > 0.3)
    hollow = (body < -0.5 * WALL) & ~edge & (arm > 0.3) & (z > FLOOR_Z - 0.4)
    s = np.where(hollow, DARK, s)
    return np.where(edge, EDGE, s)


def whole_body(fl, m):
    d = solid(fl)
    verts, quads = surface_nets(d, (live.X0, live.Y0, live.Z0), live.H)
    quads = drop_islands(verts, quads)
    whole = finish_whole(mesh_object("tan_dome_wreck", verts, quads))
    bm = bmesh.new()
    bm.from_mesh(whole.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    bm.to_mesh(whole.data)
    bm.free()
    shear_to_camera(whole)
    whole.data.update()
    centres, normals = face_data(whole)
    assign(whole, shades(centres, normals, fl), m)
    return whole


def build():
    options = k.args()
    out = mk.outdir(options)
    k.reset()
    bpy.context.scene.view_settings.view_transform = "Standard"
    m = live.materials()
    m[DARK] = k.material("tan_dome_hollow", palette=DARK, metallic=0.0, roughness=0.95)   # (dull: no sheen of the sky)
    fl = live.paint_fields()
    whole = whole_body(fl, m)
    print("whole wreck: %d triangles" % len(whole.data.polygons))
    if "whole" in options:
        view = whole.copy()
        view.data = whole.data.copy()
        bpy.context.scene.collection.objects.link(view)
        triangulate([view])
        mk.export([view], options["whole"] + "tan_dome_wreck.glb")
        bpy.data.objects.remove(view)
    # The pieces as the live ones (decimated, shaded as the whole, coloured by shades() above).
    live.shades = shades
    try:
        live.pieces_of(whole, [], SPECS, m, options, out, fl, False)
    finally:
        live.shades = LIVE_SHADES


if __name__ == "__main__":
    build()
