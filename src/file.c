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
#include "file.h"

#include "opentyr.h"
#include "varz.h"

#include <SDL3/SDL.h>

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

const char *custom_data_dir = NULL;

static const char *found_data_dir = NULL;

// Tyrian3D: the folder the player chose for the game's data (data_dir_ask), remembered in the
// user's application support folder (Tyrian3D/data_dir.txt).
static const char *remembered_data_dir(void)
{
	static char remembered[1024];
	char *pref = SDL_GetPrefPath("", "Tyrian3D");
	if (pref == NULL)
		return NULL;
	char path[1200];
	SDL_snprintf(path, sizeof(path), "%sdata_dir.txt", pref);
	SDL_free(pref);
	FILE *f = fopen(path, "r");
	if (f == NULL)
		return NULL;
	const bool read = fgets(remembered, sizeof(remembered), f) != NULL;
	fclose(f);
	if (!read)
		return NULL;
	remembered[strcspn(remembered, "\r\n")] = '\0';
	return remembered[0] != '\0' ? remembered : NULL;
}

bool data_dir_found(void)
{
	return data_dir()[0] != '\0';
}

static bool chosen_dir_done;
static char chosen_dir[1024];

static void SDLCALL chosen_folder(void *user, const char *const *files, int filter)
{
	(void)user, (void)filter;
	if (files != NULL && files[0] != NULL)
		SDL_strlcpy(chosen_dir, files[0], sizeof(chosen_dir));
	chosen_dir_done = true;
}

bool data_dir_ask(void)
{
	if (data_dir_found())
		return true;
	if (!SDL_InitSubSystem(SDL_INIT_VIDEO))
		return false;
	for (;;)
	{
		SDL_ShowSimpleMessageBox(SDL_MESSAGEBOX_INFORMATION, "Tyrian3D",
		                         "Tyrian3D plays the data of Tyrian 2000 (freeware), which it doesn't include.\n\n"
		                         "Choose the folder that has the game's files (tyrian1.lvl and the rest).", NULL);
		chosen_dir_done = false;
		chosen_dir[0] = '\0';
		SDL_ShowOpenFolderDialog(chosen_folder, NULL, NULL, NULL, false);
		while (!chosen_dir_done)
		{
			SDL_Event event;
			SDL_WaitEventTimeout(&event, 50);
		}
		if (chosen_dir[0] == '\0')
			return false;  // cancelled
		if (dir_file_exists(chosen_dir, "tyrian1.lvl"))
			break;
		SDL_ShowSimpleMessageBox(SDL_MESSAGEBOX_WARNING, "Tyrian3D",
		                         "That folder doesn't have the game's files (tyrian1.lvl). Please choose another.", NULL);
	}

	char *pref = SDL_GetPrefPath("", "Tyrian3D");
	if (pref != NULL)
	{
		char path[1200];
		SDL_snprintf(path, sizeof(path), "%sdata_dir.txt", pref);
		SDL_free(pref);
		FILE *f = fopen(path, "w");
		if (f != NULL)
		{
			fprintf(f, "%s\n", chosen_dir);
			fclose(f);
		}
	}
	found_data_dir = NULL;  // look again
	custom_data_dir = chosen_dir;
	return data_dir_found();
}

// finds the Tyrian data directory
const char *data_dir(void)
{
	// Tyrian3D: an app bundle looks for the game's data in its Resources ("data"), in the user's
	// application support folder (Tyrian3D/data), beside the app and in the folder the player chose
	// (data_dir_ask).
	static char bundled[1024], user[1024], beside[1024];
	const char *base = SDL_GetBasePath();
	SDL_snprintf(bundled, sizeof(bundled), "%sdata", base != NULL ? base : "");
	char *pref = SDL_GetPrefPath("", "Tyrian3D");
	SDL_snprintf(user, sizeof(user), "%sdata", pref != NULL ? pref : "");
	SDL_free(pref);
	SDL_snprintf(beside, sizeof(beside), "%s../../../data", base != NULL ? base : "");

	const char *const dirs[] =
	{
		custom_data_dir,
		TYRIAN_DIR,
		"data",
		".",
		bundled,
		user,
		beside,
		remembered_data_dir(),
	};

	const char *dir = found_data_dir;

	if (dir != NULL)
		return dir;

	for (uint i = 0; i < COUNTOF(dirs); ++i)
	{
		if (dirs[i] == NULL)
			continue;

		FILE *f = dir_fopen(dirs[i], "tyrian1.lvl", "rb");
		if (f)
		{
			fclose(f);

			dir = dirs[i];
			break;
		}
	}

	if (dir == NULL) // data not found
		dir = "";

	found_data_dir = dir;
	return dir;
}

// prepend directory and fopen
FILE *dir_fopen(const char *dir, const char *file, const char *mode)
{
	char *path = malloc(strlen(dir) + 1 + strlen(file) + 1);
	sprintf(path, "%s/%s", dir, file);

	FILE *f = fopen(path, mode);

	free(path);

	return f;
}

// warn when dir_fopen fails
FILE *dir_fopen_warn(const char *dir, const char *file, const char *mode)
{
	FILE *f = dir_fopen(dir, file, mode);

	if (f == NULL)
		fprintf(stderr, "warning: failed to open '%s': %s\n", file, strerror(errno));

	return f;
}

// die when dir_fopen fails
FILE *dir_fopen_die(const char *dir, const char *file, const char *mode)
{
	FILE *f = dir_fopen(dir, file, mode);

	if (f == NULL)
	{
		fprintf(stderr, "error: failed to open '%s': %s\n", file, strerror(errno));
		fprintf(stderr, "error: One or more of the required Tyrian " TYRIAN_VERSION " data files could not be found.\n"
		                "       Please read the README file.\n");
		JE_tyrianHalt(1);
	}

	return f;
}

// check if file can be opened for reading
bool dir_file_exists(const char *dir, const char *file)
{
	FILE *f = dir_fopen(dir, file, "rb");
	if (f != NULL)
		fclose(f);
	return (f != NULL);
}

// returns end-of-file position
long ftell_eof(FILE *f)
{
	long pos = ftell(f);

	fseek(f, 0, SEEK_END);
	long size = ftell(f);

	fseek(f, pos, SEEK_SET);

	return size;
}

void fread_die(void *buffer, size_t size, size_t count, FILE *stream)
{
	size_t result = fread(buffer, size, count, stream);
	if (result != count)
	{
		fprintf(stderr, "error: An unexpected problem occurred while reading from a file.\n");
		SDL_Quit();
		exit(EXIT_FAILURE);
	}
}

void fwrite_die(const void *buffer, size_t size, size_t count, FILE *stream)
{
	size_t result = fwrite(buffer, size, count, stream);
	if (result != count)
	{
		fprintf(stderr, "error: An unexpected problem occurred while writing to a file.\n");
		SDL_Quit();
		exit(EXIT_FAILURE);
	}
}
