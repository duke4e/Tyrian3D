# Tyrian3D: plan novog sadržaja

Datum: **2026-10-09**. Korisnikove ideje: rogue mode s karticama, nova epizoda (iz mapa grupiranih po
tilesetovima i statistike neprijatelja, s nastavkom priče), novi brodovi i oružja u dučanu (iz stvari
koje postoje a ne prodaju se), overclock oružja (razine snage iznad 11), nova oružja nadahnuta
sidekickovima i obrnuto, beskonačni mode s proceduralnim levelima. Ovo je plan za razmišljanje i
odluke; ništa od ovoga još nije u kodu.

## 0. Principi

1. **Originalna igra ostaje originalna.** Epizode 1–5, njihovi dučani i balans se ne mijenjaju; novi
   sadržaj živi u novim modeovima (rogue, beskonačni), u novoj epizodi i iza postavke (npr. "Prošireni
   dučan"). 2D put (F3) i dalje radi i za novi sadržaj.
2. **Sadržaj je podatak.** Nova oružja, brodovi, sidekickovi, karte i leveli su datoteke u `assets/content/`
   (čitljiv format, npr. JSON), koje igra učitava pored originalnih podataka; ništa novo se ne
   "zakucava" u C.
3. **Leveli se grade alatima, ne ručno bajt po bajt.** Kompajler levela iz opisa (mapa iz dijelova
   postojećih mapa + događaji iz predložaka) u strukture igre; terrain/vegetacija/brisanje se generiraju
   isto kao za originalne mape.
4. **Debug let je alat za sve ovo**: svaki novi level se leti, premotava i snima.

## 1. Što imamo (činjenice iz podataka igre)

- **Neprodani predmeti** (postoje u podacima, ni jedan dučan epizoda 1–5 ih ne nudi):
  - brodovi: Stalker (8), U-Ship (10), Silver Ship (11), Nort Ship (12), Red Dragon (15), PeteZoomer
    (17), Rum Bottle (18); većina ih se koristi u Arcade/Super Arcade modeovima, Rum Bottle nigdje;
  - oružja (portovi): 6, 23–26, 31–39, 44, 46, 47 (Super Arcade, Nort cheat, SuperTyrian, HotDog...);
    portovi 48–60 su slobodni ("Test");
  - sidekickovi: Quicksilver (24), Flying Punch (32, nigdje korišten); 33–37 slobodni;
  - štit HXS Class B (10); specijalci (48 imenovanih) se nikad ne prodaju, dobivaju se kombinacijama
    tipki po brodu, dropovima i u Super Arcadeu.
- **Model oružja:** port ima 1–2 moda × 11 razina snage; svaka razina je zapis oružja (do 8 pod-hitaca,
  brzine, sprite, šteta, kašnjenje, navođenje...). U podacima je 1638 mjesta za zapise, ~750 korištenih;
  E4–5 imaju svoj (rebalansirani) skup.
- **Sidekick** je jedan zapis oružja (+ stil: fiksni, prateći, sprijeda, orbitalni; municija; punjenje),
  bez razina snage.
- **Leveli:** 70 mapa, samo **5 tilesetova** (`z` Tyrian/asteroidi/Deliani/rudnici – 37 mapa; `y` Savara;
  `x` džungla/Gryphon; `w` led/Ixmucane; lava/pustinja E4). Level = 3 sloja mapa (14×300, 14×600,
  15×600 tileova), lista do 40 nasumičnih neprijatelja, do 2500 događaja (sat je pozicija skrolanja).
  Ukupno ~60 000 događaja; najčešći su spawn (tlo/nebo/vrh), pomaci i ubrzanja grupa, dropovi.
  Igra čita levele samo iz datoteka (čitač se da refaktorirati da čita iz memorije).
- **Statistika neprijatelja:** 2653 tipa u katalogu, 1749 se stvarno spawna; po tilesetu se zna koji se
  pojavljuju, na kojem sloju i koliko često; 43 mape imaju bossa (grupe od 4 dijela, oklop 254/255).
- **Priča:** datacubeovi (`cubetxtN.dat`) i tekstovi u skriptama epizoda. E5 završava otvoreno
  (Hazudra Collectors se ne javljaju, "tajna te progoni"); otvorene niti: tko su Hazudra, knjige o
  "Zemlji" i gravitacijskoj kori Tyriana, Vykromod kao bestjelesni entitet, Gencoreov "Nova" sustav,
  zmajevi Torm, kapetan Nob, oslabljeni Microsol.
- **Modeovi** u kodu: puna igra, arcade, 2 igrača, timed battle, Super Arcade/SuperTyrian, Galaga/ALE,
  Destruct. `dev_setup_game` već postavlja igru bez izbornika – dobra polazna točka za nove modeove.

## 2. Tehnička ograničenja (prije svega ostalog)

| Ograničenje | Posljedica | Rješenje |
|---|---|---|
| Fiksne veličine nizova predmeta (`PORT_NUM` itd.), slobodnih mjesta samo za portove (13), sidekickove (5), specijalce (6) | Novi brodovi/štitovi nemaju mjesta | Povećati nizove; novi sadržaj iz `assets/content` dodaje zapise iza originalnih |
| Snaga oružja do 11 raširena po kodu; arcade životi su spremljeni u bajtu snage; 20 od 47 portova već koristi 8 pod-hitaca na 11; najviše 81 hitac igrača; oklop neprijatelja do 254 | Overclock nije samo "još 4 zapisa" | Razdvojiti životi/snaga, podići granicu hitaca, overclock dobiva drugačije efekte (prodor, ponavljanje, jači pogodak) umjesto više pod-hitaca; jači neprijatelji samo u novom sadržaju |
| `EPISODE_MAX` 5, najviše 21 mapa po datoteci, `mainLevel` bajt, dva skupa podataka predmeta | Nova epizoda ne stane "pored" | Epizoda 6 kao vlastiti format (`assets/content/episode6/`), učitavanje levela iz memorije |
| Leveli konačni, ≤ 2500 događaja, sat u16 | Beskonačni level nije jedan level | Beskonačni = niz segmenata (svaki "mali level"), ili petlje kao u ALE/SQUADRON |
| Teren/vegetacija/brisanje se računaju offline po hashu mape | Proceduralne mape nemaju 3D teren | Segmenti iz unaprijed obrađenih dijelova mapa, ili ubrzati alate da rade u igri |
| Dučan: do 10 stavki po kategoriji, ilustracije samo za postojeće slike | Novi predmeti trebaju umjetnost | Modeli za nove predmete (već radimo modele), nove slike za dučan |

## 3. Plan po fazama (preporučeni redoslijed)

### Faza A – Temelji sadržaja (preduvjet za sve)
- Sloj sadržaja: `assets/content/*.json` za oružja (portovi + zapisi po razinama), brodove,
  sidekickove, specijalce, karte; učitavanje uz originalne podatke; veći nizovi.
- Čitač levela iz memorije + **kompajler levela**: opis (koje mape/dijelovi, tileset, događaji) → strukture
  igre; teren/vegetacija/brisanje se generiraju alatima za svaki kompajlirani level.
- Analizator levela (već ga ima istraživanje: događaji po temi, valovi, bossovi) kao alat u `tools/content/`.

### Faza B – Brze pobjede
- **Prošireni dučan** (postavka, isključena po defaultu za epizode 1–5): neprodani brodovi, portovi,
  sidekickovi i štit raspoređeni po dučanima prema napretku. Modeli brodova već postoje; trebaju slike/
  modeli dučana za nove portove.
- **Nova oružja iz sidekickova** (npr. Phoenix, Plasma Storm, Zica Flamethrower kao prednja oružja s 11
  razina, generiranih pravilima iz sidekickovog zapisa) i **novi sidekickovi iz oružja** (sidekick puca
  jednu razinu prednjeg oružja; jednostavno jer je sidekick samo jedan zapis).

### Faza C – Rogue mode (MVP bez novih levela)
- Igra = niz "sektora": svaki je postojeći level (ili njegov dio) iz teme; nakon sektora bira se 1 od 3
  **kartice**; smrt = kraj runa.
- Kartice u prvoj verziji koriste postojeće stvari: +razina oružja, novi port, sidekick, štit, generator,
  specijalac, popravak oklopa, novac. Druga verzija: kartice s novim efektima (veća šteta %, brža
  paljba, prodorni hici, štit koji se brže puni, odbijanje metaka...) – to je novi kod u logici hitaca.
- Mapa runa (grananje kao FTL/Slay the Spire) s izborom težine/nagrade; bossovi na kraju "čina".
- Debug let i autopilot za balans; statistika runova.

### Faza D – Overclock
- Razine 12–15 za odabrana oružja (u novoj epizodi i rogue modeu): novi zapisi u `assets/content`,
  razdvajanje snage od arcade života, podignute granice (hici, HUD do 15 kockica, cijene u dučanu).
  Overclock razine dobivaju kvalitativne efekte, ne samo više hitaca.

### Faza E – Epizoda 6
- **Priča:** nastavak niti o Hazudrama (zašto su probudili Trenta, što je "tajna"), Vykromod, gravitacijska
  kora Tyriana i knjige o "Zemlji"; novi datacubeovi i tekstovi u stilu originala.
- **Leveli:** po temama tilesetova (5 tema), derivacije postojećih mapa (rekombinacija dijelova, zrcaljenje,
  nove kombinacije slojeva) + događaji iz statističkih predložaka (valovi, tipični neprijatelji teme,
  bossovi); svaki level se ručno dotjeruje debug letom.
- **Novi neprijatelji** kao varijacije postojećih (oklop, oružja, ponašanje), s modelima.
- Overclock, novi brodovi i oružja dolaze kroz njene dučane.
- **Nova sekcija dučana: specijalna oružja** (korisnik, 2026-10-09): Flare i ostali specijalci (48 imenovanih;
  u originalu se nikad ne prodaju, dobivaju se kombinacijama tipki po brodu, dropovima i u Super Arcadeu) mogu
  se kupiti; kupljeni specijal se aktivira kao sad (punjenje/streljivo po svojim pravilima). Treba nova
  kategorija u izborniku dučana (ikona, opis, cijena, prikaz u simulatoru) i u `]I` listama nove epizode.

### Faza F – Beskonačni mode
- Proceduralni niz segmenata po temama: segment = komad mape (iz unaprijed obrađenih dijelova, s
  terenom) + generirani valovi iz statistike; težina raste; bossovi povremeno.
- Rezultati, ljestvica; može dijeliti kartice s rogue modeom (beskonačni rogue).

## 4. Odluke (korisnik, 2026-10-09)

1. **Prošireni dučan ne ide u prvi prolaz** originalnih epizoda; kasnije dolazi kao **New Game+**.
2. **Rogue:** da – permadeath, kratki runovi, mapa s grananjem, meta-napredak (otključavanja) između runova.
3. **Epizoda 6** po preporuci: nastavak niti o Hazudrama i "tajni", 8–12 levela.
4. **Overclock** po preporuci: kvalitativni efekti (prodor, brža paljba, jači pogodak...), ne više pod-hitaca.

Faza A se dijeli: **A1 sloj sadržaja** (odmah, preduvjet za B i C) i **A2 kompajler levela** (prije faze E).

## 5. Pitanja koja su bila otvorena

1. **Smiju li originalne epizode dobiti prošireni dučan** (kao opcija), ili novi predmeti samo u novom
   sadržaju?
2. **Rogue struktura:** permadeath i kratki runovi (20–40 min), mapa s granama, meta-napredak između
   runova (otključavanje karata/brodova) da ili ne?
3. **Epizoda 6:** smjer priče (Hazudra i "tajna" je najprirodniji nastavak) i duljina (8–12 levela?).
4. **Overclock:** samo kvalitativni efekti, ili i više hitaca/šteta (traži jače neprijatelje)?
5. Redoslijed: preporuka je A → B → C → D → E → F (rogue rano jer koristi postojeće levele i brzo daje
   igrivo iskustvo; epizoda 6 kad postoje alati i novi predmeti; beskonačni zadnji jer ovisi o svemu).
