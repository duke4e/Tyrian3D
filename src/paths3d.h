/*
 * Tyrian3D: where the 3D view's resources (shaders, models, map sides) are. A development build
 * finds them where it was built; an app bundle (tools/package_macos.sh) carries them beside the
 * program, in Contents/Resources.
 */
#ifndef PATHS3D_H
#define PATHS3D_H

#include <stddef.h>

// The directory named by the environment variable env if set, else `built` if it exists, else
// `name` in the program's own directory (SDL_GetBasePath). The result lives in buffer.
const char *tyr3d_resource_dir(const char *env, const char *built, const char *name, char *buffer, size_t size);

#endif /* PATHS3D_H */
