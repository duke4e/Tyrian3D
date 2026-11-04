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
