"""Every episode 7 level shot through from start to end, three ways side by side: the GBC original (the emulator), the PC
version in 2D and in 3D (the game, TYR3D_2D), the ship flying through and never firing or touching anything, so that
every enemy lives (the user, 2026-11-12: "kompletni screenshot svih levela i za gbc i za pc epizodu 7 ... bez da
uništimo i jednog protivnika", "capture u 2d i 3d modu na pc-u"). For a review page where they are compared and what is
wrong marked.

    python tools/gbc/review_shots.py gbc <out dir> [--stages 0,1,...] [--every 90]
    python tools/gbc/review_shots.py pc <out dir> --mode 3d|2d [--stages ...] [--every 60] [--jobs 3]
    python tools/gbc/review_shots.py strips <out dir>        the shots as pictures of CHUNK, and index.json

The GBC level is flown as tools/gbc/boss_rom.py flies it (Normal, the ship kept in the bottom left corner, never
firing) until it ends, BOSS_GBC frames after its script first goes back (the boss's loop), or MAX_GBC frames. The PC one (build/dev, TYR3D_START=7:<its section>, TYR3D_AUTOPILOT=ghost,
TYR3D_GODMODE) until "level over", or BOSS_SHOTS shots after its boss bar shows and the map stops for its fight (a boss
nobody shoots lives till its time runs out), or MAX_PC frames.
"""
import argparse
import glob
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
SRC = os.path.join(ROOT, 'data', 'gbc', 'episode7')
EXE = os.path.join(ROOT, 'build', 'dev', 'tyrian3d.exe' if os.name == 'nt' else 'tyrian3d')
MAX_GBC = 24000      # frames (60 a second)
MAX_PC = 30000       # frames (35 a second)
BOSS_SHOTS = 12      # shots after the boss bar first shows
BOSS_LONG = 50       # ... or after it shows, for one fought over a map that runs on (SAVARA's)
BOSS_GBC = 1200      # GBC frames after its boss's loop first goes back
CHUNK = 40           # shots a picture


def stages():
    ep = json.load(open(os.path.join(SRC, 'episode.json'), encoding='utf-8'))
    out = []
    for i, st in enumerate(ep['stages']):
        level = json.load(open(os.path.join(SRC, 'levels', st['slug'] + '.json'), encoding='utf-8'))
        out.append(dict(stage=i, slug=st['slug'], name=level['name'], gbc=level['gbc']))
    return out


def gbc_level(st, out, every):
    sys.path.insert(0, HERE)
    import extract as X
    from PIL import Image
    d = os.path.join(out, 'gbc', st['slug'])
    os.makedirs(d, exist_ok=True)
    for f in glob.glob(os.path.join(d, '*.png')):
        os.remove(f)
    g, bank, init, c = X.start_level(st['gbc'])
    g.write(0xd92a, 1)  # (Normal)
    n, prev, loop_at = 0, 0, None
    for f in range(MAX_GBC):
        g.write(0xd8da, 8)
        g.write(0xd8dd, 4)
        g.write(0xd8de, 128)  # (the ship in the bottom left corner, as boss_rom.py keeps it)
        g.run(1, 0)
        if f % every == 0:
            Image.fromarray(g.frame()).convert('RGB').save(os.path.join(d, f'{f:06d}.png'))
            n += 1
        clock = g.read(0xc439) << 8 | g.read(0xc43a)
        if loop_at is None and clock < prev:  # (the clock back: the boss's loop, which runs till it is shot down)
            loop_at = f
        prev = clock
        if g.read(0xc42d) or (loop_at is not None and f - loop_at >= BOSS_GBC):
            break
    print(f"gbc {st['slug']} {st['name']}: {n} shots, {f} frames", flush=True)


def pc_level(st, out, mode, every):
    d = os.path.join(out, 'pc' + mode, st['slug'])
    os.makedirs(d, exist_ok=True)
    for f in glob.glob(os.path.join(d, '*.bmp')) + glob.glob(os.path.join(d, '*.jpg')):
        os.remove(f)
    run = os.path.join(out, 'run', mode + '_' + st['slug'])
    os.makedirs(run, exist_ok=True)
    env = dict(os.environ, SDL_AUDIO_DRIVER='dummy', TYR3D_WINDOWED='1', TYR3D_WINDOW_SIZE='960x600',
               TYR3D_START=f"7:{2 * st['stage'] + 1}", TYR3D_AUTOPILOT='ghost', TYR3D_GODMODE='1',
               TYR3D_WEAPONS='51,53,11', TYR3D_LOG_BOSS='1', TYR3D_LOG_EVENTS='1', TYR3D_EXIT_AFTER=str(MAX_PC),
               TYR3D_DUMP_DIR=d.replace('\\', '/'), TYR3D_DUMP_FROM=str(every), TYR3D_DUMP_EVERY=str(every))
    if mode == '2d':
        env['TYR3D_2D'] = '1'
    log = os.path.join(d, 'out.txt')
    with open(log, 'w') as fo:
        p = subprocess.Popen([EXE], cwd=run, env=env, stdout=fo, stderr=subprocess.STDOUT)
        boss_at = bar_at = None
        while p.poll() is None:
            time.sleep(2)
            text = open(log, errors='ignore').read()
            shots = len(glob.glob(os.path.join(d, 'frame_*.bmp')))
            if 'level over' in text:
                time.sleep(1)
                break
            # (the boss: its bar shown and the map stopped for its fight, or BOSS_LONG shots after its bar shows for one
            # fought over a map that runs on; the game's output comes in blocks, the events' log keeps it coming)
            k = text.find('\nboss: bar')
            if bar_at is None and k >= 0:
                bar_at = shots
            if boss_at is None and k >= 0 and ' type 2 dat 0 0 0 ' in text[k:]:
                boss_at = shots
            if (boss_at is not None and shots >= boss_at + BOSS_SHOTS) or (bar_at is not None and shots >= bar_at + BOSS_LONG):
                break
        if p.poll() is None:
            p.kill()
            p.wait()
    # (as jpegs, 480 x 300: the shots go on a page)
    from PIL import Image
    n = 0
    for f in sorted(glob.glob(os.path.join(d, 'frame_*.bmp'))):
        Image.open(f).convert('RGB').resize((480, 300), Image.LANCZOS).save(f[:-4] + '.jpg', quality=80)
        os.remove(f)
        n += 1
    print(f"pc{mode} {st['slug']} {st['name']}: {n} shots{' (boss)' if boss_at is not None else ''}", flush=True)


def strips(out):
    """The shots as pictures of CHUNK shots one under another per level and way (the GBC's at its own 160 x 144, the
    PC's at 320 x 200), and index.json: each way's chunks and its shots' frames."""
    from PIL import Image
    index = []
    os.makedirs(os.path.join(out, 'strips'), exist_ok=True)
    for st in stages():
        entry = dict(st, ways={})
        for way, pat, size in (('gbc', 'gbc/{}/*.png', (160, 144)), ('pc2d', 'pc2d/{}/frame_*.jpg', (320, 200)),
                               ('pc3d', 'pc3d/{}/frame_*.jpg', (320, 200))):
            files = sorted(glob.glob(os.path.join(out, pat.format(st['slug']))))
            if not files:
                continue
            chunks = []
            for c in range(0, len(files), CHUNK):
                part = files[c:c + CHUNK]
                strip = Image.new('RGB', (size[0], size[1] * len(part)))
                for k, f in enumerate(part):
                    im = Image.open(f).convert('RGB')
                    if im.size != size:
                        im = im.resize(size, Image.LANCZOS)
                    strip.paste(im, (0, k * size[1]))
                name = f"{st['slug']}_{way}_{c // CHUNK}.jpg"
                strip.save(os.path.join(out, 'strips', name), quality=70 if way != 'gbc' else 88)
                chunks.append(dict(file='strips/' + name, count=len(part)))
            frames = [int(os.path.basename(f).split('_')[-1].split('.')[0]) for f in files]
            entry['ways'][way] = dict(width=size[0], height=size[1], chunk=CHUNK, chunks=chunks, frames=frames)
        index.append(entry)
    json.dump(index, open(os.path.join(out, 'strips', 'index.json'), 'w'), indent=1)
    print(f"{out}/strips: {sum(len(w['chunks']) for e in index for w in e['ways'].values())} pictures")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('what', choices=('gbc', 'pc', 'strips'))
    ap.add_argument('out')
    ap.add_argument('--mode', choices=('2d', '3d'), default='3d')
    ap.add_argument('--stages')
    ap.add_argument('--every', type=int)
    ap.add_argument('--jobs', type=int, default=1)
    a = ap.parse_args()
    all_st = stages()
    want = all_st if not a.stages else [all_st[int(s)] for s in a.stages.split(',')]
    if a.what == 'gbc':
        for st in want:
            gbc_level(st, a.out, a.every or 90)
    elif a.what == 'pc':
        with ThreadPoolExecutor(a.jobs) as ex:
            list(ex.map(lambda st: pc_level(st, a.out, a.mode, a.every or 60), want))
    else:
        strips(a.out)


if __name__ == '__main__':
    main()
