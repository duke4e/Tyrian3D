"""Builds data/gbc/report/index.html: what the GBC Tyrian ROM holds (from extract.py, songs.py and
the screens in data/gbc/screens), for choosing what to make of it. Local only (the ROM's content)."""
import base64
import html
import json
import os
import shutil
import subprocess
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gb as G

D = os.path.join(G.ROOT, 'data', 'gbc')
R = os.path.join(D, 'report')

CSS = """
:root{--bg:#17120d;--panel:#231b13;--ink:#efe4d2;--dim:#b5a68e;--gold:#d9a441;--line:#3a2e20}
@media (prefers-color-scheme: light){:root:not([data-theme=dark]){--bg:#f6f0e6;--panel:#fffaf2;--ink:#2a2118;--dim:#6d5f4b;--gold:#9a6a12;--line:#e2d6c2}}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 -apple-system,Segoe UI,sans-serif}
main{max-width:1180px;margin:0 auto;padding:24px 16px 64px}
h1{font-size:28px;margin:8px 0 4px;color:var(--gold)} h2{margin:36px 0 10px;border-bottom:1px solid var(--line);padding-bottom:6px}
h3{margin:18px 0 6px} p,li{max-width:80ch} .dim{color:var(--dim)}
.grid{display:flex;flex-wrap:wrap;gap:12px} figure{margin:0;background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:8px}
figcaption{font-size:12px;color:var(--dim);margin-top:4px;max-width:340px}
img.px{image-rendering:pixelated} .maps{display:flex;gap:8px;overflow-x:auto;padding-bottom:8px}
.maps figure{flex:0 0 auto} .maps img{width:132px;height:auto;display:block}
table{border-collapse:collapse;font-size:13px} td,th{border-bottom:1px solid var(--line);padding:4px 10px;text-align:left}
.opt{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:12px 16px;margin:12px 0}
.opt h3{margin-top:4px;color:var(--gold)} audio{width:260px;height:32px}
code{background:var(--panel);padding:1px 5px;border-radius:4px}
"""


def img(src, w=None, cls='px', alt=''):
    """Images go inline (data URIs) so the page shows anywhere; the audio stays beside it."""
    ws = f' width="{w}"' if w else ''
    data = base64.b64encode(open(os.path.join(R, src), 'rb').read()).decode()
    return f'<img class="{cls}" src="data:image/png;base64,{data}"{ws} alt="{html.escape(alt)}">'


def main():
    os.makedirs(os.path.join(R, 'img'), exist_ok=True)
    os.makedirs(os.path.join(R, 'audio'), exist_ok=True)
    levels = json.load(open(os.path.join(D, 'levels.json')))
    songs = json.load(open(os.path.join(D, 'music', 'songs.json')))
    lv = [levels[k] for k in sorted(levels, key=int)]

    # screens
    shots = []
    for n in ['copyright', 'intro_transon', 'title', 'title_menu', 'story', 'story2', 'shop_main', 'shop_items', 'shop_ship']:
        p = os.path.join(D, 'screens', n + '.png')
        if os.path.exists(p):
            Image.open(p).resize((320, 288), Image.NEAREST).save(os.path.join(R, 'img', f'screen_{n}.png'))
            shots.append(n)
    # level images
    for l in lv:
        d = os.path.join(D, 'levels', f"L{l['level']:02d}_{l['name']}")
        tag = f"L{l['level']:02d}"
        shutil.copy(os.path.join(d, 'map.png'), os.path.join(R, 'img', f'{tag}_map.png'))
        for n in ['gallery', 'run', 'sprites']:
            if os.path.exists(os.path.join(d, n + '.png')):
                shutil.copy(os.path.join(d, n + '.png'), os.path.join(R, 'img', f'{tag}_{n}.png'))
    # audio
    for s in songs:
        if 'file' in s:
            src = os.path.join(D, 'music', s['file'])
            dst = os.path.join(R, 'audio', s['file'].replace('.wav', '.m4a'))
            if os.path.exists(src) and not os.path.exists(dst):
                subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', src, '-c:a', 'aac', '-b:a', '96k', dst], check=True)

    song_of = {}
    for s in songs:
        song_of[(s['bank'], s['ptr'])] = s.get('file') or next(x['file'] for x in songs if x.get('file') and x['hash'] == s['hash'])
    out = [f'<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
           f'<title>Tyrian GBC ROM</title><style>{CSS}</style><main>']
    a = out.append
    a('<h1>Tyrian 2000 za Game Boy Color: što je u ROM-u</h1>')
    a('<p class="dim">Izvještaj za odabir: što bi "remaster" GBC verzije trebao biti u Tyrian3D. Sve slike i zvuk su izvučeni iz tvog ROM-a '
      '(<code>Downloads/Tyrian.gb</code>) i stoje samo lokalno u <code>data/gbc/</code> (izvan gita).</p>')

    a('<h2>Ukratko</h2><ul>')
    a('<li><b>Igra:</b> Tyrian 2000 za GBC (World Tree Games, izdavač Symmetry Entertainment, ©2000), otkazana kad je izdavač propao; '
      'World Tree Games ju je 2007. pustio kao freeware. Sasvim druga igra od PC verzije: vlastitih 24 levela, neprijatelji, bossovi, grafika i glazba; '
      'priča sažima epizode 1-4 (Transon, Gencore, Microsol...).</li>')
    a('<li><b>ROM:</b> 512 KB, MBC1 + 8 KB baterijskog RAM-a, radi i na crno-bijelom GB-u ali je rađen za GBC (CGB palete). '
      'Pisan u C-u (GBDK): kod je čitljiv, podaci su sažeti GBDK kompresijom.</li>')
    a('<li><b>Kako sam ga čitao:</b> nisam ništa skidao. Napisao sam mali GBC emulator u C-u (<code>tools/gbc/gbemu.c</code>, CPU, MBC1, PPU, CGB banke, HDMA) '
      'kojim se igra vrti bez prozora: kroz izbornike do svakog levela, uz bilježenje VRAM-a, paleta, OAM-a i zvučnih registara, plus disassembler za kod.</li>')
    a('<li><b>Izvučeno:</b> svih 24 levela (pune mape, tileovi, palete, spriteovi, galerija neprijatelja), 25 različitih pjesama (WAV), ekrani izbornika i priče.</li></ul>')

    a('<h2>Izbornici i priča</h2><div class="grid">')
    caps = {'copyright': 'Uvodni ekran', 'intro_transon': 'Transon (Gencore) u uvodu', 'title': 'Naslov', 'title_menu': 'New Game / Load / Extras',
            'story': 'Priča između levela', 'story2': 'Priča', 'shop_main': 'Trgovina: Items / Save / Start', 'shop_items': 'Ship, Weapon, Engine, Shield, Side A/B',
            'shop_ship': 'Kupnja broda (Talon...)'}
    for n in shots:
        a(f'<figure>{img(f"img/screen_{n}.png", 240)}<figcaption>{caps.get(n, n)}</figcaption></figure>')
    a('</div><p>Trgovina ima 7 brodova (Talon, Micros, Phoenix, Storm, Dragon, Carrot, U-Ship), 25 prednjih oružja (Pulse, Multi, Vulcan, Laser, Banana, Hotdog...), '
      'motore, štitove i dvije bočne kutije oružja (Side A/B: Single, Dual, Shield, Repair, Bomb, Magnet, Charge, Cold, Heat). Načini: Full Game i Arcade, '
      'težine Easy/Normal/Hard, igra za dvoje.</p>')

    a('<h2>Leveli</h2><p>Svaka mapa je okomita traka 11 blokova od 16x16 px (176 px, ekran je 160) i 125 do 200 redova (2.000-3.200 px), '
      'iz ROM-a se čita odozdo prema gore. Blok = 4 tilea + paleta po bloku. Na vrhu mape stoji boss u petlji pozadine. '
      'Zgrade, topovi i brodovi na tlu nisu dio mape nego spriteovi (neprijatelji).</p>')
    a('<div class="maps">')
    for l in lv:
        a(f"<figure>{img('img/L%02d_map.png' % l['level'], alt=l['name'])}<figcaption>{l['level']}. {html.escape(l['name'])}<br>{l['rows']} redova</figcaption></figure>")
    a('</div>')
    a('<table><tr><th>#</th><th>Level</th><th>Bank</th><th>Duljina</th><th>Blokova</th><th>Glazba</th></tr>')
    for l in lv:
        f = song_of.get((l['bank'], l['song']), '')
        a(f"<tr><td>{l['level']}</td><td>{html.escape(l['name'])}</td><td>{l['bank']:02x}</td><td>{l['rows'] * 16} px</td><td>{l['blocks']}</td><td>{f.replace('.wav', '')}</td></tr>")
    a('</table><p class="dim">Level 24 nema ime u tablici imena (bank 1f, kratka mapa od 40 redova): vjerojatno završni dio.</p>')

    a('<h2>Neprijatelji i bossovi</h2><p>Spriteovi kako ih igra slaže na ekranu dok level prolazi sam od sebe (brod puca, ne izbjegava). '
      'Neprijatelje vodi skripta po levelu: lista okidača po prijeđenoj udaljenosti i zapisi od 5 bajtova (stvori neprijatelja tipa X u slotu, '
      'promijeni mu brzinu, ...). Ponašanje pojedinih tipova je u C kodu igre.</p>')
    for l in lv:
        tag = 'L%02d' % l['level']
        if os.path.exists(os.path.join(R, 'img', f'{tag}_gallery.png')):
            a(f"<h3>{l['level']}. {html.escape(l['name'])}</h3><div class='grid'><figure>{img(f'img/{tag}_gallery.png', 480)}</figure>"
              f"<figure>{img(f'img/{tag}_run.png', 640)}<figcaption>Kadrovi iz prolaza levela</figcaption></figure></div>")

    from collections import Counter
    boss_copies = max(Counter(s['hash'] for s in songs).values())
    a('<h2>Glazba</h2><p>Svaka pjesma je odsvirana vlastitim playerom igre u emulatoru (bez ičeg drugog), zvučni registri su sintetizirani '
      f'mojom simulacijom GB zvučnog čipa (tools/gbc/apu.py; nije provjerena uz pravi GBC, pa boja zvuka može malo odstupati). '
      f'{len(songs)} pokazivača na pjesme, {sum(1 for s in songs if "file" in s)} različitih (glavna boss tema je kopirana u {boss_copies} bankova).</p><table>')
    for s in songs:
        if 'file' not in s:
            continue
        users = [x for x in songs if x['hash'] == s['hash']]
        used = sorted(set(u for x in users for u in x['used_by']))
        label = ', '.join(used) if used else ('boss' if len(users) > 2 else 'izbornik / priča / kraj')
        a(f"<tr><td>{s['file'].replace('.wav', '')}</td><td>{html.escape(label)}</td>"
          f"<td><audio controls preload='none' src='audio/{s['file'].replace('.wav', '.m4a')}'></audio></td></tr>")
    a('</table>')

    a('<h2>Što bi "remaster" mogao biti</h2>')
    a('''<div class="opt"><h3>A. GBC mod: originalna GBC igra u našem 3D rendereru (preporuka)</h3>
<p>Kao što Tyrian3D radi s PC igrom: GBC igra se vrti nepromijenjena (ugrađeni emulator, njena logika 1:1, svih 24 levela, bossovi, trgovina, priča, dvoje igrača),
a mi mijenjamo samo prikaz. Mapa iz VRAM-a postaje 3D teren (visine iz vrste bloka, ista ideja kao procedurni teren PC levela), spriteovi
se prepoznaju po tileovima i postaju volumeni pa modeli, HUD i izbornici idu u moderni UI. Zvuk: GB zvučni čip u stvarnom vremenu (ili ga se može zamijeniti boljim instrumentima).</p>
<p class="dim">Koraci: (1) GBC mod u izborniku, 2D slika u prozoru, kontrole, zvuk, spremanje → igrivo; (2) 3D: teren iz mape, spriteovi kao ploče na ravnini igre;
(3) volumeni/modeli za neprijatelje i bossove; (4) moderni HUD/izbornici; (5) jukebox i galerija. Najvjernije i najmanje rizično, jer se logika ne prepisuje.</p></div>''')
    a('''<div class="opt"><h3>B. GBC epizoda u PC enginu</h3>
<p>Njegovih 23 levela kao dodatna epizoda PC igre: PC brodovi, oružja i trgovina, a mape izgrađene iz GBC blokova (naš 3D teren),
neprijatelji iz GBC skripti prevedeni u PC neprijatelje/modele, GBC glazba. Za igrače koji žele PC arsenal na GBC levelima.</p>
<p class="dim">Puno više posla i nagađanja: GBC mapa je uža od PC polja (176 vs 264+ px), a ponašanje svakog GBC neprijatelja i bossa treba
iščitati iz koda i ponovno napisati u PC enginu. Balans PC oružja na tim levelima treba ugađati.</p></div>''')
    a('''<div class="opt"><h3>C. Samo dodaci: jukebox i galerija</h3>
<p>25 GBC pjesama u jukeboxu (i opcionalno kao glazba PC levela), galerija mapa, neprijatelja i ekrana priče u modernom UI-ju. Najmanje posla, nema igranja.</p></div>''')
    a('<p>A i C se lijepo slažu: C je usput korak 5 od A.</p>')
    a('<h2>Gdje je što</h2><ul><li><code>tools/gbc/</code>: emulator (gbemu.c + gb.py), disassembler, extract.py (leveli), songs.py + apu.py (glazba), ovaj izvještaj.</li>'
      '<li><code>data/gbc/</code> (izvan gita): kopija ROM-a, <code>levels/</code> (map.png, map.json, gallery.png, sprites.png po levelu), <code>music/</code> (WAV + zapis registara), <code>screens/</code>.</li></ul>')
    a('</main>')
    open(os.path.join(R, 'index.html'), 'w').write('\n'.join(out))
    print(os.path.join(R, 'index.html'))


if __name__ == '__main__':
    main()
