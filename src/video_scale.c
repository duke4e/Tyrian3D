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
#include "video_scale.h"

#include "video.h"

#include <string.h>

uint scaler;

const struct Scalers scalers[] =
{
	{ 1 * vga_width, 1 * vga_height, "None" },
	{ 2 * vga_width, 2 * vga_height, "2x" },
	{ 3 * vga_width, 3 * vga_height, "3x" },
	{ 4 * vga_width, 4 * vga_height, "4x" },
	{ 5 * vga_width, 5 * vga_height, "5x" },
	{ 6 * vga_width, 6 * vga_height, "6x" },
};
const uint scalers_count = COUNTOF(scalers);

void set_scaler_by_name(const char *name)
{
	for (uint i = 0; i < scalers_count; ++i)
	{
		if (strcmp(name, scalers[i].name) == 0)
		{
			scaler = i;
			return;
		}
	}

	// Software scalers from older configs ("Scale2x", "hq3x", ...) map to the same window size.
	for (const char *c = name; *c != '\0'; ++c)
	{
		if (*c >= '2' && *c <= '6')
		{
			scaler = (uint)(*c - '1');
			return;
		}
	}
}
