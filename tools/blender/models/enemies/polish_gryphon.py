"""GRYPHON's boss (sheet 0: its body and wings, 20 2x2 sprites; its neck, 0 91 beside 93; its head, 0 123 with the
frames 121 119 129), polished again (2026-10-23, round 38, the quality redo): rebuilt in place of round 37's version
of this script (each picture one heightfield in the picture's plane, painted by the sprites' shades: a soft,
washed-out relief next to the vivid sprites) as a creature of separate smooth solids.

Where it appears (found in round 37, kept): GRYPHON (episode 2) at t7100: the head, enemy 835 (0 123, armour 250, its
gun 68 and launch 836 every 71 frames when event 31 says so), at (125, y + 8), link 62; the body, custom enemies of
bank 29 (sheet 0) on the top layer, link 61 (the boss bar's): 1 3 . 7 9 . 13 15 at y - 84, 39 41 43 45 47 49 51 53 at
y - 56, . 79 81 83 85 87 89 at y - 28, the sheet's layout at x 40 + its column (24 apart), but 15 and 53 at x 202, 6
pixels left of their place over 13 and 51 (the game's right wing is 6 pixels shorter than the left); 3 and 13 have
armour 0, the rest 250 (bank 29's enemy 0: one frame, no damaged look); the neck, 91 and 93 at (112, y - 20),
(136, y - 20), link 62. The events move links 61 and 62 together into place (t7170-7240) and sway them side to side;
from t7360 the head and the neck (link 62) lunge down the screen and back again and again (90 to 120 pixels), the neck
sliding right off the body, which shows its own dark socket there, and the head's animation (123 121 121 121 119 119
119 129 129 129 119 119 119 121 121 121 123, animate 2: when it fires) drops its jaw. Episode 6's MIGRATION brings only
GRYPHON's wave 51, the head alone (enemy 1619 twice, at its t4923 and 5103): there the head flies without body and
neck (reported, not worked round: the head is whole in itself). No other enemy, launched ones included, shows any of
these sprites (frame models are safe); none is another sprite's pixels mirrored, turned or in other ramps.

The sprites are mirror images of themselves (the body about its column 96, the neck about its column 24, the head
about its column 11; in the game all three axes lie at x 130.5). Built symmetric as the sheet lays the body out, so
the models of 15 and 53 hold their sheet columns and lie 6 pixels right of the sprites' own place (their origins 6
pixels left of their boxes' middles): the game's 6 pixel short right wing becomes the sheet's whole wing.

As the sprites draw it (ramp 3's blues, the plates and claws in ramp 0's greys, red eyes in ramp 7; the body's
picture's columns and rows, its left half): wings spread out and up the screen, their feathers lying along the span
(the light streaks run parallel to the leading, lower edge, from the elbow's lobe at columns 41-57 of rows 69-75 out
to the wrist), the trailing (upper) edge stepping out in three finger tips (columns 36-47 of rows 31-37, 19-24 of row
23, 11-17 of row 17) to a grey claw at the wrist pointing up the screen (columns 4-11 of rows 11-30); the upper arm a
lit band from the shoulder to the elbow (rows 62-69); grey fans of five blades at the shoulders (columns 61-83 of rows
42-56); two long horns up the screen from its back (columns 82-95 of rows 0-44, bowed out a little, their tips at
column 87 of row 0); the torso between them (columns 82-111 of rows 44-66), scaled, a spine down it; under its foot a
dark shield (rows 63-85, columns 72-121: dark blues, dim ribs converging down it) that the neck covers at rest. The
neck (48 x 28): a column of vertebrae (columns 17-31), two small horns at its top, three grey fins a side stacked down
it (rows 7-12, 12-17, 17-22, their tips at columns 6-7), each lit along its top edge, its foot widening into the head;
the head (24 x 28): a mask: a V of light brows from its upper corners to its middle (rows 1-6), slanted red eyes at its
sides (columns 3-5 and 17-19 of rows 3-6), lit cheekbones sweeping down to the jaw, a snout's bridge down the middle,
fangs at columns 9 and 13 (rows 9-11) over a dark maw, the lower jaw (rows 13-18 in 123) with three small teeth,
dropping 2, 4 and 6 rows in 121, 119 and 129, the mouth's dark walls and side fangs showing as it opens.

Built from separate smooth solids (polish_sweep_kit: lofts along paths through superellipse sections, ellipsoids from
explicit rings), each part its own material, modelled in the picture's plane (x, y where the sprites draw them, z up
from the top layer) and sheared along the game camera's line of sight (y - z tan 20) so the camera sees each where the
sprites draw it:
- each wing: ROWS, 11 rows of long feathers (84) along the span in the wing's frame (WP: s along the span from the
  elbow, t across it), each feather a vane narrow at its quill, widest past its middle, pointed, with a rachis, arched
  and a little bent (fixed jitter), shingled (each lies over the root of the next one out, the rows nearer the leading
  edge over those behind them: the wing falls from the arm, 4.4, to the trailing edge and the tip, about 1.5), the
  rows converging a little to the tip, their last feathers drawing the trailing edge and its three finger tips; the web
  under them (dark, seen in the gaps); the upper arm (UPPER_ARM) with seven covert feathers along it, the elbow's
  lobe, the forearm along the leading edge to the wrist, the shoulder's flat mass; the wrist's talon (grey);
- the shoulders' fans: five bony blades fanned from a hinge, each bowed and banked so the next one overlaps it;
- the horns: tapering tubes along the sprite's bowed horns, ringed, rooted in the torso;
- the torso: a loft (TORSO), two back muscles, seven rows of scales pointing up the screen (the rows nearer the head
  over those behind), a crest of six knobs along the spine;
- the socket: a low dark plate over the shield's outline, three dim ribs a side converging down it (the neck lies over
  it at rest: the socket 0.4-2.6 high, the neck 1.6-7.8);
- the neck: a column of vertebrae (NECK, swelling a little between its seven knobs), two lit bands beside the spine,
  three bony fins a side (NECK_FINS: broad blades with a lit top edge, each lower one riding over the one above, their
  tips drooping), two prongs at its top; its foot carried NECK_OVERLAP pixels over the head's top (they always move
  together; alone in MIGRATION the head's top edge faces up the screen, away from the camera);
- the head: the skull (SKULL: the cranium to the eyes, the snout narrowing over the maw), the dark face beside the
  snout (MASK), the brows' chevron, the snout's bridge, the cheekbones, the eyes (glowing almonds in dark sockets), the
  fangs, the side fangs at the maw's corners, the maw (longer as the jaw drops), the lower jaw (JAW, moved down DROP
  rows a frame) with its chin ridge and three teeth; the open frames add the mouth's dark side walls.
Materials (palette indices, metallic/roughness; nothing painted from the sprites' pixels, the shading is the
geometry's and the game's light): feathers 0x37, web 0x31, arms 0x38, hide (torso, neck, skull) 0x37, the light plates
(spine knobs, scales' crest, brows, bridge, cheekbones) 0x3a, horns 0x38 (all 0.18/0.2-0.24: a little metallic, so the
highlights stay blue), the socket 0x33, the bony fans, fins and the talon 0x0a and 0x0b, the eyes 0x75 glowing 0.55
with a core of 0x77 at 0.6, teeth 0x3c, the maw 0x30; cut faces 0x32 (blue parts) and 0x05 (grey parts). Heights over
the top layer (undersides flattened at 0): the body 0-8.5 (the torso's crest; the horns 8.2, the wings 1-6.8), the
neck 0.2-8.5, the head 0-7.8 (the old models reached 8.4-10; the player's plane is 6 over the top layer).

The pieces: the body built whole and cut in the picture's plane along the sprites' edges (polish_coral_manta.cut,
caps in each part's inside colour, the faces' normals the uncut solids'), each piece checked against its sprite as the
camera sees it, sheared, moved so its sprite's middle is its origin (15 and 53: 6 pixels left of their boxes' middles),
triangulated (polish_k_pod.triangulate: the same output with and without --check) and joined (polish_deli_boss.join);
the neck cut at x -0.5 (91 | 93); the head whole, one model a frame. A box holding nothing would get a blank model (one
tiny triangle under the layer); none does. No random numbers, no booleans: md5 identical over runs, with and without
--check.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera (z 0: the top
layer). The body's picture: continuous column u and row v (pixel (c, r)'s middle at (c + 0.5, r + 0.5)), x = u - 96.5
(its axis at x 0), y = 42 - v (BP); a body sprite whose top left pixel is the picture's (c0, r0) has its origin at
(c0 - 84.5, 28 - r0), 15 and 53 at (77.5, 14) and (77.5, -14). The neck's: x = u - 24.5, y = 14 - v (NP), origins
(-12.5, 0) and (11.5, 0); at rest its row 0 is the body's row 64. The head's: x = u - 11.5, y = 14 - v (HP), origin
(0.5, 0); at rest its row 0 is the neck's row 28.

models.cfg: the model lines stay (gryphon_1 ... gryphon_89, gryphon_neck_91, gryphon_neck_93, gryphon_head; frame models
gryphon_head_123, _121, _129; all origin); the sprite lines stay (yaw=0; the top layer); the frame lines stay (0 123,
121, 129; gryphon_head is 119's); only the comments describing the build change.

Replaces round 37's version of this script (rewritten in place; it imported polish_sheet9_kit, which stays: other
scripts use it). No old generator code is left to remove (round 37 removed it).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each piece's outline as the
camera sees it against its sprite's pixels in enemy_0.png), --preview <prefix> with --pieces 1 (each model's top and
3/4 views), --only <name,...> (or the groups body, neck, head), --whole <prefix> (the sheared, uncut body, neck and
heads 123 and 129 as GLBs, for looking at).
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
from polish_coral_manta import cut  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_sweep_kit import (catmull, resample, section, set_smooth, sweep, ellipsoid, jitter,  # noqa: E402
                              feather, interp, loft_sections, mirrored, flatten_below, shear_to_camera)


# --- Materials: by part, each one palette index (the sprites' own ramps), the shading left to the geometry ----------
# key: (palette index, metallic, roughness, emission strength in its own colour)
MATS = {
    "feather": (0x37, 0.18, 0.22, 0.0),   # the wings' feathers
    "web": (0x31, 0.0, 0.7, 0.0),         # the wings' skin under them (seen in the gaps)
    "arm": (0x38, 0.18, 0.22, 0.0),       # the wings' arms along their leading edges
    "hide": (0x37, 0.18, 0.24, 0.0),      # the torso, the neck, the skull
    "scute": (0x3a, 0.18, 0.2, 0.0),      # the plates along the spine, the brows
    "horn": (0x38, 0.18, 0.2, 0.0),
    "socket": (0x33, 0.0, 0.7, 0.0),      # the dark socket the neck lies in
    "bone": (0x0a, 0.35, 0.32, 0.0),      # the silver plates: the shoulders' fans, the neck's fins
    "claw": (0x0b, 0.3, 0.26, 0.0),
    "inside": (0x32, 0.0, 0.85, 0.0),     # cut faces of the blue parts
    "eye": (0x75, 0.0, 0.2, 0.55),        # the eyes, glowing in their own red
    "eye_hot": (0x77, 0.0, 0.15, 0.6),
    "tooth": (0x3c, 0.1, 0.25, 0.0),      # the fangs and teeth (the sprite's pale blues)
    "maw": (0x30, 0.0, 0.8, 0.0),         # the mouth's dark inside
    "bone_in": (0x05, 0.2, 0.6, 0.0),     # cut faces of the grey parts
}


def materials():
    pal = k.level_palette()
    m = {}
    for key, (index, metallic, roughness, glow) in MATS.items():
        extra = dict(emission=pal[index], emission_strength=glow) if glow > 0 else {}
        m[key] = k.material("gry_%s" % key, palette=index, metallic=metallic, roughness=roughness, **extra)
    return m


# --- Coordinates ------------------------------------------------------------------------------------------------------
# The body's picture (192 x 84, the sheet's layout of its 20 sprites): continuous column u and row v (pixel (c, r)'s
# middle at (c + 0.5, r + 0.5)); x = u - 96.5 (its axis, column 96's middle, at x 0), y = 42 - v.

def BP(u, v, z=0.0):
    return Vector((u - 96.5, 42.0 - v, z))


# The left wing's frame: s along the span from the elbow (u 48, v 72) out to the tip, t across it from the leading
# (lower) edge towards the trailing (upper) one: the feathers lie along s.
W_O = (48.0, 72.0)
W_D = (-43.0 / math.hypot(43.0, 50.0), -50.0 / math.hypot(43.0, 50.0))
W_N = (-W_D[1], W_D[0])


def WP(s, t, z=0.0):
    return BP(W_O[0] + s * W_D[0] + t * W_N[0], W_O[1] + s * W_D[1] + t * W_N[1], z)


D3 = Vector((W_D[0], -W_D[1], 0.0))     # the frame's s and t directions in x, y
N3 = Vector((W_N[0], -W_N[1], 0.0))


# --- Curves and solids ------------------------------------------------------------------------------------------------


# --- The feathers ---------------------------------------------------------------------------------------------------


# The rows of feathers of the left wing, in the wing's frame: (t at the row's root, t at its end, s of its first
# feather's root, s of its last feather's tip); the rows converge a little towards the tip. Their last feathers draw
# the sprite's trailing edge and its three finger tips: row 5 the third (its tip at s 37.6), row 7 the second
# (54.5), row 8 the first (65); rows 1-3 end under the shoulder's fan, rows 9-11 under the wrist's claw.
ROWS = [(32.0, 31.0, -16.0, 7.5), (28.8, 28.0, -17.5, 9.5), (25.6, 25.0, -17.5, 11.0), (22.4, 21.0, -16.5, 33.0),
        (19.2, 18.2, -14.5, 37.6), (16.0, 15.2, -12.0, 33.5), (12.8, 10.6, -9.5, 54.5), (9.6, 8.3, -7.5, 66.4),
        (6.4, 4.6, -6.0, 66.0), (3.2, 1.4, -5.0, 63.0), (0.0, -1.6, -3.5, 60.0)]
FEATHER_LEN, FEATHER_STEP, FEATHER_HW, FEATHER_HH = 14.0, 5.6, 2.45, 0.2


def wing_z(s, t):
    """The wing's height under its feathers: highest at the arm and the body, falling to the tip and the trailing
    edge."""
    return 4.4 - 0.075 * (t + 3.0) - 0.03 * (s + 5.0)


UPPER_ARM = [(84.0, 62.4, 3.3, 4.2), (75.0, 63.6, 3.0, 3.6), (66.0, 65.0, 2.7, 3.1), (57.0, 67.2, 2.5, 2.8),
             (50.5, 69.4, 2.4, 2.6)]


def arm_row(u):
    """The upper arm's middle row at column u."""
    pts = UPPER_ARM
    if u >= pts[0][0]:
        return pts[0][1]
    for (u0, v0, _, _), (u1, v1, _, _) in zip(pts, pts[1:]):
        if u1 <= u <= u0:
            return v0 + (v1 - v0) * (u0 - u) / (u0 - u1)
    return pts[-1][1]


def covered_from(t0, t1, s0, s1):
    """Where a row comes out from under the upper arm and the elbow: the first s whose point lies above the arm's
    middle (and off the elbow's lobe)."""
    s = s0
    while s < s1:
        t = t0 + (t1 - t0) * (s - s0) / (s1 - s0)
        p = WP(s, t)
        u, v = p.x + 96.5, 42.0 - p.y
        lobe = ((u - 49.2) / 7.4) ** 2 + ((v - 71.6) / 3.6) ** 2 < 0.8
        if v < arm_row(u) - 0.6 and not lobe:
            return s
        s += 0.25
    return s1


def wing_feathers(m):
    objs = []
    for r, (t0, t1, s0, s1) in enumerate(ROWS):
        def row_t(s):
            return t0 + (t1 - t0) * (s - s0) / (s1 - s0)
        s0 = max(s0, covered_from(t0, t1, s0, s1) - 2.0)
        tips = []
        s = s1
        i = 0
        while s - FEATHER_LEN > s0 - FEATHER_LEN * 0.5:
            tips.append(s)
            s -= FEATHER_STEP * (0.85 + 0.3 * jitter(r, i, 1))
            i += 1
        # inner feathers first: each lies over the root of the next one out
        for i, st in enumerate(reversed(tips)):
            last = i == len(tips) - 1
            length = FEATHER_LEN * ((1.1 if last else 1.0) + 0.12 * (jitter(r, i, 2) - 0.5))
            sr = st - length
            root = WP(sr, row_t(sr), wing_z(sr, row_t(sr)) - 0.3)
            tip = WP(st, row_t(st), wing_z(st, row_t(st)) + 0.35)
            objs.append(feather("feather_%d_%d" % (r, i), root, tip, FEATHER_HW * (1.06 if last else 1.0),
                                FEATHER_HH, m["feather"], bank=(N3, 0.12),
                                bend=(N3, 0.5 * (jitter(r, i, 3) - 0.3))))
    return objs


# The wing's skin under the feathers: (s, t of its leading side, t of its trailing side), smoothed.
WEB = [(-17.0, 20.5, 28.0), (-12.0, 17.0, 31.0), (-8.0, 12.0, 33.0), (-5.0, 1.5, 33.0), (-2.0, -2.0, 32.0),
       (2.0, -3.4, 31.0), (8.0, -3.6, 28.0), (11.0, -3.6, 23.0), (14.0, -3.8, 21.4), (22.0, -4.6, 21.0),
       (30.0, -5.8, 21.0), (33.0, -6.2, 19.0), (36.0, -6.4, 12.5), (40.0, -6.6, 10.8), (48.0, -6.4, 10.8),
       (53.0, -5.4, 10.5), (56.0, -4.4, 7.0), (60.0, -3.0, 8.4), (63.0, -1.6, 7.6)]


def wing_web(m):
    pts = resample(catmull(WEB, 6), 60)
    rings = []
    seg = 16
    for s, t0, t1 in pts:
        mid, half = (t0 + t1) / 2, (t1 - t0) / 2
        ring = []
        for j in range(seg):
            a = 2 * math.pi * j / seg
            t = mid + half * math.cos(a)
            z = wing_z(s, t) - 0.55 + 0.22 * math.sin(a)
            ring.append(WP(s, t, z))
        rings.append(ring)
    s0, t00, t10 = pts[0]
    s1, t01, t11 = pts[-1]
    obj = k.loft("web", rings, m["web"], start_point=WP(s0 - 0.3, (t00 + t10) / 2, wing_z(s0, (t00 + t10) / 2) - 0.55),
                 end_point=WP(s1 + 0.3, (t01 + t11) / 2, wing_z(s1, (t01 + t11) / 2) - 0.55))
    return set_smooth(obj)


def wing_arm(m):
    """The arm: the upper arm from the shoulder to the elbow's lobe, the forearm along the leading edge to the wrist."""
    objs = []
    pts = resample(catmull(UPPER_ARM, 6), 20)
    objs.append(sweep("upper_arm", [BP(u, v, z) for u, v, z, w in pts],
                      [(w, w * 0.62, w * 0.62) for u, v, z, w in pts], m["arm"], segments=16))
    objs.append(ellipsoid("elbow", BP(49.2, 71.6, 2.0), (7.4, 3.6, 2.3), m["arm"], 12, 24,
                          axes=(Vector((1, 0.12, 0)).normalized(), Vector((-0.12, 1, 0)).normalized(),
                                Vector((0, 0, 1)))))
    # the coverts over the upper arm: short feathers pointing out to the elbow
    pts = resample(catmull(UPPER_ARM, 6), 60)
    for i in range(7):
        f0 = 0.04 + 0.12 * i
        a, b = pts[int(f0 * 59)], pts[min(59, int((f0 + 0.2) * 59))]
        lift = a[3] * 0.62
        root = BP(a[0], a[1] - 0.6, a[2] + lift - 0.15)
        tip = BP(b[0], b[1] + 0.2, b[2] + b[3] * 0.62 + 0.25)
        objs.append(feather("covert_%d" % i, root, tip, 2.2 - 0.08 * i, 0.3, m["feather"], arch=0.25,
                            bank=(Vector((0.0, -1.0, 0.0)), 0.1)))
    # the forearm, just inside the leading edge
    fore = []
    for s, t_lo, _ in WEB[4:]:
        z = wing_z(s, t_lo + 2.6) + 0.1
        fore.append((s, t_lo + 1.75, z, 2.6 - 0.012 * s))
    pts = resample(catmull(fore, 6), 40)
    objs.append(sweep("forearm", [WP(s, t, z) for s, t, z, w in pts], [(w, w * 0.7, w * 0.6) for s, t, z, w in pts],
                      m["arm"], segments=12))
    # the shoulder: a flat mass joining the upper arm, the fan's hinge and the torso's flank
    objs.append(ellipsoid("shoulder", BP(81.0, 59.5, 2.2), (8.0, 5.6, 2.6), m["hide"], 12, 24,
                          axes=(Vector((1, -0.35, 0)).normalized(), Vector((0.35, 1, 0)).normalized(),
                                Vector((0, 0, 1)))))
    return objs


def wing_claw(m):
    """The claw at the wrist: a grey talon pointing up the screen, broad at its middle."""
    spec = [(8.4, 30.0, 3.4, 1.2), (7.6, 26.0, 4.0, 2.2), (7.3, 21.5, 4.5, 3.0), (7.3, 17.5, 4.7, 3.1),
            (7.4, 14.5, 4.6, 2.5), (7.5, 12.4, 4.4, 1.5), (7.6, 11.2, 4.3, 0.7)]
    pts = resample(catmull(spec, 6), 22)
    return sweep("wing_claw", [BP(u, v, z) for u, v, z, w in pts],
                 [(w, min(w * 0.75, 1.9), min(w * 0.55, 1.4)) for u, v, z, w in pts], m["claw"], segments=12,
                 end=BP(7.6, 10.5, 4.2))


def left_wing(m):
    return [wing_web(m)] + wing_feathers(m) + wing_arm(m) + [wing_claw(m)]


# --- The shoulders' fans (grey bony plates) ------------------------------------------------------------------------
FAN_HINGE = (77.0, 57.2, 5.6)
FAN_TIPS = [(61.6, 46.6, 4.7), (66.0, 44.2, 5.0), (71.4, 42.8, 5.3), (76.4, 42.6, 5.5), (81.0, 43.8, 5.6)]


def shoulder_fan(m):
    objs = []
    hu, hv, hz = FAN_HINGE
    for i, (tu, tv, tz) in enumerate(FAN_TIPS):
        spec = []
        for f, w in ((0.0, 0.9), (0.25, 1.7), (0.5, 2.4), (0.72, 2.75), (0.88, 2.6), (0.97, 1.7)):
            u, v = hu + (tu - hu) * f, hv + (tv - hv) * f
            # curved: bowed out to the left a little
            bow = 1.2 * math.sin(math.pi * f)
            u -= bow * 0.6
            z = hz + (tz - hz) * f + 0.6 * math.sin(math.pi * f) + 0.12 * i
            spec.append((u, v, z, w))
        pts = resample(catmull(spec, 5), 16)
        objs.append(sweep("fan_%d" % i, [BP(u, v, z) for u, v, z, w in pts], [(w, 0.55, 0.35) for u, v, z, w in pts],
                          m["bone"], segments=10, ridge=0.25, bank=(Vector((1, 0, 0)), 0.18),
                          end=BP(tu - 0.2, tv - 0.3, tz + 0.1)))
    return objs


# --- The horns ------------------------------------------------------------------------------------------------------
HORN = [(88.6, 44.0, 4.6, 5.6), (88.0, 40.0, 4.9, 5.4), (86.7, 30.0, 5.2, 4.25), (85.4, 20.0, 5.3, 2.95),
        (85.9, 10.0, 5.1, 1.8), (86.6, 3.0, 4.9, 1.1), (87.2, 0.5, 4.8, 0.45)]


def horn(m):
    pts = resample(catmull(HORN, 8), 48)
    secs = []
    for i, (u, v, z, w) in enumerate(pts):
        f = i / (len(pts) - 1)
        ring = 1.0 + 0.07 * math.cos(2 * math.pi * f * 11) * (1 - f)   # growth rings
        secs.append((w * ring, min(w * 0.72, 3.4) * ring, min(w * 0.6, 3.0) * ring))
    return sweep("horn", [BP(u, v, z) for u, v, z, w in pts], secs, m["horn"], segments=14,
                 end=BP(87.4, -0.2, 4.8))


# --- The torso -------------------------------------------------------------------------------------------------------
# Its sections down the screen: (row, half-width, height of its top); the horns grow from its upper corners.
TORSO = [(42.8, 5.0, 5.3), (45.0, 11.0, 6.5), (48.0, 14.0, 7.1), (53.0, 14.4, 7.3), (58.0, 13.2, 7.0),
         (62.0, 11.4, 6.3), (65.5, 9.4, 4.9)]
TORSO_POWER = 2.4


def torso_z(x, v):
    """The torso's top at x (from its axis) and row v."""
    hw, top = interp(TORSO, v)
    q = min(1.0, abs(x) / hw)
    return 1.0 + (top - 1.0) * (1 - q ** TORSO_POWER) ** (1 / TORSO_POWER)


def torso(m):
    vs = [TORSO[0][0] + (TORSO[-1][0] - TORSO[0][0]) * i / 30 for i in range(31)]
    rings = []
    seg = 28
    for v in vs:
        hw, top = interp(TORSO, v)
        ring = []
        for j in range(seg):
            x, z = section(j, seg, hw, top - 1.0, 1.0, power=TORSO_POWER)
            ring.append(BP(96.5 + x, v, z + 1.0))
        rings.append(ring)
    obj = k.loft("torso", rings, m["hide"], start_point=BP(96.5, vs[0] - 0.6, 3.8),
                 end_point=BP(96.5, vs[-1] + 0.6, 3.0))
    return set_smooth(obj)


# The back's muscles either side of the spine (from, to: column, row; half-width, height over the torso), the scales
# over them in rows across the back (row, how many): each scale points up the screen, the rows nearer the head lying
# over the roots of those behind them; along the spine a crest of knobs.
MUSCLES = [((89.0, 44.5), (92.0, 62.0), 4.6, 0.75)]
SCALE_ROWS = [(46.0, 6), (49.0, 7), (52.0, 7), (55.0, 7), (58.0, 6), (61.0, 5), (63.6, 4)]
SCUTES = [44.0, 47.4, 50.8, 54.2, 57.6, 61.0]


def back_z(x, v):
    """The back's top: the torso with its muscles."""
    z = torso_z(x, v)
    for (u0, v0), (u1, v1), hw, h in MUSCLES:
        if v0 <= v <= v1:
            f = (v - v0) / (v1 - v0)
            cx = (u0 + (u1 - u0) * f) - 96.5
            for c in (cx, -cx):
                q = min(1.0, abs(x - c) / hw)
                z += h * (1 - q * q) * math.sin(math.pi * f) ** 0.5
    return z


def back(m):
    objs = []
    for i, ((u0, v0), (u1, v1), hw, h) in enumerate(MUSCLES):
        for side in (1, -1):
            path, secs = [], []
            for j in range(10):
                f = j / 9
                u, v = u0 + (u1 - u0) * f, v0 + (v1 - v0) * f
                x = side * (u - 96.5)
                path.append(BP(96.5 + x, v, torso_z(x, v) - 0.6))
                w = math.sin(math.pi * (0.06 + 0.88 * f)) ** 0.6
                secs.append((hw * w, (h + 0.6) * w, 1.2))
            objs.append(sweep("muscle_%d_%d" % (i, side), path, secs, m["hide"], segments=14))
    for r, (v, count) in enumerate(SCALE_ROWS):
        hw, _ = interp(TORSO, v)
        span = hw - 2.6
        for i in range(count):
            x = -span + 2 * span * (i + 0.5) / count
            if abs(x) < 1.8:
                continue
            root = BP(96.5 + x, v + 1.9, back_z(x, v + 1.9) - 0.1 + 0.03 * r)
            tip = BP(96.5 + x * 1.03, v - 2.1, back_z(x, v - 2.1) + 0.2 + 0.03 * r)
            objs.append(feather("scale_%d_%d" % (r, i), root, tip, 1.75, 0.24, m["hide"], arch=0.1))
    for i, v in enumerate(SCUTES):
        root = BP(96.5, v + 2.2, back_z(0.0, v + 2.2) - 0.15)
        tip = BP(96.5, v - 2.0, back_z(0.0, v - 2.0) + 0.25)
        path, secs = [], []
        for f, w in ((0.0, 0.5), (0.25, 0.9), (0.55, 1.0), (0.8, 0.85), (0.95, 0.5)):
            p = root.lerp(tip, f)
            p.z += 0.3 * math.sin(math.pi * f)
            path.append(p)
            secs.append((1.9 * w, 0.5, 0.35))
        objs.append(sweep("scute_%d" % i, path, secs, m["scute"], segments=12, ridge=0.3,
                          end=tip + Vector((0, 0.2, -0.05))))
    return objs


# --- The socket the neck lies in -----------------------------------------------------------------------------------
# Under the torso's foot the sprites draw a dark shield (rows 63-85: dark blues, dim ribs converging down it) that the
# neck covers at rest and shows when it lunges: its sections down the screen (row, half-width, height of its top).
SOCKET = [(62.5, 19.0, 2.6), (66.5, 22.0, 2.5), (70.0, 21.6, 2.4), (73.5, 18.6, 2.2), (77.0, 15.4, 2.0),
          (80.5, 12.4, 1.8), (83.0, 9.6, 1.5), (84.7, 6.0, 1.1)]
# its ribs (from, to: column, row) on the left half, mirrored
SOCKET_RIBS = [((76.5, 67.5), (88.5, 82.0)), ((82.5, 65.5), (91.0, 81.0)), ((88.5, 64.5), (93.6, 79.5))]


def socket_z(x, v):
    vs = [row[0] for row in SOCKET]
    v = min(max(v, vs[0]), vs[-1])
    for (v0, w0, h0), (v1, w1, h1) in zip(SOCKET, SOCKET[1:]):
        if v0 <= v <= v1:
            f = (v - v0) / (v1 - v0)
            hw, top = w0 + (w1 - w0) * f, h0 + (h1 - h0) * f
            q = min(1.0, abs(x) / hw)
            return 0.4 + (top - 0.4) * (1 - q ** 3) ** (1 / 3)
    return 0.4


def socket(m):
    """The shield: a low plate over the outline, dim ribs along it converging to its foot."""
    objs = []
    pts = resample(catmull(SOCKET, 6), 26)
    rings = []
    seg = 24
    for v, hw, top in pts:
        ring = []
        for j in range(seg):
            x, z = section(j, seg, hw, top - 0.4, 0.4, power=3.0)
            ring.append(BP(96.5 + x, v, z + 0.4))
        rings.append(ring)
    floor = k.loft("socket_floor", rings, m["socket"], start_point=BP(96.5, pts[0][0] - 0.4, 1.4),
                   end_point=BP(96.5, pts[-1][0] + 0.4, 0.8))
    objs.append(set_smooth(floor))
    for i, ((u0, v0), (u1, v1)) in enumerate(SOCKET_RIBS):
        path, secs = [], []
        for j in range(12):
            f = j / 11
            u, v = u0 + (u1 - u0) * f, v0 + (v1 - v0) * f
            path.append(BP(u, v, socket_z(u - 96.5, v) - 0.1))
            w = 1.0 * math.sin(math.pi * (0.08 + 0.84 * f)) ** 0.5
            secs.append((w, 0.3 * w + 0.05, 0.3))
        for side in (1, -1):
            pp = [Vector((side * q.x, q.y, q.z)) for q in path]
            objs.append(sweep("socket_rib_%d_%d" % (i, side), pp, secs, m["socket"], segments=10))
    return objs


# --- The neck --------------------------------------------------------------------------------------------------------
# Its picture (48 x 28: 0 91 beside 93): continuous column u and row v; x = u - 24.5 (its axis, column 24's middle),
# y = 14 - v. At rest its top lies over the body's socket (its row 0 is the body's row 64), its foot over the head's
# top (its row 28 is the head's row 0).

def NP(u, v, z=0.0):
    return Vector((u - 24.5, 14.0 - v, z))


# The column down its middle (row, half-width, height of its top): vertebrae, a spine of knobs along it.
NECK = [(0.6, 4.6, 6.0), (3.0, 6.0, 6.6), (8.0, 6.6, 7.0), (14.0, 6.4, 7.0), (19.0, 6.8, 6.8), (21.5, 8.6, 6.5),
        (24.0, 10.8, 6.15), (26.5, 12.2, 5.9), (29.5, 12.2, 5.75)]
NECK_KNOBS = [3.0, 6.6, 10.2, 13.8, 17.4, 21.0, 24.6]
# The fins (bony silver plates) at the left side, top to bottom: root (column, row), tip (column, row), half-width
# across, height at the root and the tip; each lower one rides over the bottom edge of the one above.
NECK_FINS = [((19.5, 10.4), (6.2, 9.4), 3.2, 5.7, 4.3), ((19.5, 15.0), (6.0, 15.0), 3.5, 5.9, 4.4),
             ((19.5, 19.8), (7.2, 19.4), 3.4, 6.1, 4.6)]
NECK_PRONG = [(20.4, 8.6, 5.8, 2.4), (19.6, 6.0, 6.3, 2.2), (19.6, 3.2, 6.5, 1.6), (20.4, 1.2, 6.4, 0.9),
              (21.0, 0.2, 6.2, 0.35)]


def neck_z(x, v):
    hw, top = interp(NECK, v)
    q = min(1.0, abs(x) / hw)
    return 1.6 + (top - 1.6) * (1 - q ** 2.6) ** (1 / 2.6)


def neck_whole(m):
    objs = []
    vs = [NECK[0][0] + (NECK[-1][0] - NECK[0][0]) * i / 30 for i in range(31)]
    rings = []
    seg = 26
    for v in vs:
        hw, top = interp(NECK, v)
        # vertebrae: the column swells a little between its knobs
        swell = 1.0 + 0.05 * math.cos(2 * math.pi * (v - 3.0) / 3.6) if v < 22 else 1.0
        ring = []
        for j in range(seg):
            x, z = section(j, seg, hw * swell, (top - 1.6) * swell, 1.4, power=2.6)
            ring.append(NP(24.5 + x, v, z + 1.6))
        rings.append(ring)
    col = k.loft("neck", rings, m["hide"], start_point=NP(24.5, vs[0] - 0.5, 4.6),
                 end_point=NP(24.5, vs[-1] + 0.3, 3.5))
    objs.append(set_smooth(col))
    # the column's lit sides: two bands either side of the spine
    for side in (1, -1):
        path, secs = [], []
        for j in range(14):
            v = 2.0 + 19.5 * j / 13
            x = side * 3.4
            path.append(NP(24.5 + x, v, neck_z(x, v) - 0.35))
            w = math.sin(math.pi * (0.05 + 0.9 * j / 13)) ** 0.5
            secs.append((2.0 * w, 0.6 * w + 0.1, 0.5))
        objs.append(sweep("neck_band_%d" % side, path, secs, m["hide"], segments=12))
    for i, v in enumerate(NECK_KNOBS):
        root = NP(24.5, v + 1.5, neck_z(0.0, v + 1.5) - 0.2)
        tip = NP(24.5, v - 1.7, neck_z(0.0, v - 1.7) + 0.2)
        path, secs = [], []
        for f, w in ((0.0, 0.5), (0.3, 0.95), (0.6, 1.0), (0.85, 0.75), (0.97, 0.4)):
            q = root.lerp(tip, f)
            q.z += 0.3 * math.sin(math.pi * f)
            path.append(q)
            secs.append((1.5 * w, 0.45, 0.3))
        objs.append(sweep("neck_knob_%d" % i, path, secs, m["scute"], segments=10, ridge=0.25,
                          end=tip + Vector((0, 0.15, -0.05))))
    left = []
    for i, ((u0, v0), (u1, v1), hw, z0, z1) in enumerate(NECK_FINS):
        path, secs = [], []
        for j in range(12):
            f = j / 11
            u, v = u0 + (u1 - u0) * f, v0 + (v1 - v0) * f
            v -= 0.6 * math.sin(math.pi * f)      # bowed up the screen a little
            # each lower fin a little higher (it rides over the one above); the tip drooping
            path.append(NP(u, v, z0 + (z1 - z0) * f + 0.35 * math.sin(math.pi * f) - 0.5 * f ** 3 + 0.18 * i))
            w = [0.85, 0.96, 1.0, 1.0, 0.98, 0.95, 0.9, 0.83, 0.74, 0.62, 0.45, 0.24][j]
            secs.append((hw * w, 0.42, 0.3))
        left.append(sweep("neck_fin_%d" % i, path, secs, m["bone"], segments=12, ridge=0.2,
                          up=(0.0, -0.35, 1.0), bank=(Vector((0.0, 1.0, 0.0)), 0.32),
                          end=NP(u1 - 0.5, v1 - 0.2, z1)))
    pts = resample(catmull(NECK_PRONG, 6), 14)
    left.append(sweep("neck_prong", [NP(u, v, z) for u, v, z, w in pts],
                      [(w, w * 0.8, w * 0.7) for u, v, z, w in pts], m["horn"], segments=12,
                      end=NP(21.2, -0.4, 6.1)))
    objs += left + mirrored(left)
    flatten_below(objs)
    for o in objs:
        o["cap"] = "bone_in" if o.data.materials[0].name.startswith("gry_bone") else "inside"
    return objs


# --- The head ---------------------------------------------------------------------------------------------------------
# Its picture (24 x 28: 0 123 and its frames): x = u - 11.5 (its axis, column 11's middle), y = 14 - v; its origin
# (its sprite's middle) at x 0.5. The lower jaw drops DROP rows in the frames.
DROP = {123: 0, 121: 2, 119: 4, 129: 6}


def HP(u, v, z=0.0):
    return Vector((u - 11.5, 14.0 - v, z))


# The skull's sections (row, half-width, height of its top): the cranium to the eyes, then the snout narrowing to its
# tip over the maw.
SKULL = [(-0.6, 11.2, 5.5), (1.5, 11.6, 6.3), (3.5, 11.0, 6.6), (5.5, 8.0, 6.4), (7.0, 4.4, 6.1), (9.5, 3.3, 5.6),
         (11.2, 2.8, 5.0), (12.6, 2.2, 4.4)]
# The dark mask under it, seen beside the snout between the cheekbones (row, half-width, height).
MASK = [(5.0, 9.4, 4.4), (7.5, 8.6, 4.0), (10.0, 7.4, 3.5), (12.6, 6.0, 3.0)]
# The lower jaw's sections (row in 123, half-width, height).
JAW = [(12.6, 7.4, 4.0), (14.0, 6.4, 4.4), (15.5, 4.8, 4.3), (17.0, 3.2, 3.9), (18.6, 1.6, 3.3)]
# The brow: a chevron from the skull's upper corners down to its apex over the snout (left arm); the snout's bridge
# from the apex down; the cheekbones sweeping down from the cranium's sides to tusks.
BROW = [(2.2, 1.0, 6.4, 1.9), (5.3, 2.4, 6.95, 2.1), (8.5, 4.3, 7.05, 1.95), (11.5, 6.1, 6.85, 1.6)]
BRIDGE = [(11.5, 5.8, 6.9, 1.4), (11.5, 8.0, 6.5, 1.25), (11.5, 10.2, 5.9, 1.05), (11.5, 12.2, 5.1, 0.8)]
CHEEK = [(0.9, 3.6, 4.8, 1.5), (1.4, 6.2, 5.3, 1.9), (2.4, 8.8, 5.2, 1.8), (3.6, 11.0, 4.7, 1.4), (4.7, 12.8, 4.1, 0.8),
         (5.3, 13.8, 3.6, 0.3)]
EYE = ((4.6, 4.6), 2.8, 1.35, 5.75, -50.0)    # middle, half-length, half-width, height, slant (degrees)


def head_whole(m, drop):
    objs = []
    objs.append(loft_sections("skull", SKULL, lambda x, v, z: HP(11.5 + x, v, z), m["hide"], power=2.0, bottom=1.2,
                              start=HP(11.5, -0.9, 3.8), end=HP(11.5, 13.0, 3.0)))
    objs.append(loft_sections("mask", MASK, lambda x, v, z: HP(11.5 + x, v, z), m["maw"], seg=20, power=2.6,
                              bottom=1.0, start=HP(11.5, 4.6, 3.0), end=HP(11.5, 13.0, 2.0), steps=12))
    # the maw: the dark inside between the snout's fangs and the lower jaw, longer as the jaw drops
    maw = [(9.0, 4.2, 3.0), (11.0, 4.8, 3.0), (13.0 + drop, 5.4 if drop else 4.6, 2.8), (14.5 + drop, 3.2, 2.6)]
    objs.append(loft_sections("maw", maw, lambda x, v, z: HP(11.5 + x, v, z), m["maw"], seg=18, power=2.6,
                              bottom=0.8, start=HP(11.5, 8.6, 2.0), end=HP(11.5, 14.9 + drop, 1.8), steps=10))
    jaw = [(v + drop, w, h) for v, w, h in JAW]
    objs.append(loft_sections("jaw", jaw, lambda x, v, z: HP(11.5 + x, v, z), m["hide"], seg=22, power=2.1,
                              bottom=1.0, start=HP(11.5, 12.2 + drop, 3.0), end=HP(11.5, 19.0 + drop, 2.6), steps=14))
    if drop > 0:
        wall = [(5.2, 12.0, 3.4, 1.1), (5.0, 12.8 + drop * 0.5, 3.2, 1.2), (5.4, 13.4 + drop, 3.3, 1.0)]
        for side in (1, -1):
            pts = resample(catmull(wall, 6), 10)
            objs.append(sweep("mouth_wall_%d" % side, [HP(11.5 + side * (u - 11.5), v, z) for u, v, z, w in pts],
                              [(w, w * 0.6, w * 0.6) for u, v, z, w in pts], m["socket"], segments=10))
    pts = resample(catmull(BRIDGE, 6), 12)
    objs.append(sweep("bridge", [HP(u, v, z) for u, v, z, w in pts], [(w, w * 0.5, w * 0.6) for u, v, z, w in pts],
                      m["scute"], segments=12, ridge=0.2, end=HP(11.5, 12.9, 4.7)))
    left = []
    pts = resample(catmull(BROW, 6), 14)
    left.append(sweep("brow", [HP(u, v, z) for u, v, z, w in pts], [(w * 0.7, w * 0.3, w * 0.5) for u, v, z, w in pts],
                      m["scute"], segments=12, ridge=0.15, end=HP(11.9, 6.4, 6.7)))
    pts = resample(catmull(CHEEK, 6), 14)
    left.append(sweep("cheek", [HP(u, v, z) for u, v, z, w in pts],
                      [(w * 0.8, w * 0.65, w * 0.6) for u, v, z, w in pts],
                      m["scute"], segments=12, ridge=0.12, end=HP(5.5, 14.3, 3.4)))
    (eu, ev), el, ew, ez, slant = EYE
    a = math.radians(slant)
    ax = Vector((math.cos(a), math.sin(a), 0.0))
    ay = Vector((-math.sin(a), math.cos(a), 0.0))
    up = Vector((0, 0, 1))
    left.append(ellipsoid("eye_socket", HP(eu, ev, ez - 0.75), (el + 0.75, ew + 0.65, 0.95), m["maw"], 10, 20,
                          axes=(ax, ay, up)))
    left.append(ellipsoid("eye", HP(eu, ev, ez), (el, ew, 0.6), m["eye"], 10, 20, axes=(ax, ay, up)))
    left.append(ellipsoid("eye_hot", HP(eu + 0.3, ev + 0.15, ez + 0.32), (el * 0.42, ew * 0.38, 0.3), m["eye_hot"],
                          8, 14,
                          axes=(ax, ay, up)))
    # the upper fangs beside the snout's tip, the side fangs at the maw's corners, the lower jaw's teeth
    left.append(sweep("fang", [HP(8.9, 8.4, 4.9), HP(9.0, 10.2, 4.6), HP(9.3, 12.0, 4.2), HP(9.7, 13.4, 3.8)],
                      [(0.95, 0.75, 0.7), (0.85, 0.66, 0.6), (0.6, 0.48, 0.45), (0.28, 0.24, 0.22)], m["tooth"],
                      segments=10, end=HP(9.9, 14.1, 3.6)))
    left.append(sweep("side_fang", [HP(6.2, 11.0, 3.6), HP(6.4, 12.6, 3.4), HP(6.7, 14.0, 3.0), HP(7.0, 15.2, 2.7)],
                      [(0.8, 0.6, 0.6), (0.7, 0.55, 0.55), (0.45, 0.35, 0.35), (0.2, 0.15, 0.15)], m["tooth"],
                      segments=10, end=HP(7.1, 15.8, 2.6)))
    objs += left + mirrored(left)
    # the lower jaw's three teeth (the sprite's columns 9, 11 and 13 of its row 13), standing up from its front edge
    for i, u in enumerate((9.5, 11.5, 13.5)):
        v = 13.5 + drop + (0.25 if i == 1 else 0.0)
        objs.append(sweep("tooth_%d" % i, [HP(u, v + 0.3, 3.7), HP(u, v, 4.2), HP(u, v - 0.25, 4.6)],
                          [(0.45, 0.4, 0.4), (0.36, 0.32, 0.32), (0.18, 0.16, 0.16)], m["tooth"], segments=8,
                          end=HP(u, v - 0.4, 4.85)))
    objs.append(sweep("chin", [HP(11.5, 13.8 + drop, 4.5), HP(11.5, 15.6 + drop, 4.5), HP(11.5, 17.6 + drop, 3.9)],
                      [(0.9, 0.45, 0.4), (0.8, 0.45, 0.4), (0.4, 0.3, 0.3)], m["scute"], segments=10,
                      end=HP(11.5, 18.4 + drop, 3.5)))
    flatten_below(objs)
    for o in objs:
        o["cap"] = "inside"
    return objs


# --- The whole body ---------------------------------------------------------------------------------------------------


def body_whole(m):
    left = left_wing(m) + shoulder_fan(m) + [horn(m)]
    whole = left + mirrored(left) + [torso(m)] + back(m) + socket(m)
    flatten_below(whole)
    for o in whole:
        o["cap"] = "bone_in" if o.data.materials[0].name.startswith("gry_bone") or \
            o.data.materials[0].name.startswith("gry_claw") else "inside"
    return whole


def export_whole(objs, path):
    copies = []
    for o in objs:
        c = o.copy()
        c.data = o.data.copy()
        bpy.context.scene.collection.objects.link(c)
        copies.append(c)
    shear_to_camera(copies)
    triangulate(copies)
    obj = join(copies, "whole")
    mk.report("whole", [obj], path)
    bpy.data.objects.remove(obj)


# --- Pieces -----------------------------------------------------------------------------------------------------------
BODY_SPRITES = [1, 3, 7, 9, 13, 15, 39, 41, 43, 45, 47, 49, 51, 53, 79, 81, 83, 85, 87, 89]
SHIFTED = {15: 6.0, 53: 6.0}      # the events draw 15 and 53 this far left of the sheet's place (see the docstring)
NECK_PIECES = [("gryphon_neck_91", 91, (-24.5, -0.5)), ("gryphon_neck_93", 93, (-0.5, 23.5))]
NECK_OVERLAP = 2.0                # the neck's pieces hold this much of its foot over the head's top
HEADS = [("gryphon_head", 119), ("gryphon_head_123", 123), ("gryphon_head_121", 121), ("gryphon_head_129", 129)]


def body_pieces():
    out = []
    for n in BODY_SPRITES:
        c0, r0 = (n - 1) % 19 * 12, (n - 1) // 19 * 14
        box = (c0 - 96.5, c0 - 72.5, 14.0 - r0, 42.0 - r0)
        centre = ((box[0] + box[1]) / 2, (box[2] + box[3]) / 2)
        out.append(("gryphon_%d" % n, n, box, (centre[0] - SHIFTED.get(n, 0.0), centre[1]), centre))
    return out


def blank(name):
    """A sprite whose box holds nothing of the model: one tiny triangle under the layer (the renderer refuses a GLB
    with no triangles)."""
    obj = k.mesh_object(name, [(0, 0, -0.2), (0.01, 0, -0.2), (0, 0.01, -0.2)], [(0, 1, 2)])
    return obj


def export_piece(name, sprite, parts, origin, centre, m, options, sheet, results):
    out = mk.outdir(options)
    if not parts:
        parts = [blank(name)]
        parts[0].data.materials.append(m["inside"])
    drop_unused(parts)
    score = None
    if sheet is not None:
        bpy.context.view_layer.update()
        score = mk.compare("%s (0 %d), as the camera sees it" % (name, sprite),
                           mk.coverage(parts, 24, 28, centre=centre), k.sprite_mask(sheet, sprite))
    shear_to_camera(parts)
    mk.transform(parts, Matrix.Translation((-origin[0], -origin[1], 0.0)))
    bpy.context.view_layer.update()
    triangulate(parts)
    obj = join(parts, name)
    obj.data.name = name
    mk.report(name, [obj], os.path.join(out, name + ".glb"))
    results[name] = (score, mk.triangles([obj]), len(obj.data.materials))
    if "preview" in options and options.get("pieces") == "1":
        mk.preview(options["preview"] + name, [obj])
    bpy.data.objects.remove(obj)


def cut_all(whole, box, m):
    bpy.context.view_layer.update()
    parts = []
    for src in whole:
        p = cut(src, box, m[src["cap"]])
        if p is not None:
            parts.append(p)
    return parts


def hide(objs, state):
    for o in objs:
        o.hide_render = state


def build():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    sheet = None
    if "check" in options:
        sheets = options["check"]
        sheet = os.path.join(sheets, "enemy_0.png") if os.path.isdir(sheets) else sheets
    results = {}

    def wanted(group, name):
        return only is None or group in only or name in only

    k.reset()
    m = materials()
    bpy.context.scene.view_settings.view_transform = "Standard"
    if "whole" in options:
        export_whole(body_whole(m), options["whole"] + "body.glb")
        k.reset()
        m = materials()
        export_whole(neck_whole(m), options["whole"] + "neck.glb")
        for frame in (123, 129):
            k.reset()
            m = materials()
            export_whole(head_whole(m, DROP[frame]), options["whole"] + "head_%d.glb" % frame)
        return
    pieces = [p for p in body_pieces() if wanted("body", p[0])]
    if pieces:
        whole = body_whole(m)
        for name, sprite, box, origin, centre in pieces:
            parts = cut_all(whole, (box[0], box[1], box[2], box[3]), m)
            hide(whole, True)
            export_piece(name, sprite, parts, origin, centre, m, options, sheet, results)
            hide(whole, False)
    pieces = [p for p in NECK_PIECES if wanted("neck", p[0])]
    if pieces:
        k.reset()
        m = materials()
        whole = neck_whole(m)
        for name, sprite, (x0, x1) in pieces:
            parts = cut_all(whole, (x0, x1, -14.0 - NECK_OVERLAP, 14.0), m)
            hide(whole, True)
            origin = ((x0 + x1) / 2, 0.0)
            export_piece(name, sprite, parts, origin, origin, m, options, sheet, results)
            hide(whole, False)
    for name, frame in HEADS:
        if not wanted("head", name):
            continue
        k.reset()
        m = materials()
        parts = head_whole(m, DROP[frame])
        export_piece(name, frame, parts, (0.5, 0.0), (0.5, 0.0), m, options, sheet, results)
    print("== summary")
    for name, (score, tris, mats) in results.items():
        print("   %-18s overlap %s  %6d triangles  %2d materials" % (
            name, "%.3f" % score if score is not None else "  -  ", tris, mats))


if __name__ == "__main__":
    build()
