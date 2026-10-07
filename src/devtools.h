/*
 * Tyrian3D developer tooling: environment-driven helpers for automated testing.
 *
 *   TYR3D_DEMO_IDLE_MS   title-screen idle time before demo playback (default 30000)
 *   TYR3D_DUMP_DIR       directory to write presented frames to (BMP)
 *   TYR3D_DUMP_EVERY     write every Nth presented frame (default 60)
 *   TYR3D_EXIT_AFTER     exit after N presented frames
 *   TYR3D_DUMP_LAYERS    also dump the captured 3D layers of each dumped frame
 */
#ifndef DEVTOOLS_H
#define DEVTOOLS_H

#include "opentyr.h"

Uint32 dev_demo_idle_ms(void);

// True if the frame about to be presented should be captured (pass its pixels below).
bool dev_capture_next_frame(void);

// Called once per presented frame, with the final RGBA8 image if it was captured (else NULL).
void dev_on_frame_presented(const Uint8 *rgba, int width, int height, int pitch);

// Called with the captured layers of the frame about to be presented.
void dev_on_layers_captured(void);

#endif /* DEVTOOLS_H */
