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
- Obični neprijatelji kao u ROM-u (2026-10-27, korisnik: da): svaki kreće početnom brzinom svog tipa
  (tablica tipova, bajtovi 3 i 4; 99 navođenje prema brodu), a s mapom pluta samo ako ga je stvorila
  naredba 03 ili parni blok (04, neparni blokovi i 21-24 ne plutaju: zastavicu računa kao 4 minus naredba); 13 s 99 uključuje navođenje, bez njega ga
  gasi. Prije su svi kretali na mjestu i plutali s mapom. Brzina po y ide u sam događaj stvaranja (po
  neprijatelju), x i navođenje po linku grupe; zemaljski koje GBC ne nosi dobivaju brzinu mape oduzetu.
  Provjera (`tools/gbc/moves.py` uz `TYR3D_LOG_MOVES`): u TYRIAN, ASTEROID, OASIS, SPACE ATK i DELICORE
  284 od 293 uparena stvaranja ide unutar piksela po ticku od GBC-a; ostatak je navođenje prema brodu
  (GBC ubrzava bez gornje granice, PC-ov 55 samo približno) i prvi koraci cik-caka.
- Brzina, nestajanje i okretanje (2026-10-28, korisnik: neki protivnici prebrzi i prenagli, neki nestaju
  sami od sebe, neki okrenuti na krivu stranu; šefovi prebrzi): prijevod GBC frame računa kao 0.375 PC
  tickova, a PC tick traje 28.75 ms, pa je sve išlo 1.55 puta brže od GBC-a. Epizoda 7 sad tickuje u ritmu
  GBC-a (44.6 ms, `GBC_PACE`). Pucanj u jednog neprijatelja ubijao je cijelu njegovu GBC grupu (PC ubija
  link zajedno); sad svaki umire sam, osim dijelova istog neprijatelja (događaj 201). Modeli više ne
  okreću glavu prema smjeru leta: gledaju niz ekran kao GBC sprajtovi i naginju se do 40° u stranu.
- Šefovi cijeli (2026-10-28, korisnik: šefovi imaju čudnih vizualnih dijelova): svaki GBC komad crtao se kao
  jedan dio PC šefa, pa su šefovi bili nepotpuni (TYRIAN 9 od 12 ASSASSIN-ovih dijelova) a komadi koji se
  odvoje izgledali kao krhotine. U 3D-u grupa od 4+ komada sad crta cijelo tijelo PC šefa (svaki dio crta
  najbliži komad, događaj 202), a manje grupe dio koji izgleda cijelo (`boss_looks.json`, po oku; WARP-ovi
  mjehuri STARGATE-ova velika kugla). JUNGLE-ovi zeleni lovci uz tenk (tip 04, list H nije učitan) crtali su se
  kao četvrtina tenka: sad 2:760 (`enemy_overrides.json`).
- Nestajanje, flare, pill (2026-10-29, korisnik: na 2. levelu asteroidi nestaju na pola ekrana, na SAVARI
  nestaju veliki avioni; flare pokazuje stare teksture; upgrade pill diže prazno stražnje oružje). 3D pregled
  nadolazećih neprijatelja crtao je i one koje događaj 66 na Easy/Normal preskače (GBC zapisi 21-24): sletjeli
  bi i nestali gdje bi se stvorili. Sad ih preskače kao i igra. Flare (filtar svjetline koji treperi svaki
  tick) mijenjao je boje tileova svaki tick, pa HD boje nikad nisu stigle: teren se sad crta u bojama bez
  filtra i samo zatamnjuje, a stari redovi terena se ne brišu nego označe za ponovno bojanje. Power-up koji u
  svom portu nema što dići (nema oružja ili je na punoj snazi) u epizodi 7 diže drugi port.
- Pickupi (2026-10-29, korisnik: pickupa je malo): PC original daje predmet grupi neprijatelja (događaji 33,
  45: arcade); GBC levelu se dodaju na vrijeme u istom omjeru prema trajanju levela. Grupa se sad bira po
  veličini kao u originalu (koliko komada ubiti), predmet ide nakon toliko komada, a neuništivi i šefovi
  (osim kad je šef cijeli level) ne nose predmete.
- Balans (2026-10-29, korisnik: Easy je prilično težak; uzmi omjere iz PC originala): svaki level i njegov
  original odigrani na Easy u Arcadeu (autopilot puca, god mode, `TYR3D_LOG_BALANCE`), šteta po 1000 tickova
  i tko ju je nanio. Uzroci: PC neprijatelji koji glume GBC-ove imali su svoje oklope i puške (BUBBLES-ovi
  mjehuri pucali su svaki tick, a GBC-ovi nikad; DELICORE-ovi zidovi se nisu mogli srušiti), a šefovi PC-ov
  Easy (oklop x0.75). Sad svaki neprijatelj dobiva GBC-ove bodove života i ritam paljbe (događaj 203: tip
  tablice bajtovi 1, 5, 6; jedna puška kao na GBC-u; naredba 0e postaje događaj 31), GBC-ova pravila težine
  (Easy pola života, puške točku manje štete; Hard 1.5x i točku više), a levelima koji su i dalje iznad
  originala neprijatelji pucaju rjeđe (`FIRE_PACE`: SAVARA 4x, JUNGLE 3.5x, DESERT 2.8x, AST.BONUS 2x, SPACE
  ATK 1.8x). Ukupna šteta 24 levela 5919 -> 1723; omjer prema originalu npr. TYRIAN 1.7 -> 0.8, ASTEROID
  2.0 -> 0.9, SAVARA 3.6 -> 1.4, JUNGLE 4.3 -> 1.2, BUBBLES 21 -> 1.6, CAMANIS 2.4 -> 0.5, SPACE ATK 5.9 ->
  1.1. Kasniji leveli (originali iz epizode 4) i dalje su lakši od originala, kao na GBC-u.
- Gornji slojevi (2026-10-29, korisnik: grafika je još gruba): GBC ima jednu mapu, pa su slojevi 2 i 3 bili
  prazni, a PC originali na njima imaju oblake, stijene, led, brodove i palube koji daju dubinu. Sad se
  slojevi 2 i 3 rade iznova iz originalovih (`episode.py` `upper_layers`, sintetizator epizode 6, jednako
  puni kao u originalu) gdje original na njima ima više od jednog tilea punila ili natpisa na startu, i
  idu brzinom koju u originalu najdulje drže prema sloju 1 (TYRIAN 2x i 3x), najviše koliko im mapa traje
  do šefa. SAVARA uzima oblake SAVARE V. Postavke terena dobivaju kao originalovi (krute stijene gdje su
  ondje kruti). Eksplozije u epizodi 7 i dalje plutaju sa slojem 1.
  Ostalo nepopravljivo slojem 1: GBC TYRIAN ima tamne jame u polju kamenja, a PC tileset nema tamnog tla.
- Feedback 2026-10-29 (korisnik, nakon igranja):
  - Šefovi su jedno tijelo: GBC bodovi života dijelova koji se mogu pogoditi idu u jedan zajednički
    spremnik (zbroj kroz korijen broja dijelova: TYRIAN 780 -> 260), svaki pogodak bilo kojeg dijela ide u
    njega, a kad se isprazni svi dijelovi umiru zajedno; traka šefa ga pokazuje. Kretanje ostaje GBC-ovo.
  - Epizoda 7 je brža: tick 1.25x PC-ovog (bio 1.55x, GBC-ov tempo), otprilike pola puta do PC-a.
  - GBC tip s 0 bodova života na GBC-u umire na prvi pogodak; dosad je zadržavao PC oklop (JUNGLE-ov
    neprijatelj za zabijanje 120, LAVA I 250). Sad ima 1. Blok čiji zbroj prelazi 255 više ne pada na PC oklop.
  - Trgovina: GBC liste su kratke kao i PC-ove (3-5), ali stalno iz istih nekoliko; sad uz GBC-ove stvari
    dolaze i stvari PC trgovine na istom mjestu napredovanja, najviše 6 po listi.
  - GBC glazba: `music.py` nalazi petlju svake pjesme iz zapisa registara i reže je; leveli epizode 7
    sviraju svoju GBC pjesmu, a kad dođe šef GBC pjesmu šefa (događaj 204). Trgovine i izbornici ostaju PC.
  - GBC glazba kroz SoundFont (korisnik: pustiti je i kroz soundfont): `midi.py` čita note iz istih zapisa
    registara (svaki okidač je nota, frekvencija visina, envelope glasnoća) i piše MIDI; dijelovi dobivaju
    GM programe po ulozi, iz palete PC pjesama (bas 38/39, lead 81/80, kratke 62, swell 50, tihe 90, šum kao
    bubnjevi). Kad glazba ide kao MIDI, epizoda 7 svira `.mid` kroz isti synth (`music_midi_song_*`), inače WAV.

## Otvoreno

- (Veliki brodovi su riješeni 2026-10-26: crveni bombarder SAVARA II i
  crvena kliješta DELI levela su PC-ovi brodovi od 7 i 12 dijelova; rudarski toranj ASTEROID2 nema PC
  parnjaka, pa je prvi vlastiti neprijatelj epizode 7: model `gbc_derrick.py`, sprajtovi iz modela u
  listu W, `tools/content/gbc/new_enemies.json`.)
- Rubovi mapa (autotile daje stepenaste prijelaze na nekim tilesetovima). Pokušano 2026-10-26: meko
  podudaranje po udjelima materijala u 4x4 podćelija tilea (glatkije obale u LAVA i JUNGLE, ali gubi
  strukturu: ASTEROID-ove rupe, DELICORE-ove zidove, SAVARA II otočiće) i hibrid s četvrtinama (sličan
  sadašnjem, ICE EXIT dobiva redove čahura). Nijedno nije jasno bolje, pa je ostao sadašnji autotile
  (Viterbi po parovima). Stepenice dolaze od malo dijagonalnih tileova u tilesetovima.
  Riješeno 2026-10-29 (korisnik: teren ima čudnih spojeva): uzrok nije bio tileset nego filtar "tlo
  stoji uz samo sebe", koji je izbacio sve kutove i rubove obala (SAVARA II je imao 16 od 58 tileova),
  pa je svaki otok bio odsječen. Sad autotile ima i njih, nepoznati par košta po neskladu piksela na
  spoju (dvije trave se spajaju, trava uz more ne), cijela mapa se rješava odjednom (belief
  propagation, pa red po red), a materijali se računaju po površini koju tileovi pokrivaju u originalu
  (CAMANIS i ICE EXIT opet imaju kaldrmu umjesto prugaste ploče). Loših spojeva u GBC redovima: 175
  umjesto 3078; otoci zaobljeni s obalama, litice, slapovi i cijevi kao u PC originalima.
- Svi šefovi provjereni na oko 2026-10-26 (PC skripte); 2026-10-27 GBC ponašanje (vidi gore).
- GBC trgovina: ROM ima svoje nazive (oružja Pulse, Multi, Scatter, Sonic, Vulcan, Mega, Proton, Thunder,
  Fireball, Rail, Chip, Hotdog, L.Ball, Ninja, Banana, Fruit, Pretzel, IcePick, Laser, PowerS, Poison, Hyper,
  Arrow, Gumball, Plasma; brodovi Talon, Micros, Phoenx, Storm, Dragon, Carrot, UShip; generatori, štitovi,
  sidekickovi, na 0xfc00). Napredovanje po levelima iščitano 2026-10-27 (`tools/gbc/shop.py`, svaka trgovina
  Full Gamea u `data/gbc/shop.json`; `build.py` ih stavlja u blokove trgovina), provjereno u igri.

## Podaci i git

ROM i sve izvučeno iz njega ostaje lokalno (`data/gbc`). `tools/gbc/episode.py` (numpy, PIL) iz
`data/gbc` i igrinih podataka piše razine kao JSON u `data/gbc/episode7`; `tools/content/gbc/build.py`
(samo standardna biblioteka) iz njih pri buildu piše `assets/content/episode7` (izvan gita, kao
epizoda 6). Bez `data/gbc` epizode 7 nema.
