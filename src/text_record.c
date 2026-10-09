/*
 * Tyrian3D: the texts the game draws on its screens. See text_record.h.
 */
#include "text_record.h"

#include "fonthand.h"
#include "layer3d.h"
#include "sprite.h"
#include "video.h"

#include <stdlib.h>
#include <string.h>

#define RECORDS 256
#define TEXT_VARIANTS 3  // older drawings kept for a place (see text_record_end)

static TextRecord records[RECORDS];
static int record_count = 0;

// The texts drawn on the playfield into the 3D frame being captured (its overlay: the score, the
// players' lives...), for the frame last captured.
#define FRAME_RECORDS 32
static TextRecord frame_records[FRAME_RECORDS];
static int frame_record_count = 0;
static Uint32 frame_records_for = 0;

static TextRecord pending;      // a screen's text while it is drawn

static int depth = 0;          // nested text drawing calls
static TextRecord *open = NULL;  // the outermost call's record, while it draws
static const SDL_Surface *open_surface = NULL;

// Records are kept for the screens the game shows (not the playfield it draws a level's frames on:
// its texts are part of the 3D frame).
static bool recording(const SDL_Surface *surface)
{
	return l3d_enabled && surface != NULL && surface != game_screen && surface->w == 320 &&
	       SDL_BITSPERPIXEL(surface->format) == 8;
}

static int glyphs_height(const char *text, unsigned int font)
{
	int h = 0;
	for (; *text != '\0'; ++text)
	{
		const int sprite_id = font_ascii[(unsigned char)*text];
		if (sprite_id != -1 && sprite_exists(font, sprite_id))
			h = SDL_max(h, (int)get_sprite_height(font, sprite_id));
	}
	return h;
}

static void copy_rect(const SDL_Surface *surface, const TextRecord *r, Uint8 *out)
{
	for (int y = 0; y < r->h; ++y)
		for (int x = 0; x < r->w; ++x)
			out[y * r->w + x] = ((const Uint8 *)surface->pixels)[(r->y + y) * surface->pitch + r->x + x];
}

void text_record_begin(const SDL_Surface *surface, int x, int y, const char *text, unsigned int font, int alignment,
                       bool shadow_only)
{
	if (depth++ > 0 || font > 2)
		return;
	const bool playfield = l3d_enabled && l3d_capturing && surface == game_screen && l3d_current_layer() == L3D_OVERLAY;
	if (!playfield && !recording(surface))
		return;
	const int width = JE_textWidth(text, font);
	if (alignment == 1)
		x -= width / 2;
	else if (alignment == 2)
		x -= width;
	// (Without the spaces some texts end in: they take no pixels.)
	char trimmed[sizeof(((TextRecord *)NULL)->text)];
	SDL_strlcpy(trimmed, text, sizeof(trimmed));
	for (int i = (int)strlen(trimmed) - 1; i >= 0 && trimmed[i] == ' '; --i)
		trimmed[i] = '\0';
	text = trimmed;
	const int text_width = JE_textWidth(text, font);
	TextRecord *r;
	if (playfield)
	{
		if (frame_records_for != l3d_frame_number)
		{
			frame_records_for = l3d_frame_number;
			frame_record_count = 0;
		}
		if (frame_record_count == FRAME_RECORDS)
			return;
		r = &frame_records[frame_record_count++];
	}
	else
		r = &pending;
	r->text_x = x;
	r->text_y = y;
	r->text_w = text_width;
	r->text_h = glyphs_height(text, font);
	SDL_strlcpy(r->text, text, sizeof(r->text));
	r->font = (int)font;
	// Centred on the screen (JE_fontCenter) counts as centred too.
	r->align = alignment == 0 && abs(x + text_width / 2 - 160) <= 2 && text_width > 0 ? 1 : alignment;
	r->shadow_only = shadow_only;
	// The text and its shadows (up to 2 pixels off), within the screen.
	r->x = SDL_max(x - 2, 0);
	r->y = SDL_max(y - 2, 0);
	r->w = SDL_min(SDL_min(x + text_width + 3, surface->w) - r->x, TEXT_RECORD_MAX_W);
	r->h = SDL_min(SDL_min(y + r->text_h + 3, surface->h) - r->y, TEXT_RECORD_MAX_H);
	if (r->w <= 0 || r->h <= 0 || text[0] == '\0')
		return;
	copy_rect(surface, r, r->before);
	open = r;
	open_surface = surface;
}

void text_record_end(void)
{
	if (--depth > 0 || open == NULL)
		return;
	copy_rect(open_surface, open, open->after);
	if (open >= frame_records && open < frame_records + FRAME_RECORDS)
	{
		open = NULL;
		return;
	}
	open = NULL;
	// A text drawn again in the same place (menus redraw their items, highlighted or not): where it
	// was drawn over the old text, what was there before that is its "before" (so taking it back
	// leaves no pixel text). The same drawing replaces the old record; a different one (the item
	// highlighted) is kept beside it, as the screen may show either again (a few per place).
	TextRecord *r = &pending;
	int variants = 0;
	for (int i = record_count - 1; i >= 0; --i)
	{
		TextRecord *old = &records[i];
		if (old->text_x != r->text_x || old->text_y != r->text_y || old->font != r->font)
			continue;
		for (int y = 0; y < r->h; ++y)
			for (int x = 0; x < r->w; ++x)
			{
				const int ox = r->x + x - old->x, oy = r->y + y - old->y;
				if (ox < 0 || oy < 0 || ox >= old->w || oy >= old->h)
					continue;
				const int k = y * r->w + x, ok = oy * old->w + ox;
				if (old->after[ok] != old->before[ok] && r->before[k] == old->after[ok])
					r->before[k] = old->before[ok];
			}
		const bool same = old->x == r->x && old->y == r->y && old->w == r->w && old->h == r->h &&
		                  strcmp(old->text, r->text) == 0 && memcmp(old->after, r->after, (size_t)(r->w * r->h)) == 0;
		if (same || ++variants > TEXT_VARIANTS)
		{
			memmove(&records[i], &records[i + 1], sizeof(records[0]) * (size_t)(record_count - i - 1));
			--record_count;
		}
	}
	if (record_count == RECORDS)
	{
		// Full: the oldest goes.
		memmove(&records[0], &records[1], sizeof(records[0]) * (RECORDS - 1));
		--record_count;
	}
	records[record_count++] = *r;
}

// Of a record's changed pixels, how many (per cent) a picture shows as the text drew them.
static int kept_percent(const TextRecord *r, const Uint8 *pixels, int pitch)
{
	int changed = 0, kept = 0;
	for (int y = 0; y < r->h; ++y)
		for (int x = 0; x < r->w; ++x)
		{
			const int k = y * r->w + x;
			if (r->after[k] == r->before[k])
				continue;
			++changed;
			kept += pixels[(r->y + y) * pitch + r->x + x] == r->after[k];
		}
	return changed > 0 ? kept * 100 / changed : 0;
}

int text_records_on(const SDL_Surface *screen, const TextRecord **out, int max, Uint8 *untexted)
{
	for (int y = 0; y < 200; ++y)
		memcpy(untexted + y * 320, (const Uint8 *)screen->pixels + y * screen->pitch, 320);
	// Newest first: a text taken back shows what was under it, maybe an older text, taken back next.
	static const TextRecord *found[RECORDS], *taken[RECORDS];
	int count = 0, taken_count = 0;
	for (int i = record_count - 1; i >= 0; --i)
	{
		const TextRecord *r = &records[i];
		if (r->w <= 0 || r->h <= 0 || r->y + r->h > 200)
			continue;
		// One drawing per place: an older one there is what the newer was drawn over.
		bool place_taken = false;
		for (int k = 0; k < taken_count && !place_taken; ++k)
			place_taken = taken[k]->text_x == r->text_x && taken[k]->text_y == r->text_y && taken[k]->font == r->font;
		if (place_taken || kept_percent(r, untexted, 320) < 85)
			continue;
		taken[taken_count++] = r;
		const bool shown = kept_percent(r, (const Uint8 *)screen->pixels, screen->pitch) >= 60;

		for (int y = 0; y < r->h; ++y)
			for (int x = 0; x < r->w; ++x)
			{
				const int k = y * r->w + x;
				Uint8 *pixel = &untexted[(r->y + y) * 320 + r->x + x];
				if (r->after[k] != r->before[k] && *pixel == r->after[k])
					*pixel = r->before[k];
			}
		if (shown)
			found[count++] = r;
	}
	// Oldest first, as they were drawn.
	int n = 0;
	for (int i = count - 1; i >= 0 && n < max; --i)
		out[n++] = found[i];
	return n;
}

int text_records_frame(const TextRecord **out, int max)
{
	if (frame_records_for != l3d_frame_number)
		return 0;
	int count = 0;
	for (int i = 0; i < frame_record_count && count < max; ++i)
		if (frame_records[i].w > 0 && frame_records[i].h > 0)
			out[count++] = &frame_records[i];
	return count;
}
