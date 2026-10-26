/*
 * Tyrian3D: the secrets found and the title menu's Secrets screen (secrets.h).
 */
#include "secrets.h"

#include "destruct.h"
#include "episodes.h"
#include "file.h"
#include "font.h"
#include "fonthand.h"
#include "helptext.h"
#include "joystick.h"
#include "keyboard.h"
#include "menus.h"
#include "mouse.h"
#include "nortsong.h"
#include "palette.h"
#include "picload.h"
#include "rogue.h"
#include "sndmast.h"
#include "sprite.h"
#include "ui.h"
#include "varz.h"
#include "vga256d.h"
#include "video.h"

#include <stdio.h>
#include <string.h>

#define SECRETS_FILE "tyrian3d_secrets.cfg"

/* --- What there is to find ---------------------------------------------------------------- */

enum { TAB_LEVELS, TAB_CODES, TAB_CUBES, TAB_OTHER, TABS };
static const char *const tab_names[TABS] = { "Levels", "Codes", "Data Cubes", "Other" };

// The levels only a warp orb or a hidden condition leads to (the episodes' scripts: the section of their
// level line, as tools/levels.py names them), and where to look.
static const struct
{
	int episode, section;
	const char *name;
	const char *hint;
} secret_levels[] = {
	{ 1, 16, "BUBBLES", "A warp orb in TYRIAN." },
	{ 1, 28, "HOLES", "Another warp orb in TYRIAN." },
	{ 1, 31, "SOH JIN", "One more warp orb in TYRIAN." },
	{ 1, 21, "ASTEROID?", "A warp orb in ASTEROID1, or in MINEMAZE." },
	{ 1, 23, "MINEMAZE", "A warp orb in ASTEROID2." },
	{ 1, 33, "WINDY", "A warp orb in ASTEROID?." },
	{ 1, 41, "** ALE **", "On your own, after ASSASSIN: the map offers it instead of the end." },
	{ 2, 15, "GEM WAR", "A warp orb in GYGES." },
	{ 2, 17, "MARKERS", "It follows GEM WAR." },
	{ 2, 19, "MISTAKES", "It follows MARKERS, or a warp orb in ASTCITY." },
	{ 3, 15, "AST. CITY", "A warp orb in STARGATE." },
	{ 3, 19, "SAWBLADES", "Another warp orb in STARGATE." },
	{ 3, 17, "TYRIAN X", "Hard or harder: the episode goes on after FLEET." },
	{ 3, 21, "SAVARA Y", "Hard or harder, after TYRIAN X." },
	{ 3, 23, "New Deli", "Hard or harder, after SAVARA Y." },
	{ 4, 27, "WINDY", "A warp orb on the SURFACE." },
	{ 4, 29, "DESERTRUN", "A warp orb in LAVA EXIT." },
	{ 4, 50, "ICESECRET", "A warp orb in ICE EXIT." },
	{ 4, 36, "SIDE EXIT", "Beat CORE's boss before its time runs out." },
	{ 4, 8, "?TUNNEL?", "It follows SIDE EXIT." },
	{ 4, 40, "TIME WAR", "After NOSE DRIP, flying the Stalker 21.126." },
	{ 4, 45, "SQUADRON", "After NOSE DRIP: the map offers it beside the end." },
	{ 6, 7, "VAULT", "A courier crossing GREY MOON carries a warp orb." },
};

// The others: the hidden difficulties, the shop that sells the Stalker.
static const struct
{
	const char *id;
	const char *name;
	const char *what;
	const char *hint;
} secret_others[] = {
	{ "difficulty 4", "Impossible", "A difficulty", "Hold Shift and a key on the difficulty menu (the one after F)." },
	{ "difficulty 5", "Suicide", "A difficulty", "Once Impossible shows, Shift and a bracket on the difficulty menu." },
	{ "difficulty 6", "Lord of Game", "A difficulty", "Once Suicide shows, spell out a lord on the difficulty menu." },
	{ "shop 4 33", "The Stalker 21.126", "A ship for sale (episode 4)", "Beat ?TUNNEL?'s boss: the shop after it." },
};

/* --- The record ---------------------------------------------------------------------------- */

#define FOUND_MAX 1024
static char found_ids[FOUND_MAX][24];
static int found_count = 0;
static bool loaded = false;

static void load(void)
{
	if (loaded)
		return;
	loaded = true;
	FILE *f = dir_fopen_warn(get_user_directory(), SECRETS_FILE, "r");
	if (f == NULL)
		return;
	char line[128];
	while (fgets(line, sizeof(line), f) != NULL && found_count < FOUND_MAX)
	{
		line[strcspn(line, "\r\n")] = '\0';
		if (strncmp(line, "found ", 6) == 0 && line[6] != '\0')
			SDL_strlcpy(found_ids[found_count++], line + 6, sizeof(found_ids[0]));
	}
	fclose(f);
}

static bool is_found(const char *id)
{
	load();
	for (int i = 0; i < found_count; ++i)
		if (strcmp(found_ids[i], id) == 0)
			return true;
	return false;
}

// Whether what the game reveals now counts: not in a demo, a rogue run, a custom episode or a dev run.
static bool recording(void)
{
	const char *forced = SDL_getenv("TYR3D_SECRETS");
	if (forced != NULL)
		return SDL_atoi(forced) != 0;
	static const char *const dev[] = { "TYR3D_START", "TYR3D_TEST_KEYS", "TYR3D_AUTOPILOT", "TYR3D_ROGUE", "TYR3D_MODE",
	                                   "TYR3D_DUMP_DIR", "TYR3D_EXIT_AFTER" };
	for (size_t i = 0; i < COUNTOF(dev); ++i)
		if (SDL_getenv(dev[i]) != NULL)
			return false;
	return !play_demo && !rogue_run && custom_episode == 0;
}

static void found(const char *id)
{
	if (!recording() || is_found(id) || found_count >= FOUND_MAX)
		return;
	SDL_strlcpy(found_ids[found_count++], id, sizeof(found_ids[0]));
	FILE *f = dir_fopen_warn(get_user_directory(), SECRETS_FILE, "w");
	if (f == NULL)
		return;
	fprintf(f, "# Tyrian3D: the secrets found (the title menu's Secrets; src/secrets.c)\n");
	for (int i = 0; i < found_count; ++i)
		fprintf(f, "found %s\n", found_ids[i]);
	fclose(f);
}

void secrets_level(int episode, int section)
{
	for (size_t i = 0; i < COUNTOF(secret_levels); ++i)
		if (secret_levels[i].episode == episode && secret_levels[i].section == section)
		{
			char id[24];
			snprintf(id, sizeof(id), "level %d %d", episode, section);
			found(id);
		}
}

void secrets_shop(int episode, int section)
{
	char id[24];
	snprintf(id, sizeof(id), "shop %d %d", episode, section);
	for (size_t i = 0; i < COUNTOF(secret_others); ++i)
		if (strcmp(secret_others[i].id, id) == 0)
			found(id);
}

void secrets_code(int code)
{
	char id[24];
	snprintf(id, sizeof(id), "code %d", code);
	found(id);
}

void secrets_difficulty(int shown)
{
	for (int n = 4; n <= SDL_min(shown, 6); ++n)
	{
		char id[24];
		snprintf(id, sizeof(id), "difficulty %d", n);
		found(id);
	}
}

void secrets_cubes(int episode, const JE_word *cubes, int count)
{
	for (int i = 0; i < count; ++i)
	{
		char id[24];
		snprintf(id, sizeof(id), "cube %d %d", episode, (int)cubes[i]);
		found(id);
	}
}

// How many data cubes an episode's cubetxt file holds (each starts with a "*" line: load_cube; a "*" that ends
// the file starts none), or 0.
static int cubes_in_episode(int episode)
{
	static int counted[EPISODE_MAX + 1];
	static bool done[EPISODE_MAX + 1];
	if (episode < 1 || episode > EPISODE_MAX)
		return 0;
	if (done[episode])
		return counted[episode];
	done[episode] = true;
	char name[16];
	snprintf(name, sizeof(name), "cubetxt%d.dat", episode);
	FILE *f = dir_fopen_warn(data_dir(), name, "rb");
	if (f == NULL)
		return 0;
	fseek(f, 0, SEEK_END);
	const long size = ftell(f);
	fseek(f, 0, SEEK_SET);
	char buf[256];
	bool star = false;
	while (ftell(f) < size)
	{
		read_encrypted_pascal_string(buf, sizeof(buf), f);
		star = buf[0] == '*';
		counted[episode] += star;
	}
	counted[episode] -= star;
	fclose(f);
	return counted[episode];
}

static int cubes_found(int episode)
{
	load();
	char prefix[16];
	const int n = snprintf(prefix, sizeof(prefix), "cube %d ", episode);
	int count = 0;
	for (int i = 0; i < found_count; ++i)
		count += strncmp(found_ids[i], prefix, (size_t)n) == 0;
	return count;
}

/* --- The screen ---------------------------------------------------------------------------- */

typedef struct
{
	char label[48];  // its name, or "???" while locked
	char what[64];   // what or where it is
	char hint[112];  // how it was found, or where to look
	bool found;
	char count[16];  // a share found ("12 / 26": data cubes), or ""
} Row;

#define ROWS_MAX 32

// A game text without its colour marks (~).
static void plain(char *out, const char *in, size_t size)
{
	size_t n = 0;
	for (; *in != '\0' && n + 1 < size; ++in)
		if (*in != '~')
			out[n++] = *in;
	out[n] = '\0';
	while (n > 0 && out[n - 1] == ' ')
		out[--n] = '\0';
}

static int rows_for(int tab, Row *rows)
{
	int n = 0;
	switch (tab)
	{
	case TAB_LEVELS:
		for (size_t i = 0; i < COUNTOF(secret_levels) && n < ROWS_MAX; ++i)
		{
			Row *r = &rows[n++];
			memset(r, 0, sizeof(*r));
			char id[24];
			snprintf(id, sizeof(id), "level %d %d", secret_levels[i].episode, secret_levels[i].section);
			r->found = is_found(id);
			SDL_strlcpy(r->label, r->found ? secret_levels[i].name : "???", sizeof(r->label));
			snprintf(r->what, sizeof(r->what), "Episode %d", secret_levels[i].episode);
			SDL_strlcpy(r->hint, secret_levels[i].hint, sizeof(r->hint));
		}
		break;
	case TAB_CODES:
		for (int i = 0; i < HELPTEXT_SPECIALNAME_COUNT && n < ROWS_MAX; ++i)
		{
			Row *r = &rows[n++];
			memset(r, 0, sizeof(*r));
			char id[24];
			snprintf(id, sizeof(id), "code %d", i);
			r->found = is_found(id) || (i + 1 == SA_DESTRUCT && destruct_discovered());
			if (r->found)
				SDL_strlcpy(r->label, specialName[i], sizeof(r->label));
			else
			{
				// (As many marks as it has letters.)
				const size_t len = SDL_min(strlen(specialName[i]), sizeof(r->label) - 1);
				memset(r->label, '?', len);
				r->label[len] = '\0';
			}
			if (i + 1 == SA_DESTRUCT)
			{
				SDL_strlcpy(r->what, "Destruct, the artillery duel", sizeof(r->what));
				SDL_strlcpy(r->hint, "Type it at the title. The last Super Arcade ship's end tells it.", sizeof(r->hint));
			}
			else if (i + 1 == SA_ENGAGE)
			{
				SDL_strlcpy(r->what, "Super Tyrian", sizeof(r->what));
				SDL_strlcpy(r->hint, "Type it at the title. Episode 4's special endings hand out its kit.", sizeof(r->hint));
			}
			else
			{
				char ship[32];
				plain(ship, superShips[i + 1], sizeof(ship));
				snprintf(r->what, sizeof(r->what), "Super Arcade: %s", r->found ? ship : "a ship");
				SDL_strlcpy(r->hint, "Type it at the title. Finishing the game tells the next code.", sizeof(r->hint));
			}
		}
		break;
	case TAB_CUBES:
		for (int e = 1; e <= EPISODE_MAX && n < ROWS_MAX; ++e)
		{
			const int total = cubes_in_episode(e);
			if (total == 0)
				continue;
			const int got = SDL_min(cubes_found(e), total);
			Row *r = &rows[n++];
			memset(r, 0, sizeof(*r));
			plain(r->label, episode_name[e], sizeof(r->label));
			snprintf(r->what, sizeof(r->what), "Episode %d", e);
			snprintf(r->count, sizeof(r->count), "%d / %d", got, total);
			r->found = got >= total;
			SDL_strlcpy(r->hint, got >= total ? "Every data cube read." :
			                     "Shot-down couriers and hidden ships drop them; the shops' Data list keeps them.", sizeof(r->hint));
		}
		break;
	case TAB_OTHER:
		for (size_t i = 0; i < COUNTOF(secret_others) && n < ROWS_MAX; ++i)
		{
			Row *r = &rows[n++];
			memset(r, 0, sizeof(*r));
			r->found = is_found(secret_others[i].id);
			SDL_strlcpy(r->label, r->found ? secret_others[i].name : "???", sizeof(r->label));
			SDL_strlcpy(r->what, secret_others[i].what, sizeof(r->what));
			SDL_strlcpy(r->hint, secret_others[i].hint, sizeof(r->hint));
		}
		break;
	}
	return n;
}

// Of a tab's rows, how many are found (data cubes: the cubes, not the episodes) of how many.
static void tab_share(int tab, int *got, int *total)
{
	Row rows[ROWS_MAX];
	const int n = rows_for(tab, rows);
	*got = *total = 0;
	if (tab == TAB_CUBES)
	{
		for (int e = 1; e <= EPISODE_MAX; ++e)
		{
			const int t = cubes_in_episode(e);
			*total += t;
			*got += SDL_min(cubes_found(e), t);
		}
		return;
	}
	*total = n;
	for (int i = 0; i < n; ++i)
		*got += rows[i].found;
}

void secrets_screen(void)
{
	load();
	if (shopSpriteSheet.data == NULL)
		JE_loadCompShapes(&shopSpriteSheet, '1');  // (the mouse pointer)
	ui_take_press();  // (no click from before)

	int tab = TAB_LEVELS, selected = 0, first = 0;
	const int visible = 12;  // rows the original screen shows
	bool restart = true;
	for (; ; )
	{
		Row rows[ROWS_MAX];
		const int count = rows_for(tab, rows);
		selected = SDL_clamp(selected, 0, SDL_max(count - 1, 0));
		if (selected < first)
			first = selected;
		if (selected >= first + visible)
			first = selected - visible + 1;

		if (restart)
		{
			JE_loadPic(VGAScreen2, 2, false);
			fill_rectangle_wh(VGAScreen2, 0, 192, 320, 8, 0);
			draw_font_hv_shadow(VGAScreen2, 160, 3, "Secrets", large_font, centered, 15, -3, false, 2);
		}
		memcpy(VGAScreen->pixels, VGAScreen2->pixels, (size_t)VGAScreen->pitch * VGAScreen->h);

		// The original screen's look: the kind and its share, the rows, the selected one's hint.
		int got, total;
		tab_share(tab, &got, &total);
		char line[96];
		snprintf(line, sizeof(line), "< %s  %d/%d >", tab_names[tab], got, total);
		draw_font_hv_shadow(VGAScreen, 160, 30, line, normal_font, centered, 15, -3, false, 2);
		for (int i = first; i < count && i < first + visible; ++i)
		{
			const int y = 50 + (i - first) * 10;
			const int brightness = i == selected ? 4 : rows[i].found ? 2 : 0;
			JE_textShade(VGAScreen, 20, y, rows[i].label, 15, brightness, FULL_SHADE);
			const char *state = rows[i].count[0] != '\0' ? rows[i].count : rows[i].found ? "Found" : "Locked";
			JE_textShade(VGAScreen, 250, y, state, 15, brightness, FULL_SHADE);
			JE_textShade(VGAScreen, 130, y, rows[i].what, 15, brightness - 1, FULL_SHADE);
		}
		if (count > 0)
			draw_font_hv(VGAScreen, 160, 178, rows[selected].hint, small_font, centered, 15, 0);

		// The modern UI's (ui.h).
		if (ui_modern())
		{
			UIMenu *ui = ui_menu_begin(UI_SCREEN_SECRETS, "Secrets");
			UISecrets *s = &ui->secrets;
			s->tab = tab;
			s->tab_count = TABS;
			for (int t = 0; t < TABS; ++t)
			{
				SDL_strlcpy(s->tab_names[t], tab_names[t], sizeof(s->tab_names[t]));
				tab_share(t, &s->found[t], &s->total[t]);
				s->all_found += s->found[t];
				s->all_total += s->total[t];
			}
			for (int i = 0; i < count; ++i)
			{
				UIItem *it = ui_menu_add(ui, UI_ITEM_ACTION, rows[i].label, 20, 50 + (i - first) * 10, 280, 10);
				it->hit = (SDL_Rect){ 0, 0, 0, 0 };  // (the UI's own rows: UI_ACTION_ITEM)
				it->owned = rows[i].found;
				SDL_strlcpy(it->value, rows[i].what, sizeof(it->value));
				SDL_strlcpy(it->value2, rows[i].count, sizeof(it->value2));
				SDL_strlcpy(it->hint, rows[i].hint, sizeof(it->hint));
			}
			ui->selected = selected;
			ui_menu_publish(ui, VGAScreen, VGAScreen2);
		}

		if (restart)
		{
			mouseCursor = MOUSE_POINTER_NORMAL;
			fade_palette(colors, 10, 0, 255);
			restart = false;
		}

		do
		{
			service_SDL_events(true);
			JE_mouseStart();
			JE_showVGA();
			JE_mouseReplace();
			SDL_Delay(16);
			push_joysticks_as_keyboard();
			service_SDL_events(false);
		} while (!(newkey || newmouse));

		// The modern UI's own widgets: a kind's tab, a row, back.
		const int action = ui_take_press();
		if (action >= UI_ACTION_PAGE && action < UI_ACTION_PAGE + TABS)
		{
			JE_playSampleNum(S_CURSOR);
			tab = action - UI_ACTION_PAGE;
			selected = first = 0;
			continue;
		}
		if (action >= UI_ACTION_ITEM && action < UI_ACTION_ITEM + count)
		{
			JE_playSampleNum(S_CURSOR);
			selected = action - UI_ACTION_ITEM;
			continue;
		}
		bool done = action == UI_ACTION_BACK || (newmouse && lastmouse_but == SDL_BUTTON_RIGHT);
		if (newkey)
		{
			switch (lastkey_scan)
			{
			case SDL_SCANCODE_UP:
				if (selected > 0)
				{
					--selected;
					JE_playSampleNum(S_CURSOR);
				}
				break;
			case SDL_SCANCODE_DOWN:
				if (selected < count - 1)
				{
					++selected;
					JE_playSampleNum(S_CURSOR);
				}
				break;
			case SDL_SCANCODE_LEFT:
			case SDL_SCANCODE_RIGHT:
				tab = (tab + (lastkey_scan == SDL_SCANCODE_LEFT ? TABS - 1 : 1)) % TABS;
				selected = first = 0;
				JE_playSampleNum(S_CURSOR);
				break;
			case SDL_SCANCODE_ESCAPE:
			case SDL_SCANCODE_RETURN:
			case SDL_SCANCODE_SPACE:
				done = true;
				break;
			default:
				break;
			}
		}
		if (done)
		{
			JE_playSampleNum(S_SPRING);
			break;
		}
	}
	fade_black(15);
	ui_screen_done();
}
