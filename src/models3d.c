/*
 * Tyrian3D: how game objects appear in 3D. See models3d.h and assets/models/models.cfg.
 */
#include "models3d.h"

#include "paths3d.h"

#include <SDL3/SDL.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

_Static_assert(M3D_VOLUME == L3D_VOLUME, "object kinds must match");

bool m3d_enabled = false;

int m3d_model_count = 0;
M3DModel m3d_models[M3D_MAX_MODELS];
unsigned int m3d_generation = 0;

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
	M3DAppearance options;  // yaw and height options shared by the listed models
} EnemyRule;

typedef struct
{
	char sheet;
	unsigned int sprite;
	M3DAppearance appearance;
} SpriteOverride;

typedef struct
{
	unsigned int ship;  // 0 = any ship (or sidekick)
	M3DAppearance appearance;
} ShipRule;

static int rule_count;
static EnemyRule rules[MAX_RULES];
static int override_count;
static SpriteOverride overrides[4096];

// frame <sheet> <sprite> <model>: while an enemy with a model shows this animation frame, this model.
static struct
{
	char sheet;
	unsigned int sprite;
	int model;
} frame_models[2048];
static int frame_model_count = 0;

// "wreck" lines: what is left of an enemy type where the ground map paints it (the clean ground's
// stand-ins, tyrian2.c draw_standins).
static struct
{
	char sheet;
	unsigned int sprite;
	int model;
} wreck_models[512], standin_models[64];
static int wreck_model_count = 0, standin_model_count = 0;

// shot <shots|shots2> <sprite> <appearance> [options]: the player's and enemies' shots.
static struct
{
	Uint8 sheet;  // 0 shots, 1 shots2
	unsigned int sprite;
	M3DAppearance appearance;
} shot_rules[1024];
static int shot_rule_count = 0;
static int ship_rule_count;
static ShipRule ship_rules[32];
static int sidekick_rule_count;
static ShipRule sidekick_rules[64];

// The store's illustration of the ship: models by the big ship's picture (option shapes) and by
// the gun's or generator's picture (weapon shapes); -1 none.
#define ILLUSTRATION_PICTURES 64
static int illustration_models[ILLUSTRATION_PICTURES];
static int mount_models[ILLUSTRATION_PICTURES];
static M3DAppearance enemy_default;

static const M3DAppearance sprite_appearance = { .model = M3D_SPRITE };

static const char *config_path(char *buffer, size_t size, const char **dir_out)
{
	static char dir_buffer[1024];
	const char *dir = tyr3d_resource_dir("TYR3D_MODEL_DIR", TYR3D_MODEL_DIR, "models", dir_buffer, sizeof(dir_buffer));
	const char *file = SDL_getenv("TYR3D_MODEL_CONFIG");
	snprintf(buffer, size, "%s/%s", dir, file != NULL ? file : "models.cfg");
	*dir_out = dir;
	return buffer;
}

static int find_model(const char *name)
{
	for (int i = 0; i < m3d_model_count; ++i)
		if (strcmp(m3d_models[i].name, name) == 0)
			return i;
	return -1;
}

// A model name, "volume" or "sprite"/"none". Returns false for unknown names.
static bool parse_kind(const char *token, int *kind)
{
	if (strcmp(token, "sprite") == 0 || strcmp(token, "none") == 0)
		*kind = M3D_SPRITE;
	else if (strcmp(token, "volume") == 0)
		*kind = M3D_VOLUME;
	else if ((*kind = find_model(token)) < 0)
		return false;
	return true;
}

static float option_float(const char *value, float fallback)
{
	char *end;
	const double v = strtod(value, &end);
	return end != value ? (float)v : fallback;
}

#define DEFAULT_GLOW_SIZE 1.25f     // glow alone: times the sprite's width
#define DEFAULT_GLOW_STRENGTH 0.3f

// key=value options shared by enemy, sprite and ship lines.
static bool parse_option(const char *token, M3DAppearance *a)
{
	if (strcmp(token, "glow") == 0)
	{
		a->glow_size = -DEFAULT_GLOW_SIZE;  // negative: relative to the sprite's width
		a->glow_strength = DEFAULT_GLOW_STRENGTH;
		return true;
	}

	const char *eq = strchr(token, '=');
	if (eq == NULL)
		return false;
	const size_t key_length = (size_t)(eq - token);
	const char *value = eq + 1;

	if (key_length == 3 && strncmp(token, "yaw", 3) == 0)
	{
		if (strcmp(value, "velocity") == 0)
			a->yaw_mode = M3D_YAW_VELOCITY;
		else if (strcmp(value, "aim") == 0)
			a->yaw_mode = M3D_YAW_AIM;
		else if (strncmp(value, "frames:", 7) == 0)
		{
			// frames:<count>[:<first frame yaw>][:ccw]
			a->yaw_mode = M3D_YAW_FRAMES;
			const int count = atoi(value + 7);
			const char *second = strchr(value + 7, ':');
			a->yaw = second != NULL ? option_float(second + 1, 180.0f) : 180.0f;
			a->yaw_step = count > 0 ? 360.0f / count : 0.0f;
			if (strstr(value, ":ccw") != NULL)
				a->yaw_step = -a->yaw_step;
		}
		else
		{
			a->yaw_mode = M3D_YAW_FIXED;
			a->yaw = option_float(value, a->yaw);
		}
		return true;
	}
	if (key_length == 4 && strncmp(token, "roll", 4) == 0 && strncmp(value, "frames:", 7) == 0)
	{
		// frames:<count>[:ccw]: the animation is a roll about the nose, a full turn in count frames
		const int count = atoi(value + 7);
		a->roll_step = count > 0 ? 360.0f / count : 0.0f;
		if (strstr(value, ":ccw") != NULL)
			a->roll_step = -a->roll_step;
		return true;
	}
	if (key_length == 6 && strncmp(token, "height", 6) == 0)
	{
		a->height = option_float(value, 0.0f);
		return true;
	}
	if (key_length == 5 && strncmp(token, "layer", 5) == 0)
	{
		a->layer = 1 + (strcmp(value, "ground") == 0 ? L3D_GROUND_ENEMY : strcmp(value, "sky") == 0 ? L3D_SKY_ENEMY :
		                strcmp(value, "top") == 0 ? L3D_TOP_ENEMY : -1);
		return a->layer > 0;
	}
	if (key_length == 7 && strncmp(token, "banking", 7) == 0)
	{
		a->banking = strcmp(value, "off") != 0 && strcmp(value, "0") != 0;
		return true;
	}
	if (key_length == 4 && strncmp(token, "spin", 4) == 0)
	{
		a->spin = option_float(value, 0.0f);
		return true;
	}
	if (key_length == 5 && strncmp(token, "color", 5) == 0 && strcmp(value, "sprite") == 0)
	{
		a->recolor = true;
		return true;
	}
	if (key_length == 4 && strncmp(token, "glow", 4) == 0)
	{
		// glow=<size>[:<strength>[:<palette index or #rrggbb>[:<dx>:<dy>]]]
		a->glow_size = option_float(value, 0.0f);
		const char *colon = strchr(value, ':');
		a->glow_strength = colon != NULL ? option_float(colon + 1, DEFAULT_GLOW_STRENGTH) : DEFAULT_GLOW_STRENGTH;
		const char *colon2 = colon != NULL ? strchr(colon + 1, ':') : NULL;
		a->glow_has_rgb = colon2 != NULL && colon2[1] == '#';
		if (a->glow_has_rgb)
		{
			const unsigned long rgb = strtoul(colon2 + 2, NULL, 16);
			a->glow_rgb[0] = (Uint8)(rgb >> 16);
			a->glow_rgb[1] = (Uint8)(rgb >> 8);
			a->glow_rgb[2] = (Uint8)rgb;
		}
		a->glow_color = colon2 != NULL && !a->glow_has_rgb ? (Uint8)SDL_clamp(atoi(colon2 + 1), 0, 255) : 0;
		const char *colon3 = colon2 != NULL ? strchr(colon2 + 1, ':') : NULL;
		const char *colon4 = colon3 != NULL ? strchr(colon3 + 1, ':') : NULL;
		a->glow_dx = colon3 != NULL ? option_float(colon3 + 1, 0.0f) : 0.0f;
		a->glow_dy = colon4 != NULL ? option_float(colon4 + 1, 0.0f) : 0.0f;
		return true;
	}
	return false;
}

// The sheet of a "sprite" line: a shape file letter, or "coins" and "powerups" (the catalogue
// calls the latter "twoplayer").
static char parse_sheet(const char *token)
{
	if (strcmp(token, "coins") == 0)
		return M3D_SHEET_COINS;
	if (strcmp(token, "powerups") == 0 || strcmp(token, "twoplayer") == 0)
		return M3D_SHEET_POWERUPS;
	// x<hex>: a sheet whose letter is a symbol, as the catalogue names it (x23 is '#', which would
	// start a comment here).
	if ((token[0] == 'x' || token[0] == 'X') && strlen(token) == 3 && SDL_isxdigit((unsigned char)token[1]) &&
	    SDL_isxdigit((unsigned char)token[2]))
		return (char)strtol(token + 1, NULL, 16);
	return (char)SDL_tolower((unsigned char)token[0]);
}

static M3DAppearance enemy_options_default(void)
{
	return (M3DAppearance){ .model = M3D_SPRITE, .yaw_mode = M3D_YAW_FIXED, .yaw = 180.0f };
}

static void parse_line(char *line, const char *dir, const char *file, int line_number)
{
	char *tokens[24];
	int count = 0;
	for (char *token = strtok(line, " \t\r\n"); token != NULL && count < 24; token = strtok(NULL, " \t\r\n"))
	{
		if (token[0] == '#')
			break;
		tokens[count++] = token;
	}
	if (count == 0)
		return;

	#define WARN(...) do { fprintf(stderr, "warning: %s:%d: ", file, line_number); fprintf(stderr, __VA_ARGS__); fputc('\n', stderr); } while (0)

	if (strcmp(tokens[0], "model") == 0 && count >= 3)
	{
		if (m3d_model_count == M3D_MAX_MODELS)
		{
			WARN("too many models");
			return;
		}
		M3DModel *model = &m3d_models[m3d_model_count++];
		SDL_strlcpy(model->name, tokens[1], sizeof(model->name));
		snprintf(model->path, sizeof(model->path), "%s/%s", dir, tokens[2]);
		// The numbers in order (size, yaw, pitch, roll); "origin" anywhere among them.
		float numbers[4] = { 0, 0, 0, 0 };
		int n = 0;
		model->keep_origin = false;
		for (int t = 3; t < count; ++t)
		{
			if (strcmp(tokens[t], "origin") == 0)
				model->keep_origin = true;
			else if (n < 4)
				numbers[n++] = option_float(tokens[t], 0.0f);
		}
		model->size = numbers[0];
		model->yaw = numbers[1];
		model->pitch = numbers[2];
		model->roll = numbers[3];
		return;
	}

	// illustration <option sprite> <model>, mount <weapon sprite> <model>: the store's illustration.
	if ((strcmp(tokens[0], "illustration") == 0 || strcmp(tokens[0], "mount") == 0) && count >= 3)
	{
		const int picture = atoi(tokens[1]);
		const int model = find_model(tokens[2]);
		if (picture < 0 || picture >= ILLUSTRATION_PICTURES)
			WARN("picture %d out of range", picture);
		else if (model < 0)
			WARN("unknown model '%s'", tokens[2]);
		else
			(tokens[0][0] == 'i' ? illustration_models : mount_models)[picture] = model;
		return;
	}

	// player <model> [options] is "ship any". sidekick <id|any> <model> [options] works the same.
	const bool sidekick = strcmp(tokens[0], "sidekick") == 0 && count >= 3;
	if ((strcmp(tokens[0], "player") == 0 && count >= 2) || (strcmp(tokens[0], "ship") == 0 && count >= 3) || sidekick)
	{
		const bool any = tokens[0][0] == 'p' || strcmp(tokens[1], "any") == 0;
		const int first_option = tokens[0][0] == 'p' ? 2 : 3;
		ShipRule rule = { .ship = any ? 0 : !sidekick && strcmp(tokens[1], "dragonwing") == 0 ? M3D_SHIP_DRAGONWING
		                                                                                     : (unsigned int)atoi(tokens[1]) };
		rule.appearance = (M3DAppearance){ .model = M3D_SPRITE, .banking = true };
		if (!parse_kind(tokens[first_option - 1], &rule.appearance.model))
		{
			WARN("unknown model '%s'", tokens[first_option - 1]);
			return;
		}
		for (int i = first_option; i < count; ++i)
			if (!parse_option(tokens[i], &rule.appearance))
				WARN("unknown option '%s'", tokens[i]);
		if (sidekick)
		{
			rule.appearance.banking = false;
			if (sidekick_rule_count < (int)COUNTOF(sidekick_rules))
				sidekick_rules[sidekick_rule_count++] = rule;
		}
		else if (ship_rule_count < (int)COUNTOF(ship_rules))
			ship_rules[ship_rule_count++] = rule;
		return;
	}

	if (strcmp(tokens[0], "enemy") == 0 && count >= 4)
	{
		if (rule_count == MAX_RULES)
		{
			WARN("too many enemy rules");
			return;
		}
		EnemyRule *rule = &rules[rule_count];
		rule->layer = strcmp(tokens[1], "ground") == 0 ? CLASS_GROUND
		            : strcmp(tokens[1], "sky") == 0 ? CLASS_SKY
		            : strcmp(tokens[1], "top") == 0 ? CLASS_TOP
		            : CLASS_ANY;
		rule->size = strcmp(tokens[2], "1x1") == 0 ? SIZE_SMALL
		           : strcmp(tokens[2], "2x2") == 0 ? SIZE_LARGE
		           : SIZE_ANY;
		rule->model_count = 0;
		rule->options = enemy_options_default();
		for (int i = 3; i < count; ++i)
		{
			int kind;
			if (parse_option(tokens[i], &rule->options))
				continue;
			if (!parse_kind(tokens[i], &kind))
				WARN("unknown model '%s'", tokens[i]);
			else if (rule->model_count < MAX_RULE_MODELS)
				rule->models[rule->model_count++] = kind;
		}
		if (rule->model_count > 0)
			++rule_count;
		return;
	}

	if (strcmp(tokens[0], "shot") == 0 && count >= 4)
	{
		if (shot_rule_count == (int)COUNTOF(shot_rules))
		{
			WARN("too many shot rules");
			return;
		}
		if (strcmp(tokens[1], "shots") != 0 && strcmp(tokens[1], "shots2") != 0)
		{
			WARN("unknown shot sheet '%s' (shots or shots2)", tokens[1]);
			return;
		}
		M3DAppearance a = { .model = M3D_SPRITE, .yaw_mode = M3D_YAW_FIXED, .yaw = 0.0f };
		if (!parse_kind(tokens[3], &a.model))
		{
			WARN("unknown model '%s'", tokens[3]);
			return;
		}
		for (int i = 4; i < count; ++i)
			if (!parse_option(tokens[i], &a))
				WARN("unknown option '%s'", tokens[i]);
		shot_rules[shot_rule_count].sheet = strcmp(tokens[1], "shots2") == 0;
		shot_rules[shot_rule_count].sprite = (unsigned int)strtoul(tokens[2], NULL, 10);
		shot_rules[shot_rule_count].appearance = a;
		++shot_rule_count;
		return;
	}

	if (strcmp(tokens[0], "frame") == 0 && count >= 4)
	{
		int model;
		if (frame_model_count == (int)COUNTOF(frame_models))
			WARN("too many frame models");
		else if (!parse_kind(tokens[3], &model) || model < 0)
			WARN("unknown model '%s'", tokens[3]);
		else
		{
			frame_models[frame_model_count].sheet = parse_sheet(tokens[1]);
			frame_models[frame_model_count].sprite = (unsigned int)strtoul(tokens[2], NULL, 10);
			frame_models[frame_model_count].model = model;
			++frame_model_count;
		}
		return;
	}

	if (strcmp(tokens[0], "standin") == 0 && count >= 4)
	{
		int model;
		if (standin_model_count == (int)COUNTOF(standin_models))
			WARN("too many stand-in models");
		else if (!parse_kind(tokens[3], &model) || model < 0)
			WARN("unknown model '%s'", tokens[3]);
		else
		{
			standin_models[standin_model_count].sheet = parse_sheet(tokens[1]);
			standin_models[standin_model_count].sprite = (unsigned int)strtoul(tokens[2], NULL, 10);
			standin_models[standin_model_count].model = model;
			++standin_model_count;
		}
		return;
	}

	if (strcmp(tokens[0], "wreck") == 0 && count >= 4)
	{
		int model;
		if (wreck_model_count == (int)COUNTOF(wreck_models))
			WARN("too many wreck models");
		else if (strcmp(tokens[3], "none") != 0 && (!parse_kind(tokens[3], &model) || model < 0))
			WARN("unknown model '%s'", tokens[3]);
		else
		{
			if (strcmp(tokens[3], "none") == 0)
				model = M3D_WRECK_NONE;
			wreck_models[wreck_model_count].sheet = parse_sheet(tokens[1]);
			wreck_models[wreck_model_count].sprite = (unsigned int)strtoul(tokens[2], NULL, 10);
			wreck_models[wreck_model_count].model = model;
			++wreck_model_count;
		}
		return;
	}

	if (strcmp(tokens[0], "sprite") == 0 && count >= 4)
	{
		if (override_count == (int)COUNTOF(overrides))
		{
			WARN("too many sprite overrides");
			return;
		}
		SpriteOverride *o = &overrides[override_count];
		o->sheet = parse_sheet(tokens[1]);
		o->sprite = (unsigned int)strtoul(tokens[2], NULL, 10);
		o->appearance = enemy_options_default();
		if (!parse_kind(tokens[3], &o->appearance.model))
		{
			WARN("unknown model '%s'", tokens[3]);
			return;
		}
		for (int i = 4; i < count; ++i)
			if (!parse_option(tokens[i], &o->appearance))
				WARN("unknown option '%s'", tokens[i]);
		++override_count;
		return;
	}

	if (strcmp(tokens[0], "default") == 0 && count >= 2)
	{
		enemy_default = enemy_options_default();
		if (!parse_kind(tokens[1], &enemy_default.model))
			WARN("unknown model '%s'", tokens[1]);
		for (int i = 2; i < count; ++i)
			if (!parse_option(tokens[i], &enemy_default))
				WARN("unknown option '%s'", tokens[i]);
		return;
	}

	WARN("can't parse line");
	#undef WARN
}

static void load(void)
{
	m3d_model_count = 0;
	rule_count = 0;
	override_count = 0;
	frame_model_count = 0;
	wreck_model_count = 0;
	standin_model_count = 0;
	shot_rule_count = 0;
	ship_rule_count = 0;
	sidekick_rule_count = 0;
	for (int i = 0; i < ILLUSTRATION_PICTURES; ++i)
		illustration_models[i] = mount_models[i] = -1;
	enemy_default = enemy_options_default();
	++m3d_generation;

	char path[600];
	const char *dir;
	config_path(path, sizeof(path), &dir);
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

	printf("models: %d models, %d enemy rules, %d sprite overrides, %d ship rules\n",
	       m3d_model_count, rule_count, override_count, ship_rule_count);
}

void m3d_init(void)
{
	load();
	m3d_enabled = SDL_getenv("TYR3D_NO_MODELS") == NULL;
}

void m3d_reload(void)
{
	load();
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

M3DAppearance m3d_enemy_appearance(char sheet, unsigned int first_sprite, bool large, L3DLayerType layer)
{
	if (!m3d_enabled || sheet == 0)
		return sprite_appearance;

	sheet = (char)SDL_tolower((unsigned char)sheet);
	for (int i = 0; i < override_count; ++i)
		if (overrides[i].sheet == sheet && overrides[i].sprite == first_sprite)
			return overrides[i].appearance;

	const LayerClass lc = layer_class(layer);
	const SizeClass sc = large ? SIZE_LARGE : SIZE_SMALL;
	for (int i = 0; i < rule_count; ++i)
	{
		const EnemyRule *rule = &rules[i];
		if ((rule->layer == CLASS_ANY || rule->layer == lc) && (rule->size == SIZE_ANY || rule->size == sc))
		{
			// Stable pick per enemy type so it keeps its look.
			const unsigned int hash = (unsigned int)(unsigned char)sheet * 2654435761u ^ first_sprite * 40503u;
			M3DAppearance a = rule->options;
			a.model = rule->models[(hash >> 7) % rule->model_count];
			return a;
		}
	}
	return enemy_default;
}

static M3DAppearance find_rule(const ShipRule *rules, int count, unsigned int id)
{
	if (!m3d_enabled)
		return sprite_appearance;

	const ShipRule *any = NULL;
	for (int i = 0; i < count; ++i)
	{
		if (rules[i].ship == id)
			return rules[i].appearance;
		if (rules[i].ship == 0 && any == NULL)
			any = &rules[i];
	}
	return any != NULL ? any->appearance : sprite_appearance;
}

M3DAppearance m3d_ship_appearance(unsigned int ship_id)
{
	return find_rule(ship_rules, ship_rule_count, ship_id);
}

M3DAppearance m3d_sidekick_appearance(unsigned int sidekick_id)
{
	return find_rule(sidekick_rules, sidekick_rule_count, sidekick_id);
}

int m3d_illustration_model(int option_sprite)
{
	return m3d_enabled && option_sprite >= 0 && option_sprite < ILLUSTRATION_PICTURES ? illustration_models[option_sprite] : -1;
}

int m3d_mount_model(int weapon_sprite)
{
	return m3d_enabled && weapon_sprite >= 0 && weapon_sprite < ILLUSTRATION_PICTURES ? mount_models[weapon_sprite] : -1;
}

bool m3d_shot_appearance(bool shots2, unsigned int sprite, M3DAppearance *appearance)
{
	if (!m3d_enabled)
		return false;
	for (int i = 0; i < shot_rule_count; ++i)
		if (shot_rules[i].sheet == shots2 && shot_rules[i].sprite == sprite)
		{
			*appearance = shot_rules[i].appearance;
			return appearance->model >= 0;
		}
	return false;
}

int m3d_frame_model(char sheet, unsigned int sprite, int model)
{
	sheet = (char)SDL_tolower((unsigned char)sheet);
	for (int i = 0; i < frame_model_count; ++i)
		if (frame_models[i].sheet == sheet && frame_models[i].sprite == sprite)
			return frame_models[i].model;
	return model;
}

int m3d_standin_model(char sheet, unsigned int sprite)
{
	sheet = (char)SDL_tolower((unsigned char)sheet);
	for (int i = 0; i < standin_model_count; ++i)
		if (standin_models[i].sheet == sheet && standin_models[i].sprite == sprite)
			return standin_models[i].model;
	return -1;
}

int m3d_wreck_model(char sheet, unsigned int sprite)
{
	sheet = (char)SDL_tolower((unsigned char)sheet);
	for (int i = 0; i < wreck_model_count; ++i)
		if (wreck_models[i].sheet == sheet && wreck_models[i].sprite == sprite)
			return wreck_models[i].model;
	return -1;
}

int m3d_find_model(const char *name)
{
	for (int i = 0; i < m3d_model_count; ++i)
		if (strcmp(m3d_models[i].name, name) == 0)
			return i;
	return -1;
}

int m3d_sprite_rule_count(void)
{
	return override_count;
}

void m3d_sprite_rule(int i, char *sheet, unsigned int *first_sprite, M3DAppearance *appearance)
{
	*sheet = overrides[i].sheet;
	*first_sprite = overrides[i].sprite;
	*appearance = overrides[i].appearance;
}
