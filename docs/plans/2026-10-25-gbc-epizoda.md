# Tyrian3D: GBC epizoda (epizoda 7)

Datum: **2026-10-25**. Korisnik je odabrao varijantu B iz izvještaja o GBC ROM-u
(`data/gbc/report/index.html`): leveli Game Boy Color Tyriana (Tyrian 2000 GBC, World Tree Games, 2000,
freeware od 2007) kao dodatna epizoda PC enginea. Napomena korisnika: "svi asseti imaju 1:1 vizualno
mapiranje na ono što ima PC varijanta", pa se epizoda slaže od PC asseta, ne od GBC grafike.

## Što je provjereno

- **Neprijatelji:** GBC spriteovi su umanjeni PC spriteovi (U-brodovi, prstenovi, jaja iz `enemy_2`...);
  usporedba silueta s PC atlasima (`upscale/in`) ih nalazi. Svaki GBC tip neprijatelja dobiva PC
  neprijatelja (epizoda, broj) iz PC levela iste teme.
- **Teren:** GBC blokovi (16x16) su ponovno nacrtani, ne umanjeni PC tileovi (podudarnost piksela
  0.2-0.4). Ali raspored materijala (zemlja, stijena, trava, rubovi) odgovara PC tilesetu iste teme. Mapa
  se zato slaže od PC tileova sintetizatorom epizode 6 (`mapsynth.py`), s GBC mapom kao planom.
- **Mjerilo:** GBC 1 px = PC 1.5 px (GBC brod 16 px = PC 24 px; GBC traka 176 px = vidljivih 264 px PC
  polja). GBC blok 16x16 = 24x24 PC px, red PC mape (28 px) = 18.7 GBC px.

## Dijelovi

| GBC | PC |
|---|---|
| mapa (11 blokova x 125-200 redova) | layer 1 (14 x 300) od tileova PC tileseta iste teme (`shapes?.dat`), layer 2/3 prazni |
| skripta neprijatelja: okidači po udaljenosti + zapisi od 5 bajtova (stvori tip u grupi, brzina grupe, ...) | događaji 6/15/7 (stvori), 19 (brzina grupe po linku), 20 (cik-cak), 33 (drop), ... |
| tip neprijatelja (tablica od 10 bajtova po levelu, sprite) | PC neprijatelj istog spritea (enemydata.Importer ga unosi u epizodu) |
| boss na vrhu mape | boss blok originalnog PC levela iste teme (kao `placements` epizode 6) |
| glazba (25 pjesama) | PC pjesma istog levela |
| trgovina (Talon, Micros, Phoenix, Storm, Dragon, Carrot, U-Ship; 25 oružja) | PC brodovi i oružja istih imena |
| priča (Transon, Gencore, Microsol...) | tekstovi između levela, data cubeovi |

## Faze (svaka igriva, dokumentirana, commitana)

1. **Kostur i mape.** ✅ Epizoda 7 u igri (izbornik, sadržaj iz `assets/content/episode7` kao epizoda 6),
   svih 24 GBC mapa složenih od PC tileova (autotile po materijalima četvrtina tilea), PC glazba,
   trgovina (PC trgovine epizoda 1-4 raspoređene po epizodi).
2. **Neprijatelji.** ✅ GBC skripta je port PC event sustava (13 = 19 brzina grupe, 14 = 20 cik-cak, 16 =
   20 ubrzanje, 0b = 39, 02 = 2, 00 = 66, 21-24 težina, 28+ blokovi); svaki GBC tip dobiva PC
   neprijatelja po spriteu (silueta, sjenčanje, boja, svi frameovi; najprije neprijatelji PC levela
   koje GBC level sažima). Ručne ispravke: `tools/gbc/enemy_overrides.json` (svih 24 levela pregledano
   2026-10-25, `tools/gbc/review.py`); PC neprijatelji od više dijelova (rakete, lice s rukama, roboti,
   zeleni bombarderi, bunkeri) kao kandidati i spawn dio po dio.
3. **Bossovi i krajevi levela.** ✅ (prvi prolaz) Boss originalnog PC levela (ili srodnog, gdje original
   nema bossa) umjesto GBC bossa. Ostaje: GBC-ovi vlastiti bossovi i veliki brodovi ručno.
4. **Priča.** ✅ GBC tekstovi redom (`tools/gbc/story.py`) kao data cubeovi s PC portretima govornika,
   GBC kraj kao kraj epizode. Trgovina po GBC napredovanju: nije rađena (PC trgovine).
5. **3D:** ✅ teren, clean ground i vegetacija za nove mape (`tools/content/gbc/terrain.py`; korisnik
   odobrio 2026-10-25 da idu u `assets/terrain` i git kao za epizodu 6): postavke originalnog levela, visine
   površina prenesene po boji.

## Polish (2026-10-26, korisnik: prijelazi terena, nagurani i krivo okrenuti neprijatelji, šef prođe kroz ekran)

- Šef: kad cijeli uđe na ekran mapa staje, sat teče dalje (53), šef se ne spušta dalje; level završava
  kad je uništen (36) ili najranije 2400 tickova kasnije.
- Nagurani: GBC slaže veliki brod od više tipova jedan do drugog i od blokova komada; svaki takav
  objekt sad je jedan PC neprijatelj (zračni brod SAVARA, bombarderi, bunkeri, roboti, veliki brodovi).
- Okretanje: u 3D-u brodovi na nebu epizode 7 gledaju kamo lete.
- Teren: autotile bira cijele redove (Viterbi) tako da parovi susjednih tileova budu kakve imaju
  originali; 3D teren ponovo izgrađen.

## Šefovi, trgovina i načini igre (2026-10-26)

- Šefovi: `tools/gbc/bosses.py` snima kako izgledaju i stavlja ih uz tijela PC šefova. Većinom su
  umanjeni PC šefovi drugih levela, pa leveli dobivaju njihove sprajtove (TYRIAN: ASSASSIN, ASTEROID i
  OASIS: ASTEROID2-ov tenk, SPACE: ICE EXIT-ova kliješta, SAVARA: zračni brod SAVARA V, SAVARA II: crvena
  tvrđava SAVARA, ASTEROID2: kupola ASTEROID1, ICE EXIT i DELI CORE: lubanja DREAD-NOT, DELIANI: brod s
  kliještima DELIANI).

## GBC ponašanje šefova iz ROM-a (2026-10-27, korisnik: kretanje i napadi što vjernije iz ROM-a)

- GBC šef nije zaseban kod: to su neprijatelji iz tablice tipova levela koje skripta stvara i vodi kao i
  ostale, a zadnji dio skripte se vrti u petlji (naredba 06 vraća sat). Naredbe: 02 s trećim bajtom
  zaustavlja mapu (sat ide dalje), 05 završava level kad grupa nestane, 0e pušku i ritam paljbe grupe,
  0a životne bodove, 1d brzinu i ritam, 13 s 99 navođenje prema brodu. Tablice tipova (`$c453`) i pušaka
  (`$c451`) daju bodove, početne brzine, puške, ritam, metke (brzina, ciljani, šteta, ulančani).
- `tools/gbc/boss_rom.py` to čita za 19 levela s petljom (`data/gbc/bosses/rom.json`) i leti svakog šefa
  u emulatoru kao referencu; `tools/gbc/boss.py` to pretvara u PC događaje: svaki GBC komad je PC
  neprijatelj (sprajt najbližeg dijela PC šefa) s GBC bodovima, početnom brzinom, puškama i lansiranjem;
  0e -> 31, 0a -> 25, navođenje -> 55, zaustavljanje mape -> 2/53/19, petlja -> 54, kraj -> 70 svakih 6
  tickova pa 41 i 11. `boss_review.py` crta `Lnn_pieces.png` za provjeru izgleda.
- Komadi grupe dijele link 101-120; u epizodi 7 komad na tim linkovima pogiba sam (`tyrian2.c`
  `gbc_piece_link`), jer u PC-u pogođeni neprijatelj ruši cijeli svoj link, a GBC-ovi komadi padaju jedan po
  jedan. Brzine grupa šefa su GBC-ove (simulacija GBC-ova pomicanja, `$2109`, provjerena okvir po okvir u
  emulatoru), svaka promjena događaj 19; ostatak razlike (cijeli tickovi, GBC-ovi polupikseli) ispravlja se
  malim pomakom prema putu iz GBC leta po petlji (TYRIAN-ov šef se dizao 18 px po petlji, SAVARA-in 104).
- Pet levela bez GBC šefa (DELICORE, AST.BONUS, LAVA I, BUBBLES, FINALE) zadržava PC šefa (`boss_fight`).
- Provjera snimanjem (brod parkiran u kutu kao u GBC letu, `TYR3D_AUTOPILOT=park`) našla je i ispravila:
  JUNGLE II (petlja je cijeli level: grupe zadržavaju GBC brzine kroz ponavljanje, šef ~560 tickova kruži
  pa odleti, kao u GBC-u, i level tada završava; prije su ga PC koraci odnijeli za par sekundi), DELIANI
  (početak petlje uz promjenu brzine zaustavljene mape: zapis brzine se ponavljao i šef je odlutao),
  ICE EXIT (brzina zaokružena na tick skoka petlje gubila se: 104 px po petlji), ASTEROID i OASIS (dijelovi
  ASTEROID2-ova tenka nacrtani oštećeni od starta u PC-u nikad ne pucaju: zastavica maknuta), WARP i
  ASTEROID2 (GBC drži najviše 17 neprijatelja i 10 metaka: lansiranja i paljba komada to sad poštuju).
- Trgovina: `tools/gbc/shop.py` čita ponudu GBC trgovine prije svakog levela (18 trgovina); `build.py` je
  preslikava na PC predmete.
- Načini igre: GBC nema vlastitih pickupova; leveli dobivaju ispuštanja svog originala (ljubičaste kugle,
  oružja) raspoređena po GBC grupama.

## Otvoreno

- Obični GBC neprijatelji (provjereno u emulatoru i ROM-u 2026-10-27): miču se svojom početnom brzinom iz
  tipa (pola piksela po frameu za brzinu 1), a s mapom samo oni koje stvara naredba 03 ili parni blok
  (04 i neparni blokovi stoje na ekranu). Glavna skripta svima na nebu daje pomak mape i poništava početnu
  brzinu; šefovi su već ispravni. Za odluku: isto i za obične neprijatelje (mijenja kretanje u svim
  levelima).
- (Veliki brodovi su riješeni 2026-10-26: crveni bombarder SAVARA II i
  crvena kliješta DELI levela su PC-ovi brodovi od 7 i 12 dijelova; rudarski toranj ASTEROID2 nema PC
  parnjaka, pa je prvi vlastiti neprijatelj epizode 7: model `gbc_derrick.py`, sprajtovi iz modela u
  listu W, `tools/content/gbc/new_enemies.json`.)
- Rubovi mapa (autotile daje stepenaste prijelaze na nekim tilesetovima). Pokušano 2026-10-26: meko
  podudaranje po udjelima materijala u 4x4 podćelija tilea (glatkije obale u LAVA i JUNGLE, ali gubi
  strukturu: ASTEROID-ove rupe, DELICORE-ove zidove, SAVARA II otočiće) i hibrid s četvrtinama (sličan
  sadašnjem, ICE EXIT dobiva redove čahura). Nijedno nije jasno bolje, pa je ostao sadašnji autotile
  (Viterbi po parovima). Stepenice dolaze od malo dijagonalnih tileova u tilesetovima.
- Svi šefovi provjereni na oko 2026-10-26 (PC skripte); 2026-10-27 GBC ponašanje (vidi gore).
- GBC trgovina: ROM ima svoje nazive (oružja Pulse, Multi, Scatter, Sonic, Vulcan, Mega, Proton, Thunder,
  Fireball, Rail, Chip, Hotdog, L.Ball, Ninja, Banana, Fruit, Pretzel, IcePick, Laser, PowerS, Poison, Hyper,
  Arrow, Gumball, Plasma; brodovi Talon, Micros, Phoenx, Storm, Dragon, Carrot, UShip; generatori, štitovi,
  sidekickovi, na 0xfc00). Napredovanje po levelima još nije iščitano; za odluku korisnika.

## Podaci i git

ROM i sve izvučeno iz njega ostaje lokalno (`data/gbc`). `tools/gbc/episode.py` (numpy, PIL) iz
`data/gbc` i igrinih podataka piše razine kao JSON u `data/gbc/episode7`; `tools/content/gbc/build.py`
(samo standardna biblioteka) iz njih pri buildu piše `assets/content/episode7` (izvan gita, kao
epizoda 6). Bez `data/gbc` epizode 7 nema.
