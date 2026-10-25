"""A Game Boy APU synthesiser: renders a log of sound register writes to stereo samples.

render(events, seconds, rate) with events as (time_s, reg, value), reg the low byte of the
$ff10-$ff3f address. The frame sequencer (length 256 Hz, sweep 128 Hz, envelope 64 Hz) runs in
blocks of 1/512 s; squares and noise are generated per sample with numpy inside each block.
"""
import numpy as np
from scipy.signal import lfilter

DUTY = np.array([[0, 0, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 1],
                 [1, 0, 0, 0, 0, 1, 1, 1], [0, 1, 1, 1, 1, 1, 1, 0]], np.float32)
NOISE_DIV = [8, 16, 32, 48, 64, 80, 96, 112]


class Ch:
    def __init__(self):
        self.on = False; self.vol = 0; self.env_dir = 0; self.env_per = 0; self.env_cnt = 0
        self.length = 0; self.len_en = False; self.freq = 0; self.phase = 0.0; self.duty = 2
        self.sw_per = 0; self.sw_dir = 0; self.sw_shift = 0; self.sw_cnt = 0; self.shadow = 0
        self.npos = 0; self.dac = False


def _lfsr_seq(width7):
    lfsr, out = 0x7fff, []
    for _ in range(127 if width7 else 32767):
        out.append((~lfsr) & 1)
        x = (lfsr ^ (lfsr >> 1)) & 1
        lfsr = (lfsr >> 1) | (x << 14)
        if width7:
            lfsr = (lfsr & ~0x40) | (x << 6)
    return np.array(out, np.float32)


LFSR = [_lfsr_seq(False), _lfsr_seq(True)]


def _noise(ch, n, rate, nr43):
    s, w, r = nr43 >> 4, (nr43 >> 3) & 1, nr43 & 7
    if s >= 14:
        return np.zeros(n, np.float32)
    hz = 4194304 / NOISE_DIV[r] / (1 << s)
    clk = ch.phase + hz / rate * np.arange(1, n + 1)
    seq = LFSR[w]
    out = seq[(ch.npos + clk.astype(np.int64)) % len(seq)]
    whole = int(clk[-1])
    ch.npos += whole
    ch.phase = clk[-1] - whole
    return out


def render(events, seconds, rate=44100):
    n_total = int(seconds * rate)
    out = np.zeros((n_total, 2), np.float32)
    regs = [0] * 0x40
    wave = np.zeros(32, np.float32)
    ch = [Ch() for _ in range(4)]
    ev = sorted(events, key=lambda e: e[0])
    ei = 0
    block = rate / 512.0
    seq = 0
    pos = 0.0

    def trigger(i):
        c = ch[i]
        c.on = c.dac
        if c.length == 0:
            c.length = 256 if i == 2 else 64
        if i != 2:
            nrx2 = regs[0x12 + 5 * i] if i < 2 else regs[0x21]
            c.vol, c.env_dir, c.env_per = nrx2 >> 4, (nrx2 >> 3) & 1, nrx2 & 7
            c.env_cnt = c.env_per
        if i == 0:
            c.shadow = c.freq
            c.sw_per, c.sw_dir, c.sw_shift = (regs[0x10] >> 4) & 7, (regs[0x10] >> 3) & 1, regs[0x10] & 7
            c.sw_cnt = c.sw_per or 8
        if i == 3:
            c.npos = 0

    def write(r, v):
        regs[r] = v
        if 0x30 <= r <= 0x3f:
            k = (r - 0x30) * 2
            wave[k] = v >> 4; wave[k + 1] = v & 15
            return
        if r == 0x26 and not (v & 0x80):
            for c in ch:
                c.on = False
        base = {0x10: 0, 0x11: 0, 0x12: 0, 0x13: 0, 0x14: 0, 0x16: 1, 0x17: 1, 0x18: 1, 0x19: 1,
                0x1a: 2, 0x1b: 2, 0x1c: 2, 0x1d: 2, 0x1e: 2, 0x20: 3, 0x21: 3, 0x22: 3, 0x23: 3}
        if r not in base:
            return
        i = base[r]
        c = ch[i]
        k = r - (0x10, 0x15, 0x1a, 0x1f)[i]
        if k == 1:
            if i == 2:
                c.length = 256 - v
            else:
                c.length = 64 - (v & 63)
                if i < 2:
                    c.duty = v >> 6
        elif k == 2 and i != 2:
            c.dac = (v & 0xf8) != 0
            if not c.dac:
                c.on = False
        elif k == 0 and i == 2:
            c.dac = bool(v & 0x80)
            if not c.dac:
                c.on = False
        elif k == 3 and i < 3:
            c.freq = (c.freq & 0x700) | v
        elif k == 4:
            if i < 3:
                c.freq = (c.freq & 0xff) | ((v & 7) << 8)
            c.len_en = bool(v & 0x40)
            if v & 0x80:
                trigger(i)

    nblocks = int(n_total / block)
    for b in range(nblocks):
        t0 = b / 512.0
        t1 = (b + 1) / 512.0
        while ei < len(ev) and ev[ei][0] < t1:
            write(ev[ei][1], ev[ei][2])
            ei += 1
        # frame sequencer step
        if seq % 2 == 0:
            for c in ch:
                if c.len_en and c.length > 0:
                    c.length -= 1
                    if c.length == 0:
                        c.on = False
        if seq % 4 == 2:
            c = ch[0]
            if c.sw_per:
                c.sw_cnt -= 1
                if c.sw_cnt <= 0:
                    c.sw_cnt = c.sw_per
                    if c.sw_shift:
                        d = c.shadow >> c.sw_shift
                        nf = c.shadow - d if c.sw_dir else c.shadow + d
                        if nf > 2047:
                            c.on = False
                        else:
                            c.shadow = c.freq = nf
        if seq == 7:
            for c in (ch[0], ch[1], ch[3]):
                if c.env_per:
                    c.env_cnt -= 1
                    if c.env_cnt <= 0:
                        c.env_cnt = c.env_per
                        if c.env_dir and c.vol < 15:
                            c.vol += 1
                        elif not c.env_dir and c.vol > 0:
                            c.vol -= 1
        seq = (seq + 1) & 7
        s0, s1 = int(round(pos)), int(round(pos + block))
        pos += block
        n = s1 - s0
        if n <= 0:
            continue
        nr51, nr50 = regs[0x25], regs[0x24]
        if not (regs[0x26] & 0x80):
            continue
        mix = np.zeros((n, 2), np.float32)
        for i, c in enumerate(ch):
            if not c.on:
                continue
            if i < 2:
                hz = 131072.0 / (2048 - c.freq)
                ph = c.phase + hz / rate * np.arange(1, n + 1)
                c.phase = ph[-1] % 1.0
                sig = DUTY[c.duty][(ph * 8).astype(np.int64) & 7] * 2 - 1
                sig *= c.vol / 15.0
            elif i == 2:
                shift = (regs[0x1c] >> 5) & 3
                if shift == 0:
                    continue
                hz = 65536.0 / (2048 - c.freq)
                ph = c.phase + hz / rate * np.arange(1, n + 1)
                c.phase = ph[-1] % 1.0
                smp = wave[(ph * 32).astype(np.int64) & 31]
                sig = ((smp / (1 << (shift - 1))) / 7.5 - 1.0)
            else:
                sig = (_noise(c, n, rate, regs[0x22]) * 2 - 1) * (c.vol / 15.0)
            if nr51 & (0x10 << i):
                mix[:, 0] += sig
            if nr51 & (1 << i):
                mix[:, 1] += sig
        mix[:, 0] *= (((nr50 >> 4) & 7) + 1) / 8.0
        mix[:, 1] *= ((nr50 & 7) + 1) / 8.0
        out[s0:s1] = mix[:len(out[s0:s1])]
    # DC-blocking high-pass (the console's output capacitor)
    a = 0.999
    y = np.zeros_like(out)
    for k in range(2):
        y[:, k] = lfilter([1, -1], [1, -a], out[:, k])
    return y * 0.2
