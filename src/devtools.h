/*
 * Tyrian3D developer tooling: environment-driven helpers for automated testing.
 *
 *   TYR3D_DEMO_IDLE_MS   title-screen idle time before demo playback (default 30000)
 *   TYR3D_DUMP_DIR       directory to write presented frames to (BMP)
 *   TYR3D_DUMP_EVERY     write every Nth presented frame (default 60)
 *   TYR3D_EXIT_AFTER     exit after N presented frames
 *   TYR3D_DUMP_LAYERS    also dump the captured 3D layers of each dumped frame
 *   TYR3D_START          "<episode>:<section>": skip the title screen and start a game at that
 *                        section of the episode script (tools/levels.py lists level sections);
 *                        shops are skipped
 *   TYR3D_AUTOPILOT      the player ship weaves across the screen and fires constantly
 *   TYR3D_SHIP           with TYR3D_START: the player's ship (id as in the shop)
 *   TYR3D_SIDEKICKS      with TYR3D_START: "<left>,<right>" sidekick ids (as in the shop)
 *   TYR3D_GODMODE        the player takes no damage
 *   TYR3D_WINDOWED       run in a window in the corner of the screen without taking the focus
 *                        (and without pausing for the lack of it); tools/capture_run.sh sets it
 *   TYR3D_WINDOW_SIZE    with TYR3D_WINDOWED: the window's size, "<w>x<h>" (e.g. 1280x720)
 *   TYR3D_TEST_PAD       a virtual gamepad, which TYR3D_TEST_KEYS' Pad keys drive
 */
#ifndef DEVTOOLS_H
#define DEVTOOLS_H

#include "opentyr.h"

Uint32 dev_demo_idle_ms(void);

// Sets up a new game as TYR3D_START requests, once. Returns false if not requested.
bool dev_start_game(void);
// Sets up a new game starting at a section of an episode's script (shops skipped unless
// TYR3D_SHOP); TYR3D_SHIP, TYR3D_WEAPONS and the like apply.
bool dev_setup_game(int episode, int section);

bool dev_godmode(void);

// TYR3D_LOG_BALANCE: what a level costs and gives the player, a "balance: <what> <value> clock <tick>" line each:
// an enemy that comes (spawn, its type) and one killed (kill, or rammed: its slot), an enemy shot fired (shot, the
// enemy's type), the damage that hits the ship (damage, in god mode too; right after what dealt it: hit, an enemy
// shot, or bump, a collision, the enemy's type), an item an enemy leaves (drop, or droplost with no free slot for it;
// its value) and one picked up (pickup).
void dev_balance(const char *what, int value);

// TYR3D_LOG_SPRITES: what the 3D view draws from sprites (HD volumes, the sprites' own volumes, flat shots) rather
// than as models, each look once as it is first drawn so ("sprites: look <kind> sheet <sheet> sprite <n> first <first
// sprite> ... -> <a model of the same thing, or "no model">"), and for each level and the run how many objects
// were drawn either way ("sprites: level ...", "sprites: run ..."). dev_log_sprites_frame: the frame captured
// (layer3d.c l3d_frame_end); dev_log_sprites_store: a shot of the store's weapon simulator.
bool dev_log_sprites_on(void);
void dev_log_sprites_frame(void);
void dev_log_sprites_store(bool shots2, unsigned int sprite, bool model);

// Every tick of a level: TYR3D_LEVEL_TICKS=<n> ends levels (cleared) after n ticks, and
// TYR3D_LEVEL_DIE=<n> destroys the ship after n ticks, for testing what comes after them.
void dev_level_tick(void);
// At a level's start (after the game has set its items): TYR3D_BOMBS, with TYR3D_START.
void dev_level_start_items(void);

// True for TYR3D_WINDOWED runs, which keep playing without the window's focus.
bool dev_background_run(void);

// Autopilot steering for one player; adds to the movement and buttons for this frame.
bool dev_autopilot(void);
void dev_autopilot_steer(int x, int y, int speed, int *dx, int *dy, bool *fire);

// True if the frame about to be presented should be captured (pass its pixels below).
bool dev_capture_next_frame(void);
// TYR3D_DUMP_KEYS: the game has taken an input event (a test key is dumped in the next frame shown).
void dev_input_taken(void);
// Whether the frame being shown is dumped (TYR3D_DUMP_DIR; not the debug flight's snapshots).
bool dev_dumping_frame(void);

// TYR3D_TEST_PAD: attaches the virtual gamepad (before the game looks for its joysticks).
void dev_attach_test_pad(void);

// Called once per presented frame, with the final RGBA8 image if it was captured (else NULL).
void dev_on_frame_presented(const Uint8 *rgba, int width, int height, int pitch);

// Called with the captured layers of the frame about to be presented.
void dev_on_layers_captured(void);

#endif /* DEVTOOLS_H */
