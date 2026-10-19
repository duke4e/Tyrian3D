"""The dark blue pipe MINEMAZE and GAUNTLET lay across their corridors (sheet S sprites 1, 7, 115 and 3, 2x2 each:
24 x 28 pixels; ground and ground2 layers; enemies 586, 588, 589 and 587, one sprite after another along a row:
the left end, plain segments, segments with a cage round a red core, the right end; also end, cage, end and cage
beside cage), polished (2026-10-19; it replaces wave3_u.py's pipe (pipe_whole() and its pieces) and
wave3_at_misc.py's maze_pipe_cage_<sprite> frames). models.cfg: model maze_pipe_end_l / maze_pipe / maze_pipe_cage /
maze_pipe_end_r / maze_pipe_cage_117 ... _123 ... origin; sprite s 1 maze_pipe_end_l yaw=0, sprite s 7 maze_pipe
yaw=0, sprite s 115 maze_pipe_cage yaw=0, sprite s 3 maze_pipe_end_r yaw=0, frame s 117 maze_pipe_cage_117, frame s
119 maze_pipe_cage_119, frame s 121 maze_pipe_cage_121, frame s 123 maze_pipe_cage_123 (enemy 589's animation:
115 115 117 117 119 119 121 121 123 123 121 121 119 119 117 117; no other enemy uses these sprites).

As the sprites and their 4x upscales draw it: a round pipe lying across the screen (rows 5-24: its axis between rows
14 and 15, a radius of 10), dark navy (the sprite's ramp 3), glossy: a highlight along its crest (row 14), a light
rim along its top edge (row 6), lighter again near each sprite's edges, where the segments meet in thin seams. The
ends taper in two shoulders (columns 0-8 of S 1: from 20 pixels across to 18, columns 2-7, and to 15, columns 0-1)
into the bronze sockets the maps paint on the walls either side (the sockets are the map's). The caged segment
(S 115): along its crest a red band (rows 14-15, glowing) between two light rails (rows 13 and 16), and four light
blue hoops wound round the pipe: two crossing over its crest in a lens (columns 6-17), two leaning out to either side
(columns 1-5 and 18-22). In its frames a red core swells out of the pipe either side of the band, inside the lens
(117: two small dull lumps, rows 8-11 and 17-20; 123: rows 7-12 and 17-22, bright, white-pink highlights).

Each sprite is built in its own place (its centre the origin): the same pipe, a half flange at every edge where it
meets the next (so any two pieces meet in a whole flange, the same section at every sprite edge: the pipe at its
radius, the flange's flat rim), the ends' shoulders, the caged segment's rails, band, hoops and core. The hoops are
flat straps round the pipe in planes tilted about the screen's vertical (about 38 degrees: the lens' pair leaning in,
crossing near the pipe's flanks where the sprite's lens closes; the outer pair leaning out), so seen from above their
upper halves draw the sprite's arcs (their lower halves stay within the segment). The core is two red blisters on the pipe's surface either side of the band,
growing with the frames, glowing brighter (emission in their own colours).

The pipe floats over the corridors' void between the walls' sockets (MINEMAZE's and GAUNTLET's terrain is a hole
there): its underside is at z = 0 (+Z up; +Y up the sprite; column c is x = c + 0.5 - 12, row r is y = 13.5 - r).

Replaces wave3_u.py's pipe (its whole and the four r.model("maze_pipe...") pieces) and wave3_at_misc.py's pipe cage
frames (CAGE_X, pipe_cage(), CAGE and its model loop); maze_pipe_cage_115.glb is no longer used (115 is
maze_pipe_cage itself).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each piece's silhouette
against enemy_S.png), --preview <prefix>, --only <name,...>.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402

AXIS_Y, AXIS_Z, R = -1.0, 10.0, 10.0
SEGMENTS = 48
# The half flange at each edge: from |x| = FLANGE_FROM its rim rises (over FLANGE_RISE) to R + FLANGE_PROUD.
FLANGE_FROM, FLANGE_RISE, FLANGE_PROUD = 10.7, 0.45, 0.32
# The left end's radius along x from its tip (x, radius): the spigot into the socket, a shoulder, the reducer, a
# shoulder, the pipe.
END = [(-12.0, 7.6), (-10.6, 7.6), (-10.15, 8.25), (-9.75, 8.8), (-5.6, 9.0), (-4.7, 9.45), (-3.9, 9.9), (-3.2, 10.0)]
# The caged segment: the rails along its crest either side of the band (|y| from the axis, radius), the band's
# half-width; the hoops: (x where the plane crosses the axis, its tilt: dx per height above the axis).
RAIL_Y, RAIL_R = 1.55, 0.42
BAND_HALF = 1.0
HOOP_R, HOOP_WIDTH, HOOP_THICK = 10.26, 1.7, 0.52
HOOPS = [(3.0, -0.78), (-3.0, 0.78), (-2.1, -0.77), (2.1, 0.77)]
SHINE = 7.0                            # the highlight painted along the plain pipe's crest: degrees either side
# The core's blisters: their angle from the crest (degrees, either side), and per frame: half-length along the pipe,
# half-width round it (pixels), height; colours.
CORE_ANGLE = 30.0

PIECES = [("maze_pipe_end_l", 1, "end_l"), ("maze_pipe", 7, "plain"), ("maze_pipe_end_r", 3, "end_r")]
# The caged segment's frames: (model, sprite, the blisters' half-length, half-width, height (None: no core), body
# (palette index, glow), heart (palette index, glow) or None).
CAGES = [
    ("maze_pipe_cage", 115, None, None, None),
    ("maze_pipe_cage_117", 117, (1.9, 1.8, 0.75), (0x42, 0.3), None),
    ("maze_pipe_cage_119", 119, (2.7, 2.3, 1.2), (0x44, 0.55), (0x46, 0.75)),
    ("maze_pipe_cage_121", 121, (3.3, 2.7, 1.65), (0x46, 0.85), (0x49, 1.1)),
    ("maze_pipe_cage_123", 123, (3.8, 3.0, 2.1), (0x48, 1.2), (0x4c, 1.6)),
]


def materials(core=None, heart=None):
    glow = k.level_palette()

    def mat(name, index, metallic=0.55, roughness=0.25):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)

    def lit(name, index, strength, roughness=0.2):
        return k.material(name, palette=index, metallic=0.0, roughness=roughness, emission=glow[index],
                          emission_strength=strength)
    m = {
        "pipe": mat("mpipe_body", 0x35, 0.6, 0.22),
        "shine": mat("mpipe_shine", 0x3b, 0.5, 0.2),
        "flange": mat("mpipe_flange", 0x37, 0.65, 0.2),
        "seam": mat("mpipe_seam", 0x31, 0.4, 0.5),
        "cap": mat("mpipe_cap", 0x32, 0.5, 0.4),
        "rail": mat("mpipe_rail", 0x3b, 0.6, 0.2),
        "hoop": mat("mpipe_hoop", 0x3b, 0.6, 0.22),
        "band": lit("mpipe_band", 0x48, 1.1, 0.2),
        "band_hot": lit("mpipe_band_hot", 0x4b, 1.3, 0.15),
        "socket": mat("mpipe_socket", 0x31, 0.4, 0.5),
    }
    if core is not None:
        m["core"] = lit(f"mpipe_core_{core[0]:x}", core[0], core[1], 0.25)
    if heart is not None:
        m["heart"] = lit(f"mpipe_heart_{heart[0]:x}", heart[0], heart[1], 0.15)
    return m


# --- The pipe -----------------------------------------------------------------------------------------------------

def flange_radius(x, left=True, right=True):
    """The pipe's radius at x with the half flanges at its edges."""
    ax = abs(x)
    if (x < 0 and not left) or (x > 0 and not right) or ax < FLANGE_FROM:
        return R
    t = min(1.0, (ax - FLANGE_FROM) / FLANGE_RISE)
    return R + FLANGE_PROUD * (0.5 - 0.5 * math.cos(math.pi * t))


def pipe_profile(kind):
    """(x, radius) along the piece from x = -12 to 12: its flanges and, for the ends, the shoulders."""
    xs = [-12.0, -11.75, -11.5, -11.25, -11.0, -10.85, -10.7, -9.0, -7.0, -5.0, -3.0, -1.0, 1.0, 3.0, 5.0, 7.0, 9.0,
          10.7, 10.85, 11.0, 11.25, 11.5, 11.75, 12.0]
    if kind == "plain" or kind == "cage":
        return [(x, flange_radius(x)) for x in xs]
    # The left end (the right end is its mirror image).
    prof = [(x, r) for x, r in END]
    for x in xs:
        if x > END[-1][0] + 0.3:
            prof.append((x, flange_radius(x, left=False)))
    return prof


def lathe_x(name, profile, mat, segments=SEGMENTS):
    """A part turned about the pipe's axis (along x): profile (x, radius); its ends closed flat."""
    rings = []
    for x, r in profile:
        rings.append([Vector((x, AXIS_Y + r * math.cos(2 * math.pi * j / segments),
                              AXIS_Z + r * math.sin(2 * math.pi * j / segments))) for j in range(segments)])
    obj = k.loft(name, rings, mat, start_point=(profile[0][0], AXIS_Y, AXIS_Z), end_point=(profile[-1][0], AXIS_Y, AXIS_Z))
    return obj


def pipe(m, kind):
    prof = pipe_profile(kind)
    if kind == "end_r":
        prof = [(-x, r) for x, r in reversed(prof)]
    obj = lathe_x("pipe", prof, m["pipe"])
    k.smooth(obj, 50)

    shine = math.cos(math.radians(SHINE))

    def pick(c, n):
        ax = abs(c.x)
        if abs(n.x) > 0.95 and ax > 11.9:
            return m["cap"]  # the flat ends (inside the next piece, or the socket)
        radial = Vector((0.0, c.y - AXIS_Y, c.z - AXIS_Z)).normalized()
        if kind != "cage" and radial.z > shine and ax < FLANGE_FROM - 0.2:
            return m["shine"]
        if ax > FLANGE_FROM + 0.05 and ((c.x > 0 and kind != "end_r") or (c.x < 0 and kind != "end_l")):
            return m["flange"]
        if kind in ("end_l", "end_r") and ax > 11.95:
            return m["socket"]
        return None
    mk.paint(obj, pick)
    return obj


# --- The cage ------------------------------------------------------------------------------------------------------

def surface_point(x, angle, lift=0.0):
    """The point on the pipe's surface at x, `angle` (degrees) round from its crest towards +y, `lift` above it."""
    a = math.radians(angle)
    r = R + lift
    return Vector((x, AXIS_Y + r * math.sin(a), AXIS_Z + r * math.cos(a)))


def rails_and_band(m):
    """Two light rails along the crest and the glowing band between them, the whole segment long."""
    made = []
    for side in (-1, 1):
        a = math.degrees(math.asin(RAIL_Y / R)) * side
        pts = [tuple(surface_point(x, a, 0.05)) for x in (-12.0, -6.0, 0.0, 6.0, 12.0)]
        rail = mk.tube(f"rail{side}", pts, RAIL_R, m["rail"], 10, cap=True)
        k.smooth(rail, 50)
        made.append(rail)
    # The band: a strip bulging a little over the crest, between the rails.
    half = math.degrees(math.asin(BAND_HALF / R))
    rings = []
    count = 7
    for x in [-12.0 + 24.0 * i / 24 for i in range(25)]:
        ring = []
        for j in range(count):
            a = -half + 2 * half * j / (count - 1)
            bulge = 0.32 * math.cos(math.pi * (j / (count - 1) - 0.5))
            ring.append(surface_point(x, a, bulge))
        for j in reversed(range(count)):
            a = -half + 2 * half * j / (count - 1)
            ring.append(surface_point(x, a, -0.2))
        rings.append(ring)
    band = k.loft("band", rings, m["band"], start_point=tuple(surface_point(-12.0, 0.0, 0.05)),
                  end_point=tuple(surface_point(12.0, 0.0, 0.05)))
    k.smooth(band, 60)
    # Hotter in the middle, over the core.
    mk.paint(band, lambda c, n: m["band_hot"] if abs(c.x) < 2.6 and n.z > 0.5 else None)
    made.append(band)
    return made


def hoop(m, name, x0, tilt):
    """A hoop round the pipe: a flat strap lying on its surface along the plane x = x0 + tilt * (height above the
    axis), its seam under the pipe."""
    count = 48
    path = []
    for j in range(count + 1):
        a = math.pi + 2 * math.pi * j / count
        dy, dz = HOOP_R * math.sin(a), HOOP_R * math.cos(a)
        path.append(Vector((x0 + tilt * dz, AXIS_Y + dy, AXIS_Z + dz)))
    rings = []
    for j, p in enumerate(path):
        t = (path[min(j + 1, count)] - path[max(j - 1, 0)]).normalized()
        if j in (0, count):
            t = (path[1] - path[count - 1]).normalized()
        nrm = Vector((0.0, p.y - AXIS_Y, p.z - AXIS_Z)).normalized()
        b = t.cross(nrm).normalized()
        ring = []
        for q in range(10):
            u, v = mk.superellipse_point(2 * math.pi * q / 10, 3.2)
            ring.append(p + b * (u * HOOP_WIDTH / 2) + nrm * (v * HOOP_THICK / 2))
        rings.append(ring)
    obj = k.loft(name, rings, m["hoop"], cap_start=False, cap_end=False)
    k.smooth(obj, 50)
    return obj


def surface_dome(name, mat, centre_a, half_len, span_a, lift):
    """A dome lying on the pipe's surface: a disc round (x = 0, centre_a degrees from the crest), half_len along
    the pipe and span_a degrees round it, each point lifted lift(x, angle, f) above the surface (f: 0 at its middle,
    1 at its rim)."""
    verts, faces = [], []
    n_r, n_a = 8, 28
    for i in range(1, n_r + 1):
        f = i / n_r
        for j in range(n_a):
            t = 2 * math.pi * j / n_a
            x = half_len * f * math.cos(t)
            a = centre_a + span_a * f * math.sin(t)
            verts.append(surface_point(x, a, lift(x, a, f)))
    centre = surface_point(0.0, centre_a, lift(0.0, centre_a, 0.0))
    verts.append(centre)
    c_index = len(verts) - 1
    for i in range(n_r - 1):
        for j in range(n_a):
            a0, a1 = i * n_a + j, i * n_a + (j + 1) % n_a
            faces.append((a0, a1, a1 + n_a, a0 + n_a))
    faces += [((j + 1) % n_a, j, c_index) for j in range(n_a)]
    obj = k.mesh_object(name, verts, faces, mat)
    k.recalc_normals(obj)
    out = (centre - Vector((0.0, AXIS_Y, AXIS_Z))).normalized()
    if sum((p.normal.dot(out) for p in obj.data.polygons)) < 0:
        obj.data.flip_normals()
    return k.smooth(obj, 70)


def core(m, size, has_heart):
    """The core: two red blisters on the pipe's surface either side of the band, swelling out of it, a hotter
    heart on each (a low dome on its top)."""
    if size is None:
        return []
    half_len, half_wid, height = size
    span = math.degrees(half_wid / R)
    made = []
    for side in (-1, 1):
        ca = CORE_ANGLE * side

        def body_lift(x, a, f, ca=ca):
            ff = min(1.0, math.sqrt((x / half_len) ** 2 + ((a - ca) / span) ** 2))
            return height * (1 - ff ** 2.2) ** 0.75 - 0.15
        made.append(surface_dome(f"core{side}", m["core"], ca, half_len, span, body_lift))
        if has_heart:
            made.append(surface_dome(f"heart{side}", m["heart"], ca, half_len * 0.45, span * 0.42,
                                     lambda x, a, f, bl=body_lift: bl(x, a, f) + 0.08 + 0.3 * (1 - f * f)))
    return made


def sprite_mask(sheet, sprite):
    return k.sprite_mask(sheet, sprite)


def finish(name, sprite, m, options, out):
    parts = mk.meshes()
    for obj in parts:
        mk.apply(obj)
    bpy.context.view_layer.update()
    if "check" in options:
        mk.compare("%s (S %d)" % (name, sprite), mk.coverage(parts, 24, 28),
                   sprite_mask(os.path.join(options["check"], "enemy_S.png"), sprite))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mk.report(name, parts, os.path.join(out, name + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + name, parts)


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options.get("only", "").split(",") if "only" in options else None
    for name, sprite, kind in PIECES:
        if only and name not in only:
            continue
        k.reset()
        m = materials()
        pipe(m, kind)
        finish(name, sprite, m, options, out)
    for name, sprite, size, body, heart in CAGES:
        if only and name not in only:
            continue
        k.reset()
        m = materials(body, heart)
        pipe(m, "cage")
        rails_and_band(m)
        for i, (x0, tilt) in enumerate(HOOPS):
            hoop(m, f"hoop{i}", x0, tilt)
        core(m, size, heart is not None)
        finish(name, sprite, m, options, out)


if __name__ == "__main__":
    build()
