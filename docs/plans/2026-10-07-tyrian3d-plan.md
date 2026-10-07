# Tyrian3D: plan razvoja nakon PoC2

Datum: **2026-10-07**. Polazište je branch `tyrian3d/poc` (repo `duke4e/Tyrian3D`, renderer
`duke4e/btbh-renderer` na branchu `tyrian3d`). Trenutno stanje opisuju
[TYRIAN3D.md](../../TYRIAN3D.md) i [TYRIAN3D_HANDOFF.md](../../TYRIAN3D_HANDOFF.md).

## 0. Odluke i principi

Korisnikove odluke od 2026-10-07:

- **Vizualni smjer: vjerni remaster.** Modeli prate siluetu, proporcije i boje originalnih spriteova.
  Tehnika je čisti low/mid-poly s PBR materijalima i emisivnim dijelovima (motori, svjetla).
  Igra se mora odmah prepoznati kao Tyrian.
- **Widescreen + HUD overlay.** 3D scena puni cijeli prozor, a HUD postaje overlay.
  Širina igrališta i sva pravila igre ostaju ista.
- **Prioritet: brodovi i neprijatelji**, pa tek onda okruženje i efekti.
- **Git.** Commit i push nakon svakog završenog koraka. Branch `tyrian3d/<milestone>` se spaja u `tyrian3d/poc`.
  Commit poruke završavaju s `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

Principi koji vrijede za cijeli plan:

1. **Logika igre se ne mijenja.** Kolizije, brzine, spawn i bodovi su originalni. Sve 3D promjene
   su samo prikaz. Dev alati koji ulaze u logiku (autopilot, neranjivost, odabir razine) aktivni su
   samo uz env varijable.
2. **Originalni 2D put uvijek radi.** F3 je referenca za usporedbu i sigurnosna mreža.
3. **Pokrivenost prije savršenstva.** Svaki objekt u igri treba imati prihvatljiv 3D prikaz prije
   nego što se pojedinačni modeli poliraju.
4. **Sve je podatak.** Mapiranja, kamera i materijali žive u konfiguraciji i asset fileovima, a ne u
   kodu, da se mogu iterirati bez rekompilacije.
5. **Svaki korak ima automatsku vizualnu provjeru**, preko demo dumpova ili sweepa razina (A1), i
   kontrolnu točku na kojoj korisnik daje dojam.
6. **Izmjene renderera idu u fork na branch `tyrian3d`**, u obliku malih općenitih API-ja kakve bi
   mogao koristiti i BTBH. Korisnikovu BTBH radnu kopiju ne diramo.

## 1. Pregled milestonea

| # | Milestone | Sadržaj | Ovisi o |
| --- | --- | --- | --- |
| M1 | Alati | odabir razine, autopilot i sweep; ekstrakcija i katalog spriteova; konvencije modela; `models.cfg` v2 | — |
| M2 | Volumetrijski spriteovi | svaki neprijatelj, brod i predmet automatski dobiva 3D volumen iz svog spritea; semantika animacija | M1 |
| M3 | Brodovi igrača | ručno rađeni vjerni modeli svih brodova i sidekickova; preglednik modela | M1, M2 |
| M4 | Widescreen + HUD | scena na cijelom prozoru, popuna bočnih strana, novi HUD overlay, postavke | M1 |
| M5 | Neprijatelji epizode 1 + sjene | najčešći neprijatelji ručno; stanja (pogodak, neranjivost); predmeti; sjene | M2, M3 |
| M6 | Bossovi i ostale epizode | višedijelni neprijatelji i bossovi; epizode 2–5 | M5 |
| M7 | Efekti | metci, laseri, eksplozije kao čestice, svjetla, bloom | M5 |
| M8 | Okruženje | pozadine u većoj rezoluciji s reljefom, oblaci, 3D strukture | M4 |
| M9 | Robustnost i izdanje | posebne razine, svi modovi igre, Vulkan i Windows, paket | M5 |

Posebne razine (naopake, spotlight) idu u M4, jer diraju kameru i svjetlo koje M4 ionako mijenja.

---

## M1: Alati

Cilj: alati s kojima se sve sljedeće može raditi i provjeravati bez ručnog igranja.

### M1.1 Odabir razine, autopilot i sweep

- `TYR3D_START=<epizoda>:<razina>`: preskače izbornike i pokreće igru na zadanoj razini, sa zadanim
  brodom i opremom.
  - Koristi postojeći tok (`JE_initEpisode`, `mainLevel`/`jumpSection`).
  - Shop preskače kao u `constantPlay`.
- `TYR3D_AUTOPILOT=1`: jednostavan bot. Stalno puca, krivuda lijevo-desno i izbjegava rubove.
  Ulaz ubacuje kroz isti put kao tipkovnica.
- `TYR3D_GODMODE=1`: igrač ne prima štetu. Gotov je samo dev hook u funkciji za štetu igrača.
- `tools/sweep.sh`: za svaku razinu svih epizoda pokreće igru N sekundi, dumpa frameove i slaže
  contact sheet po razini. Radi u 3D i u 2D modu, radi usporedbe.
- **Prihvaćanje:** jedna naredba daje slike svih razina epizoda 1–5 bez ručnog ulaza; nijedna razina
  ne ruši igru.

### M1.2 Ekstrakcija spriteova i katalog neprijatelja

Podaci: **39 enemy shape fileova × 304 ćelije** od 12×14 px. 2×2 sprite zauzima ćelije
`i, i+1, i+19, i+20`. Tome se dodaju brodovi igrača (`spriteSheet9`, `spriteSheetT2000`), metci
(`spriteSheet8`, `spriteSheet12`), predmeti (`spriteSheet10`, `spriteSheet11`) i eksplozije.

- `tools/extract`, mali C alat koji koristi loadere igre:
  - Izvozi PNG-ove svih sheetova s indeksima i sastavljene 2×2 spriteove.
  - Boje dolaze iz palete razine u kojoj se sprite pojavljuje (igra ima 24 palete).
- Katalog neprijatelja iz `enemyDat` (`tyrian.hdt`) i event podataka razina. Za svaki tip
  neprijatelja: sheet, frameovi animacije (`egr[]`), veličina, tip animacije, razine u kojima se
  pojavljuje i koliko često.
- Izlaz je `assets/catalog/enemies.json` i HTML stranica (Artifact) sa svim tipovima, frameovima i
  dodijeljenim modelom. Ta stranica postaje praćenje napretka za M5 i M6.
- **Prihvaćanje:** svaki neprijatelj kojeg sweep vidi postoji u katalogu; katalog je sortiran po
  učestalosti.

### M1.3 Konvencije i pipeline modela

- Format: **glTF 2.0 binarni (`.glb`)**, Y gore, nos prema −Z, **1 jedinica = 1 piksel igre**.
  Tada pravilo `size` nije potrebno, ali ostaje kao override.
- Raspored: `assets/models/<kategorija>/<ime>.glb`. Izvori su u `assets/models/src/`
  (generatorske skripte), licence uz svaki paket.
- Alat za modeliranje, **odluka korisnika** (odjeljak 3):
  - (a) Python generator glTF-a, samo stdlib, za proceduralne trupove (loft, ekstruzija,
    zrcaljenje, bevel). Ne treba ništa instalirati.
  - (b) **Blender headless** (`brew install --cask blender`), za ozbiljnije modeliranje: modifikatori,
    booleani, UV unwrap, bake tekstura. Preporuka za M3 i dalje.
- **Preglednik modela** u igri: `TYR3D_MODEL_VIEW=<ime>` prikazuje model na okretnom postolju uz
  originalni sprite iz istog kuta (tlocrt), s istom kamerom i svjetlom kao u igri. Dumpa slike za
  usporedbu siluete.
- **Prihvaćanje:** jedan probni model prolazi cijeli put od izvora do `.glb`, preglednika i igre.

### M1.4 `models.cfg` v2

- Ključ za neprijatelja je `sheet + egr[0]` (kao sada). Za brodove igrača ključ je ID broda
  (`shipgraphic`).
- Nova polja po zapisu:
  - **yaw**: `fixed`, `frames` (tablica frame → kut), `velocity` (smjer kretanja) ili `aim`
    (prema igraču).
  - **roll**: iz frameova naginjanja (banking).
  - **Ostalo**: pomak visine, emisivni tint, skala, sakrivanje originalne 2D sjene.
- **Fallback lanac:** ručni model → volumetrijski sprite (M2) → ravni sprite u sloju.
- Hot-reload `models.cfg` na tipku (F5), da iteracija ide bez restarta.
- **Prihvaćanje:** postojeći PoC2 mapping radi preko v2 formata; F5 primjenjuje izmjene u igri.

---

## M2: Volumetrijski spriteovi (pokrivenost 100 %)

Cilj: svaki objekt dobiva 3D volumen, svjetlo i kasnije sjenu, s **točno originalnim pikselima**.
Ovo je zajednička osnova vjernog remastera i fallback dok ručni modeli ne stignu.

### M2.1 Generator mesha iz spritea (C, pri učitavanju sheeta)

1. Iz pokrivenosti spritea uzima se silueta. Distance transform daje "jastučasti" profil (zaobljeni
   rubovi), a luminancija dodaje blagi reljef.
2. Gornja ploha nosi teksturu spritea (nearest filtering). Donja ploha je zrcalna i tamnija.
   Bokovi uzimaju rubne piksele.
3. Mesh se gradi po frameu animacije, a ključ cachea je `(sheet, indeks)`.
4. Normale su glatke, pa svjetlo s M5.4 daje volumen.
5. Parametri po tipu objekta: debljina, zaobljenost, jačina reljefa. Brod igrača je deblji, metak tanji.

- **Prihvaćanje:** u sweepu svi neprijatelji, brodovi igrača i predmeti imaju volumen. Nijedan sprite
  na sloju `player`/`*_enemy` ne ostaje ravan, osim metaka i eksplozija (M7). Trošak je manje od 2 ms
  po frameu.
- **Kontrolna točka s korisnikom:** pokazati usporedbu ravno / volumetrijski / Kenney. Ako se izgled
  ne svidi, M2 ostaje samo fallback i ne ide u igru po zadanom.

### M2.2 Semantika animacija

Klasifikacija animacija po tipu neprijatelja, iz kataloga M1.2:

- **Ciklus.** Npr. trepćuća svjetla. Mesh se mijenja po frameu, a orijentacija ostaje ista.
- **Rotacija.** Frameovi su smjerovi. Kut svakog framea procjenjuje se poravnanjem rotirane siluete
  s prvim frameom, a sumnjivi slučajevi se ručno potvrđuju u katalogu. Ručni model tada koristi
  `yaw: frames`.
- **Naginjanje** brodova igrača. Frameovi `ship_banking -2..2` daju roll.

- **Prihvaćanje:** rotirajući neprijatelji (npr. turreti koji ciljaju) s ručnim modelom okreću se
  sukladno originalnom spriteu.

---

## M3: Brodovi igrača

Cilj: ručno rađeni, vjerni modeli svih brodova iz Tyrian 2000 i njihovih sidekickova.

### M3.1 Inventar

- Popis brodova iz `ships[]` (tyrian.hdt) s grafikama iz `spriteSheet9` i `spriteSheetT2000`.
- Uključuje dvodijelne brodove: `shipGr_ 0` (vjerojatno Dragonwing, provjeriti u inventaru) i
  `shipGr_ 1` (Nortship, s posebnim frameovima i NortSparks efektom).
- Sidekickovi i opcije: svaki tip s frameovima.

### M3.2 Modeli

- Redoslijed: početni USP Talon, pa brodovi iz shopa epizode 1, pa ostali, pa tajni.
- Svaki model ima:
  - siluetu poravnatu sa spriteom u tlocrtu (preglednik M1.3);
  - materijale s bojama iz palete spritea;
  - emisivne motore i svjetla;
  - pivot u središtu kolizije.
- Banking prema M2.2. Nortship i Dragonwing s posebnim dijelovima koji prate originalne frameove.
- Sjena: originalnu 2D sjenu zamjenjuje prava sjena (M5.4). Do tada mekana blob sjena na tlu.
- **Prihvaćanje:** u preglednicima i u igri svaki brod iz tlocrta odgovara spriteu. Korisnik
  odobrava set prije M5.

---

## M4: Widescreen, HUD overlay i posebne razine

### M4.1 Scena na cijelom prozoru

- Kamera se fita na visinu prozora, a igralište od 264 px je centrirano. Fit donjeg ruba i tilt
  ostaju kao sada.
- **Bočni overscan:** `game_screen` dobiva lijevu i desnu marginu kao što sada ima gornju, preko
  većeg pitcha i pomaknutog pointera. Blitteri ne clipaju vodoravno, pa sprite djelomično izvan
  ekrana prirodno završi u margini.
  - Treba provjeriti mjesta koja koriste globalni `VGAScreen->pitch`.
  - Treba provjeriti `memcpy` cijelih površina između `VGAScreen2` i `VGAScreenSeg` u izbornicima.
- **Popuna strana izvan mape** (mapa je široka 312–336 px): rubni stupci tileova zrcale se ili
  ponavljaju i postupno tamne. M8 to kasnije zamjenjuje pravim okolišem.
- **Prihvaćanje:** na 16:9 i 16:10 prozoru nema crnih praznina u igralištu niti tvrdih rubova
  svijeta; igra se igra jednako.

### M4.2 HUD overlay

- HUD se crta iz stanja igre, a ne iz `VGAScreenSeg`: štit, oklop, snaga, oružja i njihove razine,
  sidekickovi, bodovi, poruke.
- Raspored: lijevi i desni panel na rubovima prozora, ili kompaktni overlay.
- Iteracija 1: originalne HUD grafike (`OPTION_SHAPES`) složene na nove pozicije.
- Iteracija 2: vlastiti HUD u visokoj rezoluciji u istom stilu.
- Tekstovi u igralištu ("WARNING", poruke, bodovi) ostaju overlay kao sada.
- Izbornici, shop i dijalozi ostaju originalni 2D (letterbox).
- **Prihvaćanje:** sve informacije iz originalnog HUD-a su vidljive i čitljive na 1280×720 i na 4K.

### M4.3 Postavke

- 3D on/off, modeli, preset kamere, kvaliteta. Sprema se u `opentyrian.cfg`.
- Stavke u setup izborniku igre (`opentyr.c`).

### M4.4 Posebne razine

- **Naopaki prikaz** (`starShowVGASpecialCode == 1`): kamera se zrcali, ili se zrcali projekcija.
- **Spotlight** (`== 2`): scena se zatamni, a BTBH spot svjetlo prati igrača. Prirodno 3D rješenje
  umjesto pikselske maske.
- **Prihvaćanje:** obje vrste razina izgledaju točno u sweepu.

---

## M5: Neprijatelji epizode 1, predmeti i sjene

### M5.1 Ručni modeli neprijatelja

- Redoslijed po učestalosti iz kataloga. Prvi val je oko 30 najčešćih tipova u epizodi 1.
- Svaki tip: model, yaw način, emisivni dijelovi, skala poravnata sa spriteom.

### M5.2 Stanja

- Pogodak: `enemy[i].filter` postaje emisivni bljesak u boji filtera.
- Neranjivost igrača: treperenje ili prozirnost.
- Smrt: model nestaje točno kad i sprite, a eksplozija preuzima.

### M5.3 Predmeti

Novčići, dragulji, power-upi i data cubeovi kao rotirajući 3D predmeti sa sjajem. To su "neprijatelji"
iz sheetova 10 i 11.

### M5.4 Sjene

- Directional shadow map u BTBH-u.
- Slojevi tla i pozadina primaju sjenu, a da ne izgube originalne boje. To traži varijantu shadera
  "unlit + prima sjenu" u forku renderera.
- 2D sprite sjene se isključuju kad ih zamijene prave.

- **Prihvaćanje:** prvi val ima modele, katalog pokazuje napredak, a sjene padaju na tlo i oblake.
  Korisnik odobrava izgled razine 1 kao referencu za ostale.

---

## M6: Bossovi i ostale epizode

- Višedijelni neprijatelji i bossovi slažu se od više enemy slotova. Model se dijeli na iste dijelove
  ili se jedan model veže na glavni slot, a ostali slotovi postaju skriveni dijelovi.
- Epizode 2–5 rade se valovima po učestalosti, kao u M5.1.
- **Prihvaćanje:** katalog pokazuje 100 % ručnih modela za tipove koji se pojavljuju više od N puta.
  Ostali koriste volumetrijske spriteove.

---

## M7: Efekti i svjetlo

- **Metci:** emisivni billboardi ili mali meshevi s bloomom, u boji originala. Laseri kao trake.
- **Eksplozije:** billboard animacija plus čestice i kratki bljesak svjetla.
- **Superpixeli** (`JE_drawSP`) kao čestice.
- **Svjetla:** jedno spot svjetlo za spotlight razine. Za bljeskove eksplozija treba procijeniti
  više točkastih svjetala u forku, ili radiance cascades koje BTBH već ima.
- **Post:** bloom, ACES ili PBR neutral tonemapping, blagi grading po paleti razine, SMAA. Opcionalno
  suptilni tilt-shift.
- **Prihvaćanje:** efekti ne skrivaju metke (čitljivost je prioritet). 3D prezentacija ostaje ispod
  oko 8 ms po frameu na 4K na M-seriji, uz dovoljno rezerve za tempo igre (oko 35 fps logike).

## M8: Okruženje

- **Tileovi pozadine:** pixel-art upscale (xBRZ/hqx stil) i normal ili height mape izvedene iz
  tileova, za blagi reljef pod svjetlom.
- **Oblaci (BG2/BG3):** meki alfa rubovi i dubina s više pomaknutih kopija.
- **Strukture u tileovima** (zgrade, cijevi): 3D propovi, dugoročno.
- **Bočne strane** iz M4.1 dobivaju pravi okoliš.

## M9: Robustnost i izdanje

- Svi modovi: 2 igrača, Galaga, timed battle, Super Arcade. Destruct ostaje 2D.
- Pun sweep svih epizoda u 3D i 2D modu, bez rušenja i vizualnih grešaka.
- Vulkan na macOS-u (MoltenVK). Build na Windowsu i Linuxu sa SDL3 i assimp kao vendored
  submoduleima renderera.
- Paket: macOS `.app`, odabir direktorija s podacima, licence i atribucije.

---

## 2. Rizici

| Rizik | Ublažavanje |
| --- | --- |
| Diff-based hvatanje slojeva griješi na rubnim slučajevima (pikseli iste boje, efekti preko cijelog ekrana) | Objekti s modelom i volumetrijskim spriteom ne idu kroz diff; sweep otkriva greške po razini. |
| Bočni overscan dira pretpostavke o pitchu u starom kodu | Postupno, iza zastavice; 2D put mora ostati identičan (usporedba dumpova). |
| Količina ručnih modela (stotine tipova) | Volumetrijski spriteovi daju pokrivenost odmah; ručni modeli idu po učestalosti. |
| Vjernost modela u odnosu na sprite | Preglednik s usporedbom tlocrta i kontrolne točke s korisnikom po valu. |
| Promjene renderera kolidiraju s BTBH razvojem | Male općenite funkcije na `tyrian3d` branchu, kasnije PR prema BTBH-u po želji. |

## 3. Pitanja za korisnika

1. ~~**Blender** za modeliranje od M3 dalje?~~ Odobreno; Blender 5.2.2 je već instaliran.
2. ~~**Volumetrijski spriteovi** kao zadani prikaz?~~ Da ("dobro je, kasnije lako to tweakamo").
3. **Javni repo?** `duke4e/Tyrian3D` je zasad privatan. Projekt je GPL-2.0, a podaci igre nisu u repou.

Korisnikov zahtjev od 2026-10-07: renderer igre odsijeca sve što ne stane na staru 2D kameru; 3D
kamera mora vidjeti nacrtan cijeli svijet. Za pozadine i zvjezdano polje to je riješeno
izravnim crtanjem mapa u 3D-u (`src/background3d.c`), što pokriva i dio M4.1 (popuna strana
izvan mape).

## 4. Stanje

Gotovo na branchu `tyrian3d/m1-tools`: M1.1, M1.2, M1.4, M2.1 i 3D pozadine. Od M1.3 postoji
`tools/modelkit` (stdlib glTF); preglednik modela i probni model kroz cijeli put još nisu
napravljeni. Sljedeće: M1.3 do kraja (preglednik, Blender pipeline), zatim M2.2 i M3.
