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
#include "models3d.h"
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

// When the screen published now (or the store's page) was first published: its widgets ease in.
static Uint64 published_since = 0;

void ui_menu_publish(UIMenu *menu, const SDL_Surface *shown, const SDL_Surface *picture)
{
	if (!l3d_enabled || shown == NULL || shown->w != 320 || shown->h < 200)
		return;
	if (!have_published || published.kind != menu->kind || (menu->kind == UI_SCREEN_SHOP && published.shop.page != menu->shop.page))
		published_since = SDL_GetTicks();
	published = *menu;
	for (int y = 0; y < 200; ++y)
		memcpy(published_screen + y * 320, (const Uint8 *)shown->pixels + y * shown->pitch, 320);
	if (picture == NULL)
		picture = shown;
	static const TextRecord *texts[256];
	text_records_on(picture, texts, (int)COUNTOF(texts), published_picture);
	have_published = true;
}

void ui_menu_release(void)
{
	if (have_published && published.hold)
		have_published = false;
}

static UIDialog dialog_building;

UIDialog *ui_dialog_begin(void)
{
	memset(&dialog_building, 0, sizeof(dialog_building));
	dialog_building.on = true;
	dialog_building.selected = -1;
	return &dialog_building;
}

void ui_dialog_publish(const SDL_Surface *shown)
{
	if (!have_published || !l3d_enabled || shown == NULL || shown->w != 320 || shown->h < 200)
		return;
	// The screen under it as published, with the dialog over it, as the screen shows them now.
	published.dialog = dialog_building;
	for (int y = 0; y < 200; ++y)
		memcpy(published_screen + y * 320, (const Uint8 *)shown->pixels + y * shown->pitch, 320);
}

bool ui_screen_holds(const SDL_Surface *screen)
{
	if (!have_published || !ui_modern() || screen->w != 320 || screen->h < 200)
		return false;
	if (published.hold)
		return true;
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

bool ui_screen_over_level(void)
{
	return have_published && published.kind >= UI_SCREEN_LEVEL_MENU;
}

UISceneKind ui_screen_scene(void)
{
	return have_published && published.kind == UI_SCREEN_SHOP && !ui_screen_over_level() ? published.shop.scene : UI_SCENE_NONE;
}

bool ui_screen_whole_picture(void)
{
	return !have_published || published.kind < UI_SCREEN_SHOP;
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

bool ui_wheel_scrolls_text(void)
{
	return shown_last && have_published && !published.dialog.on && published.kind == UI_SCREEN_SHOP &&
	       published.shop.page == UI_SHOP_CUBE;
}

bool ui_wheel_moves(float y)
{
	// (Not on a data cube's text, which scrolls with it its own way, nor on a question.)
	if (!shown_last || !have_published || y == 0 || published.dialog.on)
		return false;
	if (published.kind == UI_SCREEN_SHOP && published.shop.page == UI_SHOP_CUBE)
		return false;
	return published.item_count > 1 || (published.kind == UI_SCREEN_SHOP && published.shop.tab_count > 1);
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

// A page's header: the page above it (small, spaced) and its name (gold, smaller if it is too wide
// for the panel); returns its height.
static float header(Box p, const char *crumb, const char *title)
{
	const float cap_c = CAP_SMALL();
	float cap_t = CAP_TITLE();
	const float room = p.w - U(80) - (published.kind == UI_SCREEN_SHOP && published.shop.credits >= 0 ? U(220) : 0);
	const float tw = title != NULL ? text_w(FONT_BOLD, title, cap_t) : 0;
	const float full = cap_t;
	if (tw > room && room > 0)
		cap_t = SDL_max(cap_t * room / tw, CAP_ITEM());
	const float drop = full - cap_t;  // (the header keeps its height)
	float y = p.y + U(30);
	if (crumb != NULL && crumb[0] != '\0')
	{
		text(FONT_SEMIBOLD, crumb, p.x + U(40), y, cap_c, C_DIM, ALIGN_LEFT);
		y += cap_c + U(14);
	}
	text_graded(FONT_BOLD, title, p.x + U(40), y + drop, cap_t, C_GOLD_TOP, C_GOLD_BOTTOM, ALIGN_LEFT, true);
	y += full + U(24);
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

/* --- The store's and the levels' screens: shared pieces ------------------------------------ */

// The pointer's window point while the mouse is in use (for hover), else false.
static bool hovered(Box b)
{
	float x, y;
	return mouse_pointer_window(&x, &y) && inside(b, x, y);
}

// 0-1 over `seconds` since the screen (or the store's page) was first published, eased out.
static float eased_in(float seconds)
{
	const float t = SDL_clamp((SDL_GetTicks() - published_since) / (1000.0f * seconds), 0.0f, 1.0f);
	return 1 - (1 - t) * (1 - t);
}

// A brass frame round a box whose inside shows what is under it (the 3D scene, a picture): a shadow
// outside, the rim, a dark line inside it and a soft shade along the inner edges.
static void frame_box(Box b, float c)
{
	b = (Box){ snap(b.x), snap(b.y), snap(b.w), snap(b.h) };
	const Colour dark = { 0, 0, 0, 0.42f }, clear = { 0, 0, 0, 0 };
	band(b, c, -U(26), dark, dark, clear, clear);
	const float w = SDL_max(U(3), L.px);
	rim(b, c, w, C_RIM_TOP, C_RIM_BOTTOM);
	const Box in = inset(b, w);
	const float ci = chamfer_grown(c, -w);
	band(in, ci, SDL_max(U(2), L.px), C_RIM_DARK, C_RIM_DARK, with_alpha(C_RIM_DARK, 0), with_alpha(C_RIM_DARK, 0));
	band(in, ci, U(34), (Colour){ 0, 0, 0, 0.34f }, (Colour){ 0, 0, 0, 0.42f }, clear, clear);
}

// An item's icon (a sprite of the game) fitted in a well.
static void item_icon(const UIItem *it, Box well, float alpha)
{
	if (it->icon_sheet == NULL && it->icon_table > 0)
	{
		const Box in = inset(well, well.w * 0.1f);
		rgpu_ui_table_sprite((unsigned int)it->icon_table, (unsigned int)it->icon_sprite, in.x, in.y, in.w, in.h, alpha * L.alpha);
		return;
	}
	if (it->icon_sheet == NULL)
		return;
	const float aw = it->icon_large ? 24.0f : 12.0f, ah = it->icon_large ? 28.0f : 14.0f;
	const float s = SDL_min(well.w * 0.84f / aw, well.h * 0.84f / ah);
	const float w = aw * s, h = ah * s;
	rgpu_ui_sprite(it->icon_sheet, (unsigned int)it->icon_sprite, it->icon_large, snap(well.x + (well.w - w) / 2),
	               snap(well.y + (well.h - h) / 2), w, h, alpha * L.alpha);
}

// A scrolled list: the first of `count` rows shown when `fits` do, keeping the selected one in view
// (each list keeps where it was scrolled to).
enum { LIST_ROWS, LIST_CARDS, LIST_FILES, LIST_PREVIEW, LIST_KINDS };
static int list_first(int list, int count, int selected, int fits)
{
	static int firsts[LIST_KINDS];
	int first = firsts[list];
	if (count <= fits || fits <= 0)
		first = 0;
	else
	{
		if (selected >= 0 && selected < first)
			first = selected;
		if (selected >= first + fits)
			first = selected - fits + 1;
		first = SDL_clamp(first, 0, count - fits);
	}
	firsts[list] = first;
	return first;
}

// A thin scroll bar: `count` rows of which `fits` show from `first`.
static void scroll_bar(Box track, int first, int fits, int count)
{
	if (count <= fits || count <= 0)
		return;
	panel(track, track.w * 0.5f, PANEL_WELL);
	const Box in = inset(track, SDL_max(U(2), L.px));
	const float h = SDL_max(in.h * fits / count, U(24));
	const float y = in.y + (in.h - h) * first / SDL_max(count - fits, 1);
	fill_octagon((Box){ in.x, y, in.w, h }, in.w * 0.4f, C_RIM_TOP, C_RIM_BOTTOM);
}

// A small pill of text (badges: "EQUIPPED").
static float badge(float x, float y, const char *s, Colour fill, Colour ink, int align)
{
	const float cap = CAP_KEY(), w = text_w(FONT_SEMIBOLD, s, cap) + cap * 1.6f, h = cap * 1.9f;
	if (align == ALIGN_RIGHT)
		x -= w;
	else if (align == ALIGN_CENTRE)
		x -= w / 2;
	const Box b = { x, y, w, h };
	fill_octagon(b, h * 0.3f, fill, mix(fill, (Colour){ 0, 0, 0, fill.a }, 0.25f));
	text_mid(FONT_SEMIBOLD, s, b, 0, cap, ink, ALIGN_CENTRE);
	return w;
}

static const Colour C_OWNED_FILL = RGBA(64, 120, 64, 0.92f);
static const Colour C_OWNED_INK = RGB(214, 246, 200);
static const Colour C_COST_HIGH = RGB(232, 120, 96);   // more than the credits
static const Colour C_GAIN = RGB(150, 226, 140);       // credits back
static const Colour C_LOSS = RGB(240, 150, 110);       // credits spent

// Short stat bars side by side: a label above each, the bar under it.
static void stat_bars(const UIItem *it, float x, float y, float w, float h, bool dim)
{
	const int n = SDL_min(it->stat_count, 2);
	if (n <= 0)
		return;
	const float gap = U(20), each = (w - gap * (n - 1)) / n, cap = CAP_KEY();
	const float bh = SDL_max(SDL_min(h - cap - U(9), U(12)), L.px * 5);
	for (int i = 0; i < n; ++i)
	{
		const float bx = x + i * (each + gap);
		text(FONT_SEMIBOLD, it->stat_label[i], bx, y, cap, dim ? C_FAINT : C_DIM, ALIGN_LEFT);
		bar((Box){ bx, y + cap + SDL_max(U(9), L.px * 3), each, bh }, it->stat[i],
		    dim ? (Colour){ 0.5f, 0.45f, 0.38f, 1 } : (Colour){ 0.95f, 0.76f, 0.42f, 1 }, true);
	}
}

// A number with its thousands apart, signed ("+1 200", "−750").
static void grouped(unsigned long value, char *out, size_t size);
static void signed_grouped(long value, char *out, size_t size)
{
	char digits[32];
	grouped((unsigned long)(value < 0 ? -value : value), digits, sizeof(digits));
	snprintf(out, size, "%s%s", value < 0 ? "-" : "+", digits);
}

// The key hints that fit: as many as fit in `width` from the first (the last ones go).
static void key_hints_fitted(const KeyHint *hints, int count, float x, float y, float width, int align)
{
	while (count > 1 && key_hints_width(hints, count) + 2 * U(16) > width)
		--count;
	key_hints(hints, count, x, y, align);
}

/* --- A question over the screen (the store's quit and save) ---------------------------------- */

static void build_dialog(const UIDialog *d)
{
	// Over a dimmed screen; only its buttons take the mouse.
	rect(L.window, (Colour){ 0, 0, 0, 0.45f }, (Colour){ 0, 0, 0, 0.55f });
	hit_count = 0;
	const float cap = CAP_ITEM(), small = CAP_SMALL();
	const float w = SDL_min(SDL_max(U(760), cap * 26), L.safe.w - U(80));
	const float text_lines = d->text[0] != '\0' ? 3 : 0;
	const float btn_h = SDL_max(U(64), cap * 2.6f);
	const float h = U(36) + CAP_TITLE() + U(30) + text_lines * small * 1.75f + (d->field_on ? cap * 2.4f + U(30) : 0) + btn_h + U(70);
	const Box p = { L.safe.x + (L.safe.w - w) / 2, (L.window.h - h - key_hints_height() - U(24)) / 2, w, h };
	panel(p, U(22), PANEL_GLASS);
	float y = p.y + U(36);
	// (The title smaller if it is wider than the panel.)
	float cap_t = CAP_TITLE();
	const float tw = text_w(FONT_BOLD, d->title, cap_t);
	if (tw > p.w - U(80))
		cap_t = SDL_max(cap_t * (p.w - U(80)) / tw, CAP_ITEM());
	text_graded(FONT_BOLD, d->title, p.x + p.w / 2, y + (CAP_TITLE() - cap_t) / 2, cap_t, C_GOLD_TOP, C_GOLD_BOTTOM, ALIGN_CENTRE, true);
	y += CAP_TITLE() + U(30);
	if (d->text[0] != '\0')
		y += text_wrapped(FONT_MEDIUM, d->text, p.x + U(50), y, p.w - U(100), small, C_TAN, ALIGN_CENTRE, 3);
	if (d->field_on)
	{
		const Box f = { p.x + U(50), y + U(6), p.w - U(100), cap * 2.4f };
		panel(f, U(10), PANEL_WELL);
		const float lw = text_w(FONT_SEMIBOLD, d->field_label, small);
		text_mid(FONT_SEMIBOLD, d->field_label, f, U(22), small, C_DIM, ALIGN_LEFT);
		const float fx = f.x + U(22) + lw + U(16);
		text(FONT_SEMIBOLD, d->field, fx, f.y + (f.h - cap) / 2, cap, C_CREAM, ALIGN_LEFT);
		if (d->caret)
		{
			const float cx = fx + text_w(FONT_SEMIBOLD, d->field, cap) + U(4);
			rect((Box){ cx, f.y + (f.h - cap * 1.2f) / 2, SDL_max(U(3), L.px), cap * 1.2f }, C_SEL_RIM, C_SEL_RIM);
		}
		y += f.h + U(30);
	}
	// The buttons.
	const float bw = SDL_min((p.w - U(150)) / 2, U(300));
	const Box yes = { p.x + p.w / 2 - U(20) - bw, p.y + p.h - U(36) - btn_h, bw, btn_h };
	const Box no = { p.x + p.w / 2 + U(20), yes.y, bw, btn_h };
	for (int i = 0; i < 2; ++i)
	{
		const Box b = i == 0 ? yes : no;
		const bool selected = d->selected == i;
		panel(b, U(12), selected ? PANEL_CARD : hovered(b) ? PANEL_BAR : PANEL_HOVER);
		text_mid(FONT_BOLD, i == 0 ? d->yes : d->no, b, 0, cap, selected ? C_CREAM : C_TAN, ALIGN_CENTRE);
		add_hit(b, i == 0 ? d->hit_yes : d->hit_no);
	}
	const KeyHint keys[] = { { KEY_LEFT_RIGHT, "", "Choose" }, { KEY_TEXT, "Enter", "Confirm" }, { KEY_TEXT, "Esc", "Cancel" } };
	const KeyHint typing[] = { { KEY_TEXT, "Enter", "Save" }, { KEY_TEXT, "Esc", "Cancel" } };
	if (d->field_on)
		key_hints(typing, (int)COUNTOF(typing), p.x + p.w / 2, p.y + p.h + U(22), ALIGN_CENTRE);
	else
		key_hints(keys, (int)COUNTOF(keys), p.x + p.w / 2, p.y + p.h + U(22), ALIGN_CENTRE);
}

/* --- The store -------------------------------------------------------------------------------- */

typedef struct
{
	Box left;    // the column of the ship (or the map, a face)
	Box pane;    // the scene's (or the picture's) box in it
	Box under;   // under it: gauges, the weapon's power (h 0: none)
	Box right;   // the page's panel
	Box centre;  // ship specs: the ship between the two panels
	float keys_y;
	float screen_box[4];  // the box of the screen the pane shows (screen pixels)
} ShopLayout;

#define SIM_BOX_X 8   // the weapon simulator's view on the screen (above its power controls)
#define SIM_BOX_Y 8
#define SIM_BOX_W 136
#define SIM_BOX_H 129

// The box at `aspect` (w / h) as large as fits in b, centred; its size whole window pixels per
// screen pixel when `screen_w` > 0 (sharp pictures).
static Box fit_box(Box b, float aspect, float screen_w)
{
	float w = b.w, h = b.w / aspect;
	if (h > b.h)
	{
		h = b.h;
		w = h * aspect;
	}
	if (screen_w > 0)
	{
		const float k = floorf(w / screen_w / L.px) * L.px;  // points per screen pixel, whole pixels
		if (k >= L.px && k * screen_w >= w * 0.7f)
		{
			w = k * screen_w;
			h = w / aspect;
		}
	}
	return (Box){ snap(b.x + (b.w - w) / 2), snap(b.y + (b.h - h) / 2), snap(w), snap(h) };
}

static ShopLayout shop_layout(const UIMenu *m)
{
	const UIShop *s = &m->shop;
	const Box S = L.safe;
	ShopLayout k;
	memset(&k, 0, sizeof(k));
	const float margin = SDL_max(U(54), S.w * 0.028f);
	k.keys_y = S.y + S.h - U(24) - key_hints_height();
	const float top = S.y + U(40), bottom = k.keys_y - U(24);
	const float gap = U(40);
	const float inner = S.w - 2 * margin - gap;
	if (s->page == UI_SHOP_SPECS)
	{
		// Two panels with the ship between them.
		const float side = SDL_max(inner * 0.27f, U(420));
		k.left = (Box){ S.x + margin, top, side, bottom - top };
		k.right = (Box){ S.x + S.w - margin - side, top, side, bottom - top };
		k.centre = (Box){ k.left.x + k.left.w + gap, top, k.right.x - gap - (k.left.x + k.left.w + gap), bottom - top };
		k.pane = k.centre;
		k.under = (Box){ k.centre.x, bottom, k.centre.w, 0 };
	}
	else
	{
		const float lw = inner * 0.44f;
		k.left = (Box){ S.x + margin, top, lw, bottom - top };
		k.right = (Box){ k.left.x + lw + gap, top, S.x + S.w - margin - (k.left.x + lw + gap), bottom - top };
		const bool under = s->scene != UI_SCENE_NONE || s->caption[0] != '\0';
		const float under_h = !under ? 0 : s->scene == UI_SCENE_SIM ? SDL_max(U(150), CAP_SMALL() * 2 + U(110)) : SDL_max(U(118), CAP_SMALL() + U(90));
		k.pane = (Box){ k.left.x, k.left.y, k.left.w, k.left.h - (under_h > 0 ? under_h + U(18) : 0) };
		k.under = (Box){ k.left.x, k.pane.y + k.pane.h + U(18), k.left.w, under_h };
	}
	// What the pane shows of the screen.
	if (s->scene == UI_SCENE_SIM)
	{
		k.pane = fit_box(k.pane, (float)SIM_BOX_W / SIM_BOX_H, SIM_BOX_W);
		const float sb[4] = { SIM_BOX_X, SIM_BOX_Y, SIM_BOX_W, SIM_BOX_H };
		memcpy(k.screen_box, sb, sizeof(sb));
	}
	else if (s->scene == UI_SCENE_SHIP)
	{
		// The illustration's box (151 x 141 at 3, 8) round its middle, a little larger, at the pane's aspect.
		// (In a narrow pane at least as wide as the ship and its sidekicks, the ship smaller.)
		const float aspect = k.pane.w / SDL_max(k.pane.h, 1.0f);
		float h = s->page == UI_SHOP_SPECS ? 150.0f : 158.0f, w = h * aspect;
		const float least = s->scene_w > 0 ? s->scene_w : 120.0f;
		if (w < least)
		{
			w = least;
			h = w / SDL_max(aspect, 0.1f);
		}
		const float sb[4] = { 78.5f - w / 2, 78.5f - h / 2 + (s->page == UI_SHOP_SPECS ? 0.0f : 2.0f), w, h };
		memcpy(k.screen_box, sb, sizeof(sb));
	}
	else if (s->picture_part.w > 0)
		k.pane = fit_box(k.pane, (float)s->picture_part.w / s->picture_part.h, (float)s->picture_part.w);
	return k;
}

bool ui_scene_pane(const UIView *view, float rect[4], float screen_box[4])
{
	// (Without models, the screen's own picture of the ship shows there: shop_left.)
	if (ui_screen_scene() == UI_SCENE_NONE || !m3d_enabled)
		return false;
	view_now = view;
	layout_begin(view, 1);
	const ShopLayout k = shop_layout(&published);
	rect[0] = k.pane.x;
	rect[1] = k.pane.y;
	rect[2] = k.pane.w;
	rect[3] = k.pane.h;
	memcpy(screen_box, k.screen_box, sizeof(k.screen_box));
	return true;
}

// The credits at the right of a panel's header; and what is left after the change chosen.
static void shop_credits(const UIShop *s, Box p)
{
	if (s->credits < 0)
		return;
	const float x = p.x + p.w - U(40), cap_v = CAP_HEAD(), cap_l = CAP_KEY();
	float y = p.y + U(30);
	char value[32];
	const bool after = s->credits_after >= 0 && s->credits_after != s->credits;
	grouped((unsigned long)(after ? s->credits_after : s->credits), value, sizeof(value));
	text(FONT_SEMIBOLD, after ? "CREDITS AFTER" : "CREDITS", x, y, cap_l, C_DIM, ALIGN_RIGHT);
	y += cap_l + U(10);
	text_graded(FONT_BOLD, value, x, y, cap_v, C_GOLD_TOP, C_GOLD_BOTTOM, ALIGN_RIGHT, true);
	if (after)
	{
		char delta[32];
		signed_grouped(s->credits_after - s->credits, delta, sizeof(delta));
		const float vw = text_w(FONT_BOLD, value, cap_v);
		text(FONT_SEMIBOLD, delta, x - vw - U(16), y + (cap_v - CAP_SMALL()), CAP_SMALL(), s->credits_after < s->credits ? C_LOSS : C_GAIN,
		     ALIGN_RIGHT);
	}
}

// A label and a gauge in a row (the ship's shield and armor, the generator's power).
static void labelled_gauge(Box row, float label_w, const char *label, float fraction, Colour c)
{
	const float cap = CAP_SMALL();
	text(FONT_SEMIBOLD, label, row.x, row.y + (row.h - cap) / 2, cap, C_DIM, ALIGN_LEFT);
	const float bh = SDL_max(SDL_min(row.h * 0.5f, U(20)), L.px * 5);
	bar((Box){ row.x + label_w, row.y + (row.h - bh) / 2, row.w - label_w, bh }, fraction, c, true);
}

// An arrow button (the weapon's power down or up).
static void arrow_button(Box b, bool right, bool enabled, SDL_Rect hit)
{
	panel(b, U(10), enabled && hovered(b) ? PANEL_BAR : PANEL_WELL);
	const float a = b.h * 0.22f, cx = b.x + b.w / 2, cy = b.y + b.h / 2;
	const Colour c = enabled ? C_SEL_RIM : C_FAINT;
	if (right)
		triangle(cx - a * 0.6f, cy - a, cx + a * 0.8f, cy, cx - a * 0.6f, cy + a, c);
	else
		triangle(cx + a * 0.6f, cy - a, cx + a * 0.6f, cy + a, cx - a * 0.8f, cy, c);
	add_hit(b, hit);
}

// Under the ship: its name and its shield and armor; under the simulator: the weapon's power and the
// generator's.
static void shop_under(const UIMenu *m, Box u)
{
	const UIShop *s = &m->shop;
	if (u.h <= 0)
		return;
	panel(u, U(14), PANEL_SOLID);
	const Box in = { u.x + U(26), u.y + U(16), u.w - U(52), u.h - U(32) };
	const float cap = CAP_SMALL(), label_w = SDL_max(U(150), cap * 7.5f);
	if (s->scene == UI_SCENE_SIM)
	{
		const float row = in.h / 2;
		float y = in.y;
		if (s->power_on)
		{
			// ◀ 600   POWER ●●○○○○○○○○○ 2   1 200 ▶
			const float bh = SDL_min(row - U(8), U(56)), bw = bh * 1.1f;
			arrow_button((Box){ in.x, y + (row - bh) / 2, bw, bh }, false, s->power_down, s->hit_down);
			arrow_button((Box){ in.x + in.w - bw, y + (row - bh) / 2, bw, bh }, true, s->power_up && s->power_afford, s->hit_up);
			char down[24] = "", up[24] = "";
			if (s->power_down)
				signed_grouped(s->cost_down, down, sizeof(down));
			if (s->power_up)
				signed_grouped(-s->cost_up, up, sizeof(up));
			const float cy = y + (row - cap) / 2;
			text(FONT_SEMIBOLD, down, in.x + bw + U(16), cy, cap, C_GAIN, ALIGN_LEFT);
			text(FONT_SEMIBOLD, up, in.x + in.w - bw - U(16), cy, cap, s->power_afford ? C_LOSS : C_COST_HIGH, ALIGN_RIGHT);
			// The pips in the middle (room for an overclocked 15).
			const int count = SDL_max(s->power_max, 11);
			const float room = in.w - 2 * bw - 2 * U(16) - 2 * SDL_max(text_w(FONT_SEMIBOLD, "+00 000", cap), U(110));
			const float pip = SDL_clamp(room / (count * 1.35f), L.px * 5, U(22)), pgap = pip * 0.35f;
			const float pw = count * pip + (count - 1) * pgap;
			const float px = in.x + (in.w - pw) / 2;
			char level[24];
			snprintf(level, sizeof(level), "POWER %d", s->power);
			text(FONT_BOLD, level, in.x + in.w / 2, y + (row - pip) / 2 - cap - U(8), CAP_KEY(), C_CREAM, ALIGN_CENTRE);
			pips(px, y + (row - pip) / 2 + U(6), SDL_min(count, 11), SDL_min(s->power, 11), pip, pgap, C_GREEN);
			if (count > 11)
				pips(px + 11 * (pip + pgap), y + (row - pip) / 2 + U(6), count - 11, SDL_max(s->power - 11, 0), pip, pgap,
				     (Colour){ 1.0f, 0.6f, 0.25f, 1 });
		}
		else if (s->mode[0] == '\0')
		{
			text_mid(FONT_SEMIBOLD, m->items[m->selected >= 0 ? m->selected : 0].label, (Box){ in.x, y, in.w, row }, 0, CAP_ITEM(), C_CREAM,
			         ALIGN_LEFT);
		}
		y += row;
		if (s->generator >= 0)
			labelled_gauge((Box){ in.x, y, in.w, row }, label_w, "GENERATOR", s->generator, (Colour){ 1.0f, 0.82f, 0.3f, 1 });
		if (s->mode[0] != '\0')
			text(FONT_MEDIUM, s->mode, in.x + in.w, y - cap * 0.2f, CAP_KEY(), C_DIM, ALIGN_RIGHT);
		return;
	}
	if (s->caption[0] != '\0' && (s->scene == UI_SCENE_NONE || !s->gauges))
	{
		text_mid(FONT_BOLD, s->caption, in, 0, CAP_ITEM(), C_CREAM, ALIGN_CENTRE);
		return;
	}
	// The ship's name and class, its shield and armor.
	const float name_cap = CAP_ITEM();
	text(FONT_BOLD, s->ship, in.x, in.y, name_cap, C_CREAM, ALIGN_LEFT);
	if (s->ship_class[0] != '\0')
		text(FONT_SEMIBOLD, s->ship_class, in.x + text_w(FONT_BOLD, s->ship, name_cap) + U(18), in.y + (name_cap - cap), cap, C_DIM, ALIGN_LEFT);
	if (s->gauges)
	{
		const float gy = in.y + name_cap + U(16), gh = in.y + in.h - gy;
		const float half = (in.w - U(30)) / 2;
		labelled_gauge((Box){ in.x, gy, half, gh }, SDL_max(U(110), cap * 5.4f), "SHIELD", s->shield, (Colour){ 0.35f, 0.75f, 1.0f, 1 });
		labelled_gauge((Box){ in.x + half + U(30), gy, half, gh }, SDL_max(U(110), cap * 5.4f), "ARMOR", s->armor, (Colour){ 1.0f, 0.55f, 0.25f, 1 });
	}
}

// The left column: the 3D scene's frame (the scene shows in it), or a part of the screen's picture.
static void shop_left(const UIMenu *m, const ShopLayout *k)
{
	const UIShop *s = &m->shop;
	if (s->scene != UI_SCENE_NONE && !m3d_enabled)
	{
		// Flat sprites (F4): the screen's own picture of the ship, or of the simulator, in the pane.
		const SDL_Rect part = s->scene == UI_SCENE_SIM ? (SDL_Rect){ SIM_BOX_X, SIM_BOX_Y, SIM_BOX_W, SIM_BOX_H } : (SDL_Rect){ 3, 8, 151, 141 };
		const Box p = fit_box(k->pane, (float)part.w / part.h, (float)part.w);
		rgpu_ui_picture((float)part.x, (float)part.y, (float)part.w, (float)part.h, p.x, p.y, p.w, p.h, L.alpha);
		frame_box(p, U(14));
	}
	else if (s->scene != UI_SCENE_NONE)
		frame_box(k->pane, U(20));
	else if (s->picture_part.w > 0)
	{
		const Box p = k->pane;
		const float pad = SDL_max(U(10), L.px * 2);
		panel(inset(p, -pad), U(20), PANEL_SOLID);
		rgpu_ui_picture((float)s->picture_part.x, (float)s->picture_part.y, (float)s->picture_part.w, (float)s->picture_part.h, p.x, p.y,
		                p.w, p.h, L.alpha);
		frame_box(p, U(14));
	}
	if (s->page != UI_SHOP_SPECS)
		shop_under(m, k->under);
}

// The help line at a panel's foot (a rule over it); returns its top.
static float shop_foot(Box p, const char *hint)
{
	const float foot_h = CAP_SMALL() * 1.75f * 2 + U(40);
	const float y = p.y + p.h - foot_h;
	rule(p.x + U(24), y, p.w - U(48), with_alpha(C_RIM_BOTTOM, 0.6f));
	if (hint != NULL && hint[0] != '\0')
		text_wrapped(FONT_MEDIUM, hint, p.x + U(40), y + U(20), p.w - U(80), CAP_SMALL(), C_DIM, ALIGN_LEFT, 2);
	return y;
}

// Rows of a menu (name left, value right) in a box, scrolled to the selected one.
static void shop_rows(const UIMenu *m, Box area)
{
	const float cap = CAP_ITEM();
	float row_h = SDL_max(U(56), cap * 2.15f);
	const float gap_h = U(22);
	int gaps = 0;
	for (int i = 0; i < m->item_count; ++i)
		gaps += m->items[i].gap_before;
	// Smaller rows before scrolling.
	if (m->item_count * row_h + gaps * gap_h > area.h)
		row_h = SDL_max((area.h - gaps * gap_h) / SDL_max(m->item_count, 1), cap * 1.7f);
	const int fits = SDL_max((int)((area.h - gaps * gap_h) / row_h + 0.01f), 1);  // (+: rows sized to fit exactly)
	const int first = list_first(LIST_ROWS, m->item_count, m->selected, fits);
	const bool scrolls = m->item_count > fits;
	float y = area.y;
	for (int i = first; i < m->item_count && i < first + fits; ++i)
	{
		const UIItem *item = &m->items[i];
		if (item->gap_before && i > first)
			y += gap_h;
		const Box r = { area.x, y, area.w - (scrolls ? U(26) : 0), row_h };
		const bool selected = i == m->selected;
		if (selected)
			panel(inset(r, U(2)), U(10), PANEL_CARD);
		else if (hovered(r) && !item->disabled)
			panel(inset(r, U(2)), U(10), PANEL_HOVER);
		const Colour c = item->disabled ? C_FAINT : selected ? C_CREAM : C_TAN;
		text_mid(FONT_SEMIBOLD, item->label, r, U(28), cap, c, ALIGN_LEFT);
		const float label_end = r.x + U(28) + text_w(FONT_SEMIBOLD, item->label, cap);
		const float value_w = SDL_min(U(360), r.w * 0.46f);
		const Box value = { r.x + r.w - value_w - U(18), r.y, value_w, r.h };
		Box track = { 0, 0, 0, 0 };
		if (item->kind == UI_ITEM_BAR)
		{
			const float bh = SDL_max(U(22), cap * 0.95f);
			track = (Box){ value.x + U(20), r.y + (r.h - bh) / 2, value.w - U(20) - U(80), bh };
			bar(track, item->bar, item->muted ? (Colour){ 0.45f, 0.42f, 0.38f, 1 } : (Colour){ 0.95f, 0.76f, 0.42f, 1 }, true);
			char percent[16];
			snprintf(percent, sizeof(percent), "%d%%", (int)lroundf(item->bar * 100));
			text(FONT_SEMIBOLD, item->muted ? "Off" : percent, value.x + value.w, r.y + (r.h - cap) / 2, cap, item->muted ? C_DIM : c,
			     ALIGN_RIGHT);
		}
		else if (item->capturing)
		{
			const bool on = (SDL_GetTicks() / 300) % 2 == 0;
			text(FONT_SEMIBOLD, "Press a key...", value.x + value.w, r.y + (r.h - cap) / 2, cap, on ? C_SEL_RIM : C_TAN, ALIGN_RIGHT);
		}
		else if (item->value[0] != '\0')
		{
			char fitted[64];
			fit_text(FONT_SEMIBOLD, item->value, cap, SDL_max(r.x + r.w - U(18) - label_end - U(30), U(60)), fitted, sizeof(fitted));
			text(FONT_SEMIBOLD, fitted, value.x + value.w, r.y + (r.h - cap) / 2, cap, item->disabled ? C_FAINT : selected ? C_CREAM : C_SUB,
			     ALIGN_RIGHT);
		}
		if (item->cubes > 0)
		{
			// The data cubes found, as icons after the name.
			const float size = SDL_min(r.h * 0.62f, U(40));
			float x = label_end + U(28);
			for (int c2 = 0; c2 < item->cubes && x + size < r.x + r.w - U(18); ++c2, x += size + U(8))
				rgpu_ui_table_sprite(OPTION_SHAPES, 34, x, r.y + (r.h - size) / 2, size, size, L.alpha);
		}
		if (item->hit_value.w > 0 && track.w > 0)
		{
			// (The level set where the bar is clicked, as on the original's.)
			add_hit((Box){ r.x, r.y, track.x - r.x, r.h }, item->hit);
			add_hit((Box){ track.x, r.y, track.w, r.h }, item->hit_value);
		}
		else if (item->hit_value.w > 0)
		{
			add_hit((Box){ r.x, r.y, value.x - r.x, r.h }, item->hit);
			add_hit((Box){ value.x, r.y, r.x + r.w - value.x, r.h }, item->hit_value);
		}
		else
			add_hit(r, item->hit);
		y += row_h;
	}
	if (scrolls)
		scroll_bar((Box){ area.x + area.w - U(12), area.y, U(10), y - area.y }, first, fits, m->item_count);
}

// The saved games' slots (load, save): the name (or the slot's), the level and episode at the right.
static void shop_files(const UIMenu *m, Box area)
{
	const float cap = CAP_ITEM(), small = CAP_SMALL();
	float row_h = SDL_max(U(54), cap * 2.1f);
	if (m->item_count * row_h > area.h)
		row_h = SDL_max(area.h / SDL_max(m->item_count, 1), cap * 1.6f);
	const int fits = SDL_max((int)(area.h / row_h + 0.01f), 1);
	const int first = list_first(LIST_FILES, m->item_count, m->selected, fits);
	const bool scrolls = m->item_count > fits;
	for (int i = first; i < m->item_count && i < first + fits; ++i)
	{
		const UIItem *it = &m->items[i];
		const Box r = { area.x, area.y + (i - first) * row_h, area.w - (scrolls ? U(26) : 0), row_h };
		const bool selected = i == m->selected;
		if (selected)
			panel(inset(r, U(2)), U(10), PANEL_CARD);
		else if (hovered(r) && !it->disabled)
			panel(inset(r, U(2)), U(10), PANEL_HOVER);
		const bool slot = i + 1 < m->item_count;
		float x = r.x + U(24);
		if (slot)
		{
			char number[8];
			snprintf(number, sizeof(number), "%02d", i + 1);
			text(FONT_SEMIBOLD, number, x, r.y + (r.h - small) / 2, small, C_FAINT, ALIGN_LEFT);
			x += text_w(FONT_SEMIBOLD, "00", small) + U(22);
		}
		const bool saved = it->value[0] != '\0';
		const char *name = it->label[0] != '\0' ? it->label : saved ? "Unnamed" : "";
		const Colour c = it->disabled ? C_FAINT : selected ? C_CREAM : saved || !slot ? C_TAN : C_DIM;
		char fitted[64];
		fit_text(FONT_SEMIBOLD, name, cap, r.w * 0.5f, fitted, sizeof(fitted));
		text(selected ? FONT_BOLD : FONT_SEMIBOLD, fitted, x, r.y + (r.h - cap) / 2, cap, c, ALIGN_LEFT);
		if (saved)
		{
			float right = r.x + r.w - U(22);
			if (it->value2[0] != '\0')
				right -= badge(right, r.y + (r.h - CAP_KEY() * 1.9f) / 2, it->value2, (Colour){ 0.32f, 0.24f, 0.16f, 0.9f }, C_TAN, ALIGN_RIGHT) + U(16);
			text(FONT_SEMIBOLD, it->value, right, r.y + (r.h - small) / 2, small, selected ? C_SUB : C_DIM, ALIGN_RIGHT);
		}
		add_hit(r, it->hit);
	}
	if (scrolls)
		scroll_bar((Box){ area.x + area.w - U(12), area.y, U(10), fits * row_h }, first, fits, m->item_count);
}

// The store's card for a choice: its icon, name and stats; at the right its cost, or that the ship
// has it.
static void shop_card(Box r, const UIItem *it, bool selected, bool preview)
{
	const bool hover = !selected && !preview && hovered(r);
	panel(r, U(10), selected ? PANEL_CARD : hover ? PANEL_BAR : PANEL_HOVER);
	const float cap = CAP_ITEM(), small = CAP_SMALL();
	float x = r.x + U(18);
	if (it->icon_sheet != NULL || it->icon_table > 0 || it->value[0] != '\0' || it->owned)
	{
		const float iw = r.h - U(20);
		const Box well = { x, r.y + U(10), iw, iw };
		panel(well, U(8), PANEL_WELL);
		item_icon(it, well, preview && !it->owned ? 0.7f : 1.0f);
		x += iw + U(20);
	}
	const bool dim = it->unaffordable || preview;
	const Colour tc = it->disabled ? C_FAINT : selected ? C_CREAM : it->unaffordable ? C_DIM : C_TAN;
	// The right: the cost (or "equipped").
	float right_w = 0;
	if (it->owned)
		right_w = badge(r.x + r.w - U(20), r.y + (r.h - CAP_KEY() * 1.9f) / 2, "EQUIPPED", C_OWNED_FILL, C_OWNED_INK, ALIGN_RIGHT) + U(24);
	else if (it->value[0] != '\0')
	{
		const float vc = cap * 1.05f;
		text(FONT_SEMIBOLD, "COST", r.x + r.w - U(22), r.y + (r.h - vc - CAP_KEY() - U(6)) / 2, CAP_KEY(), C_DIM, ALIGN_RIGHT);
		text(FONT_BOLD, it->value, r.x + r.w - U(22), r.y + (r.h - vc - CAP_KEY() - U(6)) / 2 + CAP_KEY() + U(6), vc,
		     it->unaffordable ? C_COST_HIGH : selected ? C_GOLD_TOP : mix(C_GOLD_TOP, C_TAN, 0.3f), ALIGN_RIGHT);
		right_w = SDL_max(text_w(FONT_BOLD, it->value, vc), text_w(FONT_SEMIBOLD, "COST", CAP_KEY())) + U(40);
	}
	const float text_wd = r.x + r.w - right_w - U(18) - x;
	const bool stats = it->stat_count > 0 && r.h >= cap + small * 2.2f + U(26);
	const float total = stats ? cap + U(14) + CAP_KEY() + U(21) : cap;
	const float y = r.y + (r.h - total) / 2;
	char fitted[96];
	fit_text(FONT_SEMIBOLD, it->label, cap, text_wd, fitted, sizeof(fitted));
	text(selected ? FONT_BOLD : FONT_SEMIBOLD, fitted, x, y, cap, tc, ALIGN_LEFT);
	if (stats)
		stat_bars(it, x, y + cap + U(14), SDL_min(text_wd, U(420)), CAP_KEY() + U(21), dim && !selected);
	if (it->chosen && !it->owned && !preview)
		badge(x + text_w(selected ? FONT_BOLD : FONT_SEMIBOLD, fitted, cap) + U(16), y + (cap - CAP_KEY() * 1.9f) / 2, "ON SHIP",
		      (Colour){ 0.5f, 0.38f, 0.2f, 0.9f }, C_CREAM, ALIGN_LEFT);
}

// The parts as tabs over a box: returns the height taken.
static float shop_tabs(const UIShop *s, Box area, bool live)
{
	if (s->tab_count <= 0)
		return 0;
	float cap = CAP_SMALL(), pad = cap * 1.0f;
	const float gap = U(8);
	float total = 0;
	for (int pass = 0; pass < 3; ++pass)
	{
		total = 0;
		for (int i = 0; i < s->tab_count; ++i)
			total += text_w(FONT_SEMIBOLD, s->tab[i], cap) + 2 * pad;
		total += gap * (s->tab_count - 1);
		if (total <= area.w)
			break;
		pad *= 0.7f;
		if (pass == 1)
			cap = SDL_max(cap * area.w / total, CAP_KEY());
	}
	const float h = SDL_max(cap * 2.5f, U(44));
	// Spread over the width when there is room.
	const float extra = total < area.w ? (area.w - total) / s->tab_count : 0;
	float x = area.x;
	for (int i = 0; i < s->tab_count; ++i)
	{
		const float w = text_w(FONT_SEMIBOLD, s->tab[i], cap) + 2 * pad + SDL_min(extra, U(30));
		const Box t = { x, area.y, w, h };
		const bool selected = i == s->tab_selected;
		panel(t, h * 0.28f, selected ? PANEL_CARD : live && hovered(t) ? PANEL_BAR : PANEL_HOVER);
		text_mid(FONT_SEMIBOLD, s->tab[i], t, 0, cap, selected ? C_CREAM : live ? C_TAN : C_DIM, ALIGN_CENTRE);
		if (live)
			add_hit(t, s->tab_hit[i]);
		x += w + gap;
	}
	return h;
}

// Cards in a box (a part's choices), scrolled to the selected one; preview: the parts' list's view of
// them (not chosen from here).
static void shop_cards(const UIMenu *m, Box area, bool preview)
{
	const float cap = CAP_ITEM(), small = CAP_SMALL();
	const float gap = U(10);
	float card_h = SDL_max(U(preview ? 78 : 92), cap + small * 2.2f + U(30));
	const int count = m->item_count;
	if (count * (card_h + gap) > area.h)
		card_h = SDL_max(area.h / SDL_max(count, 1) - gap, SDL_max(U(70), cap * 2.6f));
	const int fits = SDL_max((int)((area.h + gap) / (card_h + gap) + 0.01f), 1);
	const int selected = preview ? -1 : m->selected;
	int owned = 0;
	for (int i = 0; i < count; ++i)
		if (m->items[i].owned)
			owned = i;
	const int first = list_first(preview ? LIST_PREVIEW : LIST_CARDS, count, preview ? owned : selected, fits);
	const bool scrolls = count > fits;
	for (int i = first; i < count && i < first + fits; ++i)
	{
		const UIItem *it = &m->items[i];
		const Box r = { area.x, area.y + (i - first) * (card_h + gap), area.w - (scrolls ? U(26) : 0), card_h };
		if (it->icon_sheet == NULL && it->icon_table <= 0 && it->value[0] == '\0' && !it->owned && it->stat_count == 0)
		{
			// Done (or None): a plain row.
			const bool sel = i == selected;
			if (sel)
				panel(inset(r, U(2)), U(10), PANEL_CARD);
			else if (!preview && hovered(r))
				panel(inset(r, U(2)), U(10), PANEL_HOVER);
			text_mid(sel ? FONT_BOLD : FONT_SEMIBOLD, it->label, r, U(28), cap, sel ? C_CREAM : preview ? C_DIM : C_TAN, ALIGN_LEFT);
		}
		else
			shop_card(r, it, i == selected, preview);
		if (!preview)
			add_hit(r, it->hit);
	}
	if (scrolls)
	{
		const float shown_h = SDL_min(fits, count - first) * (card_h + gap) - gap;
		scroll_bar((Box){ area.x + area.w - U(12), area.y, U(10), shown_h }, first, fits, count);
	}
}

// A data cube read: its text in the panel, scrolled as the original scrolls it.
static void shop_cube_text(const UIMenu *m, Box area)
{
	const UIShop *s = &m->shop;
	const float cap = CAP_SMALL() * 1.12f, line_h = cap * 1.75f;
	// The original's lines joined into paragraphs (an empty line ends one), wrapped to the panel.
	static char wrapped[UI_CUBE_LINES * 2][160];
	int count = 0;
	char paragraph[2048];
	size_t n = 0;
	for (int i = 0; i <= s->line_count && count < (int)COUNTOF(wrapped) - 1; ++i)
	{
		const bool end = i == s->line_count || s->lines[i][0] == '\0';
		if (!end)
		{
			const char *l = s->lines[i];
			while (*l == ' ')
				++l;
			if (n > 0 && n + 1 < sizeof(paragraph))
				paragraph[n++] = ' ';
			for (; *l != '\0' && n + 1 < sizeof(paragraph); ++l)
				paragraph[n++] = *l;
			paragraph[n] = '\0';
			continue;
		}
		if (n > 0)
		{
			// Wrap the paragraph.
			const char *p = paragraph;
			while (*p != '\0' && count < (int)COUNTOF(wrapped) - 1)
			{
				while (*p == ' ')
					++p;
				size_t best = 0, k = 0;
				for (;;)
				{
					while (p[k] != '\0' && p[k] != ' ')
						++k;
					char trial[160];
					const size_t len = SDL_min(k, sizeof(trial) - 1);
					memcpy(trial, p, len);
					trial[len] = '\0';
					if (text_w(FONT_MEDIUM, trial, cap) > area.w && best > 0)
						break;
					best = len;
					if (p[k] == '\0' || len >= sizeof(trial) - 1)
						break;
					++k;
				}
				memcpy(wrapped[count], p, best);
				wrapped[count][best] = '\0';
				++count;
				p += best;
			}
			n = 0;
			paragraph[0] = '\0';
			if (i < s->line_count)
				wrapped[count++][0] = '\0';  // the gap between paragraphs
		}
	}
	const int fits = SDL_max((int)(area.h / line_h), 1);
	// Scrolled as far as the original is through its own lines.
	const float original_range = SDL_max(s->line_count - 10.0f, 0.0f);
	const float fraction = original_range > 0 ? SDL_clamp(s->line_first / original_range, 0.0f, 1.0f) : 0;
	const float first = fraction * SDL_max(count - fits, 0);
	const int first_line = (int)floorf(first);
	const float offset = (first - first_line) * line_h;
	for (int i = first_line; i < count && i <= first_line + fits; ++i)
	{
		const float y = area.y + (i - first_line) * line_h - offset;
		if (y < area.y - line_h * 0.2f || y + cap > area.y + area.h)
			continue;
		text(FONT_MEDIUM, wrapped[i], area.x, y, cap, C_TAN, ALIGN_LEFT);
	}
	if (count > fits)
		scroll_bar((Box){ area.x + area.w + U(14), area.y, U(10), area.h }, first_line, fits, count);
}

static void build_shop(const UIMenu *m)
{
	const UIShop *s = &m->shop;
	const ShopLayout k = shop_layout(m);
	const float in_t = eased_in(0.22f);
	shop_left(m, &k);

	// Ship specs: two panels round the ship.
	if (s->page == UI_SHOP_SPECS)
	{
		const Box a = k.left, b = k.right;
		const float small = CAP_SMALL();
		panel(a, U(22), PANEL_GLASS);
		panel(b, U(22), PANEL_GLASS);
		float y = a.y + header(a, "SHIP SPECS", s->ship);
		if (s->ship_class[0] != '\0')
		{
			text(FONT_SEMIBOLD, s->ship_class, a.x + U(40), y - U(4), CAP_ITEM(), C_SUB, ALIGN_LEFT);
			y += CAP_ITEM() + U(22);
		}
		y += text_wrapped(FONT_MEDIUM, s->specs[0], a.x + U(40), y, a.w - U(80), small, C_TAN, ALIGN_LEFT, 12) + U(26);
		// The ship's armor and speed.
		for (int i = 0; i < m->item_count && y + U(60) < a.y + a.h - U(30); ++i)
		{
			const UIItem *it = &m->items[i];
			if (it->kind != UI_ITEM_BAR)
				continue;
			const Box row = { a.x + U(40), y, a.w - U(80), SDL_max(U(52), small * 2.8f) };
			labelled_gauge(row, SDL_max(U(140), small * 6.5f), it->label, it->bar, (Colour){ 0.95f, 0.76f, 0.42f, 1 });
			y += row.h;
		}
		// The overview and what it carries.
		float yb = b.y + header(b, "", "Overview");
		yb += text_wrapped(FONT_MEDIUM, s->specs[1], b.x + U(40), yb, b.w - U(80), small, C_TAN, ALIGN_LEFT, 10) + U(24);
		rule(b.x + U(24), yb, b.w - U(48), with_alpha(C_RIM_BOTTOM, 0.6f));
		yb += U(22);
		text(FONT_SEMIBOLD, "LOADOUT", b.x + U(40), yb, CAP_KEY(), C_DIM, ALIGN_LEFT);
		yb += CAP_KEY() + U(14);
		for (int i = 0; i < m->item_count && yb + U(50) < b.y + b.h - U(24); ++i)
		{
			const UIItem *it = &m->items[i];
			if (it->kind == UI_ITEM_BAR)
				continue;
			const float rh = SDL_max(U(58), small * 3.2f);
			const Box row = { b.x + U(40), yb, b.w - U(80), rh };
			text(FONT_SEMIBOLD, it->label, row.x, row.y + U(6), CAP_KEY(), C_DIM, ALIGN_LEFT);
			char fitted[64];
			fit_text(FONT_SEMIBOLD, it->value, small, row.w, fitted, sizeof(fitted));
			text(FONT_SEMIBOLD, fitted, row.x, row.y + U(6) + CAP_KEY() + U(8), small, it->value[0] == '-' ? C_FAINT : C_CREAM, ALIGN_LEFT);
			if (it->pips > 0)
			{
				const float pip = SDL_max(U(12), L.px * 4), pg = pip * 0.35f;
				pips(row.x + row.w - (it->pips * (pip + pg) - pg), row.y + U(6), it->pips, it->pips_on, pip, pg, C_GREEN);
			}
			yb += rh;
		}
		const KeyHint keys[] = { { KEY_TEXT, "Any key", "Back" } };
		key_hints(keys, 1, k.centre.x + k.centre.w / 2, k.keys_y, ALIGN_CENTRE);
		if (m->dialog.on)
			build_dialog(&m->dialog);
		return;
	}

	// The page's panel.
	const Box p = k.right;
	panel(p, U(22), PANEL_GLASS);
	const float top = p.y + header(p, m->crumb, m->title);
	shop_credits(s, p);
	const float foot = shop_foot(p, m->hint);
	Box area = { p.x + U(20), top + U(4), p.w - U(40), foot - U(16) - (top + U(4)) };
	// (Eased in: the panel's content slides up a little as a page opens.)
	area.y += (1 - in_t) * U(14);
	switch (s->page)
	{
	case UI_SHOP_UPGRADE:
	{
		const float th = shop_tabs(s, (Box){ area.x + U(4), area.y, area.w - U(8), 0 }, true);
		Box list = { area.x, area.y + th + U(22), area.w, area.h - th - U(22) };
		// "Done" at the foot of the list, the selected part's choices above it.
		const float done_h = SDL_max(U(56), CAP_ITEM() * 2.15f);
		const Box done = { list.x, list.y + list.h - done_h, list.w, done_h };
		list.h -= done_h + U(16);
		text(FONT_SEMIBOLD, "CHOICES", list.x + U(4), list.y, CAP_KEY(), C_DIM, ALIGN_LEFT);
		list.y += CAP_KEY() + U(14);
		list.h -= CAP_KEY() + U(14);
		shop_cards(m, list, true);
		const bool done_selected = s->tab_selected < 0;
		if (done_selected)
			panel(inset(done, U(2)), U(10), PANEL_CARD);
		else if (hovered(done))
			panel(inset(done, U(2)), U(10), PANEL_HOVER);
		text_mid(done_selected ? FONT_BOLD : FONT_SEMIBOLD, s->done, done, U(28), CAP_ITEM(), done_selected ? C_CREAM : C_TAN, ALIGN_LEFT);
		add_hit(done, s->hit_done);
		break;
	}
	case UI_SHOP_ITEMS:
	{
		const float th = shop_tabs(s, (Box){ area.x + U(4), area.y, area.w - U(8), 0 }, false);
		shop_cards(m, (Box){ area.x, area.y + th + U(22), area.w, area.h - th - U(22) }, false);
		break;
	}
	case UI_SHOP_CUBE:
	{
		const Box text_box = { area.x + U(20), area.y + U(10), area.w - U(70), area.h - U(90) };
		shop_cube_text(m, text_box);
		// The original takes the mouse on its text's upper and lower half (scrolling) and on Done.
		add_hit((Box){ text_box.x, text_box.y, text_box.w, text_box.h / 2 }, (SDL_Rect){ 166, 49, 130, 50 });
		add_hit((Box){ text_box.x, text_box.y + text_box.h / 2, text_box.w, text_box.h / 2 }, (SDL_Rect){ 166, 102, 130, 50 });
		const float bh = SDL_max(U(54), CAP_ITEM() * 2.1f), bw = SDL_max(U(200), text_w(FONT_BOLD, s->done, CAP_ITEM()) + U(80));
		const Box done = { area.x + area.w - bw, area.y + area.h - bh, bw, bh };
		panel(done, U(10), hovered(done) ? PANEL_CARD : PANEL_BAR);
		text_mid(FONT_BOLD, s->done, done, 0, CAP_ITEM(), C_CREAM, ALIGN_CENTRE);
		add_hit(done, s->hit_done);
		char read[48];
		snprintf(read, sizeof(read), "%d%% READ", s->percent);
		const float rw = SDL_min(area.w - bw - U(60), U(360));
		text(FONT_SEMIBOLD, read, area.x + U(20), done.y + U(2), CAP_KEY(), C_DIM, ALIGN_LEFT);
		bar((Box){ area.x + U(20), done.y + CAP_KEY() + U(14), rw, SDL_max(U(12), L.px * 4) }, s->percent / 100.0f, C_GOLD_BOTTOM, true);
		break;
	}
	default:
		if (s->note[0] != '\0')
		{
			const float nh = text_wrapped(FONT_MEDIUM, s->note, area.x + U(28), area.y + U(10), area.w - U(56), CAP_SMALL(), C_SUB, ALIGN_LEFT, 3);
			area.y += nh + U(30);
			area.h -= nh + U(30);
		}
		if (s->page == UI_SHOP_CUBES || s->page == UI_SHOP_MAP)
			shop_cards(m, area, false);
		else if (s->page == UI_SHOP_FILES)
			shop_files(m, area);
		else
			shop_rows(m, area);
		break;
	}

	// The keys.
	{
		const bool power = s->page == UI_SHOP_ITEMS && s->power_on;
		const bool turns = m->selected >= 0 && m->selected < m->item_count && m->items[m->selected].kind == UI_ITEM_BAR;
		const bool cube = s->page == UI_SHOP_CUBE;
		KeyHint keys[5];
		int n = 0;
		if (cube)
		{
			keys[n++] = (KeyHint){ KEY_UP_DOWN, "", "Scroll" };
			keys[n++] = (KeyHint){ KEY_TEXT, "Esc", "Back" };
		}
		else
		{
			keys[n++] = (KeyHint){ KEY_UP_DOWN, "", "Select" };
			if (power)
				keys[n++] = (KeyHint){ KEY_LEFT_RIGHT, "", "Power" };
			else if (turns)
				keys[n++] = (KeyHint){ KEY_LEFT_RIGHT, "", "Volume" };
			keys[n++] = (KeyHint){ KEY_TEXT, "Enter", s->page == UI_SHOP_ITEMS ? "Choose" : "Confirm" };
			keys[n++] = (KeyHint){ KEY_TEXT, "Esc", "Back" };
			keys[n++] = (KeyHint){ KEY_TEXT, "F1", "Help" };
		}
		key_hints_fitted(keys, n, p.x + p.w / 2, k.keys_y, L.safe.x + L.safe.w - p.x - U(20), ALIGN_CENTRE);
	}

	// A purchase's note (as the page goes back to the parts with fewer or more credits).
	{
		static long credits_before = -1;
		static int page_before = -1;
		static Uint64 toast_at = 0;
		static char toast[96];
		if (page_before == UI_SHOP_ITEMS && s->page == UI_SHOP_UPGRADE && credits_before >= 0 && s->credits >= 0 &&
		    s->credits != credits_before)
		{
			char delta[32];
			signed_grouped(s->credits - credits_before, delta, sizeof(delta));
			int owned = -1;
			for (int i = 0; i < m->item_count; ++i)
				if (m->items[i].owned)
					owned = i;
			snprintf(toast, sizeof(toast), "%s %s   %s", s->credits < credits_before ? "Bought" : "Fitted",
			         owned >= 0 ? m->items[owned].label : "", delta);
			toast_at = SDL_GetTicks();
		}
		if (s->page == UI_SHOP_ITEMS)
			credits_before = s->credits;
		else if (s->page != UI_SHOP_UPGRADE)
			credits_before = -1;
		page_before = (int)s->page;
		const float age = (SDL_GetTicks() - toast_at) / 1000.0f;
		if (toast_at > 0 && age < 2.4f)
		{
			const float a = SDL_clamp(SDL_min(age / 0.15f, (2.4f - age) / 0.5f), 0.0f, 1.0f);
			const float saved = L.alpha;
			L.alpha *= a;
			const float cap = CAP_ITEM(), w = text_w(FONT_SEMIBOLD, toast, cap) + U(80), h = cap * 2.6f;
			const Box t = { p.x + (p.w - w) / 2, p.y + p.h - h - U(30) + (1 - a) * U(12), w, h };
			panel(t, U(12), PANEL_CARD);
			text_mid(FONT_SEMIBOLD, toast, t, 0, cap, C_CREAM, ALIGN_CENTRE);
			L.alpha = saved;
		}
	}

	if (m->dialog.on)
		build_dialog(&m->dialog);
}

/* --- Over a level: the in-game options, help, pause, the level's end --------------------------- */

// The scene a little darker under a screen over it.
static void level_dim(float top, float bottom)
{
	rect(L.window, (Colour){ 0, 0, 0, top }, (Colour){ 0, 0, 0, bottom });
}

// The in-game options (and their 3D page): rows as setup's, centred over the playfield.
static void build_level_menu(const UIMenu *m)
{
	level_dim(0.32f, 0.42f);
	const float cap = CAP_ITEM();
	const float row_h = SDL_max(U(52), cap * 2.1f);
	const float w = SDL_min(SDL_max(U(860), cap * 28), L.safe.w - U(96));
	const float head_h = U(30) + (m->crumb[0] != '\0' ? CAP_SMALL() + U(14) : 0) + CAP_TITLE() + U(24) + U(18);
	const float foot_h = CAP_SMALL() * 1.75f * 2 + U(44);
	const float keys_h = key_hints_height() + U(28);
	const float room = L.window.h - U(48) - keys_h;
	float rh = row_h, h = head_h + m->item_count * rh + U(12) + foot_h;
	if (h > room)
	{
		rh = SDL_max((room - head_h - foot_h - U(12)) / SDL_max(m->item_count, 1), cap * 1.55f);
		h = head_h + m->item_count * rh + U(12) + foot_h;
	}
	// (No easing in: the menus over a level are shown again only on input.)
	const Box p = { L.safe.x + (L.safe.w - w) / 2, SDL_max((L.window.h - h - keys_h) / 2, U(24)), w, SDL_min(h, room) };
	panel(p, U(22), PANEL_GLASS);
	const float top = p.y + header(p, m->crumb, m->title);
	const int fits = SDL_max((int)((p.y + p.h - foot_h - U(12) - top) / rh + 0.01f), 1);
	const int first = list_first(LIST_ROWS, m->item_count, m->selected, fits);
	for (int i = first; i < m->item_count && i < first + fits; ++i)
	{
		const UIItem *item = &m->items[i];
		const Box r = { p.x + U(16), top + (i - first) * rh, p.w - U(32), rh };
		const bool selected = i == m->selected;
		if (selected)
			panel(inset(r, U(2)), U(10), PANEL_CARD);
		const Colour c = item->disabled ? C_FAINT : selected ? C_CREAM : C_TAN;
		text_mid(FONT_SEMIBOLD, item->label, r, U(28), cap, c, ALIGN_LEFT);
		const float value_w = SDL_min(U(380), r.w * 0.5f);
		const Box value = { r.x + r.w - value_w - U(14), r.y, value_w, r.h };
		if (item->kind == UI_ITEM_CHOICE)
		{
			// ◀ value ▶ (turned with Left / Right)
			const float a = cap * 0.36f;
			const float vx = value.x + value.w - U(10);
			const Colour vc = item->disabled ? C_FAINT : selected ? C_CREAM : C_SUB;
			if (selected)
			{
				triangle(vx - a * 0.2f, r.y + r.h / 2 - a, vx + a, r.y + r.h / 2, vx - a * 0.2f, r.y + r.h / 2 + a, C_SEL_RIM);
				const float tw = text_w(FONT_SEMIBOLD, item->value, cap);
				const float lx = vx - a * 1.6f - tw - a * 1.4f;
				triangle(lx + a * 0.2f, r.y + r.h / 2 - a, lx + a * 0.2f, r.y + r.h / 2 + a, lx - a, r.y + r.h / 2, C_SEL_RIM);
			}
			text(FONT_SEMIBOLD, item->value, vx - a * 1.6f, r.y + (r.h - cap) / 2, cap, vc, ALIGN_RIGHT);
		}
		else if (item->kind == UI_ITEM_BAR)
		{
			const float bh = SDL_max(U(22), cap * 0.95f);
			const Box track = { value.x + U(20), r.y + (r.h - bh) / 2, value.w - U(20) - U(80), bh };
			bar(track, item->bar, item->muted ? (Colour){ 0.45f, 0.42f, 0.38f, 1 } : (Colour){ 0.95f, 0.76f, 0.42f, 1 }, true);
			char percent[16];
			snprintf(percent, sizeof(percent), "%d%%", (int)lroundf(item->bar * 100));
			text(FONT_SEMIBOLD, item->muted ? "Off" : percent, value.x + value.w, r.y + (r.h - cap) / 2, cap, item->muted ? C_DIM : c,
			     ALIGN_RIGHT);
			// (The level set where the bar is clicked, as on the original's.)
			add_hit((Box){ r.x, r.y, track.x - r.x, r.h }, item->hit);
			add_hit((Box){ track.x, r.y, track.w, r.h }, item->hit_value);
			continue;
		}
		if (item->hit_value.w > 0)
		{
			add_hit((Box){ r.x, r.y, value.x - r.x, r.h }, item->hit);
			add_hit((Box){ value.x, r.y, r.x + r.w - value.x, r.h }, item->hit_value);
		}
		else
			add_hit(r, item->hit);
	}
	if (m->item_count > fits)
		scroll_bar((Box){ p.x + p.w - U(14), top, U(8), fits * rh }, first, fits, m->item_count);
	const UIItem *sel = m->selected >= 0 && m->selected < m->item_count ? &m->items[m->selected] : NULL;
	const float foot_y = p.y + p.h - foot_h + U(10);
	rule(p.x + U(24), foot_y, p.w - U(48), with_alpha(C_RIM_BOTTOM, 0.6f));
	if (sel != NULL)
		text_wrapped(FONT_MEDIUM, sel->hint, p.x + U(40), foot_y + U(22), p.w - U(80), CAP_SMALL(), C_DIM, ALIGN_LEFT, 2);
	const bool bar_item = sel != NULL && sel->kind == UI_ITEM_BAR, choice = sel != NULL && sel->kind == UI_ITEM_CHOICE;
	KeyHint keys[4];
	int n = 0;
	keys[n++] = (KeyHint){ KEY_UP_DOWN, "", "Select" };
	if (bar_item || choice)
		keys[n++] = (KeyHint){ KEY_LEFT_RIGHT, "", bar_item ? "Volume" : "Change" };
	if (bar_item)
		keys[n++] = (KeyHint){ KEY_TEXT, "Enter", "Mute" };
	else if (!choice)
		keys[n++] = (KeyHint){ KEY_TEXT, "Enter", "Confirm" };
	else if (m->enter_turns)
		keys[n++] = (KeyHint){ KEY_TEXT, "Enter", "Change" };
	keys[n++] = (KeyHint){ KEY_TEXT, "Esc", "Back" };
	key_hints(keys, n, p.x + p.w / 2, p.y + p.h + U(22), ALIGN_CENTRE);
}

// A small picture of the modern HUD's part a help text is about.
static void help_figure(int part, Box b)
{
	panel(b, U(10), PANEL_WELL);
	const Box in = inset(b, U(14));
	const float bh = SDL_max(U(12), L.px * 4);
	switch (part)
	{
	case 0:  // the power bar (the generator)
		bar((Box){ in.x, in.y + in.h / 2 - bh / 2, in.w, bh }, 0.75f, (Colour){ 1.0f, 0.85f, 0.3f, 1 }, true);
		break;
	case 1:  // the weapons' power
	{
		const float pip = SDL_min(in.w / 9, U(14)), g = pip * 0.3f;
		pips(in.x, in.y + in.h * 0.28f - pip / 2, 6, 3, pip, g, (Colour){ 0.45f, 1.0f, 0.55f, 1 });
		pips(in.x, in.y + in.h * 0.72f - pip / 2, 6, 2, pip, g, (Colour){ 1.0f, 0.75f, 0.35f, 1 });
		break;
	}
	case 2:  // the rear weapon's mode
	{
		const float s = SDL_min(in.h * 0.5f, U(24));
		fill_octagon((Box){ in.x + in.w * 0.25f - s / 2, in.y + (in.h - s) / 2, s, s }, s * 0.3f, C_SEL_RIM, C_RIM_BOTTOM);
		fill_octagon((Box){ in.x + in.w * 0.75f - s / 2, in.y + (in.h - s) / 2, s, s }, s * 0.3f, C_PIP_OFF, C_PIP_OFF);
		break;
	}
	case 3:  // the sidekicks' ammunition
		bar((Box){ in.x, in.y + in.h / 2 - bh / 2, in.w * 0.46f, bh }, 0.8f, (Colour){ 0x96 / 255.0f, 0x22 / 255.0f, 0x6c / 255.0f, 1 }, true);
		bar((Box){ in.x + in.w * 0.54f, in.y + in.h / 2 - bh / 2, in.w * 0.46f, bh }, 0.4f, (Colour){ 0x96 / 255.0f, 0x22 / 255.0f, 0x6c / 255.0f, 1 },
		    true);
		break;
	default:  // shield and armor
		bar((Box){ in.x, in.y + in.h * 0.3f - bh / 2, in.w, bh }, 0.85f, (Colour){ 0.35f, 0.75f, 1.0f, 1 }, true);
		bar((Box){ in.x, in.y + in.h * 0.7f - bh / 2, in.w, bh }, 0.5f, (Colour){ 1.0f, 0.55f, 0.25f, 1 }, true);
		break;
	}
}

// The in-game help: what each part of the HUD shows.
static void build_level_help(const UIMenu *m)
{
	level_dim(0.45f, 0.55f);
	const UIHelp *h = &m->help;
	const float small = CAP_SMALL(), cap = CAP_ITEM();
	const float w = SDL_min(SDL_max(U(1060), cap * 34), L.safe.w - U(96));
	const float head_h = U(30) + CAP_SMALL() + U(14) + CAP_TITLE() + U(24) + U(18);
	const float keys_h = key_hints_height() + U(28);
	const float room = L.window.h - U(48) - keys_h - head_h - U(30);
	const float part_h = SDL_max(SDL_min(room / SDL_max(h->count, 1), U(150)), cap + small * 1.75f * 2 + U(24));
	const float ph = head_h + h->count * part_h + U(30);
	const Box p = { L.safe.x + (L.safe.w - w) / 2, SDL_max((L.window.h - ph - keys_h) / 2, U(24)), w, ph };
	panel(p, U(22), PANEL_GLASS);
	const float top = p.y + header(p, "HELP", "The HUD");
	const bool figures = !twoPlayerMode && rgpu_modern_hud();
	for (int i = 0; i < h->count; ++i)
	{
		const Box r = { p.x + U(30), top + i * part_h, p.w - U(60), part_h - U(12) };
		float x = r.x;
		if (figures)
		{
			const float fw = SDL_min(U(170), r.w * 0.2f), fh = SDL_min(r.h - U(16), U(92));
			help_figure(i, (Box){ r.x, r.y + (r.h - fh) / 2, fw, fh });
			x += fw + U(28);
		}
		const float tw = r.x + r.w - x;
		text(FONT_BOLD, h->title[i], x, r.y + U(8), cap, C_CREAM, ALIGN_LEFT);
		text_wrapped(FONT_MEDIUM, h->text[i], x, r.y + U(8) + cap + U(14), tw, small, C_TAN, ALIGN_LEFT,
		             SDL_max((int)((r.h - cap - U(30)) / (small * 1.75f)), 1));
		if (i + 1 < h->count)
			rule(r.x, r.y + r.h + U(5), r.w, with_alpha(C_RIM_BOTTOM, 0.35f));
	}
	const KeyHint keys[] = { { KEY_TEXT, "Any key", "Back to the game" } };
	key_hints(keys, 1, p.x + p.w / 2, p.y + p.h + U(22), ALIGN_CENTRE);
}

// Paused: a plate over the dimmed scene.
static void build_level_pause(const UIMenu *m)
{
	level_dim(0.28f, 0.36f);
	const float cap = cap_of(56, 22), small = CAP_SMALL();
	const char *title = m->title[0] != '\0' ? m->title : "Paused";
	const float w = SDL_max(text_w(FONT_BOLD, title, cap) + U(200), U(560)), h = U(40) + cap + U(30) + small + U(46);
	const float pulse = 0.82f + 0.18f * sinf(SDL_GetTicks() / 450.0f);
	const Box p = { L.safe.x + (L.safe.w - w) / 2, L.window.h * 0.42f - h / 2, w, h };
	panel(p, U(22), PANEL_GLASS);
	text_graded(FONT_BOLD, title, p.x + p.w / 2, p.y + U(40), cap, C_GOLD_TOP, C_GOLD_BOTTOM, ALIGN_CENTRE, true);
	rule(p.x + U(60), p.y + U(40) + cap + U(16), p.w - U(120), with_alpha(C_RIM_TOP, 0.7f));
	text(FONT_MEDIUM, "Press any key to continue", p.x + p.w / 2, p.y + U(40) + cap + U(30), small, with_alpha(C_TAN, pulse), ALIGN_CENTRE);
}

// The level's end: its results, row by row as the game shows them.
static void build_level_end(const UIMenu *m)
{
	const UIResults *r = &m->results;
	// (No easing in: the end isn't shown again while it waits for a key.)
	level_dim(0.30f, 0.42f);
	const float cap = CAP_ITEM(), small = CAP_SMALL(), big = CAP_TITLE();
	const float w = SDL_min(SDL_max(U(820), cap * 27), L.safe.w - U(96));
	const float row_h = SDL_max(U(64), cap * 2.4f);
	const float head_h = U(30) + small + U(14) + big + U(24) + U(18);
	const int rows = SDL_max(r->row_count, 2);
	const float h = head_h + rows * row_h + U(30) + (r->cubes >= 0 ? row_h : 0);
	const Box p = { L.safe.x + (L.safe.w - w) / 2, SDL_max((L.window.h - h - key_hints_height() - U(28)) / 2, U(24)), w, h };
	panel(p, U(22), PANEL_GLASS);
	float y = p.y + header(p, m->crumb, r->title);
	for (int i = 0; i < r->row_count; ++i)
	{
		const Box row = { p.x + U(40), y, p.w - U(80), row_h };
		text(FONT_SEMIBOLD, r->label[i], row.x, row.y + (row.h - cap) / 2, cap, C_TAN, ALIGN_LEFT);
		const bool percent = r->percent >= 0 && strchr(r->value[i], '%') != NULL;
		if (percent)
		{
			const float bw = SDL_min(U(300), row.w * 0.4f), bh = SDL_max(U(18), cap * 0.8f);
			bar((Box){ row.x + row.w - bw - U(120), row.y + (row.h - bh) / 2, bw, bh }, r->percent / 100.0f,
			    r->percent >= 100 ? C_GREEN : (Colour){ 0.95f, 0.76f, 0.42f, 1 }, true);
		}
		text_graded(FONT_BOLD, r->value[i], row.x + row.w, row.y + (row.h - cap * 1.15f) / 2, cap * 1.15f, C_GOLD_TOP, C_GOLD_BOTTOM,
		            ALIGN_RIGHT, true);
		y += row_h;
		if (i + 1 < r->row_count)
			rule(row.x, y - U(2), row.w, with_alpha(C_RIM_BOTTOM, 0.3f));
	}
	if (r->cubes >= 0)
	{
		const Box row = { p.x + U(40), y, p.w - U(80), row_h };
		text(FONT_SEMIBOLD, "Data cubes", row.x, row.y + (row.h - cap) / 2, cap, C_TAN, ALIGN_LEFT);
		if (r->cubes == 0)
			text(FONT_SEMIBOLD, "None", row.x + row.w, row.y + (row.h - cap) / 2, cap, C_DIM, ALIGN_RIGHT);
		const float size = SDL_min(row_h * 0.7f, U(46));
		for (int i = 0; i < r->cubes; ++i)
			rgpu_ui_table_sprite(OPTION_SHAPES, 34, row.x + row.w - (r->cubes - i) * (size + U(10)), row.y + (row.h - size) / 2, size, size,
			                     L.alpha);
	}
	if (r->prompt)
	{
		const KeyHint keys[] = { { KEY_TEXT, "Any key", "Continue" } };
		key_hints(keys, 1, p.x + p.w / 2, p.y + p.h + U(22), ALIGN_CENTRE);
	}
}

void ui_build_screen(const UIView *view)
{
	hit_count = 0;
	if (!have_published)
		return;
	view_now = view;
	// (Over a level the palette's fade darkens the whole window, the scene with it: rgpu_present_3d_menu.)
	layout_begin(view, published.kind >= UI_SCREEN_LEVEL_MENU ? 1.0f : ui_screen_fade());
	// The picture behind the panels a little darker, so they read clearly (not the title's; the store
	// and the screens over a level have their own).
	if (published.kind != UI_SCREEN_TITLE && published.kind < UI_SCREEN_SHOP)
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
	case UI_SCREEN_SHOP:
		build_shop(&published);
		break;
	case UI_SCREEN_LEVEL_MENU:
		build_level_menu(&published);
		break;
	case UI_SCREEN_LEVEL_HELP:
		build_level_help(&published);
		break;
	case UI_SCREEN_LEVEL_PAUSE:
		build_level_pause(&published);
		break;
	case UI_SCREEN_LEVEL_END:
		build_level_end(&published);
		break;
	case UI_SCREEN_NONE:
		break;
	}
	if (published.dialog.on && published.kind != UI_SCREEN_SHOP)
		build_dialog(&published.dialog);
}

/* --- The HUD ------------------------------------------------------------------------------- */

/*
 * What flies under the HUD's panels: the ship (its box with its sidekicks, in the window) and the
 * enemies' shots. A panel the ship is under, or dense fire (HUD_FIRE shots or more), fades to
 * HUD_UNDER, quickly, and comes back more slowly once they have left; near it, it fades part of the
 * way. Timed in seconds, so it is the same at any frame rate.
 */
#define HUD_UNDER 0.33f
#define HUD_FIRE 3
static struct
{
	bool ship;
	Box ship_box;
	int shot_count;
	float shot_x[ENEMY_SHOT_MAX], shot_y[ENEMY_SHOT_MAX];
	float dt;  // seconds since the HUD was made last
} under;

static void hud_find_under(const UIView *view)
{
	static Uint64 last = 0;
	const Uint64 now = SDL_GetTicksNS();
	under.dt = last > 0 ? SDL_clamp((now - last) / 1e9f, 0.0f, 0.1f) : 0.0f;
	last = now;
	under.ship = false;
	under.shot_count = 0;
	if (view->menu_over)
		return;
	const Player *p = &player[0];
	if (p->is_alive)
	{
		// The ship's sprite (24 x 28 round x + 7, y + 7) and its sidekicks.
		float x0 = p->x + 7.0f - 13, x1 = p->x + 7.0f + 13, y0 = p->y + 7.0f - 15, y1 = p->y + 7.0f + 15;
		for (int i = 0; i < 2; ++i)
			if (p->items.sidekick[i] > 0)
			{
				x0 = SDL_min(x0, p->sidekick[i].x - 2.0f);
				x1 = SDL_max(x1, p->sidekick[i].x + 14.0f);
				y0 = SDL_min(y0, p->sidekick[i].y - 2.0f);
				y1 = SDL_max(y1, p->sidekick[i].y + 16.0f);
			}
		float ax, ay, bx, by;
		if (rgpu_playfield_to_window(x0, y0, &ax, &ay) && rgpu_playfield_to_window(x1, y1, &bx, &by))
		{
			under.ship = true;
			under.ship_box = (Box){ SDL_min(ax, bx), SDL_min(ay, by), SDL_fabsf(bx - ax), SDL_fabsf(by - ay) };
		}
	}
	for (int z = 0; z < ENEMY_SHOT_MAX; ++z)
	{
		if (enemyShotAvail[z])
			continue;
		float wx, wy;
		if (rgpu_playfield_to_window(enemyShot[z].sx + 6.0f, enemyShot[z].sy + 7.0f, &wx, &wy))
		{
			under.shot_x[under.shot_count] = wx;
			under.shot_y[under.shot_count] = wy;
			++under.shot_count;
		}
	}
}

// Quads from mark on fade as what flies under their box (window points) says, eased in *shown.
static void hud_fade(int mark, Box b, float *shown)
{
	const Box g = inset(b, -U(18));
	bool covered = false;
	float target = 1.0f;
	if (under.ship)
	{
		const Box s = under.ship_box;
		covered = s.x + s.w > g.x && s.x < g.x + g.w && s.y + s.h > g.y && s.y < g.y + g.h;
		if (!covered)
		{
			// Near: part of the way.
			const float dx = SDL_max(SDL_max(g.x - (s.x + s.w), s.x - (g.x + g.w)), 0.0f);
			const float dy = SDL_max(SDL_max(g.y - (s.y + s.h), s.y - (g.y + g.h)), 0.0f);
			const float d = sqrtf(dx * dx + dy * dy), reach = U(110);
			if (d < reach)
				target = HUD_UNDER + (1 - HUD_UNDER) * (0.35f + 0.65f * d / reach);
		}
	}
	int shots = 0;
	for (int i = 0; i < under.shot_count && !covered; ++i)
		shots += inside(g, under.shot_x[i], under.shot_y[i]);
	if (covered || shots >= HUD_FIRE)
		target = HUD_UNDER;
	// Quick to fade (about 0.1 s), slower back (about 0.35 s).
	const float rate = target < *shown ? 22.0f : 6.0f;
	*shown += (target - *shown) * (1 - expf(-rate * under.dt));
	*shown = SDL_clamp(*shown, HUD_UNDER, 1.0f);
	rgpu_ui_fade_since(mark, *shown);
}

static Uint32 game_over_frame = 0;
static bool game_over_seen = false;
static char game_over_text[32] = "Game Over";

void ui_note_game_over(const char *text)
{
	game_over_frame = l3d_frame_number;
	game_over_seen = true;
	if (text != NULL && text[0] != '\0')
	{
		SDL_strlcpy(game_over_text, text, sizeof(game_over_text));
		for (int i = (int)strlen(game_over_text) - 1; i >= 0 && game_over_text[i] == ' '; --i)
			game_over_text[i] = '\0';
	}
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

	// What flies under the panels, so they fade.
	hud_find_under(view);
	Box bottom_left = { 0, 0, 0, 0 }, bottom_right = { 0, 0, 0, 0 };  // (the message keeps clear of them)
	static float fades[6] = { 1, 1, 1, 1, 1, 1 };
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
		bottom_right = b;
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
		hud_fade(mark, b, &fades[0]);
	}

	// Top right: the guns' power (pips; 15 once a gun is overclocked past 11), the sidekicks' ammunition.
	float top_right_w = 0;  // (the boss bar keeps clear of it)
	{
		const float pip = SDL_max(U(20), L.px * 6), gap = SDL_max(U(5), L.px * 2);
		const int most = SDL_max(p->items.weapon[0].power, p->items.weapon[1].power) > 11 ? 15 : 11;
		const float pips_w = most * pip + (most - 1) * gap;
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
			pips(b.x + U(20) + label_w, y + (row_h - pip) / 2, 11, SDL_min(level, 11), pip, gap, gun[g]);
			if (most > 11)
				pips(b.x + U(20) + label_w + 11 * (pip + gap), y + (row_h - pip) / 2, most - 11, SDL_max(level - 11, 0), pip, gap,
				     (Colour){ 1.0f, 0.6f, 0.25f, 1 });
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
		hud_fade(mark, b, &fades[1]);
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
			w = SDL_max(w, icon + U(16) + text_w(FONT_SEMIBOLD, special_name, cap_l) + U(48) + SDL_max(U(12), L.px * 4) + U(14));
		}
		w = SDL_max(w, (extra_lives > 0 ? 3 : 0) * icon + bombs * icon * 0.8f + U(80));
		const Box b = { safe.x + margin, safe.y + safe.h - margin - h, w, h };
		bottom_left = b;
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
			// The special weapon, and its ready light (the game's beside its icon): lit when it can fire.
			rgpu_ui_sprite(&spriteSheet10, special[p->items.special].itemgraphic, true, b.x + U(20), y, icon * 24 / 28.0f, icon,
			               L.alpha * (special_ready ? 1.0f : 0.55f));
			const float name_x = b.x + U(24) + icon;
			text(FONT_SEMIBOLD, special_name, name_x, y + (icon - cap_l) / 2, cap_l, special_ready ? C_CREAM : C_DIM, ALIGN_LEFT);
			const float lamp = SDL_max(U(12), L.px * 4);
			const Box l = { name_x + text_w(FONT_SEMIBOLD, special_name, cap_l) + U(14), y + (icon - lamp) / 2, lamp, lamp };
			const Colour lit = { 1.0f, 0.42f, 0.28f, 1 };
			if (special_ready)
			{
				fill_octagon(inset(l, -lamp * 0.35f), lamp * 0.5f, with_alpha(lit, 0.25f), with_alpha(lit, 0.0f));
				fill_octagon(l, lamp * 0.3f, lit, mix(lit, (Colour){ 0, 0, 0, 1 }, 0.35f));
			}
			else
				fill_octagon(l, lamp * 0.3f, C_PIP_OFF, mix(C_PIP_OFF, (Colour){ 0, 0, 0, C_PIP_OFF.a }, 0.3f));
		}
		hud_fade(mark, b, &fades[2]);
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
			hud_fade(mark, b, &fades[3]);
		}
	}

	// The game's message (JE_drawTextWindow) in a pill at the bottom middle, while it shows.
	{
		static char shown_message[sizeof(text_window_message)] = "";
		static Uint64 message_since = 0;
		if (strcmp(shown_message, text_window_message) != 0)
		{
			SDL_strlcpy(shown_message, text_window_message, sizeof(shown_message));
			message_since = SDL_GetTicks();
		}
		if (textErase > 0 && text_window_message[0] != '\0' && !view->menu_over && rgpu_ui_text_ready())
		{
			const float age = (SDL_GetTicks() - message_since) / 1000.0f;
			const float a = SDL_clamp(SDL_min(age / 0.2f, textErase / 14.0f), 0.0f, 1.0f);
			const float cap = cap_of(19, 11);
			char fitted[sizeof(text_window_message)];
			fit_text(FONT_SEMIBOLD, text_window_message, cap, safe.w * 0.6f, fitted, sizeof(fitted));
			const float w = text_w(FONT_SEMIBOLD, fitted, cap) + U(70), h = cap * 2.5f;
			// Between the bottom panels; above them where it doesn't fit between.
			float y = safe.y + safe.h - margin - h - U(4);
			const float x = safe.x + (safe.w - w) / 2;
			const float left_end = bottom_left.w > 0 ? bottom_left.x + bottom_left.w + U(16) : safe.x;
			const float right_start = bottom_right.w > 0 ? bottom_right.x - U(16) : safe.x + safe.w;
			if (x < left_end || x + w > right_start)
				y = SDL_min(bottom_left.w > 0 ? bottom_left.y : y + h, bottom_right.w > 0 ? bottom_right.y : y + h) - h - U(16);
			const Box b = { x, y + (1 - a) * U(10), w, h };
			L.alpha = a;
			const int mark = rgpu_ui_mark();
			panel(b, U(10), PANEL_SOLID);
			text_mid(FONT_SEMIBOLD, fitted, b, 0, cap, C_CREAM, ALIGN_CENTRE);
			hud_fade(mark, b, &fades[4]);
			L.alpha = 1;
		}
	}

	// Game over: a plate in the middle while the game shows it (ui_note_game_over).
	if (game_over_seen && l3d_frame_number - game_over_frame <= 2 && !view->menu_over)
	{
		static Uint64 since = 0;
		static Uint32 shown_for = 0;
		if (shown_for == 0 || game_over_frame - shown_for > 3)
			since = SDL_GetTicks();
		shown_for = game_over_frame;
		const float age = (SDL_GetTicks() - since) / 1000.0f, a = SDL_clamp(age / 0.6f, 0.0f, 1.0f);
		const float cap = cap_of(64, 24), small = CAP_SMALL();
		L.alpha = a;
		rect(L.window, (Colour){ 0, 0, 0, 0.3f }, (Colour){ 0, 0, 0, 0.42f });
		const float w = SDL_max(text_w(FONT_BOLD, game_over_text, cap) + U(220), U(620)), h = U(44) + cap + U(30) + small + U(48);
		const Box b = { safe.x + (safe.w - w) / 2, safe.y + safe.h * 0.36f - h / 2 + (1 - a) * U(20), w, h };
		panel(b, U(22), PANEL_SOLID);
		text_graded(FONT_BOLD, game_over_text, b.x + b.w / 2, b.y + U(44), cap, (Colour){ 1.0f, 0.62f, 0.5f, 1 }, (Colour){ 0.8f, 0.3f, 0.2f, 1 },
		            ALIGN_CENTRE, true);
		rule(b.x + U(60), b.y + U(44) + cap + U(16), b.w - U(120), with_alpha(C_RIM_TOP, 0.7f));
		const float pulse = 0.75f + 0.25f * sinf(SDL_GetTicks() / 420.0f);
		text(FONT_MEDIUM, "Press any key", b.x + b.w / 2, b.y + U(44) + cap + U(32), small, with_alpha(C_TAN, pulse), ALIGN_CENTRE);
		L.alpha = 1;
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
