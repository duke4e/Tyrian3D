/* gbemu.c: a small Game Boy Color emulator for inspecting the GBC Tyrian ROM (tools/gbc).
 *
 * It runs headless as a shared library driven from Python (gb.py): frames, VRAM, OAM, palettes,
 * a per-byte map of the ROM bytes read or executed, a log of the sound register writes and logs
 * of the writes to VRAM (with the ROM byte read last) and to a watched address range.
 * CPU, MBC1, timer, PPU (scanline renderer), CGB VRAM/WRAM banks, palettes and HDMA. No sound output.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define FZ 0x80
#define FN 0x40
#define FH 0x20
#define FC 0x10

typedef struct { uint64_t cyc; uint8_t reg, val; } SndEv;
typedef struct { uint64_t cyc; uint16_t pc, addr; uint8_t bank, val; uint32_t src; } WrEv;

typedef struct GB {
	uint8_t *rom; uint32_t romsize, rombanks;
	uint8_t eram[0x8000]; int ram_enable, bank_lo, bank_hi, mbc_mode, rombank;
	uint8_t vram[0x4000]; int vbk;
	uint8_t wram[0x8000]; int svbk;
	uint8_t oam[0xa0], io[0x80], hram[0x80], ie;
	uint8_t bgpal[64], obpal[64];
	uint8_t a, f, b, c, d, e, h, l; uint16_t sp, pc;
	int ime, ime_delay, halted;
	uint64_t cycles, instrs; uint16_t divc; int tima_cnt;
	int line_dot, ly, mode, win_line, double_speed;
	int hdma_active, hdma_blocks; uint16_t hdma_src, hdma_dst;
	uint8_t joy;
	uint32_t frame[160 * 144];
	int frame_done;
	uint8_t *romflags; int fetching; uint32_t last_rom;
	SndEv *snd; int snd_n, snd_cap;
	WrEv *vw; int vw_n, vw_cap;
	WrEv *ww; int ww_n, ww_cap; uint16_t ww_lo, ww_hi;
	uint64_t frames;
} GB;

static uint8_t rb(GB *g, uint16_t a);
static void wb(GB *g, uint16_t a, uint8_t v);

static void mark(GB *g, uint32_t o)
{
	g->romflags[o] |= g->fetching ? 2 : 1;
	if (!g->fetching) g->last_rom = o;
}

static void update_bank(GB *g)
{
	int bnk = g->bank_lo & 0x1f;
	if (bnk == 0) bnk = 1;
	if (g->mbc_mode == 0) bnk |= (g->bank_hi & 3) << 5;
	g->rombank = bnk % g->rombanks;
}

static uint8_t io_read(GB *g, uint16_t a)
{
	uint8_t r = a & 0x7f;
	switch (a) {
	case 0xff00: {
		uint8_t sel = g->io[0] & 0x30, lo = 0x0f;
		if (!(sel & 0x10)) lo &= ~(g->joy & 0x0f);
		if (!(sel & 0x20)) lo &= ~(g->joy >> 4);
		return 0xc0 | sel | lo;
	}
	case 0xff04: return g->divc >> 8;
	case 0xff0f: return 0xe0 | g->io[0x0f];
	case 0xff41: return 0x80 | (g->io[0x41] & 0x78) | (g->ly == g->io[0x45] ? 4 : 0) | g->mode;
	case 0xff44: return g->ly;
	case 0xff4d: return 0x7e | (g->double_speed ? 0x80 : 0) | (g->io[0x4d] & 1);
	case 0xff4f: return 0xfe | g->vbk;
	case 0xff55: return g->hdma_active ? ((g->hdma_blocks - 1) & 0x7f) : 0xff;
	case 0xff69: return g->bgpal[g->io[0x68] & 0x3f];
	case 0xff6b: return g->obpal[g->io[0x6a] & 0x3f];
	case 0xff70: return 0xf8 | g->svbk;
	}
	return g->io[r];
}

static void hdma_block(GB *g)
{
	for (int i = 0; i < 16; i++) {
		uint8_t v = rb(g, g->hdma_src++);
		uint16_t d = 0x8000 | (g->hdma_dst++ & 0x1fff);
		wb(g, d, v);
	}
	if (--g->hdma_blocks <= 0) g->hdma_active = 0;
}

static void io_write(GB *g, uint16_t a, uint8_t v)
{
	uint8_t r = a & 0x7f;
	if (a >= 0xff10 && a <= 0xff3f) {
		if (g->snd) {
			if (g->snd_n == g->snd_cap) { g->snd_cap = g->snd_cap ? g->snd_cap * 2 : 65536; g->snd = realloc(g->snd, g->snd_cap * sizeof(SndEv)); }
			g->snd[g->snd_n++] = (SndEv){ g->double_speed ? g->cycles / 2 : g->cycles, r, v };
		}
		g->io[r] = v;
		return;
	}
	switch (a) {
	case 0xff00: g->io[0] = v & 0x30; return;
	case 0xff04: g->divc = 0; return;
	case 0xff0f: g->io[0x0f] = v & 0x1f; return;
	case 0xff40:
		if ((g->io[0x40] & 0x80) && !(v & 0x80)) { g->ly = 0; g->mode = 0; g->line_dot = 0; }
		if (!(g->io[0x40] & 0x80) && (v & 0x80)) { g->ly = 0; g->mode = 2; g->line_dot = 0; g->win_line = 0; }
		g->io[0x40] = v; return;
	case 0xff41: g->io[0x41] = v & 0x78; return;
	case 0xff44: return;
	case 0xff46: for (int i = 0; i < 0xa0; i++) g->oam[i] = rb(g, (v << 8) | i); g->io[r] = v; return;
	case 0xff4d: g->io[0x4d] = v & 1; return;
	case 0xff4f: g->vbk = v & 1; return;
	case 0xff51: g->hdma_src = (g->hdma_src & 0x00ff) | (v << 8); return;
	case 0xff52: g->hdma_src = (g->hdma_src & 0xff00) | (v & 0xf0); return;
	case 0xff53: g->hdma_dst = (g->hdma_dst & 0x00ff) | ((v & 0x1f) << 8); return;
	case 0xff54: g->hdma_dst = (g->hdma_dst & 0xff00) | (v & 0xf0); return;
	case 0xff55:
		if (g->hdma_active && !(v & 0x80)) { g->hdma_active = 0; return; }
		g->hdma_blocks = (v & 0x7f) + 1;
		if (v & 0x80) g->hdma_active = 1;
		else { g->hdma_active = 1; while (g->hdma_active) hdma_block(g); }
		return;
	case 0xff69: g->bgpal[g->io[0x68] & 0x3f] = v; if (g->io[0x68] & 0x80) g->io[0x68] = 0x80 | ((g->io[0x68] + 1) & 0x3f); return;
	case 0xff6b: g->obpal[g->io[0x6a] & 0x3f] = v; if (g->io[0x6a] & 0x80) g->io[0x6a] = 0x80 | ((g->io[0x6a] + 1) & 0x3f); return;
	case 0xff70: g->svbk = (v & 7) ? (v & 7) : 1; return;
	}
	g->io[r] = v;
}

static uint8_t rb(GB *g, uint16_t a)
{
	if (a < 0x4000) { mark(g, a); return g->rom[a]; }
	if (a < 0x8000) { uint32_t o = g->rombank * 0x4000 + (a - 0x4000); mark(g, o); return g->rom[o]; }
	if (a < 0xa000) return g->vram[g->vbk * 0x2000 + a - 0x8000];
	if (a < 0xc000) return g->ram_enable ? g->eram[(g->mbc_mode ? (g->bank_hi & 3) : 0) * 0x2000 + a - 0xa000] : 0xff;
	if (a < 0xd000) return g->wram[a - 0xc000];
	if (a < 0xe000) return g->wram[g->svbk * 0x1000 + a - 0xd000];
	if (a < 0xfe00) return rb(g, a - 0x2000);
	if (a < 0xfea0) return g->oam[a - 0xfe00];
	if (a < 0xff00) return 0xff;
	if (a < 0xff80) return io_read(g, a);
	if (a < 0xffff) return g->hram[a - 0xff80];
	return g->ie;
}

static void logw(WrEv **buf, int *n, int *cap, GB *g, uint16_t addr, uint8_t v)
{
	if (*n == *cap) { *cap = *cap ? *cap * 2 : 65536; *buf = realloc(*buf, *cap * sizeof(WrEv)); }
	(*buf)[(*n)++] = (WrEv){ g->cycles, g->pc, addr, (uint8_t)g->rombank, v, g->last_rom };
}

static void wb(GB *g, uint16_t a, uint8_t v)
{
	if (g->ww && a >= g->ww_lo && a <= g->ww_hi) logw(&g->ww, &g->ww_n, &g->ww_cap, g, a, v);
	if (a < 0x2000) { g->ram_enable = (v & 0x0f) == 0x0a; return; }
	if (a < 0x4000) { g->bank_lo = v; update_bank(g); return; }
	if (a < 0x6000) { g->bank_hi = v; update_bank(g); return; }
	if (a < 0x8000) { g->mbc_mode = v & 1; update_bank(g); return; }
	if (a < 0xa000) {
		if (g->vw) logw(&g->vw, &g->vw_n, &g->vw_cap, g, (uint16_t)(a | (g->vbk << 13)), v);
		g->vram[g->vbk * 0x2000 + a - 0x8000] = v; return;
	}
	if (a < 0xc000) { if (g->ram_enable) g->eram[(g->mbc_mode ? (g->bank_hi & 3) : 0) * 0x2000 + a - 0xa000] = v; return; }
	if (a < 0xd000) { g->wram[a - 0xc000] = v; return; }
	if (a < 0xe000) { g->wram[g->svbk * 0x1000 + a - 0xd000] = v; return; }
	if (a < 0xfe00) { wb(g, a - 0x2000, v); return; }
	if (a < 0xfea0) { g->oam[a - 0xfe00] = v; return; }
	if (a < 0xff00) return;
	if (a < 0xff80) { io_write(g, a, v); return; }
	if (a < 0xffff) { g->hram[a - 0xff80] = v; return; }
	g->ie = v;
}

static uint32_t cgb_color(const uint8_t *pal, int p, int c)
{
	uint16_t v = pal[p * 8 + c * 2] | (pal[p * 8 + c * 2 + 1] << 8);
	int r = v & 31, gg = (v >> 5) & 31, b = (v >> 10) & 31;
	r = (r << 3) | (r >> 2); gg = (gg << 3) | (gg >> 2); b = (b << 3) | (b >> 2);
	return 0xff000000u | (b << 16) | (gg << 8) | r;
}

static void render_line(GB *g)
{
	uint8_t lcdc = g->io[0x40];
	int y = g->ly;
	uint8_t bgc[160], bgp[160];
	uint32_t *out = &g->frame[y * 160];
	int scy = g->io[0x42], scx = g->io[0x43];
	int wx = g->io[0x4b] - 7, wy = g->io[0x4a];
	int win = (lcdc & 0x20) && y >= wy && g->io[0x4b] <= 166;
	for (int x = 0; x < 160; x++) {
		int px, py; uint16_t m;
		if (win && x >= wx) { px = x - wx; py = g->win_line; m = (lcdc & 0x40) ? 0x1c00 : 0x1800; }
		else { px = (x + scx) & 255; py = (y + scy) & 255; m = (lcdc & 0x08) ? 0x1c00 : 0x1800; }
		int idx = m + (py >> 3) * 32 + (px >> 3);
		uint8_t tile = g->vram[idx], attr = g->vram[0x2000 + idx];
		int tx = px & 7, ty = py & 7;
		if (attr & 0x20) tx = 7 - tx;
		if (attr & 0x40) ty = 7 - ty;
		int ta = (lcdc & 0x10) ? tile * 16 : 0x1000 + (int8_t)tile * 16;
		if (attr & 8) ta += 0x2000;
		uint8_t lo = g->vram[ta + ty * 2], hi = g->vram[ta + ty * 2 + 1];
		int ci = ((lo >> (7 - tx)) & 1) | (((hi >> (7 - tx)) & 1) << 1);
		bgc[x] = ci; bgp[x] = attr & 0x80;
		out[x] = cgb_color(g->bgpal, attr & 7, ci);
	}
	if (win) g->win_line++;
	if (!(lcdc & 2)) return;
	int hgt = (lcdc & 4) ? 16 : 8, list[10], n = 0;
	for (int i = 0; i < 40 && n < 10; i++) {
		int sy = g->oam[i * 4] - 16;
		if (y >= sy && y < sy + hgt) list[n++] = i;
	}
	for (int k = n - 1; k >= 0; k--) {
		int i = list[k];
		int sy = g->oam[i * 4] - 16, sx = g->oam[i * 4 + 1] - 8;
		uint8_t tile = g->oam[i * 4 + 2], attr = g->oam[i * 4 + 3];
		if (hgt == 16) tile &= 0xfe;
		int row = y - sy;
		if (attr & 0x40) row = hgt - 1 - row;
		int ta = tile * 16 + row * 2 + ((attr & 8) ? 0x2000 : 0);
		uint8_t lo = g->vram[ta], hi = g->vram[ta + 1];
		for (int p = 0; p < 8; p++) {
			int x = sx + p;
			if (x < 0 || x >= 160) continue;
			int bit = (attr & 0x20) ? p : 7 - p;
			int ci = ((lo >> bit) & 1) | (((hi >> bit) & 1) << 1);
			if (!ci) continue;
			if ((lcdc & 1) && bgc[x] && (bgp[x] || (attr & 0x80))) continue;
			out[x] = cgb_color(g->obpal, attr & 7, ci);
		}
	}
}

static void stat_irq(GB *g, int bit) { if (g->io[0x41] & bit) g->io[0x0f] |= 2; }
static void lyc_check(GB *g) { if (g->ly == g->io[0x45]) stat_irq(g, 0x40); }

static void ppu_tick(GB *g, int dots)
{
	if (!(g->io[0x40] & 0x80)) {
		g->line_dot += dots;
		if (g->line_dot >= 70224) { g->line_dot -= 70224; g->frame_done = 1; }
		return;
	}
	g->line_dot += dots;
	for (;;) {
		if (g->ly < 144) {
			if (g->mode == 2 && g->line_dot >= 80) { g->mode = 3; render_line(g); }
			else if (g->mode == 3 && g->line_dot >= 252) {
				g->mode = 0; stat_irq(g, 0x08);
				if (g->hdma_active) hdma_block(g);
			} else if (g->line_dot >= 456) {
				g->line_dot -= 456; g->ly++;
				if (g->ly == 144) { g->mode = 1; g->io[0x0f] |= 1; stat_irq(g, 0x10); g->frame_done = 1; g->frames++; }
				else { g->mode = 2; stat_irq(g, 0x20); }
				lyc_check(g);
			} else break;
		} else {
			if (g->line_dot >= 456) {
				g->line_dot -= 456; g->ly++;
				if (g->ly > 153) { g->ly = 0; g->mode = 2; g->win_line = 0; stat_irq(g, 0x20); }
				lyc_check(g);
			} else break;
		}
	}
}

static void tick(GB *g, int cyc)
{
	g->cycles += cyc;
	uint16_t old = g->divc;
	g->divc += cyc;
	(void)old;
	uint8_t tac = g->io[0x07];
	if (tac & 4) {
		static const int per[4] = { 1024, 16, 64, 256 };
		g->tima_cnt += cyc;
		while (g->tima_cnt >= per[tac & 3]) {
			g->tima_cnt -= per[tac & 3];
			if (++g->io[0x05] == 0) { g->io[0x05] = g->io[0x06]; g->io[0x0f] |= 4; }
		}
	}
	ppu_tick(g, g->double_speed ? cyc / 2 : cyc);
}

static uint8_t fetch(GB *g) { g->fetching = 1; uint8_t v = rb(g, g->pc++); g->fetching = 0; return v; }
static uint16_t fetch16(GB *g) { uint8_t lo = fetch(g); return lo | (fetch(g) << 8); }
static void push(GB *g, uint16_t v) { wb(g, --g->sp, v >> 8); wb(g, --g->sp, v & 0xff); }
static uint16_t pop(GB *g) { uint8_t lo = rb(g, g->sp++); return lo | (rb(g, g->sp++) << 8); }

#define HL ((uint16_t)((g->h << 8) | g->l))
static uint8_t getr(GB *g, int i)
{
	switch (i) {
	case 0: return g->b; case 1: return g->c; case 2: return g->d; case 3: return g->e;
	case 4: return g->h; case 5: return g->l; case 6: return rb(g, HL); default: return g->a;
	}
}
static void setr(GB *g, int i, uint8_t v)
{
	switch (i) {
	case 0: g->b = v; break; case 1: g->c = v; break; case 2: g->d = v; break; case 3: g->e = v; break;
	case 4: g->h = v; break; case 5: g->l = v; break; case 6: wb(g, HL, v); break; default: g->a = v;
	}
}
static uint16_t get16(GB *g, int p)
{
	switch (p) { case 0: return (g->b << 8) | g->c; case 1: return (g->d << 8) | g->e; case 2: return HL; default: return g->sp; }
}
static void set16(GB *g, int p, uint16_t v)
{
	switch (p) {
	case 0: g->b = v >> 8; g->c = v; break; case 1: g->d = v >> 8; g->e = v; break;
	case 2: g->h = v >> 8; g->l = v; break; default: g->sp = v;
	}
}
static int cond(GB *g, int y)
{
	switch (y & 3) { case 0: return !(g->f & FZ); case 1: return g->f & FZ; case 2: return !(g->f & FC); default: return g->f & FC; }
}

static void alu(GB *g, int op, uint8_t v)
{
	int a = g->a, r, c = (g->f & FC) ? 1 : 0;
	switch (op) {
	case 0: r = a + v; g->f = ((r & 0xff) ? 0 : FZ) | (((a & 15) + (v & 15)) > 15 ? FH : 0) | (r > 255 ? FC : 0); g->a = r; break;
	case 1: r = a + v + c; g->f = ((r & 0xff) ? 0 : FZ) | (((a & 15) + (v & 15) + c) > 15 ? FH : 0) | (r > 255 ? FC : 0); g->a = r; break;
	case 2: r = a - v; g->f = FN | ((r & 0xff) ? 0 : FZ) | (((a & 15) - (v & 15)) < 0 ? FH : 0) | (r < 0 ? FC : 0); g->a = r; break;
	case 3: r = a - v - c; g->f = FN | ((r & 0xff) ? 0 : FZ) | (((a & 15) - (v & 15) - c) < 0 ? FH : 0) | (r < 0 ? FC : 0); g->a = r; break;
	case 4: g->a = a & v; g->f = (g->a ? 0 : FZ) | FH; break;
	case 5: g->a = a ^ v; g->f = g->a ? 0 : FZ; break;
	case 6: g->a = a | v; g->f = g->a ? 0 : FZ; break;
	default: r = a - v; g->f = FN | ((r & 0xff) ? 0 : FZ) | (((a & 15) - (v & 15)) < 0 ? FH : 0) | (r < 0 ? FC : 0); break;
	}
}

static int exec_cb(GB *g)
{
	uint8_t op = fetch(g);
	int x = op >> 6, y = (op >> 3) & 7, z = op & 7;
	uint8_t v = getr(g, z), r = v;
	int c = (g->f & FC) ? 1 : 0;
	if (x == 0) {
		int nc;
		switch (y) {
		case 0: nc = v >> 7; r = (v << 1) | nc; break;
		case 1: nc = v & 1; r = (v >> 1) | (nc << 7); break;
		case 2: nc = v >> 7; r = (v << 1) | c; break;
		case 3: nc = v & 1; r = (v >> 1) | (c << 7); break;
		case 4: nc = v >> 7; r = v << 1; break;
		case 5: nc = v & 1; r = (v >> 1) | (v & 0x80); break;
		case 6: nc = 0; r = (v << 4) | (v >> 4); break;
		default: nc = v & 1; r = v >> 1; break;
		}
		g->f = (r ? 0 : FZ) | (nc ? FC : 0);
		setr(g, z, r);
	} else if (x == 1) {
		g->f = (g->f & FC) | FH | ((v & (1 << y)) ? 0 : FZ);
		return z == 6 ? 12 : 8;
	} else if (x == 2) setr(g, z, v & ~(1 << y));
	else setr(g, z, v | (1 << y));
	return z == 6 ? 16 : 8;
}

static int exec(GB *g)
{
	uint8_t op = fetch(g);
	int x = op >> 6, y = (op >> 3) & 7, z = op & 7, p = y >> 1, q = y & 1;
	switch (x) {
	case 0:
		switch (z) {
		case 0:
			if (y == 0) return 4;
			if (y == 1) { uint16_t a = fetch16(g); wb(g, a, g->sp & 0xff); wb(g, a + 1, g->sp >> 8); return 20; }
			if (y == 2) {
				fetch(g);
				if (g->io[0x4d] & 1) { g->double_speed ^= 1; g->io[0x4d] = 0; }
				return 4;
			}
			{
				int8_t e = (int8_t)fetch(g);
				if (y == 3 || cond(g, y - 4)) { g->pc += e; return 12; }
				return 8;
			}
		case 1:
			if (!q) { set16(g, p, fetch16(g)); return 12; }
			{
				uint32_t hl = HL, rr = get16(g, p), r = hl + rr;
				g->f = (g->f & FZ) | (((hl & 0xfff) + (rr & 0xfff)) > 0xfff ? FH : 0) | (r > 0xffff ? FC : 0);
				set16(g, 2, r); return 8;
			}
		case 2: {
			uint16_t a;
			switch (p) {
			case 0: a = (g->b << 8) | g->c; break; case 1: a = (g->d << 8) | g->e; break;
			case 2: a = HL; set16(g, 2, a + 1); break; default: a = HL; set16(g, 2, a - 1); break;
			}
			if (!q) wb(g, a, g->a); else g->a = rb(g, a);
			return 8;
		}
		case 3: set16(g, p, get16(g, p) + (q ? -1 : 1)); return 8;
		case 4: { uint8_t r = getr(g, y) + 1; g->f = (g->f & FC) | (r ? 0 : FZ) | ((r & 15) == 0 ? FH : 0); setr(g, y, r); return y == 6 ? 12 : 4; }
		case 5: { uint8_t r = getr(g, y) - 1; g->f = (g->f & FC) | FN | (r ? 0 : FZ) | ((r & 15) == 15 ? FH : 0); setr(g, y, r); return y == 6 ? 12 : 4; }
		case 6: setr(g, y, fetch(g)); return y == 6 ? 12 : 8;
		default: {
			uint8_t a = g->a; int c = (g->f & FC) ? 1 : 0, nc;
			switch (y) {
			case 0: nc = a >> 7; g->a = (a << 1) | nc; g->f = nc ? FC : 0; break;
			case 1: nc = a & 1; g->a = (a >> 1) | (nc << 7); g->f = nc ? FC : 0; break;
			case 2: nc = a >> 7; g->a = (a << 1) | c; g->f = nc ? FC : 0; break;
			case 3: nc = a & 1; g->a = (a >> 1) | (c << 7); g->f = nc ? FC : 0; break;
			case 4: {
				int adj = 0, cf = g->f & FC;
				if (!(g->f & FN)) { if (cf || a > 0x99) { adj |= 0x60; cf = FC; } if ((g->f & FH) || (a & 15) > 9) adj |= 6; a += adj; }
				else { if (cf) adj |= 0x60; if (g->f & FH) adj |= 6; a -= adj; }
				g->a = a; g->f = (g->f & FN) | (a ? 0 : FZ) | cf; break;
			}
			case 5: g->a = ~a; g->f |= FN | FH; break;
			case 6: g->f = (g->f & FZ) | FC; break;
			default: g->f = (g->f & FZ) | ((g->f & FC) ? 0 : FC); break;
			}
			return 4;
		}
		}
	case 1:
		if (op == 0x76) { g->halted = 1; return 4; }
		setr(g, y, getr(g, z));
		return (y == 6 || z == 6) ? 8 : 4;
	case 2:
		alu(g, y, getr(g, z));
		return z == 6 ? 8 : 4;
	}
	switch (z) {
	case 0:
		if (y < 4) { if (cond(g, y)) { g->pc = pop(g); return 20; } return 8; }
		if (y == 4) { wb(g, 0xff00 | fetch(g), g->a); return 12; }
		if (y == 6) { g->a = rb(g, 0xff00 | fetch(g)); return 12; }
		{
			int8_t e = (int8_t)fetch(g); uint16_t sp = g->sp; uint8_t u = (uint8_t)e;
			g->f = (((sp & 15) + (u & 15)) > 15 ? FH : 0) | (((sp & 0xff) + u) > 0xff ? FC : 0);
			if (y == 5) { g->sp = sp + e; return 16; }
			set16(g, 2, sp + e); return 12;
		}
	case 1:
		if (!q) {
			uint16_t v = pop(g);
			switch (p) { case 0: g->b = v >> 8; g->c = v; break; case 1: g->d = v >> 8; g->e = v; break;
			case 2: g->h = v >> 8; g->l = v; break; default: g->a = v >> 8; g->f = v & 0xf0; }
			return 12;
		}
		switch (p) {
		case 0: g->pc = pop(g); return 16;
		case 1: g->pc = pop(g); g->ime = 1; return 16;
		case 2: g->pc = HL; return 4;
		default: g->sp = HL; return 8;
		}
	case 2:
		if (y < 4) { uint16_t a = fetch16(g); if (cond(g, y)) { g->pc = a; return 16; } return 12; }
		if (y == 4) { wb(g, 0xff00 | g->c, g->a); return 8; }
		if (y == 5) { wb(g, fetch16(g), g->a); return 16; }
		if (y == 6) { g->a = rb(g, 0xff00 | g->c); return 8; }
		g->a = rb(g, fetch16(g)); return 16;
	case 3:
		if (y == 0) { g->pc = fetch16(g); return 16; }
		if (y == 1) return exec_cb(g);
		if (y == 6) { g->ime = 0; g->ime_delay = 0; return 4; }
		if (y == 7) { g->ime_delay = 1; return 4; }
		return 4;
	case 4:
		if (y < 4) { uint16_t a = fetch16(g); if (cond(g, y)) { push(g, g->pc); g->pc = a; return 24; } return 12; }
		return 4;
	case 5:
		if (!q) {
			uint16_t v;
			switch (p) { case 0: v = (g->b << 8) | g->c; break; case 1: v = (g->d << 8) | g->e; break;
			case 2: v = HL; break; default: v = (g->a << 8) | g->f; }
			push(g, v); return 16;
		}
		if (p == 0) { uint16_t a = fetch16(g); push(g, g->pc); g->pc = a; return 24; }
		return 4;
	case 6: alu(g, y, fetch(g)); return 8;
	default: push(g, g->pc); g->pc = y * 8; return 16;
	}
}

int gb_step(GB *g)
{
	uint8_t pend = g->ie & g->io[0x0f] & 0x1f;
	if (g->halted && pend) g->halted = 0;
	if (g->ime && pend) {
		int i = 0;
		while (!(pend & (1 << i))) i++;
		g->io[0x0f] &= ~(1 << i);
		g->ime = 0;
		push(g, g->pc);
		g->pc = 0x40 + i * 8;
		tick(g, 20);
		return 20;
	}
	if (g->halted) { tick(g, 4); return 4; }
	int ei = g->ime_delay;
	g->ime_delay = 0;
	int cyc = exec(g);
	if (ei) g->ime = 1;
	g->instrs++;
	tick(g, cyc);
	return cyc;
}

GB *gb_new(const char *path)
{
	FILE *fp = fopen(path, "rb");
	if (!fp) return NULL;
	GB *g = calloc(1, sizeof(GB));
	fseek(fp, 0, SEEK_END);
	g->romsize = ftell(fp);
	fseek(fp, 0, SEEK_SET);
	g->rom = malloc(g->romsize);
	if (fread(g->rom, 1, g->romsize, fp) != g->romsize) { fclose(fp); free(g->rom); free(g); return NULL; }
	fclose(fp);
	g->rombanks = g->romsize / 0x4000;
	g->romflags = calloc(g->romsize, 1);
	g->bank_lo = 1; update_bank(g);
	g->svbk = 1;
	g->a = 0x11; g->f = 0x80; g->b = 0; g->c = 0; g->d = 0xff; g->e = 0x56; g->h = 0; g->l = 0x0d;
	g->sp = 0xfffe; g->pc = 0x100;
	g->io[0x40] = 0x91; g->io[0x47] = 0xfc; g->mode = 2;
	for (int i = 0; i < 64; i++) { g->bgpal[i] = 0xff; g->obpal[i] = 0xff; }
	return g;
}

void gb_free(GB *g) { free(g->rom); free(g->romflags); free(g->snd); free(g->vw); free(g->ww); free(g); }

/* Runs until the next VBlank (or a frame's time with the LCD off); max_cycles guards a stuck CPU. */
int gb_run_frame(GB *g)
{
	g->frame_done = 0;
	uint64_t start = g->cycles, lim = g->double_speed ? 70224 * 4 : 70224 * 2;
	while (!g->frame_done && g->cycles - start < lim) gb_step(g);
	return g->frame_done;
}

/* Runs until PC equals pc in the given bank (bank -1: any), or max_cycles pass. Returns 1 when hit. */
int gb_run_until(GB *g, int pc, int bank, uint64_t max_cycles)
{
	uint64_t start = g->cycles;
	while (g->cycles - start < max_cycles) {
		gb_step(g);
		if (g->pc == pc && (bank < 0 || pc < 0x4000 || g->rombank == bank)) return 1;
	}
	return 0;
}

void gb_set_joy(GB *g, int joy) { if (joy & ~g->joy) g->io[0x0f] |= 0x10; g->joy = joy; }
uint32_t *gb_frame(GB *g) { return g->frame; }
uint8_t *gb_vram(GB *g) { return g->vram; }
uint8_t *gb_oam(GB *g) { return g->oam; }
uint8_t *gb_bgpal(GB *g) { return g->bgpal; }
uint8_t *gb_obpal(GB *g) { return g->obpal; }
uint8_t *gb_wram(GB *g) { return g->wram; }
uint8_t *gb_io(GB *g) { return g->io; }
uint8_t *gb_hram(GB *g) { return g->hram; }
uint8_t *gb_eram(GB *g) { return g->eram; }
uint8_t *gb_romflags(GB *g) { return g->romflags; }
int gb_read(GB *g, int a) { int f = g->fetching; uint32_t lr = g->last_rom; uint8_t v = rb(g, a); g->fetching = f; g->last_rom = lr; return v; }
void gb_write(GB *g, int a, int v) { wb(g, a, v); }
int gb_reg(GB *g, int i)
{
	switch (i) {
	case 0: return g->pc; case 1: return g->sp; case 2: return (g->a << 8) | g->f; case 3: return (g->b << 8) | g->c;
	case 4: return (g->d << 8) | g->e; case 5: return HL; case 6: return g->rombank; case 7: return g->ly;
	case 8: return g->double_speed; case 9: return g->ime;
	}
	return 0;
}
uint64_t gb_cycles(GB *g) { return g->cycles; }
uint64_t gb_frames(GB *g) { return g->frames; }

void gb_snd_enable(GB *g, int on) { if (on && !g->snd) { g->snd_cap = 65536; g->snd = malloc(g->snd_cap * sizeof(SndEv)); } g->snd_n = 0; }
int gb_snd_count(GB *g) { return g->snd_n; }
SndEv *gb_snd(GB *g) { return g->snd; }
void gb_vw_enable(GB *g, int on) { if (on && !g->vw) { g->vw_cap = 65536; g->vw = malloc(g->vw_cap * sizeof(WrEv)); } if (!on) { free(g->vw); g->vw = NULL; g->vw_cap = 0; } g->vw_n = 0; }
int gb_vw_count(GB *g) { return g->vw_n; }
WrEv *gb_vw(GB *g) { return g->vw; }
void gb_ww_enable(GB *g, int lo, int hi) { if (!g->ww) { g->ww_cap = 65536; g->ww = malloc(g->ww_cap * sizeof(WrEv)); } g->ww_lo = lo; g->ww_hi = hi; g->ww_n = 0; }
int gb_ww_count(GB *g) { return g->ww_n; }
WrEv *gb_ww(GB *g) { return g->ww; }
int gb_sizeof_state(void) { return sizeof(GB); }
/* Snapshots: the struct plus the ROM flags; pointers are kept from the live machine. */
void gb_save(GB *g, uint8_t *buf) { memcpy(buf, g, sizeof(GB)); }
void gb_load(GB *g, const uint8_t *buf)
{
	GB keep = *g;
	memcpy(g, buf, sizeof(GB));
	g->rom = keep.rom; g->romflags = keep.romflags;
	g->snd = keep.snd; g->snd_n = keep.snd_n; g->snd_cap = keep.snd_cap;
	g->vw = keep.vw; g->vw_n = keep.vw_n; g->vw_cap = keep.vw_cap;
	g->ww = keep.ww; g->ww_n = keep.ww_n; g->ww_cap = keep.ww_cap;
}

/* Sets PC (0), SP (1) or AF/BC/DE/HL (2-5), for calling routines of the ROM from Python. */
void gb_set_reg(GB *g, int i, int v)
{
	switch (i) {
	case 0: g->pc = v; break; case 1: g->sp = v; break;
	case 2: g->a = v >> 8; g->f = v & 0xf0; break; case 3: g->b = v >> 8; g->c = v; break;
	case 4: g->d = v >> 8; g->e = v; break; case 5: g->h = v >> 8; g->l = v; break;
	}
	g->halted = 0;
}
