"""Linear disassembly: disasm.py ROM BANK START [COUNT]  (START a CPU address, hex)."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from sm83 import decode, rd

rom = open(sys.argv[1], 'rb').read()
bank = int(sys.argv[2], 0)
a = int(sys.argv[3], 16)
n = int(sys.argv[4]) if len(sys.argv) > 4 else 60
for _ in range(n):
    ln, txt, _t = decode(rom, a, bank)
    raw = ' '.join(f'{rd(rom, a + i, bank):02x}' for i in range(ln))
    print(f'{bank:02x}:{a:04x}  {raw:<9} {txt}')
    a += ln
