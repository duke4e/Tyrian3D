"""The spinning claw and the dark sawblade of IXMUCANE, SAWBLADES and ?TUNNEL? (sheet #, written x23 in models.cfg),
polished (2026-10-21; it replaces wave3_ar_saw.py, whose tubes and balls drew both). Each is four 2x2 sprites meeting
at their shared corner, built whole, cut along the sprites' edges into the four pieces (models.cfg origin) and drawn
at their own places, where they meet again; one set of four pieces for every frame the level events show.

Where the levels put them (the .lvl events): the claw is enemies 426-429 (153 155 above 191 193), the sawblade
430-433 (233 235 above 271 273), shape bank 27, the same in every episode's data; no other enemy (launched ones
included) uses the bank, and no episode 6 level loads it. Each is laid out as one 48 x 56 square: the top left piece
at x, the top right at x + 24, the two below 28 pixels lower (the claw: IXMUCANE and ?TUNNEL? ground enemies, the
lower row a map row (28) lower, sky enemies spawned 28 frames apart, SAWBLADES ground 2 at y -56 and -28; the saw: top
enemies at y -56 and -28 in IXMUCANE, ground 2 in SAWBLADES), all with one link.

The pieces never animate by themselves: event 24 on their link plays frames of the enemy data beyond the first.
- The claw (gr 153 153 89 89 85 85 81 81 77 77 0 ... 13 9 5 1): ani=10 cycle=1 mode=1 plays the first ten and stops
  on 77, then ani=20 cycle=17 spins it for ever, 9 5 1 13 9 ..., a frame each game frame: the claw turning
  counter-clockwise, a quarter turn in four frames (it is four-fold symmetric). The sprites: 77 the full claw; 9 is
  77 with every grey a shade lighter; 13, 5 and 1 are 9 turned 25 degrees clockwise, 25 and 45 counter-clockwise
  (turned so here too: steps of 25, 20, 20 and 25, which read as an even spin at a frame a game frame). 153 is a
  dark little knot, 9 scaled 0.475 about the hub (its hub drawn bigger, 6 of 11 pixels), and 89, 85, 81 grow (0.8,
  0.9, 1.0) and light up (their greys 5, 4, 3, 2 and 77's 1 shade darker than 9's). The unfolding sprites are drawn
  off-centre (their hubs 0.5-1.5 pixels right and down of 77's); the models keep the hub in place, so the claw grows
  without a wobble. The hub is redrawn in every frame with its yellow lamp up and left of the middle: a reflection,
  not a lamp that turns.
- The sawblade (gr 233 229 229 165 165 161 157): ani=5 cycle=1 mode=1 plays 233 229 229 165 165 and stops, then
  ani=7 cycle=6 alternates 157 161 157 161 ... every game frame (161 is 157 turned 22.5 degrees clockwise: the
  shimmer of a spinning blade). 157 is the claw's four arms pixel for pixel (9's), the same four arms turned 45
  degrees clockwise underneath them (the two blades in each quarter: a strut out of the hub carrying a long and a
  short blade), and a blue gem for a hub. 165 is 157 two shades darker, 233 six (most of it the outline's black),
  229 233 two shades lighter (and drawn a pixel lower, a jitter left out here).

As the sprites draw them (the 48 x 56 pictures; the hub's middle is pixel (24, 27), x 0.5, y 0.5 here):
- The arm (one up the screen; the others are it turned about the hub): a steel rod out of the hub (columns 22-27 of
  rows 17-21 with the outline, lit down its left), narrowing where it goes into the hub, ending in a pincer: a palm
  across the arm (rows 14-17) with a rounded heel to the left (columns 18-22 of rows 12-17), and two parallel blades
  rising out of it up and to the right at 45 degrees, the long one from the heel to a chisel tip cut level with the
  screen (row 4, columns 26-32), the short prong from the palm's right end to its tip (row 9, columns 31-35), a slot
  between them. Each blade lit along its left half (0a-0b), a dark line down its middle (03-04), mid grey to the
  right (05-07). Built as a steel plate in the pincer's plan (bevelled, its plan kept 0.3 pixels inside the outline's
  outer edge) with a low ridge along each blade (two facets up to a groove along the crest, rising out of the palm,
  its end cut level with the tip), the rod a round bar out of the hub that sinks into the palm.
- The claw's hub: a bronze disc (11 pixels across, ramp 1 with dark brown shadows), a lighter cross over it where
  the arms meet it, the lamp (0x7c, 0x7b) up and left of its middle. Built as a bronze dome with four ribs along the
  arms and a glowing amber lens on its crown; the lens's upper left, where the sprites put the lamp, glows hotter in
  every frame (painted after the frame's turn, so it stays put while the claw spins, as a reflection would).
- The sawblade's hub: a cushion-cut blue gem (9 x 9 pixels, its corners cut; ramp 9, a white glint 0x8f at its upper
  left and lighter corners) in a thin dark bezel. Built as a cut gem (a low table, eight crown facets, the girdle,
  a pavilion inside the bezel), glowing a little in its own blues.

The steel is painted after each frame's turn by how its faces face the game's sun (from the upper left): facets
towards it lighter, away darker, the grooves and the plate's walls dark, so every frame is lit alike, as a real
spinning blade would be. Emissions: the lamp 0.3-0.5, the gem 0.08-0.35 (the cfg's glows add to them).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the whole's
origin is the corner where the four sprites meet (the hub's middle at (0.5, 0.5)); each piece is moved so that its
sprite's centre is its origin (its base on the layer: the hub's foot at z = 0).

Models (names unchanged, so models.cfg's model, sprite and frame lines for sheet # stay as they are): spin_claw_<s>
for the claw's frames' pieces (153 155 191 193, 89 91 127 129, 85 87 123 125, 81 83 119 121, 77 79 115 117, 13 15
51 53, 9 11 47 49, 5 7 43 45, 1 3 39 41) and dark_saw_<s> for the sawblade's (233 235 271 273, 229 231 267 269,
165 167 203 205, 161 163 199 201, 157 159 195 197). Frame models rather than models.cfg's yaw=frames: yaw=frames
(and spin=) turn each piece about its own centre, 12 and 14 pixels from the hub, so the pieces of one wheel would
each spin in place; and they turn every frame by its index, the unfolding ones too.

Replaces wave3_ar_saw.py (delete it) and the helpers of wave3_ar_kit.py only it uses (blade, banded, catmull,
scale_about, run, and its docstring's sheet # mentions; quad_pieces and turn_z went with wave3_at_orange.py, round 21);
sheet_mask, sheets_dir, about, quiet_import, forget and pieced stay (wave3_ar_gyges.py, wave3_ar_beasts.py and
wave3_at_kit.py's importers use them).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each frame's whole wheel and
each piece against the extracted sheet enemy_x23.png), --preview <prefix> (each frame's whole: top and 3/4 views),
--whole <prefix> (each frame's whole wheel as <prefix><name>.glb, for checks), --only <name,...> (the pieces to
export; a frame is built if any of its pieces is named).
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
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_arch import cut  # noqa: E402  (polish_machine_kit.cut without its material indices shifted twice)
from polish_k_pod import triangulate  # noqa: E402

HUB = (0.5, 0.5)            # the hub's middle in the whole's coordinates (pixel (24, 27) of the 48 x 56 picture)
COLUMNS = 19                # sprites per sheet row: the pieces are tl, tl + 2, tl + 2 rows, tl + 2 rows + 2
SHEET = "enemy_x23.png"
SUN = Vector((-0.6, 0.6, 1.0)).normalized()     # towards the game's sun (from above, the top left of the screen)

# The claw's frames: top left sprite -> (scale of the arms about the hub, of the hub, steel shades lighter than 9's,
# turn in degrees counter-clockwise, lamp strength). 153 is the first frame (the sprite lines). The knot's hub is
# drawn bigger than the arms' scale (6 of 11 pixels across).
CLAW = [(153, 0.475, 0.6, -5, 0.0, 0.55), (89, 0.8, 0.85, -4, 0.0, 1.0), (85, 0.9, 0.9, -3, 0.0, 1.0),
        (81, 1.0, 1.0, -2, 0.0, 1.0), (77, 1.0, 1.0, -1, 0.0, 1.0), (13, 1.0, 1.0, 0, -25.0, 1.0),
        (9, 1.0, 1.0, 0, 0.0, 1.0), (5, 1.0, 1.0, 0, 25.0, 1.0), (1, 1.0, 1.0, 0, 45.0, 1.0)]
# The sawblade's: top left sprite -> (steel shades lighter than 157's, turn). 233 is the first frame.
SAW = [(233, -6, 0.0), (229, -4, 0.0), (165, -2, 0.0), (161, 0, -22.5), (157, 0, 0.0)]


def piece_boxes(prefix, tl):
    """The four pieces of a wheel whose top left sprite is tl: (name, sprite, box (x0, x1, y0, y1))."""
    return [(f"{prefix}{tl}", tl, (-24.0, 0.0, 0.0, 28.0)),
            (f"{prefix}{tl + 2}", tl + 2, (0.0, 24.0, 0.0, 28.0)),
            (f"{prefix}{tl + 2 * COLUMNS}", tl + 2 * COLUMNS, (-24.0, 0.0, -28.0, 0.0)),
            (f"{prefix}{tl + 2 * COLUMNS + 2}", tl + 2 * COLUMNS + 2, (0.0, 24.0, -28.0, 0.0))]


# --- Materials -------------------------------------------------------------------------------------------------------

STEEL = {          # key: (shade of the lit frames (9, 157), metallic, roughness)
    "hi": (0x0b, 0.35, 0.28),       # facets and bevels turned to the sun
    "top": (0x08, 0.35, 0.32),      # the flat tops
    "mid": (0x06, 0.3, 0.36),       # facets turned away
    "low": (0x04, 0.3, 0.4),        # facing away and down
    "rim": (0x03, 0.25, 0.45),      # the plates' walls (the sprites' outline)
    "groove": (0x02, 0.2, 0.5),     # the lines down the blades, the cuts' caps
}
BRONZE = {         # key: (palette index, metallic, roughness, emission in its own colour: the dome is a ball the
    "b_hi": (0x1b, 0.4, 0.3, 0.05),        # slanted camera sees mostly from the side away from the sun)
    "b_top": (0x19, 0.4, 0.32, 0.08),
    "b_mid": (0x17, 0.35, 0.36, 0.0),
    "b_low": (0x14, 0.3, 0.4, 0.0),
    "b_band": (0xa3, 0.3, 0.45, 0.0),
}
GEM = {            # key: (palette index, roughness, emission strength)
    "g_glint": (0x8f, 0.1, 0.35),
    "g_light": (0x9d, 0.12, 0.2),
    "g_table": (0x9b, 0.12, 0.14),
    "g_crown": (0x9a, 0.15, 0.1),
    "g_dark": (0x98, 0.2, 0.08),
    "g_girdle": (0x96, 0.3, 0.0),
}


def materials(lift, prefix, lamp=1.0, gem=False):
    """The materials of a frame: the steel lift shades lighter than the lit frames' (clamped to the ramp); the claw's
    bronze and lamp (lamp: its glow's share) or the saw's gem."""
    pal = k.level_palette()
    m = {}
    for key, (shade, metal, rough) in STEEL.items():
        s = max(1, min(15, shade + lift))
        m[key] = k.material(f"{prefix}_steel_{key}_{s:x}", palette=s, metallic=metal, roughness=rough)
    if gem:
        for key, (index, rough, glow) in GEM.items():
            m[key] = k.material(f"{prefix}_{key}", palette=index, metallic=0.1, roughness=rough,
                                emission=pal[index] if glow > 0 else None, emission_strength=glow)
        m["bezel"] = k.material(f"{prefix}_bezel", palette=0x02, metallic=0.5, roughness=0.4)
        return m
    for key, (index, metal, rough, glow) in BRONZE.items():
        m[key] = k.material(f"{prefix}_{key}", palette=index, metallic=metal, roughness=rough,
                            emission=pal[index] if glow > 0 else None, emission_strength=glow)
    for key, index, glow in (("lamp_rim", 0x7a, 0.32), ("lamp", 0x7c, 0.48), ("lamp_hot", 0x7e, 0.6)):
        lit = index if lamp >= 1.0 else index - 1
        m[key] = k.material(f"{prefix}_{key}_{lamp:.2f}", palette=lit, metallic=0.0, roughness=0.2,
                            emission=pal[lit], emission_strength=glow * lamp)
    return m


# --- Geometry helpers ------------------------------------------------------------------------------------------------

def inset(poly, d):
    """A counter-clockwise polygon's outline moved d inwards (each edge parallel, corners mitred)."""
    n = len(poly)
    lines = []
    for i in range(n):
        a, b = Vector(poly[i]), Vector(poly[(i + 1) % n])
        t = (b - a).normalized()
        inward = Vector((-t.y, t.x))
        lines.append((a + inward * d, t))
    out = []
    for i in range(n):
        (p0, t0), (p1, t1) = lines[i - 1], lines[i]
        den = t0.x * t1.y - t0.y * t1.x
        if abs(den) < 1e-9:
            out.append(tuple(p1))
            continue
        s = ((p1.x - p0.x) * t1.y - (p1.y - p0.y) * t1.x) / den
        q = p0 + t0 * s
        out.append((q.x, q.y))
    return out


def section_ring(points, frame):
    """A cross-section [(t, z)] placed in 3D: frame (origin, across) in the XY plane, t along across."""
    origin, across = frame
    return [Vector((origin.x + across.x * t, origin.y + across.y * t, z)) for t, z in points]


def loft_along(name, start, end, sections, mat):
    """A bar from start to end (x, y) through sections [(f, [(t, z), ...])] (f from 0 at start to 1 at end, every
    section the same number of points, counter-clockwise seen from the end), its ends closed."""
    a, b = Vector(start), Vector(end)
    along = (b - a).normalized()
    across = Vector((along.y, -along.x))       # to the right, looking along
    rings = [section_ring(pts, (a + (b - a) * f, across)) for f, pts in sections]
    obj = k.loft(name, rings, mat)
    return obj


def bisect_keep(obj, co, no):
    """Cuts an object by the plane through co with normal no, keeping the side behind it, the cut filled."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    res = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6, plane_co=co,
                                 plane_no=no, clear_outer=True)
    edges = [e for e in res["geom_cut"] if isinstance(e, bmesh.types.BMEdge) and e.is_valid]
    open_edges = [e for e in edges if len(e.link_faces) == 1]
    if open_edges:
        bmesh.ops.holes_fill(bm, edges=open_edges, sides=0)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    return obj


# --- The arm (pointing up the screen from the hub at the origin) ------------------------------------------------------

# The pincer's plan: the outline's outer edge (the 45-degree edges through the middles of the outline's steps),
# counter-clockwise from the palm's lower right; kept INSET inside it.
PINCER = [(3.0, 9.5), (12.0, 18.5), (7.0, 18.5), (2.0, 13.5), (1.5, 13.5), (1.5, 16.0), (9.0, 23.5), (2.0, 23.5),
          (-6.5, 15.0), (-6.5, 12.0), (-4.0, 9.5)]
INSET = 0.3
Z0, Z1 = 1.5, 3.5           # the plate's bottom and top
PLATE_BEVEL = 0.5
# The blades' ridges: the line down the blade (x - y = c), its half-width, from y0 (in the palm, where it rises out
# of the plate) to y1 (cut level with the tip, a bevel's width short of it).
RIDGES = [(-18.0, 1.78, 13.4, 22.65), (-9.0, 1.1, 12.4, 17.65)]
RIDGE_H, GROOVE_W, GROOVE_D, RIDGE_FADE = 0.5, 0.3, 0.24, 2.2
# The rod: along x = ROD_X from inside the hub to the palm, where it sinks into the plate: (y, half-width,
# half-height, height of its axis).
ROD_X = 0.35
ROD = [(3.4, 1.9, 1.05, 2.55), (5.0, 2.2, 1.15, 2.55), (6.0, 2.4, 1.2, 2.55), (10.0, 2.4, 1.2, 2.55),
       (10.9, 2.35, 1.15, 2.45), (11.8, 2.2, 1.0, 2.25)]


def pincer_plate(name, mat):
    plan = inset(PINCER, INSET)
    obj = mk.prism(name, plan, Z0, Z1, mat)
    mk.bevel(obj, PLATE_BEVEL, 2, 35)
    return obj


def ridge(name, line, hw, y0, y1, m):
    """A low ridge along the blade x - y = line, from y0 to y1: two facets up to a crest with a groove down it (the
    groove's faces m["groove"], kept by the painter), its height rising out of the plate over RIDGE_FADE pixels at the
    root; its end cut level with the tip (y = y1)."""
    over = hw + 0.5                    # the loft runs on past y1 and is cut there (level with the tip)
    start = (y0 + line, y0)
    end = (y1 + over + line, y1 + over)
    length = math.dist(start, end)
    sections = []
    steps = max(8, int(length / 0.5))
    base = Z1 - 0.12
    for i in range(steps + 1):
        f = i / steps
        rise = min(1.0, f * length / RIDGE_FADE)
        h = RIDGE_H * rise ** 0.8
        w = hw * (0.6 + 0.4 * rise)
        top = base + 0.12 + h
        g = min(GROOVE_W, w * 0.3)
        gd = GROOVE_D * rise
        # across points to the right: the points run from the right edge over the top to the left edge
        pts = [(w, base - 0.25), (w, base), (g, top), (0.0, top - gd), (-g, top), (-w, base), (-w, base - 0.25)]
        sections.append((f, pts))
    obj = loft_along(name, start, end, sections, m["hi"])
    obj.data.materials.append(m["groove"])
    n = 7
    for poly in obj.data.polygons:
        if poly.index < steps * n and poly.index % n in (2, 3):     # the groove's two walls
            poly.material_index = 1
    k.smooth(obj, 30)
    bisect_keep(obj, (0.0, y1, 0.0), (0.0, 1.0, 0.0))
    return obj


ROD_SEGMENTS = 24


def rod(name, mat):
    rings = [k.ring(y, hw, hh, ROD_SEGMENTS, z=z, x=ROD_X, power=2.2) for y, hw, hh, z in ROD]
    obj = k.loft(name, rings, mat)
    k.smooth(obj, 50)
    return obj


def paint_rod(obj, m):
    """The rod's faces in strips along it (each strip the faces between two of its sections' points), every strip
    painted by how its faces in the rod's middle face the sun: the paint's edges run straight along the rod."""
    mesh = obj.data
    n = ROD_SEGMENTS
    sides = (len(ROD) - 1) * n
    middle = 2 * n                         # the faces between the third and fourth sections (the straight run)
    picks = []
    for j in range(n):
        nrm = mesh.polygons[middle + j].normal
        f = facing(nrm)
        picks.append(m["rim"] if nrm.z < 0.3 and f < 0.45 else m["low"] if nrm.z < 0.45 else
                     m["hi"] if f > 0.88 else m["top"])
    slots = {}
    for poly in mesh.polygons:
        mat = picks[poly.index % n] if poly.index < sides else m["low"]
        if mat.name not in slots:
            slots[mat.name] = mk.slot_of(obj, mat)
        poly.material_index = slots[mat.name]


def arm(prefix, m, z_shift=0.0):
    """One arm up the screen: the plate, the ridges on its blades, the rod; returns its objects."""
    parts = [pincer_plate(f"{prefix}_plate", m["top"])]
    for i, (line, hw, y0, y1) in enumerate(RIDGES):
        parts.append(ridge(f"{prefix}_ridge{i}", line, hw, y0, y1, m))
    parts.append(rod(f"{prefix}_rod", m["top"]))
    if z_shift:
        mk.transform(parts, Matrix.Translation((0, 0, z_shift)))
    return parts


# --- The hubs (at the origin) -----------------------------------------------------------------------------------------

DOME = [(4.9, 0.0), (5.15, 0.4), (5.25, 1.2), (5.25, 2.6), (5.05, 3.5), (4.55, 4.3), (3.75, 4.95), (2.8, 5.35),
        (2.0, 5.5)]
LENS_R, LENS_Z, LENS_H = 1.6, 5.38, 0.85
RIB = [(2.4, 0.85), (3.4, 0.9), (4.3, 0.95), (5.15, 1.0)]      # (radius, half-width) along each arm


def dome_z(r):
    """The dome's height at radius r (its profile)."""
    pts = sorted((rr, z) for rr, z in DOME)
    if r <= pts[0][0]:
        return pts[0][1]
    for (r0, z0), (r1, z1) in zip(pts, pts[1:]):
        if r0 <= r <= r1:
            return z0 + (z1 - z0) * (r - r0) / (r1 - r0)
    return pts[-1][1]


def bronze_hub(m):
    """The claw's hub: a bronze dome, four ribs along the arms, a lens on its crown in a bronze bezel."""
    prof = [(r, z) for r, z in DOME]
    dome = mk.lathe("hub_dome", prof, (0.0, 0.0), m["b_top"], segments=40)
    k.smooth(dome, 50)
    parts = [dome]
    for i in range(4):
        # a flattened bar along +y lying on the dome, its sections in the XZ plane
        rings = [k.ring(r, hw, 0.4, 12, z=dome_z(r) - 0.12, bottom=0.5) for r, hw in RIB]
        rib = k.loft(f"hub_rib{i}", rings, m["b_hi"])
        k.smooth(rib, 50)
        mk.transform([rib], Matrix.Rotation(math.radians(-90.0 * i), 4, "Z"))
        parts.append(rib)
    bezel = mk.lathe("hub_bezel", [(LENS_R + 0.55, LENS_Z - 0.3), (LENS_R + 0.6, LENS_Z + 0.1),
                                   (LENS_R + 0.3, LENS_Z + 0.35), (LENS_R - 0.05, LENS_Z + 0.25),
                                   (LENS_R - 0.1, LENS_Z - 0.2)], (0.0, 0.0), m["b_mid"], segments=32)
    k.smooth(bezel, 50)
    parts.append(bezel)
    lens_prof = [(LENS_R * math.cos(a), LENS_Z + LENS_H * math.sin(a))
                 for a in [math.radians(v) for v in (0, 15, 30, 45, 60, 72, 82)]]
    lens = mk.lathe("hub_lens", [(LENS_R, LENS_Z - 0.4)] + lens_prof, (0.0, 0.0), m["lamp"], segments=32)
    k.smooth(lens, 60)
    parts.append(lens)
    return parts


GEM_HALF, GEM_CLIP = 4.6, 1.3         # the girdle: a square, its corners cut off this far along each side
BEZEL_HALF = 5.05
# The gem's rings, girdle to table: (half size, corner clip, height).
GEM_RINGS = [(GEM_HALF, GEM_CLIP, 3.65), (GEM_HALF, GEM_CLIP, 4.0), (3.55, 1.05, 4.95), (2.45, 0.75, 5.5)]
GEM_TOP, GEM_CULET = 5.66, 1.2


def octagon(half, clip):
    """A square of half size `half` with its corners cut `clip` along each side: eight points counter-clockwise from
    the right side's lower end."""
    h, c = half, half - clip
    return [(h, -c), (h, c), (c, h), (-c, h), (-h, c), (-h, -c), (-c, -h), (c, -h)]


def gem_hub(m):
    """The sawblade's hub: a cushion-cut gem (an octagonal girdle, two tiers of eight planar crown facets up to a low
    table) in a thin dark bezel."""
    bezel_plan = octagon(BEZEL_HALF, GEM_CLIP + 0.25)
    bezel = mk.prism("gem_bezel", bezel_plan, 0.0, GEM_RINGS[1][2] + 0.1, m["bezel"])
    mk.bevel(bezel, 0.3, 2, 35)
    bm = bmesh.new()
    rings = [[bm.verts.new((x, y, z)) for x, y in octagon(h, c)] for h, c, z in GEM_RINGS]
    top = bm.verts.new((0.0, 0.0, GEM_TOP))
    culet = bm.verts.new((0.0, 0.0, GEM_CULET))
    n = 8
    for i in range(n):
        j = (i + 1) % n
        for lo, hi in zip(rings, rings[1:]):
            bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
        bm.faces.new((rings[-1][i], rings[-1][j], top))
        bm.faces.new((rings[0][j], rings[0][i], culet))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new("gem")
    bm.to_mesh(mesh)
    bm.free()
    gem = bpy.data.objects.new("gem", mesh)
    bpy.context.scene.collection.objects.link(gem)
    gem.data.materials.append(m["g_crown"])
    for poly in gem.data.polygons:
        poly.use_smooth = False
    return [bezel, gem]


# --- Painting (after each frame's turn: by how the faces face the sun) ------------------------------------------------

def facing(n):
    return n.dot(SUN)


def paint_faces(obj, pick):
    """Gives faces materials: pick(material name, centre, normal) returns a material, or None to keep the face's."""
    mesh = obj.data
    slots = {}
    for poly in mesh.polygons:
        current = mesh.materials[poly.material_index].name if mesh.materials else ""
        mat = pick(current, poly.center, poly.normal)
        if mat is not None:
            if mat.name not in slots:
                slots[mat.name] = mk.slot_of(obj, mat)
            poly.material_index = slots[mat.name]


def paint_steel(obj, m, kind):
    """kind: plate or ridge (the rods: paint_rod)."""
    groove = m["groove"].name

    def pick(current, c, n):
        f = facing(n)
        if n.z < -0.3:
            return m["groove"]
        if kind == "plate":
            if n.z > 0.92:
                return m["top"]
            if n.z < 0.3:
                return m["rim"] if f < 0.25 else m["low"]
            return m["hi"] if f > 0.82 else m["mid"] if f > 0.55 else m["low"]
        if kind == "ridge":
            if current == groove:
                return None
            if n.z < 0.5:
                return m["rim"]
            return m["hi"] if f > 0.83 else m["top"]
        return None
    paint_faces(obj, pick)


def paint_bronze(obj, m, kind, scale=1.0):
    def pick(current, c, n):
        f = facing(n)
        if kind == "lens":
            return m["lamp_hot"] if f > 0.9 and n.z > 0.5 else m["lamp"] if n.z > 0.35 else m["lamp_rim"]
        if kind == "rib":
            return m["b_hi"] if n.z > 0.3 else m["b_mid"]
        if kind == "bezel":
            return m["b_mid"] if n.z > 0.3 else m["b_low"]
        # the dome: by height (its rings), so the paint's edges run round it smoothly
        return m["b_band"] if c.z < 0.9 * scale else m["b_top"]
    paint_faces(obj, pick)


def paint_gem(obj, m):
    def pick(current, c, n):
        f = facing(n)
        rel = c.xy - Vector(HUB)
        r = rel.length
        if n.z < 0.2:
            return m["g_girdle"] if n.z > -0.2 else m["g_dark"]
        if n.z > 0.97:
            return m["g_glint"] if r < 1.1 or (rel.x < -0.6 and rel.y > 0.6 and r < 2.0) else m["g_table"]
        if f > 0.9:
            return m["g_light"]
        return m["g_crown"] if f > 0.6 else m["g_dark"]
    paint_faces(obj, pick)


# --- The wholes -------------------------------------------------------------------------------------------------------

def paint_all(objects, m, scale=1.0):
    for obj in objects:
        name = obj.name
        if "_plate" in name:
            paint_steel(obj, m, "plate")
        elif "_ridge" in name:
            paint_steel(obj, m, "ridge")
        elif "_rod" in name:
            paint_rod(obj, m)
        elif name.startswith("hub_lens"):
            paint_bronze(obj, m, "lens", scale)
        elif name.startswith("hub_rib"):
            paint_bronze(obj, m, "rib", scale)
        elif name.startswith("hub_bezel"):
            paint_bronze(obj, m, "bezel", scale)
        elif name.startswith("hub_dome"):
            paint_bronze(obj, m, "dome", scale)
        elif name.startswith("gem_bezel"):
            paint_faces(obj, lambda current, c, n: m["bezel"] if n.z > 0.5 else m["groove"])
        elif name == "gem" or name.startswith("gem."):
            paint_gem(obj, m)


def place(objects, scale, turn):
    """Scales the objects about the hub (built at the origin), turns them counter-clockwise and moves them to the
    hub's place in the whole."""
    mat = Matrix.Translation((HUB[0], HUB[1], 0.0)) @ Matrix.Rotation(math.radians(turn), 4, "Z") @ \
        Matrix.Scale(scale, 4)
    mk.transform(objects, mat)
    for obj in objects:
        obj.data.update()


def build_claw(scale, hub_scale, lift, turn, lamp):
    k.reset()
    m = materials(lift, "claw", lamp)
    objs = bronze_hub(m)
    if hub_scale != scale:
        mk.transform(objs, Matrix.Scale(hub_scale / scale, 4))
    for i in range(4):
        parts = arm(f"arm{i}", m)
        mk.transform(parts, Matrix.Rotation(math.radians(-90.0 * i), 4, "Z"))
        objs += parts
    place(objs, scale, turn)
    paint_all(objs, m, hub_scale)
    return objs, m


SAW_UNDER = -0.85          # the turned arms lie this much lower than the main ones
SAW_TURNED_SCALE = 1.02


def build_saw(lift, turn):
    k.reset()
    m = materials(lift, "saw", gem=True)
    objs = gem_hub(m)
    for i in range(4):
        parts = arm(f"arm{i}", m)
        mk.transform(parts, Matrix.Rotation(math.radians(-90.0 * i), 4, "Z"))
        objs += parts
        under = arm(f"under{i}", m, SAW_UNDER)
        turned = Matrix.Rotation(math.radians(-90.0 * i - 45.0), 4, "Z") @ Matrix.Scale(SAW_TURNED_SCALE, 4)
        mk.transform(under, turned)
        objs += under
    place(objs, 1.0, turn)
    paint_all(objs, m)
    return objs, m


# --- Checks, previews, export -----------------------------------------------------------------------------------------

def wheel_mask(sheet, tl):
    """The 48 x 56 picture of the wheel whose top left sprite is tl (rows of bools)."""
    out = [[False] * 48 for _ in range(56)]
    for (dx, dy), s in zip(((0, 0), (24, 0), (0, 28), (24, 28)), (tl, tl + 2, tl + 2 * COLUMNS, tl + 2 * COLUMNS + 2)):
        mask = k.sprite_mask(sheet, s)
        for r, row in enumerate(mask):
            for c, v in enumerate(row):
                if v:
                    out[dy + r][dx + c] = True
    return out


def export_pieces(whole, m, boxes, options):
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    sheet = os.path.join(options["check"], SHEET) if "check" in options else None
    for name, sprite, box in boxes:
        if only and name not in only:
            continue
        pieces = []
        for src in whole:
            piece = cut(src, box, m["groove"])
            if piece is not None:
                # names of their own, so that the output doesn't depend on what else the run made (--whole's copies)
                piece.name = piece.data.name = f"{name}_{src.name}"
                pieces.append(piece)
        cx, cy = (box[0] + box[1]) / 2, (box[2] + box[3]) / 2
        mk.transform(pieces, Matrix.Translation((-cx, -cy, 0.0)))
        triangulate(pieces)
        bpy.context.view_layer.update()
        for src in whole:
            src.hide_render = True
        if sheet:
            mk.compare("%s (# %d)" % (name, sprite), mk.coverage(pieces, 24, 28), k.sprite_mask(sheet, sprite))
        mk.report(name, pieces, os.path.join(out, name + ".glb"))
        for obj in pieces:
            bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False


def run_frame(whole, m, label, prefix, tl, options):
    boxes = piece_boxes(prefix, tl)
    print("whole %s: %d triangles, %d objects" % (label, mk.triangles(whole), len(whole)))
    bpy.context.scene.view_settings.view_transform = "Standard"
    if "check" in options:
        sheet = os.path.join(options["check"], SHEET)
        mk.compare("whole " + label, mk.coverage(whole, 48, 56), wheel_mask(sheet, tl))
    if "preview" in options:
        mk.preview(options["preview"] + label, whole, size=(48, 56), scale=10, distance=1.6)
    if "whole" in options:
        copies = []
        for obj in whole:
            c = obj.copy()
            c.data = obj.data.copy()
            bpy.context.scene.collection.objects.link(c)
            copies.append(c)
        triangulate(copies)
        mk.export(copies, options["whole"] + label + ".glb")
        for c in copies:
            bpy.data.objects.remove(c)
    export_pieces(whole, m, boxes, options)


def wanted(prefix, tl, options):
    if "only" not in options:
        return True
    only = options["only"].split(",")
    return any(name in only for name, _, _ in piece_boxes(prefix, tl))


def build():
    options = k.args()
    for tl, scale, hub_scale, lift, turn, lamp in CLAW:
        if not wanted("spin_claw_", tl, options):
            continue
        whole, m = build_claw(scale, hub_scale, lift, turn, lamp)
        run_frame(whole, m, "spin_claw_%d" % tl, "spin_claw_", tl, options)
    for tl, lift, turn in SAW:
        if not wanted("dark_saw_", tl, options):
            continue
        whole, m = build_saw(lift, turn)
        run_frame(whole, m, "dark_saw_%d" % tl, "dark_saw_", tl, options)


if __name__ == "__main__":
    build()
