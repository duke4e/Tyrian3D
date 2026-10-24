# Tyrian3D: glasovi data cubeova

Datum: **2026-10-24**. Korisnik: "za sve data cubove uzmemo elevenlabs pretplatu, pa da ih ai procita. Grupiramo po
likovima, pa imamo orginalni glas za svakoga", zatim "Moze pripremi sve za audio". **Stanje:** alati su gotovi
(`tools/voices`, commit 7cca669e), ništa nije snimljeno; korisnik je odgodio snimanje ("Glasovi za kasnije"). Za
nastavak treba korisnikova ElevenLabs pretplata i ključ (Claude ne kupuje, ne prijavljuje se i ne upisuje ključ).

## 1. Što postoji

- `tools/voices/export_cubes.py`: čita cubeove epizoda 1-6 (`cubetxt1-5.dat` u `data/tyrian2000`, `cubetxt6.dat` u
  `assets/content/episode6`) u scenarij `data/voices/script.json` i `script.html` (za čitanje, s portretima; izvan
  gita jer je tekst igre). 175 cubeova, 170 s glasom (1:3, 4:1-4:3 i 5:12 su prazni); 2:10, 3:9, 3:10, 3:21, 4:14,
  5:6 i 5:7 nijedna epizoda ne prikazuje (`--referenced-only` ih preskače). Dijeli cube po govornicima (citati u
  naraciji, označeni dijalozi, pjesmice, rezovi urednika).
- `tools/voices/cast.json`: 53 govornika, 27 dizajniranih glasova (opis i Voice Design prompt), 26 sporednih uloga
  posuđuje jedan od njih (`voice_of`), pa sve stane u 30 mjesta Creator plana; portreti i 20 dvojbenih odluka
  (`ambiguous`: npr. Muldar je Milktoe u skrivanju, `???` s nindžinim portretom su Nanol).
- `tools/voices/pronunciation.json`: 93 izgovora (Tyrian → Tirrian, Ixmucane → Eesh-moo-kahneh, Gyges → Jye-jeez;
  korisnik treba potvrditi Vykromod = VYE-kro-mod i Javi = JAH-vee).
- `tools/voices/generate.py`: `estimate` (bez mreže), `status`, `design` (3 uzorka po glasu u
  `data/voices/previews/`), `adopt`, `generate` (eleven_v3; kratke izmjene replika kroz Text to Dialogue), `build`
  (iz lossless cachea, bez kredita), `try`, `dictionary`. Ključ čita samo iz `ELEVENLABS_API_KEY` ili
  `~/.config/tyrian3d/elevenlabs_key` i šalje ga samo u zaglavlju zahtjeva.

Procjena: ~121.000 znakova (kredita), 125-146 minuta govora; s dizajnom glasova i ponovljenim snimkama ~155.000.
Creator ($11 prvi mjesec, zatim $22; 121.000 kredita mjesečno, 30 glasova; cijene s elevenlabs.io/pricing
2026-10-24): dva mjeseca ~$33 ili jedan s naplatom viška. Izlaz: IMA ADPCM mono 24 kHz, -18 LUFS (~98 MB);
`build --format pcm16` bez kredita (~390 MB).

## 2. Koraci kad korisnik krene

1. Korisnik: pretplata na Creator, API ključ spremljen ovako (ključ kopiran u clipboard):
   `mkdir -p ~/.config/tyrian3d && pbpaste > ~/.config/tyrian3d/elevenlabs_key && chmod 600 ~/.config/tyrian3d/elevenlabs_key`
2. Korisnik pročita `data/voices/script.html` (napraviti ga nanovo: `python3 tools/voices/export_cubes.py`).
3. `python3 tools/voices/generate.py status`, pa `design`; korisnik presluša uzorke, `adopt <govornik> <broj>` za
   svaki odabrani (uzorke usvojiti brzo, mogu isteći).
4. Proba: `generate --only 4:17` (i usporedba eleven_v3 / eleven_v4 na jednom cubeu, ~2.500 kredita), pa
   `generate --jobs 4`; loše snimke `generate --retake E:N:S`. Na sluh provjeriti pjevača i vrlo kratke replike.

## 3. Igra (još nije napravljeno; nakon UI faze dućana)

- Datoteke: `<voices>/e<episodeNum>/<cubeList[currentCube]>.wav`; mapa kao ostali resursi,
  `tyr3d_resource_dir("TYR3D_VOICES_DIR", TYR3D_VOICES_DIR, "voices", ...)`, u CMakeu `data/voices` uz
  `TYR3D_SOUNDFONT_DIR`; `tools/package_macos.sh` kopira `data/voices/e*/` i `manifest.txt` u `Resources/voices`.
- Kada: jednom po frameu u petlji dućana `voice_cube_update(curMenu == MENU_DATA_CUBE_SUB ? cubeList[currentCube] : 0)`
  (isti broj → ništa, drugi → zaustavi i pokreni novi), plus `voice_stop()` kad `JE_itemScreen` završi. Jedna kuka
  pokriva svaki izlaz i klasični i moderni dućan (moderni čita isti `curMenu`).
- Sviranje u mikseru igre (`loudness.c`): učitati kao `load_sfx_replacement` (`SDL_LoadWAV` →
  `SDL_ConvertAudioSamples` u S16 mono 44,1 kHz, ~10 ms za cube od 2 minute), jedan glasovni kanal uz 8 kanala
  uzoraka, glasnoća iz `volumeFactorTable[voiceVolume]`, miješan u svakoj grani `audioCallback` (i kad su efekti
  ugašeni); start/stop pod `SDL_LockAudioStream`, buffer osloboditi nakon otključavanja, ~30 ms fade-out; glazbu
  stišati ~6 dB dok glas svira (rampa ~200 ms).
- Postavke: `Settings3D` `voices` (zadano uključeno) i `voice_volume` (0-255), redovi u modernom Setupu (uz UI
  Scale u `mainint.c`), `TYR3D_VOICES=0`; bez `manifest.txt` postavka piše "not installed". Datoteka koja nedostaje
  znači tišinu, ništa drugo se ne mijenja; tekst ostaje kao titlovi.
- Po želji automatsko pomicanje teksta: `manifest.txt` ("episode cube duration_ms line_count t0 t1 ...") daje kad
  počinje svaki red čitača (prelomljen kao `load_cube`), dok igrač ne pomakne sam.
