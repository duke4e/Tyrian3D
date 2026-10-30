"""The Protron's pearls (shots sheet sprites 225, 226, 227, 228, 244, 247 and 166; shots2 sheet sprites 101-108 and
82-87; all 1x1: 12 x 14 cells), modelled (2026-10-29, round 2 of the energy shots' models, after the Pulse-Cannon's
pilot: until then they were drawn as their sprites with volume and the automatic glow).

Who fires them (weapons as the item data numbers them):
  Protron front (port 13, the first shop, 600): pale pearls straight up and fanned out, 225 at power 1-8, 244 at 6-11
    and 226 at 11 (two to eight a volley, every 4-6 frames).
  Protron rear (port 12, shop 1:2): 227 at power 1, 3-6, 8, 10; the turning pair shots2 101-108 at 2 and from 4, the
    turning triangle shots2 82-87 from 8 (fanned out sideways and back); its second mode circles them round the ship
    (227, then 101-108, 82-87). Protron Z (port 6): 227 (with the green orb, shot_green_orb). Protron Wave (port 34):
    228 (a blue 227), 101-108, 82-87. The special Protron Field: 227 and 228.
  Sidekicks: Protron Cannon Indigo and Beno Protron System -B- 247 (a blue 226), Protron Cannon Tangerine 166 (a blue
    244); the second player's charge cannon and linked turret on rear port 12 (101-108, 82-87).
  Enemies: weapons 78 and 80 (225: EYESPY, UNDERDELI, DREAD-NOT), 141 and 142 (226: CAMANIS, ICE EXIT, BRAINIAC,
    ICESECRET, SAVARA), 134, 135, 37, 38 and 83 (227 and 244: CAMANIS, ICE EXIT, ICESECRET, BRAINIAC, SAVARA), 2, 3 and
    4 (episode 4's data: DREAD-NOT, APPROACH, SAVARA IV), 77 (244: ?TUNNEL?, BRAINIAC, HARVEST, LAVA RUN, NOSE DRIP,
    UNDERDELI), 119 and 120 (166: BRAINIAC, CORAL, EYESPY), 140 (shots2 101-107: CAMANIS; enemies show weapani frames,
    the player's shots one more).

As the sprites draw them: glass pearls lit from the upper left. 225 (4 x 4 pixels, columns 4-7, rows 5-8), 226 (5 x 5),
227 (7 x 7, columns 2-8, rows 3-9) and 244 (11 x 11, columns 0-10, rows 1-11) are ramp 8's pale cyan-grey: a white
highlight (0x8f) at the upper left, the body 0x8b-0x89 darkening to 0x85-0x81 at the lower right, where a lighter
crescent lies inside the rim (0x84-0x86 in 227; in 244 a bright one, 0x8c 0x8d, from its right side round to its
bottom). 228 and 247 are 227 and 226 in ramp 9 (blue: 0x9f at the highlight, a dark 0x92 rim); 166 is a large blue one
(11 x 11, columns 1-11), its highlight right of its middle and its crescent at the lower left. shots2 101-108 are two
pearls 6 x 6 (ramp 9, 0x9d-0x9a, dark 0x94 rims, ramp 8's 0x8f 0x8c 0x8a for the highlight) orbiting their middle, the
pair turning clockwise a frame at a time (101 one above the other, 105 side by side: the angles 0, 14, 34, 56, 90, 124,
146, 166 degrees, on an ellipse 3 x 4 pixels from the middle: the cell is 12 wide); shots2 82-87 three pearls 5 x 5
(ramp 9 with an 0x8f highlight) in a triangle, turning clockwise 20 degrees a frame (82 at -10 degrees, 87 at 90; its
middle up to 0.8 pixels off the cell's).

The models: every pearl is a ball flattened underneath (the game's camera only ever sees shots from above), its glass in
bands of the sprite's palette lying in rings round the direction its light comes from. The pearls that do not turn have
the sprites' look, the light from the upper left (the game's sun is there too): a pale highlight round that direction
(0x8e; blue 0x9f), the body darkening away from it (0x8c, 0x8a, 0x85; 0x9d, 0x9b, 0x99) and, on the far side, a crescent
of bright glass inside the rim (0x8c; 0x9d), from the right side round to the bottom: the light through the glass. The
pearls of the turning pair and triangle (turned by yaw=, frame by frame) have their rings round the vertical, so that
they look the same however they are turned: a small pale top (0x8c, the sky in the glass), the blue body (0x9c) and a
deeper blue round its foot (0x98, the sprites' dark rims), the sun's own highlight falling on their glossy tops at the
upper left (where the sprites draw their white highlight). Every
band glows in its own colour (0.38-0.56: glass reads near black from the slanted camera otherwise); glossy (roughness
0.22, the turning pearls 0.18). The mesh is built on the bands: its rings are the bands' borders (no face is cut). One
pale pearl serves 225, 226, 227 and 244 (scale=, at=), one blue pearl 228, 247 and 166 (166's crescent, drawn at the
lower left, lies on the lower right as the sun has it); the pair is one model turned per frame, the triangle one model
turned and moved per frame. 4, 4, 3 and 3 materials; 448, 448, 384 and 576 triangles.
Each shot line's glow= (in place of the automatic glow, 13 pixels at 0.7 in the sprite's brightest colour) puts a halo
of the pearls' pale colour round them, a little wider than they are.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the origin at the
sprite's centre (pixel 6, 7 of the cell: column c is x = c + 0.5 - 6, row r is y = 6.5 - r); the pearls stand on z = 0
(the game centres shot models in height on the player's layer). The single pearls are authored 7 pixels across at the
origin (227's size); their shot lines scale and move them onto each sprite.

models.cfg: the model lines and the shot lines are printed by the build (SHOTS below).

Run: Blender -b --factory-startup -P tools/blender/models/shots/polish_shot_protron.py -- [--only <name,...>]
     [--outdir <dir>] (default assets/models/shots) [--check <sheets dir>] (each model's top view against its sprites in
     <dir>/shots.png and shots2.png, from TYR3D_EXTRACT, scaled, turned and moved as their shot lines say)
     [--preview <prefix>] (top, three-quarter and game-camera views)
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ENEMIES = os.path.join(HERE, "..", "enemies")
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, ENEMIES)
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_launched_flames import lit, check_frames, turn  # noqa: E402
from polish_shot_pulse import game_view  # noqa: E402

OUTDIR = os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "shots")

# --- The sprites (palette indices, '..' transparent): the large pale pearl and one frame of each cluster -------------

SPRITES = {
    ("shots", 244): """
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. 82 83 83 82 81 .. .. .. ..
.. .. 83 88 89 89 87 83 81 .. .. ..
.. 82 8a 8c 8c 8c 8b 87 81 81 .. ..
80 86 8c 8e 8f 8e 8c 8a 85 81 84 ..
80 88 8c 8f 8f 8f 8c 8b 86 83 85 ..
81 87 8c 8e 8f 8e 8c 8a 86 84 87 ..
81 84 8b 8c 8c 8c 8a 88 84 89 89 ..
82 81 86 89 89 89 87 84 88 8c 8b ..
.. 83 81 85 86 84 84 88 8d 8b .. ..
.. .. 84 82 83 88 8c 8d 8b .. .. ..
.. .. .. 88 8a 8d 8c 8b .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
""",
    ("shots2", 101): """
.. .. .. .. 94 9d 9c 95 .. .. .. ..
.. .. .. 94 9d 8f 8a 9d 95 .. .. ..
.. .. .. 9c 8f 8c 9d 9a 9b .. .. ..
.. .. .. 9b 8a 9d 9b 94 9b .. .. ..
.. .. .. 94 9c 9b 97 99 94 .. .. ..
.. .. .. .. 94 9a 9a 94 .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. 94 9d 9c 95 .. .. .. ..
.. .. .. 94 9d 8f 8a 9d 95 .. .. ..
.. .. .. 9c 8f 8c 9d 9a 9b .. .. ..
.. .. .. 9b 8a 9d 9b 94 9b .. .. ..
.. .. .. 94 9c 9b 97 99 94 .. .. ..
.. .. .. .. 94 9a 9a 94 .. .. .. ..
""",
    ("shots2", 82): """
.. .. .. .. 9e 9c 9a .. .. .. .. ..
.. .. .. 9e 8f 9c 98 9c .. .. .. ..
.. .. .. 9d 9c 99 94 9a .. .. .. ..
.. .. .. 9b 9a 94 93 96 .. .. .. ..
.. .. .. .. 9c 9a 96 .. .. .. .. ..
.. .. .. .. .. .. .. .. 9e 9c 9a ..
.. .. 9e 9c 9a .. .. 9e 8f 9c 98 9c
.. 9e 8f 9c 98 9c .. 9d 9c 99 94 9a
.. 9d 9c 99 94 9a .. 9b 9a 94 93 96
.. 9b 9a 94 93 96 .. .. 9c 9a 96 ..
.. .. 9c 9a 96 .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
""",
}

# --- The pearls -------------------------------------------------------------------------------------------------------
# A look: the direction its light comes from (its bands lie in rings round it), the bands ((the angle from that
# direction where the band ends, degrees; palette index; emission strength): the last one runs to the far side; a band
# whose index came before takes that band's material again), the most degrees between two rings, the points round each
# ring, the height over the radius, the roughness.


class Look:
    def __init__(self, **values):
        self.__dict__.update(values)


# The pearls that do not turn: the light from the upper left and above (the sprites' and the game's sun's), 37 degrees
# from straight up: the highlight at the upper left, the crescent of bright glass on the far side (the lower right).
LIGHT = Vector((-0.42, 0.42, 0.8)).normalized()
# (The shadow a deep teal, 0x85 as the sprites' darker lower right, so that the pale pearls stand out of pale ground:
# ice, white clouds.)
PALE = Look(axis=LIGHT, step=14.0, segments=16, height=0.92, roughness=0.22,
            bands=[(22.0, 0x8e, 0.56), (50.0, 0x8c, 0.5), (82.0, 0x8a, 0.44), (104.0, 0x85, 0.34),
                   (138.0, 0x8c, 0.5), (180.0, 0x85, 0.34)])
BLUE = Look(axis=LIGHT, step=14.0, segments=16, height=0.92, roughness=0.22,
            bands=[(22.0, 0x9f, 0.56), (50.0, 0x9d, 0.5), (82.0, 0x9b, 0.46), (104.0, 0x99, 0.42),
                   (138.0, 0x9d, 0.5), (180.0, 0x99, 0.42)])
# The pearls of the turning pair and triangle: rings round the vertical (the same look turned any way): a small pale
# top (the sky in the glass; ramp 8, as the sprites' highlight is), the blue body, a deeper blue round its foot (the
# sprites' dark rims); the sun's own highlight falls on the glossy top at the upper left, where the sprites draw theirs.
TURNING = Look(axis=Vector((0.0, 0.0, 1.0)), step=14.0, segments=12, height=0.92, roughness=0.18,
               bands=[(20.0, 0x8c, 0.5), (52.0, 0x9c, 0.46), (90.0, 0x98, 0.4)])

SINGLE = 3.5  # the single pearls' radius as authored (227's 7 pixels)
PAIR = (3.0, 3.6)  # the pair's pearls' radius, and how far each is from the middle
TRIANGLE = (2.5, 3.55)  # the triangle's pearls' radius, and how far each is from the middle

# name: (the sprite it is authored as, [(look, centre, radius)], what it is)
MODELS = [
    ("shot_protron", ("shots", 227), [(PALE, (0.0, 0.0), SINGLE)], "a pale glass pearl (at the origin)"),
    ("shot_protron_blue", ("shots", 228), [(BLUE, (0.0, 0.0), SINGLE)], "a blue glass pearl (at the origin)"),
    ("shot_protron_2", ("shots2", 101), [(TURNING, (0.0, PAIR[1]), PAIR[0]), (TURNING, (0.0, -PAIR[1]), PAIR[0])],
     "two blue pearls, one above the other"),
    ("shot_protron_3", ("shots2", 82),
     [(TURNING, (TRIANGLE[1] * math.sin(math.radians(a)), TRIANGLE[1] * math.cos(math.radians(a))), TRIANGLE[0])
      for a in (0.0, 120.0, 240.0)], "three blue pearls in a triangle, one up"),
]

# The shot lines: (sheet, sprite, model, yaw (degrees clockwise from up), scale, at (dx, dy: game pixels, dy down the
# screen), glow (size, strength, palette index, dx, dy), comment). The pair's yaws are the angles the sprites draw it at
# (its middle on the cell's); the triangle's turn 20 degrees a frame, its middle moved as each frame draws it.
PALE_GLOW, BLUE_GLOW, TURNING_GLOW = 0x8d, 0x9e, 0x9d
SHOTS = [
    ("shots", 225, "shot_protron", 0, 4 / 7, None, (9, 0.45, PALE_GLOW, 0, 0), "a small pale pearl (Protron front)"),
    ("shots", 226, "shot_protron", 0, 5 / 7, (-0.5, -0.5), (10, 0.45, PALE_GLOW, -0.5, -0.5), "a pale pearl"),
    ("shots", 227, "shot_protron", 0, 1.0, (-0.5, -0.5), (12, 0.45, PALE_GLOW, -0.5, -0.5),
     "a pale pearl (Protron rear, Protron Z)"),
    ("shots", 244, "shot_protron", 0, 11 / 7, (-0.5, -0.5), (16, 0.5, PALE_GLOW, -0.5, -0.5), "a large pale pearl"),
    ("shots", 228, "shot_protron_blue", 0, 1.0, (-0.5, -0.5), (12, 0.45, BLUE_GLOW, -0.5, -0.5),
     "a blue pearl (Protron Wave)"),
    ("shots", 247, "shot_protron_blue", 0, 5 / 7, (-0.5, -0.5), (10, 0.45, BLUE_GLOW, -0.5, -0.5),
     "a small blue pearl (Protron Cannon Indigo)"),
    ("shots", 166, "shot_protron_blue", 0, 11 / 7, (0.5, -0.5), (16, 0.5, BLUE_GLOW, 0.5, -0.5),
     "a large blue pearl (Protron Cannon Tangerine)"),
] + [
    ("shots2", 101 + i, "shot_protron_2", yaw, 1.0, None, (14, 0.45, TURNING_GLOW, 0, 0),
     "two pearls turning (Protron rear, Protron Wave)" if i == 0 else "")
    for i, yaw in enumerate((0, 14, 34, 56, 90, 124, 146, 166))
] + [
    ("shots2", 82 + i, "shot_protron_3", yaw, 1.0, at, (14, 0.45, TURNING_GLOW, at[0], at[1]),
     "three pearls turning (Protron rear, Protron Wave)" if i == 0 else "")
    for i, (yaw, at) in enumerate(((350, (0.17, -0.83)), (10, (-0.17, -0.83)), (30, (-0.17, -0.5)),
                                   (50, (-0.17, -0.17)), (70, (0.17, -0.17)), (90, (0.17, -0.5))))
]


# --- Building ---------------------------------------------------------------------------------------------------------

def ring_angles(look):
    """The rings' angles from the light's direction (degrees): every band's border, with rings between them no further
    apart than look.step; the last band ends at 180 (the far pole) or 90 (the flat underside's edge, for a vertical
    light)."""
    angles = []
    start = 0.0
    for end, _, _ in look.bands:
        count = max(1, int(math.ceil((end - start) / look.step - 1e-9)))
        angles += [start + (end - start) * (i + 1) / count for i in range(count)]
        start = end
    return [a for a in angles if a < 180.0 - 1e-6]  # (the far pole is a point of its own)


def band_of(look, angle):
    for i, (end, _, _) in enumerate(look.bands):
        if angle <= end + 1e-6:
            return i
    return len(look.bands) - 1


def pearl(name, look, centre, radius, materials):
    """A pearl: a ball flattened underneath (z below its equator pressed to 0), its rings round the light's direction at
    the bands' borders (each face in one band), the faces' materials by band (a band that repeats an index takes that
    index's material)."""
    axis = look.axis.normalized()
    side = Vector((0.0, 0.0, 1.0)).cross(axis)
    if side.length < 1e-6:
        side = Vector((1.0, 0.0, 0.0))
    side.normalize()
    other = axis.cross(side).normalized()
    cx, cy = centre
    height = radius * look.height
    angles = ring_angles(look)
    vertical = abs(axis.z) > 0.999
    count = look.segments

    def point(theta, phi):
        t, p = math.radians(theta), math.radians(phi)
        q = math.cos(t) * axis + math.sin(t) * (math.cos(p) * side + math.sin(p) * other)
        return (cx + radius * q.x, cy + radius * q.y, height * max(q.z, 0.0))
    # Each ring turned half a step against the one before (even triangles round the pole).
    verts = [point(0.0, 0.0)]
    rings = []
    for i, theta in enumerate(angles):
        if vertical and theta >= 90.0 - 1e-6:
            theta = 90.0
        offset = 0.5 * (i % 2) * 360.0 / count
        rings.append(len(verts))
        verts += [point(theta, offset + 360.0 * j / count) for j in range(count)]
    far = len(verts)
    verts.append((cx, cy, 0.0) if vertical else point(180.0, 0.0))
    faces, bands = [], []
    for j in range(count):
        faces.append((0, rings[0] + j, rings[0] + (j + 1) % count))
        bands.append(band_of(look, angles[0] / 2))
    for i in range(len(rings) - 1):
        a, b = rings[i], rings[i + 1]
        band = band_of(look, (angles[i] + angles[i + 1]) / 2)
        for j in range(count):
            jj = (j + 1) % count
            if i % 2 == 0:  # (ring i + 1 is turned half a step on)
                faces.append((a + j, b + j, a + jj))
                faces.append((a + jj, b + j, b + jj))
            else:
                faces.append((a + j, b + j, b + jj))
                faces.append((a + j, b + jj, a + jj))
            bands += [band, band]
    last = rings[-1]
    for j in range(count):
        faces.append((last + (j + 1) % count, last + j, far))
        bands.append(len(look.bands) - 1)
    obj = k.mesh_object(name, verts, faces)
    for m in materials:
        obj.data.materials.append(m)
    slots = {}
    for i, (_, index, _) in enumerate(look.bands):
        slots.setdefault(index, len(slots))
    for poly, band in zip(obj.data.polygons, bands):
        poly.material_index = slots[look.bands[band][1]]
    k.recalc_normals(obj)
    return k.smooth(obj, 60)


def build_model(name, pearls):
    parts = []
    cache = {}
    for i, (look, centre, radius) in enumerate(pearls):
        mats = []
        for _, index, glow in look.bands:
            if index in [m[0] for m in mats]:
                continue
            key = (index, glow)
            if key not in cache:
                cache[key] = lit(f"protron_{index:02x}", index, glow, roughness=look.roughness)
            mats.append((index, cache[key]))
        parts.append(pearl(f"{name}_pearl{i}", look, centre, radius, [m for _, m in mats]))
    return triangulate(parts)


# --- Checks and the models.cfg lines ------------------------------------------------------------------------------

def placement(yaw, scale, at):
    """The shot line's turn, scale and offset as one matrix (model coordinates: at's dy is down the screen)."""
    dx, dy = at if at is not None else (0.0, 0.0)
    return Matrix.Translation((dx, -dy, 0.0)) @ Matrix.Scale(scale, 4) @ turn(yaw)


def cfg_lines(only=None):
    """The models.cfg lines: the model lines, then the shot lines, their options in aligned columns (at=, yaw=, scale=,
    glow=), the first of each group with its comment."""
    names = [m[0] for m in MODELS if only is None or m[0] in only]
    width = max(len(n) for n in names)
    lines = [f"model {n.ljust(width)} shots/{n}.glb" for n in names]
    rows = []
    for sheet, sprite, name, yaw, scale, at, glow, comment in SHOTS:
        if only is not None and name not in only:
            continue
        size, strength, colour, gx, gy = glow
        rows.append([f"shot {sheet.ljust(6)} {str(sprite).ljust(3)} {name.ljust(width)}",
                     f"at={at[0]:g}:{at[1]:g}" if at is not None else "", f"yaw={yaw:g}" if yaw else "",
                     f"scale={scale:.3f}".rstrip("0") if abs(scale - 1.0) > 1e-6 else "",
                     f"glow={size:g}:{strength:g}:{colour}:{gx:g}:{gy:g}", comment])
    widths = [max(len(r[i]) for r in rows) for i in range(5)]
    out = []
    for r in rows:
        cells = [r[0]] + [r[i].ljust(widths[i]) for i in range(1, 5) if widths[i]]
        line = " ".join(cells)
        out.append(line + " # " + r[5] if r[5] else line.rstrip())
    return lines + out


# --- Build ------------------------------------------------------------------------------------------------------------

def build():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    outdir = options.get("outdir", OUTDIR)
    for name, reference, pearls, what in MODELS:
        if only is not None and name not in only:
            continue
        k.reset()
        parts = build_model(name, pearls)
        bpy.context.view_layer.update()
        print(f"== {name} ({reference[0]} {reference[1]}): {what}")
        if "check" in options:
            for sheet, sprite, model, yaw, scale, at, _, _ in SHOTS:
                if model != name:
                    continue
                check_frames(parts, os.path.join(options["check"], sheet + ".png"),
                             [(sprite, placement(yaw, scale, at), f"{sheet} {sprite}")], move_to_frame=False)
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, parts, os.path.join(outdir, name + ".glb"))
        if "preview" in options:
            game_view(options["preview"] + name, parts)
    print("models.cfg:")
    for line in cfg_lines(only):
        print("  " + line)


if __name__ == "__main__":
    build()
