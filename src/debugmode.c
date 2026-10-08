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
#include "palette.h"
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

bool debug_flight = false;

/* --- The level list ---------------------------------------------------------------------- */

typedef struct
{
	int episode, section;
	char name[16];
} DebugLevel;

#define MAX_LEVELS 160
static DebugLevel levels[MAX_LEVELS];
static int level_count = -1;

// The sections of the episodes' scripts that load a level (as tools/levels.py lists them).
static void find_levels(void)
{
	level_count = 0;
	for (int episode = 1; episode <= EPISODE_MAX; ++episode)
	{
		if (!episodeAvail[episode - 1])
			continue;
		char file[32];
		snprintf(file, sizeof(file), "levels%d.dat", episode);
		FILE *f = dir_fopen(data_dir(), file, "rb");
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
	for (;;)
	{
		const int episode = levels[selected].episode;
		int first = selected, last = selected;
		while (first > 0 && levels[first - 1].episode == episode)
			--first;
		while (last + 1 < level_count && levels[last + 1].episode == episode)
			++last;
		int top = SDL_clamp(selected - ROWS / 2, first, SDL_max(first, last - ROWS + 1));

		JE_loadPic(VGAScreen, 2, false);
		JE_barShade(VGAScreen, 0, 0, 319, 199);
		JE_barShade(VGAScreen, 40, 8, 280, 191);
		draw_font_hv_shadow(VGAScreen, 160, 12, "Debug Flight", large_font, centered, 15, -3, false, 2);
		char line[64];
		snprintf(line, sizeof(line), "< Episode %d >", episode);
		draw_font_hv_shadow(VGAScreen, 160, 30, line, small_font, centered, 15, -2, false, 1);
		for (int i = top; i <= last && i < top + ROWS; ++i)
		{
			const bool here = i == selected;
			snprintf(line, sizeof(line), "%s", levels[i].name);
			draw_font_hv_shadow(VGAScreen, 160, LIST_Y + (i - top) * ROW_H, line, normal_font, centered, 15,
			                    here ? 1 : -4, false, 2);
		}
		draw_font_hv_shadow(VGAScreen, 160, 182, "Enter: fly   Esc: back   Left/Right: episode", small_font, centered, 15, -4,
		                    false, 1);
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
			while (selected > 0 && levels[selected - 1].episode == levels[selected].episode)
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

void debug_flight_from_environment(void)
{
	const char *debug = SDL_getenv("TYR3D_DEBUG");
	if (debug != NULL && SDL_atoi(debug) != 0 && gameLoaded)
		debug_flight = true;
}

/* --- Flying -------------------------------------------------------------------------------- */

#define TICKS_PER_SECOND 35
#define MAX_TICKS (TICKS_PER_SECOND * 60 * 30)  // half an hour of a level
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
} start;

static bool snapshot_wanted = false;
static char last_snapshot[64];
static Uint64 last_snapshot_time = 0;

static void apply_speed(void)
{
	nortsong_time_scale = 1.0f / speeds[speed];
}

static void set_replay(bool on)
{
	nortsong_skip_waits = on;
	set_volume(tyrMusicVolume, on ? 0 : fxVolume);
}

bool debug_flight_replaying(void)
{
	return debug_flight && replay_to >= 0 && tick < replay_to;
}

void debug_flight_level_start(void)
{
	if (!debug_flight)
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
		// The level again as it began; its input played back to the rewind's moment.
		restart = false;
		memcpy(player, start.players, sizeof(start.players));
		mt_load(start.rng);
		difficultyLevel = start.difficulty;
		mainLevel = start.section;
		set_replay(replay_to > 0);
	}
	else
	{
		restart = false;
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
	apply_speed();
}

bool debug_flight_restarting(void)
{
	return debug_flight && restart;
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

// Keys pressed since the last look (not held).
static bool pressed(SDL_Scancode key)
{
	static Uint8 was[SDL_SCANCODE_COUNT];
	const bool down = keysactive[key] != 0, edge = down && !was[key];
	was[key] = down;
	return edge;
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

void debug_flight_tick(void)
{
	if (!debug_flight)
		return;
	++tick;
	if (replay_to >= 0)
	{
		if (tick < replay_to)
			return;
		// There: the recording goes on from here.
		set_replay(false);
		recorded = SDL_min(recorded, replay_to);
		replay_to = -1;
		paused = pause_after_replay;
		pause_after_replay = false;
	}

	common_keys();
	if (pressed(SDL_SCANCODE_GRAVE))
		paused = !paused;

	// Paused: the frame stays (the camera keys work), until ` again; . goes a tick on.
	while (paused && !restart)
	{
		SDL_Delay(16);
		service_SDL_events(false);
		common_keys();
		if (pressed(SDL_SCANCODE_GRAVE))
			paused = false;
		if (pressed(SDL_SCANCODE_PERIOD))
			break;
		present_again();
	}
}

void debug_flight_input(int player_number, Player *p, JE_integer *accel_x, JE_integer *accel_y)
{
	if (!debug_flight || tick < 0 || tick >= MAX_TICKS || player_number < 1 || player_number > 2 || inputs[0] == NULL)
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
	recorded = SDL_max(recorded, tick + 1);
}

const char *debug_flight_status(void)
{
	static char status[160];
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
