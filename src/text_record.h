/*
 * Tyrian3D: the texts the game draws on its screens (menus, messages, the store), recorded so the 3D
 * view can draw them again in a TrueType font over its own picture: where, in which font, and the
 * screen's pixels before and after (to tell the text's pixels, and whether it is still there).
 */
#ifndef TEXT_RECORD_H
#define TEXT_RECORD_H

#include <SDL3/SDL.h>

#include <stdbool.h>

#define TEXT_RECORD_MAX_W 336  // the largest rectangle a text is drawn in (screen pixels)
#define TEXT_RECORD_MAX_H 32

typedef struct
{
	int x, y, w, h;     // the rectangle the drawing changed pixels in (its shadows too)
	int text_x, text_y; // the text's own top left, its width and its glyphs' height (screen pixels)
	int text_w, text_h;
	char text[96];
	int font;           // the game's: 0 large, 1 normal, 2 tiny
	int align;          // 0 left, 1 centred, 2 right (as the game placed it)
	bool shadow_only;   // only a shadow (the text is another record)
	Uint8 before[TEXT_RECORD_MAX_W * TEXT_RECORD_MAX_H];  // the rectangle's pixels before and after, w x h
	Uint8 after[TEXT_RECORD_MAX_W * TEXT_RECORD_MAX_H];
} TextRecord;

// Around a text drawing function (nested calls are part of the outermost): alignment as the game's
// FontAlignment (0 left, 1 centred, 2 right) for x.
void text_record_begin(const SDL_Surface *surface, int x, int y, const char *text, unsigned int font, int alignment,
                       bool shadow_only);
void text_record_end(void);

// The records a screen still shows (each text's changed pixels mostly as drawn), oldest first, and
// the screen with all of them taken back (320 x 200).
int text_records_on(const SDL_Surface *screen, const TextRecord **out, int max, Uint8 *untexted);

// The texts drawn on the playfield into the overlay of the 3D frame last captured (the game's own
// coordinates: x from the playfield's left edge plus L3D_PLAYFIELD_X).
int text_records_frame(const TextRecord **out, int max);

#endif /* TEXT_RECORD_H */
