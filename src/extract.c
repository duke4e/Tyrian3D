/*
 * Tyrian3D dev tool: exports sprite sheets and a catalogue of enemies and ships.
 *
 * TYR3D_EXTRACT=<dir> runs it after the game data is loaded, then exits:
 *
 *   <dir>/sheets/<name>.png    sprite sheets as 19x16 grids of 12x14 cells, in the palette the
 *                              levels are played in, with alpha. Sprite index i (1-based) is at
 *                              column (i-1) % 19, row (i-1) / 19; a 2x2 sprite covers cells i, i+1,
 *                              i+19 and i+20.
 *   <dir>/sheets/<name>.idx    the sheet's palette indices, a byte per pixel, row by row.
 *   <dir>/palette.txt          the levels' palette: a line of "r g b" per index.
 *   <dir>/catalog.json         enemy types used by each episode's levels, with sheet, frames, size,
 *                              how often and where they appear; the player ships.
 *
 * tools/catalog_html.py turns the result into a browsable page.
 */
#include "extract.h"
#include "picload.h"

#include "episodes.h"
#include "file.h"
#include "helptext.h"
#include "lvllib.h"
#include "lvlmast.h"
#include "opentyr.h"
#include "palette.h"
#include "pcxmast.h"
#include "sprite.h"
#include "video.h"

#include <btbh_gpu/btbh_gpu.h>

#include <SDL3/SDL.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>

#define SHEET_COLUMNS 19
#define SHEET_ROWS 16
#define CELL_W 12
#define CELL_H 14
#define SHEET_W (SHEET_COLUMNS * CELL_W)
#define SHEET_H (SHEET_ROWS * CELL_H)

static void sheet_file_name(char letter, char *out, size_t size)
{
	if (SDL_isalnum((unsigned char)letter))
		snprintf(out, size, "enemy_%c", letter);
	else
		snprintf(out, size, "enemy_x%02x", (unsigned char)letter);
}

// The palette levels are played in: that of the in-game panel picture (JE_loadPic(3) at the start
// of each level).
static const SDL_Color *level_palette(void)
{
	return palettes[pcxpal[3 - 1]];
}

// Draws every cell of a sprite2 sheet and writes it as a PNG with transparency, and its palette
// indices.
static void export_sheet(const char *dir, const char *name, const Sprite2_array *sheet)
{
	if (sheet->data == NULL || sheet->size < 2)
		return;

	const unsigned int count = SDL_min((unsigned int)(SDL_Swap16LE(((const Uint16 *)sheet->data)[0]) / 2),
	                                   (unsigned int)(SHEET_COLUMNS * SHEET_ROWS));

	// The blitters step rows by VGAScreen's pitch, so draw into a surface with the same width.
	// Drawing twice on different backgrounds tells transparent pixels from drawn ones.
	SDL_Surface *passes[2];
	for (int p = 0; p < 2; ++p)
	{
		passes[p] = SDL_CreateSurface(VGAScreen->w, SHEET_H, SDL_PIXELFORMAT_INDEX8);
		SDL_FillSurfaceRect(passes[p], NULL, p == 0 ? 0x00 : 0xff);
		for (unsigned int i = 1; i <= count; ++i)
		{
			const Uint16 offset = SDL_Swap16LE(((const Uint16 *)sheet->data)[i - 1]);
			if (offset >= sheet->size)
				continue;
			blit_sprite2(passes[p], (int)((i - 1) % SHEET_COLUMNS) * CELL_W, (int)((i - 1) / SHEET_COLUMNS) * CELL_H, *sheet, i);
		}
	}

	static Uint8 rgba[SHEET_W * SHEET_H * 4];
	static Uint8 indices[SHEET_W * SHEET_H];
	for (int y = 0; y < SHEET_H; ++y)
		for (int x = 0; x < SHEET_W; ++x)
		{
			const Uint8 a = ((const Uint8 *)passes[0]->pixels)[y * passes[0]->pitch + x];
			const Uint8 b = ((const Uint8 *)passes[1]->pixels)[y * passes[1]->pitch + x];
			Uint8 *out = &rgba[(y * SHEET_W + x) * 4];
			indices[y * SHEET_W + x] = a;
			const SDL_Color c = level_palette()[a];
			out[0] = c.r;
			out[1] = c.g;
			out[2] = c.b;
			out[3] = a == b ? 255 : 0;
		}

	SDL_DestroySurface(passes[0]);
	SDL_DestroySurface(passes[1]);

	char path[1024];
	snprintf(path, sizeof(path), "%s/sheets/%s.png", dir, name);
	if (btbh_gpu_write_png_rgba8(path, SHEET_W, SHEET_H, rgba) != BTBH_GPU_OK)
		fprintf(stderr, "warning: failed to write %s\n", path);

	snprintf(path, sizeof(path), "%s/sheets/%s.idx", dir, name);
	FILE *f = fopen(path, "wb");
	if (f == NULL || fwrite(indices, sizeof(indices), 1, f) != 1)
		fprintf(stderr, "warning: failed to write %s\n", path);
	if (f != NULL)
		fclose(f);
}

static void json_string(FILE *f, const char *s)
{
	fputc('"', f);
	for (; *s != '\0'; ++s)
	{
		if (*s == '"' || *s == '\\')
			fputc('\\', f);
		if ((unsigned char)*s >= 0x20)
			fputc(*s, f);
	}
	fputc('"', f);
}

// Event types that create enemies (see JE_eventSystem) and the enemy slot range they use.
static int enemy_event_slot(Uint8 type)
{
	switch (type)
	{
	case 15: case 18:          return 0;   // sky
	case 6:  case 17:          return 25;  // ground
	case 7:  case 23: case 32: return 50;  // top
	case 10: case 56:          return 75;  // ground 2
	case 12:                   return -2;  // slot chosen by the event
	default:                   return -1;
	}
}

// Event types that make an enemy leave another one when destroyed (power-ups, weapons, coins).
static bool drop_event(Uint8 type)
{
	return type == 33 || type == 45 || type == 85;
}

#define SLOT_DROP (-3)

static const char *slot_layer(int slot)
{
	switch (slot)
	{
	case 0:  return "sky";
	case 25: return "ground";
	case 50: return "top";
	case 75: return "ground";
	case SLOT_DROP: return "drop";
	default: return "any";
	}
}

typedef struct
{
	unsigned int count;
	unsigned int layer_mask;  // 1 sky, 2 ground, 4 top, 8 any, 16 dropped by another enemy
	char levels[256];
} EnemyUse;

static EnemyUse uses[ENEMY_NUM + 1];

// Custom enemies (events 49-52): enemy 0 with the event's sprite from the event's shape bank.
#define MAX_CUSTOM 512
static struct
{
	int bank, sprite;
	EnemyUse use;
} customs[MAX_CUSTOM];
static int custom_count = 0;

static void add_level_name(EnemyUse *use, const char *level_name)
{
	if (strstr(use->levels, level_name) == NULL && strlen(use->levels) + strlen(level_name) + 2 < sizeof(use->levels))
	{
		if (use->levels[0] != '\0')
			strcat(use->levels, ",");
		strcat(use->levels, level_name);
	}
}

static void note_custom(int bank, int sprite, int slot, const char *level_name)
{
	if (bank <= 0)
		bank = enemyDat[0].shapebank;
	int i = 0;
	while (i < custom_count && !(customs[i].bank == bank && customs[i].sprite == sprite))
		++i;
	if (i == custom_count)
	{
		if (custom_count == MAX_CUSTOM)
			return;
		memset(&customs[i], 0, sizeof(customs[i]));
		customs[i].bank = bank;
		customs[i].sprite = sprite;
		++custom_count;
	}
	customs[i].use.count += 1;
	customs[i].use.layer_mask |= slot == 0 ? 1 : slot == 50 ? 4 : 2;
	add_level_name(&customs[i].use, level_name);
}

static void note_use(int id, int slot, const char *level_name)
{
	if (id <= 0 || id > ENEMY_NUM)
		return;
	EnemyUse *use = &uses[id];
	use->count += 1;
	const char *layer = slot_layer(slot);
	use->layer_mask |= strcmp(layer, "sky") == 0 ? 1 : strcmp(layer, "ground") == 0 ? 2 : strcmp(layer, "top") == 0 ? 4 :
	                   strcmp(layer, "drop") == 0 ? 16 : 8;
	if (strstr(use->levels, level_name) == NULL && strlen(use->levels) + strlen(level_name) + 2 < sizeof(use->levels))
	{
		if (use->levels[0] != '\0')
			strcat(use->levels, ",");
		strcat(use->levels, level_name);
	}
}

// An enemy left by another one when destroyed, with the ones the game puts in its place.
static void note_drop(int id, const char *level_name)
{
	note_use(id, SLOT_DROP, level_name);
	if (id == 533)  // a random special weapon instead, by the player's lives
		for (int k = 829; k < 835; ++k)
			note_use(k, SLOT_DROP, level_name);
	if (id == 534)  // Super Tyrian and Super Arcade specials
		for (int k = 827; k < 835; ++k)
			note_use(k, SLOT_DROP, level_name);
}

// Level names by level file number, from the episode script's ]L lines.
static void read_level_names(char names[][16], int capacity)
{
	for (int i = 0; i < capacity; ++i)
		snprintf(names[i], 16, "level%d", i + 1);

	FILE *f = dir_fopen_warn(data_dir(), episode_file, "rb");
	if (f == NULL)
		return;
	const long size = ftell_eof(f);
	char s[256];
	while (ftell(f) < size)
	{
		read_encrypted_pascal_string(s, sizeof(s), f);
		if (s[0] == ']' && s[1] == 'L' && strlen(s) >= 27)
		{
			const int file_number = atoi(s + 25);
			if (file_number >= 1 && file_number <= capacity)
			{
				char name[10];
				SDL_strlcpy(name, s + 13, sizeof(name));
				for (int k = (int)strlen(name) - 1; k >= 0 && name[k] == ' '; --k)
					name[k] = '\0';
				for (char *c = name; *c != '\0'; ++c)
					if (*c == ',' || *c == '"')
						*c = ' ';
				SDL_strlcpy(names[file_number - 1], name, 16);
			}
		}
	}
	fclose(f);
}

// Levels that turn on a special view (event 64 sets smoothie 9: upside down, 6: spotlight).
static char special_views[2048];

static void scan_episode_levels(void)
{
	memset(uses, 0, sizeof(uses));
	custom_count = 0;

	const int level_count = (episodeNum >= 4 ? lvlNum - 1 : lvlNum) / 2;
	char names[64][16];
	read_level_names(names, 64);

	FILE *f = dir_fopen_die(data_dir(), levelFile, "rb");
	for (int level = 0; level < level_count && level < 64; ++level)
	{
		fseek(f, lvlPos[level * 2], SEEK_SET);

		char map_file, shape_file;
		Uint16 map_x[3], enemy_count;
		fread_die(&map_file, 1, 1, f);
		fread_die(&shape_file, 1, 1, f);
		fread_u16_die(map_x, 3, f);

		fread_u16_die(&enemy_count, 1, f);
		Uint16 random_enemies[100];
		if (enemy_count > COUNTOF(random_enemies))
			continue;
		fread_u16_die(random_enemies, enemy_count, f);
		for (int i = 0; i < enemy_count; ++i)
			note_use(random_enemies[i], 0, names[level]);

		Uint16 event_count;
		fread_u16_die(&event_count, 1, f);
		for (int e = 0; e < event_count; ++e)
		{
			Uint16 time;
			Uint8 type, dat4;
			Sint16 dat, dat2;
			Sint8 dat3, dat5, dat6;
			fread_u16_die(&time, 1, f);
			fread_u8_die(&type, 1, f);
			fread_s16_die(&dat, 1, f);
			fread_s16_die(&dat2, 1, f);
			fread_s8_die(&dat3, 1, f);
			fread_s8_die(&dat5, 1, f);
			fread_s8_die(&dat6, 1, f);
			fread_u8_die(&dat4, 1, f);

			if (type == 64 && (dat == 9 || dat == 6) && dat2 != 0)
			{
				char entry[128];
				snprintf(entry, sizeof(entry), "%s\n    {\"episode\": %d, \"level\": \"%s\", \"view\": \"%s\", \"time\": %d}",
				         special_views[0] != '\0' ? "," : "", episodeNum, names[level], dat == 9 ? "upside-down" : "spotlight", time);
				if (strstr(special_views, entry + (special_views[0] != '\0' ? 1 : 0)) == NULL)
					SDL_strlcat(special_views, entry, sizeof(special_views));
			}

			if (drop_event(type))
			{
				note_drop(dat, names[level]);
				continue;
			}

			if (type >= 49 && type <= 52)
			{
				note_custom(dat3, dat, (const int[]){ 25, 0, 50, 75 }[type - 49], names[level]);
				continue;
			}
			const int slot = enemy_event_slot(type);
			if (slot == -1)
				continue;
			if (type == 12)  // four enemies in a block
				for (int k = 0; k < 4; ++k)
					note_use(dat + k, 25, names[level]);
			else
				note_use(dat, slot, names[level]);
		}
	}
	fclose(f);

	// What the used enemies leave when destroyed (and what that leaves, and so on).
	for (bool changed = true; changed; )
	{
		changed = false;
		for (int id = 1; id <= ENEMY_NUM; ++id)
		{
			const int drop = enemyDat[id].eenemydie;
			if (uses[id].count > 0 && drop > 0 && drop <= ENEMY_NUM && uses[drop].count == 0)
			{
				note_drop(drop, uses[id].levels);
				changed = true;
			}
		}
	}
	// The damaged look an enemy switches to when hit hard (dgr, without a damage animation): its
	// own enemy type for models (keyed by its first sprite), as a custom enemy of the same bank.
	for (int id = 1; id <= ENEMY_NUM; ++id)
		if (uses[id].count > 0 && enemyDat[id].dgr > 0 && enemyDat[id].dani == 0)
		{
			char levels[sizeof(uses[id].levels)];
			SDL_strlcpy(levels, uses[id].levels, sizeof(levels));
			const int slot = (uses[id].layer_mask & 1) ? 0 : (uses[id].layer_mask & 4) ? 50 : 25;
			for (char *level = strtok(levels, ","); level != NULL; level = strtok(NULL, ","))
				note_custom(enemyDat[id].shapebank, enemyDat[id].dgr, slot, level);
		}
	// The ship that brings armour when the player is low on it (JE_main), and its drops.
	note_use(560, 0, "any");
	for (int k = 561; k <= 563; ++k)
		note_use(k, SLOT_DROP, "any");
}

static void write_use(FILE *json, bool *first, int id, int bank, const EnemyUse *use, int frames_count, const int *frames,
                      bool large);

static void write_episode_enemies(FILE *json, bool *first)
{
	for (int id = 1; id <= ENEMY_NUM; ++id)
	{
		const EnemyUse *use = &uses[id];
		if (use->count == 0)
			continue;
		int frames[20];
		const int frame_count = SDL_max(1, SDL_min(enemyDat[id].ani, 20));
		for (int k = 0; k < frame_count; ++k)
			frames[k] = enemyDat[id].egraphic[k];
		write_use(json, first, id, enemyDat[id].shapebank, use, frame_count, frames, enemyDat[id].esize == 1);
	}
	for (int i = 0; i < custom_count; ++i)
		write_use(json, first, 0, customs[i].bank, &customs[i].use, 1, &customs[i].sprite, enemyDat[0].esize == 1);
}

static void write_use(FILE *json, bool *first, int id, int bank, const EnemyUse *use, int frame_count, const int *frames,
                      bool large)
{
	{
		// Sheet letter as used by models.cfg, and the exported sheet file.
		char sheet[16], sheet_file[32];
		if (bank == 21)
		{
			strcpy(sheet, "coins");
			strcpy(sheet_file, "coins");
		}
		else if (bank == 26)
		{
			strcpy(sheet, "twoplayer");
			strcpy(sheet_file, "powerups");
		}
		else if (bank >= 1 && bank <= (int)COUNTOF(shapeFile))
		{
			snprintf(sheet, sizeof(sheet), "%c", shapeFile[bank - 1]);
			sheet_file_name(shapeFile[bank - 1], sheet_file, sizeof(sheet_file));
		}
		else
		{
			strcpy(sheet, "?");
			strcpy(sheet_file, "");
		}

		fprintf(json, "%s\n    {\"episode\": %d, \"id\": %d, \"sheet\": ", *first ? "" : ",", episodeNum, id);
		json_string(json, sheet);
		fprintf(json, ", \"sheet_file\": ");
		json_string(json, sheet_file);
		fprintf(json, ", \"large\": %s, \"ani\": %d, \"animate\": %d, \"armor\": %d, \"value\": %d, \"count\": %u, \"layers\": [",
		        large ? "true" : "false", id ? enemyDat[id].ani : 1, id ? enemyDat[id].animate : 0,
		        enemyDat[id].armor, enemyDat[id].value, use->count);
		const char *layer_names[5] = { "sky", "ground", "top", "any", "drop" };
		bool first_layer = true;
		for (int l = 0; l < 5; ++l)
			if (use->layer_mask & (1u << l))
			{
				fprintf(json, "%s\"%s\"", first_layer ? "" : ", ", layer_names[l]);
				first_layer = false;
			}
		fprintf(json, "], \"frames\": [");
		for (int k = 0; k < frame_count; ++k)
			fprintf(json, "%s%d", k ? ", " : "", frames[k]);
		fprintf(json, "], \"levels\": ");
		json_string(json, use->levels);
		fputc('}', json);
		*first = false;
	}
}

// The HUD panels' pictures (the screen's right column of pictures 3 and 6, one and two players),
// as references and for upscaling (the 3D view uses upscaled ones, render_gpu.c).
static void export_hud_panels(const char *dir)
{
	SDL_Surface *picture = SDL_CreateSurface(320, 200, SDL_PIXELFORMAT_INDEX8);
	if (picture == NULL)
		return;
	static const struct { int number; const char *name; } panels[] = { { 3, "hud_1p" }, { 6, "hud_2p" } };
	for (size_t p = 0; p < COUNTOF(panels); ++p)
	{
		JE_loadPic(picture, (JE_byte)panels[p].number, false);
		enum { X = 264, W = 320 - 264, H = 200 };
		static Uint8 rgba[W * H * 4];
		for (int y = 0; y < H; ++y)
			for (int x = 0; x < W; ++x)
			{
				const SDL_Color c = level_palette()[((const Uint8 *)picture->pixels)[y * picture->pitch + X + x]];
				Uint8 *out = &rgba[(y * W + x) * 4];
				out[0] = c.r;
				out[1] = c.g;
				out[2] = c.b;
				out[3] = 255;
			}
		char path[1024];
		snprintf(path, sizeof(path), "%s/sheets/%s.png", dir, panels[p].name);
		if (btbh_gpu_write_png_rgba8(path, W, H, rgba) != BTBH_GPU_OK)
			fprintf(stderr, "warning: failed to write %s\n", path);
	}
	SDL_DestroySurface(picture);
}

void dev_extract(const char *dir)
{
	char path[1024];
	mkdir(dir, 0755);
	snprintf(path, sizeof(path), "%s/sheets", dir);
	mkdir(path, 0755);

	if (explosionSpriteSheet.data == NULL)
		JE_loadCompShapes(&explosionSpriteSheet, '6');

	// Enemy shape files.
	for (size_t i = 0; i < COUNTOF(shapeFile); ++i)
	{
		Sprite2_array sheet = { 0, NULL };
		char filename[20];
		snprintf(filename, sizeof(filename), "newsh%c.shp", SDL_tolower((unsigned char)shapeFile[i]));
		if (!dir_file_exists(data_dir(), filename))
			continue;
		JE_loadCompShapes(&sheet, shapeFile[i]);
		char name[32];
		sheet_file_name(shapeFile[i], name, sizeof(name));
		export_sheet(dir, name, &sheet);
		free_sprite2s(&sheet);
	}

	export_sheet(dir, "shots", &spriteSheet8);
	export_sheet(dir, "ships", &spriteSheet9);
	export_sheet(dir, "powerups", &spriteSheet10);
	export_sheet(dir, "coins", &spriteSheet11);
	export_sheet(dir, "shots2", &spriteSheet12);
	export_sheet(dir, "ships_t2000", &spriteSheetT2000);
	export_sheet(dir, "explosions", &explosionSpriteSheet);
	export_hud_panels(dir);

	snprintf(path, sizeof(path), "%s/palette.txt", dir);
	FILE *palette = fopen(path, "w");
	if (palette != NULL)
	{
		for (int i = 0; i < 256; ++i)
			fprintf(palette, "%d %d %d\n", level_palette()[i].r, level_palette()[i].g, level_palette()[i].b);
		fclose(palette);
	}

	snprintf(path, sizeof(path), "%s/catalog.json", dir);
	FILE *json = fopen(path, "w");
	if (json == NULL)
	{
		fprintf(stderr, "error: can't write %s\n", path);
		exit(EXIT_FAILURE);
	}

	fprintf(json, "{\n  \"cell\": [%d, %d], \"columns\": %d,\n  \"enemies\": [", CELL_W, CELL_H, SHEET_COLUMNS);
	bool first = true;
	for (int episode = 1; episode <= EPISODE_MAX; ++episode)
	{
		if (!episodeAvail[episode - 1])
			continue;
		JE_initEpisode((JE_byte)episode);
		scan_episode_levels();
		write_episode_enemies(json, &first);
	}

	fprintf(json, "\n  ],\n  \"ships\": [");
	for (int i = 1; i <= SHIP_NUM; ++i)
	{
		const int graphic = ships[i].shipgraphic;
		fprintf(json, "%s\n    {\"id\": %d, \"name\": ", i > 1 ? "," : "", i);
		json_string(json, ships[i].name);
		fprintf(json, ", \"sheet\": \"%s\", \"index\": %d}", graphic >= 500 ? "ships_t2000" : "ships",
		        graphic >= 500 ? graphic - 500 : graphic);
	}
	fprintf(json, "\n  ],\n  \"special_views\": [%s\n  ],\n  \"sidekicks\": [", special_views);
	for (int i = 1; i <= OPTION_NUM; ++i)
	{
		const JE_OptionType *o = &options[i];
		const bool large = o->tr == 1 || o->tr == 2;  // drawn 2x2 from the power-ups sheet
		fprintf(json, "%s\n    {\"id\": %d, \"name\": ", i > 1 ? "," : "", i);
		json_string(json, o->name);
		fprintf(json, ", \"style\": %d, \"animation\": %d, \"sheet\": \"%s\", \"size\": \"%s\", \"frames\": [",
		        o->tr, o->option, large ? "powerups" : "ships", large ? "2x2" : "1x1");
		for (int k = 0; k < SDL_max(1, SDL_min(o->ani, 20)); ++k)
			fprintf(json, "%s%d", k ? ", " : "", o->gr[k]);
		fprintf(json, "], \"charge\": %d}", o->pwr);
	}
	fprintf(json, "\n  ]\n}\n");
	fclose(json);

	printf("extract: wrote %s\n", dir);
}
