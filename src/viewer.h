/*
 * Tyrian3D dev tool: a model viewer.
 *
 * TYR3D_VIEWER=ships shows each player ship's 3D appearance (as models.cfg gives it) beside its
 * sprite, in rows, in the 3D view with the levels' palette and lighting. It runs until Escape
 * (or TYR3D_EXIT_AFTER frames, with TYR3D_DUMP_DIR for captures), then exits.
 *
 *   TYR3D_VIEWER_YAW=<degrees>   turn the models (default 0: as in the game)
 *   TYR3D_VIEWER_ROLL=<degrees>  roll them, e.g. 90 to see them from the side
 *   TYR3D_VIEWER_SPIN=<degrees>  turn them by that much every frame
 */
#ifndef VIEWER_H
#define VIEWER_H

void dev_model_viewer(const char *what);

#endif /* VIEWER_H */
