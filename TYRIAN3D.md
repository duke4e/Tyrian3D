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
| `TYR3D_LOG_ENEMIES=1` | Print each enemy type on screen with its sprite sheet and index, for `models.cfg` |
| `TYR3D_PROFILE=1` | Print the cost of 3D presentation |
| `TYR3D_START=<episode>:<section>` | Start a game at a level section, skipping the menus (see `tools/levels.py`) |
| `TYR3D_AUTOPILOT=1`, `TYR3D_GODMODE=1` | The ship weaves and fires by itself; the player takes no damage |
| `TYR3D_SHIP=<1-18>` | With `TYR3D_START`: the player's ship, numbered as in the shop |
| `TYR3D_SIDEKICKS=<left>,<right>` | With `TYR3D_START`: the sidekicks, numbered as in the shop (the catalogue lists them) |
| `TYR3D_WINDOWED=1` | Run in a window in the corner of the screen without taking the focus, and keep playing without it (`tools/capture_run.sh` sets it) |
| `TYR3D_EXTRACT=<dir>` | Export the sprite sheets and the enemy catalogue (see `tools/catalog_html.py`) |
| `TYR3D_BACKGROUNDS=<digits>` | Draw tiles only for these background maps, e.g. `13` (for checking; default all) |
| `TYR3D_LIGHTING=<sun>,<sky>` | Override the models' light: the sun's energy and the share of the sky's light (for tuning; defaults 4, 0.3) |
| `TYR3D_SHADOWS=0` | No shadows |
| `TYR3D_SIDES=mirror` | Continue the background maps beyond their sides mirrored, as before the generated columns |
| `TYR3D_WINDOW_SIZE=<w>x<h>` | With `TYR3D_WINDOWED`: the window's size, for checking other aspect ratios |
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
- **Rendering** (`src/render_gpu.c`). Layers become textured planes at increasing heights. The
  camera is fitted so the playfield's bottom edge, at the player's height, fills the original
  playfield width; the projection is shifted onto the playfield's rectangle in the window, and
  the scene continues into the rest of the window. In one-player games the HUD panel stands at
  the window's right edge, as tall as the window, and the playfield is as large as fits beside
  it (on 16:9 it fills the window's height); messages from the bar below the playfield are shown
  as text in the playfield. Two-player games keep the original screen's layout. The HUD and
  in-playfield text are drawn flat on top.
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
| `tools/precompute_sides.sh` | Generates the columns beside every level's background maps into `assets/sides` |
| `tools/blender/` | The model pipeline (see Models) |

## Roadmap

1. ~~PoC 1: the original sprites in 3D.~~
2. ~~PoC 2: placeholder CC0 models (Kenney Space Kit) for enemies and the player.~~
3. ~~Volumetric sprites for every enemy and player ship; per-enemy appearance rules with yaw modes.~~
4. ~~Background maps drawn for everything the 3D camera sees.~~
5. Next steps (see `docs/plans/2026-10-07-tyrian3d-plan.md`):
   - ~~Shadows from models onto the ground layer.~~
   - Models for shots, power-ups and explosions (particles).
   - ~~Upside-down levels (`starShowVGASpecialCode` 1) and spotlight levels (2) in 3D.~~
   - Custom models matching the original sprites, and higher-resolution background tiles.

## Credits

- Tyrian: Eclipse Software / Jason Emery (freeware data).
- OpenTyrian / OpenTyrian2000: the OpenTyrian team and Kaito Sinclaire (GPL-2.0).
- Placeholder models: Kenney Space Kit, CC0 (`assets/models/kenney-space-kit/License.txt`).
