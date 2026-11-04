"""ctypes wrapper of gbemu.c (built on first use into build/gbc: libgbemu.dylib with cc, or on Windows gbemu.dll with
zig cc)."""
import ctypes as C
import os
import shutil
import subprocess
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
WINDOWS = os.name == 'nt'
LIB = os.path.join(ROOT, 'build', 'gbc', 'gbemu.dll' if WINDOWS else 'libgbemu.dylib')
ROM = os.path.join(ROOT, 'data', 'gbc', 'Tyrian.gb')

RIGHT, LEFT, UP, DOWN, A, B, SELECT, START = (1 << i for i in range(8))


def _lib():
    src = os.path.join(HERE, 'gbemu.c')
    if not os.path.exists(LIB) or os.path.getmtime(LIB) < os.path.getmtime(src):
        os.makedirs(os.path.dirname(LIB), exist_ok=True)
        if WINDOWS:
            # (zig's clang exports the library's functions; MSVC's cl would need them named for export)
            if shutil.which('zig') is None:
                raise RuntimeError('building gbemu.dll needs zig (zig cc) on the PATH')
            subprocess.check_call(['zig', 'cc', '-O2', '-shared', '-o', LIB, src])
        else:
            subprocess.check_call(['cc', '-O2', '-shared', '-fPIC', '-o', LIB, src])
    lib = C.CDLL(LIB)
    vp, i, u8p = C.c_void_p, C.c_int, C.POINTER(C.c_uint8)
    sig = {
        'gb_new': (vp, [C.c_char_p]), 'gb_run_frame': (i, [vp]), 'gb_run_until': (i, [vp, i, i, C.c_uint64]),
        'gb_step': (i, [vp]), 'gb_set_joy': (None, [vp, i]), 'gb_frame': (C.POINTER(C.c_uint32), [vp]),
        'gb_read': (i, [vp, i]), 'gb_write': (None, [vp, i, i]), 'gb_reg': (i, [vp, i]),
        'gb_cycles': (C.c_uint64, [vp]), 'gb_frames': (C.c_uint64, [vp]),
        'gb_snd_enable': (None, [vp, i]), 'gb_snd_count': (i, [vp]), 'gb_snd': (vp, [vp]),
        'gb_vw_enable': (None, [vp, i]), 'gb_vw_count': (i, [vp]), 'gb_vw': (vp, [vp]),
        'gb_ww_enable': (None, [vp, i, i]), 'gb_ww_count': (i, [vp]), 'gb_ww': (vp, [vp]),
        'gb_sizeof_state': (i, []), 'gb_set_reg': (None, [vp, i, i]), 'gb_save': (None, [vp, vp]), 'gb_load': (None, [vp, vp]),
    }
    for n in ['gb_vram', 'gb_oam', 'gb_bgpal', 'gb_obpal', 'gb_wram', 'gb_io', 'gb_hram', 'gb_eram', 'gb_romflags']:
        sig[n] = (u8p, [vp])
    for n, (res, args) in sig.items():
        f = getattr(lib, n)
        f.restype, f.argtypes = res, args
    return lib


SND = np.dtype([('cyc', '<u8'), ('reg', 'u1'), ('val', 'u1'), ('pad', 'V6')])
WR = np.dtype([('cyc', '<u8'), ('pc', '<u2'), ('addr', '<u2'), ('bank', 'u1'), ('val', 'u1'), ('pad', 'V2'), ('src', '<u4'), ('pad2', 'V4')])


class GB:
    def __init__(self, rom=ROM):
        self.L = _lib()
        self.g = self.L.gb_new(rom.encode())
        if not self.g:
            raise IOError(rom)
        self.romsize = os.path.getsize(rom)

    def _arr(self, fn, n):
        return np.ctypeslib.as_array(fn(self.g), shape=(n,))

    def frame(self):
        a = np.ctypeslib.as_array(self.L.gb_frame(self.g), shape=(144 * 160,)).copy()
        return a.view(np.uint8).reshape(144, 160, 4)[:, :, :3]

    def run(self, frames=1, joy=0):
        self.L.gb_set_joy(self.g, joy)
        for _ in range(frames):
            self.L.gb_run_frame(self.g)

    def press(self, joy, hold=4, after=8):
        self.run(hold, joy)
        self.run(after, 0)

    def until(self, pc, bank=-1, max_cycles=50_000_000):
        return self.L.gb_run_until(self.g, pc, bank, max_cycles)

    def reg(self, i): return self.L.gb_reg(self.g, i)
    @property
    def pc(self): return self.reg(0)
    @property
    def bank(self): return self.reg(6)
    def set_reg(self, i, v): self.L.gb_set_reg(self.g, i, v)
    def read(self, a): return self.L.gb_read(self.g, a)
    def write(self, a, v): self.L.gb_write(self.g, a, v)
    def vram(self): return self._arr(self.L.gb_vram, 0x4000).copy()
    def oam(self): return self._arr(self.L.gb_oam, 0xa0).copy()
    def bgpal(self): return self._arr(self.L.gb_bgpal, 64).copy()
    def obpal(self): return self._arr(self.L.gb_obpal, 64).copy()
    def wram(self): return self._arr(self.L.gb_wram, 0x8000).copy()
    def io(self): return self._arr(self.L.gb_io, 0x80).copy()
    def hram(self): return self._arr(self.L.gb_hram, 0x80).copy()
    def romflags(self): return self._arr(self.L.gb_romflags, self.romsize)

    def snd_enable(self, on=True): self.L.gb_snd_enable(self.g, int(on))
    def snd_log(self):
        n = self.L.gb_snd_count(self.g)
        if not n: return np.zeros(0, SND)
        return np.frombuffer(C.string_at(self.L.gb_snd(self.g), n * SND.itemsize), SND).copy()
    def vw_enable(self, on=True): self.L.gb_vw_enable(self.g, int(on))
    def vw_log(self):
        n = self.L.gb_vw_count(self.g)
        if not n: return np.zeros(0, WR)
        return np.frombuffer(C.string_at(self.L.gb_vw(self.g), n * WR.itemsize), WR).copy()
    def ww_enable(self, lo, hi): self.L.gb_ww_enable(self.g, lo, hi)
    def ww_log(self):
        n = self.L.gb_ww_count(self.g)
        if not n: return np.zeros(0, WR)
        return np.frombuffer(C.string_at(self.L.gb_ww(self.g), n * WR.itemsize), WR).copy()

    def call(self, addr, bank=None, max_cycles=20_000_000):
        """Calls a routine of the ROM (switching to bank first) and runs until it returns."""
        if bank is not None:
            self.write(0x2000, bank)
        sp = self.reg(1) - 2
        self.write(sp, 0xf0); self.write(sp + 1, 0xff)
        self.set_reg(1, sp); self.set_reg(0, addr)
        return self.until(0xfff0, -1, max_cycles)

    def save(self):
        buf = C.create_string_buffer(self.L.gb_sizeof_state())
        self.L.gb_save(self.g, buf)
        return buf
    def load(self, buf): self.L.gb_load(self.g, buf)


def cgb_rgb(pal_bytes):
    """64 palette bytes -> (8, 4, 3) uint8 RGB."""
    v = pal_bytes[0::2].astype(np.uint16) | (pal_bytes[1::2].astype(np.uint16) << 8)
    rgb = np.stack([v & 31, (v >> 5) & 31, (v >> 10) & 31], -1)
    return ((rgb << 3) | (rgb >> 2)).astype(np.uint8).reshape(8, 4, 3)
