/*
 * Tyrian3D: the rogue mode. See rogue.h.
 */
#include "rogue.h"

#include "config.h"
#include "content.h"
#include "episodes.h"
#include "file.h"
#include "font.h"
#include "fonthand.h"
#include "game_menu.h"
#include "joystick.h"
#include "keyboard.h"
#include "loudness.h"
#include "lvlmast.h"
#include "mainint.h"
#include "mouse.h"
#include "musmast.h"
#include "nortsong.h"
#include "palette.h"
#include "params.h"
#include "paths3d.h"
#include "picload.h"
#include "player.h"
#include "sndmast.h"
#include "sprite.h"
#include "varz.h"
#include "vga256d.h"
#include "video.h"

#include <SDL3/SDL.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

bool rogue_run = false;

/* --- The data (assets/content/rogue.cfg) ------------------------------------------------- */

#define MAX_ACTS 6
#define MAX_ACT_LEVELS 32
#define MAX_BOSSES 8
#define MAX_POOL 256
#define MAX_UNLOCKS 16

typedef struct
{
	Uint8 episode, section;
	char name[12];
} RogueLevel;

typedef struct
{
	char name[40];
	int difficulty, rows;
	RogueLevel levels[MAX_ACT_LEVELS];
	int level_count;
	RogueLevel bosses[MAX_BOSSES];
	int boss_count;
} Act;

typedef enum
{
	ITEM_FRONT,
	ITEM_REAR,
	ITEM_LEFT,
	ITEM_RIGHT,
	ITEM_SHIELD,
	ITEM_GENERATOR,
	ITEM_SHIP,
	ITEM_SPECIAL,
	ITEM_KINDS
} ItemKind;

static const char *const item_kind_names[ITEM_KINDS] = { "front", "rear", "left", "right", "shield", "generator", "ship", "special" };
static const char *const item_kind_titles[ITEM_KINDS] =
	{ "Front Gun", "Rear Gun", "Left Sidekick", "Right Sidekick", "Shield", "Generator", "Ship", "Special" };

typedef struct
{
	Uint8 kind, id, tier;
	Sint8 unlock;  // the unlock it needs, or -1
} PoolItem;

typedef struct
{
	char name[16];
	int cost;
	char title[32];
	char text[64];
} Unlock;

static Act acts[MAX_ACTS];
static int act_count = 0;
static PoolItem pool[MAX_POOL];
static int pool_count = 0;
static Unlock unlocks[MAX_UNLOCKS];
static int unlock_count = 0;

static int unlock_index(const char *name)
{
	for (int i = 0; i < unlock_count; ++i)
		if (strcmp(unlocks[i].name, name) == 0)
			return i;
	return -1;
}

static const char *value_of(char **tokens, int count, const char *key)
{
	const size_t length = strlen(key);
	for (int i = 0; i < count; ++i)
		if (strncmp(tokens[i], key, length) == 0 && tokens[i][length] == '=')
			return tokens[i] + length + 1;
	return NULL;
}

static bool load_data(void)
{
	if (act_count > 0)
		return true;
	char dir[1024], path[1200];
	snprintf(path, sizeof(path), "%s/rogue.cfg", tyr3d_resource_dir("TYR3D_CONTENT_DIR", TYR3D_CONTENT_DIR, "content", dir, sizeof(dir)));
	FILE *f = fopen(path, "r");
	if (f == NULL)
	{
		fprintf(stderr, "warning: rogue: no %s\n", path);
		return false;
	}
	// Unlocks first (items name them), so the file is read twice.
	char line[512];
	for (int pass = 0; pass < 2; ++pass)
	{
		rewind(f);
		while (fgets(line, sizeof(line), f) != NULL)
		{
			char *tokens[16];
			const int count = content_tokenize(line, tokens, 16);
			if (count < 2)
				continue;
			const char *v;
			if (pass == 0)
			{
				if (strcmp(tokens[0], "unlock") == 0 && unlock_count < MAX_UNLOCKS)
				{
					Unlock *u = &unlocks[unlock_count++];
					SDL_strlcpy(u->name, tokens[1], sizeof(u->name));
					u->cost = (v = value_of(tokens, count, "cost")) != NULL ? atoi(v) : 1;
					SDL_strlcpy(u->title, (v = value_of(tokens, count, "title")) != NULL ? v : u->name, sizeof(u->title));
					SDL_strlcpy(u->text, (v = value_of(tokens, count, "text")) != NULL ? v : "", sizeof(u->text));
				}
				continue;
			}
			if (strcmp(tokens[0], "act") == 0)
			{
				const int n = atoi(tokens[1]);
				if (n < 1 || n > MAX_ACTS)
					continue;
				Act *a = &acts[n - 1];
				SDL_strlcpy(a->name, (v = value_of(tokens, count, "name")) != NULL ? v : "Act", sizeof(a->name));
				a->difficulty = (v = value_of(tokens, count, "difficulty")) != NULL ? atoi(v) : DIFFICULTY_NORMAL;
				a->rows = SDL_clamp((v = value_of(tokens, count, "rows")) != NULL ? atoi(v) : 3, 1, 6);
				act_count = SDL_max(act_count, n);
			}
			else if ((strcmp(tokens[0], "level") == 0 || strcmp(tokens[0], "boss") == 0) && count >= 4)
			{
				const int n = atoi(tokens[1]);
				int episode = 0, section = 0;
				if (n < 1 || n > MAX_ACTS || sscanf(tokens[2], "%d:%d", &episode, &section) != 2 ||
				    episode < 1 || episode > EPISODE_MAX || !episodeAvail[episode - 1])
					continue;
				Act *a = &acts[n - 1];
				const bool boss = tokens[0][0] == 'b';
				RogueLevel *l = boss ? (a->boss_count < MAX_BOSSES ? &a->bosses[a->boss_count++] : NULL)
				                     : (a->level_count < MAX_ACT_LEVELS ? &a->levels[a->level_count++] : NULL);
				if (l == NULL)
					continue;
				l->episode = (Uint8)episode;
				l->section = (Uint8)section;
				SDL_strlcpy(l->name, tokens[3], sizeof(l->name));
			}
			else if (strcmp(tokens[0], "item") == 0 && count >= 3 && pool_count < MAX_POOL)
			{
				int kind = 0;
				while (kind < ITEM_KINDS && strcmp(item_kind_names[kind], tokens[1]) != 0)
					++kind;
				if (kind == ITEM_KINDS)
					continue;
				PoolItem *p = &pool[pool_count++];
				p->kind = (Uint8)kind;
				p->id = (Uint8)atoi(tokens[2]);
				p->tier = (Uint8)SDL_clamp((v = value_of(tokens, count, "tier")) != NULL ? atoi(v) : 1, 1, 3);
				p->unlock = (Sint8)((v = value_of(tokens, count, "unlock")) != NULL ? unlock_index(v) : -1);
			}
		}
	}
	fclose(f);
	// An act needs levels and a boss.
	for (int i = 0; i < act_count; ++i)
		if (acts[i].level_count < 2 || acts[i].boss_count < 1)
			act_count = i;
	printf("rogue: %d acts, %d items, %d unlocks\n", act_count, pool_count, unlock_count);
	return act_count > 0;
}

/* --- The profile (kept between runs) ------------------------------------------------------ */

static struct
{
	int cores, runs, wins, best_act;
	Uint32 unlocked;  // a bit per unlock
} profile;

static bool profile_loaded = false;

static void load_profile(void)
{
	if (profile_loaded)
		return;
	profile_loaded = true;
	FILE *f = dir_fopen_warn(get_user_directory(), "tyrian3d_rogue.cfg", "r");
	if (f == NULL)
		return;
	char line[512];
	while (fgets(line, sizeof(line), f) != NULL)
	{
		char *tokens[24];
		const int count = content_tokenize(line, tokens, 24);
		if (count < 2)
			continue;
		if (strcmp(tokens[0], "cores") == 0)
			profile.cores = atoi(tokens[1]);
		else if (strcmp(tokens[0], "runs") == 0)
			profile.runs = atoi(tokens[1]);
		else if (strcmp(tokens[0], "wins") == 0)
			profile.wins = atoi(tokens[1]);
		else if (strcmp(tokens[0], "best_act") == 0)
			profile.best_act = atoi(tokens[1]);
		else if (strcmp(tokens[0], "unlocked") == 0)
			for (int i = 1; i < count; ++i)
			{
				const int u = unlock_index(tokens[i]);
				if (u >= 0)
					profile.unlocked |= 1u << u;
			}
	}
	fclose(f);
}

static void save_profile(void)
{
	// Test runs (TYR3D_ROGUE) leave the player's profile alone.
	if (SDL_getenv("TYR3D_ROGUE") != NULL)
		return;
	FILE *f = dir_fopen_warn(get_user_directory(), "tyrian3d_rogue.cfg", "w");
	if (f == NULL)
		return;
	fprintf(f, "# Tyrian3D rogue mode: cores, unlocks and runs\ncores %d\nruns %d\nwins %d\nbest_act %d\nunlocked",
	        profile.cores, profile.runs, profile.wins, profile.best_act);
	for (int i = 0; i < unlock_count; ++i)
		if (profile.unlocked & (1u << i))
			fprintf(f, " %s", unlocks[i].name);
	fprintf(f, "\n");
	fclose(f);
}

static bool unlocked(const char *name)
{
	const int u = unlock_index(name);
	return u >= 0 && (profile.unlocked & (1u << u)) != 0;
}

/* --- The run ------------------------------------------------------------------------------ */

enum
{
	NODE_FIGHT,
	NODE_ELITE,
	NODE_MERCHANT,
	NODE_BOSS,
};

#define MAX_ROWS 8
#define MAX_COLS 3

typedef struct
{
	Uint8 kind;
	Sint8 level;  // in the act's levels (its bosses for a boss)
	Uint8 next;   // a bit per node of the next row it leads to
	Uint8 planet;  // its sprite (PLANET_SHAPES)
} Node;

static struct
{
	Uint32 rng;
	int act;
	int rows;  // the act's rows, the boss's the last
	int width[MAX_ROWS];
	Node nodes[MAX_ROWS][MAX_COLS];
	int row, col;  // where the ship is (row -1: the act's start)
	bool used[MAX_ACTS][MAX_ACT_LEVELS];
	int lives;     // extra lives
	int levels, bosses;
	int cores;     // earned this run
	Player at_start;  // as the level began, for a life
	int kind;      // the level's node kind
	const RogueLevel *level;
} run;

static Uint32 rnd(void)
{
	// xorshift32: the run's own numbers, apart from the game's.
	Uint32 x = run.rng;
	x ^= x << 13;
	x ^= x >> 17;
	x ^= x << 5;
	return run.rng = x;
}

static int rnd_below(int n)
{
	return n > 0 ? (int)(rnd() % (Uint32)n) : 0;
}

static const Node *node_at(int row, int col)
{
	return &run.nodes[row][col];
}

static int pick_level(int act, int kind)
{
	const Act *a = &acts[act];
	if (kind == NODE_BOSS)
		return rnd_below(a->boss_count);
	int free[MAX_ACT_LEVELS], count = 0;
	for (int i = 0; i < a->level_count; ++i)
		if (!run.used[act][i])
			free[count++] = i;
	if (count == 0)
	{
		memset(run.used[act], 0, sizeof(run.used[act]));
		return rnd_below(a->level_count);
	}
	const int i = free[rnd_below(count)];
	run.used[act][i] = true;
	return i;
}

// A planet for a node: a sprite of the shop's map (the first frame of a turning planet); bosses
// get the big ones.
static Uint8 pick_planet(bool boss, int level, const Node *row, int count)
{
	static const Uint8 planets[] = { 3, 35, 67, 83, 99, 115, 131, 150 }, big[] = { 35, 99, 115, 150 };
	const Uint8 *from = boss ? big : planets;
	const int n = boss ? (int)COUNTOF(big) : (int)COUNTOF(planets);
	// The level's own (the same in every run), unless a node beside it has that one.
	for (int k = 0; k < n; ++k)
	{
		const Uint8 planet = from[(level * 5 + run.act * 3 + k) % n];
		bool taken = false;
		for (int i = 0; i < count; ++i)
			taken |= row[i].planet == planet;
		if (!taken)
			return planet;
	}
	return from[0];
}

// The act's map: rows of 2-3 nodes (the first row only fights), each leading to the nearest
// nodes of the next row, and the boss.
static void make_map(void)
{
	const Act *a = &acts[run.act];
	run.rows = SDL_min(a->rows + 1, MAX_ROWS);
	memset(run.nodes, 0, sizeof(run.nodes));
	for (int r = 0; r < run.rows; ++r)
	{
		const bool boss = r == run.rows - 1;
		run.width[r] = boss ? 1 : 2 + rnd_below(2);
		bool merchant = false;
		for (int c = 0; c < run.width[r]; ++c)
		{
			Node *n = &run.nodes[r][c];
			if (boss)
				n->kind = NODE_BOSS;
			else if (r == 0)
				n->kind = NODE_FIGHT;
			else
			{
				const int roll = rnd_below(100);
				n->kind = roll < 22 ? NODE_ELITE : (roll < 38 && !merchant) ? NODE_MERCHANT : NODE_FIGHT;
				merchant |= n->kind == NODE_MERCHANT;
			}
			n->level = (Sint8)(n->kind == NODE_MERCHANT ? -1 : pick_level(run.act, n->kind));
			n->planet = pick_planet(boss, n->level, run.nodes[r], c);
		}
	}
	// Each node leads to the next row's nodes near it; each node there is reached from one.
	for (int r = 0; r + 1 < run.rows; ++r)
	{
		const int w = run.width[r], w2 = run.width[r + 1];
		for (int c = 0; c < w; ++c)
		{
			const float x = (c + 0.5f) / w;
			int nearest = 0;
			for (int k = 0; k < w2; ++k)
			{
				const float x2 = (k + 0.5f) / w2;
				if (SDL_fabsf(x2 - x) <= 0.34f)
					run.nodes[r][c].next |= (Uint8)(1u << k);
				if (SDL_fabsf(x2 - x) < SDL_fabsf((nearest + 0.5f) / w2 - x))
					nearest = k;
			}
			run.nodes[r][c].next |= (Uint8)(1u << nearest);
		}
		for (int k = 0; k < w2; ++k)
		{
			bool reached = false;
			for (int c = 0; c < w; ++c)
				reached |= (run.nodes[r][c].next >> k) & 1;
			if (!reached)
				run.nodes[r][SDL_min(k * w / w2, w - 1)].next |= (Uint8)(1u << k);
		}
	}
	run.row = -1;
	run.col = 0;
}

static bool reachable(int row, int col)
{
	if (row != run.row + 1 || row >= run.rows || col >= run.width[row])
		return false;
	return run.row < 0 || ((node_at(run.row, run.col)->next >> col) & 1);
}

/* --- Cards -------------------------------------------------------------------------------- */

typedef enum
{
	CARD_ITEM,
	CARD_POWER_FRONT,
	CARD_POWER_REAR,
	CARD_LIFE,
	CARD_CASH,
} CardKind;

typedef struct
{
	Uint8 kind, item_kind, id, tier;
	Uint32 amount;  // credits
	Uint32 price;   // at a merchant
	bool sold;
} Card;

static Uint8 *item_slot(int kind)
{
	PlayerItems *items = &player[0].items;
	switch (kind)
	{
	case ITEM_FRONT: return &items->weapon[FRONT_WEAPON].id;
	case ITEM_REAR: return &items->weapon[REAR_WEAPON].id;
	case ITEM_LEFT: return &items->sidekick[LEFT_SIDEKICK];
	case ITEM_RIGHT: return &items->sidekick[RIGHT_SIDEKICK];
	case ITEM_SHIELD: return &items->shield;
	case ITEM_GENERATOR: return &items->generator;
	case ITEM_SHIP: return &items->ship;
	default: return &items->special;
	}
}

static long item_cost(int kind, int id)
{
	switch (kind)
	{
	case ITEM_FRONT:
	case ITEM_REAR: return weaponPort[id].cost;
	case ITEM_LEFT:
	case ITEM_RIGHT: return options[id].cost;
	case ITEM_SHIELD: return shields[id].cost;
	case ITEM_GENERATOR: return powerSys[id].cost;
	case ITEM_SHIP: return ships[id].cost;
	default: return 4000 + 3000 * (long)special[id].pwr / 10;
	}
}

// Whether the card for this item is worth offering: a different item, and for shields and
// generators a better one.
static bool item_wanted(const PoolItem *p)
{
	if (p->unlock >= 0 && !(profile.unlocked & (1u << p->unlock)))
		return false;
	const int current = *item_slot(p->kind);
	if (current == p->id)
		return false;
	if (p->kind == ITEM_SHIELD)
		return shields[p->id].mpwr > shields[current].mpwr;
	if (p->kind == ITEM_GENERATOR)
		return powerSys[p->id].power > powerSys[current].power;
	return true;
}

// A card's tier: rarer ones later in the run and from harder levels (boost).
static int roll_tier(int boost)
{
	static const int weights[5][3] = { { 75, 22, 3 }, { 50, 40, 10 }, { 30, 45, 25 }, { 15, 45, 40 }, { 5, 40, 55 } };
	const int *w = weights[SDL_clamp(run.act + boost, 0, 4)];
	const int roll = rnd_below(100);
	return roll < w[0] ? 1 : roll < w[0] + w[1] ? 2 : 3;
}

static bool same_card(const Card *a, const Card *b)
{
	return a->kind == b->kind && (a->kind != CARD_ITEM || (a->item_kind == b->item_kind && a->id == b->id));
}

static Card deal_card(int boost, const Card *others, int other_count)
{
	const PlayerItems *items = &player[0].items;
	Card card = { 0 };
	for (int attempt = 0; attempt < 64; ++attempt)
	{
		memset(&card, 0, sizeof(card));
		card.tier = (Uint8)roll_tier(boost);
		const int front_power = items->weapon[FRONT_WEAPON].power, rear_power = items->weapon[REAR_WEAPON].power;
		const int w_power = front_power < 11 ? 22 : 0;
		const int w_rear = items->weapon[REAR_WEAPON].id != 0 && rear_power < 11 ? 10 : 0;
		const int w_life = card.tier == 3 ? 6 : 0;
		const int w_cash = 9;
		const int w_item = 60;
		int roll = rnd_below(w_power + w_rear + w_life + w_cash + w_item);
		if ((roll -= w_power) < 0)
		{
			card.kind = CARD_POWER_FRONT;
			card.tier = (Uint8)(front_power >= 7 ? 3 : front_power >= 4 ? 2 : 1);
		}
		else if ((roll -= w_rear) < 0)
		{
			card.kind = CARD_POWER_REAR;
			card.tier = (Uint8)(rear_power >= 7 ? 3 : rear_power >= 4 ? 2 : 1);
		}
		else if ((roll -= w_life) < 0)
			card.kind = CARD_LIFE;
		else if ((roll -= w_cash) < 0)
		{
			card.kind = CARD_CASH;
			card.amount = (Uint32)(2000 + 2000 * run.act) * card.tier;
		}
		else
		{
			// An item of that tier (or the nearest tier that has one).
			int candidates[MAX_POOL], count = 0;
			for (int t = 0; t < 3 && count == 0; ++t)
			{
				const int tier = card.tier + (t == 1 ? -1 : t == 2 ? 1 : 0);
				for (int i = 0; i < pool_count; ++i)
					if (pool[i].tier == tier && item_wanted(&pool[i]))
						candidates[count++] = i;
				if (count > 0)
					card.tier = (Uint8)tier;
			}
			if (count == 0)
				continue;
			const PoolItem *p = &pool[candidates[rnd_below(count)]];
			card.kind = CARD_ITEM;
			card.item_kind = p->kind;
			card.id = p->id;
		}
		bool repeated = false;
		for (int i = 0; i < other_count; ++i)
			repeated |= same_card(&card, &others[i]);
		if (!repeated)
			break;
	}
	// The merchant's price.
	switch (card.kind)
	{
	case CARD_ITEM:
		card.price = (Uint32)SDL_max(500, item_cost(card.item_kind, card.id) * (card.item_kind <= ITEM_REAR ? 3 : 1));
		break;
	case CARD_POWER_FRONT:
	case CARD_POWER_REAR:
	{
		const int w = card.kind == CARD_POWER_FRONT ? FRONT_WEAPON : REAR_WEAPON;
		card.price = (Uint32)weapon_upgrade_cost(weaponPort[items->weapon[w].id].cost, items->weapon[w].power);
		break;
	}
	case CARD_LIFE:
		card.price = 25000;
		break;
	default:
		card.price = 0;
		break;
	}
	return card;
}

static void apply_card(const Card *card)
{
	PlayerItems *items = &player[0].items;
	switch (card->kind)
	{
	case CARD_ITEM:
		*item_slot(card->item_kind) = card->id;
		break;
	case CARD_POWER_FRONT:
		items->weapon[FRONT_WEAPON].power = (Uint8)SDL_min(items->weapon[FRONT_WEAPON].power + 1, 11);
		break;
	case CARD_POWER_REAR:
		items->weapon[REAR_WEAPON].power = (Uint8)SDL_min(items->weapon[REAR_WEAPON].power + 1, 11);
		break;
	case CARD_LIFE:
		++run.lives;
		break;
	case CARD_CASH:
		player[0].cash += card->amount;
		break;
	}
	printf("rogue: card %d %d %d, items: ship %d front %d/%d rear %d/%d sidekicks %d %d shield %d generator %d special %d\n",
	       card->kind, card->item_kind, card->id, items->ship, items->weapon[FRONT_WEAPON].id,
	       items->weapon[FRONT_WEAPON].power, items->weapon[REAR_WEAPON].id, items->weapon[REAR_WEAPON].power,
	       items->sidekick[LEFT_SIDEKICK], items->sidekick[RIGHT_SIDEKICK], items->shield, items->generator, items->special);
}

/* --- Drawing ------------------------------------------------------------------------------- */

// Hues of the shop's palette (the screens' palette): greys, orange to yellow, red, light blue.
#define HUE_TEXT 0
#define HUE_GOLD 7
#define HUE_RED 4
#define HUE_BLUE 8

static const char *trimmed(const char *name)
{
	static char out[4][40];
	static int next = 0;
	char *o = out[next++ % 4];
	SDL_strlcpy(o, name, sizeof(out[0]));
	char *gap = strstr(o, "  ");  // sidekicks name their ammunition after two spaces
	if (gap != NULL)
		*gap = '\0';
	for (int i = (int)strlen(o) - 1; i >= 0 && o[i] == ' '; --i)
		o[i] = '\0';
	return o;
}

static void line(SDL_Surface *s, int x0, int y0, int x1, int y1, Uint8 color, bool dotted)
{
	const int dx = abs(x1 - x0), dy = -abs(y1 - y0), sx = x0 < x1 ? 1 : -1, sy = y0 < y1 ? 1 : -1;
	int err = dx + dy, n = 0;
	for (; ; )
	{
		if (!dotted || (n++ / 2) % 2 == 0)
			JE_pix(s, x0, y0, color);
		if (x0 == x1 && y0 == y1)
			break;
		const int e2 = 2 * err;
		if (e2 >= dy)
			err += dy, x0 += sx;
		if (e2 <= dx)
			err += dx, y0 += sy;
	}
}

// The screens' backdrop: stars, in the shop's palette (the items' icons need it).
static void backdrop(SDL_Surface *s)
{
	JE_loadPic(s, 1, false);  // for its palette
	fill_rectangle_xy(s, 0, 0, 319, 199, 0);
	Uint32 seed = 12345;
	for (int i = 0; i < 260; ++i)
	{
		seed = seed * 1103515245u + 12345u;
		const int x = (int)((seed >> 8) % 320);
		seed = seed * 1103515245u + 12345u;
		const int y = (int)((seed >> 8) % 200);
		seed = seed * 1103515245u + 12345u;
		const int kind = (int)((seed >> 8) % 16);
		const Uint8 hue = kind == 0 ? HUE_BLUE : kind == 1 ? HUE_GOLD : HUE_TEXT;
		const int value = 3 + (int)((seed >> 16) % 7) + (kind < 2 ? 3 : 0);
		JE_pix(s, x, y, (Uint8)(hue * 16 + value));
	}
}

static void panel(SDL_Surface *s, int x, int y, int w, int h, Uint8 border)
{
	JE_barShade(s, x, y, x + w - 1, y + h - 1);
	JE_rectangle(s, x, y, x + w - 1, y + h - 1, border);
}

static void text(SDL_Surface *s, int x, int y, const char *t, Font font, FontAlignment align, Uint8 hue, Sint8 value)
{
	draw_font_hv_shadow(s, x, y, t, font, align, hue, value, false, 1);
}

// Text wrapped into lines of at most width pixels (centred on x); the y below it.
static int wrapped(SDL_Surface *s, int x, int y, int width, const char *t, Font font, Uint8 hue, Sint8 value, int max_lines)
{
	char buffer[128];
	SDL_strlcpy(buffer, t, sizeof(buffer));
	char *p = buffer;
	const int height = font == small_font ? 7 : 11;
	for (int n = 0; *p != '\0' && n < max_lines; ++n)
	{
		// The longest run of words that fits.
		char *end = p, *fits = NULL;
		for (; ; )
		{
			while (*end != '\0' && *end != ' ')
				++end;
			const char saved = *end;
			*end = '\0';
			const bool ok = JE_textWidth(p, font) <= width;
			*end = saved;
			if (!ok)
				break;
			fits = end;
			if (*end == '\0')
				break;
			++end;
		}
		if (fits == NULL)
			fits = end;  // a word longer than the line
		const char saved = *fits;
		*fits = '\0';
		text(s, x, y, p, font, centered, hue, value);
		*fits = saved;
		y += height;
		p = fits;
		while (*p == ' ')
			++p;
	}
	return y;
}

// Whether every word of the text fits in width pixels.
static bool words_fit(const char *t, Font font, int width)
{
	char buffer[128];
	SDL_strlcpy(buffer, t, sizeof(buffer));
	for (char *word = strtok(buffer, " "); word != NULL; word = strtok(NULL, " "))
		if (JE_textWidth(word, font) > width)
			return false;
	return true;
}

static void card_icon(SDL_Surface *s, const Card *card, int cx, int y)
{
	const PlayerItems *items = &player[0].items;
	// JE_drawItem's item types: 1 ship, 2 and 3 front and rear, 4 shield, 5 generator, 6 and 7 sidekicks.
	static const JE_byte draw_type[ITEM_KINDS] = { 2, 3, 6, 7, 4, 5, 1, 0 };
	int type = 0, id = 0;
	switch (card->kind)
	{
	case CARD_ITEM:
		type = draw_type[card->item_kind];
		id = card->id;
		break;
	case CARD_POWER_FRONT:
		type = 2, id = items->weapon[FRONT_WEAPON].id;
		break;
	case CARD_POWER_REAR:
		type = 3, id = items->weapon[REAR_WEAPON].id;
		break;
	case CARD_LIFE:
		type = 1, id = items->ship;
		break;
	}
	if (type != 0 && id != 0)
		JE_drawItem((JE_byte)type, (JE_word)id, (JE_word)(cx - 12), (JE_word)y);
	else if (card->kind == CARD_ITEM && card->item_kind == ITEM_SPECIAL && spriteSheet10.data != NULL &&
	         special[card->id].itemgraphic > 0)
		blit_sprite2x2(s, cx - 12, y, spriteSheet10, special[card->id].itemgraphic);
	else
		text(s, cx, y + 6, card->kind == CARD_CASH ? "$" : "?", large_font, centered, HUE_GOLD, 4);
}

static void card_texts(const Card *card, const char **title, const char **name, char *detail, size_t size)
{
	const PlayerItems *items = &player[0].items;
	*title = "";
	*name = "";
	detail[0] = '\0';
	switch (card->kind)
	{
	case CARD_ITEM:
	{
		const int id = card->id;
		*title = item_kind_titles[card->item_kind];
		switch (card->item_kind)
		{
		case ITEM_FRONT:
		case ITEM_REAR:
			*name = trimmed(weaponPort[id].name);
		{
			const int current = items->weapon[card->item_kind == ITEM_FRONT ? FRONT_WEAPON : REAR_WEAPON].id;
			if (current != 0)
				snprintf(detail, size, "Replaces %s, power kept", trimmed(weaponPort[current].name));
			else
				snprintf(detail, size, "A rear gun at power %d", items->weapon[REAR_WEAPON].power);
			break;
		}
		case ITEM_LEFT:
		case ITEM_RIGHT:
		{
			*name = trimmed(options[id].name);
			const char *ammo = strstr(options[id].name, "Ammo");
			if (ammo != NULL)
				snprintf(detail, size, "%s", trimmed(ammo));
			else
				snprintf(detail, size, "%s", options[id].pwr > 0 ? "Charges up" : "Unlimited fire");
			break;
		}
		case ITEM_SHIELD:
			*name = trimmed(shields[id].name);
			snprintf(detail, size, "Strength %d (now %d)", shields[id].mpwr, shields[items->shield].mpwr);
			break;
		case ITEM_GENERATOR:
			*name = trimmed(powerSys[id].name);
			snprintf(detail, size, "Power %d (now %d)", powerSys[id].power, powerSys[items->generator].power);
			break;
		case ITEM_SHIP:
			*name = trimmed(ships[id].name);
			snprintf(detail, size, "Armor %d (now %d)", ships[id].dmg, ships[items->ship].dmg);
			break;
		default:
			*name = trimmed(special[id].name);
			snprintf(detail, size, "Fires with the main gun");
			break;
		}
		break;
	}
	case CARD_POWER_FRONT:
	case CARD_POWER_REAR:
	{
		const int w = card->kind == CARD_POWER_FRONT ? FRONT_WEAPON : REAR_WEAPON;
		*title = "Power Up";
		*name = trimmed(weaponPort[items->weapon[w].id].name);
		snprintf(detail, size, "Power %d to %d", items->weapon[w].power, SDL_min(items->weapon[w].power + 1, 11));
		break;
	}
	case CARD_LIFE:
		*title = "Extra Life";
		*name = "Spare Hull";
		snprintf(detail, size, "Survive one more death");
		break;
	case CARD_CASH:
		*title = "Credits";
		*name = "Bounty";
		snprintf(detail, size, "+%lu credits", (unsigned long)card->amount);
		break;
	}
}

static void draw_card(SDL_Surface *s, const Card *card, int x, int y, int w, int h, bool selected, bool show_price)
{
	static const Uint8 tier_hue[4] = { HUE_TEXT, HUE_TEXT, HUE_BLUE, HUE_GOLD };
	static const Uint8 tier_border[4] = { HUE_TEXT * 16 + 8, HUE_TEXT * 16 + 8, HUE_BLUE * 16 + 8, HUE_GOLD * 16 + 12 };
	static const char *const tier_names[4] = { "", "Common", "Rare", "Epic" };
	panel(s, x, y, w, h, selected ? 255 : tier_border[card->tier]);
	if (selected)
		JE_rectangle(s, x + 1, y + 1, x + w - 2, y + h - 2, 255);
	const int cx = x + w / 2;
	const char *title, *name;
	char detail[64];
	card_texts(card, &title, &name, detail, sizeof(detail));
	text(s, cx, y + 4, tier_names[card->tier], small_font, centered, tier_hue[card->tier], selected ? 4 : 1);
	text(s, cx, y + 13, title, small_font, centered, HUE_TEXT, selected ? 2 : -1);
	card_icon(s, card, cx, y + 25);
	const Font name_font = words_fit(name, normal_font, w - 6) ? normal_font : small_font;
	int ty = wrapped(s, cx, y + 58, w - 6, name, name_font, HUE_TEXT, selected ? 4 : 1, 3);
	if (!card->sold)
		wrapped(s, cx, ty + 3, w - 6, detail, small_font, HUE_TEXT, selected ? 0 : -3, 4);
	if (show_price)
	{
		char price[32];
		if (card->sold)
			snprintf(price, sizeof(price), "Sold");
		else
			snprintf(price, sizeof(price), "%lu", (unsigned long)card->price);
		text(s, cx, y + h - 11, price, small_font, centered, card->price <= player[0].cash || card->sold ? HUE_GOLD : HUE_RED,
		     card->sold ? -4 : 3);
	}
}

/* --- Input ---------------------------------------------------------------------------------- */

// TYR3D_ROGUE_AUTO: the screens choose by themselves (the first card, a node at random, merchants
// left at once, messages not waited for), for whole runs played by the autopilot.
bool rogue_automatic(void)
{
	return rogue_run && SDL_getenv("TYR3D_ROGUE_AUTO") != NULL;
}

static bool automatic(void)
{
	return rogue_automatic();
}

static void show_screen(void)
{
	service_SDL_events(true);  // input from before the screen showed is not for it
	JE_mouseStart();
	JE_showVGA();
	JE_mouseReplace();
}

// Waits for a key, a click or the mouse moving.
static void wait_for_input(bool *mouse_moved)
{
	*mouse_moved = false;
	do
	{
		SDL_Delay(16);
		const Sint32 x = mouse_x, y = mouse_y;
		push_joysticks_as_keyboard();
		service_SDL_events(false);
		*mouse_moved = mouse_x != x || mouse_y != y;
	} while (!(newkey || newmouse || *mouse_moved));
}

static bool inside(Sint32 px, Sint32 py, int x, int y, int w, int h)
{
	return px >= x && px < x + w && py >= y && py < y + h;
}

/* --- Screens ------------------------------------------------------------------------------- */

static void status_line(SDL_Surface *s, int y)
{
	char line[96];
	snprintf(line, sizeof(line), "Lives %d    Credits %lu    Cores +%d", 1 + run.lives, player[0].cash, run.cores);
	text(s, 160, y, line, small_font, centered, HUE_TEXT, 1);
}

// A pick of cards (count of them), or a merchant (prices, any number bought). False when skipped.
static bool card_screen(const char *heading, const char *subheading, int count, int boost, bool merchant)
{
	Card cards[5];
	count = SDL_clamp(count, 1, 5);
	for (int i = 0; i < count; ++i)
		cards[i] = deal_card(boost, cards, i);

	const int gap = merchant ? 4 : count > 3 ? 6 : 12;
	const int w = (300 - gap * (count - 1)) / count, h = merchant ? 128 : 124;
	const int x0 = (320 - (w * count + gap * (count - 1))) / 2, y0 = 38;
	int selected = 0;
	bool picked = false;

	backdrop(VGAScreen2);
	text(VGAScreen2, 160, 6, heading, normal_font, centered, HUE_TEXT, 4);
	mouseCursor = MOUSE_POINTER_NORMAL;
	bool first = true;
	for (; ; )
	{
		memcpy(VGAScreen->pixels, VGAScreen2->pixels, (size_t)VGAScreen->pitch * VGAScreen->h);
		text(VGAScreen, 160, 20, subheading, small_font, centered, HUE_TEXT, 0);
		if (merchant)
			status_line(VGAScreen, 28);
		for (int i = 0; i < count; ++i)
			draw_card(VGAScreen, &cards[i], x0 + i * (w + gap), y0, w, h, i == selected, merchant);
		text(VGAScreen, 160, 176, merchant ? "Enter: buy    Esc: leave" : "Enter: take the card    Esc: skip (+1000 credits)",
		     small_font, centered, HUE_TEXT, -2);
		show_screen();
		if (first)
		{
			fade_palette(colors, 10, 0, 255);
			first = false;
		}
		if (automatic())
		{
			SDL_Delay(300);
			if (!merchant)
				apply_card(&cards[0]);
			picked = !merchant;
			break;
		}

		bool mouse_moved;
		wait_for_input(&mouse_moved);
		bool action = false, leave = false;
		if (mouse_moved || newmouse)
			for (int i = 0; i < count; ++i)
				if (inside(mouse_x, mouse_y, x0 + i * (w + gap), y0, w, h))
				{
					if (selected != i)
						JE_playSampleNum(S_CURSOR);
					selected = i;
					if (newmouse && lastmouse_but == SDL_BUTTON_LEFT)
						action = true;
				}
		if (newmouse && lastmouse_but == SDL_BUTTON_RIGHT)
			leave = true;
		if (newkey)
		{
			switch (lastkey_scan)
			{
			case SDL_SCANCODE_LEFT:
				selected = (selected + count - 1) % count;
				JE_playSampleNum(S_CURSOR);
				break;
			case SDL_SCANCODE_RIGHT:
				selected = (selected + 1) % count;
				JE_playSampleNum(S_CURSOR);
				break;
			case SDL_SCANCODE_RETURN:
			case SDL_SCANCODE_SPACE:
				action = true;
				break;
			case SDL_SCANCODE_ESCAPE:
				leave = true;
				break;
			default:
				break;
			}
		}
		if (action)
		{
			Card *card = &cards[selected];
			if (!merchant)
			{
				JE_playSampleNum(S_SELECT);
				apply_card(card);
				picked = true;
				break;
			}
			if (!card->sold && card->price <= player[0].cash)
			{
				JE_playSampleNum(S_ITEM);
				player[0].cash -= card->price;
				apply_card(card);
				card->sold = true;
				picked = true;
			}
			else
				JE_playSampleNum(S_CLICK);
		}
		if (leave)
		{
			JE_playSampleNum(S_SPRING);
			if (!merchant)
				player[0].cash += 1000;
			break;
		}
	}
	fade_black(10);
	return picked;
}

// A planet as the shop's map draws it, in its own palette (18), its colours mapped to the nearest
// of the screen's (the shop's, which the items' icons need).
static void blit_planet(SDL_Surface *s, int x, int y, unsigned int index, int scale)
{
	static Uint8 remap[256];
	static bool made = false;
	if (!made)
	{
		const SDL_Color *from = palettes[17], *to = palettes[0];
		for (int i = 0; i < 256; ++i)
		{
			int best = 0, best_d = 1 << 30;
			for (int k = 1; k < 256; ++k)
			{
				const int dr = from[i].r - to[k].r, dg = from[i].g - to[k].g, db = from[i].b - to[k].b;
				const int d = 3 * dr * dr + 4 * dg * dg + 2 * db * db;
				if (d < best_d)
					best_d = d, best = k;
			}
			remap[i] = (Uint8)best;
		}
		made = true;
	}
	if (!sprite_exists(PLANET_SHAPES, index))
		return;
	const Sprite *sp = sprite(PLANET_SHAPES, index);
	const Uint8 *data = sp->data, *end = data + sp->size;
	int px = 0, py = 0;
	for (; data < end; ++data)
	{
		if (*data == 255)
			px += *++data;
		else if (*data == 254)
			px = sp->width;
		else if (*data == 253)
			++px;
		else
		{
			const int sx = x + px / scale, sy = y + py / scale;
			if (px % scale == 0 && py % scale == 0 && sx >= 0 && sx < s->w && sy >= 0 && sy < s->h)
				((Uint8 *)s->pixels)[sy * s->pitch + sx] = remap[*data];
			++px;
		}
		if (px >= sp->width)
			px -= sp->width, ++py;
	}
}

// The map runs left to right: a row of the act is a column of nodes.
static void node_position(int row, int col, int *x, int *y)
{
	const int left = 66, right = 286, top = 38, height = 124;
	*x = run.rows > 1 ? left + (right - left) * row / (run.rows - 1) : right;
	*y = top + (height * (2 * col + 1)) / (2 * run.width[row]);
}

#define START_X 22
#define START_Y 100

static const char *node_name(int row, int col)
{
	const Node *n = node_at(row, col);
	if (n->kind == NODE_MERCHANT)
		return "Merchant";
	const Act *a = &acts[run.act];
	return n->kind == NODE_BOSS ? a->bosses[n->level].name : a->levels[n->level].name;
}

static void draw_node(SDL_Surface *s, int row, int col, bool selected, bool can_go)
{
	const Node *n = node_at(row, col);
	int x, y;
	node_position(row, col, &x, &y);
	const bool visited = row < run.row || (row == run.row && col == run.col);
	const bool lit = selected || can_go || visited;
	const Sint8 value = selected ? 4 : can_go ? 1 : visited ? -1 : -4;
	// The selection's frame first, around the planet and its labels (a line through a text would
	// keep it from turning into the TrueType one).
	if (selected)
	{
		const int ph = n->kind == NODE_MERCHANT ? 14 : get_sprite_height(PLANET_SHAPES, n->planet) /
		               (n->kind != NODE_BOSS && get_sprite_width(PLANET_SHAPES, n->planet) > 30 ? 2 : 1);
		const int below = n->kind == NODE_MERCHANT ? 3 : n->kind == NODE_ELITE ? 18 : 11;
		JE_rectangle(s, x - 25, y - ph / 2 - 3, x + 25, y + ph / 2 + below, 255);
	}
	if (n->kind == NODE_MERCHANT)
	{
		panel(s, x - 14, y - 7, 28, 14, (Uint8)(HUE_GOLD * 16 + (lit ? 12 : 5)));
		text(s, x, y - 3, "Shop", small_font, centered, HUE_GOLD, value);
	}
	else
	{
		// Planets wider than a node's place at half size (a boss's as it is).
		const unsigned int planet = n->planet;
		const int scale = n->kind != NODE_BOSS && get_sprite_width(PLANET_SHAPES, planet) > 30 ? 2 : 1;
		const int pw = get_sprite_width(PLANET_SHAPES, planet) / scale, ph = get_sprite_height(PLANET_SHAPES, planet) / scale;
		blit_planet(s, x - pw / 2, y - ph / 2, planet, scale);
		if (!lit)
			for (int i = 0; i < 2; ++i)
				JE_barShade(s, x - pw / 2, y - ph / 2, x + pw / 2, y + ph / 2);
		// The kind: the name's colour (elite orange, boss red).
		const Uint8 hue = n->kind == NODE_BOSS ? HUE_RED : n->kind == NODE_ELITE ? HUE_GOLD : HUE_TEXT;
		const char *label = n->kind == NODE_ELITE ? "Elite" : n->kind == NODE_BOSS ? "Boss" : NULL;
		text(s, x, y + ph / 2 + 2, node_name(row, col), small_font, centered, hue, value);
		if (label != NULL && n->kind == NODE_BOSS)
			text(s, x, y - ph / 2 - 9, label, small_font, centered, hue, value);
		else if (label != NULL)
			text(s, x, y + ph / 2 + 9, label, small_font, centered, hue, (Sint8)(value - 2));
	}
}

// The map: the next node picked (run.row, run.col move there). False when the run is abandoned.
static bool map_screen(void)
{
	const int next_row = run.row + 1;
	int choices[MAX_COLS], count = 0;
	for (int c = 0; c < run.width[next_row]; ++c)
		if (reachable(next_row, c))
			choices[count++] = c;
	int selected = 0;

	backdrop(VGAScreen2);
	text(VGAScreen2, 160, 4, acts[run.act].name, normal_font, centered, HUE_TEXT, 4);
	// The paths.
	for (int r = 0; r + 1 < run.rows; ++r)
		for (int c = 0; c < run.width[r]; ++c)
			for (int k = 0; k < run.width[r + 1]; ++k)
				if ((node_at(r, c)->next >> k) & 1)
				{
					int x0, y0, x1, y1;
					node_position(r, c, &x0, &y0);
					node_position(r + 1, k, &x1, &y1);
					line(VGAScreen2, x0 + 14, y0, x1 - 14, y1, (Uint8)(HUE_TEXT * 16 + (r < run.row ? 10 : 6)), r >= run.row);
				}
	if (run.row < 0)
	{
		// The start: lines to the first row.
		for (int c = 0; c < run.width[0]; ++c)
		{
			int x, y;
			node_position(0, c, &x, &y);
			line(VGAScreen2, START_X + 14, START_Y, x - 14, y, (Uint8)(HUE_TEXT * 16 + 6), true);
		}
	}
	mouseCursor = MOUSE_POINTER_NORMAL;
	bool first = true;
	for (; ; )
	{
		memcpy(VGAScreen->pixels, VGAScreen2->pixels, (size_t)VGAScreen->pitch * VGAScreen->h);
		status_line(VGAScreen, 16);
		for (int r = 0; r < run.rows; ++r)
			for (int c = 0; c < run.width[r]; ++c)
			{
				bool can_go = false, is_selected = false;
				for (int i = 0; i < count; ++i)
					if (r == next_row && choices[i] == c)
						can_go = true, is_selected = i == selected;
				draw_node(VGAScreen, r, c, is_selected, can_go);
			}
		// The ship where it is.
		{
			int x = START_X, y = START_Y;
			if (run.row >= 0)
				node_position(run.row, run.col, &x, &y);
			JE_drawItem(1, player[0].items.ship, (JE_word)(x - 12), (JE_word)(y - 14));
		}
		const Node *n = node_at(next_row, choices[selected]);
		char info[96];
		static const char *const what[] = { "a level", "an elite level: harder, better cards and a bounty",
		                                     "a merchant: cards for credits", "the boss: the act's end" };
		snprintf(info, sizeof(info), "%s: %s", node_name(next_row, choices[selected]), what[n->kind]);
		text(VGAScreen, 160, 176, info, small_font, centered, HUE_GOLD, 4);
		text(VGAScreen, 160, 188, "Up/Down: choose    Enter: go    Esc: abandon the run", small_font, centered, HUE_TEXT, 0);
		show_screen();
		if (first)
		{
			fade_palette(colors, 10, 0, 255);
			first = false;
		}
		if (automatic())
		{
			SDL_Delay(300);
			run.row = next_row;
			run.col = choices[rnd_below(count)];
			fade_black(10);
			return true;
		}

		bool mouse_moved;
		wait_for_input(&mouse_moved);
		bool action = false;
		if (mouse_moved || newmouse)
			for (int i = 0; i < count; ++i)
			{
				int x, y;
				node_position(next_row, choices[i], &x, &y);
				if (inside(mouse_x, mouse_y, x - 22, y - 18, 44, 36))
				{
					if (selected != i)
						JE_playSampleNum(S_CURSOR);
					selected = i;
					if (newmouse && lastmouse_but == SDL_BUTTON_LEFT)
						action = true;
				}
			}
		if (newkey)
		{
			switch (lastkey_scan)
			{
			case SDL_SCANCODE_UP:
			case SDL_SCANCODE_LEFT:
				selected = (selected + count - 1) % count;
				JE_playSampleNum(S_CURSOR);
				break;
			case SDL_SCANCODE_DOWN:
			case SDL_SCANCODE_RIGHT:
				selected = (selected + 1) % count;
				JE_playSampleNum(S_CURSOR);
				break;
			case SDL_SCANCODE_RETURN:
			case SDL_SCANCODE_SPACE:
				action = true;
				break;
			case SDL_SCANCODE_ESCAPE:
				JE_playSampleNum(S_SPRING);
				if (JE_quitRequest())
				{
					fade_black(10);
					return false;
				}
				break;
			default:
				break;
			}
		}
		if (action)
		{
			JE_playSampleNum(S_SELECT);
			run.row = next_row;
			run.col = choices[selected];
			fade_black(10);
			return true;
		}
	}
}

// A message screen until a key: the title and lines.
static void message_screen(const char *title, const char *const *lines, int line_count)
{
	backdrop(VGAScreen);
	text(VGAScreen, 160, 40, title, large_font, centered, HUE_TEXT, 4);
	for (int i = 0; i < line_count; ++i)
		text(VGAScreen, 160, 80 + 12 * i, lines[i], normal_font, centered, HUE_TEXT, 1);
	text(VGAScreen, 160, 180, "Press a key", small_font, centered, HUE_TEXT, -3);
	JE_showVGA();
	fade_palette(colors, 10, 0, 255);
	if (automatic())
		SDL_Delay(300);
	else
	{
		wait_noinput(true, true, true);
		wait_input(true, true, true);
	}
	fade_black(10);
}

/* --- The run's flow ------------------------------------------------------------------------ */

// Sets up the level of the node the ship is at, for start_level_first.
static void set_up_level(void)
{
	const Node *n = node_at(run.row, run.col);
	const Act *a = &acts[run.act];
	run.kind = n->kind;
	run.level = n->kind == NODE_BOSS ? &a->bosses[n->level] : &a->levels[n->level];
	if (run.level->episode != episodeNum)
		JE_initEpisode(run.level->episode);
	mainLevel = run.level->section;
	difficultyLevel = (JE_shortint)SDL_clamp(a->difficulty + (n->kind == NODE_ELITE ? 1 : 0), DIFFICULTY_EASY, DIFFICULTY_ZINGLON);
	initialDifficulty = difficultyLevel;
	oldDifficultyLevel = difficultyLevel;
	run.at_start = player[0];
	printf("rogue: act %d row %d: %s (episode %d section %d, difficulty %d)\n", run.act + 1, run.row + 1,
	       run.level->name, run.level->episode, run.level->section, difficultyLevel);
}

// Moves on the map until a level is picked (merchants on the way), set up. False when the run is
// abandoned.
static bool next_level(void)
{
	play_song(DEFAULT_SONG_BUY);
	for (; ; )
	{
		if (!map_screen())
			return false;
		if (node_at(run.row, run.col)->kind != NODE_MERCHANT)
			break;
		card_screen("Merchant", "Cards for credits", 5, 1, true);
	}
	set_up_level();
	return true;
}

static void run_over(bool won, const char *why)
{
	if (won)
		run.cores += 3;
	profile.cores += run.cores;
	profile.runs += 1;
	profile.wins += won ? 1 : 0;
	profile.best_act = SDL_max(profile.best_act, run.act + (won ? 1 : 0));
	save_profile();

	char lines[4][64];
	snprintf(lines[0], sizeof(lines[0]), "%s", why);
	snprintf(lines[1], sizeof(lines[1]), "Levels cleared %d, bosses %d", run.levels, run.bosses);
	snprintf(lines[2], sizeof(lines[2]), "Cores earned %d (now %d)", run.cores, profile.cores);
	snprintf(lines[3], sizeof(lines[3]), "Cores buy unlocks in the Rogue Run menu");
	const char *const texts[4] = { lines[0], lines[1], lines[2], lines[3] };
	fade_song();
	message_screen(won ? "Victory" : "Run Over", texts, 4);
	rogue_run = false;
	printf("rogue: run over (%s), %d levels, %d cores\n", won ? "won" : why, run.levels, run.cores);
}

static void start_run(Uint32 seed)
{
	load_profile();
	memset(&run, 0, sizeof(run));
	run.rng = seed != 0 ? seed : 0x9e3779b9u;
	for (int i = 0; i < 8; ++i)
		rnd();

	// A full game's start (JE_initPlayerData has set the ship up), without its shops; the item
	// data of the first act's episode (the cards and the map draw items).
	JE_initEpisode(acts[0].levels[0].episode);
	initial_episode_num = episodeNum;
	onePlayerAction = false;
	twoPlayerMode = false;
	timedBattleMode = false;
	superTyrian = false;
	galagaMode = false;
	richMode = false;
	constantPlay = false;
	if (SDL_getenv("TYR3D_ROGUE_UNLOCKS") != NULL && strcmp(SDL_getenv("TYR3D_ROGUE_UNLOCKS"), "all") == 0)
		profile.unlocked = (1u << unlock_count) - 1;  // for tests
	player[0].cash = unlocked("capital") ? 15000 : 10000;
	run.lives = unlocked("hull") ? 1 : 0;
	if (unlocked("warmup"))
		player[0].items.weapon[FRONT_WEAPON].power = 2;

	rogue_run = true;
	run.act = 0;
	make_map();
	gameLoaded = true;
	printf("rogue: run with seed %u\n", seed);
}

bool rogue_level_over(void)
{
	if (playerEndLevel)
	{
		run_over(false, "Run abandoned");
		return false;
	}
	if (all_players_dead())
	{
		fade_song();
		fade_black(10);
		if (run.lives <= 0)
		{
			run_over(false, "Destroyed");
			return false;
		}
		// A spare hull: the level again, as it began.
		--run.lives;
		player[0] = run.at_start;
		char line[64];
		snprintf(line, sizeof(line), "Extra lives left: %d", run.lives);
		const char *const lines[2] = { "The spare hull takes over", line };
		message_screen("Ship Lost", lines, 2);
		set_up_level();
		return true;
	}

	// Cleared.
	JE_endLevelAni();
	fade_song();
	run.levels += 1;
	run.cores += 1;
	char subheading[64];
	snprintf(subheading, sizeof(subheading), "%s cleared", run.level->name);
	const int cards = unlocked("fourth") ? 4 : 3;
	if (run.kind == NODE_BOSS)
	{
		run.bosses += 1;
		run.cores += 2;
		card_screen("Boss Defeated", subheading, cards, 2, false);
		if (run.act + 1 >= act_count)
		{
			run_over(true, "All acts cleared");
			return false;
		}
		run.act += 1;
		make_map();
		char line[64];
		snprintf(line, sizeof(line), "Difficulty rises: the levels are harder");
		const char *const lines[1] = { line };
		message_screen(acts[run.act].name, lines, 1);
	}
	else if (run.kind == NODE_ELITE)
	{
		const Uint32 bounty = 3000u * (Uint32)(run.act + 1);
		player[0].cash += bounty;
		char heading[64];
		snprintf(heading, sizeof(heading), "Elite Bounty +%lu", (unsigned long)bounty);
		card_screen(heading, subheading, cards, 1, false);
	}
	else
		card_screen("Choose a Card", subheading, cards, 0, false);

	return next_level();
}

/* --- The rogue screen ---------------------------------------------------------------------- */

static void unlocks_screen(void)
{
	int selected = 0;
	bool first = true;
	for (; ; )
	{
		backdrop(VGAScreen);
		text(VGAScreen, 160, 6, "Unlocks", normal_font, centered, HUE_TEXT, 4);
		char line[96];
		snprintf(line, sizeof(line), "Cores %d", profile.cores);
		text(VGAScreen, 160, 20, line, small_font, centered, HUE_GOLD, 3);
		for (int i = 0; i < unlock_count; ++i)
		{
			const bool owned = (profile.unlocked >> i) & 1;
			const int y = 36 + 14 * i;
			if (i == selected)
				panel(VGAScreen, 30, y - 2, 260, 13, 255);
			text(VGAScreen, 40, y, unlocks[i].title, normal_font, left_aligned, HUE_TEXT, i == selected ? 4 : owned ? -2 : 1);
			snprintf(line, sizeof(line), owned ? "Owned" : "%d cores", unlocks[i].cost);
			text(VGAScreen, 280, y + 2, line, small_font, right_aligned, owned ? HUE_TEXT : HUE_GOLD,
			     owned ? -3 : unlocks[i].cost <= profile.cores ? 3 : -2);
		}
		if (unlock_count > 0)
			text(VGAScreen, 160, 166, unlocks[selected].text, small_font, centered, HUE_TEXT, 2);
		text(VGAScreen, 160, 186, "Enter: unlock    Esc: back", small_font, centered, HUE_TEXT, -3);
		show_screen();
		if (first)
		{
			fade_palette(colors, 10, 0, 255);
			first = false;
		}
		bool mouse_moved;
		wait_for_input(&mouse_moved);
		bool action = false;
		if (mouse_moved || newmouse)
			for (int i = 0; i < unlock_count; ++i)
				if (inside(mouse_x, mouse_y, 30, 34 + 14 * i, 260, 13))
				{
					selected = i;
					if (newmouse && lastmouse_but == SDL_BUTTON_LEFT)
						action = true;
				}
		if (newmouse && lastmouse_but == SDL_BUTTON_RIGHT)
			break;
		if (newkey)
		{
			if (lastkey_scan == SDL_SCANCODE_UP && unlock_count > 0)
				selected = (selected + unlock_count - 1) % unlock_count, JE_playSampleNum(S_CURSOR);
			else if (lastkey_scan == SDL_SCANCODE_DOWN && unlock_count > 0)
				selected = (selected + 1) % unlock_count, JE_playSampleNum(S_CURSOR);
			else if (lastkey_scan == SDL_SCANCODE_RETURN || lastkey_scan == SDL_SCANCODE_SPACE)
				action = true;
			else if (lastkey_scan == SDL_SCANCODE_ESCAPE)
				break;
		}
		if (action && unlock_count > 0)
		{
			if (!((profile.unlocked >> selected) & 1) && unlocks[selected].cost <= profile.cores)
			{
				profile.cores -= unlocks[selected].cost;
				profile.unlocked |= 1u << selected;
				save_profile();
				JE_playSampleNum(S_ITEM);
			}
			else
				JE_playSampleNum(S_CLICK);
		}
	}
	JE_playSampleNum(S_SPRING);
	fade_black(10);
}

bool rogue_menu(void)
{
	if (!load_data())
		return false;
	load_profile();
	if (shopSpriteSheet.data == NULL)
		JE_loadCompShapes(&shopSpriteSheet, '1');

	static const char *const items[] = { "Start Run", "Unlocks", "Back" };
	int selected = 0;
	bool first = true;
	for (; ; )
	{
		backdrop(VGAScreen);
		text(VGAScreen, 160, 20, "Rogue Run", large_font, centered, HUE_TEXT, 4);
		char line[96];
		snprintf(line, sizeof(line), "Cores %d    Runs %d    Wins %d    Best act %d", profile.cores, profile.runs, profile.wins,
		         profile.best_act);
		text(VGAScreen, 160, 46, line, small_font, centered, HUE_GOLD, 2);
		text(VGAScreen, 160, 60, "Three acts, a map with branches, a card after every level.", small_font, centered, HUE_TEXT, 0);
		text(VGAScreen, 160, 69, "One life: dying ends the run. Cores buy unlocks.", small_font, centered, HUE_TEXT, 0);
		for (int i = 0; i < 3; ++i)
			text(VGAScreen, 160, 100 + 20 * i, items[i], normal_font, centered, HUE_TEXT, i == selected ? 4 : -2);
		show_screen();
		if (first)
		{
			fade_palette(colors, 10, 0, 255);
			first = false;
		}
		bool mouse_moved;
		wait_for_input(&mouse_moved);
		bool action = false;
		if (mouse_moved || newmouse)
			for (int i = 0; i < 3; ++i)
				if (inside(mouse_x, mouse_y, 100, 98 + 20 * i, 120, 16))
				{
					selected = i;
					if (newmouse && lastmouse_but == SDL_BUTTON_LEFT)
						action = true;
				}
		if (newmouse && lastmouse_but == SDL_BUTTON_RIGHT)
			selected = 2, action = true;
		if (newkey)
		{
			if (lastkey_scan == SDL_SCANCODE_UP)
				selected = (selected + 2) % 3, JE_playSampleNum(S_CURSOR);
			else if (lastkey_scan == SDL_SCANCODE_DOWN)
				selected = (selected + 1) % 3, JE_playSampleNum(S_CURSOR);
			else if (lastkey_scan == SDL_SCANCODE_RETURN || lastkey_scan == SDL_SCANCODE_SPACE)
				action = true;
			else if (lastkey_scan == SDL_SCANCODE_ESCAPE)
				selected = 2, action = true;
		}
		if (!action)
			continue;
		JE_playSampleNum(selected == 2 ? S_SPRING : S_SELECT);
		fade_black(10);
		if (selected == 0)
		{
			start_run((Uint32)SDL_GetTicksNS() | 1u);
			if (next_level())
				return true;
			run_over(false, "Run abandoned");
			return false;
		}
		if (selected == 1)
		{
			unlocks_screen();
			first = true;
			continue;
		}
		return false;
	}
}

bool rogue_from_environment(void)
{
	static bool done = false;
	const char *seed = SDL_getenv("TYR3D_ROGUE");
	if (done || seed == NULL)
		return false;
	done = true;
	if (strcmp(seed, "menu") == 0)
		return rogue_menu();
	if (!load_data())
		return false;
	if (shopSpriteSheet.data == NULL)
		JE_loadCompShapes(&shopSpriteSheet, '1');
	start_run((Uint32)strtoul(seed, NULL, 10));
	if (next_level())
		return true;
	rogue_run = false;
	return false;
}
