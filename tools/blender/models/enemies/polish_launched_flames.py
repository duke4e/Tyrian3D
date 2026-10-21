"""The glowing shots that enemies launch (enemies the player can shoot, made by their launchers: catalog.json lists
none of them; the game drew them as pixelated stand-ins built from the sprite), polished (2026-10-21; nothing replaced:
no generator made models of these sprites, and models.cfg had no lines for them). All 1x1 sprites (12 x 14 cells).
Launched enemies keep their launcher's layer: these come from ground turrets (drawn on the ground enemies' layer,
height 4: the game centres them in height there) and some from sky launchers.

- fire_spindle (sheet J sprite 19; episode 1 enemy 839 and episode 2's 752, 755, 762 and 767, launched by A 91, G 167,
  G 231, G 267 and J 119 in BONUS, BOTANY A, BOTANY B, SOH JIN and TORM, about 130 launchers; flying straight, (-3, 3),
  (4, 0), (-4, 0), (-3, -3) or (3, -3)). The sprite: a fireball, an 8 x 14 ellipse of the fire's ramp 7, a dark red rim
  (0x72-0x75), orange (0x79, 0x7b), yellow (0x7c, 0x7d) and a white-hot heart (0x7e, 0x7f, columns 5-6 of rows 6-7).
  Its frames 19 38 57 76 (three game frames each) are the same flame turned 0, 45, 90 and 135 degrees clockwise (38 and
  76 are each other's mirror images; 57 is 19 turned and cut to the cell's 12 columns): it spins, 15 degrees a game
  frame. The model is one flame along the screen's y, turned by models.cfg (yaw=frames:24:-15: 360/24 degrees every
  step of the animation, which counts game frames, from -15, so each sprite's heading is the middle of its three
  frames; the flame looks the same turned half round, so the jump from 150 back to -15 is the next 15 degrees). spin=
  would turn it as fast (spin=15, degrees per game frame) about the same axis (the world's vertical: render_gpu.c
  turns models about the ground's normal, which the near top-down camera sees as a turn in the screen's plane), but
  from a slot-dependent start (47 degrees a slot), not in step with the sprite's frames.
  Built as a spindle of fire, round in section (an ellipse in plan, 4.05 x 7.1 pixels), two pairs of flame tongues
  twisting round it (ridges along a double helix, so that it looks the same turned half round), painted with the
  sprite's heat (its shades smoothed, polish_flame_drop.py's Heat) in bands of ramp 7, cooler where it turns away
  from the camera and along the tongues' troughs, hotter on their crests; every band glows in its own colour, more the
  hotter (0.1-0.62).

- pulse_ring, pulse_ring_38, _57, _76, _95 (sheet I sprites 19 38 57 76 95; enemy 511 of episodes 1, 3 and 5,
  launched every 30 game frames by SAVARA's airship's gun pods (I 79, 81, 115, 121; SAVARA, SAVARA V, SAVARA Y, about
  180 launchers) and aimed at the player at launch (speed 2)). The sprite: a dark red ring (ramp 4) 12 pixels across,
  its band two pixels wide outside a one-pixel dark line (0x20; 0x01-0x03 in the brighter frames), the hole showing
  the ground, and inside its upper right a crescent of the band's red (from column 4 of row 4 round to column 8 of row
  8) that joins the band at the upper right (rows 3-5), where the band is brightest (it darkens towards the lower
  left). The frames are the same pixels brightening: 19 38 57 76 95 76 57 38 (two game frames each), shades 0-6 of
  the ramp in 19 up to 6-13 and white (0x1f) in 95; nothing else changes, so a frame model each (no other enemy shows
  these sprites), the same mesh with brighter materials and more emission (0-0.1 in 19 up to 0.12-0.6 in 95): the
  ring pulses as the sprite does.
  Built as a ring lying in the ground plane: the band (a rounded section revolved, 3.95-6.05 from the middle), a
  lower dark lip inside it (2.98-4.02) and the crescent, a ledge sloping down into the hole from the lip, widest at
  33 degrees (the upper right), its ends running out at -62 and 128 degrees; where it joins the band (25-70 degrees)
  it reaches out over the lip (sunk there) to the band. Painted as the sprite shades it, in seven classes (frame 19's
  shades 0x40-0x46; each frame gives a class its own palette index): the band brightest at the upper right and
  darkest at the lower left, its inner side brighter than its outer edge, the crescent brightest along its outer edge
  at its middle, the lip dark save where the crescent joins the band, the undersides darker. I 19's damaged graphic
  I 114 (dgr 114, dlevel 1: after a hit of 1) is left to the base model: catalogue enemy 0 also shows I 114 (as a 2x2
  sprite in SAVARA), and frame lines apply to every enemy with a model.

- red_needle (sheet F sprite 171; enemy 501 of episodes 1-3, launched by SAVARA's boss (F 195, F 197, F 234; SAVARA,
  SAVARA V, SAVARA Y, TORM) and aimed at the player at launch (speed 4)). The sprite: a thin needle of ramp 4 (salmon
  red), 12 pixels long and 3 wide, hot in its middle (0x4d) and dark red at its points (0x43, 0x44), its middle column
  a shade or two above its sides. Its frames 171 190 209 228 (three game frames each) are the needle lying across the
  screen, then turned 45, 90 and 135 degrees counter-clockwise (228 is 190 mirrored): it spins the other way, 15
  degrees a game frame (yaw=frames:24:105:ccw: 171 lies across, at 90 degrees; ccw counts down).
  Built as a slender spindle (a lathe, 1.45 pixels at its middle, tapering hard into its points), painted with the
  sprite's heat along its length in seven bands of ramp 4, cooler down its sides, glowing more the hotter (0.08-0.5).

- deli_bolt (sheet C sprite 190; enemy 515 of episodes 1 and 3, launched every 40 game frames by DELI's ground pod
  (C 163, pod_dome) in DELI, New Deli and BONUS, falling (0, 3)). The sprite (6 x 12 pixels, columns 4-9: its middle
  1 pixel right of the cell's): a pink orb (ramp 5, 0x55-0x5c, its highlight at its upper left; columns 5-8 of rows
  7-10) in a light blue cup (ramp 3, 0x3d, 0x3a, 0x39 to its point at row 12), from whose rim two thin prongs (columns
  4 and 9) run up the screen to row 1, dark at their tips (0x34) and lighter down to the cup (0x3d), and a short dark
  spine (columns 6-7 of rows 3-6, 0x33-0x39) behind the orb. Its frames 190 209 228 247 266 285 304 171 (two game
  frames each) flicker the prongs and the spine (a shade or two, a pixel longer or shorter) and the orb's highlight:
  a shimmer the model's glow covers, one model (no frame models).
  Built as a cup lathed round the bolt's axis (its mouth up the screen, round the orb's lower half), the orb in it,
  the two prongs tapering from the cup's rim to their tips and the spine, all painted along their length with the
  sprite's shades of ramp 3 in bands, glowing a little near the cup; the orb glows in its own pink (0.35-0.5).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the origin at the
sprite's centre (pixel 6, 7 of the cell: column c is x = c + 0.5 - 6, row r is y = 6.5 - r). The game centres these
models in height (keep the frame models' bounds equal: the ring's frames share one mesh).

models.cfg (new): model fire_spindle enemies/fire_spindle.glb, sprite j 19 fire_spindle yaw=frames:24:-15
glow=12:0.3; model pulse_ring (and pulse_ring_38, _57, _76, _95) enemies/pulse_ring*.glb, sprite i 19 pulse_ring yaw=0
glow=14:0.15, frame i 38 pulse_ring_38, frame i 57 pulse_ring_57, frame i 76 pulse_ring_76, frame i 95 pulse_ring_95;
model red_needle enemies/red_needle.glb, sprite f 171 red_needle yaw=frames:24:105:ccw glow=8:0.25; model deli_bolt
enemies/deli_bolt.glb, sprite c 190 deli_bolt yaw=0 glow=9:0.3:90:1:2 (the orb).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes against
each frame of the sprite, the model turned as the frame's heading and moved to the frame's own centre), --preview
<prefix>, --only <name,...>.
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
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_flame_drop import Heat  # noqa: E402

TOP = 7.0  # the y of a 1x1 sprite's top edge


def grid(art):
    """Rows of palette indices (ints) or None from art written as two hex digits a pixel, '..' transparent."""
    return [[None if t == ".." else int(t, 16) for t in line.split()] for line in art.strip("\n").splitlines()]


def shades(rows, ramp):
    """The shades (index & 15) of the pixels of one ramp, None elsewhere."""
    return [[None if i is None or i >> 4 != ramp else i & 15 for i in row] for row in rows]


def smoothstep(e0, e1, x):
    return mk.smoothstep(e0, e1, x)


def vertex_normals(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.normal_update()
    normals = [v.normal.copy() for v in bm.verts]
    bm.free()
    return normals


def lit(name, index, strength, roughness=0.3, metallic=0.0, emission_index=None):
    """A palette material glowing in its own colour (or another index's)."""
    pal = k.level_palette()
    return k.material(name, palette=index, metallic=metallic, roughness=roughness,
                      emission=pal[index if emission_index is None else emission_index] if strength > 0 else None,
                      emission_strength=strength)


def revolve(name, section, phis, closed=True, mat=None):
    """A surface turned about the z axis: section(phi) -> [(r, z), ...], a closed loop of the same count for every phi
    (counter-clockwise in r, z), at each of phis (radians, increasing). closed: the last joins the first; else the ends
    are closed by fans to their sections' middles."""
    verts, starts = [], []
    n = len(section(phis[0]))
    for phi in phis:
        starts.append(len(verts))
        c, s = math.cos(phi), math.sin(phi)
        verts += [(r * c, r * s, z) for r, z in section(phi)]
    faces = []
    m = len(phis)
    for i in range(m if closed else m - 1):
        a, b = starts[i], starts[(i + 1) % m]
        faces += [(a + j, a + (j + 1) % n, b + (j + 1) % n, b + j) for j in range(n)]
    if not closed:
        for i, flip in ((0, True), (m - 1, False)):
            a = starts[i]
            centre = Vector((0, 0, 0))
            for j in range(n):
                centre += Vector(verts[a + j])
            verts.append(tuple(centre / n))
            c = len(verts) - 1
            faces += [((a + (j + 1) % n, a + j, c) if flip else (a + j, a + (j + 1) % n, c)) for j in range(n)]
    obj = k.mesh_object(name, verts, faces, mat)
    k.recalc_normals(obj)
    return obj


def superellipse(cx, cz, hw, hh, count, power=2.0, start=0.0):
    """A closed loop in (r, z): a superellipse round (cx, cz), counter-clockwise."""
    pts = []
    for j in range(count):
        a = start + 2 * math.pi * j / count
        c, s = math.cos(a), math.sin(a)
        pts.append((cx + math.copysign(abs(c) ** (2 / power), c) * hw,
                    cz + math.copysign(abs(s) ** (2 / power), s) * hh))
    return pts


# --- The checks ------------------------------------------------------------------------------------------------------

def mask_centre(m):
    """The middle of a mask's covered box, in model coordinates (x, y) of its cell."""
    rows = [r for r, row in enumerate(m) if any(row)]
    cols = [c for c in range(len(m[0])) if any(row[c] for row in m)]
    return (cols[0] + cols[-1] + 1) / 2 - len(m[0]) / 2, len(m) / 2 - (rows[0] + rows[-1] + 1) / 2


def vertex_bounds(objects, matrix=Matrix.Identity(4)):
    """The objects' bounds from their vertices (bound_box lags behind mesh edits), seen through matrix."""
    points = [matrix @ (obj.matrix_world @ v.co) for obj in objects for v in obj.data.vertices]
    return (Vector([min(p[i] for p in points) for i in range(3)]),
            Vector([max(p[i] for p in points) for i in range(3)]))


def check_frames(objects, sheet, frames, move_to_frame=True, large=False):
    """The silhouettes against frames [(sprite, turn matrix, label)]: the model turned as the frame's heading and (for
    turning sprites, whose pixel grids put their middles half a pixel apart) moved to the frame's own middle."""
    scores = []
    w, h = (24, 28) if large else (12, 14)
    for sprite, turn, label in frames:
        m = k.sprite_mask(sheet, sprite, large=large)
        shift = Matrix.Identity(4)
        if move_to_frame:
            low, high = vertex_bounds(objects, turn)
            mx, my = mask_centre(m)
            shift = Matrix.Translation((mx - (low.x + high.x) / 2, my - (low.y + high.y) / 2, 0))
        # Copies turned and moved (the models themselves stay as built, so the output is the same with --check).
        copies = []
        for obj in objects:
            copy = obj.copy()
            copy.data = obj.data.copy()
            bpy.context.scene.collection.objects.link(copy)
            copies.append(copy)
        mk.transform(copies, shift @ turn)
        bpy.context.view_layer.update()
        scores.append(mk.compare(label, mk.coverage(copies, w, h), m))
        for copy in copies:
            mesh = copy.data
            bpy.data.objects.remove(copy)
            bpy.data.meshes.remove(mesh)
    return scores


def turn(degrees_clockwise):
    """A heading on screen (clockwise, as models.cfg's yaw) as a rotation about +Z."""
    return Matrix.Rotation(math.radians(-degrees_clockwise), 4, "Z")


# --- J 19: the spinning fireball --------------------------------------------------------------------------------------

FIRE_19 = """
.. .. .. .. 72 75 75 72 .. .. .. ..
.. .. .. 72 75 79 79 75 72 .. .. ..
.. .. .. 75 79 7b 7b 79 75 .. .. ..
.. .. .. 77 7b 7c 7c 7b 77 .. .. ..
.. .. 73 79 7c 7d 7d 7c 79 73 .. ..
.. .. 75 7b 7d 7e 7e 7d 7b 75 .. ..
.. .. 75 7b 7e 7f 7f 7e 7b 75 .. ..
.. .. 75 7b 7e 7f 7f 7e 7b 75 .. ..
.. .. 75 7b 7d 7e 7e 7d 7b 75 .. ..
.. .. 73 79 7c 7d 7d 7c 79 73 .. ..
.. .. .. 77 7b 7c 7c 7b 77 .. .. ..
.. .. .. 75 79 7b 7b 79 75 .. .. ..
.. .. .. 72 75 79 79 75 72 .. .. ..
.. .. .. .. 72 75 75 72 .. .. .. ..
"""

# The spindle: its half-width and half-length (an ellipse in plan), the half-depths above and below its axis (times
# the half-width), the rings along it and the points round each.
SPINDLE = (4.05, 7.1)
SPINDLE_DEPTH = (0.84, 0.72)
SPINDLE_RINGS, SPINDLE_SEGMENTS = 30, 28
# The tongues: how many round it (even, so that it looks the same turned half round), the twist (radians a pixel
# along y), how far their crests stand out and their troughs sink (pixels, at the middle; nothing at the ends), and
# how much hotter their crests are (shades).
TONGUES, TWIST, TONGUE_LIFT, TONGUE_HEAT = 4, 0.3, 0.2, 1.8
# The heat: the sprite's shades scaled (its smoothed peak is lower than its pixels'), the sides turning away from the
# camera cooler (heat times SIDE_COOL[0] + SIDE_COOL[1] * smoothstep(SIDE_COOL[2], SIDE_COOL[3], normal z)).
FIRE_GAIN = 1.04
SIDE_COOL = (0.42, 0.58, -0.35, 0.6)
# The bands: (lowest heat, palette index, emission strength in the palette colour), ramp 7 from the rim's dark red to
# white; low glows (the game's bloom and models.cfg's glow add on top).
FIRE_BANDS = [(-99.0, 0x72, 0.1), (2.5, 0x73, 0.12), (4.0, 0x75, 0.16), (6.0, 0x77, 0.22), (8.0, 0x79, 0.28),
              (10.0, 0x7b, 0.36), (11.5, 0x7c, 0.43), (12.6, 0x7d, 0.5), (13.8, 0x7e, 0.56), (14.7, 0x7f, 0.62)]


def fire_spindle(name):
    a, b = SPINDLE
    heat = Heat(shades(grid(FIRE_19), 7), TOP, sigma=(0.6, 0.6))
    ys = [-b + 2 * b * (i + 0.5) / SPINDLE_RINGS for i in range(SPINDLE_RINGS)]
    ys = sorted(set(ys) | {-b + d for d in (0.06, 0.18)} | {b - d for d in (0.06, 0.18)})
    rings, info = [], []
    for y in ys:
        w = a * math.sqrt(max(0.0, 1 - (y / b) ** 2))
        env = max(0.0, 1 - (y / b) ** 2)
        ring = []
        for j in range(SPINDLE_SEGMENTS):
            t = 2 * math.pi * j / SPINDLE_SEGMENTS
            c, s = math.cos(t), math.sin(t)
            depth = SPINDLE_DEPTH[0] if s >= 0 else SPINDLE_DEPTH[1]
            ridge = math.cos(TONGUES * (t - TWIST * y))
            # out along the section's normal (the ellipse's, in x and z)
            nx, nz = c / a, s / (a * depth)
            nl = math.hypot(nx, nz) or 1.0
            lift = TONGUE_LIFT * env * ridge
            ring.append(Vector((w * c + lift * nx / nl, y, w * s * depth + lift * nz / nl)))
            info.append(ridge * env)
        rings.append(ring)
    obj = k.loft(name, rings, None, start_point=(0, -b, 0), end_point=(0, b, 0))
    info += [0.0, 0.0]  # the end points
    normals = vertex_normals(obj)
    values = []
    for v, n, ridge in zip(obj.data.vertices, normals, info):
        h = heat(v.co.x, v.co.y) * FIRE_GAIN
        h *= SIDE_COOL[0] + SIDE_COOL[1] * smoothstep(SIDE_COOL[2], SIDE_COOL[3], n.z)
        h += TONGUE_HEAT * ridge * smoothstep(-0.2, 0.4, n.z)
        values.append(h)
    mats = [(lowest, lit(f"fire19_{index:02x}", index, glow, roughness=0.3 if index < 0x79 else 0.24))
            for lowest, index, glow in FIRE_BANDS]
    band_split(obj, values, mats)
    k.smooth(obj, 75)
    return [obj]


def fire_frames():
    # 19 as built (heading 0); 38 turned 45 degrees clockwise, 57 90, 76 135.
    return [(19, turn(0), "J 19"), (38, turn(45), "J 38"), (57, turn(90), "J 57"), (76, turn(135), "J 76")]


# --- I 19: the pulsing ring -------------------------------------------------------------------------------------------

# The band: the middle of its section (radius, z), half-width and half-height, superellipse power; the dark lip
# inside it (the same; sunk by LIP_SINK and flattened where the crescent joins the band); the crescent: its ends
# (degrees from +x, counter-clockwise), its outer radius (tucked under the lip; out to the band's where it joins it),
# its widest (pixels inward from there, at the middle of its ends) and its section's heights (inner edge, outer edge,
# bottom).
BAND = (5.0, 0.15, 1.05, 0.95, 2.6)
LIP = (3.5, -0.1, 0.52, 0.42, 2.4)
LIP_SINK = 0.35
CRESCENT_ENDS = (-62.0, 128.0)
CRESCENT_OUTER, CRESCENT_JOIN, CRESCENT_WIDE = 3.05, 4.0, 1.65
CRESCENT_Z = (0.12, 0.78, -0.4)
# Where the crescent joins the band (no dark line between them): degrees, half-width, soft edge.
MERGE = (47.0, 22.0, 14.0)
RING_SEGMENTS, BAND_POINTS, LIP_POINTS, CRESCENT_STEPS = 40, 12, 8, 20
# The painting, as the sprite shades the ring: brightest at the upper right (RING_BRIGHT_AT degrees), darkest at the
# lower left (the band's value RING_BASE + RING_SWING * cos(angle - RING_BRIGHT_AT)), its inner side brighter than
# its outer edge (RING_INNER either way across the band), the underside darker; the crescent brightest along its
# outer edge at its middle (CRESCENT_PAINT: its peak, the share its inner edge keeps), the lip dark. The classes are
# frame 19's shades 0x40-0x46 (values -1.5 to 5.5 and up; below -1.5 the lip). Each frame's palette index and
# emission strength per class ("lip" first).
RING_BASE, RING_SWING, RING_BRIGHT_AT, RING_INNER = 2.6, 2.0, 40.0, 1.2
CRESCENT_PAINT = (6.3, 0.5)
RING_BORDERS = [-99.0, -1.5, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5]
RING_FRAMES = {
    19: [(0x20, 0.0), (0x40, 0.0), (0x41, 0.0), (0x42, 0.02), (0x43, 0.04), (0x44, 0.06), (0x45, 0.08), (0x46, 0.1)],
    38: [(0x01, 0.0), (0xa1, 0.02), (0x42, 0.05), (0x43, 0.08), (0x45, 0.11), (0x46, 0.14), (0x48, 0.17), (0x4a, 0.2)],
    57: [(0x02, 0.0), (0x12, 0.05), (0x43, 0.1), (0x45, 0.15), (0x48, 0.2), (0x49, 0.25), (0x4a, 0.3), (0x4c, 0.35)],
    76: [(0x03, 0.0), (0x14, 0.08), (0x45, 0.15), (0x48, 0.22), (0x4a, 0.3), (0x4b, 0.37), (0x4d, 0.44), (0x4e, 0.5)],
    95: [(0x03, 0.0), (0x46, 0.12), (0x48, 0.2), (0x4a, 0.3), (0x4d, 0.4), (0x4d, 0.45), (0x1f, 0.5), (0x1f, 0.58)],
}


def angle_off(a, b):
    return (a - b + 180.0) % 360.0 - 180.0


def crescent_bump(phi_deg):
    """0 at the crescent's ends, 1 at its middle."""
    a0, a1 = CRESCENT_ENDS
    t = (phi_deg - a0) / (a1 - a0)
    if t <= 0 or t >= 1:
        return 0.0
    return math.sin(math.pi * t) ** 0.9


def merge_at(phi_deg):
    return smoothstep(MERGE[1] + MERGE[2], MERGE[1], abs(angle_off(phi_deg, MERGE[0])))


def ring_meshes(prefix):
    phis = [2 * math.pi * i / RING_SEGMENTS for i in range(RING_SEGMENTS)]
    cx, cz, hw, hh, power = BAND
    band = revolve(f"{prefix}_band", lambda phi: superellipse(cx, cz, hw, hh, BAND_POINTS, power), phis)
    lx, lz, lw, lh, lpower = LIP

    def lip_section(phi):
        m = merge_at(math.degrees(phi))
        return superellipse(lx, lz - LIP_SINK * m, lw, lh * (1 - 0.5 * m), LIP_POINTS, lpower)
    lip = revolve(f"{prefix}_lip", lip_section, phis)
    a0, a1 = CRESCENT_ENDS
    cphis = [math.radians(a0 + (a1 - a0) * (0.012 + 0.976 * i / (CRESCENT_STEPS - 1))) for i in range(CRESCENT_STEPS)]
    z_in, z_out, z_bottom = CRESCENT_Z

    def crescent_section(phi):
        deg = math.degrees(phi)
        bump = crescent_bump(deg)
        w = max(0.06, CRESCENT_WIDE * bump)
        r_out = CRESCENT_OUTER + (CRESCENT_JOIN - CRESCENT_OUTER) * merge_at(deg)
        r_in = CRESCENT_OUTER - w
        f = max(0.05, bump) ** 0.5
        top_in, top_out, bottom = z_in * f, z_out * f + 0.02, z_bottom * f - 0.02
        pts = [(r_out - (r_out - r_in) * i / 3, bottom) for i in range(3)]  # the bottom, outer edge inwards
        for i in range(4):  # round the inner edge, from below to above
            a = math.pi * (1.5 - i / 3.0)
            pts.append((r_in + 0.12 * w * (1 + math.cos(a)),
                        (bottom + top_in) / 2 - (top_in - bottom) / 2 * math.sin(a)))
        for i in range(1, 5):  # the top, sloping up to the outer edge
            u = i / 4
            pts.append((r_in + (r_out - r_in) * u, top_in + (top_out - top_in) * u ** 0.6))
        pts.append((r_out, (top_out + bottom) / 2))
        return pts
    crescent = revolve(f"{prefix}_crescent", crescent_section, cphis, closed=False)
    return band, lip, crescent


def band_paint(phi_deg, r):
    return (RING_BASE + RING_SWING * math.cos(math.radians(phi_deg - RING_BRIGHT_AT)) +
            RING_INNER * max(-1.0, min(1.0, (BAND[0] - r) / BAND[2])))


def ring_values(obj, part):
    """Each vertex's painting value (the classes of RING_BORDERS): see RING_BASE."""
    values = []
    for v, n in zip(obj.data.vertices, vertex_normals(obj)):
        x, y = v.co.x, v.co.y
        phi = math.degrees(math.atan2(y, x))
        r = math.hypot(x, y)
        if part == "band":
            value = band_paint(phi, r)
        elif part == "lip":
            m = merge_at(phi)
            value = -5.0 + (band_paint(phi, 4.0) + 5.0) * m
        else:
            bump = crescent_bump(phi)
            r_in = CRESCENT_OUTER - CRESCENT_WIDE * bump
            r_out = CRESCENT_OUTER + (CRESCENT_JOIN - CRESCENT_OUTER) * merge_at(phi)
            out = max(0.0, min(1.0, (r - r_in) / max(r_out - r_in, 1e-3)))
            peak, keep = CRESCENT_PAINT
            value = peak * bump ** 0.7 * (keep + (1 - keep) * out) - 0.5
        if n.z < 0.0:
            value -= 2.5 * smoothstep(0.0, -0.6, n.z)
        values.append(value)
    return values


def pulse_ring(name, frame):
    mats = [(lowest, lit(f"ring{frame}_{i}", index, glow, roughness=0.6 if i == 0 else 0.32 if i < 4 else 0.26))
            for i, (lowest, (index, glow)) in enumerate(zip(RING_BORDERS, RING_FRAMES[frame]))]
    objects = []
    for obj, part in zip(ring_meshes(name), ("band", "lip", "crescent")):
        band_split(obj, ring_values(obj, part), mats)
        k.smooth(obj, 50 if part == "crescent" else 70)
        objects.append(obj)
    return objects


# --- F 171: the spinning red needle -----------------------------------------------------------------------------------

# The needle: half-length, half-width at its middle, where its points begin to taper (|y|) and how (r = width *
# ((length - |y|) / (length - NEEDLE_TAPER[0])) ^ NEEDLE_TAPER[1]: an ogive into a sharp point), its depth (times the
# width), the rings and the points round each.
NEEDLE = (6.3, 1.45)
NEEDLE_TAPER = (3.5, 0.62)
NEEDLE_SQUASH = 0.9
NEEDLE_RINGS, NEEDLE_SEGMENTS = 26, 14
# The heat along it (|y|, the middle column's shade: F 209's 0x4d in its middle rows down to 0x44 at its points), the
# sides cooler (shades per unit of 1 - normal z), the underside a dark red.
NEEDLE_HEAT = [(0.0, 13.2), (1.0, 12.6), (2.0, 10.6), (3.5, 8.0), (4.5, 6.1), (5.5, 4.0), (6.2, 3.2)]
NEEDLE_SIDE = 2.2
NEEDLE_BANDS = [(-99.0, 0x43, 0.08), (4.0, 0x45, 0.12), (6.0, 0x47, 0.18), (8.0, 0x49, 0.25), (9.5, 0x4a, 0.3),
                (10.5, 0x4b, 0.37), (12.0, 0x4d, 0.48)]


def needle_heat(y):
    y = abs(y)
    for (y0, h0), (y1, h1) in zip(NEEDLE_HEAT, NEEDLE_HEAT[1:]):
        if y <= y1:
            return h0 + (h1 - h0) * smoothstep(y0, y1, y)
    return NEEDLE_HEAT[-1][1]


def red_needle(name):
    length, width = NEEDLE
    ys = [-length + 2 * length * i / NEEDLE_RINGS for i in range(1, NEEDLE_RINGS)]
    ys = sorted(set(ys) | {-length + d for d in (0.08, 0.25)} | {length - d for d in (0.08, 0.25)})
    def radius(y):
        if abs(y) <= NEEDLE_TAPER[0]:
            return width * (1 - 0.04 * (abs(y) / NEEDLE_TAPER[0]) ** 2)
        return width * 0.96 * max(0.0, (length - abs(y)) / (length - NEEDLE_TAPER[0])) ** NEEDLE_TAPER[1]
    profile = [(y, radius(y)) for y in ys]
    rings = [k.ring(y, r, r * NEEDLE_SQUASH, NEEDLE_SEGMENTS) for y, r in profile]
    obj = k.loft(name, rings, None, start_point=(0, -length, 0), end_point=(0, length, 0))
    values = []
    for v, n in zip(obj.data.vertices, vertex_normals(obj)):
        h = needle_heat(v.co.y) - NEEDLE_SIDE * (1 - max(n.z, 0.0))
        if n.z < -0.2:
            h = min(h, 3.0)
        values.append(h)
    mats = [(lowest, lit(f"needle_{index:02x}", index, glow, roughness=0.3)) for lowest, index, glow in NEEDLE_BANDS]
    band_split(obj, values, mats)
    k.smooth(obj, 70)
    return [obj]


def needle_frames():
    # 209 as built (along y); 171 across (90), 190 45 degrees counter-clockwise from 209's... the sprite turns
    # counter-clockwise from 171: 171 (90), 190 (45), 209 (0), 228 (-45).
    return [(171, turn(90), "F 171"), (190, turn(45), "F 190"), (209, turn(0), "F 209"), (228, turn(-45), "F 228")]


# --- C 190: DELI's falling bolt ---------------------------------------------------------------------------------------

# The bolt's axis (x; the sprite's columns 4-9) and the height of its middle; the orb (y of its middle, radius); the cup
# (its profile round the axis: (y, outer radius), from its point up to its rim, and its wall); the prongs (x either
# side of the axis, from the cup's rim at PRONG_Y[0] up to their tips at PRONG_Y[1], radius at the root and the tip,
# their lean up towards the camera); the spine (from the orb up to its tip, its radius at the root and the tip).
BOLT_X, BOLT_Z = 1.0, 0.0
ORB_Y, ORB_R, ORB_RISE = -2.0, 1.95, 0.1
CUP = [(-6.05, 0.0), (-5.9, 0.55), (-5.5, 1.1), (-5.0, 1.62), (-4.4, 2.08), (-3.7, 2.42), (-2.9, 2.6), (-2.1, 2.62),
       (-1.3, 2.58), (-0.6, 2.5), (0.0, 2.42), (0.45, 2.36)]
CUP_WALL, CUP_ARC = 0.42, (188.0, 352.0)
PRONG_DX, PRONG_Y, PRONG_R, PRONG_LEAN = 2.5, (-3.4, 6.15), (0.5, 0.24), 0.6
SPINE_Y, SPINE_R = (-0.2, 4.1), (0.95, 0.28)
# The paint along y (the sprite's shades of ramp 3 down the prongs: 0x34 at row 1 to 0x3d at row 9), the bands
# (lowest shade, palette index, emission), the orb's bands (heat: its highlight at the upper left).
PRONG_SHADES = [(6.2, 3.6), (5.5, 4.0), (4.5, 5.0), (3.5, 6.0), (2.5, 7.0), (1.5, 8.2), (0.5, 10.0), (-0.5, 11.0),
                (-1.5, 12.0), (-2.5, 13.0), (-3.5, 11.0)]
SPINE_SHADES = [(4.2, 2.8), (3.5, 3.2), (2.5, 4.0), (1.5, 6.0), (0.5, 8.6), (-0.3, 10.0)]
BLUE_BANDS = [(-99.0, 0x33, 0.0), (3.5, 0x34, 0.0), (4.5, 0x36, 0.03), (6.5, 0x38, 0.07), (8.5, 0x3a, 0.12),
              (10.5, 0x3b, 0.17), (11.5, 0x3c, 0.22), (12.5, 0x3d, 0.28)]
ORB_BANDS = [(-99.0, 0x55, 0.3), (0.3, 0x57, 0.36), (0.55, 0x59, 0.42), (0.75, 0x5a, 0.46), (0.9, 0x5c, 0.5)]


def along(points, y):
    """Linear in a table [(y, value)] ordered by decreasing y."""
    if y >= points[0][0]:
        return points[0][1]
    for (y0, v0), (y1, v1) in zip(points, points[1:]):
        if y >= y1:
            return v0 + (v1 - v0) * (y0 - y) / (y0 - y1)
    return points[-1][1]


def cradle(name, profile, wall, arc, segments=14):
    """The cup: the lower part of a bowl lathed round the bolt's axis (along y), open towards the camera and up the
    screen: its sections arcs from arc[0] round below to arc[1] (degrees in the x-z plane, 0 = +x, 90 = towards the
    camera), profile [(y, outer radius)] from its point up, its wall `wall` thick."""
    a0, a1 = (math.radians(a) for a in arc)
    rings = []
    for y, r in profile:
        r = max(r, 0.04)
        inner = max(r - wall, 0.02)
        outer_arc = [a0 + (a1 - a0) * j / segments for j in range(segments + 1)]
        pts = [Vector((BOLT_X + r * math.cos(a), y, BOLT_Z + r * math.sin(a))) for a in outer_arc]
        pts += [Vector((BOLT_X + inner * math.cos(a), y, BOLT_Z + inner * math.sin(a))) for a in reversed(outer_arc)]
        rings.append(pts)
    return k.loft(name, rings, None)


def deli_bolt(name):
    blue = [(lowest, lit(f"bolt_{index:02x}", index, glow, roughness=0.28, metallic=0.15))
            for lowest, index, glow in BLUE_BANDS]
    objects = [cradle("cup", CUP, CUP_WALL, CUP_ARC)]
    # The prongs: tapered tubes from the rim up, leaning a little up towards the camera.
    for side in (-1, 1):
        count = 14
        path, radii = [], []
        for i in range(count):
            u = i / (count - 1)
            y = PRONG_Y[0] + (PRONG_Y[1] - PRONG_Y[0]) * u
            path.append((BOLT_X + side * PRONG_DX * (1 - 0.06 * u), y, BOLT_Z + PRONG_LEAN * u ** 1.5))
            radii.append(PRONG_R[0] + (PRONG_R[1] - PRONG_R[0]) * u ** 1.2)
        objects.append(mk.tube(f"prong{side}", path, PRONG_R[0], None, segments=10, radii=radii))
    # The spine: a tapered rod behind the orb.
    count = 10
    path = [(BOLT_X, SPINE_Y[0] + (SPINE_Y[1] - SPINE_Y[0]) * i / (count - 1), BOLT_Z + 0.35) for i in range(count)]
    radii = [SPINE_R[0] + (SPINE_R[1] - SPINE_R[0]) * (i / (count - 1)) ** 1.1 for i in range(count)]
    objects.append(mk.tube("spine", path, SPINE_R[0], None, segments=10, radii=radii))
    for obj in objects:
        is_spine = obj.name.startswith("spine")
        values = []
        for v, n in zip(obj.data.vertices, vertex_normals(obj)):
            shade = along(SPINE_SHADES if is_spine else PRONG_SHADES, v.co.y)
            if obj.name == "cup":
                shade = 12.0 + 1.0 * smoothstep(-0.2, 0.7, n.z) - 2.5 * smoothstep(-3.5, -5.8, v.co.y)
            shade -= 2.0 * smoothstep(0.0, -0.7, n.z)
            values.append(shade)
        band_split(obj, values, blue)
        k.smooth(obj, 60)
    # The orb: glowing pink, its highlight at the upper left (as the sprite's 0x5c), darker low on the right.
    orb = mk.ball("orb", (BOLT_X, ORB_Y, BOLT_Z + ORB_RISE), (ORB_R, ORB_R, ORB_R), None, segments=24, rings=12)
    pink = [(lowest, lit(f"orb_{index:02x}", index, glow, roughness=0.2)) for lowest, index, glow in ORB_BANDS]
    values = []
    light = Vector((-0.5, 0.45, 0.74)).normalized()
    for v, n in zip(orb.data.vertices, vertex_normals(orb)):
        values.append(0.5 + 0.5 * n.dot(light))
    band_split(orb, values, pink)
    k.smooth(orb, 70)
    objects.append(orb)
    return objects


# --- Build ------------------------------------------------------------------------------------------------------------

MODELS = [
    ("fire_spindle", "J", lambda name: fire_spindle(name), fire_frames),
    ("pulse_ring", "I", lambda name: pulse_ring(name, 19), lambda: [(19, turn(0), "I 19")]),
    ("pulse_ring_38", "I", lambda name: pulse_ring(name, 38), lambda: [(38, turn(0), "I 38")]),
    ("pulse_ring_57", "I", lambda name: pulse_ring(name, 57), lambda: [(57, turn(0), "I 57")]),
    ("pulse_ring_76", "I", lambda name: pulse_ring(name, 76), lambda: [(76, turn(0), "I 76")]),
    ("pulse_ring_95", "I", lambda name: pulse_ring(name, 95), lambda: [(95, turn(0), "I 95")]),
    ("red_needle", "F", lambda name: red_needle(name), needle_frames),
    ("deli_bolt", "C", lambda name: deli_bolt(name), lambda: [(190, turn(0), "C 190")]),
]
TURNING = {"fire_spindle", "red_needle"}


def build():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    for name, sheet, make, frames in MODELS:
        if only is not None and name not in only:
            continue
        k.reset()
        objects = make(name)
        triangulate(objects)
        bpy.context.view_layer.update()
        if "check" in options:
            check_frames(objects, os.path.join(options["check"], f"enemy_{sheet}.png"), frames(),
                         move_to_frame=name in TURNING)
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, objects, os.path.join(mk.outdir(options), name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, objects, size=(12, 14), scale=32, distance=0.42)


if __name__ == "__main__":
    build()
