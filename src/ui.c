/*
 * Tyrian3D: the modern UI. See ui.h.
 */
#include "ui.h"

#include "config.h"
#include "episodes.h"
#include "game_menu.h"
#include "helptext.h"
#include "joystick.h"
#include "keyboard.h"
#include "layer3d.h"
#include "mainint.h"
#include "models3d.h"
#include "mouse.h"
#include "musmast.h"
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
#include <stdlib.h>
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
	// Filling the window, cut where the window's shape differs from 8:5 (its top and bottom in a wider window, its
	// sides in a narrower one); on ultrawide only the window's 16:9 middle, the picture's blurred copy round it.
	// (Cut more at the bottom than at the top: the pictures' titles and logos are near their tops.)
	int w = SDL_min(window_w, window_h * 16 / 9), h = w * 5 / 8;
	if (h < window_h)
	{
		h = window_h;
		w = h * 8 / 5;
	}
	const int y = h > window_h ? (window_h - h) * 3 / 10 : (window_h - h) / 2;
	*out = (SDL_Rect){ (window_w - w) / 2, y, w, h };
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

// A text of the game without its highlight marks ('~'), its leading and trailing spaces and a colon at
// its end (in and out may be the same).
static void plain_label_ui(char *out, const char *in, size_t size)
{
	while (*in == ' ')
		++in;
	size_t n = 0;
	for (; *in != '\0' && n + 1 < size; ++in)
		if (*in != '~')
			out[n++] = *in;
	out[n] = '\0';
	while (n > 0 && (out[n - 1] == ' ' || out[n - 1] == ':'))
		out[--n] = '\0';
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

// A filled disc (a joystick's button), of `sides` sides.
static void disc(float cx, float cy, float r, Colour c)
{
	const int sides = 20;
	for (int i = 0; i < sides; ++i)
	{
		const float a0 = i * 2 * (float)M_PI / sides, a1 = (i + 1) * 2 * (float)M_PI / sides;
		triangle(cx, cy, cx + r * cosf(a0), cy + r * sinf(a0), cx + r * cosf(a1), cy + r * sinf(a1), c);
	}
}

// KEY_PAD_*, KEY_BUTTON: a joystick's (the key hints when the joystick was the last input).
typedef enum { KEY_TEXT, KEY_UP_DOWN, KEY_LEFT_RIGHT, KEY_PAD_UP_DOWN, KEY_PAD_LEFT_RIGHT, KEY_BUTTON } KeyGlyph;

static float glyph_width(KeyGlyph glyph, const char *key, float cap)
{
	const float h = cap * 2.1f;
	switch (glyph)
	{
	case KEY_TEXT:
		return SDL_max(text_w(FONT_SEMIBOLD, key, cap) + cap * 1.4f, h);
	case KEY_UP_DOWN:
	case KEY_LEFT_RIGHT:
		return cap * 3.2f;
	default:
		return h;
	}
}

// A key's cap with its name or arrows (or a joystick's pad or button), and what it does after it;
// returns the width taken.
static float key_hint(float x, float y, KeyGlyph glyph, const char *key, const char *action, Colour c)
{
	const float cap = CAP_KEY(), h = cap * 2.1f, small = CAP_SMALL();
	const float w = glyph_width(glyph, key, cap);
	const Box k = { x, y, w, h };
	const Colour kc = mix(C_CREAM, c, 0.3f);
	const float cx = k.x + k.w / 2, cy = k.y + k.h / 2;
	if (glyph == KEY_BUTTON)
	{
		// A round button with its number.
		disc(cx, cy, h * 0.5f, C_WELL_RIM);
		disc(cx, cy, h * 0.5f - SDL_max(U(1.5f), L.px), mix(C_WELL, (Colour){ 0.2f, 0.14f, 0.09f, 0.95f }, 0.5f));
		text_mid(FONT_BOLD, key, k, 0, cap, kc, ALIGN_CENTRE);
	}
	else
	{
		panel(k, h * 0.22f, PANEL_WELL);
		if (glyph == KEY_TEXT)
			text_mid(FONT_SEMIBOLD, key, k, 0, cap, kc, ALIGN_CENTRE);
		else if (glyph == KEY_PAD_UP_DOWN || glyph == KEY_PAD_LEFT_RIGHT)
		{
			// A direction pad: the cross, the arms that act lit.
			const float arm = h * 0.34f, t = h * 0.2f;
			const Colour off = with_alpha(C_FAINT, 0.55f);
			const bool vertical = glyph == KEY_PAD_UP_DOWN;
			rect((Box){ cx - t / 2, cy - arm, t, 2 * arm }, vertical ? kc : off, vertical ? kc : off);
			rect((Box){ cx - arm, cy - t / 2, 2 * arm, t }, vertical ? off : kc, vertical ? off : kc);
		}
		else
		{
			const float a = cap * 0.62f;
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

#define KEY_HINTS_MAX 12

// The hints as shown: when the joystick was the last input (joystick.h), its pad for the arrows and the
// buttons the menus take for Enter and Esc (fire and change fire: push_joysticks_as_keyboard), the keys
// it has nothing for left out. Returns how many.
static int shown_hints(const KeyHint *hints, int count, KeyHint *out)
{
	count = SDL_min(count, KEY_HINTS_MAX);
	if (!joystick_last_input)
	{
		memcpy(out, hints, sizeof(*hints) * (size_t)count);
		return count;
	}
	static char confirm[8], cancel[8];
	const int b_confirm = joystick_action_button(0), b_cancel = joystick_action_button(1);
	snprintf(confirm, sizeof(confirm), "%d", b_confirm > 0 ? b_confirm : 1);
	snprintf(cancel, sizeof(cancel), "%d", b_cancel > 0 ? b_cancel : 2);
	int n = 0;
	for (int i = 0; i < count; ++i)
	{
		KeyHint h = hints[i];
		if (h.glyph == KEY_UP_DOWN)
			h.glyph = KEY_PAD_UP_DOWN;
		else if (h.glyph == KEY_LEFT_RIGHT)
			h.glyph = KEY_PAD_LEFT_RIGHT;
		else if (strcmp(h.key, "Enter") == 0)
			h = (KeyHint){ KEY_BUTTON, confirm, h.action };
		else if (strcmp(h.key, "Esc") == 0)
			h = (KeyHint){ KEY_BUTTON, cancel, h.action };
		else if (strcmp(h.key, "Any key") == 0)
			h.key = "Any button";
		else
			continue;
		out[n++] = h;
	}
	return n;
}

static float key_hints_width(const KeyHint *given, int given_count)
{
	KeyHint hints[KEY_HINTS_MAX];
	const int count = shown_hints(given, given_count, hints);
	const float cap = CAP_KEY(), small = CAP_SMALL();
	float w = 0;
	for (int i = 0; i < count; ++i)
		w += glyph_width(hints[i].glyph, hints[i].key, cap) + cap * 0.6f + text_w(FONT_MEDIUM, hints[i].action, small) + cap * 1.8f;
	return w - CAP_KEY() * 1.8f;
}

static float key_hints_height(void)
{
	return CAP_KEY() * 2.1f + 2 * U(10);
}

// A row of key hints on a backing; align as text (x is their left, middle or right), y their top.
static void key_hints(const KeyHint *given, int given_count, float x, float y, int align)
{
	KeyHint hints[KEY_HINTS_MAX];
	const int count = shown_hints(given, given_count, hints);
	if (count == 0)
		return;
	const float pad = U(16);
	const float w = key_hints_width(given, given_count) + 2 * pad;
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
// rectangle of the original's item it stands for (screen pixels), or the UI's own widget it is (action).
#define HITS 96
static struct
{
	Box box;
	SDL_Rect hit;
	int action;  // UI_ACTION_*: the UI's own (the original takes the point of nothing there), or 0
} hits[HITS];
static int hit_count = 0;

static void add_hit(Box b, SDL_Rect r)
{
	if (hit_count < HITS && r.w > 0 && r.h > 0 && b.w > 0 && b.h > 0)
	{
		hits[hit_count].box = b;
		hits[hit_count].hit = r;
		hits[hit_count].action = 0;
		++hit_count;
	}
}

// A widget of the UI's own: a click on it is the screen's to take (ui_take_press).
static void add_action(Box b, int action)
{
	if (hit_count < HITS && action > 0 && b.w > 0 && b.h > 0)
	{
		hits[hit_count].box = b;
		hits[hit_count].hit = (SDL_Rect){ 0, 0, 0, 0 };
		hits[hit_count].action = action;
		++hit_count;
	}
}

static int hover_action = 0;    // the UI's own widget the pointer was mapped on last
static int pressed_action = 0;  // and the one pressed, not yet taken

void ui_note_press(int button)
{
	pressed_action = button == SDL_BUTTON_LEFT ? hover_action : 0;
}

int ui_take_press(void)
{
	const int action = pressed_action;
	pressed_action = 0;
	return action;
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

bool ui_published_is(UIScreenKind kind)
{
	return have_published && published.kind == kind;
}

const UIMenu *ui_published(void)
{
	return have_published ? &published : NULL;
}

void ui_screen_done(void)
{
	have_published = false;
	hit_count = 0;
	hover_action = pressed_action = 0;
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
	const SDL_Color *target = published.palette != NULL ? published.palette : colors;
	for (int i = published.text_color; i < published.text_color + 16 && i < 256; ++i)
	{
		const Uint8 *c = (const Uint8 *)&rgb_palette[i];
		now += c[0] + c[1] + c[2];
		full += target[i].r + target[i].g + target[i].b;
	}
	return full > 0 ? SDL_clamp(now / full, 0.0f, 1.0f) : 1.0f;
}

bool ui_map_pointer(float wx, float wy, Sint32 *x, Sint32 *y)
{
	hover_action = 0;
	if (!shown_last || !have_published)
		return false;
	for (int i = hit_count - 1; i >= 0; --i)
	{
		const Box b = hits[i].box;
		if (!inside(b, wx, wy))
			continue;
		if (hits[i].action > 0)
		{
			// The UI's own: the original takes it at its point of nothing.
			hover_action = hits[i].action;
			break;
		}
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

bool ui_wheel_moves(float y, SDL_Scancode *key)
{
	// (Not on a data cube's text, which scrolls with it its own way, nor on a question.)
	if (!shown_last || !have_published || y == 0 || published.dialog.on || published.wheel == UI_WHEEL_NONE)
		return false;
	if (published.kind == UI_SCREEN_SHOP && published.shop.page == UI_SHOP_CUBE)
		return false;
	if (published.wheel == UI_WHEEL_LEFT_RIGHT)
	{
		*key = y > 0 ? SDL_SCANCODE_LEFT : SDL_SCANCODE_RIGHT;
		return true;
	}
	*key = y > 0 ? SDL_SCANCODE_UP : SDL_SCANCODE_DOWN;
	// (The jukebox's songs: Up and Down play the one before or after.)
	return published.item_count > 1 || (published.kind == UI_SCREEN_SHOP && published.shop.tab_count > 1) ||
	       published.kind == UI_SCREEN_JUKEBOX;
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
static float paging_controls(const UIPaging *pg, Box p, float y);

static void build_setup(const UIMenu *m)
{
	const float cap = CAP_ITEM();
	const float row_h = SDL_max(U(56), cap * 2.2f);
	const float w = SDL_min(SDL_max(U(940), cap * 30), L.safe.w - U(96));
	// (The pages as tabs under the title, the panel as tall on every tab: m->rows.)
	const bool tabbed = m->paging.count > 1;
	const float tabs_h = tabbed ? SDL_max(CAP_SMALL() * 2.5f, U(44)) + U(18) : 0;
	const int rows = SDL_max(m->item_count, m->rows);
	const float head_h = U(30) + (m->crumb[0] != '\0' ? CAP_SMALL() + U(14) : 0) + CAP_TITLE() + U(24) + U(18) + tabs_h;
	const float foot_h = CAP_SMALL() * 1.75f * 2 + U(44);
	float h = head_h + rows * row_h + U(12) + foot_h;
	const float keys_h = key_hints_height() + U(28);
	float rh = row_h;
	const float room = L.window.h - U(48) - keys_h;
	if (h > room)
	{
		rh = SDL_max((room - head_h - foot_h - U(12)) / SDL_max(rows, 1), cap * 1.6f);
		h = head_h + rows * rh + U(12) + foot_h;
	}
	const Box p = { L.safe.x + (L.safe.w - w) / 2, SDL_max((L.window.h - h - keys_h) / 2, U(24)), w, h };
	panel(p, U(22), PANEL_GLASS);
	float top = p.y + header(p, m->crumb, m->title);
	if (tabbed)
		top += paging_controls(&m->paging, p, top - U(4)) + U(14);
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
	else if (tabbed)
	{
		const KeyHint keys[] = { { KEY_UP_DOWN, "", "Select" }, { KEY_TEXT, "Enter", sel != NULL && sel->kind == UI_ITEM_CHOICE ? "Change" : "Confirm" },
		                         { KEY_TEXT, "Tab", "Next Tab" }, { KEY_TEXT, "Esc", "Back" } };
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
// An episode the episode screen shows beside the game's own: episode 7 and up (the GBC's) and custom ones.
static bool extra_episode(const char *label)
{
	if (SDL_strncasecmp(label, "Custom", 6) == 0)
		return true;
	int number = 0;
	return SDL_sscanf(label, "Episode %d", &number) == 1 && number >= 7;
}

static void choice_card(const UIMenu *m, int i, Box r, bool episodes)
{
	const float cap = CAP_ITEM(), small = CAP_SMALL();
	const UIItem *item = &m->items[i];
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
		text(FONT_BOLD, name, r.x + U(28), y + small + U(10), cap, item->disabled ? C_FAINT : selected ? C_CREAM : C_TAN, ALIGN_LEFT);
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

static void build_choices(const UIMenu *m)
{
	const float cap = CAP_ITEM(), small = CAP_SMALL();
	const bool episodes = m->kind == UI_SCREEN_EPISODES;
	// (The episode screen: the game's own episodes in the panel, the GBC's and custom ones in a panel beside it.)
	int main_count = m->item_count;
	if (episodes)
		for (int i = 0; i < m->item_count; ++i)
			if (extra_episode(m->items[i].label))
			{
				main_count = i;
				break;
			}
	const int extra_count = m->item_count - main_count;
	float card_h = SDL_max(U(episodes ? 84 : 88), cap + small * 1.9f + U(30));
	const float gap = U(10);
	const float side_w = extra_count > 0 ? SDL_min(U(560), L.safe.w * 0.34f) : 0;
	const float side_gap = extra_count > 0 ? U(30) : 0;
	const float w = SDL_min(SDL_max(U(820), cap * 27), L.safe.w - U(96) - side_w - side_gap);
	const float head_h = U(30) + CAP_TITLE() + U(24) + U(18);
	const float keys_h = key_hints_height() + U(28);
	const int rows = SDL_max(main_count, extra_count);
	float h = head_h + main_count * (card_h + gap) + U(24);
	const float room = L.window.h - U(48) - keys_h;
	if (head_h + rows * (card_h + gap) + U(24) > room)
	{
		card_h = SDL_max((room - head_h - U(24)) / SDL_max(rows, 1) - gap, cap * 1.8f);
		h = head_h + main_count * (card_h + gap) + U(24);
	}
	const float x0 = L.safe.x + (L.safe.w - (w + side_gap + side_w)) / 2;
	const Box p = { x0, SDL_max((L.window.h - h - keys_h) / 2, U(24)), w, h };
	panel(p, U(22), PANEL_GLASS);
	const float top = p.y + header(p, "", m->title);
	for (int i = 0; i < main_count; ++i)
		choice_card(m, i, (Box){ p.x + U(24), top + i * (card_h + gap), p.w - U(48), card_h }, episodes);
	if (extra_count > 0)
	{
		const float sh = head_h + extra_count * (card_h + gap) + U(24);
		const Box sp = { p.x + p.w + side_gap, p.y, side_w, sh };
		panel(sp, U(22), PANEL_GLASS);
		const float stop = sp.y + header(sp, "", "Extras");
		for (int i = 0; i < extra_count; ++i)
			choice_card(m, main_count + i, (Box){ sp.x + U(24), stop + i * (card_h + gap), sp.w - U(48), card_h }, episodes);
	}
	const KeyHint keys[] = { { KEY_UP_DOWN, "", "Select" }, { KEY_TEXT, "Enter", "Confirm" }, { KEY_TEXT, "Esc", "Back" } };
	key_hints(keys, (int)COUNTOF(keys), x0 + (w + side_gap + side_w) / 2, p.y + p.h + U(22), ALIGN_CENTRE);
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

// An item's own 3D model rendered (rgpu_ui_model_icon), square in a well, the same margin round every model; false if
// it has no such render.
static bool model_icon(int model, Box well, float alpha)
{
	const float side = SDL_min(well.w, well.h) * 0.94f;
	return model >= 0 && rgpu_ui_model_icon(model, well.x + (well.w - side) / 2, well.y + (well.h - side) / 2, side, side, alpha);
}

// An item's icon fitted in a well: its own 3D model rendered, or a sprite of the game.
static void item_icon(const UIItem *it, Box well, float alpha)
{
	if (model_icon(it->icon_model - 1, well, alpha * L.alpha))
		return;
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
	// (The text's lines, about: as many as its width takes, at most 3.)
	const float text_lines = d->text[0] != '\0' ? SDL_clamp(ceilf(text_w(FONT_MEDIUM, d->text, small) * 1.06f / (w - U(100))), 1.0f, 3.0f) : 0;
	const float btn_h = SDL_max(U(64), cap * 2.6f);
	const float note_cap = CAP_TITLE() * 1.15f;
	const float note_h = d->note_label[0] != '\0' ? CAP_KEY() + U(12) + note_cap + U(44) : 0;
	const float h = U(36) + CAP_TITLE() + U(30) + text_lines * small * 1.75f + note_h + (d->field_on ? cap * 2.4f + U(30) : 0) + btn_h + U(70);
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
	if (d->note_label[0] != '\0')
	{
		// A value large (a high score).
		y += U(14);
		text(FONT_SEMIBOLD, d->note_label, p.x + p.w / 2, y + U(4), CAP_KEY(), C_DIM, ALIGN_CENTRE);
		text_graded(FONT_BOLD, d->note, p.x + p.w / 2, y + U(4) + CAP_KEY() + U(12), note_cap, C_GOLD_TOP, C_GOLD_BOTTOM, ALIGN_CENTRE, true);
		y += note_h - U(14);
	}
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
		if (d->actions)
			add_action(b, i == 0 ? UI_ACTION_YES : UI_ACTION_NO);
		else
			add_hit(b, i == 0 ? d->hit_yes : d->hit_no);
	}
	const KeyHint keys[] = { { KEY_LEFT_RIGHT, "", "Choose" }, { KEY_TEXT, "Enter", "Confirm" }, { KEY_TEXT, "Esc", "Cancel" } };
	const KeyHint typing[] = { { KEY_TEXT, "Enter", d->actions ? d->yes : "Save" }, { KEY_TEXT, "Esc", d->actions ? d->no : "Cancel" } };
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
		float under_h = !under ? 0 : s->scene == UI_SCENE_SIM ? SDL_max(U(150), CAP_SMALL() * 2 + U(110)) : SDL_max(U(118), CAP_SMALL() + U(90));
		// (Two players' columns, the Super Arcade's weapons: taller.)
		if (under && s->scene == UI_SCENE_SHIP && s->player_count == 2)
			under_h = SDL_max(U(206), CAP_ITEM() + CAP_SMALL() * 5.4f + U(70));
		else if (under && s->scene == UI_SCENE_SHIP && s->super_title[0] != '\0')
			under_h = SDL_max(U(236), CAP_ITEM() + CAP_SMALL() * 6.2f + U(60));
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
	if (s->player_count == 2 && s->scene == UI_SCENE_SHIP)
	{
		// Two players: a column each, as their ships stand over it.
		const float col_w = (in.w - U(40)) / 2, small = CAP_SMALL(), key = CAP_KEY(), name_cap = CAP_ITEM();
		for (int k = 0; k < 2; ++k)
		{
			const float x = in.x + k * (col_w + U(40));
			float y = in.y;
			text(FONT_SEMIBOLD, s->players[k].name, x, y, key, C_DIM, ALIGN_LEFT);
			char score[32];
			grouped(strtoul(s->players[k].score, NULL, 10), score, sizeof(score));
			if (s->players[k].score[0] != '\0')  // (twin-stick's turret: the ship's score is both's)
				text_graded(FONT_BOLD, score, x + col_w, y - U(2), CAP_HEAD(), C_GOLD_TOP, C_GOLD_BOTTOM, ALIGN_RIGHT, true);
			y += key + U(14);
			char fitted[48];
			fit_text(FONT_BOLD, s->players[k].ship, name_cap, col_w, fitted, sizeof(fitted));
			text(FONT_BOLD, fitted, x, y, name_cap, C_CREAM, ALIGN_LEFT);
			y += name_cap + U(16);
			// The gun and its power.
			fit_text(FONT_SEMIBOLD, s->players[k].weapon, small, col_w, fitted, sizeof(fitted));
			text(FONT_SEMIBOLD, fitted, x, y, small, C_TAN, ALIGN_LEFT);
			y += small + U(10);
			const int count = s->players[k].power_max;
			const float pip = SDL_clamp(col_w / (count * 1.4f), L.px * 4, U(18)), pg = pip * 0.4f;
			pips(x, y, SDL_min(count, 11), SDL_min(s->players[k].power, 11), pip, pg, k == 0 ? (Colour){ 0.45f, 1.0f, 0.55f, 1 } : (Colour){ 1.0f, 0.75f, 0.35f, 1 });
			if (count > 11)
				pips(x + 11 * (pip + pg), y, count - 11, SDL_max(s->players[k].power - 11, 0), pip, pg, (Colour){ 1.0f, 0.6f, 0.25f, 1 });
			y += pip + U(14);
			// Lives, bombs, the input it plays with.
			char line[64] = "";
			if (s->players[k].lives >= 0)
				snprintf(line, sizeof(line), "Lives %d", s->players[k].lives + 1);
			if (s->players[k].bombs > 0)
				snprintf(line + strlen(line), sizeof(line) - strlen(line), "%sBombs %d", line[0] != '\0' ? "   " : "", s->players[k].bombs);
			text(FONT_MEDIUM, line, x, y, small, C_DIM, ALIGN_LEFT);
			if (s->players[k].input[0] != '\0')
				badge(x + col_w, y + (small - key * 1.9f) / 2, s->players[k].input, (Colour){ 0.32f, 0.24f, 0.16f, 0.9f }, C_TAN, ALIGN_RIGHT);
		}
		// (Between them.)
		rect((Box){ in.x + col_w + U(19), in.y, SDL_max(U(2), L.px), in.h }, with_alpha(C_RIM_BOTTOM, 0.5f), with_alpha(C_RIM_BOTTOM, 0.1f));
		return;
	}
	if (s->caption[0] != '\0' && (s->scene == UI_SCENE_NONE || !s->gauges))
	{
		text_mid(FONT_BOLD, s->caption, in, 0, CAP_ITEM(), C_CREAM, ALIGN_CENTRE);
		return;
	}
	if (s->super_title[0] != '\0' && s->scene == UI_SCENE_SHIP)
	{
		// The Super Arcade (Super Tyrian): the mode, the ship's name, its shield and armor, its main and
		// special weapons (as the original's help boxes).
		const float small = CAP_SMALL(), key = CAP_KEY(), name_cap = CAP_ITEM();
		float y = in.y;
		char title[40];
		plain_label_ui(title, s->super_title, sizeof(title));
		for (char *c = title; *c != '\0'; ++c)
			*c = (char)SDL_toupper(*c);
		text(FONT_SEMIBOLD, title, in.x, y, key, C_SUB, ALIGN_LEFT);
		y += key + U(12);
		text(FONT_BOLD, s->ship, in.x, y, name_cap, C_CREAM, ALIGN_LEFT);
		y += name_cap + U(14);
		if (s->gauges)
		{
			const float half = (in.w - U(30)) / 2, gh = SDL_max(U(34), small * 2.0f);
			labelled_gauge((Box){ in.x, y, half, gh }, SDL_max(U(110), small * 5.4f), "SHIELD", s->shield, (Colour){ 0.35f, 0.75f, 1.0f, 1 });
			labelled_gauge((Box){ in.x + half + U(30), y, half, gh }, SDL_max(U(110), small * 5.4f), "ARMOR", s->armor,
			               (Colour){ 1.0f, 0.55f, 0.25f, 1 });
			y += gh + U(12);
		}
		rule(in.x, y, in.w, with_alpha(C_RIM_BOTTOM, 0.45f));
		y += U(12);
		for (int i = 0; i < 2; ++i)
		{
			const float row = SDL_max(U(44), small * 2.3f);
			char label[40];
			plain_label_ui(label, s->super[i][0], sizeof(label));
			for (char *c = label; *c != '\0'; ++c)
				*c = (char)SDL_toupper(*c);
			const float lw = SDL_max(text_w(FONT_SEMIBOLD, label, key) + U(24), SDL_max(U(220), small * 9));
			text(FONT_SEMIBOLD, label, in.x, y + (row - key) / 2, key, C_DIM, ALIGN_LEFT);
			float x = in.x + lw;
			float pips_w = 0;
			if (i == 0 && s->power > 0)
			{
				const float pip = SDL_max(U(12), L.px * 4), pg = pip * 0.35f;
				const int count = s->power > 11 ? 15 : 11;
				pips_w = count * (pip + pg) - pg;
				pips(in.x + in.w - pips_w, y + (row - pip) / 2, count, s->power, pip, pg, C_GREEN);
				pips_w += U(16);
			}
			char fitted[48];
			fit_text(FONT_SEMIBOLD, s->super[i][1], small * 1.1f, in.x + in.w - pips_w - x, fitted, sizeof(fitted));
			text(FONT_SEMIBOLD, fitted, x, y + (row - small * 1.1f) / 2, small * 1.1f, C_CREAM, ALIGN_LEFT);
			y += row;
		}
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

// The next level's map, drawn anew in the pane (the original's map window, its screen pixels scaled): deep space,
// a faint brass grid scrolling at half the planets' pace, the routes' dots (the selected route lit as far as it has
// come), the planets (drawn anew where data/hd/icons has them), the selected destination ringed, where the ship is
// marked.
static void shop_map(const UIShop *s, Box p)
{
	const SDL_Rect box = s->picture_part;
	const float k = p.w / box.w;
	rect(p, (Colour){ 0.035f, 0.045f, 0.06f, 1 }, (Colour){ 0.015f, 0.02f, 0.03f, 1 });
	// The grid: lines every 15 of the map's pixels, at the original's places.
	const Colour line = with_alpha(C_RIM_BOTTOM, 0.22f);
	const float lw = SDL_max(L.px, U(1.5f));
	for (int i = 1; i <= 20; ++i)
	{
		const float gx = 15.0f * i - s->map_grid_x, gy = 15.0f * i - s->map_grid_y;
		if (gx > box.x && gx < box.x + box.w)
			rect((Box){ p.x + (gx - box.x) * k, p.y, lw, p.h }, line, line);
		if (gy > box.y && gy < box.y + box.h)
			rect((Box){ p.x, p.y + (gy - box.y) * k, p.w, lw }, line, line);
	}
	// The routes' dots.
	for (int i = 0; i < s->map_dot_count; ++i)
	{
		const float dx = s->map_dot[i].x, dy = s->map_dot[i].y;
		if (dx < box.x + 2 || dx > box.x + box.w - 2 || dy < box.y + 2 || dy > box.y + box.h - 2)
			continue;
		const float r = (s->map_dot[i].lit ? 1.6f : 1.1f) * k;
		const Box d = { p.x + (dx - box.x) * k - r, p.y + (dy - box.y) * k - r, 2 * r, 2 * r };
		const Colour c = s->map_dot[i].lit ? C_GOLD_TOP
		               : with_alpha(C_TAN, s->map_dot[i].route ? 0.55f : 0.3f);
		fill_octagon(d, r * 0.6f, c, mix(c, (Colour){ 0, 0, 0, c.a }, 0.35f));
	}
	// The planets, whole inside the window (the original's frame covered what reached past it).
	for (int i = 0; i < s->map_planet_count; ++i)
	{
		const float w = s->map_planet[i].w, h = s->map_planet[i].h, cx = s->map_planet[i].x, cy = s->map_planet[i].y;
		if (cx - w / 2 < box.x - 2 || cx + w / 2 > box.x + box.w + 2 || cy - h / 2 < box.y - 2 || cy + h / 2 > box.y + box.h + 2)
			continue;
		const Box b = { p.x + (cx - w / 2 - box.x) * k, p.y + (cy - h / 2 - box.y) * k, w * k, h * k };
		rgpu_ui_table_sprite(PLANET_SHAPES, (unsigned int)s->map_planet[i].sprite, b.x, b.y, b.w, b.h, L.alpha);
		if (s->map_planet[i].selected || s->map_planet[i].origin)
		{
			// A brass ring round the selected destination, pulsing; a faint one where the ship is.
			const float pulse = s->map_planet[i].selected ? 0.65f + 0.35f * sinf(SDL_GetTicks() / 260.0f) : 0.45f;
			const float pad = U(10), d = SDL_max(b.w, b.h) + 2 * pad;
			const Box ring = { b.x + b.w / 2 - d / 2, b.y + b.h / 2 - d / 2, d, d };
			rim(ring, d * 0.29f, SDL_max(U(s->map_planet[i].selected ? 4 : 2), L.px), with_alpha(C_SEL_RIM, pulse),
			    with_alpha(C_RIM_BOTTOM, pulse));
		}
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
		if (s->page == UI_SHOP_MAP && s->map_planet_count > 0)
			shop_map(s, p);
		else
			rgpu_ui_picture((float)s->picture_part.x, (float)s->picture_part.y, (float)s->picture_part.w, (float)s->picture_part.h, p.x,
			                p.y, p.w, p.h, L.alpha);
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
		const Colour c = it->disabled ? (selected ? mix(C_CREAM, C_DIM, 0.5f) : C_FAINT) : selected ? C_CREAM : saved || !slot ? C_TAN : C_DIM;
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
	const bool hover = !selected && hovered(r);
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
		// (The choice tried on the ship: "BUY", what Enter or a click on it again does.)
		const char *label = selected && !it->unaffordable && !preview ? "BUY" : "COST";
		text(FONT_SEMIBOLD, label, r.x + r.w - U(22), r.y + (r.h - vc - CAP_KEY() - U(6)) / 2, CAP_KEY(), selected ? C_SUB : C_DIM, ALIGN_RIGHT);
		text(FONT_BOLD, it->value, r.x + r.w - U(22), r.y + (r.h - vc - CAP_KEY() - U(6)) / 2 + CAP_KEY() + U(6), vc,
		     it->unaffordable ? C_COST_HIGH : selected ? C_GOLD_TOP : mix(C_GOLD_TOP, C_TAN, 0.3f), ALIGN_RIGHT);
		right_w = SDL_max(text_w(FONT_BOLD, it->value, vc), text_w(FONT_SEMIBOLD, "COST", CAP_KEY())) + U(40);
	}
	else if (it->badge[0] != '\0')  // (a data cube the store's player plays: "PLAYING", "PAUSED")
		right_w = badge(r.x + r.w - U(20), r.y + (r.h - CAP_KEY() * 1.9f) / 2, it->badge, (Colour){ 0.2f, 0.15f, 0.09f, 0.9f }, C_GOLD_TOP,
		                ALIGN_RIGHT) + U(24);
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

// The ship's parts as rows (the upgrade page): each what the ship has there, its icon, the part's name above it.
static void shop_parts(const UIMenu *m, Box area)
{
	const float cap = CAP_ITEM(), key = CAP_KEY();
	const float gap = U(8);
	const int count = m->item_count;
	const float row_h = SDL_max(SDL_min((area.h + gap) / SDL_max(count, 1) - gap, U(96)), cap + key + U(26));
	for (int i = 0; i < count; ++i)
	{
		const UIItem *it = &m->items[i];
		const Box r = { area.x, area.y + i * (row_h + gap), area.w, row_h };
		if (r.y + r.h > area.y + area.h + U(2))
			break;
		const bool selected = i == m->selected;
		panel(r, U(10), selected ? PANEL_CARD : hovered(r) ? PANEL_BAR : PANEL_HOVER);
		const float iw = r.h - U(16);
		const Box well = { r.x + U(14), r.y + U(8), iw, iw };
		panel(well, U(8), PANEL_WELL);
		item_icon(it, well, 1.0f);
		const float x = well.x + iw + U(20);
		const float y = r.y + (r.h - (key + U(8) + cap)) / 2;
		text(FONT_SEMIBOLD, it->value2, x, y, key, selected ? C_SUB : C_DIM, ALIGN_LEFT);
		char fitted[96];
		fit_text(FONT_SEMIBOLD, it->label, cap, r.x + r.w - U(24) - x, fitted, sizeof(fitted));
		text(selected ? FONT_BOLD : FONT_SEMIBOLD, fitted, x, y + key + U(8), cap, selected ? C_CREAM : C_TAN, ALIGN_LEFT);
		add_hit(r, it->hit);
	}
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
		else
			add_action(r, UI_ACTION_ITEM + i);  // (the store opens its part with it: game_menu.c)
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

static void action_button(Box b, const char *label, bool on, int action);

// The data cubes' player in the row under the left column: the previous, play or pause, the next, the
// cube playing and how far it is.
static void shop_cube_player(const UIShop *s, const ShopLayout *k)
{
	if (!s->cube_player)
		return;
	const Box p = { k->left.x, k->keys_y, k->left.w, key_hints_height() };
	panel(p, U(10), PANEL_BAR);
	const bool playing = s->cube_playing >= 0;
	const float bh = p.h - 2 * U(7), bw = bh * 1.35f, gap = U(6);
	Box b = { p.x + U(7), p.y + U(7), bw, bh };
	const float a = bh * 0.2f;
	action_button(b, "", false, UI_ACTION_PREV);
	{
		const float cx = b.x + b.w / 2, cy = b.y + b.h / 2;
		triangle(cx + a * 0.2f, cy - a, cx + a * 0.2f, cy + a, cx - a * 1.3f, cy, C_SEL_RIM);
		triangle(cx + a * 1.7f, cy - a, cx + a * 1.7f, cy + a, cx + a * 0.2f, cy, C_SEL_RIM);
	}
	b.x += bw + gap;
	action_button(b, "", playing && !s->cube_paused, UI_ACTION_PLAY_PAUSE);
	{
		const float cx = b.x + b.w / 2, cy = b.y + b.h / 2;
		const Colour c = playing && !s->cube_paused ? C_CREAM : C_SEL_RIM;
		if (playing && !s->cube_paused)
		{
			rect((Box){ cx - a * 0.85f, cy - a, a * 0.6f, a * 2 }, c, c);
			rect((Box){ cx + a * 0.25f, cy - a, a * 0.6f, a * 2 }, c, c);
		}
		else
			triangle(cx - a * 0.7f, cy - a, cx + a * 1.0f, cy, cx - a * 0.7f, cy + a, c);
	}
	b.x += bw + gap;
	action_button(b, "", false, UI_ACTION_NEXT);
	{
		const float cx = b.x + b.w / 2, cy = b.y + b.h / 2;
		triangle(cx - a * 0.2f, cy - a, cx + a * 1.3f, cy, cx - a * 0.2f, cy + a, C_SEL_RIM);
		triangle(cx - a * 1.7f, cy - a, cx - a * 0.2f, cy, cx - a * 1.7f, cy + a, C_SEL_RIM);
	}
	// What plays: "CUBE 2 / 4" and its title; the voice's progress along the foot.
	const float x = b.x + bw + U(20), right = p.x + p.w - U(20), key = CAP_KEY(), small = CAP_SMALL();
	char label[32];
	if (playing)
		snprintf(label, sizeof(label), "%s %d / %d", s->cube_paused ? "PAUSED" : "CUBE", s->cube_playing + 1, s->cube_count);
	else
		snprintf(label, sizeof(label), "DATA CUBES %d", s->cube_count);
	text(FONT_SEMIBOLD, label, x, p.y + (p.h - key) / 2, key, C_DIM, ALIGN_LEFT);
	const float tx = x + text_w(FONT_SEMIBOLD, label, key) + U(16);
	char fitted[48];
	fit_text(FONT_SEMIBOLD, playing ? s->cube_title : "Listen to the cubes", small, right - tx, fitted, sizeof(fitted));
	text(FONT_SEMIBOLD, fitted, tx, p.y + (p.h - small) / 2, small, playing ? C_CREAM : C_TAN, ALIGN_LEFT);
	if (playing)
	{
		const float lh = SDL_max(U(3), L.px * 2);
		rect((Box){ x, p.y + p.h - U(9) - lh, (right - x) * SDL_clamp(s->cube_progress, 0.0f, 1.0f), lh }, C_GOLD_TOP, C_GOLD_BOTTOM);
	}
}

static void build_shop(const UIMenu *m)
{
	const UIShop *s = &m->shop;
	const ShopLayout k = shop_layout(m);
	const float in_t = eased_in(0.22f);
	shop_left(m, &k);
	shop_cube_player(s, &k);

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
		// The parts as rows (as the original's list), "Done" at the foot.
		Box list = area;
		const float done_h = SDL_max(U(56), CAP_ITEM() * 2.15f);
		const Box done = { list.x, list.y + list.h - done_h, list.w, done_h };
		list.h -= done_h + U(12);
		shop_parts(m, list);
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
		// (The part's name is the title: no tabs, the list of its choices alone, as the original's.)
		shop_cards(m, area, false);
		break;
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
		KeyHint keys[6];
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
		if (s->cube_player)  // (the cubes' player: P, [ and ] in the store)
			keys[n++] = (KeyHint){ KEY_TEXT, "P", "Listen" };
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

// The in-game options (and their graphics page): rows as setup's, centred over the playfield; the graphics
// at its left side, the 3D view behind them bright so that what each change does shows (preview).
static void build_level_menu(const UIMenu *m)
{
	if (m->preview)
	{
		// (A little darker under the panel only.)
		const Box dark = { L.window.x, L.window.y, L.safe.x + L.safe.w * 0.55f, L.window.h };
		rect(dark, (Colour){ 0, 0, 0, 0.12f }, (Colour){ 0, 0, 0, 0.2f });
	}
	else
		level_dim(0.32f, 0.42f);
	const float cap = CAP_ITEM();
	const float row_h = SDL_max(U(52), cap * 2.1f);
	const float w = m->preview ? SDL_min(SDL_max(U(700), cap * 23), L.safe.w * 0.46f)
	                           : SDL_min(SDL_max(U(860), cap * 28), L.safe.w - U(96));
	const float head_h = U(30) + (m->crumb[0] != '\0' ? CAP_SMALL() + U(14) : 0) + CAP_TITLE() + U(24) + U(18);
	const float foot_h = CAP_SMALL() * 1.75f * 2 + U(44);
	const float keys_h = key_hints_height() + U(28);
	// (The graphics page keeps clear of the HUD's score at the playfield's foot.)
	const float room = L.window.h - U(48) - keys_h - (m->preview ? U(130) : 0);
	float rh = row_h, h = head_h + m->item_count * rh + U(12) + foot_h;
	if (h > room)
	{
		rh = SDL_max((room - head_h - foot_h - U(12)) / SDL_max(m->item_count, 1), cap * 1.55f);
		h = head_h + m->item_count * rh + U(12) + foot_h;
	}
	// (No easing in: the menus over a level are shown again only on input.)
	const float px = m->preview ? L.safe.x + U(48) : L.safe.x + (L.safe.w - w) / 2;
	const Box p = { px, m->preview ? U(24) : SDL_max((L.window.h - h - keys_h) / 2, U(24)), w, SDL_min(h, room) };
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

/* --- Stage 3's screens: the high scores, the story texts, title cards, loading, the jukebox, the
 * instructions, the credits, the rogue run ------------------------------------------------------ */

// A centred glass panel w wide and h high in the safe area, room left under it for the keys.
static Box centred_panel(float w, float h)
{
	const float keys_h = key_hints_height() + U(28);
	w = SDL_min(w, L.safe.w - U(96));
	h = SDL_min(h, L.window.h - U(48) - keys_h);
	return (Box){ snap(L.safe.x + (L.safe.w - w) / 2), snap(SDL_max((L.window.h - h - keys_h) / 2, U(24))), snap(w), snap(h) };
}

// The paging's controls: big arrows beside the panel (where the original takes the mouse on its own)
// and its pages as tabs at y (clicked: the UI's own, UI_ACTION_PAGE + n); returns the tabs' height.
static float paging_controls(const UIPaging *pg, Box p, float y)
{
	const float ah = SDL_max(U(96), CAP_ITEM() * 3.6f), aw = SDL_max(U(56), CAP_ITEM() * 2.1f);
	const float ay = p.y + (p.h - ah) / 2;
	if (pg->prev || pg->next)
	{
		const Box left = { p.x - aw - U(22), ay, aw, ah }, right = { p.x + p.w + U(22), ay, aw, ah };
		if (left.x > L.window.x + U(4))
		{
			arrow_button(left, false, pg->prev, pg->prev ? pg->hit_prev : (SDL_Rect){ 0, 0, 0, 0 });
			arrow_button(right, true, pg->next, pg->next ? pg->hit_next : (SDL_Rect){ 0, 0, 0, 0 });
		}
	}
	bool tabs_on = false;
	for (int i = 0; i < pg->count && i < UI_PAGES; ++i)
		tabs_on |= pg->tab[i][0] != '\0';
	if (!tabs_on || pg->count <= 1)
		return 0;
	// As the store's parts: spread over the width, smaller when they don't fit.
	const Box area = { p.x + U(36), y, p.w - U(72), 0 };
	float cap = CAP_SMALL(), pad = cap * 1.0f;
	const float gap = U(8);
	float total = 0;
	for (int pass = 0; pass < 3; ++pass)
	{
		total = 0;
		for (int i = 0; i < pg->count; ++i)
			total += text_w(FONT_SEMIBOLD, pg->tab[i], cap) + 2 * pad;
		total += gap * (pg->count - 1);
		if (total <= area.w)
			break;
		pad *= 0.7f;
		if (pass == 1)
			cap = SDL_max(cap * area.w / total, CAP_KEY());
	}
	const float h = SDL_max(cap * 2.5f, U(44));
	const float extra = total < area.w ? (area.w - total) / pg->count : 0;
	float x = area.x;
	for (int i = 0; i < pg->count; ++i)
	{
		const float w = text_w(FONT_SEMIBOLD, pg->tab[i], cap) + 2 * pad + extra;
		const Box t = { x, y, w, h };
		const bool selected = i == pg->index;
		panel(t, h * 0.28f, selected ? PANEL_CARD : pg->tabs_click && hovered(t) ? PANEL_BAR : PANEL_HOVER);
		text_mid(FONT_SEMIBOLD, pg->tab[i], t, 0, cap, selected ? C_CREAM : C_TAN, ALIGN_CENTRE);
		if (pg->tabs_click && !selected)
			add_action(t, UI_ACTION_PAGE + i);
		x += w + gap;
	}
	return h;
}

// A rank's medal: gold, silver, bronze.
static void rank_medal(Box b, int rank)
{
	static const Colour medal[3][2] = { { RGB(250, 214, 120), RGB(176, 128, 50) }, { RGB(226, 226, 230), RGB(130, 134, 146) },
	                                    { RGB(224, 160, 110), RGB(140, 84, 46) } };
	const int k = SDL_clamp(rank, 0, 2);
	const float cx = b.x + b.w / 2, cy = b.y + b.h / 2, r = SDL_min(b.w, b.h) * 0.5f;
	disc(cx, cy + L.px, r, (Colour){ 0, 0, 0, 0.45f });
	disc(cx, cy, r, medal[k][1]);
	disc(cx, cy - r * 0.08f, r * 0.84f, medal[k][0]);
	char n[4];
	snprintf(n, sizeof(n), "%d", rank + 1);
	text_graded(FONT_BOLD, n, cx, cy - CAP_SMALL() / 2, CAP_SMALL(), (Colour){ 0.25f, 0.16f, 0.08f, 1 }, (Colour){ 0.16f, 0.1f, 0.05f, 1 },
	            ALIGN_CENTRE, false);
}

// The difficulty's colour (0 unranked .. 10 Zinglon).
static Colour tier_colour(int tier)
{
	static const Colour c[] = { RGBA(120, 104, 84, 0.9f), RGBA(70, 120, 70, 0.92f), RGBA(110, 92, 58, 0.92f), RGBA(150, 104, 40, 0.92f),
	                            RGBA(170, 80, 40, 0.92f), RGBA(160, 50, 44, 0.92f), RGBA(130, 40, 70, 0.92f), RGBA(110, 40, 100, 0.92f) };
	return c[SDL_clamp(tier, 0, (int)COUNTOF(c) - 1)];
}

// The high scores: a board's tables (its tabs and paging, or the entry just made, highlighted).
static void build_scores(const UIMenu *m)
{
	const UIScores *s = &m->scores;
	const float cap = CAP_ITEM(), small = CAP_SMALL();
	const float row_h = SDL_max(U(58), cap * 2.3f), head_row = small + U(30);
	const bool tabs = m->paging.count > 1;
	const float head_h = U(30) + CAP_SMALL() + U(14) + CAP_TITLE() + U(24) + U(18);
	const float tabs_h = tabs ? SDL_max(CAP_SMALL() * 2.5f, U(44)) + U(22) : 0;
	const float foot_h = m->hint[0] != '\0' ? CAP_SMALL() * 1.75f + U(44) : U(20);
	float tables_h = 0;
	for (int t = 0; t < s->table_count; ++t)
		tables_h += head_row + UI_SCORE_ROWS * row_h + U(18);
	const Box p = centred_panel(SDL_max(U(1060), cap * 34), head_h + tabs_h + tables_h + foot_h + U(10));
	panel(p, U(22), PANEL_GLASS);
	float y = p.y + header(p, m->crumb, m->title);
	y += paging_controls(&m->paging, p, y);
	if (tabs)
		y += U(22);
	const float x0 = p.x + U(40), x1 = p.x + p.w - U(40);
	const float medal_w = SDL_max(U(40), small * 2.2f);
	const float score_r = x0 + medal_w + U(24) + SDL_max(U(230), cap * 8);  // the scores' right edge
	for (int t = 0; t < s->table_count; ++t)
	{
		const UIScoreTable *tb = &s->table[t];
		text(FONT_SEMIBOLD, tb->heading, x0, y + U(10), small, C_DIM, ALIGN_LEFT);
		rule(x0 + text_w(FONT_SEMIBOLD, tb->heading, small) + U(20), y + U(10) + small / 2, x1 - x0 - text_w(FONT_SEMIBOLD, tb->heading, small) - U(20),
		     with_alpha(C_RIM_BOTTOM, 0.45f));
		y += head_row;
		for (int r = 0; r < tb->count && r < UI_SCORE_ROWS; ++r)
		{
			const Box row = { p.x + U(20), y, p.w - U(40), row_h };
			const bool fresh = s->new_table == t && s->new_row == r;
			if (fresh)
				panel(inset(row, U(2)), U(10), PANEL_CARD);
			const float my = row.y + row.h / 2;
			rank_medal((Box){ x0, my - medal_w / 2, medal_w, medal_w }, r);
			text_graded(FONT_BOLD, tb->score[r], score_r, my - cap * 0.6f, cap * 1.2f, C_GOLD_TOP, C_GOLD_BOTTOM, ALIGN_RIGHT, true);
			const float name_x = score_r + U(48);
			// The difficulty as a badge at the right.
			const float bw = badge(x1, my - CAP_KEY() * 0.95f, tb->rank[r], tier_colour(tb->tier[r]), C_CREAM, ALIGN_RIGHT);
			char fitted[48];
			fit_text(FONT_SEMIBOLD, tb->name[r], cap, x1 - bw - U(30) - name_x, fitted, sizeof(fitted));
			text(fresh ? FONT_BOLD : FONT_SEMIBOLD, fitted, name_x, my - cap / 2, cap, fresh ? C_CREAM : C_TAN, ALIGN_LEFT);
			if (fresh)
				badge(name_x + text_w(FONT_BOLD, fitted, cap) + U(16), my - CAP_KEY() * 0.95f, "NEW", C_OWNED_FILL, C_OWNED_INK, ALIGN_LEFT);
			y += row_h;
		}
		y += U(18);
	}
	if (m->hint[0] != '\0')
	{
		const float foot_y = p.y + p.h - foot_h + U(10);
		rule(p.x + U(24), foot_y, p.w - U(48), with_alpha(C_RIM_BOTTOM, 0.6f));
		text_mid(FONT_MEDIUM, m->hint, (Box){ p.x, foot_y + U(6), p.w, foot_h - U(16) }, U(40), small, C_DIM, ALIGN_LEFT);
	}
	if (m->paging.label[0] != '\0')
		text(FONT_SEMIBOLD, m->paging.label, p.x + p.w - U(40), p.y + U(30), CAP_KEY(), C_DIM, ALIGN_RIGHT);
	const KeyHint browse[] = { { KEY_LEFT_RIGHT, "", "Board" }, { KEY_TEXT, "Esc", "Back" } };
	const KeyHint any[] = { { KEY_TEXT, "Any key", "Continue" } };
	// (A board alone: the entry just made, a key goes on.)
	if (s->prompt || m->paging.count <= 1)
		key_hints(any, 1, p.x + p.w / 2, p.y + p.h + U(22), ALIGN_CENTRE);
	else
		key_hints(browse, (int)COUNTOF(browse), p.x + p.w / 2, p.y + p.h + U(22), ALIGN_CENTRE);
}

/*
 * A story text's lines, laid out: the original's lines (written for its 320-pixel screen) joined into
 * paragraphs and wrapped to the panel; a line set apart by many leading spaces centred, a short line
 * in capitals a heading, a short line ending in a colon (a speaker, "Warning:") a line of its own.
 * Each character keeps where it was in the original's lines, so the text shows as far as the
 * original has revealed it.
 */
enum { STORY_BODY, STORY_HEADING, STORY_LABEL, STORY_CENTRED, STORY_GAP };
#define STORY_OUT 48
#define STORY_CHARS 160
typedef struct
{
	int style;
	int len;
	char text[STORY_CHARS];
	int src[STORY_CHARS];  // each character's place in the original's text (lines one after another)
} StoryLine;

static StoryLine story_out[STORY_OUT];

static int story_font(int style)
{
	return style == STORY_HEADING ? FONT_BOLD : style == STORY_LABEL || style == STORY_CENTRED ? FONT_SEMIBOLD : FONT_MEDIUM;
}

static int story_style_of(const char *line)
{
	int lead = 0;
	while (line[lead] == ' ')
		++lead;
	const char *t = line + lead;
	int n = (int)strlen(t);
	while (n > 0 && t[n - 1] == ' ')
		--n;
	if (n == 0)
		return STORY_GAP;
	if (lead >= 6)
		return STORY_CENTRED;
	int letters = 0, lower = 0;
	for (int i = 0; i < n; ++i)
	{
		letters += SDL_isalpha((unsigned char)t[i]) != 0;
		lower += SDL_islower((unsigned char)t[i]) != 0;
	}
	if (n <= 28 && letters >= 3 && lower == 0)
		return STORY_HEADING;
	if (n <= 44 && t[n - 1] == ':')
		return STORY_LABEL;
	return STORY_BODY;
}

// Wraps a run of characters (with their places) into lines no wider than w; returns the lines made.
static int story_wrap(const char *text, const int *src, int len, int style, float cap, float w, int out_at)
{
	int made = 0, at = 0;
	const int font = story_font(style);
	while (at < len && out_at + made < STORY_OUT)
	{
		while (at < len && text[at] == ' ')
			++at;
		if (at >= len)
			break;
		int best = 0, k = 0;
		for (;;)
		{
			while (at + k < len && text[at + k] != ' ')
				++k;
			char trial[STORY_CHARS];
			const int n = SDL_min(k, STORY_CHARS - 1);
			memcpy(trial, text + at, (size_t)n);
			trial[n] = '\0';
			if (text_w(font, trial, cap) > w && best > 0)
				break;
			best = n;
			if (at + k >= len || n >= STORY_CHARS - 1)
				break;
			++k;
		}
		StoryLine *o = &story_out[out_at + made++];
		o->style = style;
		o->len = best;
		memcpy(o->text, text + at, (size_t)best);
		o->text[best] = '\0';
		memcpy(o->src, src + at, sizeof(int) * (size_t)best);
		at += best;
	}
	return made;
}

// The story's lines from line `from` on, laid out at cap into width w; returns how many.
static int story_layout(const UIStory *s, int from, float cap, float w)
{
	int count = 0, base = 0;
	char para[STORY_CHARS * 4];
	int para_src[STORY_CHARS * 4];
	int n = 0;
	for (int i = 0; i < from && i < s->line_count; ++i)
		base += (int)strlen(s->lines[i]);
	for (int i = from; i <= s->line_count && count < STORY_OUT; ++i)
	{
		const char *line = i < s->line_count ? s->lines[i] : "";
		const int style = i < s->line_count ? story_style_of(line) : STORY_GAP;
		if (style == STORY_BODY)
		{
			// Joined to the paragraph.
			int lead = 0;
			while (line[lead] == ' ')
				++lead;
			if (n > 0 && n + 1 < (int)COUNTOF(para))
			{
				para[n] = ' ';
				para_src[n] = base + lead;
				++n;
			}
			for (int k = lead; line[k] != '\0' && n + 1 < (int)COUNTOF(para); ++k)
			{
				para[n] = line[k];
				para_src[n] = base + k;
				++n;
			}
		}
		else
		{
			// The paragraph so far ends; the line is one of its own.
			if (n > 0)
				count += story_wrap(para, para_src, n, STORY_BODY, cap, w, count);
			n = 0;
			if (style == STORY_GAP)
			{
				if (count > 0 && count < STORY_OUT && story_out[count - 1].style != STORY_GAP && i < s->line_count)
				{
					story_out[count].style = STORY_GAP;
					story_out[count].len = 0;
					story_out[count].text[0] = '\0';
					++count;
				}
			}
			else
			{
				int lead = 0, len = (int)strlen(line);
				while (line[lead] == ' ')
					++lead;
				while (len > lead && line[len - 1] == ' ')
					--len;
				int src[STORY_CHARS];
				for (int k = lead; k < len && k - lead < STORY_CHARS; ++k)
					src[k - lead] = base + k;
				count += story_wrap(line + lead, src, SDL_min(len - lead, STORY_CHARS), style, cap * (style == STORY_HEADING ? 1.08f : 1.0f), w, count);
			}
		}
		if (i < s->line_count)
			base += (int)strlen(line);
	}
	// (Without a gap at the end.)
	while (count > 0 && story_out[count - 1].style == STORY_GAP)
		--count;
	return count;
}

// How many characters of the original's text are revealed (all: a large number).
static int story_revealed(const UIStory *s)
{
	if (s->shown_line >= s->line_count)
		return 1 << 30;
	int n = 0;
	for (int i = 0; i < s->shown_line; ++i)
		n += (int)strlen(s->lines[i]);
	return n + SDL_max(s->shown_chars, 0);
}

// A laid-out line as far as revealed, its last characters fading in as the original's glow.
static void story_line_draw(const StoryLine *o, float x, float y, float cap, int revealed, Colour c, int align, float w)
{
	int shown = 0;
	while (shown < o->len && o->src[shown] < revealed)
		++shown;
	if (shown == 0)
		return;
	const int font = story_font(o->style);
	if (align == ALIGN_CENTRE)
		x += (w - text_w(font, o->text, cap)) / 2;  // (centred as the whole line will be)
	const int tail = SDL_min(shown, 5), whole = shown - tail;
	char part[STORY_CHARS];
	memcpy(part, o->text, (size_t)whole);
	part[whole] = '\0';
	text(font, part, x, y, cap, c, ALIGN_LEFT);
	for (int k = whole; k < shown; ++k)
	{
		// The fresher the fainter (only while it is being revealed).
		const int age = revealed >= (1 << 29) ? 99 : revealed - 1 - o->src[k];
		const float a = SDL_clamp(0.35f + age * 0.16f, 0.0f, 1.0f);
		memcpy(part, o->text, (size_t)k);
		part[k] = '\0';
		const float px = x + text_w(font, part, cap);
		const char one[2] = { o->text[k], '\0' };
		text(font, one, px, y, cap, with_alpha(c, a), ALIGN_LEFT);
	}
}

// The story texts between levels: in a glass panel over their picture, low on it (high for the
// original's red texts at the top); a warning's panel with a red rim and bars at the window's edges
// that pulse, as the original's alarm; an episode's end with its score, then its hint.
static void build_story(const UIMenu *m)
{
	const UIStory *s = &m->story;
	const float cap = cap_of(22, 12), line_h = cap * 1.78f;
	const float t = SDL_GetTicks() / 1000.0f;
	const float pulse = 0.5f + 0.5f * sinf(t * 5.2f);
	const Colour red = RGB(236, 84, 60);
	const bool warning = s->kind == UI_STORY_WARNING;
	if (warning)
	{
		// The alarm's bars at the window's top and bottom.
		const float bh = SDL_max(U(10), L.px * 3);
		const Colour bar = with_alpha(red, 0.35f + 0.55f * pulse);
		rect((Box){ 0, 0, L.window.w, bh }, bar, with_alpha(bar, 0.0f));
		rect((Box){ 0, L.window.h - bh, L.window.w, bh }, with_alpha(bar, 0.0f), bar);
	}
	const float w = SDL_min(SDL_max(U(1180), cap * 46), L.safe.w - U(96));
	const float tw = w - U(100);
	// The ending's scores, then the rest.
	int from = 0;
	if (s->kind == UI_STORY_ENDING)
		from = SDL_min(s->score_lines, s->line_count);
	// A warning's first line ("Warning:") is its header.
	char warn_title[64] = "";
	if (warning && s->line_count > 0 && SDL_strncasecmp(s->lines[0], "warning", 7) == 0)
	{
		plain_label_ui(warn_title, s->lines[0], sizeof(warn_title));
		from = 1;
	}
	const int count = story_layout(s, from, cap, tw);
	const int revealed = story_revealed(s);
	float body_h = 0;
	for (int i = 0; i < count; ++i)
		body_h += story_out[i].style == STORY_GAP ? line_h * 0.55f : line_h;
	const bool header_on = warning || s->kind == UI_STORY_ENDING;
	const float head_h = s->kind == UI_STORY_ENDING ? U(30) + CAP_SMALL() + U(14) + CAP_TITLE() + U(24) + U(18)
	                   : warning ? U(34) + CAP_TITLE() + U(24) + U(18) : U(34);
	(void)header_on;
	float scores_h = 0;
	if (s->kind == UI_STORY_ENDING)
		scores_h = from * SDL_max(U(64), cap * 2.6f) + U(20);
	const float keys_h = key_hints_height() + U(28);
	const float h = SDL_min(head_h + scores_h + body_h + U(44), L.window.h - U(48) - keys_h);
	Box p;
	if (s->kind == UI_STORY_ENDING)
		p = centred_panel(w, h);
	else
	{
		// Low on the picture (as the original writes it from a quarter down), or at the top.
		const float x = snap(L.safe.x + (L.safe.w - w) / 2);
		const float y = s->top ? U(54) : SDL_max(L.window.h - keys_h - U(30) - h, U(24));
		p = (Box){ x, snap(y), snap(w), snap(h) };
	}
	panel(p, U(22), PANEL_GLASS);
	if (warning)
	{
		const float rw = SDL_max(U(3), L.px);
		rim(p, U(22), rw, with_alpha(red, 0.45f + 0.5f * pulse), with_alpha(red, 0.3f + 0.4f * pulse));
	}
	float y = p.y;
	if (warning)
	{
		// An alarm's sign (pulsing), the title (the original's first line, "Warning").
		const float ct = CAP_TITLE(), ty = y + U(34);
		const float sx = p.x + U(40), sw = ct * 1.25f;
		const Colour sign = with_alpha(red, 0.55f + 0.45f * pulse);
		triangle(sx + sw / 2, ty - ct * 0.12f, sx + sw, ty + ct * 1.05f, sx, ty + ct * 1.05f, sign);
		triangle(sx + sw / 2, ty + ct * 0.14f, sx + sw - ct * 0.2f, ty + ct * 0.92f, sx + ct * 0.2f, ty + ct * 0.92f, (Colour){ 0.16f, 0.06f, 0.04f, 1 });
		rect((Box){ sx + sw / 2 - ct * 0.06f, ty + ct * 0.34f, ct * 0.12f, ct * 0.32f }, sign, sign);
		rect((Box){ sx + sw / 2 - ct * 0.06f, ty + ct * 0.72f, ct * 0.12f, ct * 0.11f }, sign, sign);
		const char *title = warn_title[0] != '\0' ? warn_title : "Warning";
		text_graded(FONT_BOLD, title, sx + sw + U(20), ty, ct, (Colour)RGB(255, 196, 150), (Colour)RGB(226, 110, 80), ALIGN_LEFT, true);
		y += head_h;
		rule(p.x + U(24), y - U(18), p.w - U(48), with_alpha(red, 0.5f));
	}
	else if (s->kind == UI_STORY_ENDING)
	{
		y += header(p, m->crumb, m->title);
		// The scores: label and value, the value large.
		for (int i = 0; i < from; ++i)
		{
			const char *line = s->lines[i];
			char label[64], value[32] = "";
			plain_label_ui(label, line, sizeof(label));
			// "Your total Score: 123456": the number at its end.
			char *end = label + strlen(label);
			while (end > label && SDL_isdigit((unsigned char)end[-1]))
				--end;
			if (*end != '\0')
			{
				char digits[32];
				SDL_strlcpy(digits, end, sizeof(digits));
				grouped(strtoul(digits, NULL, 10), value, sizeof(value));
				*end = '\0';
				plain_label_ui(label, label, sizeof(label));
			}
			const float rh = SDL_max(U(64), cap * 2.6f);
			const bool shown = revealed > 0;
			if (shown)
			{
				text(FONT_SEMIBOLD, label, p.x + U(50), y + (rh - cap) / 2, cap, C_TAN, ALIGN_LEFT);
				text_graded(FONT_BOLD, value, p.x + p.w - U(50), y + (rh - cap * 1.5f) / 2, cap * 1.5f, C_GOLD_TOP, C_GOLD_BOTTOM, ALIGN_RIGHT,
				            true);
			}
			y += rh;
		}
		rule(p.x + U(24), y + U(8), p.w - U(48), with_alpha(C_RIM_BOTTOM, 0.6f));
		y += U(20);
	}
	else
		y += U(34);
	// The text.
	const float x = p.x + U(50);
	for (int i = 0; i < count; ++i)
	{
		const StoryLine *o = &story_out[i];
		if (o->style == STORY_GAP)
		{
			y += line_h * 0.55f;
			continue;
		}
		if (y + cap > p.y + p.h - U(20))
			break;
		const Colour c = o->style == STORY_HEADING ? C_GOLD_TOP : o->style == STORY_LABEL ? C_SUB : o->style == STORY_CENTRED ? C_CREAM : C_TAN;
		story_line_draw(o, x, y, o->style == STORY_HEADING ? cap * 1.08f : cap, revealed, c,
		                o->style == STORY_CENTRED || o->style == STORY_HEADING ? ALIGN_CENTRE : ALIGN_LEFT, tw);
		y += line_h;
	}
	if (s->prompt)
	{
		const KeyHint keys[] = { { KEY_TEXT, "Any key", "Continue" } };
		const float a = L.alpha;
		L.alpha *= 0.75f + 0.25f * sinf(t * 3.0f);
		key_hints(keys, 1, p.x + p.w / 2, p.y + p.h + U(22), ALIGN_CENTRE);
		L.alpha = a;
	}
}

// A title card: the crumb, the title (gold, large for an episode's name), a sprite of the game, lines,
// a code word to type, "press a key".
static void build_card(const UIMenu *m)
{
	const UICard *c = &m->card;
	const float cap = CAP_ITEM(), small = CAP_SMALL();
	const float cap_t = c->large ? cap_of(64, 24) : CAP_TITLE();
	const float icon = c->icon_sheet != NULL ? SDL_max(U(130), L.px * 40) : 0;
	float w = SDL_max(U(860), text_w(FONT_BOLD, m->title, cap_t) + U(200));
	for (int i = 0; i < c->line_count; ++i)
		w = SDL_max(w, text_w(FONT_MEDIUM, c->lines[i], cap) + U(160));
	const float code_h = c->code[0] != '\0' ? cap * 2.8f + U(24) : 0;
	const float h = U(40) + (m->crumb[0] != '\0' ? small + U(18) : 0) + cap_t + U(40) + (icon > 0 ? icon + U(26) : 0) +
	                c->line_count * cap * 1.8f + code_h + (c->line_count > 0 || code_h > 0 ? U(40) : U(14));
	const Box p = centred_panel(w, h);
	panel(p, U(22), PANEL_GLASS);
	float y = p.y + U(40);
	const float cx = p.x + p.w / 2;
	if (m->crumb[0] != '\0')
	{
		text(FONT_SEMIBOLD, m->crumb, cx, y, small, C_DIM, ALIGN_CENTRE);
		y += small + U(18);
	}
	char title[64];
	fit_text(FONT_BOLD, m->title, cap_t, p.w - U(80), title, sizeof(title));
	text_graded(FONT_BOLD, title, cx, y, cap_t, C_GOLD_TOP, C_GOLD_BOTTOM, ALIGN_CENTRE, true);
	y += cap_t + U(22);
	const float tw = SDL_min(text_w(FONT_BOLD, title, cap_t) * 1.2f, p.w - U(120));
	rule(cx - tw / 2, y, tw, with_alpha(C_RIM_TOP, 0.8f));
	y += U(18);
	if (icon > 0)
	{
		const Box well = { cx - icon / 2, y, icon, icon };
		panel(well, U(12), PANEL_WELL);
		// (The ship's own 3D model rendered, else its sprite.)
		const bool t2000 = c->icon_sheet == (const void *)&spriteSheetT2000;
		int model = -1;
		for (int id = 1; id <= SHIP_NUM && model < 0 && (t2000 || c->icon_sheet == (const void *)&spriteSheet9); ++id)
			if (ships[id].shipgraphic == (unsigned int)c->icon_sprite + (t2000 ? 500u : 0u))
				model = shop_item_model(2, id);
		const float s = SDL_min(icon * 0.8f / 24.0f, icon * 0.8f / 28.0f);
		if (!model_icon(model, well, L.alpha))
			rgpu_ui_sprite(c->icon_sheet, (unsigned int)c->icon_sprite, true, snap(cx - 12 * s), snap(y + (icon - 28 * s) / 2), 24 * s, 28 * s,
			               L.alpha);
		y += icon + U(26);
	}
	for (int i = 0; i < c->line_count; ++i)
	{
		text(FONT_MEDIUM, c->lines[i], cx, y, cap, i == 0 ? C_CREAM : C_TAN, ALIGN_CENTRE);
		y += cap * 1.8f;
	}
	if (c->code[0] != '\0')
	{
		// The word to type, as keys.
		const float kc = cap * 1.1f;
		const float kw = text_w(FONT_BOLD, c->code, kc) + U(70), kh = cap * 2.8f;
		const Box k = { cx - kw / 2, y + U(10), kw, kh };
		panel(k, U(12), PANEL_WELL);
		text_mid(FONT_BOLD, c->code, k, 0, kc, C_GOLD_TOP, ALIGN_CENTRE);
	}
	if (c->prompt)
	{
		const KeyHint keys[] = { { KEY_TEXT, "Any key", "Continue" } };
		const float a = L.alpha;
		L.alpha *= 0.75f + 0.25f * sinf(SDL_GetTicks() / 330.0f);
		key_hints(keys, 1, cx, p.y + p.h + U(22), ALIGN_CENTRE);
		L.alpha = a;
	}
}

// Load a game (the title's): the players' pages as tabs, the slots as the store's.
static void build_load(const UIMenu *m)
{
	const float cap = CAP_ITEM();
	const float row_h = SDL_max(U(54), cap * 2.1f);
	const float head_h = U(30) + CAP_SMALL() + U(14) + CAP_TITLE() + U(24) + U(18);
	const float tabs_h = SDL_max(CAP_SMALL() * 2.5f, U(44)) + U(22);
	const float foot_h = CAP_SMALL() * 1.75f + U(44);
	const Box p = centred_panel(SDL_max(U(1080), cap * 34), head_h + tabs_h + m->item_count * row_h + U(16) + foot_h);
	panel(p, U(22), PANEL_GLASS);
	float y = p.y + header(p, m->crumb, m->title);
	y += paging_controls(&m->paging, p, y) + U(22);
	const float foot_y = p.y + p.h - foot_h + U(10);
	shop_files(m, (Box){ p.x + U(20), y, p.w - U(40), foot_y - U(12) - y });
	rule(p.x + U(24), foot_y, p.w - U(48), with_alpha(C_RIM_BOTTOM, 0.6f));
	text_mid(FONT_MEDIUM, m->hint, (Box){ p.x, foot_y + U(6), p.w, foot_h - U(16) }, U(40), CAP_SMALL(), C_DIM, ALIGN_LEFT);
	const KeyHint keys[] = { { KEY_UP_DOWN, "", "Select" }, { KEY_LEFT_RIGHT, "", "Players" }, { KEY_TEXT, "Enter", "Load" },
	                         { KEY_TEXT, "Esc", "Back" } };
	key_hints_fitted(keys, (int)COUNTOF(keys), p.x + p.w / 2, p.y + p.h + U(22), L.safe.w - U(40), ALIGN_CENTRE);
}

// A button of the UI's own with a label (or a glyph drawn by the caller), lit when on.
static void action_button(Box b, const char *label, bool on, int action)
{
	panel(b, U(10), on ? PANEL_CARD : hovered(b) ? PANEL_BAR : PANEL_HOVER);
	if (label != NULL && label[0] != '\0')
		text_mid(FONT_SEMIBOLD, label, b, 0, CAP_SMALL(), on ? C_CREAM : C_TAN, ALIGN_CENTRE);
	add_action(b, action);
}

// The jukebox: the songs in a list (a click plays one), the one playing large with its controls,
// over the stars; hidden (Space), only the stars.
static void build_jukebox(const UIMenu *m)
{
	const UIJukebox *j = &m->jukebox;
	if (j->hidden)
		return;
	const float cap = CAP_ITEM(), small = CAP_SMALL();
	const float w = SDL_min(SDL_max(U(1500), cap * 48), L.safe.w - U(96));
	const float keys_h = key_hints_height() + U(28);
	const float h = SDL_min(SDL_max(U(470), cap * 17), L.window.h * 0.56f);
	const Box p = { snap(L.safe.x + (L.safe.w - w) / 2), snap(L.window.h - keys_h - U(24) - h), snap(w), snap(h) };
	panel(p, U(22), PANEL_GLASS);
	// The list at the left.
	const float lw = p.w * 0.42f;
	const Box list = { p.x + U(20), p.y + U(24), lw - U(20), p.h - U(48) };
	const float row_h = SDL_max(U(44), small * 2.3f);
	const int fits = SDL_max((int)(list.h / row_h), 1);
	const int first = list_first(LIST_ROWS, j->song_count, j->song, fits);
	for (int i = first; i < j->song_count && i < first + fits; ++i)
	{
		const Box r = { list.x, list.y + (i - first) * row_h, list.w - U(26), row_h };
		const bool playing = i == j->song;
		if (playing)
			panel(inset(r, U(2)), U(8), PANEL_CARD);
		else if (hovered(r))
			panel(inset(r, U(2)), U(8), PANEL_HOVER);
		char n[8];
		snprintf(n, sizeof(n), "%02d", i + 1);
		text(FONT_SEMIBOLD, n, r.x + U(18), r.y + (r.h - small) / 2, small, playing ? C_SUB : C_FAINT, ALIGN_LEFT);
		char title[56];
		fit_text(FONT_SEMIBOLD, musicTitle[i], small, r.w - U(90), title, sizeof(title));
		text(playing ? FONT_BOLD : FONT_SEMIBOLD, title, r.x + U(70), r.y + (r.h - small) / 2, small, playing ? C_CREAM : C_TAN, ALIGN_LEFT);
		if (!playing)
			add_action(r, UI_ACTION_ITEM + i);
	}
	scroll_bar((Box){ list.x + list.w - U(12), list.y, U(10), fits * row_h }, first, fits, j->song_count);
	// The song playing.
	const float rx = p.x + lw + U(30), rw = p.x + p.w - U(40) - rx;
	float y = p.y + U(34);
	char count[48];
	snprintf(count, sizeof(count), "JUKEBOX    %d / %d", j->song + 1, j->song_count);
	text(FONT_SEMIBOLD, count, rx, y, small, C_DIM, ALIGN_LEFT);
	// Back (as Esc), at the top right; the visuals' look (V) beside it.
	{
		const float bw = SDL_max(U(120), text_w(FONT_SEMIBOLD, "Back", small) + U(48)), bh = small * 2.3f;
		action_button((Box){ rx + rw - bw, y + small / 2 - bh / 2, bw, bh }, "Back", false, UI_ACTION_BACK);
		if (j->look[0] != '\0')
		{
			char look[40];
			snprintf(look, sizeof(look), "Look: %s", j->look);
			const float lw = text_w(FONT_SEMIBOLD, look, small) + U(48);
			action_button((Box){ rx + rw - bw - U(12) - lw, y + small / 2 - bh / 2, lw, bh }, look, false, UI_ACTION_LOOK);
		}
	}
	y += small + U(16);
	const float cap_t = CAP_TITLE();
	char title[56];
	fit_text(FONT_BOLD, j->song >= 0 && j->song < MUSIC_NUM ? musicTitle[j->song] : "", cap_t, rw, title, sizeof(title));
	text_graded(FONT_BOLD, title, rx, y, cap_t, C_GOLD_TOP, C_GOLD_BOTTOM, ALIGN_LEFT, true);
	y += cap_t + U(14);
	text(FONT_MEDIUM, j->stopped ? "Stopped" : j->fading ? "Fading out" : "Playing", rx, y, small, j->stopped ? C_DIM : C_SUB, ALIGN_LEFT);
	y += small + U(30);
	// The controls: previous, stop or play again, next.
	const float bh = SDL_max(U(64), cap * 2.6f), bw = SDL_max(U(96), bh * 1.4f), gap = U(14);
	Box b = { rx, y, bw, bh };
	action_button(b, "", false, UI_ACTION_PREV);
	{
		const float a = bh * 0.16f, cx = b.x + b.w / 2, cy = b.y + b.h / 2;
		triangle(cx + a * 0.2f, cy - a, cx + a * 0.2f, cy + a, cx - a * 1.3f, cy, C_SEL_RIM);
		triangle(cx + a * 1.7f, cy - a, cx + a * 1.7f, cy + a, cx + a * 0.2f, cy, C_SEL_RIM);
	}
	b.x += bw + gap;
	action_button(b, "", false, j->stopped ? UI_ACTION_RESTART : UI_ACTION_STOP);
	{
		const float a = bh * 0.17f, cx = b.x + b.w / 2, cy = b.y + b.h / 2;
		if (j->stopped)
			triangle(cx - a * 0.7f, cy - a, cx + a * 1.0f, cy, cx - a * 0.7f, cy + a, C_SEL_RIM);
		else
			rect((Box){ cx - a * 0.8f, cy - a * 0.8f, a * 1.6f, a * 1.6f }, C_SEL_RIM, C_SEL_RIM);
	}
	b.x += bw + gap;
	action_button(b, "", false, UI_ACTION_NEXT);
	{
		const float a = bh * 0.16f, cx = b.x + b.w / 2, cy = b.y + b.h / 2;
		triangle(cx - a * 0.2f, cy - a, cx + a * 1.3f, cy, cx - a * 0.2f, cy + a, C_SEL_RIM);
		triangle(cx - a * 1.7f, cy - a, cx - a * 0.2f, cy, cx - a * 1.7f, cy + a, C_SEL_RIM);
	}
	// The settings: fade looped songs, fade out now.
	const float sw = SDL_min((rx + rw - (b.x + bw + U(30))) / 2 - U(8), U(260));
	if (sw > U(120))
	{
		Box t = { rx + rw - 2 * sw - U(12), y, sw, bh };
		action_button(t, "Fade loops", j->fade_looped, UI_ACTION_FADE_LOOPED);
		t.x += sw + U(12);
		action_button(t, "Fade out", j->fading, UI_ACTION_FADE);
	}
	y += bh + U(26);
	// The sound effects.
	const Box fx = { rx, y, rw, SDL_max(U(60), cap * 2.4f) };
	if (fx.y + fx.h <= p.y + p.h - U(20))
	{
		panel(fx, U(10), PANEL_WELL);
		const Box mode = { fx.x + U(8), fx.y + U(8), SDL_max(U(190), small * 9), fx.h - U(16) };
		action_button(mode, "Sound effects", j->sfx, UI_ACTION_SFX);
		if (j->sfx)
		{
			char line[48];
			snprintf(line, sizeof(line), "%d  %s", j->sfx_number + 1, j->sfx_title);
			text(FONT_SEMIBOLD, line, mode.x + mode.w + U(24), fx.y + (fx.h - small) / 2, small, C_CREAM, ALIGN_LEFT);
			const Box play = { fx.x + fx.w - U(8) - SDL_max(U(120), small * 5), mode.y, SDL_max(U(120), small * 5), mode.h };
			action_button(play, "Play", false, UI_ACTION_PLAY_SFX);
		}
		else
			text(FONT_MEDIUM, "/ switches to the sound effects", mode.x + mode.w + U(24), fx.y + (fx.h - small) / 2, small, C_DIM, ALIGN_LEFT);
	}
	const KeyHint keys[] = { { KEY_LEFT_RIGHT, "", "Song" }, { KEY_TEXT, "S", "Stop" }, { KEY_TEXT, "R", "Restart" }, { KEY_TEXT, "V", "Look" },
	                         { KEY_TEXT, "Space", "Hide" }, { KEY_TEXT, "Esc", "Back" } };
	const KeyHint fx_keys[] = { { KEY_TEXT, ",", "" }, { KEY_TEXT, ".", "Sound" }, { KEY_TEXT, ";", "Play" }, { KEY_LEFT_RIGHT, "", "Song" },
	                            { KEY_TEXT, "V", "Look" }, { KEY_TEXT, "Esc", "Back" } };
	const int look_keys = j->look[0] != '\0' ? 0 : 1;  // (no V without the visuals)
	if (look_keys == 0)
		key_hints_fitted(j->sfx ? fx_keys : keys, 6, p.x + p.w / 2, p.y + p.h + U(22), L.safe.w - U(40), ALIGN_CENTRE);
	else
	{
		const KeyHint plain[] = { keys[0], keys[1], keys[2], keys[4], keys[5] }, plain_fx[] = { fx_keys[0], fx_keys[1], fx_keys[2], fx_keys[3], fx_keys[5] };
		key_hints_fitted(j->sfx ? plain_fx : plain, 5, p.x + p.w / 2, p.y + p.h + U(22), L.safe.w - U(40), ALIGN_CENTRE);
	}
}

// The instructions' page: the topic's help texts (their titles from the original's ~highlights~), the
// page's number; the window's halves take a click as the original's screen does (back, on).
static void build_help_page(const UIMenu *m)
{
	const UIHelp *h = &m->help;
	const float small = CAP_SMALL(), cap = CAP_ITEM();
	const float head_h = U(30) + CAP_SMALL() + U(14) + CAP_TITLE() + U(24) + U(18);
	const float keys_h = key_hints_height() + U(28);
	const float w = SDL_min(SDL_max(U(1160), cap * 36), L.safe.w - U(300));
	// Each part's height from its text's lines.
	float part_h[UI_HELP_PARTS], total = 0;
	const float tw = w - U(80);
	for (int i = 0; i < h->count; ++i)
	{
		// (About: the text's width over the line's, plus its title.)
		const float lines = SDL_max(ceilf(text_w(FONT_MEDIUM, h->text[i], small) / (tw * 0.93f)), 1.0f);
		part_h[i] = (h->title[i][0] != '\0' ? cap + U(12) : 0) + lines * small * 1.75f + U(26);
		total += part_h[i];
	}
	const float foot_h = small + U(46);
	const float room = L.window.h - U(48) - keys_h;
	const float scale = head_h + total + foot_h > room ? SDL_max((room - head_h - foot_h) / SDL_max(total, 1.0f), 0.5f) : 1.0f;
	// The window's halves first (the buttons over them).
	add_hit((Box){ 0, 0, L.window.w / 2, L.window.h }, (SDL_Rect){ 0, 0, 160, 190 });
	add_hit((Box){ L.window.w / 2, 0, L.window.w / 2, L.window.h }, (SDL_Rect){ 160, 0, 160, 190 });
	const Box p = centred_panel(w, head_h + total * scale + foot_h);
	panel(p, U(22), PANEL_GLASS);
	float y = p.y + header(p, m->crumb, m->title);
	for (int i = 0; i < h->count; ++i)
	{
		const float ph = part_h[i] * scale;
		float ty = y + U(6);
		if (h->title[i][0] != '\0')
		{
			text(FONT_BOLD, h->title[i], p.x + U(40), ty, cap, C_CREAM, ALIGN_LEFT);
			ty += cap + U(12);
		}
		text_wrapped(FONT_MEDIUM, h->text[i], p.x + U(40), ty, tw, small, C_TAN, ALIGN_LEFT,
		             SDL_max((int)((y + ph - ty - U(10)) / (small * 1.75f)), 1));
		y += ph;
		if (i + 1 < h->count)
			rule(p.x + U(30), y - U(10), p.w - U(60), with_alpha(C_RIM_BOTTOM, 0.35f));
	}
	// The page's number.
	const float fy = p.y + p.h - foot_h + U(12);
	rule(p.x + U(24), fy, p.w - U(48), with_alpha(C_RIM_BOTTOM, 0.6f));
	text(FONT_SEMIBOLD, m->paging.label, p.x + p.w / 2, fy + U(18), small, C_DIM, ALIGN_CENTRE);
	const float pip = SDL_max(U(12), L.px * 4), pg = pip * 0.6f;
	const float pw = m->paging.count * pip + (m->paging.count - 1) * pg;
	pips(p.x + p.w - U(40) - pw, fy + U(18) + (small - pip) / 2, m->paging.count, m->paging.index + 1, pip, pg, C_SEL_RIM);
	paging_controls(&m->paging, p, 0);
	const KeyHint keys[] = { { KEY_LEFT_RIGHT, "", "Page" }, { KEY_TEXT, "Esc", "Back" } };
	key_hints(keys, (int)COUNTOF(keys), p.x + p.w / 2, p.y + p.h + U(22), ALIGN_CENTRE);
}

// The credits rolling: a dark column where the original writes them, each line where it is, the names
// large and cream, their parts under them in tan; fading at the column's top and bottom.
static void build_credits(const UIMenu *m)
{
	const UICredits *c = &m->credits;
	const Box pic = picture_box();
	const float k = pic.h / 200.0f;  // points per screen pixel
	const Box col = { pic.x + 6 * k, pic.y + 10 * k, 208 * k, 180 * k };
	const Colour dark = { 0.05f, 0.035f, 0.025f, 0.62f };
	rect_h((Box){ col.x - U(30), col.y, U(30), col.h }, with_alpha(dark, 0), dark);
	rect(col, dark, dark);
	rect_h((Box){ col.x + col.w, col.y, U(30), col.h }, dark, with_alpha(dark, 0));
	const float cap = SDL_max(k * 6.2f, L.px * 10);
	const float fade = 22 * k;
	// The ship flying by (the original's sprite), its 3D model's picture, fading under the bars at the top and bottom.
	if (c->ship_model >= 0)
	{
		const float side = 30 * k, x = pic.x + (c->ship_x + 12) * k - side / 2, y = pic.y + (c->ship_y + 14) * k - side / 2;
		const float a = SDL_clamp(SDL_min((y + side - col.y) / fade, (col.y + col.h - y) / fade), 0.0f, 1.0f);
		if (a > 0)
			rgpu_ui_model_icon(c->ship_model, x, y, side, side, L.alpha * a);
	}
	for (int i = 0; i < c->count; ++i)
	{
		const float x = pic.x + c->x[i] * k, y = pic.y + c->y[i] * k;
		if (y < col.y - cap || y > col.y + col.h)
			continue;
		const float a = SDL_clamp(SDL_min((y - col.y) / fade, (col.y + col.h - cap - y) / fade), 0.0f, 1.0f);
		const bool name = c->colour[i] < 0;
		const float saved = L.alpha;
		L.alpha *= a;
		char line[68];
		fit_text(name ? FONT_BOLD : FONT_MEDIUM, c->text[i], name ? cap * 1.12f : cap, col.w - U(20), line, sizeof(line));
		if (strchr(line, '*') != NULL)
			text_graded(FONT_BOLD, line, x, y, cap * 1.2f, C_GOLD_TOP, C_GOLD_BOTTOM, ALIGN_CENTRE, true);
		else
			text(name ? FONT_BOLD : FONT_MEDIUM, line, x, y, name ? cap * 1.12f : cap, name ? C_CREAM : C_TAN, ALIGN_CENTRE);
		L.alpha = saved;
	}
	if (c->note[0] != '\0')
		text(FONT_MEDIUM, c->note, pic.x + 5 * k, pic.y + 181 * k, SDL_max(k * 5.0f, L.px * 9), C_DIM, ALIGN_LEFT);
}

// The rogue run's chips (cores, runs...): small label over a value, in a row from x; returns its width.
static float rogue_chips(const UIRogue *r, float x, float y, bool right)
{
	const float cap_l = CAP_KEY(), cap_v = CAP_HEAD();
	float w = 0;
	float widths[UI_ROGUE_STATS];
	for (int i = 0; i < r->stat_count; ++i)
	{
		widths[i] = SDL_max(text_w(FONT_SEMIBOLD, r->stat_label[i], cap_l), text_w(FONT_BOLD, r->stat_value[i], cap_v)) + U(40);
		w += widths[i];
	}
	if (right)
		x -= w;
	for (int i = 0; i < r->stat_count; ++i)
	{
		text(FONT_SEMIBOLD, r->stat_label[i], x, y, cap_l, C_DIM, ALIGN_LEFT);
		text_graded(FONT_BOLD, r->stat_value[i], x, y + cap_l + U(10), cap_v, C_GOLD_TOP, C_GOLD_BOTTOM, ALIGN_LEFT, true);
		x += widths[i];
	}
	return w;
}

static const Colour C_TIER[4] = { RGB(150, 128, 98), RGB(196, 178, 140), RGB(110, 170, 240), RGB(250, 200, 90) };

// A rogue card: its tier's ribbon, its kind, the item's icon, its name and what it does, its price.
static void rogue_card(Box r, const UIItem *it, bool selected, bool show_price)
{
	const bool hover = !selected && hovered(r);
	// (Over the stars: an unselected card as solid as a bar, lit when hovered.)
	if (!selected)
		panel(r, U(14), PANEL_SOLID);
	panel(r, U(14), selected ? PANEL_CARD : hover ? PANEL_BAR : PANEL_HOVER);
	const Colour tier = C_TIER[SDL_clamp(it->tier, 0, 3)];
	// The tier's band along its top.
	const Box band_box = { r.x + U(14), r.y + U(12), r.w - U(28), SDL_max(U(6), L.px * 2) };
	rect_h(band_box, with_alpha(tier, 0.2f), tier);
	const float small = CAP_SMALL(), cap = CAP_ITEM(), key = CAP_KEY();
	float y = r.y + U(30);
	static const char *const tier_names[4] = { "", "COMMON", "RARE", "EPIC" };
	text(FONT_BOLD, tier_names[SDL_clamp(it->tier, 0, 3)], r.x + r.w / 2, y, key, tier, ALIGN_CENTRE);
	y += key + U(12);
	text(FONT_SEMIBOLD, it->badge, r.x + r.w / 2, y, small, selected ? C_SUB : C_DIM, ALIGN_CENTRE);
	y += small + U(18);
	// The icon in a well.
	const float iw = SDL_min(r.w * 0.5f, U(150));
	const Box well = { r.x + (r.w - iw) / 2, y, iw, iw };
	panel(well, U(10), PANEL_WELL);
	if (it->icon_sheet != NULL || it->icon_table > 0)
		item_icon(it, well, it->owned ? 0.45f : 1.0f);
	else
		text_mid(FONT_BOLD, it->value2[0] != '\0' ? it->value2 : "?", well, 0, cap * 1.6f, C_GOLD_TOP, ALIGN_CENTRE);
	y += iw + U(20);
	// The name and what it does.
	y += text_wrapped(FONT_BOLD, it->label, r.x + U(18), y, r.w - U(36), cap * 0.95f, it->owned ? C_DIM : selected ? C_CREAM : C_TAN, ALIGN_CENTRE,
	                  2) * 0.95f;
	y += U(6);
	if (!it->owned)
		text_wrapped(FONT_MEDIUM, it->hint, r.x + U(18), y, r.w - U(36), small, selected ? C_SUB : C_DIM, ALIGN_CENTRE, 3);
	if (show_price)
	{
		const float py = r.y + r.h - U(26) - cap;
		if (it->owned)
			badge(r.x + r.w / 2, py + (cap - CAP_KEY() * 1.9f) / 2, "SOLD", (Colour){ 0.32f, 0.24f, 0.16f, 0.9f }, C_DIM, ALIGN_CENTRE);
		else
			text(FONT_BOLD, it->value, r.x + r.w / 2, py, cap, it->unaffordable ? C_COST_HIGH : C_GOLD_TOP, ALIGN_CENTRE);
	}
}

// The rogue run's screens.
// The rogue run's sky (its screens' own backdrop, the game leaving its pixels of stars out): stars in three depths
// drifting slowly to the left, the far ones small and dim, a few twinkling, a faint warm haze low down.
static void rogue_sky(void)
{
	const Box w = L.window;
	rect((Box){ w.x, w.y + w.h * 0.55f, w.w, w.h * 0.45f }, (Colour){ 0, 0, 0, 0 }, (Colour){ 0.05f, 0.025f, 0.03f, 0.6f });
	const float t = SDL_GetTicks() / 1000.0f;
	Uint32 seed = 0x9e3779b9u;
	for (int i = 0; i < 260; ++i)
	{
		seed = seed * 1664525u + 1013904223u;
		const float rx = (seed >> 8) / 16777216.0f;
		seed = seed * 1664525u + 1013904223u;
		const float ry = (seed >> 8) / 16777216.0f;
		seed = seed * 1664525u + 1013904223u;
		const float rz = (seed >> 8) / 16777216.0f;
		const int depth = rz < 0.6f ? 0 : rz < 0.9f ? 1 : 2;
		const float speed = depth == 0 ? 0.004f : depth == 1 ? 0.009f : 0.018f;
		const float x = w.x + fmodf(rx + 1 - fmodf(t * speed, 1.0f), 1.0f) * w.w, y = w.y + ry * w.h;
		const float size = SDL_max(L.px, U(depth == 0 ? 1.6f : depth == 1 ? 2.4f : 3.4f));
		float a = depth == 0 ? 0.35f : depth == 1 ? 0.6f : 0.9f;
		if (i % 9 == 0)
			a *= 0.6f + 0.4f * sinf(t * (1.5f + rz * 3) + rx * 40);
		const Colour c = i % 13 == 0 ? (Colour){ 0.7f, 0.82f, 1, a } : i % 17 == 0 ? (Colour){ 1, 0.85f, 0.55f, a } : (Colour){ 0.92f, 0.92f, 1, a };
		fill_octagon((Box){ x - size / 2, y - size / 2, size, size }, size * 0.3f, c, c);
	}
}

// A path of the rogue run's map: dots from a to b (window points), the ends kept clear of the nodes.
static void rogue_path(float ax, float ay, float ar, float bx, float by, float br, bool flown, bool open)
{
	const float dx = bx - ax, dy = by - ay, len = sqrtf(dx * dx + dy * dy);
	if (len < 1)
		return;
	const float step = SDL_max(U(13), L.px * 3), from = ar + U(10), to = len - br - U(10);
	const Colour c = flown ? C_GOLD_TOP : with_alpha(C_TAN, open ? 0.75f : 0.35f);
	for (float d = from; d <= to; d += step)
	{
		const float r = flown ? U(3.2f) : U(2.4f);
		const float x = ax + dx / len * d, y = ay + dy / len * d;
		fill_octagon((Box){ x - r, y - r, 2 * r, 2 * r }, r * 0.6f, c, mix(c, (Colour){ 0, 0, 0, c.a }, 0.3f));
	}
}

static void build_rogue(const UIMenu *m)
{
	const UIRogue *r = &m->rogue;
	const float cap = CAP_ITEM(), small = CAP_SMALL();
	rogue_sky();
	switch (r->page)
	{
	case UI_ROGUE_MENU:
	{
		const float card_h = SDL_max(U(88), cap + small * 1.9f + U(30)), gap = U(10);
		const float head_h = U(30) + CAP_TITLE() + U(24) + U(18);
		const float stats_h = CAP_KEY() + U(10) + CAP_HEAD() + U(30);
		const float text_h = small * 1.75f * 2 + U(24);
		const Box p = centred_panel(SDL_max(U(900), cap * 29), head_h + stats_h + text_h + m->item_count * (card_h + gap) + U(24));
		panel(p, U(22), PANEL_GLASS);
		float y = p.y + header(p, "", m->title);
		rogue_chips(r, p.x + U(40), y, false);
		y += stats_h;
		for (int i = 0; i < 2; ++i)
			if (r->text[i][0] != '\0')
			{
				text(FONT_MEDIUM, r->text[i], p.x + U(40), y, small, C_TAN, ALIGN_LEFT);
				y += small * 1.75f;
			}
		y += U(24) + small * 1.75f * (r->text[1][0] == '\0' ? 1 : 0);
		for (int i = 0; i < m->item_count; ++i)
		{
			const UIItem *it = &m->items[i];
			const Box c = { p.x + U(24), y + i * (card_h + gap), p.w - U(48), card_h };
			item_card(c, it->label, it->hint, NULL, i == m->selected, it->disabled, 0);
			add_hit(c, it->hit);
		}
		const KeyHint keys[] = { { KEY_UP_DOWN, "", "Select" }, { KEY_TEXT, "Enter", "Confirm" }, { KEY_TEXT, "Esc", "Back" } };
		key_hints(keys, (int)COUNTOF(keys), p.x + p.w / 2, p.y + p.h + U(22), ALIGN_CENTRE);
		break;
	}
	case UI_ROGUE_UNLOCKS:
	{
		const float row_h = SDL_max(U(56), cap * 2.2f);
		const float head_h = U(30) + CAP_SMALL() + U(14) + CAP_TITLE() + U(24) + U(18);
		const float foot_h = small * 1.75f * 2 + U(44);
		const Box p = centred_panel(SDL_max(U(1000), cap * 32), head_h + m->item_count * row_h + U(16) + foot_h);
		panel(p, U(22), PANEL_GLASS);
		const float top = p.y + header(p, m->crumb, m->title);
		rogue_chips(r, p.x + p.w - U(40), p.y + U(30), true);
		const float foot_y = p.y + p.h - foot_h + U(10);
		const float rh = SDL_min(row_h, (foot_y - U(12) - top) / SDL_max(m->item_count, 1));
		for (int i = 0; i < m->item_count; ++i)
		{
			const UIItem *it = &m->items[i];
			const Box row = { p.x + U(16), top + i * rh, p.w - U(32), rh };
			const bool selected = i == m->selected;
			if (selected)
				panel(inset(row, U(2)), U(10), PANEL_CARD);
			else if (hovered(row))
				panel(inset(row, U(2)), U(10), PANEL_HOVER);
			text_mid(selected ? FONT_BOLD : FONT_SEMIBOLD, it->label, row, U(28), cap, it->owned ? C_DIM : selected ? C_CREAM : C_TAN, ALIGN_LEFT);
			if (it->owned)
				badge(row.x + row.w - U(22), row.y + (row.h - CAP_KEY() * 1.9f) / 2, "OWNED", C_OWNED_FILL, C_OWNED_INK, ALIGN_RIGHT);
			else
				text(FONT_BOLD, it->value, row.x + row.w - U(22), row.y + (row.h - cap) / 2, cap, it->unaffordable ? C_COST_HIGH : C_GOLD_TOP,
				     ALIGN_RIGHT);
			add_hit(row, it->hit);
		}
		rule(p.x + U(24), foot_y, p.w - U(48), with_alpha(C_RIM_BOTTOM, 0.6f));
		if (m->selected >= 0 && m->selected < m->item_count)
			text_wrapped(FONT_MEDIUM, m->items[m->selected].hint, p.x + U(40), foot_y + U(22), p.w - U(80), small, C_DIM, ALIGN_LEFT, 2);
		const KeyHint keys[] = { { KEY_UP_DOWN, "", "Select" }, { KEY_TEXT, "Enter", "Unlock" }, { KEY_TEXT, "Esc", "Back" } };
		key_hints(keys, (int)COUNTOF(keys), p.x + p.w / 2, p.y + p.h + U(22), ALIGN_CENTRE);
		break;
	}
	case UI_ROGUE_MAP:
	{
		// Over the map as the game draws it (its planets, paths and the ship): a bar at the top with the
		// act and the run's chips, the nodes' names and their state, the selected one ringed, what it is.
		const Box pic = picture_box();
		const float k = pic.h / 200.0f;
		const float bar_h = SDL_max(U(96), CAP_HEAD() + CAP_KEY() + U(50));
		const Box top = { snap(L.safe.x + U(40)), U(20), snap(L.safe.w - U(80)), snap(bar_h) };
		panel(top, U(16), PANEL_BAR);
		text_graded(FONT_BOLD, m->title, top.x + U(30), top.y + (top.h - CAP_TITLE()) / 2, CAP_TITLE(), C_GOLD_TOP, C_GOLD_BOTTOM, ALIGN_LEFT,
		            true);
		rogue_chips(r, top.x + top.w - U(10), top.y + (top.h - (CAP_KEY() + U(10) + CAP_HEAD())) / 2, true);
		// (The planets drawn anew, the map leaving its own out: 3D spheres, render_gpu.c planet3d_quad, or data/hd/icons.)
		for (int i = 0; i < r->node_count; ++i)
			if (r->nodes[i].planet >= 0)
			{
				// (The ones out of reach dimmed, as the map dims them.)
				const float pw = r->nodes[i].planet_w * k, ph = r->nodes[i].planet_h * k;
				const bool lit = r->nodes[i].can_go || r->nodes[i].visited || r->nodes[i].kind == 3;
				rgpu_ui_table_sprite(PLANET_SHAPES, (unsigned int)r->nodes[i].planet, pic.x + r->nodes[i].x * k - pw / 2,
				                     pic.y + r->nodes[i].y * k - ph / 2, pw, ph, L.alpha * (lit ? 1.0f : 0.45f));
			}
		// The paths (drawn by the UI: the game leaves them out of its picture), the ones open now brighter.
		for (int e = 0; e < r->edge_count; ++e)
		{
			const int from = r->edge[e].from, to = r->edge[e].to;
			if (to < 0 || to >= r->node_count || from >= r->node_count)
				continue;
			const float ax = pic.x + (from < 0 ? r->start_x : r->nodes[from].x) * k, ay = pic.y + (from < 0 ? r->start_y : r->nodes[from].y) * k;
			const float ar = from < 0 ? 14 * k : SDL_max(r->nodes[from].r * k, U(20));
			const float bx = pic.x + r->nodes[to].x * k, by = pic.y + r->nodes[to].y * k, br = SDL_max(r->nodes[to].r * k, U(20));
			const bool open = r->nodes[to].can_go && (from < 0 || r->nodes[from].visited);
			rogue_path(ax, ay, ar, bx, by, br, r->edge[e].flown, open);
		}
		// The ship where it is, drawn anew (the game leaves it out of the picture).
		if (r->ship_sheet != NULL)
		{
			const float sw = 24 * k * 1.25f, sh = 28 * k * 1.25f;
			rgpu_ui_sprite(r->ship_sheet, (unsigned int)r->ship_sprite, true, pic.x + r->ship_x * k - sw / 2, pic.y + r->ship_y * k - sh / 2, sw, sh,
			               L.alpha);
		}
		for (int i = 0; i < r->node_count; ++i)
		{
			const float nx = pic.x + r->nodes[i].x * k, ny = pic.y + r->nodes[i].y * k, nr = SDL_max(r->nodes[i].r * k, U(20));
			const bool lit = r->nodes[i].can_go || r->nodes[i].visited;
			const Colour kind_c = r->nodes[i].kind == 3 ? (Colour)RGB(240, 110, 90) : r->nodes[i].kind == 1 ? (Colour)RGB(250, 190, 90)
			                    : r->nodes[i].kind == 2 ? (Colour)RGB(240, 214, 140) : C_CREAM;
			if (r->nodes[i].selected)
			{
				// A brass ring round it, pulsing.
				const float pulse = 0.65f + 0.35f * sinf(SDL_GetTicks() / 260.0f);
				const Box ring = { nx - nr - U(12), ny - nr - U(12), 2 * nr + U(24), 2 * nr + U(24) };
				rim(ring, ring.w * 0.29f, SDL_max(U(4), L.px * 2), with_alpha(C_SEL_RIM, pulse), with_alpha(C_RIM_BOTTOM, pulse));
			}
			else if (r->nodes[i].can_go)
			{
				const Box ring = { nx - nr - U(8), ny - nr - U(8), 2 * nr + U(16), 2 * nr + U(16) };
				rim(ring, ring.w * 0.29f, SDL_max(U(2), L.px), with_alpha(C_RIM_TOP, 0.6f), with_alpha(C_RIM_BOTTOM, 0.6f));
			}
			// The name under it on a pill.
			const char *kind_name = r->nodes[i].kind == 1 ? "ELITE" : r->nodes[i].kind == 3 ? "BOSS" : NULL;
			const float lc = SDL_max(CAP_KEY(), L.px * 9);
			const float nw = text_w(FONT_SEMIBOLD, r->nodes[i].name, lc) + U(24), nh = lc * 2.0f;
			const Box pill = { nx - nw / 2, ny + nr + U(10), nw, nh };
			const float a = lit ? 1.0f : 0.55f;
			const float saved = L.alpha;
			L.alpha *= a;
			fill_octagon(pill, nh * 0.3f, with_alpha(C_FILL_BOTTOM, 0.85f), with_alpha(C_FILL_BOTTOM, 0.92f));
			text_mid(FONT_SEMIBOLD, r->nodes[i].name, pill, 0, lc, r->nodes[i].selected ? C_CREAM : kind_c, ALIGN_CENTRE);
			if (kind_name != NULL)
				badge(nx, pill.y + pill.h + U(6), kind_name, r->nodes[i].kind == 3 ? (Colour)RGBA(150, 50, 40, 0.92f) : (Colour)RGBA(150, 104, 40, 0.92f), C_CREAM,
				      ALIGN_CENTRE);
			L.alpha = saved;
		}
		// The selected node's line, and the keys.
		const float keys_y = L.window.h - U(24) - key_hints_height();
		if (r->info[0] != '\0')
			hint_pill(r->info, L.safe.x + L.safe.w / 2, keys_y - key_hints_height() - U(16));
		for (int i = 0; i < m->item_count; ++i)
			add_hit((Box){ pic.x + m->items[i].hit.x * k, pic.y + m->items[i].hit.y * k, m->items[i].hit.w * k, m->items[i].hit.h * k }, m->items[i].hit);
		const KeyHint keys[] = { { KEY_UP_DOWN, "", "Choose" }, { KEY_TEXT, "Enter", "Go" }, { KEY_TEXT, "Esc", "Abandon the run" } };
		key_hints(keys, (int)COUNTOF(keys), L.safe.x + L.safe.w / 2, keys_y, ALIGN_CENTRE);
		break;
	}
	case UI_ROGUE_CARDS:
	{
		// The heading in a panel at the top (a merchant's: the credits), the cards in a row under it.
		const float head_h = U(34) + CAP_TITLE() + U(14) + small + U(30);
		const float keys_y = L.window.h - U(24) - key_hints_height();
		const float tw = SDL_min(L.safe.w - U(96), SDL_max(U(1300), r->merchant ? U(1500) : U(1300)));
		const Box top = { snap(L.safe.x + (L.safe.w - tw) / 2), U(40), snap(tw), snap(head_h) };
		panel(top, U(18), PANEL_GLASS);
		text_graded(FONT_BOLD, m->title, top.x + U(40), top.y + U(34), CAP_TITLE(), C_GOLD_TOP, C_GOLD_BOTTOM, ALIGN_LEFT, true);
		text(FONT_MEDIUM, r->subheading, top.x + U(40), top.y + U(34) + CAP_TITLE() + U(14), small, C_SUB, ALIGN_LEFT);
		rogue_chips(r, top.x + top.w - U(40), top.y + (top.h - (CAP_KEY() + U(10) + CAP_HEAD())) / 2, true);
		const int n = SDL_max(m->item_count, 1);
		const float gap = U(24);
		const float area_y = top.y + top.h + U(36), area_h = keys_y - U(30) - area_y;
		float cw = SDL_min((tw - gap * (n - 1)) / n, U(360));
		// As tall as what a card holds (its texts' lines at most).
		const float iw = SDL_min(cw * 0.5f, U(150));
		const float content = U(30) + CAP_KEY() + U(12) + small + U(18) + iw + U(20) + 2 * cap * 0.95f * 1.75f + U(6) + 3 * small * 1.75f +
		                      (r->merchant ? cap + U(46) : U(24));
		const float ch = SDL_min(area_h, content);
		const float total = n * cw + (n - 1) * gap;
		float x = L.safe.x + (L.safe.w - total) / 2;
		for (int i = 0; i < m->item_count; ++i)
		{
			const Box c = { snap(x), snap(area_y + (area_h - ch) / 2), snap(cw), snap(ch) };
			rogue_card(c, &m->items[i], i == m->selected, r->merchant);
			add_hit(c, m->items[i].hit);
			x += cw + gap;
		}
		const KeyHint pick[] = { { KEY_LEFT_RIGHT, "", "Choose" }, { KEY_TEXT, "Enter", "Take the card" }, { KEY_TEXT, "Esc", "Skip (+1 000 credits)" } };
		const KeyHint buy[] = { { KEY_LEFT_RIGHT, "", "Choose" }, { KEY_TEXT, "Enter", "Buy" }, { KEY_TEXT, "Esc", "Leave" } };
		key_hints(r->merchant ? buy : pick, 3, L.safe.x + L.safe.w / 2, keys_y, ALIGN_CENTRE);
		break;
	}
	}
}

/* --- Destruct (destruct.c) ----------------------------------------------------------------- */

// A row of keys ("X|Left Shift": each a cap) and what they do after them; returns its width.
static float destruct_key_row(float x, float y, const char *keys, const char *action, Colour c)
{
	char names[24];
	SDL_strlcpy(names, keys, sizeof(names));
	const float x0 = x;
	char *next = names;
	while (next != NULL && *next != '\0')
	{
		char *bar = strchr(next, '|');
		if (bar != NULL)
			*bar = '\0';
		x += key_hint(x, y, KEY_TEXT, next, bar == NULL ? action : "", c);
		next = bar != NULL ? bar + 1 : NULL;
	}
	return x - x0;
}

// Both sides' keys in two columns, what restarts under them.
static void build_destruct_help(const UIMenu *m)
{
	const UIDestruct *d = &m->destruct;
	const float cap = CAP_ITEM(), small = CAP_SMALL(), row_h = CAP_KEY() * 2.1f + U(14);
	const float head_h = U(30) + small + U(14) + CAP_TITLE() + U(24) + U(18);
	const float col_h = cap + U(10) + small + U(22) + UI_DESTRUCT_KEYS * row_h;
	const float foot_h = small + U(46);
	const Box p = centred_panel(SDL_max(U(1180), cap * 40), head_h + col_h + U(20) + foot_h);
	panel(p, U(22), PANEL_GLASS);
	const float top = p.y + header(p, "DESTRUCT", m->title);
	const float col_w = (p.w - U(80) - U(40)) / 2;
	for (int s = 0; s < 2; ++s)
	{
		const UIDestructSide *side = &d->side[s];
		const float x = p.x + U(40) + s * (col_w + U(40));
		float y = top + U(4);
		text(FONT_BOLD, side->help_title, x, y, cap, C_CREAM, ALIGN_LEFT);
		y += cap + U(10);
		text(FONT_MEDIUM, side->help_note, x, y, small, C_DIM, ALIGN_LEFT);
		y += small + U(22);
		for (int k = 0; k < UI_DESTRUCT_KEYS; ++k)
		{
			if (side->help_key[k][0] != '\0')
				destruct_key_row(x, y, side->help_key[k], side->help_action[k], C_TAN);
			y += row_h;
		}
	}
	const float fy = p.y + p.h - foot_h + U(12);
	rule(p.x + U(24), fy, p.w - U(48), with_alpha(C_RIM_BOTTOM, 0.6f));
	text(FONT_SEMIBOLD, d->help_footer, p.x + p.w / 2, fy + U(18), small, C_DIM, ALIGN_CENTRE);
	const KeyHint keys[] = { { KEY_TEXT, "Any key", "Back to the battle" } };
	key_hints(keys, 1, p.x + p.w / 2, p.y + p.h + U(22), ALIGN_CENTRE);
}

// A thick line from a to b.
static void destruct_line(float ax, float ay, float bx, float by, float width, Colour c)
{
	const float dx = bx - ax, dy = by - ay, length = sqrtf(dx * dx + dy * dy);
	if (length <= 0)
		return;
	const float nx = -dy / length * width / 2, ny = dx / length * width / 2;
	const float x[4] = { ax + nx, bx + nx, bx - nx, ax - nx };
	const float y[4] = { ay + ny, by + ny, by - ny, ay - ny };
	const Colour cs[4] = { c, c, c, c };
	quad(x, y, cs);
}

// The barrel's angle: a quarter dial from flat to straight up, opening towards the other side.
static void destruct_dial(float cx, float cy, float r, float degrees, bool mirror, bool live)
{
	const float sign = mirror ? -1.0f : 1.0f, w = SDL_max(U(3), L.px * 1.5f);
	for (int k = 0; k < 18; ++k)
	{
		const float a0 = k * 5.0f * (float)M_PI / 180.0f, a1 = (k + 1) * 5.0f * (float)M_PI / 180.0f;
		destruct_line(cx + sign * cosf(a0) * r, cy - sinf(a0) * r, cx + sign * cosf(a1) * r, cy - sinf(a1) * r, w, C_WELL_RIM);
	}
	for (int k = 0; k <= 90; k += 15)
	{
		const float a = k * (float)M_PI / 180.0f, inner = r - U(k % 45 == 0 ? 12 : 7);
		destruct_line(cx + sign * cosf(a) * inner, cy - sinf(a) * inner, cx + sign * cosf(a) * r, cy - sinf(a) * r, w * 0.7f, C_TAN);
	}
	if (live)
	{
		const float a = SDL_clamp(degrees, 0.0f, 90.0f) * (float)M_PI / 180.0f;
		destruct_line(cx, cy, cx + sign * cosf(a) * (r - U(4)), cy - sinf(a) * (r - U(4)), w * 1.2f, C_CREAM);
	}
	disc(cx, cy, U(5), C_RIM_TOP);
}

// A side's panel at the top: who plays it and its score, the unit chosen and how many stand, its
// weapon, the barrel's angle, the power and the armor.
static void destruct_side(const UIDestruct *d, int s)
{
	const UIDestructSide *side = &d->side[s];
	const bool right = s == 1;
	const float cap = CAP_ITEM(), small = CAP_SMALL(), key = CAP_KEY();
	const float pw = SDL_min(U(540), L.safe.w * 0.31f), ph = U(136);
	const Box p = { snap(right ? L.safe.x + L.safe.w - U(20) - pw : L.safe.x + U(20)), U(14), snap(pw), ph };
	panel(p, U(16), PANEL_GLASS);
	const Colour team = right ? (Colour){ 0.45f, 0.86f, 0.45f, 1 } : (Colour){ 0.9f, 0.7f, 0.38f, 1 };
	rect((Box){ right ? p.x + p.w - U(12) : p.x + U(8), p.y + U(24), U(4), p.h - U(48) }, team, with_alpha(team, 0.6f));
	const float x = p.x + U(30);
	char who[32];
	snprintf(who, sizeof(who), "%s  -  %s", right ? "RIGHT" : "LEFT", side->cpu ? "COMPUTER" : "PLAYER");
	text(FONT_SEMIBOLD, who, x, p.y + U(14), key, C_DIM, ALIGN_LEFT);
	char score[16];
	snprintf(score, sizeof(score), "%d", side->score);
	const float sx = p.x + p.w - U(30);
	text_graded(FONT_BOLD, score, sx, p.y + U(8), cap * 1.5f, C_GOLD_TOP, C_GOLD_BOTTOM, ALIGN_RIGHT, true);
	text(FONT_SEMIBOLD, "PTS", sx - text_w(FONT_BOLD, score, cap * 1.5f) - U(12), p.y + U(18), key, C_DIM, ALIGN_RIGHT);
	// The unit, and the units standing as pips.
	text_graded(FONT_BOLD, side->unit[0] != '\0' ? side->unit : "None left", x, p.y + U(36), cap * 1.15f, C_GOLD_TOP, C_GOLD_BOTTOM,
	            ALIGN_LEFT, true);
	const float pip = SDL_max(U(12), L.px * 4);
	pips(x, p.y + U(70), SDL_min(side->units, 10), SDL_min(side->units_left, 10), pip, pip * 0.6f, team);
	// The weapon: its icon and name.
	const Box wb = { x, p.y + p.h - U(46), SDL_min(U(240), p.w * 0.46f), U(34) };
	panel(wb, U(8), PANEL_WELL);
	if (d->sheet != NULL && side->weapon_sprite > 0)
		rgpu_ui_sprite(d->sheet, (unsigned int)side->weapon_sprite, false, snap(wb.x + U(8)), snap(wb.y + (wb.h - U(29)) / 2), U(25), U(29),
		               L.alpha);
	text_mid(FONT_SEMIBOLD, side->weapon, (Box){ wb.x + U(42), wb.y, wb.w - U(48), wb.h }, 0, small, C_CREAM, ALIGN_LEFT);
	// The angle, the power, the armor.
	const float gx = wb.x + wb.w + U(22);
	const float r = U(46);
	destruct_dial(right ? gx + r + U(6) : gx + U(6), p.y + p.h - U(14), r, side->angle, right, side->aims);
	char angle[16] = "-";
	if (side->aims)
		snprintf(angle, sizeof(angle), "%d", (int)lroundf(side->angle));
	text(FONT_BOLD, angle, gx + r / 2 + U(6), p.y + U(66), small * 1.15f, side->aims ? C_CREAM : C_FAINT, ALIGN_CENTRE);
	const float bx = gx + r + U(28);
	const float bar_w = SDL_max(p.x + p.w - U(30) - bx, U(60));
	text(FONT_SEMIBOLD, "POWER", bx, p.y + U(62), key, C_DIM, ALIGN_LEFT);
	bar((Box){ bx, p.y + U(62) + key + U(6), bar_w, U(15) }, side->powered ? side->power : 0, (Colour){ 0.92f, 0.7f, 0.34f, 1 }, true);
	text(FONT_SEMIBOLD, "ARMOR", bx, p.y + U(97), key, C_DIM, ALIGN_LEFT);
	bar((Box){ bx, p.y + U(97) + key + U(6), bar_w, U(11) }, side->armor,
	    side->armor > 0.35f ? C_GREEN : (Colour){ 0.92f, 0.45f, 0.3f, 1 }, true);
}

// The battle's HUD: both sides' panels, the battle and the score between them, who won a round, keys.
static void build_destruct_hud(const UIMenu *m)
{
	const UIDestruct *d = &m->destruct;
	destruct_side(d, 0);
	destruct_side(d, 1);
	const float cap = CAP_ITEM(), key = CAP_KEY();
	const float cw = U(280), ch = U(84);
	const Box c = { snap(L.safe.x + (L.safe.w - cw) / 2), U(14), snap(cw), ch };
	panel(c, U(14), PANEL_GLASS);
	char mode[32];
	SDL_strlcpy(mode, d->mode, sizeof(mode));
	for (char *k = mode; *k != '\0'; ++k)
		*k = (char)SDL_toupper(*k);
	text(FONT_SEMIBOLD, mode, c.x + c.w / 2, c.y + U(12), key, C_DIM, ALIGN_CENTRE);
	char score[24];
	snprintf(score, sizeof(score), "%d  :  %d", d->side[0].score, d->side[1].score);
	text_graded(FONT_BOLD, score, c.x + c.w / 2, c.y + U(32), cap * 1.5f, C_GOLD_TOP, C_GOLD_BOTTOM, ALIGN_CENTRE, true);
	if (d->winner >= 0)
	{
		const char *won = d->winner == 0 ? "The left side wins the round" : "The right side wins the round";
		const float bw = text_w(FONT_BOLD, won, CAP_TITLE()) + U(120), bh = CAP_TITLE() + U(56);
		const Box b = { snap(L.safe.x + (L.safe.w - bw) / 2), snap(L.window.h * 0.36f), snap(bw), snap(bh) };
		panel(b, U(18), PANEL_GLASS);
		text_graded(FONT_BOLD, won, b.x + b.w / 2, b.y + U(28), CAP_TITLE(), C_GOLD_TOP, C_GOLD_BOTTOM, ALIGN_CENTRE, true);
	}
	const KeyHint keys[] = { { KEY_TEXT, "F1", "Help" }, { KEY_TEXT, "P", "Pause" }, { KEY_TEXT, "Bksp", "New field" },
	                         { KEY_TEXT, "Esc", "Battles" } };
	key_hints(keys, (int)COUNTOF(keys), L.safe.x + L.safe.w / 2, L.window.h - U(18) - key_hints_height(), ALIGN_CENTRE);
}

// The secrets: a panel with how many are found, their kinds as tabs (each with its share), the kind's rows
// (found: its name and a FOUND badge; locked: "???"), what the selected one is or where to look.
static void build_secrets(const UIMenu *m)
{
	const UISecrets *s = &m->secrets;
	const float cap = CAP_ITEM(), small = CAP_SMALL(), key = CAP_KEY();
	const Box p = centred_panel(SDL_max(U(1200), cap * 40), L.window.h);
	panel(p, U(22), PANEL_GLASS);
	float y = p.y + header(p, "", m->title);
	// All found, at the header's right.
	{
		char all[32];
		snprintf(all, sizeof(all), "%d / %d", s->all_found, s->all_total);
		const float x = p.x + p.w - U(40);
		text(FONT_SEMIBOLD, "FOUND", x, p.y + U(30), key, C_DIM, ALIGN_RIGHT);
		text_graded(FONT_BOLD, all, x, p.y + U(30) + key + U(10), CAP_HEAD(), C_GOLD_TOP, C_GOLD_BOTTOM, ALIGN_RIGHT, true);
	}
	// The kinds as tabs (a click goes to one: UI_ACTION_PAGE + n).
	{
		char names[UI_SECRET_TABS][40];
		const char *labels[UI_SECRET_TABS];
		const int n = SDL_min(s->tab_count, UI_SECRET_TABS);
		for (int t = 0; t < n; ++t)
		{
			snprintf(names[t], sizeof(names[t]), "%s  %d/%d", s->tab_names[t], s->found[t], s->total[t]);
			labels[t] = names[t];
		}
		float widths[UI_SECRET_TABS];
		const float th = tabs(p.x + U(40), y, labels, n, s->tab, widths);
		float x = p.x + U(40);
		for (int t = 0; t < n; ++t)
		{
			if (t != s->tab)
				add_action((Box){ x, y, widths[t], th }, UI_ACTION_PAGE + t);
			x += widths[t] + U(8);
		}
		y += th + U(22);
	}
	// The rows, scrolled to the selected one.
	const float foot_h = small * 1.75f * 2 + U(44);
	const float foot_y = p.y + p.h - foot_h + U(10);
	const Box area = { p.x + U(16), y, p.w - U(32), foot_y - U(12) - y };
	const float row_h = SDL_max(U(64), cap + small * 1.9f + U(22));
	const int fits = SDL_max((int)(area.h / row_h), 1);
	const int first = list_first(LIST_ROWS, m->item_count, m->selected, fits);
	const bool scrolls = m->item_count > fits;
	for (int i = first; i < m->item_count && i < first + fits; ++i)
	{
		const UIItem *it = &m->items[i];
		const Box row = { area.x, area.y + (i - first) * row_h, area.w - (scrolls ? U(26) : 0), row_h };
		const bool selected = i == m->selected;
		if (selected)
			panel(inset(row, U(2)), U(10), PANEL_CARD);
		else if (hovered(row))
			panel(inset(row, U(2)), U(10), PANEL_HOVER);
		add_action(row, UI_ACTION_ITEM + i);
		// The right: the share found (the data cubes), and FOUND or LOCKED.
		float right = row.x + row.w - U(22);
		const float by = row.y + (row.h - key * 1.9f) / 2;
		const bool share = it->value2[0] != '\0';
		if (it->owned)
			right -= badge(right, by, "FOUND", C_OWNED_FILL, C_OWNED_INK, ALIGN_RIGHT) + U(18);
		else if (!share)
			right -= badge(right, by, "LOCKED", (Colour){ 0.18f, 0.14f, 0.1f, 0.85f }, C_FAINT, ALIGN_RIGHT) + U(18);
		if (share)
		{
			text(FONT_BOLD, it->value2, right, row.y + (row.h - cap) / 2, cap, it->owned ? C_GOLD_TOP : C_TAN, ALIGN_RIGHT);
			right -= text_w(FONT_BOLD, it->value2, cap) + U(24);
		}
		// The left: its name (or ???) and what it is under it.
		const float x = row.x + U(28), total = cap + small * 1.9f, ty = row.y + (row.h - total) / 2;
		char fitted[64];
		fit_text(FONT_SEMIBOLD, it->label, cap, right - x, fitted, sizeof(fitted));
		text(selected ? FONT_BOLD : FONT_SEMIBOLD, fitted, x, ty, cap, it->owned || share ? (selected ? C_CREAM : C_TAN) : C_DIM, ALIGN_LEFT);
		fit_text(FONT_MEDIUM, it->value, small, right - x, fitted, sizeof(fitted));
		text(FONT_MEDIUM, fitted, x, ty + cap + small * 0.9f, small, selected ? C_SUB : C_DIM, ALIGN_LEFT);
	}
	if (scrolls)
		scroll_bar((Box){ area.x + area.w - U(12), area.y, U(10), SDL_min(fits, m->item_count - first) * row_h }, first, fits,
		           m->item_count);
	// The selected one: how it was found, or where to look.
	rule(p.x + U(24), foot_y, p.w - U(48), with_alpha(C_RIM_BOTTOM, 0.6f));
	if (m->selected >= 0 && m->selected < m->item_count)
		text_wrapped(FONT_MEDIUM, m->items[m->selected].hint, p.x + U(40), foot_y + U(22), p.w - U(80), small, C_DIM, ALIGN_LEFT, 2);
	const KeyHint keys[] = { { KEY_UP_DOWN, "", "Select" }, { KEY_LEFT_RIGHT, "", "Kind" }, { KEY_TEXT, "Esc", "Back" } };
	key_hints(keys, (int)COUNTOF(keys), p.x + p.w / 2, p.y + p.h + U(22), ALIGN_CENTRE);
}

static void build_destruct(const UIMenu *m)
{
	switch (m->destruct.page)
	{
	case UI_DESTRUCT_INTRO:
	case UI_DESTRUCT_PAUSE:
		build_card(m);
		break;
	case UI_DESTRUCT_MODES:
		build_choices(m);
		break;
	case UI_DESTRUCT_HELP:
		build_destruct_help(m);
		break;
	case UI_DESTRUCT_PLAY:
		build_destruct_hud(m);
		break;
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
	// and the screens over a level have their own; a story's picture, the jukebox's and the credits'
	// stars and pictures are what they show).
	if (published.kind == UI_SCREEN_STORY || (published.kind == UI_SCREEN_ROGUE && published.rogue.page == UI_ROGUE_MAP))
		rect(picture_box(), (Colour){ 0, 0, 0, 0.08f }, (Colour){ 0, 0, 0, 0.3f });
	else if (published.kind != UI_SCREEN_TITLE && published.kind != UI_SCREEN_JUKEBOX && published.kind != UI_SCREEN_ENDING &&
	         published.kind != UI_SCREEN_CREDITS &&
	         published.kind < UI_SCREEN_SHOP && !(published.kind == UI_SCREEN_DESTRUCT && published.destruct.page == UI_DESTRUCT_PLAY))
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
	case UI_SCREEN_SCORES:
		build_scores(&published);
		break;
	case UI_SCREEN_SCORE_NAME:
		break;  // (its question: below)
	case UI_SCREEN_STORY:
		build_story(&published);
		break;
	case UI_SCREEN_CARD:
		build_card(&published);
		break;
	case UI_SCREEN_LOAD:
		build_load(&published);
		break;
	case UI_SCREEN_JUKEBOX:
		build_jukebox(&published);
		break;
	case UI_SCREEN_HELP:
		build_help_page(&published);
		break;
	case UI_SCREEN_CREDITS:
		build_credits(&published);
		break;
	case UI_SCREEN_ROGUE:
		build_rogue(&published);
		break;
	case UI_SCREEN_DESTRUCT:
		build_destruct(&published);
		break;
	case UI_SCREEN_SECRETS:
		build_secrets(&published);
		break;
	case UI_SCREEN_ENDING:
		break;  // (the scene alone: render_gpu.c present_jukebox_scene)
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
	int ships;           // the ships' boxes (two players: both)
	Box ship_box[2];
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
	under.ships = 0;
	under.shot_count = 0;
	if (view->menu_over)
		return;
	for (int k = 0; k < (twoPlayerMode && !galagaMode ? 2 : 1); ++k)
	{
		const Player *p = &player[k];
		if (!p->is_alive)
			continue;
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
			under.ship_box[under.ships++] = (Box){ SDL_min(ax, bx), SDL_min(ay, by), SDL_fabsf(bx - ax), SDL_fabsf(by - ay) };
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
	for (int k = 0; k < under.ships && !covered; ++k)
	{
		const Box s = under.ship_box[k];
		covered = s.x + s.w > g.x && s.x < g.x + g.w && s.y + s.h > g.y && s.y < g.y + g.h;
		if (!covered)
		{
			// Near: part of the way.
			const float dx = SDL_max(SDL_max(g.x - (s.x + s.w), s.x - (g.x + g.w)), 0.0f);
			const float dy = SDL_max(SDL_max(g.y - (s.y + s.h), s.y - (g.y + g.h)), 0.0f);
			const float d = sqrtf(dx * dx + dy * dy), reach = U(110);
			if (d < reach)
				target = SDL_min(target, HUD_UNDER + (1 - HUD_UNDER) * (0.35f + 0.65f * d / reach));
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

static Uint32 insert_coin_frame = 0;
static bool insert_coin_seen = false;
static char insert_coin_text[32] = "Insert Coin";

void ui_note_insert_coin(const char *text)
{
	insert_coin_frame = l3d_frame_number;
	insert_coin_seen = true;
	if (text != NULL && text[0] != '\0')
	{
		SDL_strlcpy(insert_coin_text, text, sizeof(insert_coin_text));
		for (int i = (int)strlen(insert_coin_text) - 1; i >= 0 && insert_coin_text[i] == ' '; --i)
			insert_coin_text[i] = '\0';
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

/*
 * Two players: a player's panel at a bottom corner of the 16:9 area (player 1 the left, 2 the right):
 * the player's name and score, shield and armor, the gun the player fires (player 1 the front, player 2
 * the rear, as the game's panel shows them) and its power, player 2's sidekicks' level and charge, the
 * sidekicks' ammunition, the extra lives and super bombs. Returns its box.
 */
static Box hud_player_panel(int k, Box safe, float margin, float row_h, float label_w, const float shown[2])
{
	const Player *p = &player[k];
	const float cap = cap_of(17, 9), cap_n = cap_of(30, 14), cap_l = cap_of(15, 9);
	const float pip = SDL_max(U(18), L.px * 6), pgap = SDL_max(U(5), L.px * 2);
	const int weapon = k == 0 ? FRONT_WEAPON : REAR_WEAPON;
	const int power_now = p->items.weapon[weapon].id > 0 ? p->items.weapon[weapon].power : 0;
	const int most = power_now > 11 ? 15 : 11;
	const float pips_w = most * pip + (most - 1) * pgap;
	const float bar_w = SDL_max(U(240), pips_w);
	const bool level = k == 1 && p->items.sidekick_level >= 101 && p->items.sidekick_level <= 103;
	const bool charge = k == 1 && chargeMax > 0;
	int ammo_rows = 0;
	for (int i = 0; i < 2; ++i)
		ammo_rows += p->items.sidekick[i] > 0 && p->sidekick[i].ammo_max > 0;
	const int extra_lives = p->lives != NULL ? (int)*p->lives - 1 : 0;
	const int bombs = (int)SDL_min(p->superbombs, 10u);
	const float icon = SDL_max(U(30), L.px * 11);
	const int rows = 3 + (level ? 1 : 0) + (charge ? 1 : 0) + (ammo_rows > 0 ? 1 : 0);
	const float head_h = cap_n + U(14);
	const float lives_h = extra_lives > 0 || bombs > 0 ? icon + U(10) : 0;
	const float w = label_w + bar_w + U(40), h = U(16) + head_h + rows * row_h + lives_h + U(16);
	const Box b = { k == 0 ? safe.x + margin : safe.x + safe.w - margin - w, safe.y + safe.h - margin - h, w, h };
	panel(b, U(12), PANEL_SOLID);
	float y = b.y + U(16);
	// The player and the score.
	char name[24], score[32];
	plain_label_ui(name, miscText[48 + k], sizeof(name));
	for (char *c = name; *c != '\0'; ++c)
		*c = (char)SDL_toupper(*c);
	grouped(p->cash, score, sizeof(score));
	text(FONT_SEMIBOLD, name, b.x + U(20), y + (cap_n - cap_l) - U(2), cap_l, C_DIM, ALIGN_LEFT);
	text_graded(FONT_BOLD, score, b.x + b.w - U(20), y, cap_n, C_GOLD_TOP, C_GOLD_BOTTOM, ALIGN_RIGHT, true);
	y += head_h;
	Colour armor = { 1.0f, 0.55f, 0.25f, 1 };
	if (p->armor < 7 && (SDL_GetTicks() / 250) % 2 == 0)  // low armor flashes
		armor = (Colour){ 1.0f, 0.15f, 0.1f, 1 };
	hud_gauge(b.x + U(20), y, label_w, bar_w, row_h, "SHIELD", shown[0], (Colour){ 0.35f, 0.75f, 1.0f, 1 });
	y += row_h;
	hud_gauge(b.x + U(20), y, label_w, bar_w, row_h, "ARMOR", shown[1], armor);
	y += row_h;
	static const Colour gun[2] = { { 0.45f, 1.0f, 0.55f, 1 }, { 1.0f, 0.75f, 0.35f, 1 } };
	text(FONT_MEDIUM, k == 0 ? "FRONT" : "REAR", b.x + U(20), y + (row_h - cap) / 2, cap, (Colour){ 0.9f, 0.86f, 0.76f, 0.95f }, ALIGN_LEFT);
	pips(b.x + U(20) + label_w, y + (row_h - pip) / 2, 11, SDL_min(power_now, 11), pip, pgap, gun[weapon]);
	if (most > 11)
		pips(b.x + U(20) + label_w + 11 * (pip + pgap), y + (row_h - pip) / 2, most - 11, SDL_max(power_now - 11, 0), pip, pgap,
		     (Colour){ 1.0f, 0.6f, 0.25f, 1 });
	y += row_h;
	if (level)
	{
		text(FONT_MEDIUM, "LEVEL", b.x + U(20), y + (row_h - cap) / 2, cap, (Colour){ 0.9f, 0.86f, 0.76f, 0.95f }, ALIGN_LEFT);
		pips(b.x + U(20) + label_w, y + (row_h - pip) / 2, 3, p->items.sidekick_level - 100, pip, pgap, C_SEL_RIM);
		y += row_h;
	}
	if (charge)
	{
		text(FONT_MEDIUM, "CHARGE", b.x + U(20), y + (row_h - cap) / 2, cap, (Colour){ 0.9f, 0.86f, 0.76f, 0.95f }, ALIGN_LEFT);
		pips(b.x + U(20) + label_w, y + (row_h - pip) / 2, SDL_min((int)chargeMax, 15), SDL_min((int)chargeLevel, 15), pip, pgap,
		     (Colour){ 0.55f, 0.8f, 1.0f, 1 });
		y += row_h;
	}
	if (ammo_rows > 0)
	{
		const float aw = (bar_w - U(12)) / 2;
		text(FONT_MEDIUM, "AMMO", b.x + U(20), y + (row_h - cap) / 2, cap, (Colour){ 0.9f, 0.86f, 0.76f, 0.95f }, ALIGN_LEFT);
		for (int i = 0; i < 2; ++i)
			if (p->items.sidekick[i] > 0 && p->sidekick[i].ammo_max > 0)
			{
				const float bh = SDL_max(row_h * 0.42f, L.px * 4);
				bar((Box){ b.x + U(20) + label_w + i * (aw + U(12)), y + (row_h - bh) / 2, aw, bh }, (float)p->sidekick[i].ammo / p->sidekick[i].ammo_max,
				    (Colour){ 0x96 / 255.0f, 0x22 / 255.0f, 0x6c / 255.0f, 1 }, true);
			}
		y += row_h;
	}
	if (lives_h > 0)
	{
		float x = b.x + U(20);
		if (extra_lives > 0)
		{
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
	}
	return b;
}

// Two players: player 2's charge over the ship, as the game shows it there (its pips).
static void hud_player2_charge(void)
{
	if (twoPlayerLinked || chargeMax == 0 || !player[1].is_alive)
		return;
	float x, y;
	if (!rgpu_playfield_to_window(player[1].x + 7.0f, player[1].y - 13.0f, &x, &y))
		return;
	const float pip = SDL_max(U(9), L.px * 3), gap = pip * 0.35f;
	const int n = SDL_min((int)chargeMax, 15);
	const float w = n * pip + (n - 1) * gap;
	const Box back = { x - w / 2 - U(6), y - pip / 2 - U(6), w + U(12), pip + U(12) };
	fill_octagon(back, back.h * 0.3f, with_alpha(C_FILL_BOTTOM, 0.7f), with_alpha(C_FILL_BOTTOM, 0.8f));
	pips(x - w / 2, y - pip / 2, n, SDL_min((int)chargeLevel, 15), pip, gap, (Colour){ 0.55f, 0.8f, 1.0f, 1 });
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

	// Two players: a panel each at the bottom corners (the left player's at the left).
	float top_right_w = 0;  // (the boss bar keeps clear of it)
	const bool two = twoPlayerMode && !galagaMode && !twin_stick();  // (twin-stick: one player's, player.h)
	if (two)
	{
		static float shown2[2][2] = { { -1, -1 }, { -1, -1 } };
		for (int k = 0; k < 2; ++k)
		{
			const Player *q = &player[k];
			const float t2[2] = { q->shield_max > 0 ? (float)q->shield / q->shield_max : 0, q->armor / 28.0f };
			for (int i = 0; i < 2; ++i)
				shown2[k][i] = shown2[k][i] < 0 ? t2[i] : shown2[k][i] + (t2[i] - shown2[k][i]) * 0.25f;
			const int mark = rgpu_ui_mark();
			const Box b = hud_player_panel(k, safe, margin, row_h, label_w, shown2[k]);
			if (k == 0)
				bottom_left = b;
			else
				bottom_right = b;
			hud_fade(mark, b, &fades[k == 0 ? 2 : 0]);
		}
		if (!view->menu_over)
			hud_player2_charge();
	}

	// Bottom right: shield, armor, the generator's power; a rogue run's experience.
	if (!two)
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
	// (Twin-stick: the turret's gun, its charge and the sidekicks are player 2's: player.h.)
	if (!two)
	{
		const Player *gun_of[2] = { p, twin_stick() ? &player[1] : p }, *sk = gun_of[1];
		const bool charge = twin_stick() && chargeMax > 0;
		const float pip = SDL_max(U(20), L.px * 6), gap = SDL_max(U(5), L.px * 2);
		const int most = SDL_max(gun_of[0]->items.weapon[0].power, gun_of[1]->items.weapon[1].power) > 11 ? 15 : 11;
		const float pips_w = most * pip + (most - 1) * gap;
		int sidekick_rows = 0;
		for (int i = 0; i < 2; ++i)
			sidekick_rows += sk->items.sidekick[i] > 0 && sk->sidekick[i].ammo_max > 0;
		const int rows = 2 + (charge ? 1 : 0) + (sidekick_rows > 0);
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
			text(FONT_MEDIUM, g == 0 ? "FRONT" : twin_stick() ? "TURRET" : "REAR", b.x + U(20), y + (row_h - cap) / 2, cap,
			     (Colour){ 0.9f, 0.86f, 0.76f, 0.95f }, ALIGN_LEFT);
			const int level = gun_of[g]->items.weapon[g].id > 0 ? gun_of[g]->items.weapon[g].power : 0;
			pips(b.x + U(20) + label_w, y + (row_h - pip) / 2, 11, SDL_min(level, 11), pip, gap, gun[g]);
			if (most > 11)
				pips(b.x + U(20) + label_w + 11 * (pip + gap), y + (row_h - pip) / 2, most - 11, SDL_max(level - 11, 0), pip, gap,
				     (Colour){ 1.0f, 0.6f, 0.25f, 1 });
		}
		if (charge)
		{
			// (The turret's charge, which its shots fire with: the two players' charge.)
			const float y = b.y + U(14) + 2 * row_h;
			text(FONT_MEDIUM, "CHARGE", b.x + U(20), y + (row_h - cap) / 2, cap, (Colour){ 0.9f, 0.86f, 0.76f, 0.95f }, ALIGN_LEFT);
			pips(b.x + U(20) + label_w, y + (row_h - pip) / 2, SDL_min((int)chargeMax, 15), SDL_min((int)chargeLevel, 15), pip, gap,
			     (Colour){ 0.55f, 0.8f, 1.0f, 1 });
		}
		if (sidekick_rows > 0)
		{
			const float y = b.y + U(14) + (charge ? 3 : 2) * row_h;
			const float w = (pips_w - U(12)) / 2;
			text(FONT_MEDIUM, "AMMO", b.x + U(20), y + (row_h - cap) / 2, cap, (Colour){ 0.9f, 0.86f, 0.76f, 0.95f }, ALIGN_LEFT);
			const Colour ammo = { 0x96 / 255.0f, 0x22 / 255.0f, 0x6c / 255.0f, 1 };  // Tyrian purple, lit
			for (int i = 0; i < 2; ++i)
				if (sk->items.sidekick[i] > 0 && sk->sidekick[i].ammo_max > 0)
				{
					const float bh = SDL_max(row_h * 0.42f, L.px * 4);
					bar((Box){ b.x + U(20) + label_w + i * (w + U(12)), y + (row_h - bh) / 2, w, bh },
					    (float)sk->sidekick[i].ammo / sk->sidekick[i].ammo_max, ammo, true);
				}
		}
		hud_fade(mark, b, &fades[1]);
	}

	// Bottom left: the score (the cash), lives (arcade), super bombs, the special weapon.
	if (!two)
	{
		const float cap_l = cap_of(15, 9), cap_n = cap_of(36, 16);
		char score[32];
		// (Twin-stick: the ship's and the turret's together, as the game's score.)
		grouped(p->cash + (twin_stick() ? player[1].cash : 0), score, sizeof(score));
		const float score_w = SDL_max(text_w(FONT_BOLD, score, cap_n), U(160));
		const bool lives = onePlayerAction || twoPlayerMode;
		const int extra_lives = lives && p->lives != NULL ? (int)*p->lives - 1 : 0;
		const bool special_on = p->items.special > 0 && p->items.special < COUNTOF(special);
		const int bombs = (int)SDL_min(p->superbombs + (twin_stick() ? player[1].superbombs : 0), 10u);
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
			// The special weapon, and its ready light (the game's beside its icon): lit when it can fire. (Some specials
			// have no icon: the Lightning specials' item graphic is 0.)
			if (special[p->items.special].itemgraphic > 0)
				rgpu_ui_sprite(&spriteSheet10, special[p->items.special].itemgraphic, true, b.x + U(20), y, icon * 24 / 28.0f,
				               icon, L.alpha * (special_ready ? 1.0f : 0.55f));
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
	float message_top = -1;  // (the low-armor warning keeps clear of it)
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
			message_top = b.y;
		}
	}

	// The low-armor warning (the game draws red bars at the screen's top and bottom and a WARNING among its displays):
	// red light at the window's top and bottom edges and a WARNING over the bottom middle, pulsing faster the less
	// armor is left, as the game's warning sound repeats.
	if (armor_warning >= 0 && !view->menu_over && rgpu_ui_text_ready())
	{
		const float period = (armor_warning * 4 + 8) / 35.0f;  // seconds
		const float pulse = 0.5f + 0.5f * sinf(SDL_GetTicks() / 1000.0f * 6.2831853f / period);
		const float glow_h = U(80);
		const Colour red = { 0.92f, 0.1f, 0.05f, 0.16f + 0.22f * pulse }, clear = { 0.92f, 0.1f, 0.05f, 0 };
		rect((Box){ L.window.x, L.window.y, L.window.w, glow_h }, red, clear);
		rect((Box){ L.window.x, L.window.y + L.window.h - glow_h, L.window.w, glow_h }, clear, red);
		const float cap = cap_of(22, 12);
		const float w = text_w(FONT_BOLD, "WARNING", cap) + U(64), h = cap * 2.3f;
		// Between the bottom panels and under the message; above them where it doesn't fit between.
		const float x = safe.x + (safe.w - w) / 2;
		float y = safe.y + safe.h - margin - h - U(4);
		const float left_end = bottom_left.w > 0 ? bottom_left.x + bottom_left.w + U(16) : safe.x;
		const float right_start = bottom_right.w > 0 ? bottom_right.x - U(16) : safe.x + safe.w;
		if (x < left_end || x + w > right_start)
			y = SDL_min(bottom_left.w > 0 ? bottom_left.y : y + h, bottom_right.w > 0 ? bottom_right.y : y + h) - h - U(16);
		if (message_top >= 0)
			y = SDL_min(y, message_top - h - U(12));
		const Box b = { x, y, w, h };
		panel(b, U(10), PANEL_SOLID);
		text_mid(FONT_BOLD, "WARNING", b, 0, cap, (Colour){ 1.0f, 0.28f + 0.3f * pulse, 0.2f + 0.15f * pulse, 1 }, ALIGN_CENTRE);
	}

	// The game's notice flashing at the screen's top while displayTime runs (a warp to a secret level taken:
	// miscText[59]), which it draws among its displays: a plate at the top middle, its text glowing as it flashes.
	if (displayTime > 0 && !view->menu_over && rgpu_ui_text_ready())
	{
		char notice[48];
		plain_label_ui(notice, miscText[59], sizeof(notice));
		const float a = SDL_clamp(SDL_min(displayTime / 20.0f, (150 - displayTime) / 8.0f), 0.0f, 1.0f);
		const float pulse = 0.5f + 0.5f * sinf(SDL_GetTicks() / 160.0f);
		const float cap = cap_of(34, 16);
		const float w = text_w(FONT_BOLD, notice, cap) + U(110), h = cap * 2.4f;
		const Box b = { safe.x + (safe.w - w) / 2, safe.y + safe.h * 0.3f - h / 2 + (1 - a) * U(12), w, h };  // (under the level's name)
		L.alpha = a;
		panel(b, U(14), PANEL_SOLID);
		text_graded(FONT_BOLD, notice, b.x + b.w / 2, b.y + (h - cap) / 2, cap, mix(C_GOLD_TOP, (Colour){ 1, 1, 1, 1 }, 0.4f * pulse),
		            C_GOLD_BOTTOM, ALIGN_CENTRE, true);
		L.alpha = 1;
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

	// Insert coin: at the top while a demo plays (ui_note_insert_coin), blinking as an arcade's does.
	if (insert_coin_seen && l3d_frame_number - insert_coin_frame <= 2 && !view->menu_over)
	{
		const float cap = cap_of(40, 16);
		const float pulse = 0.7f + 0.3f * sinf(SDL_GetTicks() / 300.0f);
		L.alpha = pulse;
		text_graded(FONT_BOLD, insert_coin_text, safe.x + safe.w / 2, safe.y + safe.h * 0.05f, cap, C_GOLD_TOP, C_GOLD_BOTTOM,
		            ALIGN_CENTRE, true);
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
	return (float)settings3d.pointer_size * settings3d.ui_scale / 100.0f;
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
	const int size = SDL_clamp((int)lroundf(ui_pointer_points() / pixel), 8, 192);
	static Uint32 rgba[192 * 192];
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
