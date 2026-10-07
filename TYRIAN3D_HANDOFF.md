# Tyrian3D: predaja rada

Datum predaje: **2026-10-07**. Ovo je početna točka za novog agenta, bez potrebe za starim
razgovorom. Putanje su relativne prema rootu repozitorija
`/Users/duke4e/Documents/GitHub/Tyrian3D`, osim ako je navedeno drukčije.

Najprije pročitaj ovaj dokument, zatim [TYRIAN3D.md](TYRIAN3D.md) (build, kontrole i opis
arhitekture za korisnika).

## 1. Zadatak i stanje koje preuzimaš

Cilj: OpenTyrian2000 prenijeti u 2.5D/3D tako da logika igre ostane identična originalu.
Mijenja se samo prikaz. Korisnik je zadao ove faze:

1. **PoC1**: originalni spriteovi u 3D perspektivi prihvatljivoj za vertikalni shmup. **Gotovo.**
2. **PoC2**: besplatni modeli umjesto spriteova, samo da se dobije osjećaj. **Gotovo** (Kenney Space Kit).
3. Kasnije: vlastiti modeli po uzoru na originalne spriteove i rekonstrukcija ostale grafike
   (pozadine, efekti). **Nije započeto.**

Korisnikove odluke:

- C + Vulkan/Metal, a ne prepisivanje u Godot ili Unity.
- Grafička baza je korisnikov BTBH renderer: r3d fork s backendom na SDL3 SDL_GPU, Metal i Vulkan.
- Korisnik je odobrio preuzimanje Tyrian 2000 podataka (freeware, camanis.net).
- Kenney modeli nisu preuzimani s interneta. Kopirani su iz korisnikova lokalnog projekta
  (`~/Documents/GitHub/QIX Rouguelike (GPT 5.3)/assets/kenney/space-kit`), CC0.

**Git (stanje 2026-10-07):**

- Rad je commitan i pushan na branch `tyrian3d/poc` repoa `https://github.com/duke4e/Tyrian3D`.
  Repo je privatan.
- Upstream OpenTyrian2000 je remote `upstream`.
- Renderer je na branchu `tyrian3d` repoa `duke4e/btbh-renderer` (commit `bba9f4a`).
- Korisnik je odobrio commit i push nakon svakog završenog koraka.
- Commit poruke završavaju s `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

**Plan:** [docs/plans/2026-10-07-tyrian3d-plan.md](docs/plans/2026-10-07-tyrian3d-plan.md),
milestonei M1–M9. Korisnikove odluke: vjerni remaster, widescreen + HUD overlay, prvo brodovi i
neprijatelji.

## 2. Repozitoriji i okruženje

**Tyrian3D (root)**

- Remote `origin` je `https://github.com/duke4e/Tyrian3D.git`.
- Remote `upstream` je `https://github.com/KScl/opentyrian2000.git`. Puna povijest; klon više nije shallow.

**`external/btbh-renderer`** (git submodule)

- Klonirano iz korisnikove lokalne kopije, zatim je URL prebačen na
  `https://github.com/duke4e/btbh-renderer.git`.
- Branch `tyrian3d` (commit `bba9f4a`, iznad `f75a25f`) je pushan na GitHub.
- Korisnikova radna kopija renderera je
  `~/Documents/GitHub/Be-The-Bullet-Hell/City Generator (r3d)/Vendor/BTBHRenderer`.
  **Nju ne diraj.** Ondje traje drugi aktivni posao. Sve izmjene renderera idu na branch
  `tyrian3d` u ovom submoduleu.

**Ugniježđeni submoduli renderera**

- Inicijalizirani (iz lokalnih kopija):
  - `external/SDL_shadercross`, sa svim podmodulima (DXC, SPIRV-Cross, SPIRV-Tools).
  - `external/raylib`, samo zbog `stb_image`/`stb_truetype`/`cgltf` headera.
- Nisu inicijalizirani: `external/SDL` i `external/assimp`. Umjesto njih koriste se brew SDL3 i brew assimp.

**Ostalo**

- Podaci igre: `data/tyrian2000/`. Gitignorirano; preuzeto iz `https://www.camanis.net/tyrian/tyrian2000.zip`.
- Build direktoriji (gitignorirano):
  - `build/shadercross/`: SDL_shadercross CLI, buildan jednom.
  - `build/game/`: igra (CMake, Debug) i kompajlirani shaderi u `build/game/shaders/`.
- Stroj: macOS 27.0.1, arm64.
- Brew paketi: `sdl3` 3.4.16, `assimp` 6.0.5, `cmake`, `shaderc`, `molten-vk`, `vulkan-loader`.
- Metal toolchain dolazi iz Xcodea (`xcrun metal`).
- Instaliran je i `sdl2-compat`, ali se više ne koristi.

Build i pokretanje:

```bash
cmake -S . -B build/game -DCMAKE_BUILD_TYPE=Debug && cmake --build build/game -j10
```

```bash
build/game/tyrian3d
```

Naredba za build shadercrossa nalazi se u TYRIAN3D.md.

## 3. Što je napravljeno

1. **Port sa SDL2 na SDL3** (preduvjet za SDL_GPU).
   - Prvo su pokrenute SDL-ove `rename_*` skripte, zatim su ručno prepisani audio, joystick,
     eventi i video.
   - Audio koristi `SDL_OpenAudioDeviceStream` s callbackom koji puni postojeći mixer
     (`src/loudness.c`).
   - Konverzija zvučnih uzoraka koristi `SDL_ConvertAudioSamples` (`src/nortsong.c`).
   - Mreža je isključena, jer SDL3_net nije dostupan i `WITH_NETWORK` nije definiran.
   - Softverski scaleri (hqNx i ostali) su uklonjeni. "Scaler" sada samo određuje početnu
     veličinu prozora (`src/video_scale.c`), a zadana je 3x.
2. **Prikaz kroz GPU.** `src/render_gpu.c` koristi `btbh_gpu`:
   - 2D put: palete se pretvaraju u RGBA, a zatim se crta preko canvasa.
   - 3D put: slojevi su ravnine u sceni, a HUD je canvas iznad njih.
3. **Hvatanje slojeva** (`src/layer3d.c`).
   - U glavnoj petlji (`tyrian2.c`) je oko 15 markera `l3d_phase(...)` i `l3d_modify()`.
   - Na kraju svake faze ekran se uspoređuje sa snapshotom. Pikseli koji su se promijenili
     pripadaju sloju te faze.
   - Filteri (water, lava, blur, `JE_darkenBackground`) su "modify" faze. Njihove promjene se
     upisuju u sloj koji posjeduje taj piksel (prati se preko polja `owner`).
   - `JE_filterScreen` se u 3D modu ne primjenjuje na kompozit. Parametri se spremaju i
     primjenjuju kao remap indeksa palete po sloju.
4. **Overscan.**
   - `game_screen` i `VGAScreen2` imaju 64 retka memorije iznad retka 0.
   - Blitteri koriste `surface_pixels_ll()` i `surface_top()` iz `video.h`.
   - Pozadine se u 3D modu crtaju funkcijom `blit_background_rows_3d()` u `backgrnd.c`. Ona
     crta i retke iznad ekrana te jedan stupac tileova lijevo.
   - Uvjeti crtanja neprijatelja u `JE_drawEnemy` su olabavljeni za `screen_overscan_rows`.
5. **Kamera.**
   - Zadano: tilt 20°, FOV 30°.
   - Fit: donji rub playfielda, na visini sloja igrača, popunjava originalnu širinu playfielda.
   - Projekcija je pomaknuta na pravokutnik playfielda u prozoru (`fit_camera()`).
   - Rubovi svijeta se postepeno zatamnjuju (`edge_fade` u `build_layer_atlas()`).
6. **Modeli (PoC2).**
   - Mapiranje je u `assets/models/models.cfg`, a parser u `src/models3d.c`.
   - Hook za neprijatelje je `draw_enemy_model()` u `tyrian2.c`. Ključ je slovo shape filea +
     `egr[0]`, tj. prvi frame animacije, da model ne treperi kad se sprite animira.
   - Hook za igrača je `ship_model` u `mainint.c`. Vrijedi samo za obične brodove (`shipGr_ > 1`).
     Sprite i 2D sjena se tada ne crtaju; nagib dolazi iz `ship_banking`.
   - Objekti (`L3DObject`) se renderiraju kao modeli batchom po materijalu, uz sunce i ambient.
   - Slojevi su u opaque passu s alpha cutoffom, pa se modeli i slojevi ispravno zaklanjaju po dubini.
7. **Kontrole i alati.**
   - F3 prebacuje 3D/2D, F4 uključuje i isključuje modele.
   - PgUp/PgDn mijenja tilt, Home/End FOV, Ins/Del razmak visina slojeva.
   - Tipke se obrađuju u `video_handle_key()`, a poziva ih `keyboard.c`.
   - Env varijable i dev alati su u `src/devtools.c`. Popis je u TYRIAN3D.md.

**Provjereno automatski** (dumpovi frameova iz demo snimke `demo.1`, samo Metal):

- PoC1, overscan i PoC2.
- 2D mod (vizualno isti kao original; nije rađena usporedba piksel po piksel).
- Naslovni ekran.
- Cijena 3D prezentacije je oko 1–2 ms po frameu u Debugu.

**Nije provjereno:**

- Vulkan backend.
- Interaktivno igranje.
- Dva igrača.
- Fullscreen i promjena veličine prozora.
- Joystick.
- Druge epizode i razine s posebnim efektima.

## 4. Karta datoteka

| Datoteka | Uloga |
| --- | --- |
| `CMakeLists.txt` | Builda `btbh_gpu` iz submodulea (brew SDL3 + assimp) i kompajlira produkcijske HLSL shadere renderera (popis se čita iz njegova CMakeLists) u SPIR-V i metallib. Builda i igru. |
| `src/layer3d.[ch]` | Hvatanje slojeva po fazama, objekti modela, nominalne visine slojeva (`layer_info`). |
| `src/render_gpu.[ch]` | Sve vezano uz BTBH: device i prozor, teksture, atlas slojeva, HUD, kamera, batchevi slojeva i modela, osvjetljenje, readback za dumpove. |
| `src/models3d.[ch]` | Parser za `models.cfg` i odabir modela za neprijatelje i igrača. |
| `src/devtools.[ch]` | Env-driven alati: demo nakon N ms, dump frameova i slojeva, izlaz nakon N frameova. |
| `src/video.[ch]` | Prozor (stvara ga renderer), overscan površine, `JE_showVGA` (2D) i `JE_showVGA3D` (3D), tipke za prikaz. |
| `src/tyrian2.c` | Glavna petlja s markerima faza, `JE_starShowVGA` (bira 2D ili 3D prezentaciju), hook za modele neprijatelja. |
| `src/mainint.c` | Hook za model igrača. |
| `src/backgrnd.c` | Overscan crtanje pozadina; presretanje `JE_filterScreen`. |
| `src/sprite.c` | Clipping s overscanom. |
| `assets/models/` | `models.cfg` i Kenney modeli s licencom. |
| `tools/capture_run.sh` | Pokreće igru u demo modu i dumpa frameove (vidi odjeljak 6). |
| `tools/montage.py` | Slaže BMP dumpove u jedan PNG (samo stdlib; PIL nije instaliran). |

## 5. Izmjene u fork rendereru (branch `tyrian3d`, commit `bba9f4a`)

- `include/btbh_gpu/btbh_gpu.h`, `src/gpu/btbh_gpu_texture.c`:
  - `btbh_gpu_window_texture_create_rgba8_ex()`: RGBA tekstura iz memorije, sRGB ili linear, opcionalno s mipovima.
  - `btbh_gpu_texture_update_rgba8()`: streaming upload regije teksture.
- `src/gpu/btbh_gpu_window.c`: `btbh_gpu_window_sdl_window()` vraća `SDL_Window *`.

## 6. Kako testirati

Nema unit testova. Provjera je vizualna, preko dumpova:

```bash
tools/capture_run.sh /tmp/neki/novi/dir 150 900
```

Argumenti su redom izlazni direktorij, svaki N-ti frame i izlaz nakon N frameova. Na kraj se mogu
dodati env varijable, npr. `TYR3D_DUMP_LAYERS=1`, `TYR3D_LOG_ENEMIES=1`, `TYR3D_2D=1` ili `TYR3D_PROFILE=1`.

- Skripta postavlja `TYR3D_DEMO_IDLE_MS=300`, pa demo počinje odmah. Oko frameova 300–1300 je gameplay prve razine.
- U 3D modu frameovi se snimaju GPU readbackom u punoj rezoluciji (1920×1200 na Retini).
- Pretvorba u PNG: `sips -s format png -Z 1000 frame_000600.bmp --out f.png`, ili `tools/montage.py`.
- Koristi novi izlazni direktorij za svaki run. Sigurnosna provjera blokira `rm` s varijablom u putanji.

## 7. Zamke koje su već riješene (nemoj ih ponovno otkrivati)

- Igra se mora buildati s `NDEBUG`, kao upstream. Neki upstream asserti (npr. u `helptext.c`) okidaju na ispravnim T2000 podacima.
- Brewov assimp CMake paket ima hardkodiran `libz.tbd` iz SDK-a koji ne postoji. Zato se assimp linka izravno (`find_library`), a zlib preko `ZLIB::ZLIB`.
- BTBH prozor se po zadanom ne može mijenjati u veličini. U `rgpu_init()` se zove `SDL_SetWindowResizable`.
- Igra sama poziva `SDL_PollEvent` (`keyboard.c`). `btbh_gpu_window_poll_events` se **ne** zove; inače bi pojeo evente.
- Nakon `scene_present` uvijek mora slijediti `canvas_present` u istom frameu. U frameu sa scenom canvas pass ne smije imati `clear_enabled`.
- Nulama inicijaliziran `BTBHGPUSceneGeometryBatch` je nevaljan. Koristi `init_batch()`: stencil "disabled" kombinacija, `material_slot = -1`, boje 255, `uv_scale = 1`.
- Teksture za scenu su sRGB, jer post pass radi linear→sRGB. Canvas teksture su UNORM.
- Batch modela ne uzima materijal sam od sebe. Za svaki materijal je zaseban batch s `material_slot` i `btbh_gpu_model_material_info`.
- Visine slojeva rastu redoslijedom crtanja, najmanje za 0.05 po sloju, da se slojevi iste nominalne visine ne bore u depth bufferu.
- Present mode je IMMEDIATE (nema vsynca). Tempo određuje vlastiti timer igre.
- Readback BMP-a je RGBA; boje su provjerene.

## 8. Poznati problemi

1. **Gornji kutovi su crni** pri većem tiltu. Mapa pozadine je široka samo oko 312–336 px, pa se lijevo i desno nema što dodati. Ublaženo zatamnjenjem rubova.
2. **Razine s posebnim prikazom.** Naopaki prikaz (`starShowVGASpecialCode == 1`) i spotlight (`== 2`) nemaju 3D obradu. U 3D modu se prikazuju normalno.
3. **Mali plavi neprijatelji** u prvoj razini ostaju spriteovi. `TYR3D_LOG_ENEMIES` ih ne prijavljuje kao neprijatelje iz enemy sheeta, pa izvor nije utvrđen. Moguće su enemy shots ili posebni objekti.
4. **Sjene.** Model igrača nema sjenu, jer je 2D sjena isključena kad se crta model. Modeli ne bacaju sjene na tlo.
5. **Neprijatelji koji se okreću** (više sprite frameova za rotaciju) imaju statičan model okrenut prema dolje.
6. **Pikseli iste boje.** Kad sprite iscrta piksel iste boje kakva je već ispod, diff ga ne vidi, pa taj piksel ostaje u nižem sloju. Vizualno je zanemarivo.
7. **Specijalni brodovi.** `shipGr_ 0` i `1` (dvodijelni brodovi, Nortship) uvijek su spriteovi.
8. **Pozadina na rubu mape.** Pozadine koje se ponavljaju (`BKwrap`) mogu na vrhu overscana pokazati nekontinuirani komad mape.

## 9. Predloženi sljedeći koraci (redom)

1. Slijediti plan u `docs/plans/2026-10-07-tyrian3d-plan.md`. Prvi korak je M1.1.
2. Korisnik ručno isproba igru. Kalibrirati zadani tilt, FOV i visine slojeva prema njegovom dojmu (tipke za kameru ispisuju vrijednosti u stdout).
3. Bolji PoC2:
   - Mapiranje po tipu neprijatelja preko `sprite` pravila u `models.cfg`; `TYR3D_LOG_ENEMIES=1` daje popis.
   - Yaw iz indeksa animacijskog framea za rotirajuće neprijatelje.
4. Sjene: osvijetljen sloj tla koji prima sjene i directional shadow map u BTBH-u (`lighting.directional_shadow_*`).
5. Metci, power-upi i eksplozije kao 3D ili čestice (sada su spriteovi u sloju `player`/`explosion`).
6. Razine s posebnim efektima iz odjeljka 8.2.
7. Faza 3: vlastiti modeli po uzoru na originalne spriteove; tileovi pozadine u većoj rezoluciji ili 3D teren.
8. Isprobati Vulkan (`TYR3D_GPU_BACKEND=vulkan`, na macOS-u preko MoltenVK) i build na Windowsu/Linuxu. Za Windows treba riješiti izvor SDL3 i assimp, npr. vendored submodule renderera.

## 10. Memorija

Postoje zapisi u `~/.claude/projects/-Users-duke4e-Documents-GitHub-Tyrian3D/memory/`:
`tyrian3d-project.md` (ciljevi i pravila arhitekture) i `btbh-renderer.md` (gdje je renderer i što se ne dira).
