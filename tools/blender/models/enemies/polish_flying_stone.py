"""The small stones flying at the player in ASSASSIN, IXMUCANE and SAWBLADES (sheet R sprites 171 and 190, 1x1: 12 x 14
pixels; sky layer; enemies 660 and 661 of episodes 1 and 3, the levels' random enemies (levelEnemy, event 14 turns
them on); one frame each, not animated), polished (2026-10-22, round 36; they replace wave3_af.py's faceted_rock()
models, lumps whose facets were painted from the sprite and which stood as deep below their middle as above it).
models.cfg: sprite r 171 flying_stone_a yaw=0 spin=3, sprite r 190 flying_stone_b yaw=0 spin=3 (the lines as they are:
they turn slowly as they fly).

Neither is another sprite's pixels mirrored, turned or in other ramps (no twin on any sheet); they are two different
stones.

As the sprites and their 4x upscales draw them, lit from the upper left:
- R 171 (flying_stone_a): an angular lump of brown-grey rock (ramp 10, a2-ab), 9 x 11 pixels (rows 1-11, columns 1-9),
  rounded, its broad lit facet at the upper left (aa at column 3 of rows 3-4), its top a little right of the middle
  (ab at column 5 of row 6), falling away dark to the right and to the bottom (a2-a3), a hairline crease down from its
  top edge to the middle; a rusty red streak along its upper left edge (42 43 42 at (3, 1), (2, 2), (1, 3)).
- R 190 (flying_stone_b): a longer tan pebble (ramp 1, 13-1b) lying on the diagonal from the upper right (row 2,
  columns 6-8) to the lower left (row 12, columns 3-5), lit along its middle in two broad facets (1b at columns 6-7
  of rows 4-5, and at column 4 of row 8 and column 6 of row 9), a crease across its upper half from its right edge
  (the dark b2-b3 at column 10 of rows 6-7), its ends darker.

Built as the polished pebbles of the asteroid levels are (polish_pebbles.py and its machinery, polish_asteroids.py):
each stone one convex block, its footprint's walls rising steeply, its top facets lit as the sprite's are (roof planes
leaning towards the light where the sprite is lit), a rounded cap of large facets and a few chips off it, the creases
cut in as narrow V-shaped grooves of darker stone, the faces the game's camera sees retriangulated evenly and moved a
little by smooth noise (weathered stone, its facets' edges kept sharp). Flat underneath, 3.8 and 4.7 pixels high
(the game centres sky enemies in height; spinning about the vertical, the camera never sees their bellies). Colours
are the sprites' own palette indices: flying_stone_a 0xa6, its crease 0xa3, the rusty streak 0x43 painted on the
faces along its upper left edge; flying_stone_b 0x18, its hairline creases 0x16. A little sheen, as the pebbles; no
glow.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; origin at the
sprite's centre (pixel 6, 7): column c's left edge is x = c - 6, row r's top edge y = 7 - r. The specs give pixel
corners (column, row) of the 12 x 14 sprite (polish_pebbles.P() moves them into polish_asteroids' picture).

Replaces wave3_af.py (all of it: flying_stone() and the two @model registrations flying_stone_a(), flying_stone_b();
delete it) and wave3_af_art.py's PEBBLE_A and PEBBLE_B, which only wave3_af.py reads.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each stone's silhouette
against enemy_R.png), --preview <prefix> (each stone's top and 3/4 views), --only <name,...>.
"""
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_asteroids as pa  # noqa: E402
import polish_pebbles as pp  # noqa: E402  (its build() runs only as a script)
from polish_pebbles import crack, block  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402

# The walls (inset, height): steep from the ground, curving in towards the cap (the pebbles' a little lower: the
# stones are smaller).
OUTER = [(0.0, 0.0), (0.3, 1.6), (0.8, 3.0), (1.5, 4.1), (2.4, 5.0)]
INNER = [(0.0, 0.0), (0.1, 2.0), (0.3, 3.8), (0.7, 5.0), (1.3, 5.6)]


def spec(name, sprite, blocks, cracks, hairlines, crack_shade, hairline_shade):
    return {"prefix": name, "sprite": sprite, "blocks": blocks, "cracks": cracks, "hairlines": list(hairlines),
            "outer": OUTER, "inner": INNER, "crack_shade": crack_shade, "hairline_shade": hairline_shade,
            "bowls": []}


# --- R 171: flying_stone_a ------------------------------------------------------------------------------------------
# The outline (rows 1-11: row 1 columns 3-4, rows 5-6 columns 1-9, row 11 columns 3-7), its steps cut through their
# middles. One lump: the broad lit facet at the upper left, the top right of the middle, facets falling to the right
# and to the bottom; a hairline crease from the top edge (column 6) to the middle.

STONE_A = spec("flying_stone_a", 171, [
    block("lump", [(3.2, 1.0), (5.0, 1.0), (6.2, 2.0), (8.0, 3.0), (9.2, 4.0), (10.0, 5.0), (10.0, 7.2), (9.4, 8.2),
                   (9.0, 10.2), (8.2, 11.4), (7.0, 12.0), (4.0, 12.0), (2.8, 11.2), (2.0, 10.0), (1.6, 8.0),
                   (1.0, 6.8), (1.0, 3.4), (2.0, 2.2)],
          [(5.6, 6.4, 5.1, 0.0, 0.0), (3.0, 3.8, 4.7, -0.38, 0.3), (8.4, 6.2, 4.4, 0.45, 0.05),
           (5.4, 10.2, 4.3, 0.05, -0.42)],
          0xa6, (5.5, 6.6, 6.2, 7.0, 9.6, -3.9, 22), seed=5),
], {}, [crack([(6.2, 2.2), (5.6, 3.8), (4.8, 5.6)], 0.42, 0.45)], 0xa3, 0xa3)

# The rusty streak along the upper left edge: the sprite's pixels (3, 1), (2, 2), (1, 3) (their middles).
RUST = [(3.5, 1.5), (2.5, 2.5), (1.5, 3.5)]

# --- R 190: flying_stone_b ------------------------------------------------------------------------------------------
# Lying on the diagonal (row 2 columns 6-8 down to row 12 columns 3-5): one lump along it, a lit facet on its upper
# half and a second on its lower half, the right side falling dark, both ends lower; a crease across its upper half
# in from its right edge (row 6.6) and a hairline on to the lower left of the middle.

STONE_B = spec("flying_stone_b", 190, [
    block("lump", [(6.2, 2.0), (8.8, 2.0), (9.8, 2.8), (10.6, 3.6), (11.0, 4.6), (11.0, 7.6), (10.4, 8.4),
                   (10.0, 9.2), (9.4, 10.0), (8.6, 10.8), (7.0, 11.4), (6.0, 12.4), (5.2, 13.0), (3.8, 13.0),
                   (2.6, 12.2), (2.0, 11.2), (2.0, 9.4), (2.6, 8.6), (3.0, 7.4), (3.0, 6.2), (3.6, 5.4),
                   (4.2, 4.6), (4.8, 3.4), (5.4, 2.6)],
          [(6.6, 7.2, 4.8, 0.0, 0.0), (6.8, 4.4, 4.6, -0.16, 0.22), (4.4, 9.2, 4.5, -0.3, 0.04),
           (9.6, 7.4, 4.0, 0.46, -0.12), (3.8, 12.0, 3.7, -0.18, -0.46), (8.6, 2.6, 3.8, 0.24, 0.46)],
          0x18, (6.6, 7.4, 5.6, 7.4, 9.0, -3.8, 24), chips=3, seed=9),
], {}, [crack([(11.0, 6.4), (9.4, 6.8), (7.6, 7.4)], 0.5, 0.55, ends=("out", "in")),
        crack([(5.6, 9.8), (4.4, 10.6), (3.6, 11.0)], 0.38, 0.4)], 0x15, 0x16)

SPECS = {"flying_stone_a": STONE_A, "flying_stone_b": STONE_B}


def paint_rust(rock, mat):
    """The faces along the upper left edge of flying_stone_a where the sprite draws its rusty streak (within 1.1
    pixels of the line through its pixels, facing up or out), in rust."""
    slot = mk.slot_of(rock, mat)
    pts = [Vector((c - 6.0, 7.0 - r)) for c, r in RUST]
    mesh = rock.data
    for poly in mesh.polygons:
        if poly.normal.z < -0.2 or poly.center.z < 0.25:
            continue
        p = Vector((poly.center.x, poly.center.y))
        best = 99.0
        for a, b in zip(pts, pts[1:]):
            ab = b - a
            t = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared))
            best = min(best, (p - (a + ab * t)).length)
        # Beyond the line's ends a little: the streak runs out along the rim.
        if best < 1.1:
            poly.material_index = slot


def build_one(s, options):
    k.reset()
    pa.REACH = pp.REACH
    rock, _ = pa.build_rock(s)
    pp.finish_materials(rock)
    if s["prefix"] == "flying_stone_a":
        rust = k.material("flying_stone_a_rust", palette=0x43, metallic=pp.METALLIC, roughness=pp.ROUGHNESS)
        paint_rust(rock, rust)
    parts = triangulate([rock])
    bpy.context.view_layer.update()
    name = s["prefix"]
    if "check" in options:
        sheet = os.path.join(options["check"], "enemy_R.png")
        mk.compare("%s (R %d)" % (name, s["sprite"]), mk.coverage(parts, 12, 14),
                   k.sprite_mask(sheet, s["sprite"], large=False))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mk.report(name, parts, os.path.join(mk.outdir(options), name + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + name, parts, size=(12, 14), scale=24, distance=0.45)


def build():
    options = k.args()
    only = options["only"].split(",") if "only" in options else list(SPECS)
    for name in only:
        build_one(SPECS[name], options)


if __name__ == "__main__":
    build()
