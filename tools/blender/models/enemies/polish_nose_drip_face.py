"""NOSE DRIP's face (episode 4, NOSE DRIP's boss; all top-layer enemies of one frame, none animated, no damaged looks:
dgr 0), polished (2026-10-22, round 37):
- face_eye (5 270; enemy 780, two of them): the eyeballs;
- nose_bridge, nose_tip_left, nose_tip_right (5 154 above 191 beside 193; enemies 781, 782, 783): the nose;
- nosedrip_nostrils, nosedrip_tongue (x5e 267 above 269; enemies 792, 793): the tongue (the first is its root: the
  name is the old one);
- fire_bowl_left, fire_bowl_right (5 156 beside 158; enemies 786, 787, four pairs): the bowl of flames it sneezes.
They replace wave2_e.py's face_eye() (a white ball with caps for the iris), wave2_e_parts.py's nose (an inflated outline
with bumps), wave3_i.py's nosedrip_nostrils() and nosedrip_tongue() (regions raised from the pixels, two models that
did not meet) and wave3_l_parts.py's fire bowl (a molten trough with tubes for tongues).

How NOSE DRIP puts the face together (its events at t100, event 7: the top layer; the sprites' middles, x and dat5):
the tongue first (792 x5e 267 at 171, -26 over 793 x5e 269 at 171, 2: link 16), the boss's red blob (790, 5 121 at
171, -20: polish_blobs.py's blob_big), the bridge (781, 5 154 at 170, -28: link 19), the tip's halves (782 5 191 at
158, 0: link 18; 783 5 193 at 182, 0: link 17; t242 event 39 joins them to link 19), and last the eyes (780 at 156,
-30 and 184, -30: links 14 and 15). The game draws them in that order, so at rest the nose covers the tongue and the
blob and the eyes lie over the nose's flanks. Then every link moves on its own (event 19): the eyes fly out and come
back (t300-720), the blob leaves its hiding place behind the nose (t250 on), the tongue slides out from under the nose
32 pixels (t1112, 1170, 1270) and once 120 (t1350-1390), the nose wanders and comes back (t1139-1590) and becomes the
boss (link 254, t5001). So every part is a whole object on its own, as it is seen alone. The bowl of flames (786 at
x 158, 787 at 182, dat5 100: the tips' place then; t406 joins them into one link) is made at t405, 645, 1120 and 1620
right over the nose's tip and falls down the screen (eyc 3). Nothing else shows these sprites; 5 270 is EYESPY's
green eye (5 79) pixel for pixel in ramp 3, every shade three lighter (clipped at 15).

As the sprites and their 4x upscales draw them (lit from the upper left):
- The eye (5 270): polish_green_eye.py's eyeball in blue and white: a white glossy ball in a dark blue outline, its
  blue iris below the middle looking down the screen at the player and up at the camera, a black pupil.
- The nose (a 48 x 56 picture: 154 at its columns 12-35 of rows 0-27 over 191 and 193 at 0-23 and 24-47 of rows
  28-55; ramp 1's tans and browns, 0x01 black): a narrow bridge from row 2 widening down to the tip, its crest lit
  (columns 19-22: shades b-d), its right flank in shadow down to a dark side wall (columns 30-34 of rows 15-28) that
  runs on into the right wing; the round tip (columns 17-30 of rows 27-40, lit on its upper left, shades d-f), the
  wings either side (columns 6-17 and 30-43 of rows 29-47, the left one lit, the right one dull, an alar crease
  between the tip and the right wing), black nostrils under the wings (columns 12-21 of rows 40-45 and 28-37 of rows
  39-47) and the columella between them down to row 51.
- The tongue (a 24 x 56 picture: 267 over 269; ramp 4's reds, 0x40 its dark outline): a broad tongue hanging down the
  screen, a groove down its middle (columns 11-12), its rounded tip at row 49; its root at the top (rows 2-12) torn
  and lumpy, three sores glowing in the fire's reds (ramp 7: columns 3-6 of rows 6-9, 10-14 of rows 5-10, 17-20 of
  rows 8-11), a glint at column 13 of row 8.
- The bowl of flames (a 48 x 28 picture: 156 beside 158; ramp 7, the fire's): a crescent of fire, white-hot and yellow
  low in the bowl, orange and red up its walls, tongues of flame rising from its rim (rows 0-10), dark red at its
  edges.

Built for the game's camera as polish_skull_chest.py and polish_green_shell.py are (the nose, the tongue and the bowl
each one heightfield in the picture's plane, sheared along the camera's line of sight, y - z tan 20, on
polish_gyges_wall.Plate's grid, 0.5 pixel apart, whose lines are the pieces' edges, so each piece is the cells of its
sprite's box; every point is where the sprite draws it): the nose's bridge a rounded ridge rising from 3.0 at its root
to 9.9 over the tip and running on under it into the columella, the tip a dome 11.4 high, the wings domes 8 high, the
columella a ridge, all on a mound (the nose's lower part, 6 high) and joined by a smooth maximum, the nostrils sunk to
NOSTRIL_FLOOR (painted dark all through), the outline rounded over FALL; the tongue a slab TONGUE_H high, a little
domed, its groove sunk (and painted darker and duller: a long wall in the sun's glint drew a white line), the root's
lumps round its sores, pits glowing in the fire's reds (low: polish_drip.py's strengths); the bowl a trough whose
height follows the fire's heat, the hottest parts swelling, its tongues of flame low ridges falling to their tips.
Painted by the sprites' shades (polish_green_shell's Paint: each face the shade of the pixels under it, blurred,
lifted and lighter where the game's sun lights it less), the bowl in polish_drip.py's bands of the fire (each band
glowing in its own colour, 0.08-0.55, a little cooler than the drip's tubes, whose sides turn away). Heights (z over
the layer: origin pieces stand on it): the nose 0 to 11.5, the tongue 0 to 3.0 (so that the nose, drawn over it,
covers it at rest: its nostrils' floor is 4.3), the bowl 0 to 7.4. The eye stays polish_green_eye's ball, centred in
height (the game centres models without origin): -10.45 to 10.7.

The bowl is made right over the nose's tip and drawn after it: in the sprites it covers the nose's lower half for the
few ticks it takes to fall clear (3-5 pixels a tick); in 3D the nose's wings and tip (8-11.5 high) stand out of the
fire (7.4) for those ticks, the bowl bursting out from under them.

The pieces of each object meet when drawn at their own origins (models.cfg origin): the bridge's origin is the nose
picture's pixel edge (24, 14), the tip's (12, 42) and (36, 42); the tongue's (12, 14) and (12, 42); the bowl's (12, 14)
and (36, 14). Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; in a
picture, column c's left edge is x = c - w/2 and row r's top edge y = h/2 - r.

models.cfg: the model lines of nose_bridge, nose_tip_left, nose_tip_right, fire_bowl_left and fire_bowl_right stay
(origin); nosedrip_nostrils and nosedrip_tongue get origin (the two halves of one tongue now); face_eye stays (centred
in height, yaw=aim). The sprite lines stay.

Replaces wave2_e.py (all of it: face_eye() and the registration of wave2_e_parts.PIECES are all it builds; delete it),
wave2_e_parts.py and wave2_e_art.py (the nose only: delete them), wave3_i.py's nosedrip_nostrils() and
nosedrip_tongue() (its "^ 267, 269" section and their docstring line) with wave3_i_art.py's NOSE and TONGUE, and
wave3_l_parts.py's fire bowl (drip_bands(), BOWL, BOWL_PIECES, build_fire_bowl(), bowl_piece(), its PIECES entries and
its w.whole("fire_bowl", ...) registration) with wave3_l_art.py's FIRE_BOWL.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the outlines as the camera
sees them against the sprites' pixels, each object and each piece), --preview <prefix>, --only <name,...>.
"""
import math
import os
import sys

import bpy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_gyges_wall as gw  # noqa: E402  (Plate, the shear to the camera, the faces' light)
import polish_green_eye as ge  # noqa: E402  (the eyeball: 5 270 is 5 79's pixels in ramp 3)
from polish_green_shell import edt, limit_materials  # noqa: E402

S = 4                             # the fine grid of the fields: S cells a pixel


# --- The eye (5 270) ----------------------------------------------------------------------------------------------------
# polish_green_eye's eyeball (its shape, iris, groove, fibres, flecks and pupil, its middle at (-0.5, -1.5) looking up
# the screen LOOK_TILT up at the camera, so that yaw=aim turns it to look at the player) in the face eye's colours:
# ramp 3, every shade three lighter than the green eye's (as the sprite's are), the sclera four (the sprite's is nearly
# all white, 0x3d-0x3f), white-blue and glowing a little in its own colour (the slanted camera sees much of the ball's
# side away from the sun).

EYE_RAMP, EYE_LIFT = 3, 3


def eye_materials():
    pal = k.level_palette()

    def m(key, shade, glow=0.0, **kw):
        index = 16 * EYE_RAMP + min(15, shade + EYE_LIFT)
        if glow:
            kw.update(emission=pal[index], emission_strength=glow)
        return k.material("feye_%s" % key, palette=index, **kw)
    return {
        "sclera": m("sclera", 0x0b, 0.26, metallic=0.0, roughness=0.2),             # (0x3e: the sprite's is white)
        "sclera_shade": m("sclera_shade", 0x09, 0.2, metallic=0.0, roughness=0.24),
        "outline": m("outline", 0x04, 0.0, metallic=0.0, roughness=0.45),
        "groove": m("groove", 0x08, 0.0, metallic=0.0, roughness=0.25),
        "limbus": m("limbus", 0x03, 0.0, metallic=0.0, roughness=0.3),
        "iris": m("iris", 0x07, 0.22, metallic=0.0, roughness=0.1),
        "fibre": m("fibre", 0x08, 0.25, metallic=0.0, roughness=0.1),
        "flecks": m("flecks", 0x09, 0.3, metallic=0.0, roughness=0.1),
        "pupil": m("pupil", 0x00, 0.0, metallic=0.0, roughness=0.05),
    }


def build_eye():
    """polish_green_eye.eye() with the face eye's materials (its fields and displacement as they are there)."""
    shape = ge.Eye(ge.CENTRE, (ge.RADIUS, ge.RADIUS, ge.RADIUS))

    def rim(p, n):
        return n.z

    def round_look(p, n):
        return ge.from_look(shape.last)[0]

    def fibres(p, n):
        a, phi = ge.from_look(shape.last)
        if not ge.PUPIL < a < ge.IRIS:
            return -1.0
        wave = math.cos(ge.FIBRES * phi + ge.FIBRE_WOBBLE * math.sin(ge.FIBRE_LOBES * phi) + 0.06 * (a - ge.FLECKS))
        return wave - math.cos(math.pi * ge.FIBRE_WIDTH)

    def flecks(p, n):
        a, phi = ge.from_look(shape.last)
        return a - ge.FLECK_WAVE * math.cos(ge.FLECK_LOBES * phi + 1.1 * math.sin(2 * phi + 0.5))

    def displace(d, p, n):
        a, _ = ge.from_look(d)
        bulge = ge.CORNEA_BULGE * (1 - ge.smoothstep(ge.IRIS - 9.0, ge.IRIS, a))
        sink = ge.PUPIL_SINK * (1 - ge.smoothstep(ge.PUPIL - 2.0, ge.PUPIL + 1.0, a))
        g0, g1 = ge.GROOVE
        mid, half = (g0 + g1) / 2, (g1 - g0) / 2
        groove = ge.GROOVE_DEPTH * max(0.0, 1 - ((a - mid) / half) ** 2)
        return ge.RADIUS * (bulge - sink - groove)

    def iris_area(d):
        return ge.REFINE[0] < ge.from_look(d)[0] < ge.REFINE[1]

    paint = [
        (rim, (ge.OUTLINE_Z, ge.SHADE_Z), ("outline", "sclera_shade", "sclera")),
        (round_look, (ge.IRIS, ge.FLOOR[0], ge.FLOOR[1], ge.GROOVE[1]), ("iris", "groove", "limbus", "groove", None)),
        (fibres, (0.0,), (None, "fibre")),
        (flecks, (ge.FLECKS,), ("flecks", None)),
        (round_look, (ge.PUPIL,), ("pupil", None)),
    ]
    return ge.painted_eye("face_eye", shape, paint, eye_materials(), displace, iris_area)


def eye_model(out, options):
    k.reset()
    obj = build_eye()
    bpy.context.scene.view_settings.view_transform = "Standard"
    mk.report("face_eye", [obj], os.path.join(out, "face_eye.glb"))
    # The checks and previews: the eye as the game shows it with the player straight below it (yaw 180).
    ge.turned(180)
    if "check" in options:
        sheets = options["check"]
        k.check_silhouette(os.path.join(sheets, "enemy_5.png") if os.path.isdir(sheets) else sheets, 270)
    if "preview" in options:
        mk.preview(options["preview"] + "face_eye", [obj], distance=0.6)


# --- Pictures and fields ------------------------------------------------------------------------------------------------

class Picture:
    """A picture of palette indices (h, w; -1 none) placed in the picture's plane, its middle at the origin: column c's
    left edge at x = c - w/2, row r's top edge at y = h/2 - r; fields on its fine grid (S cells a pixel)."""

    def __init__(self, text, w, h, first_row):
        self.w, self.h = w, h
        self.left, self.top = -w / 2.0, h / 2.0
        a = -np.ones((h, w), int)
        for i, line in enumerate(text.split()):
            for c in range(w):
                t = line[2 * c:2 * c + 2]
                if t != "..":
                    a[first_row + i, c] = int(t, 16)
        self.a = a
        self.ramp = np.where(a >= 0, a >> 4, -1)
        self.shade = np.where(a >= 0, a & 15, 0).astype(float)

    def x(self, c):
        return c + self.left

    def y(self, r):
        return self.top - r

    def up(self, m):
        return np.repeat(np.repeat(m, S, 0), S, 1)

    def fine_xy(self):
        xs = self.left + (np.arange(self.w * S) + 0.5) / S
        ys = self.top - (np.arange(self.h * S) + 0.5) / S
        return np.meshgrid(xs, ys)

    def fine(self, values):
        """A sampler of values on the fine grid (bilinear between its cells' middles)."""
        return Field(values, self.left, self.top, S)

    def coarse(self, values):
        """A sampler of values of the pixels (bilinear between their middles)."""
        return Field(values, self.left, self.top, 1)

    def soft_mask(self, mask, sigma=0.8):
        """The mask on the fine grid with its outline smoothed (the 0.5 contour of its blur)."""
        return gw.blur(self.up(mask.astype(float)), sigma * S) > 0.5


class Field:
    def __init__(self, values, left, top, scale):
        self.v, self.left, self.top, self.s = values, left, top, scale

    def __call__(self, Xa, Ya):
        h, w = self.v.shape
        fc = np.clip((np.asarray(Xa, float) - self.left) * self.s - 0.5, 0.0, w - 1.0)
        fr = np.clip((self.top - np.asarray(Ya, float)) * self.s - 0.5, 0.0, h - 1.0)
        c0 = np.minimum(np.floor(fc).astype(int), w - 2)
        r0 = np.minimum(np.floor(fr).astype(int), h - 2)
        tc, tr = fc - c0, fr - r0
        v = self.v
        return ((v[r0, c0] * (1 - tc) + v[r0, c0 + 1] * tc) * (1 - tr) +
                (v[r0 + 1, c0] * (1 - tc) + v[r0 + 1, c0 + 1] * tc) * tr)


def rounded(depth, height, fall):
    """A top `height` high inside, rounded over `fall` at its edge (depth: how far inside)."""
    return height * np.sqrt(1.0 - (1.0 - np.clip(depth / fall, 0.0, 1.0)) ** 2)


def dome(X, Y, centre, radii, height, power=0.5, angle=0.0):
    (x0, y0), (a, b) = centre, radii
    ca, sa = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    u = (X - x0) * ca + (Y - y0) * sa
    v = -(X - x0) * sa + (Y - y0) * ca
    return height * np.clip(1.0 - (u / a) ** 2 - (v / b) ** 2, 0.0, None) ** power


def ridge(X, Y, points, power=0.6):
    """A ridge along a path of the plane: points (x, y, half-width, height), its section an ellipse to the power."""
    out = np.zeros_like(X)
    for (px_, py_, pw, ph), (qx, qy, qw, qh) in zip(points, points[1:]):
        dx, dy = qx - px_, qy - py_
        t = np.clip(((X - px_) * dx + (Y - py_) * dy) / max(1e-9, dx * dx + dy * dy), 0.0, 1.0)
        d = np.hypot(X - (px_ + t * dx), Y - (py_ + t * dy))
        w = pw + t * (qw - pw)
        h = ph + t * (qh - ph)
        out = np.maximum(out, h * np.clip(1.0 - (d / w) ** 2, 0.0, None) ** power)
    return out


def smax(a, b, kk):
    return gw.smax(a, b, kk)


def smoothstep(e0, e1, x):
    return gw.smoothstep(e0, e1, x)


# --- Painting (polish_green_shell's way) --------------------------------------------------------------------------------
# Each face of a heightfield the ink of the pixels under it (the ink with the most weight there), in the shade of that
# ink's pixels there (filled out from the ink's own pixels and blurred), LIFT lighter and lighter still where the game's
# sun lights the face less (COMP about LIT_MEAN: so that its light and the sprite's drawn light don't add up), the
# nearest of the ink's shades; where the sprite's darkest pixels lie, the dark key.

LIT_MEAN = 0.72


class Ink:
    def __init__(self, name, mask, shades, finish, lift, comp, contrast=1.0, glows=None, sigma=0.5):
        self.name, self.mask, self.shades, self.finish = name, mask, list(shades), finish
        self.lift, self.comp, self.contrast, self.glows, self.sigma = lift, comp, contrast, glows or {}, sigma


class Paint:
    def __init__(self, pic, inks, dark_mask, prefix, dark_index):
        self.pic, self.inks, self.prefix, self.dark_index = pic, inks, prefix, dark_index
        self.soft, self.weight = [], []
        for ink in inks:
            soft = gw.blur(gw.fill(pic.shade, ink.mask), ink.sigma)
            self.soft.append(pic.coarse(7.0 + ink.contrast * (soft - 7.0)))
            self.weight.append(pic.coarse(gw.blur(ink.mask.astype(float), 0.6)))
        self.dark = pic.coarse(gw.blur(dark_mask.astype(float), 0.55))

    def keys(self, Xa, Ya, normals, force=None, offset=None):
        """Each face's key: (ink name, palette index) or "dark". force: an ink's name per face (or None) to use that
        ink there; offset: shades added per face."""
        lit_by = gw.sun_on(normals)
        weights = np.stack([w(Xa, Ya) for w in self.weight], 0)
        which = weights.argmax(0)
        dark = self.dark(Xa, Ya)
        extra = np.zeros(len(Xa)) if offset is None else offset
        per = [gw.nearest(soft(Xa, Ya) + ink.lift + ink.comp * (LIT_MEAN - lit_by) + extra, ink.shades)
               for ink, soft in zip(self.inks, self.soft)]
        names = [ink.name for ink in self.inks]
        out = []
        for i in range(len(Xa)):
            w = which[i]
            if force is not None and force[i] is not None:
                w = names.index(force[i])
            elif dark[i] > 0.6 and weights[w, i] < 0.35:
                out.append("dark")
                continue
            out.append((self.inks[w].name, int(per[w][i])))
        return out

    def material(self, key):
        if key == "dark":
            return k.material("%s_dark_%x" % (self.prefix, self.dark_index), palette=self.dark_index, metallic=0.0,
                              roughness=0.6)
        ink = next(i for i in self.inks if i.name == key[0])
        glow = ink.glows.get(key[1], 0.0)
        extra = dict(emission=k.level_palette()[key[1]], emission_strength=glow) if glow > 0 else {}
        return k.material("%s_%s_%x" % (self.prefix, key[0], key[1]), palette=key[1], metallic=ink.finish[0],
                          roughness=ink.finish[1], **extra)

    def assign(self, obj, keys):
        keys = limit_materials(keys)
        order = sorted(set(keys), key=lambda key: str(key))
        slot = {key: i for i, key in enumerate(order)}
        mesh = obj.data
        mesh.materials.clear()
        for key in order:
            mesh.materials.append(self.material(key))
        mesh.polygons.foreach_set("material_index", [slot[key] for key in keys])
        mesh.update()


def coverage_check(label, pic, inside, layout, sheet_file):
    """The object's outline as the camera sees it (the sheared heightfield puts each point where the sprites draw it:
    its cells, inside(X, Y)) against the sprites' pixels, the whole and each piece (layout: name, sheet sprite, its
    column and row in the picture)."""
    covered = gw.own_coverage(inside, pic.w, pic.h, pic.left, pic.top)
    mask = [[False] * pic.w for _ in range(pic.h)]
    for _, sprite, c0, r0 in layout:
        for r, line in enumerate(k.sprite_mask(sheet_file, sprite)):
            for c, v in enumerate(line):
                if v:
                    mask[r0 + r][c0 + c] = True
    mk.compare(label, covered, mask)
    for name, sprite, c0, r0 in layout:
        sub_c = [row[c0:c0 + 24] for row in covered[r0:r0 + 28]]
        sub_m = [row[c0:c0 + 24] for row in mask[r0:r0 + 28]]
        both = sum(p and q for rp, rq in zip(sub_c, sub_m) for p, q in zip(rp, rq))
        either = sum(p or q for rp, rq in zip(sub_c, sub_m) for p, q in zip(rp, rq))
        print("silhouette overlap %s (%d): %.3f" % (name, sprite, both / max(1, either)))


def box_of(pic, c0, r0):
    return (pic.x(c0), pic.x(c0 + 24), pic.y(r0 + 28), pic.y(r0))


def export_pieces(pic, plate, layout, paint_faces, out, options, only, extra=None):
    """Each piece: the plate's cells in its sprite's box, painted (paint_faces(obj, kinds) -> keys), sheared to the
    camera, moved to its sprite's middle, exported (polish_gyges_wall.finish_piece). extra(name, box) -> more parts."""
    for name, sprite, c0, r0 in layout:
        if only is not None and name not in only:
            continue
        k.reset()
        box = box_of(pic, c0, r0)
        obj, kinds, wall_z = plate.mesh(name, gw.piece_owner(box))
        parts = []
        if obj is not None:
            paint_faces(obj, kinds, wall_z)
            parts.append(obj)
        if extra is not None:
            parts += extra(name, box)
        gw.finish_piece(name, parts, box, out, options)


# --- The nose (5 154 over 191 beside 193) ------------------------------------------------------------------------------
# Its parts in the picture's plane (points as (column, row) of the 48 x 56 picture's pixel edges): the bridge a ridge
# along the outline's middle (column AXIS_C) whose half-width follows the outline and whose height rises down it
# (BRIDGE: row, half-width, height; between the rows a smooth curve), the tip, the wings and the columella, all of it
# on a mound FLOOR high (the bridge's sides low, the nose's lower part, its wings and the sill under the nostrils,
# higher: BASE), joined by a smooth maximum (BLEND), the nostrils sunk to NOSTRIL_FLOOR, the sprite's fine shading as a
# little relief (DETAIL), the outline rounded over FALL.

NOSE_W, NOSE_H = 48, 56
NOSE_LAYOUT = [("nose_bridge", 154, 12, 0), ("nose_tip_left", 191, 0, 28), ("nose_tip_right", 193, 24, 28)]
AXIS_C = 24.5
BRIDGE = [(1.6, 2.7, 3.0), (3.0, 4.7, 3.6), (5.0, 5.9, 4.3), (8.0, 6.3, 5.2), (11.0, 7.1, 6.1), (14.0, 8.3, 6.9),
          (17.0, 9.4, 7.6), (20.0, 9.9, 8.2), (23.0, 10.2, 8.7), (26.0, 10.8, 9.2), (29.0, 11.2, 9.7), (33.0, 9.6, 9.9),
          (36.0, 7.8, 9.2), (39.0, 5.8, 7.6), (41.0, 4.5, 6.6)]
BRIDGE_END = (38.5, 41.5)                       # (rows: it runs on under the tip and fades into the columella)
TIP = ((24.4, 33.6), (7.4, 6.9), 11.4)          # middle (column, row), radii (pixels), height
WINGS = [((11.9, 38.4), (6.6, 8.4), 8.2), ((37.3, 38.2), (6.7, 8.6), 7.9)]
COLUMELLA = [(24.4, 39.0, 3.9, 7.8), (24.3, 44.0, 3.4, 6.8), (24.2, 48.0, 2.8, 6.0), (24.0, 50.8, 1.9, 5.0)]
FLOOR = 2.2                                      # the least height inside the outline
MOUND = ((24.5, 39.5), (20.0, 12.5), 6.0, 0.45)  # the nose's lower part (wings, sill, columella's foot) on a mound:
#                                                  middle, radii, height, how far in (of the radius squared) it is full
BLEND = 1.4
NOSTRILS = [(12, 21, 39, 46), (27, 37, 39, 48)]   # the boxes (columns, rows) where the dark pixels are nostrils
NOSTRIL_FLOOR = 4.3                              # (above the tongue's top, which the nose covers at rest)
DETAIL = (0.08, 0.3)                             # the fine shading as relief: per shade, its limit (pixels)
FALL = 2.0


def table(rows, x):
    """Values of a table of rows (x, value, ...) at x (arrays), smooth between its rows (polish_drip's monotone curve
    per column), held at its ends."""
    from polish_drip import Curve
    curve = Curve(rows)
    xs = np.asarray(x, float)
    flat = xs.ravel()
    lo, hi = rows[0][0], rows[-1][0]
    samples = np.linspace(lo, hi, 400)
    values = np.array([curve(v) for v in samples])
    if values.ndim == 1:
        values = values[:, None]
    out = [np.interp(np.clip(flat, lo, hi), samples, values[:, j]).reshape(xs.shape) for j in range(values.shape[1])]
    return out if len(out) > 1 else out[0]


class Nose:
    def __init__(self):
        pic = self.pic = Picture(NOSE, NOSE_W, NOSE_H, 2)
        a = pic.a
        body = a >= 0
        self.fine_inside = pic.soft_mask(body)
        self.inside = pic.fine(self.fine_inside.astype(float))
        self.depth = pic.fine(edt(self.fine_inside, 1.0 / S))
        dark = (a == 0x01) | (a == 0x10)
        nostril = np.zeros_like(body)
        for c0, c1, r0, r1 in NOSTRILS:
            nostril[r0:r1, c0:c1] = True
        self.nostril = pic.fine(gw.blur(pic.up((dark & nostril).astype(float)), 0.8 * S))
        known = body & ~dark
        soft = gw.blur(gw.fill(pic.shade, known), 0.6)
        broad = gw.blur(gw.fill(pic.shade, known), 2.2)
        self.fine_shade = pic.coarse(soft - broad)

    def P(self, c, r):
        return self.pic.x(c), self.pic.y(r)

    def shapes(self, X, Y):
        P = self.P
        rows = self.pic.top - Y
        w, h = table(BRIDGE, rows)
        u = (X - self.pic.x(AXIS_C)) / w
        fade = smoothstep(0.6, 1.8, rows) * (1.0 - smoothstep(BRIDGE_END[0], BRIDGE_END[1], rows))
        z = h * np.clip(1.0 - u * u, 0.0, None) ** 0.6 * fade
        (c, r), radii, ht = TIP
        z = smax(z, dome(X, Y, P(c, r), radii, ht), BLEND)
        for (c, r), radii, ht in WINGS:
            z = smax(z, dome(X, Y, P(c, r), radii, ht, power=0.6), BLEND)
        z = smax(z, ridge(X, Y, [(P(c, r)[0], P(c, r)[1], wd, ht) for c, r, wd, ht in COLUMELLA], power=0.55),
                 BLEND * 0.7)
        (c, r), (rx, ry), ht, full = MOUND
        (x0, y0) = P(c, r)
        q = ((X - x0) / rx) ** 2 + ((Y - y0) / ry) ** 2
        z = smax(z, ht * smoothstep(0.0, full, 1.0 - q), 0.8)
        return np.maximum(z, FLOOR)

    def heights(self, X, Y):
        X, Y = np.asarray(X, float), np.asarray(Y, float)
        z = self.shapes(X, Y)
        z = z + np.clip(DETAIL[0] * self.fine_shade(X, Y), -DETAIL[1], DETAIL[1])
        z = z - np.clip(z - NOSTRIL_FLOOR, 0.0, None) * self.pit(X, Y)
        z = np.minimum(z, rounded(self.depth(X, Y), 14.0, FALL))
        return np.where(self.inside(X, Y) > 0.5, z, 0.0)

    def pit(self, X, Y):
        return smoothstep(0.15, 0.55, self.nostril(X, Y))

    def cells(self, X, Y):
        return self.inside(X, Y) > 0.5


NOSE_INKS = lambda pic: [   # noqa: E731
    Ink("skin", (pic.ramp == 1) & (pic.a >= 0x12), [0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x1b, 0x1c,
                                                    0x1d], (0.12, 0.38), lift=1.6, comp=1.5),
]
NOSE_DARK = 0x10
NOSE_WALL = "dark"                               # (the walls round the outline: the sprite's dark rim)


def nose_models(out, options, only):
    nose = Nose()
    pic = nose.pic
    if "check" in options and only is None:
        sheets = options["check"]
        coverage_check("the nose (its 48 x 56 picture)", pic, nose.cells, NOSE_LAYOUT,
                       os.path.join(sheets, "enemy_5.png"))
    plate = gw.Plate((pic.left, -pic.left, -pic.top, pic.top), nose.heights, cells=nose.cells)
    dark = (pic.a == 0x01) | (pic.a == 0x10) | (pic.a == 0x11)
    paint = Paint(pic, NOSE_INKS(pic), dark, "nose", NOSE_DARK)

    def paint_faces(obj, kinds, wall_z):
        centres, normals = gw.face_data(obj)
        centres, normals = np.round(centres, 4), np.round(normals, 4)
        top = paint.keys(centres[:, 0], centres[:, 1], normals)
        pit = nose.pit(centres[:, 0], centres[:, 1]) > 0.4          # the nostrils dark all through
        paint.assign(obj, [NOSE_WALL if kinds[i] != 0 or pit[i] else top[i] for i in range(len(kinds))])
    export_pieces(pic, plate, NOSE_LAYOUT, paint_faces, out, options, only)


# --- The tongue (x5e 267 over 269) -------------------------------------------------------------------------------------
# A slab TONGUE_H high over the outline (rounded over TONGUE_FALL: a thick, fleshy edge), a little domed across, the
# median groove sunk along column GROOVE_C; at its root the three sores sunk SORE_DEPTH into lumps round them (LUMPS),
# their fire glowing. Its top stays under the nose's lowest parts over it at rest (NOSTRIL_FLOOR).

TONGUE_W, TONGUE_H_PX = 24, 56
TONGUE_LAYOUT = [("nosedrip_nostrils", 267, 0, 0), ("nosedrip_tongue", 269, 0, 28)]
TONGUE_H = 3.0
TONGUE_FALL = 2.6
GROOVE_C, GROOVE_ROWS, GROOVE = 12.0, (11.0, 47.0), (0.45, 1.8)   # column, rows, (depth, half-width)
GROOVE_SHADE = 2.5                # the groove painted this many shades darker at its floor
LUMPS = [((5.0, 9.0), (3.6, 3.2), 0.5), ((10.5, 8.0), (3.4, 3.6), 0.6), ((15.5, 6.6), (3.0, 2.8), 0.5)]
SORE_DEPTH = 0.7


class Tongue:
    def __init__(self):
        pic = self.pic = Picture(TONGUE, TONGUE_W, TONGUE_H_PX, 2)
        a = pic.a
        body = a >= 0
        self.fine_inside = pic.soft_mask(body)
        self.inside = pic.fine(self.fine_inside.astype(float))
        self.depth = pic.fine(edt(self.fine_inside, 1.0 / S))
        self.sore_mask = pic.ramp == 7
        self.sore = pic.fine(gw.blur(pic.up(self.sore_mask.astype(float)), 0.6 * S))
        known = body & (pic.ramp == 4) & (a != 0x40)
        soft = gw.blur(gw.fill(pic.shade, known), 0.6)
        broad = gw.blur(gw.fill(pic.shade, known), 2.2)
        self.fine_shade = pic.coarse(soft - broad)

    def heights(self, X, Y):
        pic = self.pic
        X, Y = np.asarray(X, float), np.asarray(Y, float)
        rows = pic.top - Y
        d = self.depth(X, Y)
        z = rounded(d, TONGUE_H, TONGUE_FALL)
        for (c, r), radii, h in LUMPS:
            z = z + dome(X, Y, (pic.x(c), pic.y(r)), radii, h, power=1.0)
        z = z - GROOVE[0] * self.groove(X, Y) * np.clip(d / 2.0, 0.0, 1.0)
        z = z + np.clip(0.06 * self.fine_shade(X, Y), -0.15, 0.15)
        z = z - SORE_DEPTH * smoothstep(0.3, 0.8, self.sore(X, Y)) * np.clip(d / 1.5, 0.0, 1.0)
        z = np.minimum(z, TONGUE_H)
        return np.where(self.inside(X, Y) > 0.5, np.maximum(z, 0.05), 0.0)

    def groove(self, X, Y):
        pic = self.pic
        rows = pic.top - np.asarray(Y, float)
        across = np.exp(-((np.asarray(X, float) - pic.x(GROOVE_C)) / GROOVE[1]) ** 2)
        return across * smoothstep(GROOVE_ROWS[0], GROOVE_ROWS[0] + 3.0, rows) * \
            (1.0 - smoothstep(GROOVE_ROWS[1] - 4.0, GROOVE_ROWS[1], rows))

    def cells(self, X, Y):
        return self.inside(X, Y) > 0.5


# The sores glow in the fire's reds (polish_drip.py's strengths for these shades).
SORE_GLOWS = {0x72: 0.12, 0x73: 0.15, 0x74: 0.18, 0x75: 0.22, 0x76: 0.25, 0x77: 0.3, 0x78: 0.33}
TONGUE_INKS = lambda pic: [   # noqa: E731
    Ink("flesh", (pic.ramp == 4) & (pic.a >= 0x42), [0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0x49, 0x4a, 0x4b, 0x4c],
        (0.05, 0.4), lift=0.6, comp=1.4),
    Ink("sore", pic.ramp == 7, [0x72, 0x73, 0x74, 0x75, 0x76, 0x77, 0x78], (0.0, 0.3), lift=0.6, comp=0.0,
        glows=SORE_GLOWS, sigma=0.4),
    # the groove's floor and walls (only where forced; on a tie of weights the flesh, listed first, wins): the flesh,
    # duller (a long wall in the sun's glint would draw a white line down the tongue)
    Ink("groove", (pic.ramp == 4) & (pic.a >= 0x42), [0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48], (0.0, 0.8), lift=0.6,
        comp=1.4),
]
TONGUE_DARK = 0x40


def tongue_models(out, options, only):
    tongue = Tongue()
    pic = tongue.pic
    if "check" in options and only is None:
        sheets = options["check"]
        coverage_check("the tongue (its 24 x 56 picture)", pic, tongue.cells, TONGUE_LAYOUT,
                       os.path.join(sheets, "enemy_x5e.png"))
    plate = gw.Plate((pic.left, -pic.left, -pic.top, pic.top), tongue.heights, cells=tongue.cells)
    dark = (pic.a == 0x40) | (pic.a == 0x01) | (pic.a == 0x41)
    paint = Paint(pic, TONGUE_INKS(pic), dark, "tongue", TONGUE_DARK)

    def paint_faces(obj, kinds, wall_z):
        centres, normals = gw.face_data(obj)
        centres, normals = np.round(centres, 4), np.round(normals, 4)
        g = tongue.groove(centres[:, 0], centres[:, 1])
        force = ["groove" if v > 0.3 else None for v in g]
        top = paint.keys(centres[:, 0], centres[:, 1], normals, force=force, offset=-GROOVE_SHADE * g)
        paint.assign(obj, [top[i] if kinds[i] == 0 else "dark" for i in range(len(kinds))])
    export_pieces(pic, plate, TONGUE_LAYOUT, paint_faces, out, options, only)


# --- The bowl of flames (5 156 beside 158) ------------------------------------------------------------------------------
# A heightfield of the fire: over the outline (rounded over BOWL_FALL) its height follows the fire's heat (the sprites'
# shades smoothed: polish_drip.Heat's way), BOWL_LOW where it is coolest to BOWL_HIGH where it is white-hot, so the
# hottest parts swell; the tongues of flame along the rim stand as thin ridges falling to their tips. Painted in
# polish_drip.py's bands of the fire's ramp by the heat (and cooler where the surface turns away from the camera),
# each band glowing in its own colour (its strengths).

BOWL_W, BOWL_H_PX = 48, 28
BOWL_LAYOUT = [("fire_bowl_left", 156, 0, 0), ("fire_bowl_right", 158, 24, 0)]
BOWL_FALL = 1.2
BOWL_LOW, BOWL_HIGH = 2.4, 7.4
BOWL_FACING = 0.9                 # (a heightfield's faces mostly face up: the drip's FACING about this normal's z)
BOWL_COOL = 0.5                   # and the whole a little cooler than the drip's tubes (their sides turn away)


class Bowl:
    def __init__(self):
        pic = self.pic = Picture(BOWL, BOWL_W, BOWL_H_PX, 0)
        a = pic.a
        body = a >= 0
        self.fine_inside = pic.soft_mask(body, 0.6)
        self.inside = pic.fine(self.fine_inside.astype(float))
        self.depth = pic.fine(edt(self.fine_inside, 1.0 / S))
        heat = gw.blur(gw.fill(pic.shade, body), 0.9)
        self.heat = pic.coarse(heat)
        self.raw = pic.coarse(gw.blur(gw.fill(pic.shade, body), 0.7))

    def heights(self, X, Y):
        X, Y = np.asarray(X, float), np.asarray(Y, float)
        h = self.heat(X, Y)
        z = BOWL_LOW + (BOWL_HIGH - BOWL_LOW) * smoothstep(1.0, 13.0, h)
        z = np.minimum(z, rounded(self.depth(X, Y), 12.0, BOWL_FALL) * (0.35 + 0.65 * smoothstep(0.0, 3.0,
                                                                                               self.depth(X, Y))))
        return np.where(self.inside(X, Y) > 0.5, np.maximum(z, 0.05), 0.0)

    def cells(self, X, Y):
        return self.inside(X, Y) > 0.5


def bowl_keys(bowl, Xa, Ya, normals):
    """polish_drip's bands of the heat: the sprites' shades (scaled and raised as the drip's), cooler where the surface
    (sheared to the camera) turns away from it."""
    from polish_drip import BANDS, HEAT, FACING  # noqa: F401
    world = normals.copy()
    world[:, 2] += gw.TAN_T * world[:, 1]
    world /= np.maximum(1e-9, np.linalg.norm(world, axis=1))[:, None]
    value = HEAT[0] * bowl.raw(Xa, Ya) + HEAT[1] - BOWL_COOL + FACING[0] * (world[:, 2] - BOWL_FACING)
    borders = [lowest for lowest, _, _ in BANDS[1:]]
    return [BANDS[int(sum(v > t for t in borders))][1] for v in value]


def bowl_material(index):
    from polish_drip import BANDS
    glow = {i: g for _, i, g in BANDS}[index]
    return k.material("drip_%02x" % index, palette=index, metallic=0.0,
                      roughness=0.4 if index < 0x74 else 0.3 if index < 0x78 else 0.24,
                      emission=k.level_palette()[index], emission_strength=glow)


def bowl_models(out, options, only):
    bowl = Bowl()
    pic = bowl.pic
    if "check" in options and only is None:
        sheets = options["check"]
        coverage_check("the bowl of flames (its 48 x 28 picture)", pic, bowl.cells, BOWL_LAYOUT,
                       os.path.join(sheets, "enemy_5.png"))
    plate = gw.Plate((pic.left, -pic.left, -pic.top, pic.top), bowl.heights, cells=bowl.cells)

    def paint_faces(obj, kinds, wall_z):
        centres, normals = gw.face_data(obj)
        centres, normals = np.round(centres, 4), np.round(normals, 4)
        keys = bowl_keys(bowl, centres[:, 0], centres[:, 1], normals)
        keys = [keys[i] if kinds[i] == 0 else 0x70 for i in range(len(kinds))]
        order = sorted(set(keys))
        mesh = obj.data
        mesh.materials.clear()
        for key in order:
            mesh.materials.append(bowl_material(key))
        mesh.polygons.foreach_set("material_index", [order.index(key) for key in keys])
        mesh.update()
    export_pieces(pic, plate, BOWL_LAYOUT, paint_faces, out, options, only)


# --- Main ---------------------------------------------------------------------------------------------------------------

def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    if only is None or "face_eye" in only:
        eye_model(out, options)
    if only is None or any(name in only for name, _, _, _ in NOSE_LAYOUT):
        nose_models(out, options, only)
    if only is None or any(name in only for name, _, _, _ in TONGUE_LAYOUT):
        tongue_models(out, options, only)
    if only is None or any(name in only for name, _, _, _ in BOWL_LAYOUT):
        bowl_models(out, options, only)


# --- The sprites' pixels ------------------------------------------------------------------------------------------------
# Each pixel its palette index as two hex digits ('..' none), rows top to bottom (the pictures' empty rows left out).

NOSE = """
............................................1112121010..........................................
........................................121214141412121110......................................
......................................1111141515151312121110....................................
......................................1112151515151313121210....................................
......................................1215151516161413121210....................................
......................................1315161718161514121210....................................
......................................1315181a19171615131210....................................
......................................13161b1d1a171615131210....................................
....................................1313171c1c1917161513131101..................................
....................................13141b1e1a1817161514121110..................................
..................................1314151b1a19181716151513111001................................
..................................1315161a1918181716151513111101................................
..................................131516191918171715151414111101................................
................................1314161619181817171514141411111001..............................
..............................13131416161a18171717151414141111111110............................
..............................13141516161c18171716151414151111111211............................
..............................13131515161d18171716141414151111121311............................
..............................13141515161d19171716141415151111121311............................
..............................13141415151c19171716141415141111121311............................
..............................1213141415191d171616141516141111121311............................
..............................121314141517181c1716151615131111121311............................
..............................12121314141617181918171413121111131312............................
..............................12121314141516161717151312111112131312............................
..............................12121314141516161616141312111113131312............................
..............................12121314141515161818141312111212111312............................
............................1212121314141516181a1a16141311111112131310..........................
..........................1312131314141416181c1a1b1617151311111111121011........................
......................131313141414141415171d1d1a1b16161615131111111111111111....................
..................13131414151515141415161d1f1a1a1b161515161513111112121212121111................
................1313161717171517141315181f1d1b1b1c16161515161311111113131313121111..............
..............13131518191a1a1917151417181f1c1b1b1c1716151516151311101314141413121111............
..............1315171a1b1e1e1d18151518191d1c1c1b1c1716161516151311101219171514131211............
............131316181a1c1d1c1a17161619191c1d1c1c1c161616161714141111121516161313121111..........
............13141718191a1a191916151618181a1d1d1c1c161616171614141111121314151313121311..........
............1214171718191918161413161717181a1c1d1c161517161515141112111213131313121410..........
............12141617171818171513131517161718191a1a171717151414121212111213131312131511..........
............13141517171717151413131515151616171616151414141313121211111113131212131511..........
............12141516161616151413131415151515161615131313121212121111111112121212141612..........
............12141516161515141010101315151515151514121111111313110101010111111112151711..........
............12131415151512010101011113151515151514111111131511010101010101111214161811..........
..............1114141514100110101001011215151515141112141612010101010101011113161913............
..............1113151614110101010101011011141515151314151001010101010101011314181511............
................121214161110101011111110101213151411121001010101011001011111171611..............
..................12121517161413121111111011131514121210010101011010111012151611................
....................1212141514141415141312111315141211010101101111111111121111..................
........................10111011111112121414141514121111101010010101010110......................
......................................1013141314141111100110....................................
........................................111213131310010110......................................
..........................................01011010010101........................................
..............................................111001............................................
"""

TONGUE = """
........................4040404040..............
....................4041434545424040............
..........40404040404041454744414040............
........414443424143444342444372014040..........
......40434a4741447273014143747372404040........
......4143444001467273014345777472014040........
....4040737240014773737243474e477343404040......
..404072747442464774737373454643404446404040....
404072737472444947487575734341414343444444010140
4343737372464948464b4a46724101434644014441414340
414242434449474646474b49434246484646424041424444
43454849494746474746484b4a4846464646440101424444
444546474747464748464546484747464645434242444444
4445464745454a4b4a474644454647464645454443444444
43454645444c4c4949474645444647464645454545444440
414442434b4a494949474444444647474646464545444440
4041414849494a4949484644444646474646464545444440
404446494a4a494848484644444648474746464545444440
40454648484847494847464444474a464746464545444440
434546484948474947474644444749474747464545444440
44454748474846484747454444474b474747464545444440
444547474747474747474544444749474846464545444440
434547464847464847474543444749474746464544444340
434547464848464847474643454849484746464544444340
43454747474848474747464345484b494746454544444340
43454647474748474847464345484b474746454544444240
43444648474646474747464345484b474846454544444140
01444647474747474846464345484b4948464544444440..
0144464647474847484646434547484846464544444301..
0144454747474648474746434547474746454544444301..
0144454647474648474746434547484746454544444201..
0143454647474747464745434447484646454444464101..
..404546474647474747454444464646464544444501....
..404546474647464747454444464645454544454640....
..404446474647464747454344464646454444464540....
..404346464646474646454244464645454445464440....
..404245464646474746454244464645444445474240....
....01454647464747464542444645454444464701......
....01444646464646454542444545454445484640......
....40444646464645454542444545444445474440......
......0145464646454544434445454444464640........
......0142444544454544444445444344484540........
........014344454545444444444344454740..........
........014343444545444444444445484540..........
..........01424243444444444446484640............
............0142414343434446474440..............
..............400142434344444040................
..................0140404040....................
"""

BOWL = """
......70..................................................................................70....
......7070......70..............................................................70......7171....
....707170......7071..........................................................0170......727370..
....70737301....717471......................................................017170....72737570..
....71747571....72777670........71..............................70........71727271....72757572..
....0176787471..737a787471....7172..........70......70..........7170....7074737372..7073757772..
....017779767170737a7875747170727471......7070......7172......70737070727375747573717175787772..
....707679757270737a7677777271737772....727170......717471....717572707376777677757172787a7671..
....717678767371747876777a74707478737071737170......72757270727376737274767a78787571747a7b7571..
....727577797572747874787a76717579757172747170......74767471737377757374767977767472747a797370..
....7073797a797275797678797672777978777676727070..72767b79747375787672757577757575737579787270..
....0173797e7973777a78777675737779787878787371707073797d7e787575787773767773757878757677797270..
....0171797c7872787c79767575737879797777787573737174777a7a757677797874787a75797c7b787576777370..
....707176797777797e7a76747774777a7a787778777575747476787a7476787a7974797b76777978777473777270..
....707174787a797d7e7c76767875777a7a797779797776757477797b77767a7b7a797a7c75767675747475767270..
....707176797b797b7d7b75777b77787a7b7a76797a787777787b7c7b77797c7f7c7a7c7c75777774757677767270..
......72767a7c79797a79747a7e7a787b7d7d78777b7a78767b7e7d7b77797b7c7b7b7d7b757877747677767470....
......7074787a7878797a737c7f7c787c7f7d7b777a7c79767e7f7d7b78797776797b7b7b73797a777676747170....
........71757876777a7c767a7e7b797a7c7d7b767a7e7c797e7e7d7a7676787b79787a76747a7b7776727270......
..........717677787a7c7a797a797878787b7c79797c7d77797b7a7676767b7d7b75747677797a77727270........
............727476797a79797a787777787a7e7b777b7c7c7a77767876747b7d79747576757775737270..........
..............71727376787a7b7b7977797c7f7d7a7d7f7f7b77797a78767a7a797474757672737270............
................70707275777c7d7c7a7b7d7f7f7a7d7f7d7a777b7b787477777674767474727170..............
....................707173767a7c7c7c7c7b7875787a7a7676797975727274747677757370..................
......................707071727375757474747070727575767775727173747474747101....................
............................707070717071707070707070717171717171717072..........................
"""


if __name__ == "__main__":
    build()
