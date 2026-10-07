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
 *   TYR3D_GODMODE        the player takes no damage
 */
#ifndef DEVTOOLS_H
#define DEVTOOLS_H

#include "opentyr.h"

Uint32 dev_demo_idle_ms(void);

// Sets up a new game as TYR3D_START requests, once. Returns false if not requested.
bool dev_start_game(void);

bool dev_godmode(void);

// Autopilot steering for one player; adds to the movement and buttons for this frame.
bool dev_autopilot(void);
void dev_autopilot_steer(int x, int y, int speed, int *dx, int *dy, bool *fire);

// True if the frame about to be presented should be captured (pass its pixels below).
bool dev_capture_next_frame(void);

// Called once per presented frame, with the final RGBA8 image if it was captured (else NULL).
void dev_on_frame_presented(const Uint8 *rgba, int width, int height, int pitch);

// Called with the captured layers of the frame about to be presented.
void dev_on_layers_captured(void);

#endif /* DEVTOOLS_H */
