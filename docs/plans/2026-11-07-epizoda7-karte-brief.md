# Episode 7 maps: the user's hand check (2026-11-07)

The user reviewed every episode 7 level's GBC map beside the PC map made from it (the check page,
https://claude.ai/artifact/XeH3FhXSYNQpAaMBQRGQZF, db collection `checks`, docs `m7-<slug>`; the atlas
https://claude.ai/artifact/Jpv4F9FzLYE17v2VEZTqVN shows the maps, 3D screens and enemies). Their overall ask: the
PC maps should follow the GBC maps 1:1 in layout, without abrupt transitions or seams, in the right theme/tileset,
keeping the GBC's paths, structures (rock arches, pyramids, buildings) and the turrets drawn into the GBC maps.

## Notes per level (the user's words, translated)

| Stage | Level | Note |
|---|---|---|
| 01 | TYRIAN | Shape is good, but abrupt transitions, mostly at the grass edge. |
| 02 | ASTEROID | Paths don't match the original's paths; some turrets became red lines. |
| 03 | SPACE | OK. |
| 04 | SAVARA | Abrupt transitions; it should be earth, not concrete. |
| 05 | SAVARA II | Abrupt transitions, some islands missing, shapes not followed 100%, some turrets missing. |
| 06 | OASIS | The rock arches are missing. |
| 07 | DESERT | Abrupt transitions, map not 1:1, rock arches and pyramids missing, some tiles wrongly taken as rocks. |
| 08 | JUNGLE | Rocks totally wrong; the layout doesn't follow the map 1:1. |
| 09 | JUNGLE II | Same as JUNGLE; the paths are missing. |
| 10 | ASTEROID2 | Paths and geometry wrong, not 1:1, abrupt breaks. |
| 11 | WARP | No background at all (at least on the screenshot); follow the clusters of circles 1:1. |
| 12 | BUBBLES | Follow the clusters of circles 1:1. |
| 13 | CAMANIS | Paths wrong; abrupt breaks at the edges. |
| 14 | ICE EXIT | No paths at all; abrupt breaks at the edges; some buildings missing. |
| 15 | AST.BONUS | Abrupt breaks, not 1:1, turrets missing. |
| 16 | SPACE ATK | OK. |
| 17 | FLEET | All structures laid out wrong, like a heap of random tiles; use the ready structures of the PC FLEET level. |
| 18 | DELIANI | Wrong tileset: take the PC DELIANI level's, and follow the level's structures much better. |
| 19 | TUNNEL | OK. |
| 20 | DELICORE | Wrong tileset, the level's structure not followed, buildings and turrets missing. |
| 21 | DELI CORE | Same as DELICORE. |
| 22 | LAVA I | OK. |
| 23 | LAVA II | A few tiles still to join so that the lava river is followed better; the rest OK. |
| 24 | FINALE | OK. |

## Where things are

- Map making: `tools/gbc/episode.py` (`make_level`, `autotile`, `plan_targets`, the LEVELS specs: `pc`, `maps`,
  `pool`, `fills`, `rare`, `exclude`, `as_they_are`, `match`), GBC maps in `data/gbc/levels/Lnn_*/map.png` and
  `map.json`; TYRIAN3D.md's episode 7 section describes the autotile (quarters, candidates, pair costs, rare pairs).
- The committed levels (`data/gbc/episode7/levels/*.json`) are episode.py's output worked over since (enemy
  overrides, retype.py, reboss.py, boss LOOK events by hand): remaking a level's events loses that work. To change a
  map, run `episode.make_level(spec)` from a driver and splice only `maps` (and for upper layers `upper` and event 2's
  `d2`/`d3`) into the committed JSON (memory note ep7-regeneration).
- Terrain after map changes: `TYR3D_GAME_DIR=build/dev python tools/content/gbc/terrain.py "<LEVEL>"`; it re-carries
  `tools/terrain/levels.json` and drops hand-set values (TUNNEL bg3 `slivers` 21, DESERT `#715d47` 0): diff it,
  restore them, and rebuild with `tools/terrain/make_terrain.py build <hashes>`.
- PC map renders: the game's map export (`export/maps/map_<hash>_N.png`, 14 columns plus 16 side columns each side,
  300 rows; the level uses the bottom `pc_rows`).
- Review the same way as the hand check: a page with the GBC map beside the new PC map, the user's marks in its db.

## Rules (CLAUDE.md)

Commit and push each done-and-checked step without asking (stage only its files, never the `external/btbh-renderer`
pointer); after each, build `build/game` (RelWithDebInfo) unless its `tyrian3d.exe` runs; work and test in
`build/dev`; fly each changed level to its end (`fly.sh`-style autopilot runs) before committing.

## Why the maps come out so (episode.py's autotile)

Each quarter of a PC tile gets a *material* from the GBC map's colours (k-means of the original tileset's main
colours) and the map is the PC tiles whose quarters and neighbour pairs fit those materials best. That loses what is
not a colour: paths and rock outlines become blobs of material (layout not 1:1), two materials meet where no PC tile
joins them (abrupt transitions, seams), drawn structures (rock arches, pyramids, buildings, the turrets painted into
the GBC maps) dissolve into materials (or become stray lines), and the tileset is the original PC level's (the DELIs'
and SAVARA's look wrong).

## Possible ways (to choose with the user)

1. Keep the autotile, fix by kind: the right tileset per level (DELIANI's for the three DELIs, SAVARA's earth), path
   and edge materials of their own, transitions only through tiles the originals use between two materials, and the
   structures placed whole (the original levels' tile groups or ground enemies for arches, pyramids, buildings,
   turrets) where they stand in the GBC map. Smaller steps, each level reviewed.
2. A tile dictionary: each GBC metatile (16 px) mapped to a PC tile (or a small group) per level, proposed by
   matching and fixed by the user on a page, then the PC map laid tile for tile after the GBC map (1:1 by
   construction). The GBC's 16 px rows are the PC's 28 px tiles made 1.5x as 24: the vertical scale differs from the
   tiles', which the events' timing (clock = 1.5 x GBC position) depends on, so rows need patterns or the timing a
   rescale.
