"""The station of STATION and TIME WAR (sheet L: its two halves, each an axle end and four 2x2 sprites, and their damaged
looks) and TIME WAR's grey capsule (sheet L 1 3 above 39 41 above 77 79), polished (2026-10-22, round 36; they replace
wave3_z_station.py (the halves: a lathed axle, rounded-box docks, tube struts and slab panels painted by the sprite; the
capsule: a lofted hull with boxes and tubes), wave3_ap_station.py (their damaged looks: the same with parts removed,
repainted and dented with random numbers, so that its output changed from run to run) and wave2_e.py's station_end (the
axle ends, lathed)).

Where they appear: TIME WAR (episode 4) t120, event 7 (the top layer): half A, 659 (L 11) and 660 (13) at x 10 and 34, y
-28, 661 (49) and 662 (51) at x 10 and 34, y 0, 663 (its axle end, 34) at x 58, y -14 (link 26); half B, 664 (its axle
end, 24) at x 236, y -14, 665 (7) and 666 (9) at x 260 and 284, y -28, 667 (45) and 668 (47) at y 0 (link 25): each half
72 x 56, its end beside the middle of its side, the ends facing each other across the screen; t6950 event 25 makes them
mortal (armour 254); the ends fire (guns 151, 152). STATION (episode 5) t3420 the same at x 20 ... 68 and 266 ... 314,
swaying up and down the screen (events 19). Every piece switches to its damaged sprite and stays so when the station is
killed (dlevel -1): 11 13 49 51 34 -> 87 89 125 127 110, 24 7 9 45 47 -> 100 83 85 121 123. The capsule: TIME WAR t110,
event 15 (the sky), 653-658 at x 64 and 88 (y -56, -28, 0), and again at x 136 and 160: two capsules side by side. Half
A is half B's pixels mirrored (L 11 = 9, 13 = 7, 49 = 47, 51 = 45, 34 = 24 mirrored, and so are their damaged sprites:
polish tools' twins check, pixel for pixel); no other enemy shows these sprites (launched ones included); the capsule's
sprites are no others' twins.

As the sprites and their 4x upscales draw half B (its picture's columns and rows; the upper side lit, the lower one in
shadow): a steel axle along its middle (row 27) from its end (24) at the left: a rounded knob (columns 4-6), a tube
(7-11), two flanges (12-13 and 17-18, 21 pixels tall) with a ring of red lamps between them (column 15), a collar with
red clamps (20-28); then a hub (29-32), a blue band in a neck (33-36), the housing (37-49) with a saddle over it
(columns 42-54 of rows 18-21), a red clamp (51-55) and rod (to 58) and the docking block (59-70, rows 22-32) with a
panel in its face; struts above and below from the hub and the saddle to four solar panels (frames round four cells):
one straight up (columns 35-45 of rows 0-11) and down, one at 45 degrees at each outer corner (columns 52-67 of rows
3-17 and their mirror). The damaged sprites shoot the panels away to shards, tear the dock off to a stub and burn the
axle black in patches. The capsule (its 48 x 84 picture): a grey body lying along the screen, nose up, turned about
column 24.5: a mushroom head (rows 5-17), a long body (rows 18-56) with a red glowing slot down each side (columns 17-19
and 31-33), a spine with a panel box, side rails, a flange with red lights (row 61), a ring, a broad tail disc (rows
72-75) and a red exhaust glow under it (rows 77-78).

Built for the game's camera as polish_green_shell.py is: each half and the capsule one heightfield in the picture's
plane, sheared along the camera's line of sight (y - z tan 20), on polish_gyges_wall.Plate's grid (0.5 pixel; its lines
on the sprites' edges, so each piece is the cells of its sprite's box, the axle end's box 24 x 28 at the middle of the
half's side), with tops and bases over the middle plane (z 0, where the axle's axis is: the object floats, its parts
reach under it) and walls between them round its cells (no bottom: never seen): the axle turned (its half-width row by
row PROFILE, its sections SQUASH flat), the dock a box with rounded edges and a sunken panel, the flat parts from the
sprite's own pixels (the panels thin plates, their dark cells sunk in their frames; the saddle over the housing; the
struts the rest, rounded bars); the capsule turned about its axis by the sprite's half-width row by row, its red slots
and lights sunk into it, its dark lines creased, its holes left open. Half A is half B mirrored. The damaged look is the
same heightfield on the damaged sprites' pixels (their cells), sunk DENT deep where they are burnt (darker than intact).
Painted by the sprites' shades (polish_green_shell's Paint: each face the ink of the pixels under it, steel, red, blue
or soot, in that ink's shade there, blurred, lifted and lighter where the game's sun lights it less), the reds glowing a
little (0.3-0.58), the damaged look's burns soot (0x01-0x03). Heights: the halves z -4.7 to 6.5 (the flanges; the axle
4.7, the saddle 4.4, the panels 1.2), the capsule -8.6 to 8.6 (as the old ones: -4.6 to 4.6 and -8.4 to 8.4).
Deterministic (no random numbers; the faces' centres and normals rounded before they pick their shades).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera. A half's origin is
its picture's middle (its pixel edge 36, 28): column c's left edge is x = c - 36, row r's top edge y = 28 - r; its
pieces' origins are their sprites' middles: half B's end (-24, 0), 7 (0, 14), 9 (24, 14), 45 (0, -14), 47 (24, -14);
half A's end (24, 0), 13 (0, 14), 11 (-24, 14), 51 (0, -14), 49 (-24, -14). The capsule's origin is its picture's middle
(24, 42): its pieces' at (-12, 28), (12, 28), (-12, 0), (12, 0), (-12, -28), (12, -28).

models.cfg: the model and sprite lines stay (yaw=0; the station's and the capsule's pieces origin); the axle ends' model
lines (station_end_left, _right and their damaged ones) get origin, as pieces of their halves now are (they were centred
in height, their old models symmetric about the axle).

Replaces wave3_z_station.py and wave3_ap_station.py (all of both: the station, its ends' damaged looks and the capsule
are all they build; nothing imports either but wave3_ap_station, which loads wave3_z_station and wave2_e),
wave3_z_art.py's STATION and POD and wave3_ap_art.py's STATION_DMG (read only by them), and wave2_e.py's station_end()
with its two model() lines (wave3_ap_station loads it; its other models stay).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the outlines as the camera
sees them against the sprites' pixels, each half intact and damaged, the capsule, each piece), --preview <prefix> (each
piece's top and 3/4 views), --only <name,...> (pieces to export).
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_gyges_wall as gw  # noqa: E402  (Plate, the shear to the camera, the faces' light)
from polish_green_shell import edt, limit_materials  # noqa: E402

W, H = 72, 56                     # a half's picture (L 24 beside 7 9 above 45 47); its origin its middle, pixel edge (36, 28)
LEFT, TOP = -36.0, 28.0
S = 4                             # the fine grid of the fields: S cells a pixel
AXIS = 27.5                       # the axle's middle (a pixel-edge row: y 0.5)


def px(c):
    return c - 36.0


def py(r):
    return 28.0 - r


def parse_picture(text):
    a = -np.ones((H, W), int)
    for i, line in enumerate(text.split()):
        for c in range(W):
            t = line[2 * c:2 * c + 2]
            if t != "..":
                a[i, c] = int(t, 16)
    return a


def patched(base, text):
    a = base.copy()
    for item in text.split():
        r, c, hexes = item.split(":")
        r, c = int(r), int(c)
        for i in range(len(hexes) // 2):
            t = hexes[2 * i:2 * i + 2]
            a[r, c + i] = -1 if t == ".." else int(t, 16)
    return a


def up(m):
    return np.repeat(np.repeat(m, S, 0), S, 1)


def fine_xy():
    xs = LEFT + (np.arange(W * S) + 0.5) / S
    ys = TOP - (np.arange(H * S) + 0.5) / S
    return np.meshgrid(xs, ys)


class Field:
    """Values on the fine grid, sampled bilinearly between its cells' middles."""

    def __init__(self, values):
        self.v = values

    def __call__(self, Xa, Ya):
        h, w = self.v.shape
        fc = np.clip((np.asarray(Xa, float) - LEFT) * S - 0.5, 0.0, w - 1.0)
        fr = np.clip((TOP - np.asarray(Ya, float)) * S - 0.5, 0.0, h - 1.0)
        c0 = np.minimum(np.floor(fc).astype(int), w - 2)
        r0 = np.minimum(np.floor(fr).astype(int), h - 2)
        tc, tr = fc - c0, fr - r0
        v = self.v
        return ((v[r0, c0] * (1 - tc) + v[r0, c0 + 1] * tc) * (1 - tr) +
                (v[r0 + 1, c0] * (1 - tc) + v[r0 + 1, c0 + 1] * tc) * tr)


def in_polygon(X, Y, poly):
    inside = np.zeros(np.shape(X), bool)
    n = len(poly)
    for i in range(n):
        (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % n]
        crosses = (y0 > Y) != (y1 > Y)
        xc = x0 + (Y - y0) * (x1 - x0) / ((y1 - y0) if y1 != y0 else 1e-9)
        inside ^= crosses & (X < xc)
    return inside


# --- The half's shapes (in pixel-edge columns and rows; the lower side is the upper one mirrored about the axle) ------

SQUASH = 0.62                     # the turned parts' sections: this flat (as station_end's always were)
# The axle's half-width in the picture along it (column: half-width; steps where two follow at one column).
PROFILE = [(4.0, 0.6), (4.4, 2.4), (5.2, 3.3), (6.0, 3.5), (7.0, 3.5), (7.0, 5.5), (12.0, 5.5), (12.0, 10.5),
           (14.0, 10.5), (14.0, 6.2), (15.0, 6.2), (15.0, 9.6), (16.0, 9.6), (16.0, 6.2), (17.0, 6.2), (17.0, 10.5),
           (19.0, 10.5), (19.0, 7.5), (29.0, 7.5), (29.0, 6.5), (33.0, 6.5), (33.0, 4.2), (37.0, 4.2), (37.0, 5.5),
           (50.0, 5.5), (50.0, 3.0), (55.5, 3.0), (55.5, 0.9), (59.2, 0.9)]
DOCK = (59.0, 71.0, 21.0, 34.0, 3.6, 0.8)    # the docking block: columns, rows, its half-height, its edges' rounding
DOCK_PANEL = (62.0, 69.0, 24.0, 31.0, 0.5)   # the panel sunk in its face
# The upper side's flat parts: (kind, its region (a polygon of pixel edges), top, base): what of the sprite's pixels
# lies in it is raised from base to top, its edges rounded over ROUND. The struts are drawn the rest.
PANELS = [("panel", [(35.0, -0.1), (46.0, -0.1), (46.0, 11.0), (35.0, 11.0)], 1.2, 0.3),
          ("panel", [(61.5, 2.0), (68.5, 9.2), (60.6, 17.0), (52.6, 10.2)], 1.2, 0.3),
          ("saddle", [(41.5, 18.0), (55.0, 18.0), (55.0, 21.6), (41.5, 21.6)], 4.4, 0.0)]
STRUT = (1.5, 1.1, 0.9)           # the struts: their middle's height, how far they rise round it, their rounding
ROUND = 0.5                       # the panels' edges
CELL_SINK = 0.25                  # the panels' cells (their darker pixels) sunk this much in their frames
DENT = 0.9                        # the damaged look: sunk this deep where it is burnt (its pixels darker than intact)


def profile_r(xc):
    """The axle's half-width at picture column xc (pixel edges); 0 off it."""
    cols = [c for c, _ in PROFILE]
    out = np.zeros(np.shape(xc))
    for (c0, r0), (c1, r1) in zip(PROFILE, PROFILE[1:]):
        if c1 <= c0:
            continue
        sel = (xc >= c0) & (xc < c1)
        out = np.where(sel, r0 + (r1 - r0) * (xc - c0) / (c1 - c0), out)
    del cols
    return out


class Half:
    """Half B of the station (its axle end, L 24, on its left) as a heightfield in the picture's plane: tops and bases
    over z 0 (the axle's middle plane), from the analytic axle and dock and the picture's flat parts; `mirror`: half A
    (L 11 13 above 49 51 beside 34), the same mirrored across its middle. a: the look's picture (as half B draws it),
    intact: the intact one (the dents are where the look is darker)."""

    def __init__(self, a, intact, mirror=False):
        self.a, self.mirror = a, mirror
        Xf, Yf = fine_xy()
        cf = Xf - LEFT                     # the fine cells' middles as picture columns and rows (pixel edges)
        rf = TOP - Yf
        rm = np.minimum(rf, 2 * AXIS - rf)   # the upper side's row of each (the lower mirrored onto it)
        opaque = up(a >= 0)
        soft = gw.blur(opaque.astype(float), 0.45 * S) > 0.5
        # The axle: turned; its top over the middle plane.
        R = profile_r(cf)
        dy = np.abs(rf - AXIS)
        axle = np.where(dy < R, SQUASH * np.sqrt(np.clip(R * R - dy * dy, 0.0, None)), -1.0)
        # The dock: a box with rounded edges, a panel sunk in its face.
        c0, c1, r0, r1, hh, rr = DOCK
        e = np.minimum(np.minimum(cf - c0, c1 - cf), np.minimum(rf - r0, r1 - rf))
        dock = np.where(e > 0, hh * np.sqrt(1.0 - (1.0 - np.clip(e / rr, 0.0, 1.0)) ** 2), -1.0)
        q0, q1, s0, s1, sink = DOCK_PANEL
        ep = np.minimum(np.minimum(cf - q0, q1 - cf), np.minimum(rf - s0, s1 - rf))
        dock = np.where(e > 0, dock - sink * np.clip(ep / 0.4, 0.0, 1.0), dock)
        top = np.maximum(axle, dock)
        base = np.where(axle >= 0, -axle, np.where(dock >= 0, -hh, 0.0))
        # Round the axle and the dock their outlines (the sprite's dark pixels there) lie flat at the middle plane.
        zone = (dy < R + 1.0) | (e > -1.0)
        top = np.where(zone & (top < 0), 0.0, top)
        # The flat parts: panels and saddles where their regions say, struts the rest of the picture's pixels.
        flat = soft & ~zone
        depth = edt(flat, 1.0 / S)
        kind_top = np.full(np.shape(Xf), -1.0)
        kind_base = np.zeros(np.shape(Xf))
        claimed = np.zeros(np.shape(Xf), bool)
        shade = np.where(a >= 0, a & 15, 0).astype(float)
        dark_cells = up(gw.blur(np.where(a >= 0, shade <= 4, False).astype(float), 0.4))
        for kind, poly, ztop, zbase in PANELS:
            region = in_polygon(cf, rm, poly) & flat & ~claimed
            prof = np.sqrt(1.0 - (1.0 - np.clip(depth / ROUND, 0.0, 1.0)) ** 2)
            z = zbase + (ztop - zbase) * prof
            if kind == "panel":
                z = z - CELL_SINK * np.clip(dark_cells, 0.0, 1.0) * np.clip(depth / 1.2, 0.0, 1.0)
            kind_top = np.where(region, z, kind_top)
            kind_base = np.where(region, zbase - 0.4 if kind == "panel" else zbase, kind_base)
            claimed |= region
        mid, rise, rnd = STRUT
        strut = flat & ~claimed
        z = mid + rise * np.sqrt(1.0 - (1.0 - np.clip(depth / rnd, 0.0, 1.0)) ** 2)
        kind_top = np.where(strut, z, kind_top)
        kind_base = np.where(strut, mid - 0.5, kind_base)
        top = np.where(flat, kind_top, top)
        base = np.where(flat, kind_base, base)
        # The damaged look: sunk where it is burnt (darker than intact), its gone parts gone (the cells: its pixels).
        if intact is not None and not np.array_equal(a, intact):
            si = np.where(intact >= 0, intact & 15, 0).astype(float)
            burnt = gw.blur(np.where((a >= 0) & (intact >= 0), np.clip((si - shade) / 6.0, 0.0, 1.0), 0.0), 0.8)
            top = top - DENT * up(burnt)
        self.cells_f = Field(soft.astype(float))
        top = np.where(soft, top, 0.0)
        base = np.where(soft, np.minimum(base, top - 0.05), 0.0)
        self.top_f, self.base_f = Field(top), Field(base)

    def _xy(self, Xa, Ya):
        Xa = np.asarray(Xa, float)
        return (-Xa if self.mirror else Xa), np.asarray(Ya, float)

    def cells(self, cx, cy):
        x, y = self._xy(cx, cy)
        return self.cells_f(x, y) > 0.5

    def heights(self, Xa, Ya):
        x, y = self._xy(Xa, Ya)
        return self.top_f(x, y)

    def bases(self, Xa, Ya):
        x, y = self._xy(Xa, Ya)
        return self.base_f(x, y)


# --- Painting (polish_green_shell's way) --------------------------------------------------------------------------------

INKS = {   # shades, (metallic, roughness), glow strengths by shade, lift, contrast (about shade 7), comp
    "metal": ([0x03, 0x05, 0x07, 0x09, 0x0b, 0x0d, 0x0f], (0.3, 0.32), {}, 1.6, 1.1, 2.0),
    "red": ([0x72, 0x74, 0x76, 0x78], (0.1, 0.3), {0x72: 0.3, 0x74: 0.4, 0x76: 0.5, 0x78: 0.58}, 1.5, 1.0, 0.8),
    "blue": ([0x33, 0x36, 0x39, 0x3c], (0.4, 0.28), {}, 1.5, 1.0, 1.5),
    "soot": ([0x01, 0x02, 0x03], (0.0, 0.8), {}, 0.6, 1.0, 0.6),   # the damaged look's burns (black over intact steel)
}
RAMPS = {"metal": 0, "red": 7, "blue": 3}
WALL = ("metal", 0x05)            # the sides (seen off the screen's middle)
LIT_MEAN = 0.72


def pal(prefix, index, metallic, roughness, glow=0.0):
    extra = dict(emission=k.level_palette()[index], emission_strength=glow) if glow > 0 else {}
    return k.material("%s_%x" % (prefix, index), palette=index, metallic=metallic, roughness=roughness, **extra)


def mat_of(key):
    shades, (met, rough), glows, _, _, _ = INKS[key[0]]
    return pal("station_" + key[0], key[1], met, rough, glows.get(key[1], 0.0))


class Paint:
    def __init__(self, a, intact, mirror=False):
        self.mirror = mirror
        shade = np.where(a >= 0, a & 15, 0).astype(float)
        ramp = np.where(a >= 0, a >> 4, -1)
        burnt = (a == 1) & (intact > 1)
        self.inks = []
        for name, (shades, _, _, lift, contrast, comp) in INKS.items():
            if name == "soot":
                mask = burnt
            else:
                mask = (ramp == RAMPS[name]) & (a >= 1) & ~burnt
            if not mask.any():
                continue
            soft = gw.blur(gw.fill(shade, mask), 0.5)
            self.inks.append((name, shades, gw.blur(mask.astype(float), 0.6), 7.0 + contrast * (soft - 7.0), lift,
                              comp))

    def sample(self, field, Xa, Ya):
        Xa = -np.asarray(Xa, float) if self.mirror else np.asarray(Xa, float)
        fc = np.clip(Xa - LEFT - 0.5, 0.0, W - 1.0)
        fr = np.clip(TOP - np.asarray(Ya, float) - 0.5, 0.0, H - 1.0)
        c0 = np.minimum(np.floor(fc).astype(int), W - 2)
        r0 = np.minimum(np.floor(fr).astype(int), H - 2)
        tc, tr = fc - c0, fr - r0
        return ((field[r0, c0] * (1 - tc) + field[r0, c0 + 1] * tc) * (1 - tr) +
                (field[r0 + 1, c0] * (1 - tc) + field[r0 + 1, c0 + 1] * tc) * tr)

    def keys(self, Xa, Ya, normals):
        lit_by = gw.sun_on(normals)
        weights = np.stack([self.sample(ink[2], Xa, Ya) for ink in self.inks], 0)
        which = weights.argmax(0)
        per = [gw.nearest(self.sample(soft, Xa, Ya) + lift + comp * (LIT_MEAN - lit_by), shades)
               for name, shades, _, soft, lift, comp in self.inks]
        return [(self.inks[w][0], int(per[w][i])) for i, w in enumerate(which)]


def assign(obj, keys):
    keys = limit_materials(keys)
    order = sorted(set(keys), key=lambda key: str(key))
    slot = {key: i for i, key in enumerate(order)}
    mesh = obj.data
    mesh.materials.clear()
    for key in order:
        mesh.materials.append(mat_of(key))
    mesh.polygons.foreach_set("material_index", [slot[key] for key in keys])
    mesh.update()


# --- TIME WAR's grey capsule (L 1 3 above 39 41 above 77 79: one 48 x 84 picture) ---------------------------------------

CW, CH = 48, 84                   # its picture; its origin its middle, the pixel edge (24, 42)
CAP_AXIS = 24.5                   # its axis (a pixel-edge column: x 0.5)
CAP_SQUASH = 0.62                 # its sections: this flat (as the station's)
CAP_SLOT = 0.55                   # its red slots and lights sunk this deep into the hull
CAP_GROOVE = 0.55                 # its dark lines (black, the darkest greys) creased this deep


class Capsule:
    """The capsule lying along the screen, nose up: a body turned about its axis whose half-width row by row is the
    sprite's (smoothed), its red slots sunk into it, its dark lines creased; tops and bases (mirrored) over its middle
    plane; the sprite's holes left open."""

    def __init__(self, a):
        self.a = a
        xs = -24.0 + (np.arange(CW * S) + 0.5) / S
        ys = 42.0 - (np.arange(CH * S) + 0.5) / S
        X, Y = np.meshgrid(xs, ys)
        opaque = a >= 0
        widths = np.zeros(CH)
        for r in range(CH):
            cs = np.nonzero(opaque[r])[0]
            if len(cs):
                widths[r] = max(CAP_AXIS - cs.min(), cs.max() + 1 - CAP_AXIS)
        wf = np.repeat(widths, S)
        k_ = np.exp(-0.5 * (np.arange(-4, 5) / 2.0) ** 2)
        wf = np.convolve(np.pad(wf, 4, mode="edge"), k_ / k_.sum(), mode="valid")
        R = np.maximum(wf[:, None] + 0.4, 0.5) + np.zeros_like(X)
        dx = np.abs(X - (CAP_AXIS - 24.0))
        hull = CAP_SQUASH * np.sqrt(np.clip(R * R - dx * dx, 0.0, None))
        ramp = np.where(a >= 0, a >> 4, -1)
        shade = np.where(a >= 0, a & 15, 0)
        red = gw.blur(up_c(ramp == 7).astype(float), 0.4 * S)
        dark = gw.blur(up_c(((a == 1) | ((ramp == 0) & (shade <= 2))) & opaque).astype(float), 0.4 * S)
        top = hull - CAP_SLOT * np.clip(red * 1.5, 0.0, 1.0) - CAP_GROOVE * np.clip(dark * 1.3, 0.0, 1.0)
        soft = gw.blur(up_c(opaque).astype(float), 0.45 * S) > 0.5
        top = np.where(soft, np.maximum(top, 0.0), 0.0)
        self.cells_f = CapField(soft.astype(float))
        self.top_f = CapField(top)
        self.base_f = CapField(np.where(soft, -hull, 0.0))

    def cells(self, cx, cy):
        return self.cells_f(cx, cy) > 0.5

    def heights(self, Xa, Ya):
        return self.top_f(Xa, Ya)

    def bases(self, Xa, Ya):
        return np.minimum(self.base_f(Xa, Ya), self.top_f(Xa, Ya) - 0.05)


def up_c(m):
    return np.repeat(np.repeat(m, S, 0), S, 1)


class CapField:
    """Values on the capsule's fine grid, sampled bilinearly."""

    def __init__(self, values):
        self.v = values

    def __call__(self, Xa, Ya):
        h, w = self.v.shape
        fc = np.clip((np.asarray(Xa, float) + 24.0) * S - 0.5, 0.0, w - 1.0)
        fr = np.clip((42.0 - np.asarray(Ya, float)) * S - 0.5, 0.0, h - 1.0)
        c0 = np.minimum(np.floor(fc).astype(int), w - 2)
        r0 = np.minimum(np.floor(fr).astype(int), h - 2)
        tc, tr = fc - c0, fr - r0
        v = self.v
        return ((v[r0, c0] * (1 - tc) + v[r0, c0 + 1] * tc) * (1 - tr) +
                (v[r0 + 1, c0] * (1 - tc) + v[r0 + 1, c0 + 1] * tc) * tr)


class CapPaint(Paint):
    """polish_station.Paint on the capsule's picture."""

    def __init__(self, a):
        Paint.__init__(self, a, a)

    def sample(self, field, Xa, Ya):
        fc = np.clip(np.asarray(Xa, float) + 24.0 - 0.5, 0.0, CW - 1.0)
        fr = np.clip(42.0 - np.asarray(Ya, float) - 0.5, 0.0, CH - 1.0)
        c0 = np.minimum(np.floor(fc).astype(int), CW - 2)
        r0 = np.minimum(np.floor(fr).astype(int), CH - 2)
        tc, tr = fc - c0, fr - r0
        return ((field[r0, c0] * (1 - tc) + field[r0, c0 + 1] * tc) * (1 - tr) +
                (field[r0 + 1, c0] * (1 - tc) + field[r0 + 1, c0 + 1] * tc) * tr)


def parse_capsule(text, first_row=4):
    a = -np.ones((CH, CW), int)
    for i, line in enumerate(text.split()):
        for c in range(CW):
            t = line[2 * c:2 * c + 2]
            if t != "..":
                a[first_row + i, c] = int(t, 16)
    return a


CAPSULE_PIECES = [("grey_capsule_tl", 1, (-24.0, 0.0, 14.0, 42.0)), ("grey_capsule_tr", 3, (0.0, 24.0, 14.0, 42.0)),
                  ("grey_capsule_ml", 39, (-24.0, 0.0, -14.0, 14.0)), ("grey_capsule_mr", 41, (0.0, 24.0, -14.0, 14.0)),
                  ("grey_capsule_bl", 77, (-24.0, 0.0, -42.0, -14.0)),
                  ("grey_capsule_br", 79, (0.0, 24.0, -42.0, -14.0))]


def check_capsule(cap, sheet):
    covered = gw.own_coverage(lambda Xa, Ya: cap.cells(Xa, Ya), CW, CH, -24.0, 42.0)
    mask = [[False] * CW for _ in range(CH)]
    for _, sprite, box in CAPSULE_PIECES:
        c0, r0 = int(box[0] + 24.0), int(42.0 - box[3])
        for r, line in enumerate(k.sprite_mask(sheet, sprite)):
            for c, v in enumerate(line):
                if v:
                    mask[r0 + r][c0 + c] = True
    mk.compare("the grey capsule (its 48 x 84 picture)", covered, mask)
    for name, sprite, box in CAPSULE_PIECES:
        c0, r0 = int(box[0] + 24.0), int(42.0 - box[3])
        sub_c = [row[c0:c0 + 24] for row in covered[r0:r0 + 28]]
        sub_m = [row[c0:c0 + 24] for row in mask[r0:r0 + 28]]
        both = sum(p and q for rp, rq in zip(sub_c, sub_m) for p, q in zip(rp, rq))
        either = sum(p or q for rp, rq in zip(sub_c, sub_m) for p, q in zip(rp, rq))
        print("silhouette overlap %s (l %d): %.3f" % (name, sprite, both / max(1, either)))


def build_capsule(options, only, out, sheet):
    a = parse_capsule(CAPSULE)
    cap = Capsule(a)
    if sheet and only is None:
        check_capsule(cap, sheet)
    plate = gw.Plate((-24.0, 24.0, -42.0, 42.0), cap.heights, base=cap.bases, cells=cap.cells, bottom=False)
    paint = CapPaint(a)
    for name, sprite, box in CAPSULE_PIECES:
        if only is not None and name not in only:
            continue
        k.reset()
        obj, kinds, _ = plate.mesh(name, gw.piece_owner(box))
        centres, normals = gw.face_data(obj)
        centres, normals = np.round(centres, 4), np.round(normals, 4)
        top = paint.keys(centres[:, 0], centres[:, 1], normals)
        keys = [top[i] if kinds[i] == 0 else WALL for i in range(len(kinds))]
        assign(obj, keys)
        gw.finish_piece(name, [obj], box, out, options)


# --- The pieces ---------------------------------------------------------------------------------------------------------
# (name, sprite, damaged name, damaged sprite, box in the half's plane); half B's, and half A's (its mirror image).
PIECES_B = [("station_end_left", 24, "station_end_left_damaged", 100, (-36.0, -12.0, -14.0, 14.0)),
            ("station_l_tl", 7, "station_l_tl_damaged", 83, (-12.0, 12.0, 0.0, 28.0)),
            ("station_l_tr", 9, "station_l_tr_damaged", 85, (12.0, 36.0, 0.0, 28.0)),
            ("station_l_bl", 45, "station_l_bl_damaged", 121, (-12.0, 12.0, -28.0, 0.0)),
            ("station_l_br", 47, "station_l_br_damaged", 123, (12.0, 36.0, -28.0, 0.0))]
PIECES_A = [("station_end_right", 34, "station_end_right_damaged", 110, (12.0, 36.0, -14.0, 14.0)),
            ("station_r_tr", 13, "station_r_tr_damaged", 89, (-12.0, 12.0, 0.0, 28.0)),
            ("station_r_tl", 11, "station_r_tl_damaged", 87, (-36.0, -12.0, 0.0, 28.0)),
            ("station_r_br", 51, "station_r_br_damaged", 127, (-12.0, 12.0, -28.0, 0.0)),
            ("station_r_bl", 49, "station_r_bl_damaged", 125, (-36.0, -12.0, -28.0, 0.0))]


def place(box):
    """A piece's sprite's top left pixel in its half's picture."""
    return int(box[0] - LEFT), int(TOP - box[3])


def check(half, pieces, sheet, label):
    covered = gw.own_coverage(lambda Xa, Ya: half.cells(Xa, Ya), W, H, LEFT, TOP)
    mask = [[False] * W for _ in range(H)]
    for _, sprite, _, _, box in pieces:
        c0, r0 = place(box)
        for r, line in enumerate(k.sprite_mask(sheet, sprite)):
            for c, v in enumerate(line):
                if v:
                    mask[r0 + r][c0 + c] = True
    mk.compare(label, covered, mask)
    for name, sprite, _, _, box in pieces:
        c0, r0 = place(box)
        sub_c = [row[c0:c0 + 24] for row in covered[r0:r0 + 28]]
        sub_m = [row[c0:c0 + 24] for row in mask[r0:r0 + 28]]
        both = sum(p and q for rp, rq in zip(sub_c, sub_m) for p, q in zip(rp, rq))
        either = sum(p or q for rp, rq in zip(sub_c, sub_m) for p, q in zip(rp, rq))
        print("silhouette overlap %s (l %d): %.3f" % (name, sprite, both / max(1, either)))


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    sheet = None
    if "check" in options:
        sheets = options["check"]
        sheet = os.path.join(sheets, "enemy_L.png") if os.path.isdir(sheets) else sheets
    intact = parse_picture(PICTURE)
    damaged = patched(intact, DAMAGED)
    for look, pic in (("intact", intact), ("damaged", damaged)):
        for mirror, pieces in ((False, PIECES_B), (True, PIECES_A)):
            half = Half(pic, intact, mirror)
            if sheet and only is None:
                sel = [(d if look == "damaged" else n, ds if look == "damaged" else s, None, None, b)
                       for n, s, d, ds, b in pieces]
                check(half, sel, sheet, "half %s, %s (its 72 x 56 picture)" % ("A" if mirror else "B", look))
            plate = gw.Plate((-36.0, 36.0, -28.0, 28.0), half.heights, base=half.bases, cells=half.cells,
                             bottom=False)
            paint = Paint(pic, intact, mirror)
            for name, sprite, dname, dsprite, box in pieces:
                model = dname if look == "damaged" else name
                if only is not None and model not in only:
                    continue
                k.reset()
                obj, kinds, _ = plate.mesh(model, gw.piece_owner(box))
                centres, normals = gw.face_data(obj)
                centres, normals = np.round(centres, 4), np.round(normals, 4)
                top = paint.keys(centres[:, 0], centres[:, 1], normals)
                keys = [top[i] if kinds[i] == 0 else WALL for i in range(len(kinds))]
                assign(obj, keys)
                gw.finish_piece(model, [obj], box, out, options)
    build_capsule(options, only, out, sheet)


# --- The sprites' pixels ----------------------------------------------------------------------------------------------
# Each pixel its palette index as two hex digits ('..' none), rows top to bottom (the picture's empty rows left out).

PICTURE = """
....................................................................010101010101010101..........................................................
....................................................................01080808080808080701........................................................
....................................................................0108040404040404070601......................................................
....................................................................0109040807050806040601..........................010101......................
....................................................................0109040808050808040601........................0105050301....................
....................................................................0109050808050808050701......................01050302060301..................
....................................................................010a070707050707050701....................010602050502050301................
....................................................................010a070808060908050801..................0106030506060203060301..............
....................................................................020b080808050808060801................01070305060602040503060301............
....................................................................020b070605040607080901..............0108030503050304060603050501............
....................................................................020c0a0a0a0a09090a0701............010905050606030506060305070301............
....................................................................0104010106080501010201............010b050506030502050305070301..............
....................................................................0101....010601....0101............01070a05030506060205070301................
..........................................................................0104050301..................0102080a0505060305070301..................
..............................................................010101010101010406020101010101............0106090a050305060301....................
........................................................01010101070505050504030502040605040201......0101010505080a06070301......................
......................................................010205040409070707070707070707070504030201..0105060901020408080301........................
........................010101..01010101............0103060101010b0a0a0a0a0a0a090807060503020301010303090601..01010101..........................
........................0104010101040301............010501....0101010101010101010104040302030405030604010401....................................
........................0106017401050501........0101010401....................0101050504050505060703060401......................................
........................0107020301060601010101010104040401......................01080808080808080808010101......................................
........................010803030208060172727271010505050101010101..............0101010909090909090902010101010101..............................
..............010101010101090405030907017374010101080706020305050301....010101010101010b09090909090a02030304020401......01010101010101010101....
..............0105040404040b0607040b0a0101010106020b0808030407070401....010705050505050b0a0a0a0a0a0a04050808030701......010b060606050505050401..
........0101010108080808050d0509040d0d0204050508040c09090406070705323232010b08080807070d0b0b0b0b0b0b0406097201010101..01040903030303020302020301
........010706050a090a0a060b0409040b0a040707050a060d0b0b04070a0b06343736350c09090908080704030202020201047273700106040104050803040404030404020301
........010b07050c0b0c0b06090408030a080509090408070a08090406070705343b3b370f0c0c0c0a090806050404040404067275720101010104050803040404030404020301
........0107040309070706040804060209070406060307060907080405060604313232340b07080808080808070606060606077276737373737202020503020202020202020101
........0104010106060605040703040207040101020105030805050203040502343736390a07070707070707070707070707067274720101010104050803040404030404020301
........0103020206040404030501020105040102010104020604040103030501343434370705050504040404040404040404037172710103030104050803040404030404020301
........0101010107020201010401010104030101020104020403040102020401303132330504040403030c0808080808080202020101010101..01040903030303020302020301
..............010503020201030101010302010101010301020205010102060101....010201010101010806060606060602010102010401......010b060606050505050401..
..............010101010101030101010202017171010101020205010103020101....010101010101010705050505050602050605010501......01010101010101010101....
........................010301020102020170717101010304050101010101..............0101010505050505050501010101010101..............................
........................0104010101030301010101010102030101......................01040404040404040404010101......................................
........................0105017201040501........0101010101....................0101010101010101020301020101......................................
........................0107010101060501............010101....0101010101010101010101010101010101010201010101....................................
........................010101..01010101............0101020101010a0706060606060504030201010101010101010502010101010101..........................
......................................................010101010107040303030303030303030101010101..0101020501010104040101........................
........................................................01010101030101010101010101010201010101......0101010101040602030101......................
..............................................................010101010101010102010101010101..........0101020506010101020101....................
..........................................................................0101010101..................010104060101020101030101..................
....................................................................0101010101020101010101............01030601010102020101030101................
....................................................................0101010102040101010101............0107010102010101010101030101..............
....................................................................0108060606060507070301............010501010202010102020101030101............
....................................................................0107030201010203050601..............0104010101010101020201010101............
....................................................................0107040404010404020601................01040101020201010101020101............
....................................................................0106030404020504010601..................0104010102020101020101..............
....................................................................0106030303010303010601....................010401010101010101................
....................................................................0105010404010404010601......................01040101010101..................
....................................................................0105010404010404010601........................0104020101....................
....................................................................0105010403010402010601..........................010101......................
....................................................................0104010101010101030401......................................................
....................................................................0104040404040404030101......................................................
....................................................................01010101010101010101........................................................
................................................................................................................................................
"""

DAMAGED = """
0:34:..................
1:34:....................
2:34:......................
3:34:......................
3:58:......
4:34:................0101
4:57:..........
5:34:..............0103
5:56:..............
6:34:............0105
6:55:..................
7:34:..........020607
7:55:....................
8:34:......05010105
8:55:02....................
9:35:010101010105
9:54:020201..................
10:35:0a04020208
10:54:03010401................
11:35:01
11:38:0106
11:54:03010101..............
12:39:03
12:54:02010301............
13:38:020201
13:53:07030102
13:58:01........
14:38:010101
14:53:02010101
14:58:01......
15:35:040201010101
15:53:02010108
15:59:01..
16:35:06040301010406
16:51:0407
16:54:0101
17:36:09070401010104
17:46:02
17:50:020703
18:41:010102
18:45:020104
18:49:05
18:52:03
19:41:0204
19:45:030104050105
20:45:0602060505
21:43:08080603080607
22:18:06
22:26:0605
22:43:070503030b0709
22:60:....................
23:16:030806
23:25:0a050502
23:39:03020103040203090708
23:60:......................
24:8:070707
24:14:04070106070103
24:25:0b040402
24:38:050401010207030505080a
24:59:..........................
25:6:040105060608
25:13:0901010103
25:19:03
25:25:0a03030105
25:37:0a03020103
25:43:0301010101
25:59:01........................
26:5:0a0301070405070302010101
26:24:06040101010206
26:37:0b04020409
26:43:060401010103030305
26:60:010101..................
27:5:040101010101010101010101
27:24:030101010101
27:37:060101010706020101010102020204
27:59:0101..0101................
28:5:02
28:8:0101010101010103
28:24:010101010101
28:37:040101020401010101010102030303
28:59:0101050102010101..........
29:6:0101010101010206
29:23:0301010205
29:29:01
29:37:010101030101010101010101020302
29:59:010104010103
29:66:01..........
30:9:0503
30:24:01020602
30:29:01
30:31:02
30:37:01010102
30:42:020a0404040406
30:60:02070202
30:65:01............
31:8:0402
31:25:04
31:27:04
31:30:0103
31:37:01
31:43:0603020405
31:64:01............
32:30:0101
32:44:0304
32:64:............
36:52:....
37:37:04030202
37:51:................
38:36:020101010102
38:50:....................
39:50:......................
40:51:......................
41:51:........................
42:51:..........................
43:51:............................
44:42:0602
44:51:..............................
45:35:06
45:42:0304
45:52:............................
46:35:04
46:41:020103..
46:53:..........................
47:35:010206
47:40:0403
47:43:....
47:54:......................
48:35:010105
48:40:0201......
48:55:..................
49:35:02
49:37:08
49:40:02........
49:56:..............
50:35:06
50:40:0303......
50:57:..........
51:35:04
51:43:....
51:58:......
52:42:0101..
"""

CAPSULE = """
............................................010101..............................................
..............................05060606040605050204040505040101030302............................
..........................0406070708070409080803060408070601030504030201........................
........................0406070a0a0908050504040307040404030304060504030202......................
......................0406070a0c0b0908070908080407050a0908020406050403020303....................
......................040507080909080807060607050806060606040506050403020305....................
......................040507080808080808080909060807080909060706050403020306....................
......................040506080808080808070707070807070707060706050403020406....................
......................030405070808080808080808080808080707070605040302040705....................
........................03040506070707070707070707070707060605040302040705......................
..........................0303030304040505050505050505050505040404050605........................
..............................03040505050505050506040404040405050606............................
..............................04050506060606060607040404040404030404............................
..............................0202020304040404050704020203030302................................
..........................03050506070808080903060804020a0605040403020202........................
........................04040402010202020202010608040201010101......020202......................
......................01050703070a0303030304050708040402010101010504..0302......................
......................0305090306080305050506070708040403020202010604..030202....................
......................030407030608030403050607070804040302......0604..030202....................
......................030406030608037303050607070804040302..72..0504..040202....................
......................030406030202037503060607070804040303..72........040202....................
......................030406030271737703070607070804040303..727371..02050202....................
......................020305040372737603070607070804040403..727371..02040202....................
........................0204040574747403090606070804040403..727371..020202......................
........................0102020273747403090606070804040403..727371..010101......................
........................0104060771747403080606070705040403..72737106040303......................
........................0204040671737403070606070605040302..72737104020202......................
........................0304040670727403050606060605030301..72737104020202......................
........................0404040670707002020405050504030201..70707004020202......................
........................0404040571717102020202030202010101..70717004020202......................
........................04040405717372040b0807070706060607..71727004020202......................
........................0404040571737203070504030303040505..71727004020202......................
........................0404040571717103070403030303030405..70717104020202......................
........................0404040571737803070303030303030305..73757204020202......................
........................04040405727376030703030303030303040172737104020202......................
........................04040405727375030703030303030303040172737104020202......................
........................04040405727374030703030303030303040172737104020202......................
........................04040405707274030703030303030303040171737104020202......................
........................0404040570707003070403030303030404..70707004020202......................
........................0404040571727103060504030303040405..71717004020202......................
........................0404040571737203060505040404040505..71727004020202......................
........................04040405717372..0101010102010101....71727004020202......................
........................0404040571717101010304050402030101..70717104020202......................
........................0304040571737801030606050503040401..73757204020202......................
........................0204040572737602060607090804040403..72737104020202......................
........................0204040572737503080708090906040403..72737104020202......................
........................0204040572737403090708090906040403..72737103020101......................
........................0103030172737403090708080805040403..727371..010101......................
........................0204040373737403090607070804040403..72737103030303......................
........................0204040474747403090606070804040403..72737101020202......................
........................0204040574747403090606070804040403..727371..020202......................
........................0204040574747403090606070804040403..727371..020202......................
..........................0204057474040806060607080404040403..7270..0102........................
..............................01730308050506060709050404040303..72..............................
..................................090605060606070a05030404040304................................
..................................060506060606090a08060204050606................................
......................................0204060907070708050301020101..............................
....................................73760509070707070708047571..................................
..................................02050506090707070707090504030201..............................
............................040707070707090a07070707070a08060606050403..........................
..........................040707080808090a0a0707070707090a09090706040404........................
........................04060708090909090907060606070706070607070605040304......................
........................05070709090909080203030303030303040606060605040306......................
........................060708090b0d0b080304040404040404040606060605040306......................
..................................010204030606060505040301020101010101..........................
................................04050807070706060505050505060302020305..........................
............................010204050807070706060505050505060302020304..........................
..............................0101010405060606050404030302010101010202..........................
........................030607090b0d0f0f0e0d0c0b0a090808070606050403030303......................
........................03050606060606060707070707060606060505040303040603......................
..........................0304050505050505050505050505050504030303040602........................
..............................04040404040404040404040404030403040505............................
....................................010203030505040302020201....................................
..................................7173767a7977757575757778767472................................
..................................717275777877767575747475757371................................
..............................................0101..............................................
"""


if __name__ == "__main__":
    build()
