/*
 * Tyrian3D: the texts the game draws on its screens. See text_record.h.
 */
#include "text_record.h"

#include "fonthand.h"
#include "layer3d.h"
#include "sprite.h"
#include "video.h"

#include <string.h>

#define RECORDS 96

static TextRecord records[RECORDS];
static int record_count = 0;

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
	if (depth++ > 0 || !recording(surface) || font > 2)
		return;
	const int width = JE_textWidth(text, font);
	if (alignment == 1)
		x -= width / 2;
	else if (alignment == 2)
		x -= width;
	TextRecord *r = &records[record_count < RECORDS ? record_count : RECORDS - 1];
	if (record_count == RECORDS)
	{
		// Full: the oldest goes.
		memmove(&records[0], &records[1], sizeof(records[0]) * (RECORDS - 1));
		r = &records[RECORDS - 1];
	}
	r->text_x = x;
	r->text_y = y;
	r->text_w = width;
	r->text_h = glyphs_height(text, font);
	SDL_strlcpy(r->text, text, sizeof(r->text));
	r->font = (int)font;
	r->shadow_only = shadow_only;
	// The text and its shadows (up to 2 pixels off), within the screen.
	r->x = SDL_max(x - 2, 0);
	r->y = SDL_max(y - 2, 0);
	r->w = SDL_min(SDL_min(x + width + 3, surface->w) - r->x, TEXT_RECORD_MAX_W);
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
	// The same text again in the same place replaces the old record.
	const int index = (int)(open - records);
	for (int i = 0; i < (record_count < RECORDS ? record_count : RECORDS - 1); ++i)
		if (i != index && records[i].text_x == open->text_x && records[i].text_y == open->text_y &&
		    records[i].font == open->font && strcmp(records[i].text, open->text) == 0)
		{
			records[i].w = 0;  // dropped (kept in place: indices stay)
		}
	if (index == record_count && record_count < RECORDS)
		++record_count;
	open = NULL;
}

int text_records_on(const SDL_Surface *screen, const TextRecord **out, int max)
{
	int count = 0;
	for (int i = 0; i < record_count && count < max; ++i)
	{
		const TextRecord *r = &records[i];
		if (r->w <= 0 || r->h <= 0)
			continue;
		int changed = 0, kept = 0;
		for (int y = 0; y < r->h; ++y)
			for (int x = 0; x < r->w; ++x)
			{
				const int k = y * r->w + x;
				if (r->after[k] == r->before[k])
					continue;
				++changed;
				kept += ((const Uint8 *)screen->pixels)[(r->y + y) * screen->pitch + r->x + x] == r->after[k];
			}
		if (changed > 0 && kept * 100 >= changed * 85)
			out[count++] = r;
	}
	return count;
}
