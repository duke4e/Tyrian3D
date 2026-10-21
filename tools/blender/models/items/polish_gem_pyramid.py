"""The pyramid gems, polished (2026-10-20; they replace wave2_e.py's gem_pyramid() and wave3_ai_items.py's
gem_pyramid_purple(), a flat pyramid with a square table):

- gem_pyramid: the small red gem worth 50 credits (coins 76, 1x1: an 11 x 11 diamond in the 12 x 14 cell; in
  the sky of GEM WAR, MARKERS, MISTAKES, SURFACE and CORE, dropped in IXMUCANE, SAWBLADES, CORE and SAVARA).
- gem_pyramid_purple: the violet one worth 2000 or 100 credits (coins 57; dropped in MISTAKES, in the sky of
  CORE and LAVA EXIT). Coins 57 is coins 76 shade for shade in ramp 5 instead of ramp 4 (their palette
  indices differ only by the ramp, but for one stray dark pixel left of the middle row: 0xd0 and 0xe0, both
  near black): the same cut, written once in each ramp. (One model with models.cfg's color=sprite could serve
  both, but its emission would not follow the sprite's colour: the glow would stay red.)
- gem_pyramid_teal: the teal shard that ICE EXIT's blue crystals (7 53) launch, falling (coins 133, enemy 507 of
  episode 4; added 2026-10-21): coins 76 shade for shade in ramp 13 (one stray dark pixel in ramp 6).
models.cfg: sprite coins 76 gem_pyramid spin=1.5 glow=12:0.25, sprite coins 57 gem_pyramid_purple spin=1.5
glow=12:0.25, sprite coins 133 gem_pyramid_teal spin=1.5 glow=12:0.25.

As the sprite and its 4x upscale draw it: a diamond (rows 2-12, columns 1-11), a square pyramid seen from
above with its corners up, down and to the sides, lit from its middle: a star glint (the brightest pixel,
shade 13, at row 7, column 6, the bright cross of its ridges running out along row 7 and column 6 to the
corners, shades 10 to 4), dark red facets between the arms (shades 2-7, lighter towards the middle and in
the upper half), a dark rim.

Built as a cutter cuts a pyramid gem: the girdle a square turned 45 degrees (the sprite's diamond), a thin
dark band; the crown above it a square pyramid in two tiers (a steeper bezel and the upper facets), its four
ridges ground off into narrow facets (the star's arms, glowing, brighter on the upper tier) meeting at a
small table at the top (the star's middle, glowing most); the pavilion below a shallower pyramid in two
tiers to a point, its ridges ground off too. Every cross-section is the same chamfered square scaled, so
every facet is a plane; flat shading. All the palette shades of the sprite's ramp, each glowing in its own
colour (the lighter, the more): the game's slanted camera sees much of the gem's shaded side, and the item
turns (spin) so its facets catch the game's sun in turn.

Origin at the sprite's centre (pixel 6, 7); +Y up the screen, +Z towards the camera (the game centres sky
models in height); the gem's middle at (0.5, -0.5) (row 7, column 6), the girdle's half-diagonal GIRDLE.

Replaces wave2_e.py's gem_pyramid() and wave3_ai_items.py's gem_pyramid_purple(): remove them (and their
docstring lines) so that they don't overwrite these models.

Options after "--": --outdir <dir> (default assets/models/items), --check <sheets dir> (each model's
silhouette against its sprite in coins.png), --preview <prefix>, --only <name,...>.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "enemies"))
import tyrkit as k  # noqa: E402
from polish_balls import preview  # noqa: E402

CX, CY = 0.5, -0.5
GIRDLE = 6.3         # the girdle's half-diagonal (a little outside the middles of the sprite's steps: its edge pixels)
RIDGE = 0.06         # each ridge's narrow facet, as a fraction of the gem's edge on each side

# The gem from the culet (a point) up to the table: its cross-sections (height z, half-diagonal) and the band
# of facets above each; the last is the table's edge.
CULET_Z = -3.5
RINGS = [(-1.8, 3.7, "pavilion_high"), (-0.35, GIRDLE, "girdle"), (0.35, GIRDLE, "crown_low"),
         (2.0, 4.15, "crown_high"), (4.05, 0.58, None)]
FIRST_BAND = "pavilion_low"   # the culet up to the first ring

# Palette shades (0-15 of the ramp) and how strongly each glows in its own colour, by part.
SHADES = {
    "table": (13, 1.3),
    "ridge_high": (11, 0.8), "ridge_low": (8, 0.45),
    "crown_high": (8, 0.35), "crown_low": (6, 0.28),
    "girdle": (4, 0.15),
    "pavilion_ridge": (7, 0.3), "pavilion": (5, 0.22),
}
# The models: (name, sprite in coins.png, ramp).
MODELS = [("gem_pyramid", 76, 4), ("gem_pyramid_purple", 57, 5), ("gem_pyramid_teal", 133, 13)]


def materials(name, ramp):
    pal = k.level_palette()
    out = {}
    for part, (shade, glow) in SHADES.items():
        index = 16 * ramp + shade
        out[part] = k.material(f"{name}_{part}", palette=index, metallic=0.15,
                               roughness=0.12 if part in ("table", "ridge_high", "ridge_low") else 0.16,
                               emission=pal[index], emission_strength=glow)
    return out


def section(a, z):
    """A cross-section: the square turned 45 degrees (corners east, north, west and south at half-diagonal a),
    each corner cut by a ridge's narrow facet: 8 points counter-clockwise from above, a corner's two in a
    row (east first)."""
    corners = [Vector((a, 0)), Vector((0, a)), Vector((-a, 0)), Vector((0, -a))]
    t = RIDGE * a * math.sqrt(2)
    out = []
    for i, c in enumerate(corners):
        prev, nxt = corners[i - 1], corners[(i + 1) % 4]
        for p in (c + (prev - c).normalized() * t, c + (nxt - c).normalized() * t):
            out.append(Vector((CX + p.x, CY + p.y, z)))
    return out


def part_of(band, s):
    """The part a face of a band is: sector s spans points s and s + 1 (even: a corner's ridge facet)."""
    ridge = s % 2 == 0
    if band == "girdle":
        return "girdle"
    if band.startswith("pavilion"):
        return "pavilion_ridge" if ridge else "pavilion"
    return ("ridge_high" if band == "crown_high" else "ridge_low") if ridge else band


def gem(name, m):
    rings = [section(a, z) for z, a, _ in RINGS]
    n = 8
    verts = [v for r in rings for v in r]
    culet = len(verts)
    verts.append(Vector((CX, CY, CULET_Z)))
    faces, parts = [], []

    def idx(r, s):
        return r * n + s % n

    for s in range(n):
        faces.append((culet, idx(0, s + 1), idx(0, s)))
        parts.append(part_of(FIRST_BAND, s))
    for r in range(len(rings) - 1):
        for s in range(n):
            faces.append((idx(r, s), idx(r, s + 1), idx(r + 1, s + 1), idx(r + 1, s)))
            parts.append(part_of(RINGS[r][2], s))
    faces.append(tuple(idx(len(rings) - 1, s) for s in range(n)))
    parts.append("table")
    obj = k.mesh_object(name, verts, faces)
    used = [p for p in SHADES if p in parts]
    for p in used:
        obj.data.materials.append(m[p])
    for poly, p in zip(obj.data.polygons, parts):
        poly.material_index = used.index(p)
        poly.use_smooth = False
    k.recalc_normals(obj)
    return obj


def build():
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "items"))
    only = set(options["only"].split(",")) if "only" in options else None
    for name, sprite, ramp in MODELS:
        if only is not None and name not in only:
            continue
        k.reset()
        obj = gem(name, materials(name, ramp))
        tris = sum(len(p.vertices) - 2 for p in obj.data.polygons)
        used = sorted(mat.name for mat in obj.data.materials)
        print("== %s (coins %d): %d triangles, %d materials: %s" % (name, sprite, tris, len(used), ", ".join(used)))
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        path = os.path.join(outdir, name + ".glb")
        k.export(path)
        print("%s: %d bytes" % (path, os.path.getsize(path)))
        if "check" in options:
            k.check_silhouette(os.path.join(options["check"], "coins.png"), sprite, large=False)
        if "preview" in options:
            preview(options["preview"] + name, size=(12, 14), distance=0.45)


if __name__ == "__main__":
    build()
