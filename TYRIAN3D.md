# Tyrian3D

A 2.5D/3D port of [OpenTyrian2000](https://github.com/KScl/opentyrian2000). The original game
logic runs unchanged. Only the presentation changes: the playfield is drawn under a tilted
perspective camera, and selected sprites are replaced by 3D models.

Rendering uses the BTBH renderer (`external/btbh-renderer`, branch `tyrian3d`), which runs on
SDL3's SDL_GPU: Metal on macOS, Vulkan on Windows and Linux.

## Build (macOS)

```bash
brew install sdl3 assimp cmake
git submodule update --init external/btbh-renderer
```

Shaders are compiled with SDL_shadercross, which is built once from the renderer's submodule:

```bash
cmake -S external/btbh-renderer/external/SDL_shadercross -B build/shadercross -DCMAKE_BUILD_TYPE=Release -DSDLSHADERCROSS_DXC=ON -DSDLSHADERCROSS_VENDORED=ON -DSDLSHADERCROSS_SHARED=OFF -DSDLSHADERCROSS_STATIC=ON -DSDLSHADERCROSS_SPIRVCROSS_SHARED=OFF -DSDLSHADERCROSS_CLI=ON -DSDLSHADERCROSS_CLI_STATIC=OFF -DSDLSHADERCROSS_INSTALL=OFF -DSDLSHADERCROSS_TESTS=OFF -DSPIRV_SKIP_TESTS=ON
```

```bash
cmake --build build/shadercross --target shadercross -j
```

Then build the game:

```bash
cmake -S . -B build/game && cmake --build build/game -j
```

The game needs the freeware Tyrian 2000 data in `data/tyrian2000`
(https://www.camanis.net/tyrian/tyrian2000.zip).

```bash
build/game/tyrian3d
```

To make an app bundle (`build/package/Tyrian3D.app`, with its shaders, models, map sides and
libraries inside):

```bash
tools/package_macos.sh
```

The app looks for the game data in `~/Library/Application Support/Tyrian3D/data` or in a folder
named `data` beside the app (or `open Tyrian3D.app --args -t <folder>`). If it finds none, it asks
for the folder and remembers it (`~/Library/Application Support/Tyrian3D/data_dir.txt`).

## Controls

The original controls are unchanged. These are added:

| Key | Action |
| --- | --- |
| F3 | Switch between the 3D view and the original 2D view |
| F4 | Switch 3D appearances (models, volumetric sprites) on or off; off shows the flat sprites |
| F5 | Reload `assets/models/models.cfg` |
| Page Up / Page Down | Camera tilt |
| Home / End | Field of view |
| Insert / Delete | Height spread between layers |

The camera keys work only while the 3D view is on screen.

The setup menu has a **3D** page: the view (3D or the original 2D screen), objects (3D or flat
sprites), shadows, effects (explosion particles, glowing shots), a camera preset (Standard,
Steep, Overhead), the mouse, and the HUD: Modern (the playfield fills the window; in a 16:9 area
round it, so on ultrawide it stays near the action: shield, armor and power at the bottom right, the
guns' power and the sidekicks' ammunition at the top right, the score with the lives, super bombs
and special weapon (lit while it is ready) at the bottom left, the boss bar and the level timer at the top, all from the
game's state (the game's own drawing of them is left out), each fading to a third while the ship or
dense enemy fire is under it; the level's name as it starts, the game's messages in a pill at the
bottom, "game over" on a plate; under a menu the game shows over the level; two players have a
panel each at the bottom corners: the score, shield and armor, the gun each fires and its power,
player 2's sidekick level and charge (its pips over the ship too), lives and super bombs) or Classic
(the original panel beside the playfield). The **Graphics** page adds the menus:
Modern (the new UI over the 3D view, below) or Classic (the original screens), Screens: Fill (the
game's other 320x200 screens fill the window's height, in whole steps and then smoothly, over a
blurred, dimmed copy of themselves) or Integer (as Scaling Mode says, black bars), and the UI Scale
(75-150 %). They are kept in the `[tyrian3d]` section of `opentyrian.cfg`; F3 and F4
change the first two as well. In a level, Escape's options are Return to Game, **Graphics**, the two
volumes, the music (SoundFont or AdLib) and its SoundFont, the game speed, the mouse and Quit Level; Graphics is a page
of the 3D page's settings with the menus, screens, UI scale and the original's detail level, each
changed with Left/Right, Enter or a click and taking effect at once, with the modern menus at the
playfield's left and the 3D view bright beside them, so what each change does shows behind it
(`ingame_options_3d` in `mainint.c`; turning the view to 2D and back there shows the 3D view again).

**The modern UI** (Menus: Modern, the 3D view): the title screen, setup and its pages and pickers,
the new game's choices (players, episode, difficulty, timed battle), the store between levels and the
screens over a level, in dark glass panels with brass rims, in Oxanium, at any window size, in a 16:9
area (`src/ui.c`). The store: the ship as a large 3D model on a lit pad at the left (the weapon
simulator in its place for the weapons, the generator and the sidekicks, with the weapon's power,
its costs and the generator's output under it), the page at the right: the parts to upgrade as tabs,
their choices as cards with an icon, short stats against the best on offer, the cost or that the
ship has it, the credits and what is left after the change chosen, a note when a purchase is made;
ship specs round the ship; options, load and save, the keyboard, joystick and mouse, the next
level's map, the data cubes and their texts, and the store's questions (quit, save) as dialogs.
Lists scroll. Two players: both ships side by side, what each has under them (the ship, the score,
the gun and its power, lives, the input device). The Super Arcade and Super Tyrian: the mode, the
ship's name, its main and special weapons (the original's help boxes there). Over a level (the scene
blurred under the glass): the in-game options and their graphics
page, the help (F1), pause, the level's results, game over. And the other screens: the high scores
(the boards as tabs, medals, the difficulty played; the name of a new high score typed in a
question with its score), the story texts between levels (reflowed in Oxanium in a glass panel over
their picture, revealed as the original writes them; a warning's panel and the window's edges pulse
red; an episode's end shows its score and the hint), title cards (the next episode, the Super
Arcade's ship and the code to type), load game (the players' pages as tabs), the instructions (the
topics, the pages of help with their titles), the jukebox (the songs as a list, the one playing
large with its controls, the sound effects, over visuals that play with the music: V or the Look
button switches between the Orrery and the Warp, Space hides the panel), the credits rolling in a column, and the rogue run's
screens (its menu with the profile, the unlocks, the act's map with its nodes named and the next
ringed, the cards and the merchants as large cards with their tiers, the messages as cards). The
mouse works on the panels (hover, click, the wheel moves through the items, the pages and the cards
and scrolls a data cube's text), the keys and the joystick as ever; when the joystick was used
last, the key hints show its pad and buttons. The store's next-level map is the UI's own (`ui.c` `shop_map`, from what `game_menu.c` publishes of
`JE_updateNavScreen`'s planets, routes and grid): deep space, a faint brass grid scrolling at half the planets' pace,
the routes' dots (the selected route lit as far as it has come), the planets drawn anew, a pulsing brass ring round the
selected destination and a faint one where the ship is. In the store one click chooses (the original's first
click only selects; `shop_one_click`), but a part's choices, where the first click tries one on the
ship ("BUY" over its cost) and the next buys it, the volumes, the map's planets and the saved games;
a choice's card on Upgrade Ship opens its part with that choice tried. The pointer is a smooth one sized in window points.
The original screens stay for Menus: Classic and the 2D view.

**Playfield** (3D page and the in-game 3D options, from the next level): **Wide** (the default in
3D) plays in all the 3D view shows: the whole width the game draws (game x 0-319 instead of
24-287, the maps held still instead of the horizontal parallax, so the maps' edge columns and
what stands on them can be played) and 64 pixels above the screen, where enemies are made ahead of
their time (as far up as they fly down meanwhile, so from where the original makes them on they
fly as there; those that don't come down start at the playfield's top). The 2D view then shows
the 264 pixels round the ship. **Original** is the game 1:1 (`l3d_field_wide`, `TYR3D_PLAYFIELD`).
What lies outside the playfield shows darkened, dimmed enemies coming or leaving included.

## Debug flight

Setup → **Debug Flight...** lists every level of the episodes; Enter flies it from its start (the
following levels follow, shops skipped) without losing lives. A line at the top shows the level,
its time and tick, and the speed. While flying:

| Key | Action |
|---|---|
| `-` / `=` | Slower / faster (1/4×, 1/2×, 1×, 2×, 4×, 8×) |
| Backspace | Back 5 seconds (the level restarts and the input so far is played back, quickly and unseen) |
| `` ` `` | Pause / resume (the camera keys work while paused) |
| `.` | One tick on, while paused |
| F12 | Snapshot to `export/feedback/<LEVEL>_e<episode>s<section>_t<tick>_<time>.png` |
| `[` / `]` | Front weapon: the previous / next weapon port (the new ones too) |
| `9` / `0` | Rear weapon: the previous / next weapon port |
| `;` / `'` | Both weapons' power down / up (1-11) |
| `7` / `8` | The next left / right sidekick |

A loadout change also changes the level's start, so a rewind keeps it.

The tick in a snapshot's name finds the moment again: `TYR3D_START=<episode>:<section> TYR3D_DEBUG=1
TYR3D_DEBUG_SEEK=<tick>` starts a debug flight there.

## New content

New items live in the item data's free slots, so the original ones stay as they are: weapons
819-999, weapon ports 48-60, sidekicks 33-37, specials 49-54. `assets/content/items.cfg` lists them
(the format is in `src/content.h`); the game reads it each time it loads the item data
(`content_apply` at the end of `JE_loadItemDat`). `tools/content/make_items.py` writes the file by
rules from the original data (`tools/content/tyrdata.py` reads it), so the rules change, not the file.

| Port / sidekick | Made from | Its 11 levels |
|---|---|---|
| 48 Phoenix Cannon | the Phoenix Device's fireballs | 1-3 fireballs in a fan; a hit bursts into a small blast, then an eight-way burst, at 10-11 the Phoenix's own fireworks |
| 49 Wobble Cannon | the Wobbley's blobs | pairs weaving side to side, 1-3 pairs, damage 1-4 |
| 50 Micro-Missile Swarm | the Mini-Missile | 1-5 tubes, 1-3 missiles a trigger, faster |
| 51 Zica Flamer | the Zica Flamethrower | flames passing through enemies, reaching further, burning harder |
| 52 8-Way Burst (rear) | the 8-Way MicroBomb | bombs in 2-8 directions |
| 53 Mine Layer (rear) | the Post-It Mine | sticky mines drifting slowly ahead, more often, in pairs from 7 |
| 33 Laser Option | Laser power 6 | gun pod |
| 34 Sonic Option | Sonic Wave power 5 | twin pods |
| 35 Lightning Option | Lightning Cannon power 5 | rotary pod |
| 36 Banana Option | Banana Blast power 5 | gun pod |
| 37 Guided Option | Guided Bombs power 4 | orbiting satellite |

No shop sells them yet (that comes with the new episode and the rogue mode); the debug flight's
loadout keys and `TYR3D_WEAPONS` / `TYR3D_SIDEKICKS` fly them.

## Rogue mode

Start New Game → **Rogue Run**. A run is three acts of the episodes' own levels (episodes 1, 2-3
and 4-5), each a map with branches: two or three nodes a row, three rows, then a boss. After every
level you take one of three cards: a weapon (front or rear, its power kept), a power level, a
sidekick, a shield or generator (better ones only), a ship, a special weapon, an extra life or
credits; cards are common, rare or epic, rarer later in the run and after harder levels. Elite
nodes fly a level one difficulty higher for a bounty and better cards; merchants sell cards for
credits; the acts are Normal, Hard and Impossible. Dying without an extra life ends the run (an
extra life flies the level again, as it began). Purple orbs are experience in a run (in the full game they slowly power the front gun up). They drop
as in arcade mode: the arcade's drops (event 45 marks enemy groups to leave one when they die) all
leave an orb in a run, its weapons and items being the cards. Every experience level (10, 15,
20... orbs) is an extra card after the level; the HUD shows it as XP. Orbs, the XP bar and the
sidekicks' ammunition are Tyrian purple (#66023c). Runs
earn cores (one a level, two more a boss,
three for winning), which buy unlocks between runs: the new weapons and sidekicks, special weapons,
ships no shop sells, more credits, an extra life or a warmer gun at the start, a fourth card.

The acts, their levels, the items and the unlocks are `assets/content/rogue.cfg` (written by
`tools/content/make_rogue.py` from the game's data; format in `src/rogue.h`). The profile (cores,
unlocks, runs) is `tyrian3d_rogue.cfg` beside `opentyrian.cfg`. A run skips the episode scripts'
shops, story texts and pictures, and never writes the player's save slots.

## Twin-stick

Start New Game → **1 Player Twin-Stick**: one player alone with the two players' linked ship (in a
two-player game the ships join into one when they meet: player 1 flies it, player 2 turns and fires
the Dragonwing's gun). It is a two-player arcade game (the Silver Ship with the Dragonwing behind it,
power-ups instead of the shop, the two-player Game Menu between levels) whose two players are one:

* **Keyboard and mouse**: the arrows (or WASD, unless the keys are bound to something else) fly the
  ship; the mouse aims the turret, which turns to the pointer (a brass crosshair, with a line across
  and one down the playfield through it, fading to its edges, to find it in a busy screen: drawn by
  the 3D view, `aim_line_quads` in `render_gpu.c`; the ship doesn't follow the mouse, whatever the
  mouse setting); the left button, or the fire key, fires the front
  gun and the turret together; the other buttons and keys do what the settings say (the sidekicks,
  super bombs, the rear gun's mode).
* **Controller**: the left stick (or the pad) flies, the right stick aims (let go, the turret keeps
  its way), the right trigger or the fire button fires both guns, the left trigger fires the
  sidekicks. The sticks are read through SDL's gamepad API, so any controller SDL knows as a gamepad
  has them; the buttons are the joystick settings' as ever.
* Whichever was moved last aims: the mouse or the right stick.
* The ship and the turret are always linked (the sidekick buttons don't part them); the turret is
  never hit on its own (only the ship's hits count), armor pick-ups go whole to the ship, and the
  turret goes and comes back with the ship: its lives are the ship's (the front gun's
  power, as in arcade play); the rear power-ups power the turret, the sidekicks are the turret's, as
  player 2's are. The difficulty is as chosen (two players' is a step harder).
* The modern HUD is one player's: the score (both guns' together), lives, super bombs and special
  weapon at the bottom left, shield and armor at the bottom right, the front gun, the turret, its
  charge (the two players' charge gun, which the turret fires) and the sidekicks' ammunition at the
  top right. The store's Game Menu shows the ship and the turret side by side with the score and
  each one's gun, and Fly and Aim in place of the two players' input devices. Pick-up messages are
  one player's. The classic HUD keeps the original's two-player panel.
* A twin-stick game is saved as a two-player game whose input devices are both "any" (0), which is
  how a save, and the arcade's continue after game over, know it again (`twinStickMode`,
  `twin_stick()` in `player.h`; `JE_playerMovement` in `mainint.c`).

## Episode 6

Episode 6, "The Grey Books" (plan: `docs/plans/2026-10-09-epizoda-6.md`), is written in the game's
own formats by `tools/content/episode6/build.py` into `assets/content/episode6` (`tyrian6.lvl`,
`levels6.dat`, `cubetxt6.dat`), at build time when the game's data is there: it is made from that
data, so it isn't in the repository. The game finds those files in the content directory
(`dir_fopen`), lists the episode in the episode menu and plays it like the others; a full game goes on to it after episode 5
(`last_episode()`).

Its levels are generated anew, the original levels only their inspiration
(`tools/content/episode6/generate.py`, run with a Python that has numpy and PIL): the maps from
the tiles of originals of the same look, by a plan of the level's design (`mapsynth.py`: each
tile follows its neighbours as the originals have them, row by row, nothing copied), the events
from the originals' waves placed anew along a difficulty curve, stationary ground enemies on tiles
that suit them, a boss at the end (`compose.py`, `waves.py`; the event rules in
`tools/content/EVENTS.md`, `tools/content/tyrevents.py` prints any level's events). The originals' gimmicks are mixed in per
level (`gimmicks` in the designs, `compose.py`): a boss of another level in the middle (the map
stops, its pattern loops until it is gone: events 2, 53, 54, 70), rushes (all layers faster),
ambushes from behind with their warning, dark stretches with the ship's spotlight and the screen
upside down (effects 6 and 9), a siege (the map stops, waves come round until the level timer,
67, runs out). Secrets: in most levels a courier crosses the top of the screen
fast; shot down, it leaves a data cube (shown in the next shop after the stage's own, `]+` and
`]?`), and in GREY MOON a warp orb to the secret bonus level VAULT (`$$`: dying costs nothing).
After THE CORE comes INVADERS, a Space Invaders mini-game in rounds (`minigames.py`) as ALE is
at the end of episode 1. MIGRATION and GRAVITRON are seen from the side (Tyrian3D event 200): the
game runs as ever, the 3D view is turned a quarter so the level scrolls from left to right (the
controls turned with it, every model on its side so craft show in profile, the shots as they
are), over open space with the stars in depth and rocks along the window's top and bottom edges
(`layer3d.c` `add_side_decor`); their playfield reaches 250 pixels further ahead (event 200's d3:
enemies are made there, shots and the ship go there), so it fills the window on its side. The
generated
levels (`levels/*.json`: our maps and events, and references to the original waves and bosses)
are in the repository; `build.py` expands them with the game's data at build time and brings the
enemies of episodes 1-3 they use into episode 6's item data (`enemydata.py`). Map pictures go to
`export/episode6`.

## Episode 7: Tyrian GBC

The levels of Tyrian 2000 for the Game Boy Color (World Tree Games, 2000; never sold, freeware since
2007) as an episode of the PC game, flown with its ships, weapons and enemies (plan:
`docs/plans/2026-10-25-gbc-epizoda.md`). It is made from the user's copy of the GBC ROM, so neither
the ROM nor anything taken from it is in the repository: the ROM goes to `data/gbc/Tyrian.gb`, and
the tools in `tools/gbc` (run with the tools' Python, which has numpy, scipy and PIL) read it:

* `extract.py` runs the ROM in the tools' own GBC emulator (`gbemu.c`, a shared library driven from
  Python by `gb.py`: CPU, MBC1, PPU, CGB banks and palettes, HDMA, logs of ROM reads, VRAM and sound
  register writes) through the menus into each of its 24 levels (the level dispatcher, bank 7
  `$4fea`, reads the level from `$d92f`), and writes each level's map (11 blocks of 16x16 a row,
  read upwards from the pointer the level's init routine sets at `$c449`), tiles, palettes, sprites
  and a gallery of what it shows to `data/gbc/levels`; `songs.py` and `apu.py` render its 25 songs
  (played by the ROM's own driver, ticked alone, `$1a5f`) to `data/gbc/music`; `report.py` writes
  the overview the user chose this episode from (`data/gbc/report/index.html`).
* `episode.py` makes each GBC level a PC level of the original level it is a version of (TYRIAN,
  ASTEROID1, SAVARA IV, TORM, STARGATE, CAMANIS, FLEET, BRAINIAC, LAVA EXIT...: the GBC artists drew
  their own, smaller tiles of the same looks, so the tiles are matched by material, not by pixels;
  its enemies are the PC sprites made small). The GBC map is scaled 1.5x (its 176 pixels are the 264
  the PC playfield shows) and cut into the PC tiles' quarters; each quarter's material (the tile
  set's main colours, the GBC lightness range moved to the tile set's, the GBC grain blurred) picks a
  tile with those quarters among the originals' ground tiles (not the objects standing on it), the
  common ones and pairs the originals have side by side more often. Space levels are the original's
  blank tile with the stars. The levels, in the GBC game's Full Game order (found by flying it
  through in the emulator) with its five Arcade-only levels after one of their look, go to
  `data/gbc/episode7` as episode 6's level JSON, with `preview/` pictures (the GBC map beside the
  PC one).
* `enemies.py` flies each GBC level in the emulator on Hard (so every enemy type shows; the ship kept
  alive and never firing, so every enemy lives out its path) and logs its script as it runs; for every spawn it draws the new enemy's
  sprites and gives each GBC enemy type the PC enemy whose sprite looks most like it (silhouette and
  shading against the PC atlases in `upscale/in`, 4-part enemies as 48x56 blocks, at the 1.5x scale;
  the enemies of the original level first; of a type's frames only those of about its main one's
  size and shape, as the frames can catch a neighbour), into `data/gbc/enemies` (`Lnn.json`, and
  `Lnn_matches.png`: each type beside its candidates). The PC enemies made of several are candidates
  too (`composites()`): the original levels spawn their parts together, each at its offset (the long
  rockets, the face with arms, the robots of four, the green bombers, the desert bunkers); a group of
  one enemy (a row of fighters) is not one, and a chain with a run of the same part (a rocket's
  body) also comes with that run of one and of two, as the GBC versions are shorter.
  `enemy_overrides.json` holds the corrections by eye (`"L23:29": [episode, enemy]`,
  `[episode, enemy, 4]` for an event 12 block, `[episode, [[enemy, dx, dy], ...]]` for a composite,
  or `null` to leave the type out; checked over all 24 levels on 2026-10-25); their sprite sheets are
  loaded before the other types' (after the boss's). `review.py` draws the sheets for that check:
  `Lnn_review.png` (one row per look of the level's types, most spawned first: the GBC sprite, the
  PC enemy the level uses, the six best candidates with the sheets each needs, green if loaded;
  composites' parts in `Lnn_review.txt`) and `Lnn_pool.png` (every enemy of the originals the level
  condenses).
* `script.py` turns a GBC script into PC events: the GBC game's script is a port of the PC event
  system with its own numbers (trigger positions in scrolled pixels; records of command, a, b, c,
  group): enemies (03/04, on Hard or Normal only 21-24, blocks 28+) become sky or ground spawns of
  their PC enemies (ground when the originals make that enemy on the ground) with a link per GBC
  group, the group speed (13) event 19, its zig-zag (14: every |c| frames the speed steps by 1,
  turning at the third byte, as the PC's) events 20 and 27, its acceleration (16) event 20, turn
  speeds (15) event 27, a group's new group (0b) event 39, the scroll (02) event 2, the difficulty
  skip (00) event 66. A GBC frame is 0.375 PC ticks and a speed unit 2 PC px a tick (a GBC pixel is
  1.5 PC pixels, its scroll of a pixel every 4 frames the PC's 1 px a tick); the GBC enemies move
  with the map, so sky ones get the scroll as fixedmovey. Backgrounds 2 and 3 (empty) scroll with
  layer 1 (at the usual 2x and 3x they run out of map at clock 8274 and 5516, which these levels
  pass). The GBC boss (whose script runs from RAM) is the original level's boss, or a related
  level's where the original has none, placed as episode 6 places them, with all its sprite sheets;
  an event 11 ends the level if the boss is never destroyed (as the originals have one near 8100;
  after the boss block's last event where that runs longer). What the GBC script does past its map's
  top (while its boss arena loops) is pressed into the time before the boss (at most clock 7000). Every GBC type is a PC enemy: the best candidate on the level's
  sheets (4-part ones as event 12 blocks, a composite's parts each spawned at its offset from the
  GBC enemy's top left, in its link; a GBC block record is the pieces of one big enemy, two columns
  one robot, so a type with a PC enemy of several parts makes it once). `episode.py` names the spawns it leaves out (types never seen
  in the flight, or with no candidate on the level's sheets).
* `story.py` flies the GBC Full Game through (each level ended at once) and logs the story texts
  (plain ASCII in the ROM: `/` a new line, `|` a new page) and the speaker names it reads, in order,
  into `data/gbc/story.json`: Transon's greeting and Trent's escape before the first shop, one text
  after each level (News, Javi, Reid, Vykromod, the captain...), the ending.
* `tools/content/gbc/build.py` (standard library; run by the build when `data/gbc/episode7` is
  there; when the item data has no free gun slot left for a brought-in enemy, its gun is episode
  5's of that number) makes the story the episode's data cubes (each shop holds what the GBC game tells after the
  level before it; the GBC capitals in sentence case, the names marked; the speaker's PC portrait:
  Transon, Reid, Vykromod, the captain, the news...) and the GBC ending its ending, expands the bosses (episode 6's `compose.expand`) and brings the enemies into the episode's
  item data (`enemydata.py`) and writes `assets/content/episode7`: `tyrian7.lvl`, `levels7.dat` (a shop before every level:
  the originals' shops of episodes 1-4 spread over the episode, the planet map pointing at the
  original level's planet; the original level's song) and `cubetxt7.dat`.

Its 3D view's assets are made as episode 6's (`tools/content/gbc/terrain.py`, with the game built):
each level's maps are exported and their side columns written, the export marked episode 7 (several
GBC levels have an original's name, and `make_cleanground.py` takes their maps, like episode 6's, as
not teaching the tilesets), each ground map gets its original's terrain settings in
`tools/terrain/levels.json` (marked `"episode": 7`) with its surfaces' heights carried over by colour
(the original map's classes, each one's mean colour with its height, as make_terrain.py's
`"materials"`), then the ground enemies are logged and the clean ground, terrain and vegetation are
built into `assets/terrain`. Maps an original has too (open space of one tile) stay the original's.
`tools/levels.py` lists episode 7's sections.

The game finds those files in the content directory as it finds episode 6's (`src/file.c`) and lists
"Episode 7: Tyrian GBC" in the episode menu when they are there. It is played on its own: a full
game doesn't go on to it after episode 6 (`last_episode`), and its end goes back to the title screen
without a high score (the save file's tables are episodes 1-6's). Its level file has 49 entries (24
levels and the item data): the table of a level file's entries holds 100 now (`lvllib.h`; it held
42, and a longer file overran it). A background whose pointer runs past its map's top (a long level
at the layer's speed) draws nothing there (`backgrnd.c`) rather than reading outside the map. `TYR3D_START=7:<section>` starts
one of its levels (the levels are the even sections, 2-48). Stages 1-5 of the plan: the maps, shops,
songs, enemies, bosses, story and the 3D terrain, and the enemies checked by eye; next: the GBC's own
bosses.

The GBC's big ships are mostly the PC's made smaller: SAVARA II's red bomber is SAVARA's of seven parts
(1:302-308), the DELI levels' red claws DELIANI's claw ship of twelve (1:400-411; the GBC makes it of two
types side by side, the second left out), both given by the overrides as composites; a composite is
centred on the GBC enemy (its sprite, or a block's pieces: script.py `sizes`). What no PC level has is
episode 7's own (`tools/content/gbc/new_enemies.json`): so far ASTEROID2's derrick, a mining rig on four
legs with a wrecking ball hanging from its beam (`["gbc", "derrick"]` in the overrides). Its model is
built like the PC enemies' (`tools/blender/models/enemies/gbc_derrick.py`: whole, leaned back as the
levels' tall ground objects, cut into the four pieces of a 4-part ground enemy) and its sprites are
drawn from it: the model's top view (`--sprite`) in the levels' palette, cut into the 2x2 sprites
(`tools/content/gbc/sheet.py`, PIL) of a sheet of its own, W (`newshw.shp`, with `sheet_w.png` to look
at; the game's compressed sprite format, checked against the game's sheets both ways), which the
build copies into `assets/content/episode7`. The game takes it as the 37th sheet (`shapeFile`,
`lvlmast.c`; `src/file.c` finds it in episode 7's content); the enemy's records are its base's (its
guns, its explosion) with those sprites, its armour and value (`build.py` `new_enemy`).

## Custom episodes

Episodes the community made in the game's own formats play beside the game's, without replacing
any of its files (`src/episodes.h`). Each is a folder of `data/custom` (`TYR3D_CUSTOM_DIR`; for the
app, `custom` in the game data's folder) holding the episode's files under the names they have for
the episode N they were made as: `levels<N>.dat` (the script: shops, levels, texts) and
`tyrian<N>.lvl` (the maps, their events and, for episodes 4 and up, the item data with the enemies),
optionally `cubetxt<N>.dat`, in small letters or capitals; `name.txt` (one line) is the name the
menus show, else the folder's. Start New Game's episode menu lists them after the game's episodes
("Custom: <name>"; not in a network game), and so does the debug flight. One is played as episode N
with every file of its folder standing in for the data's of that name (`dir_fopen`; the shapes,
music and pictures it doesn't have are the game's). It isn't saved (Save Game in its shop does
nothing: a save would load as the original episode N), has no high score (the board would be
episode N's) and its end (`]Q`) goes back to the title screen. `TYR3D_START=<folder>:<section>`
starts one in a test run, and `tools/levels.py` lists their sections that way, so the tools that go
through every level (`each_level.sh`, `ground_log.sh`, `review.sh`) take them too.

**Camanis 2** (`data/custom/camanis2`, from `LEVELS4.DAT` and `TYRIAN4.LVL` made for episode 4,
2005): a shop (`Camanis 2 Buy/Sell`), one level, the end. The level is on CAMANIS's ice tileset
(`shapesw.dat`, a third of its ground rows are CAMANIS's) with backgrounds 2 and 3 empty; its item
data is episode 4's with 190 enemies changed, most of them episode 1-3 enemies (CAMANIS's and
IXMUCANE's) copied into episode 4's slots, and a boss of four `b` sheet pieces (link 254) that is
hit only from clock 8300 (armour 254) and whose death (event 57) ends the level. Its 3D view: the
missing HD tiles of tileset W (`tools/tiles_hd.py --add`: shapes 248-250, 259, 260, 270), terrain
`3bf11c7517b5e2ad` (the rocky snow plateaus +18 as CAMANIS's, the rest `~` over the ice at 0),
clean ground and stand-ins (all 11 looks have CAMANIS's wreck models), its side columns. Of the 63
enemy looks it shows, one has no model and shows with volume: the ground gun turret that opens the
level (enemy 267, sheet `2` sprites 41, 131, 43, 93 turning; no original level has it).

## Destruct

Tyrian's secret minigame (`src/destruct.c`): an artillery duel of two armies (tanks, nuke and dirt
launchers, magnets, lasers, jumpers, helicopters, satellites) on a field of dirt that every shot digs
into, in five battles (5-Card War, Traditional, Heli Assault, Heli Defense, Outgunned; Custom from
`[destruct custom]` in `opentyrian.cfg`). Its logic is the original's (there is no wind).

It is reached as in the original: **DESTRUCT** typed at the title screen. Once it has been played
(`discovered` in `opentyrian.cfg`'s `[destruct]`), the title's menu offers it too, between Setup and
Demo (`destruct_discovered`, `titleScreen`).

With the modern UI its screens are panels over its field (`UI_SCREEN_DESTRUCT`, `UIDestruct` in
`ui.h`, published by `destruct.c` as it draws them): the intro as a card, the battles as a list with
what each side has (the mouse picks one), the help (F1) as both sides' keys as configured, the pause.
The keys: the left side X/Shift fire, C/V angle, A/Z power, Space/Ctrl weapon, Alt next unit; the
right side Enter/Insert, Left/Right, Up/Down, PgUp/PgDn, \ or Num 5; F10 and F11 hand the left and
the right side to the computer or back, Backspace makes a new field, P pauses, Esc goes back to the
battles. Test runs reach it with `TYR3D_TEST_KEYS=60:Space,4000:TypeDESTRUCT,3000:Space,2500:Return`
(the intro's logos skipped, the code typed, the intro passed, the first battle); F11 then hands the
right side to the computer, so the battle plays itself.

In the 3D view (with the modern UI) the battle is a diorama (`src/destruct3d.c`, drawn by
`present_destruct` in `render_gpu.c` while Destruct's screen is published): the field is the cut face
of a ridge seen a little from above, the game's plane (where the units stand and the shots fly) 4
pixels behind the face. The game's 320x200 picture of dirt stays the truth: the ridge is a density
field over its columns, rows and 14 slices 2 pixels apart, made into meshes by surface nets in chunks
of 16 columns, each made again when the dirt under it changes. Where the game digs dirt away the face
is dug back into the ridge in a bowl as deep as the hole is wide (each dug pixel's distance to the
dirt left, smoothed), so the explosions' holes are craters; the field's pixels on fire (the
explosions' 241-255) glow in the game's plane, and each explosion lights what is round it. The faces
show the earth in layers, darker down and back in the bowls, what faces up dry topsoil. Behind the
ridge the land falls away (the faster, the higher the ridge stands there) to rolling hills fading into
the dark; beside the field it goes on from its edges; a starry sky with faint nebulae and a red planet
lit by the sun. The units and the walls are models (`tools/blender/models/destruct/destruct.py`,
`assets/models/destruct`, models.cfg's `destruct_*` lines): for each side in its colours (the left
brass, the right green) a tank, a nuke launcher, a dirt launcher, a magnet, a laser, a jumper, a
helicopter and a satellite, a quarter larger than the game's sprites about their feet, the right side's
mirrored to face the left; their barrel, rail, tube or emitter (a model of its own) turned by the
unit's angle, a helicopter's rotor turning and the helicopter facing the way it flies, its nose dipping
as it speeds up; the walls blocks of blue stone. (A unit without a model shows as the game's sprite
with volume.) The crosshairs are gold rings. The effects (`destruct3d.c`, its own random numbers, never
the game's): an explosion flashes, burns in billowing fire, throws sparks, smoke that rises and, in the
dirt, clods that fall and stay where they land; a large one sends a shock wave and shakes the camera; a
dirt shot's burst throws clods and dust; each shot leaves a trail (sparks, a lasers' blue streak, the
big shells' smoke, dust) and a flash and a puff at the muzzle as it leaves; a magnet pushing sends
blue rings from its poles; a unit badly damaged smokes, one destroyed smokes where it stood for five
seconds; the field's pixels on fire spread a little over their neighbours, embers rather than squares. The modern HUD: each side's panel at the top (who plays it, its points, the unit chosen and how
many stand, the weapon with its icon, the barrel's angle on a dial, the power and the armor), the
battle and the score between them, the round's winner, the keys at the bottom. The camera fits the
field to the window's width and height (on wide windows the land beside it shows). `TYR3D_PROFILE=1`
prints the frames a second and what a frame and the ridge's meshes take.

A wall placed at the field's right edge (x 309 or more) made the original read and write past its
320 columns of heights, into the screen pointer after them, and the next field's terrain was drawn
from there: a crash. Placement now stops at the field's last column (`JE_placementPosition`).

## Environment variables

| Variable | Meaning |
| --- | --- |
| `TYR3D_2D=1` | Start in the original 2D view |
| `TYR3D_NO_MODELS=1` | Start with flat sprites (as after F4) |
| `TYR3D_MODEL_CONFIG` | Appearance file in `assets/models` (default `models.cfg`; `models_kenney.cfg` has the PoC 2 models) |
| `TYR3D_TILT`, `TYR3D_FOV`, `TYR3D_HEIGHT_SCALE` | Initial camera (defaults 20, 30, 1) |
| `TYR3D_GPU_BACKEND=vulkan` | Use Vulkan instead of Metal (macOS needs MoltenVK) |
| `TYR3D_DEMO_IDLE_MS` | Title-screen idle time before the demo starts (default 30000) |
| `TYR3D_DUMP_DIR`, `TYR3D_DUMP_EVERY`, `TYR3D_EXIT_AFTER`, `TYR3D_DUMP_LAYERS` | Frame dumps for automated checks (see `tools/capture_run.sh`) |
| `TYR3D_LOG_ENEMIES=1` | Print each enemy type on screen with its sprite sheet and index, for `models.cfg` (and, with frame dumps, which dump is which 3D frame) |
| `TYR3D_PROFILE=1` | Print the cost of 3D presentation, and of presenting the game's other screens (menus, the store, the screens over a level) |
| `TYR3D_START=<episode>:<section>` | Start a game at a level section, skipping the menus (see `tools/levels.py`); `<custom episode folder>:<section>` starts a custom episode's |
| `TYR3D_AUTOPILOT=1`, `TYR3D_GODMODE=1` | The ship weaves and fires by itself; the player takes no damage (`TYR3D_AUTOPILOT=nofire`: it never fires, so enemies live to be looked at). With `TYR3D_START` the autopilot steers in place of constant play's drift and held buttons (until 2026-10-25 the drift cancelled its steering and held the ship at the left edge, x 23, and fired with `nofire` too: ground logs, reviews and sweeps made with the autopilot before then flew there, so `tools/terrain/ground_log.sh` may log more after) |
| `TYR3D_SEED=<n>` | With `TYR3D_START`: the game's random seed (default 1; runs with the autopilot repeat frame for frame) |
| `TYR3D_MUSIC=midi\|opl` | The music through the SoundFont as MIDI, or on the emulated AdLib chip (default: the setting, Sound → Music). The player's chip writes become MIDI as they come (`music_midi.c`): a note while its channel's key is on, its loudness from the chip's total level, key scale level and envelope (the decay to the sustain level and, with a decaying envelope, on to silence while the key is held: a note that fades out on the chip ends there); instruments whose MIDI program is 128 and up are drums, the General MIDI drum note (program - 128) on the drum channel (Loudness's MIDI drums: hi-hats, snares, bass drums, cymbals) |
| `TYR3D_DEBUG_MIDI=1` | Print each MIDI note as it starts with the chip's registers for it (level, envelope) |
| `TYR3D_JUKEBOX=<song>` | Open the jukebox at once (no intro, no title screen), playing that song (1-41) first; for its visuals' test runs |
| `TYR3D_JUKEBOX_LOOK=<n>` | The jukebox's visuals' look for the run: 0 Orrery, 1 Warp (default: the setting, V in the jukebox) |
| `TYR3D_LOG_MUSICVIZ=1` | Print what the jukebox's visuals measure of the music every half second: loudness, lows, mids, highs, onsets, beats, each chip channel's note (+ sounding, level, pitch, notes started, d a drum), the drums' hits, the spectrum |
| `TYR3D_VOICES=0\|1` | The data cubes and story texts read aloud, off or on, for the run (default: the setting, Sound → Voices) |
| `TYR3D_VOICES_DIR=<dir>` | Where the voices are: `manifest.txt`, `e<episode>/<cube>.wav`, `story/e<episode>_<n>.wav` (default `data/voices`; see Voices) |
| `TYR3D_DEBUG_VOICES=1` | Print each voice event: the manifest read, a voice played (its file, length and load time), stopped or ended, a text without a voice or whose text differs from its voice's |
| `TYR3D_SOUNDFONT=<file>` | Another SoundFont for the music (for the run; the menus' SoundFont choice, Sound → SoundFont or the in-game options, picks among the `.sf2` files in `data/soundfonts`, kept as `soundfont` in `[tyrian3d]`) |
| `TYR3D_RECORD_AUDIO=<file>` | Write the game's sound output as raw 16-bit mono samples at 44.1 kHz |
| `TYR3D_EXPORT_SFX=<dir>` | Write the sound effects and voices as WAV files (`<number>_<title>.wav`, 11025 Hz) |
| `TYR3D_ORIGINAL_SFX=1` | Ignore replacement sounds in the data's `sfx` directory |
| `TYR3D_CONTENT_DIR=<dir>` | Where `items.cfg` and `rogue.cfg` are (default `assets/content`) |
| `TYR3D_CUSTOM_DIR=<dir>` | Where the custom episodes' folders are (default `data/custom`; see Custom episodes) |
| `TYR3D_ROGUE=<seed>`, `TYR3D_ROGUE=menu` | A rogue run at once with that seed, or the rogue screen; the profile isn't saved |
| `TYR3D_ROGUE_AUTO=1` | In a rogue run the screens choose by themselves (whole runs with the autopilot) |
| `TYR3D_ROGUE_UNLOCKS=all` | Every unlock for that run |
| `TYR3D_LEVEL_TICKS=<n>`, `TYR3D_LEVEL_DIE=<n>` | End every level as cleared after n ticks, or destroy the ship after n ticks (for testing what follows) |
| `TYR3D_DUMP_KEYS=1` | With `TYR3D_DUMP_DIR`: dump the first frame shown after the game has taken each test key (its key, button, wheel or pointer event) instead of every n-th (menus) |
| `TYR3D_UPSCALE_DIR=<dir>` | Where the HD resources are: `tiles/*.hdt`, `sheets/*.hd`, `hud_1p.png`, `hud_2p.png`, `pictures/pic_NN.png` (default `data/hd`) |
| `TYR3D_MODE=<mode>` | With `TYR3D_START`: `arcade`, `two` (two players), `twin` (twin-stick), `galaga` (the secret level's mode), `timed:<1-2>` (timed battle; start at section 1) or `super:<1-9>` (Super Arcade) instead of a full game |
| `TYR3D_TEST_PAD=1` | A virtual gamepad ("Tyrian3D test pad", which SDL takes in background windows too) that `TYR3D_TEST_KEYS`' Pad keys drive: `PadLX<v>`, `PadLY<v>`, `PadRX<v>`, `PadRY<v>` put a stick's axis at v (-1..1, right and down positive) and leave it there, `PadLT<v>`, `PadRT<v>` a trigger (0..1), `PadA`, `PadB`, `PadX`, `PadY`, `PadBack`, `PadStart`, `PadLB`, `PadRB` press a button (`*<ms>` holds it) |
| `TYR3D_SHIP=<1-18>` | With `TYR3D_START`: the player's ship, numbered as in the shop |
| `TYR3D_PLAYFIELD=wide` or `original` | The playfield for the run (as the setting) |
| `TYR3D_SIDEWAYS=<1-3>` | Every level seen from the side (as episode 6's side-scrolling levels; 2 and 3 add asteroids or crags along the edges) |
| `TYR3D_DIFFICULTY=<n>` | With `TYR3D_START`: the difficulty (1 easy, 2 normal, the default, 3 hard, 4 impossible ...; `config.h`); episode 1's TYRIAN and SAVARA have maps of their own from Hard on |
| `TYR3D_SHOP=1` | With `TYR3D_START`: the store between levels isn't skipped (start at the section before a level to see it) |
| `TYR3D_CUBES=1` | Every store holds all the data cubes its script lists, as if they were picked up (to test the reader and its voices) |
| `TYR3D_SECRETS=0\|1` | Record the secrets found, or not, whatever the run (by default a dev run, a demo, a rogue run or a custom episode records none; see Secrets). Use with its own `XDG_CONFIG_HOME` |
| `TYR3D_TEST_KEYS=<frame>:<key>[,<ms>:<key>...]` | Press a key (an SDL scancode name: `P`, `Escape`, `Return`, `Down`...; `MouseLeft`, `MouseRight`, `MouseMiddle`; `<key>*<ms>` holds it (a modifier, `Left Shift`, `Left Ctrl`..., in SDL's modifier state too, so `Left Shift*3000,400:G` is Shift+G); `MouseTo<x>x<y>` moves the game's pointer to that window point, where the mouse buttons then click, without moving the system's; `WheelUp`, `WheelDown` turn the mouse wheel a notch; `Joy<key>` presses the key as the joystick's, as its menu input does, so the key hints show the joystick's; `Type<text>` types the text, as a name or a code at the title) when that frame shows, then each next one so many milliseconds after the one before; any length |
| `TYR3D_DUMP_FROM=<frame>` | With `TYR3D_DUMP_DIR`: dump from that frame on |
| `TYR3D_DEBUG=pick` | The debug flight's level list first, instead of the intro and title screen |
| `TYR3D_DEBUG=1`, `TYR3D_DEBUG_SEEK=<tick>` | With `TYR3D_START`: a debug flight (see above), starting that many ticks in |
| `TYR3D_FONTS=0` | The game's texts in its pixel fonts, not in Oxanium, over the 3D view |
| `TYR3D_ERASE=0` | The maps' clean ground is left out: the objects, wrecks and palms painted into the map stay in the ground under their models, and no stand-ins are drawn |
| `TYR3D_LOG_STANDINS=1` | Every 30th frame, print the stand-ins shown on the screen (their look, placeholder or own model, where on the screen and on the map, as the `.std` has it, and the nearest enemy) and how many are covered by their enemies (with frame dumps, `dump:` lines say which 3D frame a dump is) |
| `TYR3D_DARK_LIGHTING=0` | Spotlight levels show the game's lit cone as an overlay, instead of being dark and lit by the ship's lamp |
| `TYR3D_RC=off\|low\|high` | The radiance cascades: light of what glows spreads over the playfield (default low, with Effects) |
| `TYR3D_RC_INTENSITY=<0-2>` | How much light they add (default 1) |
| `TYR3D_LOG_RC=1` | Print the radiance cascades' state now and then |
| `TYR3D_GLOW_LIGHTS=0` | Shots and other glows don't light their surroundings |
| `TYR3D_LOG_LIGHTS=1` | Print the point lights of each frame |
| `TYR3D_LOG_BOSS=1` | Print the boss bar's armor each time it changes |
| `TYR3D_LOG_JUMPS=1` | Print the level clock's jumps (loops, timers, mid-level bosses), scroll speed changes, warp orbs and data cubes picked up |
| `TYR3D_TEST_EXPLOSION=<x>,<y>,<every>` | A large explosion at this screen point every so many frames, to look at the particles |
| `TYR3D_WEAPONS=<front>,<rear>[,<power>]` | With `TYR3D_START`: the weapons, ids as in the shop's weapon ports, and their power (1-11) |
| `TYR3D_SIDEKICKS=<left>,<right>` | With `TYR3D_START`: the sidekicks, numbered as in the shop (the catalogue lists them) |
| `TYR3D_SPECIAL=<n>`, `TYR3D_BOMBS=<n>` | With `TYR3D_START`: a special weapon (its id in the item data), super bombs at each level's start (0-10) |
| `TYR3D_WINDOWED=1` | Run in a window in the corner of the screen without taking the focus, and keep playing without it (`tools/capture_run.sh` sets it) |
| `TYR3D_EXPORT_MUSIC=<dir>` | Export every song as a MIDI file (with the General MIDI instruments the composer set for MIDI devices, the drums on the drum channel), and the instruments they use (`instruments.json`, with each one's raw MIDI bytes: program, dum1, dum2) |
| `TYR3D_EXTRACT=<dir>` | Export the sprite sheets and the enemy catalogue (see `tools/catalog_html.py`) |
| `TYR3D_EXPORT_PICTURES=<dir>` | Export the game's pictures as PNGs, each in its palette, to be drawn anew: the 14 full-screen pictures of `tyrian.pic` (menus, title, HUD panels, logos, story pictures), `tshp2.pcx`, the data cubes' faces and the ending's animation frame by frame; `README.txt` in it says where each shows (e.g. `export/legacy`) |
| `TYR3D_BACKGROUNDS=<digits>` | Draw tiles only for these background maps, e.g. `13` (for checking; default all) |
| `TYR3D_HD_TILES=0` | Leave out the HD tiles (`data/hd/tiles`, `tools/tiles_hd.py`): the maps' tiles at their size |
| `TYR3D_DEBUG_TILES=1` | Tint the map tiles by background: background 2 magenta, background 3 cyan (for checking which map a tile belongs to) |
| `TYR3D_LIGHTING=<sun>,<sky>` | Override the models' light: the sun's energy and the share of the sky's light (for tuning; defaults 4, 0.3) |
| `TYR3D_SHADOWS=0`, `TYR3D_EFFECTS=0` | No shadows, no particles and glows (override the 3D settings) |
| `TYR3D_SIDES=mirror` | Continue the background maps beyond their sides mirrored, as before the generated columns |
| `TYR3D_WINDOW_SIZE=<w>x<h>` | With `TYR3D_WINDOWED`: the window's size, for checking other aspect ratios |
| `TYR3D_GLINTS=<scale>,<strength>,<sharpness>,<tilt>` | Tune the sun's glints on water (defaults 1, 0.5, 140, 3) |
| `TYR3D_SMOOTH=0` | Show each of the game's frames once, as it renders them (no frames between ticks) |
| `TYR3D_DUMP_AHEAD=1` | Frame dumps include the frames shown between ticks |
| `TYR3D_SOFTWARE_POINTER=1` | Draw the mouse pointer into the screen as the original does, instead of the system pointer |
| `TYR3D_HUD=modern\|classic` | The HUD over the playfield, or the original panel beside it |
| `TYR3D_MENUS=modern\|classic` | The menus in the modern UI's style, or the original screens (as Graphics > Menus) |
| `TYR3D_SCREENS=fill\|integer` | With the modern UI: the old 320x200 screens fill the window's height over a blurred copy, or as Scaling Mode says |
| `TYR3D_UI_SCALE=<percent>` | The modern UI's and the HUD's size (50-200; the setting has 75-150) |
| `TYR3D_UI_GALLERY=1` | The title screen shows the modern UI's widgets (tabs, item cards, pickers, bars, keys) instead of its menu, to judge the style by |
| `TYR3D_MOUSE=direct\|original` | The ship goes where the (hidden) pointer is, which moves as on the desktop (default), or the original's mouse control (a speed, with momentum) |
| `TYR3D_RENDER_SCALE=<0.25..1>` | Render the 3D scene at this scale of the window's pixels (default: the window's size in points, half on high-density displays) |
| `TYR3D_TILES_ONLY=1` | Leave out the background layers the game drew, so only the map's tiles show the backgrounds (to compare them) |
| `TYR3D_LAYER_PARALLAX=1` | Show the layers' planes unscaled (positions on different layers no longer line up as in the game) |
| `TYR3D_LOG_SPAWNS=1` | Print each enemy an event makes, and whether the 3D view showed it coming |
| `TYR3D_AA=<0..3>` | Anti-aliasing: 0 off, 1 SMAA low, 2 SMAA high (default), 3 FXAA |
| `TYR3D_LOG_CLOUDS=1` | Print which tiles of backgrounds 2 and 3 are shown as cloud puffs, and each cloud canvas's height and the ground under it |
| `TYR3D_TERRAIN=0` | Leave out the terrain from assets (the ground flat or with per-tile relief, backgrounds 2 and 3 flat) |
| `TYR3D_VEGETATION=0` | Leave out the vegetation (palms, trees and grass from `assets/terrain/<map>.veg`) |
| `TYR3D_VIEWER_FIRST=<n>` | Model viewer (`TYR3D_VIEWER=enemies`): start at the n-th sprite rule of `models.cfg` |
| `TYR3D_HD=0` | Leave out the HD volumes (the generated models from the 4x upscaled sheets) |
| `TYR3D_FILTER=0` | Show the maps' tiles and the layers as sharp pixels instead of smoothly filtered |
| `TYR3D_DEBUG_TERRAIN=1` | Print each frame which backgrounds can be terrain and why not (blended, filtered, composed) |
| `TYR3D_LOG_GROUND_MODE=1` | Print how the ground is drawn whenever that changes: as terrain (its map, heights and holes), in relief by tiles, or flat and why (stars, a filter) |
| `TYR3D_TURBO=<factor>` | Run the game that many times faster, showing only every so many ticks (for collecting data over whole levels) |
| `TYR3D_LOG_GROUND=1` | Print where ground enemies stand or move on the background maps (`ground:` lines: also their sheet and first sprite, where on the screen, the 3D frame, and the object each is a piece of) and what their models cover round them (`groundmodel:`), for `tools/terrain/make_terrain.py` (`tools/terrain/ground_log.sh`); the top enemies riding background 3 as `riding:` lines on its map (for `make_cleanground.py`'s upper maps: `cleanground.json` `upper_maps`, whose `.std` stand-ins the game draws among the top enemies) |
| `TYR3D_LOG_CLIP=1` | Every 10th frame, print each enemy model that raised ground or a background hides in part, or that shows where the game hides it, by more than 2 pixels: its model's triangles as drawn, rasterized as the camera sees them, each point that shows checked on its way to the camera (`render_gpu.c` `log_clipping`): `clip: <kind> frame <3D frame> layer <layer> sheet <sheet> sprite <first sprite> model <name> at <x>,<y> depth <pixels> of <its height> area <percent> inside <percent> screen <x>,<y>` (depth in the model's game pixels; area: the share of what shows of the model affected that deep; inside: of that, where the model is in the terrain or solid rather than behind raised ground in front of it; screen: its middle in the window, 0-1, and with frame dumps `dump:` lines say which 3D frame a dump is). Kinds: `terrain` (the ground's terrain), `bg2-solid`, `bg3-solid` (backgrounds 2 and 3 as solids), `ground` (background 1 drawn flat), `bg2-plane`, `bg3-plane` (backgrounds 2 and 3 drawn flat hiding a model the game draws over them), `bg2-over`, `bg3-over` (a model showing above one of them where the game draws it over the enemy), `float` (a ground enemy on raised or covered ground: its lowest points seen stand higher above the ground drawn under them than they would above a flat ground; leaning, its lowest points above its leaning base, the lean counted in its lift; depth is how much higher, area the share of those points, and a `gap <pixels>` at the end how far above the ground the worst one is). With frame dumps every dumped frame is checked too. Sheet and sprite as in `models.cfg`'s `sprite` lines; `TYR3D_LOG_CLIP=2` adds where the deepest point is, the lift the model got, the ground drawn under its middle, the terrain stored at its position and its lean (degrees across x and z) |
| `TYR3D_RELIEF=<height>` | Per-tile relief of the ground where a map has no terrain asset (default 8, 0 off) |
| `TYR3D_DEBUG_WATER=1` | Tint the procedural water red (to see where it is) |
| `TYR3D_EXPLOSION_LIGHTS=0` | Leave out the explosions' lights |
| `TYR3D_TEST_LIGHT=<x>,<y>,<height>,<radius>,<energy>` | Add a point light at a game position (to check the lighting) |
| `TYR3D_BLOOM=<intensity>,<threshold>,<knee>,<radius>` | Tune the bloom (defaults 0.5, 1, 0.1, 1.2; intensity 0 turns it off) |
| `TYR3D_SUN=<x>,<y>,<z>` | Override the direction the sun's light travels (for tuning; default 0.6,-1,0.6: from the top left of the screen) |
| `TYR3D_VIEWER=ships` | Model viewer: each ship's 3D look beside its sprite (see `src/viewer.h`), with `TYR3D_VIEWER_YAW`, `_ROLL`, `_SPIN`; `sidekicks` shows the sidekicks |

## How it works

- **SDL3 port.** OpenTyrian2000 was moved from SDL2 to SDL3, which SDL_GPU requires.
- **Layer capture** (`src/layer3d.c`). The main loop marks where each draw phase starts:
  background 1, ground enemies, background 2, sky enemies, background 3, player and shots,
  explosions, and so on. At the end of each phase the screen is diffed against a snapshot, and
  the pixels that changed become that phase's layer. Each layer is captured before later phases
  cover it, so it is complete. Filter effects (water, blur, darkening) write their changes back
  into the layer that owns each pixel. The level's colour filter is applied per layer, as a
  palette remap.
- **Background maps** (`src/background3d.c`). The game draws only the background tiles that fit
  on its screen; the tilted camera sees much more. So the 3D view draws the three background maps
  itself, as tiles on each background's plane, for the whole area the camera sees (up to 640
  pixels ahead, then fading out). Each time the game draws a background its scroll state is
  recorded, so the tiles line up with the game's own drawing, and scrolling further up follows
  the map's wrap points. Beside the map, 16 columns on each side are generated from the map's
  own tiles by wave function collapse (`src/wfc.c`): which tile may stand next to which is
  learned from the map, and the columns next to it must fit its edge. They are made ahead of
  time for every level (`tools/precompute_sides.sh`, into `assets/sides`); a map without them
  gets them when it loads, kept in `tyrian3d-sides` in the user's directory. Further out the
  map continues mirrored; everything beyond the map slowly darkens. `TYR3D_SIDES=mirror`
  mirrors only, for comparison.
  Inside the playfield the captured layer is drawn over the tiles. Backgrounds that the game
  filters (lava, water, ice) cannot be tiles, since the filters blur and waver across tile edges:
  they are composed on the CPU for the area the camera sees and run through the game's own
  filter code, with the waver aligned to the game's screen.
- **Overscan.** Sprites can be seen above the original top edge, so in 3D mode the game also draws
  enemies into 64 extra rows above the screen.
- **Rendering** (`src/render_gpu.c`). Layers become textured planes at increasing heights, each
  scaled about the point below the camera so that a position on any layer is seen where the game
  draws it (a turret's shots and explosion stay on the turret); objects scale with their plane. What
  stands on the ground stands on it as drawn (`render_gpu.c` `stand_lift`: the terrain's relief under it in
  the world, on the edge of its footprint the camera sees), and on terrain leans with it, by pitch and roll
  of at most 12 degrees, following it smoothly as the map scrolls (`compute_object_lifts`, `lean_matrix`;
  what leans is moved along the camera's rays so it is still seen where the game draws it): a thing alone
  by the plane of the ground under its footprint, where that ground is one; the pieces of one enemy, made
  together by the level's events, on one plane, leaning as best fits the ground under them, at their lifts'
  mean but none deeper in the ground than half its height. What the game draws under a solid background 2
  or 3 and lies mostly inside it fades out (`hide_in_solids`). Solids scroll at their own speed over the ground's
  terrain (TYRIAN's stone platforms three times as fast), so its raised ground and plants would stand up through
  their tops: the tops alone are drawn first and mark their pixels in the stencil, the ground and its plants aren't
  drawn there (as the game draws the solids over the ground), then the solids whole, their walls going down into the
  ground as drawn; plants under a solid's top aren't drawn at all (`not_on_solids`, `under_solid`). The enemies of a layer the game draws after
  a background stand above that background's plane (`layer_base`; background 3 drawn under the sky enemies
  is the layer `bg3-low`, below them). The camera is fitted so the playfield's bottom edge, at the player's height, fills the original
  playfield width; the projection is shifted onto the playfield's rectangle in the window, and
  the scene continues into the rest of the window. The HUD panel stands at the window's right
  edge, as tall as the window, and the playfield is as large as fits beside it (on 16:9 it fills
  the window's height); messages from the bar below the playfield are shown as text in the
  playfield. Two-player games have the same layout. The HUD and in-playfield text are drawn flat
  on top; the HUD panel at four times its resolution (Scale2x twice). If the panel's picture
  has been upscaled (`data/hd/hud_1p.png`, `hud_2p.png`, see HD resources below), that
  picture is drawn, and only the pixels the game changed on it (gauges, text) come from the game.
- **The modern UI** (`src/ui.c`). Sizes are virtual units, 1080 to the window's height times the
  UI scale, with a smallest size for text in the window's pixels; everything is placed in a 16:9
  safe area (the window, at most 16:9 wide, centred). Panels are octagons (cut corners) drawn as quads
  with a pixel-wide soft edge, the blurred picture under them as frosted glass; text from Oxanium's
  rasters; all of it through the overlay's quads (`rgpu_ui_*`), as the HUD. A menu keeps drawing the
  original screen and publishes what it shows (`ui_menu_publish`: items, selection, an open picker,
  where the original takes the mouse on each); while the screen still shows that (98 % of its pixels),
  `rgpu_present_ui` draws the screen's picture (its texts taken off) and the menu in the new style.
  The pointer's window position on a widget is handed to the menu as a point of the original's item
  (`mapWindowPointToScreen`), so the menu's own code takes the mouse as ever; the wheel is Up and
  Down. The old screens' fill: the screen magnified in whole steps into a target, then drawn smoothly
  (`sharp_steps`), the window round it a blurred copy (80x50, made again only when the picture
  changes). The game's displays on the playfield (score, lives, bombs, special, boss bar, timer) are
  a layer of their own (`L3D_HUD`), left out under the modern HUD.
  The store publishes what it shows each time it shows (`shop_publish` in `game_menu.c`: its menu, the
  parts' choices with costs, icons and stats, the weapon's power, the credits, where the original takes
  the mouse on each) and the 3D view draws its own layout over the picture blurred, with the ship's
  models or the weapon simulator's (its stars and shots without models from the screen) drawn by the
  scene into the layout's pane (`rgpu_present_ui`). Screens that animate on their own while shown (ship
  specs, a level's end) are published with `hold` and shown so until released. The screens over a level
  are drawn over the 3D scene (`rgpu_present_3d_menu` with `modern`); their glass shows the scene copied
  once it is drawn and made smaller in halves by the canvas (`scene_blur`), again only when the scene
  changes. The HUD's panels fade by what is under them: the ship's box and the enemies' shots in the
  window (`hud_fade`); two players: both ships.
  The other screens publish the same way, each with its own data in `UIMenu`: the high scores
  (`UIScores`, `JE_highScoreScreen`, `JE_highScoreCheck`), story texts (`UIStory`: `JE_displayText`
  publishes before each frame `JE_outCharGlow` shows, with how far the original has revealed the text,
  over the picture as it was before the text, `story_begin`; the text is laid out again in paragraphs,
  each character keeping its place in the original's lines, so it shows as far as the original's),
  title cards (`UICard`, `card_publish`), load (`UIPaging` for the players' pages), the jukebox
  (`UIJukebox`, published every frame over its visuals: below), the instructions, the credits (`UICredits`:
  the lines where the original draws them) and the rogue run (`UIRogue`). Where the original takes no
  mouse (the high scores' and load's tabs, the jukebox's buttons and songs, the name question's
  buttons), the widgets are the UI's own: the pointer on one maps to the screen's point of nothing,
  and the screen's code takes a click on it with `ui_take_press` (modern only). The wheel moves
  Up/Down or Left/Right as the screen says (`UIMenu.wheel`). A screen that is over calls
  `ui_screen_done`, so the next screen can't match its picture. The key hints show the joystick's pad
  and buttons when the last key came from the joystick (`push_key` counts its keys:
  `joystick_last_input`).
- **The jukebox's visuals** (`src/musicviz.c`, `src/jukebox3d.c`). With the modern menus the jukebox shows a
  3D scene that plays with the music under its panel, instead of the original's starfield (Classic menus
  keep the original). The music is measured where it is made (`musicviz.h`): the audio callback hands over
  the mixed output (as heard: the music and the sound effects) into a ring, and after each of the player's
  updates the chip's state (`adlib_registers`): each channel's key, pitch, instrument (its General MIDI
  program, 128 and up a drum), the notes it has started (`lds_channel_notes`) and how loud it sounds (its
  operators' levels, key scaling and envelope, `midi_chip_channel_db`, then its release) — both kinds of
  music, the chip and MIDI through the SoundFont, play from the same chip writes. Nothing waits for a lock
  in the audio thread (a ring with an atomic count, a spinlock for two numbers). Each frame the main thread
  reads them where the output is heard now (about 2048 samples behind the newest, on by the clock since the
  last buffer): 2048-sample Hann windows every 512 samples, FFT, 48 bands from 30 Hz to 16 kHz (+4.5 dB an
  octave above 1 kHz), against a reference that follows the music's loudest of late (up in 0.35 s, down in
  14 s; the bands 46 dB below it to it, to the power 1.45), quick to rise and slower to fall, with falling peaks; onsets as the spectrum's rise (the lows
  twice); beats from the song's own kick and snare notes, else from the onsets. Silent test runs
  (SDL's dummy audio driver) measure the same.
  The scene (`jukebox3d_frame`) is boxes, bars, spheres, glows, rings and models that `render_gpu.c`
  draws over the whole window (`present_jukebox_scene`), bloom and all, the panel's glass showing it
  blurred (made again each frame); its middle higher while the panel shows (Space hides it). Between the
  jukebox's ticks it is shown again at the display's rate (`video_wait_tick_ui`). Two looks, V or the
  panel's Look button (kept as `jukebox_look` in `[tyrian3d]`):
  - **Orrery**: a planet (a gas giant made at start) with a crown of 72 bars of lit metal on a ring round
    it, the lows tall at the back, the highs in front, both sides the same, their tops glowing with the
    bars' heat and their peaks floating above them; the chip's nine channels as moons orbiting it in their
    colours, higher with higher notes, lit while their notes sound and flashing as each starts, leaving
    trails and lighting the planet and the bars (point lights); the kick (or a beat) a ring of sparks
    running out from the bars (at most every 0.3 s), the snare sparks from the bars' tops, the toms a ripple
    round the ring, the cymbals a flare behind the planet, the hi-hats the stars; faint nebulae behind; the
    camera sways slowly and comes nearer on the beats.
  - **Warp**: one of the game's ships (a fighter for each song, the USP Talon first) flies towards
    the camera, seen from above at a slant, drawing the spectrum behind it as rings of a tunnel (20 a
    second and on every drum, the lows at the top; the quiet in the tunnel's colour, which goes round teal,
    blue, violet, magenta and amber with the mids, the loud in the bars' heat) and the channels' notes as
    lanes of light along it, round the tunnel by their pitch (an octave a third of the way round), as long
    as each sounds (a piano roll); the drums flash and thicken the rings and shake the camera, the cymbals
    light them all, the stars streak past faster with the music's loudness and its lows.
- **Clean ground and stand-ins** (`tools/terrain/make_cleanground.py`, `src/tyrian2.c` `draw_standins`).
  The maps paint under many ground enemies what is left of them once destroyed (a crater, a burnt housing,
  a broken pyramid), or the object itself, or its base; in 2D the sprite covers it while the enemy lives, in
  3D it showed under and round the model. Offline, each ground map's painted art at the places where ground
  enemies stand (and its copies where none stands), and the desert maps' painted palms, are erased and
  filled with the map's own ground round them (`assets/terrain/<map>.era`: pixels taken from the map at an
  offset, so the palette effects and the HD tiles fill them too; `erase_painted_enemies` applies them as
  the terrain's rows are made). Only where something 3D takes the place: landscape the game animates
  (waterfalls), the rock arches and paintings without a model stay. Where the original shows the painting
  (before the enemy comes, once it is destroyed, where none ever stands), the 3D view shows its model, a
  stand-in (`assets/terrain/<map>.std`): the look the game leaves when the enemy is destroyed, the object's
  own model where the map paints the object as it is (or, where the map paints it in other colours, models.cfg's
  `standin <sheet> <sprite> <model>`: TYRIAN's and SOH JIN's rubble in rock browns, `tools/glb_palette_remap.py`
  makes such colour variants), its wreck model (models.cfg `wreck <sheet> <sprite>
  <model>`: the painting as a model, drawn with the enemy type's options; `none`: nothing), or until it has one the enemy's
  model slumped and darkened (`render_gpu.c` `STANDIN_SLUMP`, `STANDIN_SHADE`). A stand-in is drawn while no ground
  enemy of its looks (the enemy itself, its damaged and dead looks, what it turns into) stands on its place;
  it is only drawn, the game knows nothing of it. A wreck's pieces stand together on the terrain as an object's
  pieces do (at their lifts' mean), unless the ground under them steps by more than 6 pixels (a slot on the edge
  of SAVARA V's sea rocks): then each stands on its own (`render_gpu.c` `STANDIN_STEP`). The terrain and the vegetation are made on the clean
  ground, so grass grows round the turrets and the palms stand on bare sand; the plants are kept off the
  models' footprints, and in the game cleared only under the enemies that move.
- **Appearances** (`src/models3d.c`, `assets/models/models.cfg`). Each enemy type and player
  ship is shown as a model, as its sprite with generated volume, or as the flat sprite. For the
  first two the game records a 3D object instead of drawing the sprite; objects are depth-tested
  against the layers and lit by a sun and ambient light.
- **Volumetric sprites** (`src/volume3d.c`). The default appearance: a sprite's silhouette is
  inflated into a rounded relief and textured with the sprite's own pixels. The sun's shading is
  baked into the mesh, scaled so that faces pointing up keep exactly the sprite's colours: every
  object has volume while it keeps its original look. Ground objects, whose sprites include the
  ground around them, stay nearly flat.

## Models

Models are built in Blender by Python scripts in `tools/blender/models`, using the kit in
`tools/blender/tyrkit.py`, and exported to `assets/models` as glTF binaries:

```bash
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P tools/blender/models/ships/talon.py -- --preview /tmp/talon
```

`--preview` also renders a top view framed like the sprite and a three-quarter view. Conventions:
1 unit = 1 game pixel, the nose up the screen (+Y in Blender), the origin at the sprite's centre.
Materials take the colour an up-facing surface should show in the game, so sprite colours can be
used directly. Better, `tyrkit.material(palette=<index>)` takes a palette index: the game then
colours the material from the current palette, as it does the sprites, so models follow the
level's palette, fades and filters (such materials are named `<name>@<index>`).
`tools/blender/sprite_profile.py` lists a sprite's silhouette and palette indices, from sheets
exported by `TYR3D_EXTRACT` (in the levels' palette, `tools/blender/palette_levels.txt`). The
export reverses the triangles' winding (`tools/blender/glb_winding.py`):
BTBH takes clockwise triangles as the front of static models, glTF counter-clockwise; models
from elsewhere need the same treatment once.

Items (coins, gems, crystals, data cubes, armour, power-ups) are grey models that take the colour
of the sprite's current frame (`color=sprite` in `models.cfg`), so one model serves every colour
and follows animations that cycle colours; see the options at the top of `models.cfg`.

The model viewer shows the models in the game's view and light beside their sprites:

```bash
tools/capture_run.sh /tmp/viewer 30 30 TYR3D_VIEWER=ships
```

(or run the game with `TYR3D_VIEWER=ships` and look; `TYR3D_VIEWER_ROLL=90` shows the side.)

## HD resources

The 3D view's HD pictures are made from the game's data, so, like the data, they are not in the repository; the
game loads them from `data/hd` (beside `data/tyrian2000`; `TYR3D_UPSCALE_DIR` overrides it): `tiles/<tileset>.hdt`
(the background tiles at 4x), `sheets/<sheet>.hd` (the sprite sheets at 4x, for the HD volumes) and `hud_1p.png`,
`hud_2p.png` (the HUD panel). Without them the game draws the original pixels. `pictures/pic_NN.png` and
`pictures/tshp2.png` are the game's full-screen pictures drawn anew (by hand or an image generator, from
`TYR3D_EXPORT_PICTURES`' pictures, in the same frame at any size; `tools/hd_pictures.py <dir>` puts them there, a
picture with alpha laid on black): where the screen shows one of them much as the game loaded it (45 % of its own,
not black, pixels or more: the logos as the game starts, the title, the menus' backgrounds, a story's picture), in
the modern UI or the old screens, the new picture shows under the screen, which keeps only what the game drew over
its picture (the title's logo, texts), and fades with the palette, to black or white (the median over the picture's
colours, so that colours the screen animates don't count) (`render_gpu.c` `match_hd_picture`;
`TYR3D_DEBUG_PICTURES=1` prints the matches and fades). The user's reconstructions are in `data/hd/pictures`
(not the HUD panels and the old screens' pictures, which the modern UI draws itself, nor the ending's animation).
`pictures/logo_tyrian.png` and `pictures/logo_2000.png` are the title's logo and its 2000(tm) drawn anew (from the
export's `logo_tyrian.png` and `logo_2000.png`, in the same frame at any size, with alpha): over the title's picture,
where the screen shows the logo's sprite (also while it flies in), the new logo shows in its box and the sprite's
pixels are taken off (`render_gpu.c` `find_hd_logos`); a fully clear `logo_2000.png` takes the 2000(tm) away.
`pictures/face_NN.png` are the data cubes' faces drawn anew (the user's, from the export's `face_NN.png`, any size,
clear round the figure): `tools/hd_pictures.py` fits each into the store's portrait window (the export's
`face_frame.png`: the frame, its window clear), as large as it takes to cover it, cut to its shape with a soft edge,
over the whole portrait at 6x; where the store's screen shows a face as it draws it, its pixels give way to the
window's colour and the new face shows over the portrait, fading with its palette (`render_gpu.c` `find_hd_face`; in
the modern UI and the old store with the 3D view; only the face shown is loaded). `pictures/portrait_frame.png` is the
portrait's frame round them drawn anew (the export's `face_frame.png` through `tools/upscale_sprites.py` with
4x-BigFArt-Detail, cut to the portrait by `tools/hd_pictures.py --frame-hd <the upscale>`): drawn over the frame, under
the face, where the store's screen shows it (`find_hd_frame`). `icons/` holds the modern UI's icons drawn anew (`shop_`, `ship_`,
`shipt_`, `ship_s_`, `special_`, `option_`, `planet_<sprite>.png`): the export's `icons/` (the store's items as its cards
show them, the ships, the HUD's small ship and bomb, the specials, the data cube icons, the planets of its map, each in
its screen's palette) through `tools/upscale_sprites.py` with 4x-BigFArt-Detail; where one is there
the UI draws it instead of the sprite's pixels (`render_gpu.c` `hd_icon`: the store's cards and its map's planets, and
the rogue run's map, its planets drawn anew over the map's in their own palette's colours). `upscale/` is only the work folder
(atlases to upscale, the upscaled atlases, pictures to look at) and can be deleted; `export/maps` (`tools/export_maps.sh`)
is the HD tiles' input. To make everything again (the upscales take 3-4 hours on the GPU):

```bash
tools/setup_tools_venv.sh
PY=~/Library/Caches/Tyrian3D/tools-venv/bin/python
MODEL=~/Library/Caches/Tyrian3D/esrgan/4x-Fatality.pth
DETAIL=~/Library/Caches/Tyrian3D/esrgan/4x-BigFArt-Detail.pth
$PY tools/tiles_hd.py $DETAIL --tilesets z,y,x,w --work upscale/out/tiles_bigfart
$PY tools/tiles_hd.py $MODEL --tilesets ')'
TYR3D_EXTRACT=export/extract build/game/tyrian3d
$PY tools/make_atlases.py export/extract upscale/in
$PY tools/upscale_sprites.py $MODEL upscale/in upscale/out
$PY tools/hd_sheets.py
```

The sprites, the HUD panels and the lava's tiles (x29) are upscaled with 4x-Fatality by twittman (OpenModelDB, CC BY-NC-SA
4.0); the other tilesets' tiles (z: asteroids, TYRIAN, DELI; y: SAVARA; x: TORM and the jungles; w: the ice) since
2026-10-26 with 4x-BigFArt-Detail by DinJerr (OpenModelDB, CC BY-NC 4.0): sharper stones, grids and ice (the user
chose Fatality for the lava after a comparison in the game on 2026-10-18; the comparison of the others is in item 58 of
`TYRIAN3D_HANDOFF.md`). The Fatality tiles of z, y, x and w are kept in `data/hd/tiles_fatality` (`cp
data/hd/tiles_fatality/*.hdt data/hd/tiles/` goes back). BigFArt-Detail is not in OpenModelDB's own storage: its
author's public OneDrive folder holds it as `4x_BigFArt_Detail_300000_G.pth` (SHA-256
0f8007e6a5ee9b08567c1219def8c13fc2b902f1cfc5f4d6fa17103b69c06002, 66 958 607 bytes; OneDrive's anonymous API: a
token from `https://api-badgerp.svc.ms/v1.0/token` with app id 5cbed6ac-a083-4e14-b191-b4ba07653de2, then the share
`https://1drv.ms/u/s!Aip-EMByJHY23if0ac150Sj2qnbp?e=qLp7SP` encoded as `u!<base64url>` under
`https://api.onedrive.com/v1.0/shares/.../driveitem/children` with `Authorization: Badger <token>`; ask the user
before downloading).

## Tools

| Tool | What it does |
| --- | --- |
| `tools/capture_run.sh` | Runs the game in a background window, silent (`TYR3D_AUDIO=1` keeps the sound), and dumps frames (see the environment variables) |
| `tools/sweep.sh`, `tools/levels.py` | Plays every level for a while and makes a contact sheet per level; `levels.py` lists the level sections (`TYR3D_START`'s), the custom episodes' too |
| `tools/review.sh` | Visual review: plays each level briefly (or the given episodes or `episode:section`s) in a background window and keeps a few frames per level as PNGs; the big BMP dumps are deleted right away |
| `tools/blender/render_models.py`, `tools/model_sheet.py` | Renders `.glb` models in one Blender run (`--list` of files), then contact sheets of the enemy models beside their 4x sprites (with a `TYR3D_EXTRACT` catalogue: ordered by how often they appear, by episode; needs PIL) |
| `tools/catalog_html.py` | Browsable page of the `TYR3D_EXTRACT` catalogue |
| `tools/make_atlases.py` | PNG atlases of the sprites by group (ships, sidekicks, enemies by episode, items), for upscaling and as references |
| `tools/anim_semantics.py` | Sorts the enemies' animations into rotations, rolls, cycles and changes of shape, for models that move as the sprites do (needs numpy, e.g. Blender's Python) |
| `tools/package_macos.sh` | Builds the macOS app bundle |
| `tools/fetch_soundfont.sh` | Downloads the SoundFonts the music can play through into `data/soundfonts` (checked by SHA-256): GeneralUser GS (the default), FluidR3 GM (MIT, from Debian's package) and Arachno 1.0 (private, non-commercial use only: the app leaves it out); `fetch_soundfont.sh fluid` for one |
| `tools/voices/export_cubes.py`, `tools/voices/generate.py`, `tools/voices/say_placeholders.py` | The data cubes and story texts read aloud (see Voices): the script from the game's data, the ElevenLabs render, placeholder voices from macOS `say` |
| `tools/upscale_sfx.py` | Upscales the sound effects and voices with AudioSR into the data's `sfx` directory (run with AudioSR's Python) |
| `tools/hd_sheets.py` | Puts the upscaled atlases back together as 4x sprite sheets (`data/hd/sheets/<sheet>.hd`) for the HD volumes, and copies the upscaled HUD panels to `data/hd` |
| `tools/sprite_reference.py` | An enemy type's reference picture for modelling: every animation frame from the 4x upscales, beside the original |
| `tools/terrain/make_terrain.py` | Terrain for the background maps: `classify` sorts an exported ground map's pixels into surfaces (a review image in `export/terrain`), `build` writes `assets/terrain/<map>.ter` from the settings in `tools/terrain/levels.json` (class heights, chasms where space is black, backgrounds 2 and 3 as solids, or with `"ground": true` a background 2 that covers the whole ground under its enemies as the ground itself; level pads under what stands and gentle roads along what moves, as far as the terrain drawn under them reaches, so their models stand flat; solids clear round what the models cover) and a relief image to review (with the enemies' tracks), `sheets` puts the reliefs on contact sheets (needs numpy, scipy, PIL) |
| `tools/fix_macho_tls.py` | Makes pip's scipy load on macOS 27 (its modules' zero-fill thread-local sections carry a file offset the new dyld refuses): clears the offsets and signs the modules again. The terrain tools' Python is a venv in `~/Library/Caches/Tyrian3D/tools-venv` (numpy, scipy, Pillow from pip, then this over its `site-packages`) |
| `tools/terrain/make_cleanground.py` | Clean ground (replaces `make_erasures.py`): for the ground maps, the art painted under and round the ground enemies (wrecks, housings, stumps, the objects themselves, their copies where none stands) and the painted palms, erased and filled with the map's own ground round them, where a model takes its place, into `assets/terrain/<map>.era`; the stand-ins shown there while no enemy covers the place into `assets/terrain/<map>.std`; review pictures `export/terrain/<map>_clean.png` and `export/terrain/standins.txt` (what stands in for each look). Overrides (paintings that stay, stand-in looks, maps left alone) in `tools/terrain/cleanground.json`. Run it before `make_terrain.py build` and `make_vegetation.py`, which take the clean ground. Episode 6's and the custom episodes' maps are cleaned with what the game's own maps teach about their tilesets, not teaching them |
| `tools/terrain/footprints.py` | What the ground enemies' models cover of the ground seen from above (their triangles as the renderer turns and scales them), for the clean ground and the vegetation's keep-out; `check` compares them with the renderer's `groundmodel:` boxes |
| `tools/terrain/make_vegetation.py` | Vegetation for the ground maps, on the clean ground: palms (where the maps paint them on desert maps, `"palms": true`), trees (textured green areas) and grass (smooth green areas), off the footprints of the models that stand on the map (ground enemies and stand-ins), into `assets/terrain/<map>.veg` |
| `tools/terrain/ground_log.sh` | Plays every level fast with the autopilot and collects where the ground enemies stand and move, and what their models cover, into `export/terrain/ground.txt` (the terrain keeps them on the ground) | (episode 1's SAVARA has a map of its own from Hard on: log, export and build it with `TYR3D_START=1:10 TYR3D_DIFFICULTY=3`)
| `tools/polish_progress.py` | How far the models' polish is: the share of the catalogue's enemy appearances (`TYR3D_EXTRACT`'s `catalog.json`, weighted by count) whose model was last written with a `polish_*.py` script, for the enemies, launched enemies and drops, blank looks (invisible markers) left out; and the most seen looks still missing (run with the tools' Python) |
| `tools/sweep.sh` | Plays every section of the episodes with the autopilot, one run after another, and reports each run's level, whether it ran to the end and its warnings |
| `tools/tiles_hd.py` | HD background tiles that still tile: whole exported maps (`tools/export_maps.sh`) through an ESRGAN model, every tile the per-pixel median of its upscales among its real neighbours, quantized to the palette ramps it uses (palette effects keep working); writes `data/hd/tiles/<tileset>.hdt`, which the game loads with the maps (atlas and terrain at 4x), and its pictures to look at and kept medians to `upscale/out/tiles`. `--requantize` writes them again from the kept medians; `--add` makes only the shapes the kept medians lack (maps exported since, a custom episode's) and keeps the rest. Tiles are per tileset and shape, so generated maps get them too |
| `tools/upscale_sprites.py` | Upscales the sprite atlases 4x with an ESRGAN model (`.pth`, e.g. from OpenModelDB), with alpha (run with a Python that has torch) |
| `tools/setup_tools_venv.sh` | Makes the tools' Python (numpy, scipy, Pillow, torch: `~/Library/Caches/Tyrian3D/tools-venv`) and fetches the ESRGAN model 4x-Fatality (`~/Library/Caches/Tyrian3D/esrgan`); downloads ~180 MB |
| `tools/precompute_sides.sh` | Generates the columns beside every level's background maps into `assets/sides` |
| `tools/content/make_items.py` | Writes `assets/content/items.cfg`, the new weapons and sidekicks, by rules from the original data (see New content) |
| `tools/content/make_rogue.py` | Writes `assets/content/rogue.cfg`: the rogue mode's acts (levels, bosses found by their boss bars), the items its cards offer (the shops' lists, tiered by price) and its unlocks |
| `tools/content/episode6/build.py`, `tools/content/tyrformat.py` | Episode 6 in the game's formats (the encrypted script and data cubes, the level file with the episode's item data); run at build time |
| `tools/gbc/extract.py`, `songs.py`, `report.py`, `episode.py` | The GBC Tyrian ROM (`data/gbc/Tyrian.gb`, the user's) read in the tools' GBC emulator (`gbemu.c`, `gb.py`; `disasm.py` disassembles): its levels, music and an overview to `data/gbc`, and its levels as PC levels for episode 7 (see Episode 7) |
| `tools/content/gbc/build.py` | Episode 7 in the game's formats from `data/gbc/episode7`; run at build time when those are there |
| `tools/content/gbc/sheet.py` | Episode 7's own enemies' sprites (sheet W, `newshw.shp`) from their models' top views (needs PIL) |
| `tools/content/tyrdata.py` | Reads the game's item data (weapons, ports, sidekicks, ships, enemies...) for the content tools |
| `tools/blender/` | The model pipeline (see Models) |

## Secrets

The title menu's **Secrets** (where the instructions were; `src/secrets.c`) lists the game's secrets in four kinds,
as tabs with how many of each are found: the levels only a warp orb or a hidden condition leads to (episodes 1-4
and 6: BUBBLES, HOLES, SOH JIN, ASTEROID?, MINEMAZE, WINDY and ALE; GEM WAR, MARKERS, MISTAKES; AST. CITY,
SAWBLADES and the hard-only TYRIAN X, SAVARA Y, New Deli; episode 4's WINDY, DESERTRUN, ICESECRET, SIDE EXIT,
?TUNNEL?, TIME WAR, SQUADRON; episode 6's VAULT), the codes typed at the title (the nine Super Arcade ships,
DESTRUCT, ENGAGE: locked ones as a question mark per letter), the data cubes read in each episode (of how many its
`cubetxt` file holds), and the others (the hidden difficulties Impossible, Suicide and Lord of Game, episode 4's
shop that sells the Stalker 21.126). A found one shows its name, a locked one "???"; the selected one's line says
where to look. Modern UI: a panel over the menus' picture (tabs, rows with FOUND or LOCKED, a click on a tab or a
row); classic: the original screen's fonts. Left/Right change the kind, Up/Down the row, Esc goes back.

The game reveals them as it plays (`tyrian2.c`: a secret level's `]L` line read, the shop's `]I` in its section,
a code accepted at the title; `menus.c`: a difficulty shown; `game_menu.c` `load_cubes`: the store's cubes), and
each is kept at once in the user directory's `tyrian3d_secrets.cfg` (`found <id>` lines: `level <episode>
<section>`, `code <n>`, `cube <episode> <n>`, `difficulty <n>`, `shop <episode> <section>`). Nothing is recorded
in a demo, a rogue run, a custom episode or a dev run (`TYR3D_START`, `TYR3D_TEST_KEYS`, `TYR3D_AUTOPILOT`,
`TYR3D_ROGUE`, `TYR3D_MODE`, `TYR3D_DUMP_DIR`, `TYR3D_EXIT_AFTER`), unless `TYR3D_SECRETS=1`. Destruct counts as
found once it has been discovered (`[destruct] discovered`).

## Voices

The data cubes and the story texts between levels are read aloud (`src/voiceover.c`): when the store's
data cube reader opens a cube, or a story text, a warning or an episode's end with its secret hint shows
(classic or modern menus), its voice plays over the music, which is ducked by about 6 dB (200 ms ramps,
`loudness.c`), and a story's stops when the text closes (a 30 ms fade); the text stays as the subtitles.
A cube's voice plays on when its reader closes, until the store closes: the store's data cube player (the
modern UI's bar under the ship: previous, play or pause, next, the cube playing and how far; P plays or
pauses, `[` and `]` go to the previous or next cube, wrapping round) plays the store's cubes while you
shop, and a cube opened in the reader plays from its start; the Data list marks the cube playing ("PLAYING",
"PAUSED"). Sound →
**Voices** in Setup is its volume (Left/Right) and on/off (Enter), kept as `voices` and `voice_volume` in
`[tyrian3d]`; "No voices installed" when there are none.

The voices go in `data/voices` (outside git; `TYR3D_VOICES_DIR`): `e<episode>/<cube>.wav` (the cube's
number in its episode's `cubetxt` file), `story/e<episode>_<n>.wav` and `manifest.txt`, which lists each
with the hash of the text it reads (32-bit FNV-1a over the cube's text lines or the story's
`levelWarningText` lines); the game plays a voice only over its own text, so an edited cube (episode 6's
are generated) or a custom episode's cubes stay silent. Any WAV SDL reads works; the render writes IMA
ADPCM, 24 kHz mono, -18 LUFS (`tools/package_macos.sh` copies them into the app when they are there).

Rendering them (ElevenLabs, the user's own subscription, a paid plan for voice design; the key is
read only from `ELEVENLABS_API_KEY`, the gitignored `.env.local` that `npx @elevenlabs/cli@latest
onboard connect --env-path .env.local` writes, or `~/.config/tyrian3d/elevenlabs_key`, and goes only
into the request header):

1. `python3 tools/voices/export_cubes.py` writes the script `data/voices/script.json` and the
   proofreading copy `script.html` from the game's data: 170 cubes (`E:N`), the 96 story texts and
   hints (`E:101`... in the order of the episode's script, the end's secret hints `E:201`...), split
   by speaker. `tools/voices/cast.json` has the speakers (28 designed voices; minor parts borrow one,
   `voice_of`), which cubes and stories each reads (`cube_rules`, by the same ids) and the voice
   prompts; `pronunciation.json` the names' readings.
2. `python3 tools/voices/generate.py estimate` (no network): characters, minutes, credits and the plan
   (about 134,000 characters, 140-163 minutes). `status` shows the account's credits.
3. `generate.py design [--speaker K]` makes three previews per voice in `data/voices/previews/`;
   `adopt K N` makes the one chosen the speaker's voice (its `voice_id` in `cast.json`).
4. `generate.py generate [--only E:N,...] [--jobs 4]` renders what is not in the render cache
   (`data/voices/cache`, keyed by text, voice and settings: a changed line renders again alone) and
   builds the WAVs and the manifest; `--retake E:N[:S]` renders a cube or segment again;
   `generate.py build` rebuilds from the cache without the network.

Rendered 2026-10-25 with `eleven_v4` (about 0.44 credits a character; about 69,000 credits with the voice
design): all 170 cubes and the 96 story texts and hints, about 140 minutes, 100 MB of WAVs, with the
render cache (about 400 MB) beside them in `data/voices`. The voices chosen are in `cast.json` (`voice_id`,
`adopted_preview`); the account's 30 custom voices hold the 28 and the user's own;
another take of a cube is `generate.py generate --retake E:N`, a speaker's tempo its `settings.speed`
and `generate.py build --only ...` (from the cache, free).

`tools/voices/say_placeholders.py --out DIR --only 1:1,1:101 --stories` makes placeholder voices with
macOS's `say` (no account), to try the playback with `TYR3D_VOICES_DIR=DIR`.

## Roadmap

1. ~~PoC 1: the original sprites in 3D.~~
2. ~~PoC 2: placeholder CC0 models (Kenney Space Kit) for enemies and the player.~~
3. ~~Volumetric sprites for every enemy and player ship; per-enemy appearance rules with yaw modes.~~
4. ~~Background maps drawn for everything the 3D camera sees.~~
5. Next steps (see `docs/plans/2026-10-07-tyrian3d-plan.md`):
   - ~~Shadows from models onto the ground layer.~~
   - Models for shots and power-ups; explosions as particles (started: `src/particles3d.c` adds a
     flash, sparks, smoke and debris to every explosion).
   - ~~Upside-down levels (`starShowVGASpecialCode` 1) and spotlight levels (2) in 3D.~~
   - Custom models matching the original sprites, and higher-resolution background tiles.

## Credits

See `LICENSES.md` for the licenses (the macOS app has them in `Contents/Resources/licenses`).

- Tyrian: Eclipse Software / Jason Emery (freeware data).
- OpenTyrian / OpenTyrian2000: the OpenTyrian team and Kaito Sinclaire (GPL-2.0).
- Placeholder models: Kenney Space Kit, CC0 (`assets/models/kenney-space-kit/License.txt`).
- Music synth: TinySoundFont by Bernhard Schelling, MIT (`external/tinysoundfont/LICENSE`).
- SoundFonts: GeneralUser GS by S. Christian Collins, free to use; FluidR3 GM by Frank Wen, MIT;
  Arachno SoundFont by Maxime Abbey, freeware for private, non-commercial use (not in the app) (all
  downloaded by `tools/fetch_soundfont.sh` with their licenses; not in git).
- Sound effect upscaling: AudioSR by Haohe Liu et al. (run locally, results not in git).
- Voices of the data cubes and story texts: ElevenLabs text to speech (rendered with the user's own
  subscription by `tools/voices/generate.py`; not in git).
