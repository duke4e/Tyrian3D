/*
 * Tyrian3D: new content from assets/content/items.cfg. See content.h.
 */
#include "content.h"

#include "episodes.h"
#include "lvlmast.h"
#include "paths3d.h"

#include <SDL3/SDL.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_TOKENS 48

static const char *content_file = "items.cfg";
static int line_number = 0;

#define WARN(...) (fprintf(stderr, "warning: content %s:%d: ", content_file, line_number), fprintf(stderr, __VA_ARGS__), \
                   fputc('\n', stderr))

// Splits a line into tokens: words, key=value pairs, "quoted text" (quotes taken off, in values too).
static int tokenize(char *line, char *tokens[MAX_TOKENS])
{
	int count = 0;
	char *p = line;
	while (*p != '\0' && count < MAX_TOKENS)
	{
		while (*p == ' ' || *p == '\t' || *p == '\r' || *p == '\n')
			++p;
		if (*p == '\0' || *p == '#')
			break;
		tokens[count++] = p;
		bool quoted = false;
		char *out = p;
		for (; *p != '\0'; ++p)
		{
			if (*p == '"')
			{
				quoted = !quoted;
				continue;
			}
			if (!quoted && (*p == ' ' || *p == '\t' || *p == '\r' || *p == '\n' || *p == '#'))
				break;
			*out++ = *p;
		}
		const bool comment = *p == '#';
		if (*p != '\0')
			++p;
		*out = '\0';
		if (comment)
			break;
	}
	return count;
}

// Up to max numbers separated by commas; the count read.
static int numbers(const char *value, long *out, int max)
{
	int n = 0;
	const char *p = value;
	while (*p != '\0' && n < max)
	{
		char *end;
		out[n++] = strtol(p, &end, 10);
		if (end == p)
			return n - 1;
		p = *end == ',' ? end + 1 : end;
		if (*end != ',')
			break;
	}
	return n;
}

static bool number(const char *value, long *out)
{
	return numbers(value, out, 1) == 1;
}

static void set_name(char *name, const char *value)
{
	SDL_strlcpy(name, value, 31);
}

static void weapon_line(char **tokens, int count)
{
	const long id = atol(tokens[1]);
	if (id < CONTENT_WEAPON_FIRST || id > CONTENT_WEAPON_LAST)
	{
		WARN("weapon %ld: new weapons go in %d-%d", id, CONTENT_WEAPON_FIRST, CONTENT_WEAPON_LAST);
		return;
	}
	JE_WeaponType *w = &weapons[id];
	memset(w, 0, sizeof(*w));
	for (int i = 2; i < count; ++i)
	{
		char *eq = strchr(tokens[i], '=');
		if (eq == NULL)
		{
			WARN("'%s' is not key=value", tokens[i]);
			continue;
		}
		*eq = '\0';
		const char *key = tokens[i], *value = eq + 1;
		long v, list[8];
		const int n = numbers(value, list, 8);
		if (strcmp(key, "copy") == 0 && number(value, &v) && v >= 0 && v <= WEAP_NUM)
			*w = weapons[v];
#define SCALAR(field) else if (strcmp(key, #field) == 0 && n == 1) w->field = list[0];
		SCALAR(drain) SCALAR(shotrepeat) SCALAR(multi) SCALAR(weapani) SCALAR(max) SCALAR(tx) SCALAR(ty) SCALAR(aim)
		SCALAR(acceleration) SCALAR(accelerationx) SCALAR(circlesize) SCALAR(sound) SCALAR(trail) SCALAR(shipblastfilter)
#undef SCALAR
#define ARRAY(field) else if (strcmp(key, #field) == 0 && n >= 1) for (int k = 0; k < 8; ++k) w->field[k] = list[SDL_min(k, n - 1)];
		ARRAY(attack) ARRAY(del) ARRAY(sx) ARRAY(sy) ARRAY(bx) ARRAY(by) ARRAY(sg)
#undef ARRAY
		else
			WARN("weapon: unknown or bad '%s=%s'", key, value);
	}
}

static void port_line(char **tokens, int count)
{
	const long id = atol(tokens[1]);
	if (id < CONTENT_PORT_FIRST || id > PORT_NUM)
	{
		WARN("port %ld: new ports go in %d-%d", id, CONTENT_PORT_FIRST, PORT_NUM);
		return;
	}
	for (int i = 2; i < count; ++i)
	{
		char *eq = strchr(tokens[i], '=');
		if (eq == NULL)
			continue;
		*eq = '\0';
		const char *key = tokens[i], *value = eq + 1;
		long v, list[11];
		const int n = numbers(value, list, 11);
		if (strcmp(key, "copy") == 0 && number(value, &v) && v >= 0 && v <= PORT_NUM)
			weaponPort[id] = weaponPort[v];
		else if (strcmp(key, "name") == 0)
			set_name(weaponPort[id].name, value);
		else if ((strcmp(key, "op1") == 0 || strcmp(key, "op2") == 0) && n >= 1)
			for (int k = 0; k < 11; ++k)
				weaponPort[id].op[key[2] - '1'][k] = (JE_word)list[SDL_min(k, n - 1)];
		else if (strcmp(key, "opnum") == 0 && n == 1)
			weaponPort[id].opnum = (JE_byte)SDL_clamp(list[0], 1, 2);
		else if (strcmp(key, "cost") == 0 && n == 1)
			weaponPort[id].cost = (JE_word)list[0];
		else if (strcmp(key, "graphic") == 0 && n == 1)
			weaponPort[id].itemgraphic = (JE_word)list[0];
		else if (strcmp(key, "poweruse") == 0 && n == 1)
			weaponPort[id].poweruse = (JE_word)list[0];
		else
			WARN("port: unknown or bad '%s=%s'", key, value);
	}
}

static void sidekick_line(char **tokens, int count)
{
	const long id = atol(tokens[1]);
	if (id < CONTENT_SIDEKICK_FIRST || id > OPTION_NUM)
	{
		WARN("sidekick %ld: new sidekicks go in %d-%d", id, CONTENT_SIDEKICK_FIRST, OPTION_NUM);
		return;
	}
	JE_OptionType *o = &options[id];
	for (int i = 2; i < count; ++i)
	{
		char *eq = strchr(tokens[i], '=');
		if (eq == NULL)
			continue;
		*eq = '\0';
		const char *key = tokens[i], *value = eq + 1;
		long v, list[20];
		const int n = numbers(value, list, 20);
		if (strcmp(key, "copy") == 0 && number(value, &v) && v >= 0 && v <= OPTION_NUM)
			*o = options[v];
		else if (strcmp(key, "name") == 0)
			set_name(o->name, value);
		else if (strcmp(key, "graphic") == 0 && n == 1)
			o->itemgraphic = (JE_word)list[0];
		else if (strcmp(key, "gr") == 0 && n >= 1)
			for (int k = 0; k < 20; ++k)
				o->gr[k] = (JE_word)(k < n ? list[k] : 0);
		else if (strcmp(key, "stop") == 0 && n == 1)
			o->stop = list[0] != 0;
#define FIELD(field) else if (strcmp(key, #field) == 0 && n == 1) o->field = list[0];
		FIELD(pwr) FIELD(cost) FIELD(tr) FIELD(option) FIELD(opspd) FIELD(ani) FIELD(wport) FIELD(wpnum) FIELD(ammo)
		FIELD(icongr)
#undef FIELD
		else
			WARN("sidekick: unknown or bad '%s=%s'", key, value);
	}
}

static void special_line(char **tokens, int count)
{
	const long id = atol(tokens[1]);
	if (id < CONTENT_SPECIAL_FIRST || id > SPECIAL_NUM)
	{
		WARN("special %ld: new specials go in %d-%d", id, CONTENT_SPECIAL_FIRST, SPECIAL_NUM);
		return;
	}
	for (int i = 2; i < count; ++i)
	{
		char *eq = strchr(tokens[i], '=');
		if (eq == NULL)
			continue;
		*eq = '\0';
		const char *key = tokens[i], *value = eq + 1;
		long v;
		if (strcmp(key, "copy") == 0 && number(value, &v) && v >= 0 && v <= SPECIAL_NUM)
			special[id] = special[v];
		else if (strcmp(key, "name") == 0)
			set_name(special[id].name, value);
		else if (strcmp(key, "graphic") == 0 && number(value, &v))
			special[id].itemgraphic = (JE_word)v;
		else if (strcmp(key, "pwr") == 0 && number(value, &v))
			special[id].pwr = (JE_byte)v;
		else if (strcmp(key, "stype") == 0 && number(value, &v))
			special[id].stype = (JE_byte)v;
		else if (strcmp(key, "wpn") == 0 && number(value, &v))
			special[id].wpn = (JE_word)v;
		else
			WARN("special: unknown or bad '%s=%s'", key, value);
	}
}

void content_apply(void)
{
	char dir[1024], path[1200];
	snprintf(path, sizeof(path), "%s/%s", tyr3d_resource_dir("TYR3D_CONTENT_DIR", TYR3D_CONTENT_DIR, "content", dir, sizeof(dir)),
	         content_file);
	FILE *f = fopen(path, "r");
	if (f == NULL)
		return;
	char line[2048];
	int weapon_count = 0, port_count = 0, sidekick_count = 0, special_count = 0;
	line_number = 0;
	while (fgets(line, sizeof(line), f) != NULL)
	{
		++line_number;
		char *tokens[MAX_TOKENS];
		const int count = tokenize(line, tokens);
		if (count < 2)
			continue;
		if (strcmp(tokens[0], "weapon") == 0)
			weapon_line(tokens, count), ++weapon_count;
		else if (strcmp(tokens[0], "port") == 0)
			port_line(tokens, count), ++port_count;
		else if (strcmp(tokens[0], "sidekick") == 0)
			sidekick_line(tokens, count), ++sidekick_count;
		else if (strcmp(tokens[0], "special") == 0)
			special_line(tokens, count), ++special_count;
		else
			WARN("unknown line '%s'", tokens[0]);
	}
	fclose(f);
	static bool told = false;
	if (!told)
		printf("content: %d weapons, %d ports, %d sidekicks, %d specials from %s\n", weapon_count, port_count,
		       sidekick_count, special_count, path);
	told = true;
}
