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
Steep, Overhead), the mouse, and the HUD: Modern (the playfield fills the window; shield, armor
and power at the bottom right, the guns' power and the sidekicks' ammunition at the top right,
fading while the ship is under them; the level's name as it starts) or Classic (the original
panel beside the playfield; two players always have it). They are kept in the `[tyrian3d]` section of `opentyrian.cfg`; F3 and F4
change the first two as well. In a level, Escape's options have **3D Options** with the same
settings and the music (SoundFont or AdLib), each changed with Left/Right, Enter or a click and
taking effect at once (`ingame_options_3d` in `mainint.c`).

The game plays only in its playfield; the 3D view shows the world around it too, darkened, so
what is bright is what can be shot and reached (enemies coming or leaving show dimmed there).

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
| `TYR3D_PROFILE=1` | Print the cost of 3D presentation |
| `TYR3D_START=<episode>:<section>` | Start a game at a level section, skipping the menus (see `tools/levels.py`) |
| `TYR3D_AUTOPILOT=1`, `TYR3D_GODMODE=1` | The ship weaves and fires by itself; the player takes no damage |
| `TYR3D_SEED=<n>` | With `TYR3D_START`: the game's random seed (default 1; runs with the autopilot repeat frame for frame) |
| `TYR3D_MUSIC=midi\|opl` | The music through the SoundFont as MIDI, or on the emulated AdLib chip (default: the setting, Sound → Music) |
| `TYR3D_SOUNDFONT=<file>` | Another SoundFont for the music |
| `TYR3D_RECORD_AUDIO=<file>` | Write the game's sound output as raw 16-bit mono samples at 44.1 kHz |
| `TYR3D_EXPORT_SFX=<dir>` | Write the sound effects and voices as WAV files (`<number>_<title>.wav`, 11025 Hz) |
| `TYR3D_ORIGINAL_SFX=1` | Ignore replacement sounds in the data's `sfx` directory |
| `TYR3D_CONTENT_DIR=<dir>` | Where `items.cfg` and `rogue.cfg` are (default `assets/content`) |
| `TYR3D_ROGUE=<seed>`, `TYR3D_ROGUE=menu` | A rogue run at once with that seed, or the rogue screen; the profile isn't saved |
| `TYR3D_ROGUE_AUTO=1` | In a rogue run the screens choose by themselves (whole runs with the autopilot) |
| `TYR3D_ROGUE_UNLOCKS=all` | Every unlock for that run |
| `TYR3D_LEVEL_TICKS=<n>`, `TYR3D_LEVEL_DIE=<n>` | End every level as cleared after n ticks, or destroy the ship after n ticks (for testing what follows) |
| `TYR3D_DUMP_KEYS=1` | With `TYR3D_DUMP_DIR`: dump the frame after each test key instead of every n-th (menus) |
| `TYR3D_UPSCALE_DIR=<dir>` | Where the upscaled HUD panel pictures are (default `upscale/out`) |
| `TYR3D_MODE=<mode>` | With `TYR3D_START`: `arcade`, `two` (two players), `galaga` (the secret level's mode), `timed:<1-2>` (timed battle; start at section 1) or `super:<1-9>` (Super Arcade) instead of a full game |
| `TYR3D_SHIP=<1-18>` | With `TYR3D_START`: the player's ship, numbered as in the shop |
| `TYR3D_LOG_WRECKS=1` | Print each wreck a destroyed ground model leaves |
| `TYR3D_SIDEWAYS=<1-3>` | Every level seen from the side (as episode 6's side-scrolling levels; 2 and 3 add asteroids or crags along the edges) |
| `TYR3D_SHOP=1` | With `TYR3D_START`: the store between levels isn't skipped (start at the section before a level to see it) |
| `TYR3D_TEST_KEYS=<frame>:<key>[,<ms>:<key>...]` | Press a key (an SDL scancode name: `P`, `Escape`, `Return`, `Down`...; `MouseLeft`, `MouseRight`, `MouseMiddle`; `<key>*<ms>` holds it) when that frame shows, then each next one so many milliseconds after the one before |
| `TYR3D_DUMP_FROM=<frame>` | With `TYR3D_DUMP_DIR`: dump from that frame on |
| `TYR3D_DEBUG=pick` | The debug flight's level list first, instead of the intro and title screen |
| `TYR3D_DEBUG=1`, `TYR3D_DEBUG_SEEK=<tick>` | With `TYR3D_START`: a debug flight (see above), starting that many ticks in |
| `TYR3D_FONTS=0` | The game's texts in its pixel fonts, not in Oxanium, over the 3D view |
| `TYR3D_ERASE=0` | Ground enemies' objects painted into the map stay in the ground under their models |
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
| `TYR3D_WINDOWED=1` | Run in a window in the corner of the screen without taking the focus, and keep playing without it (`tools/capture_run.sh` sets it) |
| `TYR3D_EXPORT_MUSIC=<dir>` | Export every song as a MIDI file (with the General MIDI instruments the composer set for MIDI devices), and the instruments they use (`instruments.json`) |
| `TYR3D_EXTRACT=<dir>` | Export the sprite sheets and the enemy catalogue (see `tools/catalog_html.py`) |
| `TYR3D_BACKGROUNDS=<digits>` | Draw tiles only for these background maps, e.g. `13` (for checking; default all) |
| `TYR3D_LIGHTING=<sun>,<sky>` | Override the models' light: the sun's energy and the share of the sky's light (for tuning; defaults 4, 0.3) |
| `TYR3D_SHADOWS=0`, `TYR3D_EFFECTS=0` | No shadows, no particles and glows (override the 3D settings) |
| `TYR3D_SIDES=mirror` | Continue the background maps beyond their sides mirrored, as before the generated columns |
| `TYR3D_WINDOW_SIZE=<w>x<h>` | With `TYR3D_WINDOWED`: the window's size, for checking other aspect ratios |
| `TYR3D_GLINTS=<scale>,<strength>,<sharpness>,<tilt>` | Tune the sun's glints on water (defaults 1, 0.5, 140, 3) |
| `TYR3D_SMOOTH=0` | Show each of the game's frames once, as it renders them (no frames between ticks) |
| `TYR3D_DUMP_AHEAD=1` | Frame dumps include the frames shown between ticks |
| `TYR3D_SOFTWARE_POINTER=1` | Draw the mouse pointer into the screen as the original does, instead of the system pointer |
| `TYR3D_HUD=modern\|classic` | The HUD over the playfield, or the original panel beside it |
| `TYR3D_MOUSE=direct\|original` | The ship goes where the (hidden) pointer is, which moves as on the desktop (default), or the original's mouse control (a speed, with momentum) |
| `TYR3D_RENDER_SCALE=<0.25..1>` | Render the 3D scene at this scale of the window's pixels (default: the window's size in points, half on high-density displays) |
| `TYR3D_TILES_ONLY=1` | Leave out the background layers the game drew, so only the map's tiles show the backgrounds (to compare them) |
| `TYR3D_LAYER_PARALLAX=1` | Show the layers' planes unscaled (positions on different layers no longer line up as in the game) |
| `TYR3D_LOG_SPAWNS=1` | Print each enemy an event makes, and whether the 3D view showed it coming |
| `TYR3D_AA=<0..3>` | Anti-aliasing: 0 off, 1 SMAA low, 2 SMAA high (default), 3 FXAA |
| `TYR3D_LOG_CLOUDS=1` | Print which tiles of backgrounds 2 and 3 are shown as cloud puffs |
| `TYR3D_TERRAIN=0` | Leave out the terrain from assets (the ground flat or with per-tile relief, backgrounds 2 and 3 flat) |
| `TYR3D_VEGETATION=0` | Leave out the vegetation (palms, trees and grass from `assets/terrain/<map>.veg`) |
| `TYR3D_VIEWER_FIRST=<n>` | Model viewer (`TYR3D_VIEWER=enemies`): start at the n-th sprite rule of `models.cfg` |
| `TYR3D_HD=0` | Leave out the HD volumes (the generated models from the 4x upscaled sheets) |
| `TYR3D_FILTER=0` | Show the maps' tiles and the layers as sharp pixels instead of smoothly filtered |
| `TYR3D_DEBUG_TERRAIN=1` | Print each frame which backgrounds can be terrain and why not (blended, filtered, composed) |
| `TYR3D_TURBO=<factor>` | Run the game that many times faster, showing only every so many ticks (for collecting data over whole levels) |
| `TYR3D_LOG_GROUND=1` | Print where ground enemies stand or move on the ground map (`tools/terrain/ground_log.sh`) |
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
  draws it (a turret's shots and explosion stay on the turret); objects scale with their plane. The
  camera is fitted so the playfield's bottom edge, at the player's height, fills the original
  playfield width; the projection is shifted onto the playfield's rectangle in the window, and
  the scene continues into the rest of the window. The HUD panel stands at the window's right
  edge, as tall as the window, and the playfield is as large as fits beside it (on 16:9 it fills
  the window's height); messages from the bar below the playfield are shown as text in the
  playfield. Two-player games have the same layout. The HUD and in-playfield text are drawn flat
  on top; the HUD panel at four times its resolution (Scale2x twice). If the panel's picture
  has been upscaled (`upscale/out/hud_1p.png`, `hud_2p.png`, from `tools/make_atlases.py`), that
  picture is drawn, and only the pixels the game changed on it (gauges, text) come from the game.
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

## Tools

| Tool | What it does |
| --- | --- |
| `tools/capture_run.sh` | Runs the game in a background window, silent (`TYR3D_AUDIO=1` keeps the sound), and dumps frames (see the environment variables) |
| `tools/sweep.sh`, `tools/levels.py` | Plays every level for a while and makes a contact sheet per level |
| `tools/catalog_html.py` | Browsable page of the `TYR3D_EXTRACT` catalogue |
| `tools/make_atlases.py` | PNG atlases of the sprites by group (ships, sidekicks, enemies by episode, items), for upscaling and as references |
| `tools/anim_semantics.py` | Sorts the enemies' animations into rotations, rolls, cycles and changes of shape, for models that move as the sprites do (needs numpy, e.g. Blender's Python) |
| `tools/package_macos.sh` | Builds the macOS app bundle |
| `tools/fetch_soundfont.sh` | Downloads the GeneralUser GS SoundFont the music plays through into `data/soundfonts` |
| `tools/upscale_sfx.py` | Upscales the sound effects and voices with AudioSR into the data's `sfx` directory (run with AudioSR's Python) |
| `tools/hd_sheets.py` | Puts the upscaled atlases back together as 4x sprite sheets (`upscale/out/sheets/<sheet>.hd`) for the HD volumes |
| `tools/sprite_reference.py` | An enemy type's reference picture for modelling: every animation frame from the 4x upscales, beside the original |
| `tools/terrain/make_terrain.py` | Terrain for the background maps: `classify` sorts an exported ground map's pixels into surfaces (a review image in `export/terrain`), `build` writes `assets/terrain/<map>.ter` from the settings in `tools/terrain/levels.json` (class heights, chasms where space is black, backgrounds 2 and 3 as solids) and a relief image to review, `sheets` puts the reliefs on contact sheets (needs numpy, scipy, PIL) |
| `tools/terrain/make_vegetation.py` | Vegetation for the ground maps: palms (green patches on desert maps, `"palms": true`), trees (textured green areas) and grass (smooth green areas), clear of the ground enemies, into `assets/terrain/<map>.veg` |
| `tools/terrain/ground_log.sh` | Plays every level fast with the autopilot and collects where the ground enemies stand into `export/terrain/ground.txt` (the terrain keeps them on the ground) |
| `tools/sweep.sh` | Plays every section of the episodes with the autopilot, one run after another, and reports each run's level, whether it ran to the end and its warnings |
| `tools/upscale_sprites.py` | Upscales the sprite atlases 4x with an ESRGAN model (`.pth`, e.g. from OpenModelDB), with alpha (run with a Python that has torch) |
| `tools/precompute_sides.sh` | Generates the columns beside every level's background maps into `assets/sides` |
| `tools/content/make_items.py` | Writes `assets/content/items.cfg`, the new weapons and sidekicks, by rules from the original data (see New content) |
| `tools/content/make_rogue.py` | Writes `assets/content/rogue.cfg`: the rogue mode's acts (levels, bosses found by their boss bars), the items its cards offer (the shops' lists, tiered by price) and its unlocks |
| `tools/content/episode6/build.py`, `tools/content/tyrformat.py` | Episode 6 in the game's formats (the encrypted script and data cubes, the level file with the episode's item data); run at build time |
| `tools/content/tyrdata.py` | Reads the game's item data (weapons, ports, sidekicks, ships, enemies...) for the content tools |
| `tools/blender/` | The model pipeline (see Models) |

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
- SoundFont: GeneralUser GS by S. Christian Collins, free to use (downloaded by
  `tools/fetch_soundfont.sh` with its license; not in git).
- Sound effect upscaling: AudioSR by Haohe Liu et al. (run locally, results not in git).
