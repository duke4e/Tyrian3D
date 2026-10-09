/*
 * Tyrian3D: the rogue mode (Start New Game -> Rogue Run). A run is three acts of the episodes'
 * own levels on a map with branches: after each level a card adds to the ship (a weapon, its
 * power, a sidekick, a shield, a generator, a ship, a special, an extra life, credits); elite
 * levels are harder and pay better, merchants sell cards for credits, a boss ends each act. Dying
 * without an extra life ends the run. Runs earn cores, which buy unlocks (more cards, better
 * starts) kept between runs.
 *
 * The data (acts, their levels, the cards' items, the unlocks) is assets/content/rogue.cfg, made
 * by tools/content/make_rogue.py:
 *
 *   act <n> name= difficulty= rows=      an act: its difficulty (2 normal .. 4 impossible) and
 *                                        its rows of choices before the boss
 *   level <act> <episode>:<section> "<name>"   a level of the act (the section of its ]L)
 *   boss <act> <episode>:<section> "<name>"    a level that can end the act
 *   item <kind> <id> tier=<1-3> [unlock=<name>]   an item cards can offer: kind front, rear,
 *                                        left, right, shield, generator, ship or special
 *   unlock <name> cost=<cores> title= text=
 *
 * The profile (cores, unlocks, runs) is tyrian3d_rogue.cfg in the user directory.
 *
 *   TYR3D_ROGUE=<seed>   a run starts at once (no menus), with that seed
 *   TYR3D_ROGUE=menu     the rogue screen at once
 * (with either, the profile isn't saved: test runs leave it alone)
 *   TYR3D_ROGUE_AUTO=1   the screens choose by themselves (whole runs with the autopilot)
 *   TYR3D_ROGUE_UNLOCKS=all   every unlock, for the test run
 */
#ifndef ROGUE_H
#define ROGUE_H

#include "opentyr.h"

// A rogue run is on: it picks the levels, the episode scripts' texts, pictures, shops and backup
// saves are skipped.
extern bool rogue_run;

// The rogue screen (from the game type menu): true when a run was started and its first level
// set up.
bool rogue_menu(void);

// TYR3D_ROGUE: a run at once (once).
bool rogue_from_environment(void);

// TYR3D_ROGUE_AUTO in a run: nothing waits for the player (the level's end screen too).
bool rogue_automatic(void);

// The enemy type of the purple orb (value 30000), what the arcade's drops (event 45) leave in a run.
#define ROGUE_ORB_ENEMY 628

// A purple orb picked up: in a run it is experience (true; the game's own weapon power-up is left
// out), each level of it a card after the level.
bool rogue_purple_ball(void);
// The run's experience for the HUD: false outside a run.
bool rogue_xp(int *xp, int *needed, int *level);

// At start_level in a run, when a level ended: the reward, the map, the next level. False when
// the run is over (back to the title screen).
bool rogue_level_over(void);

#endif /* ROGUE_H */
