/*
 * OpenTyrian: A modern cross-platform port of Tyrian
 * Copyright (C) 2007-2009  The OpenTyrian Development Team
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
 */
#include "mouse.h"

#include "keyboard.h"
#include "nortvars.h"
#include "palette.h"
#include "settings3d.h"
#include "sprite.h"
#include "ui.h"
#include "video.h"
#include "vga256d.h"

#include <math.h>

#if defined(TARGET_GP2X) || defined(TARGET_DINGUX)
bool has_mouse = false;
#else
bool has_mouse = true;
#endif

bool mouseInactive = true;
JE_byte mouseCursor;
JE_word mouseX, mouseY, mouseButton;
JE_word mouseXB, mouseYB;

static JE_word mouseGrabX, mouseGrabY;
static JE_byte mouseGrabShape[24 * 28];

static void JE_drawShapeTypeOne(JE_word x, JE_word y, JE_byte *shape)
{
	JE_word xloop = 0, yloop = 0;
	JE_byte *p = shape; /* shape pointer */
	Uint8 *s;   /* screen pointer, 8-bit specific */
	Uint8 *s_limit; /* buffer boundary */

	s = (Uint8 *)VGAScreen->pixels;
	s += y * VGAScreen->pitch + x;

	s_limit = (Uint8 *)VGAScreen->pixels;
	s_limit += VGAScreen->h * VGAScreen->pitch;

	for (yloop = 0; yloop < 28; yloop++)
	{
		for (xloop = 0; xloop < 24; xloop++)
		{
			if (s >= s_limit)
				return;
			*s = *p;
			s++; p++;
		}
		s -= 24;
		s += VGAScreen->pitch;
	}
}

static void JE_grabShapeTypeOne(JE_word x, JE_word y, JE_byte *shape)
{
	JE_word xloop = 0, yloop = 0;
	JE_byte *p = shape; /* shape pointer */
	Uint8 *s;   /* screen pointer, 8-bit specific */
	Uint8 *s_limit; /* buffer boundary */

	s = (Uint8 *)VGAScreen->pixels;
	s += y * VGAScreen->pitch + x;

	s_limit = (Uint8 *)VGAScreen->pixels;
	s_limit += VGAScreen->h * VGAScreen->pitch;

	for (yloop = 0; yloop < 28; yloop++)
	{
		for (xloop = 0; xloop < 24; xloop++)
		{
			if (s >= s_limit)
				return;
			*p = *s;
			s++; p++;
		}
		s -= 24;
		s += VGAScreen->pitch;
	}
}

typedef struct
{
	Uint16 index;
	Uint8 x;
	Uint8 y;
	Uint8 w;
	Uint8 h;
	Uint8 fx;
	Uint8 fy;
} MousePointerSpriteInfo;

static const MousePointerSpriteInfo mousePointerSprites[] = // fka mouseCursorGr
{
	{ 273, 0, 0, 11, 16,  0,  0 },
	{ 275, 0, 0, 21, 16, 10,  8 },
	{ 277, 0, 0, 21, 16, 10,  7 },
	{ 279, 0, 0, 16, 21,  8, 10 },
	{ 281, 8, 0, 16, 21,  7, 10 },
};

/*
 * Tyrian3D: the pointer is the system's own, with the game's pointer picture, so it follows the
 * mouse at the display's rate instead of being drawn into the screen with each of the game's
 * frames. Screens that draw the pointer (JE_mouseStart) show it with their next frame
 * (mouse_frame_shown); others hide it. TYR3D_SOFTWARE_POINTER=1 draws it the old way.
 */
static bool native_pointer(void)
{
	static int native = -1;
	if (native < 0)
		native = SDL_getenv("TYR3D_SOFTWARE_POINTER") == NULL;
	return native;
}

static int pointer_wanted = 0;  // frames to show the pointer with
static JE_byte pointer_shape;
static Uint8 pointer_filter;

// The modern UI's pointer (ui_pointer_image): smooth, its size in window points (and a picture twice
// as large for high-density displays); made again when the shape or the size changes.
static SDL_Cursor *hd_pointer_cursor(JE_byte shape)
{
	static SDL_Cursor *cursor = NULL;
	static int made_shape = -1, made_size = 0;
	const int size = (int)lroundf(ui_pointer_points());
	if (cursor != NULL && made_shape == shape && made_size == size)
		return cursor;
	SDL_Surface *images[2] = { NULL, NULL };
	int hot_x = 0, hot_y = 0;
	for (int k = 0; k < 2; ++k)
	{
		const int s = size * (k + 1);
		images[k] = SDL_CreateSurface(s, s, SDL_PIXELFORMAT_RGBA32);
		if (images[k] == NULL)
			continue;
		int hx, hy;
		if (!ui_pointer_image(shape, s, (Uint32 *)images[k]->pixels, &hx, &hy) || images[k]->pitch != s * 4)
		{
			SDL_DestroySurface(images[k]);
			images[k] = NULL;
			continue;
		}
		if (k == 0)
		{
			hot_x = hx;
			hot_y = hy;
		}
	}
	if (images[0] != NULL && images[1] != NULL)
		SDL_AddSurfaceAlternateImage(images[0], images[1]);
	SDL_Cursor *made = images[0] != NULL ? SDL_CreateColorCursor(images[0], hot_x, hot_y) : NULL;
	for (int k = 0; k < 2; ++k)
		SDL_DestroySurface(images[k]);
	if (made != NULL)
	{
		SDL_SetCursor(made);
		if (cursor != NULL)
			SDL_DestroyCursor(cursor);
		cursor = made;
		made_shape = shape;
		made_size = size;
	}
	return cursor;
}

// The game's pointer picture as a system cursor, scale times its size (and twice that for
// high-density displays), in the current palette; made again when any of that changes. With the
// modern UI, its own smooth pointer.
static SDL_Cursor *pointer_cursor(JE_byte shape, Uint8 filter, int scale)
{
	static SDL_Cursor *cursor = NULL;
	static Uint32 made_hash = 0;

	if (ui_modern())
		return hd_pointer_cursor(shape);
	if (shopSpriteSheet.data == NULL)
		return NULL;
	const MousePointerSpriteInfo *info = &mousePointerSprites[shape];
	SDL_Surface *indexed = SDL_CreateSurface(24, 28, SDL_PIXELFORMAT_INDEX8);
	if (indexed == NULL)
		return cursor;
	SDL_FillSurfaceRect(indexed, NULL, 0);
	if (filter != 0)
		blit_sprite2x2_filter_clip(indexed, 0, 0, shopSpriteSheet, info->index, filter);
	else
		blit_sprite2x2_clip(indexed, 0, 0, shopSpriteSheet, info->index);

	Uint32 hash = 2166136261u ^ (Uint32)(scale * 31 + shape);
	Uint32 rgba[24 * 28];
	for (int y = 0; y < 28; ++y)
		for (int x = 0; x < 24; ++x)
		{
			const Uint8 index = ((const Uint8 *)indexed->pixels)[y * indexed->pitch + x];
			const SDL_Color c = colors[index];
			rgba[y * 24 + x] = index == 0 ? 0 : (Uint32)c.r | (Uint32)c.g << 8 | (Uint32)c.b << 16 | 0xff000000u;
			hash = (hash ^ rgba[y * 24 + x]) * 16777619u;
		}
	SDL_DestroySurface(indexed);
	if (cursor != NULL && hash == made_hash)
		return cursor;

	SDL_Surface *images[2] = { NULL, NULL };
	for (int k = 0; k < 2; ++k)
	{
		const int s = scale * (k + 1);
		images[k] = SDL_CreateSurface(24 * s, 28 * s, SDL_PIXELFORMAT_ABGR8888);
		if (images[k] == NULL)
			continue;
		for (int y = 0; y < 28 * s; ++y)
		{
			Uint32 *row = (Uint32 *)((Uint8 *)images[k]->pixels + y * images[k]->pitch);
			for (int x = 0; x < 24 * s; ++x)
				row[x] = rgba[(y / s) * 24 + x / s];
		}
	}
	if (images[0] != NULL && images[1] != NULL)
		SDL_AddSurfaceAlternateImage(images[0], images[1]);
	SDL_Cursor *made = images[0] != NULL ? SDL_CreateColorCursor(images[0], info->fx * scale, info->fy * scale) : NULL;
	for (int k = 0; k < 2; ++k)
		SDL_DestroySurface(images[k]);
	if (made != NULL)
	{
		SDL_SetCursor(made);
		if (cursor != NULL)
			SDL_DestroyCursor(cursor);
		cursor = made;
		made_hash = hash;
	}
	return cursor;
}

static int crosshair_wanted = 0;  // frames to show the crosshair with (mouse_show_crosshair)

// The crosshair: a ring, four ticks out of it and a dot, brass with a dark rim, a little larger than the
// modern pointer (and a picture twice as large for high-density displays); made again when the size
// changes.
static SDL_Cursor *crosshair_cursor(void)
{
	static SDL_Cursor *cursor = NULL;
	static int made_size = 0;
	// (the original pointer's size whatever Pointer Size says: it is aimed with in a level)
	const int size = SDL_max((int)lroundf(24.0f * settings3d.ui_scale / 100.0f * 1.15f), 17) | 1;  // (odd: a middle pixel)
	if (cursor != NULL && made_size == size)
		return cursor;
	SDL_Surface *images[2] = { NULL, NULL };
	for (int k = 0; k < 2; ++k)
	{
		const int s = size * (k + 1);
		images[k] = SDL_CreateSurface(s, s, SDL_PIXELFORMAT_RGBA32);
		if (images[k] == NULL)
			continue;
		const float c = (s - 1) / 2.0f, r = s * 0.27f, w = s * 0.04f + 0.35f, rim = 1.1f * (k + 1);
		const float tick_out = c - rim - 0.5f;
		for (int y = 0; y < s; ++y)
		{
			Uint8 *row = (Uint8 *)images[k]->pixels + y * images[k]->pitch;
			for (int x = 0; x < s; ++x)
			{
				// How far outside the shape (negative inside): the ring, the ticks, the dot.
				const float dx = x - c, dy = y - c, d = sqrtf(dx * dx + dy * dy);
				const float along = SDL_max(fabsf(dx), fabsf(dy)), across = SDL_min(fabsf(dx), fabsf(dy));
				float e = fabsf(d - r) - w;
				e = SDL_min(e, SDL_max(across - w, SDL_max(r - along, along - tick_out)));
				e = SDL_min(e, d - w * 1.4f);
				const float fill = SDL_clamp(0.5f - e, 0.0f, 1.0f), dark = SDL_clamp(0.5f - (e - rim), 0.0f, 1.0f) * 0.8f;
				const float a = fill + dark * (1 - fill);
				Uint8 *px = row + x * 4;
				px[0] = (Uint8)(a > 0 ? (0xf0 * fill + 0x1c * dark * (1 - fill)) / a : 0);
				px[1] = (Uint8)(a > 0 ? (0xc8 * fill + 0x13 * dark * (1 - fill)) / a : 0);
				px[2] = (Uint8)(a > 0 ? (0x6e * fill + 0x08 * dark * (1 - fill)) / a : 0);
				px[3] = (Uint8)lroundf(a * 255);
			}
		}
	}
	if (images[0] != NULL && images[1] != NULL)
		SDL_AddSurfaceAlternateImage(images[0], images[1]);
	SDL_Cursor *made = images[0] != NULL ? SDL_CreateColorCursor(images[0], size / 2, size / 2) : NULL;
	if (images[0] != NULL && SDL_getenv("TYR3D_DUMP_DIR") != NULL)  // (dev: the picture, to look at)
	{
		char path[1024];
		snprintf(path, sizeof(path), "%s/crosshair.bmp", SDL_getenv("TYR3D_DUMP_DIR"));
		SDL_SaveBMP(images[1] != NULL ? images[1] : images[0], path);
	}
	for (int k = 0; k < 2; ++k)
		SDL_DestroySurface(images[k]);
	if (made != NULL)
	{
		if (cursor != NULL)
			SDL_DestroyCursor(cursor);
		cursor = made;
		made_size = size;
	}
	return cursor;
}

void mouse_show_crosshair(void)
{
	crosshair_wanted = 2;
}

void mouse_frame_shown(void)
{
	if (!has_mouse || !native_pointer())
		return;
	if (pointer_wanted > 0 && !mouseInactive && !SDL_GetWindowRelativeMouseMode(main_window))
	{
		SDL_Cursor *cursor = pointer_cursor(pointer_shape, pointer_filter, video_pointer_scale());
		if (cursor != NULL && SDL_GetCursor() != cursor)
			SDL_SetCursor(cursor);
		SDL_ShowCursor();
		--pointer_wanted;
	}
	else if (crosshair_wanted > 0 && !SDL_GetWindowRelativeMouseMode(main_window))
	{
		// (With the keys held too: the keys fly, the mouse aims.)
		SDL_Cursor *cursor = crosshair_cursor();
		if (cursor != NULL && SDL_GetCursor() != cursor)
			SDL_SetCursor(cursor);
		SDL_ShowCursor();
		--crosshair_wanted;
	}
	else
	{
		SDL_HideCursor();
		pointer_wanted = 0;
	}
}

void JE_mouseStart(void)
{
	if (has_mouse && native_pointer())
	{
		service_SDL_events(false);
		mouseButton = mousedown ? lastmouse_but : 0; /* incorrect, possibly unimportant */
		pointer_wanted = 2;
		pointer_shape = mouseCursor;
		pointer_filter = 0;
		return;
	}

	if (has_mouse)
	{
		service_SDL_events(false);

		mouseButton = mousedown ? lastmouse_but : 0; /* incorrect, possibly unimportant */

		const MousePointerSpriteInfo *spriteInfo = &mousePointerSprites[mouseCursor];

		mouseGrabX = MIN(MAX(spriteInfo->fx, mouse_x), 320 - (spriteInfo->w - spriteInfo->fx)) - spriteInfo->fx;
		mouseGrabY = MIN(MAX(spriteInfo->fy, mouse_y), 200 - (spriteInfo->h - spriteInfo->fy)) - spriteInfo->fy;

		JE_grabShapeTypeOne(mouseGrabX, mouseGrabY, mouseGrabShape);

		if (!mouseInactive)
		{
			const Sint32 x = mouse_x - spriteInfo->x - spriteInfo->fx;
			const Sint32 y = mouse_y - spriteInfo->y - spriteInfo->fy;
			blit_sprite2x2_clip(VGAScreen, x, y, shopSpriteSheet, spriteInfo->index);
		}
	 }
}

void JE_mouseStartFilter(Uint8 filter)
{
	if (has_mouse && native_pointer())
	{
		mouseButton = mousedown ? lastmouse_but : 0; /* incorrect, possibly unimportant */
		pointer_wanted = 2;
		pointer_shape = mouseCursor;
		pointer_filter = filter;
		return;
	}

	if (has_mouse)
	{
		mouseButton = mousedown ? lastmouse_but : 0; /* incorrect, possibly unimportant */

		const MousePointerSpriteInfo *spriteInfo = &mousePointerSprites[mouseCursor];

		mouseGrabX = MIN(MAX(spriteInfo->fx, mouse_x), 320 - (spriteInfo->w - spriteInfo->fx)) - spriteInfo->fx;
		mouseGrabY = MIN(MAX(spriteInfo->fy, mouse_y), 200 - (spriteInfo->h - spriteInfo->fy)) - spriteInfo->fy;

		JE_grabShapeTypeOne(mouseGrabX, mouseGrabY, mouseGrabShape);

		if (!mouseInactive)
		{
			const Sint32 x = mouse_x - spriteInfo->x - spriteInfo->fx;
			const Sint32 y = mouse_y - spriteInfo->y - spriteInfo->fy;
			blit_sprite2x2_filter_clip(VGAScreen, x, y, shopSpriteSheet, spriteInfo->index, filter);
		}
	}
}

void JE_mouseReplace(void)
{
	if (has_mouse && !native_pointer())
		JE_drawShapeTypeOne(mouseGrabX, mouseGrabY, mouseGrabShape);
}
