"""Enemies of wave 3, batch Z, continued (sheet L): the small creatures of SQUADRON and TIME WAR and two of MINERS's
flyers, modelled as their sprites look (models.cfg: yaw=0). The kit is wave3_z_kit.py, the pixels wave3_z_art.py.

- fire_spike_ball (L 116): the spiked ball of fire that marches with SQUADRON's rows and drifts down TIME WAR
  (beside the lava ball L 115, molten_rock, and the dark ember L 118, dark_ember): a glowing core, hotter
  towards its upper left, four spikes out to the sprite's edges and four short ones between them.
- squad_eyeball (L 117): the white eyeball of the same rows, its blue iris looking down the screen and up.
- squad_bolt (L 134): SQUADRON's small grey bolt lying on the ground along the screen, a round head at the top,
  a red band round its body.
- red_mouth_lander (L 229): MINERS's grey lander (in the sky; one stands in SQUADRON): an armoured shell with
  a slatted face over a red mouth, a red glowing jet under it and two legs reaching down the screen.
- yellow_pod_fighter (L 267): MINERS's grey fighter, nose down the screen: a slim fuselage with a gun in
  front and a cream engine glow behind, and two pointed wing pods with yellow lights on their outer sides.

usage: Blender -b --factory-startup -P wave3_z_small.py -- [--only name,name] [--preview <prefix>] [--check 1]
       [--stats 1]
"""
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_z_kit as kit  # noqa: E402
import wave2_h_kit as hk  # noqa: E402
from wave3_z_kit import k, sh, w, pal, smoothstep  # noqa: E402

SPIKY = kit.frame("SPIKY", 12, (6, 7))
EYE = kit.frame("EYE", 12, (6, 7))
PIN = kit.frame("PIN", 12, (6, 7))
MECH = kit.frame("MECH", 24, (12, 14))
SHIP = kit.frame("SHIP", 24, (12, 14))


def sphere_mesh(name, centre, radii, subdivisions=4):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdivisions, radius=1.0)
    for v in bm.verts:
        v.co = Vector(centre) + Vector((v.co.x * radii[0], v.co.y * radii[1], v.co.z * radii[2]))
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


# --- L 116: the spiked fire ball -------------------------------------------------------------------

@kit.model("fire_spike_ball", mask=lambda: SPIKY.mask(), size=(12, 14))
def fire_spike_ball():
    f = SPIKY
    crust = pal("spike_crust", 0x72, metallic=0.0, roughness=0.55, glow=0.25)
    red = pal("spike_red", 0x75, metallic=0.0, roughness=0.45, glow=0.45)
    warm = pal("spike_warm", 0x78, metallic=0.0, roughness=0.4, glow=0.9)
    hot = pal("spike_hot", 0x7b, metallic=0.0, roughness=0.4, glow=1.5)
    white = pal("spike_white", 0x7d, metallic=0.0, roughness=0.4, glow=2.2)
    cx, cy = f.X(5.0), f.Y(7.0)
    centre = Vector((cx, cy, 4.6))
    core = sphere_mesh("core", centre, (4.6, 4.6, 4.2), 4)
    rng = random.Random(116)
    waves = [(Vector([rng.uniform(-1, 1) for _ in range(3)]).normalized() * rng.uniform(1.0, 2.2), rng.uniform(0, 6.3))
             for _ in range(9)]
    hot_dir = Vector((-0.45, 0.35, 0.82)).normalized()  # the sprite's bright spot, upper left
    values = []
    for v in core.data.vertices:
        n_ = (v.co - centre).normalized()
        flame = sum(math.sin(wv.dot(n_) * 2.2 + ph) for wv, ph in waves) / 3.0
        v.co = centre + (v.co - centre) * (1.0 + 0.05 * flame)
        values.append(1.25 * max(0.0, n_.dot(hot_dir)) ** 10 + 0.3 * flame + 0.1 * n_.z)
    hk.band_split(core, values, [(-9, crust), (-0.05, red), (0.42, warm), (0.9, hot), (1.18, white)], smooth_angle=70)
    # The spikes: four out to the sprite's edges (rows 0 and 13, columns 0 and 10), four short ones between.
    spikes = [((0, 1), 7.0 - cy - 0.1, 1.7), ((0, -1), cy + 7.0 - 0.1, 1.7), ((-1, 0), cx + 6.0 - 0.1, 1.6),
              ((1, 0), 5.0 - cx - 0.1, 1.6)]
    for i, ((dx, dy), reach, base) in enumerate(spikes):
        d = Vector((dx, dy, 0.08)).normalized()
        start = centre + d * 3.2
        kit.cone(f"spike{i}", tuple(start), tuple(d), reach - 3.2, base, red, segments=12)
    for i, (dx, dy) in enumerate(((-1, 1), (1, 1), (-1, -1), (1, -1))):
        d = Vector((dx, dy, 0.35)).normalized()
        kit.cone(f"nub{i}", tuple(centre + d * 3.8), tuple(d), 2.5, 1.4, crust, segments=10)
    sh.flat_bottom(w.meshes(), 0.0)


# --- L 117: the eyeball ----------------------------------------------------------------------------

@kit.model("squad_eyeball", mask=lambda: EYE.mask(), size=(12, 14))
def squad_eyeball():
    f = EYE
    pupil = pal("eyeball_pupil", 0x31, metallic=0.0, roughness=0.08)
    iris = pal("eyeball_iris", 0x37, metallic=0.1, roughness=0.15)
    ring = pal("eyeball_ring", 0x33, metallic=0.0, roughness=0.25)
    white = pal("eyeball_white", 0x0c, metallic=0.05, roughness=0.15)
    shade = pal("eyeball_shade", 0x09, metallic=0.05, roughness=0.3)
    radius = 5.45
    centre = Vector((f.X(6.0), f.Y(7.0), radius))
    look = Vector((0.0, -math.sin(math.radians(38)), math.cos(math.radians(38))))
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=40, v_segments=24, radius=1.0)
    values = []
    for v in bm.verts:
        n_ = v.co.normalized()
        angle = math.degrees(n_.angle(look))
        bulge = 0.06 * (1 - smoothstep(0, 32, angle)) - 0.03 * (1 - smoothstep(5, 10, angle))
        v.co = centre + n_ * radius * (1 + bulge)
        value = -angle
        if angle >= 31 and n_.z < -0.15:  # the white's underside, in shade
            value = -200.0
        values.append(value)
    mesh = bpy.data.meshes.new("eyeball")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("eyeball", mesh)
    bpy.context.scene.collection.objects.link(obj)
    hk.band_split(obj, values, [(-999, shade), (-150, white), (-31, ring), (-27, iris), (-9, pupil)], smooth_angle=80)
    sh.flat_bottom([obj], 0.0)


# --- L 134: the bolt -------------------------------------------------------------------------------

@kit.model("squad_bolt", mask=lambda: PIN.mask(), size=(12, 14))
def squad_bolt():
    f = PIN
    grey = pal("bolt_grey", 0x09, metallic=0.7, roughness=0.25)
    grey_dark = pal("bolt_grey_dark", 0x05, metallic=0.6, roughness=0.35)
    grey_lit = pal("bolt_grey_lit", 0x0c, metallic=0.7, roughness=0.2)
    red = pal("bolt_red", 0x74, metallic=0.4, roughness=0.3)
    x = f.X(5.5)
    axis_z = 3.0
    top = f.top(0)
    # Along -y from the sprite's top: the head (rows 0-2), the neck (3-4), the collar (5-6), the body
    # (7-10) with the red band (row 8), the tail (11-12).
    profile = [(0.0, 1.6), (0.15, 2.6), (0.6, 3.0), (2.6, 3.0), (3.0, 2.3), (3.7, 1.4), (4.9, 1.05), (5.2, 1.6),
               (5.5, 2.05), (6.6, 2.05), (7.0, 2.6), (7.4, 3.0), (11.0, 3.0), (11.6, 2.4), (12.4, 1.4), (12.95, 0.4),
               (13.0, 0.01)]
    body = w.lathe_axis("bolt", profile, grey, (x, top, axis_z), (0, -1, 0), 24, smooth_angle=40)
    kit.paint_faces(body, lambda c, nrm: grey_lit if nrm.z > 0.75 and nrm.x < 0.2 else grey_dark if nrm.z < 0.0
                    else None)
    w.lathe_axis("band", [(8.0, 3.0), (8.1, 3.25), (8.9, 3.25), (9.0, 3.0)], red, (x, top, axis_z), (0, -1, 0), 24)
    w.lathe_axis("head_cap", [(0.0, 0.01), (0.05, 1.7), (0.2, 1.9)], grey_dark, (x, top, axis_z), (0, -1, 0), 20)
    sh.flat_bottom(w.meshes(), 0.0)


# --- L 229: the lander -----------------------------------------------------------------------------

@kit.model("red_mouth_lander", mask=lambda: MECH.mask())
def red_mouth_lander():
    f = MECH
    X, Y = f.X, f.Y
    paint = kit.Painter("lander", shades={0: (3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13)}, metallic=0.35, roughness=0.35,
                        remap={0x01: 0x03, 0x02: 0x03})
    dark = pal("lander_dark", 0x02, metallic=0.4, roughness=0.5)
    slat = pal("lander_slat", 0x0b, metallic=0.6, roughness=0.3)
    red = pal("lander_red", 0x74, metallic=0.2, roughness=0.35, glow=0.4)
    jet = pal("lander_jet", 0x79, metallic=0.0, roughness=0.4, glow=1.4)
    jet_hot = pal("lander_jet_hot", 0x7c, metallic=0.0, roughness=0.4, glow=2.2)
    leg = pal("lander_leg", 0x07, metallic=0.6, roughness=0.3)
    leg_lit = pal("lander_leg_lit", 0x0b, metallic=0.6, roughness=0.3)
    # The shell: rows 1-17, a dome highest towards its back (up the screen), its face sloping down to the
    # mouth; painted by the sprite (its seams and panels).
    shell_f = kit.frame("MECH", 24, (12, 14)).fill({0x01, 0x02}, edge_only=True)
    polys = kit.polys_of(f, lambda v, c, r: r <= 17 and not (r >= 13 and 9 <= c <= 15 and v >> 4 == 7), smooth=2,
                         epsilon=0.3)
    yc = Y(6.5)

    def shell_z(x, y, e):
        back = smoothstep(Y(17.5), Y(5.0), y)
        return 3.2 + e * (5.5 + 4.0 * back) - 0.02 * x * x * (1 - back)
    shell = kit.heightfield("shell", polys, shell_z, None, spacing=0.5, smooth_angle=45, edge=4.5)
    kit.pixelate(shell, shell_f)
    kit.paint_sprite(shell, shell_f, paint, wall_steps=2, under=dark, blur=1)
    kit.merge_flat(shell)
    shell.data.validate()
    # The face's slats (rows 9-14, columns 9-15: light and dark stripes) as raised bars.
    for c in (9.5, 11.5, 13.5):
        kit.rounded_box(f"slat{c}", (X(c) + 0.5, Y(11.0), 9.4), (0.9, 6.0, 1.0), slat, bevel=0.3)
    # The mouth: a red glowing hollow under the face (rows 13-15), its lip a dark ridge.
    w.sphere("mouth", (X(12.0), Y(14.0), 4.6), (3.8, 1.8, 1.6), red, 18, 9)
    # The jet under the body (rows 16-24): a dark cowl down the screen with a red cone in it, pointing down
    # the screen and glowing at its end.
    kit.rounded_box("jet_cowl", (X(12.0), Y(19.6), 1.9), (6.6, 8.0, 3.4), leg, bevel=1.2)
    w.lathe_axis("jet", [(0.0, 2.4), (2.4, 2.4), (3.8, 2.0), (4.8, 1.3), (5.3, 0.01)], jet, (X(12.0), Y(17.0), 4.0),
                 (0, -1, 0.1), 18)
    w.sphere("jet_core", (X(12.0), Y(21.6), 4.4), (1.2, 1.1, 1.0), jet_hot, 12, 6)
    # The legs: from under the shell's lower corners down the screen to feet at the sprite's bottom
    # corners (columns 0-5 and 18-23, rows 17-27), bent at the knee.
    for side, (hip_c, knee_c, foot_c) in (("l", (4.5, 3.0, 1.6)), ("r", (19.5, 21.0, 22.4))):
        hip = Vector((X(hip_c), Y(15.5), 5.0))
        knee = Vector((X(knee_c), Y(20.0), 6.2))
        foot = Vector((X(foot_c), Y(25.6), 1.0))
        w.tube(f"thigh_{side}", w.catmull([hip, knee], 0.5), 1.7, leg_lit, 14)
        w.tube(f"shin_{side}", w.catmull([knee, (knee + foot) / 2 + Vector((0, 0.3, 0.5)), foot], 0.5), 1.45, leg, 14)
        w.sphere(f"knee_{side}", tuple(knee), (2.0, 2.0, 1.8), leg_lit, 16, 8)
        w.sphere(f"foot_{side}", tuple(foot + Vector((0, -0.4, -0.1))), (2.1, 1.8, 1.1), dark, 14, 7)
    sh.flat_bottom(w.meshes(), 0.0)


# --- L 267: the fighter ----------------------------------------------------------------------------

@kit.model("yellow_pod_fighter", mask=lambda: SHIP.mask())
def yellow_pod_fighter():
    f = SHIP
    X, Y = f.X, f.Y
    grey = kit.Painter("fighter", shades={6: (4, 5, 6, 7, 8, 9, 10, 11, 12)}, metallic=0.35, roughness=0.38,
                       remap={0x30: 0x64, 0x31: 0x64, 0x33: 0x64, 0x00: 0x64, 0x03: 0x64})
    dark = pal("fighter_dark", 0x62, metallic=0.4, roughness=0.4)
    light = pal("fighter_light", 0x7c, metallic=0.0, roughness=0.3, glow=1.6)
    light_deep = pal("fighter_light_deep", 0x7a, metallic=0.0, roughness=0.3, glow=1.0)
    cream = pal("fighter_glow", 0xee, metallic=0.0, roughness=0.3, glow=1.2)
    gun = pal("fighter_gun", 0x03, metallic=0.5, roughness=0.35)
    z0 = 5.0  # the ship's middle (it flies)
    # The pods (columns 0-7 and 16-23, rows 7-22): pointed lozenges, rounder at their outer sides.
    for side, c0, c1 in (("l", 0, 7), ("r", 16, 23)):
        polys = kit.polys_of(f, lambda v, c, r, c0=c0, c1=c1: c0 <= c <= c1 and 7 <= r <= 22, smooth=2, epsilon=0.3)
        pod = sh.inflate(f"pod_{side}", polys, grey(0x66), sh.round_profile(0.75, max_height=3.4), bottom=0.7,
                         base=z0, rim=0.2, spacing=0.4, sigma=1.0)
        k.smooth(pod, 50)
        pod_f = kit.frame("SHIP", 24, (12, 14)).fill({v for row in f.g for v in row if v is not None and v >> 4 == 7},
                                                     edge_only=False)
        kit.paint_sprite(pod, pod_f, grey, wall_steps=1, under=dark, blur=2)
        # The yellow lights along the outer side: a glowing strip set into the pod's surface.
        outer = -1 if side == "l" else 1
        cx = X(3.5 if side == "l" else 19.5)
        bpy.context.view_layer.update()
        pts = []
        for x_off, row in ((0.9, 10.5), (1.6, 13.5), (1.5, 16.5), (0.9, 18.6)):
            x_, y_ = cx + outer * x_off, Y(row)
            pts.append((x_, y_, sh.surface_z(pod, x_, y_, z0 + 2.0) - 0.25))
        w.tube(f"lights_{side}", w.catmull(pts, 0.4), 0.8, light, 10, squash=0.6)
    # The fuselage (columns 8-15, rows 8-24): wider behind, narrowing to the gun in front, joined to the pods.
    polys = kit.polys_of(f, lambda v, c, r: 8 <= c <= 15 and 8 <= r <= 24, smooth=2, epsilon=0.3)
    body = sh.inflate("fuselage", polys, grey(0x68), sh.round_profile(0.8, max_height=3.0), bottom=0.6, base=z0 + 0.4,
                      rim=0.2, spacing=0.4, sigma=1.0)
    k.smooth(body, 50)
    body_f = kit.frame("SHIP", 24, (12, 14)).fill({0xed, 0xee, 0xef, 0xec, 0x60}, edge_only=False)
    kit.paint_sprite(body, body_f, grey, wall_steps=1, under=dark, blur=2)
    # The struts to the pods (rows 12-16).
    kit.rounded_box("strut", (X(11.5) + 0.5, Y(14.0), z0 + 0.6), (17.0, 3.6, 1.6), grey(0x66), bevel=0.5)
    # The engine glow behind (row 9, columns 10-14) and the gun in front (rows 19-23).
    w.sphere("engine", (X(11.5) + 0.5, Y(9.2), z0 + 1.6), (2.2, 0.9, 1.1), cream, 16, 8)
    w.lathe_axis("gun", [(0.0, 0.7), (4.0, 0.6), (4.3, 0.75), (4.6, 0.01)], gun, (X(11.5) + 0.5, Y(19.0), z0 + 1.2),
                 (0, -1, 0), 12)


if __name__ == "__main__":
    kit.run()
