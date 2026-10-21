"""Mug of beer (the coins sheet's sprite 241, enemy type 474: a bonus item, 375 points; 2x2, 24 x 28 pixels; about 75
of them in the levels: BUBBLES, BONUS, ** ALE **, AST. CITY, SAVARA IV, GREY MOON), polished (2026-10-21; it replaces
wave2_f.py's beer_mug(), a faceted see-through glass with tubes for flutes round a flat brown cylinder). models.cfg:
model beer_mug items/beer_mug.glb (unchanged) and sprite coins 241 beer_mug yaw=0 (see below). One sprite, no
animation; no other enemy shows it and it is no other sprite's pixels mirrored or in other ramps.

As the sprite and its 4x upscale draw it: a fluted glass beer mug seen from the side, lying with its mouth up the
screen and its handle to the right (columns 4-21, rows 5-21; the dark brown pixels to the right of and under it,
shades 0-1 of ramp 10, are its shadow on the ground and are left out of the silhouette): a straight body 14 pixels
across (columns 4-17) and 17 long (rows 5-21), its rounded rim lit (row 6, greys 10-15), the glass above the beer
grey with vertical light and dark stripes (rows 7-11: the flutes), the beer below it amber (rows 12-20, ramp 1,
shades 1-15), striped by the flutes too (lighter at columns 8, 11 and 14), lighter in the thick base (rows 18-20);
the handle a narrow glass loop (rows 8-19, its outer side at column 20, a slot one pixel wide between it and the
body).

Built as a fluted beer mug of thick glass lying on its side (its axis along the screen's y at AXIS_X, AXIS_Z; the
game's camera, 20 degrees from straight down from the bottom of the screen, sees its side and a sliver of its base):

- the glass: one see-through skin turned round the axis, FLUTES convex panels round the body between a plain foot
  and a plain lip (sharp grooves between the panels), the foot ring and the base's hollow underside cut in a star of
  FLUTES rays, the lip rounded over into the mouth; the foot, the lip and the middles of the two panels towards the
  sun (GLINTS: the sprite's light stripes down the glass, which a fixed model can keep) in a denser, lighter glass.
  The beer and the foam fill it, so the skin has no inside of its own (only round the mouth): no second layer of
  glass dims them. The game draws see-through materials blended, without culling and without writing depth, in the
  order of their materials and then of their triangles: the see-through parts' materials come last (the exporter
  writes the parts in the order of their names: beer, bubbles, foam, then glass and handle), the skin's faces sorted
  from the bottom up, so that its far side is drawn before its near side; where the beer is behind it, the depth
  test drops the far side;
- the beer: a cylinder inside the glass, amber, glowing a little in a warmer amber (light through beer; it keeps
  its colour where the game's sun doesn't reach, as the base the camera looks at), in stripes behind the panels
  (lighter behind a panel's middle, darker behind a groove), lighter in the thick base (rows 18-20); bubbles rising
  up the glass in a few strings;
- the head of foam from the beer's line (between rows 11 and 12, a wavy edge, wet and darker along it) up the glass,
  over the lip in a lumpy crown and across the mouth in a low dome (seeded), cream (ramp 1's lightest shades), a
  little emission so that it stays light;
- the handle: a thick glass loop out of the body's side at rows 8-9 and 17-18, its outer side at column 20, round in
  section, flaring where it meets the body, see-through like the body but denser.

No spin (yaw=0): the sprite shows the mug upright, mouth up the screen; a turning mug would turn its beer and foam
sideways and upside down (the other items that turn are round or symmetric: coins, gems, crystals, cubes, the
capsule, the purple ball). The model keeps the sprite's place (its axis a pixel left of the sprite's middle): it
does not turn, so it need not be centred. It lies on z = 0 (the game centres items in height anyway).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the origin is
the sprite's centre (pixel 12, 14): column c is x = c + 0.5 - 12, row r is y = 13.5 - r.

Replaces wave2_f.py's beer_mug() (its "The mug of beer (coins 241)" section, the @model("beer_mug", "coins", 241,
out=w.ITEMS) registration with it) and its docstring's beer_mug entry.

Options after "--": --outdir <dir> (default assets/models/items), --check <sheets dir> (the silhouette against
coins.png, the shadow's pixels left out), --preview <prefix>.
"""
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_item_kit as kit  # noqa: E402
from polish_item_kit import k  # noqa: E402

NAME, SPRITE = "beer_mug", 241
SHADOW = (0xa0, 0xa1)                 # the shadow's palette indices (left out of the silhouette)

# The body: its axis (x, z), the wall's outer radius (the panels' middles), the inside (the beer's and the foam's
# radius), the base's bottom and the lip's top (y).
AXIS_X, AXIS_Z = -1.0, 6.95
R_OUT, R_IN = 6.9, 6.35
Y_BASE, Y_TOP = -7.95, 8.95
# The flutes: how many panels, their grooves' depth, how sharp the grooves are (a power under 1: sharper), where
# the panels run (y, fading in and out over FLUTE_FADE), and the panels' turn (degrees, so that one panel's middle
# is where the sprite's middle light stripe is).
FLUTES, FLUTE_D, FLUTE_P = 14, 0.28, 0.6
FLUTE_Y, FLUTE_FADE = (-6.2, 7.3), 0.9
FLUTE_TURN = -4.5
STAR_CUT = 0.26                       # how deep the star cut under the base is
GLINTS, GLINT_W = (0, 1), 3.6         # the panels that glint (0: the one at the top, 1 the next to its left), how far
#                                       either side of their middles (degrees round the axis)
AROUND = FLUTES * 6                   # segments round the axis
# The skin's profile from the middle of the base's underside out, up the outside, over the lip and into the mouth:
# (y, radius, part).
SKIN = [
    (Y_BASE + 0.3, 0.0, "lip"), (Y_BASE + 0.22, 2.6, "lip"), (Y_BASE + 0.05, 4.2, "lip"),
    (Y_BASE, 5.0, "lip"), (Y_BASE + 0.06, 5.7, "lip"), (Y_BASE + 0.3, 6.35, "lip"),
    (Y_BASE + 0.75, 6.75, "lip"), (Y_BASE + 1.2, R_OUT, "glass"),
    (FLUTE_Y[0] - FLUTE_FADE, R_OUT, "glass"), (FLUTE_Y[0], R_OUT, "glass"), (FLUTE_Y[0] + 0.5, R_OUT, "glass"),
    (FLUTE_Y[1] - 0.5, R_OUT, "glass"), (FLUTE_Y[1], R_OUT, "glass"), (FLUTE_Y[1] + FLUTE_FADE, R_OUT, "glass"),
    (8.2, 6.97, "lip"), (8.55, 7.0, "lip"), (8.8, 6.92, "lip"), (Y_TOP, 6.72, "lip"), (Y_TOP + 0.02, 6.5, "lip"),
    (8.85, R_IN + 0.06, "lip"), (8.45, R_IN + 0.02, "lip"),
]
# The beer: from its bottom (in the base) to under the foam's edge; the base's lighter part below BASE_TOP.
BEER_Y = (Y_BASE + 0.85, 2.6)
BASE_TOP = -4.6
# The foam: its edge on the beer (BEER_LINE, waving FOAM_WAVE up and down), up the glass to FOAM_RIM, then over the
# lip in a crown and across the mouth in a low dome ((y, radius) rings) to FOAM_TIP; its lumps (FOAM_LUMPS, pixels),
# how far up from its edge it is wet (darker: FOAM_WET), the seed.
BEER_LINE, FOAM_WAVE = 2.05, 0.28
FOAM_RIM = 8.3
FOAM_CROWN = [(8.72, R_IN + 0.14), (8.98, 6.74), (9.1, 6.98), (9.2, 6.92), (9.28, 6.5)]
FOAM_DOME = [(9.33, 5.3), (9.37, 3.7), (9.39, 1.9)]
FOAM_TIP = 9.4
FOAM_LUMPS, FOAM_WET, SEED = 0.14, 0.7, 241
# Bubbles: strings of them up the glass at these angles round the axis (degrees; 90 is the top), from y0 to y1.
BUBBLES = [(70.0, -3.9, 1.5, 5), (104.0, -3.2, 1.6, 4), (131.0, -4.1, 1.1, 4)]
# The handle: its middle line in the plane z = AXIS_Z (x, y), its section's radius, flaring to HANDLE_FLARE where it
# meets the body.
HANDLE = [(5.0, 4.75), (6.4, 4.75), (7.55, 4.45), (8.3, 3.6), (8.45, 2.2), (8.45, -1.4), (8.3, -2.8),
          (7.55, -3.75), (6.4, -4.05), (5.0, -4.05)]
HANDLE_R, HANDLE_FLARE = 1.12, 1.55


def smoothstep(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def materials():
    def amber(name, index, glow_colour, glow):
        return k.material(name, palette=index, metallic=0.0, roughness=0.3, emission=glow_colour,
                          emission_strength=glow)
    pal = k.level_palette()
    return {
        "beer": amber("mug_beer", 0x18, (214, 132, 28), 0.3),
        "beer_light": amber("mug_beer_light", 0x1b, (240, 170, 60), 0.36),
        "beer_dark": amber("mug_beer_dark", 0x17, (200, 112, 18), 0.28),
        "beer_base": amber("mug_beer_base", 0x1c, (240, 176, 70), 0.34),
        "foam": k.material("mug_foam", palette=0x1e, roughness=0.85, emission=pal[0x1e], emission_strength=0.08),
        "foam_shade": k.material("mug_foam_shade", palette=0x1d, roughness=0.85, emission=pal[0x1d],
                                 emission_strength=0.06),
        "bubble": k.material("mug_bubble", palette=0x1c, roughness=0.15, emission=(250, 214, 140),
                             emission_strength=0.25),
        "handle": k.material("mug_handle", palette=0x0c, metallic=0.0, roughness=0.05, alpha=0.5),
        "glass": k.material("mug_glass", palette=0x0d, metallic=0.0, roughness=0.14, alpha=0.16),
        "lip": k.material("mug_lip", palette=0x0e, metallic=0.0, roughness=0.1, alpha=0.45),
    }


def point(theta, y, r):
    """The point at angle theta (radians, from +X towards +Z round the axis), y along it, r out from it."""
    return Vector((AXIS_X + r * math.cos(theta), y, AXIS_Z + r * math.sin(theta)))


def flute(theta):
    """How deep the groove pattern is at angle theta: 0 at a panel's middle, 1 in a groove."""
    phi = FLUTES / 2 * (theta - math.radians(90.0 + FLUTE_TURN))
    return 1.0 - abs(math.cos(phi)) ** FLUTE_P


def flute_weight(y):
    return smoothstep(FLUTE_Y[0] - FLUTE_FADE, FLUTE_Y[0], y) * (1.0 - smoothstep(FLUTE_Y[1], FLUTE_Y[1] + FLUTE_FADE, y))


def skin(mats):
    """The glass skin, its faces sorted from the bottom up."""
    bm = bmesh.new()
    rings = []
    for n, (y, r, _) in enumerate(SKIN):
        if r < 1e-6:
            rings.append([bm.verts.new(point(0.0, y, 0.0))])
            continue
        w = flute_weight(y) if r >= R_OUT - 1e-6 else 0.0
        star = STAR_CUT if n in (1, 2) else 0.0      # the base's underside, cut in a star of FLUTES rays
        rings.append([bm.verts.new(point(2 * math.pi * j / AROUND, y - star * flute(2 * math.pi * j / AROUND),
                                         r - FLUTE_D * w * flute(2 * math.pi * j / AROUND)))
                      for j in range(AROUND)])
    keys = []
    for i in range(len(rings) - 1):
        a, b = rings[i], rings[i + 1]
        part = SKIN[i + 1][2]
        for j in range(AROUND):
            jj = (j + 1) % AROUND
            if len(a) == 1:
                bm.faces.new((a[0], b[jj], b[j]))
            else:
                bm.faces.new((a[j], a[jj], b[jj], b[j]))
            keys.append(part)
    for f, part in zip(bm.faces, keys):
        f.material_index = 0 if part == "glass" else 1
        if part == "glass":
            # The glints down the panels towards the sun (the sprite's light stripes): their middles in the lip's
            # denser, lighter glass, where the panels run.
            c = f.calc_center_median()
            theta = math.degrees(math.atan2(c.z - AXIS_Z, c.x - AXIS_X))
            if FLUTE_Y[0] + 0.3 < c.y < FLUTE_Y[1] - 0.3 and any(abs(theta - (90.0 + FLUTE_TURN + 360.0 / FLUTES * n))
                                                                 < GLINT_W for n in GLINTS):
                f.material_index = 1
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    # The skin is open inside the mouth: make sure its normals face out of the glass (judged on the wall's top).
    wall = [f for f in bm.faces if abs(f.calc_center_median().y) < 1.0 and f.calc_center_median().z > AXIS_Z + 5.0]
    if sum(f.normal.z for f in wall) < 0:
        for f in bm.faces:
            f.normal_flip()
    bm.faces.ensure_lookup_table()
    bm.faces.sort(key=lambda f: f.calc_center_median().z)
    bm.faces.index_update()
    obj = kit.from_bmesh("glass", bm)
    obj.data.materials.append(mats["glass"])
    obj.data.materials.append(mats["lip"])
    k.smooth(obj, 50.0)
    return obj


def beer(mats):
    """The beer: a cylinder inside the glass, striped behind the flutes, lighter in the base."""
    bm = bmesh.new()
    ys = [BEER_Y[0], BEER_Y[0] + 0.5, BASE_TOP, BASE_TOP + 0.6, BEER_Y[1]]
    rings = [[bm.verts.new(point(2 * math.pi * j / AROUND, y, R_IN - (0.7 if y == BEER_Y[0] else 0.0)))
              for j in range(AROUND)] for y in ys]
    bottom = bm.verts.new(point(0.0, BEER_Y[0] - 0.05, 0.0))
    top = bm.verts.new(point(0.0, BEER_Y[1], 0.0))
    order = ["beer", "beer_light", "beer_dark", "beer_base"]
    for i in range(len(rings) - 1):
        for j in range(AROUND):
            jj = (j + 1) % AROUND
            f = bm.faces.new((rings[i][j], rings[i][jj], rings[i + 1][jj], rings[i + 1][j]))
            g = flute(2 * math.pi * (j + 0.5) / AROUND)
            if ys[i + 1] <= BASE_TOP + 1e-6:
                key = "beer_base"
            else:
                key = "beer_light" if g < 0.12 else "beer_dark" if g > 0.45 else "beer"
            f.material_index = order.index(key)
    for j in range(AROUND):
        jj = (j + 1) % AROUND
        bm.faces.new((bottom, rings[0][jj], rings[0][j])).material_index = order.index("beer")
        bm.faces.new((top, rings[-1][j], rings[-1][jj])).material_index = order.index("beer")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = kit.from_bmesh("beer", bm)
    for key in order:
        obj.data.materials.append(mats[key])
    k.smooth(obj, 50.0)
    return obj


def foam(mats):
    """The head of foam: from its wavy edge on the beer up the glass to the mouth, over the lip in a lumpy crown and
    across the mouth in a low dome; along its edge on the beer in its darker shade (wetter)."""
    rng = random.Random(SEED)
    waves = [(rng.randint(4, 9), rng.uniform(0, 2 * math.pi), rng.uniform(0.4, 1.0)) for _ in range(3)]
    lumps = [(rng.randint(5, 13), rng.uniform(0, 2 * math.pi), rng.uniform(0, 2 * math.pi)) for _ in range(5)]
    wsum = sum(w[2] for w in waves)

    def edge(theta):
        return BEER_LINE + FOAM_WAVE * sum(a * math.sin(n * theta + p) for n, p, a in waves) / wsum

    def lump(theta, row):
        return sum(math.sin(m * theta + p + 1.7 * row) * math.cos(q + 0.9 * row) for m, p, q in lumps) / 5

    r_foam = R_IN + 0.04
    # The rows: (y(theta), radius(theta)) from the edge tucked into the beer up to the dome's last ring.
    rows = [lambda t: (edge(t) - 0.3, R_IN - 0.25), lambda t: (edge(t), r_foam),
            lambda t: (edge(t) + FOAM_WET, r_foam)]
    for f in (0.25, 0.5, 0.75, 1.0):
        rows.append(lambda t, f=f: (edge(t) + (FOAM_RIM - edge(t)) * f, r_foam + 0.03 * FOAM_LUMPS * lump(t, f)))
    for n, (y, r) in enumerate(FOAM_CROWN):
        rows.append(lambda t, y=y, r=r, n=n: (y + 0.5 * FOAM_LUMPS * lump(t, 2 + n), r + FOAM_LUMPS * lump(t, 7 + n)))
    for n, (y, r) in enumerate(FOAM_DOME):
        rows.append(lambda t, y=y, r=r, n=n: (y + 0.6 * FOAM_LUMPS * lump(t, 12 + n), r))
    bm = bmesh.new()
    rings = [[bm.verts.new(point(2 * math.pi * j / AROUND, *row(2 * math.pi * j / AROUND))) for j in range(AROUND)]
             for row in rows]
    tip = bm.verts.new(point(0.0, FOAM_TIP, 0.0))
    for i in range(len(rings) - 1):
        for j in range(AROUND):
            jj = (j + 1) % AROUND
            bm.faces.new((rings[i][j], rings[i][jj], rings[i + 1][jj], rings[i + 1][j]))
    for j in range(AROUND):
        jj = (j + 1) % AROUND
        bm.faces.new((tip, rings[-1][j], rings[-1][jj]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for i, f in enumerate(bm.faces):
        f.material_index = 1 if i < 2 * AROUND else 0     # the faces under the edge and along it: the wet shade
    obj = kit.from_bmesh("foam", bm)
    obj.data.materials.append(mats["foam"])
    obj.data.materials.append(mats["foam_shade"])
    k.smooth(obj, 60.0)
    return obj


def bubbles(mats):
    parts = []
    for n, (deg, y0, y1, count) in enumerate(BUBBLES):
        theta = math.radians(deg)
        for i in range(count):
            t = i / max(1, count - 1)
            y = y0 + (y1 - y0) * t
            size = 0.1 + 0.07 * t                       # growing as they rise
            wobble = 0.06 * math.sin(3.1 * i + n)
            c = point(theta + wobble, y, R_IN + 0.08)
            parts.append(k.ellipsoid(f"bubble{n}_{i}", tuple(c), (size, size, size), mats["bubble"], 6, 4))
    return parts


def catmull(points, steps=6):
    out = []
    pts = [Vector(p) for p in points]
    for i in range(len(pts) - 1):
        p0, p1, p2 = pts[max(i - 1, 0)], pts[i], pts[i + 1]
        p3 = pts[min(i + 2, len(pts) - 1)]
        for s in range(steps):
            t = s / steps
            out.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t +
                              (-p0 + 3 * p1 - 3 * p2 + p3) * t * t * t))
    out.append(pts[-1])
    return out


def handle(mats):
    """The handle: a round glass bar along HANDLE, flaring at both ends."""
    path = catmull([(x, y, AXIS_Z) for x, y in HANDLE], 4)
    n = len(path)
    segments = 14
    bm = bmesh.new()
    rings = []
    for i, p in enumerate(path):
        t = (path[min(i + 1, n - 1)] - path[max(i - 1, 0)]).normalized()
        up = Vector((0.0, 0.0, 1.0))
        side = t.cross(up).normalized()
        # Flaring towards the ends (the first and last 18 % of the bar).
        u = i / (n - 1)
        end = min(u, 1.0 - u)
        r = HANDLE_R + (HANDLE_FLARE - HANDLE_R) * (1.0 - smoothstep(0.0, 0.18, end))
        rings.append([bm.verts.new(p + side * r * math.cos(2 * math.pi * j / segments) +
                                   up * r * math.sin(2 * math.pi * j / segments)) for j in range(segments)])
    for i in range(n - 1):
        for j in range(segments):
            jj = (j + 1) % segments
            bm.faces.new((rings[i][j], rings[i][jj], rings[i + 1][jj], rings[i + 1][j]))
    for ring in (rings[0], rings[-1]):
        bm.faces.new(ring)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.faces.ensure_lookup_table()
    bm.faces.sort(key=lambda f: f.calc_center_median().z)
    bm.faces.index_update()
    obj = kit.from_bmesh("handle", bm, mats["handle"])
    k.smooth(obj, 60.0)
    return obj


def check(opts, parts):
    """The silhouette against the sprite (its shadow left out), the glass counted as solid (the coverage reads the
    render's alpha, which see-through glass would lower)."""
    if "check" not in opts:
        return
    alphas = [(m, m.node_tree.nodes["Principled BSDF"].inputs["Alpha"]) for m in bpy.data.materials
              if m.node_tree is not None and "Principled BSDF" in m.node_tree.nodes]
    saved = [(socket, socket.default_value) for _, socket in alphas]
    for socket, _ in saved:
        socket.default_value = 1.0
    kit.check(opts, "%s (coins %d)" % (NAME, SPRITE), parts, SPRITE, True, SHADOW)
    for socket, value in saved:
        socket.default_value = value


def build():
    opts = kit.options()
    k.reset()
    mats = materials()
    # Opaque parts first, the see-through ones last (the handle, then the body's glass).
    parts = [beer(mats), foam(mats)] + bubbles(mats)
    parts += [handle(mats), skin(mats)]
    bpy.context.view_layer.update()
    check(opts, parts)
    kit.finish({key: value for key, value in opts.items() if key != "check"}, NAME, parts, SPRITE, large=True,
               distance=0.8)


if __name__ == "__main__":
    build()
