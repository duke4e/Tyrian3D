"""The sidekicks' and specials' ordnance (shots sheet sprites 34, 142, 71, 271, 272, 273, 274 and 238, all 1x1: 12 x 14
cells), modelled (2026-10-30, round 4 of the shots' models: until then each was drawn as its sprite with volume and the
automatic glow, 13 pixels at 0.7 in the sprite's brightest colour). Objects, not energy: built as Batch AS built the
missiles and bombs (shot_kit.py, shots_missiles.py: turned bodies, fins, a nozzle and a flame), but as half-bodies
(round on top, flat underneath: the game's camera never sees an underside) whose rings lie on the colours' borders (no
face is cut), as the energy shots are.

Who fires them (weapons as the item data numbers them; sidekicks by their shop ids, specials by their item ids):
- 34: the MegaMissile sidekick (6, sold from shop 1:3; ammo 5), weapon 15: five missiles a volley, 4 and 7 pixels out to
  either side, the outer ones first dropping back (1 and 4 pixels a frame) as all of them accelerate up the screen (a
  pixel a frame each frame); a volley every 8 frames while there is ammo (one more every 400 frames).
- 142: the Atom Bombs sidekick (7, shop 1:5; ammo 20), weapon 19: two bombs a volley flying up at 7 pixels a frame,
  drifting apart a pixel a frame; the Atom Bomb special (38, weapon 19, costs 2 armour). (The MicroSol Option special
  31 FAMILIES.txt names spawns sidekick 19; it fires none of these.)
- 71: the Buster Rocket sidekick (11, shop 2:5; ammo 30), weapon 94: one rocket accelerating up the screen.
- 271-274: the MicroBomb sidekick (13, shop 1:7; ammo 60), weapon 29: a bomb drifting up a pixel a frame; the 8-Way
  MicroBomb (14, shop 1:11; ammo 30), weapon 298: eight, a pixel a frame every way; the specials MineField (9: weapon
  29 sprayed through a flare), Minefield (20: weapon 710 sprayed) and 8-Way Microbomb (45: weapon 29). A player's shot
  shows weapani + 1 frames: 271 272 273 274, one a frame (274 is 272 again).
- 238: the Post-It Mine sidekick (15, shop 1:2; ammo 20), weapon 86: one mine standing, then accelerating up the screen
  (a pixel a frame each frame); the Post-It Blast special (21, weapon 708: seven fanned out, costs 5 armour).
None of them is drawn turned: every sprite flies as drawn (yaw 0). All but the Post-It Mine and the MicroBomb leave
smoke in the game's data (trail 6): their lines take trail (the smoke trail and its spark), as Batch AS's missiles do.

As the sprites draw them (palette indices; a dark outline 0x20 round the first three):
- 34: a pink-red missile (ramp 4) 4 pixels wide (columns 3-6, its axis between columns 4 and 5: x = -1) from a blunt
  pale nose (rows 0-2: 0x4c-0x4e) down a body of 0x48-0x4a, lit down its left middle, to its tail (rows 8-13), where two
  wide fins (columns 0-2 and 7-9, 0x4a-0x4d at their outer edges) stand out to either side and a 2-pixel nozzle closes
  the body at the cell's bottom edge.
- 142: a stubby bomb 6 pixels wide (columns 3-8, x = 0): a grey nose cap (rows 1-4, ramp 0, 0x0f at its upper left), a
  waist 4 pixels wide glowing red (rows 5-8, ramp 7, hottest 0x7c at row 6), a grey tail (rows 9-12): a bright collar
  (row 10) and three fins seen from above (columns 3, 5-6 and 8, dark between).
- 71: the same tail under a blue glowing core (rows 4-8, ramp 9, hottest 0x9e at row 6) held in a grey head: a crossbar
  10 pixels wide (rows 2-3) with three prongs on top (row 1, columns 2-3, 5-6, 8-9) and two legs hanging down beside
  the core (columns 1 and 10, rows 4-7).
- 271-274: a ball 11 pixels across (columns 0-10, rows 2-12; its middle at x = -0.5, y = -0.5) of steel blue (ramp 3)
  round a belt of fire across its middle (rows 6-8, ramp 7), flashing: 271 dim (the belt 0x73-0x7f), 272 brighter, 273
  nearly white (its caps 0x3f, the belt 0x7f), 274 = 272.
- 238: an X 12 pixels across: a tan stick (ramp 11: 0xb5-0xbe, slate 0x65-0x68 at its edges) from the upper right to the
  lower left, a steel one (ramp 6: 0x6b 0x6c, its edges a dark brown 0xb1 0xb2) from the upper left to the lower right,
  crossing at a pale knot (0xbf 0xbc) flanked by slate (0x67).

The models (each as its sprite draws it, its origin the cell's middle, built on z = 0):
- shot_megamissile (34): a half-body turned about the sprite's axis: a pale pink nose cone (0x4d), a dark seam (0x43),
  the body (0x48), a pale collar (0x4d) and the tail (0x4a) narrowing into a dark nozzle (0x43); two wide swept side
  fins and a smaller one on top (0x4a); a short flame (0x7a round 0x7d) out of the nozzle. 6 materials.
- shot_atombomb (142): a grey nose cap (0x0a, its dome 0x0d), the waist a glowing core (0x76, its middle 0x79 round the
  sprite's hottest row, glowing 0.45-0.55), the tail (shared with the Buster Rocket): a grey ring and a pale collar, a
  narrower body with three swept fins and a dark nozzle with a small flame in the core's colours. 5 materials.
- shot_buster (71): the tail, a blue glowing core (0x99, its middle 0x9c), a grey crossbar puffed round on top with
  three prongs and two tapering legs, a flame of fire (0x7a round 0x7d) as the other missiles' (the trail's spark is
  orange).
- shot_microbomb_271, _272, _273 (274 takes _272): a ball flattened underneath, turned about the screen's y so that its
  belt runs across its middle as the sprite's does, the belt standing a little proud between dark lips (0x35); one
  mesh, the three flashes' materials (caps 0x3b, 0x3c, 0x3e glowing 0.28-0.48; the belt 0x79/0x7b, 0x7a/0x7c,
  0x7c/0x7e glowing 0.45-0.62); leant towards the camera (LEAN: the camera then sees its belt across its middle, not
  over its top). 4 materials.
- shot_postit (238): two spindles crossed as the sprite's sticks, a brass one (0xbb) tipped with slate (0x68) lying over
  a steel one (0x6c) tipped dark (0x66), pinned by a pale domed rivet (0xbe) in a dark ring (0x66).
Glow (each line's glow= replaces the automatic glow): on the flames, the cores and the belt in their own colours, small;
a pale one on the Post-It's rivet (its thin spikes read at 1x with it, as the sprite's glowing X did).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the origin at the
sprite's centre (pixel 6, 7 of the cell: column c is x = c + 0.5 - 6, row r is y = 6.5 - r, its top edge y = 7 - r).

Triangles: 892 (the missile), 730 (the Atom Bomb), 1 452 (the Buster Rocket), 750 (each MicroBomb), 960 (the Post-It
Mine). The fins are flat plates (fin() below: shot_kit.fin's bevelled slab came out of Blender's bevel split differently
from build to build).

models.cfg: --cfg <file> writes the block (MODELS and TITLE below: the model lines, the shot lines with their glow=).

Run: Blender -b --factory-startup -P tools/blender/models/shots/polish_shot_ordnance.py -- [--only <name,...>]
     [--outdir <dir>] (default assets/models/shots) [--check <sheets dir>] (each model's top view against its sprite in
     <dir>/shots.png, from TYR3D_EXTRACT) [--preview <prefix>] (top, three-quarter and game-camera views) [--cfg <file>]
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "enemies"))
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
import shot_kit as sk  # noqa: E402  (Batch AS's kit: fins, the top-view raster against the sprites)
from shot_kit import s  # noqa: E402  (the sidekicks' shapes: puff, lathe_axis, tube, sphere, hoop)
from polish_shot_fireball import view  # noqa: E402

OUTDIR = os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "shots")


# === The kit (polish_shot_novelty.py imports it) ======================================================================

def pal(name, index, emit=0.0, roughness=0.4, metallic=0.0):
    """A palette material (its colour follows the level's palette, fades and filters), glowing in its own colour."""
    return k.material(f"{name}_{index:02x}", palette=index, metallic=metallic, roughness=roughness,
                      emission=k.level_palette()[index] if emit > 0 else None, emission_strength=emit)


def finish(name, verts, faces, face_mats, angle=60.0):
    """A mesh from faces and their materials (each used material one slot, in the order first used)."""
    obj = k.mesh_object(name, verts, faces)
    used = []
    for m in face_mats:
        if m not in used:
            used.append(m)
    for m in used:
        obj.data.materials.append(m)
    for poly, m in zip(obj.data.polygons, face_mats):
        poly.material_index = used.index(m)
    k.recalc_normals(obj)
    return k.smooth(obj, angle)


def half_revolve(name, profile, x=0.0, z=0.0, segments=10, squash=1.0, under=None, angle=60.0):
    """A half-body turned about the line along +Y through (x, z): round on top, flat underneath (z). profile: [(y, r,
    material)] in increasing y (rings at the colours' borders, so no face is cut); the surface from a ring to the next
    takes the ring's material. r == 0 at an end: a point; r > 0: a flat half-disc closes it (the end ring's material).
    Two rings at the same y make a step. under: the flat underside's material (default the first ring's)."""
    verts, faces, mats = [], [], []
    rings = []
    for y, r, _ in profile:
        if r <= 1e-6:
            verts.append((x, y, z))
            rings.append(len(verts) - 1)
        else:
            ring = []
            for j in range(segments + 1):
                a = math.pi * j / segments
                verts.append((x + r * math.cos(a), y, z + r * math.sin(a) * squash))
                ring.append(len(verts) - 1)
            rings.append(ring)
    under = under if under is not None else profile[0][2]
    for i in range(len(rings) - 1):
        a, b, m = rings[i], rings[i + 1], profile[i][2]
        if isinstance(a, int) and isinstance(b, int):
            continue
        if isinstance(a, int):
            for j in range(segments):
                faces.append((a, b[j + 1], b[j]))
                mats.append(m)
            faces.append((a, b[0], b[-1]))
            mats.append(under)
        elif isinstance(b, int):
            for j in range(segments):
                faces.append((a[j], a[j + 1], b))
                mats.append(m)
            faces.append((a[-1], a[0], b))
            mats.append(under)
        else:
            for j in range(segments):
                faces.append((a[j], a[j + 1], b[j + 1], b[j]))
                mats.append(m)
            faces.append((a[-1], a[0], b[0], b[-1]))
            mats.append(under)
    if not isinstance(rings[0], int):
        faces.append(tuple(rings[0]))
        mats.append(profile[0][2])
    if not isinstance(rings[-1], int):
        faces.append(tuple(reversed(rings[-1])))
        mats.append(profile[-2][2] if len(profile) > 1 else profile[-1][2])
    return finish(name, verts, faces, mats, angle)


def smooth_profile(points, borders=(), step=0.4):
    """A smooth radius profile [(y, r)] (tyrkit.profile: Catmull-Rom through the points, every step) with samples added
    at each border y (where the colours change: those become rings of the mesh)."""
    samples = k.profile(points, step=step)
    out = list(samples)
    for b in borders:
        if points[0][0] < b < points[-1][0] and not any(abs(b - y) < 1e-6 for y, _ in out):
            out.append((b, sk.interp(samples, b)))
    return sorted(out)


def banded(profile, bands):
    """[(y, r, material)] from a profile [(y, r)] and bands [(from y, material)] (ascending; the first from -inf)."""
    out = []
    for y, r in profile:
        m = bands[0][1]
        for y0, mat in bands:
            if y >= y0 - 1e-6:
                m = mat
        out.append((y, r, m))
    return out


def flame(name, x, y_root, y_tip, radius, outer, core, z=0.0):
    """A rocket's flame along -Y out of a nozzle at y_root: a half-cone of outer round a raised core (flat
    underneath)."""
    length = y_root - y_tip
    parts = [half_revolve(name, [(y_tip, 0.0, outer), (y_tip + length * 0.45, radius * 0.62, outer),
                                 (y_tip + length * 0.8, radius * 0.98, outer), (y_root, radius, outer)],
                          x=x, z=z, segments=8, angle=80)]
    parts.append(half_revolve(name + "_core", [(y_tip + length * 0.45, 0.0, core),
                                               (y_tip + length * 0.75, radius * 0.5, core),
                                               (y_root + 0.05, radius * 0.62, core)],
                              x=x, z=z, segments=6, squash=1.35, angle=80))
    return parts


def fin(name, root, tip, angle, mat, thickness=0.4, x=0.0, z=0.0):
    """A swept fin standing out from a body along Y (as shot_kit.fin takes it): root = (radius, y front, y back) where
    it leaves the body, tip = (radius, y front, y back) at its outer edge; angle round the body (0 = +X, 90 = up towards
    the camera). A plate thinner at its tip, its faces flat (shot_kit.fin's bevelled slab came out of Blender's bevel
    with its faces split differently from run to run: the GLBs must be the same every build)."""
    r0, f0, b0 = root
    r1, f1, b1 = tip
    outline = [(r0, f0, 1.0), (r1, f1, 0.55), (r1, b1, 0.55), (r0, b0, 1.0)]
    verts = []
    for side in (1, -1):
        for r, y, t in outline:
            verts.append((r, y, side * thickness / 2 * t))
    faces = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    obj = finish(name, verts, faces, [mat] * len(faces), 30.0)
    # Built in the XY plane (its span along X), turned round Y to its angle, then moved to the axis.
    obj.data.transform(Matrix.Translation((x, 0, z)) @ Matrix.Rotation(-math.radians(angle), 4, "Y"))
    k.recalc_normals(obj)
    return obj


def objects():
    return [o for o in bpy.context.scene.objects if o.type == "MESH"]


# The game's camera looks down from the bottom of the screen, 20 degrees off straight down at the bottom of the view and
# 35 at its top: an upright ball's top shows a pixel or two above its middle (a belt over it looks drawn across its top)
# and its near side wide. Round objects lean towards the camera (every point moved down the screen by LEAN times its
# height, tan 26.6 degrees: polish_shot_pellet.py's way), so that the camera sees them laid out as the sprite draws
# them.
LEAN = 0.5


def lean(parts, amount=LEAN):
    for obj in parts:
        obj.data.transform(Matrix(((1, 0, 0, 0), (0, 1, -amount, 0), (0, 0, 1, 0), (0, 0, 0, 1))))
    return parts


def upright_copies(parts, amount=LEAN):
    """Copies of leant parts set upright again (for the top-view checks); remove them with remove_copies."""
    copies = []
    for obj in parts:
        copy = obj.copy()
        copy.data = obj.data.copy()
        bpy.context.scene.collection.objects.link(copy)
        copies.append(copy)
    return lean(copies, -amount)


def remove_copies(copies):
    for copy in copies:
        mesh = copy.data
        bpy.data.objects.remove(copy)
        bpy.data.meshes.remove(mesh)


# --- Checks -----------------------------------------------------------------------------------------------------------

def check_sprite(name, parts, sheets, sheet, sprite, leant=0.0):
    """The model's top view (shot_kit.raster: every triangle seen from above, at the sprite's 12 x 14 pixels) against
    the sprite: the overlap (intersection over union), the mean colour difference where both cover, and the map ('#'
    both, '+' the model only, '-' the sprite only). A model leant towards the camera is set upright again first (its top
    as the game's camera sees it over its footprint)."""
    tris = sk.top_triangles()
    if leant:
        tris[0][..., 1] += leant * tris[0][..., 2]
    sprite_data = sk.sprite_image(sheets, sheet, sprite)
    cov, rgb = sk.raster(tris, 0)
    print("  %s on %s %d: overlap %.3f, colour difference %.3f" % (name, sheet, sprite, sk.overlap(cov, sprite_data[0]),
                                                                 sk.colour_distance(cov, rgb, sprite_data)))
    sk.print_map(cov, sprite_data[0])


# --- The registry and the build loop ----------------------------------------------------------------------------------

class Model:
    """One GLB: name, its sprites' shot lines [(sheet, sprite, options, comment)], the builder (returns its objects) and
    the sprite its top view is checked against; origin: drawn at its own origin (pieces of one object); leant: how far
    the builder leans it towards the camera (the check sets it upright again)."""

    def __init__(self, name, lines, build, what, check=None, origin=False, leant=0.0):
        self.name, self.lines, self.build, self.what, self.check, self.origin = name, lines, build, what, check, origin
        self.leant = leant


def cfg_block(models, title):
    """The block's model lines and shot lines, aligned as the earlier shot blocks are."""
    out = ["# " + line for line in title]
    width = max(len(m.name) for m in models)
    for m in models:
        out.append(("model %s shots/%s.glb%s" % (m.name.ljust(width), m.name, " origin" if m.origin else "")).rstrip())
    rows = []
    for m in models:
        for sheet, sprite, opts, comment in m.lines:
            rows.append(("shot %s %s" % (("%s %d" % (sheet, sprite)).ljust(10), m.name.ljust(width)), opts, comment))
    w0 = max(len(r[0]) for r in rows)
    w1 = max(len(r[1]) for r in rows)
    for head, opts, comment in rows:
        out.append("%s %s  # %s" % (head.ljust(w0), opts.ljust(w1), comment))
    return out


def run(models, groups=(), title=()):
    """Builds every model (or --only's), exports it to --outdir, checks it against its sprite (--check), previews it
    (--preview <prefix>) and writes the models.cfg block (--cfg <file>). groups: [(names, builder)] whose builder
    returns {name: objects} for several models at once (an object built whole and cut into the sprites' pieces)."""
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    outdir = options.get("outdir", OUTDIR)
    sheets = options.get("check")
    by_name = {m.name: m for m in models}
    for m in models:
        if only is not None and m.name not in only or any(m.name in names for names, _ in groups):
            continue
        k.reset()
        parts = triangulate(m.build())
        bpy.context.view_layer.update()
        print("== %s: %s" % (m.name, m.what))
        if sheets and m.check:
            check_sprite(m.name, parts, sheets, *m.check, leant=m.leant)
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(m.name, parts, os.path.join(outdir, m.name + ".glb"))
        if "preview" in options:
            view(options["preview"] + m.name, parts)
    for names, builder in groups:
        if only is not None and not any(n in only for n in names):
            continue
        k.reset()
        pieces = builder(sheets)
        for name in names:
            if only is not None and name not in only:
                continue
            parts = pieces[name]
            for o in objects():
                o.hide_render = o not in parts
            print("== %s: %s" % (name, by_name[name].what))
            bpy.context.scene.view_settings.view_transform = "Standard"
            mk.report(name, parts, os.path.join(outdir, name + ".glb"))
            if "preview" in options:
                view(options["preview"] + name, parts)
    if "cfg" in options:
        with open(options["cfg"], "w") as f:
            f.write("\n".join(cfg_block(models, title)) + "\n")
        print("wrote", options["cfg"])


# === The models =======================================================================================================

# --- The MegaMissile (34) ---------------------------------------------------------------------------------------------

MM_X = -1.0  # the axis: between the sprite's columns 4 and 5
# The body's radius along it (y, r) from the nozzle's end (the cell's bottom edge) to the nose's tip (its top edge); the
# outline the sprite draws round it is in the radius (2.0 coloured, 2.2 with a little of the outline).
MM_PROFILE = [(-7.0, 1.0), (-6.4, 1.15), (-5.8, 1.35), (-5.45, 1.75), (-5.1, 2.1), (-4.6, 2.2), (3.9, 2.2),
              (4.6, 2.12), (5.3, 1.88), (6.0, 1.45), (6.55, 0.92), (6.92, 0.42), (7.05, 0.0)]
# Its colours along it (from y, palette index): the nozzle, the tail, a pale collar, the body, a dark seam, the nose.
MM_BANDS = [(-99.0, 0x43), (-5.45, 0x4a), (-3.9, 0x4d), (-3.1, 0x4a), (-2.3, 0x48), (4.15, 0x43), (4.55, 0x4d)]
MM_EMIT = {0x4d: 0.15, 0x4a: 0.06, 0x48: 0.06}
MM_ROUGH, MM_METAL = 0.34, 0.25


def megamissile():
    mats = {i: pal("mm", i, MM_EMIT.get(i, 0.0), MM_ROUGH, MM_METAL) for i in (0x43, 0x48, 0x4a, 0x4d)}
    borders = [b for b, _ in MM_BANDS[1:]]
    prof = banded(smooth_profile(MM_PROFILE, borders, 0.6), [(b, mats[i]) for b, i in MM_BANDS])
    prof[0] = (prof[0][0], prof[0][1], mats[0x43])
    parts = [half_revolve("mm_body", prof, x=MM_X, segments=12)]
    # Two wide fins out to the sides (the sprite's columns 0-2 and 7-9, rows 8-13) and a smaller one on top.
    for a in (0, 180):
        parts.append(fin("mm_fin", (1.9, -0.8, -6.4), (4.5, -2.9, -7.25), a, mats[0x4a], 0.45, x=MM_X))
    parts.append(fin("mm_fin_top", (1.9, -1.8, -6.3), (3.0, -3.6, -6.9), 90, mats[0x4a], 0.4, x=MM_X))
    outer, core = pal("mm_flame", 0x7a, 0.55, 0.5), pal("mm_flame", 0x7d, 0.6, 0.45)
    parts += flame("mm_flame", MM_X, -6.95, -9.4, 0.85, outer, core)
    return parts


# --- The tail the Atom Bomb and the Buster Rocket share (rows 9-12) ---------------------------------------------------

def tail(prefix, grey, pale, dark, flame_outer, flame_core):
    """A grey ring under the core (row 9), a pale collar (row 10), a narrower body (rows 11-12) with three swept fins
    (left, right, on top: the sprite's columns 3, 5-6 and 8), a dark nozzle and a small flame."""
    prof = [(-6.25, 0.95, dark), (-5.95, 1.25, grey), (-5.4, 1.65, grey), (-4.7, 1.95, grey), (-4.25, 2.0, grey),
            (-4.25, 2.9, pale), (-3.95, 3.05, pale), (-3.15, 3.05, pale), (-3.0, 2.75, dark), (-2.75, 2.75, dark),
            (-2.6, 3.0, grey), (-2.05, 3.0, grey), (-2.0, 0.0, grey)]
    parts = [half_revolve(prefix + "tail", prof, segments=12)]
    for a in (0, 180):
        parts.append(fin(prefix + "fin", (1.7, -4.25, -6.0), (3.2, -4.75, -6.45), a, grey, 0.42))
    parts.append(fin(prefix + "fin_top", (1.7, -4.25, -6.0), (3.05, -4.85, -6.45), 90, pale, 0.4))
    parts += flame(prefix + "flame", 0.0, -6.2, -8.0, 0.8, flame_outer, flame_core)
    return parts


# --- The Atom Bomb (142) ----------------------------------------------------------------------------------------------

AB_CORE = ((0x76, 0.45), (0x79, 0.55))  # the glowing waist (rows 5-8): its ends' colour and glow, its middle's
AB_HOT = (-0.55, 1.05)  # where its middle band lies (y: the sprite's hottest row 6, a row above the waist's middle)


def atombomb():
    grey, pale, dark = pal("ab", 0x0a, 0.0, 0.35, 0.3), pal("ab", 0x0d, 0.0, 0.3, 0.3), pal("ab", 0x04, 0.0, 0.5, 0.2)
    core, hot = (pal("ab_core", i, e, 0.4) for i, e in AB_CORE)
    parts = tail("ab_", grey, pale, dark, core, hot)
    # The glowing waist (rows 5-8, 4 pixels wide), hotter round the sprite's hottest row.
    lo, hi = AB_HOT
    parts.append(half_revolve("ab_core", [(-2.05, 2.05, core), (lo, 2.05, hot), (hi, 2.05, core), (2.05, 2.05, core)],
                              segments=12, angle=80))
    # The nose cap (rows 1-4): a short drum with a domed top.
    cap = [(2.0, 3.0, dark), (2.25, 3.1, grey), (2.55, 3.15, grey), (4.9, 3.15, grey), (5.35, 2.95, pale),
           (5.8, 2.55, pale), (6.15, 1.9, pale), (6.38, 1.05, pale), (6.48, 0.0, pale)]
    parts.append(half_revolve("ab_cap", cap, segments=12))
    return parts


# --- The Buster Rocket (71) -------------------------------------------------------------------------------------------

BR_CORE = ((0x99, 0.45), (0x9c, 0.58))  # the blue core (rows 4-8): its ends', its middle's colour and glow
BR_HOT = (-0.5, 1.2)  # its middle band (the sprite's 0x9e, row 6)


def buster():
    grey, pale, dark = pal("br", 0x0a, 0.0, 0.35, 0.3), pal("br", 0x0d, 0.0, 0.3, 0.3), pal("br", 0x04, 0.0, 0.5, 0.2)
    core, hot = (pal("br_core", i, e, 0.35) for i, e in BR_CORE)
    parts = tail("br_", grey, pale, dark, pal("br_flame", 0x7a, 0.55, 0.5), pal("br_flame", 0x7d, 0.6, 0.45))
    # The blue core (rows 4-8): a capsule rising into the crossbar, its hot spot raised out of its top.
    lo, hi = BR_HOT
    pts = [(-2.05, 2.0, core), (lo, 2.0, hot), (hi, 2.0, core), (1.6, 2.0, core), (2.0, 1.85, core), (2.5, 1.5, core),
           (2.9, 1.0, core), (3.15, 0.0, core)]
    parts.append(half_revolve("br_core", pts, segments=12, angle=80))
    # The crossbar (rows 2-3, columns 1-10) puffed round on top, with three prongs (row 1) and two legs down beside the
    # core (columns 1 and 10, rows 4-7).
    bar = s.superellipse(0.0, 4.2, 5.05, 1.3, power=5.0, count=32)
    parts.append(s.puff("br_bar", bar, 0.0, 2.7, grey, side=0.3, steps=4, power=2.4))
    parts.append(s.puff("br_bar_top", s.superellipse(-0.2, 4.45, 3.6, 0.7, power=4.0, count=20), 2.2, 2.95, pale,
                        side=0.2, steps=3, power=2.2))
    for px_ in (-3.0, 0.0, 3.0):
        parts.append(s.lathe_axis("br_prong", [(0.0, 0.95), (0.45, 0.92), (0.95, 0.7), (1.35, 0.38), (1.6, 0.0)],
                                  pale if px_ == 0.0 else grey, (px_, 5.0, 1.15), (0, 1, 0), segments=10, squash=0.9,
                                  smooth_angle=70))
    for side in (-1, 1):
        pts = [(side * 4.35, 3.6, 1.05), (side * 4.5, 2.2, 0.95), (side * 4.55, 0.6, 0.85), (side * 4.6, -1.2, 0.7)]
        parts.append(s.tube("br_leg", pts, [1.05, 0.9, 0.7, 0.45], grey, 8, squash=0.9))
    return parts


# --- The MicroBomb (271-274) ------------------------------------------------------------------------------------------

MB_CENTRE = (-0.5, -0.5)  # the ball's middle (columns 0-10, rows 2-12)
MB_RADIUS = 5.2
MB_BELT = 1.45  # half the belt's height (rows 6-8)
MB_PROUD = 0.28  # how far the belt stands out of the ball
MB_LIP = 0x35  # the belt's lips: dark steel (a seam round each cap too made the ball a striped beach ball)
# The three flashes: (caps' index, glow), (the belt's lower and upper halves' indices), glows.
MB_FRAMES = {
    271: (0x3b, 0.28, 0x79, 0.45, 0x7b, 0.5),
    272: (0x3c, 0.34, 0x7a, 0.5, 0x7c, 0.56),
    273: (0x3e, 0.48, 0x7c, 0.56, 0x7e, 0.62),
}


def microbomb(frame):
    cap_i, cap_e, low_i, low_e, high_i, high_e = MB_FRAMES[frame]
    cap = pal("mb_cap", cap_i, cap_e, 0.3, 0.35)
    lip = pal("mb_lip", MB_LIP, 0.1, 0.45, 0.3)
    low, high = pal("mb_belt", low_i, low_e, 0.45), pal("mb_belt", high_i, high_e, 0.42)
    cx, cy = MB_CENTRE
    R = MB_RADIUS

    def ball(dy):
        return math.sqrt(max(R * R - dy * dy, 0.0))
    # The south cap's rings (closer near the pole, where the ball turns fastest), the belt, the north cap mirrored.
    prof = []
    south = [-R, -5.05, -4.7, -4.15, -3.5, -2.8, -2.15, -MB_BELT - 0.12]
    for dy in south:
        prof.append((cy + dy, 0.0 if dy == -R else ball(dy), cap))
    # The belt: a lip, the lower half, the upper half, a lip.
    lip_r = ball(MB_BELT) + MB_PROUD
    prof += [(cy - MB_BELT - 0.12, lip_r - 0.05, lip), (cy - MB_BELT + 0.15, lip_r, lip),
             (cy - MB_BELT + 0.3, ball(MB_BELT - 0.3) + MB_PROUD - 0.06, low),
             (cy - 0.6, ball(0.6) + MB_PROUD - 0.08, low), (cy, ball(0.0) + MB_PROUD - 0.06, high),
             (cy + 0.6, ball(0.6) + MB_PROUD - 0.08, high),
             (cy + MB_BELT - 0.3, ball(MB_BELT - 0.3) + MB_PROUD - 0.06, lip), (cy + MB_BELT - 0.15, lip_r, lip),
             (cy + MB_BELT + 0.12, lip_r - 0.05, cap)]
    for dy in reversed(south):
        prof.append((cy - dy, 0.0 if dy == -R else ball(dy), cap))
    return lean([half_revolve("mb_ball", prof, x=cx, segments=14, angle=70, under=cap)])


# --- The Post-It Mine (238) -------------------------------------------------------------------------------------------

def spindle(name, p0, p1, radius, shaft, tip, tip_len=1.5, z=0.9, segments=8):
    """A spindle (thick in the middle, pointed at both ends) from p0 to p1 at height z: a shaft of one material and
    tips of another, turned round its axis."""
    a, b = Vector((p0[0], p0[1], z)), Vector((p1[0], p1[1], z))
    d = (b - a)
    length = d.length
    d.normalize()
    mid = [(tip_len - 0.05, radius * 0.72), (length * 0.28, radius * 0.92), (length * 0.5, radius),
           (length * 0.72, radius * 0.92), (length - tip_len + 0.05, radius * 0.72)]
    parts = [s.lathe_axis(name, mid, shaft, tuple(a), tuple(d), segments=segments, smooth_angle=70)]
    for t0, sign in ((0.0, 1), (length, -1)):
        prof = [(0.0, 0.0), (0.12, radius * 0.25), (tip_len * 0.55, radius * 0.55), (tip_len, radius * 0.72)]
        start = a + d * t0
        parts.append(s.lathe_axis(name + "_tip", prof, tip, tuple(start), tuple(d * sign), segments=segments,
                                  smooth_angle=70))
    return parts


def postit():
    brass, slate = pal("pm", 0xbb, 0.12, 0.35, 0.4), pal("pm", 0x68, 0.08, 0.35, 0.5)
    steel, dark = pal("pm", 0x6c, 0.1, 0.3, 0.5), pal("pm", 0x66, 0.05, 0.45, 0.3)
    rivet = pal("pm", 0xbe, 0.25, 0.3, 0.3)
    parts = spindle("pm_steel", (-4.75, 4.75), (4.7, -4.7), 1.15, steel, dark, 1.5, z=1.1)
    parts += spindle("pm_brass", (-5.75, -5.75), (5.75, 5.75), 1.2, brass, slate, 1.6, z=1.5)
    parts.append(s.hoop("pm_ring", (0.0, 0.0, 1.75), 1.65, 1.65, 0.45, dark, 24, 8, squash=0.8))
    parts.append(s.sphere("pm_rivet", (0.0, 0.0, 1.95), (1.55, 1.55, 1.0), rivet, 16, 8))
    return parts


# === The block ========================================================================================================

MODELS = [
    Model("shot_megamissile", [("shots", 34, "trail glow=8:0.4:122:-1:8.4", "MegaMissile (sidekick 6, weapon 15)")],
          megamissile, "a pink-red missile, a pale nose, wide swept fins, a flame", ("shots", 34)),
    Model("shot_atombomb", [("shots", 142, "trail glow=9:0.45:122:0:0", "Atom Bombs (sidekick 7, special 38)")],
          atombomb, "a stubby grey bomb round a glowing red core, fins", ("shots", 142)),
    Model("shot_buster", [("shots", 71, "trail glow=9:0.45:156:0:-0.5", "Buster Rocket (sidekick 11, weapon 94)")],
          buster, "a grey rocket, a blue glowing core in a three-pronged head, fins", ("shots", 71)),
    Model("shot_microbomb_271", [("shots", 271, "glow=10:0.3:122:-0.5:0.5",
                                  "MicroBomb (sidekicks 13, 14; specials 9, 20, 45): dim")],
          lambda: microbomb(271), "a steel-blue ball round a glowing belt (dim)", ("shots", 271), leant=LEAN),
    Model("shot_microbomb_272", [("shots", 272, "glow=10:0.4:123:-0.5:0.5", "... brighter"),
                                 ("shots", 274, "glow=10:0.4:123:-0.5:0.5", "... (274 is 272)")],
          lambda: microbomb(272), "the same, brighter", ("shots", 272), leant=LEAN),
    Model("shot_microbomb_273", [("shots", 273, "glow=10:0.5:124:-0.5:0.5", "... flashing")],
          lambda: microbomb(273), "the same, flashing", ("shots", 273), leant=LEAN),
    Model("shot_postit", [("shots", 238, "glow=9:0.3:190:0:0", "Post-It Mine (sidekick 15, special 21)")],
          postit, "a brass spike crossed over a steel one, pinned by a pale rivet", ("shots", 238)),
]

TITLE = [
    "The sidekicks' and specials' ordnance (tools/blender/models/shots/polish_shot_ordnance.py): the MegaMissile's",
    "pink-red missile (34), the Atom Bombs' stubby grey bomb round a glowing red core (142), the Buster Rocket's",
    "grey rocket with a blue glowing core in a three-pronged head (71), the MicroBomb's steel-blue ball round a belt",
    "of fire, flashing frame by frame (271 272 273 274: three models, 274 is 272; leant towards the camera, so that",
    "its belt shows across its middle as the sprite's), the Post-It Mine's brass spike crossed over a steel one",
    "(238). Half-bodies (flat underneath) as their sprites draw them, flying as drawn; the missiles' lines take",
    "trail (their weapons leave smoke); each glow= sits on the flame, the core, the belt or the Post-It's rivet.",
]


if __name__ == "__main__":
    run(MODELS, title=TITLE)
