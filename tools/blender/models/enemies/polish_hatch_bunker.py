"""The hatch in DESERTRUN's bunker roofs (sheet 3 sprite 18, 2x2: 24 x 28 pixels; ground layer; enemy 183, 20 of them
on the long grey bunkers; its animation 18 56 94 284 284 284 284 94 94 94 94 56 56 56 56 18: it opens to fire),
polished (2026-10-19; it replaces wave3_n.py's hatch_bunker(), an inflated collar with a tube frame, and
wave3_ar_beasts.py's hatch_bunker_<sprite> frames). models.cfg: model hatch_bunker / hatch_bunker_56 /
hatch_bunker_94 / hatch_bunker_284; sprite 3 18 hatch_bunker yaw=0, frame 3 56 hatch_bunker_56, frame 3 94
hatch_bunker_94, frame 3 284 hatch_bunker_284 (no other enemy uses these sprites).

As the sprites and their 4x upscales draw it: a square hatch sunk in the roof (columns 2-21 of rows 2-24: its walls
dark at the top and left, lit at the right and bottom), a thin red frame round its opening (columns 3-19 of rows
3-22, lit at its top left), and in the opening two grey doors meeting in a dark seam (row 13), each stiffened by a
diagonal rib (the upper one rising to the right, the lower one falling). The frames open it: the doors draw back
under the frame, 2 pixels each (56), 4 (94), all the way (284, slivers of their edges left at rows 5-6 and 20), on
a pit where a grey sensor dome (columns 8-14 of rows 9-16) looks up with a big red eye (columns 9-13 of rows 11-14),
on a thin post, small fins at its sides.

The sprite of the shut hatch is the map's own tile (DESERTRUN's 50, pixel for pixel; tile 13 is the same roof
without it): the 3D view erases what the sprite shares with the map under the model (assets/terrain/<map>.era),
filling it with the plain roof, so the model is the whole hatch: a low armoured collar on the roof with sloping
outer walls, the red frame on it, the pit inside, the doors and the sensor. The doors roll back under the frame
(their visible parts shrink, the ribs moving with them and cut off at the frame); the sensor rises as they open (in
56 its eye shows between the doors, below them; in 94 and 284 the dome is up through the opening; in 18 it is down,
unseen, and left out).

All the frames have the same height bounds, z 0 to PIN_Z: each carries a speck at PIN_Z (a triangle a thousandth of
a pixel across, invisible), so the game places them alike, on the roof (it centres a model in height on the ground
enemies' layer, 4, and lifts it to 0.3 when it would reach lower: half of PIN_Z is more than 3.7).

Origin at the sprite's centre (pixel 12, 14); +X right, +Y up the sprite, +Z up from the roof (z = 0); column c is
x = c + 0.5 - 12, row r is y = 13.5 - r.

Replaces wave3_n.py's hatch_bunker() (its @n.model("hatch_bunker", ...) registration; HATCH_TOP and HATCH_DOOR_Z go
with it once wave3_ar_beasts.py's hatch frames are gone; wave3_n_art.py's BUNKER if nothing else uses it) and
wave3_ar_beasts.py's hatch section (HATCH_TOP, HATCH_BOTTOM, DOOR_Z, hatch_bunker(), HATCH and its n.model loop);
hatch_bunker_18.glb is no longer used (18 is hatch_bunker itself).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each frame's silhouette
against the hatch, columns 2-21 of rows 2-24), --preview <prefix>, --only <name,...>.
"""
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402

# The collar: its foot's plan (x0, x1, y0, y1: the hatch's recess, columns 2-21 of rows 2-24), its top's (inset:
# the outer walls slope), its height.
COLLAR_FOOT = (-10.0, 10.0, -11.0, 12.0)
COLLAR_TOP = (-9.4, 9.2, -10.2, 11.6)
COLLAR_H = 2.0
# The red frame on the collar (columns 3-19 of rows 3-22) round the opening (columns 4-18 of rows 4-21).
FRAME_OUT = (-9.0, 8.0, -9.0, 11.0)
OPENING = (-8.0, 7.0, -8.0, 10.0)
FRAME_TOP = 2.75
PIT_FLOOR = 0.12
# The doors: their plane (bottom, top), where they meet when shut (y), their ribs ((x, y) from, to; shut).
DOOR_Z = (1.62, 2.02)
SEAM_Y = 0.5
RIB_UP = ((-4.6, 1.3), (6.0, 6.8))
RIB_DOWN = ((-6.6, -3.2), (3.6, -7.4))
RIB_R = 0.34
# The sensor: its middle (x, y), the dome's radius and height, the eye's radii (across, up the screen, height).
SENSOR = (-0.5, 1.0)
DOME_R, DOME_H = 3.45, 2.7
EYE = (2.15, 2.0, 1.1)
PIN_Z = 7.6

# The frames: (model, sprite, how far each door has drawn back from the seam, the sensor dome's top (None: left out),
# the eye (palette index, glow), its heart's).
FRAMES = [
    ("hatch_bunker", 18, 0.0, None, (0x74, 0.6), (0x7a, 1.0)),
    ("hatch_bunker_56", 56, 2.25, 1.5, (0x75, 1.1), (0x7b, 1.8)),
    ("hatch_bunker_94", 94, 4.25, 3.6, (0x76, 1.4), (0x7b, 2.2)),
    ("hatch_bunker_284", 284, 6.6, 4.7, (0x77, 1.6), (0x7c, 2.6)),
]


def materials(eye, hot):
    glow = k.level_palette()

    def mat(name, index, metallic=0.4, roughness=0.45):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)

    def lit(name, index, strength, roughness=0.12):
        return k.material(name, palette=index, metallic=0.0, roughness=roughness, emission=glow[index],
                          emission_strength=strength)
    return {
        "collar": mat("hatch_collar", 0x05, 0.4, 0.5),
        "collar_top": mat("hatch_collar_top", 0x06, 0.4, 0.45),
        "wall": mat("hatch_wall", 0x02, 0.3, 0.6),
        "pit": mat("hatch_pit", 0x01, 0.2, 0.7),
        "frame": mat("hatch_frame", 0x49, 0.45, 0.35),
        "frame_top": mat("hatch_frame_top", 0x4b, 0.45, 0.3),
        "door": mat("hatch_door", 0x05, 0.45, 0.4),
        "door_edge": mat("hatch_door_edge", 0x02, 0.5, 0.45),
        "rib": mat("hatch_rib", 0x07, 0.45, 0.32),
        "sensor": mat("hatch_sensor", 0x0a, 0.35, 0.28),
        "sensor_dark": mat("hatch_sensor_dark", 0x04, 0.45, 0.42),
        "eye": lit(f"hatch_eye_{eye[0]:x}", eye[0], eye[1]),
        "eye_hot": lit(f"hatch_eye_hot_{hot[0]:x}", hot[0], hot[1], 0.1),
    }


def collar(m):
    """The collar: a low block with sloping outer walls, its top flat, the opening's pit cut through it down to the
    pit's floor; the pit's walls dark."""
    fx0, fx1, fy0, fy1 = COLLAR_FOOT
    tx0, tx1, ty0, ty1 = COLLAR_TOP
    body = mk.prism("collar", [(fx0, fy0), (fx1, fy0), (fx1, fy1), (fx0, fy1)], 0.0, COLLAR_H, m["collar"])
    # The sloping walls: the top's corners moved in.
    for v in body.data.vertices:
        if v.co.z > COLLAR_H * 0.5:
            v.co.x = tx0 if v.co.x < 0 else tx1
            v.co.y = ty0 if v.co.y < 0 else ty1
    ox0, ox1, oy0, oy1 = OPENING
    cutter = mk.box("pit_cut", ox0, ox1, oy0, oy1, PIT_FLOOR, COLLAR_H + 2.0)
    mk.boolean(body, cutter, "DIFFERENCE")
    mk.cleanup(body)
    mk.bevel(body, 0.3, 2, 30)
    mk.shade(body, 35)

    def pick(c, n):
        inside = ox0 - 0.05 < c.x < ox1 + 0.05 and oy0 - 0.05 < c.y < oy1 + 0.05
        if inside and c.z < PIT_FLOOR + 0.05 and n.z > 0.8:
            return m["pit"]
        if inside:
            return m["wall"]
        if n.z > 0.85:
            return m["collar_top"]
        return None
    mk.paint(body, pick)
    return body


def frame(m):
    """The red frame: a flat square ring on the collar round the opening, its edges rounded, lighter on top."""
    x0, x1, y0, y1 = FRAME_OUT
    ox0, ox1, oy0, oy1 = OPENING
    ring = mk.prism("frame", [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], COLLAR_H - 0.3, FRAME_TOP, m["frame"])
    hole = mk.box("frame_hole", ox0, ox1, oy0, oy1, 0.0, FRAME_TOP + 1.0)
    mk.boolean(ring, hole, "DIFFERENCE")
    mk.cleanup(ring)
    mk.bevel(ring, 0.22, 2, 35)
    mk.shade(ring, 35)
    mk.paint(ring, lambda c, n: m["frame_top"] if n.z > 0.9 else None)
    return ring


def clip_y(obj, y_min, y_max):
    """Cuts an object to y_min <= y <= y_max, the cuts closed."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    for co, no in (((0, y_min, 0), (0, -1, 0)), ((0, y_max, 0), (0, 1, 0))):
        if not bm.faces:
            break
        result = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=co,
                                        plane_no=no, clear_outer=True)
        edges = [e for e in result["geom_cut"] if isinstance(e, bmesh.types.BMEdge) and e.is_valid and
                 len(e.link_faces) == 1]
        if edges:
            bmesh.ops.holes_fill(bm, edges=edges, sides=0)
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def doors(m, drawn):
    """The two doors, each drawn back `drawn` from the seam under the frame (rolled up there): plates in the
    opening from the frame's edge to their leading edge, their ribs moved with them and cut off at the frame."""
    ox0, ox1, oy0, oy1 = OPENING
    z0, z1 = DOOR_Z
    made = []
    for name, lead, far, rib, sign in (("door_up", SEAM_Y + 0.07 + drawn, oy1 + 0.6, RIB_UP, 1),
                                       ("door_down", SEAM_Y - 0.07 - drawn, oy0 - 0.6, RIB_DOWN, -1)):
        if sign * (far - lead) < 0.4:
            continue
        ya, yb = sorted((lead, far))
        plate = mk.box(name, ox0 - 0.4, ox1 + 0.4, ya, yb, z0, z1, m["door"])
        mk.bevel(plate, 0.16, 2, 35)
        mk.shade(plate, 35)
        mk.paint(plate, lambda c, n: m["door_edge"] if n.z < 0.6 else None)
        made.append(plate)
        # The rib: a rounded bar on the door, moved with it, cut to its visible part.
        (ax, ay), (bx, by) = rib
        a = Vector((ax, ay + sign * drawn, z1 + 0.02))
        b = Vector((bx, by + sign * drawn, z1 + 0.02))
        bar = mk.tube(f"{name}_rib", [tuple(a.lerp(b, t / 8)) for t in range(9)], RIB_R, m["rib"], 10)
        for v in bar.data.vertices:  # half sunk: a ridge
            if v.co.z < z1:
                v.co.z = z1 - 0.05
        k.smooth(bar, 50)
        lo, hi = (lead + 0.25, oy1 - 0.1) if sign > 0 else (oy0 + 0.1, lead - 0.25)
        clip_y(bar, lo, hi)
        if bar.data.polygons:
            made.append(bar)
        else:
            bpy.data.objects.remove(bar)
    return made


def sensor(m, top):
    """The sensor: a grey dome with its top at `top`, a red eye looking up from it, fins at its sides, on a post
    from the pit's floor."""
    sx, sy = SENSOR
    base = top - DOME_H
    made = []
    post_top = max(base + 0.4, PIT_FLOOR + 0.3)
    post = mk.lathe("sensor_post", [(1.15, PIT_FLOOR), (1.15, post_top - 0.3), (1.6, post_top), (0.01, post_top)],
                    (sx, sy - 0.6), m["sensor_dark"], 24)
    k.smooth(post, 40)
    made.append(post)
    dome = mk.dome("sensor_dome", (sx, sy), (DOME_R, DOME_R, DOME_H), base, m["sensor"], 36, 10, power=2.3)
    made.append(dome)
    # A dark band round the dome's foot.
    band = mk.lathe("sensor_band", [(DOME_R + 0.12, base - 0.05), (DOME_R + 0.12, base + 0.35),
                                    (DOME_R * 0.98, base + 0.55), (0.01, base + 0.55)], (sx, sy), m["sensor_dark"], 36)
    k.smooth(band, 40)
    made.append(band)
    ew, eh, ez = EYE
    eye_z = base + DOME_H * 0.62
    eye = mk.dome("eye", (sx, sy + 0.2), (ew, eh, ez), eye_z, m["eye"], 32, 8, power=2.2)
    made.append(eye)
    hot = mk.dome("eye_hot", (sx - 0.3, sy + 0.55), (ew * 0.42, eh * 0.42, 0.3), eye_z + ez - 0.25, m["eye_hot"], 20, 4)
    made.append(hot)
    # Fins at the dome's sides.
    for side in (-1, 1):
        fin = mk.box(f"fin{side}", -0.3, 0.3, -1.2, 1.2, 0.0, 1.5, m["sensor"])
        mk.bevel(fin, 0.2, 2, 35)
        fin.data.transform(Matrix.Translation((sx + side * (DOME_R + 0.05), sy - 0.2, base + 0.3)))
        k.smooth(fin, 40)
        made.append(fin)
    # What would be below the pit's floor is cut away.
    for obj in made:
        mk.apply(obj)
        if min(v.co.z for v in obj.data.vertices) < PIT_FLOOR:
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5,
                                   plane_co=(0, 0, PIT_FLOOR), plane_no=(0, 0, -1), clear_outer=True)
            bm.to_mesh(obj.data)
            bm.free()
    return [o for o in made if len(o.data.polygons) > 0]


def pin(m):
    e = 0.001
    x, y = SENSOR
    return k.mesh_object("pin", [(x, y, PIN_Z), (x + e, y, PIN_Z), (x, y + e, PIN_Z)], [(0, 1, 2)], m["pit"])


def hatch_mask():
    mask = [[False] * 24 for _ in range(28)]
    for r in range(2, 25):
        for c in range(2, 22):
            mask[r][c] = True
    return mask


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options.get("only", "").split(",") if "only" in options else None
    for name, sprite, drawn, top, eye, hot in FRAMES:
        if only and name not in only:
            continue
        k.reset()
        m = materials(eye, hot)
        collar(m)
        frame(m)
        doors(m, drawn)
        if top is not None:
            sensor(m, top)
        pin(m)
        parts = mk.meshes()
        for obj in parts:
            mk.apply(obj)
        bpy.context.view_layer.update()
        if "check" in options:
            mk.compare("%s (3 %d, the hatch)" % (name, sprite), mk.coverage(parts, 24, 28), hatch_mask())
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts)


if __name__ == "__main__":
    build()
