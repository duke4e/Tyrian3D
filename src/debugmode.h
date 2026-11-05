/*
 * Tyrian3D: the debug flight. A level picked from a list (Setup -> Debug Flight...) is flown
 * without losing lives, with keys to change the game's speed, rewind, pause and step, and save a
 * snapshot named after the level and the moment (export/feedback), for looking at levels closely.
 *
 * Rewinding restarts the level and plays the recorded input back to the moment wanted, quickly
 * and without showing it (the game is deterministic given its input and random seed).
 *
 * Keys while flying: - and = slower and faster (1/4x to 8x), Backspace back 5 seconds, ` pause,
 * . one tick on while paused, F12 snapshot; the loadout: [ and ] the front weapon, 9 and 0 the rear
 * weapon, ; and ' their power, 7 and 8 the left and right sidekick (the new items of content.h too).
 *
 *   TYR3D_DEBUG=1          with TYR3D_START: the game starts as a debug flight
 *   TYR3D_DEBUG=pick       the level list first, instead of the title screen
 *   TYR3D_DEBUG_SEEK=<n>   with it: the level starts n ticks in (played without showing)
 */
#ifndef DEBUGMODE_H
#define DEBUGMODE_H

#include "opentyr.h"
#include "player.h"

extern bool debug_flight;

// The level list (Setup -> Debug Flight...): true when a level was picked and a game set up.
bool debug_pick_and_start(void);

// Turns the debug flight on for a game TYR3D_START set up, if TYR3D_DEBUG asks for it.
void debug_flight_from_environment(void);
// TYR3D_DEBUG=pick: the level list instead of the title screen (once).
bool debug_picker_from_environment(void);

// At a level's start, before its map loads (JE_main): remembers the start, or puts it back when
// the level restarts to rewind.
void debug_flight_level_start(void);
// At start_level: true when the level restarts (a rewind) rather than ending.
bool debug_flight_restarting(void);
// At start_level, the ship lost: true when the level plays again to its last checkpoint passed (then
// debug_flight_restarting too). Tyrian3D's checkpoints in the long levels, on the debug flight's recording.
bool checkpoint_restart(void);
// In JE_loadMap: true (once) when the level starts again for a checkpoint: it is launched as it was (tyrian2.c
// launch_again), without the script.
bool checkpoint_relaunch(void);
// The playfield's width (l3d_field_wide) for the level starting: as it began when it starts again
// for a rewind (the input played back was played on it; a change of the setting or the view in
// between waits for the next level).
bool debug_flight_field_wide(bool wide);
// Every tick of the level's loop: keys, the pause, the speed, the replay.
void debug_flight_tick(void);
// In JE_playerMovement once the player's input is read: records it, or replays it.
void debug_flight_input(int player_number, Player *player, JE_integer *accel_x, JE_integer *accel_y);

// Playing back towards a rewind's moment: nothing is shown nor waited for.
bool debug_flight_replaying(void);

// The debug keys in any game (Setup -> Debug Keys, or TYR3D_DEBUG_KEYS=1): F9 the ship invincible, - and = the game
// slower and faster. On (not in the debug flight, which has its own, nor network games and demos)?
bool debug_keys_on(void);
// The ship invincible by F9 (as recorded, while a checkpoint's replay plays).
bool debug_invincible(void);
// The game's speed (1: as it is) the debug keys or the debug flight set.
float debug_speed(void);
// Every tick the game goes on (the level's loop, the rail's): the keys; what to say of a change (NULL: none).
const char *debug_keys_tick(void);

// The line the HUD shows while flying (empty otherwise).
const char *debug_flight_status(void);
const char *debug_flight_keys(void);
const char *debug_flight_loadout(void);

bool debug_flight_snapshot_wanted(void);
void debug_flight_snapshot(const Uint8 *rgba, int width, int height, int pitch);

#endif /* DEBUGMODE_H */
