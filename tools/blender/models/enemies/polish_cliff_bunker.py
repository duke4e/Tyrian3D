"""The sentry box at the foot of TORM's grey cliffs (sheet G sprite 153 above 191, 2x2 each: one 24 x 56 picture;
ground layer; enemies 758 and 759 of TORM, BOTANY A, BOTANY B and BONUS, 758 and 1603 of ROOST; the animations
153 155 157 159 161 161 161 159 159 159 157 157 157 155 155 155 153 and 191 193 ... 199 ... 191), polished
(2026-10-19; it replaces wave3_r.py's bunker_whole() and bunker_piece(), rounded boxes and a lathed shutter).
models.cfg: model cliff_bunker_top / cliff_bunker_base (and their frames) ... origin; sprite g 153 cliff_bunker_top
yaw=0, sprite g 191 cliff_bunker_base yaw=0, frame g 155 cliff_bunker_top_155 ... frame g 199 cliff_bunker_base_199.
The levels stack the two exactly: 758 = 153 at (x, y - 28), 759 = 191 at (x, y) (TORM's events 945; BOTANY A puts
two side by side, 24 pixels apart), on the map's cliff tiles (TORM: 576 above 586, the bunker wrecked and burning).

As the sprites and their 4x upscales draw it (columns and rows of the 24 x 56 picture): a steel box at the cliff's
foot (columns 2-21 of rows 17-32), its face a grey frame (columns 3 and 19, rows 18-19 and 31; lit at its top left)
round a window (columns 4-18 of rows 20-30) closed by a dark shutter; dark brackets down its sides (columns 2 and
20-21) with a round hinge knob each (columns 0-1 and 21-22 of rows 23-25); on its top a dark mount (columns 11-18
of rows 13-16) from which a strut runs back up the cliff (column 16, rows 3-13); under it two legs (columns 1-2 and
20, rows 32-40) and a grille of bars (columns 14-19). The frames roll the shutter up (its lower edge, a light lip,
at row 29, 27, 25 and 23; in 161 it is rolled up at the window's top, rows 21-22) on a red eye that glows brighter
as it shows (157: its top, dim; 161: columns 7-16 of rows 23-29, white-yellow in its middle).

The cliff round it (rows 0-16 but the strut and the mount), the rubble and the leaves under it (rows 33-55 but the
legs and the grille) are the map's: TORM's terrain is flat there (the cliff is painted on the ground), so the box
stands on the ground (z = 0) at the cliff's foot, leaning back against it at BOX_TILT so that its face looks up at
the game's slanted camera as the sprites draw it face on; its legs reach forward to the ground, the strut back.

One model per frame and piece: the shutter's lower edge, its roll and the eye's light change; all are cut alike.
The box is built whole (in its face's frame, then turned and placed) and cut along the sprites' edge (y = 0;
polish_arch.py's cut(): the pieces keep the whole's shading across the cut), each piece moved so its sprite's
centre is its origin.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground (z = 0); the
whole's origin is the edge between the two sprites (column c of the picture is x = c + 0.5 - 12, row r is
y = 27.5 - r).

Replaces wave3_r.py's bunker: remove BUNKER_ORIGIN, bpx(), bpy(), bunker_whole() (its @r.whole("bunker", ...)
registration), bunker_piece() and the two r.model("cliff_bunker_...") lines, so that they don't overwrite these
models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette of the whole
and of each piece against the box's own pixels, written below), --preview <prefix>, --only <name,...>.
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
from polish_arch import cut  # noqa: E402  (polish_machine_kit.cut without its material indices shifted twice)

# The box's own pixels in the 24 x 56 picture ('#'): the cliff, rubble and leaves round it left out.
OWN = """
........................
........................
........................
................##......
................##......
................##......
................##......
................##......
................##......
................##......
................##......
................##......
................##......
...........########.....
...........########.....
...........########.....
...........########.....
..####################..
..####################..
..####################..
..####################..
..####################..
..####################..
#######################.
#######################.
#######################.
#######################.
..####################..
..####################..
..####################..
..####################..
..####################..
.####################...
.##............######...
.##............######...
.##............######...
.##............######...
.##............######...
.##............######...
.##............######...
.#.............###......
..#.................#...
........................
""" + "........................\n" * 14

# The pieces: (name, sprite, the rows of the picture it covers (y0, y1)).
PIECES = [("cliff_bunker_top", 153, (0.0, 28.0)), ("cliff_bunker_base", 191, (-28.0, 0.0))]

# The box, in its face's frame: x across, s up the face, n out of it (the face is n = 0). The face's foot (s = 0)
# is at FACE_FOOT (y, z); it leans back BOX_TILT from lying flat, BOX_DEPTH deep.
BOX_X = (-9.1, 8.1)
BOX_TILT = math.radians(30.0)
FACE_FOOT = (-4.0, 4.6)
BOX_H = 16.2                       # the face's height (rows 18-31: 14 pixels seen from above)
BOX_DEPTH = 4.8
FRAME_X, FRAME_S = (-9.0, 8.0), (0.1, 16.1)    # the frame's outer edges
WINDOW_X, WINDOW_S = (-8.0, 7.0), (1.2, 13.9)  # the window (columns 4-18 of rows 20-30)
FRAME_PROUD = 0.7
RECESS = 2.5                       # how deep the window's floor is behind the face
SHUTTER_N = -0.45                  # the shutter's plane, just behind the frame
SLAT = 1.15                        # its slats' pitch
EYE = (-0.5, 6.35, 4.6, 3.6, 1.25)  # the eye on the window's floor: x, s, half-width, half-height, how far it stands
BRACKETS = [(-10.0, -9.1), (8.1, 10.0)]          # the side brackets' x
KNOB_S, KNOB_R = 9.2, 1.05                      # the hinge knobs: up the face, radius
LEGS_X = (-9.9, 8.6)
LEG_FOOT_Y = -12.2
GRILLE_X, GRILLE_BARS = (2.8, 7.4), 3
STRUT = ((4.6, 16.9, -3.6), (4.6, 23.8, 0.0))   # the strut: from the mount (x, s, n) back to the ground (x, y, z)
MOUNT = (-0.6, 6.6, 15.9, 17.7, -4.2, -0.6)      # the mount on the box's top: x0, x1, s0, s1, n0, n1

# The frames: (top model, base model, top sprite, base sprite, the shutter's lower edge up the face (None: rolled
# up), its roll's radius, the eye (palette index, glow), its hot middle (palette index, glow) or None).
FRAMES = [
    ("cliff_bunker_top", "cliff_bunker_base", 153, 191, 2.3, 0.55, ((0x70, 0.0), (0x71, 0.0)), None),
    ("cliff_bunker_top_155", "cliff_bunker_base_193", 155, 193, 4.62, 0.7, ((0x70, 0.0), (0x71, 0.15)), None),
    ("cliff_bunker_top_157", "cliff_bunker_base_195", 157, 195, 6.93, 0.85, ((0x71, 0.4), (0x73, 0.7)), None),
    ("cliff_bunker_top_159", "cliff_bunker_base_197", 159, 197, 9.24, 1.0, ((0x72, 0.7), (0x76, 1.2)), (0x79, 1.6)),
    ("cliff_bunker_top_161", "cliff_bunker_base_199", 161, 199, None, 1.15, ((0x73, 0.9), (0x77, 1.6)), (0x7d, 2.6)),
]


def materials(eye, hot):
    """eye: the lens' (palette index, glow) and its middle's; hot: its heart's, or None."""
    glow = k.level_palette()

    def mat(name, index, metallic=0.5, roughness=0.4):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)

    def lit(name, index, strength, roughness=0.12):
        if strength <= 0:
            return k.material(name, palette=index, metallic=0.1, roughness=roughness)
        return k.material(name, palette=index, metallic=0.0, roughness=roughness, emission=glow[index],
                          emission_strength=strength)
    m = {
        "box": mat("cbunker_box", 0x05, 0.5, 0.42),
        "box_top": mat("cbunker_box_top", 0x06, 0.5, 0.4),
        "frame": mat("cbunker_frame", 0x08, 0.55, 0.3),
        "dark": mat("cbunker_dark", 0x03, 0.45, 0.5),
        "pit": mat("cbunker_pit", 0x01, 0.2, 0.7),
        "shutter": mat("cbunker_shutter", 0x04, 0.45, 0.42),
        "lip": mat("cbunker_lip", 0x08, 0.55, 0.3),
        "roll": mat("cbunker_roll", 0x09, 0.55, 0.26),
        "knob": mat("cbunker_knob", 0x07, 0.6, 0.3),
        "steel": mat("cbunker_steel", 0x05, 0.55, 0.36),
        "eye": lit(f"cbunker_eye_{eye[0][0]:x}", eye[0][0], eye[0][1]),
        "eye_mid": lit(f"cbunker_eye_mid_{eye[1][0]:x}", eye[1][0], eye[1][1]),
    }
    if hot is not None:
        m["hot"] = lit(f"cbunker_eye_hot_{hot[0]:x}", hot[0], hot[1], 0.1)
    return m


# --- The face's frame ------------------------------------------------------------------------------------------

def face_matrix():
    """From the face's frame (x, s, n) to the world: turned about x by BOX_TILT, its foot at FACE_FOOT."""
    y0, z0 = FACE_FOOT
    return Matrix.Translation((0.0, y0, z0)) @ Matrix.Rotation(BOX_TILT, 4, "X")


def to_world(x, s, n):
    return face_matrix() @ Vector((x, s, n))


def placed(obj):
    obj.data.transform(face_matrix())
    return obj


# --- The parts --------------------------------------------------------------------------------------------------

def box(m):
    """The box: a block behind the face, its edges rounded, the window's recess cut into it."""
    x0, x1 = BOX_X
    body = mk.box("box", x0, x1, 0.0, BOX_H, -BOX_DEPTH, 0.0, m["box"])
    wx0, wx1 = WINDOW_X
    ws0, ws1 = WINDOW_S
    cutter = mk.box("recess_cut", wx0, wx1, ws0, ws1, -RECESS, 1.0)
    mk.boolean(body, cutter, "DIFFERENCE")
    mk.cleanup(body)
    mk.bevel(body, 0.35, 2, 35)
    mk.shade(body, 35)

    def pick(c, n):
        if n.z > 0.85 and c.z < -RECESS + 0.05 and wx0 < c.x < wx1 and ws0 < c.y < ws1:
            return m["pit"]
        if wx0 - 0.05 < c.x < wx1 + 0.05 and ws0 - 0.05 < c.y < ws1 + 0.05 and c.z < 0.0:
            return m["dark"]  # the recess' walls
        if n.y > 0.85:
            return m["box_top"]
        return None
    mk.paint(body, pick)
    return placed(body)


def frame(m):
    """The frame round the window: four bars standing proud of the face, bevelled."""
    fx0, fx1 = FRAME_X
    fs0, fs1 = FRAME_S
    wx0, wx1 = WINDOW_X
    ws0, ws1 = WINDOW_S
    outline = [(fx0, fs0), (fx1, fs0), (fx1, fs1), (fx0, fs1)]
    ring = mk.prism("frame", outline, -0.2, FRAME_PROUD, m["frame"])
    hole = mk.prism("frame_hole", [(wx0, ws0), (wx1, ws0), (wx1, ws1), (wx0, ws1)], -1.0, FRAME_PROUD + 1.0)
    mk.boolean(ring, hole, "DIFFERENCE")
    mk.cleanup(ring)
    mk.bevel(ring, 0.25, 2, 35)
    mk.shade(ring, 35)
    placed(ring)
    # A brow over the window: the top bar thicker, standing further out, its front edge rounded.
    brow = mk.box("brow", fx0 + 0.1, fx1 - 0.1, ws1 + 0.2, fs1 - 0.15, 0.2, FRAME_PROUD + 0.65, m["frame"])
    mk.bevel(brow, 0.3, 2, 35)
    mk.shade(brow, 35)
    placed(brow)
    # Rivets in the frame's corners.
    for i, (x, s) in enumerate(((fx0 + 0.5, fs0 + 0.55), (fx1 - 0.5, fs0 + 0.55), (fx0 + 0.5, ws1 - 0.6),
                                (fx1 - 0.5, ws1 - 0.6))):
        rivet = mk.dome(f"rivet{i}", (x, s), (0.3, 0.3, 0.2), FRAME_PROUD - 0.05, m["knob"], 10, 3)
        placed(rivet)
    return ring


def brackets(m):
    """The dark brackets down the box's sides, a hinge knob on each."""
    made = []
    for i, (x0, x1) in enumerate(BRACKETS):
        b = mk.box(f"bracket{i}", x0, x1, -0.3, BOX_H + 0.2, -BOX_DEPTH + 0.6, 0.3, m["dark"])
        mk.bevel(b, 0.25, 2, 35)
        mk.shade(b, 35)
        made.append(placed(b))
        # The knob: a short round boss on the bracket's outside, a cap on it.
        side = -1 if i == 0 else 1
        xa = x0 if side < 0 else x1
        prof = [(0.0, KNOB_R * 0.9), (0.15, KNOB_R), (0.9, KNOB_R), (1.15, KNOB_R * 0.75), (1.25, 0.0)]
        rings = []
        for t, r in prof:
            if r <= 0:
                continue
            rings.append([Vector((xa + side * t, KNOB_S + r * math.cos(2 * math.pi * j / 16),
                                  -1.8 + r * math.sin(2 * math.pi * j / 16))) for j in range(16)])
        knob = k.loft(f"knob{i}", rings, m["knob"], start_point=(xa - side * 0.2, KNOB_S, -1.8),
                      end_point=(xa + side * 1.25, KNOB_S, -1.8))
        k.smooth(knob, 50)
        made.append(placed(knob))
    return made


def window(m, shutter_bottom, roll_r, has_hot):
    """In the window: the eye on its floor; the shutter from its roll at the window's top down to its lip (None:
    rolled up); the roll."""
    made = []
    ex, es, ew, eh, ez = EYE
    # The eye: a red lens on a dark socket ring.
    socket = mk.lathe("eye_socket", [(1.25, -RECESS - 0.1), (1.25, -RECESS + 0.35), (1.08, -RECESS + 0.55),
                                     (0.9, -RECESS + 0.45)], (ex, es), m["dark"], 40, squash=(ew, eh))
    k.smooth(socket, 45)
    made.append(placed(socket))
    eye = mk.dome("eye", (ex, es), (ew, eh, ez), -RECESS + 0.05, m["eye"], 40, 10, power=2.2)
    made.append(placed(eye))
    mid = mk.dome("eye_mid", (ex - 0.15, es + 0.2), (ew * 0.66, eh * 0.66, ez * 0.32), -RECESS + 0.05 + ez * 0.72,
                  m["eye_mid"], 32, 6)
    made.append(placed(mid))
    if has_hot:
        hot = mk.dome("eye_hot", (ex - 0.3, es + 0.35), (ew * 0.32, eh * 0.34, 0.25), -RECESS + 0.05 + ez * 0.93,
                      m["hot"], 24, 5)
        made.append(placed(hot))
    wx0, wx1 = WINDOW_X
    ws0, ws1 = WINDOW_S
    # The roll at the window's top, under the frame's top bar.
    rc = ws1 - roll_r - 0.05
    rings = []
    for xx in (wx0 + 0.05, wx1 - 0.05):
        rings.append([Vector((xx, rc + roll_r * math.cos(2 * math.pi * j / 20),
                              SHUTTER_N - 0.1 + roll_r * math.sin(2 * math.pi * j / 20))) for j in range(20)])
    roll = k.loft("roll", rings, m["roll"])
    k.smooth(roll, 50)
    made.append(placed(roll))
    if shutter_bottom is not None:
        # The shutter: slats from the roll down to the lip, each a shallow rounded strip.
        top = rc
        slats = []
        s = shutter_bottom + 0.45
        while s < top:
            s1 = min(s + SLAT, top)
            slat = mk.box(f"slat{len(slats)}", wx0 + 0.05, wx1 - 0.05, s + 0.06, s1 - 0.06, SHUTTER_N - 0.22,
                          SHUTTER_N + 0.1, m["shutter"])
            mk.bevel(slat, 0.1, 1, 35)
            slats.append(slat)
            s = s1
        for sl in slats:
            mk.shade(sl, 35)
            made.append(placed(sl))
        lip = mk.box("lip", wx0 + 0.05, wx1 - 0.05, shutter_bottom, shutter_bottom + 0.5, SHUTTER_N - 0.3,
                     SHUTTER_N + 0.2, m["lip"])
        mk.bevel(lip, 0.15, 2, 35)
        mk.shade(lip, 35)
        made.append(placed(lip))
    return made


def mount_and_strut(m):
    """The mount on the box's top and the strut from it back up the cliff into the ground, a foot plate there."""
    x0, x1, s0, s1, n0, n1 = MOUNT
    mount = mk.box("mount", x0, x1, s0, s1, n0, n1, m["dark"])
    mk.bevel(mount, 0.4, 2, 35)
    mk.shade(mount, 35)
    placed(mount)
    for i, x in enumerate((x0 + 1.0, x1 - 1.0)):
        p = to_world(x, s1 - 0.2, n1 - 0.9)
        mk.ball(f"mount_bolt{i}", tuple(p), (0.5, 0.5, 0.5), m["knob"], 12, 6)
    (ax, a_s, an), (bx, by, bz) = STRUT
    a = to_world(ax, a_s, an)
    b = Vector((bx, by, bz))
    mid = a.lerp(b, 0.5) + Vector((0, 0, 0.6))
    strut = mk.smooth_tube("strut", [tuple(a) + (0.95,), tuple(mid) + (0.85,), tuple(b + Vector((0, 0, 0.4))) + (0.9,)],
                           m["steel"], 12, iterations=2)
    k.smooth(strut, 60)
    foot = mk.box("strut_foot", bx - 1.6, bx + 1.6, by - 1.4, by + 1.4, 0.0, 0.45, m["dark"])
    mk.bevel(foot, 0.18, 2, 35)
    mk.shade(foot, 35)
    # A collar where the strut meets the mount.
    d = (b - a).normalized()
    collar = mk.tube("strut_collar", [tuple(a + d * 0.6), tuple(a + d * 1.5)], 1.15, m["knob"], 14)
    k.smooth(collar, 40)


def legs_and_grille(m):
    """The legs from the box's foot forward to the ground, and the grille of bars between the right leg and the
    middle."""
    for i, x in enumerate(LEGS_X):
        a = to_world(x, 0.6, -1.2)
        b = Vector((x, LEG_FOOT_Y, 0.35))
        mid = a.lerp(b, 0.5) + Vector((0, 0.3, 0.2))
        leg = mk.smooth_tube(f"leg{i}", [tuple(a) + (0.75,), tuple(mid) + (0.7,), tuple(b) + (0.75,)], m["dark"], 12,
                             iterations=2)
        k.smooth(leg, 60)
        mk.dome(f"leg_pad{i}", (x, LEG_FOOT_Y), (1.25, 1.25, 0.55), 0.0, m["dark"], 16, 4)
    # The grille: two rails and bars between them, from the box's foot forward and down.
    gx0, gx1 = GRILLE_X
    top_a, top_b = to_world(gx0, 0.4, -0.6), to_world(gx1, 0.4, -0.6)
    low_y, low_z = LEG_FOOT_Y + 1.2, 0.7
    rail = mk.smooth_tube("grille_rail", [tuple(top_a) + (0.4,), tuple(top_b) + (0.4,)], m["steel"], 10, iterations=0)
    k.smooth(rail, 50)
    rail2 = mk.smooth_tube("grille_rail2", [(gx0, low_y, low_z, 0.4), (gx1, low_y, low_z, 0.4)], m["steel"], 10,
                           iterations=0)
    k.smooth(rail2, 50)
    for j in range(GRILLE_BARS):
        x = gx0 + (gx1 - gx0) * (j + 0.5) / GRILLE_BARS
        a = to_world(x, 0.4, -0.6)
        bar = mk.smooth_tube(f"grille_bar{j}", [tuple(a) + (0.36,), (x, low_y, low_z, 0.36)], m["steel"], 8,
                             iterations=0)
        k.smooth(bar, 50)


# --- Build ------------------------------------------------------------------------------------------------------

def build_whole(m, shutter_bottom, roll_r, has_hot):
    box(m)
    frame(m)
    brackets(m)
    window(m, shutter_bottom, roll_r, has_hot)
    mount_and_strut(m)
    legs_and_grille(m)
    whole = mk.meshes()
    for obj in whole:
        mk.apply(obj)
        # Nothing reaches below the ground (the legs' and the strut's ends).
        if min(v.co.z for v in obj.data.vertices) < -1e-4:
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=(0, 0, 0),
                                   plane_no=(0, 0, -1), clear_outer=True)
            bm.to_mesh(obj.data)
            bm.free()
    bpy.context.view_layer.update()
    return [o for o in whole if len(o.data.polygons) > 0]


def own_mask(r0=0, rows=56):
    lines = [line for line in OWN.strip("\n").split("\n")]
    mask = [[ch == "#" for ch in line] for line in lines[:56]]
    return mask[r0:r0 + rows]


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options.get("only", "").split(",") if "only" in options else None
    for top_name, base_name, top_sprite, base_sprite, shutter_bottom, roll_r, eye, hot in FRAMES:
        if only and top_name not in only and base_name not in only:
            continue
        k.reset()
        m = materials(eye, hot)
        whole = build_whole(m, shutter_bottom, roll_r, hot is not None)
        print("whole (%s / %s): %d triangles, %d objects" % (top_name, base_name, mk.triangles(whole), len(whole)))
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        if "check" in options and top_sprite == 153:
            mk.compare("whole (G 153 above 191, the box's own pixels)", mk.coverage(whole, 24, 56), own_mask())
        if "preview" in options:
            mk.preview(options["preview"] + top_name + "_whole", whole, size=(24, 56), scale=8, distance=1.4)
        for name, sprite, (y0, y1) in ((top_name, top_sprite, PIECES[0][2]), (base_name, base_sprite, PIECES[1][2])):
            box_xy = (-12.0, 12.0, y0, y1)
            pieces = [p for p in (cut(src, box_xy, m["dark"]) for src in whole) if p is not None]
            mk.transform(pieces, Matrix.Translation((0, -(y0 + y1) / 2, 0)))
            bpy.context.view_layer.update()
            for src in whole:
                src.hide_render = True
            if "check" in options and top_sprite == 153:
                r0 = 0 if y0 >= 0 else 28
                mk.compare("%s (G %d)" % (name, sprite), mk.coverage(pieces, 24, 28), own_mask(r0, 28))
            mk.report(name, pieces, os.path.join(out, name + ".glb"))
            if "preview" in options:
                mk.preview(options["preview"] + name, pieces)
            for obj in pieces:
                bpy.data.objects.remove(obj)
            for src in whole:
                src.hide_render = False


if __name__ == "__main__":
    build()
