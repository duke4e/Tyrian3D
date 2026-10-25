"""Drive the emulator with a script of inputs and save frames and a state.

play.py [--state IN] [--save OUT] [--shots DIR] [--every N] SCRIPT
SCRIPT: comma-separated steps "KEYS:FRAMES" (KEYS from A B S(tart) E(select) U D L R, '_' for none),
e.g. "A:4,_:60,D:4,_:10". The last frame is written to DIR/last.png.
"""
import argparse
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gb as G
from PIL import Image

KEYS = {'A': G.A, 'B': G.B, 'S': G.START, 'E': G.SELECT, 'U': G.UP, 'D': G.DOWN, 'L': G.LEFT, 'R': G.RIGHT, '_': 0}

ap = argparse.ArgumentParser()
ap.add_argument('--state'); ap.add_argument('--save'); ap.add_argument('--shots', default='.')
ap.add_argument('--every', type=int, default=0); ap.add_argument('script')
a = ap.parse_args()
g = G.GB()
if a.state:
    import ctypes
    raw = open(a.state, 'rb').read()
    g.load(ctypes.create_string_buffer(raw, len(raw)))
os.makedirs(a.shots, exist_ok=True)
n = 0
shots = []
for step in a.script.split(','):
    k, f = step.split(':')
    joy = 0
    for ch in k:
        joy |= KEYS[ch]
    for _ in range(int(f)):
        g.run(1, joy)
        n += 1
        if a.every and n % a.every == 0:
            shots.append(Image.fromarray(g.frame()))
Image.fromarray(g.frame()).resize((320, 288), Image.NEAREST).save(os.path.join(a.shots, 'last.png'))
if shots:
    cols = min(8, len(shots)); rows = (len(shots) + cols - 1) // cols
    s = Image.new('RGB', (160 * cols, 144 * rows))
    for i, im in enumerate(shots):
        s.paste(im, ((i % cols) * 160, (i // cols) * 144))
    s.save(os.path.join(a.shots, 'sheet.png'))
if a.save:
    open(a.save, 'wb').write(g.save().raw)
print('frames', n, 'pc', hex(g.pc), 'bank', g.bank)
