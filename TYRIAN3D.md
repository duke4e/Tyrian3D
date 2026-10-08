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
sprites), shadows, effects (explosion particles, glowing shots) and a camera preset (Standard,
Steep, Overhead). They are kept in the `[tyrian3d]` section of `opentyrian.cfg`; F3 and F4
change the first two as well.

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
| `TYR3D_UPSCALE_DIR=<dir>` | Where the upscaled HUD panel pictures are (default `upscale/out`) |
| `TYR3D_MODE=<mode>` | With `TYR3D_START`: `arcade`, `two` (two players), `galaga` (the secret level's mode), `timed:<1-2>` (timed battle; start at section 1) or `super:<1-9>` (Super Arcade) instead of a full game |
| `TYR3D_SHIP=<1-18>` | With `TYR3D_START`: the player's ship, numbered as in the shop |
| `TYR3D_LOG_WRECKS=1` | Print each wreck a destroyed ground model leaves |
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
| `tools/capture_run.sh` | Runs the game in a background window and dumps frames (see the environment variables) |
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
