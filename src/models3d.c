/*
 * Tyrian3D: which game objects are shown as 3D models instead of sprites. See models3d.h.
 */
#include "models3d.h"

#include <SDL3/SDL.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

bool m3d_enabled = false;

int m3d_model_count = 0;
M3DModel m3d_models[M3D_MAX_MODELS];

typedef enum { CLASS_ANY, CLASS_GROUND, CLASS_SKY, CLASS_TOP } LayerClass;
typedef enum { SIZE_ANY, SIZE_SMALL, SIZE_LARGE } SizeClass;

#define MAX_RULES 32
#define MAX_RULE_MODELS 8

typedef struct
{
	LayerClass layer;
	SizeClass size;
	int model_count;
	int models[MAX_RULE_MODELS];
} EnemyRule;

typedef struct
{
	char sheet;
	unsigned int index;
	int model;  // -1 for "none"
} SpriteOverride;

static int player_model = -1;
static int rule_count = 0;
static EnemyRule rules[MAX_RULES];
static int override_count = 0;
static SpriteOverride overrides[128];

static int find_model(const char *name)
{
	for (int i = 0; i < m3d_model_count; ++i)
		if (strcmp(m3d_models[i].name, name) == 0)
			return i;
	return -1;
}

static void parse_line(char *line, const char *dir, const char *file, int line_number)
{
	char *tokens[16];
	int count = 0;
	for (char *token = strtok(line, " \t\r\n"); token != NULL && count < 16; token = strtok(NULL, " \t\r\n"))
	{
		if (token[0] == '#')
			break;
		tokens[count++] = token;
	}
	if (count == 0)
		return;

	if (strcmp(tokens[0], "model") == 0 && count >= 4 && m3d_model_count < M3D_MAX_MODELS)
	{
		M3DModel *model = &m3d_models[m3d_model_count++];
		SDL_strlcpy(model->name, tokens[1], sizeof(model->name));
		snprintf(model->path, sizeof(model->path), "%s/%s", dir, tokens[2]);
		model->size = (float)SDL_atof(tokens[3]);
		model->yaw = count > 4 ? (float)SDL_atof(tokens[4]) : 0.0f;
		model->pitch = count > 5 ? (float)SDL_atof(tokens[5]) : 0.0f;
		model->roll = count > 6 ? (float)SDL_atof(tokens[6]) : 0.0f;
		return;
	}

	if (strcmp(tokens[0], "player") == 0 && count >= 2)
	{
		player_model = find_model(tokens[1]);
		if (player_model < 0)
			fprintf(stderr, "warning: %s:%d: unknown model '%s'\n", file, line_number, tokens[1]);
		return;
	}

	if (strcmp(tokens[0], "enemy") == 0 && count >= 4 && rule_count < MAX_RULES)
	{
		EnemyRule *rule = &rules[rule_count];
		rule->layer = strcmp(tokens[1], "ground") == 0 ? CLASS_GROUND
		            : strcmp(tokens[1], "sky") == 0 ? CLASS_SKY
		            : strcmp(tokens[1], "top") == 0 ? CLASS_TOP
		            : CLASS_ANY;
		rule->size = strcmp(tokens[2], "1x1") == 0 ? SIZE_SMALL
		           : strcmp(tokens[2], "2x2") == 0 ? SIZE_LARGE
		           : SIZE_ANY;
		rule->model_count = 0;
		for (int i = 3; i < count && rule->model_count < MAX_RULE_MODELS; ++i)
		{
			const int model = find_model(tokens[i]);
			if (model < 0)
				fprintf(stderr, "warning: %s:%d: unknown model '%s'\n", file, line_number, tokens[i]);
			else
				rule->models[rule->model_count++] = model;
		}
		if (rule->model_count > 0)
			++rule_count;
		return;
	}

	if (strcmp(tokens[0], "sprite") == 0 && count >= 4 && override_count < (int)COUNTOF(overrides))
	{
		SpriteOverride *o = &overrides[override_count++];
		o->sheet = (char)SDL_tolower((unsigned char)tokens[1][0]);
		o->index = (unsigned int)strtoul(tokens[2], NULL, 10);
		o->model = strcmp(tokens[3], "none") == 0 ? -1 : find_model(tokens[3]);
		return;
	}

	fprintf(stderr, "warning: %s:%d: can't parse line\n", file, line_number);
}

void m3d_init(void)
{
	const char *dir = SDL_getenv("TYR3D_MODEL_DIR");
	if (dir == NULL)
		dir = TYR3D_MODEL_DIR;

	char path[600];
	snprintf(path, sizeof(path), "%s/models.cfg", dir);
	FILE *f = fopen(path, "r");
	if (f == NULL)
	{
		fprintf(stderr, "warning: no model mapping at %s; 3D models disabled\n", path);
		return;
	}

	char line[512];
	int line_number = 0;
	while (fgets(line, sizeof(line), f) != NULL)
		parse_line(line, dir, path, ++line_number);
	fclose(f);

	printf("models: %d models, %d enemy rules, %d sprite overrides\n", m3d_model_count, rule_count, override_count);
	m3d_enabled = m3d_model_count > 0 && SDL_getenv("TYR3D_NO_MODELS") == NULL;
}

static LayerClass layer_class(L3DLayerType layer)
{
	switch (layer)
	{
	case L3D_GROUND_ENEMY: return CLASS_GROUND;
	case L3D_SKY_ENEMY:    return CLASS_SKY;
	case L3D_TOP_ENEMY:    return CLASS_TOP;
	default:               return CLASS_ANY;
	}
}

int m3d_enemy_model(char sheet, unsigned int sprite_index, bool large, L3DLayerType layer)
{
	if (!m3d_enabled || sheet == 0)
		return -1;

	sheet = (char)SDL_tolower((unsigned char)sheet);
	for (int i = 0; i < override_count; ++i)
		if (overrides[i].sheet == sheet && overrides[i].index == sprite_index)
			return overrides[i].model;

	const LayerClass lc = layer_class(layer);
	const SizeClass sc = large ? SIZE_LARGE : SIZE_SMALL;
	for (int i = 0; i < rule_count; ++i)
	{
		const EnemyRule *rule = &rules[i];
		if ((rule->layer == CLASS_ANY || rule->layer == lc) && (rule->size == SIZE_ANY || rule->size == sc))
		{
			// Stable pick per sprite so each enemy type keeps its look.
			const unsigned int hash = (unsigned int)(unsigned char)sheet * 2654435761u ^ sprite_index * 40503u;
			return rule->models[(hash >> 7) % rule->model_count];
		}
	}
	return -1;
}

int m3d_player_model(void)
{
	return m3d_enabled ? player_model : -1;
}
