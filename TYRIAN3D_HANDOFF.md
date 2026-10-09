# Tyrian3D: predaja rada

Datum predaje: **2026-10-07**, ažurirano istog dana nakon M1, M2.1 i 3D pozadine. Ovo je
početna točka za novog agenta, bez potrebe za starim razgovorom. Putanje su relativne prema rootu repozitorija
`/Users/duke4e/Documents/GitHub/Tyrian3D`, osim ako je navedeno drukčije.

Najprije pročitaj ovaj dokument, zatim [TYRIAN3D.md](TYRIAN3D.md) (build, kontrole i opis
arhitekture za korisnika).

## 1. Zadatak i stanje koje preuzimaš

Cilj: OpenTyrian2000 prenijeti u 2.5D/3D tako da logika igre ostane identična originalu.
Mijenja se samo prikaz. Korisnik je zadao ove faze:

1. **PoC1**: originalni spriteovi u 3D perspektivi prihvatljivoj za vertikalni shmup. **Gotovo.**
2. **PoC2**: besplatni modeli umjesto spriteova, samo da se dobije osjećaj. **Gotovo** (Kenney Space Kit).
3. Kasnije: vlastiti modeli po uzoru na originalne spriteove i rekonstrukcija ostale grafike
   (pozadine, efekti). **U tijeku**, po planu u `docs/plans/` (odjeljak 9 dolje).

Korisnikove odluke:

- C + Vulkan/Metal, a ne prepisivanje u Godot ili Unity.
- Grafička baza je korisnikov BTBH renderer: r3d fork s backendom na SDL3 SDL_GPU, Metal i Vulkan.
- Korisnik je odobrio preuzimanje Tyrian 2000 podataka (freeware, camanis.net).
- Kenney modeli nisu preuzimani s interneta. Kopirani su iz korisnikova lokalnog projekta
  (`~/Documents/GitHub/QIX Rouguelike (GPT 5.3)/assets/kenney/space-kit`), CC0.
- Volumetrijski spriteovi (M2.1) su odobreni i zadani su prikaz za sve bez ručnog modela
  ("dobro je, kasnije lako to tweakamo").
- Blender je odobren za modeliranje. Već je instaliran: `/Applications/Blender.app`, 5.2.2 LTS.
- Renderer igre ne smije biti ograničen na staru 2D kameru: sve što 3D kamera vidi mora biti
  nacrtano (riješeno za pozadine, odjeljak 3.10).

**Git (stanje 2026-10-07):**

- PoC je na branchu `tyrian3d/poc` repoa `https://github.com/duke4e/Tyrian3D`. Repo je privatan.
- Rad na planu ide na branch `tyrian3d/m1-tools` (M1.1/M1.2, M1.4/M2.1, 3D pozadine). Još nije
  spojen u `tyrian3d/poc`.
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
7. **Kontrole i alati (PoC).**
   - F3 prebacuje 3D/2D, F4 uključuje i isključuje modele.
   - PgUp/PgDn mijenja tilt, Home/End FOV, Ins/Del razmak visina slojeva.
   - Tipke se obrađuju u `video_handle_key()`, a poziva ih `keyboard.c`.
   - Env varijable i dev alati su u `src/devtools.c`. Popis je u TYRIAN3D.md.

8. **Dev alati (M1.1, M1.2).** `TYR3D_START=<epizoda>:<sekcija>` pokreće razinu bez izbornika,
   `TYR3D_AUTOPILOT` i `TYR3D_GODMODE` igraju sami. `tools/sweep.sh` prolazi sve razine i slaže
   contact sheet po razini. `TYR3D_EXTRACT=<dir>` (`src/extract.c`) izvozi sheetove i katalog
   neprijatelja; `tools/catalog_html.py` od njega radi HTML stranicu.
9. **Izgled objekata (M1.4, M2.1).** `models.cfg` v2: model, `volume` ili `sprite` po pravilu;
   pravila po brodu (`ship`), `default`, opcije `yaw=` (fiksno, `velocity`, `aim`, `frames:`),
   `height=`, `banking=`. F5 ponovno učitava datoteku, `TYR3D_MODEL_CONFIG` bira drugu
   (`models_kenney.cfg` je PoC2). Volumetrijski spriteovi (`src/volume3d.c`): silueta spritea se
   napuhne u zaobljeni reljef sa zidovima do baze i teksturom samog spritea; zadani su prikaz.
   Sjenčanje od sunca zapečeno je u boje vertexa i crta se unlit, pa ploha okrenuta prema gore
   ima točno boje spritea. Zemaljski objekti (stil FLAT) su gotovo ravni, bez zaobljenog ruba.
   `tools/modelkit` je stdlib Python generator `.glb` modela.
10. **Pozadine u 3D-u (`src/background3d.c`).** Igra crta samo tileove koji stanu na njen ekran,
    a nagnuta kamera vidi puno više. Zato 3D prikaz sam crta sve tri pozadinske mape kao tileove
    na ravnini svake pozadine, za cijelo područje koje kamera vidi (`plane_footprint()`, do 640 px
    naprijed, pa se gase).
    - Svako crtanje pozadine u igri zapisuje stanje scrolla (`l3d_add_background()` u
      `backgrnd.c`), pa se tileovi poklapaju s crtežom igre. Redovi iznad prate `BKwrap` petlje.
    - Izvan bočnih rubova mapa se nastavlja zrcaljeno i postupno tamni (gradijent preko tilea).
    - Unutar igrališta snimljeni sloj se crta iznad tileova (tileovi su 0,05 ispod sloja), pa su
      filteri igre tamo točni. Izvan igrališta tileovi ih aproksimiraju mapiranjem palete:
      miješana pozadina 2 (`draw_background_2_blend`, uz prosječnu svjetlinu tla razine), voda,
      lava, led (`l3d_add_effect()`).
    - Atlas tileova (`b3d_build_atlas()`) ima 4 stranice obojene različitim paletama; tileovi
      se crtaju instancirano, batch po ćeliji atlasa.
    - Staro crtanje pozadina u overscan je uklonjeno; overscan od 64 reda ostaje za spriteove.

**Provjereno automatski** (dumpovi frameova iz demo snimke `demo.1`, samo Metal):

- PoC1, overscan i PoC2.
- 2D mod (vizualno isti kao original; nije rađena usporedba piksel po piksel).
- Naslovni ekran.
- Cijena 3D prezentacije je oko 1–2 ms po frameu u Debugu.

**Nije provjereno:**

- Interaktivno igranje (provjere su automatske: autopilot, dumpovi frameova).
- Fullscreen i promjena veličine prozora.
- Joystick.
- Galaga mod (tajna razina).

## 4. Karta datoteka

| Datoteka | Uloga |
| --- | --- |
| `CMakeLists.txt` | Builda `btbh_gpu` iz submodulea (brew SDL3 + assimp) i kompajlira produkcijske HLSL shadere renderera (popis se čita iz njegova CMakeLists) u SPIR-V i metallib. Builda i igru. |
| `src/layer3d.[ch]` | Hvatanje slojeva po fazama, objekti (modeli, volumetrijski spriteovi), zapisi pozadina i filtera, nominalne visine slojeva (`layer_info`). |
| `src/render_gpu.[ch]` | Sve vezano uz BTBH: device i prozor, teksture, atlas slojeva, HUD, kamera i njeno vidno polje na ravnini (`plane_footprint`), batchevi slojeva, tileova pozadine, modela i volumena, osvjetljenje, readback za dumpove. |
| `src/background3d.[ch]` | Pozadinske mape u 3D-u: atlas tileova, odabir tileova za zadano područje (scroll, `BKwrap`, zrcaljenje izvan mape), mapiranje palete za miješanje i filtere. |
| `src/volume3d.[ch]` | Volumetrijski spriteovi: dekodiranje sheeta i generiranje mesha iz spritea. |
| `src/models3d.[ch]` | Parser za `models.cfg` (v2) i izbor izgleda za neprijatelje i brodove. |
| `src/devtools.[ch]` | Env-driven alati: demo nakon N ms, dump frameova i slojeva (uz ispis zapisa pozadina), izlaz nakon N frameova, start razine, autopilot, godmode. |
| `src/extract.[ch]` | `TYR3D_EXTRACT`: izvoz sheetova u PNG i katalog neprijatelja/brodova u JSON. |
| `src/video.[ch]` | Prozor (stvara ga renderer), overscan površine, `JE_showVGA` (2D) i `JE_showVGA3D` (3D), tipke za prikaz. |
| `src/tyrian2.c` | Glavna petlja s markerima faza, `JE_starShowVGA` (bira 2D ili 3D prezentaciju), hook za modele neprijatelja. |
| `src/mainint.c` | Hook za model igrača. |
| `src/backgrnd.c` | Zapisi crtanja pozadina i filtera za 3D (`l3d_add_background`, `l3d_add_effect`); presretanje `JE_filterScreen`. |
| `src/sprite.c` | Clipping s overscanom. |
| `assets/models/` | `models.cfg` (zadano: volumetrijski), `models_kenney.cfg` (PoC2) i Kenney modeli s licencom. |
| `tools/capture_run.sh` | Pokreće igru u demo modu i dumpa frameove (vidi odjeljak 6). |
| `tools/sweep.sh`, `tools/levels.py` | Sweep svih razina (autopilot, godmode) i popis sekcija razina. |
| `tools/catalog_html.py` | HTML katalog neprijatelja iz `TYR3D_EXTRACT` izvoza. |
| `tools/modelkit/` | Stdlib Python: `.glb` writer i proceduralni oblici. |
| `tools/blender/` | Blender pipeline: `tyrkit.py` (konvencije, materijali, loft, izvoz, pregledi), `glb_winding.py`, modeli u `models/` (npr. `ships/talon.py`). |
| `tools/montage.py` | Slaže BMP dumpove u jedan PNG (samo stdlib; PIL nije instaliran). |

## 5. Izmjene u fork rendereru (branch `tyrian3d`)

- `include/btbh_gpu/btbh_gpu.h`, `src/gpu/btbh_gpu_texture.c`:
  - `btbh_gpu_window_texture_create_rgba8_ex()`: RGBA tekstura iz memorije, sRGB ili linear, opcionalno s mipovima.
  - `btbh_gpu_texture_update_rgba8()`: streaming upload regije teksture.
- `src/gpu/btbh_gpu_window.c`: `btbh_gpu_window_sdl_window()` vraća `SDL_Window *`.
- `unlit_enabled = 2`: unlit površine koje primaju sjenu primarnog directional svjetla (45 % svjetla u sjeni); shadow mapa 2048.
- Površina `BTBH_GPU_SCENE_SURFACE_GLINTS` (6): sunčevi odsjaji na valovima, maska u plavom kanalu ORM teksture.
- Bloom u post lancu (`BTBHGPUScenePost.bloom_*`, shaderi `production_bloom_{down,up,composite}`): prag sa
  soft kneeom i Karisovim prosjekom, šest polovičnih razina dolje i natrag gore (tent filter), zbroj se dodaje
  sceni prije tonemappinga. `bloom_intensity` 0 ga gasi.
- Reljef unlit površina iz svjetline teksture: negativan `normal_scale` (pozadine s postavkom Effects, `BACKGROUND_RELIEF`) — normala iz razlike svjetline susjednih piksela (vodoravna površina, u uz +X, v uz +Z); vidi se samo pod točkastim svjetlima.
- Do osam točkastih svjetala bez sjena (`BTBHGPUSceneLighting.point_lights`, `point_light_count`): pozicija, radijus,
  boja, energija; u konstantama shadera prije polja za sjene (isti raspored za varijante sa sjenama i bez). Osvjetljavaju
  lit površine (difuzno, omekšano: i strana okrenuta od svjetla dobiva 30 %) i posvjetljuju unlit površine (tlo).

## 6. Kako testirati

Nema unit testova. Provjera je vizualna, preko dumpova:

```bash
tools/capture_run.sh /tmp/neki/novi/dir 150 900
```

Argumenti su redom izlazni direktorij, svaki N-ti frame i izlaz nakon N frameova. Na kraj se mogu
dodati env varijable, npr. `TYR3D_DUMP_LAYERS=1`, `TYR3D_LOG_ENEMIES=1`, `TYR3D_2D=1` ili `TYR3D_PROFILE=1`.

- Skripta postavlja `TYR3D_DEMO_IDLE_MS=300`, pa demo počinje odmah. Oko frameova 300–1300 je gameplay prve razine.
- Za određenu razinu: `TYR3D_START=1:3 TYR3D_AUTOPILOT=1 TYR3D_GODMODE=1` (sekcije daje `tools/levels.py`; Timed Battle sekcije nisu na popisu, jer bez pripreme tog načina igre vise).
- Sve razine: `tools/sweep.sh <dir> [epizoda...]`, contact sheet po razini (oko 40 minuta za 68 razina na 4K prozoru). Zadnji sweep (2026-10-07): sve razine rade, bez rušenja.
- `TYR3D_BACKGROUNDS=13` crta tileove samo za navedene pozadine, za izoliranje grešaka.
- Skripta postavlja i `TYR3D_WINDOWED=1`: igra radi u malom prozoru u donjem desnom kutu, ne uzima fokus i ne pauzira bez njega, pa ne smeta korisniku dok radi. Nikad ne pokreći testove u fullscreenu. (Skriveni prozor ne radi: bez prikazanog prozora nema swapchaina.)
- U 3D modu frameovi se snimaju GPU readbackom u punoj rezoluciji prozora (prozor 3x je 960×600 točaka, na Retini 1920×1200).
- `TYR3D_SHIP=<1-18>` uz `TYR3D_START` bira brod (brojevi kao u shopu).
- Ne pokreći dvije instance igre istovremeno (sweep i ručni capture se ne smiju preklapati).
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
- Visine slojeva rastu redoslijedom crtanja, najmanje za 0.1 po sloju (`LAYER_STEP`), da se slojevi iste nominalne visine ne bore u depth bufferu. Tileovi pozadine su 0.05 ispod svog sloja.
- BTBH-ov lit put (PBR) dodaje ambijent ("multiple scattering") i spekular neovisno o albedu, pa
  tamne boje postaju sivkaste. Gdje boje moraju ostati vjerne (volumetrijski spriteovi), crta se
  unlit, a sjenčanje se peče u boje vertexa.
- **Namotaj trokuta modela.** BTBH-ova scena uzima trokute u smjeru kazaljke na satu kao prednja lica statičkih modela, a normale stražnjih lica okreće. glTF koristi suprotan smjer, pa su svi modeli (i Kenney) bili osvijetljeni iznutra: sunce na njih nije djelovalo. `tools/blender/glb_winding.py` okreće namotaj (izvoz iz `tyrkit` to radi sam; Kenney modeli su okrenuti jednom). Pazi: Blender dijeli index buffer među meshovima iste topologije.
- **Rasvjeta modela.** Sunce 4,0 iz gornjeg lijevog kuta ekrana (kao na spriteovima) i IBL proceduralno nebo (`set_environment`, SH9 irradijancija računata na CPU-u) skalirano na 0,3 (`SKY_FILL`), za kontrast kakav imaju spriteovi; `ambient_energy` uz IBL ne djeluje. Refleksije neba su prigušene (0,3), jer bi tamne boje posivjele. Bez mape okoline metal je taman, zato su materijali uglavnom dielektrici. Ploha okrenuta gore dobiva oko 1,16× albedo (`MODEL_UP_FACING_LIGHT`; `tyrkit.material()` uzima boju kakva se vidi u igri). Provjera: srednja svjetlina modela prema spriteu (bez obruba) u pregledniku je 0,97.
- **Boje modela iz palete.** Igra levele igra u paleti 5 (`pcxpal[2]`, paleta HUD slike), a ne 0. Materijali `ime@indeks` (`tyrkit.material(palette=...)`) dobivaju boju iz trenutne palete u svakom frameu (`read_palette_materials`, cgltf čita imena), pa prate fadeove i filtere.
- **Galerija brodova u levelu je varljiva:** prvih ~100 tickova igrač je neranjiv (sprite se crta poluprozirno, model "bljeska" 2,5×), a `constantPlay` (TYR3D_START) sam pomiče brod i puca. Za usporedbu modela i spriteova koristi `TYR3D_VIEWER=ships`.
- BTBH nema UV po instanci (`uv_transform` je po batchu), zato tileovi pozadine idu u batch po ćeliji atlasa. Boja instance (`instance.color`) množi boju, što se koristi za tamnjenje.
- Present mode je IMMEDIATE (nema vsynca). Tempo određuje vlastiti timer igre.
- Readback BMP-a je RGBA; boje su provjerene.

## 8. Poznati problemi

1. **Razine s posebnim prikazom (M4.4).** Naopaki prikaz (`starShowVGASpecialCode == 1`, npr. LAVA RUN i EYESPY u epizodi 4) zrcali pogled okomito u `fit_camera`; modeli se pritom zrcale lijevo-desno, pa izgledaju okrenuto (kao spriteovi) a lica im ostaju ispravno orijentirana za osvjetljenje. Tekstovi u igralištu (bodovi, traka bossa) namjerno ostaju čitljivi; original ih okreće. Spotlight (`== 2`, npr. ASSASSIN) je crni overlay preko prozora po formuli iz `JE_starShowVGA` (`build_spotlight`). Katalog (`TYR3D_EXTRACT`) navodi razine s posebnim prikazom i vrijeme događaja (`special_views`).
2. **Mali plavi neprijatelji** u prvoj razini ostaju spriteovi. `TYR3D_LOG_ENEMIES` ih prijavljuje sa sheetom `'?'` (nisu iz enemy shape filea), pa za njih ne vrijede pravila iz `models.cfg`.
3. **Sjene (M5.4).** Modeli i volumetrijski spriteovi bacaju sunčevu sjenu (directional shadow mapa 2048, ortografska, pokriva tlo oko igrališta: `shadow_view_projection`). Slojevi, tileovi i volumeni su unlit, pa je primaju preko `unlit_enabled = 2` (renderer, branch `tyrian3d`: u sjeni zadržavaju 45 % svjetla). Slojevi ne bacaju sjenu (shadow pass ne radi alpha test, pa bi bacali cijeli pravokutnik), pa je nemaju ni metci ni eksplozije. Sjena visokih objekata pada daleko (igrač je 44 px iznad tla). `TYR3D_SHADOWS=0` ih gasi. Originalna 2D sjena broda ostaje isključena kad se crta 3D izgled.
4. **Pikseli iste boje.** Kad sprite iscrta piksel iste boje kakva je već ispod, diff ga ne vidi, pa taj piksel ostaje u nižem sloju. Za pozadine to više ne vrijedi (tileovi su ispod snimljenog sloja). Vizualno je zanemarivo.
5. **Dvodijelni brodovi.** `shipGr_ 0` (Dragonwing, brod drugog igrača; u `models.cfg` `ship dragonwing`) i `1` (Nort Ship) imaju modele centrirane na par polovica, kao ostali brodovi; bez modela dobivaju volumen polovicu po polovicu (`two_part_volume` u `mainint.c`). Bočni potisnici Nort Shipa i NortSparks ostaju 2D. Preglednik (`TYR3D_VIEWER=ships`) ih prikazuje u dvostrukoj ćeliji.
6. **Filteri i miješanje izvan igrališta.** Pozadine koje igra filtrira (lava, voda, led) ili miješa s onim ispod (`draw_background_2_blend`, npr. voda u razini 1), i sve ispod njih, komponiraju se na CPU-u za vidljivo područje i prolaze kroz iste formule kao `lava_filter`/`water_filter` (`b3d_compose`), pa nema šava na rubu igrališta. Preostale razlike: igra za piksel iznad čita prošli frame (ovdje nefiltrirani piksel), vremensko zamućenje leda i blura je izostavljeno, a miješana pozadina 2 nacrtana nakon filtera miješa se samo s komponiranim pozadinama ispod (ne sa spriteovima i pozadinom 3). Trošak: oko 1–2 ms po frameu na tim razinama (RelWithDebInfo). `JE_darkenBackground` (SuperWild) i "astral" stanje izvan igrališta nisu preneseni.
7. **Boja 0 pozadine 1 je prozirna** (kroz nju se vide zvijezde, kao u igri). Izvan igrališta se ondje vidi crna boja clear-a, a ne boja palete 0 (koja je inače crna).
8. **Daljina iznad ekrana.** Igra stvara neprijatelje tek kad skrol dođe do njihovog eventa, na crti iznad ekrana (y = −28), a metke briše čim izađu iz ekrana. 3D pogled vidi dalje, pa: neprijatelji iz eventa sljedećeg dijela mape prikazuju se unaprijed, gdje bi bili da već postoje, kako se kreću prema mjestu nastanka (`draw_coming_enemies`; samo čitanje eventa, bez RNG-a; nasumično postavljeni se izostavljaju; eventi 6/7/10/12/15, "custom" 49–52, oni koji dolaze odozdo 17/18/23/32/56, i na sporo skrolajućim mapama; eventi dolaze na početku ticka, prije pomaka mape, pa je predviđeni neprijatelj točno tick pomaka prije prve prave pozicije; novi neprijatelj odmah dobiva svoju brzinu za frameove između tickova (`l3d_new_object_velocity`); `TYR3D_LOG_SPAWNS` pokazuje što je promašeno i gdje je bio prikazan — na 1:1, 2:1, 3:1, 4:1 ostaju samo neprijatelji sa starta razine, oni izvan pogleda i oni koje igra stvara usred ekrana); igračevi metci koji izađu kroz vrh nastavljaju let dok ne odu daleko (`l3d_shot_departed`). Na razinama s filterima (lava, voda, led) rub igrališta prelazi ditheringom u rekonstrukciju filtera izvan njega, pa nema pravokutnog šava.
9. **HUD (M4.1/M4.2, iteracija 1).** U 3D-u panel HUD-a stoji uz desni rub prozora, visok koliko prozor, a igralište je najveće što stane pored (`layout_3d`); traka s porukama ispod igrališta se ne crta, nego se poruka (`text_window_message`) ponovno iscrta tekstom u dnu igrališta. Isto vrijedi za dva igrača (njihov ekran ima isti raspored). Iteracija 2 (upscale Lady0101 u `upscale/out`; zelene oznake i njihove kutije uvijek su iz igre jer ih upscaler razmaže): panel se crta u 4× rezoluciji (Scale2x dvaput, linearni filter, `hud_panel_hd`); ako postoji upscalana slika panela (`upscale/out/hud_1p.png` / `hud_2p.png`, izvezene u katalogu kao `sheets/hud_*.png` iz slika 3/6 `tyrian.pic` i kopirane u `upscale/in` alatom `make_atlases.py`), crta se ona, a preko nje samo pikseli panela koji se razlikuju od originalne slike (mjerači, tekst, oružja; `load_panel_art`). Mjerači su i dalje igrini pikseli; mogli bi se crtati izravno iz stanja igre.
10. **Stanja (M5.2).** Neranjivi brod je poluproziran kao u originalu (`l3d_ghost_last_object`; batch s `transparency_enabled` i pola alfe). Sprite filter (pogođeni neprijatelji, led, Magneto: `blit_sprite2_filter`, indeks = filter | nijansa) primjenjuje se točno: paletni materijali modela uzimaju `filter | (indeks & 0x0f)`, a volumeni dobivaju filtriranu varijantu teksture sheeta (`filtered_volume_texture`). Ne-paletni (emisivni) materijali se ne mijenjaju.
11. **Strane mape (WFC).** Stupci uz mapu (16 sa svake strane) generiraju se iz tileova same mape (`src/wfc.c`, `make_sides` u `background3d.c`) unaprijed za sve razine (`tools/precompute_sides.sh` → `assets/sides`, zlib, oko 0,5 MB); ako ih nema, pri učitavanju razine (`b3d_prepare_sides` u `JE_loadMap`) uz keš u `~/.config/opentyrian2000/tyrian3d-sides/` (ime = hash mape i postavki; promjena algoritma traži novi `SIDE_CACHE_VERSION` i ponovni precompute). Prvo generiranje traje oko 0,2–0,4 s po pozadini u Debug buildu. Trake od 24 reda rješavaju se redom; ako ne uspiju, pokušava se bez veze s trakom iznad, pa bez veze s rubom mape, a tek onda zrcaljenje. Šav nastaje na mjestima petlje mape (BKwrap) i između traka koje nisu vezane.

12. **Particlei i svjetla eksplozija (M7).** `src/particles3d.c`: svaka eksplozija (`JE_setupExplosion`) u 3D-u dobiva bljesak, iskre, dim i na tlu krhotine; originalni sprite eksplozije ostaje. Bljesak je i kratko točkasto svjetlo (`p3d_lights`; četvrtine velike eksplozije spajaju se u jedno jače, gasne kroz 6–12 frejmova, putuje s eksplozijama); osam najjačih osvjetljava scenu (`add_explosion_lights`, poravnato kao sve ostalo), s postavkom Effects. `TYR3D_EXPLOSION_LIGHTS=0` ih gasi, `TYR3D_TEST_LIGHT` dodaje jedno za provjeru. Vlastiti RNG (ne dira `mt_rand`), pomiču se s `explodeMove`, crtaju se kao billboardi (aditivno i alfa, `transparency_enabled`, ne bacaju ni primaju sjenu). Izgled je prva procjena; treba ga dotjerati po dojmu. **Kasnije:** eksplozije su samo particli (sprite se u 3D-u ne crta kad `p3d_explosion` vrati true, polje `particles` u `Explosion`): vatrena kugla (`P3D_FIRE`, tekstura `fire_texture`, kvadratno gašenje), žar, udarni prsten koji leži na tlu (`P3D_RING`, na velikim eksplozijama), dimni stup (`P3D_SMOKE`, rotira); vatra, sjaj i prsten crtaju se bez depth testa (ne reže ih teren), dim s njim.

13. **Sjaj metaka i odsjaji na vodi (M7, M8).** Svaki metak (igračev i neprijateljski) bilježi `l3d_add_glow` (boja = najsvjetliji piksel spritea, indeks palete), a renderer crta aditivni billboard. Voda u pozadinskim slojevima (tlo, pozadine 2 i 3), u tileovima i u komponiranim pozadinama dobiva sunčeve odsjaje na animiranim valovima (u prvoj razini voda je pozadina 2, ne tlo): nova površina `BTBH_GPU_SCENE_SURFACE_GLINTS` u rendereru (branch `tyrian3d`) dodaje odsjaj na boju (radi i za unlit) gdje plavi kanal ORM teksture kaže; maske vode (`layer_water`, `tile_water`) računaju se iz boje piksela (plavo do cijan, `water_color`). Oboje se gasi postavkom Effects.
14. **Postavke (M4.3).** `src/settings3d.c`: izbornik Setup → 3D (prikaz, objekti, sjene, efekti, kamera: Standard/Steep/Overhead), sekcija `[tyrian3d]` u `opentyrian.cfg`; env varijable ih nadjačavaju; F3/F4 ih mijenjaju.
15. **Predmeti (M5.3).** Novčići, dragulji, kristali, data cubeovi, oklop, power-up kapsule i ljubičasta kugla imaju modele (`tools/blender/models/items`). Pravila `sprite coins …` / `sprite powerups …` u `models.cfg` (u kodu slova `$` i `+`, `enemy_sheet_letter`); jedan sivi model po vrsti dobiva boju trenutnog frejma spritea (`color=sprite`: rampa glavne boje kao sprite filter, pa data cube mijenja boje kao u originalu), `spin=` ih okreće (`l3d_frame_number`), `glow` dodaje svjetlo u boji rampe. Novčići se prevrću (`roll=frames:12`), kristali kotrljaju, dragulji okreću s iskrom. Katalog (`TYR3D_EXTRACT`) sada navodi i predmete koje ostavljaju uništeni neprijatelji (sloj `drop`: eventi 33/45/85, `eenemydie`, nasumične zamjene 533/534, brod s oklopom 560). Oružja u kuglama (powerups sheet) i posebna oružja ostaju volumetrijski spriteovi. Renderer diže modele koji bi zbog rotacije zašli ispod tla (`reach` u `add_object_batches`).
16. **Bloom i duboki svemir (M7, M8).** Bloom u forku (odjeljak 5) uključen je s postavkom Effects: prag 1.0, pa svijetli samo ono što scena pokaže svjetlije od bijele (aditivni sjajevi, bljeskovi eksplozija, emisija, odsjaji); boje palete nikad ne prelaze bijelu, pa tlo, spriteovi i HUD ne cvjetaju (`TYR3D_BLOOM`). U svemiru (zvjezdano polje igre je uključeno) boja 0 sloja sa zvijezdama je prazan prostor kroz koji se vidi duboko zvjezdano polje: tri sloja proceduralnih zvijezda 40–340 px ispod tla, skrolaju brzinom zvijezda igre, pa dublji izgledaju sporiji (`add_deep_star_batch`). Isto s postavkom Effects.
17. **Zvučni efekti (M10).** `TYR3D_EXPORT_SFX=<dir>` izvozi 40 zvukova (31 efekt, 9 glasova) kao WAV; igra učitava istoimene WAV-ove iz `sfx` uz podatke igre (`data/tyrian2000/sfx`), osim uz `TYR3D_ORIGINAL_SFX=1`. `tools/upscale_sfx.py` ih provlači kroz AudioSR (48 kHz, ista duljina, glasnoća po RMS-u, tišina gdje je original tih). AudioSR je u venvu `~/Library/Caches/Tyrian3D/audiosr` (Python 3.11; scipy 1.14.1, numpy 1.23.5, setuptools<81, matplotlib 3.9, contourpy<1.3; torchaudio.load zamijenjen soundfileom jer novi torchaudio traži TorchCodec), model u `~/.cache/huggingface` (~5,8 GB). Upscalani zvukovi su izvedeni iz podataka igre, pa nisu u gitu; za `.app` ih treba kopirati u `sfx` uz podatke.
18. **Glatkoća i input.** Logika igre ostaje na svom fiksnom ticku (~35 Hz pri normalnoj brzini). U 3D-u igra čeka sljedeći tick na početku ticka (`video_wait_tick_3d` na vrhu `level_loop`), a ne između crtanja i prikaza, pa se nacrtano prikaže odmah (input kasni tick manje); tempo drži `setDelayContinued`. Dok čeka, zadnji frame se prikazuje ponovno na refreshu monitora (`rgpu_present_3d_ahead`), pomaknut za dio ticka: mape po brzinama skrolanja (`backMove*`), sloj eksplozija po `explodeMove`, objekti s ključem po brzini iz prošlog frejma (`l3d_key_last_object`: neprijatelji, predmeti i njihov sjaj), čestice i duboke zvijezde. Brod igrača i sidekickovi imaju ključ (brod ima zamah, pa je ekstrapolacija blizu); metci (igračevi i neprijateljski) su u 3D-u ravni volumetrijski spriteovi sa sjajem i pravom sjenom umjesto 2D sjene (`l3d_add_shot`), pa se i oni kreću glatko. Pikseli u slojevima (eksplozije osim drifta, posebni metci) ostaju na ticku. Pokazivač miša je sistemski (slika iz igre, `mouse_frame_shown`), pa prati miš brzinom sustava. Miš u igri (relativni) zbraja SDL-ove pomake u decimalnim točkama i čuva ostatak ispod piksela (prije se svaki pomak skraćivao na cijelu točku, a ispod ~5 točaka po ticku pomak se gubio), u mjerilu igrališta 3D pogleda (`video_window_points_per_pixel`). Postavka Mouse (Setup → 3D, `[tyrian3d] mouse`, `TYR3D_MOUSE`): Direct (zadano) stavlja brod (centar) točno gdje je sistemski pokazivač, projiciran na ravninu igrača kroz kameru (`rgpu_window_to_playfield`); pokazivač je skriven i zadržan u prozoru (mouse grab, ne relativni mod), pa se kreće točno kao na desktopu (brzina, akceleracija, rubovi). Nema originalnog ograničenja brzine (¼ pomaka, najviše 8 px po ticku) ni zamaha. Kad brod pomakne nešto drugo (tipkovnica, respawn), pokazivač se premjesti na brod (`mouse_place_pointer`), pa brod ne skoči. Između tickova brod se crta gdje je pokazivač (`player_pointer_lead`, `l3d_pointer_lead`). Original ostaje kao opcija. Scena se renderira u veličini prozora u točkama (na 4K/retina pola piksela po osi) i Lanczosom skalira; HUD ostaje u punoj rezoluciji (`TYR3D_RENDER_SCALE`). Na 4K je GPU bio usko grlo (2–2,6 frejmova po ticku umjesto 3); sad 3,0 pri 48 Hz igre i 144 Hz ekrana, frame oko 0,5 ms.
19. **Glazba kao MIDI (M10).** `src/music_midi.c` prevodi OPL registre koje LDS player piše u MIDI događaje (isti prevoditelj koristi izvoz `TYR3D_EXPORT_MUSIC`) i u stvarnom vremenu ih svira kroz TinySoundFont (`external/tinysoundfont`, MIT) sa SoundFontom GeneralUser GS (`data/soundfonts`, `tools/fetch_soundfont.sh`; u `.app` ide u `Resources/soundfonts`). Petlje, promjene pjesama i fade ostaju igrini; postavka Sound → Music (SoundFont/AdLib), `[tyrian3d] music`, `TYR3D_MUSIC=midi|opl`. Programi, velocity i transpozicija su iz LDS instrumenata (midinst, midvelo, midtrans) — po sluhu se mogu mijenjati.
20. **Poravnanje slojeva.** Slojevi su ravnine na različitim visinama, pa bi ista pozicija igre u perspektivi bila na različitim mjestima ekrana (metci i eksplozija turreta pored turreta). Svaka ravnina (i sve na njoj: tileovi, modeli, volumeni, sjaj, čestice) skalira se oko točke ispod kamere omjerom udaljenosti od kamere prema ravnini igrača (`aligned` u `write_instance`), pa se pozicija na bilo kojem sloju vidi gdje je i u igri; dubina i dalje odlučuje što je ispred, a svjetlo i sjene su 3D. Iznimke u svjetskim koordinatama: duboke zvijezde i sjenovna kamera. `TYR3D_LAYER_PARALLAX=1` vraća ravnine bez skaliranja.

21. **Dijelovi velikih neprijatelja i bossova.** Neprijatelj iste veličine odmah do drugoga, u istoj grupi slotova, čiji sprite se s ovim spaja duž većeg dijela zajedničkog ruba, nastavlja ga: volumetrijski spriteovi tu nemaju zaobljeni rub ni zid (`enemy_open_sides`, `V3D_OPEN_*`, `v3d_sprite_edges`), pa bossovi složeni od dijelova nemaju žljebove na spojevima. Mesh se kešira i po otvorenim stranama.
22. **Superpixeli i iskre.** `JE_drawSP` u 3D-u ne mijenja piksele nego bilježi sjaj u boji iskre (`l3d_add_color_glow`), koji se kreće između tickova i gasne kao pikseli.
23. **Modeli neprijatelja.** Epizoda 1: oko 30 tipova (50 % pojavljivanja); epizode 2–5: svaki tip koji se pojavljuje više od 100 puta (osim plamenova, lave i dijelova velikih struktura, koji namjerno ostaju volumetrijski). Skripte u `tools/blender/models/enemies` (`blocks`, `jets`, `rounds`, `misc`, `later_episodes`); siluete iz spriteova (`tools/blender/silhouette.py`: obrub piksela pojednostavljen Douglas-Peuckerom). Pregled bez igre: učitati GLB-ove u Blender i renderirati odozgo.
24. **Sweep (M9).** `tools/sweep.sh` igra svaku sekciju epizoda s autopilotom; log razine (`level: ...`) iz `tyrian2.c`.
25. **Oblaci (M8).** Tileovi pozadina 2 i 3 koji su svijetli, mekih boja i bez tamnog obruba (`b3d_tile_is_cloud`; u praksi oblaci SAVARE — voda razine 1 i WINDY je miješana pozadina 2, pa je izuzeta) postaju volumetrijski "puffovi": tileovi složeni kao 2x2 spriteovi (`b3d_tile_sprites`) idu kroz isti graditelj kao spriteovi, spojeni sa susjednim oblačnim tileovima (otvorene strane), na visini svog sloja, i bacaju sjenu; njihovi pikseli u igralištu se izostavljaju iz sloja (`b3d_cloud_mask`). Samo za pozadine koje nisu miješane ni filtrirane, s postavkom Objects. `TYR3D_LOG_CLOUDS` ispisuje klasifikaciju.

26. **Uljepšavanje (2026-10-08, korisnik: može odstupati od originala za ljepšu grafiku, naglasak na dubini).** Oblaci (pozadina koju igra miješa u razini 1 i WINDY, i SAVARINI) su meki prozirni oblaci na canvasu (`build_cloud_canvas`: zamućeni rubovi, detalj tileova unutra, sjenčanje po debljini, šum koji se drži mape), dva sloja i blaga sjena na tlu. SAVARINO more je proceduralna voda (forkova površina `PIXEL_WATER`, `assets/models/terrain.cfg` navodi razine s vodom: boje same ne razlikuju vodu od plavog metala). **Teren**: tlo (pozadina 1) iz offline visina (`tools/terrain/make_terrain.py` → `assets/terrain/<mapa>.ter`): pikseli mape razvrstani u klase površine, svakoj klasi visina u `tools/terrain/levels.json` (po mapi; `~` = visina okoline, za rubove); igra crta redove mape kao mesheve na visinama (`build_terrain_row`), bacaju sjenu, sloj tla se ne crta. Tlo gdje stoje neprijatelji ostaje na 0 (igrivost se poklapa), platoi i zidovi se dižu prema kameri, slojevi iznad neprijatelja na tlu dižu se za `TERRAIN_HEADROOM` (36). Za mape bez asseta: reljef po tileu (`relief_mesh`, `TYR3D_RELIEF`).
    - **Ponori**: u svemirskim mapama crni prostor je rupa (`"void": "hole"`, uzorak `B3D_TERRAIN_HOLE`, verzija 2 `.ter`): platforme imaju zaobljene rubove i zidove do `TERRAIN_HOLE_DEPTH` (52) koji tamne u dubinu, zvijezde se crtaju ispod ponora (`stars_below_layer`). Teren preko zvijezda samo s rupama.
    - **Čvrsta tijela**: pozadine 2 i 3 (u `levels.json` `"solid": true`) postaju tijela: ploha na vrhu, prozirni pikseli su rupe, zidovi do tla (boja zida = površina malo unutra od ruba, `TERRAIN_WALL_INSET`). Samo kad se crtaju iznad neprijatelja na tlu (ne `bg2-low`), nefiltrirane; vrhovi ispod letećih neprijatelja (`solid_top`: pozadina 3 do 6 px ispod sky-enemy sloja, 2 još 12 niže), miješanje (detalj Pentium) se za njih ne primjenjuje. Gdje su zemaljski neprijatelji ispod njih, alat izrezuje udubine.
    - **Bez komponiranja nad terenom**: kad je tlo teren, ništa se ne komponira (`b3d_terrain_ground`); miješana pozadina 2 crta se kao tileovi u bojama miješanja, filtri tla kao boje (bez valovanja).
    - **Neprijatelji na terenu**: modeli/volumeni neprijatelja na tlu, njihove eksplozije i svjetla dižu se na visinu terena (`terrain_lift`; poravnanje čuva pozicije igre); alat ispod stacionarnih neprijatelja izravna teren. Položaje skuplja `tools/terrain/ground_log.sh` (`TYR3D_LOG_GROUND`, `TYR3D_TURBO`).
    - **Filtriranje tekstura** (korisnik: svi spriteovi će ionako biti modeli): atlas tileova i slojevi linearno (`TYR3D_FILTER=0` isključuje), prozirni pikseli dobiju boju susjeda (`bleed_into_clear`). Terenski redovi uzorkuju vlastitu teksturu mape (`terrain_ring`: prsten od 80 redova, ponavlja se okomito) jer atlas ćelija ne zna susjedni tile pa bi filtriranje dalo šavove; ravni tileovi uzorkuju od središta prvog do zadnjeg piksela (`tile_inset`).
    - **HD volumeni** (korisnik: sve spriteove u modele; prvo automatski, zatim ručno po važnosti): `tools/hd_sheets.py` sastavlja 4× (Lady0101) upscaleove natrag u listove (`upscale/out/sheets/*.hd`, nisu u gitu). Volumeni se tada grade iz njih (`v3d_build_hd_mesh`): mreža svaka 2 HD piksela, obris pomaknut na granicu alfe 0,5 (gladak), zaobljeno tijelo viših profila, reljef iz detalja upscalea; tekstura linearna s mipmapama. Boje: upscale je u paleti razina, paleta kadra ga tonira (`hd_tint`, zatamnjenja); filtrirani spriteovi i oni kojih nema u upscaleu ostaju 1×. Spojeni dijelovi neprijatelja: niži prag alfe uz otvorene strane. `TYR3D_HD=0` isključuje. Ručni modeli: agenti po briefu (power-upovi, pa neprijatelji po važnosti iz kataloga), `tools/sprite_reference.py` daje reference.
    - **Vegetacija** (korisnik: palme, grmlje i trava kao pravi modeli, trava uspravna i animirana): `tools/terrain/make_vegetation.py` nalazi zelene površine (boja), male mrlje na pustinjskim mapama su palme (`"palms": true`), velike teksturirane šuma (drvo na svakom svijetlom vrhu krošnje), glatke trava (busen svakih ~5 px); bez palmi/drveća gdje stoje ili prolaze zemaljski neprijatelji, bez trave gdje stoje. `assets/terrain/<mapa>.veg`. Igra gradi proceduralne mreže po mapi u bojama mape (`build_palm`, `build_tree`, `build_grass`, sjenčanje u boje vrhova), crta ih po redovima terena na visini terena, vjetar = smicanje po instanci (trava najviše), bacaju sjenu. `TYR3D_VEGETATION=0`.
    - **Ručni modeli, val 1** (agenti po briefu u scratchpadu): 37 power-upova (`tools/blender/models/items/powerups*.py`, bez okretanja zbog čitljivosti simbola) i 38 neprijatelja (`wave1_b/c/d.py`). Dijelovi jednog objekta (kliješta FLEET-a, polovice vrata, kometa…) imaju `origin` u `model` liniji: crtaju se u svom ishodištu, ne centrirani po visini. Modeli u pikselima igre (bez size) više se ne centriraju po bounding boxu na ekranu (ishodište = središte spritea). `TYR3D_VIEWER=enemies TYR3D_VIEWER_FIRST=<n>` pokazuje ih uz spriteove. `M3D_MAX_MODELS` 1024.
    - **Ručni modeli, val 3 (cijeli listovi)**: agent po listu spriteova (`tools/blender/models/enemies/wave3_<x>*.py`), svaki čita događaje razina da bi složio višedijelne objekte (bossovi, zgrade, zidovi) cijele pa ih izrezao na dijelove (`origin`). Uključeni su oštećeni izgledi (`dgr`, katalog ih bilježi kao vlastite tipove), sidekickovi (`tools/blender/models/sidekicks`, opcije sada rade i za njih) i, u tijeku, pucnji (`shot` pravila) i animacije koje mijenjaju oblik (`frame` pravila). Novi `models.cfg` alati: `layer=` (dijelovi na različitim slojevima crtaju se na jednoj visini), `glow=<veličina>:<jačina>:<indeks palete>:<dx>:<dy>`, `frame <list> <sprite> <model>`, `shot <shots|shots2> <sprite> <model>`, listovi sa simbolom kao `x<hex>`. Ukupno ~1470 ručnih modela; spajanje: `merge_cfg.py` / `commit_batch.sh` iz scratchpada (provjera duplikata). Preostali tipovi namjerno ostaju HD volumeni (objekti koji se vrte oko zajedničkog kuta ili mijenjaju oblik kroz cijelu animaciju).
    - **Oblaci s volumenom**: na canvasu oblaka rubovi su razbijeni šumom (domain warp + erozija), a iznad leže "pahuljice" (`cloud_puffs`, tekstura `create_puff_texture`: režnjevi osvijetljeni odozgo-lijevo) — billboardi okrenuti kameri, sortirani po dubini, najviši u sredini oblaka (`wide`), rjeđi na rubovima, mjesta vezana za mapu.
    - **Izbornici preko 3D-a** (korisnik: pauza, kraj razine i ESC opcije bile su 2D): u razini, kad igra nacrta izbornik ili poruku preko igrališta i pozove `JE_showVGA`, prikazuje se zadnji 3D frame (`rgpu_present_3d_menu`): ono što se razlikuje od ekrana kakav je bio kad se frame prikazao (`take_backdrop` u `JE_showVGA3D`) ide preko scene, kutije koje je `JE_barShade` zatamnio zatamnjuju scenu (`video_backdrop_shade`), fade palete ide preko cijelog prozora. Vrijedi dok se panel (desni stupac) ne promijeni (trgovina, naslovni ekran → opet 2D). Izbornik usred ticka završava hvatanje framea (`l3d_frame_end_early`: na površini na kojoj je faza počela, `phase_surface`, jer izbornici mijenjaju `VGAScreen`; inače hvatanje prati `VGAScreen` kao prije — na razinama sa smoothiejima okvir počinje na `VGAScreen2`, koji ESC izbornik koristi kao kopiju svog ekrana). Sjene teksta koje tamne piksele ispod zatamnjuju scenu. Miš u izbornicima: `last_output_rect` je ekran postavljen na igralište u 3D rasporedu. Test: `TYR3D_TEST_KEYS=150:P,1500:P` (ili `Escape`).
    - **Trgovina u 3D-u**: ilustracija broda (`draw_ship_illustration`) i simulator oružja (`JE_weaponViewFrame`) su scene (`rgpu_present_showcase`): slika okvira bez broda leži na tlu, kamera ravno odozgo (`fit_camera` bez nagiba) točno na okvir, modeli iznad nje osvijetljeni suncem sa sjenom; ekran trgovine ide preko svega osim gdje još pokazuje tu sliku. Ilustracija: model broda lebdi, lagano se okreće i naginje, sidekickovi u svojim utorima, luk štita ostaje na slici (`video_showcase_begin/backdrop/end`). Simulator: brod i hici koji imaju modele crtaju se kao modeli umjesto spriteova (`video_sim_ship`, `video_sim_shot` u `simulate_player_shots`), ostali hici ostaju pikseli preko scene. Lighting i post izdvojeni u `scene_lighting`/`scene_post`. Test: `TYR3D_SHOP=1 TYR3D_START=1:2`.
    - **Moderni HUD** (korisnik: bez kompletnog sidebara, samo bitno; postavka 3D → HUD: Modern/Classic, `TYR3D_HUD`, `[tyrian3d] hud`): igralište zauzima cijeli prozor (`layout_3d` bez panela), mjerači iz stanja igre crtani kao quadovi canvasa (`build_modern_hud`, `HudQuad`): dolje desno štit/oklop/snaga generatora (glatko klize, oklop ispod 25 % treperi), gore desno razine prednjeg/stražnjeg oružja (11 kockica) i municija sidekickova, naslov razine prvih 4 s. Tekst fontovima igre (Scale2x dvaput, bijelo, tonirano, sjena). Grupa blijedi kad je brod ispod nje (`hud_fade`). Lijevi kutovi ostaju igrini (rezultat, bombe, životi, specijalno oružje u overlay sloju). Poruke (`JE_drawTextWindow`) su više (`MESSAGE_AT`). Dva igrača uvijek klasični panel.
    - **Svjetlo hitaca** (korisnik: bolje osvjetljenje, normal mapping): fork ima 32 točkasta svjetla (bilo 8). Uz svjetla eksplozija, sjaj svakog hica i drugih svijetlećih stvari (`frame->glows`) je svjetlo u boji svog spritea, ispod njega (0,35 visine sloja, da osvjetljava tlo a ne sam model), domet visina + 2,6 promjera; biraju se najvažnija (energija × domet, eksplozije prve). Svi redovi terena imaju reljef iz svjetline (`normal_scale` negativan) koji svjetla izvlače. Isprobano i odbačeno: osvijetljeno tlo suncem s reljefom (sunce je visoko pa se reljef jedva vidi, a zidovi i sjene postaju crni); radiance cascades: vidi sljedeću stavku.
    - **Radiance cascades** (korisnik: imamo ih, iskoristiti): forkov HRC radi na Metalu. Fork je dobio dvije stvari za pixel art: `rc_receiver` (unlit površina prima odbijeno svjetlo, dodano svojoj boji, i nije izvor; u G-bufferu emisija alfa 0,75, resolve daje `albedo × bounce` s alfom 2, compose zbraja) i `additive` (bez neba i sunca na rubovima polja; sve površine samo dodaju svjetlo onoga što svijetli, vlastito osvjetljenje scene ostaje). U igri: sve unlit površine osim particla i sjajeva su primatelji; izvori su particli eksplozija, sjajevi hitaca i emisivni dijelovi modela. Polje 128×128 ćelija po 4 piksela preko igrališta, bez okluzije (sljedeće: okluzija iz visina terena, da zidovi zaklanjaju). Default Low (s Effects), trošak neprimjetan (3 framea po ticku i dalje). `TYR3D_RC`, `TYR3D_RC_INTENSITY`.
    - **Tamne razine** (korisnik: pravo osvjetljenje umjesto lažnog trokuta; ASSASSIN, SURFACE, BRAINIAC, ICESECRET): bez overlaya; fork ima `unlit_darkness` / `unlit_glow_threshold` u `BTBHGPUSceneLighting` (unlit površine zadrže 1 − tama boje, spot svjetlo — brodova lampa — ih osvjetljava (0,6 snage kao za modele, s reljefom), pikseli svjetliji od praga sjaje i dalje (lava), točkasta svjetla eksplozija i hitaca dodaju). Tama 0,95 linearno (≈ 25 % sRGB kao overlay originala), prag sjaja 0,7. Modeli: sunce, ambijent i nebo × 0,05. Prozirne unlit površine (oblaci, dim) ne prolaze kroz taj shader pa im se boja zatamni u igri. `TYR3D_DARK_LIGHTING=0` vraća overlay.
    - **Obale i džungle** (korisnik: stara voda uz obale, 2D drveće kod SAVARINOG bossa): tileovi s malo vode (≥ 6 %, `WATER_SHORE`) su obala: njihovi izrazito plavi pikseli su voda (proceduralna), tamni ostaju kopno; voda u dobrom dijelu ostaje `WATER_TILE` (i hladni i tamni pikseli; samo oni nemaju reljef). Vegetacija: alat više ne čisti biljke gdje neprijatelji na tlu prolaze (samo gdje stoje); igra ih skriva ispod neprijatelja na tlu gdje su sad (krug oko svakog objekta sloja `L3D_GROUND_ENEMY`). `levels.json` `"forest": "palm"`: šuma su palme (SAVARE).
    - **Brisanje naslikanih objekata** (korisnik: ispod modela se vidi stari sprite integriran u tileset): `tools/terrain/make_erasures.py <extract dir>` za svako mjesto gdje stoji neprijatelj na tlu (`ground.txt`) traži sprite te razine koji se poklapa s pikselima mape (±2 px, ≥ 30 %); pikseli jednaki mapi (i obrub) brišu se i pune tileom tla: za svaki tile koji objekt dira, najčešći tile oko njega (gdje nitko ne stoji), s najbližeg mjesta gdje ga ima (pomak od cijelih tileova, pa je spoj bešavan); na generiranim bočnim stupcima tlo iz blizine koje najbolje odgovara (i bojama iznutra). `assets/terrain/<mapa>.era`; igra ih primjenjuje pri gradnji reda teksture terena (`erase_painted_enemies`, indeksi palete iz tileova → prate paletu). `TYR3D_ERASE=0`. Modeli s pločom tla iz spritea (batch AV): `match_ground.py` (scratchpad) poklapa sprite svakog neprijatelja na tlu s mapom ispod njega; 250 kandidata podijeljeno u tri liste, ~180 modela popravljeno (bez ploče tla mape; uspravni: stupovi UNDERDELIJA, IXMUCANEOV zid, kameni stup MINERS, pumpa i toranj za bušenje asteroida, FRUITOVI stupovi/kristali/kapsule, crveni šiljak), komentari u `models.cfg` ažurirani. Svjesno ostavljeno: zeleni tornjevi TORM-a (četiri neprijatelja, uspravno bi razdvojilo vidljivo i pogodivo), krov hangara asteroida (nagib 50°), `dome_cannon_barrel`. Uspravni gornji dijelovi stoje niže od svojih spriteova (pogodak gađa mjesto spritea).
    - **Fontovi** (korisnik: custom fontovi slični originalu): Oxanium (OFL, `assets/fonts`, Bold/SemiBold/Medium za veliki/normalni/mali font igre) kroz forkov `btbh_gpu_window_font_load` (atlas sada linearan). HUD i naslov razine crtaju se njime (`text_quads`). Tekstovi igre (izbornici, poruke, trgovina) bilježe se (`text_record.c`: svaka funkcija za tekst u `fonthand.c`/`font.c` omotana `text_record_begin/end`; pikseli prije i poslije, ugniježđeni pozivi u vanjskom); pri prikazu se oni koje ekran još pokazuje (85 % promijenjenih piksela) skinu s kopije ekrana (`screen_without_texts`) i nacrtaju Oxaniumom (jedna veličina po fontu, boja najsvjetlijih piksela, sjena), u izbornicima preko 3D-a, u 2D ekranima dok je 3D uključen (trgovina, naslov) i u izlogu trgovine. `TYR3D_FONTS=0`.
    - **Debug let** (korisnik: odabrati level, preletjeti bez gubitka života, ubrzanje, premotavanje, pauza, za screenshot feedback): `src/debugmode.c`. Setup → Debug Flight... (popis sekcija s `]L` iz `levelsN.dat`, kao `tools/levels.py`), `dev_setup_game` (izdvojen iz `dev_start_game`), god mode. Brzina: `nortsong_time_scale` u `setDelay*` (prikaz preskače tickove iznad 2×). Premotavanje: na početku razine pamti se `player[]`, stanje RNG-a (`mt_save/mt_load`), težina i sekcija; svaki tick bilježi se unos igrača nakon čitanja (`debug_flight_input`: x, y, brzine, akceleracija, tipke); unazad = `reallyEndLevel` + na `start_level` skok na `start_level_first`, vraćanje stanja i reprodukcija unosa do cilja bez čekanja (`nortsong_skip_waits`), bez prikaza i 3D hvatanja, bez zvuka. Snimka (F12) kroz readback u `export/feedback` s imenom razine, sekcije, ticka i vremena; `TYR3D_DEBUG_SEEK` vraća na tick. Brisanje naslikanih objekata bira tile podloge s najviše jednakih piksela (objekt je naslikan preko njega).

27. **Novi sadržaj, faza A1 i početak B (2026-10-09; plan i korisnikove odluke u `docs/plans/2026-10-09-novi-sadrzaj.md`).** Sloj sadržaja `src/content.c`: `assets/content/items.cfg` (format u `content.h`) puni slobodna mjesta podataka predmeta (oružja 819–999 između dvije banke, portovi 48–60 "Test", sidekickovi 33–37, specijalci 49–54) nakon svakog `JE_loadItemDat`, pa originalni predmeti ostaju isti; `copy=` počinje od postojećeg predmeta. Datoteku piše `tools/content/make_items.py` pravilima iz originalnih zapisa (`tools/content/tyrdata.py`). Prvi predmeti (faza B): prednja oružja iz sidekickova (Phoenix Cannon, Wobble Cannon, Micro-Missile Swarm, Zica Flamer), stražnja (8-Way Burst, Mine Layer) i sidekickovi iz oružja (Laser, Sonic, Lightning, Banana, Guided Option). Pravila koja vrijede za zapise oružja: `del` je život hica u tickovima (98–100 prate miš, 101–119 animacija, 121 bez traga), `attack` 100–249 na pogodak ispaljuje oružje `attack−100` (lančano), 250+ prolazi kroz neprijatelje sa štetom `attack−250`; `sy` > 0 je naprijed; `circlesize` 20+x je njihanje x u stranu; stražnji port s većom potrošnjom ne puca jer prednji prvi troši generator (zato 20–40). Ništa ih još ne prodaje; debug let ima tipke za opremu (`[ ]` prednje, `9 0` stražnje, `; '` snaga, `7 8` sidekickovi). `tools/package_macos.sh` sada kopira i `fonts` i `content` (fontovi su nedostajali u `.app`).

28. **Rogue mode, faza C (2026-10-09).** `src/rogue.c`: Start New Game → Rogue Run (`gameplaySelect` ima šestu stavku) otvara ekran s Start Run / Unlocks. Run su tri čina (`assets/content/rogue.cfg` iz `tools/content/make_rogue.py`: leveli epizoda 1, 2–3 i 4–5 po sekcijama, bossovi = leveli s boss barom, događaj 79), svaki karta s granama (2–3 čvora po redu, 3 reda + boss; elite +1 težina i nagrada, trgovac prodaje karte za kredite). Level se pokreće kao debug let (`JE_initEpisode`, `mainLevel` = sekcija s `]L`), ali bez `constantPlay` (on puca sam i gasi igru na Quit); u runu `JE_loadMap` preskače `]I` dučane, `]W/]P/]U/]V/]R` tekstove i slike i `]b` backup save (preskače ga i debug let, da ne pregazi korisnikov slot 11). Kraj levela: `start_level` zove `rogue_level_over()` prije originalne grane smrti/učitavanja: smrt bez dodatnog života = kraj runa, s njim se level ponavlja od stanja na početku (`run.at_start`); inače `JE_endLevelAni`, karte (3, s unlockom 4; tier po činu i težini čvora), pa karta i sljedeći level. Ekrani su 2D u paleti dučana (ikone predmeta), zvjezdana pozadina, tekst kroz Oxanium zapise. Profil `tyrian3d_rogue.cfg` u korisničkom direktoriju; test runovi (`TYR3D_ROGUE`) ga ne spremaju. Za testove: `TYR3D_ROGUE_AUTO`, `TYR3D_ROGUE_UNLOCKS=all`, `TYR3D_LEVEL_TICKS`, `TYR3D_LEVEL_DIE`, `TYR3D_DUMP_KEYS` (dump nakon test tipke umjesto svakog frejma: dump svakog frejma tijekom levela napunio je disk do 0 bajtova).

29. **Feedback na rogue i polja sila (2026-10-09).** (a) Naslovni izbornik: tekst iscrtan ponovno na istom mjestu s drugim pikselima (označena stavka) više ne zamjenjuje stari zapis nego se čuva kao varijanta (do 3 po mjestu, `TEXT_VARIANTS`), a `text_records_on` uzima jednu po mjestu, pa stavke ostaju Oxanium kad oznaka ode. (b) Rogue karta ide slijeva nadesno; planeti iz dučanove karte (`PLANET_SHAPES`, prvi frame okretanja) crtaju se s bojama prebačenima iz palete 18 u paletu dučana (najbliža boja), veći na pola veličine; okvir odabira ispod natpisa. (c) Ljubičaste kugle su u runu iskustvo (`rogue_purple_ball` umjesto `handle_got_purple_ball`), razine 3, 5, 7... kugli, svaka razina dodatna karta nakon levela; moderni HUD ima red XP; smrt vraća XP na stanje s početka levela. Karte jednog izbora su različitih vrsta. (d) Polja sila neprijatelja (`p3d_field`, `show_field` u `JE_drawEnemy`): Magneto RePulse (255) šalje plave prstenove do 80 px i iskre van, Suck-O-Magnet (251) prstenove i iskre prema sebi, kratki magneti (253/254) iskre u stranu; prsten najviše svakih 14 frejmova po neprijatelju.

30. **Ljubičaste kugle po arcade algoritmu (2026-10-09).** U arcadeu event 45 daje grupi neprijatelja (linknum) predmet koji ostave kad umru (`enemydie`): uglavnom kuglu (tip 628, vrijednost 30000), ponegdje oružja i predmete (602–629). Puna igra ga preskače. U rogue runu event 45 vrijedi i svaki takav drop je kugla (`ROGUE_ORB_ENEMY`), pa XP dolazi u svakom levelu (MINES ima samo arcade predmete); oružja daju karte. Uz jako oružje SAVARA ostavi ~90 kugli, pa razine traže 10, 15, 20... Boje: model kugle (`purpleball.py`, Tyrian purple #66023c, malo emisije), sjaj u boji izvan palete (`glow=…:#rrggbb` u `models.cfg`, `L3DGlow.has_rgb`, `l3d_add_rgb_glow`), XP traka i streljivo sidekickova u HUD-u. Test runovi su tihi (`SDL_AUDIO_DRIVER=dummy` u `capture_run.sh` i `ground_log.sh`); `TYR3D_WEAPONS` vrijedi i za `TYR3D_ROGUE` test runove.

31. **Epizoda 6, korak A2a (2026-10-09; plan `docs/plans/2026-10-09-epizoda-6.md`).** E6 je u izvornim formatima: `tools/content/tyrformat.py` (šifriranje skripti, pisanje level datoteke: svaki level dva unosa, zaglavlje s događajima i 22368 bajtova tablica i mapa; zadnji unos su podaci predmeta kao u E4/E5), `tools/content/episode6/build.py` piše `assets/content/episode6` (gitignore: izvedeno iz podataka igre; CMake ga gradi ako postoje podaci i Python). Igra: `EPISODE_MAX` 6 (`EPISODE_AVAILABLE` ostaje 5), `dir_fopen` traži `tyrian6.lvl`/`levels6.dat`/`cubetxt6.dat` u `content/episode6`, ime epizode postavljeno u `helptext.c`, izbornik epizoda prikazuje 6. kad postoji, `JE_findNextEpisode` ne vodi iz E5 u E6, početni novac E6 30000. Za sada jedan level (kopija E5 SAVARA kao DIG SITE), dučan, kraj (]Q vraća na E1 kao kraj zadnje epizode).

32. **Epizoda 6: generator levela i prvi level DIG SITE (2026-10-09).** Korisnik: E6 ide u puni tok nakon E5 (`last_episode()`), 12 levela + tajni, leveli novi (originali samo inspiracija). Mape (`mapsynth.py`): tile prema lijevom, donjem, dolje-lijevom i dolje-desnom susjedu kako ih imaju originali istog izgleda, red po red odozdo; red se rješava točno kao lanac (s desna koji tileovi još dopuštaju kraj reda, pa izbor s lijeva), red bez valjanog reda iznad radi se ponovno (backtracking); plan po materijalima (boje tileova) težinama, težina 0 zabranjuje (bez fallbacka; backtracking nađe drugi put); sloj ima najviše 72/71/70 tileova. Događaji (`compose.py`, `waves.py`): valovi originala (spawnovi neba i vrha u nizu, s događajima na njihovim linkovima do 1500 px; link pripada zadnjem valu koji ga je spawnao) postavljeni po krivulji težine, novi linkovi (>40: blok od 20 zadržava mjesto), nepomični neprijatelji na tlu na tileovima na kojima su stajali u originalima, boss blok zadnjeg boss bara. JSON levela drži naše mape i događaje i samo reference na valove/bossove (podaci igre); `build.py` ih širi pri buildu. Neprijatelji E1-3 u podatke E6 (`enemydata.py`): samo oni koji se razlikuju od E5 (E4 je isti kao E5), oružja u niske slotove (tur je bajt) koje ništa ne koristi, lanci i lansirani neprijatelji. Ključni podaci: sat levela = skrol sloja 1 u pikselima, mapa 1 traje do 8148, tlo: d2 = 24c−30, t = 28(291−r)−8.

33. **Epizoda 6: levele 2-7 (2026-10-09; korisnik odigrao DIG SITE: "sve je super").** REEF (Savara obala), GREY MOON (asteroidna baza, valovi s tlom: `ground_waves`), ROOST (Torm džungla s rijekom), DEEP ICE (Ixmucane led), GLACIER (Ice Exit snijeg), CRUSTGATE (lava). Imena levela najviše 9 znakova (format skripte). `generate.py` sad ima dizajne kao podatke (`LEVELS`: izvori mapa po sloju, plan, valovi, boss, tlo, izgled s početnim događajima originala, brzine), `zones()` za planove po zonama, `frozen` za odigrane levele (DIG SITE se ne generira ponovno: plan bi dao drugu mapu). Od efekata izgleda (64) samo lava, voda, spotlight (blur i sl. su u 3D-u ravne ploče). 4-dijelni neprijatelji (12) dobivaju 4 uzastopna broja (`enemy_block`). 3D za nove mape kao za originale: `tools/levels.py` uključuje E6, `ground_log.sh` za položaje, `TYR3D_EXPORT_MAPS`, `make_terrain.py classify/build` (visine u `tools/terrain/levels.json` po klasama), `make_vegetation.py`, bočni stupci (`TYR3D_SIDES_WRITE`). Bez terena nove mape dobiju reljef po tileu, koji je na ledu izgledao kao ploča.

34. **Epizoda 6, druga verzija levela (2026-10-09; korisnik: prva dva levela "izgledaju kao pozadina i random otoci", treći ima građevine ali su protivnici razbacani, svima nedostaje novca, protivnici i bossovi neka ne dolaze iz istih levela kao tileset).**
    - **Planovi mapa** (`plan.py`): oblici (obala, otok, rijeka, pojas, raspršeno, mirno more `calm`, `fill`) materijala po bojama tileova; unutar strogih oblika samo tileovi tog materijala, rubovi slobodni za prijelaze iz originala. Generator (`mapsynth.py`) red koji stalno pada uzima plan blaže (zabranjeno postaje malo vjerojatno), bira prvi red koji odgovara planu, gleda unaprijed ispod fiksnih ćelija.
    - **Objekti** (`objects.py`): grupe ne-baznih tileova originala s prstenom oko sebe (bunkeri, stupovi, otoci, stanice, brodovi), bez onih širokih kao mapa (to su dijelovi levela). Lijepe se nakon generiranja u mirne zone gdje je okolina točno njihov obični tile (bez šavova); `min_core` za landmarke. Kao fiksne ćelije u generatoru nisu radili (prestrogo).
    - **Neprijatelji na tlu** (`compose.place_ground`): samo na tileovima (ili 2x2 blokovima za 4-dijelne) koji u originalima u većini pojava nose neprijatelja (stopa ≥ 0,45): podloge topova, bunkeri. Prije: na bilo kojem tileu na kojem je ikad netko stajao.
    - **Miješanje**: valovi iz druge teme, boss iz treće (npr. DIG SITE: Savara mapa, valovi CAMANIS/SAWBLADES, boss TYRIAN X); listovi neprijatelja: boss, pa tlo (najviše 2), pa valovi.
    - **Novac**: 65 % valova ostavlja novčiće/dragulje (neprijatelji 390-399) do zadanog bogatstva levela (12k → 45k), a u podacima E6 neprijatelji vrijede 2,5× (`VALUE_FACTOR`, ne mijenja druge epizode). Autopilot (bez skupljanja novčića) na DIG SITE: ~8,4k prema ~9,5k originalne SAVARE; s novčićima do ~12k više.
    - **3D za nove mape** jednim alatom: `tools/content/episode6/terrain.py` (izvoz mapa, ground_log, visine po materijalima iz dizajna, `make_terrain.py` opcija `materials`, vegetacija, bočni stupci; preskače mape koje imaju i originali, npr. prazan sloj; briše postavke i assete starih verzija E6 mapa). Igra sad ispisuje i već izvezene mape i "level over: … cash" na kraju levela.
    - DEEP ICE zadržava staru mapu (`keep_map`); DELI RUIN i ROOST stari pristup mapi (nova je bila lošija).

## 9. Predloženi sljedeći koraci (redom)

Plan je gotov (vidi `docs/plans/2026-10-07-tyrian3d-plan.md`, odjeljak 4). Dalje, korisnikovim redom:

1. Korisnik isproba: blokovi u WINDY, svjetla eksplozija, oblaci u SAVARI, miš (Direct), HUD.
2. Uljepšavanje: složeniji modeli neprijatelja i bossova (reference u `upscale/out`), 3D propovi za
   strukture u tileovima, mjerači HUD-a iz stanja igre, oblaci i u drugim razinama ako ih ima.
3. Novi sadržaj: brodovi, oružja, neprijatelji, proceduralna epizoda.
4. Windows (kasnije, na Windows stroju; kod je bez GCC built-insa).

**Performanse (2026-10-07, Release, 1920×1080):** 3D prezentacija troši 1,1–1,2 ms CPU-a po frameu na običnim razinama, do ~3,7 ms na razinama s filterima (LAVA RUN) i spotlightom; bloom i duboko zvjezdano polje su uključeni. Vulkan backend (MoltenVK) daje isti prikaz kao Metal.

35. **Epizoda 6: gimmicki originala (2026-10-09, korisnik: "ima jednoličnih levela... ubrzanje scrollanja, bossovi na pola levela, flippanje slike, flashlight...").** `compose.py` prima `gimmicks` iz dizajna levela: `midboss` (boss drugog originala na pola levela: mapa stane eventom 2 i 53 gdje je original staje ili kad je boss u vidu, njegov obrazac se vrti skokom 54, svakih 50 tickova event 70 provjerava je li pao i skače van, zatim brzine levela i 53 off; tlo nakon njega pomaknuto za trajanje borbe), `bursts` (sve brzine × faktor, upozorenje 7), `ambush` (val originala koji dolazi odozdo, upozorenje 1, njegov sheet rezerviran), `dark` (efekt 6, spotlight) i `flip` (efekt 9). `generate.py --events` drži mape (i teren) i radi samo događaje. `TYR3D_LOG_JUMPS` ispisuje skokove sata i promjene brzine. Sheetovi: bossovi i zasjede dobivaju mjesto prije tla i valova (assert ako midboss ne stane).

36. **Epizoda 6: tajne, bonus level, mini-igra (2026-10-09, korisnik: "mini igre tipa space invaders kako je na kraju 1 epizode, bonus leveli, secreti, više data cubeova").** Gimmick `couriers` (`compose.py`): neprijatelj s vala levela (ili E4/E5 na sheetovima levela) preleti vrh ekrana brzinom 3 na linku 40 (valovi dobivaju linkove 1-39), event 33 mu daje nagradu: datacube 512 ili warp kuglu (593, sheet 20 rezerviran; `build.py` je kopira s vrijednošću 10000 + sekcija tajnog levela, `Importer.custom`). `story.py`: `secret` (tajne kockice levela, prikazane u sljedećem shopu: `]+[ k` za kockice priče pa `]?[` s pričom pa tajnima), `kind` "secret" (VAULT iza GREY MOON, samo warp vodi tamo, vraća se na sljedeći shop) i "bonus" (INVADERS nakon THE CORE). `build.layout()` dodjeljuje sekcije; bonus/tajni leveli imaju `$$`. Kockice iz valova originala postaju novčići (priča ima svoje). `scale_values` više ne dira vrijednost 1 (kockice). `minigames.py`: INVADERS na mapama COLLECTOR-a (`shared_maps`, teren isti; `terrain.py` ga preskače): mapa stoji (2 + 53), 5 rundi po 3×6 neprijatelja, svaki na svom linku (link umire s pogotkom), marš eventom 19 po linku, pucanje 31, novčići 33, tanjur (top sloj, x = d2 − 66) s draguljem, 70/54 za kraj runde. `ground_sheets` ograničava nove sheetove tla (GREY MOON 0 zbog warp sheeta). `ground_log.sh`: log se kreira prije pokretanja igre (utrka je davala 0 pozicija). `TYR3D_LOG_JUMPS` ispisuje i pokupljene warp kugle i kockice.

37. **Epizoda 6: bočno skrolanje (2026-10-09, korisnik: "nedostaju nam još sidescrolling leveli"; zatim "da je side level što više side level... zvijezde s paralaxom, svi brodovi zarotirani na bok, patterne metaka kako jesu, 3D ukrasi gore i dolje").** Event 200 (Tyrian3D; d1 uključi/isključi, d2 ukrasi) postavlja `l3d_sideways` / `l3d_side_decor` (reset na početku levela; `TYR3D_SIDEWAYS=<1-3>` za bilo koji level). Logika igre i 2D nepromijenjeni. `render_gpu.c`: `fit_camera(..., sideways)` okreće pogled u smjeru kazaljke (post matrica: x prozora iz y pogleda, y iz −x), pravokutnik je cijeli prozor od 6 % s lijeva (dno polja tamo, ostatak naprijed, pa daleki desni dio i dalje gleda na level, ne iznad horizonta), `ndc_slopes()` za zrake (footprint, miš), `BACKGROUND_AHEAD` 1100 bočno, `SIDE_ROLL` 90° oko osi skrolanja za sve modele (profil), `L3DObject.scale`. Kontrole: `mainint.c` okreće pomak (desno = naprijed po levelu, dolje = desno po polju) i analogni ulaz; autopilot upravlja u koordinatama levela (njegov pomak se unaprijed okrene natrag). Duboke zvijezde: četvrti, bliski sloj samo bočno. `layer3d.c add_side_decor`: kamenje (asteroid_lumpy/crag_*) uz rubove polja, uglavnom izvan njega, hash po mjestu, klizi 3× brzinom mape (brže od zvijezda). `generate.py` dizajn `side`/`blank`: prazna mapa (prazni tile), zvijezde on (9), event 200; teren se ne radi. MIGRATION (iza ROOST, GRYPHON/SOH JIN valovi, GEM WAR boss) i GRAVITRON (iza CRUSTGATE, BRAINIAC/GAUNTLET, DREAD-NOT, jurnjava), kockice 23-26. Također: valovi i tlo provjeravaju sheetove i lansiranih/ispuštenih neprijatelja (`waves.sheets_of`; ROOST je imao TORM-ove kupole koje lansiraju sheet 14).

## 10. Memorija

Postoje zapisi u `~/.claude/projects/-Users-duke4e-Documents-GitHub-Tyrian3D/memory/`:
`tyrian3d-project.md` (ciljevi i pravila arhitekture) i `btbh-renderer.md` (gdje je renderer i što se ne dira).
