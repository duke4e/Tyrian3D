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
 *   <dir>/catalog.json         enemy types used by each episode's levels (and what they leave, launch
 *                              or turn into when damaged), with sheet, frames, size,
 *                              how often and where they appear; the player ships; the shots'
 *                              sprites with the weapons that fire them (p: the player's, e: enemies').
 *
 * tools/catalog_html.py turns the result into a browsable page.
 */
#include "extract.h"
#include "picload.h"

#include "animlib.h"
#include "pcxload.h"

#include "episodes.h"
#include "file.h"
#include "game_menu.h"
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
	unsigned int layer_mask;  // 1 sky, 2 ground, 4 top, 8 any, 16 dropped by another enemy, 32 launched by another enemy
	                          // (64: ground 2, not written)
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
	use->layer_mask |= slot == 75 ? 64 : 0;
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

	// What the used enemies leave when destroyed and what they launch (and what those leave or launch, and so on). A
	// launched enemy is made on its launcher's layer (JE_drawEnemy: a ground launcher's on ground 2) and shows at least
	// as often as its launchers.
	static bool launched_only[ENEMY_NUM + 1], credited[ENEMY_NUM + 1];
	for (bool changed = true; changed; )
	{
		changed = false;
		for (int id = 1; id <= ENEMY_NUM; ++id)
		{
			if (uses[id].count == 0)
				continue;
			const int drop = enemyDat[id].eenemydie;
			if (drop > 0 && drop <= ENEMY_NUM && uses[drop].count == 0)
			{
				note_drop(drop, uses[id].levels);
				changed = true;
			}
			// (as JE_makeEnemy takes it: the second bank's types whole)
			const int launch = enemyDat[id].elaunchfreq == 0 ? 0 : id > 1000 ? enemyDat[id].elaunchtype : enemyDat[id].elaunchtype % 1000;
			if (launch > 0 && launch <= ENEMY_NUM && !credited[id] && (uses[launch].count == 0 || launched_only[launch]))
			{
				const unsigned int mask = uses[id].layer_mask;
				note_use(launch, (mask & 1) ? 0 : (mask & 2) ? 75 : 50, uses[id].levels);
				uses[launch].count += uses[id].count - 1;
				uses[launch].layer_mask |= (mask & (1 | 2 | 4 | 64)) | 32;
				launched_only[launch] = credited[id] = true;
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
		const char *layer_names[6] = { "sky", "ground", "top", "any", "drop", "launched" };
		bool first_layer = true;
		for (int l = 0; l < 6; ++l)
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

// The store's pictures of ship parts (sheets/store, in the store's palette): every sprite of the
// weapon shapes (guns and generators) and of the option shapes (the big ships among them), and
// the illustration of the ship (draw_ship_illustration) with each gun on its mount, 4x; and
// store.json: which sprite each gun, generator and ship uses and where it sits on the illustration.
static void write_store_png(const char *path, const SDL_Surface *surface, int x0, int y0, int w, int h, int scale)
{
	const SDL_Color *palette = palettes[pcxpal[1 - 1]];
	Uint8 *rgba = malloc((size_t)w * scale * h * scale * 4);
	if (rgba == NULL)
		return;
	for (int y = 0; y < h * scale; ++y)
		for (int x = 0; x < w * scale; ++x)
		{
			const Uint8 index = ((const Uint8 *)surface->pixels)[(y0 + y / scale) * surface->pitch + x0 + x / scale];
			Uint8 *out = &rgba[((size_t)y * w * scale + x) * 4];
			out[0] = palette[index].r;
			out[1] = palette[index].g;
			out[2] = palette[index].b;
			out[3] = index != 0 ? 255 : 0;
		}
	if (btbh_gpu_write_png_rgba8(path, (uint32_t)(w * scale), (uint32_t)(h * scale), rgba) != BTBH_GPU_OK)
		fprintf(stderr, "warning: failed to write %s\n", path);
	free(rgba);
}

static void export_store(const char *dir)
{
	char path[1024];
	snprintf(path, sizeof(path), "%s/sheets/store", dir);
	mkdir(path, 0755);
	SDL_Surface *surface = SDL_CreateSurface(320, 200, SDL_PIXELFORMAT_INDEX8);
	if (surface == NULL)
		return;

	static const struct { unsigned int table; const char *name; } tables[] = {
		{ WEAPON_SHAPES, "weapon" }, { OPTION_SHAPES, "option" },
	};
	snprintf(path, sizeof(path), "%s/sheets/store/store.json", dir);
	FILE *json = fopen(path, "w");
	if (json == NULL)
	{
		SDL_DestroySurface(surface);
		return;
	}
	fprintf(json, "{\n  \"sprites\": {");
	for (size_t t = 0; t < COUNTOF(tables); ++t)
	{
		fprintf(json, "%s\n    \"%s\": [", t > 0 ? "," : "", tables[t].name);
		bool first = true;
		for (unsigned int i = 0; i < sprite_table[tables[t].table].count; ++i)
		{
			if (!sprite_exists(tables[t].table, i))
				continue;
			const int w = get_sprite_width(tables[t].table, i), h = get_sprite_height(tables[t].table, i);
			SDL_FillSurfaceRect(surface, NULL, 0);
			blit_sprite(surface, 0, 0, tables[t].table, i);
			snprintf(path, sizeof(path), "%s/sheets/store/%s_%u.png", dir, tables[t].name, i);
			write_store_png(path, surface, 0, 0, w, h, 1);
			fprintf(json, "%s{\"index\": %u, \"w\": %d, \"h\": %d}", first ? "" : ", ", i, w, h);
			first = false;
		}
		fprintf(json, "]");
	}
	fprintf(json, "\n  },\n");

	// Where the pieces go: the default ship and generator, each gun.
	PlayerItems items;
	memset(&items, 0, sizeof(items));
	items.ship = 1;
	items.generator = 1;
	unsigned int table;
	int sprite_id, x, y;
	fprintf(json, "  \"ships\": [");
	for (int i = 1; i <= SHIP_NUM; ++i)
	{
		items.ship = (JE_byte)i;
		if (ships[i].bigshipgraphic == 0 || !ship_illustration_piece(ILLUSTRATION_SHIP, &items, &table, &sprite_id, &x, &y))
			continue;
		fprintf(json, "%s\n    {\"id\": %d, \"name\": ", i > 1 ? "," : "", i);
		json_string(json, ships[i].name);
		fprintf(json, ", \"option_sprite\": %d, \"x\": %d, \"y\": %d}", sprite_id, x, y);
	}
	items.ship = 1;
	fprintf(json, "\n  ],\n  \"generators\": [");
	for (int i = 1; i <= 6; ++i)
	{
		items.generator = (JE_byte)i;
		if (!ship_illustration_piece(ILLUSTRATION_GENERATOR, &items, &table, &sprite_id, &x, &y))
			continue;
		fprintf(json, "%s\n    {\"id\": %d, \"name\": ", i > 1 ? "," : "", i);
		json_string(json, powerSys[i].name);
		fprintf(json, ", \"weapon_sprite\": %d, \"x\": %d, \"y\": %d}", sprite_id, x, y);
	}
	items.generator = 1;
	fprintf(json, "\n  ],\n  \"guns\": [");
	bool first = true;
	for (int id = 1; id <= PORT_NUM; ++id)
	{
		PlayerItems front = items, rear = items;
		front.weapon[FRONT_WEAPON].id = (JE_byte)id;
		rear.weapon[REAR_WEAPON].id = (JE_byte)id;
		int fx, fy, rx, ry, fs = -1, rs = -1;
		const bool has_front = ship_illustration_piece(ILLUSTRATION_FRONT, &front, &table, &fs, &fx, &fy);
		const bool has_rear = ship_illustration_piece(ILLUSTRATION_REAR, &rear, &table, &rs, &rx, &ry);
		if (!has_front && !has_rear)
			continue;
		fprintf(json, "%s\n    {\"id\": %d, \"name\": ", first ? "" : ",", id);
		json_string(json, weaponPort[id].name);
		if (has_front)
			fprintf(json, ", \"front\": {\"weapon_sprite\": %d, \"x\": %d, \"y\": %d}", fs, fx, fy);
		if (has_rear)
			fprintf(json, ", \"rear\": {\"weapon_sprite\": %d, \"x\": %d, \"y\": %d}", rs, rx, ry);
		fputc('}', json);
		first = false;

		// The illustration with this gun on its mount(s), 4x.
		SDL_FillSurfaceRect(surface, NULL, 0);
		PlayerItems both = items;
		both.weapon[FRONT_WEAPON].id = has_front ? (JE_byte)id : 0;
		both.weapon[REAR_WEAPON].id = has_rear ? (JE_byte)id : 0;
		static const IllustrationPart parts[] = { ILLUSTRATION_SHIP, ILLUSTRATION_GENERATOR, ILLUSTRATION_FRONT, ILLUSTRATION_REAR };
		for (size_t k = 0; k < COUNTOF(parts); ++k)
			if (ship_illustration_piece(parts[k], &both, &table, &sprite_id, &x, &y))
				blit_sprite(surface, x, y, table, sprite_id);
		snprintf(path, sizeof(path), "%s/sheets/store/illustration_gun_%d.png", dir, id);
		write_store_png(path, surface, 0, 0, 160, 150, 4);
	}
	fprintf(json, "\n  ]\n}\n");
	fclose(json);
	SDL_DestroySurface(surface);
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
	// The weapon ports as the shop sells them: name and the weapons of their 11 power levels.
	fprintf(json, "\n  ],\n  \"ports\": [");
	for (int port = 1; port <= PORT_NUM; ++port)
	{
		fprintf(json, "%s\n    {\"id\": %d, \"name\": ", port > 1 ? "," : "", port);
		json_string(json, weaponPort[port].name);
		fprintf(json, ", \"weapons\": [");
		for (int level = 0; level < 11; ++level)
			fprintf(json, "%s%d", level ? ", " : "", weaponPort[port].op[0][level]);
		fprintf(json, "]}");
	}
	// The shots: every sprite a weapon fires (its pattern's graphic and the animation's frames),
	// with the weapons and who fires them (the player's ports, or enemies).
	fprintf(json, "\n  ],\n  \"shots\": [");
	{
		static char users[2][300][160];  // by sheet (shots, shots2) and sprite
		memset(users, 0, sizeof(users));
		static bool by_player[WEAP_NUM + 1], by_enemy[WEAP_NUM + 1];
		memset(by_player, 0, sizeof(by_player));
		memset(by_enemy, 0, sizeof(by_enemy));
		for (int port = 1; port <= PORT_NUM; ++port)
			for (int mode = 0; mode < 2; ++mode)
				for (int level = 0; level < 11; ++level)
					if (weaponPort[port].op[mode][level] <= WEAP_NUM)
						by_player[weaponPort[port].op[mode][level]] = true;
		for (int id = 1; id <= ENEMY_NUM; ++id)
			for (int t = 0; t < 3; ++t)
				if (enemyDat[id].tur[t] > 0)
					by_enemy[enemyDat[id].tur[t]] = true;
		for (int w = 1; w <= WEAP_NUM; ++w)
		{
			const JE_WeaponType *weapon = &weapons[w];
			for (int p = 0; p < SDL_min((int)weapon->multi, 8); ++p)
				for (int a = 0; a < SDL_max(1, (int)weapon->weapani); ++a)
				{
					unsigned int frame = weapon->sg[p] + a;
					if (weapon->sg[p] == 0 || frame > 60000)
						continue;
					frame %= 1000;
					const int sheet = frame > 500, sprite = sheet ? (int)frame - 500 : (int)frame;
					if (sprite <= 0 || sprite >= 300)
						continue;
					char tag[16];
					snprintf(tag, sizeof(tag), "%s%d", by_player[w] ? "p" : by_enemy[w] ? "e" : "w", w);
					if (strlen(users[sheet][sprite]) + strlen(tag) + 2 < sizeof(users[sheet][sprite]))
					{
						if (users[sheet][sprite][0] != '\0')
							strcat(users[sheet][sprite], ",");
						strcat(users[sheet][sprite], tag);
					}
				}
		}
		bool first_shot = true;
		for (int sheet = 0; sheet < 2; ++sheet)
			for (int sprite = 1; sprite < 300; ++sprite)
				if (users[sheet][sprite][0] != '\0')
				{
					fprintf(json, "%s\n    {\"sheet\": \"%s\", \"sprite\": %d, \"weapons\": ", first_shot ? "" : ",",
					        sheet ? "shots2" : "shots", sprite);
					json_string(json, users[sheet][sprite]);
					fputc('}', json);
					first_shot = false;
				}
	}
	fprintf(json, "\n  ]\n}\n");
	fclose(json);

	export_store(dir);  // with an episode's items loaded
	printf("extract: wrote %s\n", dir);
}

/* --- The game's pictures (TYR3D_EXPORT_PICTURES) ------------------------------------------------ */

// A part of an 8-bit surface as a PNG in a palette; colour 0 transparent if asked.
static void write_picture(const char *path, const SDL_Surface *surface, int w, int h, const SDL_Color *palette,
                          bool clear_zero)
{
	Uint8 *rgba = malloc((size_t)w * h * 4);
	if (rgba == NULL)
		return;
	for (int y = 0; y < h; ++y)
		for (int x = 0; x < w; ++x)
		{
			const Uint8 index = ((const Uint8 *)surface->pixels)[y * surface->pitch + x];
			Uint8 *out = &rgba[(y * w + x) * 4];
			out[0] = palette[index].r;
			out[1] = palette[index].g;
			out[2] = palette[index].b;
			out[3] = clear_zero && index == 0 ? 0 : 255;
		}
	if (btbh_gpu_write_png_rgba8(path, (uint32_t)w, (uint32_t)h, rgba) != BTBH_GPU_OK)
		fprintf(stderr, "warning: failed to write %s\n", path);
	else
		printf("%s\n", path);
	free(rgba);
}

typedef struct
{
	const char *dir;
} AnimExport;

static void write_anim_frame(int number, void *data)
{
	const AnimExport *e = data;
	char path[1024];
	snprintf(path, sizeof(path), "%s/tyrend/frame_%03d.png", e->dir, number + 1);
	write_picture(path, VGAScreen, 320, 200, colors, false);
}

void dev_export_pictures(const char *dir)
{
	mkdir(dir, 0755);
	char path[1024];
	SDL_Surface *surface = SDL_CreateSurface(320, 200, SDL_PIXELFORMAT_INDEX8);
	if (surface == NULL)
		return;

	// tyrian.pic: the full-screen pictures, each in its palette.
	for (int n = 1; n <= PCX_NUM; ++n)
	{
		JE_loadPic(surface, (JE_byte)n, false);
		snprintf(path, sizeof(path), "%s/pic_%02d.png", dir, n);
		write_picture(path, surface, 320, 200, palettes[pcxpal[n - 1]], false);
	}

	// tshp2.pcx (a story picture: ]P0), in its own palette.
	JE_loadPCX("tshp2.pcx");
	snprintf(path, sizeof(path), "%s/tshp2.png", dir);
	write_picture(path, VGAScreen, 320, 200, colors, false);

	// The data cubes' faces (FACE_SHAPES), each in its palette (facepal), the rest of the picture clear.
	for (unsigned int i = 0; i < sprite_table[FACE_SHAPES].count; ++i)
	{
		if (!sprite_exists(FACE_SHAPES, i))
			continue;
		const Sprite *face = sprite(FACE_SHAPES, i);
		SDL_FillSurfaceRect(surface, NULL, 0);
		blit_sprite(surface, 0, 0, FACE_SHAPES, i);
		snprintf(path, sizeof(path), "%s/face_%02u.png", dir, i + 1);
		write_picture(path, surface, face->width, face->height, palettes[i < 12 ? facepal[i] : 0], true);
	}
	// And the store's portrait frame round them (OPTION_SHAPES 20) where the store draws it, its window clear:
	// tools/hd_pictures.py fits the faces drawn anew into the window.
	SDL_FillSurfaceRect(surface, NULL, 0);
	blit_sprite(surface, 1, 1, OPTION_SHAPES, 20);
	snprintf(path, sizeof(path), "%s/face_frame.png", dir);
	write_picture(path, surface, 147, 172, palettes[pcxpal[0]], true);

	// The title's logo (PLANET_SHAPES 146) and its "2000(tm)" (151), each alone and together as the title shows
	// them once they have flown in, in the title picture's palette, clear round them.
	{
		static const struct { const char *name; int sprites[2]; int at[2][2]; } logos[] = {
			{ "logo_tyrian", { 146, -1 }, { { 0, 0 } } },
			{ "logo_2000", { 151, -1 }, { { 0, 0 } } },
			{ "logo_tyrian2000", { 146, 151 }, { { 11, 4 }, { 155, 73 } } },  // (titleScreen's places)
		};
		const SDL_Color *palette = palettes[pcxpal[4 - 1]];
		for (size_t l = 0; l < COUNTOF(logos); ++l)
		{
			int x0 = 1 << 30, y0 = 1 << 30, x1 = -1, y1 = -1;
			for (int k = 0; k < 2 && logos[l].sprites[k] >= 0; ++k)
			{
				if (!sprite_exists(PLANET_SHAPES, (unsigned int)logos[l].sprites[k]))
					continue;
				const Sprite *sp = sprite(PLANET_SHAPES, (unsigned int)logos[l].sprites[k]);
				x0 = SDL_min(x0, logos[l].at[k][0]);
				y0 = SDL_min(y0, logos[l].at[k][1]);
				x1 = SDL_max(x1, logos[l].at[k][0] + sp->width);
				y1 = SDL_max(y1, logos[l].at[k][1] + sp->height);
			}
			if (x1 < 0 || x1 - x0 > 320 || y1 - y0 > 200)
				continue;
			SDL_FillSurfaceRect(surface, NULL, 0);
			for (int k = 0; k < 2 && logos[l].sprites[k] >= 0; ++k)
				if (sprite_exists(PLANET_SHAPES, (unsigned int)logos[l].sprites[k]))
					blit_sprite(surface, logos[l].at[k][0] - x0, logos[l].at[k][1] - y0, PLANET_SHAPES, (unsigned int)logos[l].sprites[k]);
			snprintf(path, sizeof(path), "%s/%s.png", dir, logos[l].name);
			write_picture(path, surface, x1 - x0, y1 - y0, palette, true);
		}
	}

	// The ending's animation (tyrend.anm), frame by frame.
	AnimExport e = { dir };
	snprintf(path, sizeof(path), "%s/tyrend", dir);
	mkdir(path, 0755);
	JE_eachAnimFrame("tyrend.anm", write_anim_frame, &e);

	SDL_DestroySurface(surface);

	snprintf(path, sizeof(path), "%s/README.txt", dir);
	FILE *readme = fopen(path, "w");
	if (readme == NULL)
		return;
	fputs("The game's pictures (TYR3D_EXPORT_PICTURES), 320 x 200 as the game shows them (on a 4:3 screen: its\n"
	      "pixels are 1.2 times as tall as wide), each in its own palette. Drawn anew in the same frame (16:10, any\n"
	      "size), pic_NN.png goes to data/hd/pictures/pic_NN.png: the modern UI shows it instead of the original.\n\n"
	      "pic_01  the game menu and the store (the modern UI blurs it behind its panels), the Super Arcade's start\n"
	      "pic_02  the menus behind the title: setup, options, load, high scores, the jukebox, network\n"
	      "pic_03  the in-game HUD for one player: the right column (data/hd/hud_1p.png is its upscale)\n"
	      "pic_04  the title screen\n"
	      "pic_06  the in-game HUD for two players (data/hd/hud_2p.png)\n"
	      "pic_10  the first logo as the game starts (intro_logos)\n"
	      "pic_11  Destruct (the hidden artillery game)\n"
	      "pic_12  the second logo as the game starts (intro_logos)\n"
	      "pic_13  the high score's name entry in a timed battle\n"
	      "others  story pictures between levels (the episode texts' ]P and ]U commands)\n"
	      "tshp2   a story picture (]P0)\n"
	      "face_NN the data cubes' faces in the store (who wrote the cube), clear round them\n"
	      "face_frame the store's portrait frame round the faces (screen pixels from 0, 0), its window clear\n"
	      "logo_tyrian, logo_2000, logo_tyrian2000  the title's logo alone, its 2000(tm), and both as the title shows them\n"
	      "  (redrawn logo_tyrian.png and logo_2000.png go to data/hd/pictures too; a clear logo_2000.png hides the 2000)\n"
	      "tyrend/  the ending's animation (episode 1's end), frame by frame\n",
	      readme);
	fclose(readme);
}
