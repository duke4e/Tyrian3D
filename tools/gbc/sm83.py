"""SM83 (Game Boy CPU) instruction decoder for the GBC Tyrian tools.

decode(rom, addr, bank) -> (length, text, targets)  addr is a CPU address (0000-7FFF);
targets lists the CPU addresses a jump/call can reach, for tracing code.
"""
R8 = ['b', 'c', 'd', 'e', 'h', 'l', '(hl)', 'a']
R16 = ['bc', 'de', 'hl', 'sp']
R16S = ['bc', 'de', 'hl', 'af']
R16M = ['(bc)', '(de)', '(hli)', '(hld)']
CC = ['nz', 'z', 'nc', 'c']
ALU = ['add a,', 'adc a,', 'sub ', 'sbc a,', 'and ', 'xor ', 'or ', 'cp ']
ROT = ['rlc', 'rrc', 'rl', 'rr', 'sla', 'sra', 'swap', 'srl']

IO = {0xff00: 'P1', 0xff04: 'DIV', 0xff0f: 'IF', 0xff40: 'LCDC', 0xff41: 'STAT', 0xff42: 'SCY', 0xff43: 'SCX',
      0xff44: 'LY', 0xff45: 'LYC', 0xff46: 'DMA', 0xff47: 'BGP', 0xff48: 'OBP0', 0xff49: 'OBP1', 0xff4a: 'WY',
      0xff4b: 'WX', 0xff4d: 'KEY1', 0xff4f: 'VBK', 0xff51: 'HDMA1', 0xff52: 'HDMA2', 0xff53: 'HDMA3',
      0xff54: 'HDMA4', 0xff55: 'HDMA5', 0xff68: 'BCPS', 0xff69: 'BCPD', 0xff6a: 'OCPS', 0xff6b: 'OCPD',
      0xff70: 'SVBK', 0xffff: 'IE', 0xff26: 'NR52', 0xff25: 'NR51', 0xff24: 'NR50'}
for i, n in enumerate(['NR10', 'NR11', 'NR12', 'NR13', 'NR14', None, 'NR21', 'NR22', 'NR23', 'NR24', 'NR30', 'NR31',
                       'NR32', 'NR33', 'NR34', None, 'NR41', 'NR42', 'NR43', 'NR44']):
    if n:
        IO[0xff10 + i] = n


def rd(rom, addr, bank):
    if addr < 0x4000:
        return rom[addr]
    if addr < 0x8000:
        return rom[bank * 0x4000 + addr - 0x4000]
    return 0


def a16(v):
    if v in IO:
        return IO[v]
    return f'${v:04x}'


def decode(rom, addr, bank):
    op = rd(rom, addr, bank)
    n8 = rd(rom, addr + 1, bank)
    n16 = n8 | (rd(rom, addr + 2, bank) << 8)
    x, y, z = op >> 6, (op >> 3) & 7, op & 7
    p, q = y >> 1, y & 1
    rel = (addr + 2 + (n8 - 256 if n8 > 127 else n8)) & 0xffff
    if op == 0xcb:
        x2, y2, z2 = n8 >> 6, (n8 >> 3) & 7, n8 & 7
        if x2 == 0:
            return 2, f'{ROT[y2]} {R8[z2]}', []
        return 2, f"{['', 'bit', 'res', 'set'][x2]} {y2},{R8[z2]}", []
    if x == 0:
        if z == 0:
            if y == 0: return 1, 'nop', []
            if y == 1: return 3, f'ld (${n16:04x}),sp', []
            if y == 2: return 2, 'stop', []
            if y == 3: return 2, f'jr ${rel:04x}', [('jp', rel)]
            return 2, f'jr {CC[y - 4]},${rel:04x}', [('jc', rel)]
        if z == 1:
            if q == 0: return 3, f'ld {R16[p]},${n16:04x}', []
            return 1, f'add hl,{R16[p]}', []
        if z == 2:
            if q == 0: return 1, f'ld {R16M[p]},a', []
            return 1, f'ld a,{R16M[p]}', []
        if z == 3:
            return 1, f"{'inc' if q == 0 else 'dec'} {R16[p]}", []
        if z == 4: return 1, f'inc {R8[y]}', []
        if z == 5: return 1, f'dec {R8[y]}', []
        if z == 6: return 2, f'ld {R8[y]},${n8:02x}', []
        return 1, ['rlca', 'rrca', 'rla', 'rra', 'daa', 'cpl', 'scf', 'ccf'][y], []
    if x == 1:
        if op == 0x76: return 1, 'halt', []
        return 1, f'ld {R8[y]},{R8[z]}', []
    if x == 2:
        return 1, f'{ALU[y]}{R8[z]}', []
    # x == 3
    if z == 0:
        if y < 4: return 1, f'ret {CC[y]}', [('retc', None)]
        if y == 4: return 2, f'ldh ({a16(0xff00 + n8)}),a', []
        if y == 5: return 2, f'add sp,{n8 - 256 if n8 > 127 else n8}', []
        if y == 6: return 2, f'ldh a,({a16(0xff00 + n8)})', []
        return 2, f'ld hl,sp+{n8 - 256 if n8 > 127 else n8}', []
    if z == 1:
        if q == 0: return 1, f'pop {R16S[p]}', []
        return 1, ['ret', 'reti', 'jp hl', 'ld sp,hl'][p], [('ret', None)] if p < 2 else ([('jphl', None)] if p == 2 else [])
    if z == 2:
        if y < 4: return 3, f'jp {CC[y]},${n16:04x}', [('jc', n16)]
        if y == 4: return 1, 'ld (c),a', []
        if y == 5: return 3, f'ld ({a16(n16)}),a', []
        if y == 6: return 1, 'ld a,(c)', []
        return 3, f'ld a,({a16(n16)})', []
    if z == 3:
        if y == 0: return 3, f'jp ${n16:04x}', [('jp', n16)]
        if y == 6: return 1, 'di', []
        if y == 7: return 1, 'ei', []
        return 1, f'db ${op:02x}', [('bad', None)]
    if z == 4:
        if y < 4: return 3, f'call {CC[y]},${n16:04x}', [('call', n16)]
        return 1, f'db ${op:02x}', [('bad', None)]
    if z == 5:
        if q == 0: return 1, f'push {R16S[p]}', []
        if p == 0: return 3, f'call ${n16:04x}', [('call', n16)]
        return 1, f'db ${op:02x}', [('bad', None)]
    if z == 6:
        return 2, f'{ALU[y]}${n8:02x}', []
    return 1, f'rst ${y * 8:02x}', [('call', y * 8)]
