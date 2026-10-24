/*
 * Tyrian3D: the modern UI. See ui.h.
 */
#include "ui.h"

#include "config.h"
#include "episodes.h"
#include "helptext.h"
#include "keyboard.h"
#include "layer3d.h"
#include "mainint.h"
#include "mouse.h"
#include "palette.h"
#include "player.h"
#include "render_gpu.h"
#include "rogue.h"
#include "settings3d.h"
#include "sprite.h"
#include "text_record.h"
#include "tyrian2.h"
#include "varz.h"
#include "video.h"

#include <math.h>
#include <stdio.h>
#include <string.h>

/* --- Switches ------------------------------------------------------------------------------- */

static bool fonts_wanted(void)
{
	static int on = -1;
	if (on < 0)
		on = SDL_getenv("TYR3D_FONTS") == NULL || SDL_atoi(SDL_getenv("TYR3D_FONTS")) != 0;
	return on;
}

bool ui_modern(void)
{
	return settings3d.menus_modern && l3d_enabled && fonts_wanted() && rgpu_ui_text_ready();
}

bool ui_fill_screens(void)
{
	return settings3d.screens_fill && ui_modern();
}

void ui_fill_rect(int window_w, int window_h, SDL_Rect *out)
{
	int w = window_h * 8 / 5, h = window_h;
	if (w > window_w)
	{
		w = window_w;
		h = window_w * 5 / 8;
	}
	*out = (SDL_Rect){ (window_w - w) / 2, (window_h - h) / 2, w, h };
}

/* --- Colours: the original's brass, gold and warm browns ------------------------------------ */

typedef struct { float r, g, b, a; } Colour;

#define RGB(r, g, b) { (r) / 255.0f, (g) / 255.0f, (b) / 255.0f, 1.0f }
#define RGBA(r, g, b, a) { (r) / 255.0f, (g) / 255.0f, (b) / 255.0f, (a) }

static const Colour C_FILL_TOP = RGBA(54, 40, 29, 0.80f);     // a panel's glass, at its top ...
static const Colour C_FILL_BOTTOM = RGBA(30, 21, 15, 0.88f);  // ... and its bottom
static const Colour C_RIM_TOP = RGB(214, 176, 112);           // the brass rim, lit from above
static const Colour C_RIM_BOTTOM = RGB(132, 100, 60);
static const Colour C_RIM_DARK = RGBA(22, 15, 10, 0.75f);     // the line inside the rim
static const Colour C_SEL_TOP = RGBA(136, 100, 58, 0.96f);    // the selected item's card
static const Colour C_SEL_BOTTOM = RGBA(100, 72, 40, 0.96f);
static const Colour C_SEL_RIM = RGB(244, 206, 128);
static const Colour C_WELL = RGBA(18, 12, 8, 0.82f);          // inset wells (bars, keys)
static const Colour C_WELL_RIM = RGB(110, 86, 56);
static const Colour C_GOLD_TOP = RGB(250, 222, 160);          // titles
static const Colour C_GOLD_BOTTOM = RGB(206, 158, 88);
static const Colour C_CREAM = RGB(248, 238, 216);             // selected and primary text
static const Colour C_TAN = RGB(214, 186, 136);               // items
static const Colour C_DIM = RGB(150, 128, 98);                // hints, disabled
static const Colour C_FAINT = RGB(110, 92, 70);
static const Colour C_SUB = RGB(196, 204, 156);               // lines under titles (the shop's costs)
static const Colour C_GREEN = RGB(120, 230, 120);             // pips lit
static const Colour C_PIP_OFF = RGBA(64, 52, 40, 0.9f);

/* --- Layout --------------------------------------------------------------------------------- */

typedef struct { float x, y, w, h; } Box;

static struct
{
	float unit;   // window points per virtual unit (1080 to the window's height at the UI scale 100 %)
	float px;     // a window pixel, points
	Box window;
	Box safe;     // the 16:9 area
	float alpha;  // the whole UI's opacity (the screen fading in or out)
} L;

// Units to points.
#define U(v) ((v) * L.unit)

static void layout_begin(const UIView *view, float alpha)
{
	const float scale = settings3d.ui_scale / 100.0f;
	L.px = view->pixel > 0 ? view->pixel : 1;
	// (At most 1440 units wide too: narrow windows (5:4) keep a 4:3 room for the layouts.)
	L.unit = SDL_min(view->h / 1080.0f, view->w / 1440.0f) * scale;
	L.window = (Box){ 0, 0, view->w, view->h };
	const float safe_w = SDL_min(view->w, view->h * 16.0f / 9.0f);
	L.safe = (Box){ (view->w - safe_w) / 2, 0, safe_w, view->h };
	L.alpha = alpha;
}

// A cap height: units, but not under a size in the window's pixels (legible in small windows).
static float cap_of(float units, float min_pixels)
{
	return SDL_max(U(units), min_pixels * L.px);
}

#define CAP_TITLE() cap_of(40, 20)
#define CAP_HEAD() cap_of(28, 15)
#define CAP_ITEM() cap_of(23, 14)
#define CAP_SMALL() cap_of(16, 11)
#define CAP_KEY() cap_of(14, 10)

static Box inset(Box b, float d)
{
	return (Box){ b.x + d, b.y + d, b.w - 2 * d, b.h - 2 * d };
}

static bool inside(Box b, float x, float y)
{
	return x >= b.x && x < b.x + b.w && y >= b.y && y < b.y + b.h;
}

static float snap(float v)
{
	return roundf(v / L.px) * L.px;
}

/* --- Drawing ---------------------------------------------------------------------------------- */

static void quad(const float x[4], const float y[4], const Colour c[4])
{
	float rgba[4][4];
	for (int k = 0; k < 4; ++k)
	{
		rgba[k][0] = c[k].r;
		rgba[k][1] = c[k].g;
		rgba[k][2] = c[k].b;
		rgba[k][3] = c[k].a * L.alpha;
	}
	rgpu_ui_quad(x, y, rgba);
}

static void rect(Box b, Colour top, Colour bottom)
{
	const float x[4] = { b.x, b.x + b.w, b.x + b.w, b.x };
	const float y[4] = { b.y, b.y, b.y + b.h, b.y + b.h };
	const Colour c[4] = { top, top, bottom, bottom };
	quad(x, y, c);
}

static void rect_h(Box b, Colour left, Colour right)
{
	const float x[4] = { b.x, b.x + b.w, b.x + b.w, b.x };
	const float y[4] = { b.y, b.y, b.y + b.h, b.y + b.h };
	const Colour c[4] = { left, right, right, left };
	quad(x, y, c);
}

static Colour with_alpha(Colour c, float a)
{
	c.a *= a;
	return c;
}

static Colour mix(Colour a, Colour b, float t)
{
	t = SDL_clamp(t, 0.0f, 1.0f);
	return (Colour){ a.r + (b.r - a.r) * t, a.g + (b.g - a.g) * t, a.b + (b.b - a.b) * t, a.a + (b.a - a.a) * t };
}

// A rectangle with its corners cut by c (an octagon): its eight corners clockwise from the top
// edge's left end.
static void octagon(Box b, float c, float x[8], float y[8])
{
	c = SDL_clamp(c, 0.0f, SDL_min(b.w, b.h) * 0.5f);
	const float x0 = b.x, x1 = b.x + b.w, y0 = b.y, y1 = b.y + b.h;
	const float px[8] = { x0 + c, x1 - c, x1, x1, x1 - c, x0 + c, x0, x0 };
	const float py[8] = { y0, y0, y0 + c, y1 - c, y1, y1, y1 - c, y0 + c };
	memcpy(x, px, sizeof(px));
	memcpy(y, py, sizeof(py));
}

// The chamfer of a box grown by d (shrunk if d < 0), so its cut edges stay parallel.
static float chamfer_grown(float c, float d)
{
	return SDL_max(c + 0.4142f * d, 0.0f);
}

// An octagon's colour at a height: from top to bottom of the box `ref`.
static Colour shade_at(Colour top, Colour bottom, Box ref, float y)
{
	return mix(top, bottom, ref.h > 0 ? (y - ref.y) / ref.h : 0);
}

static void fill_octagon(Box b, float c, Colour top, Colour bottom)
{
	float x[8], y[8];
	octagon(b, c, x, y);
	static const int parts[3][4] = { { 0, 1, 4, 5 }, { 7, 0, 5, 6 }, { 1, 2, 3, 4 } };
	for (int p = 0; p < 3; ++p)
	{
		float qx[4], qy[4];
		Colour qc[4];
		for (int k = 0; k < 4; ++k)
		{
			qx[k] = x[parts[p][k]];
			qy[k] = y[parts[p][k]];
			qc[k] = shade_at(top, bottom, b, qy[k]);
		}
		quad(qx, qy, qc);
	}
}

// The blurred picture under an octagon (frosted glass), where there is one.
static void frost_octagon(Box b, float c, float brightness)
{
	if (!rgpu_ui_frost_ready())
		return;
	float x[8], y[8];
	octagon(b, c, x, y);
	static const int parts[3][4] = { { 0, 1, 4, 5 }, { 7, 0, 5, 6 }, { 1, 2, 3, 4 } };
	const float tint[4] = { brightness, brightness * 0.97f, brightness * 0.93f, L.alpha };
	for (int p = 0; p < 3; ++p)
	{
		float qx[4], qy[4];
		for (int k = 0; k < 4; ++k)
		{
			qx[k] = x[parts[p][k]];
			qy[k] = y[parts[p][k]];
		}
		rgpu_ui_frost(qx, qy, tint);
	}
}

// A band between an octagon and one inside it (d further in, d < 0: outside), coloured from top to
// bottom at each edge: outer and inner colours.
static void band(Box b, float c, float d, Colour out_top, Colour out_bottom, Colour in_top, Colour in_bottom)
{
	float ox[8], oy[8], ix[8], iy[8];
	octagon(b, c, ox, oy);
	octagon(inset(b, d), chamfer_grown(c, -d), ix, iy);
	const Box ref = d >= 0 ? b : inset(b, d);
	for (int e = 0; e < 8; ++e)
	{
		const int n = (e + 1) % 8;
		const float qx[4] = { ox[e], ox[n], ix[n], ix[e] };
		const float qy[4] = { oy[e], oy[n], iy[n], iy[e] };
		const Colour qc[4] = { shade_at(out_top, out_bottom, ref, oy[e]), shade_at(out_top, out_bottom, ref, oy[n]),
		                       shade_at(in_top, in_bottom, ref, iy[n]), shade_at(in_top, in_bottom, ref, iy[e]) };
		quad(qx, qy, qc);
	}
}

// A rim of width w along an octagon's edge, smoothed by a pixel on either side.
static void rim(Box b, float c, float w, Colour top, Colour bottom)
{
	const Colour none_t = with_alpha(top, 0), none_b = with_alpha(bottom, 0);
	band(b, c, -L.px, top, bottom, none_t, none_b);       // the outer edge's smoothing
	band(b, c, w, top, bottom, top, bottom);               // the rim
	band(inset(b, w), chamfer_grown(c, -w), L.px, top, bottom, none_t, none_b);  // the inner edge's
}

// A soft shadow round an octagon, a little below it.
static void drop_shadow(Box b, float c, float spread, float strength)
{
	const Box s = { b.x, b.y + spread * 0.3f, b.w, b.h };
	const Colour dark = { 0, 0, 0, strength }, clear = { 0, 0, 0, 0 };
	band(s, c, -spread, dark, dark, clear, clear);
}

typedef enum
{
	PANEL_GLASS,  // a window of the menu: frosted glass in a brass rim
	PANEL_SOLID,  // the same, opaque enough for over the level (the HUD's, no frost)
	PANEL_CARD,   // the selected item's card
	PANEL_WELL,   // an inset well (bars, keys)
	PANEL_HOVER,  // a faint card (an item that can be chosen, not selected)
	PANEL_BAR,    // a small bar of text over a picture (hints, keys): nearly opaque
} PanelStyle;

static void panel(Box b, float c, PanelStyle style)
{
	b = (Box){ snap(b.x), snap(b.y), snap(b.w), snap(b.h) };
	switch (style)
	{
	case PANEL_GLASS:
		drop_shadow(b, c, U(28), 0.42f);
		frost_octagon(b, c, 0.75f);
		fill_octagon(b, c, C_FILL_TOP, C_FILL_BOTTOM);
		rim(b, c, SDL_max(U(2.5f), L.px), C_RIM_TOP, C_RIM_BOTTOM);
		band(inset(b, SDL_max(U(2.5f), L.px)), chamfer_grown(c, -SDL_max(U(2.5f), L.px)), SDL_max(U(1.5f), L.px), C_RIM_DARK,
		     C_RIM_DARK, with_alpha(C_RIM_DARK, 0), with_alpha(C_RIM_DARK, 0));
		break;
	case PANEL_SOLID:
		drop_shadow(b, c, U(16), 0.3f);
		fill_octagon(b, c, with_alpha(C_FILL_TOP, 0.78f), with_alpha(C_FILL_BOTTOM, 0.78f));
		rim(b, c, SDL_max(U(2), L.px), with_alpha(C_RIM_TOP, 0.85f), with_alpha(C_RIM_BOTTOM, 0.85f));
		break;
	case PANEL_CARD:
		drop_shadow(b, c, U(10), 0.35f);
		fill_octagon(b, c, C_SEL_TOP, C_SEL_BOTTOM);
		rim(b, c, SDL_max(U(2.5f), L.px), C_SEL_RIM, mix(C_SEL_RIM, C_RIM_BOTTOM, 0.45f));
		// A sheen along its top.
		fill_octagon((Box){ b.x + U(3), b.y + U(3), b.w - U(6), b.h * 0.42f }, SDL_max(c - U(2), 0),
		             (Colour){ 1, 0.95f, 0.8f, 0.14f }, (Colour){ 1, 0.95f, 0.8f, 0.0f });
		break;
	case PANEL_WELL:
		fill_octagon(b, c, C_WELL, mix(C_WELL, (Colour){ 0.12f, 0.08f, 0.05f, 0.82f }, 1));
		rim(b, c, SDL_max(U(1.5f), L.px), C_WELL_RIM, with_alpha(C_WELL_RIM, 0.6f));
		break;
	case PANEL_HOVER:
		fill_octagon(b, c, (Colour){ 0.55f, 0.42f, 0.25f, 0.16f }, (Colour){ 0.45f, 0.33f, 0.2f, 0.1f });
		rim(b, c, SDL_max(U(1.5f), L.px), with_alpha(C_RIM_BOTTOM, 0.55f), with_alpha(C_RIM_BOTTOM, 0.35f));
		break;
	case PANEL_BAR:
		drop_shadow(b, c, U(12), 0.35f);
		fill_octagon(b, c, (Colour){ C_FILL_TOP.r, C_FILL_TOP.g, C_FILL_TOP.b, 0.92f },
		             (Colour){ C_FILL_BOTTOM.r, C_FILL_BOTTOM.g, C_FILL_BOTTOM.b, 0.94f });
		rim(b, c, SDL_max(U(2), L.px), with_alpha(C_RIM_TOP, 0.9f), with_alpha(C_RIM_BOTTOM, 0.9f));
		break;
	}
}

// A thin horizontal rule, fading at its ends.
static void rule(float x, float y, float w, Colour c)
{
	const float h = SDL_max(U(1.5f), L.px);
	const float fade = SDL_min(w * 0.2f, U(60));
	const Box l = { x, snap(y), fade, h }, m = { x + fade, snap(y), w - 2 * fade, h }, r = { x + w - fade, snap(y), fade, h };
	rect_h(l, with_alpha(c, 0), c);
	rect(m, c, c);
	rect_h(r, c, with_alpha(c, 0));
}

/* --- Text ----------------------------------------------------------------------------------- */

enum { FONT_BOLD = RGPU_FONT_BOLD, FONT_SEMIBOLD = RGPU_FONT_SEMIBOLD, FONT_MEDIUM = RGPU_FONT_MEDIUM };
enum { ALIGN_LEFT, ALIGN_CENTRE, ALIGN_RIGHT };

static float text_w(int font, const char *s, float cap)
{
	return rgpu_ui_text_width(font, s, cap);
}

// Text with its capitals' top at y, aligned on x, shaded from top to bottom.
static void text_graded(int font, const char *s, float x, float y, float cap, Colour top, Colour bottom, int align, bool shadow)
{
	if (s == NULL || s[0] == '\0')
		return;
	const float w = text_w(font, s, cap);
	if (align == ALIGN_CENTRE)
		x -= w / 2;
	else if (align == ALIGN_RIGHT)
		x -= w;
	const float t[4] = { top.r, top.g, top.b, top.a * L.alpha };
	const float b[4] = { bottom.r, bottom.g, bottom.b, bottom.a * L.alpha };
	rgpu_ui_text(font, s, x, y, cap, t, b, shadow ? SDL_max(cap * 0.07f, L.px) : 0);
}

static void text(int font, const char *s, float x, float y, float cap, Colour c, int align)
{
	text_graded(font, s, x, y, cap, c, mix(c, (Colour){ c.r * 0.82f, c.g * 0.8f, c.b * 0.78f, c.a }, 1), align, true);
}

// Text in a box's middle (vertically).
static void text_mid(int font, const char *s, Box b, float pad, float cap, Colour c, int align)
{
	const float x = align == ALIGN_LEFT ? b.x + pad : align == ALIGN_RIGHT ? b.x + b.w - pad : b.x + b.w / 2;
	text(font, s, x, b.y + (b.h - cap) / 2, cap, c, align);
}

// A string cut to fit a width, ending in "..." if cut.
static void fit_text(int font, const char *s, float cap, float width, char *out, size_t size)
{
	SDL_strlcpy(out, s, size);
	if (text_w(font, out, cap) <= width)
		return;
	size_t n = strlen(out);
	while (n > 0)
	{
		out[--n] = '\0';
		char trial[160];
		snprintf(trial, sizeof(trial), "%s...", out);
		if (text_w(font, trial, cap) <= width)
		{
			SDL_strlcpy(out, trial, size);
			return;
		}
	}
}

// Text wrapped at word boundaries into lines no wider than w, from y down; returns the height used.
// (lines: at most that many, the last cut with "..." if the text is longer.)
static float text_wrapped(int font, const char *s, float x, float y, float w, float cap, Colour c, int align, int lines)
{
	const float line_h = cap * 1.75f;
	char line[200];
	int count = 0;
	const char *p = s;
	while (*p != '\0' && count < lines)
	{
		while (*p == ' ')
			++p;
		size_t best = 0;
		size_t n = 0;
		for (;;)
		{
			while (p[n] != '\0' && p[n] != ' ')
				++n;
			char trial[200];
			const size_t len = SDL_min(n, sizeof(trial) - 1);
			memcpy(trial, p, len);
			trial[len] = '\0';
			if (text_w(font, trial, cap) > w && best > 0)
				break;
			best = len;
			if (p[n] == '\0' || len >= sizeof(trial) - 1)
				break;
			++n;
		}
		memcpy(line, p, best);
		line[best] = '\0';
		p += best;
		++count;
		if (count == lines && *p != '\0')
		{
			char cut[200];
			snprintf(cut, sizeof(cut), "%s %s", line, p);
			fit_text(font, cut, cap, w, line, sizeof(line));
		}
		const float lx = align == ALIGN_CENTRE ? x + w / 2 : align == ALIGN_RIGHT ? x + w : x;
		text(font, line, lx, y + (count - 1) * line_h, cap, c, align);
	}
	return count * line_h;
}

/* --- Widgets ------------------------------------------------------------------------------- */

// A filled triangle (arrows): its three corners.
static void triangle(float x0, float y0, float x1, float y1, float x2, float y2, Colour c)
{
	const float x[4] = { x0, x1, x2, x2 }, y[4] = { y0, y1, y2, y2 };
	const Colour cc[4] = { c, c, c, c };
	quad(x, y, cc);
}

typedef enum { KEY_TEXT, KEY_UP_DOWN, KEY_LEFT_RIGHT } KeyGlyph;

// A key's cap with its name or arrows, and what it does after it; returns the width taken.
static float key_hint(float x, float y, KeyGlyph glyph, const char *key, const char *action, Colour c)
{
	const float cap = CAP_KEY(), h = cap * 2.1f, small = CAP_SMALL();
	float w = glyph == KEY_TEXT ? text_w(FONT_SEMIBOLD, key, cap) + cap * 1.4f : cap * 3.2f;
	w = SDL_max(w, h);
	const Box k = { x, y, w, h };
	panel(k, h * 0.22f, PANEL_WELL);
	const Colour kc = mix(C_CREAM, c, 0.3f);
	if (glyph == KEY_TEXT)
		text_mid(FONT_SEMIBOLD, key, k, 0, cap, kc, ALIGN_CENTRE);
	else
	{
		const float a = cap * 0.62f, cx = k.x + k.w / 2, cy = k.y + k.h / 2;
		if (glyph == KEY_UP_DOWN)
		{
			triangle(cx - a * 1.45f, cy + a * 0.42f, cx - a * 0.25f, cy + a * 0.42f, cx - a * 0.85f, cy - a * 0.5f, kc);
			triangle(cx + a * 0.25f, cy - a * 0.42f, cx + a * 1.45f, cy - a * 0.42f, cx + a * 0.85f, cy + a * 0.5f, kc);
		}
		else
		{
			triangle(cx - a * 0.2f, cy - a * 0.6f, cx - a * 0.2f, cy + a * 0.6f, cx - a * 1.2f, cy, kc);
			triangle(cx + a * 0.2f, cy - a * 0.6f, cx + a * 1.2f, cy, cx + a * 0.2f, cy + a * 0.6f, kc);
		}
	}
	float used = w + cap * 0.6f;
	if (action != NULL && action[0] != '\0')
	{
		text(FONT_MEDIUM, action, x + used, y + (h - small) / 2, small, c, ALIGN_LEFT);
		used += text_w(FONT_MEDIUM, action, small) + cap * 1.8f;
	}
	return used;
}

typedef struct
{
	KeyGlyph glyph;
	const char *key, *action;
} KeyHint;

static float key_hints_width(const KeyHint *hints, int count)
{
	const float cap = CAP_KEY(), small = CAP_SMALL();
	float w = 0;
	for (int i = 0; i < count; ++i)
	{
		const float h = cap * 2.1f;
		float kw = hints[i].glyph == KEY_TEXT ? text_w(FONT_SEMIBOLD, hints[i].key, cap) + cap * 1.4f : cap * 3.2f;
		kw = SDL_max(kw, h);
		w += kw + cap * 0.6f + text_w(FONT_MEDIUM, hints[i].action, small) + cap * 1.8f;
	}
	return w - CAP_KEY() * 1.8f;
}

static float key_hints_height(void)
{
	return CAP_KEY() * 2.1f + 2 * U(10);
}

// A row of key hints on a backing; align as text (x is their left, middle or right), y their top.
static void key_hints(const KeyHint *hints, int count, float x, float y, int align)
{
	const float pad = U(16);
	const float w = key_hints_width(hints, count) + 2 * pad;
	if (align == ALIGN_CENTRE)
		x -= w / 2;
	else if (align == ALIGN_RIGHT)
		x -= w;
	panel((Box){ x, y, w, key_hints_height() }, U(10), PANEL_BAR);
	x += pad;
	for (int i = 0; i < count; ++i)
		x += key_hint(x, y + U(10), hints[i].glyph, hints[i].key, hints[i].action, mix(C_TAN, C_DIM, 0.4f));
}

// A gauge: its well, the fill (darker to brighter), a sheen.
static void bar(Box b, float fraction, Colour c, bool well)
{
	if (well)
		panel(b, b.h * 0.3f, PANEL_WELL);
	const Box in = inset(b, SDL_max(U(3), L.px * 2));
	fraction = SDL_clamp(fraction, 0.0f, 1.0f);
	if (fraction <= 0 || in.w <= 0)
		return;
	const Box f = { in.x, in.y, in.w * fraction, in.h };
	rect_h(f, mix(c, (Colour){ 0, 0, 0, c.a }, 0.45f), c);
	rect((Box){ f.x, f.y, f.w, f.h * 0.4f }, (Colour){ 1, 1, 1, 0.22f * c.a }, (Colour){ 1, 1, 1, 0.04f * c.a });
}

// A row of pips, `on` of them lit.
static void pips(float x, float y, int count, int on, float size, float gap, Colour c)
{
	for (int k = 0; k < count; ++k)
	{
		const Box p = { snap(x + k * (size + gap)), snap(y), snap(size), snap(size) };
		if (k < on)
		{
			fill_octagon(p, size * 0.2f, c, mix(c, (Colour){ 0, 0, 0, c.a }, 0.35f));
			fill_octagon((Box){ p.x, p.y, p.w, p.h * 0.45f }, size * 0.2f, (Colour){ 1, 1, 1, 0.3f * c.a }, (Colour){ 1, 1, 1, 0 });
		}
		else
			fill_octagon(p, size * 0.2f, C_PIP_OFF, mix(C_PIP_OFF, (Colour){ 0, 0, 0, C_PIP_OFF.a }, 0.3f));
	}
}

// A picker's value: the value and a mark that it opens a list.
static void choice_value(Box b, const char *value, float cap, Colour c, bool open)
{
	const float a = cap * 0.42f;
	const float cx = b.x + b.w - a * 1.4f, cy = b.y + b.h / 2;
	if (open)
		triangle(cx - a, cy + a * 0.5f, cx + a, cy + a * 0.5f, cx, cy - a * 0.6f, c);
	else
		triangle(cx - a, cy - a * 0.5f, cx + a, cy - a * 0.5f, cx, cy + a * 0.6f, c);
	char fitted[64];
	fit_text(FONT_SEMIBOLD, value, cap, b.w - a * 4, fitted, sizeof(fitted));
	text(FONT_SEMIBOLD, fitted, cx - a * 2.2f, b.y + (b.h - cap) / 2, cap, c, ALIGN_RIGHT);
}

// Tabs: labels in a row, one selected; returns the height taken. (The shop's, later.)
static float tabs(float x, float y, const char *const *labels, int count, int selected, float *widths_out)
{
	const float cap = CAP_SMALL(), h = cap * 2.6f, pad = cap * 1.1f, gap = U(8);
	for (int i = 0; i < count; ++i)
	{
		const float w = text_w(FONT_SEMIBOLD, labels[i], cap) + 2 * pad;
		const Box t = { x, y, w, h };
		panel(t, h * 0.3f, i == selected ? PANEL_CARD : PANEL_HOVER);
		text_mid(FONT_SEMIBOLD, labels[i], t, 0, cap, i == selected ? C_CREAM : C_TAN, ALIGN_CENTRE);
		if (widths_out != NULL)
			widths_out[i] = w;
		x += w + gap;
	}
	return h;
}

// An item card (the shop's items, the episodes): a title, a line under it, maybe a value at the
// right, and a well for an icon on the left (icon_w 0: none).
static void item_card(Box b, const char *title, const char *line, const char *value, bool selected, bool disabled, float icon_w)
{
	panel(b, U(10), selected ? PANEL_CARD : PANEL_HOVER);
	float x = b.x + U(22);
	if (icon_w > 0)
	{
		const Box w = { x, b.y + (b.h - icon_w) / 2, icon_w, icon_w };
		panel(w, U(8), PANEL_WELL);
		x += icon_w + U(20);
	}
	const float cap = CAP_ITEM(), small = CAP_SMALL();
	const bool two = line != NULL && line[0] != '\0';
	const float total = two ? cap + small * 1.9f : cap;
	const float y = b.y + (b.h - total) / 2;
	const Colour tc = disabled ? C_FAINT : selected ? C_CREAM : C_TAN;
	float value_w = 0;
	if (value != NULL && value[0] != '\0')
	{
		value_w = text_w(FONT_BOLD, value, cap) + U(24);
		text(FONT_BOLD, value, b.x + b.w - U(22), b.y + (b.h - cap) / 2, cap, disabled ? C_FAINT : C_GOLD_TOP, ALIGN_RIGHT);
	}
	char fitted[96];
	fit_text(FONT_SEMIBOLD, title, cap, b.x + b.w - U(22) - value_w - x, fitted, sizeof(fitted));
	text(FONT_SEMIBOLD, fitted, x, y, cap, tc, ALIGN_LEFT);
	if (two)
	{
		fit_text(FONT_MEDIUM, line, small, b.x + b.w - U(22) - value_w - x, fitted, sizeof(fitted));
		text(FONT_MEDIUM, fitted, x, y + cap + small * 0.9f, small, disabled ? C_FAINT : selected ? C_SUB : C_DIM, ALIGN_LEFT);
	}
}

/* --- Published screens -------------------------------------------------------------------- */

static UIMenu building;
static UIMenu published;
static bool have_published = false;
static Uint8 published_screen[320 * 200];   // the screen as it showed the menu
static Uint8 published_picture[320 * 200];  // its picture, without the texts
static bool shown_last = false;              // the frame shown last was the published screen

// Where the mouse is taken on the widgets of the frame built last: a box (window points) and the
// rectangle of the original's item it stands for (screen pixels).
#define HITS 64
static struct
{
	Box box;
	SDL_Rect hit;
} hits[HITS];
static int hit_count = 0;

static void add_hit(Box b, SDL_Rect r)
{
	if (hit_count < HITS && r.w > 0 && r.h > 0 && b.w > 0 && b.h > 0)
	{
		hits[hit_count].box = b;
		hits[hit_count].hit = r;
		++hit_count;
	}
}

UIMenu *ui_menu_begin(UIScreenKind kind, const char *title)
{
	memset(&building, 0, sizeof(building));
	building.kind = kind;
	SDL_strlcpy(building.title, title != NULL ? title : "", sizeof(building.title));
	building.text_color = 0xf0;
	building.nowhere = (SDL_Point){ 319, 199 };
	return &building;
}

UIItem *ui_menu_add(UIMenu *menu, UIItemKind kind, const char *label, int x, int y, int w, int h)
{
	if (menu->item_count >= UI_MENU_ITEMS)
		return &menu->items[UI_MENU_ITEMS - 1];
	UIItem *item = &menu->items[menu->item_count++];
	memset(item, 0, sizeof(*item));
	item->kind = kind;
	SDL_strlcpy(item->label, label != NULL ? label : "", sizeof(item->label));
	item->hit = (SDL_Rect){ x, y, w, h };
	return item;
}

void ui_menu_publish(UIMenu *menu, const SDL_Surface *shown, const SDL_Surface *picture)
{
	if (!l3d_enabled || shown == NULL || shown->w != 320 || shown->h < 200)
		return;
	published = *menu;
	for (int y = 0; y < 200; ++y)
		memcpy(published_screen + y * 320, (const Uint8 *)shown->pixels + y * shown->pitch, 320);
	if (picture == NULL)
		picture = shown;
	static const TextRecord *texts[256];
	text_records_on(picture, texts, (int)COUNTOF(texts), published_picture);
	have_published = true;
}

bool ui_screen_holds(const SDL_Surface *screen)
{
	if (!have_published || !ui_modern() || screen->w != 320 || screen->h < 200)
		return false;
	int same = 0;
	for (int y = 0; y < 200; ++y)
	{
		const Uint8 *a = (const Uint8 *)screen->pixels + y * screen->pitch, *b = published_screen + y * 320;
		for (int x = 0; x < 320; ++x)
			same += a[x] == b[x];
	}
	return same >= 320 * 200 * 98 / 100;
}

void ui_screen_shown(bool shown)
{
	shown_last = shown;
}

const Uint8 *ui_screen_picture(void)
{
	return published_picture;
}

float ui_screen_fade(void)
{
	// How bright the menu's text colours are against the palette faded in (fade_palette's target).
	float now = 0, full = 0;
	for (int i = published.text_color; i < published.text_color + 16 && i < 256; ++i)
	{
		const Uint8 *c = (const Uint8 *)&rgb_palette[i];
		now += c[0] + c[1] + c[2];
		full += colors[i].r + colors[i].g + colors[i].b;
	}
	return full > 0 ? SDL_clamp(now / full, 0.0f, 1.0f) : 1.0f;
}

bool ui_map_pointer(float wx, float wy, Sint32 *x, Sint32 *y)
{
	if (!shown_last || !have_published)
		return false;
	for (int i = hit_count - 1; i >= 0; --i)
	{
		const Box b = hits[i].box;
		if (!inside(b, wx, wy))
			continue;
		const SDL_Rect r = hits[i].hit;
		const float fx = (wx - b.x) / b.w, fy = (wy - b.y) / b.h;
		*x = SDL_clamp(r.x + (Sint32)floorf(fx * r.w), r.x, r.x + r.w - 1);
		*y = SDL_clamp(r.y + (Sint32)floorf(fy * r.h), r.y, r.y + r.h - 1);
		return true;
	}
	*x = published.nowhere.x;
	*y = published.nowhere.y;
	return true;
}

bool ui_wheel_moves(float y)
{
	return shown_last && have_published && published.item_count > 1 && y != 0;
}

/* --- The screens ------------------------------------------------------------------------- */

static const UIView *view_now;

static Box picture_box(void)
{
	return (Box){ view_now->picture[0], view_now->picture[1], view_now->picture[2], view_now->picture[3] };
}

static Box intersect(Box a, Box b)
{
	const float x0 = SDL_max(a.x, b.x), y0 = SDL_max(a.y, b.y);
	const float x1 = SDL_min(a.x + a.w, b.x + b.w), y1 = SDL_min(a.y + a.h, b.y + b.h);
	return (Box){ x0, y0, SDL_max(x1 - x0, 0.0f), SDL_max(y1 - y0, 0.0f) };
}

// A hint line in a pill (the selected item's description).
static void hint_pill(const char *s, float cx, float y)
{
	if (s == NULL || s[0] == '\0')
		return;
	const float cap = CAP_SMALL();
	const float w = SDL_min(text_w(FONT_MEDIUM, s, cap) + cap * 3, L.safe.w - U(120));
	const Box b = { cx - w / 2, y, w, key_hints_height() };
	panel(b, U(10), PANEL_BAR);
	char fitted[160];
	fit_text(FONT_MEDIUM, s, cap, w - cap * 2, fitted, sizeof(fitted));
	text_mid(FONT_MEDIUM, fitted, b, 0, cap, C_CREAM, ALIGN_CENTRE);
}

// The title screen: the menu in a glass panel at the picture's lower left (under the logo, over the
// planet), the selected item's description below it, the keys at the right (below the description
// when there's no room beside it).
static void build_title(const UIMenu *m)
{
	const Box pic = picture_box();
	const Box area = intersect(pic, L.safe);
	const float cap = CAP_ITEM(), cap_s = CAP_SMALL();
	const float pad = U(22), gap = U(20);
	const UIItem *sel = m->selected >= 0 && m->selected < m->item_count ? &m->items[m->selected] : NULL;
	const KeyHint keys[] = { { KEY_UP_DOWN, "", "Select" }, { KEY_TEXT, "Enter", "Confirm" }, { KEY_TEXT, "Esc", "Quit" } };
	const float keys_w = key_hints_width(keys, (int)COUNTOF(keys)) + 2 * U(16), bar_h = key_hints_height();
	const float left = area.x + SDL_max(U(64), area.w * 0.04f), right = area.x + area.w - U(48);
	const float hint_w = sel != NULL && sel->hint[0] != '\0' ? SDL_min(text_w(FONT_MEDIUM, sel->hint, cap_s) + cap_s * 3, area.w * 0.9f) : 0;
	const bool stacked = hint_w > 0 && left + hint_w + gap > right - keys_w;
	float row_h = SDL_max(U(50), cap * 2.05f);
	const float w = SDL_min(SDL_max(U(400), cap * 15), area.w * 0.45f);
	float h = m->item_count * row_h + 2 * pad;
	// Under the logo: no higher than about the picture's middle.
	const float bottom = area.y + area.h - (stacked ? 2 * bar_h + 3 * U(18) : bar_h + U(70));
	const float top_limit = area.y + area.h * 0.46f;
	if (bottom - h < top_limit)
	{
		row_h = SDL_max((bottom - top_limit - 2 * pad) / SDL_max(m->item_count, 1), cap * 1.7f);
		h = m->item_count * row_h + 2 * pad;
	}
	const Box p = { left, bottom - h, w, h };
	panel(p, U(18), PANEL_GLASS);
	for (int i = 0; i < m->item_count; ++i)
	{
		const UIItem *item = &m->items[i];
		const Box r = { p.x + U(12), p.y + pad + i * row_h, p.w - U(24), row_h };
		const bool selected = i == m->selected;
		if (selected)
			panel(inset(r, U(2)), U(10), PANEL_CARD);
		const Colour c = item->disabled ? C_FAINT : selected ? C_CREAM : C_TAN;
		text_mid(selected ? FONT_BOLD : FONT_SEMIBOLD, item->label, r, U(26), cap, c, ALIGN_LEFT);
		if (selected)
		{
			// A brass marker at the left.
			const float a = cap * 0.3f, mx = r.x + U(15), my = r.y + r.h / 2;
			triangle(mx - a * 0.55f, my - a, mx - a * 0.55f, my + a, mx + a * 0.65f, my, C_SEL_RIM);
		}
		add_hit(r, item->hit);
	}
	// The description, and the keys.
	const float hint_y = p.y + p.h + U(18);
	if (hint_w > 0)
		hint_pill(sel->hint, left + hint_w / 2, hint_y);
	if (stacked)
		key_hints(keys, (int)COUNTOF(keys), left, hint_y + bar_h + U(18), ALIGN_LEFT);
	else
		key_hints(keys, (int)COUNTOF(keys), right, hint_y, ALIGN_RIGHT);
	if (m->footer[0] != '\0')
		text(FONT_MEDIUM, m->footer, right, area.y + area.h - U(18) - CAP_KEY(), CAP_KEY(), with_alpha(C_DIM, 0.75f), ALIGN_RIGHT);
}

// A page's header: the page above it (small, spaced) and its name (gold); returns its height.
static float header(Box p, const char *crumb, const char *title)
{
	const float cap_t = CAP_TITLE(), cap_c = CAP_SMALL();
	float y = p.y + U(30);
	if (crumb != NULL && crumb[0] != '\0')
	{
		text(FONT_SEMIBOLD, crumb, p.x + U(40), y, cap_c, C_DIM, ALIGN_LEFT);
		y += cap_c + U(14);
	}
	text_graded(FONT_BOLD, title, p.x + U(40), y, cap_t, C_GOLD_TOP, C_GOLD_BOTTOM, ALIGN_LEFT, true);
	y += cap_t + U(24);
	rule(p.x + U(24), y, p.w - U(48), with_alpha(C_RIM_BOTTOM, 0.8f));
	return y + U(18) - p.y;
}

// A dropdown of the picker's choices, below the value (above it if there's no room).
static void picker_list(const UIMenu *m, Box value)
{
	const float cap = CAP_ITEM();
	const float row_h = SDL_max(U(46), cap * 1.95f);
	float w = value.w + U(40);
	for (int i = 0; i < m->picker_count; ++i)
		w = SDL_max(w, text_w(FONT_SEMIBOLD, m->picker[i], cap) + U(90));
	const float h = m->picker_count * row_h + U(20);
	float x = value.x + value.w - w + U(20);
	x = SDL_min(x, L.safe.x + L.safe.w - w - U(24));
	float y = value.y + value.h + U(6);
	if (y + h > L.window.h - U(24))
		y = SDL_max(value.y - h - U(6), U(24));
	const Box p = { x, y, w, h };
	panel(p, U(12), PANEL_GLASS);
	for (int i = 0; i < m->picker_count; ++i)
	{
		const Box r = { p.x + U(10), p.y + U(10) + i * row_h, p.w - U(20), row_h };
		const bool selected = i == m->picker_selected;
		if (selected)
			panel(inset(r, U(2)), U(8), PANEL_CARD);
		text_mid(FONT_SEMIBOLD, m->picker[i], r, U(22), cap, selected ? C_CREAM : C_TAN, ALIGN_LEFT);
		add_hit(r, m->picker_hit[i]);
	}
}

// Setup and its pages: a centred glass panel, the items in rows (name left, value right), the
// selected item's description at the panel's foot, the keys below it.
static void build_setup(const UIMenu *m)
{
	const float cap = CAP_ITEM();
	const float row_h = SDL_max(U(56), cap * 2.2f);
	const float w = SDL_min(SDL_max(U(940), cap * 30), L.safe.w - U(96));
	const float head_h = U(30) + (m->crumb[0] != '\0' ? CAP_SMALL() + U(14) : 0) + CAP_TITLE() + U(24) + U(18);
	const float foot_h = CAP_SMALL() * 1.75f * 2 + U(44);
	float h = head_h + m->item_count * row_h + U(12) + foot_h;
	const float keys_h = key_hints_height() + U(28);
	float rh = row_h;
	const float room = L.window.h - U(48) - keys_h;
	if (h > room)
	{
		rh = SDL_max((room - head_h - foot_h - U(12)) / SDL_max(m->item_count, 1), cap * 1.6f);
		h = head_h + m->item_count * rh + U(12) + foot_h;
	}
	const Box p = { L.safe.x + (L.safe.w - w) / 2, SDL_max((L.window.h - h - keys_h) / 2, U(24)), w, h };
	panel(p, U(22), PANEL_GLASS);
	const float top = p.y + header(p, m->crumb, m->title);
	const bool picking = m->picker_count > 0;
	Box picker_value = { 0, 0, 0, 0 };
	for (int i = 0; i < m->item_count; ++i)
	{
		const UIItem *item = &m->items[i];
		const Box r = { p.x + U(16), top + i * rh, p.w - U(32), rh };
		const bool selected = i == m->selected;
		if (selected)
			panel(inset(r, U(2)), U(10), PANEL_CARD);
		const Colour c = item->disabled || (picking && !selected) ? C_FAINT : selected ? C_CREAM : C_TAN;
		// The name (without the original's trailing colon), and the value at the right.
		char label[64];
		SDL_strlcpy(label, item->label, sizeof(label));
		const size_t n = strlen(label);
		if (n > 0 && label[n - 1] == ':')
			label[n - 1] = '\0';
		text_mid(FONT_SEMIBOLD, label, r, U(28), cap, c, ALIGN_LEFT);
		const float value_w = SDL_min(U(380), r.w * 0.48f);
		const Box value = { r.x + r.w - value_w - U(14), r.y, value_w, r.h };
		if (item->kind == UI_ITEM_CHOICE)
		{
			choice_value(value, item->value, cap, item->disabled || (picking && !selected) ? C_FAINT : selected ? C_CREAM : C_TAN,
			             picking && selected);
			if (selected)
				picker_value = value;
		}
		else if (item->kind == UI_ITEM_BAR)
		{
			const float bh = SDL_max(U(22), cap * 0.95f);
			const Box b = { value.x + U(20), r.y + (r.h - bh) / 2, value.w - U(20) - U(70), bh };
			bar(b, item->bar, item->muted ? (Colour){ 0.45f, 0.42f, 0.38f, 1 } : (Colour){ 0.95f, 0.76f, 0.42f, 1 }, true);
			char percent[16];
			snprintf(percent, sizeof(percent), "%d%%", (int)lroundf(item->bar * 100));
			text(FONT_SEMIBOLD, item->muted ? "Off" : percent, value.x + value.w, r.y + (r.h - cap) / 2, cap,
			     item->muted ? C_DIM : c, ALIGN_RIGHT);
		}
		if (!picking)
		{
			// The name takes the original's name, the value its value (for the volumes: where on it).
			if (item->hit_value.w > 0)
			{
				add_hit((Box){ r.x, r.y, value.x - r.x, r.h }, item->hit);
				add_hit((Box){ value.x, r.y, r.x + r.w - value.x, r.h }, item->hit_value);
			}
			else
				add_hit(r, item->hit);
		}
	}
	// The description.
	const UIItem *sel = m->selected >= 0 && m->selected < m->item_count ? &m->items[m->selected] : NULL;
	const float foot_y = p.y + p.h - foot_h + U(10);
	rule(p.x + U(24), foot_y, p.w - U(48), with_alpha(C_RIM_BOTTOM, 0.6f));
	if (sel != NULL)
		text_wrapped(FONT_MEDIUM, sel->hint, p.x + U(40), foot_y + U(22), p.w - U(80), CAP_SMALL(), C_DIM, ALIGN_LEFT, 2);
	// The keys.
	const float ky = p.y + p.h + U(22);
	if (picking)
	{
		const KeyHint keys[] = { { KEY_UP_DOWN, "", "Choose" }, { KEY_TEXT, "Enter", "Set" }, { KEY_TEXT, "Esc", "Cancel" } };
		key_hints(keys, (int)COUNTOF(keys), p.x + p.w / 2, ky, ALIGN_CENTRE);
	}
	else if (sel != NULL && sel->kind == UI_ITEM_BAR)
	{
		const KeyHint keys[] = { { KEY_UP_DOWN, "", "Select" }, { KEY_LEFT_RIGHT, "", "Volume" }, { KEY_TEXT, "Enter", "Mute" },
		                         { KEY_TEXT, "Esc", "Back" } };
		key_hints(keys, (int)COUNTOF(keys), p.x + p.w / 2, ky, ALIGN_CENTRE);
	}
	else
	{
		const KeyHint keys[] = { { KEY_UP_DOWN, "", "Select" }, { KEY_TEXT, "Enter", sel != NULL && sel->kind == UI_ITEM_CHOICE ? "Change" : "Confirm" },
		                         { KEY_TEXT, "Esc", "Back" } };
		key_hints(keys, (int)COUNTOF(keys), p.x + p.w / 2, ky, ALIGN_CENTRE);
	}
	if (picking && picker_value.w > 0)
		picker_list(m, picker_value);
}

// The new game's choices (players, episode, difficulty, timed battle): a centred glass panel with
// a card for each choice, its description in it (the episodes: their number above their name).
static void build_choices(const UIMenu *m)
{
	const float cap = CAP_ITEM(), small = CAP_SMALL();
	const bool episodes = m->kind == UI_SCREEN_EPISODES;
	float card_h = SDL_max(U(episodes ? 84 : 88), cap + small * 1.9f + U(30));
	const float gap = U(10);
	const float w = SDL_min(SDL_max(U(820), cap * 27), L.safe.w - U(96));
	const float head_h = U(30) + CAP_TITLE() + U(24) + U(18);
	const float keys_h = key_hints_height() + U(28);
	float h = head_h + m->item_count * (card_h + gap) + U(24);
	const float room = L.window.h - U(48) - keys_h;
	if (h > room)
	{
		card_h = SDL_max((room - head_h - U(24)) / SDL_max(m->item_count, 1) - gap, cap * 1.8f);
		h = head_h + m->item_count * (card_h + gap) + U(24);
	}
	const Box p = { L.safe.x + (L.safe.w - w) / 2, SDL_max((L.window.h - h - keys_h) / 2, U(24)), w, h };
	panel(p, U(22), PANEL_GLASS);
	const float top = p.y + header(p, "", m->title);
	for (int i = 0; i < m->item_count; ++i)
	{
		const UIItem *item = &m->items[i];
		const Box r = { p.x + U(24), top + i * (card_h + gap), p.w - U(48), card_h };
		const bool selected = i == m->selected;
		if (episodes)
		{
			// "Episode 1: Escape": the number small above the name.
			char number[48] = "", name[48];
			SDL_strlcpy(name, item->label, sizeof(name));
			const char *colon = strchr(item->label, ':');
			if (colon != NULL)
			{
				const size_t n = (size_t)(colon - item->label);
				SDL_strlcpy(number, item->label, SDL_min(n + 1, sizeof(number)));
				const char *rest = colon + 1;
				while (*rest == ' ')
					++rest;
				SDL_strlcpy(name, rest, sizeof(name));
			}
			for (char *c = number; *c != '\0'; ++c)
				*c = (char)SDL_toupper(*c);
			panel(r, U(10), selected ? PANEL_CARD : PANEL_HOVER);
			const float y = r.y + (r.h - (small + U(10) + cap)) / 2;
			text(FONT_SEMIBOLD, number, r.x + U(28), y, small, item->disabled ? C_FAINT : selected ? C_SUB : C_DIM, ALIGN_LEFT);
			text(FONT_BOLD, name, r.x + U(28), y + small + U(10), cap, item->disabled ? C_FAINT : selected ? C_CREAM : C_TAN,
			     ALIGN_LEFT);
			if (item->disabled)
				text(FONT_MEDIUM, "Not installed", r.x + r.w - U(28), r.y + (r.h - small) / 2, small, C_FAINT, ALIGN_RIGHT);
		}
		else
		{
			item_card(r, item->label, item->hint, NULL, selected, item->disabled, 0);
			if (item->pips > 0)
			{
				const float size = SDL_max(U(16), L.px * 6), pgap = SDL_max(U(6), L.px * 2);
				const float pw = item->pips * size + (item->pips - 1) * pgap;
				pips(r.x + r.w - U(28) - pw, r.y + (r.h - size) / 2, item->pips, item->pips_on, size, pgap,
				     item->pips_on >= 5 ? (Colour){ 1.0f, 0.45f, 0.3f, 1 } : item->pips_on >= 3 ? (Colour){ 1.0f, 0.78f, 0.35f, 1 } : C_GREEN);
			}
		}
		add_hit(r, item->hit);
	}
	const KeyHint keys[] = { { KEY_UP_DOWN, "", "Select" }, { KEY_TEXT, "Enter", "Confirm" }, { KEY_TEXT, "Esc", "Back" } };
	key_hints(keys, (int)COUNTOF(keys), p.x + p.w / 2, p.y + p.h + U(22), ALIGN_CENTRE);
}

// TYR3D_UI_GALLERY=1 (dev): over the title, the widgets the next screens are made of (the shop's tabs and
// item cards, pickers, bars, pips, keys, wrapped text), to judge the style by.
static void build_gallery(void)
{
	const Box S = L.safe;
	const float cap = CAP_ITEM(), small = CAP_SMALL();
	const Box p = { S.x + U(80), U(70), SDL_min(U(1100), S.w - U(160)), L.window.h - U(140) };
	panel(p, U(22), PANEL_GLASS);
	const float top = p.y + header(p, "WIDGETS", "Front Gun");
	static const char *const labels[] = { "Ship", "Front", "Rear", "Shield", "Generator", "Sidekicks", "Specials" };
	const float tabs_h = tabs(p.x + U(36), top, labels, (int)COUNTOF(labels), 1, NULL);
	static const struct { const char *name, *line, *cost; int power; } items[] = {
		{ "Pulse-Cannon", "Damage 3, fast", "500", 1 }, { "Multi-Cannon", "Spread, 2 at power 3", "750", 0 },
		{ "Protron", "Damage 2, wide", "600", 0 }, { "Missile Launcher", "Homing from power 4", "850", 0 },
	};
	float y = top + tabs_h + U(24);
	const float card_h = SDL_max(U(92), cap + small * 1.9f + U(30));
	for (int i = 0; i < (int)COUNTOF(items); ++i)
	{
		const Box r = { p.x + U(24), y, p.w * 0.62f, card_h };
		item_card(r, items[i].name, items[i].line, items[i].cost, i == 0, false, card_h - U(28));
		if (i == 0)
		{
			const float size = SDL_max(U(16), L.px * 6), gap = SDL_max(U(5), L.px * 2);
			pips(r.x + r.w - U(24) - (11 * size + 10 * gap), r.y + r.h - U(16) - size, 11, items[i].power, size, gap, C_GREEN);
		}
		y += card_h + U(10);
	}
	// Beside the cards: bars, a picker and text.
	const float x = p.x + U(24) + p.w * 0.62f + U(30), w = p.x + p.w - U(30) - x;
	float ty = top + tabs_h + U(30);
	text(FONT_SEMIBOLD, "SHIELD", x, ty, small, C_DIM, ALIGN_LEFT);
	bar((Box){ x, ty + small + U(10), w, U(24) }, 0.8f, (Colour){ 0.35f, 0.75f, 1.0f, 1 }, true);
	ty += small + U(50);
	text(FONT_SEMIBOLD, "ARMOR", x, ty, small, C_DIM, ALIGN_LEFT);
	bar((Box){ x, ty + small + U(10), w, U(24) }, 0.45f, (Colour){ 1.0f, 0.55f, 0.25f, 1 }, true);
	ty += small + U(60);
	const Box pick = { x, ty, w, cap * 2.2f };
	panel(pick, U(10), PANEL_HOVER);
	choice_value(pick, "Power 1 / 11", cap, C_CREAM, false);
	ty += pick.h + U(30);
	text_wrapped(FONT_MEDIUM, "The Pulse-Cannon fires bolts straight ahead; each power level adds damage and speed. Left and right "
	             "choose the power level, Enter buys, Esc goes back.", x, ty, w, small, C_TAN, ALIGN_LEFT, 6);
	const KeyHint keys[] = { { KEY_UP_DOWN, "", "Select" }, { KEY_LEFT_RIGHT, "", "Power" }, { KEY_TEXT, "Enter", "Buy" },
	                         { KEY_TEXT, "Esc", "Back" } };
	key_hints(keys, (int)COUNTOF(keys), p.x + p.w / 2, p.y + p.h + U(18), ALIGN_CENTRE);
	text_graded(FONT_BOLD, "Credits 10 000", p.x + p.w - U(40), p.y + U(34), CAP_HEAD(), C_GOLD_TOP, C_GOLD_BOTTOM, ALIGN_RIGHT, true);
}

void ui_build_screen(const UIView *view)
{
	hit_count = 0;
	if (!have_published)
		return;
	view_now = view;
	layout_begin(view, ui_screen_fade());
	// The picture behind the panels a little darker, so they read clearly (not the title's).
	if (published.kind != UI_SCREEN_TITLE)
		rect(picture_box(), (Colour){ 0, 0, 0, 0.25f }, (Colour){ 0, 0, 0, 0.4f });
	static int gallery = -1;
	if (gallery < 0)
		gallery = SDL_getenv("TYR3D_UI_GALLERY") != NULL;
	switch (published.kind)
	{
	case UI_SCREEN_TITLE:
		if (gallery)
			build_gallery();
		else
			build_title(&published);
		break;
	case UI_SCREEN_SETUP:
		build_setup(&published);
		break;
	case UI_SCREEN_PLAYERS:
	case UI_SCREEN_EPISODES:
	case UI_SCREEN_DIFFICULTY:
	case UI_SCREEN_TIMED:
		build_choices(&published);
		break;
	case UI_SCREEN_NONE:
		break;
	}
}

/* --- The HUD ------------------------------------------------------------------------------- */

// Quads from mark on fade when the ship is near their box (window points), eased in *shown.
static void fade_near_ship(int mark, Box b, float ship_x, float ship_y, float reach, float *shown)
{
	const float dx = SDL_max(SDL_max(b.x - ship_x, ship_x - (b.x + b.w)), 0.0f);
	const float dy = SDL_max(SDL_max(b.y - ship_y, ship_y - (b.y + b.h)), 0.0f);
	const float distance = sqrtf(dx * dx + dy * dy);
	const float target = distance < reach ? 0.3f + 0.7f * distance / reach : 1.0f;
	*shown += (target - *shown) * 0.2f;
	rgpu_ui_fade_since(mark, *shown);
}

// A number with its thousands apart ("10 000").
static void grouped(unsigned long value, char *out, size_t size)
{
	char digits[32];
	snprintf(digits, sizeof(digits), "%lu", value);
	const int n = (int)strlen(digits);
	size_t k = 0;
	for (int i = 0; i < n && k + 2 < size; ++i)
	{
		if (i > 0 && (n - i) % 3 == 0)
			out[k++] = ' ';
		out[k++] = digits[i];
	}
	out[k] = '\0';
}

// A label and a gauge in a HUD row.
static void hud_gauge(float x, float y, float label_w, float bar_w, float row_h, const char *label, float fraction, Colour c)
{
	const float cap = cap_of(17, 9);
	text(FONT_MEDIUM, label, x, y + (row_h - cap) / 2, cap, (Colour){ 0.9f, 0.86f, 0.76f, 0.95f }, ALIGN_LEFT);
	const float bh = SDL_max(row_h * 0.42f, L.px * 4);
	bar((Box){ x + label_w, y + (row_h - bh) / 2, bar_w, bh }, fraction, c, true);
}

void ui_build_hud(const UIView *view)
{
	view_now = view;
	layout_begin(view, 1);
	const Player *p = &player[0];

	// The 16:9 area round the playfield: the HUD stays in it (on ultrawide near the action).
	const Box safe = L.safe;
	const float margin = U(34);

	// Shown values ease towards the game's, so gauges slide.
	static float shown[3] = { -1, -1, -1 };
	const float target[3] = {
		p->shield_max > 0 ? (float)p->shield / p->shield_max : 0,
		p->armor / 28.0f,
		power / 900.0f,
	};
	for (int i = 0; i < 3; ++i)
		shown[i] = shown[i] < 0 ? target[i] : shown[i] + (target[i] - shown[i]) * 0.25f;

	// Where the ship is, so what is over it fades.
	float ship_x = -1e9f, ship_y = -1e9f;
	if (!view->menu_over)
		rgpu_playfield_to_window(p->x + 7.0f, p->y + 7.0f, &ship_x, &ship_y);
	static float fades[4] = { 1, 1, 1, 1 };
	const float reach = U(150);
	const float row_h = SDL_max(U(38), L.px * 14);
	const float label_w = SDL_max(U(104), cap_of(17, 9) * 5.4f);

	// Bottom right: shield, armor, the generator's power; a rogue run's experience.
	{
		const bool generator = !onePlayerAction && !twoPlayerMode;
		int xp = 0, xp_needed = 1, xp_level = 0;
		const bool experience = rogue_xp(&xp, &xp_needed, &xp_level);
		const int rows = 2 + (generator ? 1 : 0) + (experience ? 1 : 0);
		const float bar_w = U(300);
		const Box b = { safe.x + safe.w - margin - (label_w + bar_w + U(40)), safe.y + safe.h - margin - (rows * row_h + U(28)),
		                label_w + bar_w + U(40), rows * row_h + U(28) };
		const int mark = rgpu_ui_mark();
		panel(b, U(12), PANEL_SOLID);
		float y = b.y + U(14);
		Colour armor = { 1.0f, 0.55f, 0.25f, 1 };
		if (target[1] < 0.25f && (SDL_GetTicks() / 250) % 2 == 0)  // low armor flashes
			armor = (Colour){ 1.0f, 0.15f, 0.1f, 1 };
		hud_gauge(b.x + U(20), y, label_w, bar_w, row_h, "SHIELD", shown[0], (Colour){ 0.35f, 0.75f, 1.0f, 1 });
		y += row_h;
		hud_gauge(b.x + U(20), y, label_w, bar_w, row_h, "ARMOR", shown[1], armor);
		y += row_h;
		if (generator)
		{
			hud_gauge(b.x + U(20), y, label_w, bar_w, row_h, "POWER", shown[2], (Colour){ 1.0f, 0.85f, 0.3f, 1 });
			y += row_h;
		}
		if (experience)
		{
			char label[16];
			snprintf(label, sizeof(label), "XP %d", xp_level);
			hud_gauge(b.x + U(20), y, label_w, bar_w, row_h, label, (float)xp / SDL_max(xp_needed, 1),
			          (Colour){ 0x66 / 255.0f, 0x02 / 255.0f, 0x3c / 255.0f, 1 });  // Tyrian purple
		}
		fade_near_ship(mark, b, ship_x, ship_y, reach, &fades[0]);
	}

	// Top right: the guns' power (pips), the sidekicks' ammunition.
	float top_right_w = 0;  // (the boss bar keeps clear of it)
	{
		const float pip = SDL_max(U(20), L.px * 6), gap = SDL_max(U(5), L.px * 2);
		const float pips_w = 11 * pip + 10 * gap;
		int sidekick_rows = 0;
		for (int i = 0; i < 2; ++i)
			sidekick_rows += p->items.sidekick[i] > 0 && p->sidekick[i].ammo_max > 0;
		const int rows = 2 + (sidekick_rows > 0);
		const Box b = { safe.x + safe.w - margin - (label_w + pips_w + U(40)), safe.y + margin, label_w + pips_w + U(40),
		                rows * row_h + U(28) };
		top_right_w = b.w;
		const int mark = rgpu_ui_mark();
		panel(b, U(12), PANEL_SOLID);
		static const Colour gun[2] = { { 0.45f, 1.0f, 0.55f, 1 }, { 1.0f, 0.75f, 0.35f, 1 } };
		const float cap = cap_of(17, 9);
		for (int g = 0; g < 2; ++g)
		{
			const float y = b.y + U(14) + g * row_h;
			text(FONT_MEDIUM, g == 0 ? "FRONT" : "REAR", b.x + U(20), y + (row_h - cap) / 2, cap, (Colour){ 0.9f, 0.86f, 0.76f, 0.95f },
			     ALIGN_LEFT);
			const int level = p->items.weapon[g].id > 0 ? p->items.weapon[g].power : 0;
			pips(b.x + U(20) + label_w, y + (row_h - pip) / 2, 11, level, pip, gap, gun[g]);
		}
		if (sidekick_rows > 0)
		{
			const float y = b.y + U(14) + 2 * row_h;
			const float w = (pips_w - U(12)) / 2;
			text(FONT_MEDIUM, "AMMO", b.x + U(20), y + (row_h - cap) / 2, cap, (Colour){ 0.9f, 0.86f, 0.76f, 0.95f }, ALIGN_LEFT);
			const Colour ammo = { 0x96 / 255.0f, 0x22 / 255.0f, 0x6c / 255.0f, 1 };  // Tyrian purple, lit
			for (int i = 0; i < 2; ++i)
				if (p->items.sidekick[i] > 0 && p->sidekick[i].ammo_max > 0)
				{
					const float bh = SDL_max(row_h * 0.42f, L.px * 4);
					bar((Box){ b.x + U(20) + label_w + i * (w + U(12)), y + (row_h - bh) / 2, w, bh },
					    (float)p->sidekick[i].ammo / p->sidekick[i].ammo_max, ammo, true);
				}
		}
		fade_near_ship(mark, b, ship_x, ship_y, reach, &fades[1]);
	}

	// Bottom left: the score (the cash), lives (arcade), super bombs, the special weapon.
	{
		const float cap_l = cap_of(15, 9), cap_n = cap_of(36, 16);
		char score[32];
		grouped(p->cash, score, sizeof(score));
		const float score_w = SDL_max(text_w(FONT_BOLD, score, cap_n), U(160));
		const bool lives = onePlayerAction || twoPlayerMode;
		const int extra_lives = lives && p->lives != NULL ? (int)*p->lives - 1 : 0;
		const bool special_on = p->items.special > 0 && p->items.special < COUNTOF(special);
		const int bombs = (int)SDL_min(p->superbombs, 10u);
		const float icon = SDL_max(U(34), L.px * 12);
		float w = score_w + U(48);
		float extra_h = 0;
		if (extra_lives > 0 || bombs > 0)
			extra_h += icon + U(10);
		if (special_on)
			extra_h += icon + U(10);
		const float h = U(18) + cap_l + U(12) + cap_n + U(18) + extra_h;
		char special_name[40] = "";
		if (special_on)
		{
			SDL_strlcpy(special_name, special[p->items.special].name, sizeof(special_name));
			for (int i = (int)strlen(special_name) - 1; i >= 0 && special_name[i] == ' '; --i)
				special_name[i] = '\0';
			w = SDL_max(w, icon + U(16) + text_w(FONT_SEMIBOLD, special_name, cap_l) + U(48));
		}
		w = SDL_max(w, (extra_lives > 0 ? 3 : 0) * icon + bombs * icon * 0.8f + U(80));
		const Box b = { safe.x + margin, safe.y + safe.h - margin - h, w, h };
		const int mark = rgpu_ui_mark();
		panel(b, U(12), PANEL_SOLID);
		float y = b.y + U(18);
		text(FONT_SEMIBOLD, "SCORE", b.x + U(24), y, cap_l, C_DIM, ALIGN_LEFT);
		y += cap_l + U(12);
		text_graded(FONT_BOLD, score, b.x + U(24), y, cap_n, C_GOLD_TOP, C_GOLD_BOTTOM, ALIGN_LEFT, true);
		y += cap_n + U(18);
		if (extra_lives > 0 || bombs > 0)
		{
			float x = b.x + U(24);
			if (extra_lives > 0)
			{
				// The ship's own little picture (the panel's), and how many.
				rgpu_ui_sprite(&spriteSheet9, 285, false, x, y, icon * 12 / 14.0f, icon, L.alpha);
				x += icon * 12 / 14.0f + U(8);
				char count[16];
				snprintf(count, sizeof(count), "x%d", extra_lives);
				text(FONT_SEMIBOLD, count, x, y + (icon - cap_l) / 2, cap_l, C_CREAM, ALIGN_LEFT);
				x += text_w(FONT_SEMIBOLD, count, cap_l) + U(22);
			}
			for (int i = 0; i < bombs; ++i)
			{
				rgpu_ui_sprite(&spriteSheet9, 304, false, x, y, icon * 12 / 14.0f, icon, L.alpha);
				x += icon * 0.8f;
			}
			y += icon + U(10);
		}
		if (special_on)
		{
			rgpu_ui_sprite(&spriteSheet10, special[p->items.special].itemgraphic, true, b.x + U(20), y, icon * 24 / 28.0f, icon, L.alpha);
			text(FONT_SEMIBOLD, special_name, b.x + U(24) + icon, y + (icon - cap_l) / 2, cap_l, C_TAN, ALIGN_LEFT);
		}
		fade_near_ship(mark, b, ship_x, ship_y, reach, &fades[2]);
	}

	// Top middle: the boss bars and the level's timer.
	{
		const int bars = (boss_bar[0].link_num != 0) + (boss_bar[1].link_num != 0);
		const bool timer = levelTimer && levelTimerCountdown > 0;
		if (bars > 0 || timer)
		{
			const float cap = cap_of(17, 9);
			// As wide as there is room for between the top corners' panels (the right one's mirrored).
			const float room = safe.w - 2 * (top_right_w + margin + U(24));
			const float fixed = (timer ? U(200) : 0) + (bars > 0 ? U(80) + bars * U(40) : 0);
			const float bar_w = SDL_max(SDL_min(U(bars == 2 ? 330 : 520), (room - fixed) / SDL_max(bars, 1)), U(120));
			const float bar_h = SDL_max(U(22), L.px * 7);
			float total = 0;
			if (timer)
				total += U(200);
			if (bars > 0)
				total += bars * (bar_w + U(40)) + U(80);
			const Box b = { safe.x + (safe.w - total) / 2, safe.y + margin, total, row_h + U(28) };
			const int mark = rgpu_ui_mark();
			panel(b, U(12), PANEL_SOLID);
			float x = b.x + U(22);
			const float y = b.y + U(14);
			if (timer)
			{
				char seconds[24];
				snprintf(seconds, sizeof(seconds), "%d.%d", levelTimerCountdown / 100, (levelTimerCountdown / 10) % 10);
				const bool urgent = levelTimerCountdown <= 200 && (levelTimerCountdown / 10) % 2 == 0;
				text(FONT_MEDIUM, "TIME", x, y + (row_h - cap) / 2, cap, C_DIM, ALIGN_LEFT);
				text(FONT_BOLD, seconds, x + U(160), y + (row_h - cap * 1.25f) / 2, cap * 1.25f,
				     urgent ? (Colour){ 1.0f, 0.45f, 0.35f, 1 } : C_CREAM, ALIGN_RIGHT);
				x += U(200);
			}
			if (bars > 0)
			{
				text(FONT_BOLD, "BOSS", x, y + (row_h - cap) / 2, cap, (Colour){ 1.0f, 0.55f, 0.45f, 1 }, ALIGN_LEFT);
				x += U(80);
				for (int i = 0; i < bars; ++i)
				{
					// (Flashing white as it is hit, as the game's.)
					const Colour hit = { 1.0f, 0.9f, 0.85f, 1 }, red = { 0.95f, 0.22f, 0.16f, 1 };
					bar((Box){ x, y + (row_h - bar_h) / 2, bar_w, bar_h }, boss_bar[i].armor / 255.0f,
					    boss_bar[i].color > 0 ? mix(red, hit, boss_bar[i].color / 6.0f) : red, true);
					x += bar_w + U(40);
				}
			}
			fade_near_ship(mark, b, ship_x, ship_y, reach, &fades[3]);
		}
	}

	// The level's name, for a few seconds as a level starts.
	{
		static char shown_level[11] = "";
		static Uint64 level_since = 0;
		if (strcmp(shown_level, levelName) != 0)
		{
			SDL_strlcpy(shown_level, levelName, sizeof(shown_level));
			level_since = SDL_GetTicks();
		}
		const float since = (SDL_GetTicks() - level_since) / 1000.0f;
		if (since < 4.0f && levelName[0] != '\0' && !view->menu_over)
		{
			const float alpha = SDL_clamp(SDL_min(since / 0.5f, (4.0f - since) / 1.0f), 0.0f, 1.0f);
			char name[sizeof(levelName)];
			SDL_strlcpy(name, levelName, sizeof(name));
			for (int i = (int)strlen(name) - 1; i >= 0 && name[i] == ' '; --i)
				name[i] = '\0';
			const float cap = cap_of(52, 18);
			const float w = text_w(FONT_BOLD, name, cap);
			const float y = safe.y + safe.h * 0.16f;
			L.alpha = alpha;
			text_graded(FONT_BOLD, name, safe.x + safe.w / 2, y, cap, C_GOLD_TOP, C_GOLD_BOTTOM, ALIGN_CENTRE, true);
			rule(safe.x + (safe.w - w * 1.3f) / 2, y + cap + U(22), w * 1.3f, with_alpha(C_RIM_TOP, 0.85f));
			L.alpha = 1;
		}
	}
}

/* --- The pointer --------------------------------------------------------------------------- */

float ui_pointer_points(void)
{
	return 24.0f * settings3d.ui_scale / 100.0f;
}

// The pointer's outline in a 24 x 24 box (the arrow: its tip at the top left).
static int pointer_shape(int shape, float (*pts)[2], float *hot)
{
	switch (shape)
	{
	case MOUSE_POINTER_NORMAL:
	{
		static const float arrow[][2] = { { 2, 1.5f }, { 2, 19.5f }, { 6.6f, 15.4f }, { 9.6f, 22.2f }, { 12.6f, 20.9f },
		                                  { 9.7f, 14.3f }, { 15.8f, 14.3f } };
		memcpy(pts, arrow, sizeof(arrow));
		hot[0] = 2;
		hot[1] = 1.5f;
		return (int)COUNTOF(arrow);
	}
	case MOUSE_POINTER_UP:
	case MOUSE_POINTER_DOWN:
	case MOUSE_POINTER_LEFT:
	case MOUSE_POINTER_RIGHT:
	{
		// A broad arrow pointing up, turned to its direction; its hot spot in the middle.
		static const float up[][2] = { { 12, 2 }, { 21, 11.5f }, { 15.5f, 11.5f }, { 15.5f, 21 }, { 8.5f, 21 }, { 8.5f, 11.5f },
		                               { 3, 11.5f } };
		const int n = (int)COUNTOF(up);
		for (int i = 0; i < n; ++i)
		{
			const float x = up[i][0] - 12, y = up[i][1] - 12;
			float rx = x, ry = y;
			if (shape == MOUSE_POINTER_DOWN)
				rx = -x, ry = -y;
			else if (shape == MOUSE_POINTER_LEFT)
				rx = y, ry = -x;
			else if (shape == MOUSE_POINTER_RIGHT)
				rx = -y, ry = x;
			pts[i][0] = rx + 12;
			pts[i][1] = ry + 12;
		}
		hot[0] = hot[1] = 12;
		return n;
	}
	default:
		return 0;
	}
}

// Signed distance from a point to a polygon (negative inside).
static float polygon_distance(const float (*pts)[2], int n, float x, float y)
{
	bool in = false;
	float best = 1e9f;
	for (int i = 0, j = n - 1; i < n; j = i++)
	{
		const float ax = pts[j][0], ay = pts[j][1], bx = pts[i][0], by = pts[i][1];
		if (((ay > y) != (by > y)) && x < (bx - ax) * (y - ay) / (by - ay) + ax)
			in = !in;
		const float ex = bx - ax, ey = by - ay;
		const float t = SDL_clamp(((x - ax) * ex + (y - ay) * ey) / SDL_max(ex * ex + ey * ey, 1e-6f), 0.0f, 1.0f);
		const float dx = x - (ax + ex * t), dy = y - (ay + ey * t);
		best = SDL_min(best, dx * dx + dy * dy);
	}
	const float d = sqrtf(best);
	return in ? -d : d;
}

bool ui_pointer_image(int shape, int size, Uint32 *rgba, int *hot_x, int *hot_y)
{
	float pts[16][2], hot[2];
	const int n = pointer_shape(shape, pts, hot);
	if (n == 0 || size <= 0)
		return false;
	const float k = size / 24.0f;  // pixels per box unit
	const float outline = 1.5f, shadow_dx = 1.2f, shadow_dy = 1.6f, shadow_blur = 2.4f;
	for (int py = 0; py < size; ++py)
		for (int px = 0; px < size; ++px)
		{
			const float x = (px + 0.5f) / k, y = (py + 0.5f) / k;
			const float d = polygon_distance((const float (*)[2])pts, n, x, y) * k;   // pixels
			const float ds = polygon_distance((const float (*)[2])pts, n, x - shadow_dx, y - shadow_dy) * k;
			const float cover = SDL_clamp(0.5f - d, 0.0f, 1.0f);
			const float body = SDL_clamp(0.5f - (d + outline * k), 0.0f, 1.0f);
			// Gold, lighter at the top; the outline dark brown.
			const float t = SDL_clamp(y / 22.0f, 0.0f, 1.0f);
			const float gold[3] = { 1.0f - 0.18f * t, 0.86f - 0.26f * t, 0.56f - 0.3f * t };
			const float edge[3] = { 0.12f, 0.08f, 0.05f };
			float c[3];
			for (int i = 0; i < 3; ++i)
				c[i] = edge[i] + (gold[i] - edge[i]) * body;
			const float shade = 0.4f * SDL_clamp(1.0f - (ds + 0.5f) / (shadow_blur * k), 0.0f, 1.0f) * (ds > -1 ? 1.0f : 1.0f);
			// The pointer over its shadow (straight alpha).
			const float a = cover + shade * (1 - cover);
			float out[3];
			for (int i = 0; i < 3; ++i)
				out[i] = a > 0 ? c[i] * cover / a : 0;
			const Uint8 rgba8[4] = { (Uint8)(SDL_clamp(out[0], 0.0f, 1.0f) * 255), (Uint8)(SDL_clamp(out[1], 0.0f, 1.0f) * 255),
			                         (Uint8)(SDL_clamp(out[2], 0.0f, 1.0f) * 255), (Uint8)(SDL_clamp(a, 0.0f, 1.0f) * 255) };
			memcpy(&rgba[py * size + px], rgba8, 4);
		}
	*hot_x = (int)lroundf(hot[0] * k);
	*hot_y = (int)lroundf(hot[1] * k);
	return true;
}

void ui_build_pointer(const UIView *view, float x, float y, int shape)
{
	// The system's pointer's own picture (hd_pointer_cursor, mouse.c), at the window's pixels.
	const float pixel = view->pixel > 0 ? view->pixel : 1;
	const int size = SDL_clamp((int)lroundf(ui_pointer_points() / pixel), 8, 128);
	static Uint32 rgba[128 * 128];
	static int made_shape = -1, made_size = 0, hot_x = 0, hot_y = 0;
	if (made_shape != shape || made_size != size)
	{
		if (!ui_pointer_image(shape, size, rgba, &hot_x, &hot_y))
			return;
		made_shape = shape;
		made_size = size;
	}
	rgpu_ui_image((Uint32)(shape * 1000 + size), rgba, size, size, x - hot_x * pixel, y - hot_y * pixel, size * pixel, size * pixel);
}
