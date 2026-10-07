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
3. **Sjene.** Objekti ne bacaju sjene na tlo; 2D sjena broda je isključena kad se crta 3D izgled (plan: M5.4).
4. **Pikseli iste boje.** Kad sprite iscrta piksel iste boje kakva je već ispod, diff ga ne vidi, pa taj piksel ostaje u nižem sloju. Za pozadine to više ne vrijedi (tileovi su ispod snimljenog sloja). Vizualno je zanemarivo.
5. **Specijalni brodovi.** `shipGr_ 0` i `1` (dvodijelni brodovi, Nortship) uvijek su spriteovi.
6. **Filteri izvan igrališta.** Pozadine koje igra filtrira (lava, voda, led) komponiraju se na CPU-u za vidljivo područje i prolaze kroz iste formule kao `lava_filter`/`water_filter` (`b3d_compose`), pa nema šava na rubu igrališta. Preostale razlike: igra za piksel iznad čita prošli frame (ovdje nefiltrirani piksel), vremensko zamućenje leda i blura je izostavljeno, a miješana pozadina 2 nacrtana nakon filtera miješa se samo s komponiranim pozadinama ispod (ne sa spriteovima i pozadinom 3). Trošak: oko 1–2 ms po frameu na tim razinama (RelWithDebInfo). `JE_darkenBackground` (SuperWild) i "astral" stanje izvan igrališta nisu preneseni.
7. **Boja 0 pozadine 1 je prozirna** (kroz nju se vide zvijezde, kao u igri). Izvan igrališta se ondje vidi crna boja clear-a, a ne boja palete 0 (koja je inače crna).
8. **Neprijatelji se pojavljuju naglo pri većem tiltu.** Tlo se vidi daleko naprijed, ali igra stvara neprijatelje tek kad im red dođe do vrha ekrana, a objekti se crtaju do 64 reda iznad njega. To je logika igre.
9. **HUD (M4.1/M4.2, iteracija 1).** U 3D-u (jedan igrač) panel HUD-a stoji uz desni rub prozora, visok koliko prozor, a igralište je najveće što stane pored (`layout_3d`); traka s porukama ispod igrališta se ne crta, nego se poruka (`text_window_message`) ponovno iscrta tekstom u dnu igrališta. Dva igrača imaju originalni raspored. Sljedeće: HUD iz stanja igre u višoj rezoluciji (iteracija 2), postavke (M4.3).
10. **Neranjivost broda.** Original crta neranjivi brod poluprozirno (`blit_sprite2x2_blend`); model umjesto toga "bljeska" (svjetlina 2,5×). Prozirnost bi trebala alfa u BTBH-ovom MRT model shaderu (plan: M5.2 stanja).
11. **Strane mape (WFC).** Stupci uz mapu (16 sa svake strane) generiraju se iz tileova same mape (`src/wfc.c`, `make_sides` u `background3d.c`) unaprijed za sve razine (`tools/precompute_sides.sh` → `assets/sides`, zlib, oko 0,5 MB); ako ih nema, pri učitavanju razine (`b3d_prepare_sides` u `JE_loadMap`) uz keš u `~/.config/opentyrian2000/tyrian3d-sides/` (ime = hash mape i postavki; promjena algoritma traži novi `SIDE_CACHE_VERSION` i ponovni precompute). Prvo generiranje traje oko 0,2–0,4 s po pozadini u Debug buildu. Trake od 24 reda rješavaju se redom; ako ne uspiju, pokušava se bez veze s trakom iznad, pa bez veze s rubom mape, a tek onda zrcaljenje. Šav nastaje na mjestima petlje mape (BKwrap) i između traka koje nisu vezane.

## 9. Predloženi sljedeći koraci (redom)

1. Korisnik ručno isproba igru i kaže dojam o pozadinama i volumetrijskim spriteovima. Kalibrirati zadani tilt, FOV i visine slojeva (tipke za kameru ispisuju vrijednosti).
2. M3: korisnik odobrava set brodova (preglednik `TYR3D_VIEWER=ships`); doraditi Storm i ostale prema dojmu; sidekickovi.
3. M2.2: semantika animacija (rotacija, ciklus, naginjanje) iz kataloga.
5. M4: HUD kao overlay (scena već puni prozor), posebne razine.
6. M5.4 sjene: varijanta shadera "unlit + prima sjenu" za slojeve, tileove i volumetrijske spriteove.
7. Vulkan (`TYR3D_GPU_BACKEND=vulkan`, na macOS-u preko MoltenVK) i build na Windowsu/Linuxu (M9).

## 10. Memorija

Postoje zapisi u `~/.claude/projects/-Users-duke4e-Documents-GitHub-Tyrian3D/memory/`:
`tyrian3d-project.md` (ciljevi i pravila arhitekture) i `btbh-renderer.md` (gdje je renderer i što se ne dira).
