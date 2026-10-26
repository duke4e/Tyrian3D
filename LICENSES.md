# Licenses and credits

Tyrian3D is OpenTyrian2000 with a 3D view. Its code is under the GNU General Public License,
version 2 (`COPYING`). The parts it is built from, and the tools its assets were made with:

| Part | Author | License | Where |
| --- | --- | --- | --- |
| Tyrian, Tyrian 2000 (the game's data, not included) | Eclipse Software, Jason Emery | freeware | the player's own copy |
| OpenTyrian, OpenTyrian2000 | the OpenTyrian team, Kaito Sinclaire | GPL-2.0 | `COPYING` |
| Tyrian3D (3D view, models, tools) | Tyrian3D authors | GPL-2.0 | `COPYING` |
| BTBH renderer (a fork of r3d) | Le Juez Victor (r3d); BTBH | zlib-style | `external/btbh-renderer/LICENSE` |
| SDL 3 | Sam Lantinga and contributors | zlib | `licenses/SDL3-LICENSE.txt` in the app (from Homebrew) |
| SDL_shadercross (build tool) | the SDL team | zlib | `external/btbh-renderer/external/SDL_shadercross/LICENSE.txt` |
| Open Asset Import Library (assimp) | the assimp team | BSD-3-Clause | `licenses/assimp-LICENSE.txt` in the app (from Homebrew) |
| uthash | Troy D. Hanson | BSD | `external/btbh-renderer/external/uthash/LICENSE` |
| TinySoundFont, TinyMidiLoader | Bernhard Schelling | MIT | `external/tinysoundfont/LICENSE` |
| GeneralUser GS SoundFont | S. Christian Collins | free to use, see its license | `data/soundfonts/GeneralUser-GS-LICENSE.txt` (downloaded by `tools/fetch_soundfont.sh`) |
| FluidR3 GM SoundFont | Frank Wen | MIT | `data/soundfonts/FluidR3_GM-LICENSE.txt` (downloaded by `tools/fetch_soundfont.sh`, from Debian's package) |
| Arachno SoundFont (not in the app) | Maxime Abbey | freeware for private, non-commercial use | `data/soundfonts/Arachno-Documentation.html` (downloaded by `tools/fetch_soundfont.sh`; left out of `tools/package_macos.sh`) |
| Kenney Space Kit (placeholder models) | Kenney | CC0 | `assets/models/kenney-space-kit/License.txt` |
| Oxanium (the HUD's and menus' font) | The Oxanium Project Authors (Severin Meyer) | SIL Open Font License 1.1 | `assets/fonts/Oxanium-OFL.txt` |

Made with, not included:

- **Blender** builds the models from the scripts in `tools/blender` (the models are the scripts'
  output, under the project's license).
- **AudioSR** (Haohe Liu et al.) upscales the sound effects (`tools/upscale_sfx.py`); the upscaled
  sounds are made from the game's data and are not in the repository.
- **ESRGAN models from OpenModelDB**: 4x-Fatality by twittman (CC BY-NC-SA 4.0) upscales the sprite
  atlases, the HUD panels and the lava's background tiles; 4x-BigFArt-Detail by DinJerr (CC BY-NC 4.0)
  the other background tiles (`tools/upscale_sprites.py`, `tools/tiles_hd.py`; earlier, for comparison,
  4x-Lady0101 and 4x-Rebout-Blend). The upscales are made from the game's data and are not in the
  repository (`data/hd`). Both models are licensed for non-commercial use only.
