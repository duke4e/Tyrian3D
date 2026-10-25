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
   koje GBC level sažima). Ručne ispravke: `tools/gbc/enemy_overrides.json`.
3. **Bossovi i krajevi levela.** ✅ (prvi prolaz) Boss originalnog PC levela (ili srodnog, gdje original
   nema bossa) umjesto GBC bossa. Ostaje: GBC-ovi vlastiti bossovi i veliki brodovi ručno.
4. **Priča.** ✅ GBC tekstovi redom (`tools/gbc/story.py`) kao data cubeovi s PC portretima govornika,
   GBC kraj kao kraj epizode. Trgovina po GBC napredovanju: nije rađena (PC trgovine).
5. **3D:** ✅ teren, clean ground i vegetacija za nove mape (`tools/content/gbc/terrain.py`; korisnik
   odobrio 2026-10-25 da idu u `assets/terrain` i git kao za epizodu 6): postavke originalnog levela, visine
   površina prenesene po boji.

## Otvoreno

- Pregled podudaranja neprijatelja po levelima (`data/gbc/episode7/preview/Lnn_enemies.png`).
- Rubovi mapa (autotile daje stepenaste prijelaze na nekim tilesetovima).

## Podaci i git

ROM i sve izvučeno iz njega ostaje lokalno (`data/gbc`). `tools/gbc/episode.py` (numpy, PIL) iz
`data/gbc` i igrinih podataka piše razine kao JSON u `data/gbc/episode7`; `tools/content/gbc/build.py`
(samo standardna biblioteka) iz njih pri buildu piše `assets/content/episode7` (izvan gita, kao
epizoda 6). Bez `data/gbc` epizode 7 nema.
