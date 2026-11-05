/*
 * Tyrian3D: the debug flight. See debugmode.h.
 */
#include "debugmode.h"

#include "config.h"
#include "devtools.h"
#include "episodes.h"
#include "file.h"
#include "font.h"
#include "fonthand.h"
#include "helptext.h"
#include "joystick.h"
#include "keyboard.h"
#include "layer3d.h"
#include "loudness.h"
#include "mainint.h"
#include "mtrand.h"
#include "nortsong.h"
#include "network.h"
#include "palette.h"
#include "params.h"
#include "rogue.h"
#include "settings3d.h"
#include "tyrian2.h"
#include "picload.h"
#include "vga256d.h"
#include "varz.h"
#include "video.h"

#include <btbh_gpu/btbh_gpu.h>

#include <SDL3/SDL.h>

#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>

#ifdef _WIN32
#include <direct.h>
#define mkdir(path, mode) _mkdir(path)
#endif

bool debug_flight = false;

/* --- The level list ---------------------------------------------------------------------- */

typedef struct
{
	int episode, section;
	int custom;  // a custom episode's (1-based, episodes.h), 0 for the game's own
	char name[16];
} DebugLevel;

// The levels of one episode are together, a custom episode's apart from the episode it is played as.
static bool same_episode(const DebugLevel *a, const DebugLevel *b)
{
	return a->episode == b->episode && a->custom == b->custom;
}

#define MAX_LEVELS 160
static DebugLevel levels[MAX_LEVELS];
static int level_count = -1;

// The sections of the episodes' scripts that load a level (as tools/levels.py lists them).
static void find_levels(void)
{
	level_count = 0;
	const int playing_custom = custom_episode;
	for (int e = 1; e <= EPISODE_MAX + custom_episode_count; ++e)
	{
		// The game's episodes, then the custom episodes (their scripts from their folders).
		const int custom = e > EPISODE_MAX ? e - EPISODE_MAX : 0;
		const int episode = custom != 0 ? custom_episodes[custom - 1].episode : e;
		if (custom == 0 && !episodeAvail[episode - 1])
			continue;
		char file[32];
		snprintf(file, sizeof(file), "levels%d.dat", episode);
		custom_episode = custom;
		FILE *f = dir_fopen(data_dir(), file, "rb");
		custom_episode = playing_custom;
		if (f == NULL)
			continue;
		const long size = ftell_eof(f);
		int section = 0, last_section = -1;
		bool timed_battle = false;
		char s[256];
		while (ftell(f) < size && level_count < MAX_LEVELS)
		{
			read_encrypted_pascal_string(s, sizeof(s), f);
			if (s[0] == '*')
			{
				++section;
				char lower[256];
				for (int i = 0; s[i] != '\0' && i < 255; ++i)
					lower[i] = (char)tolower((unsigned char)s[i]), lower[i + 1] = '\0';
				timed_battle = strstr(lower, "timed battle") != NULL;
			}
			else if (s[0] == ']' && s[1] == 'L' && strlen(s) >= 22 && section != last_section && !timed_battle)
			{
				last_section = section;
				DebugLevel *l = &levels[level_count++];
				l->episode = episode;
				l->section = section;
				l->custom = custom;
				SDL_strlcpy(l->name, s + 13, 10);
				for (int i = (int)strlen(l->name) - 1; i >= 0 && l->name[i] == ' '; --i)
					l->name[i] = '\0';
			}
		}
		fclose(f);
	}
}

static void start_flight(const DebugLevel *l)
{
	custom_episode = l->custom;
	dev_setup_game(l->episode, l->section);
	// Fire power enough to look at what is destroyed.
	if (player[0].items.weapon[FRONT_WEAPON].power < 6)
		player[0].items.weapon[FRONT_WEAPON].power = 6;
	debug_flight = true;
	printf("debug: flying episode %d section %d (%s)\n", l->episode, l->section, l->name);
}

bool debug_pick_and_start(void)
{
	if (level_count < 0)
		find_levels();
	if (level_count == 0)
		return false;

	static int selected = 0;
	enum { ROWS = 12, ROW_H = 11, LIST_Y = 44 };
	bool faded_in = false;
	for (;;)
	{
		const DebugLevel *const shown = &levels[selected];
		int first = selected, last = selected;
		while (first > 0 && same_episode(&levels[first - 1], shown))
			--first;
		while (last + 1 < level_count && same_episode(&levels[last + 1], shown))
			++last;
		int top = SDL_clamp(selected - ROWS / 2, first, SDL_max(first, last - ROWS + 1));

		JE_loadPic(VGAScreen, 2, false);
		JE_barShade(VGAScreen, 0, 0, 319, 199);
		JE_barShade(VGAScreen, 40, 8, 280, 191);
		draw_font_hv_shadow(VGAScreen, 160, 12, "Debug Flight", large_font, centered, 15, -3, false, 2);
		char line[64];
		if (shown->custom != 0)
			snprintf(line, sizeof(line), "< Custom: %s >", custom_episodes[shown->custom - 1].title);
		else
			snprintf(line, sizeof(line), "< Episode %d >", shown->episode);
		draw_font_hv_shadow(VGAScreen, 160, 30, line, small_font, centered, 15, 2, false, 1);
		for (int i = top; i <= last && i < top + ROWS; ++i)
		{
			const bool here = i == selected;
			snprintf(line, sizeof(line), "%s", levels[i].name);
			draw_font_hv_shadow(VGAScreen, 160, LIST_Y + (i - top) * ROW_H, line, normal_font, centered, 15,
			                    here ? 1 : -4, false, 2);
		}
		draw_font_hv_shadow(VGAScreen, 160, 182, "Enter: fly   Esc: back   Left/Right: episode", small_font, centered, 15, 0,
		                    false, 1);
		if (!faded_in)
		{
			fade_palette(colors, 10, 0, 255);  // (the menus before it faded to black)
			faded_in = true;
		}
		JE_showVGA();

		service_SDL_events(true);
		do
		{
			SDL_Delay(16);
			push_joysticks_as_keyboard();
			service_SDL_events(false);
		} while (!newkey);

		switch (lastkey_scan)
		{
		case SDL_SCANCODE_UP:
			selected = selected > first ? selected - 1 : last;
			JE_playSampleNum(S_CURSOR);
			break;
		case SDL_SCANCODE_DOWN:
			selected = selected < last ? selected + 1 : first;
			JE_playSampleNum(S_CURSOR);
			break;
		case SDL_SCANCODE_PAGEUP:
			selected = SDL_max(selected - ROWS, first);
			break;
		case SDL_SCANCODE_PAGEDOWN:
			selected = SDL_min(selected + ROWS, last);
			break;
		case SDL_SCANCODE_LEFT:
			selected = first > 0 ? first - 1 : level_count - 1;
			while (selected > 0 && same_episode(&levels[selected - 1], &levels[selected]))
				--selected;
			JE_playSampleNum(S_CURSOR);
			break;
		case SDL_SCANCODE_RIGHT:
			selected = last + 1 < level_count ? last + 1 : 0;
			JE_playSampleNum(S_CURSOR);
			break;
		case SDL_SCANCODE_RETURN:
		case SDL_SCANCODE_SPACE:
			JE_playSampleNum(S_SELECT);
			fade_black(10);
			start_flight(&levels[selected]);
			return true;
		case SDL_SCANCODE_ESCAPE:
			JE_playSampleNum(S_SPRING);
			return false;
		default:
			break;
		}
	}
}

bool debug_picker_from_environment(void)
{
	static bool done = false;
	const char *debug = SDL_getenv("TYR3D_DEBUG");
	if (done || debug == NULL || SDL_strcasecmp(debug, "pick") != 0)
		return false;
	done = true;
	return true;
}

void debug_flight_from_environment(void)
{
	const char *debug = SDL_getenv("TYR3D_DEBUG");
	if (debug != NULL && SDL_atoi(debug) != 0 && gameLoaded)
		debug_flight = true;
}

/* --- Flying -------------------------------------------------------------------------------- */

#define TICKS_PER_SECOND 35
#define MAX_TICKS (TICKS_PER_SECOND * 60 * 90)  // an hour and a half of a level (episode 6's HOARD fights are long)
#define REWIND_TICKS (TICKS_PER_SECOND * 5)

typedef struct
{
	Sint16 x, y, vx, vy, ax, ay;
	Uint8 buttons;
} DebugInput;

static DebugInput *inputs[2];
static int tick = -1;          // the level's tick (counted from 0)
static int recorded = 0;       // ticks of input recorded
static int replay_to = -1;     // replaying the input up to this tick
static bool restart = false, paused = false, pause_after_replay = false;
static int speed = 2;
static const float speeds[] = { 0.25f, 0.5f, 1.0f, 2.0f, 4.0f, 8.0f };

static struct
{
	bool valid;
	JE_byte section;
	Player players[2];
	JE_byte difficulty;
	void *rng;
	bool again;       // the level starting again for a rewind
	bool field_wide;  // the playfield it began on
} start;

static bool snapshot_wanted = false;
static char last_snapshot[64];
static Uint64 last_snapshot_time = 0;

/* --- Checkpoints ------------------------------------------------------------------------- */

// Tyrian3D: checkpoints in the long levels (the user, 2026-11-04: "možemo na dužim levelima dodati checkpointove?"),
// on the debug flight's recording: a one-player full game records its input from the level's start as the debug
// flight does; past a checkpoint (the middle of a level whose events go on past CHECKPOINT_LONG clock, the thirds of
// one past twice that; or where the level's own events 208 put them: episode 6's HOARD, one at every fight but its
// first) a death plays the level again from its start, its recorded input played back unseen and
// unwaited to the checkpoint's tick, so the ship is there as it was (its savings, what it had shot down), and the game
// goes on from there, the ship a moment unhurt. Not in network games, demos, timed battles, rogue runs, arcade or two-
// player play, nor the debug flight (which rewinds its own way).
#define CHECKPOINT_LONG 4500
static bool checkpoints = false;   // recording for them (the level began in a game that has them)
static bool relaunching = false;   // the level starting again for one (checkpoint_relaunch)
static int checkpoint_tick = 0;    // the last one passed (0: none yet)
static int checkpoint_marks[32], checkpoint_mark_count = -1;  // their clocks (-1: not yet found)

static bool checkpoints_allowed(void)
{
	return !debug_flight && !isNetworkGame && !play_demo && !record_demo && !timedBattleMode && !rogue_run &&
	       !onePlayerAction && !twoPlayerMode && !superTyrian && superArcadeMode == SA_NONE;
}

// Recording, for the debug flight or the checkpoints.
static bool recording(void)
{
	return debug_flight || checkpoints;
}

static void checkpoint_marks_find(void)
{
	const int last = level_last_event_clock();
	checkpoint_mark_count = level_checkpoint_clocks(checkpoint_marks, (int)COUNTOF(checkpoint_marks));
	if (checkpoint_mark_count > 0)
		return;
	if (last > 2 * CHECKPOINT_LONG)
	{
		checkpoint_marks[checkpoint_mark_count++] = last / 3;
		checkpoint_marks[checkpoint_mark_count++] = last * 2 / 3;
	}
	else if (last > CHECKPOINT_LONG)
		checkpoint_marks[checkpoint_mark_count++] = last / 2;
}

// quiet: playing back towards the last one (those passed on the way are passed again, unsaid)
static void checkpoint_tick_check(bool quiet)
{
	if (checkpoint_mark_count < 0)
		checkpoint_marks_find();
	for (int k = 0; k < checkpoint_mark_count; ++k)
		if (curLoc >= checkpoint_marks[k] && checkpoint_marks[k] > 0 && (quiet || (checkpoint_tick < tick && player[0].is_alive)))
		{
			checkpoint_marks[k] = 0;  // (passed)
			if (quiet)
				continue;
			checkpoint_tick = tick;
			JE_drawTextWindow("Checkpoint");
			printf("checkpoint: %s tick %d clock %d, the ship at %d %d, armor %u\n", levelName, tick, curLoc, player[0].x, player[0].y,
			       player[0].armor);
		}
}

// Keys pressed since the last look (not held).
static bool pressed(SDL_Scancode key)
{
	static Uint8 was[SDL_SCANCODE_COUNT];
	const bool down = keysactive[key] != 0, edge = down && !was[key];
	was[key] = down;
	return edge;
}

static void apply_speed(void)
{
	nortsong_time_scale = 1.0f / speeds[speed];
}

static void set_replay(bool on)
{
	nortsong_skip_waits = on;
	// (Muting the samples didn't hold: the level's start sets their volume again, and the replay's sounds came all at
	// once, the user: "kad se očitava checkpoint, dobijemo neki neugodni zvuk".)
	audio_hold(on);
}

/* --- Debug keys ---------------------------------------------------------------------------- */

// Tyrian3D: keys for trying levels out in any game (Setup -> Debug Keys; the user, 2026-11-05: "debug tipke za
// besmrtnost i ubrzanje i usporavanje gameplaya"): F9 the ship invincible or not, - and = the game slower and faster
// (the debug flight's speeds). The invincibility goes with the recorded input, so a checkpoint's replay has it where
// it was, and after it is as F9 last left it. Not in network games nor demos.
#define INPUT_INVINCIBLE (1 << 4)  // (DebugInput.buttons: past the four buttons)
static bool invincible = false;           // F9's
static bool invincible_replayed = false;  // the recording's, while it plays back

bool debug_keys_on(void)
{
	return !debug_flight && !isNetworkGame && !play_demo && (settings3d.debug_keys || SDL_getenv("TYR3D_DEBUG_KEYS") != NULL);
}

bool debug_invincible(void)
{
	return debug_flight_replaying() ? invincible_replayed : invincible && debug_keys_on();
}

float debug_speed(void)
{
	return speeds[speed];
}

const char *debug_keys_tick(void)
{
	static char said[32];
	if (!debug_keys_on())
	{
		if (!debug_flight && speed != 2)
		{
			speed = 2;
			apply_speed();
		}
		return NULL;
	}
	if (debug_flight_replaying())
		return NULL;
	const char *say = NULL;
	if (pressed(SDL_SCANCODE_F9))
	{
		invincible = !invincible;
		say = invincible ? "Invincible" : "Invincible off";
	}
	const int was = speed;
	if (pressed(SDL_SCANCODE_MINUS) && speed > 0)
		--speed;
	if (pressed(SDL_SCANCODE_EQUALS) && speed + 1 < (int)SDL_arraysize(speeds))
		++speed;
	if (speed != was)
	{
		apply_speed();
		if (speeds[speed] < 1.0f)
			snprintf(said, sizeof(said), "Speed 1/%dx", (int)(1.0f / speeds[speed] + 0.5f));
		else
			snprintf(said, sizeof(said), "Speed %dx", (int)speeds[speed]);
		say = said;
	}
	if (say != NULL)
		printf("debug keys: %s\n", say);
	return say;
}

bool debug_flight_replaying(void)
{
	return recording() && replay_to >= 0 && tick < replay_to;
}

void debug_flight_level_start(void)
{
	if (!restart)
	{
		checkpoints = checkpoints_allowed();
		checkpoint_tick = 0;
	}
	checkpoint_mark_count = -1;
	if (!debug_flight && !debug_keys_on())
		speed = 2;
	apply_speed();
	if (!recording())
		return;
	if (start.rng == NULL)
		start.rng = malloc(mt_state_size());
	for (int i = 0; i < 2; ++i)
		if (inputs[i] == NULL)
			inputs[i] = calloc(MAX_TICKS, sizeof(DebugInput));
	if (start.rng == NULL || inputs[0] == NULL || inputs[1] == NULL)
		return;

	if (restart && start.valid)
	{
		// The level again as it began; its input played back to the rewind's moment. (A checkpoint's: as the script
		// launched it, the ships and the random numbers then: tyrian2.c launch_again.)
		restart = false;
		start.again = true;
		if (checkpoints)
			relaunching = true;
		else
		{
			memcpy(player, start.players, sizeof(start.players));
			mt_load(start.rng);
			difficultyLevel = start.difficulty;
			mainLevel = start.section;
		}
		set_replay(replay_to > 0);
	}
	else
	{
		restart = false;
		start.again = false;
		start.valid = true;
		start.section = mainLevel;
		memcpy(start.players, player, sizeof(start.players));
		mt_save(start.rng);
		start.difficulty = difficultyLevel;
		recorded = 0;
		replay_to = -1;
		paused = false;
		// TYR3D_DEBUG_SEEK: the first level starts that far in.
		static bool seeked = false;
		const char *seek = SDL_getenv("TYR3D_DEBUG_SEEK");
		if (!seeked && seek != NULL && SDL_atoi(seek) > 0)
		{
			replay_to = SDL_atoi(seek);
			set_replay(true);
		}
		seeked = true;
	}
	tick = -1;
}

bool debug_flight_field_wide(bool wide)
{
	if (!recording())
		return wide;
	if (start.again)
		return start.field_wide;
	start.field_wide = wide;
	return wide;
}

bool debug_flight_restarting(void)
{
	return recording() && restart;
}

bool checkpoint_relaunch(void)
{
	const bool was = relaunching;
	relaunching = false;
	return was;
}

bool checkpoint_restart(void)
{
	if (!checkpoints || checkpoint_tick <= 0 || !start.valid || !all_players_dead())
		return false;
	replay_to = checkpoint_tick;
	pause_after_replay = false;
	restart = true;
	printf("checkpoint: %s again from tick %d, at %u ms\n", levelName, checkpoint_tick, (unsigned)SDL_GetTicks());
	return true;
}

static void rewind_by(int ticks)
{
	if (!start.valid || restart)
		return;
	replay_to = SDL_max(tick - ticks, 0);
	pause_after_replay = paused;
	paused = false;
	restart = true;
	reallyEndLevel = true;
	printf("debug: rewind to tick %d\n", replay_to);
}

static void present_again(void)
{
	if (l3d_enabled)
		JE_showVGA3D();
	else
		JE_showVGA();
}

// The keys for the speed, the rewind and snapshots (all but the pause's own).
static void common_keys(void)
{
	if (pressed(SDL_SCANCODE_MINUS) && speed > 0)
	{
		--speed;
		apply_speed();
	}
	if (pressed(SDL_SCANCODE_EQUALS) && speed + 1 < (int)SDL_arraysize(speeds))
	{
		++speed;
		apply_speed();
	}
	if (pressed(SDL_SCANCODE_BACKSPACE))
		rewind_by(REWIND_TICKS);
	if (pressed(SDL_SCANCODE_F12))
		snapshot_wanted = true;
}

// The loadout keys. The level's start takes a change too, so a rewind keeps it (the input played
// back was flown with the old loadout, so the moment may differ a little).
static bool usable_name(const char *name)
{
	return name[0] != '\0' && SDL_strncasecmp(name, "None", 4) != 0 && SDL_strncasecmp(name, "Test", 4) != 0 &&
	       SDL_strncasecmp(name, "Misc", 4) != 0;
}

static int next_port(int id, int step)
{
	for (int n = 0; n <= PORT_NUM; ++n)
	{
		id = (id + step + PORT_NUM + 1) % (PORT_NUM + 1);
		if (id == 0 || (usable_name(weaponPort[id].name) && weaponPort[id].op[0][0] != 0))
			return id;
	}
	return 0;
}

static int next_sidekick(int id)
{
	for (int n = 0; n <= OPTION_NUM; ++n)
	{
		id = (id + 1) % (OPTION_NUM + 1);
		if (id == 0 || (usable_name(options[id].name) && options[id].wpnum != 0))
			return id;
	}
	return 0;
}

static void loadout_keys(void)
{
	Player *p = &player[0];
	PlayerItems *items = &p->items;
	const PlayerItems before = *items;
	if (pressed(SDL_SCANCODE_LEFTBRACKET))
		items->weapon[FRONT_WEAPON].id = (JE_byte)next_port(items->weapon[FRONT_WEAPON].id, -1);
	if (pressed(SDL_SCANCODE_RIGHTBRACKET))
		items->weapon[FRONT_WEAPON].id = (JE_byte)next_port(items->weapon[FRONT_WEAPON].id, 1);
	if (pressed(SDL_SCANCODE_9))
		items->weapon[REAR_WEAPON].id = (JE_byte)next_port(items->weapon[REAR_WEAPON].id, -1);
	if (pressed(SDL_SCANCODE_0))
		items->weapon[REAR_WEAPON].id = (JE_byte)next_port(items->weapon[REAR_WEAPON].id, 1);
	const int power_step = pressed(SDL_SCANCODE_APOSTROPHE) - pressed(SDL_SCANCODE_SEMICOLON);
	for (int w = 0; w < 2; ++w)
		items->weapon[w].power = (JE_byte)SDL_clamp(items->weapon[w].power + power_step, 1, WEAPON_POWER_OVERCLOCK);
	if (pressed(SDL_SCANCODE_7))
		items->sidekick[LEFT_SIDEKICK] = (JE_byte)next_sidekick(items->sidekick[LEFT_SIDEKICK]);
	if (pressed(SDL_SCANCODE_8))
		items->sidekick[RIGHT_SIDEKICK] = (JE_byte)next_sidekick(items->sidekick[RIGHT_SIDEKICK]);
	if (memcmp(&before, items, sizeof(before)) == 0)
		return;

	if (items->weapon[REAR_WEAPON].id != before.weapon[REAR_WEAPON].id)
		p->weapon_mode = 1;
	if (memcmp(before.sidekick, items->sidekick, sizeof(before.sidekick)) != 0)
		JE_drawOptions();  // the sidekicks' ammo, style and HUD
	start.players[0].items = *items;
	start.players[0].weapon_mode = p->weapon_mode;
	printf("debug: front %d, rear %d, power %d, sidekicks %d, %d\n", items->weapon[FRONT_WEAPON].id,
	       items->weapon[REAR_WEAPON].id, items->weapon[FRONT_WEAPON].power, items->sidekick[LEFT_SIDEKICK],
	       items->sidekick[RIGHT_SIDEKICK]);
}

void debug_flight_tick(void)
{
	const char *said = debug_keys_tick();
	if (said != NULL)
		JE_drawTextWindow(said);
	if (!recording())
		return;
	++tick;
	if (replay_to >= 0)
	{
		if (tick < replay_to)
		{
			if (tick < recorded && tick < MAX_TICKS && inputs[0] != NULL)
				invincible_replayed = (inputs[0][tick].buttons & INPUT_INVINCIBLE) != 0;
			if (checkpoints)
				checkpoint_tick_check(true);
			return;
		}
		// There: the recording goes on from here.
		set_replay(false);
		printf("debug: played back to tick %d, at %u ms, the ship at %d %d, armor %u\n", tick, (unsigned)SDL_GetTicks(), player[0].x,
		       player[0].y, player[0].armor);
		recorded = SDL_min(recorded, replay_to);
		replay_to = -1;
		paused = pause_after_replay;
		pause_after_replay = false;
		if (checkpoints)  // (back at a checkpoint: a moment unhurt; it, passed again, unsaid)
		{
			player[0].invulnerable_ticks = SDL_max(player[0].invulnerable_ticks, 100);
			checkpoint_tick_check(true);
		}
	}
	if (!debug_flight)
	{
		checkpoint_tick_check(false);
		return;
	}

	common_keys();
	loadout_keys();
	if (pressed(SDL_SCANCODE_GRAVE))
		paused = !paused;

	// Paused: the frame stays (the camera keys work), until ` again; . goes a tick on.
	while (paused && !restart)
	{
		SDL_Delay(16);
		service_SDL_events(false);
		common_keys();
		loadout_keys();
		if (pressed(SDL_SCANCODE_GRAVE))
			paused = false;
		if (pressed(SDL_SCANCODE_PERIOD))
			break;
		present_again();
	}
}

void debug_flight_input(int player_number, Player *p, JE_integer *accel_x, JE_integer *accel_y)
{
	if (!recording() || tick < 0 || tick >= MAX_TICKS || player_number < 1 || player_number > 2 || inputs[0] == NULL)
		return;
	DebugInput *in = &inputs[player_number - 1][tick];
	if (debug_flight_replaying())
	{
		if (tick >= recorded)
			return;  // (seeking further than played: no input)
		p->x = in->x;
		p->y = in->y;
		p->x_velocity = in->vx;
		p->y_velocity = in->vy;
		*accel_x = in->ax;
		*accel_y = in->ay;
		for (int i = 0; i < 4; ++i)
			button[i] = (in->buttons >> i) & 1;
		return;
	}
	*in = (DebugInput){ (Sint16)p->x, (Sint16)p->y, (Sint16)p->x_velocity, (Sint16)p->y_velocity, (Sint16)*accel_x,
	                    (Sint16)*accel_y, 0 };
	for (int i = 0; i < 4; ++i)
		in->buttons |= button[i] ? 1 << i : 0;
	if (player_number == 1 && debug_invincible())
		in->buttons |= INPUT_INVINCIBLE;
	recorded = SDL_max(recorded, tick + 1);
}

const char *debug_flight_status(void)
{
	static char status[160];
	if (debug_keys_on() && (invincible || speed != 2))
	{
		char speed_text[16] = "";
		if (speeds[speed] < 1.0f)
			snprintf(speed_text, sizeof(speed_text), "1/%dx", (int)(1.0f / speeds[speed] + 0.5f));
		else if (speed != 2)
			snprintf(speed_text, sizeof(speed_text), "%dx", (int)speeds[speed]);
		snprintf(status, sizeof(status), "%s%s%s", invincible ? "INVINCIBLE" : "", invincible && speed != 2 ? "   " : "", speed_text);
		return status;
	}
	if (!debug_flight || tick < 0)
		return "";
	char name[16];
	SDL_strlcpy(name, levelName, sizeof(name));
	for (int i = (int)strlen(name) - 1; i >= 0 && name[i] == ' '; --i)
		name[i] = '\0';
	const int seconds = tick / TICKS_PER_SECOND;
	char speed_text[16];
	if (speeds[speed] < 1.0f)
		snprintf(speed_text, sizeof(speed_text), "1/%dx", (int)(1.0f / speeds[speed] + 0.5f));
	else
		snprintf(speed_text, sizeof(speed_text), "%dx", (int)speeds[speed]);
	const bool saved = last_snapshot[0] != '\0' && SDL_GetTicks() - last_snapshot_time < 2500;
	snprintf(status, sizeof(status), "DEBUG   %s (%d:%d)   %d:%02d  tick %d   %s%s%s%s", name, episodeNum, start.section,
	         seconds / 60, seconds % 60, tick, speed_text, paused ? "   PAUSED" : "", saved ? "   saved " : "",
	         saved ? last_snapshot : "");
	return status;
}

const char *debug_flight_keys(void)
{
	return debug_flight ? "-/= speed    Backspace back 5 s    ` pause    . step    F12 snapshot" : "";
}

// An item's name without its trailing spaces and the ammunition some sidekicks name ("Ammo 5").
static const char *short_name(const char *name)
{
	static char out[4][32];
	static int next = 0;
	char *o = out[next++ % 4];
	SDL_strlcpy(o, name, sizeof(out[0]));
	char *gap = strstr(o, "  ");
	if (gap != NULL)
		*gap = '\0';
	for (int i = (int)strlen(o) - 1; i >= 0 && o[i] == ' '; --i)
		o[i] = '\0';
	return o;
}

const char *debug_flight_loadout(void)
{
	static char loadout[192];
	if (!debug_flight || tick < 0)
		return "";
	const PlayerItems *items = &player[0].items;
	snprintf(loadout, sizeof(loadout), "[ ] %s    9 0 %s    ; ' power %d    7 8 %s, %s",
	         short_name(weaponPort[items->weapon[FRONT_WEAPON].id].name),
	         short_name(weaponPort[items->weapon[REAR_WEAPON].id].name), items->weapon[FRONT_WEAPON].power,
	         short_name(options[items->sidekick[LEFT_SIDEKICK]].name), short_name(options[items->sidekick[RIGHT_SIDEKICK]].name));
	return loadout;
}

bool debug_flight_snapshot_wanted(void)
{
	return debug_flight && snapshot_wanted;
}

void debug_flight_snapshot(const Uint8 *rgba, int width, int height, int pitch)
{
	snapshot_wanted = false;
	char name[16];
	int n = 0;
	for (const char *c = levelName; *c != '\0' && n < (int)sizeof(name) - 1; ++c)
		if (isalnum((unsigned char)*c))
			name[n++] = *c;
	name[n] = '\0';
	const int seconds = SDL_max(tick, 0) / TICKS_PER_SECOND;
	snprintf(last_snapshot, sizeof(last_snapshot), "%s_e%ds%d_t%d_%dm%02ds.png", name, episodeNum, start.section,
	         SDL_max(tick, 0), seconds / 60, seconds % 60);

	char dir[1024], path[1200];
	snprintf(dir, sizeof(dir), "%s", TYR3D_FEEDBACK_DIR);
	mkdir(dir, 0755);
	snprintf(path, sizeof(path), "%s/%s", dir, last_snapshot);
	// The picture packed (its rows may be padded).
	Uint8 *packed = malloc((size_t)width * height * 4);
	if (packed == NULL)
		return;
	for (int y = 0; y < height; ++y)
		memcpy(packed + (size_t)y * width * 4, rgba + (size_t)y * pitch, (size_t)width * 4);
	if (btbh_gpu_write_png_rgba8(path, (uint32_t)width, (uint32_t)height, packed) != BTBH_GPU_OK)
		fprintf(stderr, "warning: failed to write %s\n", path);
	else
		printf("debug: snapshot %s\n", path);
	free(packed);
	last_snapshot_time = SDL_GetTicks();
}
