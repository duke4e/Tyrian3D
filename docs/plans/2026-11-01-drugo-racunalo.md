# Razvoj na drugom računalu: kod i resursi u jednom klonu

Stanje 2026-11-01. Ovaj Mac drži oko 4,5 GB izvan gita: `data/`, `upscale/`, `export/`, `build/`, `assets/content/episode6|7` i cacheove u `~/Library/Caches/Tyrian3D`. Cilj je da `git clone` na drugom računalu donese kod i sve resurse odjednom, a sve što se može izraditi iznova da ne opterećuje git.

## Odluka: jedan javni repo, običan git

Igra je besplatna, to je projekt iz ljubavi, i javni repo treba imati sve da igra izgleda onako kako je želimo (3D, HD, zvuk). Ne treba ni privatni repo ni LFS:

- **Renderer je javan** od 2026-11-01 (`duke4e/btbh-renderer`, zlib). Prije objave pregledana mu je povijest: nema ključeva ni koda igre. Jedino što je nađeno je istekli ključ lokalnog brainstorm servera iz srpnja (`.superpowers`, `localhost`).
- **Tyrian3D postaje javan** kad su resursi u njemu. Njegova povijest je pregledana: nema ključeva ni datoteka većih od 5 MB, a `data/` nikad nije bio commitan.
- **U repo ide (običan git):** HD grafika, glasovi, poboljšani zvukovi, GeneralUser GS i epizoda 7. Epizoda 7 je naša rekonstrukcija GBC levela.
- **Preuzima se kao i dosad, sa stranice camanis.net, s provjerom SHA-256:** Tyrian 2000, GBC ROM (`Tyrian.gb`) i Camanis 2.
- **GBC glazba ne ide.** Bez `data/gbc/music/loops/loops.json` `build.py` ne piše `music.txt`, pa epizoda 7 svira PC pjesme (`gbc_music` u `src/tyrian2.c`). Iz ROM-a se može izraditi i lokalno.
- **Alati za ponovnu izradu idu u GitHub Release `devtools` istog repoa:** ESRGAN modeli, log tla, medijani pločica i cache glasova. Release ne napuhava povijest i nema kvotu; svaka datoteka mora biti manja od 2 GiB.
- **Licence:** ESRGAN modeli su nekomercijalni (Fatality CC BY-NC-SA 4.0, BigFArt CC BY-NC 4.0). Zato se HD grafika smije dijeliti samo u besplatnoj igri, a igra je ionako besplatna. Isti uvjeti vrijede i za ponovno dijeljenje samih modela u Releaseu, uz navođenje autora.
- **Javno postaje:**
  - adresa `duke4e@gmail.com` u 506 commitova (u rendereru je već javna, u 235 commitova);
  - `docs/plans`;
  - jedna datoteka s lokalnom putanjom `/Users/duke4e`.

GitHub za običan git nema kvotu pohrane ni prometa. Odbija datoteke veće od 100 MB, a najveća naša ima 31 MB (GeneralUser GS). Preporučena veličina repoa je do 1 GB, a odlučno do 5 GB. Svaka nova verzija binarne datoteke ostaje u povijesti zauvijek; na primjer, novi upscale sheetova doda 62 MB.

## Svi resursi izvan gita

"Iznova" znači može li se izraditi iznova bez tebe i bez plaćanja. Vremena su ona izmjerena ili zapisana u `TYRIAN3D.md`; "—" znači da nije mjereno.

| Resurs | Veličina | Iznova? | Kako | Kamo |
| --- | --- | --- | --- | --- |
| **Podaci igre** | | | | |
| `data/tyrian2000` (bez `sfx`) | 12 MB | da, preuzimanje | freeware zip s camanis.net | preuzimanje |
| `data/tyrian2000/sfx` | 3,4 MB | da, sporo | AudioSR (`tools/upscale_sfx.py`; AudioSR venv i model se preuzimaju) | repo |
| `data/custom/camanis2` | 0,3 MB | da, preuzimanje | zajednički level iz 2005., s camanis.net | preuzimanje |
| **HD grafika (`data/hd`)** | | | | |
| `tiles` | 4,1 MB | da, sati | `export_maps.sh` → `tiles_hd.py` (BigFArt za z/y/x/w, Fatality za lavu) | repo |
| `tiles_fatality` | 3,6 MB | da, sati | `tiles_hd.py` s Fatalityjem | repo |
| `sheets`, `hud_1p/2p.png` | 62 MB | da, sati | `TYR3D_EXTRACT` → `make_atlases.py` → `upscale_sprites.py` → `hd_sheets.py` (svi upscaleovi zajedno 3-4 h na GPU-u) | repo |
| `icons` | 6 MB | da | `TYR3D_EXPORT_PICTURES` → `upscale_sprites.py` s BigFArtom | repo |
| `planets` | 21 MB | da | `tools/planets3d.py` | repo |
| `pictures` | 28 MB | **ne** | tvoje rekonstrukcije (ručno ili generatorom); samo `portrait_frame` i `face_none` rade skripte | repo |
| **Glasovi (`data/voices`)** | | | | |
| `e1-e7`, `story`, `*.json`, `manifest.txt` | 103 MB | samo uz plaćanje | `tools/voices/generate.py` (oko 134 000 znakova kredita, oko 140 min zvuka); bez cachea ispadaju i druge izvedbe | repo |
| `cache` | 425 MB | samo uz plaćanje | isti `generate.py`; čuva da se iznova renderiraju samo promijenjene replike | Release |
| `previews` | 30 MB | samo uz plaćanje | `generate.py design` | ne |
| **GBC epizoda (`data/gbc`)** | | | | |
| `Tyrian.gb` | 0,5 MB | da, preuzimanje | s camanis.net, uz Tyrian 2000 | preuzimanje |
| `episode7`, `shop.json`, `story*.json`, `enemies`, `bosses`, `cache` | ~37 MB | da, iz ROM-a | `tools/gbc`: `extract.py`, `episode.py`, `shop.py`, `story.py`, `boss_rom.py` (—) | repo |
| `music/loops` | 50 MB | da, iz ROM-a | `songs.py` i `apu.py` → `music.py` (—) | ne (svira PC glazba) |
| `music` (ostalo) | 631 MB | da, iz ROM-a | `songs.py` (—) | ne |
| `report`, `levels`, `screens` | ~55 MB | da, iz ROM-a | `report.py`, `extract.py` | ne |
| **SoundFontovi (`data/soundfonts`)** | | | | |
| GeneralUser GS (zadani) | 32 MB | da, preuzimanje | `tools/fetch_soundfont.sh` | repo |
| FluidR3 GM, Arachno, MV30, Jnsgm2, Timbres of Heaven | ~900 MB | — | izostavljeni: ide samo GeneralUser GS | ne |
| **Radne mape** | | | | |
| `upscale/out/tiles`, `tiles_bigfart` | 87 MB | da, sati | `tiles_hd.py`; spremljeni medijani, s njima `--add` radi samo pločice novih mapa | Release |
| `upscale/in`, ostatak `upscale/out` | ~310 MB | da | `make_atlases.py`, `upscale_sprites.py` | ne |
| `export/terrain/ground.txt` (i `ground_savara_hard.txt`) | 728 MB (zstd: **28 MB**) | da, sporo | `tools/terrain/ground_log.sh` odigra svaki level s autopilotom; ulaz za teren, čisto tlo i vegetaciju | Release, kao `.zst` |
| `export/terrain` (slike) | ~190 MB | da | slike za pregled iz `make_terrain.py` i `make_cleanground.py` | ne |
| `export/maps` | 658 MB | da | `tools/export_maps.sh` (ulaz za HD pločice) | ne |
| `export/legacy` | 60 MB | da | `TYR3D_EXPORT_PICTURES` | ne |
| `export/episode6`, `review`, `jukebox` | 65 MB | da | izgradnja epizode 6 i alati za pregled | ne |
| **Izgradnja** | | | | |
| `build/` | 582 MB | da | `cmake` (shadercross s DXC-om prvi put traje dugo) | ne |
| `assets/content/episode6`, `episode7` | 52 MB | da, sam | izgradnja (`build.py`) | ne |
| **Izvan projekta** | | | | |
| `~/Library/Caches/Tyrian3D/tools-venv` | 799 MB | da | `tools/setup_tools_venv.sh` (preuzimanja), pa `fix_macho_tls.py` | ne |
| ESRGAN modeli (Fatality, BigFArt) | 128 MB | da, preuzimanje | `setup_tools_venv.sh`; BigFArt ručno s autorova OneDrivea | Release |
| `~/.config/opentyrian2000` | 1,3 MB | **ne** | tvoje postavke i spremljene igre | ne, ručno |
| ElevenLabs ključ | — | novi u ElevenLabsu | — | nikad |
| Claudeova memorija | < 0,1 MB | **ne** | — | ručno |

**Ukupno:**
- **repo:** ~300 MB novih resursa, pa s današnjih 325 MB povijesti ima oko 0,6 GB;
- **Release `devtools`:** oko 670 MB, od čega je 425 MB cache glasova.

## Kompresija: što se isplati

Izmjereno na ovim datotekama:

- **HD slike (`data/hd`): ne isplati se.** To su PNG i `.hd`/`.hdt`, već komprimirani. Sa zstd -19 su ispale 129 MB naspram 124 MB, dakle veće.
- **Glasovi (`e1-e7`): ne isplati se.** Već su IMA ADPCM (4 bita po uzorku); FLAC je od jednog napravio 1,07 MB naspram 0,42 MB. Opus bi ih prepolovio, ali uz gubitak kvalitete i novi dekoder u igri, a to nije vrijedno 50 MB.
- **Cache glasova: ne treba.** Sirovi PCM; FLAC bi dao oko 40 % manje (425 → oko 250 MB), ali Release nema kvotu.
- **SoundFontovi: ne treba.** Ide samo GeneralUser GS (32 MB).
- **Log tla (`export/terrain/ground.txt`): da.** To je tekst, pa zstd -19 daje 722 → 28 MB (26 puta manje, 80 s). U Release ide kao `ground.txt.zst`.

## Koraci

**Stanje 2026-11-01:**
- **Gotovo:** koraci 1-6 i 9-10 (commiti `e9f9563b`..`d3cc78c3`, Release `devtools`).
- **Provjera (korak 11):** svježi clone s `bootstrap.sh` daje iste epizode 6 i 7 (bajt po bajt). Slike levela 1:3, 6:2, 7:2 i Camanis 2 iste su kao iz glavnog stabla (najviše 0,05 % piksela razlike, animacija).
- **Otvoreno:**
  - odakle dolaze GBC ROM i Camanis 2 (camanis.net ima samo Tyrian 1.1, 2.1 i 2000);
  - stvarno preuzimanje s camanis.net (do sada testirano lokalnom kopijom zipa);
  - zadana grana (`master` je još OpenTyrian2000);
  - korak 8, objava.

1. ~~**Renderer javan**~~ (gotovo 2026-11-01).
2. **`tools/fetch_data.sh`:** preuzima Tyrian 2000, `Tyrian.gb` i Camanis 2 s camanis.net, s provjerom SHA-256. URL-ove i preuzimanja odobravaš ti.
3. **`.gitignore` i `.gitattributes`:**
   - `/data/` se više ne ignorira cijeli. Propuštaju se `hd`, glasovi (bez `cache` i `previews`), `tyrian2000/sfx`, `soundfonts/GeneralUser-GS*` i GBC rekonstrukcija; ostalo ostaje ignorirano.
   - Binarne datoteke se označe kao `binary` (`*.png *.hd *.hdt *.wav *.sf2`).
4. **Commit resursa** na `tyrian3d/m1-tools`. To je oko 300 MB u jednom pushu, a GitHub prima do 2 GB po pushu.
5. **Release `devtools`** (`gh release create`): ESRGAN modeli, `ground.txt.zst`, arhiva medijana pločica i arhiva cachea glasova. Prije uploada provjeriti da JSON-ovi u cacheu nemaju ništa osim teksta i postavki glasa. `tools/fetch_devtools.sh` ih skida i raspakira, a `setup_tools_venv.sh` uzima modele odande.
6. **Licence i README:**
   - `LICENSES.md`: HD grafika (nekomercijalni modeli), glasovi (ElevenLabs), zvukovi (AudioSR), rekonstrukcija epizode 7, te Tyrian i ROM koji se preuzimaju.
   - `README`: kako doći do igre (clone, `fetch_data.sh`, izgradnja).
7. **Pregled prije objave:** lokalna putanja u jednoj datoteci, `docs/plans`, odluka o emailu u commitovima.
8. **Tyrian3D javan** (`gh repo edit --visibility public`), uz tvoju potvrdu.
9. **`tools/bootstrap.sh`** koji na svježem klonu izradi sve što nije u repou:
   - provjera alata;
   - `fetch_data.sh`;
   - izgradnja shadercrossa i igre;
   - po izboru: `fetch_devtools.sh`, `export/maps` i venv za alate.
10. **Dokumentacija i memorija:**
    - `TYRIAN3D.md` dobiva odlomak "Drugo računalo";
    - u memoriji se ispravlja pravilo "podaci izvan gita".
11. **Provjera na ovom Macu:**
    - svježi `git clone --recursive` u praznu mapu, `bootstrap.sh` i izgradnja;
    - po jedan level epizoda 1, 6 i 7: HD pločice, glasovi, Camanis 2, PC glazba u epizodi 7;
    - usporedba sa slikama iz glavnog stabla.

## Na drugom računalu (ručno, ne ide u git)

- **Ključ ElevenLabsa** (`~/.config/tyrian3d/elevenlabs_key` ili `.env.local`): prenosiš ga sam, npr. kroz upravitelj lozinki.
- **Claudeova memorija** (`~/.claude/projects/-Users-duke4e-Documents-GitHub-Tyrian3D/memory`): kopirati u istoimenu mapu za putanju projekta na novom računalu. Ime mape ovisi o putanji, npr. `-Users-<ime>-...`.
- **Postavke i spremljene igre** (`~/.config/opentyrian2000`, 1,3 MB): po želji.
- **Alati:**
  - `brew install sdl3 assimp cmake`;
  - Blender za modele;
  - AudioSR samo ako ponovno radiš zvukove (rezultati su već u `data/tyrian2000/sfx`).

## Ako je drugo računalo Windows

Prijenos resursa je isti, ali igra se na Windowsu još nikad nije gradila: M9 je za Windows preskočen, a renderer tamo radi na Vulkanu. Uz gornje, trebat će:

- izgradnja s MSVC-om i vcpkgom (SDL3, assimp);
- shadercross s DXC-om;
- skripte u `tools/*.sh` kroz Git Bash ili WSL;
- venv alata na drugom mjestu (umjesto `~/Library/Caches`);
- `fix_macho_tls.py` tamo ne treba.

To je zaseban zadatak nakon prijenosa resursa.
