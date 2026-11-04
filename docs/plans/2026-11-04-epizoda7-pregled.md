# Epizoda 7: vizualni pregled (noć 2026-11-04)

Sva 24 levela snimljena u 3D-u (1280x800, autopilot ne puca, god mode, tri do četiri kadra po levelu oko
350/950/1550 tickova). Kadrove je pregledao pomoćni agent, a ja sam provjerio najteže nalaze. Koordinate su u kadru
od 640x400.

## Nalazi, najteži prvi

1. **DELICORE, turret pored svoje kućice.** Turret stoji u okrugloj crnoj jami, a njegova plava kućica u obliku slova U
   stoji oko 40 px desno, prazna. Isti razred problema kao kvadratni turreti na DELIANI levelima: dijelovi jednog
   objekta (GBC-ova kompozicija od više protivnika) crtaju se s krivim razmakom. Provjereno. Popravak: naći koji su to
   protivnici (`TYR3D_LOG_SPRITES` u tom kadru) i ispraviti pomak dijela u `tools/gbc` sastavljanju ili
   `models.cfg` (`at=`).
2. **DELICORE i DELI CORE, ravne trake preko ljubičastih cijevi.** Preko segmentiranih cijevi leže glatke, neosjenčane
   ljubičaste trake s ravnim rubovima; u DELI CORE jedna presijeca okrugli spremnik i ide do desnog stupa. Provjereno.
   Izgleda kao tile bez HD verzije i reljefa (kao nedostajući HD tileovi seta W za Camanis 2: `tools/tiles_hd.py --add`,
   traži ESRGAN modele iz `devtools` Releasea).
3. **ASTEROID2, stepenasti ravni rubovi platformi bez kamenog ruba** (svi kadrovi). Postavke terena iste su kao za
   ASTEROID i AST.BONUS (`void: hole`, zaobljen rub je već uključen), pa rubovi dolaze iz same rekonstruirane karte
   (tileovi ravnih rubova). Popravak u rekonstrukciji karte (`tools/gbc/episode.py`: izbor PC tileova na rubovima).
4. **DELIANI:** vodena površina s ravnim gornjim rubom reže dno stupova (bez bijelog ruba kao drugi bazeni); desni
   bazen ima ravan rez na x≈530; duga siva cijev završava u zraku iznad crnog; velike crne površine bez poda (možda
   namjerno).
5. **SAVARA:** crna pukotina kroz platformu dolje lijevo, gdje se spušta stepenicom (oko 122-135, 340-385).
6. **LAVA II:** stijene kao četvrtasti i L-blokovi ravnih okomitih stranica; tamne pravokutne mrlje na narančastom tlu.
7. **ICE EXIT:** glatka užljebljena ploča i glatka traka ravnog donjeg ruba u mjehurastom ledu (možda namjerno).
8. **DELICORE:** hrpa praznih plavih U-kućica koje se preklapaju (vjerojatno isti uzrok kao 1).
9. **TUNNEL:** visoka uska kamena „rebra“ i ploče koje lebde, sa stranicama razvučene teksture (zidovi solida uzimaju
   boju ruba površine do dna: `render_gpu.c`, mreža reda terena).
10. Manje i nesigurno: TYRIAN (komadi olupina pored kratera, ne u njima), SPACE (siva kapsula kao pola ljuske), FLEET
   (blok trupa ravnog donjeg ruba), LAVA I (turreti na lavi umjesto na stijeni), SAVARA II (stup koji naglo prestaje).

Bez nalaza: ASTEROID, WARP, BUBBLES, CAMANIS, AST.BONUS, SPACE ATK, OASIS, DESERT, JUNGLE, JUNGLE II. FINALE-ov drugi
kadar je samo tamnosiv (snimka, ne nužno greška).

## Već napravljeno ove noći za epizodu 7

- Dijelovi jedne slike uništavaju se zajedno (`tyrian2.c` `gbc_mark_picture`).
- Novčići i kristali vrijede što piše (sve epizode).
- Companion shipovi lete kao pratnja (sve epizode), checkpointovi u dugim levelima (puna igra, jedan igrač).
- Do epizode 7 vodi izbor na kraju epizode 6 (Camanis 2 pa epizoda 7).

## Predloženi redoslijed

1, 8 (pomaci dijelova, isti uzrok), 2 (HD tileovi), 3 i 6 (rekonstrukcija karata), ostalo uz igranje.

## Drugi prolaz (2026-11-04, dan)

- **1 i 8 (DELICORE-ove prazne U-kućice):** nisu stand-inovi (DELICORE nema `.std`) ni pomaknuti dijelovi. To su
  samostalni protivnici epizode 3 broj 212 (sprite B81, model `camanis_boss_81`: donji lijevi režanj Camanisova srca),
  koje je prepoznavanje GBC protivnika (`tools/gbc/enemies.py`) izabralo za jedan DELICORE-ov tip (događaji 15 u 1371,
  1395, 1491, 1539...). I sam 2D sprite B81 je prazna plava U-kućica, pa 3D model vjerno prati sprite. Je li izbor
  dobar, vidi se tek uz GBC original: `data/gbc/Tyrian.gb` nije na ovom računalu. Ako nije, popravak je red u
  `tools/gbc/enemy_overrides.json` (`"L01:<tip>"`) i ponovno pokretanje `tools/gbc/episode.py`. Turret u okrugloj jami
  zaseban je protivnik. Objekte kadra ispisuje `TYR3D_LOG_OBJECTS=1`.
- **2 (ljubičaste trake):** DELICORE i DELI CORE nemaju nijedan tile bez HD verzije (provjereno prema `z.hdt`). Trake
  su ravni ljubičasti tileovi koje je sinteza karte (`tools/gbc/episode.py`, mapsynth) složila po GBC planu cijevi.
  Ista je priroda nalaza 3, 4, 5, 6 i 7: svi traže ponovnu sintezu karata, a za nju GBC ROM.
- **9 (TUNNEL):** zidovi solida i rupa sad uzimaju teksturu dublje s površine (piksel teksture na dva piksela dubine, do
  ruba tilea; `render_gpu.c` `TERRAIN_WALL_INSET`), pa pokazuju uzorak površine umjesto razvučenog ruba. Uska rebra i
  ploče koje lebde dio su karte.

## Treći prolaz: s GBC ROM-om (2026-11-04)

ROM je dodan (`data/gbc/Tyrian.gb`); emulator se na Windowsu gradi `zig cc`-om (`tools/gbc/gb.py`), a alat za teren
epizode 7 radi i na Windowsu (`tools/content/gbc/terrain.py`, `TYR3D_GAME_DIR`). Levele sam napravio iznova samo u
kartama (njihove događaje, koje je dorađivao i `tools/gbc/boss.py`, zadržao sam), pa im napravio novi teren:

- **Rijetki parovi tileova** (`episode.py` `rare`, `RARE`): par koji originali imaju manje od 12 puta sada košta, a
  par koji nemaju nikad košta barem toliko. ASTEROID2 dobiva duge ravne platforme kao PC original i više kamenih
  rubova umjesto stepenica, TUNNEL glatke zidove kanjona umjesto rebara, LAVA II rijeku lave bez prekida, a DELIANI i
  SAVARA urednije blokove. ICE EXIT s blažom postavkom (5, 0.25): ledena rijeka ostaje cijela, s manje ravnih ploča.
- **DELICORE i DELI CORE:** gornji slojevi uzeti su iz originala kakvi jesu (`as_they_are` (2, 3)), umjesto da ih
  sinteza slaže iznova, pa cijevi imaju prstenove i krajeve. Jedan tanak ravan komad cijevi ostaje, ali takav je i u
  originalu.
- **Plave U-letjelice na DELICORE-u** (GBC tipovi 2, 7 i 15, roj u formacijama) dobile su potkovu-elektromagnet
  iz SURFACE-a i CORE-a (epizoda 4, protivnik 202) umjesto donjeg režnja Camanisova srca (ocjena para bila je samo
  0,09). Novi par je zapisan u `enemy_overrides.json`.

Ostaje: DELIANI je crn tamo gdje GBC ima pod, jer je napravljen od BRAINIAC-ovih tileova (strukture nad prazninom).
Za pod bi trebao drugi PC original. Od pregleda još ostaju SAVARA-ina pukotina i ICE EXIT-ove glatke ploče (gornji
sloj). Vjerojatno su manje vidljive, ali nisu posebno provjerene.
